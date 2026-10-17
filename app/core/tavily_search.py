"""
Mangesh Nano Pro AI Studio - Tavily AI Live Web Search Engine
Provides real-time internet search, factual retrieval, live news, and Remote MCP integration.
"""

import os
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import credentials_vault


class TavilySearchEngine:
    """
    High-performance, resilient live web search engine powered by Tavily AI.
    Delivers clean markdown, structured citations, and Remote MCP URL compatibility.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY", "")
        self.base_url = "https://api.tavily.com/search"

    def _resolve_api_key(self) -> str:
        if self.api_key and not self.api_key.startswith("••"):
            return self.api_key
        # Check CredentialsVault
        for s_name in ["TAVILY_SEARCH", "TAVILY_SEARCH_API"]:
            cred = credentials_vault.get_credential(s_name)
            if cred and cred.get("secret_value") and not cred["secret_value"].startswith("••"):
                self.api_key = cred["secret_value"]
                return self.api_key
        self.api_key = os.getenv("TAVILY_API_KEY", "")
        return self.api_key

    def is_available(self) -> bool:
        k = self._resolve_api_key()
        return bool(k and k.startswith("tvly-"))

    def get_mcp_url(self) -> str:
        k = self._resolve_api_key()
        return f"https://mcp.tavily.com/mcp/?tavilyApiKey={k}" if k else ""

    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_images: bool = False,
        timeout: float = 15.0
    ) -> Dict[str, Any]:
        """
        Executes a real-time web search via Tavily AI.
        Returns dictionary with query, results (title, url, content, score), and response_time.
        """
        k = self._resolve_api_key()
        if not k:
            raise ValueError("Tavily API Key is not configured. Set TAVILY_API_KEY environment variable.")

        t_start = time.time()
        payload = {
            "query": query,
            "max_results": max(1, min(max_results, 20)),
            "search_depth": search_depth,
            "include_images": include_images
        }

        # Try official tavily SDK first if installed
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=k)
            res = client.search(query=query, max_results=max_results, search_depth=search_depth)
            dur_ms = round((time.time() - t_start) * 1000, 1)
            res["duration_ms"] = dur_ms
            log_event(f"Tavily SDK Search completed for '{query[:40]}' in {dur_ms}ms ({len(res.get('results', []))} results)", component="TavilySearch")
            return res
        except Exception as sdk_err:
            log_event(f"Tavily SDK fallback to direct HTTP API ({sdk_err})", component="TavilySearch")

        # Direct HTTP API fallback
        req = urllib.request.Request(
            self.base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {k}",
                "User-Agent": "NanoPro-AI-Studio/2.0"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                dur_ms = round((time.time() - t_start) * 1000, 1)
                data["duration_ms"] = dur_ms
                log_event(f"Tavily HTTP Search completed for '{query[:40]}' in {dur_ms}ms ({len(data.get('results', []))} results)", component="TavilySearch")
                return data
        except urllib.error.HTTPError as e:
            err_msg = str(e)
            try:
                err_body = e.read().decode("utf-8")
                err_json = json.loads(err_body)
                err_msg = err_json.get("error", err_body)
            except Exception:
                pass
            log_event(f"Tavily Search HTTP Error ({e.code}): {err_msg}", level="ERROR", component="TavilySearch")
            raise RuntimeError(f"Tavily API Error ({e.code}): {err_msg}")
        except Exception as e:
            log_event(f"Tavily Search Connection Error: {e}", level="ERROR", component="TavilySearch")
            raise e

    def get_markdown_summary(self, query: str, max_results: int = 5) -> str:
        """
        Executes web search and formats results into clean, readable Markdown with clickable citations.
        """
        res = self.search(query, max_results=max_results)
        results = res.get("results", [])
        if not results:
            return f"No live web results found for query: *{query}*."

        lines = [f"### 🌐 Live Web Search Results: *{query}*\n"]
        for idx, r in enumerate(results, start=1):
            title = r.get("title", "Source")
            url = r.get("url", "#")
            content = r.get("content", "").strip()
            lines.append(f"**{idx}. [{title}]({url})**")
            lines.append(f"> {content}\n")

        return "\n".join(lines)


# Global Singleton instance
tavily_search_engine = TavilySearchEngine()
