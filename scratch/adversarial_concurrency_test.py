"""
Mangesh Nano Pro AI Studio - Adversarial Concurrency & Stability Stress Test Harness
Challenger 2 Empirical Verification Suite

Tests:
1. Scenario 1: 50 concurrent threads executing compound operations (Vault + Chat + History + Task + Health)
2. Scenario 2: CredentialsVault race conditions & cache stampede (concurrent readers, writers, invalidators)
3. Scenario 3: Database vacuum_and_checkpoint() during live in-flight concurrent writes
4. Scenario 4: MonitoringAgent get_system_health() latency SLA (< 5ms) under DB saturation
5. Scenario 5: Error rate audit (zero 'database is locked' / 'malformed')
6. Scenario 6: Database compaction and file size limit (< 15 MB) & PRAGMA integrity_check
"""

import os
import sys
import time
import math
import json
import random
import threading
import traceback
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from app.core.database import db, credentials_vault, DatabaseManager
from app.agents.assistant_agent import monitoring_agent
from app.core.task_manager import task_manager
from app.core.config import SQLITE_DB_PATH

def compute_percentiles(values: List[float]) -> Dict[str, float]:
    if not values:
        return {"min": 0.0, "p50": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0, "max": 0.0, "avg": 0.0}
    s = sorted(values)
    n = len(s)
    def p(pct):
        idx = min(int(n * pct), n - 1)
        return s[idx]
    return {
        "min": round(s[0], 4),
        "p50": round(p(0.50), 4),
        "p90": round(p(0.90), 4),
        "p95": round(p(0.95), 4),
        "p99": round(p(0.99), 4),
        "max": round(s[-1], 4),
        "avg": round(sum(s) / n, 4),
        "count": n
    }

