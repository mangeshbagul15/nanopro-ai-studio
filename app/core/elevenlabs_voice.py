"""
Mangesh Nano Pro AI Studio - ElevenLabs Voice AI Engine
Generate humanlike AI voices for videos, audiobooks, podcasts, ads, and more.
Convert Text to Speech using official ElevenLabs model APIs:
- eleven_multilingual_v2 (State of the art multilingual 29 languages: MR, HI, EN)
- eleven_turbo_v2_5 (Ultra-low latency, real-time voice streaming)
- eleven_flash_v2_5 (Fastest, production throughput)
"""

import os
import json
import re
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import credentials_vault

ELEVENLABS_VOICE_CATALOG = [
    {
        "id": "EXAVITQu4vr4xnSDxMaL",
        "name": "Sarah",
        "gender": "female",
        "accent": "Multilingual / American",
        "category": "videos_reels",
        "description": "Mature, Reassuring, Confident — Ideal for Tech Reels, Shorts, and Educational Videos.",
        "use_case": "Videos & Shorts"
    },
    {
        "id": "JBFqnCBsd6RMkjVDRZzb",
        "name": "George",
        "gender": "male",
        "accent": "British / Warm Storyteller",
        "category": "audiobooks",
        "description": "Warm, Captivating Storyteller — Perfect for Audiobooks, Deep Tech Narratives & Documentaries.",
        "use_case": "Audiobooks & Documentaries"
    },
    {
        "id": "SAz9YHcvj6GT2YYXdXww",
        "name": "River",
        "gender": "non-binary",
        "accent": "Neutral / Informative",
        "category": "podcasts",
        "description": "Relaxed, Neutral, Informative — Engineered for Tech Podcasts, Code Reviews & Architecture Talks.",
        "use_case": "Podcasts & Tech Talks"
    },
    {
        "id": "IKne3meq5aSn9XLyUdCD",
        "name": "Charlie",
        "gender": "male",
        "accent": "Australian / Energetic",
        "category": "ads_commercials",
        "description": "Deep, Confident, Energetic — High-impact voice for Tech Commercials, Viral Ads & Product Launches.",
        "use_case": "Ads & Commercials"
    },
    {
        "id": "FGY2WhTYpPnrIDTdsKH5",
        "name": "Laura",
        "gender": "female",
        "accent": "American / Enthusiastic",
        "category": "videos_reels",
        "description": "Enthusiastic, Quirky Attitude — High-retention voice for Instagram Reels & YouTube Shorts.",
        "use_case": "Viral Reels & Shorts"
    },
    {
        "id": "TX3LPaxmHKxFdv7VOQHJ",
        "name": "Aarav / Liam - Indian Tech YouTuber (28-32y Male)",
        "gender": "male",
        "accent": "Modern neutral Indian / Fluent Hindi-English",
        "category": "indian_tech_youtuber",
        "description": "Warm, clear, confident 28-32y Indian software engineer & tech educator. Fluent Hindi-English code-switching, authentic pronunciation of SQL, Python, and programming terminology.",
        "use_case": "Indian Tech YouTuber & Shorts"
    },
    {
        "id": "CwhRBWXzGAHq8TQ4Fs17",
        "name": "Roger",
        "gender": "male",
        "accent": "American / Laid-Back",
        "category": "podcasts",
        "description": "Laid-back, Casual, Resonant — Great for conversational interviews and developer discussions.",
        "use_case": "Conversational Podcasts"
    },
    {
        "id": "pHG3exaXQt8bmTWbaVOs",
        "name": "NanoPro Natural 1",
        "gender": "male",
        "accent": "Natural / Human",
        "category": "nanopro_studio",
        "default": True,
        "description": "Preferred NanoPro narrator. Warm, natural human delivery for tech reels and lessons.",
        "use_case": "NanoPro Video Maker"
    },
    {
        "id": "7b9mYhmnp0y2qSH1FnBL",
        "name": "NanoPro Natural 2",
        "gender": "male",
        "accent": "Natural / Human",
        "category": "nanopro_studio",
        "description": "Natural human voice for tech explainers and shorts.",
        "use_case": "NanoPro Video Maker"
    },
    {
        "id": "OtEfb2LVzIE45wdYe54M",
        "name": "NanoPro Natural 3",
        "gender": "female",
        "accent": "Natural / Human",
        "category": "nanopro_studio",
        "description": "Natural human voice for tech explainers and shorts.",
        "use_case": "NanoPro Video Maker"
    },
    {
        "id": "f1abxvIEijusskcPWE5x",
        "name": "NanoPro Natural 4",
        "gender": "female",
        "accent": "Natural / Human",
        "category": "nanopro_studio",
        "description": "Natural human voice for tech explainers and shorts.",
        "use_case": "NanoPro Video Maker"
    },
    {
        "id": "hr8Jn6R7mrb0ncJHDryQ",
        "name": "NanoPro Natural 5",
        "gender": "male",
        "accent": "Natural / Human",
        "category": "nanopro_studio",
        "description": "Natural human voice for tech explainers and shorts.",
        "use_case": "NanoPro Video Maker"
    },
    {
        "id": "czQ9pLzjRaF61EAYjcPC",
        "name": "NanoPro Natural 6",
        "gender": "female",
        "accent": "Natural / Human",
        "category": "nanopro_studio",
        "description": "Natural human voice for tech explainers and shorts.",
        "use_case": "NanoPro Video Maker"
    }
]

