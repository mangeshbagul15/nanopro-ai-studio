# -*- coding: utf-8 -*-
"""
Empirical Challenger M2-2 Test Suite:
Specialized for Milestone M2:
1. Subtitle Timestamp Monotonicity (Deepgram Nova-2 STT & Heuristic Pacing Fallback)
2. Media Pipeline Resilience (Simulated 3.5s Timeouts & Network Failures)
3. JS DOM & Ledger Compatibility (DOM ID verification, dual-lookups, and null safety)

Author: Challenger M2-2
"""

import os
import sys
import asyncio
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.video_maker.sql_short_engine import SqlShortVideoEngine, sql_short_engine
from app.ui.sql_video_workspace import get_sql_video_workspace_html
from app.ui.sql_video_js import get_sql_video_js


class TestSubtitleTimestampMonotonicity(unittest.IsolatedAsyncioTestCase):
    """Stress-test word-level subtitle timestamp monotonicity under all conditions."""

    async def asyncSetUp(self):
        self.engine = SqlShortVideoEngine()
        self.mock_stages = [
            {"id": 1, "title": "Scene 1 Intro", "speech": "In relational databases, performance matters.", "start": 0.0, "end": 4.0},
            {"id": 2, "title": "Scene 2 Index", "speech": "A B-Tree index accelerates search queries.", "start": 4.0, "end": 8.0},
            {"id": 3, "title": "Scene 3 Demo", "speech": "Looking up records becomes instantaneous.", "start": 8.0, "end": 12.0}
        ]

    async def test_heuristic_fallback_monotonicity(self):
        """
        Test the heuristic linear pacing fallback when STT returns empty or None.
        Must satisfy strictly:
          - start >= 0.0
          - end > start (positive duration)
          - start >= prev_end (monotonic non-overlapping)
        """
        with patch.object(self.engine, "_parse_master_prompt_text", return_value={"id": "test_scn", "stages": self.mock_stages, "scenes": self.mock_stages}):
            with patch("app.video_maker.deepgram_provider.transcribe_audio_with_timestamps", return_value=None):
                with patch("app.core.neural_tts.neural_tts.generate_speech_async", return_value=True):
                    with patch("app.video_maker.sql_short_engine.get_mp3_duration", return_value=12.0):
                        res = await self.engine.generate_short_prompt_async(
                            topic_or_question="## SCENE 1\nExplain SQL B-Tree index",
                            language="en"
                        )

        word_timestamps = res.get("word_timestamps", [])
        self.assertTrue(len(word_timestamps) > 0, "Heuristic fallback must emit word timestamps")

        prev_end = 0.0
        for idx, item in enumerate(word_timestamps):
            start = item["start"]
            end = item["end"]
            word = item["word"]

            self.assertGreaterEqual(start, 0.0, f"Word {idx} ('{word}') has negative start: {start}")
            self.assertGreater(end, start, f"Word {idx} ('{word}') has non-positive duration: {start} -> {end}")
            self.assertGreaterEqual(
                start, prev_end,
                f"Word {idx} ('{word}') inversion: start={start} < prev_end={prev_end}"
            )
            prev_end = end

    async def test_deepgram_nova2_ideal_stt_monotonicity(self):
        """
        Test Deepgram Nova-2 STT with standard non-overlapping word timestamps.
        """
        mock_stt_response = {
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {
                                "transcript": "In relational databases performance matters",
                                "words": [
                                    {"word": "In", "start": 0.08, "end": 0.22},
                                    {"word": "relational", "start": 0.25, "end": 0.75},
                                    {"word": "databases", "start": 0.80, "end": 1.35},
                                    {"word": "performance", "start": 1.40, "end": 2.05},
                                    {"word": "matters", "start": 2.10, "end": 2.65}
                                ]
                            }
                        ]
                    }
                ]
            }
        }

        with patch.object(self.engine, "_parse_master_prompt_text", return_value={"id": "test_scn", "stages": self.mock_stages, "scenes": self.mock_stages}):
            with patch("os.path.exists", return_value=True):
                with patch("app.video_maker.deepgram_provider.transcribe_audio_with_timestamps", return_value=mock_stt_response):
                    with patch("app.core.neural_tts.neural_tts.generate_speech_async", return_value=True):
                        with patch("app.video_maker.sql_short_engine.get_mp3_duration", return_value=3.0):
                            res = await self.engine.generate_short_prompt_async(
                                topic_or_question="## SCENE 1\nIn relational databases performance matters",
                                language="en"
                            )

        word_timestamps = res.get("word_timestamps", [])
        self.assertTrue(len(word_timestamps) > 0, "STT must emit word timestamps")

        prev_end = 0.0
        for idx, item in enumerate(word_timestamps):
            start = item["start"]
            end = item["end"]
            word = item["word"]

            self.assertGreaterEqual(start, 0.0, f"Word {idx} ('{word}') negative start: {start}")
            self.assertGreater(end, start, f"Word {idx} ('{word}') non-positive duration: {start} -> {end}")
            self.assertGreaterEqual(start, prev_end, f"Word {idx} ('{word}') inversion: start={start} < prev_end={prev_end}")
            prev_end = end

    async def test_deepgram_nova2_overlapping_coarticulation_words(self):
        """
        Adversarial test: Deepgram Nova-2 often returns co-articulated overlapping word timestamps:
        e.g. Word A ends at 0.45, but Word B starts at 0.40 due to continuous speech.
        The engine post-processing must enforce: start >= prev_end, end > start.
        """
        mock_overlapping_stt = {
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {
                                "transcript": "Fast data processing pipeline",
                                "words": [
                                    {"word": "Fast", "start": 0.10, "end": 0.45},
                                    {"word": "data", "start": 0.40, "end": 0.85},     # Overlaps Fast by 0.05s
                                    {"word": "processing", "start": 0.80, "end": 1.30}, # Overlaps data by 0.05s
                                    {"word": "pipeline", "start": 1.25, "end": 1.80}   # Overlaps processing by 0.05s
                                ]
                            }
                        ]
                    }
                ]
            }
        }

        with patch.object(self.engine, "_parse_master_prompt_text", return_value={"id": "test_scn", "stages": self.mock_stages, "scenes": self.mock_stages}):
            with patch("os.path.exists", return_value=True):
                with patch("app.video_maker.deepgram_provider.transcribe_audio_with_timestamps", return_value=mock_overlapping_stt):
                    with patch("app.core.neural_tts.neural_tts.generate_speech_async", return_value=True):
                        with patch("app.video_maker.sql_short_engine.get_mp3_duration", return_value=2.0):
                            res = await self.engine.generate_short_prompt_async(
                                topic_or_question="## SCENE 1\nFast data processing pipeline",
                                language="en"
                            )

        word_timestamps = res.get("word_timestamps", [])
        self.assertTrue(len(word_timestamps) > 0)

        inversions = []
        prev_end = 0.0
        for idx, item in enumerate(word_timestamps):
            start = item["start"]
            end = item["end"]
            word = item["word"]

            if start < prev_end:
                inversions.append((idx, word, start, prev_end))
            prev_end = end

        # If inversions exist, this test detects the bug in line 1967/1974 where last_start is used instead of prev_end
        self.assertEqual(
            len(inversions), 0,
            f"Found {len(inversions)} timestamp overlaps/inversions in STT post-processing: {inversions}"
        )


