"""Update cloudflare_worker_gateway.js with 8 Banking Projects and Airflow/SFTP API endpoints."""
import json
import re

path = 'deploy/cloudflare_worker_gateway.js'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update /api/ai/explorer/catalog endpoint
catalog_target = 'if (path === "/api/ai/explorer/catalog") {'
new_catalog_block = '''    // 8 CORE BANKING PROJECTS EXPLORER CATALOG API (Snowflake BANK_DB, AWS S3, DuckDB, BigQuery)
    if (path === "/api/ai/explorer/catalog") {
      const BANKING_CATALOG = [
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

      return new Response(JSON.stringify({
        status: "success",
        databases: BANKING_CATALOG
      }), {
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*", "X-Edge-Explorer": "True" }
      });
    }

    // 8 BANKING AIRFLOW DAGS & ORCHESTRATION APIS
    if (path === "/api/banking/dag/list") {
      const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
      const dags = [
        { dag_id: "dag_aml_pipeline", project_id: "aml", project_name: "AML (Anti-Money Laundering)", code: "AML", schedule: "EOD (20:00 IST) Daily T-1", status: "SUCCESS", latest_run_type: "INCREMENTAL_LOAD", execution_date_t1: yesterday, report_filename: `AML_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, report_size_mb: 2.4, email_rule_applied: "ATTACH_WITH_BODY", can_rollback: true },
        { dag_id: "dag_alm_pipeline", project_id: "alm", project_name: "ALM (Asset Liability Management)", code: "ALM", schedule: "EOD (20:00 IST) Daily T-1", status: "SUCCESS", latest_run_type: "FULL_LOAD", execution_date_t1: yesterday, report_filename: `ALM_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, report_size_mb: 3.1, email_rule_applied: "ATTACH_WITH_BODY", can_rollback: true },
        { dag_id: "dag_credit_card_pipeline", project_id: "credit_card", project_name: "Credit Card", code: "CC", schedule: "EOD (20:00 IST) Daily T-1", status: "SUCCESS", latest_run_type: "INCREMENTAL_LOAD", execution_date_t1: yesterday, report_filename: `CC_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, report_size_mb: 7.8, email_rule_applied: "LINK_ONLY_EXCEEDS_5MB", can_rollback: true },
        { dag_id: "dag_bureau_mart_pipeline", project_id: "bureau_mart", project_name: "Bureau Mart (CIBIL / Experian)", code: "BUREAU", schedule: "SOD (08:30 IST) Monthly/Daily", status: "SUCCESS", latest_run_type: "FULL_LOAD", execution_date_t1: yesterday, report_filename: `BUREAU_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, report_size_mb: 4.2, email_rule_applied: "ATTACH_WITH_BODY", can_rollback: true },
        { dag_id: "dag_adf_cims_pipeline", project_id: "adf_cims", project_name: "ADF CIMS (RBI Reporting)", code: "CIMS", schedule: "EOD (20:00 IST) Fortnightly/Daily", status: "SUCCESS", latest_run_type: "CUT_PARTITION", execution_date_t1: yesterday, report_filename: `CIMS_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, report_size_mb: 1.8, email_rule_applied: "ATTACH_WITH_BODY", can_rollback: true },
        { dag_id: "dag_upi_settlement_pipeline", project_id: "upi", project_name: "UPI (Unified Payments Interface)", code: "UPI", schedule: "SOD (08:30 IST) / EOD Intraday T-1", status: "SUCCESS", latest_run_type: "INCREMENTAL_LOAD", execution_date_t1: yesterday, report_filename: `UPI_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, report_size_mb: 12.5, email_rule_applied: "LINK_ONLY_EXCEEDS_5MB", can_rollback: true },
        { dag_id: "dag_jlg_collection_pipeline", project_id: "jlg_collection", project_name: "JLG-Non JLG Collection", code: "JLG", schedule: "EOD (20:00 IST) Daily T-1", status: "SUCCESS", latest_run_type: "INCREMENTAL_LOAD", execution_date_t1: yesterday, report_filename: `JLG_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, report_size_mb: 3.6, email_rule_applied: "ATTACH_WITH_BODY", can_rollback: true },
        { dag_id: "dag_los_lms_pipeline", project_id: "los_lms", project_name: "LOS and LMS (Origination & Servicing)", code: "LOS_LMS", schedule: "BOD (06:00 IST) & EOD (20:00 IST)", status: "SUCCESS", latest_run_type: "INCREMENTAL_LOAD", execution_date_t1: yesterday, report_filename: `LOS_LMS_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, report_size_mb: 4.9, email_rule_applied: "ATTACH_WITH_BODY", can_rollback: true }
      ];
      return new Response(JSON.stringify({ status: "success", dags }), {
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
      });
    }

    if (path === "/api/banking/dag/trigger") {
      let b = {}; try { b = await request.json(); } catch (_) {}
      const pid = b.project_id || "aml";
      const loadType = b.load_type || "INCREMENTAL_LOAD";
      const mode = b.mode || "APPEND";
      const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
      const filename = `${pid.toUpperCase()}_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`;
      const sizeMb = loadType === "FULL_LOAD" ? 7.2 : 2.8;

      return new Response(JSON.stringify({
        status: "success",
        result: {
          success: true,
          run_id: `edge_run_${pid}_${Date.now()}`,
          dag_id: `dag_${pid}_pipeline`,
          load_type: loadType,
          mode: mode,
          t1_basis: yesterday,
          quality_gate: "PASSED_100_PCT",
          status: "SUCCESS",
          report_filename: filename,
          report_size_mb: sizeMb,
          sftp_path: `/sftp/outbound/reports/${filename}`,
          email_dispatched: {
            from: "mangeshbagul15@gmail.com",
            to: "nanoproaistudio@gmail.com",
            rule: sizeMb <= 5.0 ? "ATTACH_WITH_BODY" : "LINK_ONLY_EXCEEDS_5MB",
            attached: sizeMb <= 5.0
          }
        }
      }), {
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
      });
    }

    if (path === "/api/banking/dag/rollback") {
      let b = {}; try { b = await request.json(); } catch (_) {}
      const pid = b.project_id || "aml";
      const targetLayer = b.target_layer || "L1_HARMONIZED";
      return new Response(JSON.stringify({
        status: "success",
        result: {
          success: true,
          project_id: pid,
          target_layer: targetLayer,
          rolled_back_at: new Date().toISOString(),
          message: `Successfully rolled back ${pid.toUpperCase()} to last stable ${targetLayer} watermark. Pipeline ready for clean execution.`
        }
      }), {
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
      });
    }

    if (path === "/api/sftp/reports/list") {
      const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
      const reports = [
        { filename: `AML_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, size_mb: 2.4, size_formatted: "2.4 MB", sftp_path: `/sftp/outbound/reports/AML_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, email_rule: "Attached (<= 5MB)" },
        { filename: `ALM_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, size_mb: 3.1, size_formatted: "3.1 MB", sftp_path: `/sftp/outbound/reports/ALM_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, email_rule: "Attached (<= 5MB)" },
        { filename: `CC_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, size_mb: 7.8, size_formatted: "7.8 MB", sftp_path: `/sftp/outbound/reports/CC_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, email_rule: "Link Only (> 5MB)" },
        { filename: `BUREAU_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, size_mb: 4.2, size_formatted: "4.2 MB", sftp_path: `/sftp/outbound/reports/BUREAU_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, email_rule: "Attached (<= 5MB)" },
        { filename: `CIMS_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, size_mb: 1.8, size_formatted: "1.8 MB", sftp_path: `/sftp/outbound/reports/CIMS_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, email_rule: "Attached (<= 5MB)" },
        { filename: `UPI_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, size_mb: 12.5, size_formatted: "12.5 MB", sftp_path: `/sftp/outbound/reports/UPI_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, email_rule: "Link Only (> 5MB)" },
        { filename: `JLG_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, size_mb: 3.6, size_formatted: "3.6 MB", sftp_path: `/sftp/outbound/reports/JLG_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, email_rule: "Attached (<= 5MB)" },
        { filename: `LOS_LMS_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, size_mb: 4.9, size_formatted: "4.9 MB", sftp_path: `/sftp/outbound/reports/LOS_LMS_EOD_T1_${yesterday.replace(/-/g, '')}.xlsx`, email_rule: "Attached (<= 5MB)" }
      ];
      return new Response(JSON.stringify({
        status: "success",
        reports,
        sftp_connection: {
          protocol: "SFTP",
          host: "nanopro-studio.onrender.com",
          port: 22,
          username: "mangeshbagul15",
          inbound_path: "/data/sftp/inbound/",
          outbound_path: "/data/sftp/outbound/reports/"
        }
      }), {
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
      });
    }

    if (path === "/api/sftp/reports/download") {
      const filename = url.searchParams.get("filename") || "AML_EOD_REPORT.xlsx";
      // Generate synthetic binary excel stream
      const header = `NanoPro Enterprise Banking EOD Report: ${filename}\\nGenerated on T-1 Basis\\nAudited & Cleared\\n`;
      return new Response(header, {
        headers: {
          "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          "Content-Disposition": `attachment; filename="${filename}"`,
          "Access-Control-Allow-Origin": "*"
        }
      });
    }
'''

# Find the end of the previous /api/ai/explorer/catalog handler
pattern = r'(\s+// DATA MODELING EXPLORER CATALOG API[^\n]*\n\s+if \(path === "/api/ai/explorer/catalog"\) \{[\s\S]*?\}\s*\}\);\s*\})'
match = re.search(pattern, code)
if match:
    code = code[:match.start()] + "\n" + new_catalog_block + "\n" + code[match.end():]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Updated cloudflare_worker_gateway.js catalog and routes")
else:
    print("FAILED: pattern not matched in cloudflare_worker_gateway.js")
