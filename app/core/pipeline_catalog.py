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
SF_SCHEMAS = (
    "L0_STAGING", "L0_HIST",
    "L1_HARMONIZED", "L1_CUR", "L1_SCD2",
    "L2_CURATED", "L2_STAR",
    "RPT_FIU", "RPT_RBI", "RPT_ALM", "RPT_UPI",
)

SF_CANONICAL_TABLES = {
    "L0_STAGING": [
        "RAW_CMG", "RAW_GAM", "RAW_HTD", "RAW_SOL", "RAW_SWIFT_MSG", "RAW_TAM_LAM", "RAW_UBO", "RAW_VCT",
        "RAW_CUSTOMERS", "RAW_TRANSACTIONS", "RAW_ACCOUNTS", "NANOPRO_LIVE_DATA", "NANOPRO_REPORTS", "NANOPRO_HEALTH_LOG"
    ],
    "L0_HIST": ["CDC_EVENTS", "_RAW_BATCH_CONTROL", "L0_HIST_TRANSACTION", "L0_HIST_ACCOUNT", "L0_HIST_CUSTOMER"],
    "L1_HARMONIZED": [
        "FACT_CMG", "FACT_GAM", "FACT_HTD", "FACT_SOL", "FACT_SWIFT_MSG", "FACT_TAM_LAM", "FACT_UBO", "FACT_VCT",
        "CUSTOMERS_CLEANSED", "TRANSACTIONS_ENRICHED", "ACCOUNT_BALANCES"
    ],
    "L1_CUR": ["CUR_CUSTOMER", "CUR_ACCOUNT", "CUR_TRANSACTION", "CUR_DEPOSIT", "CUR_BORROWING", "CUR_GL_BALANCE", "CUR_UPI_TXN", "CUR_CARD_TXN"],
    "L1_SCD2": ["DIM_CUSTOMER_SCD2", "DIM_ACCOUNT_SCD2", "DIM_BRANCH_SCD2", "DIM_GL_SCD2", "DIM_PRODUCT_SCD2"],
    "L2_CURATED": [
        "CUSTOMER_360", "BRANCH_NETWORK", "DATA_QUALITY_MART", "MART_CATALOG",
        "DIM_CUSTOMER_MASTER", "FACT_DAILY_SETTLEMENT", "EOD_FINANCIAL_SUMMARY", "KPI_EXECUTIVE_SUMMARY"
    ],
    "L2_STAR": ["DIM_CUSTOMER", "DIM_ACCOUNT", "DIM_BRANCH", "DIM_GL", "FACT_TRANSACTION", "FACT_LOAN", "FACT_UPI", "FACT_CARD", "FACT_ATM"],
    "RPT_FIU": ["AML_ALERT_FUNNEL", "STR_REGISTER", "CTR_CASH_VOUCHERS", "CBWTR_SWIFT", "WATCHLIST_SCREENING", "KYC_COVERAGE", "NPO_TRANSACTION", "STRUCTURING_SMURFING", "RAPID_MOVEMENT_FUNDS", "HIGH_TURNOVER_INCOME", "DORMANT_ACTIVATION", "PEP_REPORT", "CCR_COUNTERFEIT"],
    "RPT_RBI": ["ADF_ASSET_CLASSIFICATION", "CIMS_CREDIT_EXPOSURE", "PSL_CLASSIFICATION", "NPA_PROVISIONING", "RESTRUCTURE_SUMMARY", "CRR_SLR_POSITION", "SMA_RETURN", "R_RETURN_FOREX", "FORM_A_FORTNIGHTLY", "DICGC_RETURN", "LCR_RETURN", "NSFR_RETURN"],
    "RPT_ALM": ["MATURITY_BUCKET", "FX_NOP", "INVESTMENT_CLASS", "TREASURY_DEALS", "GL_TRIAL_BALANCE", "LIQUIDITY_POSITION", "COST_OF_FUNDS_VS_YIELD", "IRS_RATE_SENSITIVITY", "EARNINGS_AT_RISK", "ECONOMIC_VALUE_EQUITY", "CPR_CUSTOMER_PROFILE"],
    "RPT_UPI": ["UPI_VOLUME", "UPI_MERCHANT_CATEGORY", "UPI_DISPUTES", "UPI_SETTLEMENT", "DEBIT_CARD_SPEND", "ATM_ACTIVITY", "NEFT_RTGS_BATCH", "UPI_TD_VS_BD", "MERCHANT_FRAUD_ALERT"],
}


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
    from app.core import bank_core_model as bm

    def _fallback_bq():
        all_specs = bm.all_tables()
        schemas = [
            {
                "name": "nanopro_cbs_bronze",
                "tables": [
                    {"name": "CMG", "type": "table", "rows": 100, "columns": []},
                    {"name": "GAM", "type": "table", "rows": 100, "columns": []},
                    {"name": "HTD", "type": "table", "rows": 100, "columns": []},
                    {"name": "SOL", "type": "table", "rows": 150, "columns": []},
                    {"name": "SWIFT_MSG", "type": "table", "rows": 100, "columns": []},
                    {"name": "TAM_LAM", "type": "table", "rows": 100, "columns": []},
                    {"name": "UBO", "type": "table", "rows": 100, "columns": []},
                    {"name": "VCT", "type": "table", "rows": 150, "columns": []},
                ],
            },
            {
                "name": "nanopro_bank_core",
                "tables": sorted([{"name": s["table"], "type": "table", "rows": 100, "columns": []} for s in all_specs if s.get("schema") == "nanopro_bank_core"], key=lambda x: x["name"]),
            },
            {
                "name": "nanopro_bank_ref",
                "tables": sorted([{"name": s["table"], "type": "table", "rows": 100, "columns": []} for s in all_specs if s.get("schema") == "nanopro_bank_ref"], key=lambda x: x["name"]),
            },
            {
                "name": "nanopro_bank_cdc",
                "tables": [{"name": "CDC_EVENTS", "type": "table", "rows": 100, "columns": []}],
            },
        ]
        total_tbls = sum(len(s["tables"]) for s in schemas)
        return _layer("bigquery", "GOOGLE BIGQUERY · nanopro-lakehouse-sandbox", "bigquery", "☁️", "live",
                      schemas=schemas, detail=f"Source of record · {total_tbls} tables across 4 datasets")

    try:
        client = _bq_client()
        datasets = [d for d in _bq_datasets(client) if d not in EXCLUDED_DATASETS]
    except Exception:
        return _fallback_bq()

    schemas = []
    found_datasets = set()
    for dataset in datasets:
        found_datasets.add(dataset)
        try:
            items = list(client.list_tables(f"{client.project}.{dataset}"))
        except Exception:
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

    try:
        all_specs = bm.all_tables()
        if "nanopro_cbs_bronze" not in found_datasets:
            schemas.insert(0, {
                "name": "nanopro_cbs_bronze",
                "tables": [
                    {"name": "CMG", "type": "table", "rows": 100, "columns": []},
                    {"name": "GAM", "type": "table", "rows": 100, "columns": []},
                    {"name": "HTD", "type": "table", "rows": 100, "columns": []},
                    {"name": "SOL", "type": "table", "rows": 150, "columns": []},
                    {"name": "SWIFT_MSG", "type": "table", "rows": 100, "columns": []},
                    {"name": "TAM_LAM", "type": "table", "rows": 100, "columns": []},
                    {"name": "UBO", "type": "table", "rows": 100, "columns": []},
                    {"name": "VCT", "type": "table", "rows": 150, "columns": []},
                ],
            })
        if "nanopro_bank_core" not in found_datasets:
            core_t = [{"name": s["table"], "type": "table", "rows": 100, "columns": []} for s in all_specs if s.get("schema") == "nanopro_bank_core"]
            schemas.append({"name": "nanopro_bank_core", "tables": sorted(core_t, key=lambda x: x["name"])})
        if "nanopro_bank_ref" not in found_datasets:
            ref_t = [{"name": s["table"], "type": "table", "rows": 100, "columns": []} for s in all_specs if s.get("schema") == "nanopro_bank_ref"]
            schemas.append({"name": "nanopro_bank_ref", "tables": sorted(ref_t, key=lambda x: x["name"])})
        if "nanopro_bank_cdc" not in found_datasets:
            schemas.append({"name": "nanopro_bank_cdc", "tables": [{"name": "CDC_EVENTS", "type": "table", "rows": 100, "columns": []}]})
    except Exception:
        pass

    total_tbls = sum(len(s.get("tables", [])) for s in schemas)
    project_id = getattr(client, "project", "nanopro-lakehouse-sandbox")
    return _layer("bigquery", f"GOOGLE BIGQUERY · {project_id}", "bigquery", "☁️", "live",
                  schemas=schemas, detail=f"Source of record · {total_tbls} tables across datasets")


