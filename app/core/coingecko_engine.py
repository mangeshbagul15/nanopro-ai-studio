"""
Mangesh Nano Pro AI Studio - CoinGecko Crypto & Financial Market Intelligence Engine
Provides real-time cryptocurrency prices, market cap, 24h trends, exchange volumes,
and on-chain DEX analytics powered by CoinGecko API v3 and GeckoTerminal.
"""

import os
import time
import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import credentials_vault


class CoinGeckoEngine:
    """
    Enterprise Cryptocurrency & DEX Market Intelligence Engine.
    Supports CoinGecko Demo & Pro tiers with automatic Keyless Public fallback.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("COINGECKO_API_KEY", "")
        self.tier = os.getenv("COINGECKO_TIER", "demo").lower()
        self.base_url = "https://pro-api.coingecko.com/api/v3" if self.tier == "pro" else "https://api.coingecko.com/api/v3"

    def _resolve_api_key(self) -> str:
        if self.api_key and not self.api_key.startswith("••"):
            return self.api_key

        for s_name in ["COINGECKO_API", "COINGECKO_API_KEY", "COINGECKO"]:
            cred = credentials_vault.get_credential(s_name)
            if cred and cred.get("secret_value") and not cred["secret_value"].startswith("••"):
                self.api_key = cred["secret_value"]
                return self.api_key

        self.api_key = os.getenv("COINGECKO_API_KEY", "")
        return self.api_key

    def is_available(self) -> bool:
        # CoinGecko is always available (either with key or keyless public)
        return True

    def _api_get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, timeout: float = 10.0) -> Any:
        k = self._resolve_api_key()
        headers = {
            "User-Agent": "NanoPro-AI-Studio/2.0 (CoinGeckoEngine)",
            "Accept": "application/json"
        }
        if k:
            header_name = "x-cg-pro-api-key" if self.tier == "pro" else "x-cg-demo-api-key"
            headers[header_name] = k

        qs = urllib.parse.urlencode(params or {})
        url = f"{self.base_url}{endpoint}?{qs}" if qs else f"{self.base_url}{endpoint}"

        t0 = time.time()
        try:
            req = urllib.request.Request(url, headers=headers)
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
            log_event(f"CoinGecko HTTP {e.code}: {err_msg}", level="ERROR", component="CoinGecko")
            raise RuntimeError(f"CoinGecko Error ({e.code}): {err_msg}")
        except Exception as e:
            log_event(f"CoinGecko Connection Error: {e}", level="ERROR", component="CoinGecko")
            raise e

    def ping(self) -> bool:
        """Pings the CoinGecko API. Returns True if server is responsive."""
        try:
            data = self._api_get("/ping")
            return "gecko_says" in data
        except Exception:
            return False

    def get_prices(
        self,
        coin_ids: Optional[List[str]] = None,
        vs_currencies: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Retrieves real-time prices, 24h change, and market cap for requested coins.
        """
        ids = coin_ids or ["bitcoin", "ethereum", "solana", "binancecoin", "ripple", "cardano", "dogecoin"]
        currencies = vs_currencies or ["usd", "inr"]

        params = {
            "ids": ",".join(ids),
            "vs_currencies": ",".join(currencies),
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
            "include_last_updated_at": "true"
        }
        data = self._api_get("/simple/price", params=params)
        log_event(f"CoinGecko retrieved prices for {len(ids)} coins", component="CoinGecko")
        return data

    def get_top_markets(self, vs_currency: str = "usd", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves top cryptocurrency rankings by market capitalization with 24h change & ATH.
        """
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": max(1, min(limit, 250)),
            "page": 1,
            "sparkline": "false"
        }
        items = self._api_get("/coins/markets", params=params)
        return items if isinstance(items, list) else []

    def get_trending(self) -> Dict[str, Any]:
        """
        Retrieves top trending coins, NFTs, and categories searched in the last 24h.
        """
        return self._api_get("/search/trending")

    def search_asset(self, query: str) -> List[Dict[str, Any]]:
        """
        Resolves coin names or symbols to CoinGecko IDs.
        """
        data = self._api_get("/search", params={"query": query})
        return data.get("coins", [])[:10]

    def get_onchain_trending_pools(self) -> Dict[str, Any]:
        """
        Retrieves trending DEX on-chain liquidity pools via GeckoTerminal.
        """
        return self._api_get("/onchain/networks/trending_pools")

    def get_markdown_crypto_report(self) -> str:
        """
        Generates a clean, rich Markdown crypto market briefing for agents and users.
        """
        try:
            prices = self.get_prices(["bitcoin", "ethereum", "solana", "binancecoin", "ripple"])
            trending = self.get_trending()

            lines = [
                f"### 🪙 CoinGecko Real-Time Crypto & Financial Intelligence",
                f"**Engine Status:** 🟢 **LIVE & CONNECTED** | **Tier:** `{self.tier.upper()} Plan`",
                "",
                "| Coin | Price (USD) | Price (INR) | 24h Change | Market Cap (USD) |",
                "|---|---|---|---|---|"
            ]

            names = {
                "bitcoin": "Bitcoin (BTC)",
                "ethereum": "Ethereum (ETH)",
                "solana": "Solana (SOL)",
                "binancecoin": "BNB (BNB)",
                "ripple": "XRP (XRP)"
            }

            for cid, label in names.items():
                cinfo = prices.get(cid, {})
                if not cinfo:
                    continue
                usd_p = f"${cinfo.get('usd', 0):,}"
                inr_p = f"₹{cinfo.get('inr', 0):,}"
                chg = cinfo.get("usd_24h_change", 0)
                chg_str = f"🟢 +{chg:.2f}%" if chg >= 0 else f"🔴 {chg:.2f}%"
                mcap = f"${cinfo.get('usd_market_cap', 0):,.0f}" if cinfo.get('usd_market_cap') else "N/A"
                lines.append(f"| **{label}** | `{usd_p}` | `{inr_p}` | {chg_str} | {mcap} |")

            lines.append("")

            # Trending Coins
            t_coins = trending.get("coins", [])[:5]
            if t_coins:
                lines.append("🔥 **Top 5 Trending Coins (Past 24h):**")
                for c in t_coins:
                    item = c.get("item", {})
                    rank = item.get("market_cap_rank", "N/A")
                    lines.append(f"- **{item.get('name')}** (`{item.get('symbol')}`): Rank #{rank}")
                lines.append("")

            lines.append(f"> *Financial intelligence powered by CoinGecko API v3 & GeckoTerminal*")
            return "\n".join(lines)

        except Exception as e:
            return f"⚠️ **CoinGecko Crypto Audit Error:** {str(e)}"


# Global Singleton instance
coingecko_engine = CoinGeckoEngine()
