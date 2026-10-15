"""
Adversarial Stress Test Harness for NanoPro AI Studio
Target: ModelManager, ProviderCircuitBreaker, and Failover Cascade in app/core/model_adapter.py
Author: Challenger 1 (Empirical Challenger)

Tests:
1. High-frequency 429 bursts (100 rapid concurrent calls to Groq)
2. Transient network disconnects, TCP connection drops, and socket timeouts
3. Half-open state oscillation and recovery under jitter
4. Concurrent multithreaded failover (multiple threads hitting ModelManager while Groq trips)
5. Failover cascade latency SLA (< 500ms) under simulated provider outage
6. Fastpath conversational queries latency SLA (< 10ms) under load
"""

import sys
import time
import socket
import http.client
import urllib.error
import threading
import concurrent.futures
from pathlib import Path
from typing import Dict, Any, List, Tuple
from unittest.mock import patch, MagicMock

# Ensure repo root is on path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from app.core.model_adapter import (
    ModelManager,
    ProviderCircuitBreaker,
    CircuitBreakerState,
    GroqAdapter,
    GeminiAdapter,
    OllamaAdapter,
    TelemetryDict,
    model_manager,
    provider_circuit_breaker
)
from app.core.conversational_intelligence import conversational_intelligence


def calculate_percentiles(latencies: List[float]) -> Dict[str, float]:
    if not latencies:
        return {"count": 0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "min": 0.0, "max": 0.0, "avg": 0.0}
    s = sorted(latencies)
    n = len(s)
    def pct(p):
        idx = min(int(round(p * n)), n - 1)
        return s[idx]
    return {
        "count": n,
        "p50": round(pct(0.50), 3),
        "p95": round(pct(0.95), 3),
        "p99": round(pct(0.99), 3),
        "min": round(s[0], 3),
        "max": round(s[-1], 3),
        "avg": round(sum(s) / n, 3)
    }


# ==============================================================================
# TEST 1: High-Frequency 429 Bursts (100 rapid concurrent calls to Groq)
# ==============================================================================
def run_test_1_high_frequency_429_burst() -> Dict[str, Any]:
    print("\n" + "=" * 80)
    print("TEST 1: HIGH-FREQUENCY 429 BURSTS (100 RAPID CONCURRENT CALLS TO GROQ)")
    print("=" * 80)

    cb = ProviderCircuitBreaker(failure_threshold=3, recovery_timeout=30.0)
    groq = GroqAdapter(api_key="gsk_adversarial_test_key", circuit_breaker=cb)

    groq_call_counter = 0
    counter_lock = threading.Lock()

    def mock_create(*args, **kwargs):
        nonlocal groq_call_counter
        with counter_lock:
            groq_call_counter += 1
        time.sleep(0.002)  # 2ms simulate network roundtrip
        raise Exception("429 Too Many Requests: Rate limit reached for default-org")

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = mock_create
    groq._client = mock_client

    results = []
    latencies = []

    def worker(idx: int):
        t0 = time.perf_counter()
        try:
            groq.chat("openai/gpt-oss-120b", f"Test burst query {idx}")
            lat = (time.perf_counter() - t0) * 1000
            return (True, None, lat)
        except Exception as e:
            lat = (time.perf_counter() - t0) * 1000
            return (False, str(e), lat)

    # Launch 100 threads concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as pool:
        futures = [pool.submit(worker, i) for i in range(100)]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            results.append(res)
            latencies.append(res[2])

    failures = [r for r in results if not r[0]]
    fast_aborts = [r for r in results if not r[0] and "circuit breaker is OPEN" in r[1]]
    direct_429s = [r for r in results if not r[0] and "429" in r[1]]

    stats = calculate_percentiles(latencies)
    final_state = cb.get_state("groq")

    print(f"Total concurrent calls: {len(results)}")
    print(f"Total failures: {len(failures)}")
    print(f"Calls that actually reached Groq API before trip: {groq_call_counter}")
    print(f"Direct 429 errors from Groq API: {len(direct_429s)}")
    print(f"Fast-aborted by Circuit Breaker: {len(fast_aborts)}")
    print(f"Final Circuit Breaker State: {final_state}")
    print(f"Latency Percentiles: p50={stats['p50']}ms, p95={stats['p95']}ms, p99={stats['p99']}ms, max={stats['max']}ms")

    passed = (
        final_state == CircuitBreakerState.OPEN
        and len(failures) == 100
        and len(fast_aborts) > 0
        and groq_call_counter <= 20  # Fast trip should prevent the bulk of calls from hitting Groq
    )
    status_str = "PASS" if passed else "FAIL"
    print(f"Result: [{status_str}]")
    return {
        "test": "High-Frequency 429 Bursts",
        "passed": passed,
        "total_calls": len(results),
        "groq_calls_reached": groq_call_counter,
        "fast_aborts": len(fast_aborts),
        "final_state": final_state,
        "latencies": stats
    }


