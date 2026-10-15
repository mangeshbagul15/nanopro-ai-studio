"""
Empirical SLA Benchmark: 20 Threads (Baseline SLA) vs 50 Threads (Stress SLA)
"""

import sys
import time
import json
import threading
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from app.core.database import db
from app.core.task_manager import task_manager

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

def run_bench(num_threads: int, calls_per_thread: int):
    create_job_latencies = []
    get_chat_latencies = []
    lock_errors = []

    # Pre-seed session
    for tid in range(num_threads):
        db.add_chat_message(f"bench_sess_{num_threads}_{tid}", "user", "seed message")

    barrier = threading.Barrier(num_threads)

    def worker(tid: int):
        sess = f"bench_sess_{num_threads}_{tid}"
        barrier.wait()
        for c in range(calls_per_thread):
            # create_job
            t0 = time.perf_counter()
            try:
                task_manager.create_job(f"bench prompt {tid}-{c}", agent_id="manager")
            except Exception as e:
                if "locked" in str(e).lower() or "busy" in str(e).lower():
                    lock_errors.append(str(e))
            t1 = time.perf_counter()
            create_job_latencies.append((t1 - t0) * 1000.0)

            # get_chat_history
            t2 = time.perf_counter()
            try:
                db.get_chat_history(sess, limit=10)
            except Exception as e:
                if "locked" in str(e).lower() or "busy" in str(e).lower():
                    lock_errors.append(str(e))
            t3 = time.perf_counter()
            get_chat_latencies.append((t3 - t2) * 1000.0)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    task_manager.flush()
    return {
        "threads": num_threads,
        "create_job": compute_percentiles(create_job_latencies),
        "get_chat_history": compute_percentiles(get_chat_latencies),
        "lock_errors": len(lock_errors)
    }

print("Running 20-thread benchmark...")
r20 = run_bench(20, 25)
print("20-Thread Results:")
print("  create_job:", r20["create_job"])
print("  get_chat_history:", r20["get_chat_history"])
print("  lock_errors:", r20["lock_errors"])

print("\nRunning 50-thread benchmark...")
r50 = run_bench(50, 10)
print("50-Thread Results:")
print("  create_job:", r50["create_job"])
print("  get_chat_history:", r50["get_chat_history"])
print("  lock_errors:", r50["lock_errors"])
