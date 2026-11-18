"""Exports the BigQuery CBS bronze tables to S3 as Snappy Parquet.

Chat command, e.g. "export bronze to s3". Each table is read through the same
ADC BigQuery client the chat already uses, written to Parquet with DuckDB,
checksummed with SHA-256 and uploaded under bronze/cbs/<table>/<table>.parquet.
A _MANIFEST.json and _SUCCESS marker describe the run.
"""
import hashlib
import json
import os
import re
import tempfile
import time
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

BRONZE_SCHEMA = "nanopro_cbs_bronze"
EXPORT_PREFIX = "bronze/cbs"
DEFAULT_S3_BUCKET = "nanopro-data-lake-765865641438"

_EXPORT_Q = re.compile(r"\b(export|upload|push|copy|transfer)\b|एक्सपोर्ट|टाक|पाठव|काढ", re.IGNORECASE)
_S3_Q = re.compile(r"\bs3\b|\baws\b|बकेट", re.IGNORECASE)
_BRONZE_Q = re.compile(r"\bbronze\b|\bcbs\b|nanopro_cbs_bronze|सगळ|सर्व|\ball\b|all\s+tables", re.IGNORECASE)

_DUCK_TYPES = {
    "STRING": "VARCHAR",
    "BYTES": "BLOB",
    "INTEGER": "BIGINT",
    "INT64": "BIGINT",
    "FLOAT": "DOUBLE",
    "FLOAT64": "DOUBLE",
    "BOOLEAN": "BOOLEAN",
    "BOOL": "BOOLEAN",
    "DATE": "DATE",
    "DATETIME": "TIMESTAMP",
    "TIMESTAMP": "TIMESTAMPTZ",
    "TIME": "TIME",
    "JSON": "VARCHAR",
    "GEOGRAPHY": "VARCHAR",
}


class ExportError(Exception):
    pass


def _duck_type(field: Any) -> str:
    base = (getattr(field, "field_type", "STRING") or "STRING").upper()
    if base in ("NUMERIC", "BIGNUMERIC", "DECIMAL"):
        precision = int(getattr(field, "precision", None) or 38)
        scale = int(getattr(field, "scale", None) or 0)
        precision = max(1, min(precision, 38))
        scale = max(0, min(scale, precision))
        return f"DECIMAL({precision},{scale})"
    return _DUCK_TYPES.get(base, "VARCHAR")


def _quote(name: str) -> str:
    return '"' + str(name).replace('"', '""') + '"'


def _cell(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, default=str)
    if isinstance(value, (date, datetime)):
        return value.isoformat() if isinstance(value, date) and not isinstance(value, datetime) else value
    return value


def _aws_config() -> Dict[str, str]:
    from app.core.connection_manager import connection_manager

    cfg = connection_manager.get_connection_config("AWS_S3_DATA_LAKE", mask=False) or {}
    meta = cfg.get("metadata") or {}
    if isinstance(meta, str):
        meta = {}
    bucket = (
        os.environ.get("AWS_S3_BUCKET")
        or str(meta.get("bucket") or cfg.get("database_name") or "")
    ).strip()
    # Legacy vault rows still carry the pre-account bucket name.
    if bucket in ("", "nanopro-data-lake"):
        bucket = DEFAULT_S3_BUCKET
    return {
        "access_key": (os.environ.get("AWS_ACCESS_KEY_ID") or str(cfg.get("username") or "")).strip(),
        "secret_key": (os.environ.get("AWS_SECRET_ACCESS_KEY") or str(cfg.get("secret_value") or "")).strip(),
        "region": (os.environ.get("AWS_DEFAULT_REGION") or str(meta.get("region") or "") or "ap-southeast-2").strip(),
        "bucket": bucket,
    }


def _s3_client(config: Dict[str, str]):
    import boto3

    return boto3.Session(
        region_name=config["region"],
        aws_access_key_id=config["access_key"],
        aws_secret_access_key=config["secret_key"],
    ).client("s3")


def _bq_client():
    from app.core.chat_bigquery_data import _client

    client, _ = _client()
    return client


def _table_fields(client: Any, schema: str, table: str) -> List[Any]:
    return list(client.get_table(f"{client.project}.{schema}.{table}").schema)


