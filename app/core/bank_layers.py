"""Bank-style warehouse layers on top of the NanoPro bronze lake.

The target bank shape is:

    Finacle 3NF -> CDC I/U/D (SCN order) -> immutable raw delta batches
    -> L0 append + raw history -> L1 3NF merge + SCD2
    -> L2 conformed dimensions + facts -> RBI/FIU/ALM/UPI report marts

This module reproduces that on free-tier services:

* raw zone   : ``s3://<bucket>/raw/cdc/<table>/dt=../batch=../cdc.parquet``
               written by :mod:`app.core.bank_core_seed` (immutable per batch)
* L0_HIST    : every CDC event appended once, guarded by a batch control table
* L1_CUR     : latest row per business key (deletes drop the key)
* L1_SCD2    : type-2 history for the SCD tables declared in the model
* L2_STAR    : conformed dimensions + facts
* RPT_*      : report-shaped extracts (FIU, RBI, ALM, UPI/Cards)

Nothing is fabricated: every number is aggregated from the L1/L2 tables that
were built from the seeded source rows and the CDC events.
"""
from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from app.core import bank_core_model as model
from app.core.logger import log_event

HIST_SCHEMA = "L0_HIST"
CUR_SCHEMA = "L1_CUR"
SCD_SCHEMA = "L1_SCD2"
STAR_SCHEMA = "L2_STAR"
REPORT_SCHEMAS = ("RPT_FIU", "RPT_RBI", "RPT_ALM", "RPT_UPI")
RAW_PREFIX = "raw/cdc/"
CONTROL_TABLE = "_RAW_BATCH_CONTROL"
IST = timezone(timedelta(hours=5, minutes=30))

STATE: Dict[str, Any] = {
    "status": "idle",
    "running": False,
    "last_run": "",
    "database": "",
    "stages": {},
    "errors": [],
}

_LOCK = threading.Lock()

_HIST_DDL = (
    "EVENT_ID VARCHAR, TABLE_NAME VARCHAR, OP VARCHAR, COMMIT_SCN NUMBER(38,0), "
    "COMMIT_TS VARCHAR, PK_JSON VARCHAR, ROW_JSON VARCHAR, BATCH_ID VARCHAR, "
    "_SOURCE_KEY VARCHAR, _LOADED_AT TIMESTAMP_NTZ"
)


def _enabled() -> bool:
    return (os.environ.get("NANOPRO_BANK_LAYERS") or "1").strip().lower() not in (
        "0", "false", "no", "off")


def _now() -> str:
    return datetime.now(IST).isoformat(timespec="seconds")


def _cast(type_sql: str) -> str:
    base = str(type_sql or "STRING").split("(", 1)[0].upper()
    return {
        "STRING": "VARCHAR",
        "INT64": "NUMBER(38,0)",
        "FLOAT64": "FLOAT",
        "BOOL": "BOOLEAN",
        "DATE": "DATE",
        "TIMESTAMP": "TIMESTAMP_NTZ",
        "NUMERIC": "NUMBER(18,2)",
        "BIGNUMERIC": "NUMBER(38,9)",
    }.get(base, "VARCHAR")


def _json_columns(spec: Dict[str, Any], indent: str = "         ") -> str:
    parts = [f'{indent}PARSE_JSON(ROW_JSON):"{name}"::{_cast(type_sql)} AS "{name}"'
             for name, type_sql in spec["columns"]]
    return ",\n".join(parts)


# ----------------------------------------------------------------------------
# Connection / schema bootstrap
# ----------------------------------------------------------------------------
def _connect():
    from app.core.snowflake_lakehouse import _connect as lakehouse_connect

    return lakehouse_connect()


def _lit(value: Any) -> str:
    from app.core.snowflake_lakehouse import _lit as lakehouse_lit

    return lakehouse_lit(value)


def _ensure_schemas(cursor, database: str) -> None:
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    for schema in (HIST_SCHEMA, CUR_SCHEMA, SCD_SCHEMA, STAR_SCHEMA) + REPORT_SCHEMAS:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {database}.{schema}")


def _infoschema(cursor, database: str, schema: str) -> Set[str]:
    try:
        cursor.execute(
            "SELECT TABLE_NAME FROM "
            f"{database}.INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = {_lit(schema)}"
        )
        return {str(row[0]).upper() for row in cursor.fetchall() or []}
    except Exception:
        return set()


def _count(cursor, fqtn: str) -> Optional[int]:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {fqtn}")
        return int((cursor.fetchone() or [0])[0] or 0)
    except Exception:
        return None


# ----------------------------------------------------------------------------
# Raw zone -> L0_HIST (append-only, guarded per batch/table)
# ----------------------------------------------------------------------------
def _s3_client():
    import boto3

    from app.core.chat_s3_export import _aws_config

    config = _aws_config()
    if not config.get("bucket"):
        raise RuntimeError("AWS_S3_BUCKET is not configured.")
    return boto3.Session(
        region_name=config["region"],
        aws_access_key_id=config["access_key"],
        aws_secret_access_key=config["secret_key"],
    ).client("s3"), config["bucket"]


def _manifest_keys(s3, bucket: str) -> List[str]:
    keys: List[str] = []
    token = None
    while True:
        kwargs: Dict[str, Any] = {"Bucket": bucket, "Prefix": RAW_PREFIX + "_MANIFEST_"}
        if token:
            kwargs["ContinuationToken"] = token
        page = s3.list_objects_v2(**kwargs)
        keys.extend(str(item["Key"]) for item in page.get("Contents") or [])
        if not page.get("IsTruncated"):
            break
        token = page.get("NextContinuationToken")
    return sorted(keys)


def _ensure_history(cursor, database: str) -> None:
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {database}.{HIST_SCHEMA}.{CONTROL_TABLE} ("
                   "BATCH_ID VARCHAR, TABLE_NAME VARCHAR, ROWS NUMBER(38,0), "
                   "LOADED_AT TIMESTAMP_NTZ)")


def _loaded_tables(cursor, database: str, batch_id: str) -> Set[str]:
    cursor.execute(f"SELECT TABLE_NAME FROM {database}.{HIST_SCHEMA}.{CONTROL_TABLE} "
                   f"WHERE BATCH_ID = {_lit(batch_id)}")
    return {str(row[0]).upper() for row in cursor.fetchall() or []}


