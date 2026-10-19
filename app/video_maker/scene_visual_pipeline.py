"""Prompt-specific portrait scene imagery and optional image-to-video motion."""

from __future__ import annotations

import asyncio
import gc
import hashlib
import urllib.request
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

from app.core.config import BASE_DIR
from app.agents.image_agent import image_creation_agent
from app.core.runway_video import runway_video


def _normalize_portrait(source: Path, destination: Path) -> tuple[int, int]:
    try:
        from PIL import Image, ImageFilter, ImageOps
    except ImportError as exc:
        raise RuntimeError("Pillow is required to normalize generated scene images.") from exc
    with Image.open(source) as image:
        if image.format == "JPEG" and max(image.size) > 1400:
            # Have libjpeg decode straight to a smaller RGB buffer. A 2K provider
            # frame would otherwise materialise a ~25 MB bitmap per scene, which is
            # what pushed the 512 MB Render instance into a restart.
            image.draft("RGB", (1080, 1920))
        fitted = ImageOps.fit(
            image.convert("RGB"),
            (1080, 1920),
            # Bias slightly above centre: generated keyframes usually place the
            # subject in the upper half, so a dead-centre crop decapitates them.
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.44),
        )
    # LANCZOS resampling softens micro-detail; restore local contrast so the frame
    # still reads as sharp footage once the video is re-encoded to H.264.
    fitted = fitted.filter(ImageFilter.UnsharpMask(radius=1.4, percent=105, threshold=3))
    destination.parent.mkdir(parents=True, exist_ok=True)
    fitted.save(destination, format="JPEG", quality=95, optimize=True, subsampling=0)
    return 1080, 1920


async def _animate_if_available(asset_url: str, prompt: str, duration: int, public_base_url: str):
    parsed = urlparse(public_base_url)
    if not runway_video.is_available() or parsed.scheme != "https" or parsed.hostname in {"localhost", "127.0.0.1"}:
        return None
    try:
        task = await asyncio.to_thread(
            runway_video.create_image_to_video,
            image_url=asset_url,
            prompt_text=f"Animate the existing scene naturally: {prompt}",
            ratio="720:1280",
            duration=max(5, min(10, round(duration or 5))),
            model="gen4_turbo",
        )
        task_id = task.get("task_id")
        if not task_id:
            return None
        for _ in range(30):
            status = await asyncio.to_thread(runway_video.get_task_status, task_id)
            state = str(status.get("status", "")).lower()
            if state in {"succeeded", "success", "completed"}:
                return status.get("video_url") or status.get("output_url")
            if state in {"failed", "error", "cancelled"}:
                return None
            await asyncio.sleep(2)
    except Exception:
        # Keep the exact topic-specific generated image; motion may fall back to canvas camera movement.
        return None
    return None


async def _cache_runway_video(remote_url: str | None, destination: Path, public_base_url: str) -> str | None:
    if not remote_url:
        return None
    try:
        request = urllib.request.Request(remote_url, headers={"User-Agent": "NanoProAI/1.0"})
        with await asyncio.to_thread(urllib.request.urlopen, request, timeout=90) as response:
            content = await asyncio.to_thread(response.read)
        if len(content) < 1024:
            return None
        local_path = destination.with_suffix(".mp4")
        temp_path = local_path.with_suffix(".mp4.part")
        temp_path.write_bytes(content)
        temp_path.replace(local_path)
        return f"{public_base_url.rstrip('/')}/assets/video_scenes/{local_path.name}"
    except Exception:
        return None


async def generate_scene_assets(
    scenes: list[dict],
    job_id: str,
    public_base_url: str,
    progress_callback: Callable[[str, int], None],
) -> list[dict]:
    """Create one cached 9:16 model-generated keyframe per storyboard scene."""
    asset_root = Path(BASE_DIR) / "data" / "assets" / "video_scenes"
    asset_root.mkdir(parents=True, exist_ok=True)
    # One scene image at a time keeps peak RSS inside the 512 MB free Render tier.
    # Raise this only when the instance genuinely has memory headroom.
    semaphore = asyncio.Semaphore(1)
    progress_lock = asyncio.Lock()
    completed = 0

    async def build(index: int, scene: dict) -> dict:
        nonlocal completed
        visual_prompt = str(scene.get("visual_prompt", "")).strip()
        title = str(scene.get("title") or f"Scene {index + 1}")
        if not visual_prompt:
            raise RuntimeError(f"Could not create scene {index + 1} ({title}): visual prompt is missing.")
        cache_material = "|".join((
            visual_prompt,
            str(scene.get("continuity", "")),
            str(scene.get("speech", "")),
            "flux|1080x1920|strict|portrait|cinematic-v3",
        ))
        prompt_hash = hashlib.sha256(cache_material.encode("utf-8")).hexdigest()
        filename = f"{prompt_hash}.jpg"
        destination = asset_root / filename
        async with semaphore:
            if not destination.exists():
                last_error = None
                for _ in range(2):
                    try:
                        generated = await asyncio.to_thread(
                            image_creation_agent.generate_image,
                            visual_prompt,
                            style="modern_tech",
                            width=1080,
                            height=1920,
                            allow_local_fallback=False,
                            preserve_prompt=True,
                        )
                        source = Path(generated["file_path"])
                        if not source.is_file():
                            raise RuntimeError("Image provider returned no local image file.")
                        _normalize_portrait(source, destination)
                        # Release the decoded provider bitmap before the next scene.
                        gc.collect()
                        last_error = None
                        break
                    except Exception as exc:
                        last_error = exc
                if last_error:
                    raise RuntimeError(f"Could not create scene {index + 1} ({title}): {last_error}") from last_error
            image_url = f"{public_base_url.rstrip('/')}/assets/video_scenes/{filename}"
            duration = float(scene.get("duration", scene.get("duration_seconds", 5)) or 5)
            progress_callback(f"image_motion:{index + 1}/{len(scenes)}", int(completed * 100 / max(1, len(scenes))))
            remote_video_url = await _animate_if_available(image_url, visual_prompt, int(duration), public_base_url)
            video_url = await _cache_runway_video(remote_video_url, destination, public_base_url)
            async with progress_lock:
                completed += 1
                progress_callback(f"scene_images:{completed}/{len(scenes)}", int(completed * 100 / max(1, len(scenes))))
            return {
                "scene_id": str(scene.get("id") or index),
                "image_url": image_url,
                "video_url": video_url,
                "provider": "runway-gen4-turbo" if video_url else "prompt-specific-ai-image",
                "start": float(scene.get("start", 0) or 0),
                "end": float(scene.get("end", (scene.get("start", 0) or 0) + duration) or 0),
                "duration": duration,
                "prompt_hash": prompt_hash,
                "width": 1080,
                "height": 1920,
            }

    return await asyncio.gather(*(build(index, scene) for index, scene in enumerate(scenes)))