def _read_rows(client: Any, schema: str, table: str) -> Tuple[List[Any], List[Dict[str, Any]]]:
    fields = _table_fields(client, schema, table)
    job = client.query(f"SELECT * FROM `{client.project}.{schema}.{table}`")
    rows = []
    for row in job.result(timeout=600):
        item = dict(row.items())
        rows.append({field.name: _cell(item.get(field.name)) for field in fields})
    return fields, rows


def _write_parquet(fields: List[Any], rows: List[Dict[str, Any]], path: str) -> None:
    import duckdb

    columns = ", ".join(f"{_quote(field.name)} {_duck_type(field)}" for field in fields)
    con = duckdb.connect()
    try:
        con.execute(f"CREATE TABLE bronze_export ({columns})")
        if rows:
            placeholders = ", ".join("?" for _ in fields)
            con.executemany(
                f"INSERT INTO bronze_export VALUES ({placeholders})",
                [[row.get(field.name) for field in fields] for row in rows],
            )
        con.execute(f"COPY bronze_export TO '{path.replace(os.sep, '/')}' (FORMAT PARQUET, COMPRESSION SNAPPY)")
    finally:
        con.close()


def _remote_sha(s3: Any, bucket: str, key: str) -> str:
    try:
        head = s3.head_object(Bucket=bucket, Key=key)
    except Exception:
        return ""
    return str((head.get("Metadata") or {}).get("sha256") or "")


def export_tables(bq_client: Any, s3: Any, bucket: str, schema: str, tables: List[str],
                  prefix: str = EXPORT_PREFIX) -> Dict[str, Any]:
    files: List[Dict[str, Any]] = []
    failures: List[str] = []
    exported_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with tempfile.TemporaryDirectory() as tmp:
        for table in tables:
            try:
                fields, rows = _read_rows(bq_client, schema, table)
                path = os.path.join(tmp, f"{table.lower()}.parquet")
                _write_parquet(fields, rows, path)
                with open(path, "rb") as handle:
                    body = handle.read()
                digest = hashlib.sha256(body).hexdigest()
                key = f"{prefix}/{table.lower()}/{table.lower()}.parquet"
                skipped = _remote_sha(s3, bucket, key) == digest
                if not skipped:
                    s3.put_object(
                        Bucket=bucket,
                        Key=key,
                        Body=body,
                        ContentType="application/vnd.apache.parquet",
                        Metadata={"sha256": digest, "rows": str(len(rows)), "source": f"bigquery:{schema}.{table}"},
                    )
                files.append({
                    "dataset": schema,
                    "table": table,
                    "key": key,
                    "rows": len(rows),
                    "bytes": len(body),
                    "sha256": digest,
                    "status": "unchanged" if skipped else "uploaded",
                    "columns": [{"name": f.name, "type": _duck_type(f)} for f in fields],
                })
            except Exception as exc:
                failures.append(f"{table}: {str(exc)[:160]}")

    manifest = {
        "bucket": bucket,
        "prefix": prefix,
        "source": f"bigquery:{schema}",
        "exported_at": exported_at,
        "files": files,
        "failures": failures,
    }
    manifest_body = json.dumps(manifest, indent=2, default=str).encode("utf-8")
    manifest_key = f"{prefix}/_MANIFEST.json"
    s3.put_object(Bucket=bucket, Key=manifest_key, Body=manifest_body,
                  ContentType="application/json",
                  Metadata={"sha256": hashlib.sha256(manifest_body).hexdigest()})
    success_key = f"{prefix}/_SUCCESS"
    if not failures:
        s3.put_object(Bucket=bucket, Key=success_key, Body=exported_at.encode("utf-8"),
                      ContentType="text/plain")

    manifest["manifest_key"] = manifest_key
    manifest["manifest_sha256"] = hashlib.sha256(manifest_body).hexdigest()
    manifest["success_marker"] = success_key if not failures else None
    return manifest


