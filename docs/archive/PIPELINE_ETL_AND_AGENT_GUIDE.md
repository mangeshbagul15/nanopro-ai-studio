# Mangesh Nano Pro AI Studio — Enterprise Pipeline, ETL & Agent Operations Guide

This guide details how the **AI Operations Manager** and specialized agents orchestrate end-to-end data pipelines, cross-system ETL, and natural language prompts.

---

## 1. Enterprise Data Pipeline Architecture

```
┌─────────────────────────┐
│ Oracle Database XE     │ ──(1. Source Extraction: Incremental / Full Table SQL)──┐
│ (192.168.31.240:1521)   │                                                         │
└─────────────────────────┘                                                         │
                                                                                    ▼
┌─────────────────────────┐                                        ┌─────────────────────────┐
│ Online Cloud SFTP /     │ ──(External Vendor CSV / Excel /       │ S3 Lake / Staging Buffer│
│ AWS Transfer Family     │    Pipe '|' Delimited Inbound)───────► │ (s3://nanopro-data-lake)│
└─────────────────────────┘                                        └───────────┬─────────────┘
                                                                               │
                                                                               │ (2. Bulk Ingest)
                                                                               ▼
┌─────────────────────────┐                                        ┌─────────────────────────┐
│ Oracle Reverse ETL Sync │ ◄──(4. Reverse ETL / Golden Marts)──── │ Snowflake Warehouse     │
│ (Target Core Systems)   │                                        │ (BANK_DB Medallion)     │
└─────────────────────────┘                                        └─────────────────────────┘
                                                                               │
                                                                               ▼
                                                                   ┌─────────────────────────┐
                                                                   │ T-1 Audit & Alerts      │
                                                                   │ (Gmail SMTP & Telegram) │
                                                                   └─────────────────────────┘
```

### Medallion Architecture in Snowflake (`BANK_DB`):
1. **Bronze (`L0_STAGING`)**: Raw ingestion buffer preserving original source payloads (`RAW_TRANSACTIONS`, `RAW_CUSTOMERS`, `RAW_ACCOUNTS`).
2. **Silver (`L1_HARMONIZED`)**: Automated data standardization, type casting, schema evolution, and deduplication.
3. **Gold (`L2_CURATED`)**: Fact & Dimension business entities (`FACT_DAILY_BANK_TRANSACTIONS`).

---

## 2. Natural Language Prompts Supported by Manager Agent

The **AI Manager** (`/api/manager/chat`) understands prompts in both **Marathi and English**:

| User Intent | Marathi Prompt Example | English Prompt Example | Action Taken by Manager |
| :--- | :--- | :--- | :--- |
| **Database Discovery** | *"db konte ahet sang"* | *"What databases are connected?"* | Returns list of all active DBs (`BANK_DB`, `XEPDB1`, `studio_memory.db`, S3) |
| **Table Inventory** | *"table konte ahet"* | *"Show all tables"* | Lists accessible tables across Snowflake, Oracle, and SQLite |
| **Row Counts** | *"count kay ahe"* | *"Show table row counts"* | Reports record count statistics across tables |
| **Data Transfer & ETL** | *"oracle madhun data snowflake madhe transfer kar"* | *"Transfer data from Oracle to Snowflake"* | Triggers automated extraction, lake staging, and Snowflake L0 bulk load |
| **Append Records** | *"new records append kar"* | *"Append records to Snowflake"* | Runs incremental ETL append with deduplication |
| **Table Deletion (Safety)** | *"table delete kar"* | *"Drop table old_records"* | Intercepts high-risk command, creates Approval Request in Approval Queue |
| **Pipeline Explanation** | *"all pipeline and etl samjav"* | *"Explain the ETL pipeline"* | Delivers full multi-stage architecture walkthrough |
| **Agent & Tasks Status** | *"all task and info sang"* | *"Show all tasks and agent info"* | Reports live telemetry of all 8 specialized agents |

---

## 3. Specialized AI Agent Team

1. **Manager Agent**: Central orchestrator, natural language conversational interface, and safety gatekeeper.
2. **Data Engineer Agent**: Automated schema discovery, folder batch ingestion (`data_ingestion/`), and reconciliation.
3. **Task Planning Agent**: DAG pipeline builder and dependency coordinator.
4. **Snowflake Admin Agent**: Role & warehouse governance (`ACCOUNTADMIN`, `COMPUTE_WH`).
5. **Data Quality Agent**: 99.4% quality score verification, null constraint checks, and anomalous data detection.
6. **Harmonisation & Curated Agent**: Medallion pipeline execution (Bronze L0 ➔ Silver L1 ➔ Gold L2).
7. **Report Generation Agent**: Automated Excel (`.xlsx`) and PDF financial briefings.
8. **Communication Agent**: Automated notifications via Gmail SMTP (`GMAIL_SMTP`) and Telegram (`@mangesh_technews_bot`).

---

## 4. Security & Human-in-the-Loop Governance

Destructive DDL/DML operations (`DROP TABLE`, `TRUNCATE`, `DELETE FROM`) are never executed automatically without human approval:
1. When a destructive prompt is issued, the Manager generates a unique **Approval Request ID** (e.g. `appr_1791658131412`).
2. The action is held in the persistent SQLite database.
3. The user opens the **Approval Queue** in the Web UI and clicks **Approve** to execute, or **Reject** to abort.
