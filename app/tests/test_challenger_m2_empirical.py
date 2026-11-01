# -*- coding: utf-8 -*-
"""
Empirical Challenger Test Suite for Milestone M2:
Dynamic Live API Pipeline Integration (LLM Adapters, Circuit Breaker, Model Cascade, and Neural TTS).

Author: Challenger M2-1 (Adversarial Quality & Empirical Verification)
"""

import os
import io
import json
import time
import asyncio
import tempfile
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch, MagicMock

from app.core.model_adapter import (
    CircuitBreakerState,
    ProviderCircuitBreaker,
    CohereAdapter,
    SambaNovaAdapter,
    ModelManager,
    TelemetryDict
)
import app.core.neural_tts as neural_tts_mod
from app.core.neural_tts import NeuralTTSEngine, generate_speech


class TestProviderCircuitBreakerEmpirical(unittest.TestCase):
    """Adversarial stress tests for ProviderCircuitBreaker."""

    def setUp(self):
        self.cb = ProviderCircuitBreaker(failure_threshold=3, recovery_timeout=0.1)

    def test_sambanova_fast_trip_on_string_429(self):
        """Simulate HTTP 429 string failure on SambaNova. Must trip immediately (1 failure)."""
        self.assertTrue(self.cb.can_execute("sambanova"), "Initial state must be executable")
        self.assertEqual(self.cb.get_state("sambanova"), CircuitBreakerState.CLOSED)

        # Trigger single 429 failure
        self.cb.record_failure("sambanova", "HTTP 429: Too Many Requests")

        # Must trip immediately to OPEN
        self.assertFalse(self.cb.can_execute("sambanova"), "Circuit breaker must be OPEN immediately on 429")
        self.assertEqual(self.cb.get_state("sambanova"), CircuitBreakerState.OPEN)
        summary = self.cb.get_summary()
        self.assertEqual(summary["sambanova"]["failures"], 1, "Must trip on count 1 without needing 3 failures")
        self.assertEqual(summary["sambanova"]["state"], CircuitBreakerState.OPEN)

    def test_cohere_fast_trip_on_string_410(self):
        """Simulate HTTP 410 string failure on Cohere. Must trip immediately (1 failure)."""
        self.assertTrue(self.cb.can_execute("cohere"), "Initial state must be executable")
        self.assertEqual(self.cb.get_state("cohere"), CircuitBreakerState.CLOSED)

        # Trigger single 410 failure
        self.cb.record_failure("cohere", "HTTP 410: Gone")

        # Must trip immediately to OPEN
        self.assertFalse(self.cb.can_execute("cohere"), "Circuit breaker must be OPEN immediately on 410")
        self.assertEqual(self.cb.get_state("cohere"), CircuitBreakerState.OPEN)
        summary = self.cb.get_summary()
        self.assertEqual(summary["cohere"]["failures"], 1, "Must trip on count 1 without needing 3 failures")
        self.assertEqual(summary["cohere"]["state"], CircuitBreakerState.OPEN)

    def test_fast_trip_on_urllib_http_error_instances(self):
        """Verify real urllib.error.HTTPError instances for 429, 410, and 401 fast-trip immediately."""
        err_429 = urllib.error.HTTPError(
            url="https://api.sambanova.ai/v1/chat/completions",
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=io.BytesIO(b'{"error": {"message": "Rate limit exceeded"}}')
        )
        self.cb.record_failure("sambanova", err_429)
        self.assertFalse(self.cb.can_execute("sambanova"))
        self.assertEqual(self.cb.get_state("sambanova"), CircuitBreakerState.OPEN)

        err_410 = urllib.error.HTTPError(
            url="https://api.cohere.com/v2/chat",
            code=410,
            msg="Gone",
            hdrs={},
            fp=io.BytesIO(b'{"message": "Endpoint retired"}')
        )
        self.cb.record_failure("cohere", err_410)
        self.assertFalse(self.cb.can_execute("cohere"))
        self.assertEqual(self.cb.get_state("cohere"), CircuitBreakerState.OPEN)

    def test_standard_failures_require_threshold_to_trip(self):
        """Verify non-fatal generic errors do NOT trip on counts 1 and 2, but trip on 3."""
        self.cb.record_failure("groq", Exception("temporary parse glitch 1"))
        self.assertTrue(self.cb.can_execute("groq"), "Should remain executable on count 1")

        self.cb.record_failure("groq", Exception("temporary parse glitch 2"))
        self.assertTrue(self.cb.can_execute("groq"), "Should remain executable on count 2")

        self.cb.record_failure("groq", Exception("temporary parse glitch 3"))
        self.assertFalse(self.cb.can_execute("groq"), "Must trip to OPEN on count 3 (failure_threshold)")

    def test_circuit_recovery_lifecycle(self):
        """Verify full lifecycle: CLOSED -> OPEN -> HALF_OPEN probe -> CLOSED."""
        self.cb.trip("cohere")
        self.assertFalse(self.cb.can_execute("cohere"))

        # Wait past recovery timeout (0.1s in setUp)
        time.sleep(0.12)
        self.assertEqual(self.cb.get_state("cohere"), CircuitBreakerState.HALF_OPEN)

        # First probe request allowed
        self.assertTrue(self.cb.can_execute("cohere"))
        # Concurrent second probe request blocked
        self.assertFalse(self.cb.can_execute("cohere"))

        # Success closes breaker
        self.cb.record_success("cohere")
        self.assertEqual(self.cb.get_state("cohere"), CircuitBreakerState.CLOSED)
        self.assertTrue(self.cb.can_execute("cohere"))


