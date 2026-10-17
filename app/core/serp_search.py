"""
Mangesh Nano Pro AI Studio - SerpAPI Google Search Engine
Provides direct Google Search results, Knowledge Graphs, Google Maps,
and organic SERP intelligence for NanoPro AI Agents.
"""

import os
import json
import time
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import credentials_vault


class SerpApiEngine:
    """
    High-performance, resilient Google Search API powered by SerpAPI.
    Retrieves real-time organic Google search results, Knowledge Graphs, and answers.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY", "")
        self.base_url = "https://serpapi.com/search.json"

    def _resolve_api_key(self) -> str:
        if self.api_key and not self.api_key.startswith("••"):
            return self.api_key
        # Check CredentialsVault
        for s_name in ["SERPAPI_GOOGLE_SEARCH_API", "SERPAPI_API_KEY", "SERP_API"]:
            cred = credentials_vault.get_credential(s_name)
            if cred and cred.get("secret_value") and not cred["secret_value"].startswith("••"):
                self.api_key = cred["secret_value"]
                return self.api_key
        self.api_key = os.getenv("SERPAPI_API_KEY", "")
        return self.api_key

    def is_available(self) -> bool:
        k = self._resolve_api_key()
        return bool(k and len(k) >= 32)

    def search(
        self,
        query: str,
        engine: str = "google",
        location: str = "India",
        hl: str = "en",
        gl: str = "in",
        num: int = 5,
        timeout: float = 15.0
    ) -> Dict[str, Any]:
        """
        Executes a real-time Google search via SerpAPI.
        Returns parsed dictionary with organic results, knowledge graph, and answer box.
        """
        k = self._resolve_api_key()
        if not k:
            raise ValueError("SerpAPI Key is not configured. Set SERPAPI_API_KEY environment variable.")

        params = {
            "q": query,
            "engine": engine,
            "api_key": k,
            "location": location,
            "hl": hl,
            "gl": gl,
            "num": max(1, min(num, 20))
        }
        encoded_query = urllib.parse.urlencode(params)
        full_url = f"{self.base_url}?{encoded_query}"

        t_start = time.time()
        try:
            req = urllib.request.Request(
                full_url,
                headers={"User-Agent": "NanoPro-AI-Studio/2.0"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                dur_ms = round((time.time() - t_start) * 1000, 1)
                data["duration_ms"] = dur_ms

                organic = data.get("organic_results", [])
                log_event(
                    f"SerpAPI Google Search completed for '{query[:40]}' in {dur_ms}ms ({len(organic)} results)",
                    component="SerpAPI"
                )
                return data

        except urllib.error.HTTPError as e:
            err_msg = str(e)
            try:
                err_body = e.read().decode("utf-8")
                err_json = json.loads(err_body)
                err_msg = err_json.get("error", err_body)
            except Exception:
                pass
            log_event(f"SerpAPI HTTP Error ({e.code}): {err_msg}", level="ERROR", component="SerpAPI")
            raise RuntimeError(f"SerpAPI Error ({e.code}): {err_msg}")
        except Exception as e:
            log_event(f"SerpAPI Connection Error: {e}", level="ERROR", component="SerpAPI")
            raise e

    def get_organic_results(self, query: str, num: int = 5) -> List[Dict[str, Any]]:
        """Extracts list of clean organic search results (title, link, snippet)."""
        data = self.search(query=query, num=num)
        results = []
        for item in data.get("organic_results", []):
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "position": item.get("position", 0)
            })
        return results

    def get_knowledge_graph(self, query: str) -> Optional[Dict[str, Any]]:
        """Extracts Google Knowledge Graph if available for the query."""
        data = self.search(query=query, num=1)
        return data.get("knowledge_graph")

    def get_markdown_summary(self, query: str, num: int = 5) -> str:
        """
        Executes Google search and returns clean Markdown with citations and knowledge card.
        """
        data = self.search(query=query, num=num)
        lines = [f"### 🔍 Google Search Results: *{query}*\n"]

        # 1. Answer Box / Knowledge Graph if available
        kg = data.get("knowledge_graph")
        if kg:
            title = kg.get("title", "")
            kg_type = kg.get("type", "")
            desc = kg.get("description", "")
            lines.append(f"**📌 Knowledge Card: {title} ({kg_type})**\n> {desc}\n")

        ans_box = data.get("answer_box")
        if ans_box:
            ans = ans_box.get("answer") or ans_box.get("snippet", "")
            lines.append(f"**💡 Direct Answer:** {ans}\n")

        # 2. Organic Results
        organic = data.get("organic_results", [])
        if not organic:
            lines.append(f"No organic search results found for: *{query}*.")
        else:
            for idx, r in enumerate(organic[:num], start=1):
                title = r.get("title", "Source")
                link = r.get("link", "#")
                snippet = r.get("snippet", "").strip()
                lines.append(f"**{idx}. [{title}]({link})**")
                if snippet:
                    lines.append(f"> {snippet}\n")

        return "\n".join(lines)


# Global Singleton instance
serp_api_engine = SerpApiEngine()
