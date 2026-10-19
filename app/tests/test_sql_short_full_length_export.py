import ast
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_duration_calibrator():
    source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(
        item for item in tree.body
        if isinstance(item, ast.FunctionDef) and item.name == "compute_audio_synchronized_stages"
    )
    namespace = {
        "Any": Any,
        "Dict": Dict,
        "List": List,
        "Optional": Optional,
        "Tuple": Tuple,
        "_infer_action_type": lambda index, count: "hook" if index == 0 else "diagram",
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), "<duration-test>", "exec"), namespace)
    return namespace["compute_audio_synchronized_stages"]


class FullLengthVideoExportTests(unittest.TestCase):
    def test_scene_timeline_covers_narration_longer_than_one_minute(self):
        stages = [
            {"title": "Architecture", "speech_en": "A detailed sentence describing a system design stage."},
            {"title": "Conclusion", "speech_en": "A final sentence summarizing the complete technical scenario."},
        ]
        calibrated, duration, outro_start = load_duration_calibrator()(stages, 127.4, lang_key="en")
        self.assertEqual(duration, 127.4)
        self.assertEqual(outro_start, 127.4)
        self.assertEqual(calibrated[-1]["end"], 127.4)

    def test_browser_download_requests_final_mp4_without_duration_cap(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        self.assertIn('fetch("/api/sql_video/finalize_mp4"', source)
        self.assertIn(".mp4`", source)
        self.assertIn("totalDuration = Math.max(1, totalDuration)", source)
        self.assertIn("(timestamp - startTime) / 1000", source)
        self.assertNotIn("stepBatch = totalDuration <= 15 ? 1 : 2", source)
        self.assertNotIn("Math.min(59.5, totalDuration)", source)
        self.assertIn("Generate click produces the complete synchronized 9:16 MP4 download", source)

    def test_mp4_conversion_route_uses_h264_and_returns_a_video_file(self):
        source = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")
        self.assertIn('@app.post("/api/sql_video/finalize_mp4")', source)
        self.assertIn('"-c:v", "libx264"', source)
        self.assertIn('media_type="video/mp4"', source)

    def test_mp4_conversion_limits_encoder_memory_for_free_instances(self):
        source = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")
        route = source.split('@app.post("/api/sql_video/finalize_mp4")', 1)[1].split("@app.get(", 1)[0]
        self.assertIn('"-preset", "ultrafast"', route)
        self.assertIn('"-threads", "1"', route)
        self.assertIn('"-filter_threads", "1"', route)

    def test_universal_video_prompt_requests_topic_specific_visuals(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        self.assertIn('"visual_description"', source)
        self.assertIn('"entities"', source)
        self.assertIn("avoid repeating the same composition", source.lower())
        self.assertNotIn('"title": "Problem Hook"', source)
        self.assertNotIn('f"}}"', source)
        self.assertIn('"content_type":"tech_topic"', source)
        self.assertIn("Every user prompt must pass through", source)
        self.assertIn('audio_url = ""', source)
        self.assertNotIn('audio_url = f"/audio/preset_sql_q1_second_highest_salary_', source)

    def test_short_form_narration_targets_under_sixty_seconds(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        self.assertIn("Target 45 to 55 seconds", source)
        self.assertIn("max_narration_words = 112 if lang_key == \"en\" else 88", source)
        self.assertIn("Short narration compression notice", source)
        self.assertIn("audio_duration=actual_dur", source)

    def test_invalid_model_storyboard_retries_before_local_fallback(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        self.assertIn("retrying storyboard", source)
        self.assertIn("Make every scene specific to the user's topic", source)
        self.assertIn("Storyboard retry notice; using local topic fallback", source)

    def test_storyboard_fallback_preserves_any_topic_and_language(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        engine = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "SqlShortVideoEngine")
        method = next(node for node in engine.body if isinstance(node, ast.FunctionDef) and node.name == "_build_prompt_fallback")
        namespace = {"re": __import__("re"), "Dict": Dict, "Any": Any}
        exec(compile(ast.Module(body=[method], type_ignores=[]), "<storyboard-fallback>", "exec"), namespace)
        storyboard = namespace["_build_prompt_fallback"](None, "How does a rocket engine work?", "en")
        self.assertEqual(storyboard["content_type"], "tech_topic")
        self.assertIn("rocket engine", storyboard["title"])
        self.assertEqual(len(storyboard["scenes"]), 5)
        self.assertTrue(all(scene["speech"] and len(scene["entities"]) >= 2 for scene in storyboard["scenes"]))
        marathi = namespace["_build_prompt_fallback"](None, "क्वांटम कंप्यूटिंग", "mr")
        self.assertTrue(marathi["scenes"][0]["speech"].startswith("चला"))

    def test_storyboard_fallback_uses_topic_specific_mechanisms(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        engine = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "SqlShortVideoEngine")
        method = next(node for node in engine.body if isinstance(node, ast.FunctionDef) and node.name == "_build_prompt_fallback")
        namespace = {"re": __import__("re"), "Dict": Dict, "Any": Any}
        exec(compile(ast.Module(body=[method], type_ignores=[]), "<storyboard-fallback>", "exec"), namespace)
        storyboard = namespace["_build_prompt_fallback"](None, "Explain a CI/CD pipeline with Docker", "en")
        labels = [scene["entities"][0]["label"] for scene in storyboard["scenes"]]
        self.assertIn("Automated build", labels)
        first_visual = storyboard["scenes"][0]["visual_prompt"]
        self.assertNotIn("Portrait educational scene", first_visual)
        self.assertIn("no people", first_visual.lower())
        self.assertIn("3D technical diagram", first_visual)

    def test_universal_topics_do_not_default_to_sql_ui(self):
        engine_source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        ui_source = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        self.assertIn('else "tech_topic"', engine_source)
        self.assertIn('content_type: data.content_type || "tech_topic"', ui_source)
        self.assertIn('if (data.content_type === "sql_query" || data.solution_sql) runPipelineSandboxVerification();', ui_source)
    def test_video_maker_uses_strict_portrait_preview_and_no_short_test_export(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_workspace.py").read_text(encoding="utf-8")
        self.assertIn('aspect-ratio: 9 / 16', source)
        self.assertIn('width="1080" height="1920"', source)
        self.assertNotIn('exportSqlShortVideo(15)', source)



class SceneVisualContractTests(unittest.TestCase):
    @staticmethod
    def _validator():
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        node = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == "_validate_scene_visual_contract")
        namespace = {"Any": Any, "Dict": Dict, "List": List}
        exec(compile(ast.Module(body=[node], type_ignores=[]), "<scene-contract>", "exec"), namespace)
        return namespace["_validate_scene_visual_contract"]

    def test_accepts_prompt_specific_scene_and_native_code_overlay(self):
        scene = {
            "title": "Python list traversal",
            "speech": "The loop reads each item and adds it to the result.",
            "visual_prompt": "Close view of a Python list; the loop visits each value in order and updates the result list.",
            "continuity": "Same list and loop variable remain visible across this explanation.",
            "overlay_items": [
                {"kind": "code", "content": "for item in values:", "x": 0.12, "y": 0.82},
                {"kind": "label", "content": "result list", "x": 0.75, "y": 0.7},
            ],
        }
        validated = self._validator()(scene)
        self.assertEqual(validated["visual_prompt"], scene["visual_prompt"])
        self.assertEqual(validated["overlay_items"][0]["content"], "for item in values:")

    def test_rejects_overlay_outside_normalized_canvas(self):
        scene = {
            "title": "Photon",
            "speech": "A photon transfers energy to an electron.",
            "visual_prompt": "A photon strikes a silicon cell and releases an electron.",
            "continuity": "The same silicon cell stays in view.",
            "overlay_items": [{"kind": "label", "content": "electron", "x": 1.3, "y": 0.5}],
        }
        with self.assertRaisesRegex(ValueError, "normalized canvas"):
            self._validator()(scene)


class PromptScenePlayerTests(unittest.TestCase):
    def test_generate_ui_polls_scene_job_progress(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        self.assertIn('/api/sql_video/generate_prompt_job', source)
        self.assertIn('/api/sql_video/generation_jobs/', source)
        self.assertIn('job.result_data', source)
        self.assertIn('sqlVideoGenerationStatus', source)

    def test_scene_renderer_uses_ai_assets_and_native_overlays(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        self.assertIn('async function loadPromptSceneAssets(sceneAssets)', source)
        renderer = source.split('function renderPromptSceneAssetVisual(', 1)[1].split('function renderPromptDrivenVisual(', 1)[0]
        self.assertIn('drawImage(media', renderer)
        self.assertIn('overlay_items', renderer)

    def test_video_generation_survives_empty_server_responses(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        self.assertIn("async function readVideoJsonResponse", source)
        self.assertIn("consecutivePollFailures", source)
        self.assertIn("await readVideoJsonResponse(queuedRes)", source)
        self.assertIn("await readVideoJsonResponse(pollRes)", source)

    def test_scene_pipeline_stays_inside_free_tier_memory(self):
        image_source = (PROJECT_ROOT / "app" / "agents" / "image_agent.py").read_text(encoding="utf-8")
        self.assertIn('"imageSize": "1K"', image_source)
        self.assertNotIn('"imageSize": "2K"', image_source)
        pipeline_source = (PROJECT_ROOT / "app" / "video_maker" / "scene_visual_pipeline.py").read_text(encoding="utf-8")
        self.assertIn("asyncio.Semaphore(1)", pipeline_source)
        self.assertIn('image.draft("RGB"', pipeline_source)

    def test_video_job_skips_ai_image_generation(self):
        source = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")
        route = source.split('@app.post("/api/sql_video/generate_prompt_job")', 1)[1].split("@app.get(", 1)[0]
        self.assertIn("None,  # Diagram-only render", route)
        self.assertNotIn("generate_scene_assets", route)

    def test_video_frames_are_static_diagrams_without_ai_images(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        frame = source.split("function renderSqlShortFrame(", 1)[1]
        self.assertIn("renderArchitectureScene(ctx, W, H, p, activeStage", frame)
        self.assertNotIn("renderPromptSceneAssetVisual(ctx, W, H, p, activeStage", frame)
        self.assertNotIn("drawPromptMotionBackground(ctx, W, H, t)", frame)
        self.assertNotIn("AI VOICE", source)
        for renderer in ("drawDiagramFlow", "drawDiagramCodePanel", "drawDiagramTablePanel", "drawDiagramComparePanel"):
            self.assertIn(f"function {renderer}(", source)
        self.assertIn("DIAGRAM_GLYPHS", source)

    def test_storyboard_fallback_builds_numbered_diagram_steps(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        engine = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "SqlShortVideoEngine")
        method = next(node for node in engine.body if isinstance(node, ast.FunctionDef) and node.name == "_build_prompt_fallback")
        namespace = {"re": __import__("re"), "Dict": Dict, "Any": Any}
        exec(compile(ast.Module(body=[method], type_ignores=[]), "<storyboard-fallback>", "exec"), namespace)
        storyboard = namespace["_build_prompt_fallback"](None, "explain Docker", "en")
        first = storyboard["scenes"][0]["visual_data"]
        self.assertEqual(first["layout"], "flow")
        self.assertEqual(first["focus"], 0)
        self.assertEqual(
            [step["label"] for step in first["steps"]],
            ["Dockerfile", "Image layers", "Container runtime", "Port mapping", "Orchestration"],
        )
        self.assertTrue(all(step["icon"] for step in first["steps"]))
        self.assertEqual(storyboard["scenes"][2]["visual_data"]["focus"], 2)

    def test_edge_tts_retries_transient_failures(self):
        source = (PROJECT_ROOT / "app" / "core" / "neural_tts.py").read_text(encoding="utf-8")
        method = source.split("async def _synthesize_edge_tts(", 1)[1].split("async def synthesize_async(", 1)[0]
        self.assertIn("for attempt in range(3)", method)
        self.assertIn("asyncio.wait_for", method)
        self.assertIn("Edge Neural TTS failed after 3 attempts", method)

    def test_storyboard_fallback_covers_common_topic_families(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        engine = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "SqlShortVideoEngine")
        method = next(node for node in engine.body if isinstance(node, ast.FunctionDef) and node.name == "_build_prompt_fallback")
        namespace = {"re": __import__("re"), "Dict": Dict, "Any": Any}
        exec(compile(ast.Module(body=[method], type_ignores=[]), "<storyboard-fallback>", "exec"), namespace)
        fallback = namespace["_build_prompt_fallback"]
        cases = {
            "explain RAG pipeline": "User query",
            "how does banking payment settlement work": "Source system",
            "explain cybersecurity authentication": "User request",
            "data migration strategy": "Source",
            "explain API gateway": "Client request",
            "explain machine learning": "Input data",
            "explain generative AI": "Input prompt",
            "explain kubernetes": "Pod",
            "explain python list comprehension": "Script",
        }
        for prompt, expected_first_step in cases.items():
            steps = fallback(None, prompt, "en")["scenes"][0]["visual_data"]["steps"]
            self.assertEqual(steps[0]["label"], expected_first_step, f"wrong diagram flow for: {prompt}")
            self.assertEqual(len(steps), 5)

    def test_asset_scene_skips_generic_orbit_nodes(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        renderer = source.split('function renderPromptSceneAssetVisual(', 1)[1].split('function renderPromptDrivenVisual(', 1)[0]
        self.assertIn('ctx.drawImage(media', renderer)
        self.assertIn('return;', renderer)
        self.assertIn('aspect-ratio: 9 / 16', (PROJECT_ROOT / "app" / "ui" / "sql_video_workspace.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
