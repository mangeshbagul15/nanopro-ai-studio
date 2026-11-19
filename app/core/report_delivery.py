"""Final batch report: build the Excel, publish it to SFTP (outbound), notify.

The SFTP hub has two sides:

* ``sftp/inbound/<partner>/``  - source files partners keep dropping (CSV/TXT/XLSX)
* ``sftp/outbound/reports/``   - the final report file produced by this module

The report is built from real Snowflake L2 tables (MART_CATALOG, the marts,
DATA_QUALITY_MART and BATCH_CONTROL). If Snowflake is unreachable it falls back
to the DuckDB reconciliation report and the bronze manifest — never to invented
numbers. Delivery rules:

* email    - attachment when the file is <= 5 MB, always carries the SFTP path
* Telegram - summary + SFTP path
* WhatsApp - summary + SFTP path
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.core.logger import log_event

IST = timezone(timedelta(hours=5, minutes=30))
OUTBOUND_PREFIX = "sftp/outbound/reports"
EMAIL_ATTACH_LIMIT = 5 * 1024 * 1024
_TABLE_RE = re.compile(r"^[A-Za-z0-9_]+$")


def _s3():
    from app.core.sftp_ingestion import _s3 as sftp_s3

    return sftp_s3()


def _bucket() -> str:
    from app.core.sftp_ingestion import _bucket as sftp_bucket

    return sftp_bucket()


def _local_dir() -> str:
    path = os.path.join("data", "reports", "outbound")
    os.makedirs(path, exist_ok=True)
    return path


# ----------------------------------------------------------------------------
# Data gathering
# ----------------------------------------------------------------------------
def _clean_frame(frame):
    from datetime import date as date_type

    import pandas as pd

    frame = frame.copy()
    for column in frame.columns:
        frame[column] = frame[column].map(
            lambda value: (float(value) if isinstance(value, Decimal)
                           else value.isoformat() if isinstance(value, (datetime, date_type))
                           else value)
        )
    return frame


def _frame(cursor, database: str, schema: str, table: str, limit: int = 5000):
    import pandas as pd

    if not _TABLE_RE.match(table):
        raise ValueError(f"unsafe table name {table!r}")
    cursor.execute(f"SELECT * FROM {database}.{schema}.{table} LIMIT {int(limit)}")
    columns = [item[0] for item in (cursor.description or [])]
    rows = cursor.fetchall()
    return _clean_frame(pd.DataFrame(rows, columns=columns))


def _snowflake_frames() -> Dict[str, Any]:
    from app.core import snowflake_client

    database = str(snowflake_client.load_config().get("database") or "BANK_DB").strip()
    connection = snowflake_client.open_connection()
    try:
        cursor = connection.cursor()
        frames: Dict[str, Any] = {}
        catalog = _frame(cursor, database, "L2_CURATED", "MART_CATALOG", limit=200)
        frames["Mart Catalog"] = catalog
        mart_names = catalog["MART_NAME"].tolist() if "MART_NAME" in catalog.columns else []
        for name in mart_names[:8]:
            name = str(name or "")
            if not name or name.upper() == "DATA_QUALITY_MART":
                continue
            try:
                frames[name[:31]] = _frame(cursor, database, "L2_CURATED", name, limit=2000)
            except Exception:
                continue
        for table in ("DATA_QUALITY_MART", "BATCH_CONTROL"):
            try:
                frames[table.title().replace("_", " ")] = _frame(cursor, database, "L2_CURATED", table, limit=500)
            except Exception:
                continue
        return {"source": f"Snowflake {database}.L2_CURATED", "frames": frames}
    finally:
        try:
            connection.close()
        except Exception:
            pass


def _bronze_frames() -> Dict[str, Any]:
    import pandas as pd

    frames: Dict[str, Any] = {}
    try:
        from app.core import sftp_ingestion

        files = sftp_ingestion.bronze_files()
        frames["Bronze Tables"] = _clean_frame(pd.DataFrame([
            {"table": item.get("table"), "dataset": item.get("dataset"),
             "rows": item.get("rows"), "bytes": item.get("bytes"), "s3_key": item.get("key")}
            for item in files
        ]))
    except Exception:
        frames["Bronze Tables"] = pd.DataFrame([{"table": "unavailable"}])

    try:
        candidates = sorted(glob.glob(os.path.join("data", "reports", "duckdb", "report_*.json")),
                            key=os.path.getmtime, reverse=True)
        if candidates:
            with open(candidates[0], "r", encoding="utf-8") as handle:
                report = json.load(handle)
            frames["DuckDB Parity"] = _clean_frame(pd.DataFrame(report.get("rows_detail") or []))
    except Exception:
        pass
    return {"source": "DuckDB report + bronze manifest (Snowflake unavailable)", "frames": frames}


def _summary_frame(cycle: str, business_date: str, status: str, details: Dict[str, Any],
                   sftp_path: str, source: str):
    import pandas as pd

    from app.core import bq_export_scheduler

    state = bq_export_scheduler.STATE or {}
    last = state.get("last_result") or {}
    sf = state.get("snowflake") or {}
    duck = state.get("duckdb") or {}
    sftp_tables = 0
    sftp_rows = 0
    try:
        from app.core import sftp_ingestion

        tables = sftp_ingestion.status().get("tables") or []
        sftp_tables = len(tables)
        sftp_rows = sum(int(item.get("rows") or 0) for item in tables)
    except Exception:
        pass
    rows = [
        ("Report", f"NanoPro {cycle} batch report"),
        ("Business date", business_date),
        ("Generated at", datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")),
        ("Cycle status", status),
        ("Pipeline run id", last.get("run_id") or details.get("run_id") or ""),
        ("BigQuery tables exported", last.get("tables") or details.get("exported_tables") or 0),
        ("BigQuery rows exported", last.get("rows") or details.get("exported_rows") or 0),
        ("Bytes exported", last.get("bytes") or details.get("exported_bytes") or 0),
        ("SFTP tables in bronze", sftp_tables),
        ("SFTP rows loaded", sftp_rows),
        ("AWS services", json.dumps(last.get("services") or {}, default=str)),
        ("Snowflake status", sf.get("status") or details.get("snowflake_status") or ""),
        ("L1 duplicates removed", (sf.get("l1") or {}).get("duplicates_removed", "")),
        ("DuckDB status", duck.get("status") or details.get("duckdb_status") or ""),
        ("DuckDB parity mismatches", ", ".join(duck.get("mismatches") or []) or "none"),
        ("SFTP outbound path", sftp_path),
        ("Data source", source),
        ("Note", "Values are read from the live pipeline; nothing is estimated."),
    ]
    return pd.DataFrame(rows, columns=["Field", "Value"])


# ----------------------------------------------------------------------------
# Build + publish
# ----------------------------------------------------------------------------
def build(cycle: str = "MANUAL", business_date: str = "", status: str = "SUCCESS",
          details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create the Excel report locally and publish it to the SFTP outbound prefix."""
    import pandas as pd

    details = details or {}
    bdate = business_date or datetime.now(IST).date().isoformat()
    stamp = datetime.now(IST).strftime("%H%M%S")
    filename = f"NANOPRO_{str(cycle).upper()}_{bdate.replace('-', '')}_{stamp}.xlsx"

    try:
        bundle = _snowflake_frames()
    except Exception as exc:
        log_event(f"[Report] Snowflake read failed, using DuckDB/bronze fallback: {exc}",
                  level="WARNING", component="ReportDelivery")
        bundle = _bronze_frames()

    sftp_path = f"/sftp/outbound/reports/{filename}"
    frames = {"Summary": _summary_frame(cycle, bdate, status, details, sftp_path, bundle["source"])}
    frames.update(bundle["frames"])

    local_path = os.path.join(_local_dir(), filename)
    with pd.ExcelWriter(local_path, engine="openpyxl") as writer:
        for sheet, frame in frames.items():
            frame.to_excel(writer, sheet_name=sheet[:31], index=False)

    size = os.path.getsize(local_path)
    with open(local_path, "rb") as handle:
        body = handle.read()
    key = f"{OUTBOUND_PREFIX}/{filename}"
    upload = {"status": "unavailable", "error": ""}
    try:
        _s3().put_object(Bucket=_bucket(), Key=key, Body=body,
                         ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                         Metadata={"cycle": str(cycle), "business_date": bdate, "rows": str(len(frames))})
        upload = {"status": "uploaded", "key": key, "bucket": _bucket()}
    except Exception as exc:
        upload = {"status": "error", "error": str(exc)[:200]}

    result = {
        "status": "built" if upload["status"] == "uploaded" else "built_local_only",
        "filename": filename,
        "local_path": local_path,
        "bytes": size,
        "size_mb": round(size / (1024 * 1024), 2),
        "sheets": list(frames.keys()),
        "sftp_path": sftp_path,
        "s3_uri": f"s3://{_bucket()}/{key}" if upload["status"] == "uploaded" else "",
        "upload": upload,
        "source": bundle["source"],
    }
    log_event(f"[Report] {filename} built ({size} bytes, {len(frames)} sheets) -> {result['s3_uri'] or 'local only'}",
              component="ReportDelivery")
    return result


