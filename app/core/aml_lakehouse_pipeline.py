"""End-to-end AML lakehouse pipeline.

Source (DuckDB) -> Parquet in AWS S3 -> Snowflake L0 raw -> L1 harmonized ->
L2 curated -> business report delivered by email / WhatsApp / Telegram.

Runs are tracked in-memory and persisted under data/aml_runs/<run_id>.json so
the Data Modeling chat and the REST API can report progress.
"""

from __future__ import annotations

import json
import os
import random
import threading
import time
import traceback
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

DB = "BANK_DB"
L0 = "L0_STAGING"
L1 = "L1_HARMONIZED"
L2 = "L2_CURATED"
SOURCE_SYSTEM = "CORE_BANKING_DUCKDB"
REPORT_EMAIL = os.environ.get("AML_REPORT_EMAIL", "nanoproaistudio@gmail.com")
WHATSAPP_TO = os.environ.get("AML_WHATSAPP_TO", "918433755448")
DEFAULT_S3_BUCKET = "nanopro-data-lake-765865641438"
RUN_DIR = Path("data/aml_runs")
REPORT_DIR = Path("data/reports/aml")
SOURCE_DB = Path("data/lakehouse/aml_source.duckdb")

HIGH_RISK_COUNTRIES = ("IR", "KP", "SY", "MM", "AF", "PK", "YE", "LY", "SO", "SS")
COUNTRY_CODES = ("IN", "IN", "IN", "IN", "AE", "SG", "US", "GB", "HK", "CH", "MU",
                 "IR", "PK", "MM", "AF", "SY", "NP", "BD", "LK", "MY")
CHANNELS = ("UPI", "NEFT", "RTGS", "IMPS", "ATM", "CASH_DEPOSIT", "CASH_WITHDRAWAL",
            "MOBILE_BANKING", "INTERNET_BANKING", "BRANCH", "SWIFT")
TXN_TYPES = ("TRANSFER", "DEPOSIT", "WITHDRAWAL", "PAYMENT", "COLLECTION", "FX_CONVERSION")
STATUSES = ("SETTLED", "SETTLED", "SETTLED", "PENDING", "FAILED", "REVERSED")
PRODUCTS = ("SAVINGS", "CURRENT", "OVERDRAFT", "TERM_DEPOSIT", "CREDIT_CARD")
SEGMENTS = ("RETAIL", "RETAIL", "HNI", "CORPORATE", "SME")
RISK_RATINGS = ("LOW", "LOW", "MEDIUM", "MEDIUM", "HIGH", "CRITICAL")
LIST_SOURCES = ("UNSC", "OFAC", "RBI_CAUTION", "INTERPOL", "FATF")
ALERT_RULES = (
    ("AML_R001", "STRUCTURING"),
    ("AML_R002", "HIGH_VALUE_CASH"),
    ("AML_R003", "CROSS_BORDER_HIGH_RISK"),
    ("AML_R004", "WATCHLIST_MATCH"),
    ("AML_R005", "VELOCITY"),
    ("AML_R006", "PEP_ACTIVITY"),
)

FIRST_NAMES = ("Aarav", "Vivaan", "Aditya", "Rohan", "Kabir", "Ishaan", "Arjun", "Reyansh",
               "Sai", "Krishna", "Ananya", "Diya", "Aadhya", "Saanvi", "Pari", "Riya",
               "Meera", "Kavya", "Nisha", "Pooja", "Rahul", "Amit", "Vikram", "Sanjay",
               "Priya", "Neha", "Sneha", "Kiran", "Farhan", "Imran")
LAST_NAMES = ("Sharma", "Patel", "Singh", "Kumar", "Gupta", "Mehta", "Joshi", "Nair",
              "Reddy", "Iyer", "Desai", "Shah", "Khan", "Ansari", "Verma", "Chopra",
              "Bhat", "Menon", "Kulkarni", "Pillai")

TABLE_ORDER = ("AML_BRANCH_RAW", "AML_CUSTOMER_RAW", "AML_ACCOUNT_RAW", "AML_KYC_RAW",
               "AML_TRANSACTION_RAW", "AML_WATCHLIST_RAW", "AML_ALERT_RAW")

DDL: Dict[str, List[Tuple[str, str]]] = {
    "AML_BRANCH_RAW": [
        ("BRANCH_CODE", "VARCHAR(16)"), ("BRANCH_NAME", "VARCHAR(120)"),
        ("REGION", "VARCHAR(32)"), ("STATE", "VARCHAR(64)"), ("IFSC", "VARCHAR(16)"),
    ],
    "AML_CUSTOMER_RAW": [
        ("CUSTOMER_ID", "VARCHAR(24)"), ("FULL_NAME", "VARCHAR(160)"),
        ("DOB", "VARCHAR(12)"), ("GENDER", "VARCHAR(12)"), ("PAN", "VARCHAR(16)"),
        ("AADHAAR_LAST4", "VARCHAR(8)"), ("PHONE", "VARCHAR(20)"), ("EMAIL", "VARCHAR(160)"),
        ("OCCUPATION", "VARCHAR(64)"), ("ANNUAL_INCOME_INR", "NUMBER(18,2)"),
        ("CUSTOMER_SINCE", "VARCHAR(12)"), ("BRANCH_CODE", "VARCHAR(16)"),
        ("CUSTOMER_TYPE", "VARCHAR(24)"), ("SEGMENT", "VARCHAR(24)"),
    ],
    "AML_ACCOUNT_RAW": [
        ("ACCOUNT_ID", "VARCHAR(24)"), ("CUSTOMER_ID", "VARCHAR(24)"),
        ("ACCOUNT_TYPE", "VARCHAR(32)"), ("BRANCH_CODE", "VARCHAR(16)"),
        ("OPEN_DATE", "VARCHAR(12)"), ("CURRENCY", "VARCHAR(8)"),
        ("STATUS", "VARCHAR(16)"), ("CURRENT_BALANCE_INR", "NUMBER(18,2)"),
        ("PRODUCT_CODE", "VARCHAR(24)"),
    ],
    "AML_KYC_RAW": [
        ("KYC_ID", "VARCHAR(24)"), ("CUSTOMER_ID", "VARCHAR(24)"),
        ("KYC_STATUS", "VARCHAR(24)"), ("RISK_RATING", "VARCHAR(16)"),
        ("PEP_FLAG", "BOOLEAN"), ("LAST_REVIEW_DATE", "VARCHAR(12)"),
        ("ID_DOCUMENT_TYPE", "VARCHAR(24)"), ("ID_DOCUMENT_NUMBER", "VARCHAR(32)"),
        ("ADDRESS_COUNTRY", "VARCHAR(8)"), ("SOURCE_OF_FUNDS", "VARCHAR(32)"),
    ],
    "AML_TRANSACTION_RAW": [
        ("TXN_ID", "VARCHAR(40)"), ("ACCOUNT_ID", "VARCHAR(24)"),
        ("CUSTOMER_ID", "VARCHAR(24)"), ("TXN_TIMESTAMP", "TIMESTAMP_NTZ"),
        ("TXN_TYPE", "VARCHAR(32)"), ("CHANNEL", "VARCHAR(32)"),
        ("AMOUNT_INR", "NUMBER(18,2)"), ("CURRENCY", "VARCHAR(8)"),
        ("DR_CR", "VARCHAR(4)"), ("COUNTERPARTY_ID", "VARCHAR(24)"),
        ("COUNTERPARTY_NAME", "VARCHAR(160)"), ("COUNTERPARTY_COUNTRY", "VARCHAR(8)"),
        ("COUNTERPARTY_BANK", "VARCHAR(64)"), ("PURPOSE_CODE", "VARCHAR(24)"),
        ("BRANCH_CODE", "VARCHAR(16)"), ("STATUS", "VARCHAR(16)"), ("IS_CASH", "BOOLEAN"),
    ],
    "AML_WATCHLIST_RAW": [
        ("WATCHLIST_ID", "VARCHAR(24)"), ("ENTITY_NAME", "VARCHAR(160)"),
        ("ALIAS", "VARCHAR(160)"), ("ENTITY_TYPE", "VARCHAR(24)"),
        ("LIST_SOURCE", "VARCHAR(24)"), ("COUNTRY", "VARCHAR(8)"),
        ("RISK_LEVEL", "VARCHAR(16)"), ("LISTED_DATE", "VARCHAR(12)"),
    ],
    "AML_ALERT_RAW": [
        ("ALERT_ID", "VARCHAR(32)"), ("TXN_ID", "VARCHAR(40)"), ("ACCOUNT_ID", "VARCHAR(24)"),
        ("ALERT_TYPE", "VARCHAR(48)"), ("RULE_CODE", "VARCHAR(16)"),
        ("ALERT_SCORE", "NUMBER(6,2)"), ("ALERT_TIMESTAMP", "TIMESTAMP_NTZ"),
        ("STATUS", "VARCHAR(16)"),
    ],
}

META_COLUMNS = [("_BATCH_ID", "VARCHAR(48)"), ("_LOAD_TS", "TIMESTAMP_NTZ"),
                ("_SOURCE_SYSTEM", "VARCHAR(64)")]

_RUNS: Dict[str, Dict[str, Any]] = {}
_RUNS_LOCK = threading.Lock()
_PIPELINE_LOCK = threading.Lock()


# ---------------------------------------------------------------------------
# time helpers
# ---------------------------------------------------------------------------

def _now_ist() -> datetime:
    return datetime.utcnow() + timedelta(hours=5, minutes=30)


