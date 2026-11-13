import sys

def main():
    catalog_json = '''[
          {
            id: "duckdb",
            name: "DuckDB Local Lakehouse (gold_marts)",
            kind: "duckdb",
            icon: "🦆",
            schemas: [
              {
                name: "gold_marts",
                tables: [
                  { name: "ai_conversations", rows: 1420, columns: [{ name: "id", type: "VARCHAR PRIMARY KEY" }, { name: "chat_id", type: "VARCHAR" }, { name: "role", type: "VARCHAR" }, { name: "content", type: "TEXT" }, { name: "created_at", type: "TIMESTAMP" }] },
                  { name: "banking_transactions_cdc", rows: 28400, columns: [{ name: "tx_id", type: "BIGINT PRIMARY KEY" }, { name: "account_no", type: "VARCHAR" }, { name: "amount", type: "DECIMAL(18,2)" }, { name: "cdc_operation", type: "VARCHAR" }, { name: "branch_code", type: "VARCHAR" }] },
                  { name: "dim_customer_master", rows: 1740, columns: [{ name: "customer_id", type: "VARCHAR" }, { name: "customer_name", type: "VARCHAR" }, { name: "segment", type: "VARCHAR" }] },
                  { name: "analytics_summary", rows: 365, columns: [{ name: "report_date", type: "DATE PRIMARY KEY" }, { name: "daily_volume", type: "DECIMAL(20,2)" }, { name: "tx_count", type: "INTEGER" }] }
                ]
              }
            ]
          },
          {
            id: "snowflake",
            name: "Snowflake Enterprise DW (BANK_DB)",
            kind: "snowflake",
            icon: "❄️",
            schemas: [
              {
                name: "L0_STAGING",
                tables: [
                  { name: "RAW_CUSTOMERS", rows: 145000, columns: [{ name: "CUSTOMER_ID", type: "VARCHAR(32) PRIMARY KEY" }, { name: "FULL_NAME", type: "VARCHAR(128)" }, { name: "CITY", type: "VARCHAR(80)" }, { name: "KYC_STATUS", type: "VARCHAR(16)" }, { name: "INGESTED_AT", type: "TIMESTAMP_NTZ" }] },
                  { name: "RAW_TRANSACTIONS", rows: 1250000, columns: [{ name: "TXN_ID", type: "VARCHAR(64) PRIMARY KEY" }, { name: "SRC_ACCOUNT", type: "VARCHAR(32)" }, { name: "DEST_ACCOUNT", type: "VARCHAR(32)" }, { name: "AMOUNT", type: "NUMBER(18,2)" }, { name: "TXN_TYPE", type: "VARCHAR(16)" }, { name: "TXN_DATE", type: "TIMESTAMP_NTZ" }] },
                  { name: "RAW_ACCOUNTS", rows: 84000, columns: [{ name: "ACCOUNT_NO", type: "VARCHAR(32) PRIMARY KEY" }, { name: "CUSTOMER_ID", type: "VARCHAR(32)" }, { name: "ACCOUNT_TYPE", type: "VARCHAR(16)" }, { name: "BALANCE", type: "NUMBER(18,2)" }, { name: "BRANCH_CODE", type: "VARCHAR(16)" }] },
                  { name: "NANOPRO_LIVE_DATA", rows: 48200, columns: [{ name: "SOURCE", type: "VARCHAR(32)" }, { name: "PAYLOAD", type: "VARIANT" }, { name: "CREATED_AT", type: "TIMESTAMP_NTZ" }] },
                  { name: "NANOPRO_REPORTS", rows: 365, columns: [{ name: "REPORT_NAME", type: "VARCHAR(128)" }, { name: "CONTENT", type: "TEXT" }, { name: "CREATED_AT", type: "TIMESTAMP_NTZ" }] },
                  { name: "NANOPRO_HEALTH_LOG", rows: 14200, columns: [{ name: "UPSTREAM", type: "VARCHAR(64)" }, { name: "STATUS", type: "VARCHAR(16)" }, { name: "LATENCY_MS", type: "NUMBER" }] }
                ]
              },
              {
                name: "L1_HARMONIZED",
                tables: [
                  { name: "CUSTOMERS_CLEANSED", rows: 142800, columns: [{ name: "CUSTOMER_ID", type: "VARCHAR(32) PRIMARY KEY" }, { name: "CLEANSED_NAME", type: "VARCHAR(128)" }, { name: "STANDARDIZED_CITY", type: "VARCHAR(80)" }, { name: "IS_ACTIVE", type: "BOOLEAN" }] },
                  { name: "TRANSACTIONS_ENRICHED", rows: 1248000, columns: [{ name: "TXN_ID", type: "VARCHAR(64) PRIMARY KEY" }, { name: "ACCOUNT_NO", type: "VARCHAR(32)" }, { name: "NET_AMOUNT", type: "NUMBER(18,2)" }, { name: "CHANNEL", type: "VARCHAR(16)" }, { name: "FRAUD_FLAG", type: "BOOLEAN" }] },
                  { name: "ACCOUNT_BALANCES", rows: 84000, columns: [{ name: "ACCOUNT_NO", type: "VARCHAR(32) PRIMARY KEY" }, { name: "AVAILABLE_BAL", type: "NUMBER(18,2)" }, { name: "HOLD_BAL", type: "NUMBER(18,2)" }, { name: "LAST_UPDATED", type: "TIMESTAMP_NTZ" }] }
                ]
              },
              {
                name: "L2_CURATED",
                tables: [
                  { name: "DIM_CUSTOMER_MASTER", rows: 142800, columns: [{ name: "CUSTOMER_SK", type: "NUMBER PRIMARY KEY" }, { name: "CUSTOMER_ID", type: "VARCHAR(32)" }, { name: "SEGMENT", type: "VARCHAR(32)" }, { name: "LIFETIME_VALUE", type: "NUMBER(20,2)" }] },
                  { name: "FACT_DAILY_SETTLEMENT", rows: 1825, columns: [{ name: "SETTLEMENT_DATE", type: "DATE PRIMARY KEY" }, { name: "TOTAL_TX_COUNT", type: "NUMBER" }, { name: "GROSS_CREDIT", type: "NUMBER(22,2)" }, { name: "GROSS_DEBIT", type: "NUMBER(22,2)" }, { name: "NET_SETTLEMENT", type: "NUMBER(22,2)" }] },
                  { name: "EOD_FINANCIAL_SUMMARY", rows: 365, columns: [{ name: "EOD_DATE", type: "DATE PRIMARY KEY" }, { name: "CLOSING_LIQUIDITY", type: "NUMBER(22,2)" }, { name: "RECONCILED_FLAG", type: "BOOLEAN" }, { name: "AUDIT_HASH", type: "VARCHAR(64)" }] },
                  { name: "KPI_EXECUTIVE_SUMMARY", rows: 52, columns: [{ name: "WEEK_NO", type: "VARCHAR(10) PRIMARY KEY" }, { name: "ACTIVE_USERS", type: "NUMBER" }, { name: "CHURN_RATE", type: "FLOAT" }, { name: "NIM_RATIO", type: "FLOAT" }] }
                ]
              },
              {
                name: "SALES",
                tables: [
                  { name: "SALES_ORDERS", rows: 54000, columns: [{ name: "ORDER_ID", type: "NUMBER PRIMARY KEY" }, { name: "CUSTOMER_NAME", type: "VARCHAR(120)" }, { name: "CITY", type: "VARCHAR(80)" }, { name: "AMOUNT", type: "NUMBER(12,2)" }] },
                  { name: "V_REGION_REVENUE", rows: 12, columns: [{ name: "CITY", type: "VARCHAR(80)" }, { name: "TOTAL_ORDERS", type: "NUMBER" }, { name: "TOTAL_REVENUE", type: "NUMBER(18,2)" }] }
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
                tables: [
                  { name: "transactions_2026.parquet", rows: 150000, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/bronze/banking/transactions_2026.parquet" }, { name: "size", type: "42.8 MB" }, { name: "format", type: "SNAPPY_PARQUET" }] },
                  { name: "raw_customers.parquet", rows: 84000, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/bronze/banking/raw_customers.parquet" }, { name: "size", type: "16.4 MB" }, { name: "format", type: "PARQUET" }] },
                  { name: "incoming_stream.parquet", rows: 48200, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/bronze/cbs/incoming_stream.parquet" }, { name: "size", type: "14.1 MB" }, { name: "format", type: "PARQUET" }] }
                ]
              },
              {
                name: "silver_l1",
                tables: [
                  { name: "customers_cleansed.parquet", rows: 78400, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/silver/banking/customers_cleansed.parquet" }, { name: "size", type: "18.2 MB" }, { name: "format", type: "PARQUET" }] },
                  { name: "transactions_enriched.parquet", rows: 124800, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/silver/banking/transactions_enriched.parquet" }, { name: "size", type: "34.5 MB" }, { name: "format", type: "PARQUET" }] },
                  { name: "account_balances.parquet", rows: 62000, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/silver/banking/account_balances.parquet" }, { name: "size", type: "12.8 MB" }, { name: "format", type: "PARQUET" }] }
                ]
              },
              {
                name: "gold_l2",
                tables: [
                  { name: "dim_customer_master.parquet", rows: 1740, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/gold/marts/dim_customer_master.parquet" }, { name: "size", type: "8.4 MB" }, { name: "format", type: "PARQUET" }] },
                  { name: "fact_daily_settlement.parquet", rows: 1825, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/gold/marts/fact_daily_settlement.parquet" }, { name: "size", type: "6.2 MB" }, { name: "format", type: "PARQUET" }] },
                  { name: "gold_marts.duckdb", rows: 49000, columns: [{ name: "s3_uri", type: "s3://nanopro-data-lake-765865641438-ap-southeast-2-an/lakehouse/gold_marts.duckdb" }, { name: "size", type: "18.9 MB" }, { name: "format", type: "DUCKDB_DATABASE" }] }
                ]
              }
            ]
          },
          {
            id: "bigquery",
            name: "Google BigQuery Lakehouse",
            kind: "bigquery",
            icon: "☁️",
            schemas: [
              {
                name: "nanopro_lakehouse",
                tables: [
                  { name: "lakehouse_audit_logs", rows: 840000, columns: [{ name: "event_id", type: "STRING" }, { name: "event_timestamp", type: "TIMESTAMP" }, { name: "actor", type: "STRING" }, { name: "action", type: "STRING" }] },
                  { name: "model_inferences_2026", rows: 54000, columns: [{ name: "request_id", type: "STRING" }, { name: "provider", type: "STRING" }, { name: "model_id", type: "STRING" }, { name: "latency_ms", type: "FLOAT64" }] },
                  { name: "eod_settlement_archive", rows: 12500, columns: [{ name: "settlement_date", type: "DATE" }, { name: "batch_id", type: "STRING" }, { name: "total_cleared", type: "NUMERIC" }] },
                  { name: "customer_segments", rows: 8200, columns: [{ name: "customer_id", type: "STRING" }, { name: "rfm_score", type: "INT64" }, { name: "segment_label", type: "STRING" }] }
                ]
              }
            ]
          }
        ]'''

    # 1. Update deploy/cloudflare_worker_gateway.js
    gw_path = "deploy/cloudflare_worker_gateway.js"
    with open(gw_path, "r", encoding="utf-8") as f:
        gw_code = f.read()

    gw_start = '    // DATA MODELING EXPLORER CATALOG API (AWS, Snowflake, BigQuery, DuckDB)\n    if (path === "/api/ai/explorer/catalog") {'
    gw_end = '    if (path === "/api/ai/history/chats") {'

    idx1 = gw_code.find(gw_start)
    idx2 = gw_code.find(gw_end, idx1)

    if idx1 != -1 and idx2 != -1:
        new_gw_block = f'''    // DATA MODELING EXPLORER CATALOG API (AWS, Snowflake, BigQuery, DuckDB)
    if (path === "/api/ai/explorer/catalog") {{
      return new Response(JSON.stringify({{
        status: "success",
        databases: {catalog_json}
      }}), {{
        headers: {{ "Content-Type": "application/json", "Access-Control-Allow-Origin": "*", "X-Edge-Explorer": "True" }}
      }});
    }}

'''
        gw_code = gw_code[:idx1] + new_gw_block + gw_code[idx2:]
        with open(gw_path, "w", encoding="utf-8") as f:
            f.write(gw_code)
        print("[+] Successfully updated deploy/cloudflare_worker_gateway.js with Medallion L0/L1/L2 schemas!")
    else:
        print("[!] Gateway markers not found:", idx1, idx2)

    # 2. Update app/ui/global_ai_lab_view.py fallback catalog
    ui_path = "app/ui/global_ai_lab_view.py"
    with open(ui_path, "r", encoding="utf-8") as f:
        ui_code = f.read()

    ui_start = '    // Fallback static seed catalog\n    AILAB_EXPLORER.catalog = ['
    ui_end = '    ailabRenderExplorerTree();\n  };'

    uidx1 = ui_code.find(ui_start)
    uidx2 = ui_code.find(ui_end, uidx1)

    if uidx1 != -1 and uidx2 != -1:
        new_ui_block = f'''    // Fallback static seed catalog
    AILAB_EXPLORER.catalog = {catalog_json};

'''
        ui_code = ui_code[:uidx1] + new_ui_block + ui_code[uidx2:]
        with open(ui_path, "w", encoding="utf-8") as f:
            f.write(ui_code)
        print("[+] Successfully updated app/ui/global_ai_lab_view.py with Medallion L0/L1/L2 schemas!")
    else:
        print("[!] UI markers not found:", uidx1, uidx2)

if __name__ == "__main__":
    main()
