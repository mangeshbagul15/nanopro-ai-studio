"""Authoritative live database catalog injected into chat answers.

Chat models used to answer database/schema questions from model memory, which
invented warehouses that do not exist (BANK_DB, RAW_DATA, ANALYTICAL_DATA,
AUDIT_LOGS) even though Data Explorer showed a different, much smaller reality.
This module renders the same live snapshot the Explorer tree uses and turns it
into a system prompt the model must obey.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.logger import log_event

MAX_SCHEMAS_PER_DB = 60
MAX_TABLES_PER_SCHEMA = 60
MAX_TOTAL_TABLES = 500
# Introspection dials warehouses; a slightly longer cache keeps chat responsive
# while still reflecting tables created in the last minute or two.
CATALOG_TTL_SECONDS = 90.0

_EXPLORER_ENGINES = {"snowflake", "bigquery", "s3", "duckdb"}
_HIDDEN_SCHEMA_NAMES = {"INFORMATION_SCHEMA", "SNOWFLAKE", "SNOWFLAKE_SAMPLE_DATA", "TELEMETRY"}

_ENGINE_TERMS = (
    "bigquery|snowflake|duckdb|s3|lakehouse|postgres(?:ql)?|oracle|mysql|sqlite|"
    "warehouse|data\\s?lake"
)
_DB_TERMS = (
    "databases?|dbs?|datasets?|schemas?|tables?|engines?|connections?|catalog|explorer|"
    + _ENGINE_TERMS
    + "|डेटाबेस|डेटा\\s?बेस|स्कीमा|स्कीमाज|तक्ते|तक्ता|टेबल|कनेक्शन"
)
_ACTION_TERMS = (
    "list|show|which|what|how many|count|kit[iy]|kont[ai]|kay|ahe|ahet|kuthe|"
    "verify|check|validate|display|dakhav|dakhv|bagh|sang|"
    "आहे|आहेत|किती|कोणत|दाखव|सांग|बघ|बघा|पहा"
)

_INTENT_RE = re.compile(rf"\b(?:{_DB_TERMS})\b", re.IGNORECASE)
_ACTION_RE = re.compile(rf"\b(?:{_ACTION_TERMS})\b", re.IGNORECASE)
_ENGINE_RE = re.compile(rf"\b(?:{_ENGINE_TERMS})\b", re.IGNORECASE)
# SQL-style identifiers the user may ask about (BANK_DB, RAW_DATA, AUDIT_LOGS).
_OBJECT_RE = re.compile(r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\b")


def is_catalog_question(prompt: str) -> bool:
    """True when the answer depends on live database catalog facts."""
    text = (prompt or "").strip()
    if not text:
        return False
    if _OBJECT_RE.search(text):
        return True
    if not _INTENT_RE.search(text):
        return False
    return bool(_ACTION_RE.search(text) or _ENGINE_RE.search(text) or "?" in text)


def _visible_databases(raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    databases: List[Dict[str, Any]] = []
    for entry in raw:
        engine = str(entry.get("engine") or "").lower()
        if engine not in _EXPLORER_ENGINES:
            continue
        schemas: List[Dict[str, Any]] = []
        for schema in entry.get("schemas") or []:
            name = str(schema.get("name") or "").strip()
            if not name or any(part.strip().upper() in _HIDDEN_SCHEMA_NAMES for part in name.split(".")):
                continue
            tables = [
                str(table.get("name") or "").strip()
                for table in schema.get("tables") or []
                if str(table.get("name") or "").strip()
            ]
            schemas.append({"name": name, "tables": tables})
        databases.append({
            "id": entry.get("id") or engine,
            "name": entry.get("name") or engine.upper(),
            "engine": engine,
            "status": str(entry.get("status") or ""),
            "error": str(entry.get("error") or ""),
            "schemas": schemas,
        })
    return databases


def live_databases() -> List[Dict[str, Any]]:
    """Live connections rendered exactly as the Data Explorer tree shows them."""
    try:
        from app.core import live_catalog

        return _visible_databases(live_catalog.databases(ttl=CATALOG_TTL_SECONDS))
    except Exception as exc:  # pragma: no cover - defensive
        log_event(f"Live catalog context unavailable: {exc}", level="WARNING", component="ChatGrounding")
        return []


def _render(databases: List[Dict[str, Any]]) -> str:
    captured = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines = [f"LIVE DATA CATALOG (authoritative, captured {captured} UTC)"]
    if not databases:
        lines.append("No live database connection could be introspected in this process.")
        return "\n".join(lines)

    engine_counts: Dict[str, int] = {}
    for db in databases:
        engine_counts[db["engine"]] = engine_counts.get(db["engine"], 0) + 1
    summary = ", ".join(f"{engine}={count}" for engine, count in sorted(engine_counts.items()))
    total_schemas = sum(len(db["schemas"]) for db in databases)
    total_tables = sum(len(schema["tables"]) for db in databases for schema in db["schemas"])
    lines.append(
        f"Connections: {len(databases)} ({summary}) | visible schemas: {total_schemas} | visible tables: {total_tables}"
    )

    rendered_tables = 0
    for index, db in enumerate(databases, 1):
        status = db["status"] or "unknown"
        header = f"[{index}] {db['name']} | engine={db['engine']} | id={db['id']} | status={status}"
        if db["error"]:
            header += f" | error={db['error'][:160]}"
        lines.append(header)
        schemas = db["schemas"][:MAX_SCHEMAS_PER_DB]
        if not schemas:
            lines.append("    schemas: 0 (connection exists but exposes no schemas)")
            continue
        for schema in schemas:
            tables = schema["tables"]
            shown = tables[:MAX_TABLES_PER_SCHEMA]
            if rendered_tables >= MAX_TOTAL_TABLES:
                lines.append(f"    - {schema['name']}: (table list truncated for prompt size)")
                continue
            rendered_tables += len(shown)
            suffix = f", +{len(tables) - len(shown)} more" if len(tables) > len(shown) else ""
            listing = ", ".join(shown) if shown else "no tables"
            lines.append(f"    - {schema['name']}: {len(tables)} tables -> {listing}{suffix}")
        if len(db["schemas"]) > len(schemas):
            lines.append(f"    ... +{len(db['schemas']) - len(schemas)} more schemas")
    return "\n".join(lines)


_RULES = """RULES (non-negotiable):
1. For every question about databases, engines, connections, datasets, schemas, tables, columns, counts or storage, answer ONLY from the LIVE DATA CATALOG above. It is retrieved from the running system and overrides model memory.
2. Never invent database, dataset, schema or table names. If the user mentions a name that is not in the catalog, reply that it is not present in the live catalog and list what is present instead.
3. Always attribute each dataset/schema to the connection and engine it appears under. Never move a schema to a different engine.
4. For counting questions, count exactly the catalog entries (for example: connections = the number of listed connections, not a marketing figure).
5. When a connection says "schemas: 0", say it is connected but exposes no schemas. Do not substitute example names.
6. Earlier chat messages may contain unverified database names. Treat them as unconfirmed; the catalog always wins.
7. If the catalog is empty or failed to load, say the live catalog could not be verified and do not guess.
8. Reply in the same language the user used (Marathi, Hindi or English)."""


def context_block() -> str:
    return _render(live_databases())


def system_prompt_for(prompt: str) -> Optional[str]:
    """System prompt grounding a data-catalog question, or None for other chats."""
    if not is_catalog_question(prompt):
        return None
    return f"{context_block()}\n\n{_RULES}"


def summary_line() -> str:
    """One-line live connection summary for executive system prompts."""
    databases = live_databases()
    if not databases:
        return "No live database connection could be introspected in this process."
    counts: Dict[str, int] = {}
    for db in databases:
        counts[db["engine"]] = counts.get(db["engine"], 0) + 1
    parts = [f"{db['name']} ({db['engine']}, {len(db['schemas'])} schemas)" for db in databases]
    return f"{len(databases)} live connections: " + "; ".join(parts)
