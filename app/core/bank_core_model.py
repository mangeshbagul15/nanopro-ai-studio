"""Bank-style source model for the NanoPro lakehouse.

The production bank runs Finacle on Oracle (100+ 3NF tables), GoldenGate/DMS
CDC, immutable raw delta batches, L0 raw history, L1 3NF merge/SCD2, L2 star
schema and RBI/FIU report formats.

NanoPro mirrors the same *structure* on free-tier services: BigQuery holds the
CBS snapshots plus a CDC event stream, partner/switch feeds arrive over SFTP,
and Snowflake builds the layers.  Nothing here needs Oracle or a credit-card
source system; debit-card and UPI data is enough for the card/switch reports.

This module is pure metadata: it declares every table, column, primary key,
foreign key, SCD flag and ingestion lane.  The seeder and the layer builder both
read it, so the source and the warehouse can never drift apart.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

BASE_SCHEMA = "nanopro_cbs_bronze"
CORE_SCHEMA = "nanopro_bank_core"
REF_SCHEMA = "nanopro_bank_ref"
CDC_SCHEMA = "nanopro_bank_cdc"
ROWS_PER_TABLE = 100

# Existing CBS snapshots: table -> business key.  The seeder reads the real key
# values from these tables so every new child row joins back to real accounts.
BASE_TABLES: Dict[str, str] = {
    "CMG": "CUST_ID",
    "GAM": "ACID",
    "HTD": "TRAN_ID",
    "SOL": "SOL_ID",
    "SWIFT_MSG": "SWIFT_ID",
    "TAM_LAM": "CONTRACT_ID",
    "UBO": "UBO_ID",
    "VCT": "VCT_ID",
}

CDC_TABLE = "CDC_EVENTS"
CDC_COLUMNS: List[Tuple[str, str]] = [
    ("EVENT_ID", "STRING"),
    ("TABLE_NAME", "STRING"),
    ("OP", "STRING"),
    ("COMMIT_SCN", "INT64"),
    ("COMMIT_TS", "TIMESTAMP"),
    ("PK_JSON", "STRING"),
    ("ROW_JSON", "STRING"),
    ("BATCH_ID", "STRING"),
]


def _spec(table: str, kind: str, columns: List[Tuple[str, str]], pk: str,
          scd: bool = False, fks: Optional[Dict[str, Tuple[str, str]]] = None,
          schema: str = CORE_SCHEMA, source: str = "bigquery",
          partner: str = "") -> Dict[str, Any]:
    return {
        "table": table,
        "kind": kind,
        "schema": schema,
        "source": source,
        "partner": partner,
        "pk": [pk],
        "scd": scd,
        "columns": columns,
        "fks": fks or {},
    }


# ---------------------------------------------------------------------------
# CBS extensions (1:1 with the existing snapshots; nullable child tables keep
# the base CBS data untouched while adding the bank-model attributes)
# ---------------------------------------------------------------------------
EXTENSION_TABLES: List[Dict[str, Any]] = [
    _spec("CMG_EXT", "dim", [
        ("CUST_ID", "STRING"), ("PAN_MASKED", "STRING"), ("AADHAAR_TOKEN", "STRING"),
        ("DOB", "DATE"), ("GENDER", "STRING"), ("NATIONALITY", "STRING"),
        ("OCCUPATION_CODE", "STRING"), ("MOBILE_MASKED", "STRING"), ("EMAIL_MASKED", "STRING"),
        ("ADDRESS_LINE", "STRING"), ("PIN_CODE", "STRING"), ("CUSTOMER_SINCE", "DATE"),
        ("RISK_SCORE", "INT64"), ("RISK_REVIEW_DATE", "DATE"), ("SOURCE_OF_FUNDS", "STRING"),
        ("TIN", "STRING"), ("TAX_RESIDENCY", "STRING"), ("FATCA_STATUS", "STRING"),
        ("CRS_STATUS", "STRING"), ("US_PERSON_FLAG", "BOOL"),
        ("PEP_CATEGORY", "STRING"), ("PEP_SOURCE", "STRING"), ("ENTITY_TYPE", "STRING"),
        ("INCORPORATION_DATE", "DATE"), ("IS_ACTIVE_ENTITY", "BOOL"),
        ("LAST_FILING_DATE", "DATE"), ("GST_NO", "STRING"),
    ], "CUST_ID", scd=True, fks={"CUST_ID": ("CMG", "CUST_ID")}),
    _spec("GAM_EXT", "dim", [
        ("ACID", "STRING"), ("PRODUCT_CODE", "STRING"), ("MATURITY_DATE", "DATE"),
        ("INTEREST_RATE", "FLOAT64"), ("REPRICING_FREQ", "STRING"),
        ("LAST_CREDIT_DATE", "DATE"), ("LAST_DEBIT_DATE", "DATE"),
        ("DORMANT_FLAG", "BOOL"), ("ONBOARDING_CHANNEL", "STRING"),
        ("DIGITAL_SIGN_FLAG", "BOOL"), ("STAFF_FLAG", "BOOL"), ("HOLD_FLAG", "BOOL"),
        ("OPENING_DATE", "DATE"), ("ACCT_CLOSE_DATE", "DATE"),
    ], "ACID", scd=True, fks={"ACID": ("GAM", "ACID")}),
    _spec("HTD_EXT", "fact", [
        ("TRAN_ID", "STRING"), ("DR_CR_FLAG", "STRING"), ("TRAN_MODE", "STRING"),
        ("INSTRUMENT_NO", "STRING"), ("COUNTERPARTY_ACCT", "STRING"),
        ("COUNTERPARTY_NAME", "STRING"), ("COUNTERPARTY_BANK", "STRING"),
        ("COUNTERPARTY_IFSC", "STRING"), ("COUNTERPARTY_COUNTRY", "STRING"),
        ("TXN_CITY", "STRING"), ("PURPOSE_CODE", "STRING"), ("NARRATION", "STRING"),
        ("ORIGINATOR_CUST_ID", "STRING"), ("BENEFICIARY_CUST_ID", "STRING"),
        ("DEVICE_ID", "STRING"), ("IP_HASH", "STRING"),
        ("DEPOSITOR_CUST_ID", "STRING"), ("STRUCTURING_FLAG", "BOOL"),
        ("RAPID_MOVEMENT_FLAG", "BOOL"),
    ], "TRAN_ID", fks={"TRAN_ID": ("HTD", "TRAN_ID"), "ORIGINATOR_CUST_ID": ("CMG", "CUST_ID"),
                       "DEPOSITOR_CUST_ID": ("CMG", "CUST_ID")}),
    _spec("TAM_LAM_EXT", "fact", [
        ("CONTRACT_ID", "STRING"), ("BORROWER_ID", "STRING"), ("SANCTIONED_AMT", "NUMERIC(18,2)"),
        ("SANCTION_DATE", "DATE"), ("FUND_BASED_FLAG", "BOOL"), ("FACILITY_TYPE", "STRING"),
        ("EXPOSURE_CATEGORY", "STRING"), ("PROVISION_AMT", "NUMERIC(18,2)"),
        ("RISK_WEIGHT", "FLOAT64"), ("SECTOR_CODE", "STRING"), ("INDUSTRY_CODE", "STRING"),
        ("MSME_CLASS", "STRING"), ("PSL_CODE", "STRING"), ("MATURITY_DATE", "DATE"),
        ("REPRICING_DATE", "DATE"), ("NEXT_REPAYMENT_DATE", "DATE"),
        ("NPA_DATE", "DATE"), ("SMA_DATE", "DATE"), ("RESTRUCTURE_TYPE", "STRING"),
        ("WRITE_OFF_AMT", "NUMERIC(18,2)"), ("WRITE_OFF_DATE", "DATE"),
        ("BORROWER_PAN_MASKED", "STRING"), ("GROUP_ID", "STRING"),
        ("MODIFIED_DURATION", "FLOAT64"),
        ("FORECLOSURE_DATE", "DATE"), ("FORECLOSURE_AMT", "NUMERIC(18,2)"),
        ("PREPAYMENT_PENALTY", "NUMERIC(18,2)"),
    ], "CONTRACT_ID", fks={
        "CONTRACT_ID": ("TAM_LAM", "CONTRACT_ID"), "BORROWER_ID": ("BORROWER_ENTITY", "BORROWER_ID"),
        "INDUSTRY_CODE": ("INDUSTRY_SECTOR_MASTER", "INDUSTRY_CODE"),
        "PSL_CODE": ("PSL_MASTER", "PSL_CODE"),
    }),
    _spec("SWIFT_MSG_EXT", "fact", [
        ("SWIFT_ID", "STRING"), ("REMITTER_NAME", "STRING"), ("REMITTER_COUNTRY", "STRING"),
        ("REMITTER_ADDRESS", "STRING"), ("BENEFICIARY_NAME", "STRING"),
        ("BENEFICIARY_ADDRESS", "STRING"), ("PURPOSE_CODE", "STRING"),
        ("AD_BANK_CODE", "STRING"),
    ], "SWIFT_ID", fks={"SWIFT_ID": ("SWIFT_MSG", "SWIFT_ID")}),
    _spec("VCT_EXT", "fact", [
        ("VCT_ID", "STRING"), ("CUST_ID", "STRING"), ("ACCOUNT_ID", "STRING"),
        ("TRAN_MODE", "STRING"), ("CHANNEL", "STRING"), ("CUST_OCCUPATION", "STRING"),
    ], "VCT_ID", fks={"VCT_ID": ("VCT", "VCT_ID"), "CUST_ID": ("CMG", "CUST_ID")}),
    _spec("UBO_EXT", "dim", [
        ("UBO_ID", "STRING"), ("UBO_NAME", "STRING"), ("UBO_TYPE", "STRING"),
        ("UBO_COUNTRY", "STRING"), ("ID_MASKED", "STRING"), ("OWNERSHIP_TYPE", "STRING"),
    ], "UBO_ID", scd=True, fks={"UBO_ID": ("UBO", "UBO_ID")}),
    _spec("SOL_EXT", "dim", [
        ("SOL_ID", "STRING"), ("CONTROL_OFFICE", "STRING"), ("BRANCH_TYPE", "STRING"),
        ("PSL_BRANCH_FLAG", "BOOL"), ("CURRENCY_CHEST_TYPE", "STRING"),
        ("WORKING_DAYS", "INT64"),
    ], "SOL_ID", scd=True, fks={"SOL_ID": ("SOL", "SOL_ID")}),
]


# ---------------------------------------------------------------------------
# Customer / KYC child tables
# ---------------------------------------------------------------------------
KYC_TABLES: List[Dict[str, Any]] = [
    _spec("KYC_DOCUMENT", "dim", [
        ("DOC_ID", "STRING"), ("CUST_ID", "STRING"), ("DOC_TYPE", "STRING"),
        ("DOC_NUMBER_MASKED", "STRING"), ("ISSUE_DATE", "DATE"), ("EXPIRY_DATE", "DATE"),
        ("VERIFIED_BY", "STRING"), ("VERIFIED_DATE", "DATE"),
        ("VERIFICATION_MODE", "STRING"), ("STATUS", "STRING"),
    ], "DOC_ID", fks={"CUST_ID": ("CMG", "CUST_ID")}),
    _spec("CUSTOMER_CONTACT", "dim", [
        ("CONTACT_ID", "STRING"), ("CUST_ID", "STRING"), ("CONTACT_TYPE", "STRING"),
        ("VALUE_MASKED", "STRING"), ("IS_PRIMARY", "BOOL"), ("UPDATED_AT", "TIMESTAMP"),
    ], "CONTACT_ID", fks={"CUST_ID": ("CMG", "CUST_ID")}),
    _spec("CUSTOMER_RELATIONSHIP", "dim", [
        ("REL_ID", "STRING"), ("CUST_ID", "STRING"), ("RELATED_CUST_ID", "STRING"),
        ("REL_TYPE", "STRING"), ("SINCE_DATE", "DATE"),
    ], "REL_ID", fks={"CUST_ID": ("CMG", "CUST_ID"), "RELATED_CUST_ID": ("CMG", "CUST_ID")}),
]


# ---------------------------------------------------------------------------
# Credit / RBI CIMS-ADF subject area
# ---------------------------------------------------------------------------
CREDIT_TABLES: List[Dict[str, Any]] = [
    _spec("BORROWER_ENTITY", "dim", [
        ("BORROWER_ID", "STRING"), ("CUST_ID", "STRING"), ("CONSTITUTION", "STRING"),
        ("PAN_MASKED", "STRING"), ("UDYAM_NO", "STRING"), ("MSME_CLASS", "STRING"),
        ("SECTOR_CODE", "STRING"), ("INDUSTRY_CODE", "STRING"), ("GROUP_ID", "STRING"),
        ("GROUP_NAME", "STRING"), ("RATING_CODE", "STRING"), ("RATING_AGENCY", "STRING"),
        ("RATING_DATE", "DATE"), ("PSL_CODE", "STRING"), ("REGISTERED_STATE", "STRING"),
    ], "BORROWER_ID", scd=True, fks={
        "CUST_ID": ("CMG", "CUST_ID"),
        "INDUSTRY_CODE": ("INDUSTRY_SECTOR_MASTER", "INDUSTRY_CODE"),
        "PSL_CODE": ("PSL_MASTER", "PSL_CODE"),
        "RATING_CODE": ("RATING_MASTER", "RATING_CODE"),
    }),
    _spec("CREDIT_FACILITY", "dim", [
        ("FACILITY_ID", "STRING"), ("CONTRACT_ID", "STRING"), ("BORROWER_ID", "STRING"),
        ("FACILITY_TYPE", "STRING"), ("FUND_BASED_FLAG", "BOOL"),
        ("SANCTIONED_AMT", "NUMERIC(18,2)"), ("SANCTION_DATE", "DATE"),
        ("LIMIT_EXPIRY_DATE", "DATE"), ("INTEREST_TYPE", "STRING"),
        ("INTEREST_RATE", "FLOAT64"), ("REPAYMENT_FREQ", "STRING"),
        ("MORATORIUM_END_DATE", "DATE"),
        ("DRAWN_AMT", "NUMERIC(18,2)"), ("GUARANTEE_COVER", "BOOL"),
        ("NPA_FLAG", "BOOL"),
    ], "FACILITY_ID", fks={
        "CONTRACT_ID": ("TAM_LAM", "CONTRACT_ID"),
        "BORROWER_ID": ("BORROWER_ENTITY", "BORROWER_ID"),
    }),
    _spec("COLLATERAL_REGISTER", "dim", [
        ("COLLATERAL_ID", "STRING"), ("CONTRACT_ID", "STRING"), ("SECURITY_TYPE", "STRING"),
        ("DESCRIPTION", "STRING"), ("VALUE", "NUMERIC(18,2)"), ("VALUATION_DATE", "DATE"),
        ("CHARGE_TYPE", "STRING"), ("CHARGE_HOLDER", "STRING"),
    ], "COLLATERAL_ID", fks={"CONTRACT_ID": ("TAM_LAM", "CONTRACT_ID")}),
    _spec("GUARANTOR_REGISTER", "dim", [
        ("GUARANTOR_ID", "STRING"), ("CONTRACT_ID", "STRING"), ("GUARANTOR_NAME", "STRING"),
        ("GUARANTOR_CUST_ID", "STRING"), ("PAN_MASKED", "STRING"),
        ("EXPOSURE_AMT", "NUMERIC(18,2)"), ("GUARANTEE_TYPE", "STRING"),
    ], "GUARANTOR_ID", fks={
        "CONTRACT_ID": ("TAM_LAM", "CONTRACT_ID"),
        "GUARANTOR_CUST_ID": ("CMG", "CUST_ID"),
    }),
    _spec("RESTRUCTURE_HISTORY", "fact", [
        ("RESTRUCTURE_ID", "STRING"), ("CONTRACT_ID", "STRING"),
        ("RESTRUCTURE_DATE", "DATE"), ("RESTRUCTURE_TYPE", "STRING"),
        ("RELIEF_TYPE", "STRING"), ("RESCHEDULED_AMT", "NUMERIC(18,2)"),
        ("MORATORIUM_DAYS", "INT64"),
    ], "RESTRUCTURE_ID", fks={"CONTRACT_ID": ("TAM_LAM", "CONTRACT_ID")}),
]


# ---------------------------------------------------------------------------
# ALM / treasury subject area
# ---------------------------------------------------------------------------
ALM_TABLES: List[Dict[str, Any]] = [
    _spec("DEPOSIT_MASTER", "dim", [
        ("DEPOSIT_ID", "STRING"), ("ACID", "STRING"), ("CUST_ID", "STRING"),
        ("PRODUCT_CODE", "STRING"), ("AMOUNT", "NUMERIC(18,2)"),
        ("INTEREST_RATE", "FLOAT64"), ("START_DATE", "DATE"), ("MATURITY_DATE", "DATE"),
        ("REPRICING_FREQ", "STRING"), ("PREMATURE_WD_FLAG", "BOOL"),
        ("AUTO_RENEW_FLAG", "BOOL"), ("BUCKET", "STRING"),
        ("RESIDUAL_MATURITY_DAYS", "INT64"), ("RATE_TYPE", "STRING"),
        ("BENCHMARK", "STRING"), ("SPREAD_BPS", "FLOAT64"),
        ("INTEREST_PAID", "NUMERIC(18,2)"), ("INSURED_FLAG", "BOOL"),
        ("CUSTOMER_SEGMENT", "STRING"), ("AS_OF_DATE", "DATE"),
        ("NOMINAL_RATE", "FLOAT64"), ("EFFECTIVE_RATE", "FLOAT64"),
    ], "DEPOSIT_ID", fks={
        "ACID": ("GAM", "ACID"), "CUST_ID": ("CMG", "CUST_ID"),
        "PRODUCT_CODE": ("PRODUCT_MASTER", "PRODUCT_CODE"),
    }),
    _spec("BORROWING_MASTER", "dim", [
        ("BORROWING_ID", "STRING"), ("INSTRUMENT_TYPE", "STRING"),
        ("COUNTERPARTY", "STRING"), ("AMOUNT", "NUMERIC(18,2)"),
        ("INTEREST_RATE", "FLOAT64"), ("START_DATE", "DATE"), ("MATURITY_DATE", "DATE"),
        ("REPRICING_DATE", "DATE"), ("CALL_PUT_FLAG", "BOOL"),
        ("RATE_TYPE", "STRING"), ("BENCHMARK", "STRING"),
        ("RESIDUAL_MATURITY_DAYS", "INT64"), ("SPREAD_BPS", "FLOAT64"),
    ], "BORROWING_ID"),
    _spec("INVESTMENT_PORTFOLIO", "dim", [
        ("INVEST_ID", "STRING"), ("ISIN", "STRING"), ("SECURITY_TYPE", "STRING"),
        ("FACE_VALUE", "NUMERIC(18,2)"), ("BOOK_VALUE", "NUMERIC(18,2)"),
        ("MARKET_VALUE", "NUMERIC(18,2)"), ("COUPON", "FLOAT64"),
        ("MATURITY_DATE", "DATE"), ("RATING", "STRING"), ("HTM_AFS_HFT", "STRING"),
        ("YIELD_PCT", "FLOAT64"), ("ACCRUED_INT", "NUMERIC(18,2)"),
        ("REPRICING_DATE", "DATE"), ("MODIFIED_DURATION", "FLOAT64"),
        ("RESIDUAL_MATURITY_DAYS", "INT64"), ("RATE_TYPE", "STRING"),
        ("HQLA_CLASS", "STRING"),
    ], "INVEST_ID"),
    _spec("TREASURY_DEAL", "fact", [
        ("DEAL_ID", "STRING"), ("DEAL_DATE", "DATE"), ("DEAL_TYPE", "STRING"),
        ("BUY_SELL", "STRING"), ("CCY_PAIR", "STRING"), ("AMOUNT", "NUMERIC(18,2)"),
        ("RATE", "FLOAT64"), ("VALUE_DATE", "DATE"), ("MATURITY_DATE", "DATE"),
        ("COUNTERPARTY", "STRING"), ("SETTLEMENT_STATUS", "STRING"),
    ], "DEAL_ID"),
    _spec("FX_POSITION", "fact", [
        ("POSITION_ID", "STRING"), ("AS_OF_DATE", "DATE"), ("CCY", "STRING"),
        ("OPEN_POSITION", "NUMERIC(18,2)"), ("NOP_INR", "NUMERIC(18,2)"),
        ("LIMIT_AMT", "NUMERIC(18,2)"), ("UTILISATION_PCT", "FLOAT64"),
    ], "POSITION_ID"),
    _spec("GL_MASTER", "dim", [
        ("GL_CODE", "STRING"), ("GL_NAME", "STRING"), ("GL_TYPE", "STRING"),
        ("CURRENCY", "STRING"), ("SOL_ID", "STRING"),
    ], "GL_CODE", scd=True, fks={"SOL_ID": ("SOL", "SOL_ID")}),
    _spec("GL_BALANCE_DAILY", "fact", [
        ("BALANCE_ID", "STRING"), ("AS_OF_DATE", "DATE"), ("GL_CODE", "STRING"),
        ("SOL_ID", "STRING"), ("CCY", "STRING"), ("OPENING_BAL", "NUMERIC(18,2)"),
        ("DEBIT_AMT", "NUMERIC(18,2)"), ("CREDIT_AMT", "NUMERIC(18,2)"),
        ("CLOSING_BAL", "NUMERIC(18,2)"),
    ], "BALANCE_ID", fks={
        "GL_CODE": ("GL_MASTER", "GL_CODE"), "SOL_ID": ("SOL", "SOL_ID"),
    }),
    _spec("CRR_SLR_POSITION", "fact", [
        ("POSITION_ID", "STRING"), ("AS_OF_DATE", "DATE"), ("NDTL", "NUMERIC(18,2)"),
        ("CRR_REQUIRED", "NUMERIC(18,2)"), ("CRR_HELD", "NUMERIC(18,2)"),
        ("SLR_REQUIRED", "NUMERIC(18,2)"), ("SLR_HELD", "NUMERIC(18,2)"),
        ("SLR_SECURITIES_VALUE", "NUMERIC(18,2)"),
    ], "POSITION_ID"),
]


# ---------------------------------------------------------------------------
# Cards (debit only) + trade finance
# ---------------------------------------------------------------------------
CARD_TABLES: List[Dict[str, Any]] = [
    _spec("DEBIT_CARD_MASTER", "dim", [
        ("CARD_ID", "STRING"), ("ACID", "STRING"), ("CUST_ID", "STRING"),
        ("CARD_TYPE", "STRING"), ("NETWORK", "STRING"), ("BIN", "STRING"),
        ("MASKED_PAN", "STRING"), ("ISSUE_DATE", "DATE"), ("EXPIRY_DATE", "DATE"),
        ("STATUS", "STRING"), ("DAILY_LIMIT", "NUMERIC(18,2)"),
        ("CONTACTLESS_FLAG", "BOOL"),
    ], "CARD_ID", scd=True, fks={"ACID": ("GAM", "ACID"), "CUST_ID": ("CMG", "CUST_ID")}),
    _spec("CREDIT_CARD_MASTER", "dim", [
        ("CARD_ID", "STRING"), ("CUST_ID", "STRING"), ("ACID", "STRING"),
        ("CARD_TYPE", "STRING"), ("NETWORK", "STRING"), ("BIN", "STRING"),
        ("MASKED_PAN", "STRING"), ("CREDIT_LIMIT", "NUMERIC(18,2)"),
        ("ISSUE_DATE", "DATE"), ("EXPIRY_DATE", "DATE"), ("STATUS", "STRING"),
        ("INTEREST_RATE", "FLOAT64"), ("CONTACTLESS_FLAG", "BOOL"),
    ], "CARD_ID", scd=True, source="sftp", partner="CARDNET",
        fks={"ACID": ("GAM", "ACID"), "CUST_ID": ("CMG", "CUST_ID")}),
    _spec("CREDIT_CARD_TRANSACTION", "fact", [
        ("CARD_TXN_ID", "STRING"), ("CARD_ID", "STRING"), ("TXN_DATE", "DATE"),
        ("MERCHANT_NAME", "STRING"), ("MCC", "STRING"), ("AMOUNT", "NUMERIC(18,2)"),
        ("INR_AMOUNT", "NUMERIC(18,2)"), ("CCY", "STRING"), ("AUTH_CODE", "STRING"),
        ("RESPONSE_CODE", "STRING"), ("CHANNEL", "STRING"), ("SETTLEMENT_DATE", "DATE"),
        ("DISPUTE_FLAG", "BOOL"), ("FOREIGN_FLAG", "BOOL"), ("COUNTRY", "STRING"),
    ], "CARD_TXN_ID", source="sftp", partner="CARDNET",
        fks={"CARD_ID": ("CREDIT_CARD_MASTER", "CARD_ID"), "MCC": ("MCC_MASTER", "MCC")}),
    _spec("CREDIT_CARD_STATEMENT", "fact", [
        ("STATEMENT_ID", "STRING"), ("CARD_ID", "STRING"), ("STATEMENT_DATE", "DATE"),
        ("DUE_DATE", "DATE"), ("TOTAL_DUE", "NUMERIC(18,2)"), ("MIN_DUE", "NUMERIC(18,2)"),
        ("PAYMENT_RECEIVED", "NUMERIC(18,2)"), ("DAYS_PAST_DUE", "INT64"),
        ("BUCKET", "STRING"), ("WRITTEN_OFF_FLAG", "BOOL"),
    ], "STATEMENT_ID", source="sftp", partner="CARDNET",
        fks={"CARD_ID": ("CREDIT_CARD_MASTER", "CARD_ID")}),
]

# ---------------------------------------------------------------------------
# Cash / currency-chest feeds (counterfeit detection, walk-in cash capture)
# ---------------------------------------------------------------------------
CASH_TABLES: List[Dict[str, Any]] = [
    _spec("COUNTERFEIT_INCIDENT", "fact", [
        ("INCIDENT_ID", "STRING"), ("SOL_ID", "STRING"), ("TXN_DATE", "DATE"),
        ("CI_AMOUNT", "NUMERIC(18,2)"), ("FAKE_NOTE_COUNT", "INT64"),
        ("DENOMINATION", "STRING"), ("SOURCE_CHANNEL", "STRING"),
        ("RECOVERED_FLAG", "BOOL"), ("REPORTED_TO_POLICE", "BOOL"), ("STATUS", "STRING"),
    ], "INCIDENT_ID", source="sftp", partner="CASH",
        fks={"SOL_ID": ("SOL", "SOL_ID")}),
    _spec("WALK_IN_CASH_TXN", "fact", [
        ("TXN_ID", "STRING"), ("SOL_ID", "STRING"), ("CUST_ID", "STRING"),
        ("TXN_DATE", "DATE"), ("TXN_TYPE", "STRING"), ("AMOUNT", "NUMERIC(18,2)"),
        ("PAN_CAPTURED", "BOOL"), ("FORM60", "BOOL"), ("DEPOSITOR_NAME", "STRING"),
        ("STATUS", "STRING"),
    ], "TXN_ID", source="sftp", partner="CASH",
        fks={"SOL_ID": ("SOL", "SOL_ID"), "CUST_ID": ("CMG", "CUST_ID")}),
]

TRADE_TABLES: List[Dict[str, Any]] = [
    _spec("TRADE_DOCUMENT", "fact", [
        ("DOC_ID", "STRING"), ("DOC_TYPE", "STRING"), ("CUST_ID", "STRING"),
        ("COUNTERPARTY_COUNTRY", "STRING"), ("AMOUNT", "NUMERIC(18,2)"),
        ("CCY", "STRING"), ("INR_AMOUNT", "NUMERIC(18,2)"), ("ISSUE_DATE", "DATE"),
        ("EXPIRY_DATE", "DATE"), ("STATUS", "STRING"), ("PURPOSE_CODE", "STRING"),
        ("UNIT_PRICE", "NUMERIC(18,2)"), ("MARKET_PRICE", "NUMERIC(18,2)"),
        ("HS_CODE", "STRING"), ("DISCREPANCY_FLAG", "BOOL"),
    ], "DOC_ID", fks={"CUST_ID": ("CMG", "CUST_ID")}),
    _spec("NOSTRO_ACCOUNT", "fact", [
        ("NOSTRO_ID", "STRING"), ("CCY", "STRING"), ("BANK_BIC", "STRING"),
        ("BALANCE", "NUMERIC(18,2)"), ("AS_OF_DATE", "DATE"),
    ], "NOSTRO_ID"),
]


# ---------------------------------------------------------------------------
# AML / FIU compliance tables (NanoPro-owned registers)
# ---------------------------------------------------------------------------
AML_TABLES: List[Dict[str, Any]] = [
    _spec("AML_ALERT", "fact", [
        ("ALERT_ID", "STRING"), ("CUST_ID", "STRING"), ("ACCOUNT_ID", "STRING"),
        ("TXN_ID", "STRING"), ("RULE_CODE", "STRING"), ("RULE_NAME", "STRING"),
        ("ALERT_DATE", "DATE"), ("SEVERITY", "STRING"), ("SCORE", "INT64"),
        ("STATUS", "STRING"), ("ASSIGNED_TO", "STRING"), ("CLOSED_DATE", "DATE"),
        ("DISPOSITION", "STRING"),
    ], "ALERT_ID", fks={
        "CUST_ID": ("CMG", "CUST_ID"), "ACCOUNT_ID": ("GAM", "ACID"),
        "TXN_ID": ("HTD", "TRAN_ID"),
    }),
    _spec("AML_CASE", "fact", [
        ("CASE_ID", "STRING"), ("ALERT_ID", "STRING"), ("CUST_ID", "STRING"),
        ("CASE_TYPE", "STRING"), ("OPENED_DATE", "DATE"), ("CLOSED_DATE", "DATE"),
        ("SAR_FILED_FLAG", "BOOL"), ("STR_ID", "STRING"),
    ], "CASE_ID", fks={"ALERT_ID": ("AML_ALERT", "ALERT_ID"), "CUST_ID": ("CMG", "CUST_ID")}),
    _spec("STR_REGISTER", "fact", [
        ("STR_ID", "STRING"), ("CASE_ID", "STRING"), ("FIU_REF", "STRING"),
        ("FILED_DATE", "DATE"), ("SUSPICION_TYPE", "STRING"),
        ("AMOUNT_INR", "NUMERIC(18,2)"), ("PERIOD_FROM", "DATE"),
        ("PERIOD_TO", "DATE"), ("STATUS", "STRING"),
    ], "STR_ID", fks={"CASE_ID": ("AML_CASE", "CASE_ID")}),
    _spec("REGULATORY_FILING", "fact", [
        ("FILING_ID", "STRING"), ("REPORT_TYPE", "STRING"), ("PERIOD", "STRING"),
        ("FILED_AT", "TIMESTAMP"), ("ACK_NO", "STRING"), ("STATUS", "STRING"),
        ("RECORD_COUNT", "INT64"), ("FORMAT_VERSION", "STRING"),
    ], "FILING_ID"),
    _spec("NPO_REGISTRY", "dim", [
        ("NPO_ID", "STRING"), ("NPO_NAME", "STRING"), ("REG_NO", "STRING"),
        ("DONOR_COUNTRY", "STRING"), ("PURPOSE", "STRING"), ("ACCOUNT_ID", "STRING"),
        ("RISK_BAND", "STRING"),
    ], "NPO_ID", scd=True, fks={"ACCOUNT_ID": ("GAM", "ACID")}),
    _spec("WATCHLIST_ENTRY", "dim", [
        ("ENTRY_ID", "STRING"), ("ENTITY_NAME", "STRING"), ("ALIAS", "STRING"),
        ("ENTITY_TYPE", "STRING"), ("LIST_SOURCE", "STRING"), ("COUNTRY", "STRING"),
        ("DOB", "DATE"), ("ID_MASKED", "STRING"), ("LISTED_DATE", "DATE"),
        ("RISK_LEVEL", "STRING"), ("LIST_VERSION", "STRING"), ("EFFECTIVE_DATE", "DATE"),
    ], "ENTRY_ID", scd=True, schema=REF_SCHEMA),
    _spec("SCREENING_RESULT", "fact", [
        ("SCREEN_ID", "STRING"), ("SUBJECT_TYPE", "STRING"), ("SUBJECT_ID", "STRING"),
        ("ENTRY_ID", "STRING"), ("MATCH_SCORE", "INT64"), ("STATUS", "STRING"),
        ("SCREENED_AT", "TIMESTAMP"), ("REVIEWED_BY", "STRING"),
    ], "SCREEN_ID", fks={"ENTRY_ID": ("WATCHLIST_ENTRY", "ENTRY_ID")}),
]


# ---------------------------------------------------------------------------
# Reference masters (small, seeded; shared by every subject area)
# ---------------------------------------------------------------------------
REF_TABLES: List[Dict[str, Any]] = [
    _spec("GL_CHART", "ref", [
        ("GL_CODE", "STRING"), ("GL_NAME", "STRING"), ("GL_TYPE", "STRING"),
        ("PARENT_GL", "STRING"), ("BALANCE_SHEET_FLAG", "BOOL"),
    ], "GL_CODE", schema=REF_SCHEMA),
    _spec("PRODUCT_MASTER", "ref", [
        ("PRODUCT_CODE", "STRING"), ("PRODUCT_NAME", "STRING"), ("ACCT_TYPE", "STRING"),
        ("GL_CODE", "STRING"), ("INTEREST_RULES", "STRING"),
        ("PSL_ELIGIBLE_FLAG", "BOOL"), ("ACTIVE_FLAG", "BOOL"),
    ], "PRODUCT_CODE", schema=REF_SCHEMA, fks={"GL_CODE": ("GL_CHART", "GL_CODE")}),
    _spec("MCC_MASTER", "ref", [
        ("MCC", "STRING"), ("DESCRIPTION", "STRING"), ("CATEGORY", "STRING"),
        ("PSL_RELEVANT_FLAG", "BOOL"),
    ], "MCC", schema=REF_SCHEMA),
    _spec("INDUSTRY_SECTOR_MASTER", "ref", [
        ("INDUSTRY_CODE", "STRING"), ("INDUSTRY_NAME", "STRING"), ("SECTOR", "STRING"),
        ("SUB_SECTOR", "STRING"), ("PSL_GROUP", "STRING"),
    ], "INDUSTRY_CODE", schema=REF_SCHEMA),
    _spec("PSL_MASTER", "ref", [
        ("PSL_CODE", "STRING"), ("PSL_CATEGORY", "STRING"), ("SUB_CATEGORY", "STRING"),
        ("LIMIT_AMT", "NUMERIC(18,2)"), ("WEIGHT_PCT", "FLOAT64"),
    ], "PSL_CODE", schema=REF_SCHEMA),
    _spec("COUNTRY_RISK_MASTER", "ref", [
        ("COUNTRY_CODE", "STRING"), ("COUNTRY_NAME", "STRING"), ("RISK_BAND", "STRING"),
        ("FATF_STATUS", "STRING"),
    ], "COUNTRY_CODE", schema=REF_SCHEMA),
    _spec("CURRENCY_HOLIDAY_MASTER", "ref", [
        ("CAL_ID", "STRING"), ("CAL_TYPE", "STRING"), ("CODE", "STRING"),
        ("DESCRIPTION", "STRING"), ("RATE", "FLOAT64"), ("IS_HOLIDAY", "BOOL"),
        ("BRANCH_ZONE", "STRING"), ("EFFECTIVE_DATE", "DATE"),
    ], "CAL_ID", schema=REF_SCHEMA),
    _spec("RATING_MASTER", "ref", [
        ("RATING_CODE", "STRING"), ("AGENCY", "STRING"), ("RATING", "STRING"),
        ("RISK_WEIGHT", "FLOAT64"), ("BAND", "STRING"),
    ], "RATING_CODE", schema=REF_SCHEMA),
]


# ---------------------------------------------------------------------------
# SFTP partner / switch feeds (no Oracle, no credit-card network)
# ---------------------------------------------------------------------------
SFTP_TABLES: List[Dict[str, Any]] = [
    _spec("UPI_TRANSACTION", "fact", [
        ("UPI_TXN_ID", "STRING"), ("RRN", "STRING"), ("PAYER_VPA", "STRING"),
        ("PAYEE_VPA", "STRING"), ("PAYER_ACID", "STRING"), ("PAYEE_ACID", "STRING"),
        ("AMOUNT", "NUMERIC(18,2)"), ("MCC", "STRING"), ("TXN_TYPE", "STRING"),
        ("STATUS", "STRING"), ("RESPONSE_CODE", "STRING"), ("INITIATION_MODE", "STRING"),
        ("TXN_DATE", "DATE"), ("SETTLEMENT_DATE", "DATE"), ("NPCI_REF", "STRING"),
        ("DISPUTE_FLAG", "BOOL"), ("FRAUD_FLAG", "BOOL"),
        ("SETTLEMENT_AMOUNT", "NUMERIC(18,2)"),
    ], "UPI_TXN_ID", source="sftp", partner="NPCI", fks={
        "PAYER_ACID": ("GAM", "ACID"), "MCC": ("MCC_MASTER", "MCC"),
    }),
    _spec("UPI_MERCHANT", "dim", [
        ("MERCHANT_ID", "STRING"), ("MERCHANT_NAME", "STRING"), ("MCC", "STRING"),
        ("VPA", "STRING"), ("ONBOARDED_DATE", "DATE"), ("STATUS", "STRING"),
        ("RISK_CATEGORY", "STRING"), ("FRAUD_SCORE", "INT64"),
        ("CHARGEBACK_COUNT", "INT64"),
    ], "MERCHANT_ID", scd=True, source="sftp", partner="NPCI",
        fks={"MCC": ("MCC_MASTER", "MCC")}),
    _spec("UPI_DISPUTE", "fact", [
        ("DISPUTE_ID", "STRING"), ("UPI_TXN_ID", "STRING"), ("RAISED_DATE", "DATE"),
        ("REASON_CODE", "STRING"), ("STATUS", "STRING"),
        ("ADJUDICATED_AMT", "NUMERIC(18,2)"), ("SETTLEMENT_IMPACT", "NUMERIC(18,2)"),
        ("CLOSED_DATE", "DATE"),
    ], "DISPUTE_ID", source="sftp", partner="NPCI",
        fks={"UPI_TXN_ID": ("UPI_TRANSACTION", "UPI_TXN_ID")}),
    _spec("UPI_SETTLEMENT", "fact", [
        ("SETTLEMENT_ID", "STRING"), ("SETTLEMENT_DATE", "DATE"), ("NPCI_CYCLE", "STRING"),
        ("CREDITS", "NUMERIC(18,2)"), ("DEBITS", "NUMERIC(18,2)"),
        ("NET_POSITION", "NUMERIC(18,2)"), ("STATUS", "STRING"), ("FILE_REF", "STRING"),
    ], "SETTLEMENT_ID", source="sftp", partner="NPCI"),
    _spec("NEFT_RTGS_BATCH", "fact", [
        ("BATCH_ID", "STRING"), ("BATCH_TYPE", "STRING"), ("DIRECTION", "STRING"),
        ("BATCH_DATE", "DATE"), ("TXN_COUNT", "INT64"), ("TOTAL_AMOUNT", "NUMERIC(18,2)"),
        ("STATUS", "STRING"), ("UTR_REF", "STRING"),
    ], "BATCH_ID", source="sftp", partner="NEFT"),
    _spec("ATM_SWITCH", "fact", [
        ("ATM_TXN_ID", "STRING"), ("ATM_ID", "STRING"), ("SOL_ID", "STRING"),
        ("TXN_DATE", "DATE"), ("TXN_TYPE", "STRING"), ("CARD_ID", "STRING"),
        ("AMOUNT", "NUMERIC(18,2)"), ("STATUS", "STRING"), ("CASH_POSITION", "NUMERIC(18,2)"),
        ("DOWNTIME_MIN", "INT64"),
    ], "ATM_TXN_ID", source="sftp", partner="ATM",
        fks={"SOL_ID": ("SOL", "SOL_ID"), "CARD_ID": ("DEBIT_CARD_MASTER", "CARD_ID")}),
    _spec("DEBIT_CARD_TRANSACTION", "fact", [
        ("CARD_TXN_ID", "STRING"), ("CARD_ID", "STRING"), ("TXN_DATE", "DATE"),
        ("MERCHANT_ID", "STRING"), ("MERCHANT_NAME", "STRING"), ("MCC", "STRING"),
        ("AMOUNT", "NUMERIC(18,2)"), ("INR_AMOUNT", "NUMERIC(18,2)"), ("CCY", "STRING"),
        ("AUTH_CODE", "STRING"), ("RESPONSE_CODE", "STRING"), ("CHANNEL", "STRING"),
        ("SETTLEMENT_DATE", "DATE"), ("DISPUTE_FLAG", "BOOL"), ("FOREIGN_FLAG", "BOOL"),
        ("COUNTRY", "STRING"),
    ], "CARD_TXN_ID", source="sftp", partner="CARDNET",
        fks={"CARD_ID": ("DEBIT_CARD_MASTER", "CARD_ID"),
             "MERCHANT_ID": ("UPI_MERCHANT", "MERCHANT_ID"),
             "MCC": ("MCC_MASTER", "MCC")}),
]


NEW_TABLES: List[Dict[str, Any]] = (
    EXTENSION_TABLES + KYC_TABLES + CREDIT_TABLES + ALM_TABLES +
    CARD_TABLES + CASH_TABLES + TRADE_TABLES + AML_TABLES + REF_TABLES + SFTP_TABLES
)

_TABLE_INDEX: Dict[str, Dict[str, Any]] = {spec["table"]: spec for spec in NEW_TABLES}


def all_tables() -> List[Dict[str, Any]]:
    return list(NEW_TABLES)


def bigquery_tables() -> List[Dict[str, Any]]:
    return [spec for spec in NEW_TABLES if spec["source"] == "bigquery"]


def sftp_tables() -> List[Dict[str, Any]]:
    return [spec for spec in NEW_TABLES if spec["source"] == "sftp"]


def get(table: str) -> Optional[Dict[str, Any]]:
    return _TABLE_INDEX.get(str(table or "").upper())


def columns(table: str) -> List[Tuple[str, str]]:
    spec = get(table) or {}
    return list(spec.get("columns") or [])


def scd_tables() -> List[str]:
    return [spec["table"] for spec in NEW_TABLES if spec.get("scd")]


def summary() -> Dict[str, Any]:
    lanes: Dict[str, int] = {}
    kinds: Dict[str, int] = {}
    for spec in NEW_TABLES:
        lanes[spec["source"]] = lanes.get(spec["source"], 0) + 1
        kinds[spec["kind"]] = kinds.get(spec["kind"], 0) + 1
    return {
        "datasets": {"base": BASE_SCHEMA, "core": CORE_SCHEMA, "ref": REF_SCHEMA, "cdc": CDC_SCHEMA},
        "base_tables": len(BASE_TABLES),
        "new_tables": len(NEW_TABLES),
        "total_source_tables": len(BASE_TABLES) + len(NEW_TABLES),
        "rows_per_table": ROWS_PER_TABLE,
        "lanes": lanes,
        "kinds": kinds,
        "scd_tables": len(scd_tables()),
        "tables": [
            {
                "table": spec["table"], "schema": spec["schema"], "kind": spec["kind"],
                "source": spec["source"], "scd": spec["scd"], "pk": spec["pk"][0],
                "columns": len(spec["columns"]), "fks": len(spec.get("fks") or {}),
            }
            for spec in NEW_TABLES
        ],
    }
