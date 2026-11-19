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

import json
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.logger import log_event

from concurrent.futures import ThreadPoolExecutor

CACHE_TTL_S = 180.0
_CACHE: Dict[str, Any] = {"at": 0.0, "value": None}
_LOCK = threading.Lock()
_REFRESHING = False
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

    schemas = []
    for dataset in datasets:
        try:
            items = list(client.list_tables(f"{client.project}.{dataset}"))
        except Exception as exc:
            schemas.append({"name": dataset, "tables": [], "error": str(exc)[:160]})
            continue
        row_counts: Dict[str, int] = {}
        try:
            query = f"SELECT table_id, row_count FROM `{client.project}.{dataset}.__TABLES__`"
            for row in client.query(query).result(timeout=4.0):
                row_counts[str(row.table_id)] = int(row.row_count or 0)
        except Exception:
            pass
        tables = []
        for item in items:
            t_id = item.table_id
            rows = row_counts.get(t_id, 0)
            t_type = "view" if getattr(item, "table_type", "") == "VIEW" else "table"
            tables.append({
                "name": t_id,
                "type": t_type,
                "rows": rows,
                "columns": [],
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
                      detail=f"s3://{config['bucket']}/{EXPORT_ROOT}/",
                      error=f"S3 listing failed: {str(exc)[:200]}")

    # Each dataset publishes _MANIFEST.json next to its Parquet files; it is the
    # authoritative per-table row count and column list for that export.
    manifest_keys: Dict[str, str] = {}
    for obj in objects:
        key = str(obj.get("Key") or "")
        parts = key.split("/")
        if len(parts) == 4 and parts[-1] == "_MANIFEST.json":
            manifest_keys[parts[2]] = key

    dataset_rows: Dict[str, Dict[str, int]] = {}
    dataset_columns: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for dataset, key in manifest_keys.items():
        try:
            body = s3.get_object(Bucket=config["bucket"], Key=key)["Body"].read()
            manifest = json.loads(body)
        except Exception:
            continue
        rows_map: Dict[str, int] = {}
        columns_map: Dict[str, List[Dict[str, Any]]] = {}
        for item in manifest.get("files") or []:
            name = str(item.get("table") or "").upper()
            if not name:
                continue
            rows_map[name] = int(item.get("rows") or 0)
            columns_map[name] = [_column(col.get("name"), col.get("type"))
                                 for col in item.get("columns") or []]
        dataset_rows[dataset] = rows_map
        dataset_columns[dataset] = columns_map

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
                "rows": dataset_rows.get(dataset, {}).get(table.upper(), 0),
                "bytes": size,
                "key": key,
                "columns": list(dataset_columns.get(dataset, {}).get(table.upper()) or []),
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
            glue_entry = (glue_tables.get(table["name"].upper())
                          or glue_tables.get(f"{dataset}__{table['name']}".upper()) or {})
            glue_columns = glue_entry.get("columns") or []
            if glue_columns:
                table["columns"] = glue_columns
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
def _fetch_layers_parallel() -> List[Dict[str, Any]]:
    with ThreadPoolExecutor(max_workers=3, thread_name_prefix="pipe-layer") as pool:
        f_bq = pool.submit(_bigquery_layer)
        f_aws = pool.submit(_aws_layer)
        f_sf = pool.submit(_snowflake_layer)
        return [f_bq.result(), f_aws.result(), f_sf.result()]


def _background_refresh() -> None:
    global _REFRESHING
    try:
        layers = _fetch_layers_parallel()
        value = {
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "cached": False,
            "layers": layers,
        }
        with _LOCK:
            _CACHE.update({"at": time.time(), "value": value})
        log_event(
            "Pipeline catalog background refreshed: " + ", ".join(f"{l['kind']}={l['status']}" for l in value["layers"]),
            component="PipelineCatalog",
        )
    except Exception as exc:
        log_event(f"Pipeline catalog background refresh error: {exc}", level="WARNING", component="PipelineCatalog")
    finally:
        _REFRESHING = False


def snapshot(force: bool = False) -> Dict[str, Any]:
    global _REFRESHING
    now = time.time()
    with _LOCK:
        cached = _CACHE.get("value")
        age = now - _CACHE.get("at", 0.0)

        # 1. Fresh cache hit (< 180s)
        if not force and cached is not None and age < CACHE_TTL_S:
            c = dict(cached)
            c["cached"] = True
            return c

        # 2. Stale cache: return immediately and refresh in background
        if not force and cached is not None:
            if not _REFRESHING:
                _REFRESHING = True
                threading.Thread(target=_background_refresh, daemon=True, name="pipe-catalog-bg").start()
            c = dict(cached)
            c["cached"] = True
            return c

        # 3. Cold start: fetch in parallel
        layers = _fetch_layers_parallel()
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
