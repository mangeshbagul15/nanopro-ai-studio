"""
Mangesh Nano Pro AI Studio - Unsplash 4K Cinematic Photography Provider
Provides royalty-free ultra high-resolution photos for video backdrops, thumbnails, and scenes.
"""

import os
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "glMAJsvLeD9e_jq5ZhJcnkWv8SqawBYBW_pZfCVEKKI")


def search_unsplash_photos(query: str, count: int = 5, orientation: str = "portrait") -> List[Dict[str, Any]]:
    """
    Search Unsplash for high-res photos.
    Default orientation is portrait (9:16 vertical reels).
    """
    if not UNSPLASH_ACCESS_KEY:
        return []

    url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    params = {
        "query": query,
        "per_page": min(count, 15),
        "orientation": orientation
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=12)
        if r.status_code == 200:
            results = []
            for item in r.json().get("results", []):
                urls = item.get("urls", {})
                regular_url = urls.get("regular") or urls.get("full")
                if regular_url:
                    results.append({
                        "id": item.get("id"),
                        "description": item.get("alt_description") or item.get("description"),
                        "url": regular_url,
                        "photographer": item.get("user", {}).get("name")
                    })
            return results
        else:
            print(f"[Unsplash] Search HTTP {r.status_code}: {r.text[:150]}")
    except Exception as e:
        print(f"[Unsplash] Search exception: {e}")

    return []


def download_unsplash_photo(image_url: str, output_path: str) -> bool:
    """Download Unsplash photo to disk."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        r = requests.get(image_url, timeout=20)
        if r.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(r.content)
            return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"[Unsplash] Download exception: {e}")
    return False
