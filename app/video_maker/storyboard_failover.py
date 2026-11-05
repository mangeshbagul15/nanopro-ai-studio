"""
NanoPro storyboard model failover.

If the selected storyboard model errors or returns an unusable storyboard
(bad JSON, too few scenes, generic outline), retry the same Reel request with
the next model instead of failing the whole job.
"""

import functools
import inspect
from typing import Any, Dict, List

from app.core.logger import log_event
from app.video_maker import sql_short_engine as _sse

STORYBOARD_MODEL_CHAIN: List[str] = [
    "gemini-3.5-flash-lite",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
]


def _is_storyboard_failure(res: Any) -> bool:
    if not isinstance(res, dict) or res.get("status") != "error":
        return False
    msg = str(res.get("message") or "").lower()
    return any(k in msg for k in ("storyboard", "model", "narrated scene", "api credentials"))


def _install() -> None:
    engine_cls = None
    for obj in vars(_sse).values():
        if isinstance(obj, type) and hasattr(obj, "generate_short_prompt_async"):
            engine_cls = obj
            break
    if engine_cls is None or getattr(engine_cls.generate_short_prompt_async, "_nanopro_failover", False):
        return

    original = engine_cls.generate_short_prompt_async
    signature = inspect.signature(original)

    @functools.wraps(original)
    async def generate_with_failover(self, *args, **kwargs) -> Dict[str, Any]:
        res = await original(self, *args, **kwargs)
        if not _is_storyboard_failure(res):
            return res
        try:
            bound = signature.bind(self, *args, **kwargs)
            kwargs = {k: v for k, v in bound.arguments.items() if k != "self"}
            extra = kwargs.pop("kwargs", None)
            if isinstance(extra, dict):
                kwargs.update(extra)
            args = ()
        except TypeError:
            return res

        first_model = kwargs.get("selected_model") or "openai/gpt-oss-120b"
        tried = {first_model}
        errors = [f"{first_model}: {res.get('message')}"]
        for model in STORYBOARD_MODEL_CHAIN:
            if model in tried:
                continue
            tried.add(model)
            log_event(
                f"Storyboard failed with {first_model}; auto-switching to {model}.",
                level="WARNING",
                component="StoryboardFailover",
            )
            retry_kwargs = dict(kwargs)
            retry_kwargs["selected_model"] = model
            retry_kwargs["generation_pattern"] = "hybrid"
            try:
                retry = await original(self, *args, **retry_kwargs)
            except Exception as e:  # keep trying the next model
                errors.append(f"{model}: {e}")
                continue
            if not _is_storyboard_failure(retry):
                if isinstance(retry, dict):
                    retry.setdefault("storyboard_failover", {"used_model": model, "previous_errors": errors})
                return retry
            errors.append(f"{model}: {retry.get('message')}")

        res = dict(res)
        res["message"] = "All storyboard models failed. " + " | ".join(e[:220] for e in errors[-5:])
        return res

    generate_with_failover._nanopro_failover = True
    engine_cls.generate_short_prompt_async = generate_with_failover
    log_event("Storyboard model failover installed.", component="StoryboardFailover")


_install()