# ==============================================================================
# TEST 2: Transient Disconnects, TCP Drops, and Socket Timeouts
# ==============================================================================
def run_test_2_network_disconnects_and_timeouts() -> Dict[str, Any]:
    print("\n" + "=" * 80)
    print("TEST 2: TRANSIENT NETWORK DISCONNECTS, TCP DROPS, AND SOCKET TIMEOUTS")
    print("=" * 80)

    # Matrix of realistic network errors
    error_matrix = [
        ("ConnectionResetError (WinError 10054)", ConnectionResetError(10054, "An existing connection was forcibly closed by the remote host")),
        ("socket.timeout", socket.timeout("timed out")),
        ("http.client.RemoteDisconnected", http.client.RemoteDisconnected("Remote end closed connection without response")),
        ("urllib.error.URLError (gaierror)", urllib.error.URLError(socket.gaierror(11001, "getaddrinfo failed"))),
        ("TimeoutError", TimeoutError("The write operation timed out")),
        ("ConnectionAbortedError", ConnectionAbortedError("Software caused connection abort")),
        ("BrokenPipeError", BrokenPipeError("Broken pipe")),
        ("503 Service Unavailable", urllib.error.HTTPError("https://api.groq.com", 503, "Service Unavailable", {}, None)),
        ("502 Bad Gateway", urllib.error.HTTPError("https://api.groq.com", 502, "Bad Gateway", {}, None)),
        ("504 Gateway Timeout", urllib.error.HTTPError("https://api.groq.com", 504, "Gateway Timeout", {}, None)),
        ("529 Overloaded", urllib.error.HTTPError("https://api.groq.com", 529, "Site Overloaded", {}, None)),
        ("429 RateLimitError", Exception("Error code: 429 - {'error': {'message': 'Rate limit reached'}}")),
        ("Generic Network Disconnect String", RuntimeError("Groq Disconnect during streaming"))
    ]

    findings = []
    all_passed = True

    for name, err in error_matrix:
        cb = ProviderCircuitBreaker(failure_threshold=3, recovery_timeout=30.0)
        groq = GroqAdapter(api_key="gsk_adversarial_test_key", circuit_breaker=cb)

        create_mock = MagicMock()
        create_mock.side_effect = err
        mock_client = MagicMock()
        mock_client.chat.completions.create = create_mock
        groq._client = mock_client

        t0 = time.perf_counter()
        caught = False
        try:
            groq.chat("openai/gpt-oss-120b", "Test prompt")
        except Exception:
            caught = True
        dur_ms = (time.perf_counter() - t0) * 1000

        state = cb.get_state("groq")
        calls = create_mock.call_count
        fast_tripped = (state == CircuitBreakerState.OPEN)

        # Did it fast-abort or did it retry 4 times across all models?
        retried_all_models = (calls > 1)

        finding = {
            "error_type": name,
            "fast_tripped": fast_tripped,
            "call_count": calls,
            "retried_all_models": retried_all_models,
            "latency_ms": round(dur_ms, 2)
        }
        findings.append(finding)

        # Adversarial criteria:
        # A network drop / timeout / 5xx / 429 should:
        # 1. Trip circuit breaker to OPEN on 1st failure (<1ms)
        # 2. NOT sequentially retry all 4 models on Groq if it's a provider-level connection failure!
        if not fast_tripped:
            print(f"  [VULNERABILITY] {name} DID NOT fast-trip circuit breaker to OPEN (calls={calls}, state={state})")
            all_passed = False
        elif retried_all_models:
            print(f"  [BOTTLENECK] {name} triggered sequential retry across {calls} models on Groq instead of instant failover!")
            all_passed = False
        else:
            print(f"  [PASS] {name} -> fast-trip OPEN in {dur_ms:.2f}ms after {calls} call")

    status_str = "PASS" if all_passed else "FAIL (Vulnerabilities Detected)"
    print(f"Result: [{status_str}]")
    return {
        "test": "Network Disconnects and Timeouts",
        "passed": all_passed,
        "findings": findings
    }


