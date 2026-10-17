"""
Mangesh Nano Pro AI Studio - ElevenLabs Voice AI Engine
Provides high-fidelity Text-to-Speech (TTS), Marathi/Hindi/English voice synthesis,
and custom voice cloning for AI Video voiceovers.
"""

import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import credentials_vault

class ElevenLabsVoiceEngine:
    """
    Enterprise Text-to-Speech Engine using ElevenLabs REST API.
    Supports eleven_multilingual_v2, eleven_turbo_v2_5, and voice cloning.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "")
        self.base_url = "https://api.elevenlabs.io/v1"
        # Default to high-fidelity premade voice compatible across all subscription tiers (Free, Starter, Pro)
        self.default_voice_id = "EXAVITQu4vr4xnSDxMaL"  # Sarah (Reassuring, Clear, Multilingual)
        self.output_dir = Path("data/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_api_key(self) -> str:
        if self.api_key and not self.api_key.startswith("••"):
            return self.api_key
        # Check CredentialsVault
        for s_name in ["ELEVENLABS_VOICE_API", "ELEVENLABS_API_KEY", "ELEVENLABS"]:
            cred = credentials_vault.get_credential(s_name)
            if cred and cred.get("secret_value") and not cred["secret_value"].startswith("••"):
                self.api_key = cred["secret_value"]
                return self.api_key
        self.api_key = os.getenv("ELEVENLABS_API_KEY", "")
        return self.api_key

    def is_available(self) -> bool:
        k = self._resolve_api_key()
        return bool(k and k.startswith("sk_"))

    def get_user_info(self) -> Dict[str, Any]:
        """Retrieves subscription tier, character usage, and limits."""
        k = self._resolve_api_key()
        if not k:
            raise ValueError("ElevenLabs API Key not configured. Key must start with 'sk_'.")

        url = f"{self.base_url}/user"
        req = urllib.request.Request(url, headers={"xi-api-key": k, "User-Agent": "NanoProAI/2.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def get_voices(self) -> List[Dict[str, Any]]:
        """Lists all available voices (pre-made and cloned)."""
        k = self._resolve_api_key()
        if not k:
            raise ValueError("ElevenLabs API Key not configured.")

        url = f"{self.base_url}/voices"
        req = urllib.request.Request(url, headers={"xi-api-key": k, "User-Agent": "NanoProAI/2.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("voices", [])

    def generate_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model_id: str = "eleven_multilingual_v2",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes speech from text and saves to mp3 file.
        Returns metadata and output file path.
        """
        k = self._resolve_api_key()
        if not k:
            raise ValueError("ElevenLabs API Key not configured. Key must start with 'sk_'.")

        v_id = voice_id or self.default_voice_id
        url = f"{self.base_url}/text-to-speech/{v_id}"

        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }
        json_data = json.dumps(payload).encode("utf-8")

        fname = output_filename or f"tts_{int(time.time())}.mp3"
        out_path = self.output_dir / fname

        t_start = time.time()
        req = urllib.request.Request(
            url,
            data=json_data,
            headers={
                "xi-api-key": k,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
                "User-Agent": "NanoProAI/2.0"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                audio_bytes = resp.read()
                dur_ms = round((time.time() - t_start) * 1000, 1)

                with open(out_path, "wb") as f:
                    f.write(audio_bytes)

                log_event(
                    f"ElevenLabs TTS synthesized {len(text)} chars to '{out_path.name}' ({len(audio_bytes)} bytes) in {dur_ms}ms",
                    component="ElevenLabs"
                )
                return {
                    "status": "success",
                    "file_path": str(out_path),
                    "file_name": out_path.name,
                    "bytes": len(audio_bytes),
                    "chars": len(text),
                    "duration_ms": dur_ms,
                    "model_id": model_id,
                    "voice_id": v_id
                }

        except urllib.error.HTTPError as e:
            err_msg = str(e)
            try:
                err_body = e.read().decode("utf-8")
                err_json = json.loads(err_body)
                err_msg = err_json.get("detail", {}).get("message", err_body)
            except Exception:
                pass
            log_event(f"ElevenLabs HTTP Error ({e.code}): {err_msg}", level="ERROR", component="ElevenLabs")
            raise RuntimeError(f"ElevenLabs Error ({e.code}): {err_msg}")
        except Exception as e:
            log_event(f"ElevenLabs Connection Error: {e}", level="ERROR", component="ElevenLabs")
            raise e


# Global Singleton instance
elevenlabs_voice_engine = ElevenLabsVoiceEngine()