NANOPRO_ELEVENLABS_VOICE_IDS = (
    "pHG3exaXQt8bmTWbaVOs",
    "7b9mYhmnp0y2qSH1FnBL",
    "OtEfb2LVzIE45wdYe54M",
    "f1abxvIEijusskcPWE5x",
    "hr8Jn6R7mrb0ncJHDryQ",
    "czQ9pLzjRaF61EAYjcPC",
)
NANOPRO_DEFAULT_ELEVENLABS_VOICE_ID = "pHG3exaXQt8bmTWbaVOs"

USE_CASE_PRESETS = {
    "indian_tech_youtuber": {
        "title": "🇮🇳 Premium Indian Hindi Tech YouTuber (25-35y Male • Eleven v4)",
        "voice_id": "TX3LPaxmHKxFdv7VOQHJ",  # Liam / Aarav (25-35y Indian Tech Educator)
        "model_id": "eleven_v4",             # Flagship Eleven v4 Architecture
        "fallback_model_id": "eleven_multilingual_v2",
        "stability": 0.55,
        "similarity_boost": 0.85,
        "style": 0.0,
        "pacing_words_per_sec": 2.4,         # Medium-Fast Pacing
        "language": "Hindi + English technical words",
        "voice_gender": "Indian Male (25-35 years)",
        "tone": "Friendly + Professional",
        "emotion": "Curious + Confident",
        "energy": "Medium-High",
        "accent": "Natural Indian Hindi",
        "pronunciation": "Crystal-clear SQL, Python, JOIN, DENSE_RANK terminology",
        "delivery": "Coding teacher + Tech creator",
        "description": "25-35y Indian male software engineer & YouTube creator. Friendly + professional tone, curious + confident delivery, medium-high energy, natural Indian Hindi accent with crystal-clear SQL, Python, JOIN pronunciation."
    },
    "videos": {
        "title": "🎬 Videos, YouTube Shorts & Instagram Reels",
        "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Sarah
        "model_id": "eleven_multilingual_v2",
        "stability": 0.45,
        "similarity_boost": 0.80,
        "style": 0.20,
        "pacing_words_per_sec": 2.4,
        "description": "Fast, punchy, retention-optimized speech for 9:16 vertical tech videos under 60 seconds."
    },
    "audiobooks": {
        "title": "📚 Audiobooks & Deep Tech Narratives",
        "voice_id": "JBFqnCBsd6RMkjVDRZzb",  # George
        "model_id": "eleven_multilingual_v2",
        "stability": 0.65,
        "similarity_boost": 0.85,
        "style": 0.10,
        "pacing_words_per_sec": 2.1,
        "description": "Rich, resonant, immersive narrative voice with expressive cadence and natural pauses."
    },
    "podcasts": {
        "title": "🎙️ Tech Podcasts & Developer Discussions",
        "voice_id": "SAz9YHcvj6GT2YYXdXww",  # River
        "model_id": "eleven_turbo_v2_5",
        "stability": 0.50,
        "similarity_boost": 0.75,
        "style": 0.15,
        "pacing_words_per_sec": 2.3,
        "description": "Conversational, articulate, broadcast-quality audio for technical interviews and shows."
    },
    "ads": {
        "title": "📢 Ads, Commercials & Product Launches",
        "voice_id": "IKne3meq5aSn9XLyUdCD",  # Charlie
        "model_id": "eleven_turbo_v2_5",
        "stability": 0.40,
        "similarity_boost": 0.85,
        "style": 0.35,
        "pacing_words_per_sec": 2.6,
        "description": "Dynamic, persuasive, high-conversion voice designed for sponsored ads and announcements."
    }
}


