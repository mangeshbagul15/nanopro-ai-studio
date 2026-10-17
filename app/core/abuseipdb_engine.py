"""
Mangesh Nano Pro AI Studio - AbuseIPDB Threat Intelligence Engine
Provides real-time IP reputation checks, abuse reports, honeypot telemetry,
and high-risk malicious IP blacklist retrieval powered by the AbuseIPDB API v2.
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


class AbuseIPDBEngine:
    """
    Enterprise IP Threat Intelligence & Blacklist Verification Engine.
    Leverages AbuseIPDB API v2 to protect infrastructure against brute-force, bots, and DDoS.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ABUSEIPDB_API_KEY", "")
        self.base_url = "https://api.abuseipdb.com/api/v2"

    def _resolve_api_key(self) -> str:
        if self.api_key and not self.api_key.startswith("••"):
            return self.api_key
        # Check CredentialsVault
        for s_name in ["ABUSEIPDB_API", "ABUSEIPDB_API_KEY", "ABUSEIPDB"]:
            cred = credentials_vault.get_credential(s_name)
            if cred and cred.get("secret_value") and not cred["secret_value"].startswith("••"):
                self.api_key = cred["secret_value"]
                return self.api_key
        self.api_key = os.getenv("ABUSEIPDB_API_KEY", "")
        return self.api_key

    def is_available(self) -> bool:
        k = self._resolve_api_key()
        return bool(k and len(k) >= 40)

    def _api_get(self, path: str, params: Optional[Dict[str, Any]] = None, timeout: float = 12.0) -> Dict[str, Any]:
        k = self._resolve_api_key()
        if not k:
            raise ValueError("AbuseIPDB API key is not configured. Set ABUSEIPDB_API_KEY in .env or CredentialsVault.")

        query_str = urllib.parse.urlencode(params or {})
        url = f"{self.base_url}{path}?{query_str}" if query_str else f"{self.base_url}{path}"

        req = urllib.request.Request(
            url,
            headers={
                "Key": k,
                "Accept": "application/json",
                "User-Agent": "NanoPro-AI-Studio/2.0 (AbuseIPDBEngine)"
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
                errors = err_data.get("errors", [])
                if errors and isinstance(errors, list):
                    err_msg = errors[0].get("detail", err_msg)
            except Exception:
                pass
            log_event(f"AbuseIPDB HTTP {e.code}: {err_msg}", level="ERROR", component="AbuseIPDB")
            raise RuntimeError(f"AbuseIPDB Error ({e.code}): {err_msg}")
        except Exception as e:
            log_event(f"AbuseIPDB Connection Error: {e}", level="ERROR", component="AbuseIPDB")
            raise e

    def _calculate_verdict(self, score: int, is_whitelisted: bool) -> str:
        if is_whitelisted:
            return "WHITELISTED_BENIGN"
        if score >= 75:
            return "CRITICAL_MALICIOUS"
        elif score >= 25:
            return "SUSPICIOUS"
        elif score > 0:
            return "LOW_RISK"
        return "CLEAN"

    def check_ip(self, ip_address: str, max_age_in_days: int = 90, verbose: bool = False) -> Dict[str, Any]:
        """
        Queries AbuseIPDB for IP reputation, confidence score, and abuse reports.
        """
        clean_ip = ip_address.strip()
        params = {
            "ipAddress": clean_ip,
            "maxAgeInDays": max(1, min(max_age_in_days, 365))
        }
        if verbose:
            params["verbose"] = "true"

        data = self._api_get("/check", params=params)
        ip_data = data.get("data", {})
        score = ip_data.get("abuseConfidenceScore", 0)
        whitelisted = ip_data.get("isWhitelisted", False)
        verdict = self._calculate_verdict(score, whitelisted)

        log_event(
            f"AbuseIPDB check for {clean_ip}: Score={score}%, Verdict={verdict}, Reports={ip_data.get('totalReports', 0)}",
            component="AbuseIPDB"
        )

        return {
            "status": "success",
            "ipAddress": clean_ip,
            "verdict": verdict,
            "abuseConfidenceScore": score,
            "isWhitelisted": whitelisted,
            "countryCode": ip_data.get("countryCode", "Unknown"),
            "usageType": ip_data.get("usageType", "Unknown"),
            "isp": ip_data.get("isp", "Unknown"),
            "domain": ip_data.get("domain", ""),
            "hostnames": ip_data.get("hostnames", []),
            "totalReports": ip_data.get("totalReports", 0),
            "numDistinctUsers": ip_data.get("numDistinctUsers", 0),
            "lastReportedAt": ip_data.get("lastReportedAt"),
            "duration_ms": data.get("_duration_ms", 0)
        }

    def get_blacklist(self, confidence_minimum: int = 100, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Retrieves the global list of high-confidence malicious IPs attacking internet infrastructure.
        """
        params = {
            "confidenceMinimum": max(25, min(confidence_minimum, 100)),
            "limit": max(1, min(limit, 10000))
        }
        data = self._api_get("/blacklist", params=params)
        items = data.get("data", [])
        log_event(f"Retrieved {len(items)} malicious IPs from AbuseIPDB blacklist (min confidence {confidence_minimum}%)", component="AbuseIPDB")
        return items

    def get_markdown_report(self, ip_address: str) -> str:
        """
        Generates a clean, human-readable Markdown IP threat report.
        """
        try:
            res = self.check_ip(ip_address)
            score = res["abuseConfidenceScore"]
            verdict = res["verdict"]

            badge = "🟢 **CLEAN / BENIGN**" if verdict == "CLEAN" else (
                "🛡️ **WHITELISTED (TRUSTED)**" if verdict == "WHITELISTED_BENIGN" else (
                    "🟡 **SUSPICIOUS (ELEVATED RISK)**" if verdict in ["LOW_RISK", "SUSPICIOUS"] else
                    "🔴 **CRITICAL THREAT / ACTIVE ATTACKER**"
                )
            )

            lines = [
                f"### 🛡️ AbuseIPDB Threat Intelligence Audit",
                f"**Target IP:** `{res['ipAddress']}`",
                f"**Security Verdict:** {badge}",
                f"**Abuse Confidence Score:** `{score}%`",
                f"**ISP / Carrier:** {res['isp']} ({res['usageType']})",
                f"**Country:** `{res['countryCode']}` | **Domain:** `{res['domain'] or 'N/A'}`",
                f"**Total Abuse Reports:** `{res['totalReports']:,}` (Reported by `{res['numDistinctUsers']}` distinct security analysts/honeypots)",
                ""
            ]

            if res.get("lastReportedAt"):
                lines.append(f"⏱️ **Last Attack Reported:** `{res['lastReportedAt']}`")

            if score >= 75:
                lines.append(f"⚠️ **Action Required:** IP has a critical abuse confidence score. **Recommendation: Immediate Firewall Drop / Block.**")
            elif verdict == "WHITELISTED_BENIGN":
                lines.append(f"✅ **Safe:** Verified public DNS/CDN or whitelisted benevolent infrastructure.")

            lines.append("")
            lines.append(f"> *Intelligence powered by AbuseIPDB API v2* | Latency: `{res.get('duration_ms', 0)}ms`")
            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ **AbuseIPDB Audit Error for {ip_address}:** {str(e)}"


# Global Singleton instance
abuseipdb_engine = AbuseIPDBEngine()
