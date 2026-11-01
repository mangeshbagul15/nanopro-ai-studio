# -*- coding: utf-8 -*-
"""
Milestone M2 Iteration 2 Gate Verification:
Adversarial Concurrency & Stress Testing for ProviderCircuitBreaker and ModelManager Cascade.

Author: Challenger M2-It2-1 (Adversarial Quality & Empirical Verification)
"""

import io
import time
import json
import unittest
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, MagicMock

from app.core.model_adapter import (
    CircuitBreakerState,
    ProviderCircuitBreaker,
    ModelManager,
    TelemetryDict
)


class TestCircuitBreakerConcurrencyStress(unittest.TestCase):
    """Stress tests circuit breaker fast-trip, thread-safety, and canary limits under high concurrency."""

    def test_concurrent_fast_trip_race_condition(self):
        """
        Stress test: 50 concurrent threads simultaneously recording HTTP 429 errors.
        Verifies:
        1. No deadlocks or race conditions on the internal RLock.
        2. Breaker trips to OPEN immediately.
        3. All subsequent can_execute() calls return False.
        """
        cb = ProviderCircuitBreaker(failure_threshold=3, recovery_timeout=1.0)
        num_threads = 50
        errors = [
            urllib.error.HTTPError(
                url="https://api.sambanova.ai/v1/chat/completions",
                code=429,
                msg="Too Many Requests",
                hdrs={},
                fp=io.BytesIO(b'{"error": "rate limit"}')
            )
            for _ in range(num_threads)
        ]

        def worker(err):
            cb.record_failure("sambanova", err)
            return cb.can_execute("sambanova")

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(worker, err) for err in errors]
            results = [f.result() for f in as_completed(futures)]

        self.assertEqual(cb.get_state("sambanova"), CircuitBreakerState.OPEN)
        self.assertFalse(cb.can_execute("sambanova"))
        summary = cb.get_summary()["sambanova"]
        self.assertEqual(summary["state"], CircuitBreakerState.OPEN)
        self.assertEqual(summary["failures"], num_threads)

    def test_can_execute_sub_millisecond_throughput_when_open(self):
        """
        Benchmark: 5,000 queries to can_execute() while circuit is OPEN across 10 threads.
        Verifies average check latency is sub-millisecond (< 0.05ms) with zero blocking.
        """
        cb = ProviderCircuitBreaker(failure_threshold=3, recovery_timeout=10.0)
        cb.trip("groq")
        self.assertFalse(cb.can_execute("groq"))

        total_calls = 5000
        num_workers = 10

        def check_batch(n):
            denied = 0
            for _ in range(n):
                if not cb.can_execute("groq"):
                    denied += 1
            return denied

        t0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            batch_size = total_calls // num_workers
            futures = [executor.submit(check_batch, batch_size) for _ in range(num_workers)]
            total_denied = sum(f.result() for f in as_completed(futures))
        elapsed = time.perf_counter() - t0

        avg_latency_ms = (elapsed / total_calls) * 1000
        self.assertEqual(total_denied, total_calls, "Every single call must be denied instantly")
        self.assertLess(avg_latency_ms, 0.05, f"Check must be < 0.05ms, took {avg_latency_ms:.4f}ms")

    def test_half_open_single_canary_probe_under_concurrency(self):
        """
        Concurrency test: When circuit transitions from OPEN to HALF_OPEN,
        exactly ONE thread must be granted permission (can_execute == True)
        to probe the provider, and all other concurrent threads must receive False.
        """
        cb = ProviderCircuitBreaker(failure_threshold=3, recovery_timeout=0.05, half_open_success_threshold=2)
        cb.trip("cohere")
        self.assertEqual(cb.get_state("cohere"), CircuitBreakerState.OPEN)

        # Wait for recovery timeout to expire
        time.sleep(0.07)

        # Breaker should now be ready for HALF_OPEN
        num_concurrent_threads = 30
        results = []

        def probe_worker():
            return cb.can_execute("cohere")

        with ThreadPoolExecutor(max_workers=num_concurrent_threads) as executor:
            futures = [executor.submit(probe_worker) for _ in range(num_concurrent_threads)]
            results = [f.result() for f in as_completed(futures)]

        allowed_probes = [r for r in results if r is True]
        denied_probes = [r for r in results if r is False]

        self.assertEqual(len(allowed_probes), 1, "Exactly ONE canary probe must be permitted in HALF_OPEN")
        self.assertEqual(len(denied_probes), num_concurrent_threads - 1, "All other concurrent requests must be rejected")
        self.assertEqual(cb.get_state("cohere"), CircuitBreakerState.HALF_OPEN)

        # Successful canary completes recovery
        cb.record_success("cohere")
        cb.record_success("cohere")
        self.assertEqual(cb.get_state("cohere"), CircuitBreakerState.CLOSED)
        self.assertTrue(cb.can_execute("cohere"))

    def test_concurrent_cascade_under_multi_provider_failure(self):
        """
        Stress test: 25 concurrent threads calling ModelManager.route_and_execute
        when SambaNova fails with 429 and Cohere fails with 410.
        All 25 threads must smoothly cascade to the healthy provider (Ollama)
        without hanging, leaking exceptions, or failing.
        """
        mm = ModelManager()
        # Mock availability
        mm.sambanova.is_available = MagicMock(return_value=True)
        mm.cohere.is_available = MagicMock(return_value=True)
        mm.ollama.is_available = MagicMock(return_value=True)

        call_counts = {"sambanova": 0, "cohere": 0, "ollama": 0}

        def fake_sambanova_chat(*args, **kwargs):
            call_counts["sambanova"] += 1
            err = urllib.error.HTTPError(
                url="https://api.sambanova.ai/v1/chat/completions",
                code=429,
                msg="Too Many Requests",
                hdrs={},
                fp=io.BytesIO(b'{"error": {"message": "Rate limit reached"}}')
            )
            mm.circuit_breaker.record_failure("sambanova", err)
            raise RuntimeError(f"SambaNova API HTTP 429: Rate limit reached")

        def fake_cohere_chat(*args, **kwargs):
            call_counts["cohere"] += 1
            err = urllib.error.HTTPError(
                url="https://api.cohere.com/v2/chat",
                code=410,
                msg="Gone",
                hdrs={},
                fp=io.BytesIO(b'{"message": "Endpoint retired"}')
            )
            mm.circuit_breaker.record_failure("cohere", err)
            raise RuntimeError(f"Cohere API Error (410): Endpoint retired")

        def fake_ollama_chat(*args, **kwargs):
            call_counts["ollama"] += 1
            return "Ollama fallback script successfully generated", TelemetryDict({
                "latency_ms": 12.0,
                "token_count": 40,
                "tokens_per_second": 333.3,
                "tps": 333.3,
                "model": "qwen2.5-coder:3b",
                "provider": "ollama",
                "mode": "ollama"
            })

        mm.sambanova.chat = MagicMock(side_effect=fake_sambanova_chat)
        mm.cohere.chat = MagicMock(side_effect=fake_cohere_chat)
        mm.ollama.chat = MagicMock(side_effect=fake_ollama_chat)

        num_requests = 25
        models_requested = ["Meta-Llama-3.3-70B-Instruct", "command-r-plus-08-2024", "qwen2.5-coder:3b"]

        def execute_request(i):
            content, model_used, telemetry, latency_ms = mm.route_and_execute(
                prompt=f"Create scene {i}",
                task_type="general",
                models=models_requested
            )
            return model_used, content

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(execute_request, i) for i in range(num_requests)]
            results = [f.result() for f in as_completed(futures)]

        # All requests must have succeeded with Ollama
        for model_used, content in results:
            self.assertEqual(model_used, "qwen2.5-coder:3b")
            self.assertIn("Ollama fallback", content)

        # Verify circuit breaker states
        self.assertEqual(mm.circuit_breaker.get_state("sambanova"), CircuitBreakerState.OPEN)
        self.assertEqual(mm.circuit_breaker.get_state("cohere"), CircuitBreakerState.OPEN)

        # After the initial failure trips the breaker, subsequent concurrent requests
        # must bypass failing providers without invoking their .chat() methods again!
        self.assertLess(call_counts["sambanova"], 5, f"SambaNova should have fast-tripped after initial failure, got {call_counts['sambanova']}")
        self.assertLess(call_counts["cohere"], 5, f"Cohere should have fast-tripped after initial failure, got {call_counts['cohere']}")
        self.assertEqual(call_counts["ollama"], num_requests, "All 25 requests must be processed by Ollama")


if __name__ == "__main__":
    unittest.main()
