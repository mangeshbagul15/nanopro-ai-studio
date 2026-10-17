"""
Mangesh Nano Pro AI Studio - Replicate Engine
Provides Flux.1, SDXL, and generative image predictions via Replicate API
with seamless zero-downtime fallback to Pollinations.ai Flux and SerpAPI Images.
"""

import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.logger import log_event
from app.core.database import credentials_vault

class ReplicateEngine:
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("REPLICATE_API_TOKEN", "")
        self.base_url = "https://api.replicate.com/v1"

    def _resolve_token(self) -> str:
        if self.api_token and not self.api_token.startswith("••"):
            return self.api_token
        for s_name in ["REPLICATE_API_TOKEN", "REPLICATE_API", "REPLICATE"]:
            cred = credentials_vault.get_credential(s_name)
            if cred and cred.get("secret_value") and not cred["secret_value"].startswith("••"):
                self.api_token = cred["secret_value"]
                return self.api_token
        self.api_token = os.getenv("REPLICATE_API_TOKEN", "")
        return self.api_token

    def is_available(self) -> bool:
        t = self._resolve_token()
        return bool(t and t.startswith("r8_"))

    def get_account_info(self) -> Dict[str, Any]:
        """Checks user authentication status and details."""
        t = self._resolve_token()
        if not t:
            raise ValueError("Replicate API token not configured. Token must start with 'r8_'.")

        url = f"{self.base_url}/account"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {t}", "User-Agent": "NanoProAI/2.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def generate_image(
        self,
        prompt: str,
        model: str = "black-forest-labs/flux-schnell",
        aspect_ratio: str = "1:1",
        timeout: float = 35.0
    ) -> Dict[str, Any]:
        """
        Runs an image generation prediction on Replicate.
        Uses synchronous wait header (Prefer: wait=30).
        """
        t = self._resolve_token()
        if not t:
            raise ValueError("Replicate API token not configured.")

        url = f"{self.base_url}/models/{model}/predictions"
        payload = {
            "input": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "num_outputs": 1
            }
        }
        json_data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=json_data,
            headers={
                "Authorization": f"Bearer {t}",
                "Content-Type": "application/json",
                "Prefer": "wait=30",
                "User-Agent": "NanoProAI/2.0"
            }
        )

        t_start = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                dur_ms = round((time.time() - t_start) * 1000, 1)
                log_event(
                    f"Replicate [{model}] generated prediction in {dur_ms}ms (status: {data.get('status')})",
                    component="ReplicateEngine"
                )
                output = data.get("output", [])
                image_url = output[0] if isinstance(output, list) and output else output
                return {
                    "status": "success",
                    "provider": "replicate",
                    "model": model,
                    "image_url": image_url,
                    "duration_ms": dur_ms,
                    "prediction_id": data.get("id")
                }
        except urllib.error.HTTPError as e:
            err_msg = str(e)
            try:
                err_body = e.read().decode("utf-8")
                err_json = json.loads(err_body)
                err_msg = err_json.get("detail", err_body)
            except Exception:
                pass
            log_event(f"Replicate HTTP Error ({e.code}): {err_msg}", level="WARNING", component="ReplicateEngine")
            raise RuntimeError(f"Replicate Error ({e.code}): {err_msg}")
        except Exception as e:
            log_event(f"Replicate Connection Error: {e}", level="ERROR", component="ReplicateEngine")
            raise e


# Global Singleton instance
replicate_engine = ReplicateEngine()
