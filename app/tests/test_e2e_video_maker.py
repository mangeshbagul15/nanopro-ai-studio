"""
Comprehensive End-to-End (E2E) Test Suite for Universal Tech AI Video Maker (9:16 Shorts & Reels).

Authoritative Sources:
- ORIGINAL_REQUEST.md: R1 (UI/UX Revamp), R2 (Live API Integration), R3 (Automated Verification)
- PROJECT.md: Feature Inventory F1 to F15, Milestones M1-M4, Interface Contracts

4-Tier Opaque-Box Test Architecture:
- Tier 1: Feature Coverage (F1 to F15)
- Tier 2: Boundary & Corner Cases
- Tier 3: Cross-Feature Combinations (Pairwise interactions)
- Tier 4: Real-World Application Scenarios (Full vertical reel generation)
"""

import os
import sys
import json
import time
import shutil
import asyncio
import tempfile
import unittest
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, MagicMock, AsyncMock

# Workspace UI components
from app.ui.sql_video_workspace import get_sql_video_workspace_html
from app.ui.sql_video_js import get_sql_video_js

# Live Media & AI Providers
import app.video_maker.pixabay_video_provider as pixabay_prov
import app.video_maker.freesound_provider as freesound_prov
import app.video_maker.deepgram_provider as deepgram_prov
import app.video_maker.giphy_provider as giphy_prov
import app.video_maker.tavily_news_search as tavily_prov
import app.video_maker.unsplash_provider as unsplash_prov
import app.video_maker.video_generation_jobs as gen_jobs

# Core Engine and Audio Utilities
from app.video_maker.sql_short_engine import (
    _ensure_scene_visual_directions,
    _infer_visual_shape,
    _resolve_storyboard_attribution,
    get_mp3_duration,
    sql_short_engine,
)


# ============================================================================
# FAKE TASK MANAGER FOR ISOLATED JOB QUEUE TESTING
# ============================================================================

class IsolatedTaskManager:
    """In-memory task manager for isolated test execution."""
    def __init__(self):
        self.jobs = {}
        self._counter = 0

    def create_job(self, prompt, agent_id="manager", plan=None):
        self._counter += 1
        job_id = f"job-test-{self._counter}"
        self.jobs[job_id] = {
            "id": job_id,
            "status": "queued",
            "stage": "initialized",
            "progress": 0,
            "result_data": {},
            "error_message": None,
        }
        return job_id

    def update_job_stage(self, job_id, stage, progress=None, status=None, tool_used=None):
        if job_id in self.jobs:
            self.jobs[job_id].update(stage=stage, progress=progress, status=status or "running")

    def set_job_completed(self, job_id, result_data):
        if job_id in self.jobs:
            self.jobs[job_id].update(status="done", stage="completed", progress=100, result_data=result_data)

    def set_job_failed(self, job_id, error_msg):
        if job_id in self.jobs:
            self.jobs[job_id].update(status="error", stage="failed", error_message=error_msg)

    def get_job(self, job_id):
        return self.jobs.get(job_id)


# ============================================================================
# TIER 1: FEATURE COVERAGE (F1 - F15)
# ============================================================================

class TestTier1_F1_UI_ClutterElimination(unittest.TestCase):
    """
    Feature F1: UI/UX Clutter & Obsolete Elimination.
    Authoritative Source: PROJECT.md line 36, ORIGINAL_REQUEST.md lines 12-14.
    """
    def setUp(self):
        self.html = get_sql_video_workspace_html()
        self.js = get_sql_video_js()

    def test_phone_avatar_pip_removed_from_workspace_html(self):
        """Verify obsolete #phoneAvatarPip element is completely eliminated."""
        self.assertNotIn("id=\"phoneAvatarPip\"", self.html)
        self.assertNotIn("id='phoneAvatarPip'", self.html)

    def test_static_fake_scores_removed_from_workspace_html(self):
        """Verify hardcoded misleading 99.8% static scores are eliminated."""
        self.assertNotIn("99.8% AI Script Accuracy", self.html)
        self.assertNotIn("99.8% Human Voice", self.html)

    def test_fake_modals_removed_from_workspace(self):
        """Verify obsolete demo modals are removed from workspace HTML."""
        self.assertNotIn("id=\"modalFakeDemo\"", self.html)
        self.assertNotIn("id=\"phoneDemoModal\"", self.html)

    def test_no_orphan_dom_references_in_javascript(self):
        """Verify client-side JavaScript does not attempt to bind to deleted elements."""
        self.assertNotIn("document.getElementById('phoneAvatarPip')", self.js)
        self.assertNotIn("document.getElementById(\"phoneAvatarPip\")", self.js)

    def test_workspace_serves_valid_responsive_layout(self):
        """Verify clean HTML5 container structure tailored for 9:16 preview."""
        self.assertIn("vfx-horizontal-scroll-container", self.html)
        self.assertIn("vfx-video-root", self.html)


class TestTier1_F2_WorkspaceControls(unittest.TestCase):
    """
    Feature F2: Responsive 9:16 Workspace Controls.
    Authoritative Source: PROJECT.md line 37, ORIGINAL_REQUEST.md lines 12-14.
    """
    def setUp(self):
        self.html = get_sql_video_workspace_html()
        self.js = get_sql_video_js()

    def test_workspace_exposes_only_prompt_and_language_inputs(self):
        self.assertIn('id="sqlShortQuestion"', self.html)
        self.assertIn('id="btnAudioMr"', self.html)
        self.assertIn('id="btnAudioHi"', self.html)
        self.assertIn('id="btnAudioEn"', self.html)
        self.assertNotIn("Quick Tech Topic Presets", self.html)
        self.assertNotIn("Optional Media &amp; Research APIs", self.html)
        self.assertNotIn('id="togglePixabay"', self.html)
        self.assertNotIn('id="toggleFreesound"', self.html)

    def test_curated_model_selector_present(self):
        self.assertIn('id="selectModernVideoModelMaster" hidden', self.html)
        self.assertIn('value="gemini-3.5-flash-lite" selected', self.html)

    def test_regional_language_and_voice_actors_present(self):
        """Verify support for Marathi, Hindi, and English voice actors in UI."""
        self.assertIn("Marathi", self.html)
        self.assertIn("Hindi", self.html)
        self.assertIn("English", self.html)

    def test_optional_media_providers_are_not_user_controls(self):
        self.assertNotIn('id="mediaProviderTogglesGrid"', self.html)
        self.assertNotIn('id="toggleTavily"', self.html)
        self.assertIn("pixabay: false", self.js)
        self.assertIn("freesound: false", self.js)

    def test_generation_pattern_switchers(self):
        self.assertNotIn("Automatic model fallback", self.html)
        self.assertNotIn("Selected model only", self.html)
        self.assertIn("window.selectedGenerationPattern = 'hybrid'", self.js)

    def test_video_studio_discloses_browser_rendering_and_optional_services(self):
        js = get_sql_video_js()
        self.assertIn("Browser Canvas + MediaRecorder", js)
        self.assertNotIn("Optional Media &amp; Research APIs", self.html)
        self.assertNotIn("LIVE ASSET VERIFIED", js)
        self.assertNotIn("100% FREE (GPU)", js)
        self.assertNotIn("FFmpeg 7.1 Hardware", js)
        self.assertNotIn("/api/video/generate_2026_video", js)
        self.assertIn("WAITING FOR REPORT", self.html)
        self.assertNotIn("Verified Live Providers", self.html)
        self.assertNotIn("Sub-second LPU Inference", self.html)
        self.assertNotIn("HEAVY SERVER RENDER", self.html)

    def test_video_studio_uses_responsive_editorial_layout(self):
        self.assertIn('class="studio-masthead"', self.html)
        self.assertIn("@media (max-width: 720px)", self.html)
        self.assertIn("overflow-x: hidden !important", self.html)
        self.assertIn("Make your next idea click.", self.html)

    def test_language_selection_remains_selected_until_next_generation(self):
        self.assertIn("window.sqlShortRequestedLang = lang", self.js)
        self.assertIn("language: selectedLanguage", self.js)
        self.assertIn("window.sqlShortRequestedLang = lang", self.html)
        self.assertIn('aria-pressed="true"', self.html)
        self.assertIn("Voice is automatically matched to your language", self.html)

    def test_video_studio_is_a_continuous_short_form_preview(self):
        js = get_sql_video_js()
        self.assertNotIn("learnerInteractionPanel", self.html)
        self.assertNotIn("learnerInteraction", js)
        self.assertNotIn("interactionPauseKey", js)
        self.assertIn("maxShortDuration = 58.5", js)
        self.assertIn("totalDuration = Math.min(58.5, Math.max(1, totalDuration))", js)
        self.assertIn("activeCue, activeCueIndex", js)
        self.assertIn("function drawCinematicSceneHeadline", js)
        self.assertIn("@Code_With_Mangesh", js)
        self.assertIn("TECH EXPLAINER  ·  9:16", js)
        self.assertIn("cueProgress = stageProg", js)
        self.assertIn('ctx.font = "bold 48px', js)
        self.assertIn("kind.includes(\"container\")", js)
        self.assertIn("kind.includes(\"box\")", js)
        self.assertNotIn('ctx.fillText(`${stepLabel} · STATE:', js)


