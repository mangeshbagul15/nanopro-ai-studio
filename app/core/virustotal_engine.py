"""
Mangesh Nano Pro AI Studio - VirusTotal Threat Intelligence Engine
Provides defensive cybersecurity scanning, malware hash verification,
domain and IP threat intelligence, and URL security checks powered by VirusTotal API v3.
"""

import os
import time
import base64
import urllib.request
import urllib.error
import urllib.parse
import json
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import credentials_vault


class VirusTotalEngine:
    """
    Enterprise Threat Intelligence & Malware Analysis Engine.
    Leverages VirusTotal API v3 (70+ Antivirus & Security Vendors).
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("VIRUSTOTAL_API_KEY", "")
        self.base_url = "https://www.virustotal.com/api/v3"

    def _resolve_api_key(self) -> str:
        if self.api_key and not self.api_key.startswith("••"):
            return self.api_key
        # Check CredentialsVault
        for s_name in ["VIRUSTOTAL_API", "VIRUSTOTAL_API_KEY", "VIRUS_TOTAL"]:
            cred = credentials_vault.get_credential(s_name)
            if cred and cred.get("secret_value") and not cred["secret_value"].startswith("••"):
                self.api_key = cred["secret_value"]
                return self.api_key
        self.api_key = os.getenv("VIRUSTOTAL_API_KEY", "")
        return self.api_key

    def is_available(self) -> bool:
        k = self._resolve_api_key()
        return bool(k and len(k) == 64)

    def _api_get(self, endpoint: str, timeout: float = 12.0) -> Dict[str, Any]:
        k = self._resolve_api_key()
        if not k:
            raise ValueError("VirusTotal API key is not configured. Set VIRUSTOTAL_API_KEY in .env or CredentialsVault.")

        url = f"{self.base_url}{endpoint}"
        req = urllib.request.Request(
            url,
            headers={
                "x-apikey": k,
                "User-Agent": "NanoPro-AI-Studio/2.0 (CybersecurityLab)"
            }
        )

        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                dur_ms = round((time.time() - t0) * 1000, 1)
                data["_duration_ms"] = dur_ms
                return data
        except urllib.error.HTTPError as e:
            err_msg = str(e)
            try:
                err_data = json.loads(e.read().decode("utf-8"))
                err_msg = err_data.get("error", {}).get("message", err_msg)
            except Exception:
                pass
            log_event(f"VirusTotal HTTP {e.code}: {err_msg}", level="ERROR", component="VirusTotal")
            raise RuntimeError(f"VirusTotal Error ({e.code}): {err_msg}")
        except Exception as e:
            log_event(f"VirusTotal Connection Error: {e}", level="ERROR", component="VirusTotal")
            raise e

    def _calculate_verdict(self, stats: Dict[str, int]) -> str:
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        if malicious >= 3:
            return "MALICIOUS"
        elif malicious > 0 or suspicious >= 2:
            return "SUSPICIOUS"
        elif stats.get("harmless", 0) > 0 or stats.get("undetected", 0) > 0:
            return "CLEAN"
        return "UNKNOWN"

    def check_domain(self, domain: str) -> Dict[str, Any]:
        """
        Scans a domain for reputation, malicious flags, registrar, and categories.
        """
        clean_domain = domain.strip().lower()
        if clean_domain.startswith("http://") or clean_domain.startswith("https://"):
            clean_domain = urllib.parse.urlparse(clean_domain).netloc

        data = self._api_get(f"/domains/{clean_domain}")
        attrs = data.get("data", {}).get("attributes", {})
        stats = attrs.get("last_analysis_stats", {})
        verdict = self._calculate_verdict(stats)

        log_event(
            f"VirusTotal Domain scan for '{clean_domain}': Verdict={verdict} (Malicious: {stats.get('malicious', 0)})",
            component="VirusTotal"
        )

        return {
            "status": "success",
            "type": "domain",
            "target": clean_domain,
            "verdict": verdict,
            "reputation": attrs.get("reputation", 0),
            "stats": stats,
            "categories": attrs.get("categories", {}),
            "registrar": attrs.get("registrar", "Unknown"),
            "creation_date": attrs.get("creation_date"),
            "tags": attrs.get("tags", []),
            "total_engines": sum(stats.values()),
            "duration_ms": data.get("_duration_ms", 0)
        }

    def check_ip(self, ip_address: str) -> Dict[str, Any]:
        """
        Scans an IPv4/IPv6 address for threat history, malicious activity, and AS owner.
        """
        clean_ip = ip_address.strip()
        data = self._api_get(f"/ip_addresses/{clean_ip}")
        attrs = data.get("data", {}).get("attributes", {})
        stats = attrs.get("last_analysis_stats", {})
        verdict = self._calculate_verdict(stats)

        log_event(
            f"VirusTotal IP scan for '{clean_ip}': Verdict={verdict} (Malicious: {stats.get('malicious', 0)})",
            component="VirusTotal"
        )

        return {
            "status": "success",
            "type": "ip_address",
            "target": clean_ip,
            "verdict": verdict,
            "as_owner": attrs.get("as_owner", "Unknown"),
            "asn": attrs.get("asn"),
            "country": attrs.get("country", "Unknown"),
            "reputation": attrs.get("reputation", 0),
            "stats": stats,
            "tags": attrs.get("tags", []),
            "total_engines": sum(stats.values()),
            "duration_ms": data.get("_duration_ms", 0)
        }

    def check_file_hash(self, file_hash: str) -> Dict[str, Any]:
        """
        Checks a file hash (SHA256, MD5, or SHA1) against 70+ security vendors.
        """
        clean_hash = file_hash.strip().lower()
        data = self._api_get(f"/files/{clean_hash}")
        attrs = data.get("data", {}).get("attributes", {})
        stats = attrs.get("last_analysis_stats", {})
        verdict = self._calculate_verdict(stats)

        popular_threat = attrs.get("popular_threat_classification", {})

        log_event(
            f"VirusTotal Hash scan for '{clean_hash[:16]}...': Verdict={verdict} ({stats.get('malicious', 0)} vendors flagged)",
            component="VirusTotal"
        )

        return {
            "status": "success",
            "type": "file_hash",
            "target": clean_hash,
            "verdict": verdict,
            "file_name": attrs.get("meaningful_name") or (attrs.get("names", ["Unknown"])[0] if attrs.get("names") else "Unknown"),
            "file_size": attrs.get("size", 0),
            "type_description": attrs.get("type_description", "Unknown file type"),
            "stats": stats,
            "popular_threat": popular_threat,
            "reputation": attrs.get("reputation", 0),
            "total_engines": sum(stats.values()),
            "duration_ms": data.get("_duration_ms", 0)
        }

    def scan_url(self, url: str) -> Dict[str, Any]:
        """
        Analyzes a URL for malicious/phishing flags. Uses URL identifier (base64url without padding).
        """
        clean_url = url.strip()
        url_id = base64.urlsafe_b64encode(clean_url.encode()).decode().strip("=")
        data = self._api_get(f"/urls/{url_id}")
        attrs = data.get("data", {}).get("attributes", {})
        stats = attrs.get("last_analysis_stats", {})
        verdict = self._calculate_verdict(stats)

        log_event(
            f"VirusTotal URL scan for '{clean_url[:40]}...': Verdict={verdict} ({stats.get('malicious', 0)} vendors flagged)",
            component="VirusTotal"
        )

        return {
            "status": "success",
            "type": "url",
            "target": clean_url,
            "verdict": verdict,
            "stats": stats,
            "categories": attrs.get("categories", {}),
            "reputation": attrs.get("reputation", 0),
            "total_engines": sum(stats.values()),
            "duration_ms": data.get("_duration_ms", 0)
        }

    def get_markdown_threat_report(self, target_type: str, target: str) -> str:
        """
        Generates a clean, human-readable Markdown threat intelligence audit report.
        """
        try:
            t = target_type.lower()
            if t == "domain":
                res = self.check_domain(target)
            elif t in ["ip", "ip_address"]:
                res = self.check_ip(target)
            elif t in ["hash", "file_hash", "file"]:
                res = self.check_file_hash(target)
            elif t == "url":
                res = self.scan_url(target)
            else:
                return f"Unsupported target type: {target_type}. Use domain, ip, hash, or url."

            verdict = res["verdict"]
            stats = res["stats"]
            mal = stats.get("malicious", 0)
            susp = stats.get("suspicious", 0)
            clean = stats.get("harmless", 0) + stats.get("undetected", 0)
            total = res["total_engines"]

            badge = "🟢 **CLEAN / BENIGN**" if verdict == "CLEAN" else ("🟡 **SUSPICIOUS**" if verdict == "SUSPICIOUS" else "🔴 **CRITICAL THREAT / MALICIOUS**")

            lines = [
                f"### 🛡️ VirusTotal Threat Intelligence Audit Report",
                f"**Target ({target_type.upper()}):** `{target}`",
                f"**Security Verdict:** {badge}",
                f"**Detection Ratio:** `{mal} / {total} vendors flagged as malicious` (Suspicious: {susp}, Clean/Undetected: {clean})",
                f"**Reputation Score:** `{res.get('reputation', 0)}` | **Latency:** `{res.get('duration_ms', 0)}ms`",
                ""
            ]

            if t == "domain":
                lines.append(f"- **Registrar:** {res.get('registrar', 'Unknown')}")
                cats = list(res.get("categories", {}).values())
                if cats:
                    lines.append(f"- **Categories:** {', '.join(set(cats)[:4])}")
            elif t in ["ip", "ip_address"]:
                lines.append(f"- **AS Owner:** {res.get('as_owner', 'Unknown')} (ASN: {res.get('asn', 'N/A')})")
                lines.append(f"- **Country:** {res.get('country', 'Unknown')}")
            elif t in ["hash", "file_hash", "file"]:
                lines.append(f"- **File Name:** `{res.get('file_name', 'Unknown')}`")
                lines.append(f"- **File Size:** {res.get('file_size', 0):,} bytes")
                lines.append(f"- **Type:** {res.get('type_description', 'Unknown')}")
                threat_class = res.get("popular_threat", {}).get("suggested_threat_label")
                if threat_class:
                    lines.append(f"- **Threat Classification:** ⚠️ `{threat_class}`")

            lines.append("")
            lines.append(f"> *Intelligence powered by Google Chronicle VirusTotal v3 Enterprise API*")
            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ **VirusTotal Audit Error:** {str(e)}"


# Global Singleton instance
virustotal_engine = VirusTotalEngine()
