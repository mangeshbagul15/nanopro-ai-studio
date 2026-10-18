"""
Mangesh Nano Pro AI Studio - Runway Gen-4 Video Engine (API #22)
Official integration with RunwayML API (https://api.dev.runwayml.com/v1).
Supports Gen-4 Turbo (image_to_video) and Gen-4.5 (text_to_video) with 9:16 vertical ratio (720:1280).
Includes multi-token automatic rotation (Key 1 & Key 2) and seamless cascade failover.
"""

import os
import time
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import credentials_vault


class RunwayVideoEngine:
    """
    Enterprise Runway Gen-4 Video Generation Engine with Token Rotation.
    Rotates seamlessly across Runway Token Pool (Token 1, Token 2) on quota/rate-limits.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("RUNWAY_API_KEY", "")
        self.base_url = "https://api.dev.runwayml.com/v1"
        self.version_header = "2024-09-13"

        # Multi-Token Failover Pool for Runway API
        self.runway_tokens: List[str] = [
            "key_1844428f2b071ee075875f502eae9530fdb522d6fb1ab1a4f114378857929722374d0bebd0d969f133b22dc6d302e3e6e3595c1903608da33edebe83ee6b2bfe",
            "key_d12587db38b98eedd97b34bab231bbcbe66aef4e6f756d206a31a196fc5125b78d7769d7d20f91ac444bedad9787157b366a5ad9f8943552f16479b709613e70"
        ]
        self.active_token_idx = 0
        self.tokens_depleted_until = 0.0

    def _resolve_api_tokens(self) -> List[str]:
        """Resolves all available Runway API keys from memory, vault, and environment."""
        resolved = []
        for t in self.runway_tokens:
            if t and t.startswith("key_"):
                resolved.append(t)

        for s_name in ["RUNWAY_API_KEY", "RUNWAY_API_KEY_2", "RUNWAYML", "RUNWAY"]:
            cred = credentials_vault.get_credential(s_name)
            if cred and cred.get("secret_value") and not cred["secret_value"].startswith("••"):
                val = cred["secret_value"]
                if val.startswith("key_") and val not in resolved:
                    resolved.append(val)

        env_k = os.getenv("RUNWAY_API_KEY", "")
        if env_k and env_k.startswith("key_") and env_k not in resolved:
            resolved.append(env_k)

        if resolved:
            self.runway_tokens = resolved
        return self.runway_tokens

    def is_available(self) -> bool:
        tokens = self._resolve_api_tokens()
        return len(tokens) > 0

    def get_organization_info(self, token_idx: Optional[int] = None) -> Dict[str, Any]:
        """Fetches account tier, active models, and credit balance from Runway for the selected or active token."""
        tokens = self._resolve_api_tokens()
        if not tokens:
            return {"status": "error", "message": "No Runway API keys configured in pool"}

        idx = self.active_token_idx if token_idx is None else (token_idx % len(tokens))
        k = tokens[idx]

        url = f"{self.base_url}/organization"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {k}",
                "X-Runway-Version": self.version_header,
                "Accept": "application/json"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return {
                    "status": "success",
                    "token_index": idx + 1,
                    "token_masked": f"{k[:10]}...{k[-6:]}",
                    "credit_balance": data.get("creditBalance", 0),
                    "tier": data.get("tier", {}).get("name", "Free Tier"),
                    "models_supported": list(data.get("tier", {}).get("models", {}).keys()),
                    "provider": "Runway Gen-4"
                }
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8")
            log_event(f"Runway Org Error for Token #{idx + 1} ({e.code}): {err}", level="WARNING", component="RunwayVideo")
            return {"status": "error", "code": e.code, "token_index": idx + 1, "message": err}
        except Exception as e:
            return {"status": "error", "token_index": idx + 1, "message": str(e)}

    def get_all_tokens_status(self) -> List[Dict[str, Any]]:
        """Returns health and credit balance across all Runway tokens in pool."""
        tokens = self._resolve_api_tokens()
        res = []
        for i in range(len(tokens)):
            res.append(self.get_organization_info(token_idx=i))
        return res

    def create_text_to_video(
        self,
        prompt: str,
        ratio: str = "720:1280",  # Standard 9:16 vertical ratio for Reels/Shorts
        duration: int = 5,
        model: str = "gen4.5"
    ) -> Dict[str, Any]:
        """Submits a text-to-video generation task to Runway Gen-4.5 with multi-token failover."""
        if getattr(self, "tokens_depleted_until", 0) > time.time():
            raise RuntimeError("Runway tokens out of credits (cooldown active). Auto-cascading to 3D AI Motion Engine.")

        tokens = self._resolve_api_tokens()
        if not tokens:
            raise ValueError("Runway API Key missing. Add RUNWAY_API_KEY in CredentialsVault.")

        attempts = len(tokens)
        last_error = ""

        for attempt in range(attempts):
            idx = (self.active_token_idx + attempt) % attempts
            k = tokens[idx]

            payload = {
                "promptText": prompt,
                "model": model,
                "ratio": ratio,
                "duration": duration
            }

            url = f"{self.base_url}/text_to_video"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {k}",
                    "X-Runway-Version": self.version_header,
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )

            try:
                with urllib.request.urlopen(req, timeout=25) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    task_id = data.get("id")
                    self.active_token_idx = idx
                    log_event(f"Submitted Runway text_to_video on Token #{idx + 1} [{task_id}] prompt='{prompt[:40]}'", component="RunwayVideo")
                    return {
                        "status": "success",
                        "task_id": task_id,
                        "token_used": idx + 1,
                        "created_at": time.time(),
                        "provider": "RunwayML Gen-4.5"
                    }
            except urllib.error.HTTPError as e:
                err = e.read().decode("utf-8")
                last_error = f"Token #{idx + 1} HTTP {e.code}: {err}"
                log_event(f"Runway Token #{idx + 1} failed ({last_error}). Auto-rotating to next token...", level="WARNING", component="RunwayVideo")
            except Exception as e:
                last_error = f"Token #{idx + 1} Exception: {str(e)}"
                log_event(f"Runway Token #{idx + 1} error: {e}", level="WARNING", component="RunwayVideo")

        # If all tokens fail (e.g. 0 credit balance), activate cooldown & raise clean error for cascade router
        if "credit" in last_error.lower() or "400" in last_error:
            self.tokens_depleted_until = time.time() + 1800
        raise RuntimeError(f"All {attempts} Runway tokens exhausted or out of credits. Last error: {last_error}")

    def create_image_to_video(
        self,
        image_url: str,
        prompt_text: Optional[str] = None,
        ratio: str = "720:1280",
        duration: int = 5,
        model: str = "gen4_turbo"
    ) -> Dict[str, Any]:
        """Submits an image-to-video animation task to Runway Gen-4 Turbo with multi-token failover."""
        if getattr(self, "tokens_depleted_until", 0) > time.time():
            raise RuntimeError("Runway tokens out of credits (cooldown active). Auto-cascading to 3D AI Motion Engine.")

        tokens = self._resolve_api_tokens()
        if not tokens:
            raise ValueError("Runway API Key missing.")

        attempts = len(tokens)
        last_error = ""

        for attempt in range(attempts):
            idx = (self.active_token_idx + attempt) % attempts
            k = tokens[idx]

            payload = {
                "promptImage": image_url,
                "model": model,
                "ratio": ratio,
                "duration": duration
            }
            if prompt_text:
                payload["promptText"] = prompt_text

            url = f"{self.base_url}/image_to_video"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {k}",
                    "X-Runway-Version": self.version_header,
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )

            try:
                with urllib.request.urlopen(req, timeout=25) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    task_id = data.get("id")
                    self.active_token_idx = idx
                    log_event(f"Submitted Runway image_to_video on Token #{idx + 1} [{task_id}]", component="RunwayVideo")
                    return {
                        "status": "success",
                        "task_id": task_id,
                        "token_used": idx + 1,
                        "created_at": time.time(),
                        "provider": "RunwayML Gen-4 Turbo"
                    }
            except urllib.error.HTTPError as e:
                err = e.read().decode("utf-8")
                last_error = f"Token #{idx + 1} HTTP {e.code}: {err}"
                log_event(f"Runway Token #{idx + 1} failed ({last_error}). Auto-rotating...", level="WARNING", component="RunwayVideo")
            except Exception as e:
                last_error = f"Token #{idx + 1} Exception: {str(e)}"
                log_event(f"Runway Token #{idx + 1} error: {e}", level="WARNING", component="RunwayVideo")

        if "credit" in last_error.lower() or "400" in last_error:
            self.tokens_depleted_until = time.time() + 1800
        raise RuntimeError(f"All {attempts} Runway tokens exhausted or out of credits. Last error: {last_error}")

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Polls status of a Runway generation task across active tokens."""
        tokens = self._resolve_api_tokens()
        if not tokens:
            raise ValueError("Runway API Key missing.")

        # Try active token first, then fallback to others
        for k in [tokens[self.active_token_idx]] + [t for t in tokens if t != tokens[self.active_token_idx]]:
            url = f"{self.base_url}/tasks/{task_id}"
            req = urllib.request.Request(
                url,
                headers={
                    "Authorization": f"Bearer {k}",
                    "X-Runway-Version": self.version_header,
                    "Accept": "application/json"
                }
            )

            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    status = data.get("status", "UNKNOWN").lower()
                    output = data.get("output", [])
                    video_url = output[0] if output and isinstance(output, list) else None

                    return {
                        "status": status,
                        "task_id": task_id,
                        "video_url": video_url,
                        "progress": data.get("progress", 0),
                        "failure": data.get("failure"),
                        "failure_code": data.get("failureCode")
                    }
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue  # task might belong to another token
                err = e.read().decode("utf-8")
                return {"status": "error", "code": e.code, "message": err}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        return {"status": "error", "message": f"Task {task_id} not found across configured tokens"}


# Global Singleton instance
runway_video = RunwayVideoEngine()
