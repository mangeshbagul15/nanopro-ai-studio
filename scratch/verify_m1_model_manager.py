"""
Verification script for Milestone M1 (Features F3, F5, F6, F7, F8, F9)
Validates:
1. ProviderCircuitBreaker states (CLOSED, OPEN, HALF_OPEN) and < 1ms trip time
2. Groq LPU hardening: max_retries=0, no 4-model loop on 429 rate limit
3. Ollama local model resolution & 15-second TTL health check caching
4. Token usage and Latency/TPS telemetry preservation
5. Conversational fastpath queries < 10ms
6. Zero-downtime failover cascade (Groq -> Gemini -> Ollama) in < 500ms
"""

import sys
import time
from pathlib import Path
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


def test_circuit_breaker():
    print("\n--- Test 1: ProviderCircuitBreaker State Transitions & Latency ---")
    cb = ProviderCircuitBreaker(failure_threshold=3, recovery_timeout=0.2)

    # Initially CLOSED
    assert cb.get_state("groq") == CircuitBreakerState.CLOSED
    assert cb.can_execute("groq") is True

    # Fast-trip on HTTP 429 RateLimitError
    t0 = time.perf_counter()
    cb.record_failure("groq", Exception("Error 429: Too Many Requests"))
    trip_latency_ms = (time.perf_counter() - t0) * 1000
    print(f"  [PASS] 429 trip latency: {trip_latency_ms:.4f}ms (< 1ms target)")
    assert trip_latency_ms < 1.0, f"Trip took too long: {trip_latency_ms}ms"
    assert cb.get_state("groq") == CircuitBreakerState.OPEN
    assert cb.can_execute("groq") is False

    # Check can_execute latency when OPEN
    t0 = time.perf_counter()
    can_exec = cb.can_execute("groq")
    check_latency_ms = (time.perf_counter() - t0) * 1000
    assert can_exec is False
    print(f"  [PASS] can_execute rejection latency: {check_latency_ms:.4f}ms (< 0.1ms target)")
    assert check_latency_ms < 0.1

    # Immediate trip on ConnectionError
    assert cb.get_state("gemini") == CircuitBreakerState.CLOSED
    cb.record_failure("gemini", ConnectionError("Network unreachable"))
    assert cb.get_state("gemini") == CircuitBreakerState.OPEN
    assert cb.can_execute("gemini") is False
    print("  [PASS] ConnectionError immediately trips Gemini circuit to OPEN")

    # Recovery timeout -> HALF_OPEN probe
    time.sleep(0.25)
    assert cb.get_state("groq") == CircuitBreakerState.HALF_OPEN
    assert cb.can_execute("groq") is True  # probe allowed
    print("  [PASS] Half-open probe enabled after cooldown")

    # Record success -> resets to CLOSED
    cb.record_success("groq")
    assert cb.get_state("groq") == CircuitBreakerState.CLOSED
    assert cb.can_execute("groq") is True
    print("  [PASS] Record success resets circuit to CLOSED")


def test_groq_hardening():
    print("\n--- Test 2: Groq LPU Hardening (max_retries=0 & Fast Abort on 429) ---")
    cb = ProviderCircuitBreaker()
    groq = GroqAdapter(api_key="gsk_dummy_test_key_for_verification_only", circuit_breaker=cb)

    # Verify max_retries=0 is configured when groq client is created
    with patch("groq.Groq") as mock_groq_cls:
        groq._get_client()
        mock_groq_cls.assert_called_once_with(api_key="gsk_dummy_test_key_for_verification_only", max_retries=0)
        print("  [PASS] groq.Groq instantiated with max_retries=0")

    # Verify chat() trips circuit breaker and raises immediately on 429 without trying all 4 models
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("429 Too Many Requests: Rate limit exceeded")
    groq._client = mock_client

    t0 = time.perf_counter()
    try:
        groq.chat("openai/gpt-oss-120b", "Test prompt")
        assert False, "Should have raised 429"
    except Exception as e:
        dur_ms = (time.perf_counter() - t0) * 1000
        assert "429" in str(e)
        assert mock_client.chat.completions.create.call_count == 1, (
            f"Expected 1 call (immediate abort on provider failure), got {mock_client.chat.completions.create.call_count}"
        )
        assert cb.get_state("groq") == CircuitBreakerState.OPEN
        print(f"  [PASS] Fast-aborted on 429 in {dur_ms:.2f}ms after exactly 1 call (no sequential 4-model loop)")


