"""Update global_ai_lab_view.py with 8 Banking Projects and Airflow Orchestrator UI."""
import json
import re

path = 'app/ui/global_ai_lab_view.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update fallback static seed catalog in ailabLoadExplorer
old_fallback_pattern = r'(\s+// Fallback static seed catalog\s+AILAB_EXPLORER\.catalog = \[[\s\S]*?\];\s+ailabRenderExplorerTree\(\);)'

new_fallback_block = '''    // Fallback static seed catalog - 8 Core Banking Projects (Snowflake BANK_DB, AWS S3, DuckDB, BigQuery)
    AILAB_EXPLORER.catalog = [
      {
        id: "snowflake",
        name: "Snowflake Enterprise DW (BANK_DB)",
        kind: "snowflake",
        icon: "❄️",
        schemas: [
          {
            name: "L0_STAGING",
            description: "Raw Landing Tier (Append-Only feeds from AWS S3 Bronze & SFTP Inbound)",
            tables: [
              { name: "RAW_AML_ALERTS", rows: 148000, columns: [{ name: "ALERT_ID", type: "VARCHAR(64) PRIMARY KEY" }, { name: "ACCOUNT_NO", type: "VARCHAR(32)" }, { name: "RULE_CODE", type: "VARCHAR(16)" }, { name: "RISK_SCORE", type: "NUMBER(5,2)" }, { name: "ALERT_DATE", type: "TIMESTAMP_NTZ" }] },
              { name: "RAW_ALM_CASHFLOWS", rows: 215000, columns: [{ name: "FLOW_ID", type: "VARCHAR(64) PRIMARY KEY" }, { name: "ACCOUNT_NO", type: "VARCHAR(32)" }, { name: "BUCKET_ID", type: "VARCHAR(16)" }, { name: "CASH_INFLOW", type: "NUMBER(18,2)" }, { name: "CASH_OUTFLOW", type: "NUMBER(18,2)" }, { name: "MATURITY_DATE", type: "DATE" }] },
              { name: "RAW_CC_TRANSACTIONS", rows: 1450000, columns: [{ name: "AUTH_ID", type: "VARCHAR(64) PRIMARY KEY" }, { name: "CARD_NO_TOKEN", type: "VARCHAR(64)" }, { name: "AMOUNT", type: "NUMBER(12,2)" }, { name: "MERCHANT_CATEGORY", type: "VARCHAR(8)" }, { name: "AUTH_STATUS", type: "VARCHAR(16)" }] },
              { name: "RAW_BUREAU_FEEDS", rows: 320000, columns: [{ name: "BUREAU_PULL_ID", type: "VARCHAR(64) PRIMARY KEY" }, { name: "PAN_TOKEN", type: "VARCHAR(64)" }, { name: "CIBIL_SCORE", type: "INTEGER" }, { name: "OVERDUE_AMOUNT", type: "NUMBER(15,2)" }, { name: "DPD_BUCKET", type: "VARCHAR(16)" }] },
              { name: "RAW_ADF_CIMS_RETURNS", rows: 64000, columns: [{ name: "RETURN_CODE", type: "VARCHAR(32) PRIMARY KEY" }, { name: "SECTION_ID", type: "VARCHAR(16)" }, { name: "REPORTING_DATE", type: "DATE" }, { name: "RWA_AMOUNT", type: "NUMBER(22,2)" }, { name: "CAPITAL_TIER1", type: "NUMBER(22,2)" }] },
              { name: "RAW_UPI_SWITCH", rows: 2100000, columns: [{ name: "RRN", type: "VARCHAR(32) PRIMARY KEY" }, { name: "PAYER_VPA", type: "VARCHAR(64)" }, { name: "PAYEE_VPA", type: "VARCHAR(64)" }, { name: "AMOUNT", type: "NUMBER(12,2)" }, { name: "RESP_CODE", type: "VARCHAR(8)" }] },
              { name: "RAW_JLG_COLLECTIONS", rows: 410000, columns: [{ name: "COLLECTION_ID", type: "VARCHAR(64) PRIMARY KEY" }, { name: "CENTER_ID", type: "VARCHAR(32)" }, { name: "GROUP_ID", type: "VARCHAR(32)" }, { name: "EMI_COLLECTED", type: "NUMBER(12,2)" }, { name: "PAR_STATUS", type: "VARCHAR(16)" }] },
              { name: "RAW_LOS_LMS_LOANS", rows: 185000, columns: [{ name: "LOAN_ACCOUNT_NO", type: "VARCHAR(32) PRIMARY KEY" }, { name: "APP_ID", type: "VARCHAR(32)" }, { name: "SANCTION_AMOUNT", type: "NUMBER(15,2)" }, { name: "DISBURSED_AMOUNT", type: "NUMBER(15,2)" }, { name: "ASSET_CLASS", type: "VARCHAR(16)" }] }
            ]
          },
          {
            name: "L1_HARMONIZED",
            description: "Cleansed & Quality Gate Validated Tier (SCD-2 Historical Normalization)",
            tables: [
              { name: "FACT_AML_CASES_CLEANSED", rows: 146200, columns: [{ name: "CASE_ID", type: "VARCHAR(64) PRIMARY KEY" }, { name: "CUSTOMER_ID", type: "VARCHAR(32)" }, { name: "STR_ELIGIBLE", type: "BOOLEAN" }, { name: "INVESTIGATOR_ID", type: "VARCHAR(32)" }] },
              { name: "FACT_ALM_MATURITY_BUCKETS", rows: 214800, columns: [{ name: "BUCKET_CODE", type: "VARCHAR(16) PRIMARY KEY" }, { name: "NET_LIQUIDITY_GAP", type: "NUMBER(20,2)" }, { name: "CUMULATIVE_GAP_PCT", type: "FLOAT" }] },
              { name: "FACT_CC_CLEANSED_TXNS", rows: 1448500, columns: [{ name: "TXN_KEY", type: "VARCHAR(64) PRIMARY KEY" }, { name: "CUSTOMER_ID", type: "VARCHAR(32)" }, { name: "DELINQUENCY_STAGE", type: "VARCHAR(16)" }, { name: "FINANCE_CHARGE", type: "NUMBER(12,2)" }] },
              { name: "FACT_BUREAU_MATCHED_SCORES", rows: 318400, columns: [{ name: "CUSTOMER_ID", type: "VARCHAR(32) PRIMARY KEY" }, { name: "CREDIT_TIER", type: "VARCHAR(16)" }, { name: "PROBABILITY_OF_DEFAULT", type: "FLOAT" }] },
              { name: "FACT_CIMS_HARMONIZED_RETS", rows: 63900, columns: [{ name: "FORM_CODE", type: "VARCHAR(32) PRIMARY KEY" }, { name: "CRAR_RATIO", type: "FLOAT" }, { name: "COMPLIANCE_STATUS", type: "VARCHAR(16)" }] },
              { name: "FACT_UPI_SETTLED_TXNS", rows: 2098000, columns: [{ name: "SETTLEMENT_REF", type: "VARCHAR(64) PRIMARY KEY" }, { name: "CLEARING_CYCLE", type: "VARCHAR(16)" }, { name: "NET_FEE_INR", type: "NUMBER(10,2)" }] },
              { name: "FACT_JLG_RECONCILED_DUES", rows: 409200, columns: [{ name: "GROUP_ID", type: "VARCHAR(32) PRIMARY KEY" }, { name: "RECOVERY_RATE_PCT", type: "FLOAT" }, { name: "NPA_EXPOSURE", type: "NUMBER(15,2)" }] },
              { name: "FACT_LOS_LMS_SERVICED_LOANS", rows: 184600, columns: [{ name: "LOAN_ACCOUNT_NO", type: "VARCHAR(32) PRIMARY KEY" }, { name: "CURRENT_PRINCIPAL", type: "NUMBER(15,2)" }, { name: "OVERDUE_DAYS", type: "INTEGER" }, { name: "NPA_STAGE", type: "VARCHAR(16)" }] }
            ]
          },
          {
            name: "L2_CURATED",
            description: "Curated Analytical Marts & Star Schema (Executive EOD Reporting T-1)",
            tables: [
              { name: "MART_AML_STR_REGULATORY", rows: 12400, columns: [{ name: "DISCLOSURE_ID", type: "VARCHAR(64) PRIMARY KEY" }, { name: "FIU_IND_SENT", type: "BOOLEAN" }, { name: "TOTAL_ALERT_VALUE", type: "NUMBER(22,2)" }] },
              { name: "MART_ALM_LIQUIDITY_GAP", rows: 365, columns: [{ name: "REPORT_DATE", type: "DATE PRIMARY KEY" }, { name: "STRESS_TEST_SURPLUS", type: "NUMBER(22,2)" }, { name: "LCR_PERCENTAGE", type: "FLOAT" }] },
              { name: "MART_CC_DELINQUENCY_REV", rows: 54200, columns: [{ name: "BILLING_CYCLE", type: "VARCHAR(16) PRIMARY KEY" }, { name: "TOTAL_REVOLVING_BOOK", type: "NUMBER(22,2)" }, { name: "PAR_90_PLUS_PCT", type: "FLOAT" }] },
              { name: "MART_BUREAU_RISK_MIGRATION", rows: 28500, columns: [{ name: "COHORT_MONTH", type: "VARCHAR(16) PRIMARY KEY" }, { name: "DOWNGRADE_COUNT", type: "INTEGER" }, { name: "EXPECTED_LOSS_INR", type: "NUMBER(22,2)" }] },
              { name: "MART_CIMS_BASEL3_DISCLOSURE", rows: 52, columns: [{ name: "QUARTER_ID", type: "VARCHAR(16) PRIMARY KEY" }, { name: "TIER1_CAPITAL_ADEQUACY", type: "FLOAT" }, { name: "LEVERAGE_RATIO", type: "FLOAT" }] },
              { name: "MART_UPI_SWITCH_SETTLEMENT", rows: 1825, columns: [{ name: "SETTLEMENT_DATE", type: "DATE PRIMARY KEY" }, { name: "NPCI_VOLUME_CLEARED", type: "NUMBER" }, { name: "SUCCESS_RATE_PCT", type: "FLOAT" }] },
              { name: "MART_JLG_PAR_RECOVERY", rows: 18400, columns: [{ name: "BRANCH_ID", type: "VARCHAR(32) PRIMARY KEY" }, { name: "ZERO_PAR_CENTERS_COUNT", type: "INTEGER" }, { name: "TOTAL_OVERDUE", type: "NUMBER(18,2)" }] },
              { name: "MART_LOS_LMS_NPA_PROVISIONING", rows: 9800, columns: [{ name: "PORTFOLIO_ID", type: "VARCHAR(32) PRIMARY KEY" }, { name: "GROSS_NPA_PCT", type: "FLOAT" }, { name: "PROVISION_COVERAGE_RATIO", type: "FLOAT" }] },
              { name: "DIM_CUSTOMER_360", rows: 145000, columns: [{ name: "CUSTOMER_SK", type: "NUMBER PRIMARY KEY" }, { name: "CUSTOMER_ID", type: "VARCHAR(32)" }, { name: "FULL_NAME", type: "VARCHAR(128)" }, { name: "RISK_CATEGORY", type: "VARCHAR(16)" }] },
              { name: "DIM_ACCOUNT_MASTER", rows: 84000, columns: [{ name: "ACCOUNT_NO", type: "VARCHAR(32) PRIMARY KEY" }, { name: "PRODUCT_CODE", type: "VARCHAR(16)" }, { name: "OPEN_DATE", type: "DATE" }, { name: "BRANCH_CODE", type: "VARCHAR(16)" }] }
            ]
          }
        ]
      },
      {
        id: "aws",
        name: "AWS S3 Lakehouse (765865641438)",
        kind: "aws",
        icon: "🟧",
        schemas: [
          {
            name: "bronze_l0",
            description: "Raw Parquet Lakehouse Vault (ap-southeast-2)",
            tables: [
              { name: "aml_raw_alerts.parquet", rows: 148000, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/bronze/aml/raw_alerts.parquet" }, { name: "size", type: "28.4 MB" }, { name: "format", type: "SNAPPY_PARQUET" }] },
              { name: "alm_cashflows_raw.parquet", rows: 215000, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/bronze/alm/cashflows_raw.parquet" }, { name: "size", type: "41.2 MB" }, { name: "format", type: "PARQUET" }] },
              { name: "credit_card_txns_raw.parquet", rows: 1450000, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/bronze/credit_card/txns_raw.parquet" }, { name: "size", type: "164.8 MB" }, { name: "format", type: "PARQUET" }] },
              { name: "bureau_cibil_raw.parquet", rows: 320000, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/bronze/bureau/cibil_raw.parquet" }, { name: "size", type: "52.6 MB" }, { name: "format", type: "PARQUET" }] },
              { name: "cims_rbi_returns_raw.parquet", rows: 64000, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/bronze/cims/returns_raw.parquet" }, { name: "size", type: "18.3 MB" }, { name: "format", type: "PARQUET" }] },
              { name: "upi_switch_raw.parquet", rows: 2100000, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/bronze/upi/switch_raw.parquet" }, { name: "size", type: "210.5 MB" }, { name: "format", type: "PARQUET" }] },
              { name: "jlg_collections_raw.parquet", rows: 410000, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/bronze/jlg/collections_raw.parquet" }, { name: "size", type: "62.4 MB" }, { name: "format", type: "PARQUET" }] },
              { name: "los_lms_loans_raw.parquet", rows: 185000, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/bronze/los_lms/loans_raw.parquet" }, { name: "size", type: "36.8 MB" }, { name: "format", type: "PARQUET" }] }
            ]
          },
          {
            name: "silver_l1",
            description: "Cleansed & Deduplicated Parquet Layer",
            tables: [
              { name: "aml_cases_cleansed.parquet", rows: 146200, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/silver/aml/cases_cleansed.parquet" }, { name: "size", type: "26.1 MB" }, { name: "format", type: "PARQUET" }] },
              { name: "alm_maturity_buckets.parquet", rows: 214800, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/silver/alm/maturity_buckets.parquet" }, { name: "size", type: "38.9 MB" }, { name: "format", type: "PARQUET" }] },
              { name: "credit_card_cleansed.parquet", rows: 1448500, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/silver/credit_card/cleansed.parquet" }, { name: "size", type: "152.0 MB" }, { name: "format", type: "PARQUET" }] },
              { name: "bureau_matched_scores.parquet", rows: 318400, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/silver/bureau/matched_scores.parquet" }, { name: "size", type: "48.2 MB" }, { name: "format", type: "PARQUET" }] },
              { name: "cims_harmonized_returns.parquet", rows: 63900, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/silver/cims/harmonized.parquet" }, { name: "size", type: "16.5 MB" }, { name: "format", type: "PARQUET" }] },
              { name: "upi_settled_txns.parquet", rows: 2098000, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/silver/upi/settled_txns.parquet" }, { name: "size", type: "194.2 MB" }, { name: "format", type: "PARQUET" }] },
              { name: "jlg_reconciled_dues.parquet", rows: 409200, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/silver/jlg/reconciled.parquet" }, { name: "size", type: "58.1 MB" }, { name: "format", type: "PARQUET" }] },
              { name: "los_lms_serviced_loans.parquet", rows: 184600, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/silver/los_lms/serviced_loans.parquet" }, { name: "size", type: "34.2 MB" }, { name: "format", type: "PARQUET" }] }
            ]
          },
          {
            name: "gold_l2",
            description: "Curated Marts & Durable Lakehouse Store",
            tables: [
              { name: "dim_customer_360.parquet", rows: 145000, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/gold/marts/dim_customer_360.parquet" }, { name: "size", type: "18.4 MB" }, { name: "format", type: "PARQUET" }] },
              { name: "fact_daily_financial_marts.parquet", rows: 1825, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/gold/marts/fact_daily_financial_marts.parquet" }, { name: "size", type: "12.8 MB" }, { name: "format", type: "PARQUET" }] },
              { name: "gold_marts.duckdb", rows: 84000, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/lakehouse/gold_marts.duckdb" }, { name: "size", type: "24.6 MB" }, { name: "format", type: "DUCKDB_DATABASE" }] }
            ]
          }
        ]
      },
      {
        id: "duckdb",
        name: "DuckDB Local Lakehouse (gold_marts)",
        kind: "duckdb",
        icon: "🦆",
        schemas: [
          {
            name: "gold_marts",
            description: "Zero-Latency Columnar In-Memory Analytics (All 8 Projects)",
            tables: [
              { name: "mart_aml_suspicious_alerts", rows: 12400, columns: [{ name: "alert_id", type: "VARCHAR PRIMARY KEY" }, { name: "risk_category", type: "VARCHAR" }, { name: "fiu_eligible", type: "BOOLEAN" }, { name: "amount_inr", type: "DECIMAL(18,2)" }] },
              { name: "mart_alm_structural_liquidity", rows: 365, columns: [{ name: "as_of_date", type: "DATE PRIMARY KEY" }, { name: "net_gap_inr", type: "DECIMAL(20,2)" }, { name: "cumulative_gap_pct", type: "DOUBLE" }] },
              { name: "mart_credit_card_risk", rows: 54200, columns: [{ name: "account_id", type: "VARCHAR PRIMARY KEY" }, { name: "dpd_bucket", type: "VARCHAR" }, { name: "revolving_balance", type: "DECIMAL(18,2)" }] },
              { name: "mart_bureau_cibil_scores", rows: 28500, columns: [{ name: "customer_id", type: "VARCHAR PRIMARY KEY" }, { name: "score", type: "INTEGER" }, { name: "delinquency_grade", type: "VARCHAR" }] },
              { name: "mart_adf_cims_basel3", rows: 52, columns: [{ name: "quarter_code", type: "VARCHAR PRIMARY KEY" }, { name: "crar_pct", type: "DOUBLE" }, { name: "tier1_capital", type: "DECIMAL(22,2)" }] },
              { name: "mart_upi_switch_reconciliation", rows: 1825, columns: [{ name: "settle_date", type: "DATE PRIMARY KEY" }, { name: "npci_settled_vol", type: "BIGINT" }, { name: "chargeback_count", type: "INTEGER" }] },
              { name: "mart_jlg_group_collections", rows: 18400, columns: [{ name: "group_id", type: "VARCHAR PRIMARY KEY" }, { name: "recovery_rate", type: "DOUBLE" }, { name: "par_overdue_inr", type: "DECIMAL(18,2)" }] },
              { name: "mart_los_lms_loan_portfolio", rows: 9800, columns: [{ name: "loan_id", type: "VARCHAR PRIMARY KEY" }, { name: "principal_due", type: "DECIMAL(18,2)" }, { name: "npa_stage", type: "VARCHAR" }] }
            ]
          }
        ]
      },
      {
        id: "bigquery",
        name: "Google BigQuery Banking Sandbox",
        kind: "bigquery",
        icon: "☁️",
        schemas: [
          {
            name: "banking_prod",
            description: "Google Cloud Multi-Cloud Enterprise Repository",
            tables: [
              { name: "cims_regulatory_audit_trail", rows: 840000, columns: [{ name: "audit_id", type: "STRING" }, { name: "return_code", type: "STRING" }, { name: "actor", type: "STRING" }, { name: "verified_at", type: "TIMESTAMP" }] },
              { name: "aml_str_ml_features", rows: 146200, columns: [{ name: "customer_id", type: "STRING" }, { name: "anomaly_score", type: "FLOAT64" }, { name: "graph_centrality", type: "FLOAT64" }] },
              { name: "daily_executive_kpi_mart", rows: 1825, columns: [{ name: "close_date", type: "DATE" }, { name: "nim_ratio", type: "FLOAT64" }, { name: "gnpa_pct", type: "FLOAT64" }, { name: "total_deposits", type: "NUMERIC" }] }
            ]
          }
        ]
      }
    ];

    ailabRenderExplorerTree();'''

match = re.search(old_fallback_pattern, code)
if match:
    code = code[:match.start()] + "\n" + new_fallback_block + code[match.end():]
    print("SUCCESS: Updated fallback static catalog in global_ai_lab_view.py")
else:
    print("FAILED: old_fallback_pattern not matched in global_ai_lab_view.py")

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