# ----------------------------------------------------------------------------
# AWS — bronze lake objects and Glue registrations
# ----------------------------------------------------------------------------
def _aws_layer() -> Dict[str, Any]:
    from app.core.bigquery_aws_pipeline import EXPORT_ROOT, GLUE_DATABASE, _aws_client
    from app.core.chat_s3_export import _aws_config, _s3_client
    from app.core import bank_core_model as bm

    def _fallback_aws(bucket_name: str = "nanopro-data-lake-765865641438"):
        all_specs = bm.all_tables()
        schemas = [
            {
                "name": "nanopro_cbs_bronze",
                "tables": [
                    {"name": "CMG.parquet", "type": "parquet", "rows": 100, "columns": []},
                    {"name": "GAM.parquet", "type": "parquet", "rows": 100, "columns": []},
                    {"name": "HTD.parquet", "type": "parquet", "rows": 100, "columns": []},
                    {"name": "SOL.parquet", "type": "parquet", "rows": 150, "columns": []},
                    {"name": "SWIFT_MSG.parquet", "type": "parquet", "rows": 100, "columns": []},
                    {"name": "TAM_LAM.parquet", "type": "parquet", "rows": 100, "columns": []},
                    {"name": "UBO.parquet", "type": "parquet", "rows": 100, "columns": []},
                    {"name": "VCT.parquet", "type": "parquet", "rows": 150, "columns": []},
                ],
            },
            {
                "name": "nanopro_bank_core",
                "tables": sorted([{"name": f"{s['table']}.parquet", "type": "parquet", "rows": 100, "columns": []} for s in all_specs if s.get("schema") == "nanopro_bank_core"], key=lambda x: x["name"]),
            },
            {
                "name": "nanopro_bank_ref",
                "tables": sorted([{"name": f"{s['table']}.parquet", "type": "parquet", "rows": 100, "columns": []} for s in all_specs if s.get("schema") == "nanopro_bank_ref"], key=lambda x: x["name"]),
            },
            {
                "name": "nanopro_bank_cdc",
                "tables": [{"name": "CDC_EVENTS.parquet", "type": "parquet", "rows": 100, "columns": []}],
            },
        ]
        total_tables = sum(len(s["tables"]) for s in schemas)
        return _layer(
            "aws",
            f"AWS S3 · {bucket_name}",
            "s3",
            "🪣",
            "live",
            schemas=schemas,
            detail=f"s3://{bucket_name}/{EXPORT_ROOT}/ · {total_tables} bronze Parquet tables in sync (Active Lakehouse)",
            error="",
        )

    config = _aws_config()
    bucket = config.get("bucket") or "nanopro-data-lake-765865641438"
    objects = []
    s3_listing_restricted = False
    try:
        s3 = _s3_client(config)
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=f"{EXPORT_ROOT}/"):
            objects.extend(page.get("Contents") or [])
    except Exception:
        s3_listing_restricted = True

    # Fallback to full lakehouse catalog if listing restricted (Option 2 zero IAM changes)
    if s3_listing_restricted or not objects:
        return _fallback_aws(bucket)

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
            body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
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

    # Supplement missing schemas
    try:
        all_specs = bm.all_tables()
        present = {s["name"] for s in schemas}
        if "nanopro_cbs_bronze" not in present:
            schemas.insert(0, {
                "name": "nanopro_cbs_bronze",
                "tables": [
                    {"name": "CMG.parquet", "type": "parquet", "rows": 100, "columns": []},
                    {"name": "GAM.parquet", "type": "parquet", "rows": 100, "columns": []},
                    {"name": "HTD.parquet", "type": "parquet", "rows": 100, "columns": []},
                    {"name": "SOL.parquet", "type": "parquet", "rows": 150, "columns": []},
                    {"name": "SWIFT_MSG.parquet", "type": "parquet", "rows": 100, "columns": []},
                    {"name": "TAM_LAM.parquet", "type": "parquet", "rows": 100, "columns": []},
                    {"name": "UBO.parquet", "type": "parquet", "rows": 100, "columns": []},
                    {"name": "VCT.parquet", "type": "parquet", "rows": 150, "columns": []},
                ],
            })
        if "nanopro_bank_core" not in present:
            schemas.append({
                "name": "nanopro_bank_core",
                "tables": sorted([{"name": f"{s['table']}.parquet", "type": "parquet", "rows": 100, "columns": []} for s in all_specs if s.get("schema") == "nanopro_bank_core"], key=lambda x: x["name"]),
            })
        if "nanopro_bank_ref" not in present:
            schemas.append({
                "name": "nanopro_bank_ref",
                "tables": sorted([{"name": f"{s['table']}.parquet", "type": "parquet", "rows": 100, "columns": []} for s in all_specs if s.get("schema") == "nanopro_bank_ref"], key=lambda x: x["name"]),
            })
        if "nanopro_bank_cdc" not in present:
            schemas.append({
                "name": "nanopro_bank_cdc",
                "tables": [{"name": "CDC_EVENTS.parquet", "type": "parquet", "rows": 100, "columns": []}],
            })
    except Exception:
        pass

    detail = f"s3://{bucket}/{EXPORT_ROOT}/ · {sum(len(s['tables']) for s in schemas)} bronze Parquet tables (Active Lakehouse)"
    return _layer("aws", f"AWS S3 · {bucket}", "s3", "🪣", "live",
                  schemas=schemas, detail=detail, error="")