class TestMediaPipelineResilience(unittest.IsolatedAsyncioTestCase):
    """Stress-test external media APIs under timeouts (3.5s limit) and network crashes."""

    async def asyncSetUp(self):
        self.engine = SqlShortVideoEngine()
        self.mock_stages = [
            {"id": 1, "title": "Scene 1", "speech": "Step one overview.", "start": 0.0, "end": 4.0},
            {"id": 2, "title": "Scene 2", "speech": "Step two details.", "start": 4.0, "end": 8.0}
        ]

    async def test_media_pipeline_all_timeouts_no_crash(self):
        """
        Simulate all external media APIs hanging beyond the 3.5s timeout.
        Verify:
          - No unhandled exceptions or pipeline crash
          - Result status is 'success'
          - res['scene_assets'] is populated as a list
        """
        def sync_hang(*args, **kwargs):
            import time
            time.sleep(10.0)
            return []

        with patch.object(self.engine, "_parse_master_prompt_text", return_value={"id": "test_scn", "stages": self.mock_stages, "scenes": self.mock_stages}):
            with patch("app.core.neural_tts.neural_tts.generate_speech_async", return_value=True):
                with patch("app.video_maker.sql_short_engine.get_mp3_duration", return_value=8.0):
                    with patch("app.video_maker.pixabay_video_provider.search_pixabay_videos", side_effect=sync_hang):
                        with patch("app.video_maker.unsplash_provider.search_unsplash_photos", side_effect=sync_hang):
                            with patch("app.video_maker.freesound_provider.search_sound_effects", side_effect=sync_hang):
                                with patch("app.video_maker.giphy_provider.search_giphy_stickers", side_effect=sync_hang):
                                    with patch("app.video_maker.tavily_news_search.search_trending_topic", side_effect=sync_hang):
                                        res = await self.engine.generate_short_prompt_async(
                                            topic_or_question="## SCENE 1\nTop 3 Database Sharding Strategies",
                                            language="en"
                                        )

        self.assertEqual(res.get("status"), "success")
        self.assertIn("scene_assets", res)
        self.assertTrue(len(res["scene_assets"]) > 0)

    async def test_media_pipeline_network_exceptions_no_crash(self):
        """
        Simulate network exceptions (ConnectionResetError, HTTPError 500, socket errors).
        Verify pipeline catches errors and never crashes.
        """
        def blow_up(*args, **kwargs):
            raise ConnectionResetError("Connection abruptly terminated by peer (104)")

        with patch.object(self.engine, "_parse_master_prompt_text", return_value={"id": "test_scn", "stages": self.mock_stages, "scenes": self.mock_stages}):
            with patch("app.core.neural_tts.neural_tts.generate_speech_async", return_value=True):
                with patch("app.video_maker.sql_short_engine.get_mp3_duration", return_value=8.0):
                    with patch("app.video_maker.pixabay_video_provider.search_pixabay_videos", side_effect=blow_up):
                        with patch("app.video_maker.unsplash_provider.search_unsplash_photos", side_effect=blow_up):
                            with patch("app.video_maker.freesound_provider.search_sound_effects", side_effect=blow_up):
                                with patch("app.video_maker.giphy_provider.search_giphy_stickers", side_effect=blow_up):
                                    with patch("app.video_maker.tavily_news_search.search_trending_topic", side_effect=blow_up):
                                        res = await self.engine.generate_short_prompt_async(
                                            topic_or_question="## SCENE 1\nPostgreSQL vs MySQL Connection Pooling",
                                            language="en"
                                        )

        self.assertEqual(res.get("status"), "success")
        self.assertIn("scene_assets", res)
        self.assertIn("attribution_ledger", res)

    async def test_media_pipeline_successful_assets_population(self):
        """
        Verify that when media providers return successful results,
        res['scene_assets'] is properly populated with non-blank asset URLs.
        """
        mock_pixabay = [{"id": 101, "url": "https://cdn.pixabay.com/video/broll_101.mp4", "width": 1080, "height": 1920, "duration": 15}]
        mock_unsplash = [{"id": "u1", "url": "https://images.unsplash.com/photo-101.jpg", "photographer": "Alex", "description": "Tech"}]
        mock_freesound = [{"id": 201, "name": "whoosh.mp3", "mp3_url": "https://freesound.org/whoosh.mp3", "duration": 1.2}]
        mock_giphy = [{"id": "g1", "title": "Rocket", "url": "https://media.giphy.com/media/rocket.gif"}]

        with patch.object(self.engine, "_parse_master_prompt_text", return_value={"id": "test_scn", "stages": self.mock_stages, "scenes": self.mock_stages}):
            with patch("app.core.neural_tts.neural_tts.generate_speech_async", return_value=True):
                with patch("app.video_maker.sql_short_engine.get_mp3_duration", return_value=8.0):
                    with patch("app.video_maker.pixabay_video_provider.search_pixabay_videos", return_value=mock_pixabay):
                        with patch("app.video_maker.unsplash_provider.search_unsplash_photos", return_value=mock_unsplash):
                            with patch("app.video_maker.freesound_provider.search_sound_effects", return_value=mock_freesound):
                                with patch("app.video_maker.giphy_provider.search_giphy_stickers", return_value=mock_giphy):
                                    res = await self.engine.generate_short_prompt_async(
                                        topic_or_question="## SCENE 1\nKafka Event Streaming Architecture",
                                        language="en"
                                    )

        scene_assets = res.get("scene_assets", [])
        self.assertTrue(len(scene_assets) > 0, "scene_assets must not be empty")

        for idx, asset in enumerate(scene_assets):
            self.assertTrue(bool(asset.get("video_url")), f"Scene {idx} video_url is blank")
            self.assertTrue(bool(asset.get("image_url")), f"Scene {idx} image_url is blank")
            self.assertTrue(bool(asset.get("sfx_url")), f"Scene {idx} sfx_url is blank")
            self.assertTrue(bool(asset.get("sticker_url")), f"Scene {idx} sticker_url is blank")

    async def test_media_pipeline_false_provenance_on_timeout(self):
        """
        Adversarial test: When media APIs timeout, scene_assets and attribution_ledger
        must NOT falsely attribute failed assets to Pixabay/Unsplash.
        Currently lines 2253-2256 and lines 2271-2275 check 'if pixabay_active' instead of checking
        if video_url is present, resulting in false provenance reporting.
        """
        def sync_hang(*args, **kwargs):
            import time
            time.sleep(10.0)
            return []

        with patch.object(self.engine, "_parse_master_prompt_text", return_value={"id": "test_scn", "stages": self.mock_stages, "scenes": self.mock_stages}):
            with patch("app.core.neural_tts.neural_tts.generate_speech_async", return_value=True):
                with patch("app.video_maker.sql_short_engine.get_mp3_duration", return_value=8.0):
                    with patch("app.video_maker.pixabay_video_provider.search_pixabay_videos", side_effect=sync_hang):
                        with patch("app.video_maker.unsplash_provider.search_unsplash_photos", side_effect=sync_hang):
                            res = await self.engine.generate_short_prompt_async(
                                topic_or_question="## SCENE 1\nDistributed Consensus in Raft",
                                language="en"
                            )

        # In scene_assets, if video_url is empty, broll_source should be 'Procedural Shader', NOT 'Pixabay Video'
        scene_assets = res.get("scene_assets", [])
        self.assertTrue(len(scene_assets) > 0)
        for idx, asset in enumerate(scene_assets):
            if not asset.get("video_url"):
                self.assertNotEqual(
                    asset.get("broll_source"), "Pixabay Video (4K/2K)",
                    f"Scene {idx} falsely claims 'Pixabay Video (4K/2K)' when video_url is empty"
                )