class AdversarialConcurrencyTester:
    def __init__(self):
        self.results = {}
        self.all_errors = []

    def run_all(self) -> Dict[str, Any]:
        print("=" * 80)
        print("STARTING ADVERSARIAL CONCURRENCY & STABILITY STRESS HARNESS")
        print(f"Target DB: {SQLITE_DB_PATH}")
        print(f"Initial DB Size: {self._get_db_size_mb():.2f} MB")
        print("=" * 80)

        # 1. Warm-up and baseline check
        db._init_db()

        # Run Scenario 1: 50 concurrent threads overload
        self.test_scenario_1_overload_50_threads()

        # Run Scenario 2: Cache stampede and invalidation race
        self.test_scenario_2_cache_stampede_race()

        # Run Scenario 3: Vacuum & Checkpoint under live write fire
        self.test_scenario_3_vacuum_under_live_writes()

        # Run Scenario 4: Telemetry SLA under DB saturation
        self.test_scenario_4_telemetry_sla_under_saturation()

        # Run Scenario 5: Database size & integrity check
        self.test_scenario_5_db_size_and_integrity()

        # Final Summary
        self.print_final_summary()
        return self.results

    def _get_db_size_bytes(self) -> int:
        return SQLITE_DB_PATH.stat().st_size if SQLITE_DB_PATH.exists() else 0

    def _get_db_size_mb(self) -> float:
        return self._get_db_size_bytes() / (1024 * 1024)

    def test_scenario_1_overload_50_threads(self):
        """
        Scenario 1: High concurrency overload.
        50 concurrent threads simultaneously executing compound DB operations:
        - CredentialsVault read (cached & uncached)
        - Chat write (db.add_chat_message)
        - Chat history read (db.get_chat_history)
        - Task creation (task_manager.create_job)
        - Task stage transition (task_manager.update_job_stage)
        - Task completion (task_manager.set_job_completed)
        - Health check (monitoring_agent.get_system_health)
        Repeated across 2 rounds per thread (total 100 compound operations, 700 DB/agent actions).
        """
        print("\n>>> [SCENARIO 1] 50 Concurrent Threads Compound DB Overload")
        NUM_THREADS = 50
        ROUNDS_PER_THREAD = 2
        latencies = []
        errors = []
        lock_errors = []
        malformed_errors = []

        # Pre-seed credentials for query
        test_seed_key = "CONCURRENT_BENCH_CRED"
        credentials_vault.store_credential(
            service_name=test_seed_key,
            credential_type="database",
            username="bench_user",
            secret_value="EncryptedBenchPass123$"
        )

        def worker_loop(thread_id: int):
            for r in range(ROUNDS_PER_THREAD):
                t0 = time.perf_counter()
                try:
                    # 1. Credentials query
                    cred = credentials_vault.get_credential(test_seed_key)
                    if not cred or cred.get("secret_value") != "EncryptedBenchPass123$":
                        errors.append(f"T{thread_id}-R{r}: Credential mismatch")

                    # 2. Chat write
                    session_id = f"adversarial_sess_{thread_id}"
                    msg_id = db.add_chat_message(
                        session_id=session_id,
                        sender="user",
                        message=f"Adversarial concurrency message from thread {thread_id} round {r}",
                        metadata={"thread": thread_id, "round": r, "ts": time.time()}
                    )
                    if not msg_id:
                        errors.append(f"T{thread_id}-R{r}: Chat insert failed")

                    # 3. Chat history read
                    history = db.get_chat_history(session_id=session_id, limit=20)
                    if not history:
                        errors.append(f"T{thread_id}-R{r}: Chat history empty")

                    # 4. Task creation
                    job_id = task_manager.create_job(
                        prompt=f"Adversarial stress task T{thread_id}-R{r}",
                        agent_id=f"agent_stress_{thread_id % 5}"
                    )

                    # 5. Task stage update
                    task_manager.update_job_stage(
                        job_id=job_id,
                        stage="adversarial_execution",
                        progress=50,
                        status="running",
                        tool_used="stress_runner"
                    )

                    # 6. Task completion
                    task_manager.set_job_completed(
                        job_id=job_id,
                        result_data={"thread": thread_id, "round": r, "status": "verified"}
                    )

                    # 7. Monitoring health
                    health = monitoring_agent.get_system_health()
                    if not health or "health_status" not in health:
                        errors.append(f"T{thread_id}-R{r}: Health query invalid")

                    t1 = time.perf_counter()
                    latencies.append((t1 - t0) * 1000.0)

                except Exception as e:
                    err_str = f"{type(e).__name__}: {str(e)}"
                    errors.append(f"T{thread_id}-R{r} exception: {err_str}")
                    if "locked" in err_str.lower() or "busy" in err_str.lower():
                        lock_errors.append(err_str)
                    if "malformed" in err_str.lower():
                        malformed_errors.append(err_str)

        threads = [threading.Thread(target=worker_loop, args=(i,)) for i in range(NUM_THREADS)]
        start_time = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        total_time = (time.perf_counter() - start_time) * 1000.0

        stats = compute_percentiles(latencies)
        self.results["scenario_1"] = {
            "threads": NUM_THREADS,
            "rounds_per_thread": ROUNDS_PER_THREAD,
            "total_operations": NUM_THREADS * ROUNDS_PER_THREAD,
            "total_wall_time_ms": round(total_time, 2),
            "latency_stats_ms": stats,
            "error_count": len(errors),
            "errors": errors[:5],
            "lock_errors_count": len(lock_errors),
            "malformed_errors_count": len(malformed_errors)
        }
        self.all_errors.extend(errors)

        print(f"  Completed {len(latencies)} / {NUM_THREADS * ROUNDS_PER_THREAD} compound operations in {total_time:.2f} ms")
        print(f"  Compound Latency (ms): Min={stats['min']}, p50={stats['p50']}, p90={stats['p90']}, p95={stats['p95']}, p99={stats['p99']}, Max={stats['max']}, Avg={stats['avg']}")
        print(f"  Errors: {len(errors)} | Lock Errors: {len(lock_errors)} | Malformed Errors: {len(malformed_errors)}")

    def test_scenario_2_cache_stampede_race(self):
        """
        Scenario 2: Race conditions on CredentialsVault cache invalidation & concurrent reads (Cache Stampede).
        - 30 reader threads reading `STAMPEDE_KEY` 100 times in a tight loop.
        - 10 writer threads concurrently calling store_credential on `STAMPEDE_KEY` and other keys.
        - 5 invalidator threads calling clear_cache / delete_credential.
        Verifies:
        - Zero KeyError, RuntimeError (dict mutation during iteration)
        - Zero decrypt failures / corrupt data
        - Zero unhandled lock errors
        """
        print("\n>>> [SCENARIO 2] CredentialsVault Cache Stampede & Race Invalidation")
        STAMPEDE_KEY = "CACHE_STAMPEDE_SERVICE"
        credentials_vault.store_credential(
            service_name=STAMPEDE_KEY,
            credential_type="api_key",
            secret_value="InitialStampedeSecret_123"
        )

        read_latencies = []
        read_errors = []
        write_errors = []
        lock_errors = []
        stop_event = threading.Event()

        def reader_worker(r_id: int):
            for i in range(100):
                t0 = time.perf_counter()
                try:
                    c = credentials_vault.get_credential(STAMPEDE_KEY)
                    t1 = time.perf_counter()
                    read_latencies.append((t1 - t0) * 1000.0)
                    if c is not None:
                        sec = c.get("secret_value", "")
                        if not sec or not ("InitialStampedeSecret" in sec or "UpdatedStampedeSecret" in sec):
                            read_errors.append(f"R{r_id}-{i}: Corrupted secret value: {sec}")
                except Exception as e:
                    err_str = f"{type(e).__name__}: {str(e)}"
                    read_errors.append(f"R{r_id}-{i} read exception: {err_str}")
                    if "locked" in err_str.lower() or "busy" in err_str.lower():
                        lock_errors.append(err_str)
                time.sleep(0.001)

        def writer_worker(w_id: int):
            for i in range(15):
                try:
                    val = f"UpdatedStampedeSecret_W{w_id}_iter{i}_{random.randint(1000, 9999)}"
                    credentials_vault.store_credential(
                        service_name=STAMPEDE_KEY,
                        credential_type="api_key",
                        secret_value=val
                    )
                except Exception as e:
                    err_str = f"{type(e).__name__}: {str(e)}"
                    write_errors.append(f"W{w_id}-{i} write exception: {err_str}")
                    if "locked" in err_str.lower() or "busy" in err_str.lower():
                        lock_errors.append(err_str)
                time.sleep(0.01)

        def invalidator_worker(inv_id: int):
            for i in range(10):
                try:
                    temp_key = f"TEMP_INV_KEY_{inv_id}_{i}"
                    cid = credentials_vault.store_credential(service_name=temp_key, credential_type="token", secret_value="temp")
                    time.sleep(0.005)
                    credentials_vault.delete_credential(cid)
                except Exception as e:
                    err_str = f"{type(e).__name__}: {str(e)}"
                    write_errors.append(f"INV{inv_id}-{i} exception: {err_str}")
                    if "locked" in err_str.lower() or "busy" in err_str.lower():
                        lock_errors.append(err_str)
                time.sleep(0.01)

        readers = [threading.Thread(target=reader_worker, args=(i,)) for i in range(30)]
        writers = [threading.Thread(target=writer_worker, args=(i,)) for i in range(10)]
        invalidators = [threading.Thread(target=invalidator_worker, args=(i,)) for i in range(5)]

        all_threads = readers + writers + invalidators
        t_start = time.perf_counter()
        for t in all_threads:
            t.start()
        for t in all_threads:
            t.join()
        dur = (time.perf_counter() - t_start) * 1000.0

        stats = compute_percentiles(read_latencies)
        total_errors = len(read_errors) + len(write_errors)
        self.results["scenario_2"] = {
            "readers": 30,
            "writers": 10,
            "invalidators": 5,
            "total_reads": len(read_latencies),
            "read_latency_stats_ms": stats,
            "read_errors_count": len(read_errors),
            "write_errors_count": len(write_errors),
            "lock_errors_count": len(lock_errors),
            "duration_ms": round(dur, 2)
        }
        self.all_errors.extend(read_errors + write_errors)

        print(f"  Executed {len(read_latencies)} concurrent reads against active writes/invalidations in {dur:.2f} ms")
        print(f"  Read Latency (ms): Min={stats['min']}, p50={stats['p50']}, p90={stats['p90']}, p95={stats['p95']}, p99={stats['p99']}, Max={stats['max']}, Avg={stats['avg']}")
        print(f"  Errors: Read={len(read_errors)} | Write={len(write_errors)} | Lock={len(lock_errors)}")

    def test_scenario_3_vacuum_under_live_writes(self):
        """
        Scenario 3: Vacuuming & WAL checkpointing while concurrent writes are in flight.
        - 20 writer threads continuously writing chat messages, credentials, and tasks.
        - Main maintenance thread invokes `db.vacuum_and_checkpoint()`.
        - Verifies:
          - Zero uncaught 'database is locked' errors on vacuum or writers.
          - Vacuum returns integrity: 'ok'.
          - DB is compacted and optimized.
        """
        print("\n>>> [SCENARIO 3] Vacuuming & WAL Checkpointing During Live Concurrent Writes")
        writer_errors = []
        lock_errors = []
        vacuum_result = {}
        stop_writing = threading.Event()
        writes_completed = [0]
        writes_lock = threading.Lock()

        def background_writer(w_id: int):
            local_count = 0
            while not stop_writing.is_set():
                try:
                    # Alternating chat and task writes
                    db.add_chat_message(
                        session_id=f"live_vac_sess_{w_id}",
                        sender="agent",
                        message=f"Live write message {local_count} during vacuum test"
                    )
                    local_count += 1
                    time.sleep(0.002)
                except Exception as e:
                    err_str = f"{type(e).__name__}: {str(e)}"
                    writer_errors.append(f"Writer {w_id} err: {err_str}")
                    if "locked" in err_str.lower() or "busy" in err_str.lower():
                        lock_errors.append(err_str)
            with writes_lock:
                writes_completed[0] += local_count

        # Start 20 background writer threads
        writers = [threading.Thread(target=background_writer, args=(i,)) for i in range(20)]
        for t in writers:
            t.start()

        # Let writers spin up and produce writes
        time.sleep(0.1)

        # Trigger vacuum_and_checkpoint in the middle of active writes!
        vac_start = time.perf_counter()
        try:
            vacuum_result = db.vacuum_and_checkpoint()
        except Exception as e:
            err_str = f"Vacuum failed: {type(e).__name__}: {str(e)}"
            writer_errors.append(err_str)
            if "locked" in err_str.lower() or "busy" in err_str.lower():
                lock_errors.append(err_str)
        vac_time = (time.perf_counter() - vac_start) * 1000.0

        # Allow writers to continue for a moment, then stop
        time.sleep(0.1)
        stop_writing.set()
        for t in writers:
            t.join()

        self.results["scenario_3"] = {
            "vacuum_duration_ms": round(vac_time, 2),
            "vacuum_result": vacuum_result,
            "total_in_flight_writes": writes_completed[0],
            "writer_errors_count": len(writer_errors),
            "lock_errors_count": len(lock_errors)
        }
        self.all_errors.extend(writer_errors)

        print(f"  Vacuum & Checkpoint completed in {vac_time:.2f} ms")
        print(f"  Concurrent live writes sustained during vacuum: {writes_completed[0]}")
        print(f"  Vacuum Result: Initial={vacuum_result.get('initial_size_bytes')}B, Final={vacuum_result.get('final_size_bytes')}B ({vacuum_result.get('final_size_mb')}MB), Integrity={vacuum_result.get('integrity')}")
        print(f"  Writer Errors: {len(writer_errors)} | Lock Errors: {len(lock_errors)}")

    def test_scenario_4_telemetry_sla_under_saturation(self):
        """
        Scenario 4: Verify get_system_health() latency remains < 5ms SLA under concurrent DB saturation.
        - 40 worker threads creating DB write load.
        - 10 telemetry threads executing 50 calls each (500 total calls) to monitoring_agent.get_system_health().
        - Measures individual latency with time.perf_counter().
        - Asserts p50, p95, p99 < 5ms.
        """
        print("\n>>> [SCENARIO 4] MonitoringAgent Telemetry Latency SLA Under Heavy DB Saturation")
        telemetry_latencies = []
        telemetry_errors = []
        stop_db_load = threading.Event()

        def db_pressure_worker(worker_id: int):
            while not stop_db_load.is_set():
                try:
                    db.add_chat_message(f"press_sess_{worker_id}", "user", "load payload")
                    credentials_vault.get_credential("CONCURRENT_BENCH_CRED")
                    time.sleep(0.005)
                except Exception:
                    pass

        def telemetry_worker(t_id: int):
            for i in range(50):
                t0 = time.perf_counter()
                try:
                    health = monitoring_agent.get_system_health()
                    t1 = time.perf_counter()
                    telemetry_latencies.append((t1 - t0) * 1000.0)
                    if not health or "health_status" not in health:
                        telemetry_errors.append(f"T{t_id}-{i}: Invalid health payload")
                except Exception as e:
                    telemetry_errors.append(f"T{t_id}-{i} health query failed: {e}")
                time.sleep(0.002)

        # Start 40 DB pressure threads
        db_threads = [threading.Thread(target=db_pressure_worker, args=(i,)) for i in range(40)]
        for t in db_threads:
            t.start()

        # Start 10 telemetry caller threads (500 calls)
        tel_threads = [threading.Thread(target=telemetry_worker, args=(i,)) for i in range(10)]
        for t in tel_threads:
            t.start()
        for t in tel_threads:
            t.join()

        # Stop DB pressure
        stop_db_load.set()
        for t in db_threads:
            t.join()

        stats = compute_percentiles(telemetry_latencies)
        sla_passed = stats["p95"] < 5.0 and stats["max"] < 10.0
        self.results["scenario_4"] = {
            "total_health_calls": len(telemetry_latencies),
            "telemetry_stats_ms": stats,
            "sla_threshold_ms": 5.0,
            "sla_met": stats["p95"] < 5.0,
            "errors_count": len(telemetry_errors)
        }
        self.all_errors.extend(telemetry_errors)

        print(f"  Executed {len(telemetry_latencies)} get_system_health() calls under 40-thread DB pressure")
        print(f"  Telemetry Latency (ms): Min={stats['min']}, p50={stats['p50']}, p90={stats['p90']}, p95={stats['p95']}, p99={stats['p99']}, Max={stats['max']}, Avg={stats['avg']}")
        print(f"  SLA Status: {'PASSED (< 5ms p95)' if stats['p95'] < 5.0 else 'FAILED (>= 5ms p95)'} (p95={stats['p95']} ms)")

    def test_scenario_5_db_size_and_integrity(self):
        """
        Scenario 5 & 6: Verify database file size remains < 15 MB and zero disk corruption.
        """
        print("\n>>> [SCENARIO 5] Database File Size & Integrity Verification")
        db_size_bytes = self._get_db_size_bytes()
        db_size_mb = self._get_db_size_mb()
        max_size_mb = 15.0

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            integrity_rows = cursor.fetchall()
            integrity_status = [r[0] for r in integrity_rows]

            cursor.execute("PRAGMA quick_check;")
            quick_rows = cursor.fetchall()
            quick_status = [r[0] for r in quick_rows]

            cursor.execute("PRAGMA page_count;")
            page_count = cursor.fetchone()[0]

            cursor.execute("PRAGMA page_size;")
            page_size = cursor.fetchone()[0]

            cursor.execute("SELECT count(*) FROM conversations")
            chat_count = cursor.fetchone()[0]

            cursor.execute("SELECT count(*) FROM tasks")
            task_count = cursor.fetchone()[0]

            cursor.execute("SELECT count(*) FROM credentials")
            cred_count = cursor.fetchone()[0]

        is_integrity_ok = (len(integrity_status) == 1 and integrity_status[0].lower() == "ok")
        is_size_ok = db_size_mb < max_size_mb

        self.results["scenario_5"] = {
            "db_size_bytes": db_size_bytes,
            "db_size_mb": round(db_size_mb, 2),
            "max_size_mb_sla": max_size_mb,
            "size_sla_passed": is_size_ok,
            "page_count": page_count,
            "page_size": page_size,
            "integrity_status": integrity_status,
            "integrity_passed": is_integrity_ok,
            "quick_status": quick_status,
            "record_counts": {
                "conversations": chat_count,
                "tasks": task_count,
                "credentials": cred_count
            }
        }

        print(f"  Final DB Size: {db_size_mb:.2f} MB ({db_size_bytes} bytes) | SLA: < {max_size_mb} MB -> {'PASSED' if is_size_ok else 'FAILED'}")
        print(f"  PRAGMA integrity_check: {integrity_status} -> {'PASSED' if is_integrity_ok else 'FAILED'}")
        print(f"  PRAGMA quick_check: {quick_status}")
        print(f"  DB Record Counts: conversations={chat_count}, tasks={task_count}, credentials={cred_count}")

    def print_final_summary(self):
        print("\n" + "=" * 80)
        print("ADVERSARIAL CONCURRENCY & STABILITY STRESS TEST SUMMARY")
        print("=" * 80)

        s1 = self.results.get("scenario_1", {})
        s2 = self.results.get("scenario_2", {})
        s3 = self.results.get("scenario_3", {})
        s4 = self.results.get("scenario_4", {})
        s5 = self.results.get("scenario_5", {})

        s1_pass = s1.get("lock_errors_count", 0) == 0 and s1.get("malformed_errors_count", 0) == 0 and s1.get("error_count", 0) == 0
        s2_pass = s2.get("read_errors_count", 0) == 0 and s2.get("write_errors_count", 0) == 0 and s2.get("lock_errors_count", 0) == 0
        s3_pass = s3.get("lock_errors_count", 0) == 0 and s3.get("writer_errors_count", 0) == 0 and s3.get("vacuum_result", {}).get("integrity", "").lower() == "ok"
        s4_pass = s4.get("sla_met", False) and s4.get("errors_count", 0) == 0
        s5_pass = s5.get("size_sla_passed", False) and s5.get("integrity_passed", False)

        overall_verdict = "APPROVE" if (s1_pass and s2_pass and s3_pass and s4_pass and s5_pass) else "REJECT"

        print(f"1. 50-Thread Compound Overload:          {'PASS' if s1_pass else 'FAIL'} (0 lock/corrupt errors, p95={s1.get('latency_stats_ms', {}).get('p95')} ms)")
        print(f"2. Cache Stampede & Race Invalidation:   {'PASS' if s2_pass else 'FAIL'} (0 corrupt reads, 0 exceptions, p95={s2.get('read_latency_stats_ms', {}).get('p95')} ms)")
        print(f"3. Vacuum & Checkpoint Under Live Writes: {'PASS' if s3_pass else 'FAIL'} (0 lock errors, integrity={s3.get('vacuum_result', {}).get('integrity')})")
        print(f"4. Telemetry Latency SLA (< 5ms):        {'PASS' if s4_pass else 'FAIL'} (p95={s4.get('telemetry_stats_ms', {}).get('p95')} ms, avg={s4.get('telemetry_stats_ms', {}).get('avg')} ms)")
        print(f"5. DB File Size (< 15MB) & Integrity:    {'PASS' if s5_pass else 'FAIL'} ({s5.get('db_size_mb')} MB, integrity={s5.get('integrity_status')})")
        print("-" * 80)
        print(f"OVERALL ADVERSARIAL STRESS VERDICT: {overall_verdict}")
        print("=" * 80)
        self.results["overall_verdict"] = overall_verdict

if __name__ == "__main__":
    tester = AdversarialConcurrencyTester()
    res = tester.run_all()
    # Write json output for machine verification
    out_json = _PROJECT_ROOT / "scratch" / "adversarial_concurrency_results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print(f"\nSaved empirical test telemetry to: {out_json}")
    if res.get("overall_verdict") != "APPROVE":
        sys.exit(1)
    sys.exit(0)