def load_history(cursor, database: str) -> Dict[str, Any]:
    """Append every not-yet-loaded raw CDC batch into ``L0_HIST``."""
    import io

    import pyarrow.parquet as pq

    _ensure_history(cursor, database)
    s3, bucket = _s3_client()
    manifests = _manifest_keys(s3, bucket)
    batches, tables, rows, skipped, errors = 0, 0, 0, 0, []
    for key in manifests:
        try:
            manifest = json.loads(
                s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8"))
        except Exception as exc:
            errors.append(f"{key}: {str(exc)[:160]}")
            continue
        batch_id = str(manifest.get("batch_id") or "")
        if not batch_id:
            continue
        already = _loaded_tables(cursor, database, batch_id)
        did_load = False
        for obj in manifest.get("objects") or []:
            table = str(obj.get("table") or "").upper()
            object_key = str(obj.get("key") or "")
            if not table or not object_key:
                continue
            if table in already:
                skipped += 1
                continue
            fqtn = f"{database}.{HIST_SCHEMA}.{table}"
            try:
                body = s3.get_object(Bucket=bucket, Key=object_key)["Body"].read()
                arrow = pq.read_table(io.BytesIO(body))
                records = arrow.to_pylist()
                cursor.execute("BEGIN")
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {fqtn} ({_HIST_DDL})")
                for start in range(0, len(records), 100):
                    chunk = records[start:start + 100]
                    values = ", ".join(
                        "(" + ", ".join([
                            _lit(record.get("EVENT_ID")), _lit(record.get("TABLE_NAME")),
                            _lit(record.get("OP")), str(int(record.get("COMMIT_SCN") or 0)),
                            _lit(record.get("COMMIT_TS")), _lit(record.get("PK_JSON")),
                            _lit(record.get("ROW_JSON")), _lit(record.get("BATCH_ID")),
                            _lit(object_key), "CURRENT_TIMESTAMP()",
                        ]) + ")"
                        for record in chunk
                    )
                    cursor.execute(f"INSERT INTO {fqtn} VALUES {values}")
                cursor.execute(
                    f"INSERT INTO {database}.{HIST_SCHEMA}.{CONTROL_TABLE} VALUES "
                    f"({_lit(batch_id)}, {_lit(table)}, {len(records)}, CURRENT_TIMESTAMP())")
                cursor.execute("COMMIT")
                tables += 1
                rows += len(records)
                did_load = True
            except Exception as exc:
                try:
                    cursor.execute("ROLLBACK")
                except Exception:
                    pass
                errors.append(f"{table}: {str(exc)[:180]}")
        if did_load:
            batches += 1
    return {"status": "loaded" if not errors else "partial", "batches": batches,
            "tables": tables, "rows": rows, "skipped": skipped,
            "manifests": len(manifests), "errors": errors[:8]}


# ----------------------------------------------------------------------------
# L1 current state + SCD2 history
# ----------------------------------------------------------------------------
def build_current(cursor, database: str) -> Dict[str, Any]:
    history = _infoschema(cursor, database, HIST_SCHEMA) - {CONTROL_TABLE}
    staging = _infoschema(cursor, database, "L0_STAGING")
    built, fallback, skipped, errors = [], [], [], []
    for spec in model.all_tables():
        table = spec["table"]
        pk = spec["pk"][0]
        fqtn = f"{database}.{CUR_SCHEMA}.{table}"
        try:
            if table in history:
                cursor.execute(
                    f"CREATE OR REPLACE TABLE {fqtn} AS\n"
                    "SELECT * EXCLUDE (_RN) FROM (\n"
                    f"  SELECT {_json_columns(spec)}, OP, COMMIT_SCN,\n"
                    f"         ROW_NUMBER() OVER (PARTITION BY \"{pk}\" ORDER BY COMMIT_SCN DESC) AS _RN\n"
                    f"  FROM {database}.{HIST_SCHEMA}.{table}\n"
                    ") WHERE _RN = 1 AND OP <> 'D'"
                )
                built.append(table)
            elif table in staging:
                cursor.execute(
                    f"CREATE OR REPLACE TABLE {fqtn} AS SELECT * EXCLUDE "
                    "(_RUN_ID, _LOADED_AT, _SOURCE_KEY) FROM "
                    f"{database}.L0_STAGING.{table}"
                )
                built.append(table)
                fallback.append(table)
            else:
                skipped.append(table)
        except Exception as exc:
            errors.append(f"{table}: {str(exc)[:180]}")
    return {"status": "built" if not errors else "partial", "tables": len(built),
            "current": built, "from_staging": fallback, "skipped": skipped,
            "errors": errors[:8]}


def build_scd2(cursor, database: str) -> Dict[str, Any]:
    history = _infoschema(cursor, database, HIST_SCHEMA) - {CONTROL_TABLE}
    built, skipped, errors = [], [], []
    for table in model.scd_tables():
        spec = model.get(table) or {}
        if not spec or table not in history:
            skipped.append(table)
            continue
        pk = spec["pk"][0]
        fqtn = f"{database}.{SCD_SCHEMA}.{table}"
        try:
            cursor.execute(
                f"CREATE OR REPLACE TABLE {fqtn} AS\n"
                "WITH typed AS (\n"
                f"  SELECT OP, COMMIT_SCN, COMMIT_TS,\n{_json_columns(spec)}\n"
                f"  FROM {database}.{HIST_SCHEMA}.{table}\n"
                "), seq AS (\n"
                "  SELECT *, LEAD(COMMIT_TS) OVER (PARTITION BY "
                f"\"{pk}\" ORDER BY COMMIT_SCN) AS _NEXT_TS\n"
                "  FROM typed\n"
                "), ranked AS (\n"
                "  SELECT *, ROW_NUMBER() OVER (PARTITION BY "
                f"\"{pk}\" ORDER BY COMMIT_SCN) AS _VERSION\n"
                "  FROM seq\n"
                ")\n"
                "SELECT * EXCLUDE (_NEXT_TS, OP, COMMIT_SCN, COMMIT_TS, _VERSION),\n"
                "       TO_TIMESTAMP_NTZ(COMMIT_TS) AS VALID_FROM,\n"
                "       IFF(_NEXT_TS IS NULL, NULL, DATEADD(second, -1, TO_TIMESTAMP_NTZ(_NEXT_TS))) AS VALID_TO,\n"
                "       IFF(_NEXT_TS IS NULL, TRUE, FALSE) AS IS_CURRENT,\n"
                "       _VERSION AS VERSION\n"
                "FROM ranked WHERE OP <> 'D'"
            )
            built.append(table)
        except Exception as exc:
            errors.append(f"{table}: {str(exc)[:180]}")
    return {"status": "built" if not errors else "partial", "tables": built,
            "skipped": skipped, "errors": errors[:8]}


# ----------------------------------------------------------------------------
# L2 star: conformed dimensions + facts
# ----------------------------------------------------------------------------
def _star_specs(database: str) -> List[Dict[str, Any]]:
    h = f"{database}.L1_HARMONIZED"
    c = f"{database}.{CUR_SCHEMA}"
    return [
        {
            "name": "DIM_DATE", "requires": [],
            "sql": (
                "SELECT TO_NUMBER(TO_CHAR(d, 'YYYYMMDD')) AS DATE_KEY, d AS CAL_DATE, "
                "YEAR(d) AS YEAR_NO, MONTH(d) AS MONTH_NO, QUARTER(d) AS QUARTER_NO, "
                "DAY(d) AS DAY_NO, DAYOFWEEK(d) AS DAY_OF_WEEK, "
                "IFF(DAYOFWEEK(d) IN (0, 6), TRUE, FALSE) AS IS_WEEKEND "
                "FROM (SELECT DATEADD(day, SEQ4(), TO_DATE('2026-01-01')) AS d "
                "FROM TABLE(GENERATOR(ROWCOUNT => 731)))"
            ),
        },
        {
            "name": "DIM_CUSTOMER", "requires": [("h", "CMG"), ("c", "CMG_EXT")],
            "sql": (
                "SELECT c.CUST_ID, c.CUST_NAME, c.CUSTOMER_SEGMENT, c.CUST_TYPE, "
                "c.KYC_STATUS, c.KYC_RISK_CATEGORY, c.CUST_STATUS, c.CITY, c.STATE, "
                "c.PEP_FLAG, c.SANCTIONS_HIT_FLAG, c.ANNUAL_INCOME_TURNOVER, "
                "c.RE_KYC_DUE_DATE, c.HOME_BRANCH_SOL_ID, "
                "e.DOB, e.GENDER, e.NATIONALITY, e.OCCUPATION_CODE, e.RISK_SCORE, "
                "e.RISK_REVIEW_DATE, e.SOURCE_OF_FUNDS, e.TIN, e.TAX_RESIDENCY, "
                "e.FATCA_STATUS, e.CRS_STATUS, e.US_PERSON_FLAG, e.CUSTOMER_SINCE "
                f"FROM {h}.CMG c LEFT JOIN {c}.CMG_EXT e ON e.CUST_ID = c.CUST_ID"
            ),
        },
        {
            "name": "DIM_ACCOUNT", "requires": [("h", "GAM"), ("c", "GAM_EXT")],
            "sql": (
                "SELECT a.ACID, a.CUST_ID, a.SOL_ID, a.ACCT_TYPE, a.SCHM_TYPE, "
                "a.ACCT_STATUS, a.CLR_BAL_AMT, a.UN_CLR_BAL_AMT, a.SANCT_LIM, "
                "a.DRAWING_POWER, a.NOMINEE_REGISTERED_FLAG, a.INTERNET_BANKING_FLAG, "
                "a.UPI_ENABLED_FLAG, e.PRODUCT_CODE, e.MATURITY_DATE, e.INTEREST_RATE, "
                "e.REPRICING_FREQ, e.DORMANT_FLAG, e.ONBOARDING_CHANNEL, "
                "e.DIGITAL_SIGN_FLAG, e.STAFF_FLAG, e.HOLD_FLAG "
                f"FROM {h}.GAM a LEFT JOIN {c}.GAM_EXT e ON e.ACID = a.ACID"
            ),
        },
        {
            "name": "DIM_BRANCH", "requires": [("h", "SOL"), ("c", "SOL_EXT")],
            "sql": (
                "SELECT s.SOL_ID, s.BRANCH_NAME, s.BRANCH_CATEGORY, s.REGION_ZONE, "
                "s.STATE, s.IFSC_CODE, s.BRANCH_STATUS, s.AUTHORIZED_FOREX_DEALER_FLAG, "
                "s.CURRENCY_CHEST_FLAG, e.CONTROL_OFFICE, e.BRANCH_TYPE, "
                "e.PSL_BRANCH_FLAG, e.CURRENCY_CHEST_TYPE, e.WORKING_DAYS "
                f"FROM {h}.SOL s LEFT JOIN {c}.SOL_EXT e ON e.SOL_ID = s.SOL_ID"
            ),
        },
        {
            "name": "DIM_PRODUCT", "requires": [("c", "PRODUCT_MASTER")],
            "sql": "SELECT * FROM " + c + ".PRODUCT_MASTER",
        },
        {
            "name": "DIM_GL", "requires": [("c", "GL_MASTER"), ("c", "GL_CHART")],
            "sql": (
                "SELECT g.GL_CODE, g.GL_NAME, g.GL_TYPE, g.CURRENCY, g.SOL_ID, "
                "ch.PARENT_GL, ch.BALANCE_SHEET_FLAG "
                f"FROM {c}.GL_MASTER g LEFT JOIN {c}.GL_CHART ch ON ch.GL_CODE = g.GL_CODE"
            ),
        },
        {
            "name": "DIM_BORROWER", "requires": [("c", "BORROWER_ENTITY")],
            "sql": "SELECT * FROM " + c + ".BORROWER_ENTITY",
        },
        {
            "name": "DIM_MERCHANT", "requires": [("c", "UPI_MERCHANT")],
            "sql": "SELECT * FROM " + c + ".UPI_MERCHANT",
        },
        {
            "name": "DIM_CARD", "requires": [("c", "DEBIT_CARD_MASTER")],
            "sql": "SELECT * FROM " + c + ".DEBIT_CARD_MASTER",
        },
        {
            "name": "DIM_COUNTRY", "requires": [("c", "COUNTRY_RISK_MASTER")],
            "sql": "SELECT * FROM " + c + ".COUNTRY_RISK_MASTER",
        },
        {
            "name": "FACT_TRANSACTION", "requires": [("h", "HTD"), ("c", "HTD_EXT")],
            "sql": (
                "SELECT t.TRAN_ID, t.FORACID, t.TRAN_TYPE, t.CHANNEL_ID, t.TRAN_AMT_INR, "
                "t.CASH_TRAN_FLAG, t.SUSPICIOUS_RULE_HIT, t.REVERSAL_FLAG, "
                "t.IS_WEEKEND_HOLIDAY, t.TRAN_DATE, e.DR_CR_FLAG, e.TRAN_MODE, "
                "e.INSTRUMENT_NO, e.COUNTERPARTY_ACCT, e.COUNTERPARTY_NAME, "
                "e.COUNTERPARTY_BANK, e.COUNTERPARTY_IFSC, e.COUNTERPARTY_COUNTRY, "
                "e.TXN_CITY, e.PURPOSE_CODE, e.NARRATION, e.DEVICE_ID, e.IP_HASH "
                f"FROM {h}.HTD t LEFT JOIN {c}.HTD_EXT e ON e.TRAN_ID = t.TRAN_ID"
            ),
        },
        {
            "name": "FACT_LOAN", "requires": [("h", "TAM_LAM"), ("c", "TAM_LAM_EXT")],
            "sql": (
                "SELECT t.CONTRACT_ID, t.CUST_ID, t.SOL_ID, t.FORACID, t.CONTRACT_TYPE, "
                "t.NPA_STATUS, t.SMA_CLASSIFICATION, t.PRINCIPAL_AMT, "
                "t.CURRENT_OUTSTANDING_BAL, t.OVERDUE_PRINCIPAL, t.OVERDUE_INTEREST, "
                "t.INTEREST_RATE, t.DPD_COUNT, t.RESTRUCTURED_FLAG, "
                "t.COLLATERAL_VALUATION_AMT, e.BORROWER_ID, e.SANCTIONED_AMT, "
                "e.SANCTION_DATE, e.FUND_BASED_FLAG, e.FACILITY_TYPE, e.EXPOSURE_CATEGORY, "
                "e.PROVISION_AMT, e.RISK_WEIGHT, e.SECTOR_CODE, e.INDUSTRY_CODE, "
                "e.MSME_CLASS, e.PSL_CODE, e.NPA_DATE, e.SMA_DATE, e.RESTRUCTURE_TYPE, "
                "e.WRITE_OFF_AMT, e.WRITE_OFF_DATE, e.BORROWER_PAN_MASKED, e.GROUP_ID, "
                "e.MODIFIED_DURATION "
                f"FROM {h}.TAM_LAM t LEFT JOIN {c}.TAM_LAM_EXT e ON e.CONTRACT_ID = t.CONTRACT_ID"
            ),
        },
        {
            "name": "FACT_SWIFT", "requires": [("h", "SWIFT_MSG"), ("c", "SWIFT_MSG_EXT")],
            "sql": (
                "SELECT t.SWIFT_ID, t.FORACID, t.MESSAGE_TYPE, t.DIRECTION, "
                "t.OFAC_SANCTION_SCREEN_STATUS, t.SENDER_BIC, t.RECEIVER_BIC, "
                "t.BENEFICIARY_COUNTRY, t.ORIGINAL_AMOUNT, t.AMOUNT_INR, "
                "t.EXCHANGE_RATE, t.FIU_CBWTR_REPORTED, t.VALUE_DATE, "
                "e.REMITTER_NAME, e.REMITTER_COUNTRY, e.REMITTER_ADDRESS, "
                "e.BENEFICIARY_NAME, e.BENEFICIARY_ADDRESS, e.PURPOSE_CODE, e.AD_BANK_CODE "
                f"FROM {h}.SWIFT_MSG t LEFT JOIN {c}.SWIFT_MSG_EXT e ON e.SWIFT_ID = t.SWIFT_ID"
            ),
        },
        {
            "name": "FACT_UPI", "requires": [("c", "UPI_TRANSACTION")],
            "sql": "SELECT * FROM " + c + ".UPI_TRANSACTION",
        },
        {
            "name": "FACT_CARD", "requires": [("c", "DEBIT_CARD_TRANSACTION")],
            "sql": "SELECT * FROM " + c + ".DEBIT_CARD_TRANSACTION",
        },
        {
            "name": "FACT_ATM", "requires": [("c", "ATM_SWITCH")],
            "sql": "SELECT * FROM " + c + ".ATM_SWITCH",
        },
        {
            "name": "FACT_GL_BALANCE", "requires": [("c", "GL_BALANCE_DAILY")],
            "sql": "SELECT * FROM " + c + ".GL_BALANCE_DAILY",
        },
        {
            "name": "FACT_FX_POSITION", "requires": [("c", "FX_POSITION")],
            "sql": "SELECT * FROM " + c + ".FX_POSITION",
        },
        {
            "name": "FACT_INVESTMENT", "requires": [("c", "INVESTMENT_PORTFOLIO")],
            "sql": "SELECT * FROM " + c + ".INVESTMENT_PORTFOLIO",
        },
        {
            "name": "FACT_TREASURY_DEAL", "requires": [("c", "TREASURY_DEAL")],
            "sql": "SELECT * FROM " + c + ".TREASURY_DEAL",
        },
        {
            "name": "FACT_ALM_POSITION",
            "requires": [("c", "DEPOSIT_MASTER"), ("c", "BORROWING_MASTER")],
            "sql": (
                "SELECT 'DEPOSIT' AS POSITION_TYPE, DEPOSIT_ID AS POSITION_ID, 1 AS SIDE_SIGN, "
                "AMOUNT, INTEREST_RATE, START_DATE, MATURITY_DATE, REPRICING_FREQ, "
                "BUCKET, PRODUCT_CODE AS PRODUCT, NULL AS INSTRUMENT_TYPE "
                f"FROM {c}.DEPOSIT_MASTER "
                "UNION ALL "
                "SELECT 'BORROWING' AS POSITION_TYPE, BORROWING_ID AS POSITION_ID, -1 AS SIDE_SIGN, "
                "AMOUNT, INTEREST_RATE, START_DATE, MATURITY_DATE, 'BULLET' AS REPRICING_FREQ, "
                "'BORROWING' AS BUCKET, NULL AS PRODUCT, INSTRUMENT_TYPE "
                f"FROM {c}.BORROWING_MASTER"
            ),
        },
        {
            "name": "FACT_COLLATERAL", "requires": [("c", "COLLATERAL_REGISTER")],
            "sql": "SELECT * FROM " + c + ".COLLATERAL_REGISTER",
        },
        {
            "name": "FACT_KYC_DOCUMENT", "requires": [("c", "KYC_DOCUMENT")],
            "sql": "SELECT * FROM " + c + ".KYC_DOCUMENT",
        },
        {
            "name": "FACT_AML_ALERT", "requires": [("c", "AML_ALERT")],
            "sql": "SELECT * FROM " + c + ".AML_ALERT",
        },
        {
            "name": "FACT_AML_CASE", "requires": [("c", "AML_CASE")],
            "sql": "SELECT * FROM " + c + ".AML_CASE",
        },
        {
            "name": "FACT_SCREENING", "requires": [("c", "SCREENING_RESULT")],
            "sql": "SELECT * FROM " + c + ".SCREENING_RESULT",
        },
        {
            "name": "FACT_TRADE", "requires": [("c", "TRADE_DOCUMENT")],
            "sql": "SELECT * FROM " + c + ".TRADE_DOCUMENT",
        },
    ]


def build_star(cursor, database: str, available: Set[Tuple[str, str]]) -> Dict[str, Any]:
    built, skipped, errors, rows = [], [], [], {}
    for spec in _star_specs(database):
        missing = [f"{place}.{table}" for place, table in spec["requires"]
                   if (place, table) not in available]
        if missing:
            skipped.append(f"{spec['name']}: missing {', '.join(missing)}")
            continue
        fqtn = f"{database}.{STAR_SCHEMA}.{spec['name']}"
        try:
            cursor.execute(f"CREATE OR REPLACE TABLE {fqtn} AS {spec['sql']}")
            rows[spec["name"]] = _count(cursor, fqtn)
            built.append(spec["name"])
        except Exception as exc:
            errors.append(f"{spec['name']}: {str(exc)[:180]}")
    return {"status": "built" if not errors else "partial", "tables": len(built),
            "star": built, "rows": rows, "skipped": skipped, "errors": errors[:8]}


# ----------------------------------------------------------------------------
# Report marts
# ----------------------------------------------------------------------------
def _report_specs(database: str) -> List[Dict[str, Any]]:
    h = f"{database}.L1_HARMONIZED"
    c = f"{database}.{CUR_SCHEMA}"
    star = f"{database}.{STAR_SCHEMA}"
    return [
        # ---- FIU / AML -----------------------------------------------------
        {"schema": "RPT_FIU", "name": "AML_ALERT_FUNNEL",
         "requires": [("star", "FACT_AML_ALERT"), ("star", "FACT_AML_CASE")],
         "sql": (
             "SELECT a.SEVERITY, a.STATUS, a.RULE_CODE, a.RULE_NAME, "
             "COUNT(*) AS ALERTS, ROUND(AVG(a.SCORE), 2) AS AVG_SCORE, "
             "COUNT(DISTINCT a.CUST_ID) AS CUSTOMERS, "
             "COUNT_IF(a.DISPOSITION = 'STR_FILED') AS STR_FILED_ALERTS, "
             "SUM(IFF(c.CASE_ID IS NOT NULL, 1, 0)) AS ESCALATED_CASES, "
             "CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {star}.FACT_AML_ALERT a "
             f"LEFT JOIN {star}.FACT_AML_CASE c ON c.ALERT_ID = a.ALERT_ID "
             "GROUP BY 1, 2, 3, 4"
         )},
        {"schema": "RPT_FIU", "name": "STR_REGISTER",
         "requires": [("c", "STR_REGISTER")],
         "sql": (
             "SELECT SUSPICION_TYPE, STATUS, COUNT(*) AS STR_COUNT, "
             "SUM(AMOUNT_INR) AS TOTAL_AMOUNT_INR, MIN(FILED_DATE) AS FIRST_FILED, "
             "MAX(FILED_DATE) AS LAST_FILED, CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {c}.STR_REGISTER GROUP BY 1, 2"
         )},
        {"schema": "RPT_FIU", "name": "CTR_CASH_VOUCHERS",
         "requires": [("h", "VCT")],
         "sql": (
             "SELECT SOL_ID, TRAN_NATURE, COUNT(*) AS VOUCHERS, "
             "SUM(TOTAL_CASH_AMOUNT) AS TOTAL_CASH_AMOUNT, "
             "SUM(IFF(CTR_REPORTABLE, 1, 0)) AS CTR_REPORTABLE, "
             "SUM(IFF(FORM60_SUBMITTED, 1, 0)) AS FORM60_SUBMITTED, "
             "SUM(FAKE_NOTE_COUNT) AS FAKE_NOTES, CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {h}.VCT GROUP BY 1, 2"
         )},
        {"schema": "RPT_FIU", "name": "CBWTR_SWIFT",
         "requires": [("star", "FACT_SWIFT")],
         "sql": (
             "SELECT MESSAGE_TYPE, DIRECTION, BENEFICIARY_COUNTRY, "
             "COUNT(*) AS MESSAGES, SUM(AMOUNT_INR) AS TOTAL_AMOUNT_INR, "
             "SUM(IFF(FIU_CBWTR_REPORTED, 1, 0)) AS CBWTR_REPORTED, "
             "CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {star}.FACT_SWIFT GROUP BY 1, 2, 3"
         )},
        {"schema": "RPT_FIU", "name": "WATCHLIST_SCREENING",
         "requires": [("c", "SCREENING_RESULT"), ("c", "WATCHLIST_ENTRY")],
         "sql": (
             "SELECT w.LIST_SOURCE, w.RISK_LEVEL, s.STATUS, COUNT(*) AS SCREENINGS, "
             "ROUND(AVG(s.MATCH_SCORE), 2) AS AVG_MATCH_SCORE, "
             "COUNT_IF(s.MATCH_SCORE >= 90) AS HIGH_MATCHES, CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {c}.SCREENING_RESULT s "
             f"LEFT JOIN {c}.WATCHLIST_ENTRY w ON w.ENTRY_ID = s.ENTRY_ID "
             "GROUP BY 1, 2, 3"
         )},
        {"schema": "RPT_FIU", "name": "KYC_COVERAGE",
         "requires": [("c", "KYC_DOCUMENT"), ("star", "DIM_CUSTOMER")],
         "sql": (
             "SELECT d.DOC_TYPE, d.STATUS, COUNT(*) AS DOCUMENTS, "
             "COUNT(DISTINCT d.CUST_ID) AS CUSTOMERS, "
             "COUNT_IF(d.EXPIRY_DATE < CURRENT_DATE()) AS EXPIRED, "
             "COUNT_IF(d.VERIFIED_DATE IS NULL) AS NOT_VERIFIED, "
             "CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {c}.KYC_DOCUMENT d GROUP BY 1, 2"
         )},
        # ---- RBI ADF / CIMS / PSL / CRR-SLR --------------------------------
        {"schema": "RPT_RBI", "name": "ADF_ASSET_CLASSIFICATION",
         "requires": [("star", "FACT_LOAN")],
         "sql": (
             "SELECT COALESCE(NPA_STATUS, 'STANDARD') AS ASSET_CLASS, "
             "COALESCE(SMA_CLASSIFICATION, 'NA') AS SMA_CLASS, "
             "COALESCE(FACILITY_TYPE, 'UNKNOWN') AS FACILITY_TYPE, "
             "COUNT(*) AS ACCOUNTS, SUM(CURRENT_OUTSTANDING_BAL) AS OUTSTANDING, "
             "SUM(OVERDUE_PRINCIPAL + OVERDUE_INTEREST) AS OVERDUE_AMT, "
             "SUM(PROVISION_AMT) AS PROVISION_AMT, "
             "ROUND(AVG(DPD_COUNT), 2) AS AVG_DPD, MAX(DPD_COUNT) AS MAX_DPD, "
             "CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {star}.FACT_LOAN GROUP BY 1, 2, 3"
         )},
        {"schema": "RPT_RBI", "name": "CIMS_CREDIT_EXPOSURE",
         "requires": [("star", "FACT_LOAN")],
         "sql": (
             "SELECT BORROWER_ID, MSME_CLASS, SECTOR_CODE, INDUSTRY_CODE, "
             "COUNT(*) AS FACILITIES, SUM(SANCTIONED_AMT) AS SANCTIONED_TOTAL, "
             "SUM(CURRENT_OUTSTANDING_BAL) AS OUTSTANDING_TOTAL, "
             "SUM(PROVISION_AMT) AS PROVISION_TOTAL, MAX(RISK_WEIGHT) AS MAX_RISK_WEIGHT, "
             "COUNT_IF(NPA_DATE IS NOT NULL) AS NPA_FACILITIES, CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {star}.FACT_LOAN GROUP BY 1, 2, 3, 4"
         )},
        {"schema": "RPT_RBI", "name": "PSL_CLASSIFICATION",
         "requires": [("c", "TAM_LAM_EXT"), ("c", "PSL_MASTER")],
         "sql": (
             "SELECT COALESCE(p.PSL_CATEGORY, 'NON_PSL') AS PSL_CATEGORY, "
             "COALESCE(p.SUB_CATEGORY, 'NA') AS SUB_CATEGORY, e.SECTOR_CODE, "
             "COUNT(*) AS ACCOUNTS, SUM(e.SANCTIONED_AMT) AS SANCTIONED_TOTAL, "
             "SUM(e.PROVISION_AMT) AS PROVISION_TOTAL, CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {c}.TAM_LAM_EXT e LEFT JOIN {c}.PSL_MASTER p ON p.PSL_CODE = e.PSL_CODE "
             "GROUP BY 1, 2, 3"
         )},
        {"schema": "RPT_RBI", "name": "NPA_PROVISIONING",
         "requires": [("star", "FACT_LOAN")],
         "sql": (
             "SELECT COALESCE(NPA_STATUS, 'STANDARD') AS NPA_STATUS, "
             "COUNT(*) AS LOANS, SUM(CURRENT_OUTSTANDING_BAL) AS OUTSTANDING, "
             "SUM(PROVISION_AMT) AS PROVISION_AMT, SUM(WRITE_OFF_AMT) AS WRITE_OFF_AMT, "
             "ROUND(SUM(PROVISION_AMT) / NULLIF(SUM(CURRENT_OUTSTANDING_BAL), 0) * 100, 2) "
             "AS PROVISION_COVERAGE_PCT, CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {star}.FACT_LOAN GROUP BY 1"
         )},
        {"schema": "RPT_RBI", "name": "RESTRUCTURE_SUMMARY",
         "requires": [("c", "RESTRUCTURE_HISTORY")],
         "sql": (
             "SELECT RESTRUCTURE_TYPE, RELIEF_TYPE, COUNT(*) AS RESTRUCTURES, "
             "SUM(RESCHEDULED_AMT) AS RESCHEDULED_AMT, "
             "ROUND(AVG(MORATORIUM_DAYS), 1) AS AVG_MORATORIUM_DAYS, "
             "CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {c}.RESTRUCTURE_HISTORY GROUP BY 1, 2"
         )},
        {"schema": "RPT_RBI", "name": "CRR_SLR_POSITION",
         "requires": [("c", "CRR_SLR_POSITION")],
         "sql": (
             "SELECT AS_OF_DATE, NDTL, CRR_REQUIRED, CRR_HELD, "
             "ROUND((CRR_HELD - CRR_REQUIRED) / NULLIF(CRR_REQUIRED, 0) * 100, 2) AS CRR_GAP_PCT, "
             "SLR_REQUIRED, SLR_HELD, "
             "ROUND((SLR_HELD - SLR_REQUIRED) / NULLIF(SLR_REQUIRED, 0) * 100, 2) AS SLR_GAP_PCT, "
             "CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {c}.CRR_SLR_POSITION"
         )},
        # ---- ALM / treasury ------------------------------------------------
        {"schema": "RPT_ALM", "name": "MATURITY_BUCKET",
         "requires": [("star", "FACT_ALM_POSITION")],
         "sql": (
             "SELECT POSITION_TYPE, BUCKET, COUNT(*) AS POSITIONS, "
             "SUM(AMOUNT) AS TOTAL_AMOUNT, ROUND(AVG(INTEREST_RATE), 4) AS AVG_RATE, "
             "MIN(MATURITY_DATE) AS EARLIEST_MATURITY, MAX(MATURITY_DATE) AS LATEST_MATURITY, "
             "CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {star}.FACT_ALM_POSITION GROUP BY 1, 2"
         )},
        {"schema": "RPT_ALM", "name": "FX_NOP",
         "requires": [("star", "FACT_FX_POSITION")],
         "sql": (
             "SELECT AS_OF_DATE, CCY, SUM(OPEN_POSITION) AS NET_OPEN_POSITION, "
             "SUM(NOP_INR) AS NET_OPEN_POSITION_INR, SUM(LIMIT_AMT) AS LIMIT_AMT, "
             "MAX(UTILISATION_PCT) AS MAX_UTILISATION_PCT, CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {star}.FACT_FX_POSITION GROUP BY 1, 2"
         )},
        {"schema": "RPT_ALM", "name": "INVESTMENT_CLASS",
         "requires": [("star", "FACT_INVESTMENT")],
         "sql": (
             "SELECT HTM_AFS_HFT, SECURITY_TYPE, COUNT(*) AS SECURITIES, "
             "SUM(BOOK_VALUE) AS BOOK_VALUE, SUM(MARKET_VALUE) AS MARKET_VALUE, "
             "ROUND(SUM(MARKET_VALUE) - SUM(BOOK_VALUE), 2) AS UNREALISED_GAIN_LOSS, "
             "ROUND(AVG(YIELD_PCT), 4) AS AVG_YIELD, "
             "ROUND(AVG(MODIFIED_DURATION), 4) AS AVG_MODIFIED_DURATION, "
             "CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {star}.FACT_INVESTMENT GROUP BY 1, 2"
         )},
        {"schema": "RPT_ALM", "name": "TREASURY_DEALS",
         "requires": [("star", "FACT_TREASURY_DEAL")],
         "sql": (
             "SELECT DEAL_TYPE, BUY_SELL, SETTLEMENT_STATUS, COUNT(*) AS DEALS, "
             "SUM(AMOUNT) AS DEAL_AMOUNT, ROUND(AVG(RATE), 6) AS AVG_RATE, "
             "CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {star}.FACT_TREASURY_DEAL GROUP BY 1, 2, 3"
         )},
        {"schema": "RPT_ALM", "name": "GL_TRIAL_BALANCE",
         "requires": [("star", "FACT_GL_BALANCE")],
         "sql": (
             "SELECT AS_OF_DATE, GL_CODE, SOL_ID, CCY, "
             "SUM(OPENING_BAL) AS OPENING_BAL, SUM(DEBIT_AMT) AS DEBIT_TOTAL, "
             "SUM(CREDIT_AMT) AS CREDIT_TOTAL, SUM(CLOSING_BAL) AS CLOSING_BAL, "
             "CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {star}.FACT_GL_BALANCE GROUP BY 1, 2, 3, 4"
         )},
        {"schema": "RPT_ALM", "name": "LIQUIDITY_POSITION",
         "requires": [("star", "FACT_ALM_POSITION"), ("star", "FACT_GL_BALANCE")],
         "sql": (
             "WITH deposits AS (SELECT SUM(AMOUNT) AS AMT FROM "
             f"{star}.FACT_ALM_POSITION WHERE POSITION_TYPE = 'DEPOSIT'), "
             "assets AS (SELECT SUM(IFF(CLOSING_BAL > 0, CLOSING_BAL, 0)) AS AMT FROM "
             f"{star}.FACT_GL_BALANCE) "
             "SELECT d.AMT AS TOTAL_DEPOSITS, a.AMT AS TOTAL_ASSETS, "
             "ROUND(a.AMT / NULLIF(d.AMT, 0) * 100, 2) AS LIQUIDITY_RATIO_PCT, "
             "CURRENT_TIMESTAMP() AS BUILT_AT FROM deposits d CROSS JOIN assets a"
         )},
        # ---- UPI / cards / ATM / NEFT -------------------------------------
        {"schema": "RPT_UPI", "name": "UPI_VOLUME",
         "requires": [("star", "FACT_UPI")],
         "sql": (
             "SELECT TXN_TYPE, STATUS, INITIATION_MODE, COUNT(*) AS TXNS, "
             "SUM(AMOUNT) AS TOTAL_AMOUNT, ROUND(AVG(AMOUNT), 2) AS AVG_AMOUNT, "
             "COUNT_IF(DISPUTE_FLAG) AS DISPUTED, CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {star}.FACT_UPI GROUP BY 1, 2, 3"
         )},
        {"schema": "RPT_UPI", "name": "UPI_MERCHANT_CATEGORY",
         "requires": [("star", "FACT_UPI"), ("c", "MCC_MASTER")],
         "sql": (
             "SELECT m.CATEGORY, f.MCC, COUNT(*) AS TXNS, SUM(f.AMOUNT) AS TOTAL_AMOUNT, "
             "COUNT(DISTINCT f.PAYEE_VPA) AS MERCHANTS, CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {star}.FACT_UPI f LEFT JOIN {c}.MCC_MASTER m ON m.MCC = f.MCC "
             "GROUP BY 1, 2"
         )},
        {"schema": "RPT_UPI", "name": "UPI_DISPUTES",
         "requires": [("c", "UPI_DISPUTE")],
         "sql": (
             "SELECT REASON_CODE, STATUS, COUNT(*) AS DISPUTES, "
             "SUM(ADJUDICATED_AMT) AS ADJUDICATED_AMT, "
             "SUM(SETTLEMENT_IMPACT) AS SETTLEMENT_IMPACT, "
             "CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {c}.UPI_DISPUTE GROUP BY 1, 2"
         )},
        {"schema": "RPT_UPI", "name": "UPI_SETTLEMENT",
         "requires": [("c", "UPI_SETTLEMENT")],
         "sql": (
             "SELECT NPCI_CYCLE, STATUS, COUNT(*) AS SETTLEMENTS, "
             "SUM(CREDITS) AS CREDITS, SUM(DEBITS) AS DEBITS, "
             "SUM(NET_POSITION) AS NET_POSITION, CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {c}.UPI_SETTLEMENT GROUP BY 1, 2"
         )},
        {"schema": "RPT_UPI", "name": "DEBIT_CARD_SPEND",
         "requires": [("star", "FACT_CARD")],
         "sql": (
             "SELECT CHANNEL, FOREIGN_FLAG, COUNTRY, COUNT(*) AS TXNS, "
             "SUM(INR_AMOUNT) AS TOTAL_INR_AMOUNT, ROUND(AVG(INR_AMOUNT), 2) AS AVG_INR_AMOUNT, "
             "COUNT_IF(DISPUTE_FLAG) AS DISPUTES, CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {star}.FACT_CARD GROUP BY 1, 2, 3"
         )},
        {"schema": "RPT_UPI", "name": "ATM_ACTIVITY",
         "requires": [("star", "FACT_ATM")],
         "sql": (
             "SELECT TXN_TYPE, STATUS, SOL_ID, COUNT(*) AS TXNS, "
             "SUM(AMOUNT) AS TOTAL_AMOUNT, ROUND(AVG(DOWNTIME_MIN), 2) AS AVG_DOWNTIME_MIN, "
             "CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {star}.FACT_ATM GROUP BY 1, 2, 3"
         )},
        {"schema": "RPT_UPI", "name": "NEFT_RTGS_BATCH",
         "requires": [("c", "NEFT_RTGS_BATCH")],
         "sql": (
             "SELECT BATCH_TYPE, DIRECTION, STATUS, COUNT(*) AS BATCHES, "
             "SUM(TXN_COUNT) AS TXNS, SUM(TOTAL_AMOUNT) AS TOTAL_AMOUNT, "
             "CURRENT_TIMESTAMP() AS BUILT_AT "
             f"FROM {c}.NEFT_RTGS_BATCH GROUP BY 1, 2, 3"
         )},
    ]


def build_reports(cursor, database: str, available: Set[Tuple[str, str]]) -> Dict[str, Any]:
    built, skipped, errors, rows = [], [], [], {}
    for spec in _report_specs(database):
        missing = [f"{place}.{table}" for place, table in spec["requires"]
                   if (place, table) not in available]
        if missing:
            skipped.append(f"{spec['schema']}.{spec['name']}: missing {', '.join(missing)}")
            continue
        fqtn = f"{database}.{spec['schema']}.{spec['name']}"
        try:
            cursor.execute(f"CREATE OR REPLACE TABLE {fqtn} AS {spec['sql']}")
            rows[spec["name"]] = _count(cursor, fqtn)
            built.append(f"{spec['schema']}.{spec['name']}")
        except Exception as exc:
            errors.append(f"{spec['schema']}.{spec['name']}: {str(exc)[:180]}")
    return {"status": "built" if not errors else "partial", "reports": built,
            "rows": rows, "skipped": skipped, "errors": errors[:8]}


# ----------------------------------------------------------------------------
# Orchestration
# ----------------------------------------------------------------------------
def _available(cursor, database: str, include_staging: bool = True) -> Set[Tuple[str, str]]:
    mapping = {
        "h": "L1_HARMONIZED",
        "c": CUR_SCHEMA,
        "star": STAR_SCHEMA,
    }
    available: Set[Tuple[str, str]] = set()
    for place, schema in mapping.items():
        for table in _infoschema(cursor, database, schema):
            available.add((place, table))
    if include_staging:
        for table in _infoschema(cursor, database, "L0_STAGING"):
            available.add(("h", table))
            available.add(("c", table))
    return available


def _execute(cursor, database: str, stage: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"stage": stage, "at": _now()}
    if stage in ("all", "raw"):
        result["l0_hist"] = load_history(cursor, database)
    if stage in ("all", "l1"):
        result["l1_current"] = build_current(cursor, database)
        result["l1_scd2"] = build_scd2(cursor, database)
    available = _available(cursor, database)
    if stage in ("all", "star"):
        result["l2_star"] = build_star(cursor, database, available)
        available = _available(cursor, database)
    if stage in ("all", "rpt"):
        result["reports"] = build_reports(cursor, database, available)
    return result


def build(stage: str = "all", run_id: str = "") -> Dict[str, Any]:
    """Run raw/L0 -> L1 -> L2 -> reports. ``stage`` limits the work."""
    stage = str(stage or "all").lower()
    if not _enabled():
        return {"status": "skipped", "reason": "NANOPRO_BANK_LAYERS is off"}
    if not _LOCK.acquire(blocking=False):
        return {"status": "running", "message": "A bank layer build is already running."}
    started = time.time()
    STATE.update({"running": True, "last_run": _now(), "errors": []})
    from app.core import snowflake_client

    database = str(snowflake_client.load_config().get("database") or "BANK_DB").strip()
    try:
        connection = _connect()
    except Exception as exc:
        STATE.update({"running": False, "status": "unavailable"})
        return {"status": "unavailable", "error": str(exc)[:240]}
    try:
        cursor = connection.cursor()
        _ensure_schemas(cursor, database)
        result = _execute(cursor, database, stage)
        connection.commit()
        errors: List[str] = []
        for payload in result.values():
            if isinstance(payload, dict):
                errors.extend(payload.get("errors") or [])
        status = "partial" if errors else "success"
        summary = {
            "status": status,
            "database": database,
            "run_id": run_id,
            "stage": stage,
            "l0_hist": (result.get("l0_hist") or {}).get("rows"),
            "l1": (result.get("l1_current") or {}).get("tables"),
            "scd2": len((result.get("l1_scd2") or {}).get("tables") or []),
            "star": (result.get("l2_star") or {}).get("tables"),
            "reports": len((result.get("reports") or {}).get("reports") or []),
            "stage_status": {name: str(payload.get("status") or "")
                             for name, payload in result.items() if isinstance(payload, dict)},
            "elapsed_s": round(time.time() - started, 2),
            "errors": errors[:5],
        }
        STATE.update({"status": status, "running": False, "database": database,
                      "stages": result, "errors": errors[:8]})
        log_event(
            f"[BankLayers] {status}: L0_HIST {summary['l0_hist'] or 0} events, "
            f"L1 {summary['l1'] or 0} tables, SCD2 {summary['scd2']} tables, "
            f"star {summary['star'] or 0} tables, reports {summary['reports']}",
            component="BankLayers", level="INFO" if status == "success" else "WARNING",
        )
        return summary
    except Exception as exc:
        STATE.update({"running": False, "status": "error", "errors": [str(exc)[:400]]})
        log_event(f"[BankLayers] build failed: {exc}", level="ERROR", component="BankLayers")
        return {"status": "error", "error": str(exc)[:240]}
    finally:
        try:
            connection.close()
        except Exception:
            pass
        _LOCK.release()


def catalogue(database: str = "BANK_DB") -> Dict[str, Any]:
    """Static layer catalogue: schemas, star tables and report marts."""
    star = _star_specs(database)
    reports = _report_specs(database)
    return {
        "schemas": {
            "raw": RAW_PREFIX,
            "l0_history": HIST_SCHEMA,
            "l1_current": CUR_SCHEMA,
            "l1_scd2": SCD_SCHEMA,
            "l2_star": STAR_SCHEMA,
            "reports": list(REPORT_SCHEMAS),
        },
        "star": [{"name": spec["name"], "requires": spec["requires"]} for spec in star],
        "reports": [{"schema": spec["schema"], "name": spec["name"],
                     "requires": spec["requires"]} for spec in reports],
        "counts": {"star": len(star), "reports": len(reports)},
    }


def status() -> Dict[str, Any]:
    return {
        "status": STATE.get("status"),
        "running": STATE.get("running"),
        "last_run": STATE.get("last_run"),
        "database": STATE.get("database"),
        "errors": STATE.get("errors") or [],
    }
