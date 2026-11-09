# Unit 02: Core Infrastructure & Storage (Data, Config, Connection, Storage)

## Purpose and Responsibility
Provides central filesystem path resolution, thread-safe logging, SQLite persistence for 31 distinct entities, AES-256-GCM authenticated secret encryption via `CredentialsVault`, multi-database connection management (Snowflake, Oracle XE, AWS S3, SMTP, SQLite), and local storage usage profiling with safe cleanups.

## Files Read
- `app/core/config.py`: Directory paths, OS detection, environment variables, default models [Tier 1]
- `app/core/logger.py`: Thread-safe dual stream + file logger with job-context hooks [Tier 1]
- `app/core/database.py`: Core `DatabaseManager` (31 tables), `CredentialsVault` with AES-256-GCM [Tier 1]
- `app/core/connection_manager.py`: Connectors, live handshakes, metadata discovery for Snowflake, Oracle, AWS, SMTP [Tier 1]
- `app/core/storage_inspector.py`: Category disk usage measurement, trend recording, safe pruning [Tier 1]

## Key Classes / Functions
- `DatabaseManager` (`app/core/database.py:20`): [Verified] Initializes 31 relational tables in `app/database/studio_memory.db` with WAL/thread-safe connections.
- `CredentialsVault` (`app/core/database.py:1940`): [Verified] Encrypts/decrypts service secrets using authenticated AES-256-GCM with automated migration from legacy XOR.
- `_resolve_vault_master_key()` (`app/core/database.py:1865`): [Verified] Derives master key from environment `STUDIO_VAULT_KEY` or file `.vault.key` with host-seed fallback.
- `ConnectionManager` (`app/core/connection_manager.py:49`): [Verified] Pre-seeds profiles and handles connection verification, query history, and schema introspection.
- `ensure_default_connections()` (`app/core/connection_manager.py:104`): [Verified] Verifies/seeds Snowflake, Oracle XE, Gmail SMTP, and AWS S3 credentials into the Vault on startup.
- `StorageInspector.inspect_complete_storage()` (`app/core/storage_inspector.py:51`): [Verified] Returns byte-level size metrics for DB, caches, logs, reports, backups, and host drive.
- `log_event()` (`app/core/logger.py:37`): [Verified] Routes messages to rotating logs, live RAM ring buffer (2000 items), and active job streams.

## Dependencies IN & OUT
- **Dependencies IN**: `main.py`, `app.agents.*`, `app.video_maker.*`, `app.ui.*`, and tests.
- **Dependencies OUT**:
  - Internal: `app.core.config`, `app.core.logger`, `app.core.smtp_client`, `app.core.task_manager`.
  - External: `sqlite3`, `cryptography` (AESGCM), `snowflake.connector`, `oracledb`, `boto3`, `shutil`, `dotenv`.

## Data Touched
- SQLite tables: `tasks`, `reminders`, `project_knowledge`, `prompt_history`, `backups_ledger`, `artifacts`, `approvals`, `credentials`, `conversations`, `pipelines`, `free_apis`, `github_projects`, `research_library`, `discovery_schedules`, `connection_history`, `query_history`, `connection_metadata`, `storage_measurements`, etc.
- Filesystem: `app/database/studio_memory.db`, `app/logs/*.log`, `app/reports/`, `app/cache/`.

## Config and Env Variables Used
- `STUDIO_DB_PATH`, `STUDIO_VAULT_KEY`
- `OLLAMA_HOST`, `STUDIO_HOST`, `STUDIO_PORT`
- `SNOWFLAKE_PASSWORD`, `ORACLE_PASSWORD`, `GMAIL_APP_PASSWORD`, `SMTP_PASSWORD`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`, `AWS_S3_BUCKET`, `AWS_BEARER_TOKEN`

## Error Handling, Retries, Logging, Idempotency
- Connection tests employ real handshakes (socket probes, client driver calls) without simulated mock responses.
- `execute_safe_cleanup()` restricts deletion strictly to `SAFE_CLEANUP_CATEGORIES` and explicitly avoids `.db` files.
- Thread-safe ring buffer (`_live_logs`) uses mutex locking to prevent race conditions during concurrent logging.

## Observed Issues
- **U-UNIT02-01** | Category: Security | Severity: Critical | Location: `app/core/connection_manager.py:108,122,135,148-152`
  - Evidence: Hardcoded production secrets present as fallback literals in Python source:
    - Snowflake password: `<REDACTED>`
    - Oracle password: `<REDACTED>`
    - Gmail app password: `<REDACTED>`
    - AWS Secret Access Key: `<REDACTED>`
    - AWS Bearer Token: `<REDACTED>`
  - Fix: Redact and eliminate all hardcoded secrets from Python source files. Require loading exclusively from `.env` or prompt during initial setup.
- **U-UNIT02-02** | Category: Reliability / Concurrency | Severity: Medium | Location: `app/core/database.py:26`
  - Evidence: `sqlite3.connect(..., check_same_thread=False)` is used across concurrent FastAPI request threads without write-ahead-log (WAL) pragma explicitly set on connection creation.
  - Fix: Enable `PRAGMA journal_mode=WAL;` and `PRAGMA busy_timeout=5000;` on connection factory initialization to prevent `database is locked` errors during background cron operations.
- **U-UNIT02-03** | Category: Code Quality | Severity: Low | Location: `app/core/database.py:1893`
  - Evidence: In `_resolve_vault_master_key()`, fallback host seed refers to `socket.gethostname() if 'socket' in globals() else 'host'` but `socket` is not imported at top of `database.py`.
  - Fix: Add `import socket` to imports in `app/core/database.py`.

## Open Questions
- None.
