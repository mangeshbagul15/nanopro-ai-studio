"""
Mangesh Nano Pro AI Studio - Freesound SFX & BGM Audio Engine
100% Free, Zero-Quota Cinematic Sound Effects & Audio Transition Provider.
Enables Hollywood-style sound transitions (Whoosh, Glitch, Impact, Cyber Beeps).
"""

import os
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

FREESOUND_API_KEY = os.getenv("FREESOUND_API_KEY", "Gr6WV4n8ixUaW1skiZ8SFSyAPRvPcwHFJWfZI4Ws")
BASE_URL = "https://freesound.org/apiv2/search/text/"


def search_sound_effects(query: str, count: int = 5, max_duration: float = 6.0) -> List[Dict[str, Any]]:
    """
    Search Freesound for sound effects and background ambience.
    Returns high-quality MP3 preview URLs that can be directly downloaded without OAuth.
    """
    if not FREESOUND_API_KEY:
        return []

    params = {
        "query": query,
        "token": FREESOUND_API_KEY,
        "fields": "id,name,previews,duration,tags",
        "filter": f"duration:[0.5 TO {max_duration}]",
        "page_size": min(count, 15)
    }

    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        if r.status_code == 200:
            results = []
            for hit in r.json().get("results", []):
                previews = hit.get("previews", {})
                mp3_url = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")
                if mp3_url:
                    results.append({
                        "id": hit.get("id"),
                        "name": hit.get("name"),
                        "duration": hit.get("duration"),
                        "mp3_url": mp3_url
                    })
            return results
    except Exception as e:
        print(f"[Freesound] Search error: {e}")

    return []


def download_sound_effect(mp3_url: str, output_path: str) -> bool:
    """Download the high-quality sound effect MP3 to disk."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        r = requests.get(mp3_url, stream=True, timeout=15)
        if r.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=16384):
                    if chunk:
                        f.write(chunk)
            return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"[Freesound] Download error: {e}")
    return False


def get_cached_sfx(category: str = "whoosh") -> Optional[str]:
    """Retrieve or download a standard transition sound effect for instant video cutting."""
    cache_dir = os.path.abspath("data/cache/sfx")
    os.makedirs(cache_dir, exist_ok=True)
    target_path = os.path.join(cache_dir, f"{category}.mp3")

    if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
        return target_path

    # Search and download fresh
    hits = search_sound_effects(category, count=3, max_duration=3.5)
    if hits:
        if download_sound_effect(hits[0]["mp3_url"], target_path):
            return target_path

    return None
