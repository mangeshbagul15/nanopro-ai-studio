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

    def test_universal_video_prompt_requests_topic_specific_visuals(self):
        source = (PROJECT_ROOT / "app" / "video_maker" / "sql_short_engine.py").read_text(encoding="utf-8")
        self.assertIn('"visual_description"', source)
        self.assertIn('"entities"', source)
        self.assertIn("avoid repeating the same composition", source.lower())
        self.assertNotIn('"title": "Problem Hook"', source)
        self.assertIn("Every user prompt must pass through", source)
        self.assertIn('audio_url = ""', source)
        self.assertNotIn('audio_url = f"/audio/preset_sql_q1_second_highest_salary_', source)

    def test_video_maker_uses_strict_portrait_preview_and_no_short_test_export(self):
        source = (PROJECT_ROOT / "app" / "ui" / "sql_video_workspace.py").read_text(encoding="utf-8")
        self.assertIn('aspect-ratio: 9 / 16', source)
        self.assertIn('width="1080" height="1920"', source)
        self.assertNotIn('exportSqlShortVideo(15)', source)


if __name__ == "__main__":
    unittest.main()
