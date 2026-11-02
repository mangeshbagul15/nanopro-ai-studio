import ast
import json
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


def load_pre_render_validator():
    source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = [item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name in {"build_pre_render_validation_report", "_comparison_values_match", "_infer_interaction_step"}]
    namespace = {"re": re, "json": json, "Any": Any, "Dict": Dict, "List": List, "Optional": Optional}
    exec(compile(ast.Module(body=functions, type_ignores=[]), "<pre-render-validation-test>", "exec"), namespace)
    return namespace["build_pre_render_validation_report"]


def load_duration_limit_parser():
    source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == "_extract_short_video_duration_limit")
    namespace = {"re": re}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "<duration-limit-test>", "exec"), namespace)
    return namespace["_extract_short_video_duration_limit"]


def load_min_duration_parser():
    source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == "_extract_short_video_min_duration")
    namespace = {"re": re}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "<min-duration-test>", "exec"), namespace)
    return namespace["_extract_short_video_min_duration"]


def load_sentence_cue_builder():
    source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {"_ensure_sentence_cues", "_infer_interaction_step", "_comparison_values_match"}
    functions = [item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name in names]
    namespace = {"re": re, "Any": Any, "Dict": Dict, "List": List}
    exec(compile(ast.Module(body=functions, type_ignores=[]), "<sentence-cue-builder-test>", "exec"), namespace)
    return namespace["_ensure_sentence_cues"]


def load_scene_count_parser():
    source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == "_extract_requested_scene_count")
    namespace = {"re": re, "Optional": Optional}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "<scene-count-test>", "exec"), namespace)
    return namespace["_extract_requested_scene_count"]


def load_source_target_value_parser():
    source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == "_extract_source_target_values")
    namespace = {"re": re, "Dict": Dict}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "<source-target-values-test>", "exec"), namespace)
    return namespace["_extract_source_target_values"]


def load_mismatch_prompt_classifier():
    source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == "_is_data_mismatch_prompt")
    namespace = {"re": re}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "<mismatch-classifier-test>", "exec"), namespace)
    return namespace["_is_data_mismatch_prompt"]