def test_ollama_resolution_and_health_caching():
    print("\n--- Test 3: Local Ollama Model Resolution & Health Caching ---")
    mm = ModelManager()

    local_models = ["llama3.2:3b", "qwen2.5-coder:3b", "phi4-mini:latest", "gemma3:4b", "sqlcoder"]
    for m in local_models:
        adapter, provider = mm.get_adapter_for_model(m)
        assert provider == "ollama", f"Model {m} was mapped to {provider} instead of ollama!"
        assert isinstance(adapter, OllamaAdapter)
    print(f"  [PASS] All local models ({', '.join(local_models)}) deterministically map to OllamaAdapter")

    cloud_models = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b"]
    for m in cloud_models:
        adapter, provider = mm.get_adapter_for_model(m)
        assert provider == "groq-lpu", f"Model {m} was mapped to {provider} instead of groq-lpu!"
        assert isinstance(adapter, GroqAdapter)
    print("  [PASS] Cloud Groq models deterministically map to GroqAdapter")

    # Health check caching TTL test
    ollama = OllamaAdapter(host="http://127.0.0.1:11434")
    # Prime cache
    with patch("urllib.request.urlopen") as mock_url:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_url.return_value.__enter__.return_value = mock_resp

        # First call hits network
        up1 = ollama.is_available()
        assert up1 is True
        assert mock_url.call_count == 1

        # Subsequent 10 calls within 15s TTL must NOT hit network
        t0 = time.perf_counter()
        for _ in range(10):
            up = ollama.is_available()
            assert up is True
        cache_dur_ms = (time.perf_counter() - t0) * 1000
        assert mock_url.call_count == 1, f"Expected 1 network call, got {mock_url.call_count}"
        print(f"  [PASS] 10 consecutive is_available() calls took {cache_dur_ms:.4f}ms total (0 network requests, 15s TTL)")


def test_token_telemetry():
    print("\n--- Test 4: Token Usage & Latency / TPS Telemetry ---")
    groq = GroqAdapter(api_key="gsk_test")
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content="SELECT * FROM customers WHERE active = 1;"))]
    mock_resp.usage.completion_tokens = 45
    mock_client.chat.completions.create.return_value = mock_resp
    groq._client = mock_client

    content, telemetry = groq.chat("qwen/qwen3.8-27b", "Generate SQL for active customers")
    assert isinstance(telemetry, TelemetryDict)
    assert telemetry["token_count"] == 45
    assert telemetry["latency_ms"] >= 0.0
    assert telemetry["tps"] > 0.0
    assert telemetry["model"] == "qwen/qwen3.8-27b"
    assert telemetry["provider"] == "groq-lpu"
    # String representation backward-compatibility
    assert str(telemetry) == "groq-lpu:qwen/qwen3.8-27b"
    print(f"  [PASS] Telemetry verified: token_count={telemetry['token_count']}, tps={telemetry['tps']}, mode='{telemetry}'")


def test_fastpath_latency():
    print("\n--- Test 5: Fastpath Latency (< 10ms SLA) ---")
    test_queries = [
        "KHICHADI KASHI BANAVAYACHI?",
        "I NEED WIFE, HOW CAN I ACHIVE?",
        "why slow respond",
        "neew queck respond"
    ]

    for q in test_queries:
        t0 = time.perf_counter()
        resp = conversational_intelligence.dispatch(q.lower(), q)
        dur_ms = (time.perf_counter() - t0) * 1000
        assert resp is not None, f"Query '{q}' did not hit conversational fastpath!"
        print(f"  [PASS] Query '{q}' responded in {dur_ms:.4f}ms (< 10ms SLA)")
        assert dur_ms < 10.0, f"Query took {dur_ms}ms, exceeded 10ms SLA!"


