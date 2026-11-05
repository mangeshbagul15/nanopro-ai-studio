"""
Live Snowflake access for the Data Modeling by AI workspace.

Credentials always come from the Credential Vault (NANO_PRO_SNOWFLAKE) or the
SNOWFLAKE_PASSWORD environment variable. No secrets live in source.
"""

from __future__ import annotations

import os
import threading
import time
from decimal import Decimal
from datetime import date, datetime, time as dt_time
from typing import Any, Dict, List, Optional

CONNECTION_NAME = "NANO_PRO_SNOWFLAKE"
_catalog_lock = threading.Lock()
_catalog_cache: Dict[str, Any] = {"at": 0.0, "data": None}


class SnowflakeUnavailable(RuntimeError):
    """Raised when Snowflake cannot be reached or is not configured."""


def _defaults() -> Dict[str, Any]:
    try:
        from app.core.connection_manager import SNOWFLAKE_CONFIG

        return dict(SNOWFLAKE_CONFIG)
    except Exception:
        return {}


def load_config() -> Dict[str, Any]:
    cfg: Dict[str, Any] = {}
    try:
        from app.core.connection_manager import connection_manager

        cfg = connection_manager.get_connection_config(CONNECTION_NAME, mask=False) or {}
    except Exception:
        cfg = {}
    meta = cfg.get("metadata") or {}
    if isinstance(meta, str):
        meta = {}
    merged = _defaults()
    for key, value in meta.items():
        if value not in (None, ""):
            merged[key] = value
    merged["connection_name"] = CONNECTION_NAME
    merged["username"] = str(cfg.get("username") or merged.get("username") or "").strip()
    merged["password"] = str(cfg.get("secret_value") or os.environ.get("SNOWFLAKE_PASSWORD") or "").strip()
    merged["account_url"] = str(merged.get("account_url") or "").strip()
    return merged


def driver_available() -> bool:
    try:
        import snowflake.connector  # noqa: F401

        return True
    except Exception:
        return False


def status() -> Dict[str, Any]:
    cfg = load_config()
    return {
        "account": cfg.get("account_identifier"),
        "account_url": cfg.get("account_url"),
        "user": cfg.get("username"),
        "role": cfg.get("role"),
        "warehouse": cfg.get("warehouse"),
        "database": cfg.get("database"),
        "driver": driver_available(),
        "password_set": bool(cfg.get("password")),
        "configured": bool(cfg.get("password") and driver_available()),
    }


def open_connection(
    database: Optional[str] = None,
    schema: Optional[str] = None,
    warehouse: Optional[str] = None,
    timeout: int = 20,
):
    if not driver_available():
        raise SnowflakeUnavailable(
            "snowflake-connector-python is not installed on the server. Add it to requirements.txt and redeploy."
        )
    cfg = load_config()
    if not cfg.get("password"):
        raise SnowflakeUnavailable(
            "Snowflake password is missing. Save it in the Credential Vault (NANO_PRO_SNOWFLAKE) "
            "or set the SNOWFLAKE_PASSWORD environment variable."
        )
    import snowflake.connector as sc

    kwargs: Dict[str, Any] = {
        "user": cfg.get("username"),
        "password": cfg.get("password"),
        "account": cfg.get("account_identifier") or cfg.get("account_name"),
        "role": cfg.get("role") or "ACCOUNTADMIN",
        "login_timeout": timeout,
        "network_timeout": 60,
        "application": "NanoPro_DataModelingAI",
    }
    warehouse = warehouse if warehouse is not None else cfg.get("warehouse")
    if warehouse:
        kwargs["warehouse"] = warehouse
    if database:
        kwargs["database"] = database
    if schema:
        kwargs["schema"] = schema
    try:
        return sc.connect(**kwargs)
    except Exception as exc:
        raise SnowflakeUnavailable(f"Snowflake connection failed: {str(exc)[:400]}") from exc


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date, dt_time)):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", "replace")
    return str(value)


def clear_catalog_cache() -> None:
    with _catalog_lock:
        _catalog_cache["at"] = 0.0
        _catalog_cache["data"] = None


def live_catalog(ttl: float = 120.0, max_tables: int = 800) -> List[Dict[str, Any]]:
    """Returns [{database, schema, tables:[{name,type}]}] from the live account."""
    now = time.time()
    with _catalog_lock:
        cached = _catalog_cache.get("data")
        if cached is not None and now - _catalog_cache["at"] < ttl:
            return cached

    conn = open_connection(database=None, schema=None)
    try:
        cur = conn.cursor()
        grouped: Dict[str, Dict[str, List[Dict[str, str]]]] = {}
        try:
            cur.execute("SHOW TABLES IN ACCOUNT")
            rows = cur.fetchall()
            names = [d[0].lower() for d in cur.description]
            idx = {name: i for i, name in enumerate(names)}
            for row in rows[:max_tables]:
                db = str(row[idx.get("database_name", 3)] or "")
                sch = str(row[idx.get("schema_name", 4)] or "")
                table = str(row[idx.get("name", 1)] or "")
                kind = str(row[idx.get("kind", 5)] or "TABLE").upper()
                if not db or not sch:
                    continue
                grouped.setdefault(db, {}).setdefault(sch, []).append(
                    {"name": table, "type": "view" if "VIEW" in kind else "table"}
                )
        except Exception:
            cur.execute("SHOW DATABASES")
            db_rows = cur.fetchall()
            db_names = [d[0].lower() for d in cur.description]
            db_idx = db_names.index("name") if "name" in db_names else 1
            for db_row in db_rows[:12]:
                db = str(db_row[db_idx])
                if db.upper() in ("SNOWFLAKE",):
                    continue
                try:
                    cur.execute(f'SHOW TABLES IN DATABASE "{db}"')
                    t_rows = cur.fetchall()
                    t_names = [d[0].lower() for d in cur.description]
                    ti = {n: i for i, n in enumerate(t_names)}
                    for row in t_rows[:max_tables]:
                        sch = str(row[ti.get("schema_name", 4)] or "")
                        if sch.upper() == "INFORMATION_SCHEMA":
                            continue
                        table = str(row[ti.get("name", 1)] or "")
                        kind = str(row[ti.get("kind", 5)] or "TABLE").upper()
                        grouped.setdefault(db, {}).setdefault(sch, []).append(
                            {"name": table, "type": "view" if "VIEW" in kind else "table"}
                        )
                except Exception:
                    continue
        finally:
            try:
                cur.close()
            except Exception:
                pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

    data: List[Dict[str, Any]] = []
    for db in sorted(grouped.keys()):
        for sch in sorted(grouped[db].keys()):
            tables = sorted(grouped[db][sch], key=lambda t: t["name"])
            data.append({"database": db, "schema": sch, "tables": tables})
    with _catalog_lock:
        _catalog_cache["data"] = data
        _catalog_cache["at"] = time.time()
    return data
