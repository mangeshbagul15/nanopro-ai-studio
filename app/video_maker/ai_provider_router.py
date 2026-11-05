"""Credit-aware routing for Reel scene clips and narration.

Each generation probes configured premium providers (key present + credits left)
and uses the best available one, falling back to free engines otherwise.
Probe results are cached briefly so one Reel does not re-query every scene.
"""

import asyncio
import json
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from app.core.logger import log_event

_PROBE_TTL_S = 120.0
_probe_cache: Dict[str, Any] = {"at": 0.0, "data": None}


def _luma_credits(api_key: str) -> Optional[float]:
    req = urllib.request.Request(
        "https://api.lumalabs.ai/dream-machine/v1/credits",
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return float(data.get("credit_balance", 0) or 0)
    except Exception:
        return None


def _probe_sync() -> Dict[str, Dict[str, Any]]:
    status: Dict[str, Dict[str, Any]] = {}

    try:
        from app.core.luma_video import luma_video_engine
        key = luma_video_engine._resolve_api_key()
        if key:
            credits = _luma_credits(key)
            status["luma"] = {
                "configured": True,
                "credits": credits,
                "usable": credits is None or credits > 0,
            }
        else:
            status["luma"] = {"configured": False, "usable": False}
    except Exception as e:
        status["luma"] = {"configured": False, "usable": False, "error": str(e)}

    try:
        from app.core.runway_video import runway_video
        if runway_video.is_available():
            org = runway_video.get_organization_info(token_idx=0)
            credits = float(org.get("credit_balance", 0) or 0) if org.get("status") == "success" else 0.0
            status["runway"] = {
                "configured": True,
                "credits": credits,
                "tier": org.get("tier"),
                "usable": credits > 0,
            }
        else:
            status["runway"] = {"configured": False, "usable": False}
    except Exception as e:
        status["runway"] = {"configured": False, "usable": False, "error": str(e)}

    try:
        from app.core.elevenlabs_voice import elevenlabs_voice
        if elevenlabs_voice.is_available():
            info = elevenlabs_voice.get_user_info()
            remaining = int(info.get("remaining_credits", 0) or 0) if info.get("status") == "success" else 0
            status["elevenlabs"] = {
                "configured": True,
                "credits": remaining,
                "tier": info.get("tier"),
                "usable": remaining > 0,
            }
        else:
            status["elevenlabs"] = {"configured": False, "usable": False}
    except Exception as e:
        status["elevenlabs"] = {"configured": False, "usable": False, "error": str(e)}

    return status


async def probe_providers(force: bool = False) -> Dict[str, Dict[str, Any]]:
    now = time.time()
    if not force and _probe_cache["data"] is not None and now - _probe_cache["at"] < _PROBE_TTL_S:
        return _probe_cache["data"]
    try:
        data = await asyncio.wait_for(asyncio.to_thread(_probe_sync), timeout=20.0)
    except Exception as e:
        log_event(f"Provider probe failed: {e}", level="WARNING", component="AIProviderRouter")
        data = {}
    _probe_cache.update({"at": now, "data": data})
    log_event(
        "Provider probe: " + ", ".join(f"{k}={'ok' if v.get('usable') else 'off'}" for k, v in data.items()),
        component="AIProviderRouter",
    )
    return data


def _mark_exhausted(provider: str) -> None:
    data = _probe_cache.get("data") or {}
    if provider in data:
        data[provider]["usable"] = False


def _build_clip_prompt(scene_prompt: str, topic: str) -> str:
    return (
        f"Vertical 9:16 cinematic tech explainer shot. Topic: {topic[:120]}. "
        f"Scene: {scene_prompt[:300]}. Clean modern motion graphics, glowing data flows, "
        f"dark background, no text, no logos, smooth camera move."
    )


async def _poll(fn, task_id: str, deadline: float, done_states: List[str], fail_states: List[str]) -> Optional[str]:
    while time.time() < deadline:
        await asyncio.sleep(6)
        try:
            st = await asyncio.to_thread(fn, task_id)
        except Exception:
            continue
        state = str(st.get("status", "")).lower()
        if state in done_states and st.get("video_url"):
            return st["video_url"]
        if state in fail_states:
            return None
    return None


async def _try_luma(prompt: str, deadline: float) -> Optional[str]:
    from app.core.luma_video import luma_video_engine
    res = await asyncio.to_thread(luma_video_engine.create_generation, prompt, "9:16", True)
    gen_id = res.get("generation_id")
    if not gen_id:
        return None
    return await _poll(luma_video_engine.get_generation_status, gen_id, deadline, ["completed"], ["failed", "error"])


async def _try_runway(prompt: str, deadline: float) -> Optional[str]:
    from app.core.runway_video import runway_video
    res = await asyncio.to_thread(runway_video.create_text_to_video, prompt, "720:1280", 5)
    task_id = res.get("task_id")
    if not task_id:
        return None
    return await _poll(runway_video.get_task_status, task_id, deadline, ["succeeded"], ["failed", "cancelled", "error"])


_CLIP_PROVIDERS = [
    ("luma", "Luma Dream Machine (AI video)", _try_luma),
    ("runway", "Runway Gen-4 (AI video)", _try_runway),
]


async def generate_scene_clip(scene_prompt: str, topic: str, budget_s: float = 150.0) -> Dict[str, Any]:
    """Return {"video_url", "provider", "attempts"}; video_url is empty when no premium clip was produced."""
    status = await probe_providers()
    attempts: List[Dict[str, str]] = []
    deadline = time.time() + budget_s
    prompt = _build_clip_prompt(scene_prompt, topic)

    for key, label, fn in _CLIP_PROVIDERS:
        info = status.get(key) or {}
        if not info.get("usable"):
            attempts.append({"provider": label, "result": "skipped: no key or no credits"})
            continue
        if time.time() >= deadline:
            attempts.append({"provider": label, "result": "skipped: time budget exhausted"})
            continue
        try:
            url = await fn(prompt, deadline)
            if url:
                attempts.append({"provider": label, "result": "used"})
                return {"video_url": url, "provider": label, "attempts": attempts}
            attempts.append({"provider": label, "result": "no clip before deadline"})
        except Exception as e:
            msg = str(e)
            if "credit" in msg.lower() or "402" in msg or "insufficient" in msg.lower():
                _mark_exhausted(key)
            attempts.append({"provider": label, "result": f"failed: {msg[:160]}"})
            log_event(f"{label} clip failed, cascading: {msg[:200]}", level="WARNING", component="AIProviderRouter")

    return {"video_url": "", "provider": "", "attempts": attempts}


ELEVENLABS_MODEL_BY_LANG = {
    "en": "eleven_multilingual_v2",
    "hi": "eleven_multilingual_v2",
    "mr": "eleven_v3",
}


async def synthesize_premium_voice(text: str, lang_key: str, filename: str) -> Optional[Dict[str, Any]]:
    """Use ElevenLabs when it has enough character credits for this narration; otherwise None."""
    status = await probe_providers()
    info = status.get("elevenlabs") or {}
    if not info.get("usable") or int(info.get("credits", 0) or 0) < len(text):
        return None
    from app.core.elevenlabs_voice import elevenlabs_voice
    model_id = ELEVENLABS_MODEL_BY_LANG.get(lang_key, "eleven_multilingual_v2")
    try:
        res = await asyncio.wait_for(
            asyncio.to_thread(elevenlabs_voice.generate_speech, text, None, model_id, 0.55, 0.85, 0.15, filename),
            timeout=45.0,
        )
        if res.get("status") == "success":
            info["credits"] = max(0, int(info.get("credits", 0)) - len(text))
            return res
    except Exception as e:
        msg = str(e)
        if "quota" in msg.lower() or "credit" in msg.lower() or "401" in msg:
            _mark_exhausted("elevenlabs")
        log_event(f"ElevenLabs narration failed, falling back to free TTS: {msg[:200]}", level="WARNING", component="AIProviderRouter")
    return None