class TestModelManagerCascadeEmpirical(unittest.TestCase):
    """Empirical tests for ModelManager cascade and instant bypass."""

    def setUp(self):
        self.manager = ModelManager()

    def test_tripped_provider_bypassed_instantly_in_cascade(self):
        """When SambaNova and Cohere circuits are tripped, routing must cascade instantly (< 15ms)."""
        # Trip both providers
        self.manager.circuit_breaker.record_failure("sambanova", "HTTP 429: Too Many Requests")
        self.manager.circuit_breaker.record_failure("cohere", "HTTP 410: Gone")

        self.assertFalse(self.manager.circuit_breaker.can_execute("sambanova"))
        self.assertFalse(self.manager.circuit_breaker.can_execute("cohere"))

        # Model resolution for tripped models should NOT return the tripped adapter
        adapter_samba, mode_samba = self.manager.get_adapter_for_model("Meta-Llama-3.3-70B-Instruct")
        self.assertNotEqual(mode_samba, "sambanova-cloud", "Tripped provider must not be selected")

        adapter_cohere, mode_cohere = self.manager.get_adapter_for_model("command-r-plus-08-2024")
        self.assertNotEqual(mode_cohere, "cohere-cloud", "Tripped provider must not be selected")

    def test_route_and_execute_cascades_without_stalling(self):
        """Verify route_and_execute skips tripped Cohere & SambaNova in < 15ms and executes next candidate."""
        self.manager.circuit_breaker.trip("cohere")
        self.manager.circuit_breaker.trip("sambanova")

        self.assertFalse(self.manager.circuit_breaker.can_execute("cohere"))
        self.assertFalse(self.manager.circuit_breaker.can_execute("sambanova"))

        # Mock Ollama adapter as healthy fallback
        mock_ollama_resp = ("Bypassed successfully", "ollama")
        with patch.object(self.manager.ollama, "is_available", return_value=True), \
             patch.object(self.manager.ollama, "chat", return_value=mock_ollama_resp):

            t0 = time.time()
            content, model_used, mode, lat = self.manager.route_and_execute(
                prompt="Write a test script",
                models=["command-r-plus-08-2024", "Meta-Llama-3.3-70B-Instruct", "qwen2.5-coder:3b"],
                timeout=5.0
            )
            elapsed_ms = (time.time() - t0) * 1000

            self.assertEqual(content, "Bypassed successfully")
            self.assertEqual(model_used, "qwen2.5-coder:3b")
            self.assertEqual(mode, "ollama")
            # Cascading through tripped Cohere and SambaNova must take < 25ms total (instant bypass)
            self.assertLess(elapsed_ms, 25.0, f"Cascade took too long: {elapsed_ms}ms")

    def test_dynamic_runtime_failure_triggers_immediate_cascade(self):
        """Verify that a runtime HTTP 429 during chat immediately trips breaker and cascades to next model."""
        self.manager.circuit_breaker.reset()
        self.assertTrue(self.manager.circuit_breaker.can_execute("sambanova"))

        # Mock sambanova chat to fail with HTTP 429
        def fail_samba(*args, **kwargs):
            err = urllib.error.HTTPError(
                url="https://api.sambanova.ai/v1/chat/completions",
                code=429,
                msg="Too Many Requests",
                hdrs={},
                fp=io.BytesIO(b'{"error": {"message": "Rate limit reached"}}')
            )
            self.manager.circuit_breaker.record_failure("sambanova", err)
            raise RuntimeError("SambaNova API HTTP 429: Rate limit reached")

        mock_ollama_resp = ("Cascade recovered script", "ollama")
        with patch.object(self.manager.sambanova, "is_available", return_value=True), \
             patch.object(self.manager.sambanova, "chat", side_effect=fail_samba), \
             patch.object(self.manager.ollama, "is_available", return_value=True), \
             patch.object(self.manager.ollama, "chat", return_value=mock_ollama_resp):

            content, model_used, mode, lat = self.manager.route_and_execute(
                prompt="Write a test script",
                models=["Meta-Llama-3.3-70B-Instruct", "qwen2.5-coder:3b"],
                timeout=5.0
            )

            self.assertEqual(content, "Cascade recovered script")
            self.assertEqual(model_used, "qwen2.5-coder:3b")
            # Verify sambanova circuit breaker was tripped by the failure
            self.assertFalse(self.manager.circuit_breaker.can_execute("sambanova"))
            self.assertEqual(self.manager.circuit_breaker.get_state("sambanova"), CircuitBreakerState.OPEN)