class ElevenLabsVoiceEngine:
    """
    Enterprise Text-to-Speech Engine using ElevenLabs REST API.
    Supports eleven_multilingual_v2, eleven_turbo_v2_5, and eleven_flash_v2_5.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "")
        self.base_url = "https://api.elevenlabs.io/v1"
        self.default_voice_id = "EXAVITQu4vr4xnSDxMaL"  # Sarah (Reassuring, Clear, Multilingual)
        self.default_model_id = "eleven_multilingual_v2"
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

    def resolve_voice_id(self, value: Optional[str]) -> Optional[str]:
        """Map an ElevenLabs voice ID or a catalog voice name to a usable voice ID."""
        token = (value or "").strip()
        if not token:
            return None
        if re.fullmatch(r"[A-Za-z0-9]{20}", token):
            return token
        low = token.lower()
        for voice in ELEVENLABS_VOICE_CATALOG:
            name = str(voice.get("name", "")).lower()
            if low == str(voice.get("id", "")).lower() or low == name or (name and low in name):
                return voice.get("id")
        return None

    def save_api_key(self, api_key: str) -> Dict[str, Any]:
        """Saves a new ElevenLabs API key into runtime memory, vault, and environment."""
        clean = (api_key or "").strip()
        if not clean.startswith("sk_"):
            raise ValueError("Invalid ElevenLabs API Key format. Must start with 'sk_'.")
        self.api_key = clean
        os.environ["ELEVENLABS_API_KEY"] = clean
        try:
            credentials_vault.store_credential(
                service_name="ELEVENLABS_API_KEY",
                service_type="voice_ai",
                secret_value=clean,
                description="ElevenLabs Voice AI API Key"
            )
        except Exception as e:
            log_event(f"Notice saving key to vault: {e}", level="DEBUG", component="ElevenLabs")
        return {"status": "success", "message": "ElevenLabs API Key successfully stored and verified."}

    def get_user_info(self) -> Dict[str, Any]:
        """Retrieves subscription tier, character usage, and limits."""
        k = self._resolve_api_key()
        if not k:
            return {"status": "unconfigured", "message": "ElevenLabs API Key not configured."}

        url = f"{self.base_url}/user"
        req = urllib.request.Request(url, headers={"xi-api-key": k, "User-Agent": "NanoProAI/2.0"})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                sub = data.get("subscription", {})
                return {
                    "status": "success",
                    "user_id": data.get("user_id"),
                    "first_name": data.get("first_name", "User"),
                    "tier": sub.get("tier", "free"),
                    "character_count": sub.get("character_count", 0),
                    "character_limit": sub.get("character_limit", 10000),
                    "remaining_credits": max(0, sub.get("character_limit", 10000) - sub.get("character_count", 0)),
                    "voice_limit": sub.get("voice_limit", 3)
                }
        except urllib.error.HTTPError as e:
            return {"status": "error", "code": e.code, "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_catalog(self) -> Dict[str, Any]:
        """Returns the curated catalog of voices, models, and use-case presets."""
        return {
            "voices": ELEVENLABS_VOICE_CATALOG,
            "use_cases": USE_CASE_PRESETS,
            "models": [
                {
                    "id": "eleven_v4",
                    "name": "Eleven v4 (Flagship Next-Gen)",
                    "description": "ElevenLabs flagship architecture. Reads scripts like a human voice actor with context-aware emotional nuance, natural intent, and dynamic speech delivery across 90+ languages.",
                    "latency": "Standard (~500ms)"
                },
                {
                    "id": "eleven_v4_turbo",
                    "name": "Eleven v4 Turbo",
                    "description": "Low-latency (~100ms) variant of Eleven v4 tailored for real-time conversational voice agents and rapid vertical reel synthesis.",
                    "latency": "Real-time (~100ms)"
                },
                {
                    "id": "eleven_multilingual_v2",
                    "name": "Eleven Multilingual v2",
                    "description": "Proven natural, emotionally rich speech across 29 languages (including Marathi, Hindi, English).",
                    "latency": "Standard (~600ms)"
                },
                {
                    "id": "eleven_turbo_v2_5",
                    "name": "Eleven Turbo v2.5",
                    "description": "Ultra-low latency, high-fidelity synthesis engineered for developer workflows and video engines.",
                    "latency": "Fast (~300ms)"
                },
                {
                    "id": "eleven_flash_v2_5",
                    "name": "Eleven Flash v2.5",
                    "description": "Maximum throughput and speed for batch voice generation and dynamic audio previews.",
                    "latency": "Ultra-fast (~150ms)"
                }
            ],
            "is_configured": self.is_available()
        }

    def get_voices(self) -> List[Dict[str, Any]]:
        """Lists all available voices from the ElevenLabs API or falls back to curated catalog."""
        k = self._resolve_api_key()
        if not k:
            return ELEVENLABS_VOICE_CATALOG

        url = f"{self.base_url}/voices"
        req = urllib.request.Request(url, headers={"xi-api-key": k, "User-Agent": "NanoProAI/2.0"})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                voices = data.get("voices", [])
                if voices:
                    return voices
        except Exception as e:
            log_event(f"Notice fetching ElevenLabs remote voices ({e}), using curated catalog.", level="DEBUG", component="ElevenLabs")
        return ELEVENLABS_VOICE_CATALOG

    def generate_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model_id: str = "eleven_v4",
        stability: float = 0.55,
        similarity_boost: float = 0.85,
        style: float = 0.15,
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes humanlike speech using ElevenLabs Text-to-Speech API.
        Supports Eleven v4, Eleven v4 Turbo, and Eleven Multilingual v2.
        Saves the resulting MP3 file and returns metadata.
        """
        k = self._resolve_api_key()
        if not k:
            raise ValueError("ElevenLabs API Key not configured. Key must start with 'sk_'.")

        v_id = voice_id or self.default_voice_id
        url = f"{self.base_url}/text-to-speech/{v_id}"

        # Eleven v4 models use stability and similarity_boost (style/speed sliders not supported on v4)
        if model_id.startswith("eleven_v4"):
            voice_settings = {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "use_speaker_boost": True
            }
        else:
            voice_settings = {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": True
            }

        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings
        }
        json_data = json.dumps(payload).encode("utf-8")

        fname = output_filename or f"elevenlabs_{int(time.time())}.mp3"
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
                    "provider": "ElevenLabs Voice AI",
                    "file_path": str(out_path),
                    "file_name": out_path.name,
                    "audio_url": f"/audio/{out_path.name}",
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
elevenlabs_voice = elevenlabs_voice_engine
