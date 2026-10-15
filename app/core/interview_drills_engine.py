"""
Mangesh Nano Pro AI Studio - Enterprise Technical Interview Drills Engine
Multi-Domain Senior Data Engineer Interview Scenarios covering:
- Python (Memory optimization, PySpark, Generators, Concurrency, Pydantic)
- AWS (S3, Glue DynamicFrames, Lambda triggers, DMS CDC, Athena)
- Snowflake (Micro-partitions, Dynamic Tables, Streams & Tasks, Zero-Copy Clone, Clustering)
- SQL (Window Functions, QUALIFY, CTEs, SCD Type 2 Merge, Running Totals)
- Data Pipeline & Lakehouse Architecture (Medallion L0-L1-L2, Idempotency, Watermarking)
- ETL & Data Quality (Change Data Capture, Dead-Letter Quarantine, Deduplication Hashes)

Guarantees a different real-world scenario, question, code/query solution, and interviewer tip on every single dispatch.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.core.config import BASE_DIR
from app.core.logger import log_event

STATE_DIR = BASE_DIR / "data" / "banking"
STATE_DIR.mkdir(parents=True, exist_ok=True)
DRILLS_STATE_FILE = STATE_DIR / "interview_drills_state.json"

SENIOR_DE_INTERVIEW_DRILLS: List[Dict[str, Any]] = [
    # 1. PYTHON
    {
        "id": "drill_py_01",
        "domain": "Python",
        "topic": "Memory-Efficient 10GB Dataset Ingestion & Chunking",
        "scenario": "A core banking batch dumps a 10GB raw CSV transaction file daily. The ingestion worker runs in an AWS ECS container with a strict 4GB RAM limit. Loading the file with standard `pd.read_csv()` triggers an Out-Of-Memory (OOM) fatal kill.",
        "question": "How do you ingest, validate, and compute customer-level moving aggregates on a 10GB CSV without exceeding 4GB RAM in Python?",
        "solution_type": "Python Code",
        "solution": (
            "import pandas as pd\n\n"
            "def stream_and_aggregate(csv_path: str, chunk_size: int = 100_000):\n"
            "    # Downcast datatypes to save up to 75% memory footprint\n"
            "    dtypes = {'acct_id': 'int32', 'amount': 'float32', 'txn_type': 'category'}\n"
            "    running_totals = {}\n"
            "    for chunk in pd.read_csv(csv_path, chunksize=chunk_size, dtype=dtypes, usecols=['acct_id', 'amount', 'txn_type']):\n"
            "        # Filter and group directly in chunk memory\n"
            "        grouped = chunk.groupby('acct_id')['amount'].agg(['count', 'sum'])\n"
            "        for acct, row in grouped.iterrows():\n"
            "            if acct not in running_totals:\n"
            "                running_totals[acct] = {'count': 0, 'sum': 0.0}\n"
            "            running_totals[acct]['count'] += row['count']\n"
            "            running_totals[acct]['sum'] += row['sum']\n"
            "    return running_totals"
        ),
        "interviewer_tip": "Interviewers look for chunked generator streaming (`chunksize`), memory downcasting (`float32`, `int32`), `category` dtype for low-cardinality strings, and memory profiling rather than loading everything into a single DataFrame."
    },

    # 2. AWS
    {
        "id": "drill_aws_01",
        "domain": "AWS",
        "topic": "S3 Data Lake Partitioning & Athena Scan Cost Optimization",
        "scenario": "A fintech application uploads 50 million transaction events per day to an AWS S3 bucket. Analysts running Athena queries complain that queries take 8 minutes and Athena scan costs have skyrocketed because every query does a full bucket scan.",
        "question": "How do you architect the S3 folder hierarchy and file compaction strategy to slash Athena scan costs and achieve sub-10 second queries?",
        "solution_type": "AWS Architecture & Hive Partitioning",
        "solution": (
            "# 1. Implement Hive-style partition layout in S3:\n"
            "s3://bank-lakehouse/transactions/year=2026/month=10/day=12/country=IN/data.parquet\n\n"
            "# 2. Convert raw JSON files to Apache Parquet with Snappy compression & dictionary encoding\n"
            "# 3. Run AWS Glue Crawler or explicit MSCK REPAIR TABLE / Partition Projection\n\n"
            "-- 4. Athena query with partition pruning:\n"
            "SELECT acct_id, SUM(amount) AS total_inflow\n"
            "FROM bank_lakehouse.transactions\n"
            "WHERE year = 2026 AND month = 10 AND day = 12\n"
            "GROUP BY acct_id;"
        ),
        "interviewer_tip": "Highlight: Parquet columnar format with column projection (Athena only reads queried columns) + Hive directory partitioning (prunes 99% of unneeded folders) + partition projection to skip Glue metastore catalog lookups entirely."
    },

    # 3. SNOWFLAKE
    {
        "id": "drill_sf_01",
        "domain": "Snowflake",
        "topic": "Dynamic Tables vs Streams & Tasks for Real-Time Lakehouse",
        "scenario": "Your banking architecture requires near real-time ingestion from raw Bronze staging (L0) into an SCD Type-2 Silver layer (L1) with a strict target latency of 1 minute.",
        "question": "When should you choose Snowflake Dynamic Tables over Streams & Tasks, and how do you handle lag thresholds?",
        "solution_type": "Snowflake SQL DDL",
        "solution": (
            "CREATE OR REPLACE DYNAMIC TABLE bank_db.silver.l1_customer_txns_dynamic\n"
            "TARGET_LAG = '1 minute'\n"
            "WAREHOUSE = 'ETL_WH'\n"
            "AS\n"
            "SELECT \n"
            "    txn_id,\n"
            "    account_no,\n"
            "    amount,\n"
            "    txn_timestamp,\n"
            "    CURRENT_TIMESTAMP() AS l1_ingestion_ts\n"
            "FROM bank_db.raw_staging.l0_transactions_raw\n"
            "WHERE amount IS NOT NULL AND account_no IS NOT NULL;"
        ),
        "interviewer_tip": "Dynamic Tables are declarative and automatically construct the DAG and refresh schedule based on `TARGET_LAG`. Streams & Tasks are imperative (best for complex procedural branching or calling external APIs). For pure continuous data transformation, Dynamic Tables minimize maintenance overhead."
    },

    # 4. SQL
    {
        "id": "drill_sql_01",
        "domain": "SQL",
        "topic": "Deduplication & QUALIFY Clause in Modern Cloud Warehouses",
        "scenario": "A distributed CDC feeder pushes duplicate messages for the same transaction into the staging table due to network retry policies. Each record has `txn_id`, `account_no`, `amount`, and `event_timestamp`.",
        "question": "Write an optimized SQL query to retain only the single most recent transaction per account without writing a subquery or self-join.",
        "solution_type": "Vectorized SQL",
        "solution": (
            "SELECT \n"
            "    txn_id,\n"
            "    account_no,\n"
            "    amount,\n"
            "    event_timestamp\n"
            "FROM bank_db.raw_staging.l0_transactions\n"
            "QUALIFY ROW_NUMBER() OVER (\n"
            "    PARTITION BY account_no \n"
            "    ORDER BY event_timestamp DESC, txn_id DESC\n"
            ") = 1;"
        ),
        "interviewer_tip": "The `QUALIFY` clause is supported in Snowflake, BigQuery, and Databricks. It filters results of window functions in the same execution pass, eliminating the need for wrapping the query in `WITH cte AS (...) SELECT * FROM cte WHERE rn = 1`."
    },

    # 5. DATA PIPELINE
    {
        "id": "drill_pipe_01",
        "domain": "Data Pipeline",
        "topic": "Idempotent Pipeline Architecture & Zero-Loss Replayability",
        "scenario": "A network interruption occurs at 04:30 AM halfway through a 3-hour nightly ETL batch. The scheduler re-triggers the job from the beginning.",
        "question": "How do you guarantee idempotency so that re-running the failed job never creates duplicate ledger records or corrupted financial balances?",
        "solution_type": "Idempotent Architecture Design",
        "solution": (
            "# 1. Deterministic Hash Primary Key:\n"
            "record_hash = SHA256(txn_id + account_no + txn_date + amount)\n\n"
            "# 2. Atomic Staging Partition Replacement:\n"
            "# Write output to temporary stage, then swap partition atomically:\n"
            "INSERT OVERWRITE INTO target_partition\n"
            "SELECT ... FROM stage_partition;\n\n"
            "# 3. MERGE with Match Conditions (UPSERT):\n"
            "MERGE INTO target_table t\n"
            "USING staged_batch s\n"
            "ON t.record_hash = s.record_hash\n"
            "WHEN MATCHED AND s.updated_at > t.updated_at THEN UPDATE ...\n"
            "WHEN NOT MATCHED THEN INSERT ...;"
        ),
        "interviewer_tip": "Explain that idempotency means `f(f(x)) = f(x)`. Key techniques: deterministic hash keys, partition overwriting rather than appending, and atomic transactions with automated pre-commit validation checks."
    },

    # 6. ETL
    {
        "id": "drill_etl_01",
        "domain": "ETL",
        "topic": "Dead-Letter Queue (DLQ) & Schema Drift Quarantine Gate",
        "scenario": "An upstream source system abruptly renames column `customer_ssn` to `cust_tax_id` and introduces string values into a numeric `amount` column, threatening to break all downstream banking reports.",
        "question": "How do you design a resilient ETL ingestion gate that routes invalid records to a quarantine table without halting the pipeline for valid records?",
        "solution_type": "Data Quality Quarantine Pattern",
        "solution": (
            "-- Snowflake / Spark Data Quality Assertion Pattern:\n"
            "INSERT ALL\n"
            "  -- Valid records pass to Silver\n"
            "  WHEN TRY_TO_DECIMAL(amount_raw, 18, 2) IS NOT NULL AND LENGTH(account_raw) = 10 THEN\n"
            "    INTO bank_db.silver.valid_transactions\n"
            "    VALUES (txn_id, account_raw, CAST(amount_raw AS DECIMAL(18,2)), event_time)\n"
            "  -- Corrupted records diverted to Quarantine Gate\n"
            "  ELSE\n"
            "    INTO bank_db.quarantine.invalid_payload_dlq\n"
            "    VALUES (txn_id, raw_payload, 'INVALID_AMOUNT_OR_ACCT_LEN', CURRENT_TIMESTAMP());"
        ),
        "interviewer_tip": "Never allow a pipeline to fail silently or crash the entire day's batch because of a 0.01% corrupted record rate. Split streams at the ingestion gate: valid records move to Silver, invalid records route to a DLQ with an error audit code."
    },

    # 7. PYTHON (PySpark)
    {
        "id": "drill_py_02",
        "domain": "Python",
        "topic": "PySpark Data Skew & Salting Technique in Heavy Joins",
        "scenario": "You are joining a 2-billion row transaction table with a 50-million row customer table on `customer_id`. The Spark job hangs indefinitely at 99% because 40% of all transactions belong to a single dummy corporate account `ID=999999` (severe data skew).",
        "question": "How do you resolve this join skew in PySpark without dropping the records?",
        "solution_type": "PySpark Salting Code",
        "solution": (
            "from pyspark.sql import functions as F\n\n"
            "# 1. Salt the skewed large table with a random integer (0 to 19)\n"
            "SALT_BUCKETS = 20\n"
            "df_txns_salted = df_txns.withColumn('salt', F.floor(F.rand() * SALT_BUCKETS))\n"
            "df_txns_salted = df_txns_salted.withColumn('salted_key', F.concat(F.col('customer_id'), F.lit('_'), F.col('salt')))\n\n"
            "# 2. Explode the smaller dimension table across all salt buckets\n"
            "df_cust_replicated = df_cust.withColumn('salt_array', F.array([F.lit(i) for i in range(SALT_BUCKETS)]))\n"
            "df_cust_exploded = df_cust_replicated.withColumn('salt', F.explode('salt_array'))\n"
            "df_cust_exploded = df_cust_exploded.withColumn('salted_key', F.concat(F.col('customer_id'), F.lit('_'), F.col('salt')))\n\n"
            "# 3. Execute uniform join across all executor cores\n"
            "df_joined = df_txns_salted.join(df_cust_exploded, 'salted_key', 'inner')"
        ),
        "interviewer_tip": "Data skew causes one Spark task to process gigabytes while all other executors sit idle waiting. Salting distributes the hot key evenly across multiple worker partitions."
    },

    # 8. AWS
    {
        "id": "drill_aws_02",
        "domain": "AWS",
        "topic": "AWS Glue DynamicFrame vs Spark DataFrame in Lakehouse ETL",
        "scenario": "An enterprise migration ingests inconsistent JSON data from 20 different bank branches where schema fields change dynamically across files.",
        "question": "Why would an engineer use AWS Glue `DynamicFrame` instead of a standard Spark `DataFrame` for this ingestion workload?",
        "solution_type": "AWS Glue Concept & Code",
        "solution": (
            "# Glue DynamicFrame allows nested schema variation without failing:\n"
            "from awsglue.context import GlueContext\n"
            "from awsglue.dynamicframe import DynamicFrame\n"
            "from pyspark.context import SparkContext\n\n"
            "glueContext = GlueContext(SparkContext.getOrCreate())\n"
            "dyn_frame = glueContext.create_dynamic_frame.from_options(\n"
            "    connection_type='s3',\n"
            "    connection_options={'paths': ['s3://bank-raw/branch_feeds/']},\n"
            "    format='json'\n"
            ")\n"
            "# Resolve schema ambiguities (e.g. choice type cast)\n"
            "resolved_df = dyn_frame.resolveChoice(specs=[('balance', 'cast:double')])"
        ),
        "interviewer_tip": "Spark DataFrames enforce a rigid global schema upfront on the entire dataset. Glue DynamicFrames handle schema variability per-record, resolving choice types (e.g. string vs integer in the same column) without schema errors."
    },

    # 9. SNOWFLAKE
    {
        "id": "drill_sf_02",
        "domain": "Snowflake",
        "topic": "Zero-Copy Cloning & Time Travel for Dev/Test Staging",
        "scenario": "A developer wants to test a destructive schema refactoring and migration script on an active 50TB production Snowflake database without incurring additional storage costs or affecting production queries.",
        "question": "How do you instantly provision a 50TB test database in Snowflake and restore historical data from 3 days ago?",
        "solution_type": "Snowflake DDL",
        "solution": (
            "-- 1. Instant zero-copy clone (0 additional storage cost, metadata pointer copy only):\n"
            "CREATE OR REPLACE DATABASE bank_db_dev_clone CLONE bank_db_prod;\n\n"
            "-- 2. Time Travel query to retrieve table state exactly 3 days ago:\n"
            "SELECT * \n"
            "FROM bank_db_prod.silver.customer_master \n"
            "AT(TIMESTAMP => DATEADD('day', -3, CURRENT_TIMESTAMP()));\n\n"
            "-- 3. Clone table state as of a specific query ID before a flawed batch:\n"
            "CREATE OR REPLACE TABLE restored_orders CLONE raw_orders\n"
            "BEFORE(STATEMENT => '01b2c45e-0001-2a4b-0000-000123456789');"
        ),
        "interviewer_tip": "Zero-Copy Clone copies metadata pointers to micro-partitions without duplicating storage bytes. Time Travel (up to 90 days on Enterprise edition) allows point-in-time recovery using timestamps, offsets, or query IDs."
    },

    # 10. SQL
    {
        "id": "drill_sql_02",
        "domain": "SQL",
        "topic": "Cumulative Running Balances with Window Frames",
        "scenario": "In a core banking system, you need to calculate each customer's running balance after every deposit and withdrawal, while properly handling multiple transactions occurring on the exact same millisecond.",
        "question": "Write the SQL query to calculate running customer balances using window frames and explain `ROWS BETWEEN` vs `RANGE BETWEEN`.",
        "solution_type": "Window Frame SQL",
        "solution": (
            "SELECT \n"
            "    account_id,\n"
            "    txn_id,\n"
            "    txn_date,\n"
            "    amount,\n"
            "    SUM(amount) OVER (\n"
            "        PARTITION BY account_id \n"
            "        ORDER BY txn_date, txn_id\n"
            "        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW\n"
            "    ) AS running_account_balance\n"
            "FROM bank_db.silver.account_transactions\n"
            "ORDER BY account_id, txn_date;"
        ),
        "interviewer_tip": "`ROWS BETWEEN` operates on physical row offsets and computes a discrete running sum even if timestamps match. `RANGE BETWEEN` operates on logical values, grouping identical timestamps together and potentially producing unexpected jumps."
    },

    # 11. DATA PIPELINE
    {
        "id": "drill_pipe_02",
        "domain": "Data Pipeline",
        "topic": "SCD Type-2 (Slowly Changing Dimensions) Implementation",
        "scenario": "A customer changes their residential address from Mumbai to Pune. All transactions prior to the move must reflect Mumbai, while new transactions must reflect Pune.",
        "question": "How do you design an SCD Type-2 dimension table in SQL and write the MERGE statement to track historical validity?",
        "solution_type": "SCD Type 2 SQL MERGE",
        "solution": (
            "-- Target Schema: cust_sk, cust_id, address, start_date, end_date, is_current\n"
            "MERGE INTO dim_customer t\n"
            "USING (\n"
            "    SELECT cust_id, address, CURRENT_DATE() AS eff_date FROM stage_customer\n"
            ") s\n"
            "ON t.cust_id = s.cust_id AND t.is_current = 'Y'\n"
            "-- Close out old record\n"
            "WHEN MATCHED AND t.address <> s.address THEN\n"
            "    UPDATE SET t.end_date = CURRENT_DATE() - 1, t.is_current = 'N';\n\n"
            "-- Insert new current record\n"
            "INSERT INTO dim_customer (cust_sk, cust_id, address, start_date, end_date, is_current)\n"
            "SELECT MD5(s.cust_id || s.eff_date), s.cust_id, s.address, s.eff_date, '9999-12-31', 'Y'\n"
            "FROM stage_customer s;"
        ),
        "interviewer_tip": "SCD Type 2 preserves historical state by adding new rows with `start_date`, `end_date`, and `is_current` flag. SCD Type 1 simply overwrites data with no history."
    },

    # 12. ETL
    {
        "id": "drill_etl_02",
        "domain": "ETL",
        "topic": "Oracle LogMiner CDC Ingestion Architecture",
        "scenario": "A legacy Oracle 19c database handles 10,000 transactions per second. Direct SQL polling `SELECT * FROM tbl WHERE last_updated > ?` causes high CPU locking and database timeouts.",
        "question": "How do you implement non-invasive real-time Change Data Capture (CDC) from Oracle into an AWS S3/Snowflake Lakehouse?",
        "solution_type": "CDC Architecture & Config",
        "solution": (
            "# 1. Enable Supplemental Logging on Oracle:\n"
            "ALTER DATABASE ADD SUPPLEMENTAL LOG DATA;\n"
            "ALTER TABLE transactions ADD SUPPLEMENTAL LOG DATA (ALL) COLUMNS;\n\n"
            "# 2. Stream redo logs asynchronously using Debezium / AWS DMS / Oracle LogMiner:\n"
            "# Reads binary redo log files (.dbf / archivelog) from disk without issuing SQL queries on tables.\n"
            "# 3. Stream change events (INSERT, UPDATE, DELETE) into Apache Kafka / Kinesis.\n"
            "# 4. Micro-batch sink into S3 Parquet landing, then merge into Snowflake L0 Bronze."
        ),
        "interviewer_tip": "Log-based CDC is zero-impact because it parses the binary transaction write-ahead log (WAL / Redo log) rather than running querying locks on table storage."
    },

    # 13. SQL (Recursive CTE)
    {
        "id": "drill_sql_03",
        "domain": "SQL",
        "topic": "Recursive CTE for Core Banking Branch & Subsidiary Rollup",
        "scenario": "A conglomerate bank has a 6-tier corporate structure (Holding Co -> Bank -> Regional Zones -> State Circles -> City Branches). You need to calculate total deposits rolled up to every parent node.",
        "question": "Write a recursive SQL CTE to traverse the parent-child hierarchy and compute aggregate branch deposits up to the root level.",
        "solution_type": "Recursive SQL CTE",
        "solution": (
            "WITH RECURSIVE branch_hierarchy AS (\n"
            "    -- Anchor member: Leaf branches\n"
            "    SELECT branch_id, parent_branch_id, branch_name, branch_deposit, 1 AS depth\n"
            "    FROM bank_branches\n"
            "    WHERE parent_branch_id IS NOT NULL\n"
            "    UNION ALL\n"
            "    -- Recursive member: Traverse upwards\n"
            "    SELECT b.branch_id, b.parent_branch_id, b.branch_name, bh.branch_deposit, bh.depth + 1\n"
            "    FROM bank_branches b\n"
            "    INNER JOIN branch_hierarchy bh ON b.branch_id = bh.parent_branch_id\n"
            ")\n"
            "SELECT branch_id, branch_name, SUM(branch_deposit) AS total_rolled_up_deposits\n"
            "FROM branch_hierarchy\n"
            "GROUP BY branch_id, branch_name\n"
            "ORDER BY total_rolled_up_deposits DESC;"
        ),
        "interviewer_tip": "Explain the two parts of a Recursive CTE: the Anchor Query (initial dataset) and the Recursive Query (joined with the CTE itself). Mention `CYCLE` detection or `MAXRECURSION` limit to avoid infinite loops."
    },

    # 14. PYTHON (Polars vs Pandas)
    {
        "id": "drill_py_03",
        "domain": "Python",
        "topic": "Polars LazyFrame vs Pandas for 50GB Lakehouse Parquet Queries",
        "scenario": "A data engineer runs aggregations on a 50GB Parquet file stored on NVMe disk. Pandas consumes 64GB of RAM and crashes with memory swapping. The job needs to run under 8GB RAM in under 15 seconds.",
        "question": "How do you rewrite the pipeline using Polars LazyFrames and streaming engine to maximize throughput with minimal RAM?",
        "solution_type": "Polars Vectorized Lazy Pipeline",
        "solution": (
            "import polars as pl\n\n"
            "# 1. Scan lazily without reading data into memory upfront\n"
            "lazy_df = pl.scan_parquet('s3_or_local/lakehouse_50gb/*.parquet')\n\n"
            "# 2. Build declarative transform query plan (predicate & projection pushdown)\n"
            "query = (\n"
            "    lazy_df\n"
            "    .filter(pl.col('txn_date') >= '2026-10-01')\n"
            "    .filter(pl.col('status') == 'SETTLED')\n"
            "    .group_by(['branch_code', 'account_type'])\n"
            "    .agg([\n"
            "        pl.col('amount').sum().alias('total_turnover'),\n"
            "        pl.col('amount').mean().alias('avg_ticket_size'),\n"
            "        pl.col('txn_id').count().alias('txn_count')\n"
            "    ])\n"
            "    .sort('total_turnover', descending=True)\n"
            ")\n\n"
            "# 3. Execute with streaming engine in Rust-backed multi-threaded chunks\n"
            "result_df = query.collect(streaming=True)\n"
            "print(result_df.head(10))"
        ),
        "interviewer_tip": "Polars uses Rust with Apache Arrow memory format, enabling SIMD vectorization, predicate pushdown (reading only matching row groups), projection pushdown (reading only required columns), and streaming execution without loading whole datasets into memory."
    },

    # 15. SNOWFLAKE (Search Optimization & Clustering)
    {
        "id": "drill_sf_03",
        "domain": "Snowflake",
        "topic": "Search Optimization Service vs Clustering Keys for Point Lookups",
        "scenario": "A 10-billion row credit card authorizations table in Snowflake takes 25 seconds for needle-in-a-haystack lookups like `WHERE card_hash = '8a9f...'`. Business SLA requires sub-500ms responses for customer fraud inquiries.",
        "question": "Compare Search Optimization Service (SOS) vs Clustering Keys and demonstrate how to configure SOS for instant point lookups.",
        "solution_type": "Snowflake SOS Configuration",
        "solution": (
            "-- 1. Enable Search Optimization Service on specific high-cardinality columns:\n"
            "ALTER TABLE bank_db.raw_staging.credit_authorizations\n"
            "ADD SEARCH OPTIMIZATION ON EQUALITY(card_hash, authorization_code, terminal_id);\n\n"
            "-- 2. Verify search access paths built in background by serverless maintenance:\n"
            "DESCRIBE SEARCH OPTIMIZATION ON bank_db.raw_staging.credit_authorizations;\n\n"
            "-- 3. Query executed in < 400ms (skips 99.9% of micro-partitions via SOS index structure):\n"
            "SELECT * \n"
            "FROM bank_db.raw_staging.credit_authorizations\n"
            "WHERE card_hash = '8a9f20c198b3e5a4d1e2f3a4b5c6d7e8'\n"
            "LIMIT 1;"
        ),
        "interviewer_tip": "Clustering keys re-order physical micro-partitions on disk (best for range scans, date ranges, and joins on 1-3 keys). Search Optimization builds an auxiliary persistent search access path (best for selective point equality lookups, substring LIKE '%abc%', and IP queries on high-cardinality tables)."
    },

    # 16. ORACLE (Vectorized Bulk Collect & FORALL)
    {
        "id": "drill_ora_01",
        "domain": "Oracle",
        "topic": "PL/SQL Vectorized Bulk Collect & FORALL for 10M Row Batches",
        "scenario": "An Oracle 19c / 21c batch job processing daily NEFT clearances takes 4 hours because it loops row-by-row using `FOR r IN cur LOOP INSERT ... END LOOP;` (excessive context switching between PL/SQL and SQL engines).",
        "question": "How do you vectorize this Oracle batch using `BULK COLLECT` and `FORALL` with `SAVE EXCEPTIONS` to complete in under 5 minutes?",
        "solution_type": "Oracle PL/SQL Vectorization",
        "solution": (
            "DECLARE\n"
            "    TYPE t_clearance_batch IS TABLE OF neft_inward_staging%ROWTYPE;\n"
            "    l_batch t_clearance_batch;\n"
            "    CURSOR c_txns IS SELECT * FROM neft_inward_staging WHERE status = 'PENDING';\n"
            "BEGIN\n"
            "    OPEN c_txns;\n"
            "    LOOP\n"
            "        -- Fetch in 10,000-row arrays to eliminate context switches\n"
            "        FETCH c_txns BULK COLLECT INTO l_batch LIMIT 10000;\n"
            "        EXIT WHEN l_batch.COUNT = 0;\n\n"
            "        -- Vectorized bulk insert with exception tracking\n"
            "        FORALL i IN 1..l_batch.COUNT SAVE EXCEPTIONS\n"
            "            INSERT INTO neft_cleared_journal VALUES l_batch(i);\n\n"
            "        COMMIT;\n"
            "    END LOOP;\n"
            "    CLOSE c_txns;\n"
            "END;"
        ),
        "interviewer_tip": "Row-by-row processing in Oracle causes millions of context switches between the PL/SQL runtime and the SQL execution engine. `BULK COLLECT LIMIT N` loads array memory chunks, and `FORALL` sends the entire array to the SQL engine in a single system call."
    },

    # 17. SQL (AML Velocity Spikes)
    {
        "id": "drill_sql_04",
        "domain": "SQL",
        "topic": "AML Transaction Velocity & Rapid Movement of Funds",
        "scenario": "Regulatory surveillance requires detecting accounts that receive funds and transfer out more than 90% of the deposit within 15 minutes across 3 consecutive cycles (mule account pattern).",
        "question": "Write an advanced window function query using `LEAD` and timestamp diffing to detect rapid transfer sequences.",
        "solution_type": "SQL Window Analytics",
        "solution": (
            "WITH txn_pairs AS (\n"
            "    SELECT \n"
            "        account_id,\n"
            "        txn_id,\n"
            "        txn_type,\n"
            "        amount,\n"
            "        txn_timestamp,\n"
            "        LEAD(txn_type) OVER (PARTITION BY account_id ORDER BY txn_timestamp) AS next_type,\n"
            "        LEAD(amount) OVER (PARTITION BY account_id ORDER BY txn_timestamp) AS next_amount,\n"
            "        LEAD(txn_timestamp) OVER (PARTITION BY account_id ORDER BY txn_timestamp) AS next_time\n"
            "    FROM bank_db.silver.transactions_feed\n"
            ")\n"
            "SELECT \n"
            "    account_id,\n"
            "    txn_id AS credit_txn,\n"
            "    amount AS deposit_inflow,\n"
            "    next_amount AS rapid_outflow,\n"
            "    TIMESTAMPDIFF(MINUTE, txn_timestamp, next_time) AS duration_mins\n"
            "FROM txn_pairs\n"
            "WHERE txn_type = 'CREDIT' AND next_type = 'DEBIT'\n"
            "  AND TIMESTAMPDIFF(MINUTE, txn_timestamp, next_time) <= 15\n"
            "  AND next_amount >= (amount * 0.90)\n"
            "ORDER BY duration_mins ASC;"
        ),
        "interviewer_tip": "This tests pattern detection over time-series data. Point out that `LEAD()` allows comparing adjacent events without self-joins, preserving linear $O(N)$ scanning complexity."
    },

    # 18. PYTHON (Connection Pooling & Backpressure)
    {
        "id": "drill_py_04",
        "domain": "Python",
        "topic": "Thread-Safe Database Connection Pool with Backpressure Queue",
        "scenario": "A high-frequency ingest worker spawns 200 concurrent threads to push data into a database, but the database allows a maximum of 20 concurrent connections. Direct thread execution causes connection exhaustion.",
        "question": "Implement a thread-safe connection pool using Python `queue.Queue` with timeout and context manager acquisition.",
        "solution_type": "Thread-Safe Connection Pool",
        "solution": (
            "import queue\n"
            "import sqlite3\n"
            "from contextlib import contextmanager\n\n"
            "class DatabasePool:\n"
            "    def __init__(self, db_path: str, max_connections: int = 20):\n"
            "        self.db_path = db_path\n"
            "        self.pool = queue.Queue(maxsize=max_connections)\n"
            "        for _ in range(max_connections):\n"
            "            conn = sqlite3.connect(db_path, check_same_thread=False)\n"
            "            self.pool.put(conn)\n\n"
            "    @contextmanager\n"
            "    def get_connection(self, timeout: float = 5.0):\n"
            "        # Acquire connection with backpressure timeout\n"
            "        conn = self.pool.get(timeout=timeout)\n"
            "        try:\n"
            "            yield conn\n"
            "        finally:\n"
            "            # Release back to pool\n"
            "            self.pool.put(conn)\n\n"
            "# Usage:\n"
            "# db_pool = DatabasePool('app/database/studio_memory.db', max_connections=20)\n"
            "# with db_pool.get_connection() as conn:\n"
            "#     conn.execute('SELECT 1')"
        ),
        "interviewer_tip": "Focus on the context manager (`@contextmanager`), `queue.Queue` blocking semantics with timeouts, and guaranteeing connection return inside the `finally` block even when exceptions occur."
    },

    # 19. POSTGRESQL (EXPLAIN ANALYZE & JSONB GIN)
    {
        "id": "drill_pg_01",
        "domain": "PostgreSQL",
        "topic": "PostgreSQL EXPLAIN ANALYZE Optimization with GIN Indexes on JSONB",
        "scenario": "A fintech core saves flexible webhook payloads in a PostgreSQL `payload JSONB` column. Queries filtering by `payload->>'merchant_mcc'` take 14 seconds on a 5-million row table.",
        "question": "How do you analyze the query plan with `EXPLAIN (ANALYZE, BUFFERS)` and design a GIN index to bring query latency down to under 5ms?",
        "solution_type": "Postgres Indexing & Plan Tuning",
        "solution": (
            "-- 1. Inspect physical disk hits vs shared memory cache hits:\n"
            "EXPLAIN (ANALYZE, BUFFERS, VERBOSE)\n"
            "SELECT * FROM webhooks_raw\n"
            "WHERE payload @> '{\"merchant_mcc\": \"5411\"}';\n\n"
            "-- 2. Build Generalized Inverted Index (GIN) using jsonb_path_ops for compact fast lookup:\n"
            "CREATE INDEX idx_webhooks_payload_gin ON webhooks_raw\n"
            "USING GIN (payload jsonb_path_ops);\n\n"
            "-- 3. Query rewritten to leverage GIN index (@> containment operator):\n"
            "SELECT id, received_at, payload\n"
            "FROM webhooks_raw\n"
            "WHERE payload @> '{\"merchant_mcc\": \"5411\"}'::jsonb\n"
            "LIMIT 50;"
        ),
        "interviewer_tip": "The `jsonb_path_ops` operator class creates a hash of path and value, resulting in smaller index size and up to 3x faster point lookups compared to the default `jsonb_ops` index."
    },

    # 20. AWS / LAKEHOUSE (Iceberg Metadata & Compaction)
    {
        "id": "drill_aws_03",
        "domain": "AWS",
        "topic": "Apache Iceberg Small Files Compaction & Metadata Snapshots",
        "scenario": "A streaming Kafka sink ingests events into an Apache Iceberg table on AWS S3 every 10 seconds. Over 3 months, 800,000 tiny 50KB Parquet files have accumulated. Query planners timeout due to metadata explosion.",
        "question": "How do you schedule compaction and snapshot expiration to restore sub-second query performance?",
        "solution_type": "Iceberg Table Maintenance",
        "solution": (
            "# PySpark / AWS EMR Maintenance Job:\n"
            "from pyspark.sql import SparkSession\n\n"
            "spark = SparkSession.builder.appName('IcebergMaintenance').getOrCreate()\n\n"
            "# 1. Rewrite data files into optimal 128MB or 256MB Parquet target file size:\n"
            "spark.sql(\"\"\"\n"
            "    CALL bank_catalog.system.rewrite_data_files(\n"
            "        table => 'lakehouse_silver.transactions',\n"
            "        strategy => 'binpack',\n"
            "        options => map('target-file-size-bytes', '134217728') -- 128 MB\n"
            "    )\n"
            "\"\"\")\n\n"
            "# 2. Expire old snapshots and remove orphan metadata files older than 7 days:\n"
            "spark.sql(\"\"\"\n"
            "    CALL bank_catalog.system.expire_snapshots(\n"
            "        table => 'lakehouse_silver.transactions',\n"
            "        older_than => TIMESTAMP '2026-10-05 00:00:00',\n"
            "        retain_last => 5\n"
            "    )\n"
            "\"\"\")"
        ),
        "interviewer_tip": "Streaming ingestion inevitably creates the 'small file problem'. Iceberg solves this natively with `rewrite_data_files` (combines small files into 128MB blocks without locking readers) and `expire_snapshots` (cleans orphan metadata files in S3)."
    }
]


class InterviewDrillsEngine:
    def __init__(self):
        self._ensure_state()

    def _ensure_state(self):
        if not DRILLS_STATE_FILE.exists():
            init_data = {"last_index": 0, "total_dispatched": 0, "last_updated": time.time()}
            DRILLS_STATE_FILE.write_text(json.dumps(init_data, indent=2), encoding="utf-8")

    def get_next_interview_drill(self) -> Dict[str, Any]:
        """
        Retrieves the next scenario in the rotating queue.
        Guarantees that every dispatch yields a different question across
        Python, AWS, Snowflake, SQL, Data Pipelines, and ETL.
        """
        try:
            state = json.loads(DRILLS_STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            state = {"last_index": 0, "total_dispatched": 0}

        idx = state.get("last_index", 0)
        drill = SENIOR_DE_INTERVIEW_DRILLS[idx % len(SENIOR_DE_INTERVIEW_DRILLS)]

        # Increment pointer for next time
        next_idx = (idx + 1) % len(SENIOR_DE_INTERVIEW_DRILLS)
        state["last_index"] = next_idx
        state["total_dispatched"] = state.get("total_dispatched", 0) + 1
        state["last_updated"] = time.time()
        DRILLS_STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

        log_event(f"InterviewDrillsEngine: Dispatched drill #{idx+1} ({drill['domain']} - {drill['topic']})", component="InterviewEngine")
        return drill

    def format_telegram_drill(self, drill: Optional[Dict[str, Any]] = None) -> str:
        """
        Formats a high-yield technical interview drill into an attractive Telegram card.
        """
        if not drill:
            drill = self.get_next_interview_drill()

        domain_emojis = {
            "Python": "🐍",
            "AWS": "☁️",
            "Snowflake": "❄️",
            "SQL": "🗄️",
            "Data Pipeline": "🏛️",
            "ETL": "⚡"
        }
        emoji = domain_emojis.get(drill["domain"], "💡")

        msg = (
            f"{emoji} <b>SENIOR DATA ENGINEER INTERVIEW DRILL</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Domain:</b> <code>{drill['domain'].upper()}</code> | <b>Topic:</b> {drill['topic']}\n\n"
            f"🏢 <b>Real-World Scenario:</b>\n"
            f"<i>{drill['scenario']}</i>\n\n"
            f"❓ <b>Interview Question:</b>\n"
            f"<b>{drill['question']}</b>\n\n"
            f"🛠️ <b>Production Solution ({drill['solution_type']}):</b>\n"
            f"<pre>{drill['solution']}</pre>\n\n"
            f"💡 <b>Interviewer Evaluation Tip:</b>\n"
            f"<i>{drill['interviewer_tip']}</i>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 <i>NanoPro AI Studio • Automated Technical Career Accelerator</i>"
        )
        return msg


interview_drills_engine = InterviewDrillsEngine()