class TestJsDomAndLedgerCompatibility(unittest.TestCase):
    """Verify DOM element IDs and fallback lookups between sql_video_js.py and sql_video_workspace.py."""

    def setUp(self):
        self.workspace_html = get_sql_video_workspace_html()
        self.client_js = get_sql_video_js()

    def test_pipeline_tracker_step_ids_exist_in_workspace(self):
        """
        Verify all 5 step IDs in updatePipelineTracker exist in the rendered HTML:
        ['stepLlm', 'stepVoice', 'stepMedia', 'stepSfx', 'stepRender']
        """
        step_ids = ['stepLlm', 'stepVoice', 'stepMedia', 'stepSfx', 'stepRender']
        for sid in step_ids:
            self.assertIn(
                f'id="{sid}"', self.workspace_html,
                f"Pipeline tracker step ID '{sid}' not found in workspace HTML"
            )

    def test_pipeline_overall_progress_elements_exist(self):
        """Verify genPipelineSteps and pipelineOverallPercent exist in workspace HTML."""
        self.assertIn('id="genPipelineSteps"', self.workspace_html)
        self.assertIn('id="pipelineOverallPercent"', self.workspace_html)

    def test_dual_lookup_ledger_elements_resolve_cleanly(self):
        """
        Verify dual-lookup element pairs in renderAiAttributionLedger:
        1. 'ledgerLlmName' or 'ledgerScriptModel'
        2. 'ledgerLatencyBadge' or 'ledgerElapsedTime'
        3. 'ledgerMediaSources' or 'ledgerBrollInfo'
        """
        pair1_resolved = ('id="ledgerLlmName"' in self.workspace_html) or ('id="ledgerScriptModel"' in self.workspace_html)
        self.assertTrue(pair1_resolved, "Neither 'ledgerLlmName' nor 'ledgerScriptModel' found in HTML")

        pair2_resolved = ('id="ledgerLatencyBadge"' in self.workspace_html) or ('id="ledgerElapsedTime"' in self.workspace_html)
        self.assertTrue(pair2_resolved, "Neither 'ledgerLatencyBadge' nor 'ledgerElapsedTime' found in HTML")

        pair3_resolved = ('id="ledgerMediaSources"' in self.workspace_html) or ('id="ledgerBrollInfo"' in self.workspace_html)
        self.assertTrue(pair3_resolved, "Neither 'ledgerMediaSources' nor 'ledgerBrollInfo' found in HTML")

    def test_ledger_single_lookup_elements_exist(self):
        """Verify ledgerVoiceName, ledgerScenesList exist in workspace HTML."""
        self.assertIn('id="ledgerVoiceName"', self.workspace_html)
        self.assertIn('id="ledgerScenesList"', self.workspace_html)

    def test_media_provider_toggles_exist(self):
        """Verify dynamic media provider toggle IDs exist in workspace HTML."""
        toggles = ['togglePixabay', 'toggleUnsplash', 'toggleGiphy', 'toggleFreesound', 'toggleTavily']
        for tid in toggles:
            self.assertIn(f'id="{tid}"', self.workspace_html, f"Media toggle '{tid}' not found in HTML")

    def test_js_step_ids_have_null_checks(self):
        """Verify that sql_video_js.py checks for null on stepIds and ledger elements."""
        self.assertIn("if (!el) return;", self.client_js)
        self.assertIn("if (llmEl)", self.client_js)
        self.assertIn("if (latBadge)", self.client_js)
        self.assertIn("if (mediaEl)", self.client_js)


if __name__ == "__main__":
    unittest.main()
