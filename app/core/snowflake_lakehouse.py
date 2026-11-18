"""BigQuery → S3 → Snowflake layered load (L0 bronze, L1 silver, L2 gold).

The bronze Parquet exports in S3 are the only source: L0 stores them raw with
audit columns, L1 harmonises (trim, type, exact-duplicate removal) and L2 keeps
a quality mart per table. Business marts hang off L2 once column semantics are
confirmed; nothing here fabricates metrics it cannot compute from the data.
"""
from __future__ import annotations

import io
import os
from typing import Any, Dict, List, Optional

from app.core.logger import log_event

L0_SCHEMA = "L0_STAGING"
L1_SCHEMA = "L1_HARMONIZED"
L2_SCHEMA = "L2_CURATED"
WAREHOUSE = "COMPUTE_WH"
AUDIT_COLUMNS = ("_RUN_ID", "_LOADED_AT", "_SOURCE_KEY")


def _enabled() -> bool:
    return (os.environ.get("NANOPRO_SNOWFLAKE_SYNC") or "1").strip().lower() not in ("0", "false", "no", "off")


def _sf_type(arrow_type: Any) -> str:
    import pyarrow as pa

    if pa.types.is_boolean(arrow_type):
        return "BOOLEAN"
    if pa.types.is_integer(arrow_type):
        return "NUMBER(38,0)"
    if pa.types.is_floating(arrow_type):
        return "FLOAT"
    if pa.types.is_decimal(arrow_type):
        return f"NUMBER({arrow_type.precision},{arrow_type.scale})"
    if pa.types.is_timestamp(arrow_type):
        return "TIMESTAMP_NTZ"
    if pa.types.is_date(arrow_type):
        return "DATE"
    if pa.types.is_time(arrow_type):
        return "TIME"
    if pa.types.is_binary(arrow_type):
        return "BINARY"
    return "VARCHAR"


def _lit(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("\\", "\\\\").replace("'", "''")
    return f"'{text}'"


def _connect():
    from app.core import snowflake_client

    if not snowflake_client.driver_available():
        raise RuntimeError("snowflake-connector-python is not installed.")
    config = snowflake_client.load_config()
    if not config.get("password"):
        raise RuntimeError("Snowflake password is not present in the Credential Vault.")
    connection = snowflake_client.open_connection()
    cursor = connection.cursor()
    cursor.execute(f"CREATE WAREHOUSE IF NOT EXISTS {WAREHOUSE} WITH WAREHOUSE_SIZE = 'XSMALL' "
                   "AUTO_SUSPEND = 60 AUTO_RESUME = TRUE INITIALLY_SUSPENDED = TRUE")
    cursor.execute(f"USE WAREHOUSE {WAREHOUSE}")
    return connection


def _ensure_layers(cursor, database: str) -> None:
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    for schema in (L0_SCHEMA, L1_SCHEMA, L2_SCHEMA):
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {database}.{schema}")


def _load_l0(connection, cursor, database: str, config: Dict[str, str], files: List[Dict[str, Any]], run_id: str) -> Dict[str, Any]:
    import boto3
    import pyarrow.parquet as pq

    s3 = boto3.client(
        "s3",
        region_name=config["region"],
        aws_access_key_id=config["access_key"],
        aws_secret_access_key=config["secret_key"],
    )
    loaded, rows_total, errors = [], 0, []
    for item in files:
        key = str(item.get("key") or "")
        table = str(item.get("table") or "").upper()
        if not key or not table:
            continue
        try:
            body = s3.get_object(Bucket=config["bucket"], Key=key)["Body"].read()
            arrow = pq.read_table(io.BytesIO(body))
            columns = list(arrow.schema.names)
            ddl_cols = [f'"{name}" {_sf_type(arrow.schema.field(name).type)}' for name in columns]
            ddl_cols += [f'"{c}" ' + ("TIMESTAMP_NTZ" if c == "_LOADED_AT" else "VARCHAR") for c in AUDIT_COLUMNS]
            fqtn = f"{database}.{L0_SCHEMA}.{table}"
            cursor.execute(f"CREATE OR REPLACE TABLE {fqtn} ({', '.join(ddl_cols)})")

            rows = arrow.to_pylist()
            if rows:
                col_list = ", ".join(f'"{c}"' for c in columns)
                value_cols = ", ".join(["%s"] * len(columns))
                value_rows = ", ".join(
                    "(" + ", ".join(["%s"] * (len(columns) + 2)) + ")" for _ in rows
                )
                # _LOADED_AT comes from the warehouse clock, so it is evaluated server-side.
                insert = (
                    f'INSERT INTO {fqtn} ({col_list}, "_RUN_ID", "_LOADED_AT", "_SOURCE_KEY") '
                    f"SELECT {value_cols}, %s, CURRENT_TIMESTAMP(), %s FROM VALUES {value_rows}"
                )
                flat: List[Any] = []
                for row in rows:
                    flat.extend(row.get(name) for name in columns)
                    flat.append(run_id)
                    flat.append(key)
                cursor.execute(insert, flat)
            connection.commit()
            loaded.append(table)
            rows_total += len(rows)
        except Exception as exc:
            errors.append(f"{table}: {str(exc)[:180]}")
    return {"tables": loaded, "rows": rows_total, "errors": errors}


def _build_l1(cursor, database: str, tables: List[str]) -> Dict[str, Any]:
    built, errors = [], []
    for table in tables:
        try:
            fq_l0 = f"{database}.{L0_SCHEMA}.{table}"
            fq_l1 = f"{database}.{L1_SCHEMA}.{table}"
            cursor.execute(f"SELECT * FROM {fq_l0} LIMIT 0")
            columns = [d[0] for d in cursor.description if d[0] not in AUDIT_COLUMNS]
            cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM {database}.INFORMATION_SCHEMA.COLUMNS "
                           f"WHERE TABLE_SCHEMA = '{L0_SCHEMA}' AND TABLE_NAME = '{table}'")
            types = {name: dtype for name, dtype in cursor.fetchall()}
            projected = []
            for name in columns:
                if str(types.get(name, "")).upper() == "VARCHAR":
                    projected.append(f'NULLIF(TRIM("{name}"), \'\') AS "{name}"')
                else:
                    projected.append(f'"{name}"')
            cursor.execute(
                f"CREATE OR REPLACE TABLE {fq_l1} AS "
                f"SELECT DISTINCT {', '.join(projected)} FROM {fq_l0}"
            )
            built.append(table)
        except Exception as exc:
            errors.append(f"{table}: {str(exc)[:180]}")
    return {"tables": built, "errors": errors}


