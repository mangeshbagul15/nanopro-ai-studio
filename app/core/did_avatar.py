"""
Mangesh Nano Pro AI Studio - D-ID Creative Reality Avatar Engine (API #20)
Generates high-engagement talking face avatar videos from photos or digital humans
with synchronized Marathi, Hindi, and English lip-sync.
"""

import os
import time
import json
import base64
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import credentials_vault

DEFAULT_DID_PRESENTERS = [
    {
        "id": "v2_public_Adam@0GLJgELXjc",
        "name": "Adam (Professional Tech Presenter)",
        "gender": "male",
        "thumbnail_url": "https://clips-presenters.d-id.com/v2/Adam/0GLJgELXjc/thumbnail.jpeg",
        "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Emma_m/image.jpeg"
    },
    {
        "id": "v2_public_Emma@9821hdjs",
        "name": "Emma (Fintech Anchor)",
        "gender": "female",
        "thumbnail_url": "https://clips-presenters.d-id.com/v2/Emma/thumbnail.jpeg",
        "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Emma_f/image.jpeg"
    }
]


class DIDAvatarEngine:
    """
    Enterprise D-ID Video Generation Engine.
    Creates animated talking avatar videos from text and photo inputs.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("D_ID_API_KEY", "")
        self.base_url = "https://api.d-id.com"

    def _resolve_api_key(self) -> str:
        if self.api_key and not self.api_key.startswith("••"):
            return self.api_key

        for s_name in ["D_ID_API_KEY", "D_ID", "DID"]:
            cred = credentials_vault.get_credential(s_name)
            if cred and cred.get("secret_value") and not cred["secret_value"].startswith("••"):
                self.api_key = cred["secret_value"]
                return self.api_key

        self.api_key = os.getenv("D_ID_API_KEY", "")
        return self.api_key

    def is_available(self) -> bool:
        k = self._resolve_api_key()
        return bool(k and ":" in k)

    def _get_auth_header(self) -> str:
        k = self._resolve_api_key()
        return f"Basic {k}"

    def get_credits(self) -> Dict[str, Any]:
        """Returns remaining credits on D-ID account."""
        url = f"{self.base_url}/credits"
        req = urllib.request.Request(
            url,
            headers={"Authorization": self._get_auth_header(), "Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return {
                    "status": "success",
                    "remaining": data.get("remaining", 0),
                    "total": data.get("total", 0)
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_talk(
        self,
        script: str,
        source_url: Optional[str] = None,
        language: str = "mr"
    ) -> Dict[str, Any]:
        """
        Creates an animated talking head video from text and an avatar photo.
        Supports Marathi (mr-IN-AarohiNeural), Hindi (hi-IN-SwaraNeural), and English (en-US-JennyNeural).
        """
        k = self._resolve_api_key()
        if not k:
            raise ValueError("D-ID API Key not configured. Add D_ID_API_KEY in CredentialsVault.")

        # Map voice based on language
        if language in ["mr", "minglish"]:
            voice_id = "mr-IN-AarohiNeural"
        elif language in ["hi", "hinglish"]:
            voice_id = "hi-IN-SwaraNeural"
        else:
            voice_id = "en-US-JennyNeural"

        # Default photo URL on D-ID's verified public S3
        img_url = source_url or "https://d-id-public-bucket.s3.amazonaws.com/alice.jpg"

        payload = {
            "script": {
                "type": "text",
                "subtitles": False,
                "provider": {
                    "type": "microsoft",
                    "voice_id": voice_id
                },
                "input": script
            },
            "config": {
                "fluent": True,
                "pad_audio": 0.0
            },
            "source_url": img_url
        }

        url = f"{self.base_url}/talks"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": self._get_auth_header(),
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                talk_id = data.get("id")
                log_event(f"Submitted D-ID Talk task [{talk_id}]", component="DIDAvatar")
                return {
                    "status": "success",
                    "talk_id": talk_id,
                    "created_at": time.time(),
                    "provider": "D-ID"
                }
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8")
            log_event(f"D-ID HTTP Error ({e.code}): {err}", level="ERROR", component="DIDAvatar")
            raise RuntimeError(f"D-ID Talk Error ({e.code}): {err}")
        except Exception as e:
            log_event(f"D-ID Error: {e}", level="ERROR", component="DIDAvatar")
            raise e

    def get_talk_status(self, talk_id: str) -> Dict[str, Any]:
        """Polls status of D-ID talking video."""
        url = f"{self.base_url}/talks/{talk_id}"
        req = urllib.request.Request(
            url,
            headers={"Authorization": self._get_auth_header(), "Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                status = data.get("status")  # created, started, done, error
                return {
                    "status": status,
                    "talk_id": talk_id,
                    "result_url": data.get("result_url"),
                    "duration": data.get("duration"),
                    "error": data.get("error")
                }
        except Exception as e:
            return {"status": "error", "message": str(e), "talk_id": talk_id}


# Global Singleton instance
did_avatar_engine = DIDAvatarEngine()
did_avatar = did_avatar_engine
