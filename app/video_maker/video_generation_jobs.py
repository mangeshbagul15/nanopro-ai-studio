"""Async orchestration helpers for long-running prompt-driven video generation."""

import asyncio
from typing import Any, Callable


async def _execute_generation(job_id, manager, question, difficulty, language, mode, public_base_url, blueprint_factory, assets_factory, generation_pattern="hybrid", selected_model="wan_21"):
    try:
        manager.update_job_stage(job_id, "storyboard", 10, status="running", tool_used="storyboard-model")
        blueprint = await blueprint_factory(
            topic_or_question=question,
            difficulty=difficulty,
            language=language,
            mode=mode,
            generation_pattern=generation_pattern,
            selected_model=selected_model,
        )
        if not isinstance(blueprint, dict) or blueprint.get("status") == "error":
            raise RuntimeError((blueprint or {}).get("message", "NanoPro could not create the video storyboard."))
        scenes = blueprint.get("stages") or blueprint.get("scenes") or []
        if not scenes:
            raise RuntimeError("NanoPro created an empty storyboard; no video was produced.")

        manager.update_job_stage(job_id, "audio_synced", 22, status="running", tool_used="narration-and-scene-timing")
        if assets_factory is None:
            # Diagram-only videos: no image provider is used at all, so the render is
            # fast, deterministic and cannot exhaust the free-tier memory.
            manager.update_job_stage(job_id, "diagram_layout", 70, status="running", tool_used="canvas-architecture-diagram")
            scene_assets = []
        else:
            manager.update_job_stage(job_id, "scene_images", 25, status="running", tool_used="prompt-specific-image-generation")

            def report(stage, progress):
                manager.update_job_stage(job_id, str(stage), 25 + int(max(0, min(100, progress)) * 0.6), status="running")

            scene_assets = await assets_factory(scenes, job_id, public_base_url, report)
            if len(scene_assets) != len(scenes):
                raise RuntimeError("Scene asset generation returned an incomplete video; retry the generation.")
        manager.update_job_stage(job_id, "composition_ready", 95, status="running", tool_used="9:16-canvas-composition")
        blueprint["scene_assets"] = scene_assets
        manager.set_job_completed(job_id, blueprint)
    except Exception as exc:
        manager.set_job_failed(job_id, str(exc))


def queue_generation_job(
    manager,
    question: str,
    public_base_url: str,
    blueprint_factory: Callable[..., Any],
    assets_factory: Callable[..., Any],
    difficulty: str = "Medium",
    language: str = "mr",
    mode: str = "faang_drill",
    generation_pattern: str = "hybrid",
    selected_model: str = "wan_21",
) -> dict:
    job_id = manager.create_job(
        prompt=question,
        agent_id="video_agent",
        plan=["storyboard", "voiceover_sync", "diagram_layout", "composition"],
    )
    coroutine = _execute_generation(
        job_id, manager, question, difficulty, language, mode, public_base_url, blueprint_factory, assets_factory, generation_pattern, selected_model
    )
    asyncio.get_running_loop().call_soon(asyncio.create_task, coroutine)
    return {"status": "queued", "job_id": job_id}


def get_generation_job(manager, job_id: str) -> dict | None:
    job = manager.get_job(job_id)
    if not job:
        return None
    return {
        "job_id": job_id,
        "status": job.get("status"),
        "stage": job.get("stage"),
        "progress": job.get("progress", 0),
        "result_data": job.get("result_data") or {},
        "error_message": job.get("error_message"),
    }