def _ts(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _report_date() -> str:
    return (_now_ist() - timedelta(days=1)).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# run registry
# ---------------------------------------------------------------------------

def _persist(run: Dict[str, Any]) -> None:
    try:
        RUN_DIR.mkdir(parents=True, exist_ok=True)
        safe = dict(run)
        (RUN_DIR / f"{run['run_id']}.json").write_text(
            json.dumps(safe, indent=2, default=str), encoding="utf-8"
        )
    except Exception:
        pass


def _new_run(mode: str, user: str) -> Dict[str, Any]:
    run_id = f"aml_{datetime.utcnow():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:6]}"
    run: Dict[str, Any] = {
        "run_id": run_id,
        "mode": mode.upper(),
        "user": user,
        "status": "running",
        "started_at": _ts(_now_ist()),
        "finished_at": None,
        "batch_id": f"{mode.upper()}_{datetime.utcnow():%Y%m%d%H%M%S}_{uuid.uuid4().hex[:4].upper()}",
        "stages": [],
        "counts": {},
        "s3_objects": [],
        "snowflake": {},
        "report": {},
        "delivery": {},
        "error": None,
    }
    return run


def _stage(run: Dict[str, Any], name: str, status: str, detail: Any = None) -> None:
    for entry in run["stages"]:
        if entry["stage"] == name:
            entry.update({"status": status, "detail": detail,
                          "at": _ts(_now_ist())})
            break
    else:
        run["stages"].append({"stage": name, "status": status, "detail": detail,
                              "at": _ts(_now_ist())})
    _persist(run)


def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    with _RUNS_LOCK:
        run = _RUNS.get(run_id)
    if run:
        return run
    path = RUN_DIR / f"{run_id}.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def list_runs(limit: int = 20) -> List[Dict[str, Any]]:
    with _RUNS_LOCK:
        runs = list(_RUNS.values())
    if not runs and RUN_DIR.exists():
        for path in sorted(RUN_DIR.glob("aml_*.json"), reverse=True)[:limit]:
            try:
                runs.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
    runs.sort(key=lambda r: r.get("started_at") or "", reverse=True)
    return runs[:limit]


def last_run() -> Optional[Dict[str, Any]]:
    runs = list_runs(1)
    return runs[0] if runs else None


# ---------------------------------------------------------------------------
# source data generation (bank AML model, DuckDB landing)
# ---------------------------------------------------------------------------

def _branch_rows(rng: random.Random) -> List[Dict[str, Any]]:
    cities = [("Mumbai", "WEST", "Maharashtra"), ("Pune", "WEST", "Maharashtra"),
              ("Ahmedabad", "WEST", "Gujarat"), ("Delhi", "NORTH", "Delhi"),
              ("Jaipur", "NORTH", "Rajasthan"), ("Lucknow", "NORTH", "Uttar Pradesh"),
              ("Bengaluru", "SOUTH", "Karnataka"), ("Chennai", "SOUTH", "Tamil Nadu"),
              ("Hyderabad", "SOUTH", "Telangana"), ("Kochi", "SOUTH", "Kerala"),
              ("Kolkata", "EAST", "West Bengal"), ("Patna", "EAST", "Bihar")]
    rows = []
    for i, (city, region, state) in enumerate(cities, start=1):
        code = f"BR{i:03d}"
        rows.append({
            "BRANCH_CODE": code,
            "BRANCH_NAME": f"NanoPro Bank {city} Main",
            "REGION": region,
            "STATE": state,
            "IFSC": f"NPBL0{code}",
        })
    return rows


def _person_name(rng: random.Random) -> str:
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def _pan(rng: random.Random) -> str:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return (f"{rng.choice(letters)}{rng.choice(letters)}{rng.choice(letters)}"
            f"P{rng.choice(letters)}{rng.randint(1000, 9999)}{rng.choice(letters)}")


def _customer_rows(rng: random.Random, count: int, start_idx: int,
                   branch_codes: List[str], force_names: List[str]) -> List[Dict[str, Any]]:
    rows = []
    for i in range(count):
        idx = start_idx + i
        name = force_names[i] if i < len(force_names) else _person_name(rng)
        rows.append({
            "CUSTOMER_ID": f"CUST{idx:06d}",
            "FULL_NAME": name,
            "DOB": (datetime(1960, 1, 1) + timedelta(days=rng.randint(0, 12000))).strftime("%Y-%m-%d"),
            "GENDER": rng.choice(("M", "F")),
            "PAN": _pan(rng),
            "AADHAAR_LAST4": f"{rng.randint(1000, 9999)}",
            "PHONE": f"+91{rng.randint(7000000000, 9999999999)}",
            "EMAIL": f"customer{idx:06d}@example.in",
            "OCCUPATION": rng.choice(("SALARIED", "BUSINESS", "SELF_EMPLOYED", "RETIRED",
                                      "STUDENT", "PROFESSIONAL")),
            "ANNUAL_INCOME_INR": round(rng.uniform(300000, 25000000), 2),
            "CUSTOMER_SINCE": (datetime(2012, 1, 1) + timedelta(days=rng.randint(0, 4200))).strftime("%Y-%m-%d"),
            "BRANCH_CODE": rng.choice(branch_codes),
            "CUSTOMER_TYPE": rng.choice(("INDIVIDUAL", "INDIVIDUAL", "INDIVIDUAL", "NON_INDIVIDUAL")),
            "SEGMENT": rng.choice(SEGMENTS),
        })
    return rows


def _account_rows(rng: random.Random, customers: List[Dict[str, Any]], count: int,
                  start_idx: int, branch_codes: List[str]) -> List[Dict[str, Any]]:
    rows = []
    for i in range(count):
        cust = customers[i % len(customers)]
        idx = start_idx + i
        rows.append({
            "ACCOUNT_ID": f"ACC{idx:07d}",
            "CUSTOMER_ID": cust["CUSTOMER_ID"],
            "ACCOUNT_TYPE": rng.choice(PRODUCTS),
            "BRANCH_CODE": cust["BRANCH_CODE"] or rng.choice(branch_codes),
            "OPEN_DATE": (datetime(2014, 1, 1) + timedelta(days=rng.randint(0, 3800))).strftime("%Y-%m-%d"),
            "CURRENCY": "INR",
            "STATUS": rng.choice(("ACTIVE", "ACTIVE", "ACTIVE", "DORMANT", "CLOSED")),
            "CURRENT_BALANCE_INR": round(rng.uniform(1000, 9000000), 2),
            "PRODUCT_CODE": rng.choice(("SB_GEN", "CA_GEN", "OD_SME", "TD_1Y", "CC_PLATINUM")),
        })
    return rows


def _kyc_rows(rng: random.Random, customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for i, cust in enumerate(customers, start=1):
        rows.append({
            "KYC_ID": f"KYC{i:06d}",
            "CUSTOMER_ID": cust["CUSTOMER_ID"],
            "KYC_STATUS": rng.choice(("VERIFIED", "VERIFIED", "VERIFIED", "PENDING", "RE_KYC_DUE")),
            "RISK_RATING": rng.choice(RISK_RATINGS),
            "PEP_FLAG": rng.random() < 0.06,
            "LAST_REVIEW_DATE": (datetime(2024, 1, 1) + timedelta(days=rng.randint(0, 660))).strftime("%Y-%m-%d"),
            "ID_DOCUMENT_TYPE": rng.choice(("PAN", "AADHAAR", "PASSPORT", "VOTER_ID")),
            "ID_DOCUMENT_NUMBER": f"DOC{rng.randint(100000000, 999999999)}",
            "ADDRESS_COUNTRY": rng.choice(("IN", "IN", "IN", "IN", "AE", "GB")),
            "SOURCE_OF_FUNDS": rng.choice(("SALARY", "BUSINESS_INCOME", "INVESTMENT",
                                           "REMITTANCE", "CASH_DEPOSITS")),
        })
    return rows


def _watchlist_rows(rng: random.Random, start_idx: int, extra_names: List[str]) -> List[Dict[str, Any]]:
    rows = []
    for i, name in enumerate(extra_names, start=1):
        rows.append({
            "WATCHLIST_ID": f"WL{start_idx + i:05d}",
            "ENTITY_NAME": name,
            "ALIAS": "",
            "ENTITY_TYPE": "INDIVIDUAL",
            "LIST_SOURCE": "UNSC",
            "COUNTRY": rng.choice(HIGH_RISK_COUNTRIES),
            "RISK_LEVEL": "CRITICAL",
            "LISTED_DATE": "2023-06-15",
        })
    count = 40
    for i in range(count):
        base = f"{rng.choice(FIRST_NAMES)} {rng.choice('ABCDEFGH')}. {rng.choice(LAST_NAMES)}"
        rows.append({
            "WATCHLIST_ID": f"WL{start_idx + len(rows) + 1:05d}",
            "ENTITY_NAME": base,
            "ALIAS": f"{base.split()[0][0]}. {base.split()[-1]}",
            "ENTITY_TYPE": rng.choice(("INDIVIDUAL", "ENTITY", "VESSEL")),
            "LIST_SOURCE": rng.choice(LIST_SOURCES),
            "COUNTRY": rng.choice(("IR", "KP", "SY", "PK", "AF", "MM", "AE", "RU", "CN", "IN")),
            "RISK_LEVEL": rng.choice(("HIGH", "HIGH", "CRITICAL", "MEDIUM")),
            "LISTED_DATE": (datetime(2019, 1, 1) + timedelta(days=rng.randint(0, 1900))).strftime("%Y-%m-%d"),
        })
    return rows


def _amount_profile(rng: random.Random) -> float:
    bucket = rng.random()
    if bucket < 0.10:
        return float(rng.choice((1000000, 1250000, 1500000, 2500000, 5000000)))
    if bucket < 0.24:
        return round(rng.uniform(900000, 999999), 2)
    if bucket < 0.45:
        return round(rng.uniform(100000, 900000), 2)
    return round(rng.uniform(500, 99999), 2)


def _txn_rows(rng: random.Random, accounts: List[Dict[str, Any]],
              branches: List[str], count: int, start: datetime, end: datetime,
              priority_customer_ids: List[str]) -> List[Dict[str, Any]]:
    rows = []
    window = max(int((end - start).total_seconds()), 60)
    priority_accounts = [a for a in accounts if a["CUSTOMER_ID"] in priority_customer_ids]
    for i in range(count):
        acc = rng.choice(priority_accounts) if priority_accounts and i % 9 == 0 else rng.choice(accounts)
        ts = start + timedelta(seconds=rng.randint(0, window))
        cash = rng.random() < 0.22
        channel = rng.choice(("CASH_DEPOSIT", "CASH_WITHDRAWAL", "ATM", "BRANCH")) if cash else rng.choice(CHANNELS)
        amount = _amount_profile(rng)
        country = rng.choice(COUNTRY_CODES)
        if i % 11 == 0:
            country = rng.choice(HIGH_RISK_COUNTRIES)
        dr_cr = "CR" if channel in ("CASH_DEPOSIT", "NEFT", "RTGS", "IMPS", "UPI") and rng.random() < 0.5 else "DR"
        rows.append({
            "TXN_ID": f"TXN{ts:%Y%m%d}{rng.randint(100000, 999999)}",
            "ACCOUNT_ID": acc["ACCOUNT_ID"],
            "CUSTOMER_ID": acc["CUSTOMER_ID"],
            "TXN_TIMESTAMP": ts,
            "TXN_TYPE": rng.choice(TXN_TYPES),
            "CHANNEL": channel,
            "AMOUNT_INR": amount,
            "CURRENCY": "INR",
            "DR_CR": dr_cr,
            "COUNTERPARTY_ID": f"CP{rng.randint(10000, 99999)}",
            "COUNTERPARTY_NAME": rng.choice(("Merchant Retail", "Global Traders", "Tech Services",
                                             "Overseas Imports", "Cash Counter", _person_name(rng))),
            "COUNTERPARTY_COUNTRY": country,
            "COUNTERPARTY_BANK": rng.choice(("NPBL", "HDFC", "ICICI", "SBI", "AXIS", "HSBC", "CITI")),
            "PURPOSE_CODE": rng.choice(("P2P", "P2M", "SALARY", "TRADE", "REMITTANCE",
                                        "LOAN_REPAY", "INVESTMENT")),
            "BRANCH_CODE": acc["BRANCH_CODE"],
            "STATUS": rng.choice(STATUSES),
            "IS_CASH": cash,
        })
    rows.sort(key=lambda r: r["TXN_TIMESTAMP"])
    return rows


def _alert_rows(rng: random.Random, txns: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
    rows = []
    if not txns:
        return rows
    for i in range(count):
        txn = txns[rng.randrange(len(txns))]
        rule_code, alert_type = rng.choice(ALERT_RULES)
        rows.append({
            "ALERT_ID": f"ALR{uuid.uuid4().hex[:16].upper()}",
            "TXN_ID": txn["TXN_ID"],
            "ACCOUNT_ID": txn["ACCOUNT_ID"],
            "ALERT_TYPE": alert_type,
            "RULE_CODE": rule_code,
            "ALERT_SCORE": round(rng.uniform(45, 99), 2),
            "ALERT_TIMESTAMP": txn["TXN_TIMESTAMP"] + timedelta(minutes=rng.randint(1, 240)),
            "STATUS": rng.choice(("OPEN", "OPEN", "UNDER_REVIEW", "CLOSED_FALSE_POSITIVE")),
        })
    return rows


def build_batch(mode: str, batch_id: str) -> Dict[str, pd.DataFrame]:
    """Generates one landing batch of the bank's AML model."""
    mode = mode.upper()
    seed = int(uuid.uuid4().int % 1_000_000_000) if mode == "INCREMENTAL" else 20261109
    rng = random.Random(seed)
    load_ts = datetime.utcnow().replace(microsecond=0)
    end = _now_ist().replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(days=19) if mode == "FULL" else end - timedelta(hours=10)

    branches = _branch_rows(rng)
    branch_codes = [b["BRANCH_CODE"] for b in branches]

    if mode == "FULL":
        customer_count, account_count, txn_count, alert_count = 160, 210, 950, 180
        start_idx = 1
        watchlist_extra: List[str] = []
        watchlist_start = 0
    else:
        customer_count, account_count, txn_count, alert_count = 14, 18, 95, 22
        start_idx = 1001
        watchlist_extra = []
        watchlist_start = 500

    customers = _customer_rows(rng, customer_count, start_idx, branch_codes, watchlist_extra)
    accounts = _account_rows(rng, customers, account_count, start_idx * 10, branch_codes)
    kyc = _kyc_rows(rng, customers)

    if mode == "FULL":
        hit_names = [customers[3]["FULL_NAME"], customers[17]["FULL_NAME"], customers[41]["FULL_NAME"]]
        watchlist = _watchlist_rows(rng, watchlist_start, hit_names)
        priority = [customers[3]["CUSTOMER_ID"], customers[17]["CUSTOMER_ID"],
                    customers[41]["CUSTOMER_ID"]]
    else:
        watchlist = _watchlist_rows(rng, watchlist_start, [])
        priority = [customers[0]["CUSTOMER_ID"]]

    txns = _txn_rows(rng, accounts, branch_codes, txn_count, start, end, priority)
    alerts = _alert_rows(rng, txns, alert_count)

    frames = {
        "AML_BRANCH_RAW": pd.DataFrame(branches),
        "AML_CUSTOMER_RAW": pd.DataFrame(customers),
        "AML_ACCOUNT_RAW": pd.DataFrame(accounts),
        "AML_KYC_RAW": pd.DataFrame(kyc),
        "AML_TRANSACTION_RAW": pd.DataFrame(txns),
        "AML_WATCHLIST_RAW": pd.DataFrame(watchlist),
        "AML_ALERT_RAW": pd.DataFrame(alerts),
    }
    for name, frame in frames.items():
        frame["_BATCH_ID"] = batch_id
        frame["_LOAD_TS"] = load_ts
        frame["_SOURCE_SYSTEM"] = SOURCE_SYSTEM
        frames[name] = frame[list(frame.columns)]
    return frames


def _append_to_duckdb(frames: Dict[str, pd.DataFrame], mode: str) -> Dict[str, Any]:
    import duckdb

    SOURCE_DB.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(SOURCE_DB))
    landed = {}
    try:
        for table, frame in frames.items():
            src = f"src_{table.lower()}"
            exists = con.execute(
                "SELECT COUNT(*) FROM duckdb_tables() WHERE table_name = ?", [src]
            ).fetchall()[0][0]
            con.register("_batch_df", frame)
            try:
                if exists and mode.upper() == "INCREMENTAL":
                    con.execute(f"INSERT INTO {src} SELECT * FROM _batch_df")
                else:
                    con.execute(f"CREATE OR REPLACE TABLE {src} AS SELECT * FROM _batch_df")
                landed[table] = con.execute(f"SELECT COUNT(*) FROM {src}").fetchall()[0][0]
            finally:
                con.unregister("_batch_df")
        con.execute(
            "CREATE TABLE IF NOT EXISTS src_aml_load_log (batch_id VARCHAR, mode VARCHAR, "
            "loaded_at VARCHAR, tables INTEGER)"
        )
        con.execute("INSERT INTO src_aml_load_log VALUES (?,?,?,?)",
                    [frames["AML_CUSTOMER_RAW"]["_BATCH_ID"].iloc[0], mode.upper(),
                     _ts(_now_ist()), len(frames)])
    finally:
        con.close()
    return landed


# ---------------------------------------------------------------------------
# AWS S3 Parquet landing zone
# ---------------------------------------------------------------------------

def _aws_config() -> Dict[str, str]:
    access_key = (os.environ.get("AWS_ACCESS_KEY_ID") or "").strip()
    secret_key = (os.environ.get("AWS_SECRET_ACCESS_KEY") or "").strip()
    region = (os.environ.get("AWS_DEFAULT_REGION") or "").strip()
    bucket = (os.environ.get("AWS_S3_BUCKET") or "").strip()
    if not (access_key and secret_key and bucket):
        try:
            from app.core.connection_manager import connection_manager

            cfg = connection_manager.get_connection_config("AWS_S3_DATA_LAKE", mask=False) or {}
            meta = cfg.get("metadata") or {}
            access_key = access_key or str(cfg.get("username") or "")
            secret_key = secret_key or str(cfg.get("secret_value") or "")
            bucket = bucket or str(cfg.get("database_name") or meta.get("bucket") or "")
            region = region or str(meta.get("region") or "")
        except Exception:
            pass
    return {
        "access_key": access_key,
        "secret_key": secret_key,
        "region": region or "ap-southeast-2",
        "bucket": bucket or DEFAULT_S3_BUCKET,
    }


def _upload_parquet(frames: Dict[str, pd.DataFrame], mode: str, batch_id: str,
                    run_id: str) -> List[Dict[str, Any]]:
    import boto3
    import duckdb

    cfg = _aws_config()
    if not (cfg["access_key"] and cfg["secret_key"]):
        raise RuntimeError("AWS credentials are missing; cannot write Parquet to S3.")
    s3 = boto3.client("s3", region_name=cfg["region"],
                      aws_access_key_id=cfg["access_key"],
                      aws_secret_access_key=cfg["secret_key"])
    prefix = f"raw/aml/{mode.lower()}/{datetime.utcnow():%Y%m%d}/batch_{batch_id[-8:].lower()}"
    workdir = Path("data/lakehouse/parquet_staging")
    workdir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    objects = []
    try:
        for table in TABLE_ORDER:
            frame = frames[table]
            local = workdir / f"{run_id}_{table}.parquet"
            con.register("_export_df", frame)
            try:
                con.execute(
                    f"COPY (SELECT * FROM _export_df) TO '{local.as_posix()}' "
                    f"(FORMAT PARQUET, COMPRESSION SNAPPY)"
                )
            finally:
                con.unregister("_export_df")
            body = local.read_bytes()
            key = f"{prefix}/{table.lower()}.parquet"
            s3.put_object(Bucket=cfg["bucket"], Key=key, Body=body,
                          ContentType="application/vnd.apache.parquet",
                          Metadata={"pipeline": "nanopro-aml", "layer": "raw",
                                    "table": table, "batch_id": batch_id, "run_id": run_id})
            check = s3.get_object(Bucket=cfg["bucket"], Key=key)
            payload = check["Body"].read()
            verify_path = workdir / f"{run_id}_{table}_s3.parquet"
            verify_path.write_bytes(payload)
            try:
                rows_read = con.execute(
                    f"SELECT COUNT(*) FROM read_parquet('{verify_path.as_posix()}')"
                ).fetchall()[0][0]
            finally:
                verify_path.unlink(missing_ok=True)
            local.unlink(missing_ok=True)
            objects.append({
                "table": table,
                "bucket": cfg["bucket"],
                "key": key,
                "s3_uri": f"s3://{cfg['bucket']}/{key}",
                "size_bytes": len(payload),
                "rows": int(rows_read),
                "parquet_magic_ok": payload[:4] == b"PAR1" and payload[-4:] == b"PAR1",
                "verified_rows_match": int(rows_read) == len(frame),
            })
    finally:
        con.close()
    manifest = {"run_id": run_id, "mode": mode, "batch_id": batch_id,
                "generated_at": _ts(_now_ist()), "objects": objects}
    s3.put_object(Bucket=cfg["bucket"], Key=f"{prefix}/_manifest.json",
                  Body=json.dumps(manifest, indent=2).encode("utf-8"),
                  ContentType="application/json")
    return objects


# ---------------------------------------------------------------------------
# Snowflake L0 / L1 / L2
# ---------------------------------------------------------------------------

def _ddl(table: str) -> str:
    columns = DDL[table] + META_COLUMNS
    body = ",\n  ".join(f"{name} {dtype}" for name, dtype in columns)
    return f"CREATE TABLE {DB}.{L0}.{table} (\n  {body}\n)"


def _load_snowflake(frames: Dict[str, pd.DataFrame], mode: str) -> Dict[str, Any]:
    from app.core.snowflake_client import open_connection

    def _rows_for_insert(frame: pd.DataFrame) -> List[List[Any]]:
        clean = frame.astype(object).where(pd.notnull(frame), None)
        rows: List[List[Any]] = []
        for row in clean.itertuples(index=False, name=None):
            values = []
            for value in row:
                if isinstance(value, pd.Timestamp):
                    value = value.to_pydatetime()
                elif hasattr(value, "item"):
                    value = value.item()
                values.append(value)
            rows.append(values)
        return rows

    conn = open_connection(database=DB)
    counts: Dict[str, Any] = {}
    try:
        cur = conn.cursor()
        for schema in (L0, L1, L2):
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {DB}.{schema}")
        for table in TABLE_ORDER:
            if mode.upper() == "FULL":
                cur.execute(f"DROP TABLE IF EXISTS {DB}.{L0}.{table}")
                cur.execute(_ddl(table))
            else:
                cur.execute(_ddl(table).replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ", 1))
            df = frames[table]
            columns = [c for c, _ in DDL[table]] + [c for c, _ in META_COLUMNS]
            rows = _rows_for_insert(df)
            placeholder = "(" + ",".join(["%s"] * len(columns)) + ")"
            for start in range(0, len(rows), 80):
                chunk = rows[start:start + 80]
                statement = (
                    f"INSERT INTO {DB}.{L0}.{table} ({','.join(columns)}) VALUES "
                    + ",".join([placeholder] * len(chunk))
                )
                cur.execute(statement, [v for row in chunk for v in row])
            total = cur.execute(f"SELECT COUNT(*) FROM {DB}.{L0}.{table}").fetchone()[0]
            counts[table] = {"batch_rows": int(len(rows)), "table_rows": int(total)}
        conn.commit()
        cur.close()
    finally:
        conn.close()
    return counts


L1_SQL: Dict[str, str] = {
    "AML_HARM_BRANCH": f"""
CREATE OR REPLACE TABLE {DB}.{L1}.AML_HARM_BRANCH AS
SELECT BRANCH_CODE, UPPER(TRIM(BRANCH_NAME)) AS BRANCH_NAME, UPPER(TRIM(REGION)) AS REGION,
       UPPER(TRIM(STATE)) AS STATE, UPPER(TRIM(IFSC)) AS IFSC, MAX(_LOAD_TS) AS UPDATED_AT
FROM {DB}.{L0}.AML_BRANCH_RAW
GROUP BY 1,2,3,4,5
""",
    "AML_HARM_CUSTOMER": f"""
CREATE OR REPLACE TABLE {DB}.{L1}.AML_HARM_CUSTOMER AS
SELECT CUSTOMER_ID, UPPER(TRIM(FULL_NAME)) AS FULL_NAME,
       UPPER(TRIM(REGEXP_REPLACE(FULL_NAME, '[^A-Za-z0-9 ]', ''))) AS MATCH_KEY,
       DOB, GENDER, PAN, AADHAAR_LAST4, PHONE, EMAIL, OCCUPATION, ANNUAL_INCOME_INR,
       CUSTOMER_SINCE, BRANCH_CODE, CUSTOMER_TYPE, SEGMENT,
       IFF(SEGMENT IN ('CORPORATE','SME'), TRUE, FALSE) AS IS_ENTITY,
       UPDATED_AT
FROM (
  SELECT *, MAX(_LOAD_TS) OVER (PARTITION BY CUSTOMER_ID) AS UPDATED_AT,
         ROW_NUMBER() OVER (PARTITION BY CUSTOMER_ID ORDER BY _LOAD_TS DESC) AS RN
  FROM {DB}.{L0}.AML_CUSTOMER_RAW
) WHERE RN = 1
""",
    "AML_HARM_ACCOUNT": f"""
CREATE OR REPLACE TABLE {DB}.{L1}.AML_HARM_ACCOUNT AS
SELECT ACCOUNT_ID, CUSTOMER_ID, UPPER(TRIM(ACCOUNT_TYPE)) AS ACCOUNT_TYPE, BRANCH_CODE,
       TO_DATE(OPEN_DATE) AS OPEN_DATE, UPPER(TRIM(CURRENCY)) AS CURRENCY,
       UPPER(TRIM(STATUS)) AS STATUS, CURRENT_BALANCE_INR, PRODUCT_CODE,
       IFF(UPPER(TRIM(STATUS)) = 'DORMANT', TRUE, FALSE) AS IS_DORMANT, UPDATED_AT
FROM (
  SELECT *, MAX(_LOAD_TS) OVER (PARTITION BY ACCOUNT_ID) AS UPDATED_AT,
         ROW_NUMBER() OVER (PARTITION BY ACCOUNT_ID ORDER BY _LOAD_TS DESC) AS RN
  FROM {DB}.{L0}.AML_ACCOUNT_RAW
) WHERE RN = 1
""",
    "AML_HARM_KYC": f"""
CREATE OR REPLACE TABLE {DB}.{L1}.AML_HARM_KYC AS
SELECT KYC_ID, CUSTOMER_ID, UPPER(TRIM(KYC_STATUS)) AS KYC_STATUS,
       UPPER(TRIM(RISK_RATING)) AS RISK_RATING, PEP_FLAG,
       TO_DATE(LAST_REVIEW_DATE) AS LAST_REVIEW_DATE, ID_DOCUMENT_TYPE,
       ADDRESS_COUNTRY, UPPER(TRIM(SOURCE_OF_FUNDS)) AS SOURCE_OF_FUNDS, UPDATED_AT
FROM (
  SELECT *, MAX(_LOAD_TS) OVER (PARTITION BY CUSTOMER_ID) AS UPDATED_AT,
         ROW_NUMBER() OVER (PARTITION BY CUSTOMER_ID ORDER BY LAST_REVIEW_DATE DESC, _LOAD_TS DESC) AS RN
  FROM {DB}.{L0}.AML_KYC_RAW
) WHERE RN = 1
""",
    "AML_HARM_WATCHLIST": f"""
CREATE OR REPLACE TABLE {DB}.{L1}.AML_HARM_WATCHLIST AS
SELECT WATCHLIST_ID, UPPER(TRIM(ENTITY_NAME)) AS ENTITY_NAME,
       UPPER(TRIM(REGEXP_REPLACE(ENTITY_NAME, '[^A-Za-z0-9 ]', ''))) AS MATCH_KEY,
       UPPER(TRIM(ALIAS)) AS ALIAS, UPPER(TRIM(ENTITY_TYPE)) AS ENTITY_TYPE,
       UPPER(TRIM(LIST_SOURCE)) AS LIST_SOURCE, UPPER(TRIM(COUNTRY)) AS COUNTRY,
       UPPER(TRIM(RISK_LEVEL)) AS RISK_LEVEL, TO_DATE(LISTED_DATE) AS LISTED_DATE
FROM {DB}.{L0}.AML_WATCHLIST_RAW
QUALIFY ROW_NUMBER() OVER (PARTITION BY WATCHLIST_ID ORDER BY _LOAD_TS DESC) = 1
""",
    "AML_HARM_TRANSACTION": f"""
CREATE OR REPLACE TABLE {DB}.{L1}.AML_HARM_TRANSACTION AS
SELECT TXN_ID, ACCOUNT_ID, CUSTOMER_ID, TXN_TIMESTAMP AS TXN_TS,
       TO_DATE(TXN_TIMESTAMP) AS TXN_DATE, HOUR(TXN_TIMESTAMP) AS TXN_HOUR,
       UPPER(TRIM(TXN_TYPE)) AS TXN_TYPE, UPPER(TRIM(CHANNEL)) AS CHANNEL,
       ROUND(AMOUNT_INR, 2) AS AMOUNT_INR, UPPER(TRIM(CURRENCY)) AS CURRENCY,
       UPPER(TRIM(DR_CR)) AS DR_CR,
       IFF(UPPER(TRIM(DR_CR)) = 'DR', -ROUND(AMOUNT_INR, 2), ROUND(AMOUNT_INR, 2)) AS SIGNED_AMOUNT_INR,
       COUNTERPARTY_ID, UPPER(TRIM(COUNTERPARTY_NAME)) AS COUNTERPARTY_NAME,
       UPPER(TRIM(COUNTERPARTY_COUNTRY)) AS COUNTERPARTY_COUNTRY,
       UPPER(TRIM(COUNTERPARTY_BANK)) AS COUNTERPARTY_BANK, PURPOSE_CODE, BRANCH_CODE,
       UPPER(TRIM(STATUS)) AS STATUS,
       IFF(UPPER(TRIM(COUNTERPARTY_COUNTRY)) <> 'IN', TRUE, FALSE) AS IS_CROSS_BORDER,
       IFF(UPPER(TRIM(COUNTERPARTY_COUNTRY)) IN ({",".join(repr(c) for c in HIGH_RISK_COUNTRIES)}), TRUE, FALSE) AS IS_HIGH_RISK_COUNTRY,
       IFF(UPPER(TRIM(CHANNEL)) IN ('CASH_DEPOSIT','CASH_WITHDRAWAL','ATM','BRANCH'), TRUE, FALSE) AS IS_CASH,
       IFF(ROUND(AMOUNT_INR, 2) >= 100000 AND MOD(ROUND(AMOUNT_INR), 100000) = 0, TRUE, FALSE) AS IS_ROUND_AMOUNT,
       BATCH_ID, LOAD_TS
FROM (
  SELECT TXN_ID, ACCOUNT_ID, CUSTOMER_ID, TXN_TIMESTAMP, TXN_TYPE, CHANNEL, AMOUNT_INR,
         CURRENCY, DR_CR, COUNTERPARTY_ID, COUNTERPARTY_NAME, COUNTERPARTY_COUNTRY,
         COUNTERPARTY_BANK, PURPOSE_CODE, BRANCH_CODE, STATUS,
         _BATCH_ID AS BATCH_ID, _LOAD_TS AS LOAD_TS,
         ROW_NUMBER() OVER (PARTITION BY TXN_ID ORDER BY _LOAD_TS DESC) AS RN
  FROM {DB}.{L0}.AML_TRANSACTION_RAW
) WHERE RN = 1
""",
    "AML_HARM_ALERT": f"""
CREATE OR REPLACE TABLE {DB}.{L1}.AML_HARM_ALERT AS
SELECT ALERT_ID, TXN_ID, ACCOUNT_ID, UPPER(TRIM(ALERT_TYPE)) AS ALERT_TYPE,
       UPPER(TRIM(RULE_CODE)) AS RULE_CODE, ALERT_SCORE,
       ALERT_TIMESTAMP AS ALERT_TS, UPPER(TRIM(STATUS)) AS STATUS
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY ALERT_ID ORDER BY _LOAD_TS DESC) AS RN
  FROM {DB}.{L0}.AML_ALERT_RAW
) WHERE RN = 1
""",
}

L2_SQL: Dict[str, str] = {
    "AML_DIM_BRANCH": f"""
CREATE OR REPLACE TABLE {DB}.{L2}.AML_DIM_BRANCH AS
SELECT BRANCH_CODE, BRANCH_NAME, REGION, STATE, IFSC, UPDATED_AT FROM {DB}.{L1}.AML_HARM_BRANCH
""",
    "AML_DIM_CUSTOMER": f"""
CREATE OR REPLACE TABLE {DB}.{L2}.AML_DIM_CUSTOMER AS
SELECT c.CUSTOMER_ID, c.FULL_NAME, c.PAN, c.GENDER, c.OCCUPATION, c.ANNUAL_INCOME_INR,
       c.CUSTOMER_SINCE, c.BRANCH_CODE, br.BRANCH_NAME, br.REGION,
       c.CUSTOMER_TYPE, c.SEGMENT,
       k.KYC_STATUS, k.RISK_RATING, COALESCE(k.PEP_FLAG, FALSE) AS PEP_FLAG,
       k.SOURCE_OF_FUNDS, k.ADDRESS_COUNTRY,
       IFF(k.RISK_RATING IN ('HIGH','CRITICAL'), TRUE, FALSE) AS IS_HIGH_RISK,
       IFF(w.WATCHLIST_ID IS NOT NULL, TRUE, FALSE) AS IS_WATCHLIST_MATCH,
       w.WATCHLIST_ID, w.LIST_SOURCE, w.WATCHLIST_RISK
FROM {DB}.{L1}.AML_HARM_CUSTOMER c
LEFT JOIN {DB}.{L1}.AML_HARM_BRANCH br ON br.BRANCH_CODE = c.BRANCH_CODE
LEFT JOIN {DB}.{L1}.AML_HARM_KYC k ON k.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN (
    SELECT cw.CUSTOMER_ID, wl.WATCHLIST_ID, wl.LIST_SOURCE, wl.RISK_LEVEL AS WATCHLIST_RISK
    FROM {DB}.{L1}.AML_HARM_CUSTOMER cw
    JOIN {DB}.{L1}.AML_HARM_WATCHLIST wl ON wl.MATCH_KEY = cw.MATCH_KEY
    QUALIFY ROW_NUMBER() OVER (PARTITION BY cw.CUSTOMER_ID ORDER BY wl.RISK_LEVEL) = 1
) w ON w.CUSTOMER_ID = c.CUSTOMER_ID
""",
    "AML_DIM_ACCOUNT": f"""
CREATE OR REPLACE TABLE {DB}.{L2}.AML_DIM_ACCOUNT AS
SELECT a.ACCOUNT_ID, a.CUSTOMER_ID, a.ACCOUNT_TYPE, a.BRANCH_CODE, a.OPEN_DATE,
       a.CURRENCY, a.STATUS, a.CURRENT_BALANCE_INR, a.PRODUCT_CODE, a.IS_DORMANT
FROM {DB}.{L1}.AML_HARM_ACCOUNT a
""",
    "AML_DIM_DATE": f"""
CREATE OR REPLACE TABLE {DB}.{L2}.AML_DIM_DATE AS
SELECT DISTINCT TXN_DATE AS DATE_KEY, YEAR(TXN_DATE) AS YEAR, MONTH(TXN_DATE) AS MONTH,
       DAY(TXN_DATE) AS DAY, DAYNAME(TXN_DATE) AS DAY_NAME,
       IFF(DAYOFWEEKISO(TXN_DATE) IN (6,7), TRUE, FALSE) AS IS_WEEKEND
FROM {DB}.{L1}.AML_HARM_TRANSACTION
""",
    "AML_FACT_TXN_MONITOR": f"""
CREATE OR REPLACE TABLE {DB}.{L2}.AML_FACT_TXN_MONITOR AS
SELECT t.TXN_ID, t.ACCOUNT_ID, t.CUSTOMER_ID, t.TXN_TS, t.TXN_DATE, t.TXN_HOUR,
       t.TXN_TYPE, t.CHANNEL, t.AMOUNT_INR, t.SIGNED_AMOUNT_INR, t.CURRENCY, t.DR_CR,
       t.COUNTERPARTY_NAME, t.COUNTERPARTY_COUNTRY, t.COUNTERPARTY_BANK,
       t.PURPOSE_CODE, t.BRANCH_CODE, t.STATUS, t.IS_CROSS_BORDER,
       t.IS_HIGH_RISK_COUNTRY, t.IS_CASH, t.IS_ROUND_AMOUNT, t.BATCH_ID,
       c.FULL_NAME AS CUSTOMER_NAME, c.SEGMENT, c.RISK_RATING, c.PEP_FLAG,
       c.IS_HIGH_RISK, c.IS_WATCHLIST_MATCH, c.LIST_SOURCE,
       a.ACCOUNT_TYPE, a.PRODUCT_CODE, a.ACCOUNT_STATUS,
       IFF(t.IS_CASH AND t.AMOUNT_INR >= 1000000, TRUE, FALSE) AS CTR_FLAG,
       LEAST(100, IFF(t.AMOUNT_INR >= 1000000, 40, IFF(t.AMOUNT_INR >= 500000, 25, IFF(t.AMOUNT_INR >= 100000, 10, 0)))
         + IFF(t.IS_HIGH_RISK_COUNTRY, 30, 0) + IFF(t.IS_CROSS_BORDER, 10, 0)
         + IFF(t.IS_CASH, 10, 0) + IFF(c.IS_WATCHLIST_MATCH, 40, 0)
         + IFF(c.RISK_RATING = 'CRITICAL', 20, IFF(c.RISK_RATING = 'HIGH', 12, IFF(c.RISK_RATING = 'MEDIUM', 5, 0)))
       ) AS RISK_SCORE
FROM {DB}.{L1}.AML_HARM_TRANSACTION t
LEFT JOIN {DB}.{L2}.AML_DIM_CUSTOMER c ON c.CUSTOMER_ID = t.CUSTOMER_ID
LEFT JOIN (
    SELECT ACCOUNT_ID, ACCOUNT_TYPE, PRODUCT_CODE, STATUS AS ACCOUNT_STATUS
    FROM {DB}.{L1}.AML_HARM_ACCOUNT
) a ON a.ACCOUNT_ID = t.ACCOUNT_ID
""",
    "AML_FACT_ALERTS": f"""
CREATE OR REPLACE TABLE {DB}.{L2}.AML_FACT_ALERTS AS
SELECT al.ALERT_ID, al.TXN_ID, al.ACCOUNT_ID, al.ALERT_TYPE, al.RULE_CODE, al.ALERT_SCORE,
       al.ALERT_TS, al.STATUS AS ALERT_STATUS, m.CUSTOMER_ID, m.CUSTOMER_NAME,
       m.TXN_DATE, m.AMOUNT_INR, m.CHANNEL, m.COUNTERPARTY_COUNTRY, m.RISK_SCORE
FROM {DB}.{L1}.AML_HARM_ALERT al
LEFT JOIN {DB}.{L2}.AML_FACT_TXN_MONITOR m ON m.TXN_ID = al.TXN_ID
""",
    "AML_FACT_CTR": f"""
CREATE OR REPLACE TABLE {DB}.{L2}.AML_FACT_CTR AS
SELECT ACCOUNT_ID, CUSTOMER_ID, CUSTOMER_NAME, TXN_DATE, BRANCH_CODE,
       COUNT(*) AS TXN_COUNT, SUM(AMOUNT_INR) AS TOTAL_AMOUNT_INR,
       MAX(AMOUNT_INR) AS MAX_AMOUNT_INR, MIN(TXN_TS) AS FIRST_TXN_TS, MAX(TXN_TS) AS LAST_TXN_TS,
       'CTR_10L_CASH' AS REPORT_REASON
FROM {DB}.{L2}.AML_FACT_TXN_MONITOR
WHERE CTR_FLAG
GROUP BY ACCOUNT_ID, CUSTOMER_ID, CUSTOMER_NAME, TXN_DATE, BRANCH_CODE
""",
    "AML_FACT_STR_CANDIDATES": f"""
CREATE OR REPLACE TABLE {DB}.{L2}.AML_FACT_STR_CANDIDATES AS
SELECT * FROM (
  SELECT 'STRUCTURING_BELOW_THRESHOLD' AS RULE_CODE,
         ACCOUNT_ID, CUSTOMER_ID, CUSTOMER_NAME, TXN_DATE, COUNT(*) AS TXN_COUNT,
         SUM(AMOUNT_INR) AS TOTAL_AMOUNT_INR, MIN(TXN_ID) AS SAMPLE_TXN_ID,
         'Multiple cash transactions just below the 10 lakh CTR threshold' AS REASON
  FROM {DB}.{L2}.AML_FACT_TXN_MONITOR
  WHERE IS_CASH AND AMOUNT_INR BETWEEN 900000 AND 999999
  GROUP BY ACCOUNT_ID, CUSTOMER_ID, CUSTOMER_NAME, TXN_DATE HAVING COUNT(*) >= 2
  UNION ALL
  SELECT 'HIGH_RISK_CROSS_BORDER', ACCOUNT_ID, CUSTOMER_ID, CUSTOMER_NAME, TXN_DATE,
         COUNT(*), SUM(AMOUNT_INR), MIN(TXN_ID),
         'Cross-border transfer to a high-risk jurisdiction above 5 lakh'
  FROM {DB}.{L2}.AML_FACT_TXN_MONITOR
  WHERE IS_HIGH_RISK_COUNTRY AND AMOUNT_INR >= 500000
  GROUP BY ACCOUNT_ID, CUSTOMER_ID, CUSTOMER_NAME, TXN_DATE
  UNION ALL
  SELECT 'WATCHLIST_EXPOSURE', ACCOUNT_ID, CUSTOMER_ID, CUSTOMER_NAME, TXN_DATE,
         COUNT(*), SUM(AMOUNT_INR), MIN(TXN_ID),
         'Watchlist-matched customer with material transaction value'
  FROM {DB}.{L2}.AML_FACT_TXN_MONITOR
  WHERE IS_WATCHLIST_MATCH AND AMOUNT_INR >= 100000
  GROUP BY ACCOUNT_ID, CUSTOMER_ID, CUSTOMER_NAME, TXN_DATE
  UNION ALL
  SELECT 'VELOCITY', ACCOUNT_ID, CUSTOMER_ID, CUSTOMER_NAME, TXN_DATE,
         COUNT(*), SUM(AMOUNT_INR), MIN(TXN_ID),
         'Account velocity above six transactions in a single day'
  FROM {DB}.{L2}.AML_FACT_TXN_MONITOR
  GROUP BY ACCOUNT_ID, CUSTOMER_ID, CUSTOMER_NAME, TXN_DATE HAVING COUNT(*) >= 6
)
""",
    "AML_FACT_WATCHLIST_HITS": f"""
CREATE OR REPLACE TABLE {DB}.{L2}.AML_FACT_WATCHLIST_HITS AS
SELECT m.CUSTOMER_ID, m.CUSTOMER_NAME, m.LIST_SOURCE, m.TXN_ID, m.TXN_DATE,
       m.AMOUNT_INR, m.CHANNEL, m.COUNTERPARTY_COUNTRY, m.RISK_SCORE
FROM {DB}.{L2}.AML_FACT_TXN_MONITOR m
WHERE m.IS_WATCHLIST_MATCH
""",
    "AML_DAILY_SUMMARY": f"""
CREATE OR REPLACE TABLE {DB}.{L2}.AML_DAILY_SUMMARY AS
SELECT TXN_DATE, COUNT(*) AS TOTAL_TXNS, SUM(AMOUNT_INR) AS TOTAL_AMOUNT_INR,
       SUM(IFF(IS_CASH, 1, 0)) AS CASH_TXNS,
       SUM(IFF(IS_CROSS_BORDER, 1, 0)) AS CROSS_BORDER_TXNS,
       SUM(IFF(IS_HIGH_RISK_COUNTRY, 1, 0)) AS HIGH_RISK_COUNTRY_TXNS,
       SUM(IFF(CTR_FLAG, 1, 0)) AS CTR_TXNS,
       ROUND(AVG(RISK_SCORE), 2) AS AVG_RISK_SCORE
FROM {DB}.{L2}.AML_FACT_TXN_MONITOR
GROUP BY TXN_DATE
""",
}


def _run_transforms(mode: str) -> Dict[str, Any]:
    from app.core.snowflake_client import open_connection

    conn = open_connection(database=DB)
    timings: Dict[str, Any] = {}
    try:
        cur = conn.cursor()
        for name, sql in L1_SQL.items():
            started = time.time()
            cur.execute(sql)
            count = cur.execute(f"SELECT COUNT(*) FROM {DB}.{L1}.{name}").fetchone()[0]
            timings[name] = {"layer": "L1", "rows": int(count),
                             "seconds": round(time.time() - started, 2)}
        for name, sql in L2_SQL.items():
            started = time.time()
            cur.execute(sql)
            count = cur.execute(f"SELECT COUNT(*) FROM {DB}.{L2}.{name}").fetchone()[0]
            timings[name] = {"layer": "L2", "rows": int(count),
                             "seconds": round(time.time() - started, 2)}
        cur.close()
    finally:
        conn.close()
    return timings


# ---------------------------------------------------------------------------
# business report
# ---------------------------------------------------------------------------

REPORT_QUERIES = {
    "kpi": """
SELECT COUNT(*) AS TXNS, ROUND(SUM(AMOUNT_INR),2) AS AMOUNT_INR,
       SUM(IFF(IS_CASH,1,0)) AS CASH_TXNS, SUM(IFF(CTR_FLAG,1,0)) AS CTR_TXNS,
       SUM(IFF(IS_CROSS_BORDER,1,0)) AS CROSS_BORDER_TXNS,
       SUM(IFF(IS_HIGH_RISK_COUNTRY,1,0)) AS HIGH_RISK_COUNTRY_TXNS,
       ROUND(AVG(RISK_SCORE),2) AS AVG_RISK_SCORE,
       COUNT(DISTINCT CUSTOMER_ID) AS ACTIVE_CUSTOMERS
FROM {db}.{l2}.AML_FACT_TXN_MONITOR WHERE TXN_DATE = '{day}'
""",
    "risk": """
SELECT RISK_RATING, COUNT(DISTINCT CUSTOMER_ID) AS CUSTOMERS
FROM {db}.{l2}.AML_DIM_CUSTOMER GROUP BY RISK_RATING ORDER BY CUSTOMERS DESC
""",
    "channels": """
SELECT CHANNEL, COUNT(*) AS TXNS, ROUND(SUM(AMOUNT_INR),2) AS AMOUNT_INR,
       ROUND(AVG(RISK_SCORE),2) AS AVG_RISK
FROM {db}.{l2}.AML_FACT_TXN_MONITOR WHERE TXN_DATE = '{day}'
GROUP BY CHANNEL ORDER BY AMOUNT_INR DESC
""",
    "countries": """
SELECT COUNTERPARTY_COUNTRY, COUNT(*) AS TXNS, ROUND(SUM(AMOUNT_INR),2) AS AMOUNT_INR,
       SUM(IFF(IS_HIGH_RISK_COUNTRY,1,0)) AS HIGH_RISK_TXNS
FROM {db}.{l2}.AML_FACT_TXN_MONITOR WHERE TXN_DATE = '{day}'
GROUP BY COUNTERPARTY_COUNTRY ORDER BY AMOUNT_INR DESC LIMIT 10
""",
    "alerts": """
SELECT ALERT_TYPE, COUNT(*) AS ALERTS, ROUND(AVG(ALERT_SCORE),2) AS AVG_SCORE
FROM {db}.{l2}.AML_FACT_ALERTS GROUP BY ALERT_TYPE ORDER BY ALERTS DESC
""",
    "ctr": """
SELECT * FROM {db}.{l2}.AML_FACT_CTR ORDER BY TOTAL_AMOUNT_INR DESC LIMIT 200
""",
    "str": """
SELECT * FROM {db}.{l2}.AML_FACT_STR_CANDIDATES ORDER BY TOTAL_AMOUNT_INR DESC LIMIT 200
""",
    "watchlist": """
SELECT * FROM {db}.{l2}.AML_FACT_WATCHLIST_HITS ORDER BY RISK_SCORE DESC LIMIT 200
""",
    "top_risk": """
SELECT TXN_ID, CUSTOMER_NAME, TXN_DATE, CHANNEL, AMOUNT_INR, COUNTERPARTY_COUNTRY,
       RISK_SCORE, IS_CASH, IS_CROSS_BORDER, IS_HIGH_RISK_COUNTRY, IS_WATCHLIST_MATCH
FROM {db}.{l2}.AML_FACT_TXN_MONITOR ORDER BY RISK_SCORE DESC, AMOUNT_INR DESC LIMIT 15
""",
    "daily": """
SELECT * FROM {db}.{l2}.AML_DAILY_SUMMARY ORDER BY TXN_DATE DESC LIMIT 10
""",
    "customers": """
SELECT COUNT(*) AS TOTAL_CUSTOMERS,
       SUM(IFF(IS_HIGH_RISK,1,0)) AS HIGH_RISK_CUSTOMERS,
       SUM(IFF(IS_WATCHLIST_MATCH,1,0)) AS WATCHLIST_CUSTOMERS,
       SUM(IFF(PEP_FLAG,1,0)) AS PEP_CUSTOMERS
FROM {db}.{l2}.AML_DIM_CUSTOMER
""",
}


def _latest_report_day() -> str:
    from app.core.snowflake_client import open_connection

    conn = open_connection(database=DB)
    try:
        cur = conn.cursor()
        row = cur.execute(f"SELECT MAX(TXN_DATE) FROM {DB}.{L2}.AML_FACT_TXN_MONITOR").fetchone()
        if row and row[0]:
            return str(row[0])
    finally:
        conn.close()
    return _report_date()


def _query_reports(report_day: str) -> Dict[str, pd.DataFrame]:
    from app.core.snowflake_client import open_connection

    conn = open_connection(database=DB)
    out: Dict[str, pd.DataFrame] = {}
    try:
        cur = conn.cursor()
        for key, sql in REPORT_QUERIES.items():
            rendered = sql.format(db=DB, l2=L2, day=report_day)
            cur.execute(rendered)
            rows = cur.fetchall()
            columns = [desc[0] for desc in (cur.description or [])]
            out[key] = pd.DataFrame([list(r) for r in rows], columns=columns)
        cur.close()
    finally:
        conn.close()
    return out


def _fmt_money(value: Any) -> str:
    try:
        amount = float(value or 0)
    except Exception:
        return "0"
    if amount >= 1_00_00_000:
        return f"₹{amount / 1_00_00_000:.2f} Cr"
    if amount >= 1_00_000:
        return f"₹{amount / 1_00_000:.2f} L"
    return f"₹{amount:,.0f}"


def _html_table(frame: pd.DataFrame, limit: int = 25) -> str:
    if frame is None or frame.empty:
        return "<p style='color:#64748b'>No rows for this section.</p>"
    view = frame.head(limit)
    head = "".join(f"<th style='padding:6px 8px;background:#0f172a;color:#fff;text-align:left;font-size:11px'>{c}</th>"
                   for c in view.columns)
    body_rows = []
    for _, row in view.iterrows():
        cells = "".join(
            f"<td style='padding:5px 8px;border-bottom:1px solid #e2e8f0;font-size:11px'>{'' if pd.isna(v) else v}</td>"
            for v in row.values
        )
        body_rows.append(f"<tr>{cells}</tr>")
    return (f"<table style='border-collapse:collapse;width:100%;margin:6px 0 14px'>"
            f"<thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>")


def _build_report(run: Dict[str, Any], data: Dict[str, pd.DataFrame],
                  transforms: Dict[str, Any]) -> Dict[str, Any]:
    report_dir = REPORT_DIR / run["run_id"]
    report_dir.mkdir(parents=True, exist_ok=True)
    kpi = data["kpi"].iloc[0] if not data["kpi"].empty else {}
    customers = data["customers"].iloc[0] if not data["customers"].empty else {}

    report_day = str(data["daily"].iloc[0]["TXN_DATE"]) if not data["daily"].empty else _report_date()
    files: Dict[str, str] = {}
    for key, frame in data.items():
        if frame is None or frame.empty:
            continue
        path = report_dir / f"{key}.csv"
        frame.to_csv(path, index=False)
        files[key] = str(path)

    xlsx_path = report_dir / f"AML_Surveillance_Report_{report_day}.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        sheet_names = {"kpi": "KPI", "daily": "Daily_Trend", "ctr": "CTR",
                       "str": "STR_Candidates", "watchlist": "Watchlist_Hits",
                       "channels": "Channel_Mix", "countries": "Country_Mix",
                       "alerts": "Alerts", "top_risk": "Top_Risk_TXNs",
                       "risk": "Customer_Risk", "customers": "Customer_Base"}
        for key, frame in data.items():
            if frame is None:
                continue
            frame.to_excel(writer, sheet_name=sheet_names.get(key, key[:28]), index=False)

    layers_html = "".join(
        f"<tr><td style='padding:4px 8px'>{name}</td><td style='padding:4px 8px'>{info['layer']}</td>"
        f"<td style='padding:4px 8px;text-align:right'>{info['rows']:,}</td>"
        f"<td style='padding:4px 8px;text-align:right'>{info['seconds']}s</td></tr>"
        for name, info in transforms.items()
    )
    s3_rows = "".join(
        f"<tr><td style='padding:3px 8px'>{obj['table']}</td><td style='padding:3px 8px;font-size:10px'>{obj['s3_uri']}</td>"
        f"<td style='padding:3px 8px;text-align:right'>{obj['rows']:,}</td>"
        f"<td style='padding:3px 8px;text-align:right'>{obj['size_bytes'] / 1024:.1f} KB</td></tr>"
        for obj in run["s3_objects"]
    )

    html = f"""
<html><body style="font-family:Segoe UI,Arial,sans-serif;background:#f8fafc;padding:18px;color:#0f172a">
<div style="max-width:980px;margin:0 auto;background:#fff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden">
  <div style="background:#0f172a;color:#fff;padding:18px 22px">
    <div style="font-size:12px;letter-spacing:2px;color:#38bdf8">NANOPRO AI STUDIO · AML SURVEILLANCE</div>
    <h1 style="margin:6px 0 2px;font-size:22px">Daily AML Business Report — {report_day}</h1>
    <div style="font-size:12px;color:#94a3b8">Run {run['run_id']} · {run['mode']} load · batch {run['batch_id']} · generated {_ts(_now_ist())} IST</div>
  </div>
  <div style="padding:20px 22px">
    <h2 style="font-size:15px;margin:0 0 8px">1. Executive KPI</h2>
    <table style="border-collapse:collapse;width:100%;font-size:12px">
      <tr><td style="padding:6px 8px;background:#f1f5f9">Transactions</td><td style="padding:6px 8px"><b>{int(kpi.get('TXNS', 0) or 0):,}</b></td>
          <td style="padding:6px 8px;background:#f1f5f9">Value</td><td style="padding:6px 8px"><b>{_fmt_money(kpi.get('AMOUNT_INR'))}</b></td>
          <td style="padding:6px 8px;background:#f1f5f9">Active customers</td><td style="padding:6px 8px"><b>{int(kpi.get('ACTIVE_CUSTOMERS', 0) or 0):,}</b></td></tr>
      <tr><td style="padding:6px 8px;background:#f1f5f9">Cash transactions</td><td style="padding:6px 8px">{int(kpi.get('CASH_TXNS', 0) or 0):,}</td>
          <td style="padding:6px 8px;background:#f1f5f9">CTR flagged</td><td style="padding:6px 8px"><b style="color:#dc2626">{int(kpi.get('CTR_TXNS', 0) or 0):,}</b></td>
          <td style="padding:6px 8px;background:#f1f5f9">Avg risk score</td><td style="padding:6px 8px">{kpi.get('AVG_RISK_SCORE', 0)}</td></tr>
      <tr><td style="padding:6px 8px;background:#f1f5f9">Cross-border</td><td style="padding:6px 8px">{int(kpi.get('CROSS_BORDER_TXNS', 0) or 0):,}</td>
          <td style="padding:6px 8px;background:#f1f5f9">High-risk country</td><td style="padding:6px 8px"><b style="color:#dc2626">{int(kpi.get('HIGH_RISK_COUNTRY_TXNS', 0) or 0):,}</b></td>
          <td style="padding:6px 8px;background:#f1f5f9">Watchlist / PEP</td><td style="padding:6px 8px"><b>{int(customers.get('WATCHLIST_CUSTOMERS', 0) or 0)}</b> / <b>{int(customers.get('PEP_CUSTOMERS', 0) or 0)}</b></td></tr>
    </table>

    <h2 style="font-size:15px;margin:18px 0 4px">2. CTR — Cash Transactions ≥ ₹10 Lakh</h2>
    {_html_table(data['ctr'], 15)}
    <h2 style="font-size:15px;margin:18px 0 4px">3. STR Candidates</h2>
    {_html_table(data['str'], 15)}
    <h2 style="font-size:15px;margin:18px 0 4px">4. Watchlist Hits</h2>
    {_html_table(data['watchlist'], 15)}
    <h2 style="font-size:15px;margin:18px 0 4px">5. Highest-Risk Transactions</h2>
    {_html_table(data['top_risk'], 15)}
    <h2 style="font-size:15px;margin:18px 0 4px">6. Alert Breakdown</h2>
    {_html_table(data['alerts'], 12)}
    <h2 style="font-size:15px;margin:18px 0 4px">7. Channel Mix</h2>
    {_html_table(data['channels'], 12)}
    <h2 style="font-size:15px;margin:18px 0 4px">8. Snowflake Layers</h2>
    <table style="border-collapse:collapse;width:100%;font-size:12px">
      <tr><th style="text-align:left;padding:5px 8px;background:#0f172a;color:#fff">Object</th>
          <th style="text-align:left;padding:5px 8px;background:#0f172a;color:#fff">Layer</th>
          <th style="text-align:right;padding:5px 8px;background:#0f172a;color:#fff">Rows</th>
          <th style="text-align:right;padding:5px 8px;background:#0f172a;color:#fff">Build</th></tr>
      {layers_html}
    </table>
    <h2 style="font-size:15px;margin:18px 0 4px">9. Raw Parquet Objects in AWS S3</h2>
    <table style="border-collapse:collapse;width:100%;font-size:12px">
      <tr><th style="text-align:left;padding:5px 8px;background:#0f172a;color:#fff">Table</th>
          <th style="text-align:left;padding:5px 8px;background:#0f172a;color:#fff">S3 URI</th>
          <th style="text-align:right;padding:5px 8px;background:#0f172a;color:#fff">Rows</th>
          <th style="text-align:right;padding:5px 8px;background:#0f172a;color:#fff">Size</th></tr>
      {s3_rows}
    </table>
    <p style="font-size:11px;color:#64748b;margin-top:16px">
      Automated AML surveillance report generated by NanoPro AI Studio. Source system: {SOURCE_SYSTEM} (DuckDB),
      landing: AWS S3 Parquet, warehouse: Snowflake {DB} ({L0} → {L1} → {L2}).
      Files attached: XLSX workbook and per-section CSV extracts.
    </p>
  </div>
</div>
</body></html>
"""
    html_path = report_dir / f"AML_Surveillance_Report_{report_day}.html"
    html_path.write_text(html, encoding="utf-8")
    return {
        "report_day": report_day,
        "html_path": str(html_path),
        "xlsx_path": str(xlsx_path),
        "csv_files": files,
        "kpi": {k: (None if pd.isna(v) else v) for k, v in dict(kpi).items()},
        "customers": {k: (None if pd.isna(v) else v) for k, v in dict(customers).items()},
        "html": html,
    }


# ---------------------------------------------------------------------------
# delivery
# ---------------------------------------------------------------------------

def _deliver(run: Dict[str, Any], report: Dict[str, Any]) -> Dict[str, Any]:
    kpi = report.get("kpi") or {}
    day = report.get("report_day")
    subject = f"NanoPro AML Surveillance — Daily Report {day} [{run['mode']}] {run['run_id']}"
    plain = (
        f"AML Surveillance Daily Report — {day}\n"
        f"Run: {run['run_id']} ({run['mode']} load)\n"
        f"Transactions: {int(kpi.get('TXNS') or 0):,}\n"
        f"Value: {_fmt_money(kpi.get('AMOUNT_INR'))}\n"
        f"CTR flagged: {int(kpi.get('CTR_TXNS') or 0):,}\n"
        f"STR candidates: {len(pd.read_csv(report['csv_files']['str'])) if 'str' in report['csv_files'] else 0}\n"
        f"Watchlist hits: {len(pd.read_csv(report['csv_files']['watchlist'])) if 'watchlist' in report['csv_files'] else 0}\n"
        f"Report: attached XLSX workbook + CSV extracts\n"
    )
    result: Dict[str, Any] = {}

    try:
        from app.core.smtp_client import smtp_client

        attachments = [report["xlsx_path"]] + list(report["csv_files"].values())[:4]
        email_res = smtp_client.send_email(
            recipient=REPORT_EMAIL, subject=subject, body=plain,
            html_body=report["html"], attachments=attachments,
            task_id=run["run_id"], report_name="AML Daily Surveillance Report",
            data_source="Snowflake L2_CURATED.AML_DAILY_SUMMARY",
        )
        result["email"] = {
            "to": REPORT_EMAIL,
            "success": bool(email_res.get("success") or email_res.get("status") in ("success", "sent")),
            "provider": email_res.get("provider") or email_res.get("active_tier") or email_res.get("mode"),
            "detail": {k: v for k, v in email_res.items() if k in ("status", "error", "provider", "message_id", "tier_used")},
        }
    except Exception as exc:
        result["email"] = {"to": REPORT_EMAIL, "success": False, "error": str(exc)[:300]}

    summary_text = (
        f"*NanoPro AML Surveillance* — {day}\n"
        f"Mode: {run['mode']} · run {run['run_id']}\n"
        f"Transactions: {int(kpi.get('TXNS') or 0):,} · value {_fmt_money(kpi.get('AMOUNT_INR'))}\n"
        f"CTR flagged: {int(kpi.get('CTR_TXNS') or 0):,} · high-risk country txns: {int(kpi.get('HIGH_RISK_COUNTRY_TXNS') or 0):,}\n"
        f"STR candidates: {len(pd.read_csv(report['csv_files']['str'])) if 'str' in report['csv_files'] else 0}"
        f" · watchlist hits: {len(pd.read_csv(report['csv_files']['watchlist'])) if 'watchlist' in report['csv_files'] else 0}\n"
        f"Report emailed to {REPORT_EMAIL} (XLSX + CSV attached)."
    )
    try:
        from app.core.communication_center import communication_center

        wa_res = communication_center.send_whatsapp_cloud_api(WHATSAPP_TO, summary_text)
        result["whatsapp"] = {
            "to": WHATSAPP_TO,
            "success": bool(wa_res.get("success")),
            "message_id": wa_res.get("message_id"),
            "detail": wa_res.get("status") or wa_res.get("error"),
        }
    except Exception as exc:
        result["whatsapp"] = {"to": WHATSAPP_TO, "success": False, "error": str(exc)[:300]}

    try:
        from app.core.telegram_router import send_telegram_routed_message

        tg_text = summary_text.replace("*", "<b>", 1).replace("*", "</b>", 1).replace("\n", "\n")
        tg_res = send_telegram_routed_message(
            category="reports", text=tg_text, document_path=report["xlsx_path"]
        )
        result["telegram"] = {
            "success": bool(tg_res.get("success")),
            "bot": tg_res.get("bot_used"),
            "detail": tg_res.get("error") or tg_res.get("status"),
        }
    except Exception as exc:
        result["telegram"] = {"success": False, "error": str(exc)[:300]}

    return result


# ---------------------------------------------------------------------------
# orchestrator
# ---------------------------------------------------------------------------

def _execute(run: Dict[str, Any]) -> None:
    mode = run["mode"]
    try:
        _stage(run, "source_database", "running", "DuckDB landing")
        started = time.time()
        frames = build_batch(mode, run["batch_id"])
        run["counts"]["source"] = {name: int(len(frame)) for name, frame in frames.items()}
        run["counts"]["duckdb"] = _append_to_duckdb(frames, mode)
        _stage(run, "source_database", "success",
               {"tables": len(frames), "seconds": round(time.time() - started, 2),
                "engine": "DuckDB", "path": str(SOURCE_DB)})

        _stage(run, "s3_parquet", "running", "Writing raw Parquet")
        started = time.time()
        run["s3_objects"] = _upload_parquet(frames, mode, run["batch_id"], run["run_id"])
        _stage(run, "s3_parquet", "success",
               {"objects": len(run["s3_objects"]), "seconds": round(time.time() - started, 2),
                "format": "parquet", "content_type": "application/vnd.apache.parquet"})

        _stage(run, "snowflake_l0", "running", "Loading raw tables")
        started = time.time()
        run["snowflake"]["l0"] = _load_snowflake(frames, mode)
        _stage(run, "snowflake_l0", "success",
               {"tables": len(run["snowflake"]["l0"]), "seconds": round(time.time() - started, 2)})

        _stage(run, "snowflake_l1_l2", "running", "Harmonize + curate")
        started = time.time()
        transforms = _run_transforms(mode)
        run["snowflake"]["transforms"] = transforms
        run["counts"]["l1"] = {k: v["rows"] for k, v in transforms.items() if v["layer"] == "L1"}
        run["counts"]["l2"] = {k: v["rows"] for k, v in transforms.items() if v["layer"] == "L2"}
        _stage(run, "snowflake_l1_l2", "success",
               {"objects": len(transforms), "seconds": round(time.time() - started, 2)})

        _stage(run, "report", "running", "Building business report")
        started = time.time()
        data = _query_reports(_latest_report_day())
        report = _build_report(run, data, transforms)
        run["report"] = {
            "report_day": report["report_day"],
            "xlsx_path": report["xlsx_path"],
            "html_path": report["html_path"],
            "csv_files": report["csv_files"],
            "kpi": report["kpi"],
            "customers": report["customers"],
        }
        _stage(run, "report", "success",
               {"seconds": round(time.time() - started, 2), "files": 2 + len(report["csv_files"])})

        _stage(run, "delivery", "running", "Email + WhatsApp + Telegram")
        started = time.time()
        run["delivery"] = _deliver(run, report)
        _stage(run, "delivery", "success",
               {"seconds": round(time.time() - started, 2),
                "email": run["delivery"].get("email", {}).get("success"),
                "whatsapp": run["delivery"].get("whatsapp", {}).get("success"),
                "telegram": run["delivery"].get("telegram", {}).get("success")})

        run["status"] = "success"
    except Exception as exc:
        run["status"] = "failed"
        run["error"] = f"{type(exc).__name__}: {exc}"
        run["traceback"] = traceback.format_exc()[-1800:]
        for entry in run["stages"]:
            if entry["status"] == "running":
                entry["status"] = "failed"
                entry["detail"] = run["error"]
    finally:
        run["finished_at"] = _ts(_now_ist())
        _persist(run)


def start_run(mode: str = "FULL", user: str = "") -> Dict[str, Any]:
    mode = "INCREMENTAL" if str(mode).upper().startswith("INC") else "FULL"
    if not _PIPELINE_LOCK.acquire(blocking=False):
        active = next((r for r in list_runs(5) if r.get("status") == "running"), None)
        return {"status": "busy", "active_run_id": (active or {}).get("run_id"),
                "message": "An AML pipeline run is already in progress."}
    run = _new_run(mode, user)
    with _RUNS_LOCK:
        _RUNS[run["run_id"]] = run
    _persist(run)

    def _worker() -> None:
        try:
            _execute(run)
        finally:
            _PIPELINE_LOCK.release()

    threading.Thread(target=_worker, name=f"aml-{run['run_id']}", daemon=True).start()
    return run


def wait_run(run_id: str, timeout: float = 75.0) -> Dict[str, Any]:
    deadline = time.time() + max(timeout, 1)
    while time.time() < deadline:
        run = get_run(run_id) or {}
        if run.get("status") in ("success", "failed"):
            return run
        time.sleep(1.0)
    return get_run(run_id) or {}


def summary_lines(run: Dict[str, Any]) -> str:
    if not run:
        return "No AML pipeline runs found yet."
    status = run.get("status")
    counts = run.get("counts") or {}
    s3_rows = sum(int(o.get("rows") or 0) for o in run.get("s3_objects") or [])
    delivery = run.get("delivery") or {}
    lines = [
        f"AML pipeline {run.get('run_id')} — {str(run.get('mode') or '').title()} load — {status.upper()}",
        f"Source (DuckDB): " + ", ".join(f"{k.replace('AML_','').replace('_RAW','').lower()} {v}" for k, v in (counts.get("source") or {}).items()),
        f"S3 Parquet: {len(run.get('s3_objects') or [])} objects, {s3_rows:,} rows verified",
    ]
    l0 = run.get("snowflake", {}).get("l0") or {}
    if l0:
        lines.append("Snowflake L0: " + ", ".join(f"{k.replace('AML_','').replace('_RAW','')} {v['table_rows']:,}" for k, v in l0.items()))
    l1 = counts.get("l1") or {}
    l2 = counts.get("l2") or {}
    if l1:
        lines.append("L1 harmonized: " + ", ".join(f"{k.replace('AML_HARM_','')} {v:,}" for k, v in l1.items()))
    if l2:
        lines.append("L2 curated: " + ", ".join(f"{k.replace('AML_','')} {v:,}" for k, v in l2.items()))
    report = run.get("report") or {}
    if report:
        lines.append(f"Report: {report.get('report_day')} | KPI " + ", ".join(
            f"{k} {v}" for k, v in (report.get("kpi") or {}).items() if k in ("TXNS", "CTR_TXNS", "HIGH_RISK_COUNTRY_TXNS")))
        lines.append(f"Files: {Path(str(report.get('xlsx_path'))).name}")
    if delivery:
        email = delivery.get("email") or {}
        wa = delivery.get("whatsapp") or {}
        tg = delivery.get("telegram") or {}
        lines.append(
            f"Delivery: email {REPORT_EMAIL} {'OK' if email.get('success') else 'FAILED'}"
            f" | WhatsApp {WHATSAPP_TO} {'OK' if wa.get('success') else 'FAILED'}"
            f" | Telegram {'OK' if tg.get('success') else 'FAILED'}"
        )
    if run.get("error"):
        lines.append(f"Error: {run['error']}")
    return "\n".join(lines)


def run_now(mode: str = "FULL", user: str = "", wait_seconds: float = 75.0) -> Dict[str, Any]:
    started = start_run(mode, user)
    if started.get("status") == "busy":
        return started
    return wait_run(started["run_id"], timeout=wait_seconds)
