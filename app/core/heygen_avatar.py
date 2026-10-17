"""
Mangesh Nano Pro AI Studio - HeyGen AI Talking Avatar Engine (API #19)
Generates photorealistic AI Human Avatars with lip-sync and gestures
for 9:16 Mobile Reels & YouTube Shorts.
"""

import os
import time
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import credentials_vault

# High-yield curated avatars suitable for Tech & Banking SQL interviews
CURATED_AVATARS = [
    {
        "avatar_id": "Nadim_public_5",
        "avatar_name": "Nadim (Investment Banker / Tech Lead)",
        "gender": "male",
        "preview_url": "https://files2.heygen.ai/avatar/v3/db5ad93ed00c4eaaab83ac225da62f20_62140/preview_target.webp",
        "role": "Bank SQL Lead"
    },
    {
        "avatar_id": "Wayne_20240711",
        "avatar_name": "Wayne (Senior Executive)",
        "gender": "male",
        "preview_url": "https://files2.heygen.ai/avatar/v3/Wayne_20240711/preview_target.webp",
        "role": "Wall Street Director"
    },
    {
        "avatar_id": "Daisy-inskirt-20220818",
        "avatar_name": "Daisy (Data Engineering Instructor)",
        "gender": "female",
        "preview_url": "https://files2.heygen.ai/avatar/v3/Daisy-inskirt-20220818/preview_target.webp",
        "role": "Data Architect"
    },
    {
        "avatar_id": "Monica_public_2",
        "avatar_name": "Monica (Fintech Consultant)",
        "gender": "female",
        "preview_url": "https://files2.heygen.ai/avatar/v3/Monica_public_2/preview_target.webp",
        "role": "FinTech Mentor"
    }
]


class HeyGenAvatarEngine:
    """
    Enterprise AI Avatar Presenter Engine powered by HeyGen API.
    Produces high-fidelity human presentations with synchronized voiceover.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("HEYGEN_API_KEY", "")
        self.base_url = "https://api.heygen.com"
        self.cache_file = Path("data/heygen_avatars_cache.json")
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

    def _resolve_api_key(self) -> str:
        if self.api_key and not self.api_key.startswith("••"):
            return self.api_key

        for s_name in ["HEYGEN_API_KEY", "HEYGEN", "HEYGEN_AVATAR"]:
            cred = credentials_vault.get_credential(s_name)
            if cred and cred.get("secret_value") and not cred["secret_value"].startswith("••"):
                self.api_key = cred["secret_value"]
                return self.api_key

        self.api_key = os.getenv("HEYGEN_API_KEY", "")
        return self.api_key

    def is_available(self) -> bool:
        k = self._resolve_api_key()
        return bool(k and k.startswith("sk_"))

    def get_curated_avatars(self) -> List[Dict[str, Any]]:
        """Returns fast-loading curated avatars for fintech/coding videos."""
        return CURATED_AVATARS

    def fetch_all_avatars(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Fetches complete live avatar catalog from HeyGen API with file caching."""
        if not force_refresh and self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                    if cached and isinstance(cached, list) and len(cached) > 0:
                        return cached
            except Exception:
                pass

        k = self._resolve_api_key()
        if not k:
            return CURATED_AVATARS

        try:
            req = urllib.request.Request(
                f"{self.base_url}/v2/avatars",
                headers={"X-Api-Key": k, "Accept": "application/json", "User-Agent": "NanoProAI/2.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                avatars = data.get("data", {}).get("avatars", [])
                if avatars:
                    try:
                        with open(self.cache_file, "w", encoding="utf-8") as f:
                            json.dump(avatars, f)
                    except Exception:
                        pass
                    return avatars
        except Exception as e:
            log_event(f"HeyGen avatars fetch notice: {e}", level="DEBUG", component="HeyGen")

        return CURATED_AVATARS

    def create_talking_avatar_video(
        self,
        script: str,
        avatar_id: str = "Nadim_public_5",
        title: str = "Bank SQL Short Hook",
        voice_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submits an asynchronous video generation task to HeyGen for a 9:16 vertical avatar reel.
        """
        k = self._resolve_api_key()
        if not k:
            raise ValueError("HeyGen API Key not configured. Add HEYGEN_API_KEY in CredentialsVault.")

        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id,
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "text",
                        "input_text": script,
                        "voice_id": voice_id or "2d5b0e6cf36f460aa7fc47e3eee4ba54"
                    },
                    "background": {
                        "type": "color",
                        "value": "#070B16"
                    }
                }
            ],
            "dimension": {
                "width": 1080,
                "height": 1920
            },
            "title": title
        }

        req = urllib.request.Request(
            f"{self.base_url}/v2/video/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"X-Api-Key": k, "Content-Type": "application/json", "Accept": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                video_id = data.get("data", {}).get("video_id")
                log_event(f"Submitted HeyGen video task [{video_id}] for avatar '{avatar_id}'", component="HeyGen")
                return {
                    "status": "success",
                    "video_id": video_id,
                    "avatar_id": avatar_id,
                    "title": title,
                    "created_at": time.time()
                }
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8")
            log_event(f"HeyGen HTTP Error ({e.code}): {err}", level="ERROR", component="HeyGen")
            raise RuntimeError(f"HeyGen Generation Error ({e.code}): {err}")
        except Exception as e:
            log_event(f"HeyGen Connection Error: {e}", level="ERROR", component="HeyGen")
            raise e

    def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """Polls video rendering status and returns downloadable video URL when completed."""
        k = self._resolve_api_key()
        if not k:
            raise ValueError("HeyGen API Key missing.")

        url = f"{self.base_url}/v1/video_status.get?video_id={video_id}"
        req = urllib.request.Request(url, headers={"X-Api-Key": k, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                v_data = data.get("data", {})
                status = v_data.get("status")  # pending, processing, completed, failed
                return {
                    "status": status,
                    "video_id": video_id,
                    "video_url": v_data.get("video_url"),
                    "thumbnail_url": v_data.get("thumbnail_url"),
                    "duration": v_data.get("duration"),
                    "error": v_data.get("error")
                }
        except Exception as e:
            return {"status": "error", "message": str(e), "video_id": video_id}


# Global Singleton instance
heygen_avatar_engine = HeyGenAvatarEngine()
heygen_avatar = heygen_avatar_engine