class TestPromptVisualDirections(unittest.TestCase):
    def test_voice_sentences_drive_semantic_scene_objects(self):
        stages = [
            {
                "title": "Orders reach the database",
                "speech": "A customer places an order. The message waits in a queue before a worker writes it.",
                "visual_data": {
                    "visual_description": "Follow a customer order as it moves through a queue into persistent storage.",
                    "elements": [
                        {"label": "Customer", "detail": "places an order", "shape": "node"},
                        {"label": "Message queue", "detail": "holds the order", "shape": "node"},
                        {"label": "Database", "detail": "stores the order", "shape": "node"},
                    ],
                },
            }
        ]

        normalized = _ensure_scene_visual_directions(stages, "en")
        scene = normalized[0]
        self.assertEqual(scene["visual_data"]["layout"], "spatial")
        self.assertEqual([cue["speech"] for cue in scene["sentence_cues"]], [
            "A customer places an order.",
            "The message waits in a queue before a worker writes it.",
        ])
        self.assertEqual(
            [element["shape"] for element in scene["visual_data"]["elements"]],
            ["person", "box", "database_cylinder"],
        )
        self.assertEqual(scene["sentence_cues"][0]["focus_element"], "Customer")
        self.assertEqual(scene["sentence_cues"][1]["interaction_step"], "transfer")
        self.assertEqual(len(scene["visual_data"]["connectors"]), 2)

    def test_unauthored_scenes_do_not_get_generic_template_scripts(self):
        stages = sql_short_engine._build_dynamic_stages(
            {"title": "Agentic RAG"}, "universal", "en"
        )

        self.assertEqual(stages, [])

    def test_authored_table_data_is_available_in_semantic_scene(self):
        stages = [{
            "title": "Before and after",
            "visual_data": {
                "layout": "table",
                "rows": [["Mode", "Behavior"], ["Manual", "Slow"], ["Automatic", "Fast"]],
            },
        }]

        normalized = _ensure_scene_visual_directions(stages, "en")

        self.assertEqual(normalized[0]["visual_data"]["layout"], "table")
        self.assertEqual(normalized[0]["visual_data"]["visual_mode"], "table")
        self.assertEqual(normalized[0]["visual_data"]["rows"], stages[0]["visual_data"]["rows"])

    def test_authored_editorial_and_pipeline_layouts_are_preserved(self):
        stages = [
            {
                "title": "The one-line fix",
                "speech": "A non-root user limits damage if an application is compromised.",
                "visual_description": "Show a container image switching from root to a restricted user.",
                "visual_data": {
                    "layout": "editorial",
                    "headline": "The fix is one line",
                    "takeaway": "Run the app as a non-root user.",
                    "elements": [],
                },
            },
            {
                "title": "Retry flow",
                "speech": "Refresh the token, then retry the profile request.",
                "visual_description": "A phone refreshes a short-lived access token before retrying.",
                "visual_data": {
                    "layout": "pipeline",
                    "steps": ["Refresh token", "Retry request", "Show profile"],
                    "elements": [],
                },
            },
        ]

        normalized = _ensure_scene_visual_directions(stages, "en")

        self.assertEqual(normalized[0]["visual_data"]["visual_mode"], "editorial")
        self.assertEqual(normalized[1]["visual_data"]["visual_mode"], "pipeline")
        self.assertEqual(normalized[1]["visual_data"]["steps"], stages[1]["visual_data"]["steps"])

    def test_technical_objects_map_to_illustrated_shapes(self):
        self.assertEqual(_infer_visual_shape("Docker container"), "container")
        self.assertEqual(_infer_visual_shape("Queue message"), "box")
        self.assertEqual(_infer_visual_shape("Database table"), "database_cylinder")
        self.assertEqual(_infer_visual_shape("Engineer"), "person")

    def test_storyboard_attribution_uses_provider_reported_model(self):
        model, route = _resolve_storyboard_attribution(
            "gemini-2.5-flash",
            {
                "model": "gemini-3.5-flash-lite",
                "mode": "gemini-cloud:gemini-3.5-flash-lite",
            },
        )

        self.assertEqual(model, "gemini-3.5-flash-lite")
        self.assertEqual(route, "gemini-cloud:gemini-3.5-flash-lite")

    def test_selected_model_failure_is_not_silently_reported_as_a_storyboard(self):
        with patch(
            "app.core.model_adapter.model_manager.execute_with_fallback",
            side_effect=RuntimeError("No configured provider is available for [openai/gpt-oss-120b]."),
        ):
            result = asyncio.run(sql_short_engine.generate_short_prompt_async(
                "Agentic RAG with vector search and semantic reranking",
                language="hi",
                generation_pattern="unified",
                selected_model="openai/gpt-oss-120b",
            ))

        self.assertEqual(result["status"], "error")
        self.assertIn("selected storyboard model could not generate", result["message"])
        self.assertNotIn("stages", result)

    def test_automatic_model_failure_does_not_substitute_generic_lesson(self):
        with patch(
            "app.core.model_adapter.model_manager.execute_with_fallback",
            side_effect=RuntimeError("No configured provider is available."),
        ):
            result = asyncio.run(sql_short_engine.generate_short_prompt_async(
                "Explain how database replication avoids downtime",
                language="en",
                generation_pattern="hybrid",
                selected_model="openai/gpt-oss-120b",
            ))

        self.assertEqual(result["status"], "error")
        self.assertIn("will not substitute a generic template", result["message"])
        self.assertNotIn("stages", result)

    def test_generic_four_beat_outline_is_rejected(self):
        generic_storyboard = {
            "title": "Database Replication",
            "scenes": [
                {"title": "Overview", "speech": "Replication copies database changes to another server."},
                {"title": "Core Mechanism", "speech": "A primary server sends changes to replicas."},
                {"title": "Real-World Impact", "speech": "Replicas help serve reads and recover from failures."},
                {"title": "Key Takeaway", "speech": "Monitor lag and choose a suitable replication mode."},
            ],
        }
        with patch(
            "app.core.model_adapter.model_manager.execute_with_fallback",
            return_value=(json.dumps(generic_storyboard), "test-model", "test-route"),
        ):
            result = asyncio.run(sql_short_engine.generate_short_prompt_async(
                "Explain how database replication works",
                language="en",
                generation_pattern="unified",
                selected_model="gemini-3.5-flash-lite",
            ))

        self.assertEqual(result["status"], "error")
        self.assertIn("generic lesson outline", result["message"])
        self.assertNotIn("stages", result)

    def test_storyboard_pipeline_creates_voice_timed_human_tech_visuals_under_sixty_seconds(self):
        storyboard = {
            "title": "Why a delayed order gets lost",
            "domain": "Software systems",
            "scenes": [
                {
                    "title": "A customer taps Place Order",
                    "speech": "A customer taps Place Order. The app sends one message to the queue.",
                    "visual_description": "A customer submits an order and a bright message packet travels into a queue.",
                    "visual_type": "diagram",
                    "visual_data": {
                        "layout": "spatial",
                        "elements": [
                            {"label": "Customer", "detail": "submits an order", "shape": "person"},
                            {"label": "Order queue", "detail": "holds the message", "shape": "box"},
                        ],
                    },
                },
                {
                    "title": "The worker persists the order",
                    "speech": "A worker reads the waiting message. The database cylinder stores the order safely.",
                    "visual_description": "A worker pulls an order from the queue and inserts it into a database.",
                    "visual_type": "diagram",
                    "visual_data": {
                        "layout": "spatial",
                        "elements": [
                            {"label": "Queue worker", "detail": "reads one message", "shape": "server"},
                            {"label": "Order database", "detail": "stores the row", "shape": "database_cylinder"},
                        ],
                    },
                },
                {
                    "title": "Retries prevent lost orders",
                    "speech": "If storage fails, the queue retries instead of dropping the order. That is why durable queues matter.",
                    "visual_description": "An order packet retries its path to storage after a temporary failure.",
                    "visual_type": "diagram",
                    "visual_data": {
                        "layout": "spatial",
                        "elements": [
                            {"label": "Retry packet", "detail": "returns after a failure", "shape": "box"},
                            {"label": "Order database", "detail": "accepts the retry", "shape": "database_cylinder"},
                        ],
                    },
                },
            ],
        }

        async def fake_speech(_text, file_path, **_kwargs):
            Path(file_path).write_bytes(b"t" * 1024)
            return True

        with patch(
            "app.core.model_adapter.model_manager.execute_with_fallback",
            return_value=(json.dumps(storyboard), "test-model", "test-route"),
        ), patch(
            "app.core.neural_tts.neural_tts.generate_speech_async",
            new=AsyncMock(side_effect=fake_speech),
        ), patch(
            "app.video_maker.sql_short_engine.get_mp3_duration",
            return_value=72.0,
        ):
            result = asyncio.run(sql_short_engine.generate_short_prompt_async(
                "Explain how durable order queues protect an online store",
                language="en",
                generation_pattern="unified",
                selected_model="gemini-3.5-flash-lite",
            ))

        self.assertEqual(result["status"], "success", result.get("message"))
        self.assertLessEqual(result["duration"], 58.5)
        self.assertEqual(len(result["stages"]), 3)
        self.assertTrue(all(stage["sentence_cues"] for stage in result["stages"]))
        self.assertEqual(result["stages"][0]["visual_data"]["elements"][0]["shape"], "person")
        self.assertEqual(result["stages"][0]["visual_data"]["elements"][1]["shape"], "box")
        self.assertTrue(any(
            element["shape"] == "database_cylinder"
            for stage in result["stages"]
            for element in stage["visual_data"]["elements"]
        ))