def _build_l2(cursor, database: str, tables: List[str]) -> Dict[str, Any]:
    rows = []
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {database}.{L0_SCHEMA}.{table}")
            l0_count = int((cursor.fetchone() or [0])[0] or 0)
            cursor.execute(f"SELECT COUNT(*) FROM {database}.{L1_SCHEMA}.{table}")
            l1_count = int((cursor.fetchone() or [0])[0] or 0)
            rows.append((table, l0_count, l1_count, l0_count - l1_count))
        except Exception:
            rows.append((table, None, None, None))
    fq = f"{database}.{L2_SCHEMA}.DATA_QUALITY_MART"
    cursor.execute(
        f"CREATE OR REPLACE TABLE {fq} ("
        "TABLE_NAME VARCHAR(120), L0_ROWS NUMBER(38,0), L1_ROWS NUMBER(38,0), "
        "DUPLICATES_REMOVED NUMBER(38,0), MEASURED_AT TIMESTAMP_NTZ)"
    )
    if rows:
        values = ", ".join(
            f"({_lit(t)}, {('NULL' if a is None else a)}, {('NULL' if b is None else b)}, "
            f"{('NULL' if c is None else c)}, CURRENT_TIMESTAMP())"
            for t, a, b, c in rows
        )
        cursor.execute(f"INSERT INTO {fq} VALUES {values}")
    return {"mart": f"{database}.{L2_SCHEMA}.DATA_QUALITY_MART", "tables": len(rows)}


def sync(files: Optional[List[Dict[str, Any]]] = None, run_id: str = "") -> Dict[str, Any]:
    """Load the S3 bronze files into Snowflake L0, harmonise into L1, publish L2."""
    if not _enabled():
        return {"status": "skipped", "reason": "NANOPRO_SNOWFLAKE_SYNC is off"}
    if not files:
        return {"status": "skipped", "reason": "no exported tables"}

    from app.core.chat_s3_export import _aws_config
    from app.core import snowflake_client

    config = _aws_config()
    database = str(snowflake_client.load_config().get("database") or "BANK_DB").strip()
    try:
        connection = _connect()
    except Exception as exc:
        return {"status": "unavailable", "error": str(exc)[:240]}

    try:
        cursor = connection.cursor()
        _ensure_layers(cursor, database)
        l0 = _load_l0(connection, cursor, database, config, files, run_id or "manual")
        l1 = _build_l1(cursor, database, l0["tables"])
        l2 = _build_l2(cursor, database, l0["tables"]) if l0["tables"] else {"tables": 0}
        connection.commit()
        result: Dict[str, Any] = {
            "status": "synced" if l0["tables"] and not l0["errors"] and not l1["errors"] else "partial",
            "database": database,
            "run_id": run_id,
            "l0": {"tables": len(l0["tables"]), "rows": l0["rows"]},
            "l1": {"tables": len(l1["tables"])},
            "l2": l2,
        }
        errors = l0["errors"] + l1["errors"]
        if errors:
            result["errors"] = errors[:5]
        log_event(f"Snowflake sync {run_id}: L0 {result['l0']}, L1 {result['l1']}, L2 {l2}", component="SnowflakeLakehouse")
        return result
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:240]}
    finally:
        try:
            connection.close()
        except Exception:
            pass
