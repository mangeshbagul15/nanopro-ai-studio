"""
Mangesh Nano Pro AI Studio - Pixabay HD/4K Stock Video Provider
100% Free, Zero-Quota, Zero-Cost High-Definition B-Roll Video Engine.
Provides real cinematic videos for Tech, Coding, Cyber, Cloud, and AI reels.
"""

import os
import subprocess
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")
BASE_URL = "https://pixabay.com/api/videos/"

try:
    import imageio_ffmpeg
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_BIN = "ffmpeg"


def search_pixabay_videos(query: str, per_page: int = 5, video_type: str = "all") -> List[Dict[str, Any]]:
    """
    Search Pixabay for royalty-free videos matching query.
    Returns list of video objects with direct MP4 download URLs.
    Pixabay per_page must be between 3 and 200.
    """
    if not PIXABAY_API_KEY:
        return []

    # Ensure per_page conforms to Pixabay requirements (3 - 200)
    safe_per_page = max(3, min(per_page, 200))

    params = {
        "key": PIXABAY_API_KEY,
        "q": query.strip(),
        "per_page": safe_per_page,
        "video_type": video_type,
        "safesearch": "true"
    }

    try:
        r = requests.get(BASE_URL, params=params, timeout=12)
        if r.status_code == 200:
            data = r.json()
            hits = data.get("hits", [])
            results = []
            for hit in hits:
                vids = hit.get("videos", {})
                # Prefer medium (1080p) or small (720p) for high-speed download & 9:16 crop
                chosen = vids.get("medium") or vids.get("small") or vids.get("large")
                if chosen and chosen.get("url"):
                    results.append({
                        "id": hit.get("id"),
                        "tags": hit.get("tags"),
                        "duration": hit.get("duration"),
                        "url": chosen.get("url"),
                        "width": chosen.get("width"),
                        "height": chosen.get("height"),
                        "size": chosen.get("size")
                    })
            return results
        else:
            print(f"[Pixabay] Search HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"[Pixabay] Search error for '{query}': {e}")

    return []


def download_pixabay_clip(video_url: str, output_path: str) -> bool:
    """Download the Pixabay MP4 clip to disk."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        r = requests.get(video_url, stream=True, timeout=25)
        if r.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
            return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"[Pixabay] Download error: {e}")
    return False


def crop_to_vertical_9_16(input_path: str, output_path: str, duration: Optional[float] = None) -> bool:
    """
    Use local FFmpeg to crop and scale any horizontal/4K/HD video into
    a pristine 1080x1920 (9:16 vertical) mobile reel video.
    """
    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        # Filter: crop to 9:16 center, scale to 1080x1920
        vf_filter = "crop=ih*(9/16):ih,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
        cmd = [
            FFMPEG_BIN, "-y",
            "-i", input_path,
            "-vf", vf_filter,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-an"  # Remove stock audio, narration will be added
        ]
        if duration:
            cmd.extend(["-t", str(duration)])
        cmd.append(output_path)

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=40)
        return res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"[Pixabay] FFmpeg crop error: {e}")
        return False