# ==============================================================================
# TEST 3: Half-Open State Oscillation and Recovery under Jitter
# ==============================================================================
def run_test_3_half_open_oscillation_under_jitter() -> Dict[str, Any]:
    print("\n" + "=" * 80)
    print("TEST 3: HALF-OPEN STATE OSCILLATION AND RECOVERY UNDER JITTER")
    print("=" * 80)

    cb = ProviderCircuitBreaker(failure_threshold=3, recovery_timeout=0.05)

    # 1. Force trip to OPEN
    cb.trip("groq", Exception("Initial trip"))
    assert cb.get_state("groq") == CircuitBreakerState.OPEN

    # 2. Wait for recovery timeout to transition to HALF_OPEN
    time.sleep(0.06)
    assert cb.get_state("groq") == CircuitBreakerState.HALF_OPEN
    print("  Successfully transitioned to HALF_OPEN after cooldown.")

    # 3. Adversarial Jitter Test:
    # 50 concurrent requests hit the circuit breaker while in HALF_OPEN.
    # Half of the requests succeed (simulate intermittent recovery),
    # and half fail with 429 (simulate server still throttling).
    state_history = []
    history_lock = threading.Lock()

    def jitter_worker(worker_id: int):
        # Even IDs succeed, odd IDs fail
        is_success = (worker_id % 2 == 0)
        can = cb.can_execute("groq")
        with history_lock:
            state_history.append((worker_id, "can_execute", can, cb.get_state("groq")))

        time.sleep(0.001)  # tiny simulated network duration
        if is_success:
            cb.record_success("groq")
        else:
            cb.record_failure("groq", Exception("429 RateLimitError"))

        with history_lock:
            state_history.append((worker_id, "after_report", is_success, cb.get_state("groq")))

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
        futures = [pool.submit(jitter_worker, i) for i in range(50)]
        concurrent.futures.wait(futures)

    final_state = cb.get_state("groq")

    # Analyze state transitions and flapping
    transitions = [s[3] for s in state_history]
    unique_states = set(transitions)
    flaps = 0
    for i in range(1, len(transitions)):
        if transitions[i] != transitions[i - 1]:
            flaps += 1

    print(f"Total concurrency operations during HALF_OPEN: {len(state_history)}")
    print(f"State transition count (flaps): {flaps}")
    print(f"Unique states observed: {unique_states}")
    print(f"Final circuit breaker state after jitter: {final_state}")

    # Check for canary gating: In HALF_OPEN, does cb allow ALL 50 threads through?
    can_exec_results = [s[2] for s in state_history if s[1] == "can_execute"]
    allowed_count = sum(1 for c in can_exec_results if c is True)
    print(f"Number of requests allowed through in HALF_OPEN: {allowed_count} / {len(can_exec_results)}")

    thundering_herd = (allowed_count > 5)
    if thundering_herd:
        print(f"  [ARCHITECTURAL FLAW] Thundering Herd detected! HALF_OPEN allowed {allowed_count} simultaneous requests without canary gating!")

    # Check for race condition: Did a success overwrite an active 429 trip?
    passed = (final_state in [CircuitBreakerState.OPEN, CircuitBreakerState.CLOSED])
    status_str = "WARNING (Oscillation & Thundering Herd in Half-Open)" if thundering_herd else "PASS"
    print(f"Result: [{status_str}]")

    return {
        "test": "Half-Open State Oscillation and Jitter",
        "passed": not thundering_herd,
        "thundering_herd": thundering_herd,
        "allowed_in_half_open": allowed_count,
        "flaps": flaps,
        "final_state": final_state
    }


