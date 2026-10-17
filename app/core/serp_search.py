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
        timeout: float = 15.0,
        extra_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes a real-time search via SerpAPI across multiple engines
        (google, google_images, amazon, youtube, etc.).
        """
        k = self._resolve_api_key()
        if not k:
            raise ValueError("SerpAPI Key is not configured. Set SERPAPI_API_KEY environment variable.")

        params = {
            "engine": engine,
            "api_key": k,
            "hl": hl,
            "gl": gl,
        }
        if location:
            params["location"] = location

        if engine == "amazon":
            params["k"] = query
            if "amazon_domain" not in (extra_params or {}):
                params["amazon_domain"] = "amazon.in"
        else:
            params["q"] = query
            params["num"] = max(1, min(num, 100))

        if extra_params:
            params.update(extra_params)

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

                res_count = len(data.get("organic_results", [])) or len(data.get("images_results", []))
                log_event(
                    f"SerpAPI [{engine}] search completed for '{query[:40]}' in {dur_ms}ms ({res_count} results)",
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

    def search_images(
        self,
        query: str,
        num: int = 10,
        location: str = "India",
        gl: str = "in",
        hl: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Executes Google Images search via SerpAPI (engine=google_images).
        Returns clean list of image objects with original high-res URLs, thumbnails, dimensions and sources.
        """
        data = self.search(
            query=query,
            engine="google_images",
            location=location,
            gl=gl,
            hl=hl,
            num=num
        )
        raw_images = data.get("images_results", [])
        images = []
        for img in raw_images[:num]:
            images.append({
                "position": img.get("position"),
                "title": img.get("title", ""),
                "link": img.get("link", ""),
                "source": img.get("source", ""),
                "thumbnail": img.get("thumbnail", ""),
                "original": img.get("original", ""),
                "width": img.get("original_width"),
                "height": img.get("original_height"),
                "is_product": img.get("is_product", False)
            })
        return images

    def search_products(
        self,
        query: str,
        amazon_domain: str = "amazon.in",
        num: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Searches products via SerpAPI (engine=amazon).
        Extracts product titles, ASINs, prices, ratings, and image thumbnails.
        """
        data = self.search(
            query=query,
            engine="amazon",
            extra_params={"amazon_domain": amazon_domain}
        )
        raw_products = data.get("organic_results", [])
        products = []
        for p in raw_products[:num]:
            price_val = p.get("price") or (p.get("prices", [{}])[0].get("value") if p.get("prices") else "N/A")
            products.append({
                "position": p.get("position"),
                "title": p.get("title", ""),
                "asin": p.get("asin", ""),
                "link": p.get("link", ""),
                "price": price_val,
                "rating": p.get("rating"),
                "reviews": p.get("reviews"),
                "thumbnail": p.get("thumbnail", "")
            })
        return products

    def download_image(self, image_url: str, output_path: str) -> bool:
        """Downloads an image from URL directly to disk."""
        try:
            req = urllib.request.Request(
                image_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NanoProAI/2.0"}
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                content = resp.read()
                if len(content) > 500:
                    with open(output_path, "wb") as f:
                        f.write(content)
                    log_event(f"Downloaded search image ({len(content)} bytes) to {output_path}", component="SerpAPI")
                    return True
            return False
        except Exception as e:
            log_event(f"Failed to download image from {image_url[:60]}: {e}", level="WARNING", component="SerpAPI")
            return False

    def get_markdown_image_gallery(self, query: str, num: int = 6) -> str:
        """
        Returns an inline visual Markdown gallery of images found via Google Images.
        """
        images = self.search_images(query=query, num=num)
        if not images:
            return f"No images found for *{query}*."

        lines = [f"### 🖼️ Image Search Gallery: *{query}*\n"]
        for idx, img in enumerate(images, start=1):
            title = img.get("title") or f"Image {idx}"
            orig = img.get("original") or img.get("thumbnail")
            thumb = img.get("thumbnail") or orig
            source = img.get("source") or "Web"
            lines.append(f"{idx}. **[{title}]({orig})** *(Source: {source})*")
            if thumb:
                lines.append(f"   ![{title}]({thumb})\n")
        return "\n".join(lines)

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
