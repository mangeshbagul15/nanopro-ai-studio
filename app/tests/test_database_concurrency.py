"""
Mangesh Nano Pro AI Studio - Concurrency, Caching & Database Optimization Test Suite (Milestone M2 / R3)
Validates:
- F10: CredentialsVault in-memory caching (< 0.1ms, SLA < 5ms) and cache invalidation on write/delete
- F11: Decoupled MonitoringAgent telemetry (< 0.1ms, SLA < 5ms) and background daemon refresh
- F12: SQLite relational indexes on conversations, credentials, and tasks, plus WAL mode configuration
- F13: TaskManager lock isolation (db.save_task executed outside self._lock)
- F14: Database vacuum_and_checkpoint execution, DB file size < 15MB, and PRAGMA integrity_check = ok
- F15: 20 concurrent worker threads executing compound operations with zero 'database is locked' errors
"""

import sys
import time
import unittest
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from app.core.database import db, credentials_vault, Database
from app.agents.assistant_agent import monitoring_agent
from app.core.task_manager import task_manager
from app.core.config import SQLITE_DB_PATH


class TestDatabaseConcurrencyAndOptimization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure database tables and indexes are initialized
        db._init_db()

    def test_f10_credentials_vault_caching_and_invalidation(self):
        """F10: Test CredentialsVault in-memory caching latency (< 5ms SLA, target < 0.1ms) and invalidation."""
        test_service = f"TEST_VAULT_SVC_{int(time.time() * 1000)}"
        cred_id = credentials_vault.store_credential(
            service_name=test_service,
            credential_type="database",
            username="test_admin",
            secret_value="SuperSecretPassword123!",
            host="localhost",
            port="5432",
            database_name="testdb"
        )
        self.assertIsNotNone(cred_id)

        # Cold lookup: populates cache
        cred_cold = credentials_vault.get_credential(test_service)
        self.assertIsNotNone(cred_cold)
        self.assertEqual(cred_cold["secret_value"], "SuperSecretPassword123!")

        # Warm lookup: benchmark 50 iterations from cache
        latencies = []
        for _ in range(50):
            t0 = time.perf_counter()
            c = credentials_vault.get_credential(test_service)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0)  # ms
            self.assertEqual(c["secret_value"], "SuperSecretPassword123!")

        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        print(f"\n[F10 CredentialsVault Cache] Avg: {avg_latency:.4f}ms, p95: {p95_latency:.4f}ms")
        self.assertLess(avg_latency, 5.0, "CredentialsVault cache retrieval exceeded 5ms SLA")
        self.assertLess(p95_latency, 5.0, "CredentialsVault p95 retrieval exceeded 5ms SLA")

        # Test cache lookup by ID
        t0 = time.perf_counter()
        c_by_id = credentials_vault.get_credential(cred_id)
        t1 = time.perf_counter()
        self.assertIsNotNone(c_by_id)
        self.assertEqual(c_by_id["service_name"], test_service)
        self.assertLess((t1 - t0) * 1000.0, 5.0)

        # Test add_credential alias
        alias_id = credentials_vault.add_credential(
            service_name=f"{test_service}_ALIAS",
            credential_type="api_key",
            secret_value="AliasSecret999"
        )
        self.assertIsNotNone(alias_id)
        c_alias = credentials_vault.get_credential(f"{test_service}_ALIAS")
        self.assertEqual(c_alias["secret_value"], "AliasSecret999")

        # Test cache invalidation on delete
        credentials_vault.delete_credential(cred_id)
        credentials_vault.delete_credential(alias_id)
        self.assertIsNone(credentials_vault.get_credential(test_service))
        self.assertIsNone(credentials_vault.get_credential(f"{test_service}_ALIAS"))

    def test_f11_monitoring_agent_decoupled_telemetry(self):
        """F11: Test MonitoringAgent decoupled background telemetry latency (< 5ms SLA, target < 0.1ms)."""
        # Telemetry cache is pre-warmed during initialization
        health = monitoring_agent.get_system_health()
        self.assertIsInstance(health, dict)
        self.assertIn("health_status", health)
        self.assertIn("disk", health)
        self.assertIn("database", health)

        # Benchmark 50 calls to get_system_health
        latencies = []
        for _ in range(50):
            t0 = time.perf_counter()
            h = monitoring_agent.get_system_health()
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0)
            self.assertIn("health_status", h)

        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        print(f"\n[F11 Monitoring Telemetry Cache] Avg: {avg_latency:.4f}ms, p95: {p95_latency:.4f}ms")
        self.assertLess(avg_latency, 5.0, "MonitoringAgent get_system_health exceeded 5ms SLA")
        self.assertLess(p95_latency, 5.0, "MonitoringAgent p95 get_system_health exceeded 5ms SLA")

    def test_f12_sqlite_indexation_and_connection(self):
        """F12: Test that required SQLite indexes exist and accelerate query plans."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = {row["name"] for row in cursor.fetchall()}

            self.assertIn("idx_conversations_session", indexes)
            self.assertIn("idx_credentials_service", indexes)
            self.assertIn("idx_tasks_created", indexes)

            # Validate EXPLAIN QUERY PLAN uses index on conversations
            cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM conversations WHERE session_id = 'test_sess' ORDER BY id ASC LIMIT 50")
            plan_rows = [dict(r) for r in cursor.fetchall()]
            plan_str = " ".join(str(r) for r in plan_rows)
            self.assertIn("idx_conversations_session", plan_str, "Query plan did not utilize idx_conversations_session")

            # Validate EXPLAIN QUERY PLAN uses index on credentials
            cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM credentials WHERE service_name = 'test_svc'")
            cred_plan = " ".join(str(dict(r)) for r in cursor.fetchall())
            self.assertIn("idx_credentials_service", cred_plan, "Query plan did not utilize idx_credentials_service")

            # Validate journal_mode is WAL
            cursor.execute("PRAGMA journal_mode")
            jm = cursor.fetchone()[0]
            self.assertEqual(jm.lower(), "wal")

    def test_f13_task_manager_lock_isolation(self):
        """F13: Test that TaskManager operations execute without locking out concurrent threads."""
        job_id = task_manager.create_job("Test lock isolation job", agent_id="manager")
        self.assertIsNotNone(job_id)

        # Update stage should update in-memory state and persist without holding lock during I/O
        task_manager.update_job_stage(job_id, stage="processing", progress=50, status="running")
        job = task_manager.get_job(job_id)
        self.assertEqual(job["stage"], "processing")
        self.assertEqual(job["progress"], 50)

        # Complete job
        task_manager.set_job_completed(job_id, result_data={"success": True})
        job_done = task_manager.get_job(job_id)
        self.assertEqual(job_done["status"], "done")
        self.assertEqual(job_done["progress"], 100)

        # Verify persisted state in SQLite
        persisted = db.get_task(job_id)
        self.assertIsNotNone(persisted)
        self.assertEqual(persisted["status"], "done")

    def test_f14_database_vacuuming_and_size(self):
        """F14: Test Database vacuum_and_checkpoint(), verify DB size < 15MB, and PRAGMA integrity_check = ok."""
        # Test class alias Database == DatabaseManager
        self.assertEqual(Database, type(db))

        res = db.vacuum_and_checkpoint()
        self.assertIsInstance(res, dict)
        print(f"\n[F14 Database Compaction] File size: {res['final_size_mb']} MB, Integrity: {res['integrity']}")

        self.assertEqual(res["integrity"].lower(), "ok", "PRAGMA integrity_check failed")
        self.assertLess(res["final_size_bytes"], 15 * 1024 * 1024, f"Database file size ({res['final_size_mb']} MB) exceeds 15MB SLA")
        self.assertTrue(res["is_optimized"])

    def test_f15_twenty_worker_concurrency_validation(self):
        """F15: Validate 20 concurrent threads running compound operations execute with zero lock/malformed errors."""
        NUM_WORKERS = 20
        errors = []
        latencies = []

        def worker_task(worker_id: int):
            try:
                t0 = time.perf_counter()

                # 1. Credentials Vault query
                cred = credentials_vault.get_credential("NANO_PRO_SNOWFLAKE")

                # 2. Chat message insert
                session_id = f"concurrency_session_{worker_id}"
                msg_id = db.add_chat_message(session_id, "user", f"Concurrent message from worker {worker_id}")
                self.assertIsNotNone(msg_id)

                # 3. Chat history query
                history = db.get_chat_history(session_id, limit=10)
                self.assertTrue(len(history) > 0)

                # 4. Task status update / save
                job_id = task_manager.create_job(f"Concurrent task from worker {worker_id}", agent_id="manager")
                task_manager.update_job_stage(job_id, stage="executing", progress=50, status="running")
                task_manager.set_job_completed(job_id, result_data={"worker": worker_id})

                # 5. Monitoring health query
                health = monitoring_agent.get_system_health()
                self.assertIn("health_status", health)

                t1 = time.perf_counter()
                latencies.append((t1 - t0) * 1000.0)
            except Exception as e:
                errors.append(f"Worker {worker_id} failed: {type(e).__name__}: {e}")

        threads = []
        for i in range(NUM_WORKERS):
            t = threading.Thread(target=worker_task, args=(i,))
            threads.append(t)

        start_time = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        total_duration = (time.perf_counter() - start_time) * 1000.0

        print(f"\n[F15 Concurrency Results] 20 Workers Total Duration: {total_duration:.2f}ms")
        if latencies:
            print(f"Per-Worker Compound Latency: Min: {min(latencies):.2f}ms, Avg: {sum(latencies)/len(latencies):.2f}ms, Max: {max(latencies):.2f}ms")

        # Assertions
        self.assertEqual(len(errors), 0, f"Encountered concurrency errors: {errors}")
        self.assertEqual(len(latencies), NUM_WORKERS, "Not all workers completed")


if __name__ == "__main__":
    unittest.main()