def _markdown(manifest: Dict[str, Any], duration_ms: int) -> str:
    lines = [
        f"### 📦 `{manifest['source']}` → `s3://{manifest['bucket']}/{manifest['prefix']}/`",
        "",
        "| Table | S3 key | Rows | Bytes | SHA-256 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in manifest["files"]:
        mark = "♻️" if item["status"] == "unchanged" else "✅"
        lines.append(
            f"| {mark} `{item['table']}` | `{item['key']}` | {item['rows']} | "
            f"{item['bytes']} | `{item['sha256'][:16]}…` |"
        )
    lines.append("")
    lines.append(f"Manifest: `s3://{manifest['bucket']}/{manifest['manifest_key']}`")
    if manifest["success_marker"]:
        lines.append(f"Marker: `s3://{manifest['bucket']}/{manifest['success_marker']}`")
    if manifest["failures"]:
        lines.append("")
        lines.append("**Failed tables:** " + "; ".join(manifest["failures"]))
    lines.append("")
    lines.append(f"_Completed in {duration_ms} ms._")
    return "\n".join(lines)


def _payload(manifest: Dict[str, Any], markdown: str, started: float) -> Dict[str, Any]:
    duration_ms = round((time.time() - started) * 1000)
    uploaded = sum(1 for item in manifest["files"] if item["status"] == "uploaded")
    unchanged = len(manifest["files"]) - uploaded
    return {
        "status": "success" if (manifest["files"] or not manifest["failures"]) else "error",
        "response": markdown,
        "summary": f"{len(manifest['files'])} tables exported ({uploaded} uploaded, {unchanged} unchanged)"
                   + (f", {len(manifest['failures'])} failed" if manifest["failures"] else ""),
        "message": "",
        "action": "export_s3",
        "data": {
            "bucket": manifest["bucket"],
            "prefix": manifest["prefix"],
            "files": manifest["files"],
            "manifest_key": manifest["manifest_key"],
            "manifest_sha256": manifest["manifest_sha256"],
            "failures": manifest["failures"],
        },
        "model_routed": "nanopro/s3-export",
        "model_executed": "aws/s3-parquet-export",
        "model_name": "NanoPro S3 Parquet Exporter",
        "lab_name": "NanoPro Data Plane",
        "country": "India",
        "flag": "📦",
        "date_formatted": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
        "duration_ms": duration_ms,
        "routing_decision": {
            "selected_model": "nanopro/s3-export",
            "task_domain": "Bronze Parquet export to Amazon S3",
            "sla_target_ms": 60000,
            "sla_met": duration_ms <= 60000,
        },
    }


def run_export() -> Dict[str, Any]:
    started = time.time()
    try:
        client = _bq_client()
        config = _aws_config()
        if not config["bucket"]:
            raise ExportError("AWS_S3_BUCKET is not configured.")
        tables = sorted(item.table_id for item in client.list_tables(BRONZE_SCHEMA))
        if not tables:
            raise ExportError(f"`{BRONZE_SCHEMA}` has no tables to export.")
        manifest = export_tables(client, _s3_client(config), config["bucket"], BRONZE_SCHEMA, tables)
    except ExportError as exc:
        return _error(str(exc), started)
    except Exception as exc:
        return _error(f"{type(exc).__name__}: {str(exc)[:400]}", started)

    duration_ms = round((time.time() - started) * 1000)
    if manifest["failures"] and not manifest["files"]:
        return _error("Export failed: " + "; ".join(manifest["failures"]), started)
    return _payload(manifest, _markdown(manifest, duration_ms), started)


def maybe_handle(prompt: str) -> Optional[Dict[str, Any]]:
    text = (prompt or "").strip()
    if not text:
        return None
    if not (_EXPORT_Q.search(text) and _S3_Q.search(text) and _BRONZE_Q.search(text)):
        return None

    return run_export()


def _error(message: str, started: float) -> Dict[str, Any]:
    return {
        "status": "error",
        "response": f"❌ {message}\n\n**काहीही export झालं नाही.**",
        "summary": message,
        "message": message,
        "action": "export_s3",
        "model_routed": "nanopro/s3-export",
        "model_executed": "aws/s3-parquet-export",
        "model_name": "NanoPro S3 Parquet Exporter",
        "lab_name": "NanoPro Data Plane",
        "country": "India",
        "flag": "📦",
        "duration_ms": round((time.time() - started) * 1000),
    }