# ==============================================================================
# TEST 4: Concurrent Multithreaded Failover & Telemetry Thread Safety
# ==============================================================================
def run_test_4_concurrent_failover_and_telemetry() -> Dict[str, Any]:
    print("\n" + "=" * 80)
    print("TEST 4: CONCURRENT MULTITHREADED FAILOVER & TELEMETRY INTEGRITY")
    print("=" * 80)

    mm = ModelManager()

    # Pre-populate Ollama cache to avoid test environment Ollama probe hang
    mm.ollama._cached_models = (time.time(), ["qwen2.5-coder:3b", "llama3.2:3b"])
    mm.ollama._availability_cache = (time.time(), True)

    groq_call_count = 0
    gemini_call_count = 0
    call_lock = threading.Lock()

    def mock_groq_chat(model, prompt, **kwargs):
        nonlocal groq_call_count
        with call_lock:
            groq_call_count += 1
        # Trip after 3 calls to test mid-flight failover
        raise Exception("429 RateLimit: Groq quota exceeded mid-flight")

    def mock_gemini_chat(model, prompt, **kwargs):
        nonlocal gemini_call_count
        with call_lock:
            gemini_call_count += 1
        time.sleep(0.005)  # 5ms Gemini response
        return "Gemini fallback answer", {"provider": "gemini-cloud", "mode": "gemini-cloud", "latency_ms": 5.0, "token_count": 20, "tps": 400.0}

    mm.groq.chat = mock_groq_chat
    mm.groq.is_available = MagicMock(return_value=True)
    mm.gemini.chat = mock_gemini_chat
    mm.gemini.is_available = MagicMock(return_value=True)

    num_threads = 50
    results = []
    uncaught_exceptions = []

    def client_task(thread_id: int):
        task_type = "coding" if thread_id % 2 == 0 else "dialogue"
        try:
            t0 = time.perf_counter()
            content, model, mode, lat = mm.route_and_execute(
                f"Adversarial concurrent query {thread_id}",
                task_type=task_type
            )
            total_dur = (time.perf_counter() - t0) * 1000
            return (True, content, model, total_dur)
        except Exception as e:
            return (False, str(e), None, 0.0)

    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as pool:
        futures = [pool.submit(client_task, i) for i in range(num_threads)]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            results.append(res)
            if not res[0]:
                uncaught_exceptions.append(res[1])

    successes = [r for r in results if r[0]]
    durations = [r[3] for r in results if r[0]]
    stats = calculate_percentiles(durations)

    # Check telemetry consistency across models
    telemetry_corrupted = False
    for m, t in mm.telemetry.items():
        total = t.get("total_calls", 0)
        succ = t.get("success_count", 0)
        err = t.get("error_count", 0)
        if total != (succ + err):
            print(f"  [RACE CONDITION] Model {m} telemetry mismatch: total({total}) != succ({succ}) + err({err})")
            telemetry_corrupted = True

    print(f"Total concurrent client requests: {num_threads}")
    print(f"Successful requests via failover: {len(successes)} / {num_threads}")
    print(f"Uncaught exceptions thrown to callers: {len(uncaught_exceptions)}")
    print(f"Groq attempts: {groq_call_count}, Gemini successful handoffs: {gemini_call_count}")
    print(f"Failover Latency Stats: p50={stats['p50']}ms, p95={stats['p95']}ms, max={stats['max']}ms")
    print(f"Telemetry Race Condition / Corruption: {telemetry_corrupted}")

    passed = (
        len(uncaught_exceptions) == 0
        and len(successes) == num_threads
        and not telemetry_corrupted
        and stats["p95"] < 500.0
    )
    status_str = "PASS" if passed else "FAIL"
    print(f"Result: [{status_str}]")

    return {
        "test": "Concurrent Multithreaded Failover",
        "passed": passed,
        "total_requests": num_threads,
        "successful_requests": len(successes),
        "uncaught_exceptions": len(uncaught_exceptions),
        "telemetry_corrupted": telemetry_corrupted,
        "latency_percentiles": stats
    }


