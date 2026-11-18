"""Live three-layer catalog for the NanoPro pipeline.

One read-only snapshot of every layer the data actually passes through:

* ``BIGQUERY``   – the source of record (CBS core-banking dataset)
* ``AWS``        – bronze Parquet objects in S3 plus the Glue registrations
* ``SNOWFLAKE``  – BANK_DB medallion schemas L0_STAGING / L1_HARMONIZED / L2_CURATED

Names are read live from the services themselves, so the Explorer can never
show a table that does not exist. Row counts are the engines' own metadata or
the last pipeline manifest; nothing is estimated or invented.
"""
from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.logger import log_event

CACHE_TTL_S = 60.0
_CACHE: Dict[str, Any] = {"at": 0.0, "value": None}
_LOCK = threading.Lock()
SF_SCHEMAS = ("L0_STAGING", "L1_HARMONIZED", "L2_CURATED")


def _layer(key: str, name: str, kind: str, icon: str, status: str,
           schemas: Optional[List[Dict[str, Any]]] = None,
           detail: str = "", error: str = "") -> Dict[str, Any]:
    return {
        "id": f"pipe_{key}",
        "pipe": True,
        "name": name,
        "kind": kind,
        "icon": icon,
        "status": status,
        "detail": detail,
        "error": error,
        "schemas": schemas or [],
    }


def _column(name: str, dtype: str = "") -> Dict[str, Any]:
    return {"name": str(name), "type": str(dtype or ""), "key": ""}


def _exported_rows() -> Dict[str, int]:
    from app.core.bigquery_aws_pipeline import last_run

    rows: Dict[str, int] = {}
    for item in last_run().get("tables") or []:
        table = str(item.get("table") or "").upper()
        if table:
            rows[table] = int(item.get("rows") or 0)
    return rows


# ----------------------------------------------------------------------------
# BigQuery — source of record
# ----------------------------------------------------------------------------
def _bigquery_layer() -> Dict[str, Any]:
    from app.core.bigquery_aws_pipeline import EXCLUDED_DATASETS, _bq_datasets
    from app.core.chat_s3_export import _bq_client

    try:
        client = _bq_client()
        datasets = [d for d in _bq_datasets(client) if d not in EXCLUDED_DATASETS]
    except Exception as exc:
        return _layer("bigquery", "GOOGLE BIGQUERY · source", "bigquery", "☁️",
                      "error", error=f"BigQuery unavailable: {str(exc)[:200]}")

    manifest_rows = _exported_rows()
    schemas = []
    for dataset in datasets:
        try:
            items = list(client.list_tables(f"{client.project}.{dataset}"))
        except Exception as exc:
            schemas.append({"name": dataset, "tables": [], "error": str(exc)[:160]})
            continue
        tables = []
        for item in items:
            columns: List[Dict[str, Any]] = []
            rows: Optional[int] = None
            try:
                meta = client.get_table(item.reference)
                columns = [_column(field.name, field.field_type) for field in meta.schema]
                rows = int(meta.num_rows or 0)
            except Exception:
                pass
            tables.append({
                "name": item.table_id,
                "type": "table",
                "rows": rows if rows is not None else manifest_rows.get(item.table_id.upper(), 0),
                "columns": columns,
            })
        tables.sort(key=lambda entry: entry["name"])
        schemas.append({"name": dataset, "tables": tables})

    return _layer("bigquery", f"GOOGLE BIGQUERY · {client.project}", "bigquery", "☁️", "live",
                  schemas=schemas, detail="Source of record · dataset(s): " + ", ".join(datasets))


# ----------------------------------------------------------------------------
# AWS — bronze lake objects and Glue registrations
# ----------------------------------------------------------------------------
def _aws_layer() -> Dict[str, Any]:
    from app.core.bigquery_aws_pipeline import EXPORT_ROOT, GLUE_DATABASE, _aws_client
    from app.core.chat_s3_export import _aws_config, _s3_client

    config = _aws_config()
    if not config.get("bucket"):
        return _layer("aws", "AWS · bronze lake", "s3", "🪣", "error",
                      error="AWS_S3_BUCKET is not configured.")
    try:
        s3 = _s3_client(config)
        paginator = s3.get_paginator("list_objects_v2")
        objects = []
        for page in paginator.paginate(Bucket=config["bucket"], Prefix=f"{EXPORT_ROOT}/"):
            objects.extend(page.get("Contents") or [])
    except Exception as exc:
        return _layer("aws", f"AWS S3 · {config['bucket']}", "s3", "🪣", "error",
                      error=f"S3 listing failed: {str(exc)[:200]}")

    manifest_rows = _exported_rows()
    by_dataset: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for obj in objects:
        key = str(obj.get("Key") or "")
        parts = key.split("/")
        if len(parts) < 5:
            continue
        dataset, table, filename = parts[2], parts[3], parts[-1]
        if filename.startswith("_") and not filename.endswith(".parquet"):
            continue
        prev = by_dataset.setdefault(dataset, {}).get(table)
        size = int(obj.get("Size") or 0)
        if prev is None or size > int(prev.get("size") or 0):
            by_dataset[dataset][table] = {
                "name": table,
                "type": filename.rsplit(".", 1)[-1] if "." in filename else "object",
                "rows": manifest_rows.get(table.upper(), 0),
                "bytes": size,
                "key": key,
                "columns": [],
            }

    glue_tables: Dict[str, Dict[str, Any]] = {}
    glue_error = ""
    try:
        glue = _aws_client(config, "glue")
        for item in glue.get_tables(DatabaseName=GLUE_DATABASE).get("TableList") or []:
            name = str(item.get("Name") or "")
            storage = item.get("StorageDescriptor") or {}
            glue_tables[name.upper()] = {
                "columns": [_column(col.get("Name"), col.get("Type")) for col in storage.get("Columns") or []],
                "location": storage.get("Location") or "",
            }
    except Exception as exc:
        glue_error = f"Glue catalog unavailable: {str(exc)[:160]}"

    schemas = []
    for dataset, tables in sorted(by_dataset.items()):
        for table in tables.values():
            glue_entry = glue_tables.get(table["name"].upper()) or {}
            table["columns"] = glue_entry.get("columns") or []
            if not table["columns"]:
                table["columns"] = [_column("parquet schema registered in Glue", "parquet")] if glue_entry else []
        schemas.append({"name": dataset, "tables": sorted(tables.values(), key=lambda entry: entry["name"])})

    detail = f"s3://{config['bucket']}/{EXPORT_ROOT}/ · {len(objects)} objects"
    if glue_error:
        detail += " · " + glue_error
    else:
        detail += f" · Glue db {GLUE_DATABASE}: {len(glue_tables)} table(s)"
    status = "live" if not glue_error else "partial"
    return _layer("aws", f"AWS S3 · {config['bucket']}", "s3", "🪣", status,
                  schemas=schemas, detail=detail, error=glue_error)


