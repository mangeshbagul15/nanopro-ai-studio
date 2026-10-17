"""
Mangesh Nano Pro AI Studio - Upstash Serverless Redis & Cloud Cache Engine
Provides high-performance distributed cloud caching, rate limiting, and state persistence
powered by Upstash Serverless Redis REST API.
"""

import os
import time
import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import credentials_vault

try:
    from upstash_redis import Redis as UpstashSDKRedis
    _HAS_SDK = True
except ImportError:
    _HAS_SDK = False


class UpstashRedisEngine:
    """
    Enterprise Cloud Caching Engine powered by Upstash Serverless Redis.
    Hybrid architecture: uses Upstash Python SDK with automatic fallback to native REST API.
    """

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None):
        self.url = url or os.getenv("UPSTASH_REDIS_REST_URL", "")
        self.token = token or os.getenv("UPSTASH_REDIS_REST_TOKEN", "")
        self._sdk_client: Optional[Any] = None

    def _resolve_credentials(self) -> tuple[str, str]:
        if self.url and self.token and not self.token.startswith("••"):
            return self.url, self.token

        for s_name in ["UPSTASH_REDIS", "UPSTASH_REDIS_REST_URL", "UPSTASH"]:
            cred = credentials_vault.get_credential(s_name)
            if cred:
                tok = cred.get("secret_value", "")
                u = cred.get("host", "") or os.getenv("UPSTASH_REDIS_REST_URL", "")
                if tok and not tok.startswith("••"):
                    self.token = tok
                    self.url = u
                    return self.url, self.token

        self.url = os.getenv("UPSTASH_REDIS_REST_URL", "")
        self.token = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")
        return self.url, self.token

    def is_available(self) -> bool:
        u, t = self._resolve_credentials()
        return bool(u and t and len(t) >= 20)

    def _get_sdk(self):
        if self._sdk_client:
            return self._sdk_client
        u, t = self._resolve_credentials()
        if _HAS_SDK and u and t:
            try:
                self._sdk_client = UpstashSDKRedis(url=u, token=t)
                return self._sdk_client
            except Exception:
                pass
        return None

    def _rest_cmd(self, *parts: Any) -> Any:
        """Executes a Redis command via Upstash native REST HTTP API."""
        u, t = self._resolve_credentials()
        if not u or not t:
            raise ValueError("Upstash Redis credentials are not configured.")

        # REST endpoint: POST {url} with JSON array of command parts
        headers = {
            "Authorization": f"Bearer {t}",
            "Content-Type": "application/json",
            "User-Agent": "NanoPro-AI-Studio/2.0 (UpstashRedisEngine)"
        }
        body = json.dumps([str(p) for p in parts]).encode("utf-8")
        req = urllib.request.Request(u, data=body, headers=headers, method="POST")

        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if "error" in data:
                    raise RuntimeError(f"Upstash Error: {data['error']}")
                return data.get("result")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            log_event(f"Upstash HTTP {e.code}: {err_body}", level="ERROR", component="Upstash")
            raise RuntimeError(f"Upstash Error ({e.code}): {err_body}")

    def ping(self) -> bool:
        """Pings the Upstash Redis instance. Returns True if responsive."""
        try:
            sdk = self._get_sdk()
            if sdk:
                return sdk.ping() == "PONG"
            return self._rest_cmd("PING") == "PONG"
        except Exception as e:
            log_event(f"Upstash ping failed: {e}", level="WARNING", component="Upstash")
            return False

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Sets a key-value pair with optional TTL expiry in seconds."""
        try:
            val_str = json.dumps(value) if not isinstance(value, str) else value
            sdk = self._get_sdk()
            if sdk:
                if ex:
                    sdk.set(key, val_str, ex=ex)
                else:
                    sdk.set(key, val_str)
                return True

            cmd = ["SET", key, val_str]
            if ex:
                cmd.extend(["EX", str(ex)])
            res = self._rest_cmd(*cmd)
            return res == "OK"
        except Exception as e:
            log_event(f"Upstash SET '{key}' failed: {e}", level="ERROR", component="Upstash")
            raise e

    def get(self, key: str) -> Optional[Any]:
        """Gets a value by key. Automatically deserializes JSON if applicable."""
        try:
            sdk = self._get_sdk()
            if sdk:
                val = sdk.get(key)
            else:
                val = self._rest_cmd("GET", key)

            if val is None:
                return None
            try:
                return json.loads(val)
            except Exception:
                return val
        except Exception as e:
            log_event(f"Upstash GET '{key}' failed: {e}", level="ERROR", component="Upstash")
            return None

    def delete(self, key: str) -> bool:
        """Deletes a key from Upstash Redis."""
        try:
            sdk = self._get_sdk()
            if sdk:
                return bool(sdk.delete(key))
            res = self._rest_cmd("DEL", key)
            return bool(res)
        except Exception as e:
            log_event(f"Upstash DEL '{key}' failed: {e}", level="ERROR", component="Upstash")
            return False

    def incr(self, key: str) -> int:
        """Increments a key atomically (useful for rate limiting)."""
        try:
            sdk = self._get_sdk()
            if sdk:
                return sdk.incr(key)
            return int(self._rest_cmd("INCR", key))
        except Exception as e:
            log_event(f"Upstash INCR '{key}' failed: {e}", level="ERROR", component="Upstash")
            raise e

    def keys(self, pattern: str = "*") -> List[str]:
        """Returns all keys matching pattern."""
        try:
            sdk = self._get_sdk()
            if sdk:
                return sdk.keys(pattern)
            return self._rest_cmd("KEYS", pattern) or []
        except Exception as e:
            log_event(f"Upstash KEYS '{pattern}' failed: {e}", level="ERROR", component="Upstash")
            return []

    def get_markdown_status(self) -> str:
        """Generates a clean Markdown status report of Upstash Serverless Redis."""
        t0 = time.time()
        alive = self.ping()
        latency = round((time.time() - t0) * 1000, 1)

        u, _ = self._resolve_credentials()
        host = urllib.parse.urlparse(u).netloc if u else "Not Configured"

        status_badge = "🟢 **ONLINE & RESPONSIVE**" if alive else "🔴 **OFFLINE / UNREACHABLE**"

        lines = [
            f"### ☁️ Upstash Serverless Redis Status",
            f"**Endpoint:** `{host}`",
            f"**Status:** {status_badge}",
            f"**Roundtrip Ping Latency:** `{latency}ms`",
            f"**SDK Engine:** `upstash-redis v1.8.0` with Native REST Fallback",
            f"**Features Active:** High-Speed Caching, Atomic Rate Limiting, TTL Expiration",
            ""
        ]
        if alive:
            try:
                sample_keys = self.keys("*")
                lines.append(f"- **Total Indexed Keys in Memory:** `{len(sample_keys)}`")
                if sample_keys:
                    lines.append(f"- **Sample Keys:** `{', '.join(sample_keys[:6])}`")
            except Exception:
                pass

        lines.append("")
        lines.append(f"> *Persistence powered by Upstash Global Serverless Redis*")
        return "\n".join(lines)


# Global Singleton instance
upstash_cache = UpstashRedisEngine()
