"""
Mangesh Nano Pro AI Studio - Central Agent Registry
Defines and registers 205 Specialized Enterprise AI Agents across 13 operational branches:
Group A: Core Cognitive & Orchestration (Agents 1-15)
Group B: Advanced Data Engineering, ETL/ELT & Stream Processing (Agents 16-35)
Group C: Snowflake, Oracle XE & Cloud Warehouses (Agents 36-55)
Group D: Data Quality, Governance, Observability & Lineage (Agents 56-70)
Group E: AWS DMS & Database Migration (Agents 71-85)
Group F: Data Analytics, BI, Executive Dashboards & Profiling (Agents 86-105)
Group G: AI, Deep Learning, LLM Training & MLOps (Agents 106-125)
Group H: Cybersecurity, Threat Intel, Vault & IAM Security (Agents 126-140)
Group I: Cloud Infrastructure, SRE & DevSecOps (Agents 141-155)
Group J: Career, MNC HR Outreach & Job Hunting (Agents 156-170)
Group K: Multi-Channel Communications (Telegram / WhatsApp / Email) (Agents 171-185)
Group L: Autonomous Task Schedulers, Crons & Recovery (Agents 186-195)
Group M: Daily Lifestyle, Tech News, Entertainment & Personal Ambience (Agents 196-205)

Each agent has clearly defined responsibilities, permitted tools (including verified free web APIs),
execution state machine, assigned AI models, resource tracking, and operational metrics.
"""

import time
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import db

AGENT_STATES = [
    "Idle", "Ready", "Assigned", "Running",
    "Waiting for Dependency", "Waiting for Approval",
    "Retrying", "Blocked", "Failed", "Completed", "Paused"
]

