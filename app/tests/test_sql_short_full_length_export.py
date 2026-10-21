import ast
import re
import unittest
from collections import defaultdict, deque
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


def load_detailed_brief_parser():
    source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = [
        item for item in tree.body
        if isinstance(item, ast.FunctionDef) and item.name in {"_infer_brief_layout", "_parse_detailed_brief"}
    ]
    namespace = {"re": re, "Any": Any, "Dict": Dict, "List": List, "Optional": Optional}
    exec(compile(ast.Module(body=functions, type_ignores=[]), "<brief-parser-test>", "exec"), namespace)
    return namespace["_parse_detailed_brief"]


class FullLengthVideoExportTests(unittest.TestCase):
    def test_airflow_brief_preserves_all_seven_hindi_scenes(self):
        brief = """# PROJECT: Apache Airflow DAG Kaise Kaam Karta Hai?
Duration: Maximum 60 seconds
# SCENE 1 — INTERVIEW QUESTION
### Time: 0–6 seconds
### Hindi Voiceover:
"DAG क्या है?"
### Diagram and Animation:
Show the scheduler.
# SCENE 2 — WHAT IS A DAG?
### Time: 6–14 seconds
### Hindi Voiceover:
"DAG tasks और dependencies define करता है।"
### Diagram and Animation:
Show Extract, Transform, Load.
# SCENE 3 — SCHEDULER AND TASK EXECUTION
### Time: 14–24 seconds
### Hindi Voiceover:
"Scheduler eligible tasks schedule करता है।"
### Diagram and Animation:
Reveal scheduled tasks.
# SCENE 4 — PARALLEL EXECUTION
### Time: 24–34 seconds
### Hindi Voiceover:
"Independent tasks parallel चल सकते हैं।"
### Diagram and Animation:
Show two branches merging.
# SCENE 5 — RETRY AND FAILURE HANDLING
### Time: 34–44 seconds
### Hindi Voiceover:
"Failed task configured retry के बाद चल सकता है।"
### Diagram and Animation:
Show retry loop.
# SCENE 6 — INTERVIEW ANSWER AND FINAL DAG
### Time: 44–55 seconds
### Hindi Voiceover:
"DAG dependencies बताता है, Scheduler schedule करता है।"
### Diagram and Animation:
Reveal final graph.
# SCENE 7 — CTA
### Time: 55–60 seconds
### Hindi Voiceover:
"Code With Mangesh को follow करें।"
### Diagram and Animation:
Show branding.
"""
        result = load_detailed_brief_parser()(brief)
        self.assertEqual(result["title"], "Apache Airflow DAG Kaise Kaam Karta Hai?")
        self.assertEqual(len(result["scenes"]), 7)
        self.assertIn("Independent tasks", result["scenes"][3]["speech"])
        self.assertEqual(result["max_duration_seconds"], 60)

    def test_local_narration_compression_keeps_each_scene_within_budget(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        function = next(
            item for item in tree.body
            if isinstance(item, ast.FunctionDef) and item.name == "_deterministic_condense_scenes"
        )
        condensed = ast.get_source_segment(source, function)
        namespace = {"List": List, "Dict": Dict, "re": re, "ValueError": ValueError}
        exec(compile(condensed, "<local-narration-compression>", "exec"), namespace)
        scenes = [
            {"speech": "Data Engineer interview में Airflow DAG क्या है? यह task dependencies बताता है।"},
            {"speech": "Scheduler eligible tasks को schedule करता है, workers उन्हें execute करते हैं।"},
            {"speech": "Parallel tasks साथ चलते हैं; failure पर configured retries काम आते हैं।"},
        ]
        result = namespace["_deterministic_condense_scenes"](scenes, 15)
        self.assertEqual(len(result), len(scenes))
        self.assertTrue(all(result))
        self.assertLessEqual(sum(len(speech.split()) for speech in result), 15)

    def test_scene_brief_extracts_hindi_voiceover_and_scene_titles(self):
        brief = """# PROJECT: AWS DMS explainer
Duration: Strictly 55–60 seconds.
# SCENE 1 — INTERVIEW QUESTION
### Time: 00–06 seconds
### Voiceover
[CONFIDENT, ENGAGING]
"AWS DMS, Oracle से Snowflake तक डेटा कैसे पहुँचाता है? [PAUSE 0.3s]"
### Diagram and animation
Show Oracle.
### On-screen text:
`INTERVIEW QUESTION`
---
# SCENE 2 — WHAT IS AWS DMS?
### Voiceover
"AWS DMS एक managed service है।"
### Diagram and animation
Show the cloud.
"""
        result = load_detailed_brief_parser()(brief)
        self.assertEqual(result["title"], "AWS DMS explainer")
        self.assertEqual([scene["title"] for scene in result["scenes"]], ["INTERVIEW QUESTION", "WHAT IS AWS DMS?"])
        self.assertIn("Oracle से Snowflake", result["scenes"][0]["speech"])
        self.assertNotIn("PAUSE", result["scenes"][0]["speech"])
        self.assertEqual(result["scenes"][0]["start"], 0)
        self.assertEqual(result["scenes"][0]["end"], 6)
        self.assertEqual(result["scenes"][0]["visual_data"]["layout"], "")
        self.assertEqual(result["max_duration_seconds"], 60)

    def test_aws_dms_graph_fallback_keeps_named_components_and_shapes(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        function = next(
            item for item in tree.body
            if isinstance(item, ast.FunctionDef) and item.name == "_aws_dms_fallback_graph"
        )
        namespace = {"Dict": Dict, "Any": Any}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "<aws-dms-fallback-test>", "exec"), namespace)
        graph = namespace["_aws_dms_fallback_graph"]()
        nodes = {node["label"]: node for node in graph["nodes"]}
        self.assertEqual(nodes["Oracle Database"]["shape"], "database")
        self.assertEqual(nodes["DMS Replication Instance"]["shape"], "hexagon")
        self.assertEqual(nodes["Snowflake Database"]["shape"], "database")
        self.assertIn("Replication Task", nodes)
        self.assertIn("Full Load", nodes)
        self.assertIn("CDC Change Stream", nodes)
        self.assertEqual(graph["groups"][0]["shape"], "cloud")
        node_ids = set(nodes[node]["id"] for node in nodes)
        self.assertTrue(all(edge["from"] in node_ids and edge["to"] in node_ids for edge in graph["edges"]))

    def test_airflow_graph_fallback_preserves_branch_retry_and_component_shapes(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        function = next(
            item for item in tree.body
            if isinstance(item, ast.FunctionDef) and item.name == "_airflow_fallback_graph"
        )
        namespace = {"Dict": Dict, "Any": Any}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "<airflow-graph-test>", "exec"), namespace)
        graph = namespace["_airflow_fallback_graph"]()
        nodes = {node["id"]: node for node in graph["nodes"]}
        self.assertEqual(graph["layout"], "pipeline")
        self.assertEqual(nodes["scheduler"]["shape"], "circle")
        self.assertEqual(nodes["transform"]["shape"], "hexagon")
        self.assertEqual(nodes["load"]["shape"], "database")
        self.assertEqual(nodes["validation"]["shape"], "diamond")
        self.assertEqual(nodes["monitoring"]["shape"], "dashboard")
        edge_pairs = {(edge["from"], edge["to"]) for edge in graph["edges"]}
        self.assertIn(("extract", "customer-task"), edge_pairs)
        self.assertIn(("extract", "transaction-task"), edge_pairs)
        self.assertIn(("failed-task", "retry-policy"), edge_pairs)
        self.assertIn(("retry-policy", "retry-success"), edge_pairs)
        self.assertTrue(all(edge["from"] in nodes and edge["to"] in nodes for edge in graph["edges"]))

    def test_airflow_pipeline_layout_places_parallel_tasks_side_by_side(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "architecture_animation.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        function = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == "_layout_nodes")
        namespace = {"defaultdict": defaultdict, "deque": deque, "Any": Any}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "<airflow-pipeline-layout-test>", "exec"), namespace)
        engine_source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        engine_tree = ast.parse(engine_source)
        graph_function = next(
            item for item in engine_tree.body
            if isinstance(item, ast.FunctionDef) and item.name == "_airflow_fallback_graph"
        )
        graph_namespace = {"Dict": Dict, "Any": Any}
        exec(compile(ast.Module(body=[graph_function], type_ignores=[]), "<airflow-graph-fallback>", "exec"), graph_namespace)
        graph = graph_namespace["_airflow_fallback_graph"]()
        nodes = [dict(node) for node in graph["nodes"]]
        namespace["_layout_nodes"](nodes, graph["edges"], graph["layout"])
        positions = {node["id"]: node for node in nodes}
        self.assertNotEqual(positions["customer-task"]["x"], positions["transaction-task"]["x"])
        self.assertEqual(positions["customer-task"]["y"], positions["transaction-task"]["y"])
        self.assertGreater(len({node["x"] for node in nodes}), 1)

    def test_scene_timeline_covers_narration_longer_than_one_minute(self):
        stages = [
            {"title": "Architecture", "speech_en": "A detailed sentence describing a system design stage."},
            {"title": "Conclusion", "speech_en": "A final sentence summarizing the complete technical scenario."},
        ]
        calibrated, duration, outro_start = load_duration_calibrator()(stages, 127.4, lang_key="en")
        self.assertEqual(duration, 127.4)
        self.assertEqual(outro_start, 127.4)
        self.assertEqual(calibrated[-1]["end"], 127.4)

    def test_user_authored_scene_seven_is_not_removed_as_a_template_outro(self):
        stages = [{
            "id": 7,
            "user_authored_scene": True,
            "title": "CTA",
            "speech_en": "Follow Code with Mangesh for more technical explainers.",
        }]
        calibrated, _, _ = load_duration_calibrator()(stages, 5, lang_key="en")
        self.assertEqual(len(calibrated), 1)
        self.assertEqual(calibrated[0]["title"], "CTA")

    def test_browser_download_requests_final_mp4_without_duration_cap(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        self.assertIn('fetch("/api/sql_video/finalize_mp4"', source)
        self.assertIn('fetch(`/api/sql_video/finalize_mp4/${encodeURIComponent(queuedJob.job_id)}`)', source)
        self.assertIn('status.status === "ready"', source)
        self.assertIn('status.status === "failed"', source)
        self.assertIn('finalize_mp4/${encodeURIComponent(queuedJob.job_id)}/download', source)
        self.assertIn("synchronized WebM backup", source)
        self.assertIn("${Math.round(totalDuration)}s.webm", source)
        self.assertIn(".mp4`", source)
        self.assertIn("totalDuration = Math.max(1, totalDuration)", source)
        self.assertIn("(timestamp - startTime) / 1000", source)
        self.assertIn("videoBitsPerSecond: 3500000", source)
        self.assertIn("const exportFrameRate = 24", source)
        self.assertNotIn("stepBatch = totalDuration <= 15 ? 1 : 2", source)
        self.assertNotIn("Math.min(59.5, totalDuration)", source)
        self.assertIn("Generate click produces the complete synchronized 9:16 MP4 download", source)

    def test_mp4_conversion_route_uses_h264_and_returns_a_video_file(self):
        source = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")
        self.assertIn('@app.post("/api/sql_video/finalize_mp4")', source)
        self.assertIn('"-c:v", "libx264"', source)
        self.assertIn('media_type="video/mp4"', source)
        self.assertIn('return JSONResponse({"job_id": job_token, "status": "queued"}, status_code=202)', source)
        self.assertIn('@app.get("/api/sql_video/finalize_mp4/{job_id}/download")', source)
        self.assertIn('background_tasks.add_task(_run_sql_video_mp4_conversion', source)

    def test_mp4_conversion_limits_encoder_memory_for_free_instances(self):
        source = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")
        encoder = source.split("def _run_sql_video_mp4_conversion", 1)[1].split("@app.post(", 1)[0]
        self.assertIn('"scale=720:1280:flags=fast_bilinear"', encoder)
        self.assertIn('"-r", "24"', encoder)
        self.assertIn('"-preset", "ultrafast"', encoder)
        self.assertIn('"-threads", "1"', encoder)
        self.assertIn('"-filter_threads", "1"', encoder)

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

    def test_duration_shortening_retries_when_model_exceeds_word_budget(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        method = source.split("async def _condense_narration_to_duration", 1)[1].split("async def generate_short_prompt_async", 1)[0]
        self.assertIn("for attempt in range(3)", method)
        self.assertIn("budget = max(24, int(budget * 0.8))", method)
        self.assertIn("json.JSONDecoder().raw_decode", method)
        self.assertIn("Online narration shortening failed", method)
        self.assertIn("_deterministic_condense_scenes(scenes, max_words)", method)

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

    def test_accepts_model_overlays_with_invented_kinds(self):
        scene = {
            "title": "Context assembly",
            "speech": "Retrieved chunks are added to the prompt before generation.",
            "overlay_items": [
                {"kind": "text", "content": "context block", "x": 0.5, "y": 0.4},
                {"kind": "", "content": "retrieved chunks", "x": 0.4, "y": 0.6},
            ],
        }
        validated = self._validator()(scene)
        self.assertEqual([item["kind"] for item in validated["overlay_items"]], ["label", "label"])
        self.assertTrue(validated["visual_prompt"])
        self.assertTrue(validated["continuity"])

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

    def test_architecture_renderer_uses_independent_vector_components(self):
        renderer = (PROJECT_ROOT / "app" / "ui" / "architecture_animation_renderer.py").read_text(encoding="utf-8")
        self.assertIn("function drawTechnicalArchitectureGraph(", renderer)
        self.assertIn("architectureStrokeProgress", renderer)
        self.assertIn('"packets"', renderer)
        for shape in ("database", "diamond", "hexagon", "cloud", "document", "terminal", "dashboard"):
            self.assertIn(f'shape === "{shape}"', renderer)
        self.assertNotIn("drawImage(", renderer)

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

    def test_video_job_skips_scene_images_for_diagram_render(self):
        source = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")
        route = source.split('@app.post("/api/sql_video/generate_prompt_job")', 1)[1].split("@app.get(", 1)[0]
        self.assertNotIn("generate_scene_assets", route)
        self.assertIn("sql_short_engine.generate_short_prompt_async,\n        None,", route)

    def test_video_frames_render_vector_graph_without_scene_images(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        frame = source.split("function renderSqlShortFrame(", 1)[1]
        self.assertIn("drawTechnicalArchitectureGraph(ctx, W, H, p.architecture_graph", frame)
        self.assertNotIn("renderPromptSceneAssetVisual(", frame)
        self.assertNotIn("loadPromptSceneAssets(data.scene_assets", source)
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

    def test_generated_storyboard_uses_scene_titles_as_numbered_flow(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        spec = source.split("function buildDiagramSpec(", 1)[1].split("function drawDiagramFlow(", 1)[0]
        self.assertIn("hasStageTitles", spec)
        self.assertIn("diagramIconForLabel", spec)
        self.assertIn("Number(stageIndex)", spec.replace('typeof stageIndex === "number"', "Number(stageIndex) >= 0"))
        self.assertIn("sceneList.slice(0, 5)", spec)

    def test_storyboard_source_is_reported_with_the_result(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        self.assertIn('"storyboard_source": matched.get("storyboard_source"', source)
        self.assertIn('matched["storyboard_source"] = "online_model"', source)
        self.assertIn('matched["storyboard_source"] = "local_fallback"', source)

    def test_storyboard_prompt_requests_native_language_narration(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        self.assertIn("Marathi in Devanagari script", source)
        self.assertIn("Every speech value must be written only in this language", source)
        self.assertIn("Every speech value must be written only in this language", source)

    def test_on_screen_text_is_english_only(self):
        js = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        self.assertIn("subtitleText = activeStage.speech_en", js)
        self.assertNotIn("AI VOICE", js)
        workspace = (PROJECT_ROOT / "app" / "ui" / "sql_video_workspace.py").read_text(encoding="utf-8")
        self.assertNotIn("Regional AI Voice", workspace)
        engine = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        self.assertIn('"speech_en": en[i]', engine)
        self.assertIn("Add speech_en as a natural English translation", engine)

    def test_diagram_renders_3d_isometric_slabs(self):
        js = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        self.assertIn("function drawIso3DNode(", js)
        self.assertIn("function drawIsoFloorGrid(", js)
        self.assertIn("drawIso3DNode(ctx, boxX, y, boxW, nodeH, depth", js)
        self.assertIn("drawDiagramAmbientParticles", js)

    def test_model_storyboards_get_an_english_on_screen_pass(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        self.assertIn("async def _english_on_screen_text", source)
        self.assertIn('stage["speech_en"] = str(subtitle).strip()', source)
        self.assertIn("await self._english_on_screen_text(stages,", source)
        self.assertIn('matched["title"] = english_headline', source)

    def test_detailed_brief_produces_scene_specific_layouts(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("_infer_brief_layout", "_parse_detailed_brief")]
        namespace = {"re": __import__("re"), "Optional": Optional, "Dict": Dict, "Any": Any, "List": List}
        module = ast.Module(body=nodes, type_ignores=[])
        ast.fix_missing_locations(module)
        exec(compile(module, "<brief-parser>", "exec"), namespace)
        brief = """
### SCENE 1 - HOOK (0-5 sec)
**Voiceover:** "Every second databases process transactions."
**Visual:** Split screen. Left: banking. Right: analytics.
**On-screen text:** `OLTP = Transactions` | `OLAP = Analytics`

### SCENE 2 - FLOW (5-12 sec)
**Voiceover:** "OLTP handles everyday operations."
**Visual:** Animate this flow:
`Customer -> Banking App -> OLTP Database`

### SCENE 3 - DIFF (12-22 sec)
**Voiceover:** "OLTP focuses on current operations."
**Visual:** Build a comparison table row by row.
| Feature | OLTP | OLAP |
| Purpose | Daily operations | Data analysis |
| Example | Bank transfer | Monthly report |

### SCENE 4 - TYPES (22-28 sec)
**Voiceover:** "Modern stacks mix workloads."
**Visual:** Four pill chips in a 2x2 grid: TEXT, IMAGE, VIDEO, AUDIO
"""
        parsed = namespace["_parse_detailed_brief"](brief)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["storyboard_source"], "detailed_brief")
        self.assertEqual(len(parsed["scenes"]), 4)
        layouts = [scene["visual_data"]["layout"] for scene in parsed["scenes"]]
        self.assertEqual(layouts, ["split", "pipeline", "table", "chips"])
        self.assertEqual(parsed["scenes"][0]["title"], "HOOK")
        self.assertEqual(parsed["scenes"][2]["visual_data"]["rows"][0], ["Feature", "OLTP", "OLAP"])

    def test_brief_scene_designs_exist_in_the_renderer(self):
        js = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        for name in ("drawBriefTitle", "drawBriefSplit", "drawBriefPipeline", "drawBriefTable", "drawBriefChips", "drawBriefWarning", "drawBriefCards"):
            self.assertIn(f"function {name}(", js)
        self.assertIn("if (p.show_subtitles === false) { return; }", js)

    def test_architecture_graph_uses_vertical_safe_margins(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "architecture_animation.py").read_text(encoding="utf-8")
        self.assertIn('"x": 0.5', source)
        self.assertIn('0.16 + 0.59 * index / (len(nodes) - 1)', source)
        self.assertIn('aspect-ratio: 9 / 16', (PROJECT_ROOT / "app" / "ui" / "sql_video_workspace.py").read_text(encoding="utf-8"))

    def test_audio_capture_route_is_reused_between_exports(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        export = source.split("async function exportSqlShortVideo(", 1)[1].split("window.exportSqlShortVideo", 1)[0]
        self.assertIn("window._sqlVideoAudioRoute", export)
        self.assertEqual(export.count("createMediaElementSource(audioEl)"), 1)
        self.assertIn("audioRoute.destination.stream.getAudioTracks().map(track => track.clone())", export)
        self.assertIn("refusing to export a muted video", export)
        self.assertNotIn("audioCtx.close()", export)

    def test_detailed_project_brief_preserves_explicit_scenes_for_model_parsing(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        self.assertNotIn('lang_key = "en"', source.split("brief_blueprint = _parse_detailed_brief", 1)[1].split("# 4.", 1)[0])
        self.assertIn("_architecture_from_detailed_brief(text_input, stages)", source)
        self.assertIn("No generic vertical-box fallback was rendered", source)
        self.assertIn('graph["layout"] = "pipeline"', source)
        self.assertIn("Required prompt-specific concepts that must appear as separate graph nodes", source)
        self.assertIn("Choose the number of educational scenes to fit the prompt's complexity", source)


if __name__ == "__main__":
    unittest.main()