# ==============================================================================
# TEST 5: Failover Cascade Latency SLA (< 500ms) & Bottleneck Diagnosis
# ==============================================================================
def run_test_5_failover_cascade_latency_sla() -> Dict[str, Any]:
    print("\n" + "=" * 80)
    print("TEST 5: FAILOVER CASCADE LATENCY SLA (< 500ms) & BOTTLENECK DIAGNOSIS")
    print("=" * 80)

    # Scenario 5A: Clean Mocked Environment (Warm Cache)
    mm_warm = ModelManager()
    mm_warm.ollama._cached_models = (time.time(), ["qwen2.5-coder:3b", "llama3.2:3b"])
    mm_warm.ollama._availability_cache = (time.time(), True)

    mm_warm.groq.is_available = MagicMock(return_value=True)
    mm_warm.groq.chat = MagicMock(side_effect=Exception("429 RateLimit"))
    mm_warm.gemini.is_available = MagicMock(return_value=True)
    mm_warm.gemini.chat = MagicMock(return_value=("Gemini response", {"provider": "gemini-cloud", "mode": "gemini-cloud"}))

    warm_latencies = []
    for _ in range(50):
        t0 = time.perf_counter()
        mm_warm.route_and_execute("Test prompt", task_type="coding")
        dur = (time.perf_counter() - t0) * 1000
        warm_latencies.append(dur)
    warm_stats = calculate_percentiles(warm_latencies)
    print(f"Scenario 5A (Warm Cache Groq -> Gemini Failover):")
    print(f"  p50={warm_stats['p50']}ms, p95={warm_stats['p95']}ms, max={warm_stats['max']}ms (< 500ms SLA)")

    # Scenario 5B: Cascade Groq -> Gemini -> Ollama (Cloud Completely Down)
    mm_all = ModelManager()
    mm_all.ollama._cached_models = (time.time(), ["qwen2.5-coder:3b", "llama3.2:3b"])
    mm_all.ollama._availability_cache = (time.time(), True)

    mm_all.groq.is_available = MagicMock(return_value=True)
    mm_all.groq.chat = MagicMock(side_effect=Exception("429 RateLimit"))
    mm_all.gemini.is_available = MagicMock(return_value=True)
    mm_all.gemini.chat = MagicMock(side_effect=TimeoutError("Gemini Timeout"))
    mm_all.ollama.is_available = MagicMock(return_value=True)
    mm_all.ollama.chat = MagicMock(return_value=("Ollama local code", {"provider": "ollama", "mode": "ollama-http"}))

    two_step_latencies = []
    for _ in range(50):
        t0 = time.perf_counter()
        mm_all.route_and_execute("Write code", task_type="coding")
        dur = (time.perf_counter() - t0) * 1000
        two_step_latencies.append(dur)
    two_step_stats = calculate_percentiles(two_step_latencies)
    print(f"Scenario 5B (Two-step Groq -> Gemini -> Ollama Failover):")
    print(f"  p50={two_step_stats['p50']}ms, p95={two_step_stats['p95']}ms, max={two_step_stats['max']}ms (< 500ms SLA)")

    # Scenario 5C: Cold Cache / Uninitialized Ollama Discovery Bottleneck (The Real Bug)
    # When Ollama is offline and _cached_models is None, does list_installed_models block for 1.0s?
    mm_cold = ModelManager()
    mm_cold.groq.is_available = MagicMock(return_value=True)
    mm_cold.groq.chat = MagicMock(side_effect=RuntimeError("Groq Disconnect"))
    mm_cold.gemini.is_available = MagicMock(return_value=True)
    mm_cold.gemini.chat = MagicMock(return_value=("Gemini response", {"provider": "gemini-cloud", "mode": "gemini-cloud"}))

    # Note: mm_cold has _cached_models = None by default
    print("\nScenario 5C: Cold Cache Ollama Probe Bottleneck Test (Unmocked localhost:11434):")
    t0 = time.perf_counter()
    mm_cold.route_and_execute("Test prompt", task_type="dialogue")
    cold_dur = (time.perf_counter() - t0) * 1000
    print(f"  Cold failover cascade latency: {cold_dur:.2f}ms")

    sla_exceeded = (cold_dur >= 500.0)
    if sla_exceeded:
        print(f"  [CRITICAL BOTTLENECK CONFIRMED] Cold failover cascade took {cold_dur:.2f}ms >= 500.0ms SLA!")
        print("  ROOT CAUSE: OllamaAdapter.list_installed_models() invokes synchronous urllib.request.urlopen(timeout=1.0) on every cold route_and_execute!")

    passed = (warm_stats["p95"] < 500.0 and two_step_stats["p95"] < 500.0 and not sla_exceeded)
    status_str = "FAIL (SLA Violated on Cold Start / Cache Miss)" if sla_exceeded else "PASS"
    print(f"Result: [{status_str}]")

    return {
        "test": "Failover Cascade Latency SLA",
        "passed": passed,
        "warm_p95": warm_stats["p95"],
        "two_step_p95": two_step_stats["p95"],
        "cold_latency_ms": round(cold_dur, 2),
        "sla_exceeded": sla_exceeded
    }