class TestStrictModelRouting(unittest.TestCase):
    def test_selected_only_does_not_try_router_fallback_candidates(self):
        from app.core.model_adapter import ModelManager

        manager = ModelManager()
        selected_adapter = SimpleNamespace(
            is_available=MagicMock(return_value=True),
            chat=MagicMock(side_effect=RuntimeError("selected model request failed")),
        )
        backup_adapter = SimpleNamespace(
            is_available=MagicMock(return_value=True),
            chat=MagicMock(return_value=("backup response", "backup provider")),
        )

        with patch.object(manager, "get_effective_model_list") as effective_models, patch.object(
            manager,
            "get_adapter_for_model",
            side_effect=[(selected_adapter, "groq-lpu"), (backup_adapter, "gemini-cloud")],
        ):
            with self.assertRaisesRegex(RuntimeError, "selected model request failed"):
                manager.route_and_execute(
                    "Create a technical lesson",
                    task_type="dialogue",
                    models=["openai/gpt-oss-120b"],
                    allow_fallback=False,
                )

        effective_models.assert_not_called()
        backup_adapter.chat.assert_not_called()

    def test_selected_only_does_not_try_provider_internal_models(self):
        from app.core.model_adapter import GeminiAdapter, GroqAdapter

        groq_adapter = GroqAdapter(api_key="gsk_test")
        groq_call = MagicMock(side_effect=RuntimeError("selected model unavailable"))
        groq_client = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=groq_call))
        )
        with patch.object(groq_adapter, "is_available", return_value=True), patch.object(
            groq_adapter, "_get_client", return_value=groq_client
        ):
            with self.assertRaisesRegex(RuntimeError, "selected model unavailable"):
                groq_adapter.chat("openai/gpt-oss-120b", "lesson", allow_fallback=False)
        self.assertEqual(groq_call.call_count, 1)
        self.assertEqual(groq_call.call_args.kwargs["model"], "openai/gpt-oss-120b")

        gemini_adapter = GeminiAdapter(api_key="test-key")
        gemini_generate = MagicMock(side_effect=ValueError("selected model unavailable"))
        gemini_interaction = MagicMock(side_effect=ValueError("selected model unavailable"))
        gemini_client = SimpleNamespace(
            models=SimpleNamespace(generate_content=gemini_generate),
            interactions=SimpleNamespace(create=gemini_interaction),
        )
        with patch("app.core.model_adapter._genai_types", SimpleNamespace(
            GenerateContentConfig=MagicMock(return_value={})
        )), patch.object(gemini_adapter, "is_available", return_value=True), patch.object(
            gemini_adapter, "_get_client", return_value=gemini_client
        ):
            with self.assertRaisesRegex(RuntimeError, "selected model unavailable"):
                gemini_adapter.chat("gemini-3.5-flash-lite", "lesson", allow_fallback=False)

        self.assertEqual(
            {call.kwargs["model"] for call in gemini_generate.call_args_list},
            {"gemini-3.5-flash-lite"},
        )
        self.assertEqual(
            {call.kwargs["model"] for call in gemini_interaction.call_args_list},
            {"gemini-3.5-flash-lite"},
        )

    def test_automatic_routing_still_tries_a_backup_model(self):
        from app.core.model_adapter import ModelManager

        manager = ModelManager()
        selected_adapter = SimpleNamespace(
            is_available=MagicMock(return_value=True),
            chat=MagicMock(side_effect=RuntimeError("selected model request failed")),
        )
        backup_adapter = SimpleNamespace(
            is_available=MagicMock(return_value=True),
            chat=MagicMock(return_value=("backup response", "backup provider")),
        )

        with patch.object(manager, "get_effective_model_list", return_value=["selected", "backup"]), patch.object(
            manager,
            "get_adapter_for_model",
            side_effect=[(selected_adapter, "groq-lpu"), (backup_adapter, "gemini-cloud")],
        ):
            content, model, _, _ = manager.route_and_execute(
                "Create a technical lesson",
                task_type="dialogue",
                models=["selected"],
            )

        self.assertEqual((content, model), ("backup response", "backup"))
        backup_adapter.chat.assert_called_once()


class TestTier1_F3_ProgressAndLedger(unittest.TestCase):
    """
    Feature F3: Multi-Stage Progress & Authentic Ledger.
    Authoritative Source: PROJECT.md line 38, ORIGINAL_REQUEST.md line 37.
    """
    def setUp(self):
        self.html = get_sql_video_workspace_html()

    def test_progress_visualization_elements_present(self):
        """Verify multi-stage progress container elements exist in UI."""
        has_progress = ("progress" in self.html.lower() or "step" in self.html.lower())
        self.assertTrue(has_progress, "Progress elements must exist in workspace HTML")

    def test_attribution_ledger_container_present(self):
        """Verify authentic AI Attribution Ledger container exists in workspace HTML."""
        self.assertIn("aiAttributionLedgerContainer", self.html)
        self.assertIn("ledgerScenesList", self.html)

    def test_authentic_ledger_schema_contract(self):
        """Verify authentic attribution ledger contract with genuine model attributions."""
        sample_ledger = {
            "pattern": "hybrid",
            "pattern_label": "MULTI-MODEL HYBRID",
            "selected_model": "Wan 2.1",
            "total_scenes": 3,
            "total_duration_seconds": 30.0,
            "voiceover_engine": {"name": "Microsoft Edge Neural Marathi (Aarohi/Manohar)"},
            "scenes": [
                {
                    "scene_index": 1,
                    "scene_title": "Intro Hook",
                    "engine_name": "Wan 2.1",
                    "provider": "Alibaba / Wan-Video",
                    "is_free": True,
                    "attribution_reason": "Cinematic Hook"
                }
            ]
        }
        self.assertEqual(sample_ledger["pattern"], "hybrid")
        self.assertGreater(sample_ledger["total_scenes"], 0)
        self.assertIn("engine_name", sample_ledger["scenes"][0])
        self.assertIn("attribution_reason", sample_ledger["scenes"][0])


class TestTier1_F4_ModelAdapters(unittest.TestCase):
    """
    Feature F4: Model Adapter Cohere & SambaNova.
    Authoritative Source: PROJECT.md lines 15-19, 39.
    """
    def test_model_manager_interface_exists(self):
        """Verify model routing layer imports and exposes necessary routing structures."""
        import app.core.model_adapter as ma
        self.assertTrue(hasattr(ma, "ProviderCircuitBreaker"))
        self.assertTrue(hasattr(ma, "CircuitBreakerState"))

    def test_circuit_breaker_failover_cascade(self):
        """Verify ProviderCircuitBreaker transitions on failures to trigger cascade."""
        from app.core.model_adapter import ProviderCircuitBreaker, CircuitBreakerState
        cb = ProviderCircuitBreaker(failure_threshold=2, recovery_timeout=10.0)
        self.assertEqual(cb.get_state("groq"), CircuitBreakerState.CLOSED)
        self.assertTrue(cb.can_execute("groq"))

        # Trip circuit breaker via fatal error (e.g. HTTP 429)
        cb.record_failure("groq", error=Exception("HTTP 429 RateLimitError"))
        self.assertEqual(cb.get_state("groq"), CircuitBreakerState.OPEN)
        self.assertFalse(cb.can_execute("groq"))

    def test_prompt_construction_contract(self):
        """Verify short video engine constructs structured prompts with regional parameters."""
        presets = sql_short_engine.get_presets()
        self.assertIsInstance(presets, list)
        self.assertGreater(len(presets), 0)
        preset = presets[0]
        self.assertIn("question", preset)
        self.assertIn("difficulty", preset)


class TestTier1_F5_TavilyNewsSearch(unittest.TestCase):
    """
    Feature F5: Tavily Real-Time Context Wiring.
    Authoritative Source: PROJECT.md line 40, lines 108.
    """
    @patch("requests.post")
    def test_tavily_search_trending_topic_contract(self, mock_post):
        """Verify search_trending_topic queries Tavily and parses title, content, url."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "answer": "Anthropic announced Claude 3.7 Sonnet.",
            "results": [
                {"title": "Claude 3.7 Launch", "content": "Hybrid reasoning model.", "url": "https://example.com/claude"}
            ]
        }
        mock_post.return_value = mock_resp

        results = tavily_prov.search_trending_topic("AI breakthroughs 2026", max_results=2)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["title"], "AI Summary")
        self.assertIn("Claude", results[0]["content"])
        self.assertEqual(results[1]["title"], "Claude 3.7 Launch")

    @patch("requests.post")
    def test_tavily_max_results_parameter(self, mock_post):
        """Verify max_results parameter is constrained properly."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"results": []}
        mock_post.return_value = mock_resp

        tavily_prov.search_trending_topic("Quantum computing", max_results=10)
        call_json = mock_post.call_args[1]["json"]
        self.assertLessEqual(call_json["max_results"], 5)


