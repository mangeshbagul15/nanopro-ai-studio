"""
Mangesh Nano Pro AI Studio - Giphy Stickers & Memes Provider
Enables auto-inserting trending animated stickers, emojis, and meme clips on 9:16 reels.
"""

import os
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

GIPHY_API_KEY = os.getenv("GIPHY_API_KEY", "")


def search_giphy_stickers(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search Giphy for transparent animated stickers to overlay on videos."""
    if not GIPHY_API_KEY:
        return []

    url = "https://api.giphy.com/v1/stickers/search"
    params = {
        "api_key": GIPHY_API_KEY,
        "q": query,
        "limit": min(limit, 10),
        "rating": "pg"
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            results = []
            for item in r.json().get("data", []):
                images = item.get("images", {})
                gif_url = images.get("original", {}).get("url") or images.get("fixed_height", {}).get("url")
                if gif_url:
                    results.append({
                        "id": item.get("id"),
                        "title": item.get("title"),
                        "url": gif_url
                    })
            return results
    except Exception as e:
        print(f"[Giphy] Sticker search error: {e}")

    return []


def search_giphy_gifs(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search Giphy for viral meme GIFs."""
    if not GIPHY_API_KEY:
        return []

    url = "https://api.giphy.com/v1/gifs/search"
    params = {
        "api_key": GIPHY_API_KEY,
        "q": query,
        "limit": min(limit, 10),
        "rating": "pg"
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            results = []
            for item in r.json().get("data", []):
                images = item.get("images", {})
                mp4_url = images.get("original", {}).get("mp4") or images.get("fixed_height", {}).get("mp4")
                results.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "mp4_url": mp4_url,
                    "gif_url": images.get("original", {}).get("url")
                })
            return results
    except Exception as e:
        print(f"[Giphy] GIF search error: {e}")

    return []
