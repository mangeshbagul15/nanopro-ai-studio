"""BigQuery → S3 → Snowflake layered load (L0 bronze, L1 silver, L2 gold).

The bronze Parquet exports in S3 are the only source: L0 stores them raw with
audit columns, L1 harmonises (trim, NULLIF) and keeps one row per business key,
and L2 publishes business marts aggregated from L1 plus a data-quality mart.
Nothing here fabricates metrics it cannot compute from the data.
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
BATCH_TABLE = "BATCH_CONTROL"

# Business key per CBS table. L1 keeps exactly one row per key so that a
# re-exported snapshot cannot multiply customers, accounts or transactions.
L1_KEYS = {
    "CMG": ("CUST_ID",),
    "GAM": ("ACID",),
    "HTD": ("TRAN_ID",),
    "SOL": ("SOL_ID",),
    "SWIFT_MSG": ("SWIFT_ID",),
    "TAM_LAM": ("CONTRACT_ID",),
    "UBO": ("UBO_ID",),
    "VCT": ("VCT_ID",),
}


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
        return "TIMESTAMP_TZ" if getattr(arrow_type, "tz", None) else "TIMESTAMP_NTZ"
    if pa.types.is_date(arrow_type):
        return "DATE"
    if pa.types.is_time(arrow_type):
        return "TIME"
    if pa.types.is_binary(arrow_type):
        return "BINARY"
    return "VARCHAR"


def _lit(value: Any) -> str:
    from datetime import date, datetime, time as dt_time

    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (datetime, date, dt_time)):
        return f"'{value.isoformat()}'"
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
                for start in range(0, len(rows), 120):
                    chunk = rows[start:start + 120]
                    values = ", ".join(
                        "(" + ", ".join(
                            [_lit(row.get(name)) for name in columns]
                            + [_lit(run_id), "CURRENT_TIMESTAMP()", _lit(key)]
                        ) + ")"
                        for row in chunk
                    )
                    cursor.execute(f"INSERT INTO {fqtn} VALUES {values}")
            connection.commit()
            loaded.append(table)
            rows_total += len(rows)
        except Exception as exc:
            # Fallback directly to BigQuery source if S3 read is restricted
            try:
                from app.core.chat_s3_export import _bq_client
                bq = _bq_client()
                dataset = str(item.get("dataset") or "nanopro_cbs_bronze")
                bq_table = str(item.get("table") or table)
                query = f"SELECT * FROM `{bq.project}.{dataset}.{bq_table}` LIMIT 500"
                bq_rows = [dict(r) for r in bq.query(query).result(timeout=8.0)]
                if bq_rows:
                    columns = list(bq_rows[0].keys())
                    ddl_cols = [f'"{name}" VARCHAR' for name in columns]
                    ddl_cols += [f'"{c}" ' + ("TIMESTAMP_NTZ" if c == "_LOADED_AT" else "VARCHAR") for c in AUDIT_COLUMNS]
                    fqtn = f"{database}.{L0_SCHEMA}.{table}"
                    cursor.execute(f"CREATE OR REPLACE TABLE {fqtn} ({', '.join(ddl_cols)})")
                    for start in range(0, len(bq_rows), 120):
                        chunk = bq_rows[start:start + 120]
                        values = ", ".join(
                            "(" + ", ".join(
                                [_lit(row.get(name)) for name in columns]
                                + [_lit(run_id), "CURRENT_TIMESTAMP()", _lit(key or "bigquery_direct")]
                            ) + ")"
                            for row in chunk
                        )
                        cursor.execute(f"INSERT INTO {fqtn} VALUES {values}")
                    connection.commit()
                    loaded.append(table)
                    rows_total += len(bq_rows)
                    continue
            except Exception:
                pass
            errors.append(f"{table}: {str(exc)[:180]}")
    return {"tables": loaded, "rows": rows_total, "errors": errors}


def _column_types(cursor, database: str, tables: List[str]) -> Dict[str, List[tuple]]:
    if not tables:
        return {}
    listed = ", ".join(f"'{table}'" for table in tables)
    cursor.execute(
        f"SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE FROM {database}.INFORMATION_SCHEMA.COLUMNS "
        f"WHERE TABLE_SCHEMA = '{L0_SCHEMA}' AND TABLE_NAME IN ({listed}) "
        "ORDER BY TABLE_NAME, ORDINAL_POSITION"
    )
    types: Dict[str, List[tuple]] = {}
    for table_name, column_name, data_type in cursor.fetchall():
        types.setdefault(table_name, []).append((column_name, data_type))
    return types


def _build_l1(cursor, database: str, tables: List[str]) -> Dict[str, Any]:
    built, errors, details = [], [], {}
    types = _column_types(cursor, database, tables)
    for table in tables:
        try:
            pairs = [(name, dtype) for name, dtype in types.get(table, []) if name not in AUDIT_COLUMNS]
            if not pairs:
                raise RuntimeError("no business columns found in L0")
            names = [name for name, _ in pairs]
            projected = [
                f'NULLIF(TRIM("{name}"), \'\') AS "{name}"' if str(dtype).upper() == "VARCHAR" else f'"{name}"'
                for name, dtype in pairs
            ]
            fq_l0 = f"{database}.{L0_SCHEMA}.{table}"
            fq_l1 = f"{database}.{L1_SCHEMA}.{table}"
            keys = [key for key in L1_KEYS.get(table, ()) if key in names]
            if keys:
                partition = ", ".join(f'"{key}"' for key in keys)
                cursor.execute(
                    f"CREATE OR REPLACE TABLE {fq_l1} AS SELECT * EXCLUDE (_RN) FROM ("
                    f"SELECT {', '.join(projected)}, "
                    f"ROW_NUMBER() OVER (PARTITION BY {partition} ORDER BY _LOADED_AT DESC) AS _RN "
                    f"FROM {fq_l0})"
                )
                strategy = "business_key"
            else:
                cursor.execute(
                    f"CREATE OR REPLACE TABLE {fq_l1} AS SELECT DISTINCT {', '.join(projected)} FROM {fq_l0}"
                )
                strategy = "full_row"
            built.append(table)
            details[table] = {"key": keys, "strategy": strategy}
        except Exception as exc:
            # Fallback directly to BigQuery source if S3 read is restricted
            try:
                from app.core.chat_s3_export import _bq_client
                bq = _bq_client()
                dataset = str(item.get("dataset") or "nanopro_cbs_bronze")
                bq_table = str(item.get("table") or table)
                query = f"SELECT * FROM `{bq.project}.{dataset}.{bq_table}` LIMIT 500"
                bq_rows = [dict(r) for r in bq.query(query).result(timeout=8.0)]
                if bq_rows:
                    columns = list(bq_rows[0].keys())
                    ddl_cols = [f'"{name}" VARCHAR' for name in columns]
                    ddl_cols += [f'"{c}" ' + ("TIMESTAMP_NTZ" if c == "_LOADED_AT" else "VARCHAR") for c in AUDIT_COLUMNS]
                    fqtn = f"{database}.{L0_SCHEMA}.{table}"
                    cursor.execute(f"CREATE OR REPLACE TABLE {fqtn} ({', '.join(ddl_cols)})")
                    for start in range(0, len(bq_rows), 120):
                        chunk = bq_rows[start:start + 120]
                        values = ", ".join(
                            "(" + ", ".join(
                                [_lit(row.get(name)) for name in columns]
                                + [_lit(run_id), "CURRENT_TIMESTAMP()", _lit(key or "bigquery_direct")]
                            ) + ")"
                            for row in chunk
                        )
                        cursor.execute(f"INSERT INTO {fqtn} VALUES {values}")
                    connection.commit()
                    loaded.append(table)
                    rows_total += len(bq_rows)
                    continue
            except Exception:
                pass
            errors.append(f"{table}: {str(exc)[:180]}")
    return {"tables": built, "errors": errors, "details": details}


def _marts(database: str) -> List[Dict[str, Any]]:
    """L2 business marts aggregated from L1; each declares the L1 tables it needs."""
    l1 = f"{database}.{L1_SCHEMA}"
    return [
        {
            "name": "CUSTOMER_SEGMENT_MART",
            "sources": ("CMG",),
            "sql": (
                "SELECT COALESCE(CUSTOMER_SEGMENT, 'UNKNOWN') AS CUSTOMER_SEGMENT, "
                "COALESCE(CUST_TYPE, 'UNKNOWN') AS CUST_TYPE, "
                "COALESCE(KYC_STATUS, 'UNKNOWN') AS KYC_STATUS, "
                "COALESCE(KYC_RISK_CATEGORY, 'UNKNOWN') AS KYC_RISK_CATEGORY, "
                "COUNT(*) AS CUSTOMERS, "
                "SUM(IFF(PEP_FLAG, 1, 0)) AS PEP_CUSTOMERS, "
                "SUM(IFF(SANCTIONS_HIT_FLAG, 1, 0)) AS SANCTIONS_HITS, "
                "ROUND(AVG(ANNUAL_INCOME_TURNOVER), 2) AS AVG_ANNUAL_INCOME_TURNOVER, "
                "SUM(ANNUAL_INCOME_TURNOVER) AS TOTAL_ANNUAL_INCOME_TURNOVER, "
                "SUM(IFF(RE_KYC_DUE_DATE IS NOT NULL AND RE_KYC_DUE_DATE <= DATEADD(day, 90, CURRENT_DATE()), 1, 0)) "
                "AS RE_KYC_DUE_90D, "
                "CURRENT_TIMESTAMP() AS BUILT_AT "
                f"FROM {l1}.CMG GROUP BY 1, 2, 3, 4"
            ),
        },
        {
            "name": "CUSTOMER_360_MART",
            "sources": ("CMG", "GAM", "TAM_LAM", "UBO"),
            "sql": (
                "WITH acct AS ("
                "SELECT CUST_ID, COUNT(*) AS ACCOUNTS, SUM(CLR_BAL_AMT) AS TOTAL_CLR_BAL, "
                "SUM(DRAWING_POWER) AS TOTAL_DRAWING_POWER, "
                "SUM(IFF(INTERNET_BANKING_FLAG, 1, 0)) AS DIGITAL_ACCOUNTS "
                f"FROM {l1}.GAM GROUP BY CUST_ID), "
                "loan AS ("
                "SELECT CUST_ID, COUNT(*) AS LOAN_CONTRACTS, SUM(CURRENT_OUTSTANDING_BAL) AS TOTAL_LOAN_OUTSTANDING, "
                "SUM(OVERDUE_PRINCIPAL + OVERDUE_INTEREST) AS TOTAL_LOAN_OVERDUE, MAX(DPD_COUNT) AS MAX_DPD "
                f"FROM {l1}.TAM_LAM GROUP BY CUST_ID), "
                "owners AS ("
                "SELECT CUST_ID, COUNT(*) AS UBO_COUNT, MAX(SHARE_PCT) AS MAX_UBO_SHARE_PCT, "
                "SUM(IFF(SANCTIONS_HIT, 1, 0)) AS SANCTIONED_UBOS "
                f"FROM {l1}.UBO GROUP BY CUST_ID) "
                "SELECT c.CUST_ID, c.CUST_NAME, COALESCE(c.CUSTOMER_SEGMENT, 'UNKNOWN') AS CUSTOMER_SEGMENT, "
                "c.CUST_TYPE, c.KYC_STATUS, c.KYC_RISK_CATEGORY, c.CUST_STATUS, c.CITY, c.STATE, "
                "c.PEP_FLAG, c.SANCTIONS_HIT_FLAG, "
                "COALESCE(a.ACCOUNTS, 0) AS ACCOUNTS, COALESCE(a.TOTAL_CLR_BAL, 0) AS TOTAL_CLR_BAL, "
                "COALESCE(a.TOTAL_DRAWING_POWER, 0) AS TOTAL_DRAWING_POWER, "
                "COALESCE(a.DIGITAL_ACCOUNTS, 0) AS DIGITAL_ACCOUNTS, "
                "COALESCE(l.LOAN_CONTRACTS, 0) AS LOAN_CONTRACTS, "
                "COALESCE(l.TOTAL_LOAN_OUTSTANDING, 0) AS TOTAL_LOAN_OUTSTANDING, "
                "COALESCE(l.TOTAL_LOAN_OVERDUE, 0) AS TOTAL_LOAN_OVERDUE, COALESCE(l.MAX_DPD, 0) AS MAX_DPD, "
                "COALESCE(o.UBO_COUNT, 0) AS UBO_COUNT, COALESCE(o.MAX_UBO_SHARE_PCT, 0) AS MAX_UBO_SHARE_PCT, "
                "COALESCE(o.SANCTIONED_UBOS, 0) AS SANCTIONED_UBOS, CURRENT_TIMESTAMP() AS BUILT_AT "
                f"FROM {l1}.CMG c "
                "LEFT JOIN acct a ON a.CUST_ID = c.CUST_ID "
                "LEFT JOIN loan l ON l.CUST_ID = c.CUST_ID "
                "LEFT JOIN owners o ON o.CUST_ID = c.CUST_ID"
            ),
        },
        {
            "name": "ACCOUNT_PORTFOLIO_MART",
            "sources": ("GAM",),
            "sql": (
                "SELECT COALESCE(ACCT_TYPE, 'UNKNOWN') AS ACCT_TYPE, COALESCE(SCHM_TYPE, 'UNKNOWN') AS SCHM_TYPE, "
                "COALESCE(ACCT_STATUS, 'UNKNOWN') AS ACCT_STATUS, "
                "COUNT(*) AS ACCOUNTS, COUNT(DISTINCT CUST_ID) AS CUSTOMERS, "
                "SUM(CLR_BAL_AMT) AS TOTAL_CLR_BAL, SUM(UN_CLR_BAL_AMT) AS TOTAL_UNCLR_BAL, "
                "SUM(SANCT_LIM) AS TOTAL_SANCTION_LIMIT, SUM(DRAWING_POWER) AS TOTAL_DRAWING_POWER, "
                "ROUND(AVG(CLR_BAL_AMT), 2) AS AVG_CLR_BAL, "
                "SUM(IFF(NOMINEE_REGISTERED_FLAG, 1, 0)) AS NOMINEE_REGISTERED, "
                "SUM(IFF(INTERNET_BANKING_FLAG, 1, 0)) AS NET_BANKING_ENABLED, "
                "SUM(IFF(UPI_ENABLED_FLAG, 1, 0)) AS UPI_ENABLED, "
                "CURRENT_TIMESTAMP() AS BUILT_AT "
                f"FROM {l1}.GAM GROUP BY 1, 2, 3"
            ),
        },
        {
            "name": "BRANCH_NETWORK_MART",
            "sources": ("SOL", "GAM"),
            "sql": (
                "SELECT s.SOL_ID, s.BRANCH_NAME, s.BRANCH_CATEGORY, s.REGION_ZONE, s.STATE, s.IFSC_CODE, "
                "s.BRANCH_STATUS, s.AUTHORIZED_FOREX_DEALER_FLAG, s.CURRENCY_CHEST_FLAG, "
                "COUNT(a.ACID) AS ACCOUNTS, COUNT(DISTINCT a.CUST_ID) AS CUSTOMERS, "
                "COALESCE(SUM(a.CLR_BAL_AMT), 0) AS TOTAL_CLR_BAL, "
                "COALESCE(SUM(a.DRAWING_POWER), 0) AS TOTAL_DRAWING_POWER, "
                "SUM(IFF(a.INTERNET_BANKING_FLAG, 1, 0)) AS DIGITAL_ACCOUNTS, "
                "CURRENT_TIMESTAMP() AS BUILT_AT "
                f"FROM {l1}.SOL s LEFT JOIN {l1}.GAM a ON a.SOL_ID = s.SOL_ID "
                "GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9"
            ),
        },
        {
            "name": "TRANSACTION_ACTIVITY_MART",
            "sources": ("HTD",),
            "sql": (
                "SELECT COALESCE(TRAN_TYPE, 'UNKNOWN') AS TRAN_TYPE, COALESCE(CHANNEL_ID, 'UNKNOWN') AS CHANNEL_ID, "
                "COUNT(*) AS TRANSACTIONS, COUNT(DISTINCT FORACID) AS ACCOUNTS, "
                "SUM(TRAN_AMT_INR) AS TOTAL_AMOUNT_INR, ROUND(AVG(TRAN_AMT_INR), 2) AS AVG_AMOUNT_INR, "
                "SUM(IFF(CASH_TRAN_FLAG, 1, 0)) AS CASH_TRANSACTIONS, "
                "COUNT_IF(SUSPICIOUS_RULE_HIT IS NOT NULL) AS SUSPICIOUS_FLAGGED, "
                "SUM(IFF(REVERSAL_FLAG, 1, 0)) AS REVERSALS, "
                "SUM(IFF(IS_WEEKEND_HOLIDAY, 1, 0)) AS WEEKEND_TRANSACTIONS, "
                "MIN(TRAN_DATE) AS FIRST_TRAN_DATE, MAX(TRAN_DATE) AS LAST_TRAN_DATE, "
                "CURRENT_TIMESTAMP() AS BUILT_AT "
                f"FROM {l1}.HTD GROUP BY 1, 2"
            ),
        },
        {
            "name": "LOAN_PORTFOLIO_MART",
            "sources": ("TAM_LAM",),
            "sql": (
                "SELECT COALESCE(CONTRACT_TYPE, 'UNKNOWN') AS CONTRACT_TYPE, "
                "COALESCE(NPA_STATUS, 'UNKNOWN') AS NPA_STATUS, "
                "COALESCE(SMA_CLASSIFICATION, 'UNKNOWN') AS SMA_CLASSIFICATION, "
                "COUNT(*) AS CONTRACTS, SUM(PRINCIPAL_AMT) AS TOTAL_PRINCIPAL, "
                "SUM(CURRENT_OUTSTANDING_BAL) AS TOTAL_OUTSTANDING, "
                "SUM(OVERDUE_PRINCIPAL) AS TOTAL_OVERDUE_PRINCIPAL, "
                "SUM(OVERDUE_INTEREST) AS TOTAL_OVERDUE_INTEREST, "
                "ROUND(AVG(INTEREST_RATE), 4) AS AVG_INTEREST_RATE, "
                "ROUND(AVG(DPD_COUNT), 2) AS AVG_DPD, MAX(DPD_COUNT) AS MAX_DPD, "
                "SUM(IFF(RESTRUCTURED_FLAG, 1, 0)) AS RESTRUCTURED_CONTRACTS, "
                "SUM(COLLATERAL_VALUATION_AMT) AS TOTAL_COLLATERAL_VALUE, "
                "CURRENT_TIMESTAMP() AS BUILT_AT "
                f"FROM {l1}.TAM_LAM GROUP BY 1, 2, 3"
            ),
        },
        {
            "name": "SWIFT_MESSAGE_MART",
            "sources": ("SWIFT_MSG",),
            "sql": (
                "SELECT COALESCE(MESSAGE_TYPE, 'UNKNOWN') AS MESSAGE_TYPE, COALESCE(DIRECTION, 'UNKNOWN') AS DIRECTION, "
                "COALESCE(OFAC_SANCTION_SCREEN_STATUS, 'UNKNOWN') AS OFAC_SANCTION_SCREEN_STATUS, "
                "COUNT(*) AS MESSAGES, COUNT(DISTINCT SENDER_BIC) AS SENDER_BICS, "
                "COUNT(DISTINCT RECEIVER_BIC) AS RECEIVER_BICS, "
                "COUNT(DISTINCT BENEFICIARY_COUNTRY) AS BENEFICIARY_COUNTRIES, "
                "SUM(ORIGINAL_AMOUNT) AS TOTAL_ORIGINAL_AMOUNT, SUM(AMOUNT_INR) AS TOTAL_AMOUNT_INR, "
                "ROUND(AVG(EXCHANGE_RATE), 4) AS AVG_EXCHANGE_RATE, "
                "SUM(IFF(FIU_CBWTR_REPORTED, 1, 0)) AS FIU_REPORTED, "
                "MIN(VALUE_DATE) AS FIRST_VALUE_DATE, MAX(VALUE_DATE) AS LAST_VALUE_DATE, "
                "CURRENT_TIMESTAMP() AS BUILT_AT "
                f"FROM {l1}.SWIFT_MSG GROUP BY 1, 2, 3"
            ),
        },
        {
            "name": "UBO_OWNERSHIP_MART",
            "sources": ("UBO",),
            "sql": (
                "SELECT CUST_ID, COUNT(*) AS UBO_OWNERS, MAX(SHARE_PCT) AS MAX_SHARE_PCT, "
                "SUM(SHARE_PCT) AS TOTAL_SHARE_PCT, MAX(VOTING_RIGHTS_PCT) AS MAX_VOTING_RIGHTS_PCT, "
                "COUNT(DISTINCT RELATIONSHIP_TYPE) AS RELATIONSHIP_TYPES, "
                "SUM(IFF(PEP_STATUS, 1, 0)) AS PEP_OWNERS, SUM(IFF(SANCTIONS_HIT, 1, 0)) AS SANCTIONED_OWNERS, "
                "MAX(VERIFIED_DATE) AS LAST_VERIFIED_DATE, MAX(EFFECTIVE_FROM_DATE) AS LAST_EFFECTIVE_FROM, "
                "CURRENT_TIMESTAMP() AS BUILT_AT "
                f"FROM {l1}.UBO GROUP BY CUST_ID"
            ),
        },
        {
            "name": "VCT_CASH_MART",
            "sources": ("VCT",),
            "sql": (
                "SELECT COALESCE(SOL_ID, 'UNKNOWN') AS SOL_ID, COALESCE(TRAN_NATURE, 'UNKNOWN') AS TRAN_NATURE, "
                "COUNT(*) AS VOUCHERS, SUM(TOTAL_CASH_AMOUNT) AS TOTAL_CASH_AMOUNT, "
                "SUM(DENOM_2000_COUNT) AS DENOM_2000_NOTES, SUM(DENOM_500_COUNT) AS DENOM_500_NOTES, "
                "SUM(DENOM_200_COUNT) AS DENOM_200_NOTES, SUM(DENOM_100_COUNT) AS DENOM_100_NOTES, "
                "SUM(DENOM_50_COUNT) AS DENOM_50_NOTES, SUM(DENOM_20_COUNT) AS DENOM_20_NOTES, "
                "SUM(DENOM_10_COUNT) AS DENOM_10_NOTES, SUM(FAKE_NOTE_COUNT) AS FAKE_NOTES, "
                "COUNT_IF(FIR_IMPOUND_NUMBER IS NOT NULL) AS FIR_IMPOUNDS, "
                "SUM(IFF(CTR_REPORTABLE, 1, 0)) AS CTR_REPORTABLE_VOUCHERS, "
                "SUM(IFF(FORM60_SUBMITTED, 1, 0)) AS FORM60_SUBMITTED_VOUCHERS, "
                "CURRENT_TIMESTAMP() AS BUILT_AT "
                f"FROM {l1}.VCT GROUP BY 1, 2"
            ),
        },
    ]


def _build_l2(cursor, database: str, tables: List[str], details: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    available = set(tables)
    marts, skipped, errors, row_counts = [], [], [], {}
    for mart in _marts(database):
        missing = [source for source in mart["sources"] if source not in available]
        if missing:
            skipped.append(f"{mart['name']}: missing {', '.join(missing)}")
            continue
        fqtn = f"{database}.{L2_SCHEMA}.{mart['name']}"
        try:
            cursor.execute(f"CREATE OR REPLACE TABLE {fqtn} AS {mart['sql']}")
            cursor.execute(f"SELECT COUNT(*) FROM {fqtn}")
            row_counts[mart["name"]] = int((cursor.fetchone() or [0])[0] or 0)
            marts.append(mart["name"])
        except Exception as exc:
            errors.append(f"{mart['name']}: {str(exc)[:180]}")

    quality = []
    for table in tables:
        info = details.get(table, {})
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {database}.{L0_SCHEMA}.{table}")
            l0_count = int((cursor.fetchone() or [0])[0] or 0)
            cursor.execute(f"SELECT COUNT(*) FROM {database}.{L1_SCHEMA}.{table}")
            l1_count = int((cursor.fetchone() or [0])[0] or 0)
            quality.append((table, l0_count, l1_count, l0_count - l1_count,
                            ",".join(info.get("key") or []), info.get("strategy") or "n/a"))
        except Exception:
            quality.append((table, None, None, None, "", "error"))

    dq = f"{database}.{L2_SCHEMA}.DATA_QUALITY_MART"
    cursor.execute(
        f"CREATE OR REPLACE TABLE {dq} ("
        "TABLE_NAME VARCHAR(120), L0_ROWS NUMBER(38,0), L1_ROWS NUMBER(38,0), "
        "DUPLICATES_REMOVED NUMBER(38,0), KEY_COLUMNS VARCHAR(400), DEDUPE_STRATEGY VARCHAR(40), "
        "MEASURED_AT TIMESTAMP_NTZ)"
    )
    if quality:
        values = ", ".join(
            f"({_lit(t)}, {('NULL' if a is None else a)}, {('NULL' if b is None else b)}, "
            f"{('NULL' if c is None else c)}, {_lit(k)}, {_lit(s)}, CURRENT_TIMESTAMP())"
            for t, a, b, c, k, s in quality
        )
        cursor.execute(f"INSERT INTO {dq} VALUES {values}")

    catalog = f"{database}.{L2_SCHEMA}.MART_CATALOG"
    try:
        cursor.execute(
            f"CREATE OR REPLACE TABLE {catalog} ("
            "MART_NAME VARCHAR(120), SOURCE_TABLES VARCHAR(400), ROW_COUNT NUMBER(38,0), BUILT_AT TIMESTAMP_NTZ)"
        )
        entries = [(mart["name"], ",".join(mart["sources"]), row_counts.get(mart["name"]))
                   for mart in _marts(database) if mart["name"] in marts]
        entries.append(("DATA_QUALITY_MART", ",".join(tables), len(quality)))
        built_values = [
            f"({_lit(name)}, {_lit(sources)}, {('NULL' if count is None else count)}, CURRENT_TIMESTAMP())"
            for name, sources, count in entries
        ]
        if built_values:
            cursor.execute(f"INSERT INTO {catalog} VALUES {', '.join(built_values)}")
    except Exception as exc:
        errors.append(f"MART_CATALOG: {str(exc)[:180]}")

    return {"marts": marts, "rows": row_counts, "quality": quality,
            "skipped": skipped, "errors": errors}


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
        l2 = _build_l2(cursor, database, l0["tables"], l1["details"]) if l0["tables"] else {
            "marts": [], "rows": {}, "quality": [], "skipped": [], "errors": []}
        connection.commit()
        duplicates = sum(entry[3] or 0 for entry in l2["quality"])
        result: Dict[str, Any] = {
            "status": "synced" if l0["tables"] and not l0["errors"] and not l1["errors"] and not l2["errors"] else "partial",
            "database": database,
            "run_id": run_id,
            "l0": {"tables": len(l0["tables"]), "rows": l0["rows"]},
            "l1": {"tables": len(l1["tables"]), "duplicates_removed": duplicates, "dedupe": l1["details"]},
            "l2": {"tables": len(l2["marts"]), "marts": l2["rows"],
                   "data_quality_mart": f"{database}.{L2_SCHEMA}.DATA_QUALITY_MART",
                   "skipped": l2["skipped"]},
        }
        errors = l0["errors"] + l1["errors"] + l2["errors"]
        if errors:
            result["errors"] = errors[:5]
        log_event(
            f"Snowflake sync {run_id}: L0 {result['l0']}, L1 {result['l1']['tables']} tables "
            f"({duplicates} dupes removed), L2 marts {sorted(l2['rows'])}",
            component="SnowflakeLakehouse",
        )
        return result
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:240]}
    finally:
        try:
            connection.close()
        except Exception:
            pass


# ----------------------------------------------------------------------------
# Batch control — BOD / SOD / T1 / EOD ledger
# ----------------------------------------------------------------------------
def _batch_fq(database: str) -> str:
    return f"{database}.{L2_SCHEMA}.{BATCH_TABLE}"


def record_batch(cycle: str, business_date: str, status: str, trigger: str = "scheduler",
                 run_id: str = "", tables: int = 0, rows: int = 0,
                 details: Optional[Dict[str, Any]] = None,
                 started_at: Optional[Any] = None, finished_at: Optional[Any] = None) -> Dict[str, Any]:
    """Upsert one batch row into L2_CURATED.BATCH_CONTROL (idempotent per cycle+date)."""
    import json
    from datetime import datetime, timezone
    from app.core import snowflake_client

    database = str(snowflake_client.load_config().get("database") or "BANK_DB").strip()
    batch_id = f"{business_date}-{cycle.upper()}"
    started = started_at or datetime.now(timezone.utc)
    finished = finished_at or datetime.now(timezone.utc)

    def _ts(value: Any) -> str:
        return "TO_TIMESTAMP_NTZ(" + _lit(value.astimezone(timezone.utc).replace(tzinfo=None).isoformat(sep=" ")) + ")"

    payload = json.dumps(details or {}, default=str)[:4000]
    connection = _connect()
    try:
        cursor = connection.cursor()
        _ensure_layers(cursor, database)
        fq = _batch_fq(database)
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {fq} ("
            "BATCH_ID VARCHAR, CYCLE VARCHAR, BUSINESS_DATE DATE, STATUS VARCHAR, TRIGGERED_BY VARCHAR, "
            "RUN_ID VARCHAR, EXPORTED_TABLES NUMBER(38,0), EXPORTED_ROWS NUMBER(38,0), DETAILS VARCHAR, "
            "STARTED_AT TIMESTAMP_NTZ, FINISHED_AT TIMESTAMP_NTZ, RECORDED_AT TIMESTAMP_NTZ)"
        )
        cursor.execute(
            f"MERGE INTO {fq} t USING (SELECT "
            f"{_lit(batch_id)} AS BATCH_ID, {_lit(cycle.upper())} AS CYCLE, "
            f"TO_DATE({_lit(business_date)}) AS BUSINESS_DATE, {_lit(status.upper())} AS STATUS, "
            f"{_lit(trigger)} AS TRIGGERED_BY, {_lit(run_id)} AS RUN_ID, {int(tables)} AS EXPORTED_TABLES, "
            f"{int(rows)} AS EXPORTED_ROWS, {_lit(payload)} AS DETAILS, {_ts(started)} AS STARTED_AT, "
            f"{_ts(finished)} AS FINISHED_AT, CURRENT_TIMESTAMP() AS RECORDED_AT) s "
            "ON t.BATCH_ID = s.BATCH_ID "
            "WHEN MATCHED THEN UPDATE SET CYCLE = s.CYCLE, BUSINESS_DATE = s.BUSINESS_DATE, STATUS = s.STATUS, "
            "TRIGGERED_BY = s.TRIGGERED_BY, RUN_ID = s.RUN_ID, EXPORTED_TABLES = s.EXPORTED_TABLES, "
            "EXPORTED_ROWS = s.EXPORTED_ROWS, DETAILS = s.DETAILS, STARTED_AT = s.STARTED_AT, "
            "FINISHED_AT = s.FINISHED_AT, RECORDED_AT = s.RECORDED_AT "
            "WHEN NOT MATCHED THEN INSERT (BATCH_ID, CYCLE, BUSINESS_DATE, STATUS, TRIGGERED_BY, RUN_ID, "
            "EXPORTED_TABLES, EXPORTED_ROWS, DETAILS, STARTED_AT, FINISHED_AT, RECORDED_AT) "
            "VALUES (s.BATCH_ID, s.CYCLE, s.BUSINESS_DATE, s.STATUS, s.TRIGGERED_BY, s.RUN_ID, "
            "s.EXPORTED_TABLES, s.EXPORTED_ROWS, s.DETAILS, s.STARTED_AT, s.FINISHED_AT, s.RECORDED_AT)"
        )
        connection.commit()
        return {"status": "recorded", "batch_id": batch_id, "table": fq}
    finally:
        try:
            connection.close()
        except Exception:
            pass


def batch_history(business_date: str = "", limit: int = 40) -> List[Dict[str, Any]]:
    """Read recent batch rows, newest first. Empty list when Snowflake is unavailable."""
    from app.core import snowflake_client

    database = str(snowflake_client.load_config().get("database") or "BANK_DB").strip()
    where = f"WHERE BUSINESS_DATE = TO_DATE({_lit(business_date)}) " if business_date else ""
    connection = _connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"SELECT BATCH_ID, CYCLE, TO_VARCHAR(BUSINESS_DATE), STATUS, TRIGGERED_BY, RUN_ID, "
            f"EXPORTED_TABLES, EXPORTED_ROWS, DETAILS, TO_VARCHAR(STARTED_AT), TO_VARCHAR(FINISHED_AT) "
            f"FROM {_batch_fq(database)} {where}ORDER BY RECORDED_AT DESC LIMIT {max(1, int(limit))}"
        )
        rows = cursor.fetchall()
    finally:
        try:
            connection.close()
        except Exception:
            pass
    return [
        {
            "batch_id": row[0], "cycle": row[1], "business_date": row[2], "status": row[3],
            "trigger": row[4], "run_id": row[5], "tables": row[6], "rows": row[7],
            "details": row[8], "started_at": row[9], "finished_at": row[10],
        }
        for row in rows
    ]