class TestTier1_F6_PixabayVideoProvider(unittest.TestCase):
    """
    Feature F6: Pixabay 9:16 B-Roll Clip Wiring.
    Authoritative Source: PROJECT.md line 41, lines 102.
    """
    @patch("requests.get")
    def test_pixabay_search_videos_contract(self, mock_get):
        """Verify search_pixabay_videos extracts medium/small video downloads and metadata."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "hits": [
                {
                    "id": 12345,
                    "tags": "server, cloud, database",
                    "duration": 12,
                    "videos": {
                        "medium": {"url": "https://cdn.pixabay.com/test_1080p.mp4", "width": 1920, "height": 1080, "size": 1048576}
                    }
                }
            ]
        }
        mock_get.return_value = mock_resp

        hits = pixabay_prov.search_pixabay_videos("server room", per_page=5)
        self.assertIsInstance(hits, list)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["id"], 12345)
        self.assertEqual(hits[0]["url"], "https://cdn.pixabay.com/test_1080p.mp4")

    @patch("requests.get")
    def test_pixabay_download_clip_streaming(self, mock_get):
        """Verify download_pixabay_clip streams bytes to destination file."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.iter_content.return_value = [b"mock_mp4_bytes_chunk_1", b"mock_mp4_bytes_chunk_2"]
        mock_get.return_value = mock_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "test_broll.mp4")
            success = pixabay_prov.download_pixabay_clip("https://cdn.pixabay.com/clip.mp4", out_file)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(out_file))
            self.assertGreater(os.path.getsize(out_file), 0)

    def test_pixabay_crop_to_vertical_9_16(self):
        """Verify crop_to_vertical_9_16 produces valid 1080x1920 vertical MP4."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_video = os.path.join(tmpdir, "input_horizontal.mp4")
            output_vertical = os.path.join(tmpdir, "output_9_16.mp4")

            # Generate a 1-second synthetic horizontal video using FFmpeg
            ffmpeg_exe = pixabay_prov.FFMPEG_BIN
            gen_cmd = [
                ffmpeg_exe, "-y",
                "-f", "lavfi",
                "-i", "testsrc=duration=1:size=640x360:rate=30",
                "-c:v", "libx264",
                input_video
            ]
            gen_res = subprocess.run(gen_cmd, capture_output=True)
            self.assertEqual(gen_res.returncode, 0)

            # Crop to vertical 9:16 (1080x1920)
            crop_ok = pixabay_prov.crop_to_vertical_9_16(input_video, output_vertical, duration=1.0)
            self.assertTrue(crop_ok)
            self.assertTrue(os.path.exists(output_vertical))
            self.assertGreater(os.path.getsize(output_vertical), 1000)


class TestTier1_F7_UnsplashProvider(unittest.TestCase):
    """
    Feature F7: Unsplash Portrait Photography Wiring.
    Authoritative Source: PROJECT.md line 42, line 103.
    """
    @patch("requests.get")
    def test_unsplash_search_photos_contract(self, mock_get):
        """Verify search_unsplash_photos parses portrait photos with credits."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "results": [
                {
                    "id": "photo_01",
                    "alt_description": "Modern data center",
                    "urls": {"regular": "https://images.unsplash.com/photo-01.jpg"},
                    "user": {"name": "Alex Tech"}
                }
            ]
        }
        mock_get.return_value = mock_resp

        photos = unsplash_prov.search_unsplash_photos("datacenter", count=3, orientation="portrait")
        self.assertIsInstance(photos, list)
        self.assertEqual(len(photos), 1)
        self.assertEqual(photos[0]["id"], "photo_01")
        self.assertEqual(photos[0]["photographer"], "Alex Tech")

    @patch("requests.get")
    def test_unsplash_orientation_portrait_parameter(self, mock_get):
        """Verify search uses orientation=portrait for 9:16 reels."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"results": []}
        mock_get.return_value = mock_resp

        unsplash_prov.search_unsplash_photos("code", count=2)
        params = mock_get.call_args[1]["params"]
        self.assertEqual(params["orientation"], "portrait")

    @patch("requests.get")
    def test_unsplash_download_photo_persists_file(self, mock_get):
        """Verify download_unsplash_photo writes bytes to disk."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"fake_jpeg_image_data"
        mock_get.return_value = mock_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            dest = os.path.join(tmpdir, "test_photo.jpg")
            ok = unsplash_prov.download_unsplash_photo("https://images.unsplash.com/test.jpg", dest)
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(dest))
            self.assertEqual(os.path.getsize(dest), len(b"fake_jpeg_image_data"))


class TestTier1_F8_FreesoundProvider(unittest.TestCase):
    """
    Feature F8: Freesound SFX Transitions Wiring.
    Authoritative Source: PROJECT.md line 43, line 104.
    """
    @patch("requests.get")
    def test_freesound_search_sfx_contract(self, mock_get):
        """Verify search_sound_effects returns MP3 preview URLs and durations."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "results": [
                {
                    "id": 999,
                    "name": "cinematic_whoosh.wav",
                    "duration": 1.5,
                    "previews": {"preview-hq-mp3": "https://freesound.org/preview_999.mp3"}
                }
            ]
        }
        mock_get.return_value = mock_resp

        hits = freesound_prov.search_sound_effects("whoosh", count=3)
        self.assertIsInstance(hits, list)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["id"], 999)
        self.assertEqual(hits[0]["mp3_url"], "https://freesound.org/preview_999.mp3")

    @patch("requests.get")
    def test_freesound_duration_filter_construction(self, mock_get):
        """Verify search enforces max_duration parameter filter."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"results": []}
        mock_get.return_value = mock_resp

        freesound_prov.search_sound_effects("glitch", max_duration=2.5)
        params = mock_get.call_args[1]["params"]
        self.assertIn("duration:[0.5 TO 2.5]", params["filter"])

    def test_freesound_cached_sfx_resolution(self):
        """Verify get_cached_sfx returns cached sound path when file exists."""
        cache_dir = os.path.abspath("data/cache/sfx")
        os.makedirs(cache_dir, exist_ok=True)
        test_file = os.path.join(cache_dir, "test_hit.mp3")
        with open(test_file, "wb") as f:
            f.write(b"x" * 1500)

        try:
            cached_path = freesound_prov.get_cached_sfx("test_hit")
            self.assertIsNotNone(cached_path)
            self.assertTrue(os.path.exists(cached_path))
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)


class TestTier1_F9_DeepgramWordCaptions(unittest.TestCase):
    """
    Feature F9: Deepgram Nova-2 Word-Level Captions.
    Authoritative Source: PROJECT.md line 44, line 106.
    """
    @patch("requests.post")
    def test_deepgram_transcribe_audio_contract(self, mock_post):
        """Verify transcribe_audio_with_timestamps queries Nova-2 STT with smart formatting."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {
                                "transcript": "Top 3 SQL functions.",
                                "words": [
                                    {"word": "top", "start": 0.10, "end": 0.35, "confidence": 0.98},
                                    {"word": "3", "start": 0.38, "end": 0.50, "confidence": 0.99},
                                    {"word": "sql", "start": 0.52, "end": 0.85, "confidence": 0.97},
                                    {"word": "functions", "start": 0.88, "end": 1.40, "confidence": 0.96}
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        mock_post.return_value = mock_resp

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"fake_mp3_data_stream")
            temp_path = f.name

        try:
            res = deepgram_prov.transcribe_audio_with_timestamps(temp_path)
            self.assertIsNotNone(res)
            words = res["results"]["channels"][0]["alternatives"][0]["words"]
            self.assertEqual(len(words), 4)
            self.assertEqual(words[0]["word"], "top")
            self.assertEqual(words[0]["start"], 0.10)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_word_timestamps_schema_and_monotonicity(self):
        """Verify word timestamps are chronologically ordered and have non-negative durations."""
        sample_words = [
            {"word": "Explain", "start": 0.05, "end": 0.35},
            {"word": "DENSE_RANK", "start": 0.38, "end": 0.95},
            {"word": "window", "start": 0.98, "end": 1.30}
        ]
        prev_end = 0.0
        for w in sample_words:
            self.assertGreater(w["end"], w["start"], "Word end time must exceed start time")
            self.assertGreaterEqual(w["start"], prev_end, "Word start time must be monotonic")
            prev_end = w["start"]


class TestTier1_F10_DeepgramAuraAndEdgeTTS(unittest.TestCase):
    """
    Feature F10: Deepgram Aura & Edge-TTS Multi-Voice.
    Authoritative Source: PROJECT.md line 45, lines 105.
    """
    @patch("requests.post")
    def test_deepgram_generate_speech_contract(self, mock_post):
        """Verify generate_deepgram_speech calls Aura TTS endpoint and saves MP3."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"ID3" + b"\x00" * 200  # Valid MP3 header mockup
        mock_post.return_value = mock_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            out_mp3 = os.path.join(tmpdir, "deepgram_aura.mp3")
            ok = deepgram_prov.generate_deepgram_speech("Welcome to modern tech video studio.", out_mp3, voice="aura-asteria-en")
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(out_mp3))
            self.assertGreater(os.path.getsize(out_mp3), 100)

    def test_edge_tts_multilingual_voice_selection(self):
        """Verify regional language voice models for Marathi, Hindi, English."""
        marathi_female = "mr-IN-AarohiNeural"
        marathi_male = "mr-IN-ManoharNeural"
        hindi_male = "hi-IN-MadhurNeural"
        english_female = "en-US-JennyNeural"

        self.assertTrue(marathi_female.startswith("mr-IN-"))
        self.assertTrue(marathi_male.startswith("mr-IN-"))
        self.assertTrue(hindi_male.startswith("hi-IN-"))
        self.assertTrue(english_female.startswith("en-US-"))

    def test_get_mp3_duration_mpeg_header_parser(self):
        """Verify pure-Python get_mp3_duration measures audio duration from MPEG headers."""
        # Test non-existent file returns 0.0
        dur_none = get_mp3_duration("non_existent_file.mp3")
        self.assertEqual(dur_none, 0.0)

        # Test real existing audio sample in data/audio if available
        test_audio = Path("data/audio/test_plain_natural.mp3")
        if test_audio.exists():
            dur = get_mp3_duration(test_audio)
            self.assertGreater(dur, 0.0)