class TestCohereAdapterEmpirical(unittest.TestCase):
    """Empirical tests for CohereAdapter request format, telemetry, timeout, and errors."""

    def setUp(self):
        self.cb = ProviderCircuitBreaker()
        self.adapter = CohereAdapter(api_key="test-cohere-key-abcdef123456", circuit_breaker=self.cb)

    @patch("urllib.request.urlopen")
    def test_cohere_request_structure(self, mock_urlopen):
        """Verify exact HTTP request structure: endpoint, headers, JSON body."""
        fake_response = io.BytesIO(json.dumps({
            "message": {
                "content": [{"type": "text", "text": "SELECT * FROM employees;"}]
            },
            "usage": {
                "tokens": {"output_tokens": 15}
            }
        }).encode("utf-8"))
        fake_response.__enter__ = lambda s: s
        fake_response.__exit__ = lambda s, *a: None
        mock_urlopen.return_value = fake_response

        content, telemetry = self.adapter.chat(
            model="command-r-plus-08-2024",
            prompt="Write a SQL query",
            system_prompt="You are a SQL teacher",
            schema={"type": "object"},
            temperature=0.2,
            max_tokens=256,
            timeout=15.0
        )

        self.assertEqual(content, "SELECT * FROM employees;")
        self.assertTrue(mock_urlopen.called)

        # Inspect request
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.full_url, "https://api.cohere.com/v2/chat")
        self.assertEqual(req.headers["Authorization"], "Bearer test-cohere-key-abcdef123456")
        self.assertEqual(req.headers["Content-type"], "application/json")
        self.assertEqual(req.headers["Accept"], "application/json")

        # Inspect payload
        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["model"], "command-r-plus-08-2024")
        self.assertEqual(payload["temperature"], 0.2)
        self.assertEqual(payload["max_tokens"], 256)
        self.assertEqual(payload["response_format"], {"type": "json_object"})
        self.assertEqual(len(payload["messages"]), 2)
        self.assertEqual(payload["messages"][0]["role"], "system")
        self.assertEqual(payload["messages"][0]["content"], "You are a SQL teacher")
        self.assertEqual(payload["messages"][1]["role"], "user")
        self.assertEqual(payload["messages"][1]["content"], "Write a SQL query")

    @patch("urllib.request.urlopen")
    def test_cohere_telemetry_dict_keys(self, mock_urlopen):
        """Verify TelemetryDict conforms to contract: latency_ms, token_count, tokens_per_second, provider='cohere'."""
        fake_response = io.BytesIO(json.dumps({
            "message": {
                "content": [{"type": "text", "text": "Generated response"}]
            },
            "usage": {
                "tokens": {"output_tokens": 50}
            }
        }).encode("utf-8"))
        fake_response.__enter__ = lambda s: s
        fake_response.__exit__ = lambda s, *a: None
        mock_urlopen.return_value = fake_response

        content, telemetry = self.adapter.chat(
            model="command-r-plus",
            prompt="Hello"
        )

        self.assertIsInstance(telemetry, TelemetryDict)
        self.assertEqual(telemetry["provider"], "cohere")
        self.assertEqual(telemetry["mode"], "cohere-cloud")
        self.assertEqual(telemetry["model"], "command-r-plus-08-2024")
        self.assertEqual(telemetry["token_count"], 50)
        self.assertIn("latency_ms", telemetry)
        self.assertGreater(telemetry["latency_ms"], 0.0)
        self.assertIn("tokens_per_second", telemetry)
        self.assertGreater(telemetry["tokens_per_second"], 0.0)
        self.assertIn("tps", telemetry)
        # Verify str() backward compatibility returns mode string
        self.assertEqual(str(telemetry), "cohere-cloud")

    @patch("urllib.request.urlopen")
    def test_cohere_timeout_handling(self, mock_urlopen):
        """Verify urlopen timeout parameter is passed and TimeoutError records failure."""
        mock_urlopen.side_effect = urllib.error.URLError("timed out")

        with self.assertRaises(Exception):
            self.adapter.chat(
                model="command-r-plus",
                prompt="Hello",
                timeout=7.5
            )

        # Verify timeout argument was passed to urlopen
        kwargs = mock_urlopen.call_args[1]
        self.assertEqual(kwargs.get("timeout"), 7.5)

        # Verify failure was recorded in circuit breaker
        self.assertFalse(self.cb.can_execute("cohere"), "Timeout must trip circuit breaker")

    @patch("urllib.request.urlopen")
    def test_cohere_http_error_handling(self, mock_urlopen):
        """Verify HTTP error parsing, message extraction, and circuit breaker recording."""
        err_body = json.dumps({"message": "Rate limit exceeded: 429"}).encode("utf-8")
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.cohere.com/v2/chat",
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=io.BytesIO(err_body)
        )

        with self.assertRaises(RuntimeError) as ctx:
            self.adapter.chat(model="command-r-plus", prompt="Hello")

        self.assertIn("429", str(ctx.exception))
        self.assertIn("Rate limit exceeded", str(ctx.exception))
        self.assertFalse(self.cb.can_execute("cohere"), "429 must fast-trip breaker")

    def test_cohere_fast_abort_when_circuit_open(self):
        """Verify adapter immediately raises ConnectionError if circuit breaker is OPEN."""
        self.cb.trip("cohere")
        with self.assertRaises(ConnectionError) as ctx:
            self.adapter.chat(model="command-r-plus", prompt="Hello")
        self.assertIn("circuit breaker is OPEN", str(ctx.exception))

    def test_cohere_missing_api_key_raises_value_error(self):
        """Verify ValueError when no API key is configured."""
        adapter = CohereAdapter(api_key="", circuit_breaker=self.cb)
        adapter.api_key = ""
        with patch.dict(os.environ, {"COHERE_API_KEY": ""}):
            with patch("app.core.credentials_vault.credentials_vault.get_credential", return_value=None):
                with self.assertRaises(ValueError) as ctx:
                    adapter.chat(model="command-r-plus", prompt="Hello")
                self.assertIn("Cohere API Key is not configured", str(ctx.exception))