def deliver(cycle: str = "MANUAL", business_date: str = "", status: str = "SUCCESS",
            details: Optional[Dict[str, Any]] = None, async_send: bool = True) -> Dict[str, Any]:
    """Build the report, publish to SFTP and notify email / Telegram / WhatsApp."""
    try:
        report = build(cycle, business_date, status, details)
    except Exception as exc:
        log_event(f"[Report] build failed: {exc}", level="ERROR", component="ReportDelivery")
        from app.core import pipeline_alerts

        pipeline_alerts.dispatch(
            subject=f"NanoPro {cycle} report FAILED to build",
            body=f"Report generation failed: {str(exc)[:300]}\n\n" + pipeline_alerts.pipeline_summary(),
            trigger=f"report_{str(cycle).lower()}_error",
            async_send=async_send,
        )
        return {"status": "error", "error": str(exc)[:300]}

    from app.core import pipeline_alerts

    attach = [report["local_path"]] if report["bytes"] <= EMAIL_ATTACH_LIMIT else []
    body = pipeline_alerts.pipeline_summary({
        "Batch report": report["filename"],
        "SFTP outbound path": report["sftp_path"],
        "Storage": report["s3_uri"] or report["sftp_path"],
        "Email rule": ("attached (<= 5 MB)" if attach else "link only (> 5 MB)"),
    })
    subject = f"NanoPro {str(cycle).upper()} report - {business_date or datetime.now(IST).date().isoformat()} - {status}"
    results = pipeline_alerts.dispatch(
        subject=subject, body=body, trigger=f"report_{str(cycle).lower()}",
        sftp_path=report["sftp_path"], attachments=attach, async_send=async_send,
    )
    return {"status": "delivered", "report": report, "attachments": bool(attach), "results": results}