# ----------------------------------------------------------------------------
# Snowflake — medallion layers
# ----------------------------------------------------------------------------
def _snowflake_layer() -> Dict[str, Any]:
    from app.core import snowflake_client

    if not snowflake_client.driver_available():
        return _layer("snowflake", "SNOWFLAKE · BANK_DB", "snowflake", "❄️", "error",
                      error="snowflake-connector-python is not installed.")
    cfg = snowflake_client.load_config()
    if not cfg.get("password"):
        return _layer("snowflake", "SNOWFLAKE · BANK_DB", "snowflake", "❄️", "error",
                      error="Snowflake password is not in the Credential Vault.")
    database = str(cfg.get("database") or "BANK_DB").strip()
    listed = ", ".join(f"'{schema}'" for schema in SF_SCHEMAS)
    try:
        connection = snowflake_client.open_connection(database=database)
    except Exception as exc:
        return _layer("snowflake", f"SNOWFLAKE · {database}", "snowflake", "❄️", "error",
                      error=f"Snowflake connect failed: {str(exc)[:200]}")

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT TABLE_SCHEMA, TABLE_NAME, ROW_COUNT FROM INFORMATION_SCHEMA.TABLES "
            f"WHERE TABLE_SCHEMA IN ({listed}) ORDER BY TABLE_SCHEMA, TABLE_NAME"
        )
        table_rows = cursor.fetchall()
        cursor.execute(
            "SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS "
            f"WHERE TABLE_SCHEMA IN ({listed}) ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION"
        )
        column_rows = cursor.fetchall()
    except Exception as exc:
        return _layer("snowflake", f"SNOWFLAKE · {database}", "snowflake", "❄️", "error",
                      error=f"Metadata query failed: {str(exc)[:200]}")
    finally:
        try:
            connection.close()
        except Exception:
            pass

    columns: Dict[tuple, List[Dict[str, Any]]] = {}
    for schema_name, table_name, column_name, data_type in column_rows:
        columns.setdefault((schema_name, table_name), []).append(_column(column_name, data_type))

    grouped: Dict[str, List[Dict[str, Any]]] = {schema: [] for schema in SF_SCHEMAS}
    for schema_name, table_name, row_count in table_rows:
        grouped.setdefault(schema_name, []).append({
            "name": table_name,
            "type": "table",
            "rows": int(row_count or 0),
            "columns": columns.get((schema_name, table_name), []),
        })

    schemas = [{"name": schema, "tables": grouped.get(schema, [])} for schema in SF_SCHEMAS]
    total = sum(len(schema["tables"]) for schema in schemas)
    return _layer("snowflake", f"SNOWFLAKE · {database}", "snowflake", "❄️", "live",
                  schemas=schemas, detail=f"{total} tables across L0 → L1 → L2")


# ----------------------------------------------------------------------------
# Public snapshot
# ----------------------------------------------------------------------------
def snapshot(force: bool = False) -> Dict[str, Any]:
    now = time.time()
    with _LOCK:
        if not force and _CACHE["value"] is not None and now - _CACHE["at"] < CACHE_TTL_S:
            cached = dict(_CACHE["value"])
            cached["cached"] = True
            return cached
        layers = [_bigquery_layer(), _aws_layer(), _snowflake_layer()]
        value = {
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "cached": False,
            "layers": layers,
        }
        _CACHE.update({"at": now, "value": value})
    log_event(
        "Pipeline catalog refreshed: " + ", ".join(f"{l['kind']}={l['status']}" for l in value["layers"]),
        component="PipelineCatalog",
    )
    return value
