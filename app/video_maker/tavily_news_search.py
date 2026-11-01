"""
Mangesh Nano Pro AI Studio - Tavily Real-Time AI Search Engine
Enables fetching live trending breaking news, tech launches, and verified internet facts for viral reel scripts.
"""

import os
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "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")


def search_trending_topic(topic: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search live internet using Tavily AI Search.
    Returns cleaned list of news and factual summaries.
    """
    if not TAVILY_API_KEY:
        return []

    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": topic,
        "search_depth": "basic",
        "include_answer": True,
        "max_results": min(max_results, 5)
    }

    try:
        r = requests.post(url, json=payload, timeout=12)
        if r.status_code == 200:
            data = r.json()
            answer = data.get("answer")
            results = data.get("results", [])
            out = []
            if answer:
                out.append({"title": "AI Summary", "content": answer, "url": ""})
            for item in results:
                out.append({
                    "title": item.get("title"),
                    "content": item.get("content"),
                    "url": item.get("url")
                })
            return out
        else:
            print(f"[Tavily] Search HTTP {r.status_code}: {r.text[:150]}")
    except Exception as e:
        print(f"[Tavily] Search exception: {e}")

    return []
