import asyncio
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


def load_job_helpers():
    root = Path(__file__).resolve().parents[1]
    modules = {"app": SimpleNamespace(__path__=[]), "app.video_maker": SimpleNamespace(__path__=[])}
    with patch.dict(sys.modules, modules):
        path = root / "video_maker" / "video_generation_jobs.py"
        spec = importlib.util.spec_from_file_location("video_generation_jobs_tested", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


class FakeTaskManager:
    def __init__(self):
        self.jobs = {}
    def create_job(self, prompt, agent_id="manager", plan=None):
        self.jobs["job-1"] = {"id": "job-1", "status": "queued", "stage": "initialized", "progress": 0, "result_data": {}, "error_message": None}
        return "job-1"
    def update_job_stage(self, job_id, stage, progress=None, status=None, tool_used=None):
        self.jobs[job_id].update(stage=stage, progress=progress, status=status or "running")
    def set_job_completed(self, job_id, result_data):
        self.jobs[job_id].update(status="done", stage="completed", progress=100, result_data=result_data)
    def set_job_failed(self, job_id, error_msg):
        self.jobs[job_id].update(status="error", stage="failed", error_message=error_msg)
    def get_job(self, job_id):
        return self.jobs.get(job_id)


class GenerationJobTests(unittest.IsolatedAsyncioTestCase):
    async def test_diagram_only_job_skips_image_generation(self):
        helper = load_job_helpers()
        manager = FakeTaskManager()
        async def blueprint(**kwargs):
            return {"status": "success", "duration": 50, "stages": [{"title": "Source"}], "architecture_graph": {"nodes": []}}
        helper.queue_generation_job(manager, "Oracle to Snowflake", "https://studio.example", blueprint, None)
        await asyncio.sleep(0.02)
        job = helper.get_generation_job(manager, "job-1")
        self.assertEqual(job["status"], "done")
        self.assertEqual(job["result_data"]["scene_assets"], [])
        self.assertEqual(job["stage"], "completed")

    async def test_generation_job_returns_id_and_polls_progress(self):
        helper = load_job_helpers()
        manager = FakeTaskManager()
        gate = asyncio.Event()
        async def blueprint(**kwargs):
            await gate.wait()
            return {"status": "success", "stages": [{"title": "Solar", "visual_prompt": "Solar panels convert light"}]}
        async def assets(*args, **kwargs):
            return [{"scene_id": "1", "image_url": "/assets/scene.jpg"}]
        queued = helper.queue_generation_job(manager, "Solar panel", "https://studio.example", blueprint, assets)
        self.assertEqual(queued, {"status": "queued", "job_id": "job-1"})
        self.assertEqual(helper.get_generation_job(manager, "job-1")["status"], "queued")
        gate.set()
        await asyncio.sleep(0.02)
        self.assertEqual(manager.jobs["job-1"]["status"], "done")

    async def test_generation_job_returns_complete_blueprint_and_assets(self):
        helper = load_job_helpers()
        manager = FakeTaskManager()
        async def blueprint(**kwargs):
            return {"status": "success", "duration": 43, "stages": [{"id": 1, "title": "Solar", "visual_prompt": "Solar panels convert light"}]}
        async def assets(scenes, job_id, base, callback):
            callback("scene_images:1/1", 100)
            return [{"scene_id": "1", "image_url": "/assets/solar.jpg"}]
        helper.queue_generation_job(manager, "Solar panel", "https://studio.example", blueprint, assets)
        await asyncio.sleep(0.02)
        job = helper.get_generation_job(manager, "job-1")
        self.assertEqual(job["status"], "done")
        self.assertEqual(job["result_data"]["scene_assets"][0]["image_url"], "/assets/solar.jpg")
        self.assertEqual(job["result_data"]["duration"], 43)

    async def test_generation_job_reports_scene_failure(self):
        helper = load_job_helpers()
        manager = FakeTaskManager()
        async def blueprint(**kwargs):
            return {"status": "success", "stages": [{"id": 1, "title": "Solar", "visual_prompt": "Solar panels convert light"}]}
        async def assets(*args, **kwargs):
            raise RuntimeError("Could not create scene 1 (Solar)")
        helper.queue_generation_job(manager, "Solar panel", "https://studio.example", blueprint, assets)
        await asyncio.sleep(0.02)
        job = helper.get_generation_job(manager, "job-1")
        self.assertEqual(job["status"], "error")
        self.assertIn("scene 1", job["error_message"])
        self.assertFalse(job["result_data"])


if __name__ == "__main__":
    unittest.main()