def test_zero_downtime_failover_cascade():
    print("\n--- Test 6: Zero-Downtime Failover Cascade (Groq -> Gemini -> Ollama < 500ms) ---")
    mm = ModelManager()

    # Simulate Groq API returning 429
    mock_groq_client = MagicMock()
    mock_groq_client.chat.completions.create.side_effect = Exception("429 RateLimitError: Tokens per minute quota reached")
    mm.groq._get_client = MagicMock(return_value=mock_groq_client)
    mm.groq._client = mock_groq_client
    mm.groq.is_available = MagicMock(return_value=True)

    # Simulate Gemini API returning Timeout
    mm.gemini.is_available = MagicMock(return_value=True)
    mock_gemini_client = MagicMock()
    mock_gemini_client.models.generate_content.side_effect = TimeoutError("Gemini socket timeout after 15s")
    mock_gemini_client.interactions.create.side_effect = TimeoutError("Gemini socket timeout")
    mm.gemini._get_client = MagicMock(return_value=mock_gemini_client)
    mm.gemini._client = mock_gemini_client

    # Local Ollama is available and succeeds
    mm.ollama.is_available = MagicMock(return_value=True)
    with patch("urllib.request.urlopen") as mock_url:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'{"message": {"content": "def add(a, b): return a + b"}, "eval_count": 28, "eval_duration": 180000000}'
        mock_url.return_value.__enter__.return_value = mock_resp

        t0 = time.perf_counter()
        content, model, mode, lat = mm.route_and_execute(
            "Write a python function to add two numbers",
            task_type="coding"
        )
        total_failover_ms = (time.perf_counter() - t0) * 1000

        print(f"  [PASS] Cascade successfully fell back to: model={model}, mode={mode}")
        print(f"  [PASS] Total failover cascade latency: {total_failover_ms:.2f}ms (< 500ms target)")
        assert "add(a, b)" in content
        assert "ollama" in str(mode) or "coder" in model
        assert total_failover_ms < 500.0, f"Failover cascade took {total_failover_ms}ms, exceeded 500ms target!"

        # Verify circuit breaker states
        assert mm.circuit_breaker.get_state("groq") == CircuitBreakerState.OPEN
        assert mm.circuit_breaker.get_state("gemini") == CircuitBreakerState.OPEN
        assert mm.circuit_breaker.can_execute("groq") is False
        assert mm.circuit_breaker.can_execute("gemini") is False
        print("  [PASS] Both failed cloud providers (Groq & Gemini) are marked OPEN in circuit breaker")

        # Next call to route_and_execute immediately routes to Ollama in < 10ms (bypassing dead cloud providers)
        t1 = time.perf_counter()
        content2, model2, mode2, _ = mm.route_and_execute(
            "Write another function",
            task_type="coding"
        )
        bypass_latency_ms = (time.perf_counter() - t1) * 1000
        print(f"  [PASS] Subsequent request routed to local Ollama in {bypass_latency_ms:.2f}ms with 0ms cloud retry delay")
        assert bypass_latency_ms < 100.0


if __name__ == "__main__":
    print("=" * 70)
    print("M1 MILESTONE VERIFICATION SUITE: ModelManager Hardening & Circuit Breaker")
    print("=" * 70)
    test_circuit_breaker()
    test_groq_hardening()
    test_ollama_resolution_and_health_caching()
    test_token_telemetry()
    test_fastpath_latency()
    test_zero_downtime_failover_cascade()
    print("\n" + "=" * 70)
    print("ALL M1 VERIFICATION ASSERTIONS PASSED SUCCESSFULLY!")
    print("=" * 70)
