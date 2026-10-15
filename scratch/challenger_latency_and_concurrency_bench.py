"""
Challenger 2 Empirical Verification: Microsecond Latency and Concurrency SLA Test Harness
Targeting:
1. create_job() latency under 50 concurrent threads (< 5ms SLA)
2. get_chat_history() latency under 50 concurrent threads (< 5ms SLA)
3. Zero 'database is locked' errors across 50 concurrent threads
4. Database file size < 15 MB SLA
"""

import sys
import time
import json
import threading
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from app.core.database import db, credentials_vault
from app.core.task_manager import task_manager
from app.core.config import SQLITE_DB_PATH

def compute_percentiles(values):
    if not values:
        return {"min": 0, "p50": 0, "p90": 0, "p95": 0, "p99": 0, "max": 0, "avg": 0, "count": 0}
    s = sorted(values)
    n = len(s)
    def p(pct):
        return s[min(int(n * pct), n - 1)]
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

def main():
    print("=" * 80)
    print("CHALLENGER 2 EMPIRICAL LATENCY & CONCURRENCY BENCHMARK")
    print(f"Target DB: {SQLITE_DB_PATH}")
    initial_bytes = SQLITE_DB_PATH.stat().st_size
    initial_mb = initial_bytes / (1024 * 1024)
    print(f"Starting DB File Size: {initial_mb:.2f} MB ({initial_bytes} bytes)")
    print("=" * 80)

    NUM_THREADS = 50
    CALLS_PER_THREAD = 20  # 50 * 20 = 1000 create_job and 1000 get_chat_history

    create_job_latencies = []
    get_chat_latencies = []
    lock_errors = []
    other_errors = []

    # Pre-seed deep history for multiple sessions
    print("\n[Step 1] Pre-seeding conversation history for 50 distinct sessions...")
    for sid in range(NUM_THREADS):
        session_id = f"challenger_session_{sid}"
        for m in range(20):
            db.add_chat_message(session_id, "user" if m % 2 == 0 else "agent", f"Seed message {m} for session {sid}")

    # Barrier to release all 50 threads simultaneously for maximum contention
    barrier = threading.Barrier(NUM_THREADS)

    def concurrent_worker(thread_id: int):
        session_id = f"challenger_session_{thread_id}"
        barrier.wait()

        for c in range(CALLS_PER_THREAD):
            # 1. Measure create_job() latency
            t0 = time.perf_counter()
            try:
                job_id = task_manager.create_job(
                    prompt=f"Bench task T{thread_id}-C{c}",
                    agent_id="coding_agent"
                )
                t1 = time.perf_counter()
                create_job_latencies.append((t1 - t0) * 1000.0)
            except Exception as e:
                err = f"create_job error: {type(e).__name__}: {e}"
                if "locked" in str(e).lower() or "busy" in str(e).lower():
                    lock_errors.append(err)
                else:
                    other_errors.append(err)

            # 2. Measure get_chat_history() latency
            t2 = time.perf_counter()
            try:
                hist = db.get_chat_history(session_id=session_id, limit=20)
                t3 = time.perf_counter()
                get_chat_latencies.append((t3 - t2) * 1000.0)
                if not hist:
                    other_errors.append(f"Empty history for {session_id}")
            except Exception as e:
                err = f"get_chat_history error: {type(e).__name__}: {e}"
                if "locked" in str(e).lower() or "busy" in str(e).lower():
                    lock_errors.append(err)
                else:
                    other_errors.append(err)

            # 3. Interleaving write load to create ongoing database traffic
            try:
                db.add_chat_message(session_id, "user", f"Interleaved write T{thread_id}-C{c}")
            except Exception as e:
                err = f"add_chat_message error: {type(e).__name__}: {e}"
                if "locked" in str(e).lower() or "busy" in str(e).lower():
                    lock_errors.append(err)
                else:
                    other_errors.append(err)

    print(f"\n[Step 2] Executing {NUM_THREADS} threads with simultaneous barrier release...")
    threads = [threading.Thread(target=concurrent_worker, args=(i,)) for i in range(NUM_THREADS)]
    wall_start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    wall_duration = (time.perf_counter() - wall_start) * 1000.0

    print(f"All {NUM_THREADS} threads finished in {wall_duration:.2f} ms")

    # Flush any async persist queues
    task_manager.flush()

    # Step 3: Compute latency stats
    cj_stats = compute_percentiles(create_job_latencies)
    ch_stats = compute_percentiles(get_chat_latencies)

    print("\n" + "-" * 80)
    print("EMPIRICAL LATENCY RESULTS UNDER 50 CONCURRENT THREADS:")
    print("-" * 80)
    print(f"create_job() ({cj_stats['count']} calls):")
    print(f"  Min:  {cj_stats['min']:.4f} ms")
    print(f"  p50:  {cj_stats['p50']:.4f} ms (SLA < 5.0 ms: {'PASS' if cj_stats['p50'] < 5.0 else 'FAIL'})")
    print(f"  p90:  {cj_stats['p90']:.4f} ms")
    print(f"  p95:  {cj_stats['p95']:.4f} ms (SLA < 5.0 ms: {'PASS' if cj_stats['p95'] < 5.0 else 'FAIL'})")
    print(f"  p99:  {cj_stats['p99']:.4f} ms")
    print(f"  Max:  {cj_stats['max']:.4f} ms")
    print(f"  Avg:  {cj_stats['avg']:.4f} ms (SLA < 5.0 ms: {'PASS' if cj_stats['avg'] < 5.0 else 'FAIL'})")

    print(f"\nget_chat_history() ({ch_stats['count']} calls):")
    print(f"  Min:  {ch_stats['min']:.4f} ms")
    print(f"  p50:  {ch_stats['p50']:.4f} ms (SLA < 5.0 ms: {'PASS' if ch_stats['p50'] < 5.0 else 'FAIL'})")
    print(f"  p90:  {ch_stats['p90']:.4f} ms")
    print(f"  p95:  {ch_stats['p95']:.4f} ms (SLA < 5.0 ms: {'PASS' if ch_stats['p95'] < 5.0 else 'FAIL'})")
    print(f"  p99:  {ch_stats['p99']:.4f} ms")
    print(f"  Max:  {ch_stats['max']:.4f} ms")
    print(f"  Avg:  {ch_stats['avg']:.4f} ms (SLA < 5.0 ms: {'PASS' if ch_stats['avg'] < 5.0 else 'FAIL'})")

    print(f"\nConcurrency Errors:")
    print(f"  'Database is locked' errors: {len(lock_errors)} (SLA = 0: {'PASS' if len(lock_errors) == 0 else 'FAIL'})")
    print(f"  Other errors:                {len(other_errors)} (SLA = 0: {'PASS' if len(other_errors) == 0 else 'FAIL'})")

    # Step 4: Vacuum and file size check
    print("\n[Step 4] Checking Final DB Size & Integrity...")
    vac_res = db.vacuum_and_checkpoint()
    final_bytes = SQLITE_DB_PATH.stat().st_size
    final_mb = final_bytes / (1024 * 1024)
    print(f"Final DB Size: {final_mb:.2f} MB ({final_bytes} bytes) (SLA < 15.0 MB: {'PASS' if final_mb < 15.0 else 'FAIL'})")
    print(f"Integrity Check: {vac_res['integrity']}")

    all_passed = (
        cj_stats['avg'] < 5.0 and
        ch_stats['avg'] < 5.0 and
        len(lock_errors) == 0 and
        len(other_errors) == 0 and
        final_mb < 15.0 and
        vac_res['integrity'].lower() == "ok"
    )

    verdict = "APPROVE" if all_passed else "REJECT"
    print("\n" + "=" * 80)
    print(f"FINAL CHALLENGER 2 BENCHMARK VERDICT: {verdict}")
    print("=" * 80)

    summary_data = {
        "wall_duration_ms": round(wall_duration, 2),
        "create_job_stats": cj_stats,
        "get_chat_history_stats": ch_stats,
        "lock_errors_count": len(lock_errors),
        "other_errors_count": len(other_errors),
        "final_db_size_mb": round(final_mb, 2),
        "integrity": vac_res['integrity'],
        "verdict": verdict
    }

    out_file = _ROOT / "scratch" / "challenger_latency_concurrency_summary.json"
    with open(out_file, "w") as f:
        json.dump(summary_data, f, indent=2)
    print(f"Saved benchmark summary to: {out_file}")

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
