"""Update automation_scheduler.py with 8 Banking DAGs and disable old spammy tasks."""
import re

path = 'app/core/automation_scheduler.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_block = '''                ("DUCKDB_S3_CLOUD_BACKUP", "daily", "23:30", "Cloud Lakehouse Durability Sync — Mirrors local DuckDB Gold Marts to AWS S3 (s3://nanopro-data-lake-765865641438-ap-southeast-2-an/lakehouse/gold_marts.duckdb).", True),
                ("TELEGRAM_APK_DISPATCHER", "hourly", "4", "Autonomous Telegram APK Dispatcher (@mangesh_apk_bot) — Discovers and delivers verified open-source APKs with configurable quantity & interval.", True),
                ("ORACLE_S3_SNOWFLAKE_PIPELINE_INCREMENTAL", "minutes", "15", "Oracle watermark incremental polling every 15 minutes → S3 → Snowflake L0/L1/L2.", False),
                ("ORACLE_S3_SNOWFLAKE_PIPELINE_DAILY", "daily", "10:00", "Snowflake daily T-1/live comparison report at 10:00 IST.", False),'''

new_block = '''                ("DUCKDB_S3_CLOUD_BACKUP", "daily", "23:30", "Cloud Lakehouse Durability Sync — Mirrors local DuckDB Gold Marts to AWS S3 (s3://nanopro-data-lake-765865641438-ap-southeast-2-an/lakehouse/gold_marts.duckdb).", True),
                ("DAG_AML_PIPELINE", "daily", "20:00", "Airflow DAG — Anti-Money Laundering (AML) T-1 Ingestion, L1 Quality Gate, STR Curated Marts & EOD Report.", True),
                ("DAG_ALM_PIPELINE", "daily", "20:00", "Airflow DAG — Asset Liability Management (ALM) Liquidity Gap & Interest Rate Sensitivity Analysis.", True),
                ("DAG_CREDIT_CARD_PIPELINE", "daily", "20:00", "Airflow DAG — Credit Card Delinquency (30/60/90 DPD), Revolving Balances & Chargeback Reconciliation.", True),
                ("DAG_BUREAU_MART_PIPELINE", "daily", "08:30", "Airflow DAG — Bureau Mart (CIBIL/Experian) Credit Score Migration & Default Risk Rating.", True),
                ("DAG_ADF_CIMS_PIPELINE", "daily", "20:00", "Airflow DAG — RBI Automated Data Flow (ADF CIMS) Basel-III & CRR/SLR Regulatory Returns.", True),
                ("DAG_UPI_SETTLEMENT_PIPELINE", "daily", "08:30", "Airflow DAG — UPI Real-Time NPCI Switch Settlement & Dispute Clearing.", True),
                ("DAG_JLG_COLLECTION_PIPELINE", "daily", "20:00", "Airflow DAG — JLG/SHG Microfinance Group Collections & Portfolio at Risk (PAR) Recovery.", True),
                ("DAG_LOS_LMS_PIPELINE", "daily", "06:00", "Airflow DAG — Loan Origination (LOS) & Loan Management (LMS) NPA Provisioning & Servicing.", True),
                ("TELEGRAM_APK_DISPATCHER", "hourly", "4", "Autonomous Telegram APK Dispatcher (@mangesh_apk_bot) — Discovers and delivers verified open-source APKs with configurable quantity & interval.", False),
                ("ORACLE_S3_SNOWFLAKE_PIPELINE_INCREMENTAL", "minutes", "15", "Oracle watermark incremental polling every 15 minutes → S3 → Snowflake L0/L1/L2.", False),
                ("ORACLE_S3_SNOWFLAKE_PIPELINE_DAILY", "daily", "10:00", "Snowflake daily T-1/live comparison report at 10:00 IST.", False),'''

# Normalize newlines
text_norm = text.replace('\r\n', '\n')
old_norm = old_block.replace('\r\n', '\n')
new_norm = new_block.replace('\r\n', '\n')

if old_norm in text_norm:
    updated = text_norm.replace(old_norm, new_norm)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(updated)
    print("SUCCESS: automation_scheduler.py updated successfully.")
else:
    print("FAILED: old_block not found in text.")