# ==============================================================================
# TEST 6: Fastpath Conversational Queries Latency Under Load (< 10ms)
# ==============================================================================
def run_test_6_fastpath_latency_under_load() -> Dict[str, Any]:
    print("\n" + "=" * 80)
    print("TEST 6: FASTPATH CONVERSATIONAL QUERIES LATENCY UNDER LOAD (< 10ms SLA)")
    print("=" * 80)

    test_queries = [
        "KHICHADI KASHI BANAVAYACHI?",
        "I NEED WIFE, HOW CAN I ACHIVE?",
        "why slow respond",
        "neew queck respond",
        "fast replay main key",
        "bore hotay joke sang",
        "namaskar kasa ahes",
        "chaha kasa banvaycha",
        "show me your response time",
        "today wether why heat"
    ]

    total_queries = 1000
    num_workers = 20
    latencies = []
    missed_fastpath = []

    def fastpath_worker(idx: int):
        q = test_queries[idx % len(test_queries)]
        t0 = time.perf_counter()
        resp = conversational_intelligence.dispatch(q.lower(), q)
        dur = (time.perf_counter() - t0) * 1000
        return (resp is not None, q, dur)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as pool:
        futures = [pool.submit(fastpath_worker, i) for i in range(total_queries)]
        for f in concurrent.futures.as_completed(futures):
            hit, q, dur = f.result()
            latencies.append(dur)
            if not hit:
                missed_fastpath.append(q)

    stats = calculate_percentiles(latencies)
    print(f"Total queries executed under concurrent load: {total_queries} (across {num_workers} threads)")
    print(f"Fastpath hits: {total_queries - len(missed_fastpath)} / {total_queries}")
    print(f"Fastpath misses: {len(missed_fastpath)}")
    print(f"Latency Percentiles: p50={stats['p50']}ms, p95={stats['p95']}ms, p99={stats['p99']}ms, max={stats['max']}ms, avg={stats['avg']}ms")

    sla_passed = (stats["p99"] < 10.0 and len(missed_fastpath) == 0)
    status_str = "PASS" if sla_passed else "FAIL"
    print(f"Result: [{status_str}] (SLA: < 10ms at p99)")

    return {
        "test": "Fastpath Latency Under Load",
        "passed": sla_passed,
        "total_queries": total_queries,
        "misses": len(missed_fastpath),
        "latencies": stats
    }


# ==============================================================================
# MAIN HARNESS RUNNER
# ==============================================================================
def main():
    print("=" * 80)
    print("ADVERSARIAL STRESS TEST HARNESS — NANOPRO AI STUDIO MODEL ROUTER")
    print("=" * 80)

    t_start_all = time.time()
    r1 = run_test_1_high_frequency_429_burst()
    r2 = run_test_2_network_disconnects_and_timeouts()
    r3 = run_test_3_half_open_oscillation_under_jitter()
    r4 = run_test_4_concurrent_failover_and_telemetry()
    r5 = run_test_5_failover_cascade_latency_sla()
    r6 = run_test_6_fastpath_latency_under_load()
    total_time = round(time.time() - t_start_all, 2)

    print("\n" + "=" * 80)
    print(f"ALL TESTS COMPLETED IN {total_time}s")
    print("=" * 80)
    print("SUMMARY OF EMPIRICAL ADVERSARIAL FINDINGS:")
    print(f"1. High-Frequency 429 Bursts:                 {'PASS' if r1['passed'] else 'FAIL'}")
    print(f"2. Network Disconnects & Timeouts:            {'PASS' if r2['passed'] else 'FAIL (Vulnerabilities Found)'}")
    print(f"3. Half-Open Oscillation & Jitter:            {'PASS' if r3['passed'] else 'FAIL (Flapping & Thundering Herd)'}")
    print(f"4. Concurrent Failover & Telemetry:           {'PASS' if r4['passed'] else 'FAIL'}")
    print(f"5. Failover Cascade Latency SLA (< 500ms):    {'PASS' if r5['passed'] else 'FAIL (1,000ms+ Cold Discovery Hang)'}")
    print(f"6. Fastpath Latency SLA (< 10ms):             {'PASS' if r6['passed'] else 'FAIL'}")
    print("=" * 80)

    overall_verdict = "APPROVE" if (r1["passed"] and r2["passed"] and r3["passed"] and r4["passed"] and r5["passed"] and r6["passed"]) else "REJECT"
    print(f"FINAL CHALLENGER VERDICT: {overall_verdict}")
    print("=" * 80)

    return {
        "verdict": overall_verdict,
        "results": [r1, r2, r3, r4, r5, r6]
    }


if __name__ == "__main__":
    main()