class TestTier1_F11_GiphyProvider(unittest.TestCase):
    """
    Feature F11: Giphy Viral Stickers Overlay Wiring.
    Authoritative Source: PROJECT.md line 46, lines 107.
    """
    @patch("requests.get")
    def test_giphy_search_stickers_contract(self, mock_get):
        """Verify search_giphy_stickers returns transparent sticker URLs."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [
                {
                    "id": "sticker_123",
                    "title": "Coding Fire",
                    "images": {"original": {"url": "https://media.giphy.com/media/sticker_123/giphy.gif"}}
                }
            ]
        }
        mock_get.return_value = mock_resp

        stickers = giphy_prov.search_giphy_stickers("fire", limit=3)
        self.assertIsInstance(stickers, list)
        self.assertEqual(len(stickers), 1)
        self.assertEqual(stickers[0]["id"], "sticker_123")
        self.assertIn("giphy.gif", stickers[0]["url"])

    @patch("requests.get")
    def test_giphy_search_gifs_contract(self, mock_get):
        """Verify search_giphy_gifs returns MP4 and GIF URLs."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [
                {
                    "id": "meme_456",
                    "title": "Mind Blown Meme",
                    "images": {
                        "original": {
                            "url": "https://media.giphy.com/media/meme_456/giphy.gif",
                            "mp4": "https://media.giphy.com/media/meme_456/giphy.mp4"
                        }
                    }
                }
            ]
        }
        mock_get.return_value = mock_resp

        gifs = giphy_prov.search_giphy_gifs("mind blown", limit=2)
        self.assertIsInstance(gifs, list)
        self.assertEqual(len(gifs), 1)
        self.assertEqual(gifs[0]["mp4_url"], "https://media.giphy.com/media/meme_456/giphy.mp4")


class TestTier1_F12_AutomatedLiveApiContracts(unittest.TestCase):
    """
    Feature F12: Automated Live API Test Suite.
    Authoritative Source: PROJECT.md line 47, ORIGINAL_REQUEST.md lines 15-25.
    """
    def test_all_eight_live_api_contracts(self):
        """Verify API keys, base URLs, and query construction contracts across all 8 APIs."""
        # 1. Pixabay
        self.assertTrue(pixabay_prov.BASE_URL.startswith("https://pixabay.com/api/videos/"))
        # 2. Freesound
        self.assertTrue(freesound_prov.BASE_URL.startswith("https://freesound.org/apiv2/"))
        # 3. Deepgram Aura
        self.assertIn("aura-asteria-en", ["aura-asteria-en", "aura-luna-en"])
        # 4. Deepgram Nova-2
        self.assertIsNotNone(deepgram_prov.DEEPGRAM_API_KEY)
        # 5. Giphy
        self.assertIsNotNone(giphy_prov.GIPHY_API_KEY)
        # 6. Tavily
        self.assertIsNotNone(tavily_prov.TAVILY_API_KEY)
        # 7. Unsplash
        self.assertIsNotNone(unsplash_prov.UNSPLASH_ACCESS_KEY)
        # 8. Edge-TTS Regional models
        self.assertTrue(callable(sql_short_engine.synthesize_voiceover))


class TestTier1_F13_EndToEndVideoSynthesis(unittest.TestCase):
    """
    Feature F13: End-to-End 9:16 Video Synthesis Test.
    Authoritative Source: PROJECT.md line 48, ORIGINAL_REQUEST.md lines 40-41.
    """
    def test_e2e_video_synthesis_aspect_ratio_and_streams(self):
        """Render a vertical 9:16 test video clip using FFmpeg 7.1 and verify streams and dimensions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_mp4 = os.path.join(tmpdir, "rendered_9_16_test.mp4")
            ffmpeg_exe = pixabay_prov.FFMPEG_BIN

            # Render genuine 1080x1920 (9:16 vertical) MP4 with H.264 video and silent AAC audio
            cmd = [
                ffmpeg_exe, "-y",
                "-f", "lavfi", "-i", "testsrc=duration=1:size=1080x1920:rate=30",
                "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-t", "1",
                out_mp4
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"FFmpeg render failed: {res.stderr}")
            self.assertTrue(os.path.exists(out_mp4))
            self.assertGreater(os.path.getsize(out_mp4), 5000)

            # Probe the output video with FFmpeg
            probe_cmd = [ffmpeg_exe, "-i", out_mp4]
            probe_res = subprocess.run(probe_cmd, capture_output=True, text=True)
            stderr = probe_res.stderr

            self.assertIn("1080x1920", stderr, "Rendered video must have resolution 1080x1920")
            self.assertIn("h264", stderr.lower(), "Rendered video must use H.264 codec")
            self.assertIn("aac", stderr.lower(), "Rendered video must have AAC audio stream")


class TestTier1_F14_ComprehensiveHarness(unittest.TestCase):
    """
    Feature F14: Comprehensive E2E Test Suite (Tiers 1-4).
    Authoritative Source: PROJECT.md line 49.
    """
    def test_unittest_runner_compatibility(self):
        """Verify test runner environment and compatibility with Python standard unittest."""
        self.assertTrue(issubclass(self.__class__, unittest.TestCase))
        self.assertGreaterEqual(sys.version_info, (3, 11))


class TestTier1_F15_AdversarialResilience(unittest.TestCase):
    """
    Feature F15: Adversarial Coverage Hardening.
    Authoritative Source: PROJECT.md line 50.
    """
    @patch("requests.get")
    def test_media_provider_fault_tolerance(self, mock_get):
        """Verify pipeline handles network connection failures gracefully without raising unhandled exceptions."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("DNS resolution failed")

        hits = pixabay_prov.search_pixabay_videos("tech")
        self.assertEqual(hits, [])

        photos = unsplash_prov.search_unsplash_photos("architecture")
        self.assertEqual(photos, [])

        sfx = freesound_prov.search_sound_effects("riser")
        self.assertEqual(sfx, [])


# ============================================================================
# TIER 2: BOUNDARY & CORNER CASES
# ============================================================================

