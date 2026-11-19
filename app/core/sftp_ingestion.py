"""SFTP landing zone that lives in S3.

There is no paid AWS Transfer Family endpoint: partners upload CSV / TXT / XLSX
files to ``s3://<bucket>/sftp/inbound/<partner>/`` (through the NanoPro upload
form or any S3 tool). The poller converts each new file to Parquet under
``sftp/bronze/<partner>/``, publishes a manifest next to it, registers the table
in the ``nanopro_sftp`` Glue database, and then refreshes Snowflake L0/L1/L2 and
the DuckDB report — the exact same downstream path the BigQuery source uses.

State (which file produced which table, and its SHA-256) is kept in
``sftp/_STATE.json`` in S3 so a Render redeploy does not replay old files.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.logger import log_event

LANDING_ROOT = "sftp/inbound"
BRONZE_ROOT = "sftp/bronze"
STATE_KEY = "sftp/_STATE.json"
GLUE_DATABASE = "nanopro_sftp"
MAX_BYTES = 25 * 1024 * 1024
SUPPORTED_SUFFIXES = (".csv", ".txt", ".tsv", ".xlsx", ".xls")

_LOCK = threading.RLock()
_BRONZE_CACHE = {"at": 0.0, "files": []}
_STATE_CACHE: Dict[str, Any] = {"at": 0.0, "value": {}}
STATE: Dict[str, Any] = {}


# ----------------------------------------------------------------------------
# S3 plumbing
# ----------------------------------------------------------------------------
def _config() -> Dict[str, str]:
    from app.core.chat_s3_export import _aws_config

    return _aws_config()


def _s3():
    import boto3

    config = _config()
    return boto3.client(
        "s3",
        region_name=config["region"],
        aws_access_key_id=config["access_key"],
        aws_secret_access_key=config["secret_key"],
    )


def _bucket() -> str:
    bucket = _config().get("bucket") or ""
    if not bucket:
        raise RuntimeError("AWS_S3_BUCKET is not configured.")
    return bucket


def _read_state(force: bool = False) -> Dict[str, Any]:
    now = time.time()
    if not force and _STATE_CACHE["value"] and now - _STATE_CACHE["at"] < 30:
        return dict(_STATE_CACHE["value"])
    try:
        body = _s3().get_object(Bucket=_bucket(), Key=STATE_KEY)["Body"].read()
        value = json.loads(body)
    except Exception:
        value = {}
    if not isinstance(value, dict):
        value = {}
    value.setdefault("files", {})
    value.setdefault("batches", [])
    _STATE_CACHE.update({"at": now, "value": value})
    return value


def _write_state(value: Dict[str, Any]) -> None:
    body = json.dumps(value, indent=2, default=str).encode("utf-8")
    _s3().put_object(Bucket=_bucket(), Key=STATE_KEY, Body=body, ContentType="application/json")
    _STATE_CACHE.update({"at": time.time(), "value": value})


# ----------------------------------------------------------------------------
# Naming + parsing
# ----------------------------------------------------------------------------
def _partner_of(key: str) -> str:
    parts = key.split("/")
    if len(parts) >= 4:
        return _slug(parts[2]) or "manual"
    return "manual"


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", str(value or "")).strip("_")


def _table_of(partner: str, filename: str) -> str:
    stem = os.path.splitext(os.path.basename(filename))[0]
    name = _slug(stem).upper() or "UNTITLED"
    prefix = _slug(partner).upper() or "MANUAL"
    # Partner files are often already named after the partner (hdfc_upi.csv);
    # don't repeat the prefix in the bronze table name.
    full = name if name == prefix or name.startswith(prefix + "_") else f"{prefix}_{name}"
    if not full[0].isalpha():
        full = "T_" + full
    return full[:60]


def _sniff_separator(sample: str) -> str:
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;|\t").delimiter
    except Exception:
        for candidate in ("|", ";", "\t", ","):
            if candidate in sample:
                return candidate
        return ","


def _read_frame(filename: str, data: bytes):
    import pandas as pd

    suffix = os.path.splitext(filename)[1].lower()
    if suffix in (".xlsx", ".xls"):
        frame = pd.read_excel(io.BytesIO(data), sheet_name=0)
    else:
        text = data.decode("utf-8-sig", "replace")
        separator = _sniff_separator("\n".join(text.splitlines()[:20]))
        frame = pd.read_csv(io.StringIO(text), sep=separator)
    names, used = [], {}
    for index, col in enumerate(frame.columns):
        name = _column_name(col, index)
        used[name] = used.get(name, 0) + 1
        names.append(name if used[name] == 1 else f"{name}_{used[name]}")
    frame.columns = names
    frame = frame.dropna(how="all")
    for column in frame.columns:
        if frame[column].dtype == object:
            frame[column] = frame[column].map(lambda v: v.strip() if isinstance(v, str) else v)
    if frame.empty or not len(frame.columns):
        raise ValueError("file has no data rows or no columns")
    return frame


def _column_name(value: Any, index: int) -> str:
    name = _slug(value).upper()
    if not name:
        name = f"COL_{index + 1}"
    if not name[0].isalpha():
        name = "C_" + name
    return name[:80]


def _arrow_duck(field_type) -> str:
    import pyarrow as pa

    if pa.types.is_boolean(field_type):
        return "BOOLEAN"
    if pa.types.is_integer(field_type):
        return "BIGINT"
    if pa.types.is_floating(field_type):
        return "DOUBLE"
    if pa.types.is_decimal(field_type):
        return f"DECIMAL({field_type.precision},{field_type.scale})"
    if pa.types.is_timestamp(field_type):
        return "TIMESTAMPTZ" if getattr(field_type, "tz", None) else "TIMESTAMP"
    if pa.types.is_date(field_type):
        return "DATE"
    if pa.types.is_binary(field_type):
        return "BLOB"
    return "VARCHAR"


def _parquet_bytes(frame) -> bytes:
    import pyarrow as pa
    import pyarrow.parquet as pq

    table = pa.Table.from_pandas(frame, preserve_index=False)
    buffer = io.BytesIO()
    pq.write_table(table, buffer, compression="snappy")
    columns = [
        {"name": field.name, "type": _arrow_duck(field.type)}
        for field in table.schema
    ]
    return buffer.getvalue(), columns


# ----------------------------------------------------------------------------
# Bronze + manifest + Glue
# ----------------------------------------------------------------------------
def _manifest_key(partner: str) -> str:
    return f"{BRONZE_ROOT}/{partner}/_MANIFEST.json"


def _read_manifest(partner: str) -> Dict[str, Any]:
    try:
        body = _s3().get_object(Bucket=_bucket(), Key=_manifest_key(partner))["Body"].read()
        manifest = json.loads(body)
        if isinstance(manifest, dict):
            manifest.setdefault("files", [])
            return manifest
    except Exception:
        pass
    return {"source": f"sftp:{partner}", "files": []}


def _write_manifest(partner: str, manifest: Dict[str, Any]) -> str:
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest["bucket"] = _bucket()
    manifest["prefix"] = f"{BRONZE_ROOT}/{partner}"
    body = json.dumps(manifest, indent=2, default=str).encode("utf-8")
    key = _manifest_key(partner)
    _s3().put_object(Bucket=_bucket(), Key=key, Body=body, ContentType="application/json",
                     Metadata={"sha256": hashlib.sha256(body).hexdigest()})
    return key


def _register_glue(partner: str, table: str, columns: List[Dict[str, str]], location: str) -> Dict[str, Any]:
    try:
        from app.core.bigquery_aws_pipeline import _athena_type, _aws_client

        glue = _aws_client(_config(), "glue")
        try:
            glue.create_database(DatabaseInput={"Name": GLUE_DATABASE,
                                                "Description": "NanoPro SFTP inbound landing"})
        except Exception as exc:
            if "already exists" not in str(exc).lower() and "AlreadyExists" not in type(exc).__name__:
                raise
        table_input = {
            "Name": table.lower(),
            "TableType": "EXTERNAL_TABLE",
            "Parameters": {"classification": "parquet", "EXTERNAL": "TRUE", "source": "sftp"},
            "StorageDescriptor": {
                "Columns": [
                    {"Name": str(col["name"]).lower(), "Type": _athena_type(col["type"]), "Comment": ""}
                    for col in columns
                ],
                "Location": location,
                "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
                "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
                "SerdeInfo": {"SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"},
            },
        }
        try:
            glue.create_table(DatabaseName=GLUE_DATABASE, TableInput=table_input)
            return {"status": "registered", "database": GLUE_DATABASE, "table": table.lower()}
        except Exception as exc:
            if "AlreadyExists" not in type(exc).__name__ and "already exists" not in str(exc).lower():
                raise
            glue.update_table(DatabaseName=GLUE_DATABASE, TableInput=table_input, SkipArchive=True)
            return {"status": "updated", "database": GLUE_DATABASE, "table": table.lower()}
    except Exception as exc:
        return {"status": "unavailable", "database": GLUE_DATABASE, "error": str(exc)[:200]}


# ----------------------------------------------------------------------------
# Ingest
# ----------------------------------------------------------------------------
def list_landing() -> List[Dict[str, Any]]:
    s3 = _s3()
    bucket = _bucket()
    paginator = s3.get_paginator("list_objects_v2")
    files: List[Dict[str, Any]] = []
    for page in paginator.paginate(Bucket=bucket, Prefix=f"{LANDING_ROOT}/"):
        for obj in page.get("Contents") or []:
            key = str(obj.get("Key") or "")
            name = key.rsplit("/", 1)[-1]
            if not name or name.startswith("_") or name.lower().endswith("/"):
                continue
            files.append({
                "key": key,
                "name": name,
                "partner": _partner_of(key),
                "size": int(obj.get("Size") or 0),
                "modified": obj.get("LastModified").isoformat() if obj.get("LastModified") else "",
                "etag": str(obj.get("ETag") or "").strip('"'),
            })
    files.sort(key=lambda item: item["modified"], reverse=True)
    return files


def upload(filename: str, data: bytes, partner: str = "manual") -> Dict[str, Any]:
    suffix = os.path.splitext(filename)[1].lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(f"Unsupported file type '{suffix}'. Use {', '.join(SUPPORTED_SUFFIXES)}.")
    if not data:
        raise ValueError("Uploaded file is empty.")
    if len(data) > MAX_BYTES:
        raise ValueError(f"File is larger than {MAX_BYTES // (1024 * 1024)} MB.")
    safe_partner = _slug(partner).lower() or "manual"
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", os.path.basename(filename))
    key = f"{LANDING_ROOT}/{safe_partner}/{safe_name}"
    _s3().put_object(Bucket=_bucket(), Key=key, Body=data,
                     ContentType="application/octet-stream",
                     Metadata={"sha256": hashlib.sha256(data).hexdigest(), "uploaded_by": "nanopro"})
    log_event(f"[SFTP] landed {key} ({len(data)} bytes)", component="SFTPIngest")
    return {"status": "uploaded", "key": key, "bytes": len(data),
            "s3_uri": f"s3://{_bucket()}/{key}"}


def ingest(key: str, force: bool = False) -> Dict[str, Any]:
    """Convert one landing file to bronze Parquet; safe to call repeatedly."""
    with _LOCK:
        filename = key.rsplit("/", 1)[-1]
        partner = _partner_of(key)
        bucket = _bucket()
        body = _s3().get_object(Bucket=bucket, Key=key)["Body"].read()
        digest = hashlib.sha256(body).hexdigest()
        state = _read_state()
        previous = state["files"].get(key) or {}
        if not force and previous.get("sha256") == digest and previous.get("status") == "success":
            return {"status": "skipped", "reason": "unchanged", "key": key,
                    "table": previous.get("table")}

        entry = {"key": key, "name": filename, "partner": partner, "sha256": digest,
                 "bytes": len(body), "ingested_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        try:
            frame = _read_frame(filename, body)
            parquet, columns = _parquet_bytes(frame)
            table = _table_of(partner, filename)
            bronze_key = f"{BRONZE_ROOT}/{partner}/{table}/{table}.parquet"
            _s3().put_object(Bucket=bucket, Key=bronze_key, Body=parquet,
                             ContentType="application/vnd.apache.parquet",
                             Metadata={"sha256": hashlib.sha256(parquet).hexdigest(),
                                       "rows": str(len(frame)), "source": key})
            manifest = _read_manifest(partner)
            manifest["files"] = [f for f in manifest["files"] if str(f.get("table")) != table]
            manifest["files"].append({
                "dataset": partner, "table": table, "key": bronze_key,
                "rows": int(len(frame)), "bytes": len(parquet),
                "sha256": hashlib.sha256(parquet).hexdigest(), "status": "uploaded",
                "columns": columns, "source_file": filename,
            })
            manifest_key = _write_manifest(partner, manifest)
            location = f"s3://{bucket}/{BRONZE_ROOT}/{partner}/{table}/"
            glue = _register_glue(partner, table, columns, location)
            entry.update({
                "status": "success", "table": table, "dataset": partner,
                "bronze_key": bronze_key, "manifest": manifest_key,
                "rows": int(len(frame)), "columns": len(columns),
                "glue": glue.get("status"), "error": "",
            })
            _BRONZE_CACHE["at"] = 0.0
            _record("sftp", "sftp_to_s3", "SUCCESS",
                    f"{table}: {len(frame)} rows from {filename} → s3://{bucket}/{bronze_key}")
        except Exception as exc:
            entry.update({"status": "error", "error": str(exc)[:240], "rows": 0})
            _record("sftp", "sftp_to_s3", "ERROR", f"{filename}: {entry['error']}")

        state["files"][key] = entry
        if entry["status"] == "success":
            state["batches"].insert(0, {
                "batch_id": f"SFTP-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
                "key": key, "table": entry["table"], "rows": entry["rows"],
                "at": entry["ingested_at"],
            })
            del state["batches"][50:]
        _write_state(state)
        log_event(f"[SFTP] {entry['status']} {filename} → {entry.get('table')} "
                  f"({entry.get('rows')} rows)", component="SFTPIngest",
                  level="INFO" if entry["status"] == "success" else "WARNING")
        if entry["status"] == "success":
            threading.Thread(target=_publish_aws, args=(key, dict(entry)), daemon=True,
                             name="sftp-aws-publish").start()
        return entry


def _record(actor: str, dag_id: str, status: str, message: str) -> None:
    try:
        from app.core.pipeline_orchestrator import _record_run

        _record_run("run", dag_id, status, str(message or "")[:280], actor)
    except Exception:
        pass


def _publish_downstream(result: Dict[str, Any]) -> None:
    """Share the latest Snowflake/DuckDB outcome with the DAG cards."""
    try:
        from app.core import bq_export_scheduler

        bq_export_scheduler.STATE["snowflake"] = result.get("snowflake") or {}
        bq_export_scheduler.STATE["duckdb"] = result.get("duckdb") or {}
        from app.core import pipeline_orchestrator as orch

        orch._OVERVIEW_CACHE["at"] = 0.0
    except Exception:
        pass


def _cloudwatch_sftp(config: Dict[str, str], entry: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from app.core.bigquery_aws_pipeline import _aws_client, _err

        _aws_client(config, "cloudwatch").put_metric_data(
            Namespace="NanoPro/SFTP",
            MetricData=[
                {"MetricName": "FilesIngested", "Unit": "Count", "Value": 1},
                {"MetricName": "RowsIngested", "Unit": "Count", "Value": int(entry.get("rows") or 0)},
                {"MetricName": "BytesIngested", "Unit": "Bytes", "Value": int(entry.get("bytes") or 0)},
            ],
        )
        return {"status": "published", "namespace": "NanoPro/SFTP", "metrics": 3}
    except Exception as exc:
        return {"status": "unavailable", "namespace": "NanoPro/SFTP", "error": _err(exc)}


def _sns_sftp(config: Dict[str, str], run: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from app.core.bigquery_aws_pipeline import SNS_TOPIC_NAME, _aws_client, _err

        sns = _aws_client(config, "sns")
        arn = sns.create_topic(Name=SNS_TOPIC_NAME)["TopicArn"]
        sns.publish(TopicArn=arn, Subject="NanoPro SFTP ingest",
                    Message=str(run.get("summary") or "")[:2500])
        return {"status": "published", "topic": SNS_TOPIC_NAME}
    except Exception as exc:
        return {"status": "unavailable", "topic": "nanopro-pipeline-notifications", "error": _err(exc)}


def _publish_aws(key: str, entry: Dict[str, Any]) -> None:
    """Announce one ingested partner file to the free-tier AWS side-channels."""
    table = str(entry.get("table") or "")
    partner = str(entry.get("partner") or "")
    bronze_key = str(entry.get("bronze_key") or "")
    if not table or not bronze_key:
        return
    rows = int(entry.get("rows") or 0)
    size = int(entry.get("bytes") or 0)
    try:
        config = _config()
    except Exception as exc:
        log_event(f"[SFTP] AWS side-channels skipped for {table}: {exc}",
                  level="WARNING", component="SFTPIngest")
        return

    run_id = "SFTP-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = {"run_id": run_id, "started_at": entry.get("ingested_at") or "",
           "status": "success", "tables": [{"table": table}], "rows": rows,
           "bytes": size, "duration_ms": 0,
           "summary": f"SFTP {partner}: {table} {rows} rows -> s3://{config['bucket']}/{bronze_key}"}
    event = {"event": "sftp_to_bronze", "run_id": run_id, "table": table, "dataset": partner,
             "rows": rows, "bytes": size, "key": bronze_key, "at": run["started_at"]}
    out: Dict[str, Any] = {}
    try:
        from app.core.bigquery_aws_pipeline import _dynamodb_record, _sqs_send

        out["sqs"] = _sqs_send(config, event)
        out["dynamodb"] = _dynamodb_record(config, run)
    except Exception as exc:
        out["sqs"] = out["dynamodb"] = {"status": "unavailable", "error": str(exc)[:200]}
    out["cloudwatch"] = _cloudwatch_sftp(config, entry)
    out["sns"] = _sns_sftp(config, run)
    try:
        from app.core.iceberg_lake import publish as publish_iceberg

        out["iceberg"] = publish_iceberg(config, [{"key": bronze_key, "dataset": "sftp",
                                                  "table": table, "rows": rows, "bytes": size}])
    except Exception as exc:
        out["iceberg"] = {"status": "unavailable", "error": str(exc)[:200]}

    statuses = {name: str(item.get("status") or "") for name, item in out.items()}
    try:
        with _LOCK:
            state = _read_state(force=True)
            saved = state["files"].get(key)
            if saved:
                saved["aws_services"] = statuses
                _write_state(state)
    except Exception as exc:
        log_event(f"[SFTP] AWS side-channel state write failed for {table}: {exc}",
                  level="WARNING", component="SFTPIngest")
    _BRONZE_CACHE["at"] = 0.0
    healthy = all(status in ("sent", "recorded", "published", "registered", "updated", "skipped")
                  for status in statuses.values())
    log_event(f"[SFTP] AWS side-channels for {table}: {statuses}",
              level="INFO" if healthy else "WARNING", component="SFTPIngest")


def refresh_downstream(run_id: str = "") -> Dict[str, Any]:
    """Push every bronze table (BigQuery + SFTP) through Snowflake and DuckDB."""
    files = bronze_files()
    if not files:
        return {"status": "skipped", "reason": "no bronze files"}
    run_id = run_id or f"orc_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    result: Dict[str, Any] = {"run_id": run_id, "tables": len(files)}
    try:
        from app.core.snowflake_lakehouse import sync

        result["snowflake"] = sync(files, run_id)
    except Exception as exc:
        result["snowflake"] = {"status": "error", "error": str(exc)[:240]}
    try:
        from app.core.duckdb_report_engine import build

        result["duckdb"] = build(files, run_id)
    except Exception as exc:
        result["duckdb"] = {"status": "error", "error": str(exc)[:240]}
    sf = result["snowflake"] or {}
    duck = result["duckdb"] or {}
    result["status"] = "success" if sf.get("status") == "success" else "partial"
    result["summary"] = (
        f"{result['tables']} bronze tables · Snowflake {sf.get('status')} · "
        f"DuckDB {duck.get('status')}"
    )
    _publish_downstream(result)

    sf_state = {"synced": "SUCCESS", "partial": "PARTIAL", "unavailable": "ERROR",
                "error": "ERROR", "skipped": "IDLE"}.get(str(sf.get("status") or ""), "")
    if sf_state in ("PARTIAL", "ERROR"):
        reason = str(sf.get("error") or sf.get("status") or "Snowflake sync failed")
        for dag in ("snowflake_l0", "snowflake_l1", "snowflake_l2"):
            _record("sftp", dag, sf_state, reason)
    duck_status = str(duck.get("status") or "")
    if duck_status == "error":
        _record("sftp", "duckdb_report", "ERROR", str(duck.get("error") or "DuckDB report failed"))
    elif duck.get("mismatches"):
        _record("sftp", "duckdb_report", "PARTIAL",
                f"{len(duck['mismatches'])} parity mismatch(es): "
                + ", ".join(str(item) for item in duck["mismatches"][:5]))
    return result


def bronze_files() -> List[Dict[str, Any]]:
    """All Parquet entries currently in the lake: BigQuery first, then SFTP."""
    files: List[Dict[str, Any]] = []
    try:
        from app.core.bigquery_aws_pipeline import EXPORT_ROOT

        if EXPORT_ROOT:
            s3 = _s3()
            bucket = _bucket()
            paginator = s3.get_paginator("list_objects_v2")
            keys = []
            for page in paginator.paginate(Bucket=bucket, Prefix=f"{EXPORT_ROOT}/"):
                for obj in page.get("Contents") or []:
                    key = str(obj.get("Key") or "")
                    if key.endswith("_MANIFEST.json"):
                        keys.append(key)
            for key in keys:
                try:
                    manifest = json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
                except Exception:
                    continue
                for item in manifest.get("files") or []:
                    if item.get("key") and item.get("table"):
                        files.append(item)
    except Exception as exc:
        log_event(f"[SFTP] BigQuery manifest read failed: {exc}", level="WARNING", component="SFTPIngest")

    try:
        state = _read_state()
        partners = sorted({entry.get("partner") for entry in state["files"].values()
                           if entry.get("status") == "success" and entry.get("partner")})
        for partner in partners:
            for item in _read_manifest(partner).get("files") or []:
                if item.get("key") and item.get("table"):
                    files.append(item)
    except Exception as exc:
        log_event(f"[SFTP] SFTP manifest read failed: {exc}", level="WARNING", component="SFTPIngest")

    seen, unique = set(), []
    for item in files:
        table = str(item.get("table") or "").upper()
        if table and table not in seen:
            seen.add(table)
            unique.append(item)
    return unique


def poll(force: bool = False) -> Dict[str, Any]:
    """Ingest every new landing file, then refresh Snowflake and DuckDB once."""
    with _LOCK:
        try:
            landing = list_landing()
        except Exception as exc:
            return {"status": "error", "error": str(exc)[:240]}
        processed, errors = [], []
        for item in landing:
            try:
                result = ingest(item["key"], force=force)
                if result.get("status") in ("success", "error"):
                    processed.append(result)
                    if result.get("status") == "error":
                        errors.append(f"{item['name']}: {result.get('error')}")
            except Exception as exc:
                errors.append(f"{item['name']}: {str(exc)[:160]}")
        summary = {"status": "success" if not errors else ("partial" if processed else "error"),
                   "landing_files": len(landing), "processed": processed, "errors": errors}
        if any(item.get("status") == "success" for item in processed):
            summary["downstream"] = refresh_downstream()
        STATE.clear()
        STATE.update(summary)
        STATE["finished_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        return summary


def purge(key: str, delete_landing: bool = False) -> Dict[str, Any]:
    """Roll back one ingested file: drop its Snowflake tables and bronze object."""
    with _LOCK:
        state = _read_state(force=True)
        entry = state["files"].get(key) or {}
        table = str(entry.get("table") or "")
        partner = str(entry.get("partner") or _partner_of(key))
        removed: Dict[str, Any] = {"key": key, "table": table, "bronze": False, "snowflake": [], "errors": []}

        try:
            if entry.get("bronze_key"):
                _s3().delete_object(Bucket=_bucket(), Key=entry["bronze_key"])
                removed["bronze"] = True
            manifest = _read_manifest(partner)
            manifest["files"] = [f for f in manifest["files"] if str(f.get("table")) != table]
            _write_manifest(partner, manifest)
        except Exception as exc:
            removed["errors"].append(f"bronze: {str(exc)[:160]}")

        if table:
            try:
                from app.core import snowflake_client

                connection = snowflake_client.open_connection()
                try:
                    database = str(snowflake_client.load_config().get("database") or "BANK_DB").strip()
                    cursor = connection.cursor()
                    for schema in ("L0_STAGING", "L1_HARMONIZED"):
                        cursor.execute(f"DROP TABLE IF EXISTS {database}.{schema}.{table}")
                        removed["snowflake"].append(f"{schema}.{table}")
                    connection.commit()
                finally:
                    connection.close()
            except Exception as exc:
                removed["errors"].append(f"snowflake: {str(exc)[:160]}")

        state["files"].pop(key, None)
        if delete_landing:
            try:
                _s3().delete_object(Bucket=_bucket(), Key=key)
                removed["landing_deleted"] = True
            except Exception as exc:
                removed["errors"].append(f"landing: {str(exc)[:160]}")
        _write_state(state)
        _BRONZE_CACHE["at"] = 0.0
        removed["status"] = "rolled_back" if not removed["errors"] else "partial"
        removed["table_removed"] = table
        log_event(f"[SFTP] rollback {key} → dropped {removed['snowflake']}", component="SFTPIngest",
                  level="WARNING")
        return removed


def status() -> Dict[str, Any]:
    try:
        landing = list_landing()
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:240], "files": [], "tables": []}
    state = _read_state()
    files = []
    for item in landing:
        entry = state["files"].get(item["key"]) or {}
        files.append({
            **item,
            "status": entry.get("status") or "new",
            "table": entry.get("table") or "",
            "rows": entry.get("rows") or 0,
            "columns": entry.get("columns") or 0,
            "glue": entry.get("glue") or "",
            "aws_services": entry.get("aws_services") or {},
            "error": entry.get("error") or "",
            "ingested_at": entry.get("ingested_at") or "",
            "sha256": entry.get("sha256") or "",
        })
    tables = [
        {"table": entry.get("table"), "dataset": entry.get("partner"),
         "rows": entry.get("rows"), "columns": entry.get("columns"),
         "bronze_key": entry.get("bronze_key"), "source_file": entry.get("name"),
         "ingested_at": entry.get("ingested_at")}
        for entry in state["files"].values() if entry.get("status") == "success"
    ]
    return {
        "status": "live",
        "landing_prefix": f"s3://{_bucket()}/{LANDING_ROOT}/",
        "bronze_prefix": f"s3://{_bucket()}/{BRONZE_ROOT}/",
        "glue_database": GLUE_DATABASE,
        "files": files,
        "tables": sorted(tables, key=lambda item: str(item.get("table"))),
        "batches": state.get("batches", [])[:10],
        "last_run": STATE or None,
        "supported": list(SUPPORTED_SUFFIXES),
        "max_mb": MAX_BYTES // (1024 * 1024),
    }


def sample_file(partner: str = "sample") -> Dict[str, Any]:
    sample = (
        "account_id,customer_name,branch,amount,txn_date,status\n"
        "A1001,Ravi Patil,PUNE-01,15250.50,2026-11-18,POSTED\n"
        "A1002,Sunita Deshmukh,MUM-04,8200.00,2026-11-18,POSTED\n"
        "A1003,Amit Joshi,NASHIK-02,42100.75,2026-11-19,PENDING\n"
        "A1004,Priya Kulkarni,PUNE-01,999.99,2026-11-19,POSTED\n"
    ).encode("utf-8")
    return upload("sample_transactions.csv", sample, partner=partner)
