"""
Mangesh Nano Pro AI Studio - Jina AI Reader & Web Scraping Engine
Provides high-fidelity extraction of any URL into clean, advertisement-free Markdown
for accurate LLM reasoning, code analysis, and document comprehension.
"""

import os
import json
import time
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, Optional
from app.core.logger import log_event
from app.core.database import credentials_vault


class JinaReaderEngine:
    """
    High-performance live web scraping and extraction engine powered by Jina AI Reader API.
    Converts any public webpage, news article, PDF, or documentation into clean Markdown.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("JINA_API_KEY", "")
        self.base_reader_url = "https://r.jina.ai"
        self.base_search_url = "https://s.jina.ai"

    def _resolve_api_key(self) -> str:
        if self.api_key and not self.api_key.startswith("••"):
            return self.api_key
        # Check CredentialsVault
        cred = credentials_vault.get_credential("JINA_AI_API")
        if cred and cred.get("secret_value") and not cred["secret_value"].startswith("••"):
            self.api_key = cred["secret_value"]
            return self.api_key
        self.api_key = os.getenv("JINA_API_KEY", "")
        return self.api_key

    def is_available(self) -> bool:
        k = self._resolve_api_key()
        return bool(k and k.startswith("jina_"))

    def read_url(
        self,
        target_url: str,
        timeout: float = 25.0,
        return_format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Extracts clean, structured text and markdown from any URL.
        Returns: {
            "title": str,
            "url": str,
            "content": str,
            "duration_ms": float,
            "status": "success"
        }
        """
        target_url = target_url.strip()
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = "https://" + target_url

        k = self._resolve_api_key()
        headers = {
            "Accept": "application/json",
            "X-Return-Format": return_format,
            "User-Agent": "NanoPro-AI-Studio/2.0"
        }
        if k:
            headers["Authorization"] = f"Bearer {k}"

        api_endpoint = f"{self.base_reader_url}/{target_url}"
        t_start = time.time()

        try:
            req = urllib.request.Request(api_endpoint, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resp_bytes = resp.read()
                dur_ms = round((time.time() - t_start) * 1000, 1)

                try:
                    data = json.loads(resp_bytes.decode("utf-8"))
                    payload = data.get("data", data)
                    result = {
                        "title": payload.get("title", ""),
                        "url": payload.get("url", target_url),
                        "content": payload.get("content", ""),
                        "description": payload.get("description", ""),
                        "duration_ms": dur_ms,
                        "status": "success"
                    }
                except Exception:
                    # Raw markdown fallback
                    raw_text = resp_bytes.decode("utf-8", errors="ignore")
                    result = {
                        "title": target_url,
                        "url": target_url,
                        "content": raw_text,
                        "description": "",
                        "duration_ms": dur_ms,
                        "status": "success"
                    }

                log_event(
                    f"Jina Reader extracted '{target_url[:50]}' in {dur_ms}ms ({len(result.get('content', ''))} chars)",
                    component="JinaReader"
                )
                return result

        except urllib.error.HTTPError as e:
            err_msg = str(e)
            try:
                err_body = e.read().decode("utf-8")
                err_json = json.loads(err_body)
                err_msg = err_json.get("message", err_body)
            except Exception:
                pass
            log_event(f"Jina Reader HTTP Error ({e.code}): {err_msg}", level="ERROR", component="JinaReader")
            raise RuntimeError(f"Jina Reader API Error ({e.code}): {err_msg}")
        except Exception as e:
            log_event(f"Jina Reader Connection Error: {e}", level="ERROR", component="JinaReader")
            raise e

    def get_clean_markdown(self, target_url: str, max_chars: int = 15000) -> str:
        """
        Convenience method to retrieve clean markdown capped to max_chars.
        """
        res = self.read_url(target_url)
        content = res.get("content", "").strip()
        if len(content) > max_chars:
            content = content[:max_chars] + f"\n\n... [Content truncated at {max_chars} characters for AI context window]"
        return content

    def search_web(self, query: str, timeout: float = 25.0) -> Dict[str, Any]:
        """
        Uses Jina AI Search (s.jina.ai) to search the web and return markdown directly.
        """
        k = self._resolve_api_key()
        encoded_query = urllib.parse.quote(query)
        api_endpoint = f"{self.base_search_url}/{encoded_query}"
        headers = {
            "Accept": "application/json",
            "User-Agent": "NanoPro-AI-Studio/2.0"
        }
        if k:
            headers["Authorization"] = f"Bearer {k}"

        t_start = time.time()
        try:
            req = urllib.request.Request(api_endpoint, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                dur_ms = round((time.time() - t_start) * 1000, 1)
                log_event(f"Jina Web Search completed for '{query[:40]}' in {dur_ms}ms", component="JinaSearch")
                return {
                    "query": query,
                    "results": data.get("data", []),
                    "duration_ms": dur_ms,
                    "status": "success"
                }
        except Exception as e:
            log_event(f"Jina Web Search error: {e}", level="ERROR", component="JinaSearch")
            raise e


# Global Singleton instance
jina_reader_engine = JinaReaderEngine()