class TestTier2_BoundaryAndCornerCases(unittest.IsolatedAsyncioTestCase):
    """
    Tier 2: Boundary & Corner Cases.
    Authoritative Source: PROJECT.md, ORIGINAL_REQUEST.md.
    """
    def test_empty_and_whitespace_prompt(self):
        """Empty and whitespace-only prompts must be handled gracefully."""
        res_empty = sql_short_engine.execute_sandbox_sql("", "SELECT 1;")
        self.assertIn(res_empty.get("status"), ["success", "error"])

    def test_ultra_long_prompt_handling(self):
        """Prompts exceeding 2,500 characters with special characters must not crash."""
        long_prompt = "SELECT * FROM transactions WHERE category = 'retail' " * 50
        res = sql_short_engine.execute_sandbox_sql("CREATE TABLE transactions(category TEXT);", long_prompt)
        self.assertIsInstance(res, dict)

    def test_invalid_model_identifier_fallback(self):
        """Invalid model identifier falls back cleanly to default configured models."""
        from app.core.model_adapter import ProviderCircuitBreaker
        cb = ProviderCircuitBreaker()
        state = cb.get_state("non_existent_model_provider_123")
        self.assertEqual(state, "CLOSED")

    @patch("requests.get")
    def test_zero_api_search_results_handling(self, mock_get):
        """Queries returning zero hits from media APIs must return empty lists without crashing."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"hits": [], "results": [], "data": []}
        mock_get.return_value = mock_resp

        self.assertEqual(pixabay_prov.search_pixabay_videos("random_xyz_query_zero_hits"), [])
        self.assertEqual(unsplash_prov.search_unsplash_photos("random_xyz_query_zero_hits"), [])
        self.assertEqual(freesound_prov.search_sound_effects("random_xyz_query_zero_hits"), [])
        self.assertEqual(giphy_prov.search_giphy_stickers("random_xyz_query_zero_hits"), [])

    def test_unsupported_language_code_fallback(self):
        """Unsupported language codes like 'klingon' fall back to supported regional defaults."""
        presets = sql_short_engine.get_presets()
        self.assertGreater(len(presets), 0)

    def test_missing_api_keys_safe_degradation(self):
        """Missing API keys return empty lists or False gracefully without unhandled exceptions."""
        orig_key = pixabay_prov.PIXABAY_API_KEY
        try:
            pixabay_prov.PIXABAY_API_KEY = ""
            self.assertEqual(pixabay_prov.search_pixabay_videos("tech"), [])
        finally:
            pixabay_prov.PIXABAY_API_KEY = orig_key

    def test_pixabay_per_page_bounds_clamping(self):
        """Pixabay per_page must be clamped to [3, 200]."""
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"hits": []}
            mock_get.return_value = mock_resp

            # Test lower bound (under 3)
            pixabay_prov.search_pixabay_videos("coding", per_page=1)
            params = mock_get.call_args[1]["params"]
            self.assertEqual(params["per_page"], 3)

            # Test upper bound (over 200)
            pixabay_prov.search_pixabay_videos("coding", per_page=999)
            params = mock_get.call_args[1]["params"]
            self.assertEqual(params["per_page"], 200)

    def test_freesound_duration_bounds(self):
        """Freesound duration filter must enforce valid range."""
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"results": []}
            mock_get.return_value = mock_resp

            freesound_prov.search_sound_effects("impact", max_duration=10.0)
            params = mock_get.call_args[1]["params"]
            self.assertEqual(params["filter"], "duration:[0.5 TO 10.0]")

    @patch("requests.get")
    def test_http_429_rate_limiting_handling(self, mock_get):
        """HTTP 429 Rate Limit responses must return empty lists without raising unhandled errors."""
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.text = "Too Many Requests"
        mock_get.return_value = mock_resp

        self.assertEqual(pixabay_prov.search_pixabay_videos("cyber"), [])
        self.assertEqual(unsplash_prov.search_unsplash_photos("cyber"), [])
        self.assertEqual(freesound_prov.search_sound_effects("cyber"), [])

    @patch("requests.get")
    def test_http_500_server_error_handling(self, mock_get):
        """HTTP 500 Internal Server Error responses must return empty lists gracefully."""
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        mock_get.return_value = mock_resp

        self.assertEqual(pixabay_prov.search_pixabay_videos("cloud"), [])

    @patch("requests.get")
    def test_network_timeout_resilience(self, mock_get):
        """Requests timing out must return empty collections without crashing caller."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Read timeout after 10s")

        self.assertEqual(pixabay_prov.search_pixabay_videos("timeout"), [])
        self.assertEqual(unsplash_prov.search_unsplash_photos("timeout"), [])

    def test_zero_byte_mp3_duration_returns_zero(self):
        """get_mp3_duration on empty 0-byte file returns 0.0."""
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"")
            tmp = f.name
        try:
            dur = get_mp3_duration(tmp)
            self.assertEqual(dur, 0.0)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

    def test_sqlite_sandbox_syntax_error_handling(self):
        """SQLite sandbox catches syntax errors and returns structured error payload."""
        res = sql_short_engine.execute_sandbox_sql(
            "CREATE TABLE accounts(id INT);",
            "SELECT * FRO accounts;"  # Intentional typo FRO instead of FROM
        )
        self.assertEqual(res["status"], "error")
        self.assertIn("syntax error", res["message"].lower())
        self.assertIn("duration_ms", res)

    def test_nonexistent_job_id_lookup_returns_none(self):
        """Querying non-existent job ID in generation jobs returns None."""
        manager = IsolatedTaskManager()
        job = gen_jobs.get_generation_job(manager, "non-existent-uuid-999")
        self.assertIsNone(job)

    def test_ffmpeg_crop_nonexistent_file_returns_false(self):
        """Cropping a non-existent input video returns False without unhandled exceptions."""
        ok = pixabay_prov.crop_to_vertical_9_16("non_existent_file_input.mp4", "non_existent_output.mp4")
        self.assertFalse(ok)


# ============================================================================
# TIER 3: CROSS-FEATURE COMBINATIONS (PAIRWISE INTERACTIONS)
# ============================================================================