class SpecializedAgent:
    def __init__(
        self,
        agent_id: str,
        name: str,
        group: str,
        group_name: str,
        role: str,
        description: str,
        permitted_tools: List[str],
        default_model: str = "qwen2.5-coder:7b",
        icon: str = "robot"
    ):
        self.agent_id = agent_id
        self.name = name
        self.group = group
        self.group_name = group_name
        self.role = role
        self.description = description
        self.permitted_tools = permitted_tools
        self.default_model = default_model
        self.icon = icon

        # Dynamic State
        self.current_state = "Idle"
        self.current_task = ""
        self.task_start_time = 0.0
        self.last_activity_time = time.time()
        self.progress_pct = 0
        self.waiting_for = ""
        self.last_error = None
        self.successful_tasks_count = 0
        self.failed_tasks_count = 0
        self.total_execution_seconds = 0.0

    def assign_task(self, task_name: str, task_id: Optional[str] = None):
        self.current_state = "Assigned"
        self.current_task = task_name
        self.task_start_time = time.time()
        self.last_activity_time = time.time()
        self.progress_pct = 0
        self.waiting_for = ""
        self.last_error = None
        log_event(f"Agent [{self.name}] assigned task: '{task_name}'", component="AgentRegistry")

    def set_running(self, progress: int = 10):
        self.current_state = "Running"
        self.progress_pct = progress
        self.last_activity_time = time.time()

    def set_waiting(self, dependency_or_approval: str, is_approval: bool = False):
        self.current_state = "Waiting for Approval" if is_approval else "Waiting for Dependency"
        self.waiting_for = dependency_or_approval
        self.last_activity_time = time.time()
        log_event(f"Agent [{self.name}] {self.current_state}: {dependency_or_approval}", component="AgentRegistry")

    def complete_task(self, result_summary: str = "Task completed"):
        duration = time.time() - self.task_start_time if self.task_start_time > 0 else 0.0
        self.total_execution_seconds += duration
        self.successful_tasks_count += 1
        self.current_state = "Completed"
        self.progress_pct = 100
        self.last_activity_time = time.time()
        log_event(f"Agent [{self.name}] completed task in {duration:.2f}s: {result_summary}", component="AgentRegistry")

    def fail_task(self, error_msg: str):
        duration = time.time() - self.task_start_time if self.task_start_time > 0 else 0.0
        self.total_execution_seconds += duration
        self.failed_tasks_count += 1
        self.current_state = "Failed"
        self.last_error = error_msg
        self.last_activity_time = time.time()
        log_event(f"Agent [{self.name}] failed task: {error_msg}", component="AgentRegistry", level="ERROR")

    def reset_idle(self):
        self.current_state = "Idle"
        self.current_task = ""
        self.progress_pct = 0
        self.waiting_for = ""
        self.task_start_time = 0.0

    def to_dict(self) -> Dict[str, Any]:
        duration = (time.time() - self.task_start_time) if (self.current_state in ["Running", "Assigned", "Retrying"] and self.task_start_time > 0) else 0.0
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "group": self.group,
            "group_name": self.group_name,
            "role": self.role,
            "description": self.description,
            "permitted_tools": self.permitted_tools,
            "model": self.default_model,
            "state": self.current_state,
            "current_task": self.current_task,
            "progress_pct": self.progress_pct,
            "waiting_for": self.waiting_for,
            "duration_sec": round(duration, 1),
            "last_activity": time.strftime("%H:%M:%S", time.localtime(self.last_activity_time)),
            "last_error": self.last_error,
            "successful_tasks": self.successful_tasks_count,
            "failed_tasks": self.failed_tasks_count,
            "total_execution_seconds": round(self.total_execution_seconds, 1),
            "icon": self.icon
        }

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, SpecializedAgent] = {}
        self._register_all_205_agents()

    def _register_all_205_agents(self):
        agents_def = []

        # -------------------------------------------------------------------------
        # Group A: Core Cognitive & Orchestration (Agents 1-15)
        # -------------------------------------------------------------------------
        group_a = [
            ("agent_01", "Manager Agent", "Central Request Orchestration & Strategy", "Receives user requests, understands requirements, creates end-to-end execution plans, and coordinates all worker agents.", ["task_manager", "model_router", "approval_queue", "workflow_engine"], "qwen2.5-coder:7b", "crown"),
            ("agent_02", "Task Planning Agent", "Decomposition & Dependency Sequencing", "Breaks complex requirements into granular subtasks, identifies dependencies, priorities, deadlines, and acceptance criteria.", ["plan_decomposer", "dag_builder", "priority_queue"], "qwen2.5-coder:7b", "sitemap"),
            ("agent_03", "Agent Coordination Agent", "Inter-Agent Messaging & Conflict Prevention", "Coordinates communication between agents, resolves dependency blocking, and prevents conflicting operations.", ["ipc_router", "semaphore_lock", "dependency_watcher"], "llama3.2:3b", "users"),
            ("agent_04", "AI Model Routing Agent", "Intelligent Model Selection & Load Balancer", "Selects optimal AI model based on task complexity, coding needs, structured JSON reliability, speed, and hardware availability.", ["model_adapter", "latency_benchmarker", "fallback_cascade"], "phi4-mini:latest", "network-wired"),
            ("agent_05", "Quality Assurance Agent", "Deliverable Verification & Test Validation", "Validates outputs against user acceptance criteria, executes automated tests, and identifies incomplete deliverables.", ["schema_validator", "test_runner", "diff_inspector"], "qwen2.5-coder:7b", "clipboard-check"),
            ("agent_06", "Risk Governance Agent", "High-Risk Operation Gatekeeper & Approvals", "Inspects destructive actions (DROP, DELETE, TRUNCATE), enforces approval workflows, and alerts user via Telegram.", ["risk_evaluator", "approval_manager", "telegram_alert_bot"], "qwen2.5-coder:7b", "shield-alt"),
            ("agent_07", "Cognitive Memory Agent", "Persistent Multi-Turn Context & History", "Preserves chat history, user preferences, past execution results, and conversation context in SQLite memory.", ["context_retriever", "memory_indexer", "session_cache"], "llama3.2:3b", "brain"),
            ("agent_08", "Execution Overseer Agent", "Run-Time Telemetry & Heartbeat Monitoring", "Monitors active threads, memory consumption, task execution timeouts, and agent worker availability.", ["telemetry_collector", "process_monitor", "heartbeat_sensor"], "phi4-mini:latest", "heartbeat"),
            ("agent_09", "Error Diagnostics Agent", "Root Cause Analysis & Stacktrace Triage", "Parses stack traces, isolates underlying causes (network, auth, schema mismatch), and proposes fixes.", ["stacktrace_analyzer", "log_parser", "remediation_suggester"], "qwen2.5-coder:7b", "stethoscope"),
            ("agent_10", "Self-Healing Recovery Agent", "Automatic Retry & Failover Orchestrator", "Re-queues interrupted tasks upon crash recovery, resolves locked database rows, and restarts failed workers.", ["failover_manager", "retry_engine", "rollback_handler"], "phi4-mini:latest", "first-aid"),
            ("agent_11", "Marathi NLP Specialist Agent", "Native Marathi Instruction Comprehension", "Translates, parses, and resolves Marathi / Hinglish commands into formal execution parameters.", ["indic_nlp", "marathi_tokenizer", "intent_mapper"], "qwen2.5-coder:7b", "language"),
            ("agent_12", "Hinglish Conversational Agent", "Bilingual Indian Vernacular Interpreter", "Interprets conversational mixed Hindi/English instructions and maps them accurately to studio agents.", ["hinglish_parser", "entity_extractor", "code_switch_resolver"], "llama3.2:3b", "comments"),
            ("agent_13", "Executive Summary Agent", "C-Suite Status Briefings & Daily Recaps", "Synthesizes daily metrics, completed ETL pipelines, job applications, and financial digests into concise reports.", ["markdown_synthesizer", "metric_aggregator", "briefing_engine"], "qwen2.5-coder:7b", "file-alt"),
            ("agent_14", "Budget & Cost Optimizer Agent", "LLM Compute & Cloud Egress Minimizer", "Analyzes query cost profiles in Snowflake, AWS S3 egress, and selects efficient local Ollama models.", ["cost_analyzer", "egress_monitor", "token_budgeter"], "phi4-mini:latest", "coins"),
            ("agent_15", "Studio Welcome & Ambience Agent", "Personalized Greetings & Daily Inspiration", "Delivers personalized Good Morning, Good Evening, and Good Night notes to Mangesh on Telegram.", ["greeting_synthesizer", "open_meteo_api", "quote_generator"], "llama3.2:3b", "sun")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_a:
            agents_def.append((aid, name, "A", "Core Orchestration", role, desc, tools, mdl, ico))

        # -------------------------------------------------------------------------
        # Group B: Advanced Data Engineering, ETL/ELT & Stream Processing (Agents 16-35)
        # -------------------------------------------------------------------------
        group_b = [
            ("agent_16", "Data Engineering Architect", "Pipeline Architecture & Medallion Design", "Designs end-to-end data architectures, pipeline dependencies, partitioning schemes, and processing strategies.", ["architecture_linter", "schema_designer", "storage_calculator"], "qwen2.5-coder:7b", "drafting-compass"),
            ("agent_17", "Python ETL Pipeline Agent", "Vectorized Ingestion & Chunked Batch Parsing", "Extracts, transforms, and loads high-volume tabular datasets using Pandas, Polars, and chunked generators.", ["pandas_engine", "polars_streamer", "chunk_loader"], "qwen2.5-coder:7b", "file-code"),
            ("agent_18", "SQL Developer Agent", "Complex DDL, DML & Query Assertions", "Authors DDL, complex multi-table joins, window functions, and automated test assertions across warehouses.", ["sql_generator", "query_optimizer", "ast_sql_checker"], "qwen2.5-coder:7b", "database"),
            ("agent_19", "Schema Evolution & DDL Agent", "Automated Alterations & Column Migrations", "Handles schema changes, column additions/modifications, type conversions, and backwards compatibility.", ["schema_migrator", "ddl_versioner", "alter_table_executor"], "qwen2.5-coder:7b", "layer-group"),
            ("agent_20", "Data Deduplication Agent", "Surrogate Key Matching & Exact/Fuzzy Dedup", "Identifies duplicate records using natural key hashes and fuzzy string matching across raw batches.", ["hash_deduplicator", "record_linkage", "fuzzy_matcher"], "phi4-mini:latest", "clone"),
            ("agent_21", "Data Cleansing & Sanitizer Agent", "Null Imputation & Format Normalization", "Cleans malformed telephone numbers, cleans dates, fills default values, and strips corrupt whitespaces.", ["regex_cleaner", "date_normalizer", "null_imputer"], "phi4-mini:latest", "broom"),
            ("agent_22", "Universal File Converter Agent", "Multi-Format Converter (CSV, Excel, XML, Parquet)", "Converts tabular data seamlessly between CSV, XLSX, Parquet, JSON, and Pipe-delimited files.", ["openpyxl_engine", "parquet_writer", "xml_parser"], "phi4-mini:latest", "exchange-alt"),
            ("agent_23", "SFTP & Secure Transfer Agent", "Automated Batch SFTP Ingestion & PGP Decryption", "Pulls encrypted batch files over SFTP, performs checksum validation, and loads into staging directories.", ["paramiko_sftp", "checksum_verifier", "pgp_decryptor"], "phi4-mini:latest", "file-download"),
            ("agent_24", "Streaming Ingestion Agent", "Real-Time Event Streams & Micro-Batching", "Ingests streaming transactional events, applies sliding window aggregations, and flushes to storage.", ["stream_buffer", "event_consumer", "window_aggregator"], "qwen2.5-coder:7b", "stream"),
            ("agent_25", "SCD Type 2 Historization Agent", "Slowly Changing Dimensions Historian", "Manages valid_from_date, valid_to_date, and is_current_flag SCD2 logic in data warehouse tables.", ["scd2_merger", "surrogate_key_assigner", "history_expirer"], "qwen2.5-coder:7b", "history"),
            ("agent_26", "Medallion Bronze Loader Agent", "L0 Raw Staging Buffer & Checkpoint Manager", "Loads unvalidated raw payloads into Bronze L0 staging layers with exact source audit columns.", ["bronze_loader", "checkpoint_recorder", "raw_buffer"], "phi4-mini:latest", "inbox"),
            ("agent_27", "Medallion Silver Harmonizer Agent", "L1 Cleansed Data Conformance & Typing", "Transforms raw Bronze data into typed, validated, and normalized Silver harmonized dimensional tables.", ["silver_transformer", "type_enforcer", "referential_checker"], "qwen2.5-coder:7b", "filter"),
            ("agent_28", "Medallion Gold Mart Builder Agent", "L2 Curated Business Aggregations & KPIs", "Calculates aggregated metrics, customer lifetime values, and financial summaries for reporting marts.", ["gold_aggregator", "kpi_calculator", "mart_materializer"], "qwen2.5-coder:7b", "award"),
            ("agent_29", "Apache Airflow DAG Architect", "Declarative DAG Generator & Sensor Builder", "Constructs Python Airflow DAGs with idempotent tasks, execution date templates, and SLA alerts.", ["dag_synthesizer", "airflow_linter", "task_dependency_graph"], "qwen2.5-coder:7b", "wind"),
            ("agent_30", "Linux Bash Automator Agent", "Crontab & Shell Batch Scripting Specialist", "Generates high-performance shell scripts, log rotators, environment setup, and cron schedules.", ["bash_generator", "cron_builder", "shell_linter"], "qwen2.5-coder:7b", "terminal"),
            ("agent_31", "Batch Recovery & Replay Agent", "Historical Backfill & Idempotent Reprocessing", "Replays historical batch intervals with parameterized date partitions without duplicating target data.", ["backfill_orchestrator", "partition_cleaner", "replay_verifier"], "qwen2.5-coder:7b", "redo"),
            ("agent_32", "Memory Profiling & OOM Guard Agent", "Garbage Collection & RAM Usage Guard", "Monitors DataFrame memory footprints, triggers garbage collection, and enforces streaming iterators.", ["memory_profiler", "chunk_size_tuner", "gc_enforcer"], "phi4-mini:latest", "memory"),
            ("agent_33", "AWS S3 Data Lake Optimizer", "S3 Storage Classes & Multipart Uploader", "Optimizes S3 bucket layouts, manages multipart uploads, compression, and lifecycle tiering rules.", ["boto3_s3", "multipart_uploader", "lifecycle_manager"], "phi4-mini:latest", "cloud-upload-alt"),
            ("agent_34", "DuckDB In-Memory Query Agent", "Embedded Analytical Query Engine", "Runs lightning-fast analytical queries directly over local Parquet and CSV files with zero server overhead.", ["duckdb_engine", "parquet_scanner", "in_memory_sql"], "qwen2.5-coder:7b", "bolt"),
            ("agent_35", "Data Pipeline Regression Tester", "End-to-End ETL Test Assertion Suite", "Executes 100% automated regression assertions comparing source records, transformed rows, and targets.", ["regression_suite", "reconciliation_checker", "row_counter"], "qwen2.5-coder:7b", "vial")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_b:
            agents_def.append((aid, name, "B", "Data Engineering", role, desc, tools, mdl, ico))

        # -------------------------------------------------------------------------
        # Group C: Snowflake, Oracle XE & Cloud Warehouses (Agents 36-55)
        # -------------------------------------------------------------------------
        group_c = [
            ("agent_36", "Oracle XE Administrator Agent", "Local & Remote Oracle XE DBA Operations", "Manages SYSTEM user operations, listener checks on port 1521, tablespace quotas, and session states.", ["oracledb_connector", "listener_pinger", "tablespace_inspector"], "qwen2.5-coder:7b", "server"),
            ("agent_37", "Oracle PL/SQL Specialist Agent", "Stored Procedures, Packages & Triggers", "Authors high-performance PL/SQL stored procedures, cursors, autonomous transactions, and triggers.", ["plsql_compiler", "procedure_builder", "trigger_designer"], "qwen2.5-coder:7b", "code"),
            ("agent_38", "Oracle XE Localhost Agent", "MY_ORACLE_XE_LOCAL (127.0.0.1) Specialist", "Monitors and executes queries on local Oracle instance on 127.0.0.1:1521/XEPDB1.", ["local_oracle_pinger", "xepdb1_client", "local_query_engine"], "phi4-mini:latest", "laptop"),
            ("agent_39", "Oracle XE Remote LAN Agent", "MY_ORACLE_XE_REMOTE (192.168.31.240) Specialist", "Maintains high-availability connection to primary remote LAN Oracle XE instance.", ["lan_oracle_client", "network_route_probe", "lan_data_puller"], "phi4-mini:latest", "network-wired"),
            ("agent_40", "Oracle Tailscale Mesh Agent", "MY_ORACLE_XE_REMOTE_New (100.112.86.83)", "Validates Tailscale mesh VPN routing and connects to secure remote Oracle instance.", ["tailscale_pinger", "mesh_vpn_checker", "vpn_oracle_client"], "phi4-mini:latest", "shield-alt"),
            ("agent_41", "Oracle LogMiner CDC Agent", "Transaction Log Extraction & Change Capture", "Queries Oracle V$LOGMNR_CONTENTS to stream changed row records without impacting production.", ["logminer_extractor", "redo_log_reader", "cdc_streamer"], "qwen2.5-coder:7b", "search"),
            ("agent_42", "Snowflake Account Administrator", "Snowflake Horizon Governance & RBAC Roles", "Configures ACCOUNTADMIN, SYSADMIN roles, warehouse sizes, auto-suspend, and network policies.", ["snowflake_admin_sql", "rbac_manager", "warehouse_scaler"], "qwen2.5-coder:7b", "snowflake"),
            ("agent_43", "Snowpipe Streaming Specialist", "Serverless Real-Time Micro-Batch Ingestion", "Configures Snowpipe continuous ingestion pipes auto-ingesting staged S3 files with SQS notifications.", ["snowpipe_creator", "pipe_monitor", "sqs_event_mapper"], "qwen2.5-coder:7b", "icicles"),
            ("agent_44", "Snowflake Streams & Tasks Agent", "Change Data Capture & Scheduled DAGs", "Builds declarative Snowflake STREAMS on L0 tables and chained TASKS for automated incremental refreshes.", ["stream_builder", "task_chain_builder", "cron_task_scheduler"], "qwen2.5-coder:7b", "tasks"),
            ("agent_45", "Snowflake Dynamic Tables Agent", "Declarative Near-Real-Time Pipelines", "Deploys Snowflake Dynamic Tables with TARGET_LAG = '1 MINUTE' for automated DAG refresh.", ["dynamic_table_ddl", "lag_monitor", "dag_resolver"], "qwen2.5-coder:7b", "table"),
            ("agent_46", "Snowpark Python Procedure Agent", "In-Warehouse Python UDFs & Stored Procedures", "Executes secure Snowpark Python data engineering procedures directly within Snowflake warehouses.", ["snowpark_session", "in_db_python_udf", "dataframe_reader"], "qwen2.5-coder:7b", "python"),
            ("agent_47", "Snowflake Zero-Copy Clone Agent", "Instant Sandbox Clones & Time Travel", "Clones databases and tables in seconds for dev/test without incurring extra cloud storage costs.", ["zero_copy_cloner", "time_travel_restorer", "table_swapper"], "phi4-mini:latest", "copy"),
            ("agent_48", "Snowflake Performance Tuner Agent", "Clustering Keys, Micro-partition Pruning", "Analyzes SYSTEM$CLUSTERING_INFORMATION, query profiles, and optimizes join execution trees.", ["clustering_advisor", "pruning_analyzer", "spill_detector"], "qwen2.5-coder:7b", "tachometer-alt"),
            ("agent_49", "Snowflake Credit & Cost Auditor", "Warehouse Metering & Spilling Prevention", "Audits SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY to detect runaway compute costs.", ["metering_auditor", "credit_calculator", "spill_to_remote_guard"], "phi4-mini:latest", "dollar-sign"),
            ("agent_50", "Snowflake Data Sharing Agent", "Secure Data Shares & Clean Rooms", "Manages secure data shares granting read-only access to downstream enterprise consumers.", ["data_share_admin", "reader_account_manager", "secure_view_builder"], "qwen2.5-coder:7b", "share-alt"),
            ("agent_51", "AWS Redshift Integration Agent", "Redshift Spectrum & Serverless Data Sharing", "Connects AWS Redshift clusters, manages external schemas, and executes analytical queries.", ["redshift_connector", "spectrum_mapper", "redshift_data_api"], "qwen2.5-coder:7b", "cloud"),
            ("agent_52", "Google BigQuery Data Agent", "BigQuery External Tables & Serverless SQL", "Interoperates with Google BigQuery datasets, partitioned tables, and streaming buffers.", ["bigquery_client", "partition_pruner", "storage_api_reader"], "qwen2.5-coder:7b", "cubes"),
            ("agent_53", "PostgreSQL Enterprise Agent", "Postgres MVCC & Vacuum Optimization", "Manages PostgreSQL schemas, indexes (BRIN/B-tree), JSONB columns, and connection pools.", ["psycopg2_client", "vacuum_analyzer", "jsonb_query_builder"], "qwen2.5-coder:7b", "elephant"),
            ("agent_54", "Microsoft SQL Server Agent", "T-SQL Stored Procedures & Linked Servers", "Executes T-SQL batches, manages linked server connections, and extracts relational tables.", ["pyodbc_client", "tsql_executor", "linked_server_bridge"], "qwen2.5-coder:7b", "windows"),
            ("agent_55", "Federated Multi-DB Query Router", "Cross-Engine Query Coordinator", "Routes distributed query sub-plans to the appropriate engine (Oracle, Snowflake, SQLite, S3).", ["federated_router", "cross_db_optimizer", "result_coalescer"], "qwen2.5-coder:7b", "project-diagram")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_c:
            agents_def.append((aid, name, "C", "Snowflake & Oracle", role, desc, tools, mdl, ico))

        # -------------------------------------------------------------------------
        # Group D: Data Quality, Governance, Observability & Lineage (Agents 56-70)
        # -------------------------------------------------------------------------
        group_d = [
            ("agent_56", "Great Expectations Profiler", "Declarative Data Quality Expectations", "Configures Great Expectations suites validating non-null, uniqueness, value ranges, and schemas.", ["gx_suite_builder", "checkpoint_runner", "data_docs_renderer"], "qwen2.5-coder:7b", "check-circle"),
            ("agent_57", "Data Lineage & Provenance Agent", "End-to-End Column Lineage DAG Visualizer", "Traces column-level origin from source Oracle XE tables through S3 staging to Snowflake Gold marts.", ["lineage_tracer", "column_provenance_dag", "graphviz_exporter"], "qwen2.5-coder:7b", "bezier-curve"),
            ("agent_58", "Data Anomaly Detection Agent", "Statistical Outlier & Distribution Shift", "Detects unexpected spikes, standard deviation shifts, and cardinality drift across incoming batches.", ["zscore_detector", "distribution_comparer", "drift_alert_bot"], "phi4-mini:latest", "chart-line"),
            ("agent_59", "Data Dictionary & Catalog Agent", "Automated Metadata & Column Descriptions", "Maintains automated dictionary with business glossaries, column types, descriptions, and tags.", ["catalog_generator", "glossary_indexer", "markdown_doc_builder"], "phi4-mini:latest", "book"),
            ("agent_60", "PII & Masking Compliance Agent", "Sensitive Data Discovery & Dynamic Masking", "Discovers PAN numbers, Aadhaar, account numbers, and enforces dynamic masking policies.", ["pii_scanner", "dynamic_masker", "gdpr_compliance_check"], "qwen2.5-coder:7b", "user-secret"),
            ("agent_61", "Schema Drift Sentinel Agent", "Incoming Schema Changes & Alerting", "Compares daily incoming file headers with production schema DDL to catch breaking changes.", ["header_diff_checker", "drift_alert_bot", "schema_lock_manager"], "phi4-mini:latest", "bell"),
            ("agent_62", "Referential Integrity Auditor", "Foreign Key & Orphan Record Detector", "Verifies that every foreign key in transaction tables corresponds to a valid master account entry.", ["fk_assertion_engine", "orphan_record_highlighter", "integrity_scorer"], "phi4-mini:latest", "link"),
            ("agent_63", "Row Count Reconciliation Agent", "Source vs Target Completeness Auditor", "Reconciles extract counts from Oracle against landed rows in Snowflake, generating audit receipts.", ["reconciliation_matrix", "audit_receipt_issuer", "variance_calculator"], "phi4-mini:latest", "balance-scale"),
            ("agent_64", "Data Freshness & SLA Agent", "Pipeline Arrival Latency & SLA Breach Alert", "Monitors ingestion timestamps against configured business SLAs and triggers alerts upon delays.", ["freshness_timer", "sla_breach_evaluator", "pager_duty_bot"], "phi4-mini:latest", "stopwatch"),
            ("agent_65", "Duplicate Detection Sentinel", "Real-Time Primary Key Collision Guard", "Scans incoming batch chunks before warehouse commit to guarantee zero primary key collisions.", ["pk_collision_guard", "hash_index_scanner", "quarantine_diverter"], "phi4-mini:latest", "shield-virus"),
            ("agent_66", "Null Percentage Profiler Agent", "Column Completeness & Null Variance", "Calculates exact null percentages per column and highlights critical attribute omissions.", ["null_profiler", "completeness_scorer", "variance_tracker"], "phi4-mini:latest", "percentage"),
            ("agent_67", "Data Quarantine Manager Agent", "Bad Record Segregation & Reprocessing", "Diverts corrupt records to quarantine error tables with detailed error codes without halting pipeline.", ["quarantine_table_writer", "error_code_tagger", "remediation_queue"], "phi4-mini:latest", "box-tissue"),
            ("agent_68", "Compliance & Audit Trail Agent", "BFSI Regulatory Audit Trail Ledger", "Maintains immutable audit records for RBI, AML, and SEBI compliance inspections.", ["compliance_ledger", "immutable_hash_chain", "rbi_reporting_formatter"], "qwen2.5-coder:7b", "stamp"),
            ("agent_69", "Semantic Vector Search Profiler", "Semantic Metadata & Similarity Discovery", "Embeds column descriptions and table purposes to enable semantic search across studio datasets.", ["embedding_indexer", "similarity_searcher", "faiss_vector_store"], "phi4-mini:latest", "search-plus"),
            ("agent_70", "Data Quality Health Scorer", "Composite 100-Point Quality Scorecard", "Aggregates completeness, validity, uniqueness, and timeliness into an executive 0-100 quality score.", ["quality_scorer", "health_card_generator", "executive_kpi_card"], "phi4-mini:latest", "medal")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_d:
            agents_def.append((aid, name, "D", "Data Quality & Lineage", role, desc, tools, mdl, ico))

        # -------------------------------------------------------------------------
        # Group E: AWS DMS & Database Migration (Agents 71-85)
        # -------------------------------------------------------------------------
        group_e = [
            ("agent_71", "AWS DMS Architecture Lead", "DMS Topology & Replication Sizing", "Sizes replication instances (dms.t3.medium / c5.large), VPC security groups, and multi-AZ designs.", ["dms_sizer", "vpc_topology_mapper", "aws_dms_manager"], "qwen2.5-coder:7b", "sitemap"),
            ("agent_72", "DMS Replication Instance Agent", "Instance Lifecycle & CPU/RAM Monitoring", "Monitors replication instance health, allocated storage, memory pressure, and engine version.", ["instance_lifecycle", "cw_metrics_reader", "resource_scaler"], "phi4-mini:latest", "server"),
            ("agent_73", "DMS Source Endpoint Agent", "Oracle Source Endpoint Configuration", "Configures Oracle XE endpoints with LogMiner privileges, SSL encryption, and connection testing.", ["oracle_endpoint_config", "port_1521_probe", "privilege_verifier"], "phi4-mini:latest", "plug"),
            ("agent_74", "DMS Target S3 Endpoint Agent", "AWS S3 Staging Lake Target Config", "Configures S3 target endpoints with Parquet formatting, GZIP compression, and IAM role ARNs.", ["s3_endpoint_config", "parquet_settings_builder", "iam_role_checker"], "phi4-mini:latest", "cloud-upload-alt"),
            ("agent_75", "DMS Target Snowflake Agent", "Snowflake Target Endpoint & Auto-DDL", "Configures Snowflake warehouse targets with automatic table creation and staging buffer mapping.", ["snowflake_target_config", "auto_table_creator", "stage_mapper"], "qwen2.5-coder:7b", "snowflake"),
            ("agent_76", "DMS Full Load Task Agent", "Historical Bulk Extraction & Table Loading", "Orchestrates initial historical full-load tasks with parallel threads and row validation.", ["full_load_task_runner", "parallel_table_loader", "load_progress_tracker"], "qwen2.5-coder:7b", "download"),
            ("agent_77", "DMS Continuous CDC Agent", "Real-Time Ongoing CDC Replication", "Manages ongoing CDC replication, tracks checkpoint offsets, and minimizes target commit lag.", ["cdc_task_runner", "checkpoint_tracker", "latency_minimizer"], "qwen2.5-coder:7b", "sync"),
            ("agent_78", "DMS Table Mapping Rules Agent", "JSON Selection, Renaming & Column Filters", "Authors complex DMS JSON table mapping rules (selection, transformation, schema rename, data mask).", ["mapping_rules_linter", "json_rule_builder", "schema_renamer"], "phi4-mini:latest", "code"),
            ("agent_79", "DMS Latency & Lag Monitor", "CDC Target Latency & Bottleneck Triaging", "Monitors CDC source/target latency in seconds and alerts when replication lag exceeds threshold.", ["latency_gauge", "bottleneck_detector", "lag_alert_bot"], "phi4-mini:latest", "tachometer-alt"),
            ("agent_80", "DMS Error Remediation Agent", "Table Reload & Skipped Error Resolution", "Triages failed DMS tables, resolves data type mismatches, and re-triggers isolated table reloads.", ["error_table_reloader", "datatype_caster", "dms_log_triage"], "qwen2.5-coder:7b", "wrench"),
            ("agent_81", "DMS Migration Validation Agent", "Source vs Target Verification Comparison", "Compares row counts, hash checksums, and primary key matches between Oracle and S3/Snowflake.", ["data_validator_engine", "checksum_comparator", "discrepancy_logger"], "qwen2.5-coder:7b", "check-double"),
            ("agent_82", "AWS Schema Conversion Tool Agent", "Heterogeneous Schema & Stored Proc SCT", "Automates conversion of Oracle PL/SQL, packages, sequences, and tables to modern Snowflake syntax.", ["sct_converter", "syntax_translator", "ddl_rewriter"], "qwen2.5-coder:7b", "exchange-alt"),
            ("agent_83", "DMS Task Scheduler Agent", "Automated Task Pause, Resume & Maintenance", "Schedules DMS task pauses during source batch maintenance windows and resumes automatically.", ["dms_task_scheduler", "maintenance_window_guard", "task_controller"], "phi4-mini:latest", "calendar-alt"),
            ("agent_84", "DMS CloudWatch Logs Analyzer", "Detailed Task Log Stream Analysis", "Inspects AWS CloudWatch DMS task log streams to diagnose LogMiner disconnects or memory warnings.", ["cloudwatch_reader", "logminer_warning_parser", "log_streamer"], "phi4-mini:latest", "list-alt"),
            ("agent_85", "DMS Cutover & Switchover Agent", "Zero-Downtime Production Cutover Lead", "Executes zero-downtime final cutover checklist verifying target synchronization before switch.", ["cutover_checklist_lead", "sync_point_verifier", "traffic_switch_guard"], "qwen2.5-coder:7b", "power-off")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_e:
            agents_def.append((aid, name, "E", "AWS DMS & Migration", role, desc, tools, mdl, ico))

        # -------------------------------------------------------------------------
        # Group F: Data Analytics, BI & Executive Intelligence (Agents 86-105)
        # -------------------------------------------------------------------------
        group_f = [
            ("agent_86", "Executive BI Architect", "Power BI & Tableau Semantic Modeling", "Designs star schemas, dimensional role-playing dimensions, and fast DirectQuery models.", ["semantic_modeler", "star_schema_linter", "dax_formatter"], "qwen2.5-coder:7b", "chart-pie"),
            ("agent_87", "Ad-Hoc SQL Exploration Agent", "Interactive Business Query Investigator", "Quickly answers complex business questions using multi-table SQL queries and window aggregates.", ["adhoc_query_runner", "result_pivoter", "insight_summarizer"], "qwen2.5-coder:7b", "search"),
            ("agent_88", "Customer Analytics Specialist", "Cohort Analysis, Churn & RFM Scoring", "Calculates Recency, Frequency, Monetary (RFM) segmentation and predicts telecom churn risk.", ["rfm_calculator", "churn_predictor", "cohort_analyzer"], "qwen2.5-coder:7b", "users"),
            ("agent_89", "Financial Transaction Analyst", "BFSI Balance Reconciliation & Outlier Spend", "Analyzes banking ledger variances, high-value transaction spikes, and AML velocity thresholds.", ["variance_analyzer", "velocity_threshold_check", "aml_pattern_finder"], "qwen2.5-coder:7b", "money-check-alt"),
            ("agent_90", "Executive KPI Dashboard Agent", "High-Level Executive Metrics Synthesizer", "Compiles daily revenue, active customer count, batch SLAs, and pipeline throughput into summaries.", ["kpi_synthesizer", "executive_card_builder", "trend_arrow_calculator"], "phi4-mini:latest", "chart-bar"),
            ("agent_91", "Automated Excel Report Builder", "Formatted Excel Workbooks with Formulas", "Generates styled .xlsx workbooks with cell styling, headers, totals formulas, and charts.", ["openpyxl_styler", "formula_injector", "excel_chart_maker"], "phi4-mini:latest", "file-excel"),
            ("agent_92", "Interactive Chart & Plot Agent", "Plotly & Matplotlib Visualization Specialist", "Renders rich interactive HTML charts, bar charts, time-series curves, and heatmaps.", ["plotly_generator", "matplotlib_styler", "chart_renderer"], "phi4-mini:latest", "chart-area"),
            ("agent_93", "Time-Series Forecasting Agent", "ARIMA & Exponential Smoothing Forecaster", "Forecasts upcoming transaction volumes, server storage growth, and compute requirements.", ["timeseries_forecaster", "trend_decomposer", "capacity_projector"], "qwen2.5-coder:7b", "chart-line"),
            ("agent_94", "Cohort Retention Analyzer", "Monthly & Weekly Retention Matrix", "Analyzes user retention matrices and customer lifetime value progression across acquisition cohorts.", ["retention_matrix_builder", "decay_curve_fitter", "ltv_calculator"], "phi4-mini:latest", "user-clock"),
            ("agent_95", "Funnel Conversion Analyst", "Multi-Stage Conversion Funnel Optimizer", "Tracks drop-off rates across multi-step user onboarding and banking account opening flows.", ["funnel_builder", "dropoff_calculator", "conversion_optimizer"], "phi4-mini:latest", "filter"),
            ("agent_96", "Variance & Budget Tracking Agent", "Actual vs Budget Variance Explainer", "Compares actual financial transactions against target operating budgets with variance flags.", ["variance_flagger", "budget_tracker", "variance_waterfall"], "phi4-mini:latest", "balance-scale"),
            ("agent_97", "Geographic & Regional Analyst", "Mumbai & Maharashtra Geospatial Mapping", "Analyzes branch transactions, ATM density, and revenue distribution across Maharashtra regions.", ["geo_mapper", "district_aggregator", "pin_code_resolver"], "phi4-mini:latest", "map-marked-alt"),
            ("agent_98", "Product Affinity & Basket Agent", "Association Rule Mining (Market Basket)", "Extracts co-purchase patterns and product affinities across enterprise banking product lines.", ["apriori_engine", "association_rule_miner", "cross_sell_recommender"], "phi4-mini:latest", "shopping-basket"),
            ("agent_99", "Statistical Hypothesis Tester", "P-Value, T-Test & Chi-Squared Validator", "Conducts rigorous statistical hypothesis tests verifying significance of data differences.", ["scipy_stats", "ttest_calculator", "pvalue_evaluator"], "qwen2.5-coder:7b", "calculator"),
            ("agent_100", "Executive Narrative Generator", "Storytelling from Data Insights", "Translates numbers and charts into clear, compelling plain-language executive narratives.", ["narrative_synthesizer", "bullet_point_summarizer", "takeaway_extractor"], "qwen2.5-coder:7b", "comment-alt"),
            ("agent_101", "Data Pivot & Cross-Tab Agent", "Multi-Dimensional Pivot Matrix Builder", "Pivots complex transactional feeds into multi-level hierarchical pivot matrices with subtotals.", ["pivot_matrix_builder", "crosstab_engine", "subtotal_calculator"], "phi4-mini:latest", "table"),
            ("agent_102", "Correlation Matrix Analyst", "Feature Correlation & Multicollinearity", "Computes Pearson/Spearman correlation matrices and flags collinear predictive features.", ["correlation_calculator", "heatmap_annotator", "vif_evaluator"], "phi4-mini:latest", "th"),
            ("agent_103", "Data Profiling Summary Lead", "Dataset Shape, Cardinality & Distribution", "Generates comprehensive profile summaries reporting distinct counts, min, max, mean, and quantiles.", ["profile_summary_lead", "quantiles_calculator", "cardinality_measurer"], "phi4-mini:latest", "id-card"),
            ("agent_104", "Voice BI Executive Narrator", "Spoken Audio Summary of Studio Analytics", "Converts daily analytics and KPI cards into spoken audio narration using Web Speech / Edge TTS.", ["tts_audio_synthesizer", "speech_narrator", "audio_briefing_player"], "phi4-mini:latest", "microphone"),
            ("agent_105", "Automated PDF Report Publisher", "C-Suite PDF Executive Packet Publisher", "Compiles formatted multi-page PDF briefing decks with company branding, tables, and graphs.", ["reportlab_pdf_builder", "pdf_page_formatter", "header_footer_styler"], "qwen2.5-coder:7b", "file-pdf")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_f:
            agents_def.append((aid, name, "F", "Analytics & BI", role, desc, tools, mdl, ico))

        # -------------------------------------------------------------------------
        # Group G: AI, Deep Learning, LLM Training & MLOps (Agents 106-125)
        # -------------------------------------------------------------------------
        group_g = [
            ("agent_106", "LLM Model Training Lead", "LoRA / QLoRA Fine-Tuning & Parameter Updates", "Prepares instruction fine-tuning datasets, orchestrates LoRA training runs, and evaluates loss.", ["training_orchestrator", "loss_tracker", "checkpoint_saver"], "qwen2.5-coder:7b", "brain"),
            ("agent_107", "Dataset Curation & Prep Agent", "Instruction-Tuning Dataset Synthesizer", "Cleans raw conversations into prompt-response JSONL pairs formatted for LLM supervised fine-tuning.", ["jsonl_prep_engine", "prompt_response_formatter", "tokenizer_counter"], "qwen2.5-coder:7b", "database"),
            ("agent_108", "Ollama Local Model Operator", "Local GGUF Model Deployment & Serving", "Manages local Ollama model pulls, memory context window sizing, keep-alive, and GPU offloading.", ["ollama_cli", "context_window_allocator", "gpu_vram_monitor"], "phi4-mini:latest", "microchip"),
            ("agent_109", "Quantization & GGUF Specialist", "Model Compression (4-bit, 8-bit QLoRA)", "Quantizes deep learning weights to Q4_K_M and Q8_0 GGUF formats maximizing local inference speed.", ["gguf_quantizer", "perplexity_benchmarker", "vram_sizer"], "qwen2.5-coder:7b", "compress-arrows-alt"),
            ("agent_110", "Prompt Engineering Specialist", "Few-Shot Prompting & CoT System Prompts", "Optimizes system prompts with Chain-of-Thought (CoT), few-shot examples, and strict JSON schemas.", ["cot_prompt_designer", "fewshot_curator", "json_schema_enforcer"], "qwen2.5-coder:7b", "magic"),
            ("agent_111", "RAG Knowledge Retrieval Agent", "Retrieval-Augmented Generation Specialist", "Embeds enterprise documentation into vector indexes and retrieves chunks for LLM context grounding.", ["rag_retriever", "chunk_splitter", "reranker_engine"], "qwen2.5-coder:7b", "search"),
            ("agent_112", "Hugging Face Hub Integrator", "Open-Source Weights & Dataset Downloader", "Interfaces with Hugging Face Hub, checks trending model cards, licenses, and downloads weights.", ["hf_hub_api", "model_card_evaluator", "weight_downloader"], "phi4-mini:latest", "smile"),
            ("agent_113", "Google Gemini API Specialist", "Multimodal Reasoning & Long-Context Gemini", "Calls official Google Gemini 2.5/3.0 APIs with structured output schemas and deep reasoning.", ["gemini_sdk_client", "multimodal_processor", "token_usage_tracker"], "qwen2.5-coder:7b", "gem"),
            ("agent_114", "DeepSeek Coder Integration Agent", "DeepSeek Reasoner & Coder Specialist", "Routes complex algorithmic coding challenges and architecture designs to DeepSeek models.", ["deepseek_api_client", "reasoning_extractor", "code_synthesizer"], "qwen2.5-coder:7b", "code-branch"),
            ("agent_115", "Scikit-Learn ML Workbench Agent", "Classification, Regression & Random Forest", "Trains scikit-learn models, computes ROC-AUC, precision-recall, and generates confusion matrices.", ["sklearn_pipeline", "cross_validator", "confusion_matrix_maker"], "qwen2.5-coder:7b", "cogs"),
            ("agent_116", "Feature Engineering Specialist", "One-Hot Encoding, Scaling & Interaction", "Transforms raw tabular attributes into high-impact model features using StandardScaler and PCA.", ["feature_scaler", "interaction_builder", "pca_decomposer"], "phi4-mini:latest", "sliders-h"),
            ("agent_117", "Hyperparameter Tuning Agent", "Optuna & GridSearch Optimization", "Optimizes learning rates, tree depths, and regularization parameters using Optuna Bayesian search.", ["optuna_tuner", "trial_pruner", "hyperparam_visualizer"], "phi4-mini:latest", "wrench"),
            ("agent_118", "Model Explainability (SHAP/LIME)", "Feature Importance & Model Interpretability", "Explains machine learning predictions using SHAP values and feature attribution graphs.", ["shap_explainer", "feature_importance_plotter", "lime_interpreter"], "qwen2.5-coder:7b", "eye"),
            ("agent_119", "MLflow Experiment Tracking Agent", "Experiment Tracking & Artifact Versioning", "Logs hyperparameters, validation metrics, loss curves, and serialized model artifacts.", ["mlflow_tracker", "model_artifact_logger", "run_comparator"], "phi4-mini:latest", "clipboard-list"),
            ("agent_120", "Model Registry & Deployment Agent", "ONNX Serialization & Serving Gateway", "Exports trained ML models to ONNX runtime for ultra-fast, dependency-free local inference.", ["onnx_exporter", "runtime_benchmarker", "model_deployer"], "phi4-mini:latest", "box"),
            ("agent_121", "Data Drift & Concept Drift Agent", "Population Stability Index (PSI) Monitor", "Calculates PSI and Wasserstein distance to detect when real-world data drifts from training data.", ["psi_calculator", "wasserstein_metric", "drift_alert_system"], "phi4-mini:latest", "wind"),
            ("agent_122", "Synthetic Data Generation Agent", "Synthetic Banking Data & Faker Engine", "Generates mathematically consistent synthetic transactional datasets preserving realistic correlations.", ["faker_banking_engine", "copula_synthesizer", "privacy_preserver"], "phi4-mini:latest", "dice"),
            ("agent_123", "Human-Like Conversational Persona", "Empathy, Tone & Natural Demeanor Tuner", "Ensures AI Manager communicates with human warmth, proactive helpfulness, and professional respect.", ["persona_tuner", "empathy_score_evaluator", "tone_guard"], "qwen2.5-coder:7b", "user-check"),
            ("agent_124", "AI Agent Office 3D Visualizer", "Agent Activity State Machine & Telemetry", "Feeds live execution states and progress percentages to the interactive animated Office visualizer.", ["office_telemetry_bus", "state_machine_broadcaster", "canvas_sync"], "phi4-mini:latest", "cubes"),
            ("agent_125", "Free Public AI Tools Curator", "Internet AI Tools & Open-Source Scanner", "Scans GitHub and verified directories to discover free AI APIs and utilities for the Studio.", ["github_api_scanner", "public_api_catalog", "free_tier_verifier"], "phi4-mini:latest", "globe")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_g:
            agents_def.append((aid, name, "G", "AI, DL & MLOps", role, desc, tools, mdl, ico))

        # -------------------------------------------------------------------------
        # Group H: Cybersecurity, Threat Intel, Vault & IAM Security (Agents 126-140)
        # -------------------------------------------------------------------------
        group_h = [
            ("agent_126", "Credentials Vault Guardian", "AES-256-GCM Master Key & Secrets Vault", "Guarantees zero plain-text password leakage, enforces master key rotation, and secures vault DB.", ["aes_gcm_crypto", "master_key_resolver", "vault_auditor"], "qwen2.5-coder:7b", "key"),
            ("agent_127", "Network & Port Security Sentinel", "Port 1521, 443, 587 Firewall Inspector", "Audits local listening ports, verifies Windows firewall rules, and prevents unauthorized open ports.", ["socket_port_scanner", "firewall_auditor", "ip_allowlist_checker"], "phi4-mini:latest", "network-wired"),
            ("agent_128", "SQL Injection Sentinel Agent", "Query AST Linter & Parameterization Guard", "Inspects raw SQL queries to detect and block SQL injection vectors and unsanitized parameters.", ["ast_sql_linter", "sqli_detector", "parameterization_enforcer"], "qwen2.5-coder:7b", "shield-alt"),
            ("agent_129", "Secret Leak Prevention Agent", "Git & Log Secret Scanner (Gitleaks Rule)", "Scans code commits, patches, and logs to block API keys, passwords, and private certificates.", ["gitleaks_rule_scanner", "entropy_checker", "commit_gatekeeper"], "phi4-mini:latest", "user-lock"),
            ("agent_130", "IAM Least-Privilege Auditor", "AWS IAM & Snowflake Privilege Reviewer", "Audits IAM roles, flags wildcard ('*') permissions, and generates least-privilege policy updates.", ["iam_policy_analyzer", "wildcard_permission_linter", "least_privilege_fixer"], "qwen2.5-coder:7b", "id-badge"),
            ("agent_131", "Authentication & JWT Gatekeeper", "Session Authentication & Token Expiry", "Manages studio authentication sessions, verifies JWT signatures, and enforces automatic expiry.", ["jwt_verifier", "session_token_manager", "brute_force_blocker"], "phi4-mini:latest", "lock"),
            ("agent_132", "Cybersecurity Learning Lab Agent", "Interactive Defense Drills & Exploit Labs", "Presents cybersecurity training scenarios, OWASP Top 10 drills, and defense walkthroughs.", ["cyber_lab_curator", "owasp_scenario_builder", "defense_quiz_master"], "qwen2.5-coder:7b", "graduation-cap"),
            ("agent_133", "Vulnerability Scanner Agent", "Dependency CVE & Package Audit (pip audit)", "Scans Python requirements.txt against the National Vulnerability Database to flag CVEs.", ["pip_audit_scanner", "cve_nvd_fetcher", "patch_suggester"], "phi4-mini:latest", "bug"),
            ("agent_134", "Database TLS/SSL Inspector", "Encrypted Channel & Certificate Verifier", "Verifies TLS 1.3/1.2 cipher suites, certificate validity, and encryption in-transit for all DBs.", ["tls_cert_checker", "cipher_suite_linter", "ssl_handshake_tester"], "phi4-mini:latest", "certificate"),
            ("agent_135", "Data At-Rest Encryption Auditor", "AES Storage & Transparent Data Encryption", "Audits SQLite WAL encryption, Oracle TDE status, and AWS S3 SSE-KMS bucket policies.", ["tde_status_inspector", "s3_kms_auditor", "storage_encryption_checker"], "phi4-mini:latest", "hdd"),
            ("agent_136", "Zero-Trust Architecture Sentinel", "Continuous Verification & Mutual TLS", "Enforces zero-trust principles: never trust, always verify every agent, connection, and API call.", ["zero_trust_policy_lead", "caller_authenticator", "mTLS_verifier"], "qwen2.5-coder:7b", "user-shield"),
            ("agent_137", "Security Incident Response Lead", "Automated Threat Containment & Alerting", "Isolates compromised connection credentials, locks affected vault keys, and alerts Mangesh.", ["incident_responder", "quarantine_isolator", "urgent_sms_pager"], "qwen2.5-coder:7b", "exclamation-triangle"),
            ("agent_138", "Audit Log Tamper-Proofing Agent", "Cryptographic Hash Chaining on Logs", "Creates cryptographic SHA-256 hash chains across audit logs to prevent retroactive tampering.", ["hash_chain_signer", "log_tamper_detector", "audit_ledger_signer"], "phi4-mini:latest", "link"),
            ("agent_139", "IP Allowlisting & Geofencing Agent", "Authorized IP & Tailscale Subnet Router", "Restricts sensitive administrative API calls strictly to localhost (127.0.0.1) and Tailscale IPs.", ["ip_subnet_matcher", "geofence_checker", "access_logger"], "phi4-mini:latest", "globe-asia"),
            ("agent_140", "Security Compliance Officer", "ISO 27001 & SOC 2 Readiness Checklist", "Generates periodic compliance scorecards auditing encryption, access logs, and backup retention.", ["soc2_checklist_lead", "compliance_scorecard_maker", "evidence_collector"], "qwen2.5-coder:7b", "file-contract")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_h:
            agents_def.append((aid, name, "H", "Security & Governance", role, desc, tools, mdl, ico))

        # -------------------------------------------------------------------------
        # Group I: Cloud Infrastructure, SRE & DevSecOps (Agents 141-155)
        # -------------------------------------------------------------------------
        group_i = [
            ("agent_141", "Cloud Infrastructure Lead", "AWS & Hybrid Cloud Provisioning Architect", "Manages AWS S3, IAM, Lambda, EC2, and local hardware resources with clean configuration.", ["cloud_architect", "boto3_resource_lead", "hybrid_cloud_mapper"], "qwen2.5-coder:7b", "cloud"),
            ("agent_142", "Site Reliability Engineer (SRE)", "SLI, SLO & System Availability Sentinel", "Tracks Service Level Indicators, latency percentiles (p95/p99), and maintains 99.9% uptime.", ["sli_slo_tracker", "uptime_pinger", "latency_histogram"], "phi4-mini:latest", "heartbeat"),
            ("agent_143", "Storage & Disk Capacity Sentinel", "Disk Space & SQLite Vacuum Inspector", "Monitors free gigabytes, cleans temporary video render caches, and runs SQLite WAL vacuum.", ["disk_capacity_monitor", "cache_cleaner", "vacuum_scheduler"], "phi4-mini:latest", "hdd"),
            ("agent_144", "CPU & Thread Load Balancer", "Thread Pool & Multiprocessing Manager", "Allocates worker threads, balances CPU cores across video rendering, and prevents freezes.", ["thread_pool_manager", "core_affinity_setter", "task_throttler"], "phi4-mini:latest", "microchip"),
            ("agent_145", "FastAPI Service Health Agent", "REST Endpoint Latency & Status Monitor", "Pings internal FastAPI endpoints (/api/health, /api/status) and logs sub-millisecond response times.", ["http_health_prober", "endpoint_profiler", "status_card_updater"], "phi4-mini:latest", "exchange-alt"),
            ("agent_146", "Automated Backup & Disaster Recovery", "Daily Tarball Snapshots & Cloud Sync", "Generates daily compressed backups of studio_memory.db, reports, and configs with checksum verification.", ["backup_tarball_creator", "checksum_validator", "disaster_recovery_plan"], "phi4-mini:latest", "archive"),
            ("agent_147", "Container & Docker Specialist", "Dockerfile & Microservice Containerizer", "Creates lightweight container images, multi-stage Dockerfiles, and compose configurations.", ["dockerfile_generator", "container_sizer", "compose_linter"], "qwen2.5-coder:7b", "box"),
            ("agent_148", "CI/CD Pipeline Architect", "GitHub Actions & Automated Testing DAG", "Constructs GitHub Actions workflows running unit tests, linter checks, and automated builds.", ["github_actions_builder", "workflow_linter", "test_matrix_runner"], "qwen2.5-coder:7b", "code-branch"),
            ("agent_149", "Windows Service & Startup Lead", "Windows Task Scheduler & Batch Boot Lead", "Maintains run_studio.bat, startup scripts, and ensures automatic background restart upon reboot.", ["batch_script_lead", "service_startup_config", "reboot_recovery"], "phi4-mini:latest", "power-off"),
            ("agent_150", "Log Aggregator & Splunk Specialist", "Centralized Structured JSON Logging", "Aggregates studio component logs into unified JSON format with searchable timestamps.", ["json_log_aggregator", "grep_search_engine", "log_retention_policy"], "phi4-mini:latest", "stream"),
            ("agent_151", "API Rate Limit & Throttler Agent", "External API Rate Limit & Backoff Guard", "Enforces token-bucket rate limits on external APIs with exponential backoff and jitter.", ["token_bucket_limiter", "exponential_backoff", "quota_tracker"], "phi4-mini:latest", "tachometer-alt"),
            ("agent_152", "Environment & Config Sync Agent", ".env Secret Sync & Variable Validator", "Validates presence of all required .env variables on startup and checks syntax conformance.", ["env_validator", "config_synchronizer", "missing_var_alerter"], "phi4-mini:latest", "sliders-h"),
            ("agent_153", "Git Version Control Specialist", "Branching, Atomic Commits & Merge Lead", "Automates branch commits, generates semantic changelogs, and resolves code merge conflicts.", ["git_cli_lead", "semantic_commit_maker", "changelog_builder"], "qwen2.5-coder:7b", "code-commit"),
            ("agent_154", "Dependency & Wheel Lock Agent", "requirements.txt Version Pinning Specialist", "Pins deterministic library versions and creates standalone wheel archives for offline setup.", ["wheel_packager", "dependency_tree_resolver", "hash_pinning_lead"], "phi4-mini:latest", "lock"),
            ("agent_155", "Self-Diagnostic System Sentinel", "360-Degree Comprehensive Health Auditor", "Conducts periodic end-to-end diagnostics across databases, APIs, storage, and models.", ["system_diagnostic_lead", "component_health_matrix", "audit_report_issuer"], "qwen2.5-coder:7b", "tasks")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_i:
            agents_def.append((aid, name, "I", "Cloud Infra & SRE", role, desc, tools, mdl, ico))

        # -------------------------------------------------------------------------
        # Group J: Career, MNC HR Outreach & Job Hunting (Agents 156-170)
        # -------------------------------------------------------------------------
        group_j = [
            ("agent_156", "MNC Career Intelligence Lead", "Top MNC Job Scanner (Mumbai/Thane/Navi Mumbai)", "Discovers verified openings at TCS, LTI Mindtree, Infosys, Capgemini, Barclays, Morgan Stanley.", ["mnc_portal_scanner", "job_authenticity_validator", "career_db_sync"], "qwen2.5-coder:7b", "briefcase"),
            ("agent_157", "4-Hour Job Filter Radar Agent", "Automated 4-Hour Filter-Based Job Dispatcher", "Scans jobs every 4 hours matching 3-6 yrs exp, min 6-7 LPA, and broadcasts filtered lists to Telegram.", ["job_filter_radar", "hourly_cadence_engine", "telegram_job_broadcaster"], "qwen2.5-coder:7b", "radar"),
            ("agent_158", "6-Hour MNC HR Outreach Agent", "HR Resume & Application Dispatcher", "Prepares customized cover letters every 6 hours, attaches Mangesh's resume PDF, and tracks follow-ups.", ["hr_email_drafter", "resume_attachment_lead", "outreach_scheduler"], "qwen2.5-coder:7b", "paper-plane"),
            ("agent_159", "Data Engineering Resume Matcher", "JD vs Resume Matching & Scorecard (0-100%)", "Scores Job Descriptions against Mangesh's Utkarsh SFB experience (Snowflake, AWS, Python, Oracle).", ["jd_matcher_engine", "keyword_overlap_scorer", "match_badge_issuer"], "qwen2.5-coder:7b", "award"),
            ("agent_160", "Cover Letter & Pitch Synthesizer", "High-Impact Personalized Cover Letters", "Drafts personalized emails highlighting 4 years BFSI experience, 50GB daily deltas, and zero SLA breaches.", ["pitch_synthesizer", "bfsi_narrative_builder", "email_formatter"], "qwen2.5-coder:7b", "feather-alt"),
            ("agent_161", "HR Contact & Recruiter Directory", "Verified HR Directory & Follow-Up Calendar", "Maintains authenticated directory of corporate talent acquisition teams and schedules follow-up emails.", ["recruiter_directory", "followup_calendar", "sequence_tracker"], "phi4-mini:latest", "address-book"),
            ("agent_162", "LinkedIn Job & Post Scanner", "LinkedIn Data Engineer Post Investigator", "Monitors trending LinkedIn recruiter hiring posts and extracts direct hiring manager contact emails.", ["linkedin_post_scanner", "hiring_manager_finder", "post_summarizer"], "phi4-mini:latest", "linkedin"),
            ("agent_163", "Naukri & Portal Keyword Optimizer", "ATS Keyword Density & Search Visibility", "Optimizes resume keywords (Snowpipe, Medallion, CDC, Airflow) to score 98%+ on ATS screeners.", ["ats_keyword_optimizer", "search_ranking_tuner", "density_calculator"], "qwen2.5-coder:7b", "chart-line"),
            ("agent_164", "Technical Interview Q&A Coach", "4-Year Experience Scenario Interview Drills", "Drills scenario questions (SCD Type 2, OOM avoidance, Zero-Copy Clone recovery, query pruning).", ["interview_drill_coach", "scenario_answer_evaluator", "hint_generator"], "qwen2.5-coder:7b", "graduation-cap"),
            ("agent_165", "Snowflake Certification Coach", "SnowPro Core Certification Practice Exams", "Generates SnowPro Core mock questions with explanations on micro-partitioning and credit costs.", ["snowpro_drill_master", "exam_simulator", "weak_area_highlighter"], "qwen2.5-coder:7b", "certificate"),
            ("agent_166", "AWS Data Engineering Exam Coach", "AWS Certified Data Engineer (DEA-C01) Prep", "Generates DEA-C01 practice drills covering S3 Table Buckets, AWS Glue, DMS, and Lambda triggers.", ["aws_exam_drill_master", "cloud_architecture_quizzer", "score_tracker"], "qwen2.5-coder:7b", "aws"),
            ("agent_167", "Salary Benchmarking Specialist", "Compensation Trends & 12-24 LPA Pitch", "Analyzes Mumbai tech salary trends, advises on negotiation levers, and structures bonus proposals.", ["salary_benchmarker", "negotiation_pitch_advisor", "compensation_matrix"], "phi4-mini:latest", "coins"),
            ("agent_168", "Follow-Up Sequence Automator", "Polite 3-Day & 7-Day Follow-Up Sequences", "Schedules follow-up emails to recruiters after initial resume submission to maximize reply rates.", ["followup_sequencer", "polite_reminder_drafter", "response_tracker"], "phi4-mini:latest", "clock"),
            ("agent_169", "Portfolio & Project Presentation Lead", "Data Engineering GitHub Showcases", "Formats production data engineering architectures into professional portfolio markdown articles.", ["portfolio_curator", "readme_generator", "project_showcaser"], "qwen2.5-coder:7b", "folder-open"),
            ("agent_170", "Career Momentum & Goal Tracker", "Daily Application Targets & Interview Funnel", "Tracks daily application counts, recruiter phone screens, technical rounds, and offer stages.", ["application_funnel_tracker", "daily_goal_scorer", "milestone_notifier"], "phi4-mini:latest", "bullseye")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_j:
            agents_def.append((aid, name, "J", "Career & Job Outreach", role, desc, tools, mdl, ico))

        # -------------------------------------------------------------------------
        # Group K: Multi-Channel Communications (Agents 171-185)
        # -------------------------------------------------------------------------
        group_k = [
            ("agent_171", "Communications Dispatcher Lead", "Multi-Channel Delivery Orchestration", "Central gateway routing notifications to Telegram, WhatsApp, and Gmail SMTP with audit logging.", ["communication_center", "channel_router", "delivery_ledger_writer"], "qwen2.5-coder:7b", "broadcast-tower"),
            ("agent_172", "Multi-Account Telegram Manager", "Multi-Chat & Multi-Bot Telegram Routing", "Manages multiple Telegram accounts, chat IDs, channel broadcasts, and permission allowlists.", ["multi_telegram_router", "bot_token_manager", "chat_id_allocator"], "phi4-mini:latest", "telegram"),
            ("agent_173", "Free WhatsApp Automated Dispatcher", "1-Click WhatsApp Links & CallMeBot API", "Generates free wa.me instant delivery links and triggers automated WhatsApp text messages.", ["whatsapp_link_generator", "callmebot_client", "wa_template_formatter"], "phi4-mini:latest", "whatsapp"),
            ("agent_174", "Emergency Connection Alert Bot", "Urgent DB Failure Telegram Alert Dispatcher", "Dispatches immediate critical alerts to Telegram and WhatsApp when any connection goes down.", ["urgent_telegram_bot", "sms_pager_fallback", "failure_card_formatter"], "qwen2.5-coder:7b", "exclamation-circle"),
            ("agent_175", "Process-to-Recipient Mapping Agent", "Process Mail Routing & Configuration Lead", "Configures which process sends mail to whom, ensuring targeted delivery and zero inbox clutter.", ["process_routing_manager", "recipient_configurator", "routing_table_editor"], "phi4-mini:latest", "user-cog"),
            ("agent_176", "Delivery Audit Ledger Agent", "Immutable Dispatch History & Status Tracking", "Records every email, Telegram, and WhatsApp dispatch with recipient, subject, time, and status.", ["delivery_ledger_reader", "dispatch_auditor", "failure_rate_calculator"], "phi4-mini:latest", "book-open"),
            ("agent_177", "Gmail SMTP Specialist Agent", "STARTTLS Port 587 Authenticated Dispatcher", "Manages Gmail app password authentication, attachment encoding, and bounce-back detection.", ["smtp_client", "attachment_encoder", "email_bounce_detector"], "phi4-mini:latest", "envelope"),
            ("agent_178", "HTML Email Template Designer", "Lavish Responsive Dark-Mode Email Templates", "Designs responsive HTML email bodies with status pills, styled tables, and corporate branding.", ["html_email_renderer", "responsive_designer", "dark_mode_styler"], "qwen2.5-coder:7b", "palette"),
            ("agent_179", "Telegram Interactive Inline Bot", "Inline Button Commands & Instant Approval", "Renders interactive inline buttons (Approve, Reject, View Logs) directly inside Telegram messages.", ["inline_keyboard_builder", "callback_query_handler", "telegram_button_bot"], "qwen2.5-coder:7b", "gamepad"),
            ("agent_180", "Scheduled Digest Broadcaster", "Daily Morning & Evening 360° Broadcasts", "Compiles tech news, career updates, and pipeline statuses into automated scheduled broadcasts.", ["broadcast_compiler", "scheduled_sender", "multidomain_digest"], "phi4-mini:latest", "newspaper"),
            ("agent_181", "WhatsApp Notification Formatter", "Concise Emojified WhatsApp Alert Builder", "Formats long technical reports into crisp, readable WhatsApp messages with bullet points and bold text.", ["wa_text_cleaner", "emoji_annotator", "character_counter"], "phi4-mini:latest", "mobile-alt"),
            ("agent_182", "SMS Emergency Fallback Agent", "Critical Server Outage SMS Dispatcher", "Provides fallback SMS alerting infrastructure for critical internet or network disconnection.", ["sms_gateway_client", "urgent_pager_engine", "cell_network_probe"], "phi4-mini:latest", "sms"),
            ("agent_183", "Telegram Voice Memo Agent", "Voice Note Audio Broadcaster to Telegram", "Converts daily summaries to audio files and sends them as voice messages on Telegram.", ["voice_memo_recorder", "audio_file_uploader", "ogg_opus_encoder"], "phi4-mini:latest", "microphone-alt"),
            ("agent_184", "Communication Health Sentinel", "Delivery Latency & Success Rate Tracker", "Monitors delivery latency for all channels and alerts when an email or bot token is expired.", ["delivery_health_monitor", "token_expiry_watcher", "channel_heartbeat"], "phi4-mini:latest", "heartbeat"),
            ("agent_185", "Email Unsubscribe & Bounce Manager", "Hard/Soft Bounce Cleaner & Delivery Health", "Monitors bounce rates and cleans invalid recruiter email addresses automatically.", ["bounce_classifier", "suppression_list_manager", "reputation_guard"], "phi4-mini:latest", "user-times")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_k:
            agents_def.append((aid, name, "K", "Communications", role, desc, tools, mdl, ico))

        # -------------------------------------------------------------------------
        # Group L: Autonomous Task Schedulers, Crons & Recovery (Agents 186-195)
        # -------------------------------------------------------------------------
        group_l = [
            ("agent_186", "Task Scheduler Master Lead", "Windows Task Scheduler Alternative Lead", "Manages recurring Python, SQL, and Batch automations with start times, timeouts, and recurrence.", ["automation_scheduler", "task_crud_controller", "next_run_calculator"], "qwen2.5-coder:7b", "calendar-check"),
            ("agent_187", "Cron Expression Parser Agent", "5-Field & 6-Field Cron Grammar Evaluator", "Parses and validates standard cron syntax ('*/15 * * * *', '0 8 * * 1-5') and computes schedules.", ["cron_grammar_parser", "next_occurrence_finder", "schedule_validator"], "phi4-mini:latest", "clock"),
            ("agent_188", "Scheduled Task Editor Agent", "Interactive Task Modifier & Recurrence Tuner", "Provides complete editing capabilities to modify task names, scripts, connections, and schedules.", ["task_editor_modal", "update_task_controller", "recurrence_modifier"], "qwen2.5-coder:7b", "edit"),
            ("agent_189", "Execution Run-Log Auditor", "Stdout, Stderr & Exit Code History Tracker", "Records every task run with execution duration, stdout capture, stderr details, and exit codes.", ["task_run_logger", "stdout_stream_reader", "run_history_cleaner"], "phi4-mini:latest", "list"),
            ("agent_190", "Bounded Retry & Timeout Guard", "Infinite Loop Prevention & Exponential Backoff", "Enforces strict task execution timeouts and retries failed transient tasks with exponential delay.", ["timeout_watchdog", "retry_policy_enforcer", "infinite_loop_killer"], "phi4-mini:latest", "stopwatch"),
            ("agent_191", "Startup Scheduler Recovery Lead", "Crash Recovery & Interrupted Job Re-Queuer", "Inspects incomplete tasks upon studio startup and automatically restarts them without user input.", ["startup_recovery_engine", "interrupted_job_finder", "requeue_orchestrator"], "qwen2.5-coder:7b", "redo"),
            ("agent_192", "Task Dependency DAG Scheduler", "Multi-Stage Chained Workflow Execution", "Executes multi-task pipelines where Task B only runs after Task A succeeds with zero exit code.", ["dag_dependency_resolver", "stage_gatekeeper", "chain_executor"], "qwen2.5-coder:7b", "sitemap"),
            ("agent_193", "Manual 'Run-Now' Worker Agent", "Immediate Ad-Hoc Task Background Execution", "Spawns background worker thread executing scheduled tasks immediately upon manual trigger.", ["adhoc_job_runner", "thread_worker_spawner", "instant_feedback_bot"], "phi4-mini:latest", "play"),
            ("agent_194", "Task Pause & Resume Sentinel", "Active/Pause State Machine Controller", "Pauses scheduled automations during system maintenance and resumes them cleanly.", ["task_pause_controller", "resume_handler", "state_notifier"], "phi4-mini:latest", "pause"),
            ("agent_195", "Scheduler Health & SLA Reporter", "Scheduled Automation Success Rate Auditor", "Generates daily reports on scheduled task success rates, failed runs, and average runtimes.", ["scheduler_stats_reporter", "sla_auditor", "daily_schedule_card"], "phi4-mini:latest", "chart-pie")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_l:
            agents_def.append((aid, name, "L", "Schedulers & Crons", role, desc, tools, mdl, ico))

        # -------------------------------------------------------------------------
        # Group M: Daily Lifestyle, Tech News, Entertainment & Personal Ambience (Agents 196-205)
        # -------------------------------------------------------------------------
        group_m = [
            ("agent_196", "Entertainment & Cinema Lead", "Bollywood, Hollywood & OTT Streaming Releases", "Monitors latest releases on Netflix, Prime Video, Hotstar, and box-office collections.", ["entertainment_agent", "tmdb_free_api", "ott_release_tracker"], "phi4-mini:latest", "film"),
            ("agent_197", "Fashion & Lifestyle Specialist", "Men's Modern Style & Grooming Trends", "Curates modern men's executive fashion trends, wardrobe pairings, grooming, and lifestyle notes.", ["fashion_trends_curator", "lifestyle_advisor", "style_digest"], "phi4-mini:latest", "tshirt"),
            ("agent_198", "Tech News Live Sentinel", "Hacker News, TechCrunch & GitHub Trending", "Fetches breaking technology news, AI breakthroughs, cloud updates, and software releases.", ["news_agent", "hackernews_api", "rss_feed_reader"], "phi4-mini:latest", "laptop-code"),
            ("agent_199", "National & Maharashtra News Agent", "ABP Majha & Aaj Tak Verified News Monitor", "Hourly crawler monitoring verified news in Marathi and Hindi with dual-language summaries.", ["abp_majha_rss", "aaj_tak_rss", "marathi_translator"], "phi4-mini:latest", "newspaper"),
            ("agent_200", "Live Breaking News Sentinel", "Floating Alert System for Critical News", "Identifies breaking news alerts and pops up non-blocking notification cards in the studio UI.", ["breaking_news_detector", "toast_notification_bus", "importance_ranker"], "phi4-mini:latest", "bolt"),
            ("agent_201", "Good Morning Ambient Note Agent", "07:30 AM Morning Briefing & Weather", "Prepares encouraging morning note with weather forecast (Open-Meteo), priorities, and news.", ["morning_briefing_builder", "weather_api_client", "telegram_morning_bot"], "llama3.2:3b", "sun"),
            ("agent_202", "Good Evening Progress Note Agent", "06:30 PM Evening Recap & Pipeline Summary", "Prepares evening note reviewing completed data jobs, job application receipts, and evening news.", ["evening_summary_builder", "pipeline_status_scanner", "telegram_evening_bot"], "llama3.2:3b", "cloud-sun"),
            ("agent_203", "Good Night Peaceful Note Agent", "10:30 PM Nightly Sign-Off & System Calm", "Confirms all overnight maintenance schedules are primed, wishing Mangesh peaceful sleep.", ["night_note_builder", "night_schedule_verifier", "telegram_night_bot"], "llama3.2:3b", "moon"),
            ("agent_204", "Amazon Price Drop Tracker Agent", "E-Commerce Deal Intelligence & Alerting", "Monitors tracked Amazon India products, detects price cuts, and alerts on price drops.", ["price_tracker_agent", "amazon_catalog_matcher", "price_history_db"], "phi4-mini:latest", "tags"),
            ("agent_205", "Health, Ergonomics & Fitness Coach", "Desk Ergonomics & Hydration Prompts", "Suggests healthy posture breaks, hydration reminders, and mental clarity tips for data engineers.", ["ergonomics_advisor", "hydration_timer", "wellness_prompter"], "phi4-mini:latest", "heartbeat")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_m:
            agents_def.append((aid, name, "M", "Lifestyle & Ambience", role, desc, tools, mdl, ico))

        # =========================================================================
        # Group N: Defensive Cybersecurity & Red-Teaming (Agents 206-225, 20 Agents)
        # =========================================================================
        group_n = [
            ("agent_206", "Nmap Network & Port Auditor", "Defensive Port Auditing & Latency", "Performs defensive TCP SYN/connect scans to audit open service ports and protocols.", ["nmap_port_scanner", "socket_probe", "port_remediation_advisor"], "qwen2.5-coder:7b", "network-wired"),
            ("agent_207", "Wireshark PCAP Deep Packet Inspector", "Defensive Traffic Analysis & Cleartext Hunter", "Inspects packet flows, flags unencrypted protocols, and detects cleartext credential transmission.", ["pcap_analyzer", "traffic_anomaly_detector", "tls_compliance_evaluator"], "qwen2.5-coder:7b", "search"),
            ("agent_208", "OWASP ZAP Web Application Security Auditor", "API & Web Security Verification", "Audits endpoints against OWASP Top 10 vulnerabilities, verifying CSP, CORS, and header posture.", ["owasp_zap_scanner", "header_security_auditor", "cors_evaluator"], "qwen2.5-coder:7b", "shield-alt"),
            ("agent_209", "Garak LLM Vulnerability Prober", "Prompt Injection & Jailbreak Resilience", "Evaluates LLM inference pipelines against prompt overrides, DAN roleplays, and data leakage probes.", ["garak_llm_scanner", "prompt_injection_prober", "jailbreak_evaluator"], "qwen2.5-coder:7b", "user-secret"),
            ("agent_210", "PyRIT Generative AI Red-Teamer", "Multi-Turn Adversarial Attack Testing", "Executes multi-turn adversarial red-team prompt permutations to verify AI robustness.", ["pyrit_redteam_engine", "adversarial_prompt_tester", "robustness_scorer"], "qwen2.5-coder:7b", "skull-crossbones"),
            ("agent_211", "SQL Injection & AST AST Shield Agent", "Query Parameterization & Sanitization", "Verifies all SQL queries utilize parameterized bindings and validates syntax trees.", ["sql_ast_validator", "sqli_detector", "parameter_binding_checker"], "qwen2.5-coder:7b", "database"),
            ("agent_212", "Hardware BadUSB & HID Defense Monitor", "USB Device Authorization & Whitelist", "Monitors connected USB hardware, prevents unauthorized keystroke injection, and manages device locks.", ["badusb_guard", "usb_whitelist_manager", "device_id_verifier"], "phi4-mini:latest", "usb"),
            ("agent_213", "Enterprise WPA3 Wi-Fi Posture Auditor", "Wireless Cryptography & Rogue AP Guard", "Audits 192-bit WPA3 enterprise encryption, verifies PMF (802.11w), and detects rogue APs.", ["wifi_posture_scanner", "pmf_verifier", "rogue_ap_detector"], "phi4-mini:latest", "wifi"),
            ("agent_214", "Zero-Trust IAM & Vault Token Verifier", "Least Privilege & Token Lifecycle", "Inspects IAM policies, token expiration windows, and vault authorization boundaries.", ["iam_verifier", "token_lifecycle_guard", "least_privilege_auditor"], "phi4-mini:latest", "id-badge"),
            ("agent_215", "API Endpoint CORS & CSP Header Guardian", "Browser Defense Enforcement", "Monitors HTTP response headers across all FastAPI endpoints to enforce strict CSP.", ["header_guardian", "csp_policy_builder", "xfo_enforcer"], "phi4-mini:latest", "lock"),
            ("agent_216", "Raspberry Pi 5 Edge Linux Hardening Specialist", "Single-Board Computer OS Hardening", "Hardens Debian Bookworm on Raspberry Pi 5, disables root logins, and enforces SSH keys.", ["rpi5_hardener", "ssh_config_auditor", "gpio_access_controller"], "phi4-mini:latest", "microchip"),
            ("agent_217", "ESP32-S3 IoT Secure Boot & Flash Encryption Auditor", "Microcontroller Firmware Defense", "Verifies RSA-3072 firmware signatures, XTS-AES-256 flash encryption, and TLS certificate pins.", ["esp32_firmware_auditor", "secure_boot_verifier", "flash_encryption_guard"], "phi4-mini:latest", "memory"),
            ("agent_218", "AI HAT+ 2 Edge PCIe Bus Integrity Inspector", "Hailo NPU Bus Security & DMA Isolation", "Audits PCIe Gen 3 bus communications and memory isolation for the Raspberry Pi AI HAT+ 2.", ["ai_hat_inspector", "pcie_dma_isolator", "hailo_thermal_monitor"], "phi4-mini:latest", "tachometer-alt"),
            ("agent_219", "Threat Intel MITRE ATT&CK Mapper", "Adversarial Tactics Categorization", "Maps observed system and network anomalies to standard MITRE ATT&CK enterprise techniques.", ["mitre_mapper", "threat_intel_correlator", "tactics_analyzer"], "qwen2.5-coder:7b", "crosshairs"),
            ("agent_220", "Secret Scanner & Git Repository Auditor", "Hardcoded Secret & Key Exfiltration Guard", "Scans repository commits and configuration files for exposed API keys and secrets.", ["secret_scanner", "git_repo_auditor", "entropy_checker"], "qwen2.5-coder:7b", "key"),
            ("agent_221", "Cryptographic Key Rotator & Vault Guardian", "AES-256-GCM Master Key Governance", "Oversees authenticated AES-256-GCM key rotation and HMAC verification in the Credentials Vault.", ["vault_key_rotator", "aes_gcm_verifier", "crypto_audit_logger"], "qwen2.5-coder:7b", "user-shield"),
            ("agent_222", "Docker & Container Runtime Security Inspector", "Container Isolation & Image Scanning", "Audits container configurations, non-root users, read-only root filesystems, and minimal images.", ["container_security_scanner", "cgroup_isolator", "dockerfile_linter"], "phi4-mini:latest", "docker"),
            ("agent_223", "Honeypot & Intrusion Detection Analyzer", "Deceptive Defense & Network Traps", "Monitors decoys and synthetic endpoints to catch unauthorized port probes instantly.", ["honeypot_monitor", "ids_correlator", "probe_alert_dispatcher"], "phi4-mini:latest", "eye"),
            ("agent_224", "Privilege Escalation & RBAC Boundary Verifier", "Role Separation & Sudo Rule Auditor", "Verifies strict role separation between Studio User, Data Engineer, and SOC Administrator.", ["rbac_boundary_verifier", "sudoers_auditor", "privilege_checker"], "phi4-mini:latest", "user-check"),
            ("agent_225", "SOC Incident Response & Telegram Alert Dispatcher", "Automated Security Incident Alerting", "Pipes critical security events, port anomalies, and vault modification notices to Telegram.", ["soc_incident_router", "telegram_urgent_dispatcher", "incident_ledger"], "phi4-mini:latest", "exclamation-triangle")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_n:
            agents_def.append((aid, name, "N", "Cybersecurity & Red-Teaming", role, desc, tools, mdl, ico))

        # =========================================================================
        # Group O: Advanced Data Architecture & Multi-Cloud Lakehouse (Agents 226-245, 20 Agents)
        # =========================================================================
        group_o = [
            ("agent_226", "Snowflake Micro-Partition Clustered Storage Optimizer", "Micro-Partitioning & Clustering Keys", "Analyzes clustering depth, reclustering cost, and columnar compression efficiency in Snowflake.", ["snowflake_clustering_advisor", "partition_depth_analyzer", "storage_optimizer"], "qwen2.5-coder:7b", "snowflake"),
            ("agent_227", "Dynamic Tables & Declarative Stream Processor", "Continuous Data Transformations", "Configures Snowflake Dynamic Tables with target lag intervals to replace complex tasks.", ["dynamic_table_manager", "target_lag_calculator", "stream_evaluator"], "qwen2.5-coder:7b", "sync"),
            ("agent_228", "Apache Iceberg & Delta Lake Parquet Formatter", "Open Table Formats & Metadata", "Formats parquet datasets with Iceberg metadata, snapshot manifests, and column statistics.", ["iceberg_formatter", "parquet_snappy_compressor", "manifest_builder"], "qwen2.5-coder:7b", "cubes"),
            ("agent_229", "Oracle XE Undo/Redo Log CDC Streamer", "Transaction Log Mining & Extraction", "Extracts committed delta transactions from Oracle LogMiner and publishes to S3 lake buffers.", ["oracle_logminer_streamer", "redo_log_parser", "cdc_delta_buffer"], "qwen2.5-coder:7b", "database"),
            ("agent_230", "AWS S3 Express One Zone Latency Accelerator", "Sub-10ms Object Storage Buffering", "Routes low-latency staging datasets through AWS S3 Express One Zone buckets.", ["s3_express_router", "latency_benchmarker", "bucket_tiering_engine"], "phi4-mini:latest", "bolt"),
            ("agent_231", "Medallion L0-to-L1 Quality Harmonization Agent", "Bronze to Silver Cleansing", "Deduplicates raw banking records, handles null imputation, and applies conformed schemas.", ["l0_l1_harmonizer", "ast_cleaner", "schema_conformity_checker"], "qwen2.5-coder:7b", "filter"),
            ("agent_232", "Medallion L1-to-L2 Star Schema Aggregator", "Silver to Gold Dimensional Modeling", "Aggregates silver records into facts, conforms dimensions, and constructs high-speed marts.", ["l1_l2_star_aggregator", "dimension_conformer", "fact_builder"], "qwen2.5-coder:7b", "project-diagram"),
            ("agent_233", "SCD Type 2 Temporal Validity Engine", "Slowly Changing Dimensions (History Tracking)", "Tracks valid_from, valid_to, is_current flags and MD5/SHA256 checksums on customer profiles.", ["scd2_temporal_engine", "checksum_evaluator", "historical_record_closer"], "qwen2.5-coder:7b", "history"),
            ("agent_234", "Snowpipe Continuous Ingestion Overseer", "Automated S3 Notification Ingestion", "Monitors SQS-backed Snowpipe pipes, file queuing delays, and auto-ingest credit usage.", ["snowpipe_overseer", "sqs_event_listener", "ingest_cost_tracker"], "phi4-mini:latest", "stream"),
            ("agent_235", "Multi-DB Federated Join & Python Sandbox Executor", "Cross-Database Aggregations", "Executes federated cross-database joins across Oracle XE, Snowflake, and SQLite via Python Pandas.", ["federated_join_engine", "pandas_sandbox_runner", "cross_db_mapper"], "qwen2.5-coder:7b", "link"),
            ("agent_236", "Pre-Execution Schema Validator & Error Preventer", "Query Catalog Pre-Check", "Introspects table existence and column types prior to execution, preventing runtime syntax failures.", ["catalog_pre_checker", "schema_mismatch_preventer", "table_existence_validator"], "qwen2.5-coder:7b", "check-circle"),
            ("agent_237", "Data Lineage Graph & Column Impact Analyzer", "End-to-End Lineage & Governance", "Maps data provenance from Oracle source tables through S3 to Snowflake analytical views.", ["data_lineage_grapher", "column_impact_analyzer", "provenance_tracker"], "qwen2.5-coder:7b", "sitemap"),
            ("agent_238", "Data Warehouse Cost & Virtual Compute Throttler", "Snowflake Credit Governance", "Auto-suspends idle compute warehouses and alerts when credit consumption exceeds daily budgets.", ["warehouse_cost_throttler", "credit_budget_monitor", "auto_suspend_enforcer"], "phi4-mini:latest", "coins"),
            ("agent_239", "Automated Excel Financial Recon Dispatched Agent", "T-1 Reconciliation & Spreadsheet Dispatch", "Generates styled multi-tab Excel workbooks and dispatches them via SMTP to finance leaders.", ["excel_recon_generator", "smtp_dispatch_client", "financial_formula_stamper"], "phi4-mini:latest", "file-excel"),
            ("agent_240", "Database User & Role Provisioning Controller", "Database RBAC & Privilege Grants", "Provisions and revokes least-privilege roles and users across Oracle XE and Snowflake.", ["db_role_provisioner", "privilege_grant_auditor", "user_lifecycle_mgr"], "phi4-mini:latest", "user-cog"),
            ("agent_241", "AWS DMS Replication Latency & Throughput Monitor", "Replication Health & CDC Lag", "Tracks AWS Database Migration Service CDC latency, record throughput, and endpoint health.", ["dms_latency_monitor", "replication_health_checker", "cdc_lag_alerting"], "phi4-mini:latest", "chart-line"),
            ("agent_242", "Sample Record Extractor & Test Verification Agent", "Rapid Test Sampling", "Extracts top sample rows across tables for instant interactive UI verification without full scans.", ["sample_record_extractor", "table_peek_runner", "schema_sampler"], "phi4-mini:latest", "eye"),
            ("agent_243", "Cross-Cloud Multi-Master Replication Guard", "Multi-Region Replication Integrity", "Verifies conflict-free multi-master data synchronization across cloud providers.", ["multi_master_guard", "conflict_resolver", "data_consistency_evaluator"], "qwen2.5-coder:7b", "globe"),
            ("agent_244", "Lakehouse Disaster Recovery & Fail-Safe Auditor", "Time Travel & Zero-Copy Backup", "Monitors Snowflake 90-day Time Travel retention and tests instantaneous zero-copy clones.", ["time_travel_auditor", "fail_safe_verifier", "zero_copy_clone_tester"], "phi4-mini:latest", "shield-virus"),
            ("agent_245", "Data Mesh Governance & Domain Contract Verifier", "Federated Domain Data Contracts", "Enforces strict JSON schema data contracts between upstream BFSI sources and downstream consumers.", ["data_contract_verifier", "domain_mesh_governor", "schema_compatibility_checker"], "qwen2.5-coder:7b", "file-contract")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_o:
            agents_def.append((aid, name, "O", "Multi-Cloud Lakehouse", role, desc, tools, mdl, ico))

        # =========================================================================
        # Group P: Autonomous Career & Global MNC Outreach (Agents 246-260, 15 Agents)
        # =========================================================================
        group_p = [
            ("agent_246", "BFSI Banking Domain Career Matcher", "Financial Data Engineering Alignment", "Matches candidate background in Utkarsh SFB with high-paying BFSI Data Engineering roles.", ["bfsi_career_matcher", "banking_skills_evaluator", "jd_alignment_scorer"], "llama3.2:3b", "landmark"),
            ("agent_247", "Genuine Job Authenticity & Anti-Scam Verifier", "ATS & Domain Legitimacy Audit", "Validates corporate career portals, checks ATS domains (iON, Workday), and flags scam postings.", ["anti_scam_job_verifier", "ats_domain_checker", "corporate_email_validator"], "phi4-mini:latest", "check-double"),
            ("agent_248", "ATS Resume Parser & Keyword Optimization Specialist", "Resume ATS Score Booster", "Scores candidate resume against target JD keywords to achieve 95%+ ATS passing rate.", ["ats_keyword_optimizer", "resume_scoring_engine", "bullet_point_enhancer"], "llama3.2:3b", "file-alt"),
            ("agent_249", "Mumbai & Navi Mumbai Tech Events Radar Monitor", "Regional Tech Summit Scouting", "Tracks upcoming developer conferences and cloud summits across Mumbai, Thane, and Navi Mumbai.", ["mumbai_events_radar", "summit_scraper", "event_agenda_parser"], "phi4-mini:latest", "calendar-alt"),
            ("agent_250", "Jio World Centre Snowflake & AWS Summit Tracker", "Premier Venue Conference Radar", "Monitors major summits at Jio World Convention Centre (BKC) and automates ticket reminders.", ["jio_world_summit_tracker", "bkc_conference_monitor", "summit_alert_broadcaster"], "phi4-mini:latest", "building"),
            ("agent_251", "4-Hour Automated Career Discovery & Telegram Broadcaster", "Scheduled Job Alert Stream", "Executes 4-hour job portal scans and broadcasts formatted career radar summaries to Telegram.", ["career_4hr_scheduler", "telegram_job_broadcaster", "freshness_ranker"], "phi4-mini:latest", "paper-plane"),
            ("agent_252", "Personalized HR Email Drafter & Attachment Verifier", "Outreach Email Crafting", "Drafts personalized outreach emails to recruiters, automatically verifying resume PDF attachments.", ["hr_email_drafter", "pdf_attachment_verifier", "outreach_customizer"], "llama3.2:3b", "envelope-open-text"),
            ("agent_253", "Rejection Ratio & Interview Pipeline Analytics Agent", "Application Conversion Metrics", "Analyzes application outcomes, interview conversion ratios, and rejection telemetry.", ["rejection_ratio_analyzer", "pipeline_conversion_tracker", "application_kpi_dashboard"], "phi4-mini:latest", "chart-pie"),
            ("agent_254", "LinkedIn Data Engineering Post & Architecture Creator", "Professional Thought Leadership", "Generates high-engagement LinkedIn posts on Snowflake, Airflow, and Lakehouse best practices.", ["linkedin_post_generator", "code_snippet_formatter", "engagement_booster"], "llama3.2:3b", "linkedin"),
            ("agent_255", "Technical Scenario Interview Practice Simulator", "4-Year Experience BFSI Interview Drills", "Simulates rigorous scenario-based interview questions on Finacle migrations, CDC, and ACID locks.", ["interview_drill_simulator", "scenario_question_generator", "answer_evaluator"], "qwen2.5-coder:7b", "chalkboard-teacher"),
            ("agent_256", "Government & Public Sector Banking Career Radar", "SBI, NPCI, SEBI & PSU Openings", "Tracks Specialist Officer Data Engineering openings in public sector banks and institutions.", ["psu_career_radar", "npci_job_monitor", "sbi_so_recruitment_tracker"], "phi4-mini:latest", "university"),
            ("agent_257", "Startup & High-Growth FinTech Job Scout", "Zepto, Groww, Pine Labs Opportunities", "Finds high-equity, high-growth startup data engineering openings in Mumbai and remote.", ["fintech_startup_scout", "high_growth_job_finder", "equity_compensation_calculator"], "phi4-mini:latest", "rocket"),
            ("agent_258", "Salary Benchmark & Compensation Range Analyzer", "Market Pay Telemetry (₹12-24 LPA)", "Analyzes salary trends across Mumbai for 4-year experience Snowflake and AWS Data Engineers.", ["salary_benchmark_engine", "compensation_analyzer", "ctc_negotiation_advisor"], "phi4-mini:latest", "rupee-sign"),
            ("agent_259", "Automated HR Follow-Up Scheduler & Response Monitor", "Cadence Follow-Up Engine", "Schedules polite follow-up messages 5 days after application dispatch, tracking response status.", ["hr_followup_scheduler", "response_sentiment_detector", "cadence_reminder_bus"], "phi4-mini:latest", "reply-all"),
            ("agent_260", "Multi-Format Resume PDF/DOCX Formatter & Vault Storage Agent", "Resume Generation & Versioning", "Compiles Mangesh Bagul's master profile into clean, ATS-optimized PDF and Word versions.", ["resume_pdf_compiler", "docx_resume_builder", "resume_vault_archiver"], "phi4-mini:latest", "file-pdf")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_p:
            agents_def.append((aid, name, "P", "Career & Global Outreach", role, desc, tools, mdl, ico))

        # =========================================================================
        # Group Q: E-Commerce, Price Intelligence & Crypto Asset Analytics (Agents 261-275, 15 Agents)
        # =========================================================================
        group_q = [
            ("agent_261", "Amazon vs Flipkart Cross-Platform Price Matcher", "Multi-Vendor Deal Comparison", "Compares identical tech items across Amazon India and Flipkart, computing instant savings.", ["amazon_flipkart_matcher", "savings_calculator", "cross_platform_diff"], "phi4-mini:latest", "balance-scale"),
            ("agent_262", "Weekly Price Drop & Lowest Historical Cost Detector", "Price History Intelligence", "Detects when product pricing reaches 30-day or 90-day historic lows, triggering buy alerts.", ["price_drop_detector", "historical_low_alerting", "volatility_tracker"], "phi4-mini:latest", "arrow-circle-down"),
            ("agent_263", "Tech Hardware Deal Poster & Visual Spec Generator", "Hardware Specs & Deal Posters", "Generates high-resolution deal summaries with ratings, specs, and price-drop percentages.", ["deal_poster_generator", "hardware_spec_parser", "poster_card_formatter"], "phi4-mini:latest", "image"),
            ("agent_264", "Bitcoin Blockchain Live Price Ticker & Market Monitor", "Real-Time BTC Market Rates", "Queries live CoinGecko and Blockchain.info APIs to track Bitcoin spot prices in USD and INR.", ["btc_price_ticker", "coingecko_client", "inr_usd_fx_converter"], "phi4-mini:latest", "bitcoin"),
            ("agent_265", "SegWit & Taproot Wallet Address Generator & Vault Guard", "Cryptographic Address Governance", "Generates native SegWit (Bech32) and Taproot addresses, storing private keys in Vault.", ["btc_address_generator", "segwit_encoder", "keypair_vault_storage"], "qwen2.5-coder:7b", "wallet"),
            ("agent_266", "Mempool Recommended Fee Rate Telemetry Specialist", "Sat/vB Dynamic Estimation", "Fetches fastest, half-hour, and hour fee rate recommendations from mempool.space.", ["mempool_fee_fetcher", "vsize_calculator", "miner_fee_estimator"], "phi4-mini:latest", "gas-pump"),
            ("agent_267", "Cryptographic Transaction Simulator & TXID Verifier", "TX Construction & Broadcast", "Simulates transaction input/output selection, change outputs, and generates valid double-SHA256 TXIDs.", ["tx_simulator", "txid_generator", "utxo_spender"], "qwen2.5-coder:7b", "receipt"),
            ("agent_268", "Multi-Currency Valuation Engine (BTC to USD/INR)", "Crypto-Fiat Real-Time Converter", "Calculates instantaneous fiat valuations for crypto balances and transactional fee outlays.", ["crypto_fiat_calculator", "realtime_fx_engine", "portfolio_evaluator"], "phi4-mini:latest", "exchange-alt"),
            ("agent_269", "UTXO Ledger Auditor & Balance Reconciler", "Unspent Transaction Output Accounting", "Maintains an unspent transaction output ledger in SQLite, validating confirmed confirmations.", ["utxo_ledger_auditor", "balance_reconciler", "block_confirmation_tracker"], "phi4-mini:latest", "book"),
            ("agent_270", "E-Commerce Price Volatility & Trend Forecaster", "Price Prediction & Timing Advisor", "Analyzes price trends over 60 days to advise whether to purchase now or wait for festival sales.", ["price_trend_forecaster", "sale_timing_advisor", "discount_cycle_predictor"], "phi4-mini:latest", "chart-line"),
            ("agent_271", "ASIN & Flipkart FSN Product Identifier Resolver", "Catalog Barcode & SKU Matcher", "Resolves Amazon 10-char ASINs and Flipkart FSN identifiers to map exact hardware models.", ["asin_resolver", "fsn_matcher", "sku_unifier"], "phi4-mini:latest", "barcode"),
            ("agent_272", "Deal Alert Telegram & Email Instant Notification Agent", "Omnichannel Deal Broadcasting", "Pipes significant price cuts (10%+ drops) instantly to Telegram and email.", ["deal_telegram_notifier", "price_alert_mailer", "priority_deal_flag"], "phi4-mini:latest", "bell"),
            ("agent_273", "Lightning Network & Layer-2 Scalability Researcher", "Bitcoin Layer-2 Channel Analysis", "Researches micro-payment channel capacity, routing fees, and Lightning Network developments.", ["lightning_channel_monitor", "l2_scalability_researcher", "routing_fee_tracker"], "phi4-mini:latest", "bolt"),
            ("agent_274", "Hardware Component Availability & Supply Chain Scout", "In-Stock Tracker for GPUs & RPi", "Monitors inventory levels for Raspberry Pi 5 boards, NVMe SSDs, and edge accelerators.", ["stock_availability_scout", "inventory_checker", "backorder_notifier"], "phi4-mini:latest", "boxes"),
            ("agent_275", "Financial Transaction Receipt & Audit Log Maintainer", "Crypto Accounting Ledger", "Generates signed transaction receipts for all payment simulations and maintains an audit log.", ["tx_receipt_generator", "crypto_audit_logger", "tax_accounting_ledger"], "phi4-mini:latest", "file-invoice-dollar")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_q:
            agents_def.append((aid, name, "Q", "Price & Crypto Assets", role, desc, tools, mdl, ico))

        # =========================================================================
        # Group R: IoT, Hardware Edge & Embedded Intelligence (Agents 276-290, 15 Agents)
        # =========================================================================
        group_r = [
            ("agent_276", "Raspberry Pi 5 BCM2712 Quad-Core Performance Monitor", "Edge CPU & Clock Frequency Telemetry", "Monitors ARM Cortex-A76 core frequencies, governor states, and CPU loads on Raspberry Pi 5.", ["rpi5_cpu_monitor", "frequency_governor_tuner", "core_load_tracker"], "phi4-mini:latest", "microchip"),
            ("agent_277", "ESP32-S3 Xtensa LX7 Dual-Core Microcontroller Controller", "Embedded IoT Firmware Orchestrator", "Interfaces with ESP32-S3 microcontrollers via serial UART and Wi-Fi WebSockets.", ["esp32_uart_controller", "gpio_pin_manager", "sensor_packet_receiver"], "phi4-mini:latest", "wifi"),
            ("agent_278", "Raspberry Pi AI HAT+ 2 Edge NPU Inference Manager", "Hailo-8 26 TOPS AI Processing", "Deploys INT8 neural network models onto the 26 TOPS Hailo-8 edge processor via PCIe.", ["hailo_model_deployer", "npu_fps_benchmarker", "pcie_throughput_monitor"], "qwen2.5-coder:7b", "brain"),
            ("agent_279", "I2C, SPI & GPIO Hardware Sensor Data Streamer", "Bus Protocol Interface", "Reads BMP280, BME680, and MPU6050 environmental and motion sensors over I2C/SPI buses.", ["i2c_bus_reader", "spi_streamer", "sensor_calibration_engine"], "phi4-mini:latest", "wave-square"),
            ("agent_280", "MicroPython & CircuitPython Edge Script Deployer", "Embedded Python Code Uploader", "Uploads, compiles, and restarts Python automation scripts on microcontrollers over USB CDC.", ["micropython_uploader", "repl_command_runner", "firmware_fs_manager"], "qwen2.5-coder:7b", "code"),
            ("agent_281", "Edge Thermal Telemetry & Dynamic Fan Curve Controller", "Hardware Cooling & Throttling Guard", "Reads SoC thermistor sensors and dynamically modulates PWM fan speeds to prevent throttling.", ["thermal_telemetry_reader", "pwm_fan_controller", "throttling_preventer"], "phi4-mini:latest", "fan"),
            ("agent_282", "Hardware PCIe Bus Throughput & DMA Transfer Validator", "High-Speed Bus Benchmarking", "Validates PCIe Gen 2/3 x1 packet latency and Direct Memory Access (DMA) transfer rates.", ["pcie_bus_benchmarker", "dma_transfer_validator", "bus_error_counter"], "phi4-mini:latest", "hdd"),
            ("agent_283", "MQTT Broker & Edge Telemetry Ingestion Bridge", "Lightweight Pub/Sub Telemetry", "Ingests lightweight JSON sensor metrics from ESP32 nodes into NanoPro's central SQLite store.", ["mqtt_client_bridge", "telemetry_json_unpacker", "sensor_history_db"], "phi4-mini:latest", "broadcast-tower"),
            ("agent_284", "Tailscale WireGuard Edge Mesh Node Manager", "Secure P2P Edge Networking", "Monitors WireGuard mesh tunnels to ensure headless Raspberry Pi nodes remain reachable anywhere.", ["tailscale_mesh_monitor", "wireguard_key_verifier", "peer_latency_pinger"], "phi4-mini:latest", "network-wired"),
            ("agent_285", "Low-Power Sleep Mode & Battery Conservation Agent", "Deep Sleep & RTC Wakeup Manager", "Configures ESP32 deep-sleep cycles and external interrupt wakeups for battery deployments.", ["deep_sleep_configurator", "battery_voltage_monitor", "power_budget_calculator"], "phi4-mini:latest", "battery-three-quarters"),
            ("agent_286", "Edge Camera Feed & Visual Detection Orchestrator", "CSI-2 Camera & Edge Computer Vision", "Processes local camera feeds on the AI HAT+ 2 for edge motion and object detection.", ["csi_camera_streamer", "yolo_edge_detector", "motion_bounding_box"], "qwen2.5-coder:7b", "video"),
            ("agent_287", "Hardware Interrupt & Real-Time Event Dispatcher", "Sub-Millisecond Event Dispatcher", "Handles physical GPIO button presses and sensor interrupts, triggering NanoPro automated flows.", ["gpio_interrupt_listener", "event_queue_dispatcher", "debounce_filter"], "phi4-mini:latest", "toggle-on"),
            ("agent_288", "Firmware OTA Checksum & Cryptographic Verification Agent", "Over-The-Air Firmware Security", "Verifies SHA-256 binary checksums before executing over-the-air firmware updates.", ["ota_checksum_verifier", "firmware_flasher", "rollback_guard"], "phi4-mini:latest", "cloud-upload-alt"),
            ("agent_289", "Edge Model Quantization (INT8/FP16) Optimizer", "Model Compression for Edge NPU", "Converts heavy ONNX/PyTorch models into quantized Hailo HEF and TFLite formats.", ["model_quantizer", "onnx_to_hef_converter", "quantization_loss_evaluator"], "qwen2.5-coder:7b", "compress-arrows-alt"),
            ("agent_290", "Physical Hardware Health & Diagnostics Watchdog", "Hardware Self-Test & Diagnostic Reporter", "Executes periodic hardware self-tests, validating I2C addresses, power rails, and storage media.", ["hardware_diagnostics_runner", "power_rail_checker", "smart_disk_monitor"], "phi4-mini:latest", "stethoscope")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_r:
            agents_def.append((aid, name, "R", "Hardware Edge & IoT", role, desc, tools, mdl, ico))

        # =========================================================================
        # Group S: Media, News Summarization & Omnichannel Broadcast (Agents 291-305, 15 Agents)
        # =========================================================================
        group_s = [
            ("agent_291", "ABP Majha Marathi News Synthesizer & Local Audio Agent", "Marathi News & Audio Briefing", "Synthesizes regional breaking news from ABP Majha into audio summaries and Marathi text digests.", ["abp_majha_scraper", "marathi_tts_synthesizer", "local_news_summarizer"], "llama3.2:3b", "newspaper"),
            ("agent_292", "Aaj Tak Hindi Breaking News & Video Summary Curator", "Hindi National News Summarizer", "Curates top national news stories from Aaj Tak with dual-language Hindi/English bullets.", ["aaj_tak_scraper", "hindi_news_summarizer", "bullet_digest_builder"], "llama3.2:3b", "tv"),
            ("agent_293", "Tech & AI World Live Bulletin Dispatcher", "AI Research & Open-Weight News", "Tracks Hacker News, GitHub trending, and ArXiv, publishing hourly technology updates.", ["tech_bulletin_dispatcher", "arxiv_ai_monitor", "github_trending_fetcher"], "phi4-mini:latest", "satellite-dish"),
            ("agent_294", "Entertainment, Movies & Lifestyle Digest Curator", "Box Office & OTT Stream Releases", "Curates trending movies, upcoming OTT streams on Prime/Netflix, and weekend entertainment.", ["entertainment_digest_curator", "tmdb_api_client", "box_office_tracker"], "phi4-mini:latest", "film"),
            ("agent_295", "Morning, Evening & Night Manager Note Ambient Voice Agent", "Personal Ambient Voice Greeter", "Synthesizes warm, encouraging audio greetings and status reports for Mangesh morning/night.", ["ambient_voice_greeter", "tts_voice_modulator", "greeting_script_builder"], "llama3.2:3b", "microphone"),
            ("agent_296", "Telegram 56-Domain Topic Broadcast Router", "Multi-Topic Channel Broadcast", "Routes messages across 56 distinct topic channels (Tech, Jobs, Cyber, DB, Weather, News).", ["telegram_topic_router", "chat_id_mapper", "markdown_broadcast_formatter"], "phi4-mini:latest", "paper-plane"),
            ("agent_297", "WhatsApp Free Messaging & Direct Web API Dispatcher", "Free WhatsApp Notification Hub", "Dispatches WhatsApp alert links via wa.me format and CallMeBot free API without paid keys.", ["whatsapp_direct_dispatcher", "callmebot_client", "wa_me_link_generator"], "phi4-mini:latest", "whatsapp"),
            ("agent_298", "Gmail SMTP Process-to-Recipient Smart Mail Router", "Intelligent Email Dispatch Routing", "Maps individual background processes (ETL, Price, Cyber, Jobs) to configured email recipients.", ["smtp_process_router", "recipient_policy_manager", "email_dispatch_engine"], "phi4-mini:latest", "mail-bulk"),
            ("agent_299", "Omnichannel Communication Log & Delivery Status Auditor", "Delivery Tracking & Communication History", "Logs all Telegram, WhatsApp, and Email transmissions in a unified database ledger.", ["comm_log_auditor", "delivery_status_tracker", "omnichannel_ledger_mgr"], "phi4-mini:latest", "clipboard-list"),
            ("agent_300", "Live RSS Feed Aggregator & Deduplication Engine", "News Feed Aggregation", "Parses XML/RSS news feeds from 20+ outlets, deduplicating repetitive headlines automatically.", ["rss_feed_aggregator", "headline_deduplicator", "feed_frequency_controller"], "phi4-mini:latest", "rss"),
            ("agent_301", "Marathi & Hindi Natural Language Translation Specialist", "Bilingual Translation Engine", "Translates technical and analytical reports into natural Marathi (मराठी) and Hindi (हिंदी).", ["bilingual_translator", "marathi_nlp_engine", "hindi_nlp_engine"], "llama3.2:3b", "language"),
            ("agent_302", "Audio Text-to-Speech Voice Synthesis Quality Controller", "Audio Quality & Intelligibility", "Audits generated WAV/MP3 speech output for clarity, pitch, natural pacing, and volume.", ["tts_quality_auditor", "audio_spectrum_evaluator", "speech_pacing_tuner"], "phi4-mini:latest", "volume-up"),
            ("agent_303", "Social Media Post Visual Poster & Graphic Generator", "Posters, Reels & Thumbnail Visuals", "Generates visual asset banners and post diagrams for LinkedIn, YouTube, and Telegram.", ["social_graphic_generator", "banner_canvas_styler", "visual_asset_builder"], "phi4-mini:latest", "paint-brush"),
            ("agent_304", "Daily Briefing Podcast & Audio Synthesizer", "Autonomous Daily Audio Digest", "Combines weather, schedule, critical jobs, and top news into a 3-minute morning audio podcast.", ["daily_podcast_synthesizer", "audio_track_merger", "podcast_rss_publisher"], "llama3.2:3b", "podcast"),
            ("agent_305", "Central Autonomous Operating System Meta-Manager", "High-Level Orchestration & Self-Healing", "Master executive agent coordinating all 305 agents, managing task dependencies and self-healing.", ["meta_manager_core", "dag_dependency_solver", "self_healing_orchestrator"], "qwen2.5-coder:7b", "crown")
        ]
        for aid, name, role, desc, tools, mdl, ico in group_s:
            agents_def.append((aid, name, "S", "Media & Omnichannel", role, desc, tools, mdl, ico))

        # Register all 305 specialized agents into dictionary
        for item in agents_def:
            agent = SpecializedAgent(
                agent_id=item[0],
                name=item[1],
                group=item[2],
                group_name=item[3],
                role=item[4],
                description=item[5],
                permitted_tools=item[6],
                default_model=item[7],
                icon=item[8]
            )
            self._agents[agent.agent_id] = agent

        log_event(f"Registered all {len(self._agents)} Specialized Enterprise AI Agents across 19 Groups (A-S)", component="AgentRegistry")

    def get_agent(self, agent_id: str) -> Optional[SpecializedAgent]:
        return self._agents.get(agent_id)

    def get_agent_by_name(self, name: str) -> Optional[SpecializedAgent]:
        for a in self._agents.values():
            if a.name.lower() == name.lower():
                return a
        return None

    def list_all_agents(self) -> List[Dict[str, Any]]:
        return [a.to_dict() for a in self._agents.values()]

    def list_agents_by_group(self, group: str) -> List[Dict[str, Any]]:
        return [a.to_dict() for a in self._agents.values() if a.group.upper() == group.upper()]

    def get_group_summaries(self) -> Dict[str, Dict[str, Any]]:
        groups = {
            "A": {"name": "Core Orchestration", "count": 0, "active": 0},
            "B": {"name": "Data Engineering", "count": 0, "active": 0},
            "C": {"name": "Snowflake & Oracle", "count": 0, "active": 0},
            "D": {"name": "Data Quality & Lineage", "count": 0, "active": 0},
            "E": {"name": "AWS DMS & Migration", "count": 0, "active": 0},
            "F": {"name": "Analytics & BI", "count": 0, "active": 0},
            "G": {"name": "AI, DL & MLOps", "count": 0, "active": 0},
            "H": {"name": "Security & Governance", "count": 0, "active": 0},
            "I": {"name": "Cloud Infra & SRE", "count": 0, "active": 0},
            "J": {"name": "Career & Job Outreach", "count": 0, "active": 0},
            "K": {"name": "Communications", "count": 0, "active": 0},
            "L": {"name": "Schedulers & Crons", "count": 0, "active": 0},
            "M": {"name": "Lifestyle & Ambience", "count": 0, "active": 0},
            "N": {"name": "Cybersecurity & Red-Teaming", "count": 0, "active": 0},
            "O": {"name": "Multi-Cloud Lakehouse", "count": 0, "active": 0},
            "P": {"name": "Career & Global Outreach", "count": 0, "active": 0},
            "Q": {"name": "Price & Crypto Assets", "count": 0, "active": 0},
            "R": {"name": "Hardware Edge & IoT", "count": 0, "active": 0},
            "S": {"name": "Media & Omnichannel", "count": 0, "active": 0}
        }
        for a in self._agents.values():
            g = a.group
            if g in groups:
                groups[g]["count"] += 1
                if a.current_state in ["Running", "Assigned", "Retrying"]:
                    groups[g]["active"] += 1
        return groups

agent_registry = AgentRegistry()
