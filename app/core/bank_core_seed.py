"""Seed the bank-style source model into BigQuery and SFTP.

Every new table gets exactly 100 rows (the user's volume target), keys come
from the real CBS snapshots so joins work, and the same rows are emitted as
I/U/D CDC events with a commit SCN.  The CDC batch is written once to the S3
raw zone (immutable, ``dt=/batch=``) and mirrored to ``CDC_EVENTS`` in
BigQuery so the Snowflake layer builder can replay it.

No Oracle, no credit-card source and no paid service is used.
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import threading
import time
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional, Tuple

from app.core import bank_core_model as model
from app.core.logger import log_event

IST = timezone(timedelta(hours=5, minutes=30))
_LOCK = threading.Lock()

STATE: Dict[str, Any] = {
    "status": "idle",
    "running": False,
    "started_at": "",
    "finished_at": "",
    "rows_per_table": model.ROWS_PER_TABLE,
    "steps": [],
    "counts": {},
    "errors": [],
    "batch_id": "",
    "raw": {},
    "sftp": {},
    "export": {},
}

NAMES = (
    "Rahul Sharma", "Priya Patil", "Amit Deshmukh", "Sneha Joshi", "Vikram Rao",
    "Anjali Kulkarni", "Rohit Mehta", "Kavita Nair", "Suresh Iyer", "Meera Gupta",
    "Arjun Singh", "Pooja Bhosale", "Farhan Khan", "Neha Verma", "Kiran Reddy",
    "Sanjay Menon", "Isha Patel", "Aditya Joshi", "Riya Shah", "Kabir Nair",
)
CITIES = ("Mumbai", "Pune", "Nagpur", "Nashik", "Thane", "Kolhapur", "Aurangabad", "Solapur")
STATES = ("Maharashtra", "Karnataka", "Gujarat", "Delhi", "Tamil Nadu", "Telangana", "Kerala")
OCCUPATIONS = ("SALARIED", "SELF_EMPLOYED", "BUSINESS", "AGRICULTURE", "STUDENT", "RETIRED", "HOUSEWIFE")
CONSTITUTIONS = ("INDIVIDUAL", "PROPRIETORSHIP", "PARTNERSHIP", "PRIVATE_LTD", "PUBLIC_LTD", "HUF")
SECTORS = ("AGRICULTURE", "MANUFACTURING", "SERVICES", "TRADE", "INFRASTRUCTURE", "HOUSING", "EDUCATION", "EXPORT")
MSME = ("MICRO", "SMALL", "MEDIUM", "NOT_MSME")
SECURITY_TYPES = ("PROPERTY", "GOLD", "FIXED_DEPOSIT", "SHARES", "VEHICLE", "PLEDGE")
CHANNELS = ("UPI", "NEFT", "RTGS", "IMPS", "ATM", "CASH_DEPOSIT", "CASH_WITHDRAWAL",
            "MOBILE_BANKING", "INTERNET_BANKING", "BRANCH", "SWIFT", "POS", "ECOM")
TXN_TYPES = ("TRANSFER", "DEPOSIT", "WITHDRAWAL", "PAYMENT", "COLLECTION", "FX_CONVERSION")
COUNTRIES = ("IN", "IN", "IN", "AE", "SG", "US", "GB", "HK", "IR", "PK", "NP", "BD", "LK", "MY")
CCYS = ("INR", "INR", "USD", "EUR", "GBP", "AED", "SGD")
MCCS = ("5411", "5812", "4814", "6011", "4111", "5732", "5999", "5310", "5661", "7011")
NETWORKS = ("RUPAY", "VISA", "MASTERCARD")
LIST_SOURCES = ("UNSC", "OFAC", "RBI_CAUTION", "INTERPOL", "FATF")
RISK_BANDS = ("LOW", "LOW", "MEDIUM", "MEDIUM", "HIGH", "CRITICAL")
SEVERITIES = ("LOW", "MEDIUM", "HIGH", "CRITICAL")
AML_RULES = (
    ("AML_R001", "STRUCTURING"), ("AML_R002", "HIGH_VALUE_CASH"),
    ("AML_R003", "CROSS_BORDER_HIGH_RISK"), ("AML_R004", "WATCHLIST_MATCH"),
    ("AML_R005", "VELOCITY"), ("AML_R006", "PEP_ACTIVITY"),
)
GL_TYPES = ("ASSET", "LIABILITY", "INCOME", "EXPENSE")
PRODUCTS = (
    ("PROD_SB", "SAVINGS", "SAVINGS"), ("PROD_CA", "CURRENT", "CURRENT"),
    ("PROD_TD", "TERM_DEPOSIT", "TERM_DEPOSIT"), ("PROD_OD", "OVERDRAFT", "OVERDRAFT"),
    ("PROD_HL", "HOME_LOAN", "LOAN"), ("PROD_PL", "PERSONAL_LOAN", "LOAN"),
    ("PROD_AGRI", "AGRI_LOAN", "LOAN"), ("PROD_CC", "CASH_CREDIT", "OVERDRAFT"),
)
FACILITY_TYPES = ("TERM_LOAN", "CASH_CREDIT", "OVERDRAFT", "DEMAND_LOAN", "LC", "BANK_GUARANTEE")
REPAYMENT = ("MONTHLY", "QUARTERLY", "HALF_YEARLY", "BULLET")
BUCKETS = ("1D", "7D", "14D", "1M", "3M", "6M", "1Y", "3Y", "5Y")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def _pick(values: Iterable[Any], index: int) -> Any:
    values = tuple(values)
    return values[(index - 1) % len(values)] if values else ""


def _key(table: str, index: int) -> str:
    letters = "".join(part[0] for part in str(table).split("_") if part)[:6] or "ROW"
    return f"{letters}{index:06d}"


def _money(table: str, column: str, index: int) -> float:
    upper = column.upper()
    if table in ("HTD_EXT", "VCT_EXT"):
        base = 5000 + (index * 9137) % 2_450_000
    elif table in ("TAM_LAM_EXT", "CREDIT_FACILITY", "RESTRUCTURE_HISTORY"):
        base = 100_000 + (index * 91_337) % 49_000_000
    elif table in ("GL_BALANCE_DAILY", "CRR_SLR_POSITION", "BORROWING_MASTER", "INVESTMENT_PORTFOLIO"):
        base = 10_000_000 + (index * 913_337) % 490_000_000
    elif table in ("UPI_TRANSACTION", "DEBIT_CARD_TRANSACTION", "ATM_SWITCH"):
        base = 100 + (index * 137) % 49_900
    elif table == "UPI_SETTLEMENT":
        base = 1_000_000 + (index * 71_337) % 99_000_000
    elif table in ("NEFT_RTGS_BATCH", "TREASURY_DEAL", "NOSTRO_ACCOUNT", "TRADE_DOCUMENT"):
        base = 500_000 + (index * 513_337) % 99_000_000
    elif "BAL" in upper or "AMOUNT" in upper or "VALUE" in upper:
        base = 10_000 + (index * 71_337) % 4_900_000
    else:
        base = 1_000 + (index * 137) % 99_000
    return round(float(base), 2)


def _date_value(column: str, index: int, today: date) -> str:
    upper = column.upper()
    if upper == "DOB":
        return (date(1960, 1, 1) + timedelta(days=(index * 211) % 15000)).isoformat()
    if "EXPIRY" in upper:
        return (today + timedelta(days=365 + (index * 17) % 1500)).isoformat()
    if upper in ("MATURITY_DATE", "LIMIT_EXPIRY_DATE"):
        return (today + timedelta(days=90 + (index * 37) % 3000)).isoformat()
    if upper == "NEXT_REPAYMENT_DATE":
        return (today + timedelta(days=1 + index % 30)).isoformat()
    if upper in ("AS_OF_DATE",):
        return (today - timedelta(days=index % 20)).isoformat()
    if upper in ("TXN_DATE", "TRAN_DATE", "VALUE_DATE", "BATCH_DATE", "SETTLEMENT_DATE"):
        return (today - timedelta(days=index % 30)).isoformat()
    if upper in ("LAST_CREDIT_DATE", "LAST_DEBIT_DATE", "LAST_REVIEW_DATE"):
        return (today - timedelta(days=index % 120)).isoformat()
    if upper in ("NPA_DATE", "SMA_DATE"):
        return (today - timedelta(days=30 + index % 150)).isoformat()
    return (today - timedelta(days=index % 365)).isoformat()


def _value(table: str, column: str, type_sql: str, index: int, today: date) -> Any:
    upper = column.upper()
    base = type_sql.split("(", 1)[0].upper()
    if base == "DATE":
        return _date_value(column, index, today)
    if base == "TIMESTAMP":
        return (_now() - timedelta(minutes=index)).isoformat(timespec="seconds")
    if base == "BOOL":
        return index % 3 != 0
    if base == "INT64":
        if "DPD" in upper:
            return (index * 7) % 181
        if "SCORE" in upper or "MATCH_SCORE" in upper:
            return 25 + (index * 13) % 75
        if "COUNT" in upper:
            return 1 + (index * 17) % 500
        if "DAYS" in upper or "DOWNTIME" in upper:
            return (index * 11) % 720
        if "RATING" in upper or "WEIGHT" in upper:
            return 1 + index % 150
        return index
    if base in ("FLOAT64", "NUMERIC", "BIGNUMERIC"):
        if "RATE" in upper or "COUPON" in upper or "YIELD" in upper:
            return round(2.5 + ((index * 37) % 100) / 10.0, 4)
        if "WEIGHT" in upper:
            return float((index % 3) * 50 + 50)
        if "PCT" in upper or "SHARE" in upper or "VOTING" in upper or "UTILISATION" in upper:
            return round(5 + (index * 7) % 95, 2)
        if "DURATION" in upper:
            return round(0.5 + (index % 60) / 10.0, 4)
        return _money(table, column, index)
    # STRING / everything else
    if "IFSC" in upper:
        return f"NPBL0{index:06d}"
    if upper in ("PAYER_VPA", "VPA"):
        return f"user{index:04d}@oknanopro"
    if upper == "PAYEE_VPA":
        return f"merchant{index:04d}@oknanopro"
    if "PAN" in upper and "MASKED" in upper:
        return f"ABCDE{index % 10000:04d}F"
    if "MASKED_PAN" in upper:
        return f"XXXX XXXX XXXX {1000 + index % 9000}"
    if "AADHAAR" in upper:
        return f"tok_{index:08x}"
    if "MOBILE" in upper or "PHONE" in upper:
        return f"98******{index % 100:02d}"
    if "EMAIL" in upper:
        return f"user{index:04d}@***.com"
    if upper == "TIN":
        return f"TIN{index:06d}"
    if "PIN" in upper:
        return f"4000{index % 100:02d}"
    if upper in ("CITY", "TXN_CITY"):
        return _pick(CITIES, index)
    if upper in ("STATE", "REGISTERED_STATE"):
        return _pick(STATES, index)
    if "NAME" in upper:
        return _pick(NAMES, index)
    if "GENDER" in upper:
        return "M" if index % 2 else "F"
    if "NATIONALITY" in upper or "TAX_RESIDENCY" in upper:
        return "IN"
    if "OCCUPATION" in upper:
        return _pick(OCCUPATIONS, index)
    if "CONSTITUTION" in upper:
        return _pick(CONSTITUTIONS, index)
    if "SECTOR" in upper:
        return _pick(SECTORS, index)
    if "MSME" in upper:
        return _pick(MSME, index)
    if "SECURITY_TYPE" in upper:
        return _pick(SECURITY_TYPES, index)
    if "COUNTRY" in upper:
        return _pick(COUNTRIES, index)
    if "CCY" in upper or "CURRENCY" in upper:
        return _pick(CCYS, index)
    if upper in ("MCC",):
        return f"5{100 + index:03d}"
    if "NETWORK" in upper:
        return _pick(NETWORKS, index)
    if "LIST_SOURCE" in upper:
        return _pick(LIST_SOURCES, index)
    if "RISK" in upper or "SEVERITY" in upper:
        return _pick(RISK_BANDS if "RISK" in upper else SEVERITIES, index)
    if upper in ("RULE_CODE",):
        return AML_RULES[index % len(AML_RULES)][0]
    if upper in ("RULE_NAME",):
        return AML_RULES[index % len(AML_RULES)][1]
    if upper == "REPORT_TYPE":
        return _pick(("CTR", "CBWTR", "STR", "CIMS", "PSL", "ALM", "FMR"), index)
    if upper == "BATCH_TYPE":
        return _pick(("NEFT", "RTGS", "IMPS"), index)
    if upper == "DIRECTION":
        return _pick(("INWARD", "OUTWARD"), index)
    if upper == "TXN_TYPE":
        if table == "UPI_TRANSACTION":
            return _pick(("P2P", "P2M", "COLLECT", "MANDATE"), index)
        if table == "ATM_SWITCH":
            return _pick(("CASH_WITHDRAWAL", "BALANCE_ENQUIRY", "MINI_STATEMENT"), index)
        return _pick(TXN_TYPES, index)
    if upper == "CHANNEL" or upper == "TRAN_MODE" or upper == "INITIATION_MODE":
        return _pick(CHANNELS, index)
    if upper == "GL_TYPE":
        return _pick(GL_TYPES, index)
    if upper == "HTM_AFS_HFT":
        return _pick(("HTM", "AFS", "HFT"), index)
    if upper == "DEAL_TYPE":
        return _pick(("FX", "MM", "SECURITIES", "DERIVATIVE"), index)
    if upper == "BUY_SELL":
        return _pick(("BUY", "SELL"), index)
    if upper == "CCY_PAIR":
        return _pick(("USD/INR", "EUR/INR", "GBP/INR", "AED/INR", "SGD/INR"), index)
    if upper == "INSTRUMENT_TYPE":
        return _pick(("BORROWING_TERM", "BORROWING_CALL", "REFINANCE", "CBLO"), index)
    if upper == "FACILITY_TYPE":
        return _pick(FACILITY_TYPES, index)
    if upper == "REPAYMENT_FREQ" or upper == "REPRICING_FREQ":
        return _pick(REPAYMENT, index)
    if upper == "INTEREST_TYPE":
        return _pick(("FIXED", "FLOATING"), index)
    if upper == "CAL_TYPE":
        return _pick(("CURRENCY", "HOLIDAY"), index)
    if upper == "BUCKET":
        return _pick(BUCKETS, index)
    if upper == "CASH_POSITION":
        return _pick(("LOW", "MEDIUM", "HIGH"), index)
    if upper == "RESPONSE_CODE":
        return _pick(("00", "00", "00", "51", "91", "05"), index)
    if upper == "STATUS":
        if table in ("UPI_TRANSACTION", "DEBIT_CARD_TRANSACTION", "ATM_SWITCH", "NEFT_RTGS_BATCH"):
            return _pick(("SUCCESS", "SUCCESS", "SUCCESS", "PENDING", "FAILED", "REVERSED"), index)
        if table in ("KYC_DOCUMENT", "CUSTOMER_CONTACT", "DEBIT_CARD_MASTER", "UPI_MERCHANT"):
            return _pick(("ACTIVE", "ACTIVE", "ACTIVE", "BLOCKED", "EXPIRED"), index)
        if table in ("AML_ALERT", "AML_CASE", "STR_REGISTER", "REGULATORY_FILING", "SCREENING_RESULT"):
            return _pick(("OPEN", "UNDER_REVIEW", "CLOSED", "FILED", "PENDING"), index)
        if table == "TRADE_DOCUMENT":
            return _pick(("ISSUED", "AMENDED", "SETTLED", "EXPIRED"), index)
        return _pick(("ACTIVE", "ACTIVE", "CLOSED", "DORMANT"), index)
    if upper == "SEVERITY":
        return _pick(SEVERITIES, index)
    if upper == "DISPOSITION":
        return _pick(("NO_ACTION", "ESCALATED", "FALSE_POSITIVE", "STR_FILED"), index)
    if upper == "ENTITY_TYPE":
        return _pick(("INDIVIDUAL", "ENTITY", "VESSEL"), index)
    if upper == "OWNERSHIP_TYPE":
        return _pick(("DIRECT", "INDIRECT", "BENEFICIAL"), index)
    if upper == "UBO_TYPE":
        return _pick(("INDIVIDUAL", "CORPORATE", "TRUST"), index)
    if upper == "PURPOSE" or upper == "PURPOSE_CODE":
        return _pick(("SALARY", "TRADE", "EDUCATION", "MEDICAL", "TRAVEL", "OTHERS"), index)
    if upper == "FATCA_STATUS" or upper == "CRS_STATUS":
        return _pick(("COMPLIANT", "NON_COMPLIANT", "PENDING"), index)
    if upper == "SOURCE_OF_FUNDS":
        return _pick(("SALARY", "BUSINESS", "INVESTMENT", "REMITTANCE", "AGRICULTURE"), index)
    if upper == "NARRATION":
        return _pick(("UPI payment", "NEFT credit", "Cash deposit", "ATM withdrawal", "SWIFT remittance"), index)
    if upper == "DEVICE_ID":
        return f"DEV{index:06d}"
    if upper == "IP_HASH":
        return f"ip_{index:08x}"
    if upper == "INSTRUMENT_NO":
        return f"CHQ{index:09d}"
    if upper == "AUTH_CODE":
        return f"A{index:06d}"
    if upper == "RRN":
        return f"RRN{index:012d}"
    if upper == "NPCI_REF" or upper == "UTR_REF":
        return f"REF{index:012d}"
    if upper == "FILE_REF":
        return f"FILE{index:08d}"
    if upper == "ACK_NO" or upper == "FIU_REF":
        return f"ACK{index:010d}"
    if upper == "FORMAT_VERSION":
        return "v1.0"
    if upper == "PERIOD":
        return f"2026-{1 + index % 12:02d}"
    if upper == "ISIN":
        return f"INE{index:03d}A01{index % 10:01d}"
    if upper == "BANK_BIC":
        return f"NPBLINB{index % 1000:03d}"
    if upper == "BIN":
        return f"60{7100 + index % 900:04d}"
    if upper == "ATM_ID":
        return f"ATM{index:06d}"
    if upper == "BORROWER_PAN_MASKED" or upper == "ID_MASKED" or upper == "DOC_NUMBER_MASKED":
        return f"XXXXX{index % 10000:04d}X"
    if upper == "UDYAM_NO":
        return f"UDYAM-MH-{index:02d}-{index:07d}"
    if upper == "REG_NO":
        return f"REG/{index:04d}/2026"
    if upper == "GROUP_ID":
        return f"GRP{index % 25:03d}"
    if upper == "GROUP_NAME":
        return f"{_pick(NAMES, index).split()[1]} Group"
    if upper in ("GL_CODE", "PARENT_GL"):
        return f"GL{100000 + index:06d}"
    if upper == "PRODUCT_CODE":
        return PRODUCTS[(index - 1) % len(PRODUCTS)][0]
    if upper == "RATING_CODE" or upper == "RATING":
        return f"R{100 + index:03d}"
    if upper == "AGENCY" or upper == "RATING_AGENCY":
        return _pick(("CRISIL", "ICRA", "CARE", "IND_RA"), index)
    if upper == "PSL_CODE":
        return f"PSL{100 + index:03d}"
    if upper == "PSL_CATEGORY":
        return _pick(("AGRICULTURE", "MSME", "EDUCATION", "HOUSING", "EXPORT", "OTHERS"), index)
    if upper == "SUB_CATEGORY":
        return _pick(("SMALL_FARMER", "MICRO_ENTERPRISE", "EDUCATION_LOAN", "AFFORDABLE_HOUSING"), index)
    if upper == "INDUSTRY_CODE":
        return f"IND{100 + index:03d}"
    if upper == "INDUSTRY_NAME":
        return f"{_pick(SECTORS, index)} unit"
    if upper == "SUB_SECTOR":
        return _pick(("CROP", "TEXTILE", "RETAIL", "ROADS", "SCHOOL", "SEZ"), index)
    if upper == "PSL_GROUP":
        return _pick(("PRIORITY", "NON_PRIORITY"), index)
    if upper == "COUNTRY_CODE":
        return f"C{100 + index:03d}"
    if upper == "COUNTRY_NAME":
        return _pick(("India", "UAE", "Singapore", "United States", "United Kingdom", "Hong Kong", "Iran", "Pakistan"), index)
    if upper == "CAL_ID":
        return f"CAL{index:04d}"
    if upper == "CODE":
        return f"CODE{index:05d}"
    if upper == "BRANCH_ZONE":
        return _pick(("WEST", "SOUTH", "NORTH", "EAST", "CENTRAL"), index)
    if upper == "FATF_STATUS":
        return _pick(("COMPLIANT", "GREY", "BLACK", "NON_MEMBER"), index)
    if upper == "BAND":
        return _pick(("AAA", "AA", "A", "BBB", "BB", "B", "C", "D"), index)
    if upper == "CARD_TYPE":
        return "DEBIT"
    if upper == "VALUE_MASKED":
        return f"98******{index % 100:02d}"
    if upper == "DOC_TYPE":
        if table == "TRADE_DOCUMENT":
            return _pick(("LC", "BG", "DA", "DP"), index)
        return _pick(("PAN", "AADHAAR", "PASSPORT", "VOTER_ID"), index)
    if upper == "VERIFICATION_MODE":
        return _pick(("DIGITAL", "BRANCH", "VIDEO_KYC", "AADHAAR_OTP"), index)
    if upper == "REL_TYPE":
        return _pick(("SPOUSE", "PARENT", "SUBSIDIARY", "ASSOCIATE", "SIGNATORY"), index)
    if upper == "GUARANTEE_TYPE":
        return _pick(("PERSONAL", "CORPORATE", "BANK"), index)
    if upper == "CHARGE_TYPE":
        return _pick(("FIRST", "SECOND", "PARI_PASSU"), index)
    if upper == "CHARGE_HOLDER":
        return "NANOPRO BANK"
    if upper == "RESTRUCTURE_TYPE" or upper == "RELIEF_TYPE":
        return _pick(("COVID", "STRESSED", "MSME_RESTRUCTURE", "MORATORIUM"), index)
    if upper == "HTM_AFS_HFT":
        return _pick(("HTM", "AFS", "HFT"), index)
    if upper == "COUNTERPARTY":
        return f"CP-{_pick(NAMES, index).split()[1]}"
    if upper == "SETTLEMENT_STATUS":
        return _pick(("SETTLED", "PENDING", "FAILED"), index)
    if upper == "FILED_AT":
        return (_now() - timedelta(days=index % 30)).isoformat(timespec="seconds")
    if upper == "REVIEWED_BY":
        return _pick(("analyst1", "analyst2", "compliance_officer"), index)
    if upper == "ASSIGNED_TO":
        return _pick(("analyst1", "analyst2", "compliance_officer"), index)
    if upper == "AD_BANK_CODE":
        return f"AD{index % 100:03d}"
    if upper == "SUSPICION_TYPE":
        return _pick(("STRUCTURING", "TERROR_FINANCING", "FRAUD", "CASH_INTENSIVE"), index)
    if upper == "REASON_CODE":
        return _pick(("GOODS_NOT_RECEIVED", "DUPLICATE", "FRAUD", "CUSTOMER_DISPUTE"), index)
    if upper == "NPCI_CYCLE":
        return _pick(("C1", "C2", "C3", "C4"), index)
    if upper == "MERCHANT_NAME":
        return f"{_pick(SECTORS, index).title()} Mart {index:03d}"
    if upper == "ADDRESS" or "ADDRESS_LINE" in upper or "ADDRESS" in upper:
        return f"Flat {index}, MG Road, {_pick(CITIES, index)}"
    if upper == "DESCRIPTION":
        return f"{_pick(SECTORS, index).title()} {index:03d}"
    if upper == "CATEGORY":
        return _pick(("RETAIL", "GROCERY", "FUEL", "TELECOM", "TRAVEL"), index)
    if upper == "RISK_CATEGORY":
        return _pick(RISK_BANDS, index)
    return f"{re.sub(r'[^A-Z0-9]', '', upper)[:10] or 'VAL'}{index:05d}"[:200]


def _finalise(table: str, row: Dict[str, Any], index: int) -> Dict[str, Any]:
    if table == "GL_BALANCE_DAILY":
        row["CLOSING_BAL"] = round(float(row.get("OPENING_BAL") or 0) + float(row.get("DEBIT_AMT") or 0)
                                   - float(row.get("CREDIT_AMT") or 0), 2)
    elif table == "FX_POSITION":
        rate = 83.2
        row["NOP_INR"] = round(float(row.get("OPEN_POSITION") or 0) * rate, 2)
        limit = float(row.get("LIMIT_AMT") or 1)
        row["UTILISATION_PCT"] = round(min(99.0, abs(float(row.get("OPEN_POSITION") or 0)) / limit * 100), 2)
    elif table == "CRR_SLR_POSITION":
        ndtl = float(row.get("NDTL") or 0)
        row["CRR_REQUIRED"] = round(ndtl * 0.04, 2)
        row["CRR_HELD"] = round(ndtl * 0.0404, 2)
        row["SLR_REQUIRED"] = round(ndtl * 0.18, 2)
        row["SLR_HELD"] = round(ndtl * 0.183, 2)
        row["SLR_SECURITIES_VALUE"] = round(ndtl * 0.19, 2)
    elif table == "TAM_LAM_EXT":
        npa = index % 9 == 0
        sma = index % 5 == 0
        provision = 0.004 if npa else (0.001 if sma else 0.0004)
        row["PROVISION_AMT"] = round(float(row.get("SANCTIONED_AMT") or 0) * provision, 2)
        row["RISK_WEIGHT"] = 150.0 if npa else (100.0 if not sma else 125.0)
        if npa:
            row["NPA_DATE"] = (date.today() - timedelta(days=30 + index)).isoformat()
        if sma:
            row["SMA_DATE"] = (date.today() - timedelta(days=30 + index)).isoformat()
    elif table == "UPI_SETTLEMENT":
        row["NET_POSITION"] = round(float(row.get("CREDITS") or 0) - float(row.get("DEBITS") or 0), 2)
    elif table == "DEBIT_CARD_TRANSACTION":
        ccy = str(row.get("CCY") or "INR")
        row["INR_AMOUNT"] = round(float(row.get("AMOUNT") or 0) * (83.2 if ccy != "INR" else 1.0), 2)
        row["FOREIGN_FLAG"] = ccy != "INR"
    elif table == "UPI_TRANSACTION":
        row["DISPUTE_FLAG"] = index % 20 == 0
    return row


def _fk_value(spec_table: str, column: str, parent: Tuple[str, str], keys: Dict[Tuple[str, str], List[Any]],
              index: int) -> Any:
    parent_values = keys.get(parent) or []
    if parent_values:
        return parent_values[(index - 1) % len(parent_values)]
    return _key(parent[0], index)


def _rows_for(spec: Dict[str, Any], index: int, keys: Dict[Tuple[str, str], List[Any]],
              today: date) -> Dict[str, Any]:
    row: Dict[str, Any] = {}
    for column, type_sql in spec["columns"]:
        if column in spec.get("fks", {}):
            row[column] = _fk_value(spec["table"], column, spec["fks"][column], keys, index)
        elif column == spec["pk"][0]:
            row[column] = _key(spec["table"], index)
        else:
            row[column] = _value(spec["table"], column, type_sql, index, today)
    return _finalise(spec["table"], row, index)


def _generation_order(specs: List[Dict[str, Any]], base_keys: Dict[Tuple[str, str], List[Any]]) -> List[Dict[str, Any]]:
    pending = [spec for spec in specs if spec["table"] not in model.BASE_TABLES]
    ready: List[Dict[str, Any]] = []
    done = set(model.BASE_TABLES)
    while pending:
        batch = [
            spec for spec in pending
            if all(parent in done for parent, _ in (spec.get("fks") or {}).values())
        ]
        if not batch:
            batch = [pending[0]]
        for spec in batch:
            ready.append(spec)
            done.add(spec["table"])
            pending = [item for item in pending if item["table"] != spec["table"]]
    return ready


def _ensure_dataset(client: Any, dataset: str) -> None:
    from google.cloud import bigquery

    ref = f"{client.project}.{dataset}"
    try:
        client.get_dataset(ref)
    except Exception:
        client.create_dataset(bigquery.Dataset(ref), exists_ok=True)


def _ensure_table(client: Any, schema: str, table: str, columns: List[Tuple[str, str]]) -> None:
    fqtn = f"{client.project}.{schema}.{table}"
    ddl = ", ".join(f"`{name}` {type_sql}" for name, type_sql in columns)
    try:
        client.query(f"CREATE TABLE IF NOT EXISTS `{fqtn}` ({ddl})").result(timeout=120)
    except Exception as exc:
        log_event(f"[BankCore] create {schema}.{table} failed: {exc}", level="WARNING",
                  component="BankCoreSeed")
        raise
    try:
        existing = {field.name.upper() for field in client.get_table(fqtn).schema}
        for name, type_sql in columns:
            if name.upper() in existing:
                continue
            client.query(f"ALTER TABLE `{fqtn}` ADD COLUMN `{name}` {type_sql}").result(timeout=120)
    except Exception as exc:
        log_event(f"[BankCore] alter {schema}.{table} failed: {exc}", level="WARNING",
                  component="BankCoreSeed")


def _load(client: Any, schema: str, table: str, rows: List[Dict[str, Any]]) -> int:
    from google.cloud import bigquery

    fqtn = f"{client.project}.{schema}.{table}"
    payload = [{name: (float(value) if isinstance(value, Decimal) else value) for name, value in row.items()}
               for row in rows]
    job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
    job = client.load_table_from_json(payload, fqtn, job_config=job_config)
    job.result(timeout=300)
    return int(job.output_rows or len(payload))


def _base_table_ref(client: Any, table: str) -> Optional[str]:
    candidates = [model.BASE_SCHEMA]
    try:
        candidates += [item.dataset_id for item in client.list_datasets()]
    except Exception:
        pass
    seen = set()
    for dataset in candidates:
        if dataset in seen:
            continue
        seen.add(dataset)
        fqtn = f"{client.project}.{dataset}.{table}"
        try:
            client.get_table(fqtn)
            return fqtn
        except Exception:
            continue
    return None


def _fetch_base_keys(client: Any, table: str, pk: str) -> List[Any]:
    fqtn = _base_table_ref(client, table)
    if not fqtn:
        return []
    try:
        job = client.query(f"SELECT `{pk}` FROM `{fqtn}` WHERE `{pk}` IS NOT NULL ORDER BY `{pk}` LIMIT 500")
        return [row[pk] for row in job.result(timeout=120)]
    except Exception:
        return []


def _cdc_events(rows_by_table: Dict[str, List[Dict[str, Any]]], batch_id: str) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    scn = 1000
    base_ts = _now()
    for table, rows in rows_by_table.items():
        spec = model.get(table) or {}
        pk = (spec.get("pk") or ["ID"])[0]
        for row in rows:
            scn += 1
            events.append({
                "EVENT_ID": f"EV{batch_id}_{table}_{scn}",
                "TABLE_NAME": table,
                "OP": "I",
                "COMMIT_SCN": scn,
                "COMMIT_TS": (base_ts + timedelta(milliseconds=scn)).isoformat(timespec="seconds"),
                "PK_JSON": json.dumps({pk: row.get(pk)}, default=str),
                "ROW_JSON": json.dumps(row, default=str),
                "BATCH_ID": batch_id,
            })
        # One update per table proves SCD/merge; three small tables also get a delete.
        if rows:
            updated = dict(rows[0])
            for column in ("STATUS", "DISPOSITION", "RISK_SCORE", "SCORE", "AMOUNT", "CLOSING_BAL", "UTILISATION_PCT"):
                if column in updated and not str(column).endswith("_DATE"):
                    if isinstance(updated[column], bool):
                        updated[column] = not updated[column]
                    elif isinstance(updated[column], (int, float)):
                        updated[column] = round(float(updated[column]) * 1.1, 2)
                    else:
                        updated[column] = f"{updated[column]}_UPDATED"
                    break
            scn += 1
            events.append({
                "EVENT_ID": f"EV{batch_id}_{table}_{scn}",
                "TABLE_NAME": table, "OP": "U", "COMMIT_SCN": scn,
                "COMMIT_TS": (base_ts + timedelta(milliseconds=scn)).isoformat(timespec="seconds"),
                "PK_JSON": json.dumps({pk: updated.get(pk)}, default=str),
                "ROW_JSON": json.dumps(updated, default=str), "BATCH_ID": batch_id,
            })
        if table in ("KYC_DOCUMENT", "CUSTOMER_CONTACT", "UPI_DISPUTE") and len(rows) > 2:
            deleted = rows[1]
            scn += 1
            events.append({
                "EVENT_ID": f"EV{batch_id}_{table}_{scn}",
                "TABLE_NAME": table, "OP": "D", "COMMIT_SCN": scn,
                "COMMIT_TS": (base_ts + timedelta(milliseconds=scn)).isoformat(timespec="seconds"),
                "PK_JSON": json.dumps({pk: deleted.get(pk)}, default=str),
                "ROW_JSON": json.dumps({pk: deleted.get(pk)}, default=str), "BATCH_ID": batch_id,
            })
    return events


def _write_raw(events: List[Dict[str, Any]], batch_id: str) -> Dict[str, Any]:
    try:
        import boto3
        import pyarrow as pa
        import pyarrow.parquet as pq
        from app.core.chat_s3_export import _aws_config

        config = _aws_config()
        if not config.get("bucket"):
            return {"status": "unavailable", "error": "AWS bucket not configured"}
        s3 = boto3.Session(
            region_name=config["region"],
            aws_access_key_id=config["access_key"],
            aws_secret_access_key=config["secret_key"],
        ).client("s3")
        day = _now().strftime("%Y-%m-%d")
        by_table: Dict[str, List[Dict[str, Any]]] = {}
        for event in events:
            by_table.setdefault(event["TABLE_NAME"], []).append(event)
        objects = []
        for table, table_events in by_table.items():
            buffer = io.BytesIO()
            pq.write_table(pa.Table.from_pylist(table_events), buffer)
            key = f"raw/cdc/{table.lower()}/dt={day}/batch={batch_id}/cdc.parquet"
            body = buffer.getvalue()
            s3.put_object(Bucket=config["bucket"], Key=key, Body=body,
                          ContentType="application/vnd.apache.parquet",
                          Metadata={"rows": str(len(table_events)), "batch_id": batch_id})
            objects.append({"table": table, "key": key, "rows": len(table_events), "bytes": len(body)})
        manifest = {"batch_id": batch_id, "generated_at": _iso(_now()), "objects": objects}
        manifest_key = f"raw/cdc/_MANIFEST_{batch_id}.json"
        s3.put_object(Bucket=config["bucket"], Key=manifest_key,
                      Body=json.dumps(manifest, indent=2).encode("utf-8"),
                      ContentType="application/json")
        return {"status": "written", "batch_id": batch_id, "tables": len(objects),
                "events": len(events), "manifest": f"s3://{config['bucket']}/{manifest_key}",
                "objects": objects}
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:240]}


def _seed_sftp(rows_by_table: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    from app.core import sftp_ingestion

    results = []
    for spec in model.sftp_tables():
        table = spec["table"]
        rows = rows_by_table.get(table) or []
        if not rows:
            results.append({"table": table, "status": "skipped", "error": "no rows"})
            continue
        columns = [name for name, _ in spec["columns"]]
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        filename = f"{table.lower()}_{_now().strftime('%Y%m%d')}.csv"
        try:
            uploaded = sftp_ingestion.upload(filename, buffer.getvalue().encode("utf-8"),
                                             partner=spec.get("partner") or "partner")
            ingested = sftp_ingestion.ingest(uploaded["key"])
            results.append({"table": table, "status": ingested.get("status"),
                            "rows": ingested.get("rows"), "key": uploaded["key"],
                            "bronze": ingested.get("bronze_key"), "error": ingested.get("error")})
        except Exception as exc:
            results.append({"table": table, "status": "error", "error": str(exc)[:240]})
    succeeded = [item for item in results if item.get("status") in ("success", "skipped")]
    return {"status": "success" if len(succeeded) == len(results) else "partial",
            "files": results, "ok": len(succeeded), "total": len(results)}


def _step(name: str, status: str, detail: str = "") -> None:
    STATE["steps"].append({"step": name, "status": status, "detail": detail,
                           "at": _iso(_now())})
    del STATE["steps"][-80:]


def seed(rows: int = model.ROWS_PER_TABLE, include_sftp: bool = True) -> Dict[str, Any]:
    """Create/seed the whole bank source model; safe to re-run (idempotent)."""
    if not _LOCK.acquire(blocking=False):
        return {"status": "running", "message": "A bank-core seed is already running."}
    started = time.time()
    STATE.update({"status": "running", "running": True, "started_at": _iso(_now()),
                  "finished_at": "", "steps": [], "errors": [], "counts": {}, "raw": {},
                  "sftp": {}, "export": {}})
    try:
        from app.core.live_catalog import _bigquery_client

        client, auth_source = _bigquery_client()
        _step("bigquery", "connected", auth_source)
        for dataset in (model.CORE_SCHEMA, model.REF_SCHEMA, model.CDC_SCHEMA):
            _ensure_dataset(client, dataset)

        specs = model.bigquery_tables()
        for spec in specs:
            _ensure_table(client, spec["schema"], spec["table"], spec["columns"])
        _ensure_table(client, model.CDC_SCHEMA, model.CDC_TABLE, model.CDC_COLUMNS)
        _step("schema", "ready", f"{len(specs)} BigQuery tables + {model.CDC_TABLE}")

        base_keys: Dict[Tuple[str, str], List[Any]] = {}
        for table, pk in model.BASE_TABLES.items():
            values = _fetch_base_keys(client, table, pk)
            if values:
                base_keys[(table, pk)] = values
        _step("base_keys", "loaded",
              ", ".join(f"{table}:{len(base_keys.get((table, pk)) or [])}" for table, pk in model.BASE_TABLES.items()))

        today = date.today()
        keys = dict(base_keys)
        rows_by_table: Dict[str, List[Dict[str, Any]]] = {}
        order = _generation_order(specs + model.sftp_tables(), base_keys)
        for spec in order:
            generated: List[Dict[str, Any]] = []
            for index in range(1, max(1, int(rows)) + 1):
                generated.append(_rows_for(spec, index, keys, today))
            rows_by_table[spec["table"]] = generated
            keys[(spec["table"], spec["pk"][0])] = [row.get(spec["pk"][0]) for row in generated]
        _step("generate", "done", f"{len(rows_by_table)} tables x {rows} rows")

        counts: Dict[str, int] = {}
        for spec in specs:
            table = spec["table"]
            counts[table] = _load(client, spec["schema"], table, rows_by_table.get(table) or [])
        STATE["counts"] = counts
        _step("bigquery_load", "done", f"{len(counts)} tables, {sum(counts.values())} rows")

        batch_id = "SEED_" + _now().strftime("%Y%m%dT%H%M%SZ")
        events = _cdc_events(rows_by_table, batch_id)
        _load(client, model.CDC_SCHEMA, model.CDC_TABLE, events)
        STATE["batch_id"] = batch_id
        _step("cdc", "loaded", f"{len(events)} events, batch {batch_id}")

        STATE["raw"] = _write_raw(events, batch_id)
        _step("raw", STATE["raw"].get("status", "error"), STATE["raw"].get("manifest", ""))

        if include_sftp:
            STATE["sftp"] = _seed_sftp(rows_by_table)
            _step("sftp", STATE["sftp"].get("status", "error"),
                  f"{STATE['sftp'].get('ok')}/{STATE['sftp'].get('total')} files")
        else:
            STATE["sftp"] = {"status": "skipped"}

        try:
            from app.core.bq_export_scheduler import trigger
            STATE["export"] = trigger("bank_core_seed")
        except Exception as exc:
            STATE["export"] = {"status": "error", "error": str(exc)[:240]}
        _step("export", STATE["export"].get("status", "error"),
              STATE["export"].get("message", ""))

        STATE["status"] = "success"
        STATE["elapsed_s"] = round(time.time() - started, 2)
        log_event(f"[BankCore] seeded {len(counts)} tables x {rows} rows, batch {batch_id}",
                  component="BankCoreSeed")
        return _status_payload()
    except Exception as exc:
        STATE["status"] = "error"
        STATE["errors"].append(str(exc)[:400])
        _step("error", "error", str(exc)[:400])
        log_event(f"[BankCore] seed failed: {exc}", level="ERROR", component="BankCoreSeed")
        return _status_payload()
    finally:
        STATE["running"] = False
        STATE["finished_at"] = _iso(_now())
        _LOCK.release()


def _status_payload() -> Dict[str, Any]:
    return {
        "status": STATE.get("status"),
        "running": STATE.get("running"),
        "started_at": STATE.get("started_at"),
        "finished_at": STATE.get("finished_at"),
        "elapsed_s": STATE.get("elapsed_s"),
        "batch_id": STATE.get("batch_id"),
        "rows_per_table": STATE.get("rows_per_table"),
        "counts": STATE.get("counts") or {},
        "tables": len(STATE.get("counts") or {}),
        "rows": sum((STATE.get("counts") or {}).values()),
        "steps": STATE.get("steps") or [],
        "errors": STATE.get("errors") or [],
        "raw": STATE.get("raw") or {},
        "sftp": STATE.get("sftp") or {},
        "export": STATE.get("export") or {},
    }


def status() -> Dict[str, Any]:
    return _status_payload()


def start(rows: int = model.ROWS_PER_TABLE, include_sftp: bool = True) -> Dict[str, Any]:
    if STATE.get("running"):
        return {"status": "running", "message": "Seed already running."}
    thread = threading.Thread(target=seed, args=(rows, include_sftp), daemon=True,
                              name="bank-core-seed")
    thread.start()
    return {"status": "started", "rows_per_table": rows, "include_sftp": include_sftp}