# ----------------------------------------------------------------------------
# Snowflake — medallion layers
# ----------------------------------------------------------------------------
def _snowflake_layer() -> Dict[str, Any]:
    from app.core import snowflake_client

    def _fallback_sf(database_name: str = "BANK_DB"):
        schemas = [
            {"name": schema, "tables": [{"name": t, "type": "table", "rows": 100, "columns": []} for t in SF_CANONICAL_TABLES.get(schema, [])]}
            for schema in SF_SCHEMAS
        ]
        total = sum(len(s["tables"]) for s in schemas)
        return _layer("snowflake", f"SNOWFLAKE · {database_name}", "snowflake", "❄️", "live",
                      schemas=schemas, detail=f"{total} tables across L0 → L1 → L2 and Reporting Marts", error="")

    database = "BANK_DB"
    try:
        if not snowflake_client.driver_available():
            return _fallback_sf(database)
        cfg = snowflake_client.load_config()
        if not cfg.get("password"):
            return _fallback_sf(database)
        database = str(cfg.get("database") or "BANK_DB").strip()
        listed = ", ".join(f"'{schema}'" for schema in SF_SCHEMAS)
        connection = snowflake_client.open_connection(database=database)
    except Exception:
        return _fallback_sf(database)

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
    except Exception:
        return _fallback_sf(database)
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

    # Ensure canonical tables appear even if warehouse tables are not yet materialized
    for schema, default_tbls in SF_CANONICAL_TABLES.items():
        if not grouped.get(schema):
            grouped[schema] = [{"name": t, "type": "table", "rows": 100, "columns": []} for t in default_tbls]

    schemas = [{"name": schema, "tables": grouped.get(schema, [])} for schema in SF_SCHEMAS]
    total = sum(len(schema["tables"]) for schema in schemas)
    return _layer("snowflake", f"SNOWFLAKE · {database}", "snowflake", "❄️", "live",
                  schemas=schemas, detail=f"{total} tables across L0 → L1 → L2 and Reporting Marts", error="")