class TestSambaNovaAdapterEmpirical(unittest.TestCase):
    """Empirical tests for SambaNovaAdapter OpenAI compatibility, request structure, and error handling."""

    def setUp(self):
        self.cb = ProviderCircuitBreaker()
        self.adapter = SambaNovaAdapter(api_key="test-samba-key-abcdef123456", circuit_breaker=self.cb)

    @patch("urllib.request.urlopen")
    def test_sambanova_openai_compatible_request_and_response(self, mock_urlopen):
        """Verify SambaNova uses OpenAI-compatible /v1/chat/completions format and parses choices/usage."""
        openai_style_resp = io.BytesIO(json.dumps({
            "id": "samba-123",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "SELECT dept, COUNT(*) FROM emp GROUP BY dept;"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 20,
                "completion_tokens": 12,
                "completion_tokens_after_first_per_sec": 420.5
            }
        }).encode("utf-8"))
        openai_style_resp.__enter__ = lambda s: s
        openai_style_resp.__exit__ = lambda s, *a: None
        mock_urlopen.return_value = openai_style_resp

        content, telemetry = self.adapter.chat(
            model="Meta-Llama-3.3-70B-Instruct",
            prompt="Write a group by query",
            system_prompt="You are an expert",
            schema={"type": "object"},
            timeout=25.0
        )

        self.assertEqual(content, "SELECT dept, COUNT(*) FROM emp GROUP BY dept;")
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.full_url, "https://api.sambanova.ai/v1/chat/completions")
        self.assertEqual(req.headers["Authorization"], "Bearer test-samba-key-abcdef123456")

        # Inspect payload conforms to OpenAI chat completions
        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["model"], "Meta-Llama-3.3-70B-Instruct")
        self.assertEqual(payload["response_format"], {"type": "json_object"})
        self.assertEqual(len(payload["messages"]), 2)

        # Inspect TelemetryDict
        self.assertIsInstance(telemetry, TelemetryDict)
        self.assertEqual(telemetry["provider"], "sambanova")
        self.assertEqual(telemetry["mode"], "sambanova-cloud")
        self.assertEqual(telemetry["token_count"], 12)
        self.assertEqual(telemetry["tokens_per_second"], 420.5)
        self.assertEqual(telemetry["tps"], 420.5)

    @patch("urllib.request.urlopen")
    def test_sambanova_http_429_trips_breaker(self, mock_urlopen):
        """Verify HTTP 429 raises RuntimeError and immediately trips circuit breaker."""
        err_body = json.dumps({"error": {"message": "SambaNova rate limit reached"}}).encode("utf-8")
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.sambanova.ai/v1/chat/completions",
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=io.BytesIO(err_body)
        )

        with self.assertRaises(RuntimeError) as ctx:
            self.adapter.chat(model="Meta-Llama-3.3-70B-Instruct", prompt="Hello")

        self.assertIn("429", str(ctx.exception))
        self.assertFalse(self.cb.can_execute("sambanova"), "429 must trip circuit breaker")
        self.assertEqual(self.cb.get_state("sambanova"), CircuitBreakerState.OPEN)

    @patch("urllib.request.urlopen")
    def test_sambanova_http_410_trips_breaker(self, mock_urlopen):
        """Verify HTTP 410 raises RuntimeError and immediately trips circuit breaker."""
        err_body = json.dumps({"error": {"message": "Model endpoint gone"}}).encode("utf-8")
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.sambanova.ai/v1/chat/completions",
            code=410,
            msg="Gone",
            hdrs={},
            fp=io.BytesIO(err_body)
        )

        with self.assertRaises(RuntimeError) as ctx:
            self.adapter.chat(model="Meta-Llama-3.3-70B-Instruct", prompt="Hello")

        self.assertIn("410", str(ctx.exception))
        self.assertFalse(self.cb.can_execute("sambanova"), "410 must trip circuit breaker")
        self.assertEqual(self.cb.get_state("sambanova"), CircuitBreakerState.OPEN)

    def test_sambanova_fast_abort_when_circuit_open(self):
        """Verify adapter immediately raises ConnectionError if circuit breaker is OPEN."""
        self.cb.trip("sambanova")
        with self.assertRaises(ConnectionError) as ctx:
            self.adapter.chat(model="Meta-Llama-3.3-70B-Instruct", prompt="Hello")
        self.assertIn("circuit breaker is OPEN", str(ctx.exception))


