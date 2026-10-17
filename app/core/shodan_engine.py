"""
Mangesh Nano Pro AI Studio - Shodan Internet Intelligence & Port Scanning Engine
Provides deep internet intelligence, external port scanning, banner analysis,
and IoT/server exposure assessment powered by the Shodan.io API.
"""

import os
import time
import urllib.request
import urllib.error
import urllib.parse
import json
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import credentials_vault


class ShodanEngine:
    """
    Enterprise Internet Exposure & Port Scanning Engine.
    Leverages Shodan.io API to audit internet-facing infrastructure and IoT devices.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SHODAN_API_KEY", "")
        self.base_url = "https://api.shodan.io"

    def _resolve_api_key(self) -> str:
        if self.api_key and not self.api_key.startswith("••"):
            return self.api_key
        # Check CredentialsVault
        for s_name in ["SHODAN_API", "SHODAN_API_KEY", "SHODAN"]:
            cred = credentials_vault.get_credential(s_name)
            if cred and cred.get("secret_value") and not cred["secret_value"].startswith("••"):
                self.api_key = cred["secret_value"]
                return self.api_key
        self.api_key = os.getenv("SHODAN_API_KEY", "")
        return self.api_key

    def is_available(self) -> bool:
        k = self._resolve_api_key()
        return bool(k and len(k) >= 20)

    def _api_get(self, path: str, params: Optional[Dict[str, Any]] = None, timeout: float = 12.0) -> Dict[str, Any]:
        k = self._resolve_api_key()
        if not k:
            raise ValueError("Shodan API key is not configured. Set SHODAN_API_KEY in .env or CredentialsVault.")

        query_params = {"key": k}
        if params:
            query_params.update(params)

        qs = urllib.parse.urlencode(query_params)
        url = f"{self.base_url}{path}?{qs}"

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "NanoPro-AI-Studio/2.0 (ShodanEngine)"}
        )

        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                dur_ms = round((time.time() - t0) * 1000, 1)
                if isinstance(data, dict):
                    data["_duration_ms"] = dur_ms
                return data
        except urllib.error.HTTPError as e:
            err_msg = str(e)
            try:
                err_data = json.loads(e.read().decode("utf-8"))
                err_msg = err_data.get("error", err_msg)
            except Exception:
                pass
            log_event(f"Shodan HTTP {e.code}: {err_msg}", level="ERROR", component="Shodan")
            raise RuntimeError(f"Shodan Error ({e.code}): {err_msg}")
        except Exception as e:
            log_event(f"Shodan Connection Error: {e}", level="ERROR", component="Shodan")
            raise e

    def get_api_info(self) -> Dict[str, Any]:
        """Returns account plan, query credits, and scan limits."""
        return self._api_get("/api-info")

    def get_my_ip(self) -> str:
        """Returns the public IP address of the requesting client."""
        k = self._resolve_api_key()
        url = f"{self.base_url}/tools/myip?key={k}"
        try:
            with urllib.request.urlopen(url, timeout=6.0) as resp:
                return resp.read().decode("utf-8").strip().replace('"', '')
        except Exception as e:
            return "Unknown"

    def host_lookup(self, ip: str, history: bool = False, minify: bool = False) -> Dict[str, Any]:
        """
        Retrieves complete host exposure profile from Shodan.
        Returns open ports, hostnames, organization, ISP, ASN, vulnerabilities (CVEs), and services.
        """
        clean_ip = ip.strip()
        params = {}
        if history:
            params["history"] = "true"
        if minify:
            params["minify"] = "true"

        data = self._api_get(f"/shodan/host/{clean_ip}", params=params)

        ports = data.get("ports", [])
        hostnames = data.get("hostnames", [])
        vulns = data.get("vulns", [])
        services = []

        for item in data.get("data", []):
            services.append({
                "port": item.get("port"),
                "transport": item.get("transport", "tcp"),
                "product": item.get("product", ""),
                "version": item.get("version", ""),
                "banner": (item.get("data", "")[:120] if item.get("data") else "").strip()
            })

        log_event(
            f"Shodan Host Lookup for {clean_ip}: {len(ports)} open ports, {len(vulns)} CVEs identified",
            component="Shodan"
        )

        return {
            "status": "success",
            "ip": clean_ip,
            "ports": ports,
            "total_open_ports": len(ports),
            "hostnames": hostnames,
            "org": data.get("org", "Unknown"),
            "isp": data.get("isp", "Unknown"),
            "asn": data.get("asn", "Unknown"),
            "os": data.get("os"),
            "country_name": data.get("country_name", "Unknown"),
            "country_code": data.get("country_code", ""),
            "city": data.get("city", "Unknown"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "vulnerabilities": vulns,
            "total_vulns": len(vulns),
            "services": services[:15],
            "last_update": data.get("last_update", ""),
            "duration_ms": data.get("_duration_ms", 0)
        }

    def get_markdown_host_report(self, ip: str) -> str:
        """
        Generates a clean, professional Markdown report of the host's internet exposure.
        """
        try:
            info = self.host_lookup(ip)
            ports = info.get("ports", [])
            vulns = info.get("vulnerabilities", [])
            services = info.get("services", [])

            lines = [
                f"### 🌐 Shodan Internet Exposure & Port Audit Report",
                f"**Target IP:** `{info['ip']}`",
                f"**Organization:** {info.get('org')} ({info.get('isp')})",
                f"**Location:** {info.get('city')}, {info.get('country_name')} (ASN: `{info.get('asn')}`)",
                f"**Total Open Ports Detected:** `{info.get('total_open_ports')}`",
                f"**Open Ports List:** `{', '.join(map(str, sorted(ports))) if ports else 'None Detected'}`",
                ""
            ]

            if vulns:
                lines.append(f"⚠️ **Known Vulnerabilities (CVEs Detected):** `{len(vulns)}`")
                for v in vulns[:8]:
                    lines.append(f"- 🔴 `{v}`")
                lines.append("")
            else:
                lines.append("✅ **Vulnerabilities:** No known public CVEs indexed on Shodan.")
                lines.append("")

            if services:
                lines.append("#### 🔌 Exposed Services & Banners:")
                for s in services[:6]:
                    prod_info = f" ({s['product']} {s['version']})".strip() if s.get('product') else ""
                    lines.append(f"- **Port {s['port']}/{s['transport']}**{prod_info}")
                    if s.get("banner"):
                        lines.append(f"  > `{s['banner'][:80]}...`")
                lines.append("")

            lines.append(f"> *Intelligence powered by Shodan.io Engine* | Latency: `{info.get('duration_ms', 0)}ms`")
            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ **Shodan Audit Error for {ip}:** {str(e)}"


# Global Singleton instance
shodan_engine = ShodanEngine()
