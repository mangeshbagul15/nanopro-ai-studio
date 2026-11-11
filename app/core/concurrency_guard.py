"""Admission control for the free Render tier.

0.1 CPU / 512 MB cannot serve many simultaneous AI requests, so this caps
in-flight API work and rejects excess requests with 429 instead of letting the
instance swap or get OOM-killed. Counters are plain ints mutated only between
awaits, which is safe on the single event loop.
"""
import json
import os
from typing import Dict

from app.core.runtime_profile import is_cloud

AI_PREFIXES = (
    "/api/manager/",
    "/api/antigravity/",
    "/api/data_modeling/",
    "/api/research/",
    "/api/coding/",
    "/api/career/",
    "/api/data_science/",
    "/api/data_analyst/",
)


def _int_env(name: str, default: int) -> int:
    try:
        return max(1, int(os.environ.get(name, str(default))))
    except (TypeError, ValueError):
        return default


class ConcurrencyGuardMiddleware:
    def __init__(self, app):
        global _instance
        self.app = app
        cloud = is_cloud()
        self.pools: Dict[str, Dict[str, int]] = {
            "ai": {"active": 0, "limit": _int_env("NANOPRO_AI_CONCURRENCY", 2 if cloud else 8), "rejected": 0},
            "api": {"active": 0, "limit": _int_env("NANOPRO_API_CONCURRENCY", 6 if cloud else 32), "rejected": 0},
        }
        self.rejected_total = 0
        _instance = self

    def _pool_for(self, path: str) -> str:
        return "ai" if path.startswith(AI_PREFIXES) else "api"

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            return await self.app(scope, receive, send)
        path = scope.get("path") or ""
        if not path.startswith("/api/"):
            return await self.app(scope, receive, send)

        pool = self.pools[self._pool_for(path)]
        if pool["active"] >= pool["limit"]:
            pool["rejected"] += 1
            self.rejected_total += 1
            body = json.dumps(
                {
                    "status": "busy",
                    "error": "NanoPro is handling too many concurrent requests. Please retry in a few seconds.",
                    "pool": self._pool_for(path),
                }
            ).encode()
            await send(
                {
                    "type": "http.response.start",
                    "status": 429,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"retry-after", b"3"),
                        (b"cache-control", b"no-store"),
                        (b"access-control-allow-origin", b"*"),
                    ],
                }
            )
            await send({"type": "http.response.body", "body": body})
            return

        pool["active"] += 1
        try:
            return await self.app(scope, receive, send)
        finally:
            pool["active"] -= 1

    def status(self) -> Dict[str, int]:
        return {
            "ai_active": self.pools["ai"]["active"],
            "ai_limit": self.pools["ai"]["limit"],
            "api_active": self.pools["api"]["active"],
            "api_limit": self.pools["api"]["limit"],
            "rejected_total": self.rejected_total,
        }


_instance = None


def concurrency_status() -> Dict[str, int]:
    return _instance.status() if _instance is not None else {}
