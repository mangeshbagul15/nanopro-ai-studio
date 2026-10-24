"""
NanoPro AI Studio - Star Schema Relational Data Factory
Generates realistic, schema-compliant, referentially integrated data
for all 9 Banking Projects across 54 Dimension tables and 37 Fact tables.
"""

from __future__ import annotations

import random
import uuid
import datetime
from typing import Dict, Any, List

INDIAN_CITIES = [
    ("Mumbai", "Maharashtra", "400001"),
    ("Pune", "Maharashtra", "411001"),
    ("Bengaluru", "Karnataka", "560001"),
    ("Hyderabad", "Telangana", "500001"),
    ("Delhi", "Delhi", "110001"),
    ("Chennai", "Tamil Nadu", "600001"),
    ("Kolkata", "West Bengal", "700001"),
    ("Ahmedabad", "Gujarat", "380001"),
    ("Jaipur", "Rajasthan", "302001"),
    ("Nagpur", "Maharashtra", "440001"),
]

MERCHANTS = [
    ("Amazon India", "ECOMMERCE"),
    ("Flipkart", "ECOMMERCE"),
    ("Swiggy", "FOOD_DELIVERY"),
    ("Zomato", "FOOD_DELIVERY"),
    ("Reliance Retail", "SUPERMARKET"),
    ("Tata Neu", "RETAIL"),
    ("Jio Infocomm", "TELECOM"),
    ("MakeMyTrip", "TRAVEL"),
    ("Uber India", "RIDES"),
    ("Apollo Pharmacy", "HEALTHCARE")
]

CHANNELS = ["MOBILE_APP", "NET_BANKING", "UPI", "POS_TERMINAL", "ATM", "BRANCH_COUNTER"]
BRANCHES = [("BR001", "Nariman Point"), ("BR002", "BKC Corporate"), ("BR003", "Connaught Place"), ("BR004", "MG Road Bangalore")]
PRODUCTS = ["SAVINGS_CASA", "CURRENT_ACCOUNT", "FIXED_DEPOSIT", "RECURRING_DEP", "HOME_LOAN", "AUTO_LOAN", "PERSONAL_LOAN", "CORP_OVERDRAFT"]

def _generate_column_value(col_name: str, table_name: str, today: str, yesterday: str, now_str: str, entity_pool: Dict[str, Any]) -> Any:
    col = col_name.lower()

    # Dates
    if col in ("date_of_generation", "gen_date", "generation_date"):
        return today
    if col in ("report_date", "rpt_date", "business_date"):
        return yesterday
    if col in ("execution_date", "exec_date", "created_at", "updated_at"):
        return now_str
    if "expiry" in col or "end_date" in col:
        return (datetime.date.today() + datetime.timedelta(days=random.randint(180, 1000))).strftime("%Y-%m-%d")
    if "start_date" in col or "issue_date" in col or "open_date" in col:
        return (datetime.date.today() - datetime.timedelta(days=random.randint(30, 800))).strftime("%Y-%m-%d")
    if "dob" in col:
        return f"{random.randint(1965, 2002)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    if "timestamp" in col:
        return f"{yesterday} {random.randint(0, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
    if "date" in col:
        return yesterday

    # Financial / Numeric Amounts
    if any(k in col for k in ("amount", "limit", "balance", "inr", "crr", "slr", "cashflow", "exposure")):
        return round(random.uniform(500.0, 1500000.0), 2)
    if "fee" in col or "gst" in col or "tax" in col or "cashback" in col or "penalty" in col:
        return round(random.uniform(10.0, 5000.0), 2)
    if any(k in col for k in ("score", "rate", "yield", "pct", "percent")):
        return round(random.uniform(5.5, 99.5), 2)
    if "count" in col or "qty" in col or "tenor" in col or "tenure" in col:
        return random.randint(1, 360)

    # Identifiers & Keys
    if "card_number" in col:
        return f"**** **** **** {random.randint(1000, 9999)}"
    if "pan" in col:
        return f"ABCDE{random.randint(1000, 9999)}P"
    if "vpa" in col or "upi_id" in col:
        return f"user{random.randint(100, 999)}@okbank"
    if "customer_key" in col or "customer_id" in col or "cust_key" in col:
        return random.choice(entity_pool.get("customers", [f"CUST_{random.randint(1000, 9999)}"]))
    if "account_key" in col or "account_id" in col or "acc_key" in col:
        return random.choice(entity_pool.get("accounts", [f"ACC_{random.randint(10000, 99999)}"]))
    if "card_key" in col:
        return random.choice(entity_pool.get("cards", [f"CARD_{random.randint(1000, 9999)}"]))
    if "merchant_key" in col or "merchant_id" in col:
        return random.choice(entity_pool.get("merchants", [f"MCH_{random.randint(100, 999)}"]))
    if "branch_key" in col or "branch_code" in col or "branch_id" in col:
        return random.choice(entity_pool.get("branches", ["BR001", "BR002", "BR003"]))
    if "channel_key" in col or "channel" in col:
        return random.choice(CHANNELS)
    if "gl_code" in col or "gl_account" in col or "gl_key" in col:
        return f"GL_{random.randint(1000, 4999)}"
    if "key" in col or "id" in col:
        return f"{table_name[:4]}_{random.randint(1000, 9999)}"

    # Geographic / Demographics
    if "city" in col:
        return random.choice(INDIAN_CITIES)[0]
    if "state" in col:
        return random.choice(INDIAN_CITIES)[1]
    if "pincode" in col:
        return random.choice(INDIAN_CITIES)[2]
    if "gender" in col:
        return random.choice(["M", "F"])
    if "segment" in col:
        return random.choice(["RETAIL", "HNI", "SME", "CORPORATE", "PRIORITY"])
    if "currency" in col:
        return "INR"

    # Status & Flags
    if "status" in col:
        return random.choice(["ACTIVE", "SETTLED", "APPROVED", "COMPLETED", "VERIFIED", "CURRENT"])
    if any(k in col for k in ("flag", "is_current", "enabled", "str_flag", "ctr_flag")):
        return random.choice([1, 0])
    if "risk" in col or "grade" in col:
        return random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"])
    if "category" in col or "variant" in col or "type" in col:
        return random.choice(["STANDARD", "PLATINUM", "GOLD", "SIGNATURE", "INFINITE"])

    return f"VAL_{col[:8].upper()}_{random.randint(10, 99)}"