def list_outbound(limit: int = 40) -> Dict[str, Any]:
    """Reports currently published on the SFTP outbound prefix."""
    try:
        s3 = _s3()
        bucket = _bucket()
        paginator = s3.get_paginator("list_objects_v2")
        items: List[Dict[str, Any]] = []
        for page in paginator.paginate(Bucket=bucket, Prefix=f"{OUTBOUND_PREFIX}/"):
            for obj in page.get("Contents") or []:
                key = str(obj.get("Key") or "")
                if not key or key.endswith("/"):
                    continue
                items.append({
                    "key": key,
                    "filename": key.rsplit("/", 1)[-1],
                    "bytes": int(obj.get("Size") or 0),
                    "modified": obj.get("LastModified").isoformat() if obj.get("LastModified") else "",
                    "sftp_path": "/sftp/outbound/reports/" + key.rsplit("/", 1)[-1],
                })
        items.sort(key=lambda item: item["modified"], reverse=True)
        items = items[:limit]
        for item in items:
            try:
                item["download_url"] = s3.generate_presigned_url(
                    "get_object", Params={"Bucket": bucket, "Key": item["key"]}, ExpiresIn=3600)
            except Exception:
                item["download_url"] = ""
        return {"status": "live", "prefix": f"s3://{bucket}/{OUTBOUND_PREFIX}/",
                "sftp_path": "/sftp/outbound/reports/", "reports": items}
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:240], "reports": []}


def download_url(key: str) -> str:
    if not key.startswith(f"{OUTBOUND_PREFIX}/"):
        raise ValueError("Only files under the outbound reports prefix can be downloaded.")
    return _s3().generate_presigned_url(
        "get_object", Params={"Bucket": _bucket(), "Key": key}, ExpiresIn=900
    )