class FullLengthVideoExportTests(unittest.TestCase):
    def test_pre_render_report_distinguishes_passed_from_unperformed_checks(self):
        validate = load_pre_render_validator()
        stages = [{"start": 0.0, "end": 10.0, "sentence_cues": [
            {"interaction_step": "failure", "speech": "Mismatch detected."},
            {"interaction_step": "process", "speech": "We investigate the cause."},
            {"interaction_step": "recover", "speech": "We reconcile the row."},
            {"interaction_step": "verify", "speech": "Values match.", "expected_result": "8000", "observed_result": "8000"},
        ]}]
        graph = {
            "nodes": [{"id": "oracle"}, {"id": "target"}],
            "edges": [{"id": "e1", "from": "oracle", "to": "target"}],
            "actions": [
                {"target_id": "e1", "action": "draw_edge", "start": 1.0, "end": 2.0},
                {"target_id": "e1", "action": "packets", "start": 2.0, "end": 3.0},
            ],
        }
        report = validate(stages, 10.0, 60.0, graph, duration_measured=True, mismatch_scenario=True)
        statuses = {item["name"]: item["status"] for item in report["checks"]}
        self.assertTrue(report["render_allowed"])
        self.assertEqual(statuses["Failure → diagnosis → recovery → verification"], "PASSED")
        self.assertEqual(statuses["External database / AWS / API execution"], "NOT_RUN")
        self.assertEqual(statuses["Visual safe area and readability"], "NOT_RUN")

    def test_mismatch_sequence_infers_actions_from_natural_dialogue(self):
        validate = load_pre_render_validator()
        stages = [{"start": 0.0, "end": 10.0, "sentence_cues": [
            {"speech": "Oracle shows 8000, but Snowflake has a stale value of 10000."},
            {"speech": "We trace the DMS logs and find the delayed batch."},
            {"speech": "Replay that batch and reconcile the Snowflake row."},
            {"speech": "Now validation confirms both sides match at 8000."},
        ]}]
        report = validate(stages, 10.0, 60.0, {"nodes": [], "edges": [], "actions": []}, duration_measured=True, mismatch_scenario=True)
        check = next(item for item in report["checks"] if item["name"] == "Failure → diagnosis → recovery → verification")
        self.assertEqual(check["status"], "PASSED")

    def test_generic_explainer_does_not_require_mismatch_recovery_or_completion_gate(self):
        validate = load_pre_render_validator()
        stages = [{"start": 0.0, "end": 10.0, "sentence_cues": [
            {"interaction_step": "failure", "component_state": "failed", "speech": "A model may fail on ambiguous input."},
            {"interaction_step": "complete", "component_state": "completed", "speech": "The answer is ready."},
        ]}]
        report = validate(stages, 10.0, 60.0, {"nodes": [], "edges": [], "actions": []}, duration_measured=True)
        self.assertTrue(report["render_allowed"])
        statuses = {item["name"]: item["status"] for item in report["checks"]}
        self.assertEqual(statuses["Failure and recovery order"], "NOT_RUN")
        self.assertEqual(statuses["Component completion gate"], "NOT_RUN")

    def test_fallback_sentence_cues_preserve_semantic_mismatch_sequence(self):
        build_cues = load_sentence_cue_builder()
        stage = {
            "speech_en": "A mismatch appears: source is 8000, target is stale at 10000. We trace the DMS logs. Replay the delayed batch and reconcile the row. Validation now confirms both values match at 8000.",
            "visual_data": {"elements": [{"label": "DMS", "x": 0.5, "y": 0.5}]},
        }
        build_cues([stage], "en")
        self.assertEqual([cue["interaction_step"] for cue in stage["sentence_cues"]], ["failure", "diagnose", "recover", "verify"])

    def test_mismatch_value_consistency_checks_source_stale_and_final_values(self):
        validate = load_pre_render_validator()
        stages = [{"start": 0.0, "end": 10.0, "speech": "Source balance 8000; stale target balance 10000.", "visual_data": {}, "sentence_cues": [
            {"interaction_step": "verify", "expected_result": "Source 101 balance 8000", "observed_result": "Target 101 balance 8000", "speech": "Values match."},
        ]}]
        report = validate(stages, 10.0, 60.0, {"nodes": [], "edges": [], "actions": []}, duration_measured=True, mismatch_scenario=True, source_target_values={"source": "8000", "target": "10000"})
        check = next(item for item in report["checks"] if item["name"] == "Mismatch example value consistency")
        self.assertEqual(check["status"], "PASSED")

    def test_mismatch_allows_initial_failed_comparison_before_recovery(self):
        validate = load_pre_render_validator()
        stages = [{"start": 0.0, "end": 10.0, "sentence_cues": [
            {"interaction_step": "failure", "component_state": "failed", "speech": "Record 103 is missing."},
            {"interaction_step": "verify", "speech": "Expected 12000, observed value is missing.", "expected_result": "12000", "observed_result": "missing"},
            {"interaction_step": "diagnose", "speech": "We inspect the DMS task and find a connection timeout."},
            {"interaction_step": "recover", "speech": "We fix the connection and resume the task."},
            {"interaction_step": "verify", "component_state": "verified", "speech": "Record 103 now matches.", "expected_result": "12000", "observed_result": "12000"},
            {"interaction_step": "complete", "component_state": "completed", "state_change": "pipeline status turns green", "speech": "The pipeline is complete."},
        ]}]
        report = validate(stages, 10.0, 60.0, {"nodes": [], "edges": [], "actions": []}, duration_measured=True, mismatch_scenario=True)
        self.assertTrue(report["render_allowed"], report["critical_failures"])
        self.assertEqual(report["checks"][7]["status"], "PASSED")

    def test_last_successful_record_label_is_not_pipeline_success(self):
        validate = load_pre_render_validator()
        stages = [{"start": 0.0, "end": 10.0, "sentence_cues": [
            {"interaction_step": "failure", "speech": "Record 103 is missing.", "observed_result": "Last successful record 102"},
            {"interaction_step": "diagnose", "speech": "We find the cause."},
            {"interaction_step": "recover", "speech": "We replay the missing batch."},
            {"interaction_step": "verify", "component_state": "verified", "expected_result": "5", "observed_result": "5", "speech": "The source and target now match."},
        ]}]
        report = validate(stages, 10.0, 60.0, {"nodes": [], "edges": [], "actions": []}, duration_measured=True, mismatch_scenario=True)
        check = next(item for item in report["checks"] if item["name"] == "Success follows verification")
        self.assertEqual(check["status"], "PASSED")

    def test_source_target_parser_reads_account_balance_values(self):
        parse_values = load_source_target_value_parser()
        prompt = "SOURCE:\nAccount 101 = ₹8,000\nTARGET:\nAccount 101 = ₹10,000\n"
        self.assertEqual(parse_values(prompt), {"source": "8000", "target": "10000"})

    def test_generic_failure_recovery_instructions_do_not_trigger_mismatch_gate(self):
        classify = load_mismatch_prompt_classifier()
        self.assertFalse(classify("Explain how an LLM works. Mention failure and recovery only as generic concepts."))
        self.assertTrue(classify("How to fix an AWS DMS to Snowflake data mismatch."))

    def test_repair_retry_preserves_original_prompt_for_quality_gates(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        generation = source.split("async def generate_short_prompt_async", 1)[1]
        self.assertIn("validation_prompt = str(_original_user_prompt or text_input).strip()", generation)
        self.assertIn("_original_user_prompt=validation_prompt", generation)
        self.assertIn("Do not add unrelated architecture or failure scenarios.", generation)
        self.assertIn("dms_snowflake_scenario = bool(", generation)
        self.assertIn("Return exactly {requested_scene_count} scenes", generation)
        self.assertIn("_pre_render_repair_attempt < 2", generation)
        self.assertIn("expected_result=5 and observed_result=5", generation)

    def test_pre_render_report_blocks_overlong_voice_and_false_recovery_order(self):
        validate = load_pre_render_validator()
        stages = [{"start": 0.0, "end": 61.0, "sentence_cues": [
            {"interaction_step": "failure", "speech": "Mismatch detected."},
            {"interaction_step": "recover", "speech": "We recover."},
            {"interaction_step": "verify", "speech": "Values match.", "expected_result": "8000", "observed_result": "8000"},
        ]}]
        graph = {"nodes": [], "edges": [], "actions": []}
        report = validate(stages, 61.0, 60.0, graph, duration_measured=True, mismatch_scenario=True)
        self.assertFalse(report["render_allowed"])
        self.assertIn("Narration duration limit", report["critical_failures"])
        self.assertIn("Failure → diagnosis → recovery → verification", report["critical_failures"])

    def test_pre_render_report_blocks_component_completion_before_verification(self):
        validate = load_pre_render_validator()
        stages = [{"start": 0.0, "end": 10.0, "sentence_cues": [
            {"interaction_step": "complete", "component_state": "completed", "speech": "The component is done."},
            {"interaction_step": "verify", "component_state": "verified", "speech": "The result matches.", "expected_result": "8", "observed_result": "8"},
        ]}]
        graph = {"nodes": [], "edges": [], "actions": []}
        report = validate(stages, 10.0, 60.0, graph, duration_measured=True)
        self.assertIn("Component completion gate", report["critical_failures"])

    def test_prompt_duration_is_capped_at_one_minute_and_results_are_labeled_simulated(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        renderer = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        self.assertIn("target_seconds = _extract_short_video_duration_limit(text_input, default=60.0)", source)
        self.assertIn('"result_mode": "simulated"', source)
        self.assertIn("ILLUSTRATIVE · NOT EXECUTED", renderer)
        self.assertIn("postRenderValidation", renderer)
        self.assertIn("Post-render quality gate failed", renderer)
        self.assertIn("preflight.render_allowed === false", renderer)
        self.assertIn('"component_state"', source)
        self.assertIn('"completed"', source)
        self.assertIn('interactionStep === "transfer" && isCurrentConnector && connectorProgress >= 1', renderer)
        self.assertIn('progress >= 0.08 && progress <= 0.92', renderer)

    def test_video_duration_range_enforces_requested_minimum_without_confusing_scene_times(self):
        parse_minimum = load_min_duration_parser()
        self.assertEqual(parse_minimum("Duration: 55–60 seconds"), 55)
        self.assertEqual(parse_minimum("SCENE 1 (0–6 seconds); Duration: 55-60 seconds"), 55)
        self.assertEqual(parse_minimum("Maximum duration: 60 seconds"), 0)
        validate = load_pre_render_validator()
        stages = [{"start": 0.0, "end": 49.3, "sentence_cues": []}]
        report = validate(stages, 49.3, 60.0, {"nodes": [], "edges": [], "actions": []}, duration_measured=True, min_duration=55.0)
        check = next(item for item in report["checks"] if item["name"] == "Narration duration limit")
        self.assertEqual(check["status"], "FAILED")
        self.assertIn("55.0–60.0s", check["detail"])
        self.assertIn("Narration duration limit", report["critical_failures"])

    def test_duration_parser_ignores_scene_lengths_and_caps_long_requests(self):
        parse_limit = load_duration_limit_parser()
        self.assertEqual(parse_limit("Scene 1: 0–4 seconds. Maximum duration: 60 seconds."), 60)
        self.assertEqual(parse_limit("Target duration: 45 sec; each step is 3 seconds."), 45)
        self.assertEqual(parse_limit("Maximum duration: 90 seconds."), 60)
        self.assertEqual(parse_limit("अधिकतम अवधि 30 सेकंड"), 30)

    def test_scene_count_parser_reads_explicit_and_numbered_scene_specs(self):
        parse_count = load_scene_count_parser()
        self.assertEqual(parse_count("Create exactly 6 distinct scenes."), 6)
        self.assertEqual(parse_count("SCENE 1 — HOOK; SCENE 2 — SOURCE; SCENE 9 — TAKEAWAY"), 9)
        self.assertIsNone(parse_count("Make a technical explainer."))

    def test_dms_snowflake_path_requires_an_intermediary(self):
        validate = load_pre_render_validator()
        stage = {"start": 0.0, "end": 10.0, "visual_data": {"elements": [], "connectors": [
            {"from": "AWS DMS", "to": "Amazon S3"},
            {"from": "Amazon S3", "to": "Snowpipe"},
            {"from": "Snowpipe", "to": "Snowflake"},
        ]}}
        graph = {"nodes": [], "edges": [], "actions": []}
        report = validate([stage], 10, 60, graph, duration_measured=True, dms_snowflake_scenario=True)
        route = next(item for item in report["checks"] if item["name"] == "DMS to Snowflake ingestion path")
        self.assertEqual(route["status"], "PASSED")

    def test_fallback_architecture_reveals_nodes_at_their_scene_not_upfront(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "architecture_animation.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        functions = [item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name in {"_slug", "_shape_for", "_layout_nodes", "_stage_for_time", "build_architecture_animation"}]
        namespace = {
            "re": re, "Any": Any, "defaultdict": defaultdict, "deque": deque,
            "NODE_SHAPES": {"database", "rectangle", "rounded_rectangle", "circle", "diamond", "hexagon", "cloud", "document", "table", "terminal", "dashboard"},
            "EDGE_STYLES": {"straight", "curved", "elbow", "bezier"}, "LAYOUTS": {"pipeline", "layered", "hierarchical", "tree"},
            "ACTION_ALIASES": {"reveal": "reveal_node", "enter": "reveal_node", "node_entrance": "reveal_node", "draw": "draw_edge", "draw_connector": "draw_edge", "connect": "draw_edge", "focus": "highlight_node", "highlight": "highlight_node", "data_flow": "packets", "move_data": "packets", "expand": "expand_node", "pulse": "pulse_node", "morph": "morph_node"},
        }
        exec(compile(ast.Module(body=functions, type_ignores=[]), "<progressive-architecture-test>", "exec"), namespace)
        graph = {"nodes": [{"id": label, "label": label} for label in ("Oracle", "AWS DMS", "Amazon S3", "Snowflake")], "edges": [
            {"id": "oracle-dms", "from": "Oracle", "to": "AWS DMS"},
            {"id": "dms-s3", "from": "AWS DMS", "to": "Amazon S3"},
            {"id": "s3-snowflake", "from": "Amazon S3", "to": "Snowflake"},
        ]}
        stages = [
            {"start": 0, "end": 10, "title": "Oracle source", "speech": "Oracle is our source."},
            {"start": 10, "end": 20, "title": "Replication", "speech": "AWS DMS captures changes."},
            {"start": 20, "end": 30, "title": "Target", "speech": "Amazon S3 and Snowflake receive the data."},
        ]
        animation = namespace["build_architecture_animation"](graph, stages, 30)
        reveal_times = {action["target_id"]: action["start"] for action in animation["actions"] if action["action"] == "reveal_node"}
        self.assertLess(reveal_times["oracle"], 10)
        self.assertGreaterEqual(reveal_times["aws-dms"], 10)
        self.assertGreaterEqual(reveal_times["amazon-s3"], 20)
        self.assertGreaterEqual(reveal_times["snowflake"], 20)

    def test_idempotency_payment_blueprint_is_local_12_scene_graph_animation(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        functions = [
            item for item in tree.body
            if isinstance(item, ast.FunctionDef)
            and item.name in {"_idempotency_payment_blueprint", "_idempotency_payment_graph"}
        ]
        namespace = {"Dict": Dict, "Any": Any, "List": List}
        exec(compile(ast.Module(body=functions, type_ignores=[]), "<idempotency-blueprint-test>", "exec"), namespace)
        blueprint = namespace["_idempotency_payment_blueprint"]()
        graph = blueprint["architecture_graph"]
        stages = blueprint["scenes"]
        nodes = {node["id"]: node for node in graph["nodes"]}
        edges = {edge["id"]: edge for edge in graph["edges"]}
        valid_targets = set(nodes) | set(edges)
        action_targets = {
            action["target_id"]
            for stage in stages
            for action in stage["diagram_actions"]
        }

        self.assertEqual(blueprint["storyboard_source"], "idempotency_payment_fallback")
        self.assertEqual(blueprint["max_duration_seconds"], 80)
        self.assertEqual(len(stages), 12)
        self.assertTrue(all(stage["user_authored_scene"] for stage in stages))
        self.assertTrue(all(action_targets <= valid_targets for stage in stages for action in stage["diagram_actions"]))
        self.assertTrue(set(nodes) <= action_targets)
        self.assertTrue(set(edges) <= action_targets)
        self.assertEqual(nodes["key-store"]["shape"], "database")
        self.assertEqual(nodes["provider"]["shape"], "cloud")
        self.assertIn("durable", nodes["key-store"]["description"].lower())
        self.assertIn("fingerprint", nodes["request-fingerprint"]["description"].lower())
        self.assertIn(("key-store", "order-service"), {(edge["from"], edge["to"]) for edge in edges.values()})
        self.assertIn("NOT CONFIRMED", stages[10]["title"])

        renderer_source = (PROJECT_ROOT / "app" / "video_maker" / "architecture_animation.py").read_text(encoding="utf-8")
        renderer_tree = ast.parse(renderer_source)
        renderer_functions = [
            item for item in renderer_tree.body
            if isinstance(item, ast.FunctionDef)
            and item.name in {"_slug", "_shape_for", "_layout_nodes", "_stage_for_time", "build_architecture_animation"}
        ]
        renderer_namespace = {
            "re": re, "Any": Any, "defaultdict": defaultdict, "deque": deque,
            "NODE_SHAPES": {"database", "rectangle", "rounded_rectangle", "circle", "diamond", "hexagon", "cloud", "document", "table", "terminal", "dashboard"},
            "EDGE_STYLES": {"straight", "curved", "elbow", "bezier"},
            "LAYOUTS": {"pipeline", "layered", "hierarchical", "tree"},
            "ACTION_ALIASES": {"reveal": "reveal_node", "enter": "reveal_node", "node_entrance": "reveal_node", "draw": "draw_edge", "draw_connector": "draw_edge", "connect": "draw_edge", "focus": "highlight_node", "highlight": "highlight_node", "data_flow": "packets", "move_data": "packets", "expand": "expand_node", "pulse": "pulse_node", "morph": "morph_node"},
        }
        exec(compile(ast.Module(body=renderer_functions, type_ignores=[]), "<idempotency-animation-test>", "exec"), renderer_namespace)
        duration = 80
        for index, stage in enumerate(stages):
            stage["start"] = duration * index / len(stages)
            stage["end"] = duration * (index + 1) / len(stages)
        animation = renderer_namespace["build_architecture_animation"](graph, stages, duration)
        self.assertEqual(len(animation["nodes"]), len(nodes))
        self.assertEqual(len(animation["edges"]), len(edges))
        self.assertTrue(all(action["stage_index"] in range(12) for action in animation["actions"]))
        self.assertTrue(all(0 <= node["x"] <= 1 and 0 <= node["y"] <= 1 for node in animation["nodes"]))

    def test_every_user_prompt_is_sent_to_the_model_without_topic_blueprints(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        generation = source.split("async def generate_short_prompt_async", 1)[1]
        self.assertIn("if len(text_input) > 8:", generation)
        self.assertIn("Input Prompt: {text_input}", generation)
        self.assertNotIn("_idempotency_payment_blueprint()", generation)
        self.assertNotIn("_parse_detailed_brief(text_input)", generation)
        self.assertIn("without a hardcoded storyboard fallback", generation)

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
        self.assertEqual(result["scenes"][0]["visual_data"]["layout"], "pipeline")
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

    def test_llm_brief_fallback_builds_accurate_interactive_pipeline(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        function = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == "_llm_fallback_graph")
        namespace = {"Dict": Dict, "Any": Any, "List": List}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "<llm-graph-fallback>", "exec"), namespace)
        stages = [{"title": f"Scene {index}"} for index in range(6)]
        graph = namespace["_llm_fallback_graph"](stages)
        nodes = {node["id"]: node for node in graph["nodes"]}
        self.assertEqual(graph["layout"], "pipeline")
        self.assertEqual(nodes["tokenizer"]["shape"], "hexagon")
        self.assertEqual(nodes["embeddings"]["shape"], "circle")
        self.assertEqual(nodes["next-token"]["shape"], "dashboard")
        self.assertIn("generated-response", nodes)
        edge_pairs = {(edge["from"], edge["to"]) for edge in graph["edges"]}
        self.assertIn(("generated-response", "transformer"), edge_pairs)
        valid_targets = set(nodes) | {edge["id"] for edge in graph["edges"]}
        self.assertTrue(all(action["target_id"] in valid_targets for stage in stages for action in stage["diagram_actions"]))
        self.assertTrue(all(stage["diagram_actions"] for stage in stages))

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

    def test_unmarked_educational_scene_seven_is_not_removed_by_id(self):
        stages = [{
            "id": 7,
            "title": "Quiz",
            "speech_en": "Which token should the model predict next?",
        }]
        calibrated, _, _ = load_duration_calibrator()(stages, 5, lang_key="en")
        self.assertEqual(len(calibrated), 1)
        self.assertEqual(calibrated[0]["title"], "Quiz")

    def test_browser_export_stays_local_and_saves_the_full_voice_synced_video(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        export = source.split("async function exportSqlShortVideo(", 1)[1].split("function downloadCurrentFrameAsPng", 1)[0]
        self.assertIn("window.showSaveFilePicker", export)
        self.assertIn('MediaRecorder.isTypeSupported(type)', export)
        self.assertIn('let outputExtension = mimeType ? "mp4" : "webm"', export)
        self.assertIn('mimeType = ["video/webm;codecs=vp9,opus"', export)
        self.assertIn("recorder.start(1000)", export)
        record_step = export.split("function recordStep(timestamp)", 1)[1]
        self.assertIn("frameCount - lastProgressFrame >= 15", record_step)
        self.assertLess(record_step.index("renderSqlShortFrame(t)"), record_step.index("updatePlayerScrubberUI(t)"))
        self.assertLess(record_step.index("frameCount = Math.min(totalFrames"), record_step.index("updatePlayerScrubberUI(t)"))
        self.assertIn("saveWritable.write(event.data)", export)
        self.assertNotIn("finalize_mp4", export)
        self.assertNotIn("FormData", export)
        self.assertIn("totalDuration = Math.max(1, totalDuration)", source)
        self.assertIn("(timestamp - startTime) / 1000", source)
        self.assertIn("videoBitsPerSecond: 9000000", source)
        self.assertIn("const exportFrameRate = 30", source)
        self.assertNotIn("stepBatch = totalDuration <= 15 ? 1 : 2", source)
        self.assertNotIn("Math.min(59.5, totalDuration)", source)
        self.assertIn("const videoTracks = canvas.captureStream(exportFrameRate).getVideoTracks()", export)
        self.assertIn("audioTracks", export)

    def test_universal_video_export_explains_local_render_and_api_generation_split(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_workspace.py").read_text(encoding="utf-8")
        self.assertIn("Video rendering आणि export या device वरच होतात", source)
        self.assertIn("Prompt, storyboard आणि voice NanoPro APIs मधून येतात", source)
        self.assertIn("LOCAL, VOICE SYNCED", source)
        self.assertIn("Check CPU · GPU · RAM · Storage", source)
        device_check = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        self.assertIn("function checkSqlVideoDevice()", device_check)
        self.assertIn("not physical free disk space", device_check)
        self.assertIn("browser download may buffer video chunks in RAM", device_check)

    def test_sentence_visuals_reveal_elements_and_connectors_as_each_cue_speaks(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        self.assertIn("const connectorProgress", source)
        self.assertIn("const elementProgress", source)
        self.assertIn("FOCUS · ${focusText}", source)
        self.assertIn("activeCue.speech_en || activeCue.speech", source)

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
        self.assertNotIn('"scale=1080:1920:flags=lanczos"', encoder)
        self.assertIn('"-threads", "1", "-filter_threads", "1", "-i"', encoder)
        self.assertIn('"-r", "30"', encoder)
        self.assertIn('"-b:v", "9M"', encoder)
        self.assertIn('"-b:a", "192k"', encoder)
        self.assertIn('"-preset", "ultrafast"', encoder)
        self.assertIn('"-threads", "1"', encoder)
        self.assertIn('"-filter_threads", "1"', encoder)
        self.assertIn('"-x264-params", "threads=1:lookahead-threads=1:rc-lookahead=0:sync-lookahead=0:bframes=0"', encoder)

    def test_universal_video_prompt_requests_topic_specific_visuals(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        self.assertIn("scene-specific composition", source.lower())
        self.assertIn("normalized x/y coordinates", source.lower())
        self.assertIn("do not impose an application template", source.lower())
        self.assertNotIn('"title": "Problem Hook"', source)
        self.assertIn('"content_type":"tech_topic"', source)
        self.assertIn("Every user prompt must pass through", source)
        self.assertIn('audio_url = ""', source)
        self.assertNotIn('audio_url = f"/audio/preset_sql_q1_second_highest_salary_', source)

    def test_short_form_narration_targets_under_sixty_seconds(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        self.assertIn("max_narration_words = max(24, int(target_seconds * 140 / 60))", source)
        self.assertIn("max_duration_seconds when requested", source)
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
        functions = [item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name in {"_validate_scene_visual_contract", "_infer_interaction_step", "_comparison_values_match"}]
        namespace = {"Any": Any, "Dict": Dict, "List": List, "re": re}
        exec(compile(ast.Module(body=functions, type_ignores=[]), "<scene-contract>", "exec"), namespace)
        return namespace["_validate_scene_visual_contract"]

    def test_accepts_prompt_specific_scene_and_native_code_overlay(self):
        scene = {
            "title": "Python list traversal",
            "speech": "The loop reads each item and adds it to the result.",
            "visual_prompt": "Close view of a Python list; the loop visits each value in order and updates the result list.",
            "continuity": "Same list and loop variable remain visible across this explanation.",
            "visual_data": {"composition": "Freeform loop visualization", "elements": [{"label": "List", "x": 0.5, "y": 0.5}], "connectors": []},
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
            "visual_data": {"composition": "Floating context glyphs", "elements": [{"label": "Context", "x": 0.5, "y": 0.5}], "connectors": []},
            "overlay_items": [
                {"kind": "text", "content": "context block", "x": 0.5, "y": 0.4},
                {"kind": "", "content": "retrieved chunks", "x": 0.4, "y": 0.6},
            ],
        }
        validated = self._validator()(scene)
        self.assertEqual([item["kind"] for item in validated["overlay_items"]], ["label", "label"])
        self.assertTrue(validated["visual_prompt"])
        self.assertTrue(validated["continuity"])

    def test_keeps_sentence_level_visual_cues_for_narration_sync(self):
        scene = {
            "title": "Retry safely",
            "speech": "The first request charges once. A retry reuses the same key.",
            "visual_data": {"elements": [{"label": "Request", "x": 0.5, "y": 0.4}]},
            "sentence_cues": [
                {"speech": "The first request charges once.", "speech_en": "The first request charges once.", "action": "reveal charge", "visual_data": {"elements": [{"label": "Charge", "x": 0.5, "y": 0.4}]}},
                {"speech": "A retry reuses the same key.", "speech_en": "A retry reuses the same key.", "action": "reuse key", "visual_data": {"elements": [{"label": "Same key", "x": 0.5, "y": 0.6}]}},
            ],
        }
        validated = self._validator()(scene)
        self.assertEqual(len(validated["sentence_cues"]), 2)
        self.assertEqual(validated["sentence_cues"][1]["visual_data"]["elements"][0]["label"], "Same key")
        self.assertEqual(validated["sentence_cues"][1]["interaction_step"], "introduce")

    def test_normalizes_sentence_cue_interaction_step(self):
        scene = {
            "title": "Transfer",
            "speech": "The packet moves to Snowflake.",
            "visual_data": {"elements": [{"label": "Pipeline", "x": 0.5, "y": 0.4}]},
            "sentence_cues": [{
                "speech": "The packet moves to Snowflake.",
                "interaction_step": "transfer",
                "emphasis": "DMS",
                "visual_data": {
                    "elements": [{"label": "DMS", "x": 0.35, "y": 0.4}, {"label": "Snowflake", "x": 0.7, "y": 0.6}],
                    "connectors": [{"from": "DMS", "to": "Snowflake"}, {"from": "Oracle", "to": "Unknown"}],
                },
            }],
        }
        validated = self._validator()(scene)
        self.assertEqual(validated["sentence_cues"][0]["interaction_step"], "transfer")
        self.assertEqual(validated["sentence_cues"][0]["visual_data"]["connectors"], [{"from": "DMS", "to": "Snowflake"}])

    def test_downgrades_transfer_without_a_valid_connection_path(self):
        scene = {
            "title": "Missing path",
            "speech": "The packet moves.",
            "visual_data": {"elements": [{"label": "DMS", "x": 0.3, "y": 0.4}]},
            "sentence_cues": [{
                "speech": "The packet moves.",
                "interaction_step": "transfer",
                "visual_data": {"elements": [{"label": "DMS", "x": 0.3, "y": 0.4}], "connectors": [{"from": "DMS", "to": "Missing"}]},
            }],
        }
        validated = self._validator()(scene)
        self.assertEqual(validated["sentence_cues"][0]["interaction_step"], "connect")
        self.assertEqual(validated["sentence_cues"][0]["visual_data"]["connectors"], [])

    def test_drops_malformed_sentence_visual_cues_without_rejecting_scene(self):
        scene = {
            "title": "Safe fallback",
            "speech": "The request is safe.",
            "visual_data": {"elements": [{"label": "Request", "x": 0.5, "y": 0.4}]},
            "sentence_cues": [{"speech": "The request is safe.", "visual_data": {"elements": [{"label": "Bad", "x": 8, "y": 8}]}}],
        }
        validated = self._validator()(scene)
        self.assertEqual(validated["sentence_cues"], [])

    def test_drops_sentence_cue_that_contains_multiple_sentences(self):
        scene = {
            "title": "Keep the narration sequence",
            "speech": "The event is captured. The target applies it.",
            "visual_data": {"elements": [{"label": "Pipeline", "x": 0.5, "y": 0.4}]},
            "sentence_cues": [{
                "speech": "The event is captured. The target applies it.",
                "visual_data": {"elements": [{"label": "Two steps", "x": 0.5, "y": 0.4}]},
            }],
        }
        validated = self._validator()(scene)
        self.assertEqual(validated["sentence_cues"], [])

    def test_rejects_overlay_outside_normalized_canvas(self):
        scene = {
            "title": "Photon",
            "speech": "A photon transfers energy to an electron.",
            "visual_prompt": "A photon strikes a silicon cell and releases an electron.",
            "continuity": "The same silicon cell stays in view.",
            "visual_data": {"composition": "Photon and electron", "elements": [{"label": "Photon", "x": 0.5, "y": 0.5}], "connectors": []},
            "overlay_items": [{"kind": "label", "content": "electron", "x": 1.3, "y": 0.5}],
        }
        with self.assertRaisesRegex(ValueError, "normalized canvas"):
            self._validator()(scene)


class PromptScenePlayerTests(unittest.TestCase):
    def test_generate_ui_queues_long_prompts_and_polls_job_progress(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        generation = source.split("async function generateSqlShortBlueprint()", 1)[1].split("function ", 1)[0]
        self.assertIn('async function generateSqlShortBlueprintJob(payload, statusEl)', source)
        self.assertIn('/api/sql_video/generate_prompt_job', source)
        self.assertIn('/api/sql_video/generation_jobs/', source)
        self.assertIn('const data = await generateSqlShortBlueprintJob(', generation)
        self.assertIn('job.result_data', source)
        self.assertIn('job.error_message', source)
        self.assertIn('statusEl.textContent = `Working on your prompt', source)
        self.assertNotIn('/api/sql_video/generate_prompt"', generation)
        self.assertIn('sqlVideoGenerationStatus', source)

    def test_architecture_renderer_uses_independent_vector_components(self):
        renderer = (PROJECT_ROOT / "app" / "ui" / "architecture_animation_renderer.py").read_text(encoding="utf-8")
        self.assertIn("function drawTechnicalArchitectureGraph(", renderer)
        self.assertIn("function architectureGraphForScene(", renderer)
        self.assertIn("stage.diagram_actions", renderer)
        self.assertIn("architectureStrokeProgress", renderer)
        self.assertIn('"packets"', renderer)
        for shape in ("database", "diamond", "hexagon", "cloud", "document", "terminal", "dashboard"):
            self.assertIn(f'shape === "{shape}"', renderer)
        self.assertNotIn("drawImage(", renderer)

    def test_video_generation_survives_empty_server_responses(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        self.assertIn("async function readVideoJsonResponse", source)
        self.assertIn("await readVideoJsonResponse(queuedRes)", source)
        self.assertIn("await readVideoJsonResponse(pollRes)", source)
        self.assertIn("empty: true", source)

    def test_narration_loader_accepts_audio_ready_at_timeout(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        loader = source.split("function loadSqlNarration(", 1)[1].split("function downloadVoiceoverMp3(", 1)[0]
        self.assertIn("audioEl.readyState >= 3 && !audioEl.error", loader)
        self.assertIn("}, 60000);", loader)

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
        self.assertIn("maxDur, activeStage)", frame)
        self.assertIn("const subPillY = H - 458", frame)
        self.assertIn("activeStage.caption", frame)
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
        generation = source.split("async def generate_short_prompt_async", 1)[1]
        self.assertNotIn('matched["storyboard_source"] = "local_fallback"', generation)

    def test_storyboard_prompt_requests_native_language_narration(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        self.assertIn("Marathi in Devanagari script", source)
        self.assertIn("Write Hindi in Devanagari script", source)
        self.assertIn("authentic, conversational wording, not Romanized Marathi", source)
        self.assertIn("explain each technical term in plain language", source)
        self.assertIn("Never ask the viewer to pause, type, answer, or wait", source)
        self.assertIn("Vary composition when the idea changes", source)
        self.assertIn("Select a visual_data layout that matches", source)

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

    def test_detailed_brief_parses_short_scene_captions(self):
        brief = '''
SCENE 1 (0-8 seconds): HOOK
Voiceover: "Orders are arriving quickly."
Caption: "Hazaaron orders ek saath"
**Diagram and Animation**: Show the order feed and busy server.
---
SCENE 2 (8-16 seconds): ROUTE
Voiceover: "The proxy forwards the order request."
Caption: "Request sahi backend par"
**Diagram and Animation**: Show a client request flowing to a backend service.
'''
        parsed = load_detailed_brief_parser()(brief)
        self.assertEqual(parsed["scenes"][0]["caption"], "Hazaaron orders ek saath")

    def test_api_gateway_character_brief_keeps_all_scenes_and_uses_spatial_layouts(self):
        brief = """
Scene 1 (0:00-0:08) - Hook
- Phone, glowing gateway and eight service icons arranged as a constellation, not boxes.
- Arjun (left): "How does the request reach the right service?"
- Riya (right): "The gateway is the single entry point."
Scene 2 (0:08-0:15) - Direct calls
- Curved direct calls from the phone to Restaurant, Order and Payment services.
- Riya: "What if clients call every service directly?"
- Arjun: "Each address and policy must be handled separately."
Scene 3 (0:15-0:22) - Gateway introduction
- A glowing API Gateway node becomes the single entrance.
- Riya: "The client talks to the API Gateway."
Scene 4 (0:22-0:30) - Order flow
- An animated request path moves from the app through the gateway to Order then Payment.
- Arjun: "Does it route to the right service?"
- Riya: "Yes, that is its job."
Scene 5 (0:30-0:40) - Gateway responsibilities
- Shield, speedometer and document glyphs orbit the gateway: authentication, rate limiting and monitoring.
- Riya: "These are common gateway responsibilities."
Scene 6 (0:40-0:50) - Configuration
- Split-screen gateway icons compare authentication, rate limit and monitoring status, without cards.
- Riya: "Features depend on the tool and configuration."
- Arjun: "Can we configure them ourselves?"
Scene 7 (0:50-0:58) - Failure
- The gateway freezes and turns red; downstream services stay healthy but receive no requests.
- Arjun: "What if the gateway goes down?"
- Riya: "High availability is the next step."
Scene 8 (0:58-1:05) - Closing
- Character close-up, high availability question, clean end card held two seconds.
- Riya: "Watch part two and follow."
"""
        parsed = load_detailed_brief_parser()(brief)
        self.assertEqual(len(parsed["scenes"]), 8)
        self.assertEqual(parsed["duration"], 65)
        self.assertEqual(parsed["scenes"][0]["title"], "Hook")
        self.assertTrue(all(scene["visual_data"]["layout"] == "spatial" for scene in parsed["scenes"]))
        self.assertLess(len(parsed["scenes"][-1]["speech"]), 200)
        self.assertIn("How does the request reach the right service?", parsed["scenes"][0]["speech"])
        self.assertIn("The gateway is the single entry point.", parsed["scenes"][0]["speech"])
        self.assertIn("Phone, glowing gateway", parsed["scenes"][0]["visual_data"]["visual"])

    def test_h264_export_matches_reel_delivery_spec(self):
        renderer = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        server = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")
        conversion = server.split("def _run_sql_video_mp4_conversion(", 1)[1].split("@app.post(\"/api/sql_video/finalize_mp4\")", 1)[0]
        self.assertIn("const exportFrameRate = 30", renderer)
        self.assertIn("videoBitsPerSecond: 9000000", renderer)
        self.assertIn("audioBitsPerSecond: 192000", renderer)
        self.assertNotIn('"scale=1080:1920:flags=lanczos"', conversion)
        self.assertIn('"-threads", "1", "-filter_threads", "1", "-i"', conversion)
        self.assertIn('"-r", "30"', conversion)
        self.assertIn('"-b:v", "9M"', conversion)
        self.assertIn('"-b:a", "192k"', conversion)

    def test_brief_scene_designs_exist_in_the_renderer(self):
        js = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        for name in ("drawBriefTitle", "drawBriefSplit", "drawBriefPipeline", "drawBriefTable", "drawBriefChips", "drawBriefWarning", "drawBriefCards"):
            self.assertIn(f"function {name}(", js)
        self.assertIn("function drawPromptTextOverlays(", js)
        self.assertIn("drawPromptTextOverlays(ctx, W, H, stage, visual, progress, cue)", js)

    def test_scene_visuals_use_ai_authored_compositions_before_graph_fallback(self):
        js = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        self.assertIn("function drawPromptVisualPlan(", js)
        self.assertIn("const stageVisual = activeStage?.visual_data || {}", js)
        self.assertIn("const authoredVisual = {", js)
        self.assertIn("...(activeCue?.visual_data || {})", js)
        self.assertIn("drawPromptVisualPlan(ctx, W, H, activeStage, stageProg", js)
        self.assertIn("Keep the topic-specific legacy animation only for older scenes", js)

    def test_prompt_visuals_and_captions_follow_authored_scene_cues(self):
        js = (PROJECT_ROOT / "app" / "ui" / "sql_video_js.py").read_text(encoding="utf-8")
        visual = js.split("function drawPromptVisualPlan(", 1)[1].split("function renderArchitectureScene(", 1)[0]
        subtitles = js.split("function drawKineticSubtitles(", 1)[1].split("function renderSqlShortFrame(", 1)[0]
        self.assertNotIn("ctx.arc(0, 0", visual)
        self.assertIn("stage._promptVisualBackdrops[cueIndex] = backdrop", visual)
        self.assertIn("sqlShortState.isExporting ? 0 : 20", visual)
        self.assertIn('String(item.label).replace(/[_-]+/g, " ")', visual)
        self.assertIn("const radius = elements.length <= 3 ? 78 : elements.length <= 6 ? 68 : 42", visual)
        self.assertIn('interactionStep === "transfer"', visual)
        self.assertIn("const packetX =", visual)
        self.assertIn('ctx.lineTo(-25, -14)', visual)
        self.assertIn("drawCueDetailPanel(ctx, W, H, cue, progress, time, interactionStep)", visual)
        self.assertIn("historyLabels", visual)
        self.assertIn("revealedConnectorKeys", visual)
        self.assertIn('ctx.ellipse(0, 0, 194, 174', visual)
        self.assertIn('CORE · LIVE TELEMETRY', visual)
        self.assertIn("Math.max(470, Math.min(H - 1040", visual)
        self.assertIn("activeCue?.speech", subtitles)
        self.assertIn("cueProgress * words.length", subtitles)
        self.assertIn('ctx.font = "bold 48px', subtitles)
        self.assertIn("drawCinematicSceneHeadline(ctx, W, H, activeStage", js)
        self.assertIn("drawKineticSubtitles(ctx, W, H, p, activeStage, stageProg, t, activeCue, cueProgress)", js)

    def test_architecture_graph_uses_vertical_safe_margins(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "architecture_animation.py").read_text(encoding="utf-8")
        self.assertIn('"x": 0.5', source)
        self.assertIn('"y": 0.16 if level_count == 1 else 0.16 + 0.59 * layer_index / (level_count - 1)', source)
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
        generation = source.split("async def generate_short_prompt_async", 1)[1]
        self.assertIn("Input Prompt: {text_input}", generation)
        self.assertIn("visual_data authored for that scene", generation)
        self.assertNotIn("_architecture_from_detailed_brief(text_input, stages)", generation)
        self.assertNotIn("if matched.get(\"storyboard_source\") == \"detailed_brief\":", generation)
        self.assertIn("Choose the number of educational scenes to fit the prompt's complexity", source)


if __name__ == "__main__":
    unittest.main()