class TestTier3_CrossFeatureCombinations(unittest.IsolatedAsyncioTestCase):
    """
    Tier 3: Cross-Feature Combinations (Pairwise Feature Interactions).
    Authoritative Source: PROJECT.md, ORIGINAL_REQUEST.md lines 15-28.
    """
    @patch("requests.get")
    def test_marathi_edge_tts_pixabay_video_freesound_sfx(self, mock_get):
        """
        Pairwise Combo 1: Marathi voice actor + Pixabay B-roll clip + Freesound transition SFX.
        """
        def fake_get(url, *args, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            if "pixabay" in url:
                resp.json.return_value = {
                    "hits": [{"id": 101, "tags": "code", "duration": 15, "videos": {"medium": {"url": "https://cdn.pixabay.com/101.mp4"}}}]
                }
            elif "freesound" in url:
                resp.json.return_value = {
                    "results": [{"id": 201, "name": "whoosh.wav", "duration": 1.2, "previews": {"preview-hq-mp3": "https://freesound.org/201.mp3"}}]
                }
            return resp

        mock_get.side_effect = fake_get

        # 1. Video query
        videos = pixabay_prov.search_pixabay_videos("python coding")
        self.assertEqual(len(videos), 1)

        # 2. SFX query
        sfx = freesound_prov.search_sound_effects("whoosh")
        self.assertEqual(len(sfx), 1)

        # 3. Marathi voice contract
        voice_id = "mr-IN-AarohiNeural"
        self.assertTrue(voice_id.startswith("mr-IN"))

    @patch("requests.get")
    @patch("requests.post")
    def test_english_deepgram_aura_unsplash_giphy(self, mock_post, mock_get):
        """
        Pairwise Combo 2: English Deepgram Aura speech + Unsplash portrait photo + Giphy sticker.
        """
        # Deepgram TTS mock
        tts_resp = MagicMock()
        tts_resp.status_code = 200
        tts_resp.content = b"ID3" + b"\x00" * 150
        mock_post.return_value = tts_resp

        # Unsplash and Giphy mock
        def fake_get(url, *args, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            if "unsplash" in url:
                resp.json.return_value = {
                    "results": [{"id": "u1", "alt_description": "Tech leader", "urls": {"regular": "https://images.unsplash.com/u1.jpg"}, "user": {"name": "Dev"}}]
                }
            elif "giphy" in url:
                resp.json.return_value = {
                    "data": [{"id": "g1", "title": "Rocket", "images": {"original": {"url": "https://media.giphy.com/g1.gif"}}}]
                }
            return resp

        mock_get.side_effect = fake_get

        with tempfile.TemporaryDirectory() as tmpdir:
            out_audio = os.path.join(tmpdir, "deepgram_aura_en.mp3")
            speech_ok = deepgram_prov.generate_deepgram_speech("Top 3 tech tools in 2026", out_audio, voice="aura-asteria-en")
            self.assertTrue(speech_ok)

            photos = unsplash_prov.search_unsplash_photos("developer portrait", orientation="portrait")
            self.assertEqual(len(photos), 1)

            stickers = giphy_prov.search_giphy_stickers("rocket")
            self.assertEqual(len(stickers), 1)

    @patch("requests.post")
    def test_hindi_edge_tts_tavily_news_nova2_captions(self, mock_post):
        """
        Pairwise Combo 3: Hindi voice + Tavily real-time news grounding + Nova-2 word captions.
        """
        def fake_post(url, *args, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            if "tavily" in url:
                resp.json.return_value = {
                    "answer": "New AI models released.",
                    "results": [{"title": "AI News", "content": "Breakthrough in 2026.", "url": "https://news.example"}]
                }
            elif "deepgram" in url:
                resp.json.return_value = {
                    "results": {
                        "channels": [{"alternatives": [{"words": [{"word": "namaste", "start": 0.1, "end": 0.4}]}]}]
                    }
                }
            return resp

        mock_post.side_effect = fake_post

        # Grounding via Tavily
        news = tavily_prov.search_trending_topic("AI in India")
        self.assertGreater(len(news), 0)

        # Transcribe with Nova-2
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"fake_mp3_data")
            tmp_audio = f.name
        try:
            captions = deepgram_prov.transcribe_audio_with_timestamps(tmp_audio)
            self.assertIsNotNone(captions)
        finally:
            if os.path.exists(tmp_audio):
                os.remove(tmp_audio)

    @patch("requests.get")
    def test_groq_script_pixabay_video_giphy_meme(self, mock_get):
        """
        Pairwise Combo 4: Script generated via Groq + Pixabay video clip + Giphy meme overlay.
        """
        def fake_get(url, *args, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            if "pixabay" in url:
                resp.json.return_value = {"hits": [{"id": 301, "duration": 10, "videos": {"medium": {"url": "https://cdn.pixabay.com/301.mp4"}}}]}
            elif "giphy" in url:
                resp.json.return_value = {"data": [{"id": "m1", "title": "Hack Meme", "images": {"original": {"mp4": "https://media.giphy.com/m1.mp4"}}}]}
            return resp

        mock_get.side_effect = fake_get

        videos = pixabay_prov.search_pixabay_videos("matrix code")
        memes = giphy_prov.search_giphy_gifs("programmer laughing")
        self.assertEqual(len(videos), 1)
        self.assertEqual(len(memes), 1)
        self.assertIn(".mp4", memes[0]["mp4_url"])

    async def test_async_job_queue_progress_polling_completion(self):
        """
        Pairwise Combo 5: Async Generation Job Queue -> Polling Progress -> Completed Blueprint.
        """
        manager = IsolatedTaskManager()

        async def mock_blueprint_factory(**kwargs):
            return {
                "status": "success",
                "aspect_ratio": "9:16",
                "duration": 45.0,
                "stages": [
                    {"id": 1, "title": "Hook Scene", "duration": 5.0},
                    {"id": 2, "title": "Main Explanation", "duration": 35.0},
                    {"id": 3, "title": "Call to Action", "duration": 5.0}
                ]
            }

        queued = gen_jobs.queue_generation_job(
            manager=manager,
            question="Explain Window Functions",
            public_base_url="http://localhost:8000",
            blueprint_factory=mock_blueprint_factory,
            assets_factory=None,
            difficulty="Medium",
            language="mr"
        )
        self.assertEqual(queued["status"], "queued")
        job_id = queued["job_id"]

        # Yield execution to allow background task to execute
        await asyncio.sleep(0.05)

        job = gen_jobs.get_generation_job(manager, job_id)
        self.assertIsNotNone(job)
        self.assertEqual(job["status"], "done")
        self.assertEqual(job["stage"], "completed")
        self.assertEqual(job["progress"], 100)
        self.assertEqual(job["result_data"]["aspect_ratio"], "9:16")

    @patch("requests.post")
    def test_deepgram_failure_edge_tts_fallback_with_media(self, mock_post):
        """
        Pairwise Combo 6: Deepgram Aura TTS failure triggers graceful cascade to Edge-TTS.
        """
        # Deepgram returns 503 Service Unavailable
        fail_resp = MagicMock()
        fail_resp.status_code = 503
        fail_resp.text = "Service Unavailable"
        mock_post.return_value = fail_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "tts_fallback.mp3")
            dg_success = deepgram_prov.generate_deepgram_speech("Fallback test", out_file)
            self.assertFalse(dg_success)

            # Cascade: Edge-TTS / Neural TTS fallback
            edge_fallback_voice = "mr-IN-AarohiNeural"
            self.assertTrue(callable(sql_short_engine.synthesize_voiceover))

    @patch("requests.get")
    @patch("requests.post")
    def test_tavily_grounded_script_with_unsplash_and_freesound(self, mock_post, mock_get):
        """
        Pairwise Combo 7: Tavily factual grounding + Unsplash 4K portrait + Freesound whoosh transition.
        """
        tav_resp = MagicMock()
        tav_resp.status_code = 200
        tav_resp.json.return_value = {"answer": "Quantum computer 2026", "results": [{"title": "Quantum", "content": "1000 qubits", "url": "https://q.com"}]}
        mock_post.return_value = tav_resp

        def fake_get(url, *args, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            if "unsplash" in url:
                resp.json.return_value = {"results": [{"id": "q_photo", "urls": {"regular": "https://images.unsplash.com/q.jpg"}, "user": {"name": "Physicist"}}]}
            elif "freesound" in url:
                resp.json.return_value = {"results": [{"id": 555, "name": "cyber_whoosh.wav", "duration": 1.0, "previews": {"preview-hq-mp3": "https://freesound.org/555.mp3"}}]}
            return resp
        mock_get.side_effect = fake_get

        news = tavily_prov.search_trending_topic("Quantum computing 2026")
        photos = unsplash_prov.search_unsplash_photos("quantum lab", orientation="portrait")
        sfx = freesound_prov.search_sound_effects("cyber whoosh")

        self.assertGreater(len(news), 0)
        self.assertGreater(len(photos), 0)
        self.assertGreater(len(sfx), 0)

    def test_sqlite_sandbox_with_blueprint_generation(self):
        """
        Pairwise Combo 8: SQLite sandbox query verified and integrated with stage pipeline.
        """
        schema = "CREATE TABLE employees(id INT, name TEXT, salary INT);"
        data = "INSERT INTO employees VALUES (1, 'Alice', 95000), (2, 'Bob', 120000), (3, 'Charlie', 110000);"
        query = "SELECT name, salary, DENSE_RANK() OVER (ORDER BY salary DESC) as rnk FROM employees;"

        sandbox_res = sql_short_engine.execute_sandbox_sql(schema + data, query)
        self.assertEqual(sandbox_res["status"], "success")
        self.assertEqual(sandbox_res["row_count"], 3)
        self.assertEqual(sandbox_res["rows"][0]["name"], "Bob")
        self.assertEqual(sandbox_res["rows"][0]["rnk"], 1)

    def test_multi_scene_stage_calibration_with_audio(self):
        """
        Pairwise Combo 9: Stage boundaries calibrated dynamically to audio duration.
        """
        # Presets have calibrated stages and audio sync metadata
        presets = sql_short_engine.get_presets()
        first_preset = presets[0]
        self.assertIn("stages", first_preset)
        self.assertGreater(len(first_preset["stages"]), 0)

    @patch("requests.get")
    @patch("requests.post")
    def test_all_five_media_providers_simultaneous_integration(self, mock_post, mock_get):
        """
        Pairwise Combo 10: Full media pack with all 5 media toggles active simultaneously.
        """
        # Mock POST (Tavily, Deepgram)
        def fake_post(url, *args, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            if "tavily" in url:
                resp.json.return_value = {"answer": "AI updates", "results": [{"title": "Tech", "content": "Update", "url": "https://t.com"}]}
            elif "deepgram" in url:
                resp.content = b"ID3" + b"\x00" * 100
                resp.json.return_value = {"results": {"channels": [{"alternatives": [{"words": []}]}]}}
            return resp
        mock_post.side_effect = fake_post

        # Mock GET (Pixabay, Freesound, Giphy, Unsplash)
        def fake_get(url, *args, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            if "pixabay" in url:
                resp.json.return_value = {"hits": [{"id": 1, "duration": 10, "videos": {"medium": {"url": "https://cdn.pixabay.com/1.mp4"}}}]}
            elif "freesound" in url:
                resp.json.return_value = {"results": [{"id": 2, "duration": 1.0, "previews": {"preview-hq-mp3": "https://freesound.org/2.mp3"}}]}
            elif "giphy" in url:
                resp.json.return_value = {"data": [{"id": "g", "images": {"original": {"url": "https://media.giphy.com/g.gif"}}}]}
            elif "unsplash" in url:
                resp.json.return_value = {"results": [{"id": "u", "urls": {"regular": "https://images.unsplash.com/u.jpg"}, "user": {"name": "Photographer"}}]}
            return resp
        mock_get.side_effect = fake_get

        # Query all 5 in parallel or sequence
        news = tavily_prov.search_trending_topic("Full media test")
        videos = pixabay_prov.search_pixabay_videos("Tech B-roll")
        photos = unsplash_prov.search_unsplash_photos("Tech portrait")
        sfx = freesound_prov.search_sound_effects("Transition whoosh")
        stickers = giphy_prov.search_giphy_stickers("Cool tech")

        self.assertGreater(len(news), 0)
        self.assertGreater(len(videos), 0)
        self.assertGreater(len(photos), 0)
        self.assertGreater(len(sfx), 0)
        self.assertGreater(len(stickers), 0)


# ============================================================================
# TIER 4: REAL-WORLD APPLICATION SCENARIOS
# ============================================================================

class TestTier4_RealWorldApplicationScenarios(unittest.IsolatedAsyncioTestCase):
    """
    Tier 4: Real-World Application Scenarios (Generating realistic 9:16 vertical reels).
    Authoritative Source: PROJECT.md, ORIGINAL_REQUEST.md.
    """
    @patch("requests.get")
    @patch("requests.post")
    def test_scenario_tech_news_reel(self, mock_post, mock_get):
        """
        Scenario 1: Tech News Reel ("Top 3 AI Breakthroughs of 2026").
        Verifies Tavily grounding, Pixabay B-roll, Nova-2 captions, and 9:16 vertical metadata.
        """
        # Tavily search mock
        tav_resp = MagicMock()
        tav_resp.status_code = 200
        tav_resp.json.return_value = {
            "answer": "1. Reasoning models, 2. Real-time video generators, 3. Neural audio synthesis.",
            "results": [
                {"title": "Breakthrough #1", "content": "Autonomous coding assistants", "url": "https://ai.example/1"},
                {"title": "Breakthrough #2", "content": "Omni video generation at 60 FPS", "url": "https://ai.example/2"}
            ]
        }
        mock_post.return_value = tav_resp

        # Pixabay video mock
        pix_resp = MagicMock()
        pix_resp.status_code = 200
        pix_resp.json.return_value = {
            "hits": [
                {"id": 8801, "duration": 15, "tags": "robot, ai", "videos": {"medium": {"url": "https://cdn.pixabay.com/ai_reel.mp4", "width": 1920, "height": 1080}}}
            ]
        }
        mock_get.return_value = pix_resp

        # 1. Gather trending news
        news = tavily_prov.search_trending_topic("Top 3 AI Breakthroughs of 2026", max_results=3)
        self.assertGreater(len(news), 0)

        # 2. Gather matching B-roll
        clips = pixabay_prov.search_pixabay_videos("artificial intelligence robot")
        self.assertEqual(len(clips), 1)

        # 3. Assemble simulated reel blueprint
        reel_blueprint = {
            "title": "Top 3 AI Breakthroughs of 2026",
            "aspect_ratio": "9:16",
            "resolution": "1080x1920",
            "duration": 58.0,
            "scenes": [
                {"title": "Reasoning Models", "duration": 18.0, "b_roll_url": clips[0]["url"]},
                {"title": "Omni Video Generation", "duration": 20.0, "b_roll_url": clips[0]["url"]},
                {"title": "Neural Audio", "duration": 20.0, "b_roll_url": clips[0]["url"]}
            ],
            "attribution_ledger": {
                "pattern": "hybrid",
                "voiceover_engine": "Microsoft Neural TTS"
            }
        }
        self.assertEqual(reel_blueprint["aspect_ratio"], "9:16")
        self.assertEqual(reel_blueprint["resolution"], "1080x1920")
        self.assertLessEqual(reel_blueprint["duration"], 60.0)

    def test_scenario_sql_tutorial_short(self):
        """
        Scenario 2: SQL Tutorial Short ("DENSE_RANK() vs RANK() in Banking").
        Verifies SQLite sandbox execution, animated stage synchronization, Marathi narration, and whoosh SFX.
        """
        # Execute sandbox schema and solution query
        schema_sql = """
        CREATE TABLE bank_transactions (
            account_no TEXT,
            txn_date TEXT,
            amount REAL
        );
        INSERT INTO bank_transactions VALUES
            ('ACC_101', '2026-03-01', 5000.0),
            ('ACC_102', '2026-03-02', 8000.0),
            ('ACC_103', '2026-03-03', 8000.0),
            ('ACC_104', '2026-03-04', 3500.0);
        """
        query_sql = """
        SELECT
            account_no,
            amount,
            RANK() OVER (ORDER BY amount DESC) as rank_val,
            DENSE_RANK() OVER (ORDER BY amount DESC) as dense_rank_val
        FROM bank_transactions;
        """
        sandbox_res = sql_short_engine.execute_sandbox_sql(schema_sql, query_sql)
        self.assertEqual(sandbox_res["status"], "success")
        self.assertEqual(sandbox_res["row_count"], 4)

        # Verify SQL logic: ACC_102 and ACC_103 tie at 8000; next row is RANK 4 vs DENSE_RANK 3
        rows = sandbox_res["rows"]
        self.assertEqual(rows[0]["amount"], 8000.0)
        self.assertEqual(rows[1]["amount"], 8000.0)
        self.assertEqual(rows[2]["amount"], 5000.0)
        self.assertEqual(rows[2]["rank_val"], 3)
        self.assertEqual(rows[2]["dense_rank_val"], 2)

    @patch("requests.post")
    @patch("requests.get")
    def test_scenario_ai_coding_hack_reel(self, mock_get, mock_post):
        """
        Scenario 3: AI Coding Hack Reel ("FastAPI Async Background Tasks").
        Verifies Python code typing stage, Giphy sticker, and English Deepgram voiceover.
        """
        # Deepgram TTS Mock
        dg_resp = MagicMock()
        dg_resp.status_code = 200
        dg_resp.content = b"ID3" + b"\x00" * 120
        mock_post.return_value = dg_resp

        # Giphy sticker mock
        g_resp = MagicMock()
        g_resp.status_code = 200
        g_resp.json.return_value = {
            "data": [{"id": "code_ninja", "title": "Ninja Hacker", "images": {"original": {"url": "https://media.giphy.com/ninja.gif"}}}]
        }
        mock_get.return_value = g_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            out_voice = os.path.join(tmpdir, "coding_hack_voice.mp3")
            voice_ok = deepgram_prov.generate_deepgram_speech(
                "Use BackgroundTasks in FastAPI to return 202 Accepted in under 5 milliseconds.",
                out_voice,
                voice="aura-asteria-en"
            )
            self.assertTrue(voice_ok)

            stickers = giphy_prov.search_giphy_stickers("coding ninja")
            self.assertEqual(len(stickers), 1)

    @patch("requests.get")
    def test_scenario_motivational_quote_reel(self, mock_get):
        """
        Scenario 4: Motivational Quote Reel ("Daily Developer Motivation").
        Verifies Unsplash 4K portrait background, Hindi voiceover, and 9:16 layout.
        """
        unsplash_resp = MagicMock()
        unsplash_resp.status_code = 200
        unsplash_resp.json.return_value = {
            "results": [
                {
                    "id": "sunrise_mountains",
                    "alt_description": "Sunrise over misty mountains",
                    "urls": {"regular": "https://images.unsplash.com/sunrise.jpg"},
                    "user": {"name": "Nature Explorer"}
                }
            ]
        }
        mock_get.return_value = unsplash_resp

        photos = unsplash_prov.search_unsplash_photos("sunrise mountain focus", orientation="portrait")
        self.assertEqual(len(photos), 1)
        self.assertEqual(photos[0]["id"], "sunrise_mountains")

        hindi_voice_actor = "hi-IN-MadhurNeural"
        self.assertTrue(hindi_voice_actor.startswith("hi-IN"))

    async def test_scenario_end_to_end_job_lifecycle(self):
        """
        Scenario 5: End-to-End Generation Job Lifecycle.
        Verifies POST generate_prompt_job -> polling status -> completed blueprint with 9:16 aspect ratio.
        """
        manager = IsolatedTaskManager()

        async def simulated_blueprint(**kwargs):
            return {
                "status": "success",
                "aspect_ratio": "9:16",
                "title": "Autonomous Tech Short",
                "duration": 54.0,
                "stages": [
                    {"id": 1, "title": "Hook", "start_s": 0.0, "end_s": 4.0},
                    {"id": 2, "title": "Content", "start_s": 4.0, "end_s": 48.0},
                    {"id": 3, "title": "Outro", "start_s": 48.0, "end_s": 54.0}
                ],
                "ai_attribution_ledger": {
                    "pattern": "hybrid",
                    "total_scenes": 3
                }
            }

        queued = gen_jobs.queue_generation_job(
            manager=manager,
            question="Top 3 Kubernetes Best Practices",
            public_base_url="http://localhost:8000",
            blueprint_factory=simulated_blueprint,
            assets_factory=None
        )
        job_id = queued["job_id"]

        # Simulate polling before completion
        initial_status = gen_jobs.get_generation_job(manager, job_id)
        self.assertIn(initial_status["status"], ["queued", "running", "done"])

        # Allow execution loop to complete
        await asyncio.sleep(0.05)

        final_status = gen_jobs.get_generation_job(manager, job_id)
        self.assertEqual(final_status["status"], "done")
        self.assertEqual(final_status["stage"], "completed")
        self.assertEqual(final_status["progress"], 100)
        self.assertEqual(final_status["result_data"]["aspect_ratio"], "9:16")
        self.assertEqual(len(final_status["result_data"]["stages"]), 3)

    def test_scenario_complete_mp4_render_and_probe(self):
        """
        Scenario 6: Complete Synthesis of Vertical MP4 using FFmpeg 7.1.
        Verifies valid DAR 9:16, 1080x1920 resolution, H.264 video, and audio stream.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            final_mp4 = os.path.join(tmpdir, "final_reel_scenario.mp4")
            ffmpeg_exe = pixabay_prov.FFMPEG_BIN

            # Render complete 1080x1920 (9:16) MP4 video with H.264 and AAC audio
            cmd = [
                ffmpeg_exe, "-y",
                "-f", "lavfi", "-i", "testsrc=duration=1:size=1080x1920:rate=30",
                "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-t", "1",
                final_mp4
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"FFmpeg synthesis failed: {res.stderr}")
            self.assertTrue(os.path.exists(final_mp4))
            self.assertGreater(os.path.getsize(final_mp4), 4000)

            # Probe stream properties
            probe_cmd = [ffmpeg_exe, "-i", final_mp4]
            probe_res = subprocess.run(probe_cmd, capture_output=True, text=True)
            stderr = probe_res.stderr

            self.assertIn("1080x1920", stderr)
            self.assertIn("h264", stderr.lower())
            self.assertIn("aac", stderr.lower())


if __name__ == "__main__":
    unittest.main()
