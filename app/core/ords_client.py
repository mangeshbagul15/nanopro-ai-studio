"""OAuth client for the NanoPro read-only Oracle APEX/ORDS reporting API."""
from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class ORDSClient:
    """Fetch protected reporting endpoints with an OAuth client-credentials token."""

    def __init__(self, connection_name: str = "ORACLE_APEX_23AI_CLOUD"):
        from app.core.connection_manager import connection_manager

        cfg = connection_manager.get_connection_config(connection_name, mask=False) or {}
        oauth_cfg = connection_manager.get_connection_config("NANOPRO_ORDS_REPORTING_CLIENT", mask=False) or cfg
        self.meta = cfg.get("metadata") or {}
        oauth_meta = oauth_cfg.get("metadata") or {}
        self.client_id = (oauth_meta.get("oauth_client_id") or self.meta.get("oauth_client_id") or oauth_cfg.get("username") or "").strip()
        self.client_secret = (oauth_cfg.get("secret_value") or "").strip()
        self.workspace = (self.meta.get("workspace") or "nanoprostudio").strip("/")
        configured_url = (self.meta.get("environment_url") or "https://apex.oracle.com/ords/").rstrip("/")
        self.base_url = configured_url
        endpoint = urllib.parse.urlparse(self.base_url)
        if endpoint.scheme != "https" or not endpoint.hostname:
            raise RuntimeError("The configured ORDS endpoint must be an HTTPS URL with a hostname.")
        self.hostname = endpoint.hostname
        self.port = endpoint.port or 443
        self.schema_alias = (self.meta.get("schema_alias") or self.workspace).strip("/")
        if not self.client_id or not self.client_secret:
            raise RuntimeError("NanoPro Vault needs the ORDS OAuth client ID and client secret for the APEX profile.")
        self.schema_url = f"{self.base_url}/{self.schema_alias}"

    def _request(
        self,
        url: str,
        *,
        headers: dict[str, str],
        phase: str,
        data: bytes | None = None,
    ) -> dict[str, Any]:
        request = urllib.request.Request(url, data=data, headers=headers, method="POST" if data is not None else "GET")
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                payload = response.read()
        except urllib.error.HTTPError as exc:
            # Never include response bodies or authorization material in errors/logs.
            raise RuntimeError(f"ORDS request failed with HTTP {exc.code}.") from None
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError(f"ORDS {phase} failed ({type(exc).__name__}).") from None
        try:
            return json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise RuntimeError("ORDS returned a non-JSON response; OAuth or REST access may be misconfigured.") from None

    def token(self) -> str:
        basic = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode("utf-8")).decode("ascii")
        data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("ascii")
        result = self._request(
            f"{self.schema_url}/oauth/token",
            headers={"Authorization": f"Basic {basic}", "Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
            phase="OAuth token request",
            data=data,
        )
        access_token = result.get("access_token")
        if not access_token:
            raise RuntimeError("ORDS OAuth response did not contain an access token.")
        return str(access_token)

    def get_items(self, path: str) -> list[dict[str, Any]]:
        relative = path.strip("/")
        if not relative or ".." in relative.split("/"):
            raise RuntimeError("The configured ORDS reporting route is invalid.")
        token = self.token()
        url = f"{self.schema_url}/{relative}/"
        items: list[dict[str, Any]] = []
        for _ in range(10000):
            page = self._request(
                url,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                phase="REST reporting request",
            )
            page_items = page.get("items")
            if not isinstance(page_items, list):
                raise RuntimeError("ORDS response is missing the expected items collection.")
            items.extend(row for row in page_items if isinstance(row, dict))
            next_link = next((link.get("href") for link in page.get("links", []) if link.get("rel") == "next"), None)
            if not next_link:
                return items
            parsed = urllib.parse.urlparse(next_link)
            expected = urllib.parse.urlparse(self.schema_url)
            if parsed.scheme != expected.scheme or parsed.netloc != expected.netloc or not parsed.path.startswith(expected.path + "/"):
                raise RuntimeError("ORDS pagination returned an unexpected destination; stopping safely.")
            url = next_link
        raise RuntimeError("ORDS pagination exceeded the safety limit.")

    def verify(self) -> dict[str, Any]:
        data = self.get_items("nanopro/v1/l2")
        return {"success": True, "rows": len(data), "endpoint": f"{self.schema_url}/nanopro/v1/l2/"}
