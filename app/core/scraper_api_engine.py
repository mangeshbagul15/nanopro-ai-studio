"""
Mangesh Nano Pro AI Studio - ScraperAPI E-Commerce & Anti-Captcha Scraping Engine
Provides residential/datacenter proxy rotation, headless JS rendering, and CAPTCHA bypass
for web scraping across Amazon, Flipkart, Walmart, and target websites.
"""

import os
import time
import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, Optional
from app.core.logger import log_event
from app.core.database import credentials_vault


class ScraperApiEngine:
    """
    Enterprise Web Scraping & Anti-Bot Bypass Engine.
    Powered by ScraperAPI with residential IP rotation and automatic CAPTCHA solving.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SCRAPERAPI_KEY", "")
        self.base_url = "https://api.scraperapi.com"

    def _resolve_api_key(self) -> str:
        if self.api_key and not self.api_key.startswith("••"):
            return self.api_key

        for s_name in ["SCRAPERAPI", "SCRAPERAPI_KEY", "SCRAPER_API"]:
            cred = credentials_vault.get_credential(s_name)
            if cred and cred.get("secret_value") and not cred["secret_value"].startswith("••"):
                self.api_key = cred["secret_value"]
                return self.api_key

        self.api_key = os.getenv("SCRAPERAPI_KEY", "")
        return self.api_key

    def is_available(self) -> bool:
        k = self._resolve_api_key()
        return bool(k and len(k) == 32)

    def get_account_status(self) -> Dict[str, Any]:
        """Returns account credits, concurrency limit, and billing cycle info."""
        k = self._resolve_api_key()
        if not k:
            return {"status": "error", "message": "ScraperAPI key is not configured"}

        url = f"{self.base_url}/account?api_key={k}"
        req = urllib.request.Request(url, headers={"User-Agent": "NanoPro-AI-Studio/2.0"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                data["_duration_ms"] = round((time.time() - t0) * 1000, 1)
                return data
        except Exception as e:
            log_event(f"ScraperAPI get_account_status error: {e}", level="ERROR", component="ScraperAPI")
            return {"status": "error", "message": str(e)}

    def scrape_url(
        self,
        target_url: str,
        render_js: bool = False,
        country_code: Optional[str] = None,
        premium: bool = False,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Scrapes a target website URL through ScraperAPI's rotating proxy network.
        Bypasses Cloudflare, Akamai, Datadome, and CAPTCHAs automatically.
        """
        k = self._resolve_api_key()
        if not k:
            raise ValueError("ScraperAPI key is not configured.")

        params = {
            "api_key": k,
            "url": target_url
        }
        if render_js:
            params["render"] = "true"
        if country_code:
            params["country_code"] = country_code.lower()
        if premium:
            params["premium"] = "true"

        qs = urllib.parse.urlencode(params)
        full_url = f"{self.base_url}?{qs}"

        t0 = time.time()
        try:
            req = urllib.request.Request(full_url, headers={"User-Agent": "NanoPro-AI-Studio/2.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                dur_ms = round((time.time() - t0) * 1000, 1)
                log_event(f"ScraperAPI fetched {len(body)} chars from '{target_url[:50]}' in {dur_ms}ms", component="ScraperAPI")
                return {
                    "status": "success",
                    "target_url": target_url,
                    "content_length": len(body),
                    "duration_ms": dur_ms,
                    "render_js": render_js,
                    "country_code": country_code,
                    "content": body
                }
        except urllib.error.HTTPError as e:
            err_msg = str(e)
            log_event(f"ScraperAPI HTTP {e.code}: {err_msg}", level="ERROR", component="ScraperAPI")
            raise RuntimeError(f"ScraperAPI Error ({e.code}): {err_msg}")
        except Exception as e:
            log_event(f"ScraperAPI Connection Error: {e}", level="ERROR", component="ScraperAPI")
            raise e

    def get_markdown_status(self) -> str:
        """Generates a clean Markdown status report of ScraperAPI."""
        acc = self.get_account_status()
        credits_left = acc.get("creditsLeft", 0)
        req_limit = acc.get("requestLimit", 0)
        concurrency = acc.get("concurrencyLimit", 0)
        status_badge = "🟢 **ONLINE & READY**" if credits_left > 0 else "🟡 **CREDITS EXHAUSTED**"

        lines = [
            f"### 🌐 ScraperAPI E-Commerce Scraping & Proxy Engine",
            f"**Engine Status:** {status_badge}",
            f"**Remaining Credits:** `{credits_left:,} / {req_limit:,}`",
            f"**Concurrency Limit:** `{concurrency} parallel requests`",
            f"**Capabilities Active:** Automatic Proxy Rotation, Headless Chrome Rendering, Anti-CAPTCHA",
            f"**Geotargeting Supported:** US, IN, UK, DE, FR, JP and 50+ countries",
            ""
        ]
        lines.append(f"> *Web Scraping powered by ScraperAPI Global Proxy Infrastructure*")
        return "\n".join(lines)


# Global Singleton instance
scraper_api_engine = ScraperApiEngine()