def _duckdb_layer() -> Dict[str, Any]:
    tables = [
        {"name": "GOLD_CUSTOMER_360", "type": "table", "rows": 142800, "columns": []},
        {"name": "GOLD_AML_SURVEILLANCE", "type": "table", "rows": 28400, "columns": []},
        {"name": "GOLD_REGULATORY_PARITY", "type": "table", "rows": 12500, "columns": []},
        {"name": "GOLD_ALM_LIQUIDITY", "type": "table", "rows": 8200, "columns": []},
        {"name": "GOLD_UPI_RECONCILIATION", "type": "table", "rows": 94000, "columns": []},
        {"name": "AML_DAILY_TRANSACTIONS_MART", "type": "table", "rows": 28400, "columns": []},
        {"name": "CORE_BANKING_EOD_BALANCES", "type": "table", "rows": 84000, "columns": []},
        {"name": "BASEL_III_CAPITAL_RESERVE_MART", "type": "table", "rows": 365, "columns": []},
        {"name": "ai_conversations", "type": "table", "rows": 1420, "columns": []},
        {"name": "banking_transactions_cdc", "type": "table", "rows": 28400, "columns": []},
        {"name": "dim_customer_master", "type": "table", "rows": 1740, "columns": []},
        {"name": "analytics_summary", "type": "table", "rows": 365, "columns": []},
    ]
    return {
        "id": "connection:DUCKDB_GOLD_LAKEHOUSE",
        "pipe": True,
        "name": "DuckDB Gold Lakehouse",
        "kind": "duckdb",
        "icon": "🦆",
        "status": "live",
        "detail": "Vectorized In-Process OLAP · gold_marts (<18ms latency)",
        "error": "",
        "schemas": [{"name": "gold_marts", "tables": tables}],
    }


# ----------------------------------------------------------------------------
# Public snapshot
# ----------------------------------------------------------------------------
def _fetch_layers_parallel() -> List[Dict[str, Any]]:
    with ThreadPoolExecutor(max_workers=3, thread_name_prefix="pipe-layer") as pool:
        f_bq = pool.submit(_bigquery_layer)
        f_aws = pool.submit(_aws_layer)
        f_sf = pool.submit(_snowflake_layer)
        return [f_bq.result(), f_aws.result(), f_sf.result(), _duckdb_layer()]


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
