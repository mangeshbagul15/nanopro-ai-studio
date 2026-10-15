## 2026-10-14T18:36:07Z
You are Worker M2 (Database & Telemetry Concurrency Hardening).

Your mission is to implement Milestone M2 (Features F10, F11, F12, F13, F14, F15) in `app/core/database.py`, `app/agents/assistant_agent.py`, and `app/core/task_manager.py`.

Exclusive File Ownership:
- You exclusively own:
  * c:\Mangesh\AI video\Mangesh_Nano_Pro_AI_Studio_COMPLETE (34)\Mangesh_Nano_Pro_AI_Studio\app\core\database.py
  * c:\Mangesh\AI video\Mangesh_Nano_Pro_AI_Studio_COMPLETE (34)\Mangesh_Nano_Pro_AI_Studio\app\agents\assistant_agent.py
  * c:\Mangesh\AI video\Mangesh_Nano_Pro_AI_Studio_COMPLETE (34)\Mangesh_Nano_Pro_AI_Studio\app\core\task_manager.py
- DO NOT touch app/core/model_adapter.py or test files owned by other agents.

Implementation Scope & Requirements:
1. CredentialsVault In-Memory Caching (F10):
   - In CredentialsVault (app/core/database.py), implement a thread-safe in-memory cache dictionary with timestamp/TTL.
   - On get_credential(), return from memory cache immediately if present (response latency < 0.1ms, satisfying the < 5ms SLA).
   - Invalidate cache entries on add_credential() or delete_credential().
2. Background Decoupled Telemetry (F11):
   - In MonitoringAgent (app/agents/assistant_agent.py), decouple get_system_health().
   - Start a background daemon thread that refreshes system health metrics (disk usage, DB connectivity, task list) every 10 seconds.
   - Pre-warm the cache during initialization.
   - get_system_health() must return the latest cached state in < 0.1ms (satisfying the < 5ms SLA).
3. SQLite Indexation & Connection Optimization (F12):
   - In _init_db() (app/core/database.py), add indexes:
     * CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id, id ASC);
     * CREATE INDEX IF NOT EXISTS idx_credentials_service ON credentials(service_name);
     * CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at DESC, status);
   - In get_db_connection(), remove redundant per-connection PRAGMA journal_mode = WAL; (which acquires write locks on connect). Set WAL mode once in _init_db().
4. TaskManager Lock Isolation (F13):
   - In TaskManager (app/core/task_manager.py), move db.save_task(job) outside with self._lock: so disk writes and connection setup do not block memory state updates or other threads.
5. Database Vacuuming & Size Optimization (F14):
   - Implement vacuum_and_checkpoint() in Database executing PRAGMA wal_checkpoint(TRUNCATE); and VACUUM;.
   - Ensure studio_memory.db file size is < 15 MB and PRAGMA integrity_check returns ok.
6. 20-Worker Concurrency Validation (F15):
   - Validate that 20 concurrent threads running compound database operations (Vault query + Chat insert + Chat history + Task save + Health check) execute with zero "database is locked" or "malformed" errors.

Verification Requirement:
- Run unit/integration tests verifying the changes:
  python -m unittest app/tests/test_suite.py
  and run a concurrency validation script proving 20 concurrent workers execute cleanly with < 5ms vault and telemetry latencies and < 15MB DB size.
- Document commands and results in your handoff report.

Mandatory Paths:
- Original Request: c:\Mangesh\AI video\Mangesh_Nano_Pro_AI_Studio_COMPLETE (34)\Mangesh_Nano_Pro_AI_Studio\.agents\teamwork\ORIGINAL_REQUEST.md (MANDATORY: read this first!)
- Scope Document: c:\Mangesh\AI video\Mangesh_Nano_Pro_AI_Studio_COMPLETE (34)\Mangesh_Nano_Pro_AI_Studio\PROJECT.md
- Survey Analysis: c:\Mangesh\AI video\Mangesh_Nano_Pro_AI_Studio_COMPLETE (34)\Mangesh_Nano_Pro_AI_Studio\.agents\teamwork\explorer_survey_2\analysis.md
- Your Working Directory: c:\Mangesh\AI video\Mangesh_Nano_Pro_AI_Studio_COMPLETE (34)\Mangesh_Nano_Pro_AI_Studio\.agents\teamwork\worker_m2
- Parent ID: fc9f8196-6923-4e32-92dc-f194b09dba91
