import asyncio
import importlib.util
import tempfile
import unittest
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

class SceneVisualPipelineTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source.png"
        from PIL import Image
        Image.new("RGB", (400, 300), "#336699").save(self.source)

    async def _run(self, scenes, image_fn, runway=None, base="https://studio.example"):
        fake_agent = SimpleNamespace(generate_image=image_fn)
        fake_runway = runway or SimpleNamespace(is_available=lambda: False)
        modules = {
            "app": SimpleNamespace(__path__=[]),
            "app.core": SimpleNamespace(__path__=[]),
            "app.core.config": SimpleNamespace(BASE_DIR=self.root),
            "app.agents": SimpleNamespace(__path__=[]),
            "app.agents.image_agent": SimpleNamespace(image_creation_agent=fake_agent),
            "app.core.runway_video": SimpleNamespace(runway_video=fake_runway),
        }
        with patch.dict(sys.modules, modules):
            path = Path(__file__).resolve().parents[1] / "video_maker" / "scene_visual_pipeline.py"
            spec = importlib.util.spec_from_file_location("scene_visual_pipeline_tested", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return await module.generate_scene_assets(scenes, "job-test", base, lambda *_: None)

    async def test_generates_distinct_cached_keyframes_per_visual_prompt(self):
        calls = []
        def image(prompt, **kwargs):
            calls.append(prompt)
            return {"file_path": str(self.source), "provider": "fake", "source_url": "https://img.example/key.png"}
        scenes = [
            {"title": "Solar", "visual_prompt": "A solar panel converts sunlight", "speech": "Solar works", "continuity": "one sun"},
            {"title": "SQL", "visual_prompt": "A database query filters rows", "speech": "SQL filters", "continuity": "one table"},
        ]
        result = await self._run(scenes, image)
        self.assertEqual(len(result), 2)
        self.assertNotEqual(result[0]["prompt_hash"], result[1]["prompt_hash"])
        self.assertEqual(len(calls), 2)
        self.assertEqual((result[0]["width"], result[0]["height"]), (1080, 1920))
        await self._run(scenes, image)
        self.assertEqual(len(calls), 2)

    async def test_runway_failure_keeps_same_scene_image(self):
        source_url = "https://studio.example/assets/video_scenes/keyframe.png"
        def image(prompt, **kwargs):
            return {"file_path": str(self.source), "provider": "fake", "source_url": "https://img.example/key.png"}
        runway = SimpleNamespace(
            is_available=lambda: True,
            create_image_to_video=lambda **kwargs: (_ for _ in ()).throw(RuntimeError("quota")),
        )
        result = await self._run([{"title": "Solar", "visual_prompt": "A panel tilts toward sun", "speech": "Solar", "continuity": "panel"}], image, runway)
        self.assertIsNone(result[0]["video_url"])
        self.assertIn("image_url", result[0])

    async def test_image_failure_stops_without_stock_substitution(self):
        def image(*args, **kwargs):
            raise RuntimeError("provider offline")
        with self.assertRaisesRegex(RuntimeError, "scene 1.*Solar"):
            await self._run([{"title": "Solar", "visual_prompt": "A panel converts light", "speech": "Solar", "continuity": "panel"}], image)

    async def test_solar_and_coding_prompts_produce_different_scene_assets(self):
        prompts = []
        def image(prompt, **kwargs):
            prompts.append(prompt)
            return {"file_path": str(self.source), "provider": "fake", "source_url": "https://img.example/key.png"}
        solar = await self._run([{"id": 1, "title": "Solar", "visual_prompt": "Photons strike silicon cells and release electrons", "speech": "Solar"}], image)
        coding = await self._run([{"id": 1, "title": "Python", "visual_prompt": "A Python loop reads list values and appends results", "speech": "Coding"}], image)
        self.assertIn("silicon cells", prompts[0])
        self.assertIn("Python loop", prompts[1])
        self.assertNotEqual(solar[0]["prompt_hash"], coding[0]["prompt_hash"])
        self.assertNotEqual(solar[0]["image_url"], coding[0]["image_url"])
        from PIL import Image
        with Image.open(self.root / "data" / "assets" / "video_scenes" / (solar[0]["prompt_hash"] + ".jpg")) as image_file:
            self.assertEqual(image_file.size, (1080, 1920))

    async def test_generated_scene_assets_cover_the_complete_narration_timeline(self):
        def image(prompt, **kwargs):
            return {"file_path": str(self.source), "provider": "fake"}
        scenes = [
            {"id": 1, "title": "Hook", "visual_prompt": "Solar panel in sunlight", "start": 0, "end": 8.5, "duration": 8.5},
            {"id": 2, "title": "Mechanism", "visual_prompt": "Electrons move through a circuit", "start": 8.5, "end": 25, "duration": 16.5},
            {"id": 3, "title": "Result", "visual_prompt": "Electricity powers a home", "start": 25, "end": 49.7, "duration": 24.7},
        ]
        result = await self._run(scenes, image)
        self.assertEqual(sum(asset["duration"] for asset in result), 49.7)
        self.assertEqual(result[-1]["end"], 49.7)


if __name__ == "__main__":
    unittest.main()
