"""
Hypothesis verification: Does avoiding `with conn:` in get_chat_history eliminate transaction commit lock contention?
"""

import sys
import time
import json
import threading
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from app.core.database import db

def compute_percentiles(values):
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

# 1. Standard with conn: (current implementation)
def standard_get_chat_history(session_id: str, limit: int = 20):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations WHERE session_id = ? ORDER BY id ASC LIMIT ?", (session_id, limit))
        results = [dict(r) for r in cursor.fetchall()]
        cursor.close()
        return results

# 2. Optimized pure read without transaction context manager
def pure_read_get_chat_history(session_id: str, limit: int = 20):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conversations WHERE session_id = ? ORDER BY id ASC LIMIT ?", (session_id, limit))
    results = [dict(r) for r in cursor.fetchall()]
    cursor.close()
    return results

def bench_func(func, name: str):
    NUM_THREADS = 50
    CALLS = 10
    latencies = []
    barrier = threading.Barrier(NUM_THREADS)

    def worker(tid: int):
        barrier.wait()
        for _ in range(CALLS):
            t0 = time.perf_counter()
            func(f"bench_sess_50_{tid % 10}", 20)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(NUM_THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    stats = compute_percentiles(latencies)
    print(f"[{name}] under 50 threads:")
    print(f"  Min: {stats['min']} ms, p50: {stats['p50']} ms, p95: {stats['p95']} ms, Avg: {stats['avg']} ms")

bench_func(standard_get_chat_history, "Standard with-conn (Transaction Commit)")
bench_func(pure_read_get_chat_history, "Pure Read without-transaction")
