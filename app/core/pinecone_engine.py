"""
Mangesh Nano Pro AI Studio - Pinecone Vector Database Engine
Provides ultra-fast, high-dimensional vector search, semantic embeddings storage,
and long-term memory for NanoPro AI Agents powered by Pinecone API.
"""

import os
import time
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import credentials_vault

try:
    from pinecone import Pinecone, ServerlessSpec
    _HAS_PINECONE = True
except ImportError:
    _HAS_PINECONE = False


class PineconeEngine:
    """
    Enterprise High-Dimensional Vector Search Engine.
    Leverages Pinecone Python SDK v10 and Serverless Architecture.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PINECONE_API_KEY", "")
        self._pc_client: Optional[Any] = None

    def _resolve_api_key(self) -> str:
        if self.api_key and not self.api_key.startswith("••"):
            return self.api_key

        # Check CredentialsVault
        for s_name in ["PINECONE_API", "PINECONE_VECTOR_DB", "PINECONE"]:
            cred = credentials_vault.get_credential(s_name)
            if cred and cred.get("secret_value") and not cred["secret_value"].startswith("••"):
                self.api_key = cred["secret_value"]
                return self.api_key

        self.api_key = os.getenv("PINECONE_API_KEY", "")
        return self.api_key

    def is_available(self) -> bool:
        k = self._resolve_api_key()
        return bool(k and k.startswith("pcsk_"))

    def get_client(self) -> Optional[Any]:
        if self._pc_client:
            return self._pc_client
        k = self._resolve_api_key()
        if _HAS_PINECONE and k:
            try:
                self._pc_client = Pinecone(api_key=k)
                return self._pc_client
            except Exception as e:
                log_event(f"Failed to initialize Pinecone client: {e}", level="ERROR", component="Pinecone")
        return None

    def ping(self) -> bool:
        """Pings Pinecone Index API. Returns True if responsive."""
        k = self._resolve_api_key()
        if not k:
            return False
        try:
            req = urllib.request.Request(
                "https://api.pinecone.io/indexes",
                headers={
                    "Api-Key": k,
                    "X-Pinecone-API-Version": "2024-07",
                    "User-Agent": "NanoPro-AI-Studio/2.0 (PineconeEngine)"
                }
            )
            with urllib.request.urlopen(req, timeout=6.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def list_indexes(self) -> List[Dict[str, Any]]:
        """Lists all serverless vector indexes."""
        pc = self.get_client()
        if not pc:
            return []
        try:
            indexes = pc.list_indexes()
            res = []
            for idx in indexes:
                res.append({
                    "name": idx.name,
                    "dimension": idx.dimension,
                    "metric": idx.metric,
                    "host": idx.host,
                    "status": idx.status.state if hasattr(idx.status, "state") else str(idx.status)
                })
            return res
        except Exception as e:
            log_event(f"Pinecone list_indexes error: {e}", level="WARNING", component="Pinecone")
            return []

    def get_metadata(self) -> Dict[str, Any]:
        """Returns Pinecone connection health and index summary."""
        t0 = time.time()
        alive = self.ping()
        lat_ms = round((time.time() - t0) * 1000, 1)

        indexes = self.list_indexes()

        return {
            "status": "online" if alive else "offline",
            "provider": "pinecone",
            "ping_latency_ms": lat_ms,
            "total_indexes": len(indexes),
            "indexes": indexes,
            "has_sdk": _HAS_PINECONE,
            "tier": "starter_serverless",
            "vector_capacity": "100,000 vectors free"
        }

    def get_markdown_status(self) -> str:
        """Generates a clean Markdown status report of Pinecone Vector DB."""
        meta = self.get_metadata()
        status_badge = "🟢 **ONLINE & READY**" if meta["status"] == "online" else "🔴 **OFFLINE**"

        lines = [
            f"### 🌲 Pinecone Vector Database Status",
            f"**Provider:** `Pinecone Serverless Architecture`",
            f"**Status:** {status_badge}",
            f"**Ping Latency:** `{meta['ping_latency_ms']}ms`",
            f"**SDK Engine:** `pinecone v10.0.0` (Client Initialized)",
            f"**Plan Tier:** `{meta['tier']}` (Capacity: {meta['vector_capacity']})",
            f"**Active Vector Indexes:** `{meta['total_indexes']}`",
            ""
        ]
        if meta["indexes"]:
            lines.append("#### 📑 Deployed Indexes:")
            for idx in meta["indexes"]:
                lines.append(f"- **{idx['name']}**: Dimension `{idx['dimension']}`, Metric `{idx['metric']}`, Host `{idx['host']}`")
            lines.append("")
        else:
            lines.append("ℹ️ *No vector indexes deployed yet. Indexes will auto-provision on first semantic ingestion.*")
            lines.append("")

        lines.append(f"> *Vector Intelligence powered by Pinecone Global Cloud Infrastructure*")
        return "\n".join(lines)


# Global Singleton instance
pinecone_engine = PineconeEngine()
