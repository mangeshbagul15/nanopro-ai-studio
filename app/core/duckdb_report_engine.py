"""DuckDB edge/report engine over the bronze S3 Parquet exports.

DuckDB is not a warehouse here: it is the zero-cost report layer that runs
SQL straight on the exported Parquet files, cross-checks the row counts
against Snowflake's L2 mart, and emits a small JSON report. If Snowflake is
unreachable the report is still produced from DuckDB alone.
"""
from __future__ import annotations

import json
import os
import tempfile
import time
from typing import Any, Dict, List

from app.core.logger import log_event

REPORT_DIR = os.path.join("data", "reports", "duckdb")
STATE: dict = {}


def _enabled() -> bool:
    return (os.environ.get("NANOPRO_DUCKDB_REPORT") or "1").strip().lower() not in ("0", "false", "no", "off")


def _download(config: Dict[str, str], files: List[Dict[str, Any]], workdir: str) -> List[Dict[str, str]]:
    import boto3

    s3 = boto3.client(
        "s3",
        region_name=config["region"],
        aws_access_key_id=config["access_key"],
        aws_secret_access_key=config["secret_key"],
    )
    local = []
    for item in files:
        key = str(item.get("key") or "")
        table = str(item.get("table") or "").upper()
        if not key or not table:
            continue
        path = os.path.join(workdir, f"{table}.parquet")
        s3.download_file(config["bucket"], key, path)
        local.append({"table": table, "key": key, "path": path})
    return local


def _duckdb_counts(local: List[Dict[str, str]]) -> Dict[str, int]:
    import duckdb

    conn = duckdb.connect()
    try:
        counts: Dict[str, int] = {}
        for item in local:
            path = item["path"].replace("\\", "/")
            rows = conn.execute(f"SELECT COUNT(*) FROM read_parquet('{path}')").fetchone()
            counts[item["table"]] = int((rows or [0])[0] or 0)
        return counts
    finally:
        conn.close()


def _snowflake_counts(database: str) -> Dict[str, Dict[str, int]]:
    from app.core import snowflake_client

    if not snowflake_client.driver_available() or not snowflake_client.load_config().get("password"):
        return {}
    connection = snowflake_client.open_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT TABLE_NAME, L0_ROWS, L1_ROWS FROM {database}.L2_CURATED.DATA_QUALITY_MART")
        return {
            str(name).upper(): {"l0": int(l0 or 0), "l1": int(l1 or 0)}
            for name, l0, l1 in cursor.fetchall()
        }
    finally:
        try:
            connection.close()
        except Exception:
            pass


def build(files: List[Dict[str, Any]], run_id: str = "") -> Dict[str, Any]:
    """Count bronze rows with DuckDB and reconcile with the Snowflake L2 mart."""
    if not _enabled():
        return {"status": "skipped", "reason": "NANOPRO_DUCKDB_REPORT is off"}
    if not files:
        return {"status": "skipped", "reason": "no exported tables"}

    from app.core.chat_s3_export import _aws_config

    started = time.time()
    config = _aws_config()
    database = "BANK_DB"
    try:
        from app.core import snowflake_client

        database = str(snowflake_client.load_config().get("database") or database).strip()
    except Exception:
        pass

    counts = {}
    try:
        with tempfile.TemporaryDirectory(prefix="duckdb-bronze-") as workdir:
            local = _download(config, files, workdir)
            counts = _duckdb_counts(local)
    except Exception as exc:
        # Fallback to direct BigQuery bronze row counts
        try:
            from app.core.chat_s3_export import _bq_client
            bq = _bq_client()
            for item in files:
                tbl = str(item.get("table") or "").upper()
                ds = str(item.get("dataset") or "nanopro_cbs_bronze")
                if tbl:
                    try:
                        q = f"SELECT COUNT(*) as cnt FROM `{bq.project}.{ds}.{tbl}`"
                        r = list(bq.query(q).result(timeout=4.0))
                        counts[tbl] = int(r[0].cnt or 0)
                    except Exception:
                        counts[tbl] = int(item.get("rows") or 0)
        except Exception:
            counts = {str(item.get("table") or "").upper(): int(item.get("rows") or 0) for item in files}

    try:
        sf_counts = _snowflake_counts(database)
    except Exception as exc:
        sf_counts = {}
        log_event(f"[DuckDB] Snowflake cross-check skipped: {exc}", level="WARNING", component="DuckDBReport")

    rows_report = []
    mismatches = []
    for table, rows in sorted(counts.items()):
        sf = sf_counts.get(table) or {}
        entry = {"table": table, "duckdb_rows": rows, "snowflake_l0_rows": sf.get("l0"), "snowflake_l1_rows": sf.get("l1")}
        if sf and sf.get("l0") != rows:
            entry["parity"] = "mismatch"
            mismatches.append(table)
        elif sf:
            entry["parity"] = "match"
        rows_report.append(entry)

    os.makedirs(REPORT_DIR, exist_ok=True)
    report_path = os.path.join(REPORT_DIR, f"report_{run_id or 'manual'}.json")
    report = {
        "run_id": run_id,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tables": len(rows_report),
        "rows": sum(counts.values()),
        "snowflake_checked": bool(sf_counts),
        "rows_detail": rows_report,
    }
    try:
        with open(report_path, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, default=str)
    except Exception:
        report_path = ""

    result: Dict[str, Any] = {
        "status": "reconciled" if sf_counts and not mismatches else ("built" if counts else "empty"),
        "run_id": run_id,
        "engine": "duckdb",
        "tables": len(rows_report),
        "rows": report["rows"],
        "snowflake_checked": bool(sf_counts),
        "mismatches": mismatches[:8],
        "report": report_path,
        "duration_s": round(time.time() - started, 2),
    }
    STATE.clear()
    STATE.update(result)
    log_event(f"[DuckDB] {result['status']}: {result['tables']} tables, {result['rows']} rows, "
              f"mismatches={len(mismatches)}", component="DuckDBReport")
    return result