def generate_star_schema_payload(
    project_key: str,
    star_schema_def: Dict[str, Any],
    rows_per_dim: int = 15,
    rows_per_fact: int = 35
) -> Dict[str, Any]:
    """
    Generates populated table dictionaries for all DIMS and FACTS of a project.
    Returns:
      {
        "dims": { "DIM_NAME": [ {col: val, ...}, ... ], ... },
        "facts": { "FACT_NAME": [ {col: val, ...}, ... ], ... },
        "total_tables": int,
        "total_records": int
      }
    """
    today = datetime.date.today().strftime("%Y-%m-%d")
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Shared entity pool for referential coherence
    entity_pool = {
        "customers": [f"CUST_{1000 + i}" for i in range(rows_per_dim)],
        "accounts": [f"ACC_{50000 + i}" for i in range(rows_per_dim)],
        "cards": [f"CARD_{8000 + i}" for i in range(rows_per_dim)],
        "merchants": [f"MCH_{100 + i}" for i in range(10)],
        "branches": ["BR001", "BR002", "BR003", "BR004"],
    }

    dim_data = {}
    fact_data = {}
    total_records = 0

    # 1. Generate Dimension Records
    dims_cfg = star_schema_def.get("dims", {})
    for dim_name, cols in dims_cfg.items():
        records = []
        for _ in range(rows_per_dim):
            row = {}
            for col in cols:
                row[col] = _generate_column_value(col, dim_name, today, yesterday, now_str, entity_pool)
            records.append(row)
        dim_data[dim_name] = records
        total_records += len(records)

    # 2. Generate Fact Records
    facts_cfg = star_schema_def.get("facts", {})
    for fact_name, cols in facts_cfg.items():
        records = []
        for _ in range(rows_per_fact):
            row = {}
            for col in cols:
                row[col] = _generate_column_value(col, fact_name, today, yesterday, now_str, entity_pool)
            records.append(row)
        fact_data[fact_name] = records
        total_records += len(records)

    return {
        "project": project_key,
        "dims": dim_data,
        "facts": fact_data,
        "total_dim_tables": len(dim_data),
        "total_fact_tables": len(fact_data),
        "total_tables": len(dim_data) + len(fact_data),
        "total_records": total_records,
        "generation_timestamp": now_str
    }
