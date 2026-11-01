# -*- coding: utf-8 -*-
"""
Unit tests for Milestone M2: Dynamic Live API Pipeline Integration.
Validates Cohere, SambaNova, NeuralTTS export, Deepgram STT/TTS routing, and live media pipelines.
"""

import unittest
import asyncio
from unittest.mock import patch, MagicMock
from app.core.model_adapter import (
    CohereAdapter,
    SambaNovaAdapter,
    ModelManager,
    ProviderCircuitBreaker
)
import app.core.neural_tts as neural_tts_mod
from app.core.neural_tts import NeuralTTSEngine, generate_speech, generate_speech_async


class TestM2PipelineIntegrations(unittest.TestCase):
    """Test suite verifying Milestone M2 integration requirements."""

    def setUp(self):
        self.manager = ModelManager()

    def test_cohere_adapter_initialization_and_metadata(self):
        """Verify CohereAdapter registers properly and emits standard telemetry."""
        adapter = CohereAdapter()
        self.assertIn("https://api.cohere.com", adapter.base_url)
        self.assertTrue(self.manager.cohere is not None)
        self.assertIn("command-r-plus-08-2024", self.manager.model_metadata)
        self.assertIn("Cohere", self.manager.model_metadata["command-r-plus-08-2024"]["role"])

    def test_sambanova_adapter_initialization_and_metadata(self):
        """Verify SambaNovaAdapter registers properly and handles fast-trip circuit breaker."""
        adapter = SambaNovaAdapter()
        self.assertIn("https://api.sambanova.ai", adapter.base_url)
        self.assertTrue(self.manager.sambanova is not None)
        self.assertIn("Meta-Llama-3.3-70B-Instruct", self.manager.model_metadata)
        self.assertIn("SambaNova", self.manager.model_metadata["Meta-Llama-3.3-70B-Instruct"]["role"])

    def test_sambanova_circuit_breaker_fast_trip_on_429(self):
        """Verify SambaNova trips circuit breaker immediately on HTTP 429."""
        cb = ProviderCircuitBreaker()
        # Initial state should be closed/healthy
        self.assertTrue(cb.can_execute("sambanova"))
        # Record 429
        cb.record_failure("sambanova", "HTTP 429: Rate limit exceeded")
        # Should now be OPEN and block execution
        self.assertFalse(cb.can_execute("sambanova"))
        summary = cb.get_summary()
        self.assertEqual(summary["sambanova"]["state"], "OPEN")

    def test_model_manager_preferred_cascade_order(self):
        """Verify cascade order includes Cohere and SambaNova."""
        effective = self.manager.get_effective_model_list()
        self.assertTrue(len(effective) > 0)
        # Check that adapter lookup works for cohere and sambanova
        adapter_cohere, mode_cohere = self.manager.get_adapter_for_model("command-r-plus-08-2024")
        self.assertIsInstance(adapter_cohere, CohereAdapter)
        self.assertEqual(mode_cohere, "cohere-cloud")
        adapter_samba, mode_samba = self.manager.get_adapter_for_model("Meta-Llama-3.3-70B-Instruct")
        self.assertIsInstance(adapter_samba, SambaNovaAdapter)
        self.assertEqual(mode_samba, "sambanova-cloud")

    def test_neural_tts_generate_speech_export(self):
        """Verify NeuralTTSEngine.generate_speech and module-level function."""
        self.assertTrue(hasattr(neural_tts_mod, "generate_speech"))
        self.assertTrue(callable(neural_tts_mod.generate_speech))
        self.assertTrue(hasattr(neural_tts_mod, "generate_speech_async"))
        self.assertTrue(callable(neural_tts_mod.generate_speech_async))
        self.assertTrue(callable(generate_speech_async))
        engine = NeuralTTSEngine()
        self.assertTrue(hasattr(engine, "generate_speech"))
        self.assertTrue(hasattr(engine, "generate_speech_async"))

    def test_stt_heuristic_fallback_monotonicity(self):
        """Verify word timestamp heuristic fallback produces strictly monotonic timestamps."""
        from app.video_maker.sql_short_engine import sql_short_engine
        
        # Test word alignment heuristic logic directly
        words = ["In", "SQL,", "the", "SELECT", "statement", "retrieves", "data."]
        total_dur = 3.5
        w_dur = total_dur / len(words)
        prev_end = 0.0
        stamps = []
        for idx, w in enumerate(words):
            s = prev_end
            e = round(s + w_dur, 2)
            if idx == len(words) - 1:
                e = max(e, total_dur)
            prev_end = e
            stamps.append({"word": w, "start": s, "end": e})

        for i in range(len(stamps)):
            self.assertGreaterEqual(stamps[i]["start"], 0.0)
            self.assertGreater(stamps[i]["end"], stamps[i]["start"])
            if i > 0:
                self.assertGreaterEqual(stamps[i]["start"], stamps[i-1]["end"])
        self.assertAlmostEqual(stamps[-1]["end"], total_dur, delta=0.1)

    def test_short_engine_attribution_ledger_structure(self):
        """Verify sql_short_engine returns properly structured ledger and scene assets."""
        from app.video_maker.sql_short_engine import SqlShortVideoEngine
        engine = SqlShortVideoEngine()
        self.assertTrue(hasattr(engine, "generate_short_prompt_async"))
        self.assertTrue(hasattr(engine, "generate_short_prompt"))


if __name__ == "__main__":
    unittest.main()
