"""
Mangesh Nano Pro AI Studio - Luma Dream Machine Video Engine (API #21)
Generates cinematic 3D Generative AI Videos and backgrounds from text prompts
for 9:16 Mobile Reels & YouTube Shorts.
"""

import os
import time
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import credentials_vault


class LumaVideoEngine:
    """
    Enterprise Luma Dream Machine Video Engine.
    Creates 3D cinematic moving camera shots, loops, and video backgrounds.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("LUMA_API_KEY", "")
        self.base_url = "https://api.lumalabs.ai/dream-machine/v1"

    def _resolve_api_key(self) -> str:
        if self.api_key and not self.api_key.startswith("••"):
            return self.api_key

        for s_name in ["LUMA_API_KEY", "LUMA", "LUMA_DREAM_MACHINE"]:
            cred = credentials_vault.get_credential(s_name)
            if cred and cred.get("secret_value") and not cred["secret_value"].startswith("••"):
                self.api_key = cred["secret_value"]
                return self.api_key

        self.api_key = os.getenv("LUMA_API_KEY", "")
        return self.api_key

    def is_available(self) -> bool:
        k = self._resolve_api_key()
        return bool(k and k.startswith("luma-api-"))

    def create_generation(
        self,
        prompt: str,
        aspect_ratio: str = "9:16",
        loop: bool = True
    ) -> Dict[str, Any]:
        """
        Submits a 3D generative video task to Luma Dream Machine.
        """
        k = self._resolve_api_key()
        if not k:
            raise ValueError("Luma API Key not configured. Add LUMA_API_KEY in CredentialsVault.")

        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "loop": loop
        }

        url = f"{self.base_url}/generations"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {k}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                gen_id = data.get("id")
                log_event(f"Submitted Luma video task [{gen_id}] for prompt '{prompt[:40]}'", component="LumaVideo")
                return {
                    "status": "success",
                    "generation_id": gen_id,
                    "state": data.get("state"),
                    "created_at": time.time(),
                    "provider": "Luma Dream Machine"
                }
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8")
            log_event(f"Luma HTTP Error ({e.code}): {err}", level="ERROR", component="LumaVideo")
            raise RuntimeError(f"Luma Video Error ({e.code}): {err}")
        except Exception as e:
            log_event(f"Luma Error: {e}", level="ERROR", component="LumaVideo")
            raise e

    def get_generation_status(self, generation_id: str) -> Dict[str, Any]:
        """Polls status of Luma video generation and returns video download URL when completed."""
        k = self._resolve_api_key()
        if not k:
            raise ValueError("Luma API Key missing.")

        url = f"{self.base_url}/generations/{generation_id}"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {k}", "Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                state = data.get("state")  # queued, dreaming, completed, failed
                assets = data.get("assets", {})
                return {
                    "status": state,
                    "generation_id": generation_id,
                    "video_url": assets.get("video"),
                    "thumbnail_url": assets.get("thumbnail"),
                    "failure_reason": data.get("failure_reason")
                }
        except Exception as e:
            return {"status": "error", "message": str(e), "generation_id": generation_id}


# Global Singleton instance
luma_video_engine = LumaVideoEngine()
luma_video = luma_video_engine