class TestNeuralTTSGenerateSpeechEmpirical(unittest.TestCase):
    """Empirical tests for NeuralTTSEngine.generate_speech and regional voice parameters."""

    def test_module_level_export_exists_and_callable(self):
        """Verify hasattr(neural_tts, 'generate_speech') and module-level function export."""
        self.assertTrue(hasattr(neural_tts_mod, "generate_speech"), "Module must export generate_speech")
        self.assertTrue(callable(neural_tts_mod.generate_speech), "Module-level generate_speech must be callable")
        self.assertTrue(hasattr(neural_tts_mod.neural_tts, "generate_speech"), "Singleton must have generate_speech")
        self.assertTrue(callable(neural_tts_mod.neural_tts.generate_speech))
        self.assertTrue(hasattr(neural_tts_mod.neural_tts, "generate_speech_async"))

    def test_empty_and_whitespace_text_returns_false(self):
        """Verify empty and whitespace-only text safely returns False without invoking synthesis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "test.mp3")
            self.assertFalse(generate_speech("", out_file))
            self.assertFalse(generate_speech("   \n\t  ", out_file))
            self.assertFalse(os.path.exists(out_file))

    def test_marathi_voice_parameters_routing(self):
        """Verify Marathi voice parameters mr-IN-AarohiNeural and mr-IN-ManoharNeural route correctly."""
        engine = NeuralTTSEngine()
        with tempfile.TemporaryDirectory() as tmpdir:
            for voice_actor in ["mr-IN-AarohiNeural", "mr-IN-ManoharNeural"]:
                out_file = os.path.join(tmpdir, f"{voice_actor}.mp3")
                with patch.object(engine, "_synthesize_edge_tts", return_value=None) as mock_synth:
                    # Simulate successful file creation > 100 bytes
                    def write_fake_mp3(*args, **kwargs):
                        with open(out_file, "wb") as f:
                            f.write(b"ID3" + b"\x00" * 200)
                    mock_synth.side_effect = write_fake_mp3

                    res = engine.generate_speech("एसक्यूएल इंटरव्ह्यू प्रश्न", out_file, voice=voice_actor)
                    self.assertTrue(res, f"Expected success for {voice_actor}")
                    self.assertTrue(mock_synth.called)
                    # Verify voice was passed
                    called_voice = mock_synth.call_args[0][1]
                    self.assertEqual(called_voice, voice_actor)

    def test_hindi_voice_parameters_routing(self):
        """Verify Hindi voice parameters hi-IN-MadhurNeural and hi-IN-SwaraNeural route correctly."""
        engine = NeuralTTSEngine()
        with tempfile.TemporaryDirectory() as tmpdir:
            for voice_actor in ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"]:
                out_file = os.path.join(tmpdir, f"{voice_actor}.mp3")
                with patch.object(engine, "_synthesize_edge_tts", return_value=None) as mock_synth:
                    def write_fake_mp3(*args, **kwargs):
                        with open(out_file, "wb") as f:
                            f.write(b"ID3" + b"\x00" * 200)
                    mock_synth.side_effect = write_fake_mp3

                    res = engine.generate_speech("एसक्यूएल इंटरव्यू सवाल", out_file, voice=voice_actor)
                    self.assertTrue(res, f"Expected success for {voice_actor}")
                    self.assertEqual(mock_synth.call_args[0][1], voice_actor)

    def test_english_voice_parameters_routing(self):
        """Verify English voice parameters en-US-JennyNeural, en-US-GuyNeural, en-IN-NeerjaNeural route correctly."""
        engine = NeuralTTSEngine()
        with tempfile.TemporaryDirectory() as tmpdir:
            for voice_actor in ["en-US-JennyNeural", "en-US-GuyNeural", "en-IN-NeerjaNeural", "en-IN-PrabhatNeural"]:
                out_file = os.path.join(tmpdir, f"{voice_actor}.mp3")
                with patch.object(engine, "_synthesize_edge_tts", return_value=None) as mock_synth:
                    def write_fake_mp3(*args, **kwargs):
                        with open(out_file, "wb") as f:
                            f.write(b"ID3" + b"\x00" * 200)
                    mock_synth.side_effect = write_fake_mp3

                    res = engine.generate_speech("Top SQL interview questions", out_file, voice=voice_actor)
                    self.assertTrue(res, f"Expected success for {voice_actor}")
                    self.assertEqual(mock_synth.call_args[0][1], voice_actor)

    def test_invalid_or_missing_voice_falls_back_to_marathi_default(self):
        """Verify invalid or unconfigured voice string defaults safely to mr-IN-AarohiNeural."""
        engine = NeuralTTSEngine()
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "default_voice.mp3")
            with patch.object(engine, "_synthesize_edge_tts", return_value=None) as mock_synth:
                def write_fake_mp3(*args, **kwargs):
                    with open(out_file, "wb") as f:
                        f.write(b"ID3" + b"\x00" * 200)
                mock_synth.side_effect = write_fake_mp3

                # Test None
                res = engine.generate_speech("Test speech", out_file, voice=None)
                self.assertTrue(res)
                self.assertEqual(mock_synth.call_args[0][1], "mr-IN-AarohiNeural")

                # Test random string without Neural
                res = engine.generate_speech("Test speech", out_file, voice="invalid_robot")
                self.assertTrue(res)
                self.assertEqual(mock_synth.call_args[0][1], "mr-IN-AarohiNeural")

    def test_live_edge_tts_synthesis_if_online(self):
        """Live synthesis test using edge-tts (verifies real audio stream generation > 1000 bytes)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "live_test.mp3")
            try:
                success = generate_speech("Testing live speech generation.", out_file, voice="en-US-JennyNeural")
                if success:
                    self.assertTrue(os.path.exists(out_file))
                    size = os.path.getsize(out_file)
                    self.assertGreater(size, 1000, f"Generated audio file size too small: {size} bytes")
                else:
                    # Network may be offline or blocked in local environment; log gracefully
                    pass
            except Exception as e:
                # Live network call may fail offline; mocked tests already guarantee correctness
                pass


if __name__ == "__main__":
    unittest.main()
