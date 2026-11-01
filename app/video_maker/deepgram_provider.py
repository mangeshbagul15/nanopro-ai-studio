"""
Mangesh Nano Pro AI Studio - Deepgram Aura TTS & Nova-2 STT Provider
Enables ultra-realistic conversational human speech and word-level animated subtitles.
"""

import os
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "4748f50fe427e9060b7fb85661355348aefe1121")


def generate_deepgram_speech(text: str, output_path: str, voice: str = "aura-asteria-en") -> bool:
    """
    Generate realistic human speech via Deepgram Aura TTS.
    Saves audio directly to MP3.
    """
    if not DEEPGRAM_API_KEY:
        return False

    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    url = f"https://api.deepgram.com/v1/speak?model={voice}"

    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        if r.status_code == 200 and len(r.content) > 100:
            with open(output_path, "wb") as f:
                f.write(r.content)
            return True
        else:
            print(f"[Deepgram TTS] Error {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"[Deepgram TTS] Request failed: {e}")

    return False


def transcribe_audio_with_timestamps(audio_path: str) -> Optional[Dict[str, Any]]:
    """
    Transcribe audio file to get word-level timestamps for animated captions.
    """
    if not DEEPGRAM_API_KEY or not os.path.exists(audio_path):
        return None

    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "audio/mp3"
    }
    url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&punctuate=true"

    try:
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        r = requests.post(url, headers=headers, data=audio_bytes, timeout=30)
        if r.status_code == 200:
            return r.json()
        else:
            print(f"[Deepgram STT] Error {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"[Deepgram STT] Transcription failed: {e}")

    return None
