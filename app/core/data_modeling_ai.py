"""
NanoPro Data Modeling by AI
===========================
Conversational database workspace:
  * persistent workspaces with unique ids (each workspace owns a writable SQLite database)
  * live catalog across every SQLite / DuckDB / connected warehouse in NanoPro
  * natural-language -> SQL generation and execution (read-only outside workspaces)
  * CSV / XLSX import into tables, CSV export of any result set
"""

from __future__ import annotations

import calendar
import csv
import io
import json
import os
import re
import sqlite3
import threading
import time
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import SQLITE_DB_PATH
from app.core.database import db
from app.core.duckdb_chat_store import duckdb_chat_store
from app.core.logger import log_event
from app.core.manager_contract import DELIVERY_CONTRACT

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
MODELING_DIR = DATA_DIR / "modeling"
ATTACHMENT_DIR = MODELING_DIR / "attachments"
MAX_PREVIEW_ROWS = 200
MAX_IMPORT_ROWS = 50000
MAX_ATTACHMENT_BYTES = 25 * 1024 * 1024
MAX_ATTACHMENTS_PER_MESSAGE = 5
ATTACHMENT_TTL_HOURS = 24
TABLE_ATTACHMENT_EXTS = {".csv", ".tsv", ".xlsx", ".xlsm", ".json"}
IMAGE_ATTACHMENT_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
MAX_CONTEXT_CHARS = 14000

_schema_lock = threading.Lock()
_schema_ready = False
_catalog_lock = threading.Lock()
_catalog_cache: Dict[str, Any] = {"at": 0.0, "data": []}
_catalog_refreshing = {"on": False}
_schedule_run_lock = threading.Lock()
_scheduler_start_lock = threading.Lock()
_scheduler_thread: Optional[threading.Thread] = None


def invalidate_catalog() -> None:
    with _catalog_lock:
        _catalog_cache["at"] = 0.0
        _catalog_cache["data"] = []
    try:
        from app.core import live_catalog

        live_catalog.invalidate()
    except Exception:
        pass


def catalog_snapshot(ttl: float = 8.0) -> List[Dict[str, Any]]:
    with _catalog_lock:
        data = _catalog_cache["data"]
        age = time.time() - _catalog_cache["at"]
        refreshing = _catalog_refreshing["on"]
    if data and age < ttl:
        return data
    # Stale-while-revalidate: answer instantly from the last snapshot and
    # refresh live introspection in the background so chat never waits for
    # slow warehouses.
    if data:
        if not refreshing:
            _refresh_catalog_async()
        return data
    # Cold process: let exactly one caller run the expensive global scan.
    # Parallel cold builds on a 512MB instance can spike memory and restart
    # the container, taking every workspace on the ephemeral disk with it.
    if refreshing:
        return []
    with _catalog_lock:
        if _catalog_refreshing["on"]:
            return []
        _catalog_refreshing["on"] = True
    try:
        fresh = list_catalog()
    finally:
        with _catalog_lock:
            _catalog_refreshing["on"] = False
    if fresh:
        with _catalog_lock:
            _catalog_cache["data"] = fresh
            _catalog_cache["at"] = time.time()
    return fresh


def catalog_cached() -> Tuple[List[Dict[str, Any]], bool]:
    """Return the current snapshot immediately and refresh in the background when stale."""
    with _catalog_lock:
        data = list(_catalog_cache["data"])
        age = time.time() - _catalog_cache["at"]
        refreshing = bool(_catalog_refreshing["on"])
    stale = not data or age > 8.0
    if stale and not refreshing:
        _refresh_catalog_async()
        refreshing = True
    return data, bool(refreshing and stale)


def _workspace_catalog_entry(workspace_id: str) -> Optional[Dict[str, Any]]:
    ws = get_workspace(workspace_id) or {}
    if not ws:
        return None
    return {
        "id": "workspace:" + ws["id"],
        "name": ws.get("name") or ws["id"],
        "engine": "sqlite",
        "kind": "workspace",
        "writable": True,
        "status": "live",
        "workspace_id": ws["id"],
        "schemas": ws.get("schemas") or [{"name": "main", "tables": []}],
        "updated_at": ws.get("updated_at"),
    }


def catalog_for_chat(
    workspace_id: str,
    allowed_workspaces: Optional[set] = None,
) -> List[Dict[str, Any]]:
    """Catalog view for a chat turn that never blocks on a cold scan.

    catalog_cached() returns the last snapshot immediately and refreshes live
    introspection in the background. The active workspace is overlaid from its
    own live SQLite file so a table created in the previous turn is always
    visible even when the shared snapshot is stale. On a cold process (fresh
    Render boot) we fall back to local workspace metadata only, so remote
    warehouses are never dialled while the user is waiting for a reply.
    """
    catalog, _ = catalog_cached()
    live_entry = _workspace_catalog_entry(workspace_id) if workspace_id else None
    if live_entry:
        catalog = [entry for entry in catalog if entry.get("id") != live_entry["id"]]
        catalog.insert(0, live_entry)
    if not catalog:
        catalog = [
            {
                "id": "workspace:" + ws["id"],
                "name": ws["name"],
                "engine": "sqlite",
                "kind": "workspace",
                "writable": True,
                "status": "live",
                "workspace_id": ws["id"],
                "schemas": ws.get("schemas", [{"name": "main", "tables": []}]),
            }
            for ws in _catalog_workspaces()
        ]
    if allowed_workspaces is not None:
        catalog = [
            entry
            for entry in catalog
            if entry.get("kind") != "workspace" or entry.get("workspace_id") in allowed_workspaces
        ]
    return catalog


def refresh_catalog_async() -> Tuple[List[Dict[str, Any]], bool]:
    """Keep the last snapshot on screen and rescan slowly in the background."""
    with _catalog_lock:
        has_cache = bool(_catalog_cache["data"])
        _catalog_cache["at"] = 0.0
        data = list(_catalog_cache["data"])
    try:
        from app.core import live_catalog

        live_catalog.invalidate()
    except Exception:
        pass
    if not has_cache:
        return [], False
    _refresh_catalog_async()
    return data, True


def _refresh_catalog_async() -> None:
    with _catalog_lock:
        if _catalog_refreshing["on"]:
            return
        _catalog_refreshing["on"] = True

    def worker() -> None:
        try:
            data = list_catalog()
            if data:
                with _catalog_lock:
                    _catalog_cache["data"] = data
                    _catalog_cache["at"] = time.time()
        except Exception as exc:
            log_event(f"Background catalog refresh failed: {exc}", level="WARNING", component="DataModeling")
        finally:
            with _catalog_lock:
                _catalog_refreshing["on"] = False

    threading.Thread(target=worker, name="dm-catalog-refresh", daemon=True).start()

_READ_PREFIX = re.compile(r"^\s*(select|with|pragma|explain|show|describe|desc)\b", re.IGNORECASE)
_WRITE_PREFIX = re.compile(
    r"^\s*(create\s+(table|view|index|temp\s+table|temporary\s+table)|insert\s+into|update\s+\S+\s+set|"
    r"delete\s+from|drop\s+(table|view|index))\b",
    re.IGNORECASE,
)
_DESTRUCTIVE = re.compile(
    r"\b(drop|delete|truncate|attach|detach|vacuum|reindex|grant|revoke|pragma\s+writable_schema)\b",
    re.IGNORECASE,
)
_SNOWFLAKE_WRITE = re.compile(r"^\s*(create|insert|merge|update|alter)\b", re.IGNORECASE)

_IDENT = r'(?:"[^"]+"|`[^`]+`|\[[^\]]+\]|[A-Za-z_][\w$]*)'
_QUALIFIED = _IDENT + r"(?:\." + _IDENT + r")*"
_ALTER_ALLOWED = [
    re.compile(r"^\s*alter\s+table\s+" + _QUALIFIED + r"\s+add\s+(?:column\s+)?" + _IDENT + r"\s+.+$", re.IGNORECASE),
    re.compile(r"^\s*alter\s+table\s+" + _QUALIFIED + r"\s+rename\s+(?:column\s+)?" + _IDENT + r"\s+to\s+" + _IDENT + r"\s*$", re.IGNORECASE),
    re.compile(r"^\s*alter\s+table\s+" + _QUALIFIED + r"\s+rename\s+to\s+" + _IDENT + r"\s*$", re.IGNORECASE),
    re.compile(r"^\s*alter\s+table\s+" + _QUALIFIED + r"\s+alter\s+(?:column\s+)?" + _IDENT + r"\s+(?:set\s+data\s+type|set\s+type|type)\s+.+$", re.IGNORECASE),
    re.compile(r"^\s*alter\s+table\s+" + _QUALIFIED + r"\s+modify\s+(?:column\s+)?" + _IDENT + r"\s+.+$", re.IGNORECASE),
]
_SQLITE_TYPE_CHANGE = re.compile(
    r"^\s*alter\s+table\s+(?P<table>" + _QUALIFIED + r")\s+alter\s+(?:column\s+)?(?P<column>" + _IDENT + r")\s+"
    r"(?:set\s+data\s+type|set\s+type|type)\s+(?P<type>[A-Za-z0-9_(),\s]+?)\s*$",
    re.IGNORECASE,
)
_SQLITE_MODIFY = re.compile(
    r"^\s*alter\s+table\s+(?P<table>" + _QUALIFIED + r")\s+modify\s+(?:column\s+)?(?P<column>" + _IDENT + r")\s+"
    r"(?P<type>[A-Za-z0-9_(),\s]+?)\s*$",
    re.IGNORECASE,
)



# ----------------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _clip(value: Any, size: int = 4000) -> Any:
    if isinstance(value, str) and len(value) > size:
        return value[:size] + "…"
    return value


def _quote(name: str) -> str:
    return '"' + str(name).replace('"', '""') + '"'


def _safe_ident(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", (name or "").strip()).strip("_")
    if not cleaned:
        cleaned = "table_" + uuid.uuid4().hex[:6]
    if cleaned[0].isdigit():
        cleaned = "t_" + cleaned
    return cleaned[:60]


def _table_rows(conn: sqlite3.Connection, sql: str, params: Tuple = ()) -> List[Dict[str, Any]]:
    cur = conn.execute(sql, params)
    return [dict(r) for r in cur.fetchall()]


def _ensure_schema() -> None:
    global _schema_ready
    if _schema_ready:
        return
    with _schema_lock:
        if _schema_ready:
            return
        with db.get_connection() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS dm_workspaces ("
                " id TEXT PRIMARY KEY, name TEXT NOT NULL, created_by TEXT DEFAULT '',"
                " created_at TEXT NOT NULL, updated_at TEXT NOT NULL,"
                " project_id TEXT DEFAULT '', pinned INTEGER NOT NULL DEFAULT 0)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS dm_projects ("
                " id TEXT PRIMARY KEY, name TEXT NOT NULL, created_by TEXT DEFAULT '',"
                " created_at TEXT NOT NULL, updated_at TEXT NOT NULL)"
            )
            ws_columns = {row[1] for row in conn.execute("PRAGMA table_info(dm_workspaces)").fetchall()}
            if "project_id" not in ws_columns:
                conn.execute("ALTER TABLE dm_workspaces ADD COLUMN project_id TEXT DEFAULT ''")
            if "pinned" not in ws_columns:
                conn.execute("ALTER TABLE dm_workspaces ADD COLUMN pinned INTEGER NOT NULL DEFAULT 0")
            conn.execute(
                "CREATE TABLE IF NOT EXISTS dm_messages ("
                " id INTEGER PRIMARY KEY AUTOINCREMENT, workspace_id TEXT NOT NULL,"
                " role TEXT NOT NULL, content TEXT NOT NULL, sql_text TEXT,"
                " meta TEXT, created_at TEXT NOT NULL)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS dm_runs ("
                " run_id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, sql_text TEXT,"
                " columns TEXT, rows TEXT, row_count INTEGER, created_at TEXT NOT NULL)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS dm_workspace_schemas ("
                " workspace_id TEXT NOT NULL, schema_name TEXT NOT NULL, file_name TEXT NOT NULL,"
                " created_at TEXT NOT NULL, PRIMARY KEY (workspace_id, schema_name))"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS dm_schedules ("
                " schedule_id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, name TEXT NOT NULL,"
                " kind TEXT NOT NULL DEFAULT 'sql', steps TEXT NOT NULL, target TEXT NOT NULL,"
                " frequency TEXT NOT NULL, at_time TEXT, weekday INTEGER, day_of_month INTEGER,"
                " cron_expr TEXT, enabled INTEGER NOT NULL DEFAULT 1, next_run_at TEXT,"
                " last_run_at TEXT, last_status TEXT, created_by TEXT DEFAULT '',"
                " created_at TEXT NOT NULL)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS dm_schedule_runs ("
                " run_id TEXT PRIMARY KEY, schedule_id TEXT NOT NULL, started_at TEXT NOT NULL,"
                " finished_at TEXT, status TEXT NOT NULL, message TEXT, statements INTEGER,"
                " rows_affected INTEGER)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_dm_messages_ws ON dm_messages(workspace_id, id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_dm_schedules_due ON dm_schedules(enabled, next_run_at)"
            )
            conn.commit()
        MODELING_DIR.mkdir(parents=True, exist_ok=True)
        _schema_ready = True


# ----------------------------------------------------------------------------
# workspaces
# ----------------------------------------------------------------------------

def _workspace_db_path(workspace_id: str) -> Path:
    if not re.fullmatch(r"ws_[a-f0-9]{6,20}", workspace_id or ""):
        raise ValueError("Invalid workspace id.")
    return MODELING_DIR / f"{workspace_id}.db"


def _workspace_schemas(workspace_id: str) -> List[Dict[str, str]]:
    _ensure_schema()
    with db.get_connection() as conn:
        rows = _table_rows(
            conn,
            "SELECT schema_name, file_name FROM dm_workspace_schemas WHERE workspace_id = ? ORDER BY schema_name",
            (workspace_id,),
        )
    return rows


def open_workspace_connection(workspace_id: str) -> sqlite3.Connection:
    path = _workspace_db_path(workspace_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=15.0)
    conn.row_factory = sqlite3.Row
    for schema in _workspace_schemas(workspace_id):
        try:
            conn.execute(f"ATTACH DATABASE ? AS {_quote(schema['schema_name'])}", (str(MODELING_DIR / schema["file_name"]),))
        except sqlite3.Error:
            pass
    return conn


def list_workspaces(user: str = "", light: bool = False) -> List[Dict[str, Any]]:
    _ensure_schema()
    from app.core.identity_resolver import resolve_canonical_username
    explicit_user = (user or "").strip()
    safe_user = resolve_canonical_username(explicit_user) if explicit_user else ""
    if safe_user:
        try:
            ws_list = duckdb_chat_store.list_workspaces(safe_user, light=light)
            if ws_list:
                if not light:
                    for row in ws_list:
                        schemas = [{"name": "main", "tables": []}]
                        try:
                            with open_workspace_connection(row["id"]) as wconn:
                                tables = _sqlite_table_names(wconn, "main")
                                schemas[0]["tables"] = tables
                                for schema in _workspace_schemas(row["id"]):
                                    schemas.append({"name": schema["schema_name"], "tables": _sqlite_table_names(wconn, schema["schema_name"])})
                        except Exception:
                            pass
                        row["schemas"] = schemas
                        row["table_count"] = sum(len(s["tables"]) for s in schemas)
                return ws_list
        except Exception as exc:
            log_event(f"DuckDB list_workspaces fallback: {exc}", component="DataModeling", level="WARNING")

    with db.get_connection() as conn:
        if safe_user:
            rows = _table_rows(
                conn,
                "SELECT w.*,"
                " (SELECT COUNT(*) FROM dm_messages m WHERE m.workspace_id = w.id) AS message_count,"
                " (SELECT MAX(m.created_at) FROM dm_messages m WHERE m.workspace_id = w.id) AS last_message_at"
                " FROM dm_workspaces w WHERE w.created_by = ? ORDER BY w.updated_at DESC",
                (safe_user,),
            )
        else:
            rows = _table_rows(
                conn,
                "SELECT w.*,"
                " (SELECT COUNT(*) FROM dm_messages m WHERE m.workspace_id = w.id) AS message_count,"
                " (SELECT MAX(m.created_at) FROM dm_messages m WHERE m.workspace_id = w.id) AS last_message_at"
                " FROM dm_workspaces w ORDER BY w.updated_at DESC",
            )
    for row in rows:
        row["pinned"] = bool(row.get("pinned"))
        row["project_id"] = row.get("project_id") or ""
        if light:
            row["schemas"] = []
            row["table_count"] = 0
            continue
        schemas = [{"name": "main", "tables": []}]
        try:
            with open_workspace_connection(row["id"]) as wconn:
                tables = _sqlite_table_names(wconn, "main")
                schemas[0]["tables"] = tables
                for schema in _workspace_schemas(row["id"]):
                    schemas.append({"name": schema["schema_name"], "tables": _sqlite_table_names(wconn, schema["schema_name"])})
        except Exception:
            pass
        row["schemas"] = schemas
        row["table_count"] = sum(len(s["tables"]) for s in schemas)
    return rows


def get_workspace(workspace_id: str, user: str = "") -> Optional[Dict[str, Any]]:
    _ensure_schema()
    from app.core.identity_resolver import resolve_canonical_username, is_admin_identity
    explicit_user = (user or "").strip()
    safe_user = resolve_canonical_username(explicit_user) if explicit_user else ""
    if safe_user:
        try:
            ws = duckdb_chat_store.get_workspace(safe_user, workspace_id)
            if ws:
                schemas = [{"name": "main", "tables": []}]
                try:
                    with open_workspace_connection(ws["id"]) as wconn:
                        schemas[0]["tables"] = _sqlite_table_names(wconn, "main")
                        for schema in _workspace_schemas(ws["id"]):
                            schemas.append({"name": schema["schema_name"], "tables": _sqlite_table_names(wconn, schema["schema_name"])})
                except Exception:
                    pass
                ws["schemas"] = schemas
                ws["table_count"] = sum(len(s["tables"]) for s in schemas)
                return ws
        except Exception:
            pass

    scoped = bool(safe_user) and not is_admin_identity(safe_user)
    with db.get_connection() as conn:
        query = (
            "SELECT w.*,"
            " (SELECT COUNT(*) FROM dm_messages m WHERE m.workspace_id = w.id) AS message_count,"
            " (SELECT MAX(m.created_at) FROM dm_messages m WHERE m.workspace_id = w.id) AS last_message_at"
            " FROM dm_workspaces w WHERE w.id = ?"
        )
        if scoped:
            cur = conn.execute(query + " AND w.created_by = ?", (workspace_id, safe_user))
        else:
            cur = conn.execute(query, (workspace_id,))
        row = cur.fetchone()
    if not row:
        return None
    if isinstance(row, sqlite3.Row):
        row = dict(row)
    else:
        cols = [c[0] for c in cur.description] if cur.description else []
        row = dict(zip(cols, row))
    row["pinned"] = bool(row.get("pinned"))
    row["project_id"] = row.get("project_id") or ""
    schemas = [{"name": "main", "tables": []}]
    try:
        with open_workspace_connection(row["id"]) as wconn:
            schemas[0]["tables"] = _sqlite_table_names(wconn, "main")
            for schema in _workspace_schemas(row["id"]):
                schemas.append({"name": schema["schema_name"], "tables": _sqlite_table_names(wconn, schema["schema_name"])})
    except Exception:
        pass
    row["schemas"] = schemas
    row["table_count"] = sum(len(s["tables"]) for s in schemas)
    return row


def create_workspace(name: str = "", user: str = "", project_id: str = "") -> Dict[str, Any]:
    _ensure_schema()
    wid = "ws_" + uuid.uuid4().hex[:10]
    label = (name or "New chat").strip()[:64] or "New chat"
    stamp = _now()
    from app.core.identity_resolver import resolve_canonical_username
    safe_user = resolve_canonical_username(user)
    with db.get_connection() as conn:
        project = (project_id or "").strip()
        if project and not conn.execute("SELECT 1 FROM dm_projects WHERE id = ?", (project,)).fetchone():
            project = ""
        conn.execute(
            "INSERT INTO dm_workspaces (id, name, created_by, created_at, updated_at, project_id, pinned)"
            " VALUES (?, ?, ?, ?, ?, ?, 0)",
            (wid, label, safe_user, stamp, stamp, project),
        )
        conn.commit()
    open_workspace_connection(wid).close()
    invalidate_catalog()
    ws_data = {
        "id": wid,
        "name": label,
        "created_by": safe_user,
        "created_at": stamp,
        "updated_at": stamp,
        "project_id": project,
        "pinned": False,
        "schemas": [{"name": "main", "tables": []}],
        "table_count": 0,
        "message_count": 0,
        "last_message_at": None,
    }
    if safe_user:
        try:
            duckdb_chat_store.save_workspace(safe_user, ws_data)
            duckdb_chat_store.save_user_state(safe_user, wid, project)
        except Exception as exc:
            log_event(f"DuckDB save_workspace error: {exc}", component="DataModeling", level="WARNING")
    ws_loaded = get_workspace(wid, user=safe_user)
    if ws_loaded:
        ws_data = ws_loaded
    log_event(f"Data modeling chat created: {wid} ({label}) by user [{safe_user}]", component="DataModeling")
    return ws_data


def set_workspace_pinned(workspace_id: str, pinned: bool, user: str = "") -> Dict[str, Any]:
    _ensure_schema()
    from app.core.identity_resolver import resolve_canonical_username
    safe_user = resolve_canonical_username(user)
    if safe_user:
        try:
            duckdb_chat_store.pin_workspace(safe_user, workspace_id, pinned)
        except Exception:
            pass
    with db.get_connection() as conn:
        cur = conn.execute("UPDATE dm_workspaces SET pinned = ? WHERE id = ?", (1 if pinned else 0, workspace_id))
        conn.commit()
    if not cur.rowcount and not safe_user:
        raise ValueError("Chat not found.")
    return get_workspace(workspace_id, user=safe_user) or {}


def set_workspace_project(workspace_id: str, project_id: str, user: str = "") -> Dict[str, Any]:
    _ensure_schema()
    safe_user = (user or "").strip()
    target = (project_id or "").strip()
    if safe_user:
        try:
            duckdb_chat_store.set_workspace_project(safe_user, workspace_id, target)
        except Exception:
            pass
    with db.get_connection() as conn:
        if target and not conn.execute("SELECT 1 FROM dm_projects WHERE id = ?", (target,)).fetchone():
            raise ValueError("Project not found.")
        cur = conn.execute("UPDATE dm_workspaces SET project_id = ? WHERE id = ?", (target, workspace_id))
        conn.commit()
    if not cur.rowcount and not safe_user:
        raise ValueError("Chat not found.")
    return get_workspace(workspace_id, user=safe_user) or {}


def delete_workspace(workspace_id: str, user: str = "") -> Dict[str, Any]:
    _ensure_schema()
    db_path = _workspace_db_path(workspace_id)
    safe_user = (user or "").strip()
    if safe_user:
        from app.core.identity_resolver import resolve_canonical_username, is_admin_identity

        canonical = resolve_canonical_username(safe_user)
        if not is_admin_identity(canonical):
            with db.get_connection() as conn:
                owner = conn.execute("SELECT created_by FROM dm_workspaces WHERE id = ?", (workspace_id,)).fetchone()
            if not owner or str(owner[0] or "") != canonical:
                raise ValueError("Chat not found.")
        safe_user = canonical
        try:
            duckdb_chat_store.delete_workspace(safe_user, workspace_id)
        except Exception:
            pass
    with db.get_connection() as conn:
        exists = conn.execute("SELECT 1 FROM dm_workspaces WHERE id = ?", (workspace_id,)).fetchone()
        if not exists and not safe_user:
            raise ValueError("Chat not found.")
        schedule_ids = [r["schedule_id"] for r in _table_rows(conn, "SELECT schedule_id FROM dm_schedules WHERE workspace_id = ?", (workspace_id,))]
        schema_rows = _table_rows(conn, "SELECT file_name FROM dm_workspace_schemas WHERE workspace_id = ?", (workspace_id,))
        conn.execute("DELETE FROM dm_messages WHERE workspace_id = ?", (workspace_id,))
        conn.execute("DELETE FROM dm_runs WHERE workspace_id = ?", (workspace_id,))
        conn.execute("DELETE FROM dm_schedules WHERE workspace_id = ?", (workspace_id,))
        for schedule_id in schedule_ids:
            conn.execute("DELETE FROM dm_schedule_runs WHERE schedule_id = ?", (schedule_id,))
        conn.execute("DELETE FROM dm_workspace_schemas WHERE workspace_id = ?", (workspace_id,))
        conn.execute("DELETE FROM dm_workspaces WHERE id = ?", (workspace_id,))
        conn.commit()
    for name in [db_path.name] + [row["file_name"] for row in schema_rows]:
        try:
            (MODELING_DIR / name).unlink()
        except (FileNotFoundError, PermissionError):
            pass
    invalidate_catalog()
    log_event(f"Data modeling chat deleted: {workspace_id}", component="DataModeling")
    return {"workspace_id": workspace_id, "deleted": True}


def list_projects(user: str = "") -> List[Dict[str, Any]]:
    _ensure_schema()
    from app.core.identity_resolver import resolve_canonical_username
    safe_user = resolve_canonical_username(user)
    if safe_user:
        try:
            projs = duckdb_chat_store.list_projects(safe_user)
            if projs:
                return projs
        except Exception:
            pass
    with db.get_connection() as conn:
        if safe_user:
            rows = _table_rows(
                conn,
                "SELECT p.*, (SELECT COUNT(*) FROM dm_workspaces w WHERE w.project_id = p.id) AS chat_count"
                " FROM dm_projects p WHERE p.created_by = ? ORDER BY p.updated_at DESC",
                (safe_user,),
            )
        else:
            rows = _table_rows(
                conn,
                "SELECT p.*, (SELECT COUNT(*) FROM dm_workspaces w WHERE w.project_id = p.id) AS chat_count"
                " FROM dm_projects p ORDER BY p.updated_at DESC",
            )
    return rows


def create_project(name: str = "", user: str = "") -> Dict[str, Any]:
    _ensure_schema()
    pid = "prj_" + uuid.uuid4().hex[:10]
    label = (name or "New project").strip()[:64] or "New project"
    stamp = _now()
    safe_user = (user or "").strip()
    if safe_user:
        try:
            duckdb_chat_store.create_project(safe_user, pid, label)
        except Exception:
            pass
    with db.get_connection() as conn:
        conn.execute(
            "INSERT INTO dm_projects (id, name, created_by, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (pid, label, safe_user, stamp, stamp),
        )
        conn.commit()
    return {"id": pid, "name": label, "created_by": safe_user, "created_at": stamp, "updated_at": stamp, "chat_count": 0}


def rename_project(project_id: str, name: str, user: str = "") -> Dict[str, Any]:
    label = (name or "").strip()[:64]
    if not label:
        raise ValueError("Project name cannot be empty.")
    _ensure_schema()
    safe_user = (user or "").strip()
    if safe_user:
        try:
            duckdb_chat_store.rename_project(safe_user, project_id, label)
        except Exception:
            pass
    with db.get_connection() as conn:
        cur = conn.execute("UPDATE dm_projects SET name = ?, updated_at = ? WHERE id = ?", (label, _now(), project_id))
        conn.commit()
    if not cur.rowcount and not safe_user:
        raise ValueError("Project not found.")
    for project in list_projects(user=safe_user):
        if project["id"] == project_id:
            return project
    return {"id": project_id, "name": label}


def delete_project(project_id: str, delete_chats: bool = False, user: str = "") -> Dict[str, Any]:
    _ensure_schema()
    safe_user = (user or "").strip()
    if safe_user:
        try:
            duckdb_chat_store.delete_project(safe_user, project_id, delete_chats=delete_chats)
        except Exception:
            pass
    with db.get_connection() as conn:
        exists = conn.execute("SELECT 1 FROM dm_projects WHERE id = ?", (project_id,)).fetchone()
        if not exists and not safe_user:
            raise ValueError("Project not found.")
        chat_ids = [r["id"] for r in _table_rows(conn, "SELECT id FROM dm_workspaces WHERE project_id = ?", (project_id,))]
    if delete_chats:
        for chat_id in chat_ids:
            delete_workspace(chat_id, user=safe_user)
    with db.get_connection() as conn:
        conn.execute("DELETE FROM dm_projects WHERE id = ?", (project_id,))
        if not delete_chats:
            conn.execute("UPDATE dm_workspaces SET project_id = '' WHERE project_id = ?", (project_id,))
        conn.commit()
    invalidate_catalog()
    return {"project_id": project_id, "deleted": True, "chats": len(chat_ids), "chats_deleted": bool(delete_chats)}


def rename_workspace(workspace_id: str, name: str, user: str = "") -> Dict[str, Any]:
    label = (name or "").strip()[:64]
    if not label:
        raise ValueError("Workspace name cannot be empty.")
    _ensure_schema()
    safe_user = (user or "").strip()
    if safe_user:
        try:
            duckdb_chat_store.rename_workspace(safe_user, workspace_id, label)
        except Exception:
            pass
    with db.get_connection() as conn:
        conn.execute("UPDATE dm_workspaces SET name = ?, updated_at = ? WHERE id = ?", (label, _now(), workspace_id))
        conn.commit()
    ws = get_workspace(workspace_id, user=safe_user)
    if not ws:
        raise ValueError("Workspace not found.")
    return ws


def _touch_workspace(workspace_id: str) -> None:
    with db.get_connection() as conn:
        conn.execute("UPDATE dm_workspaces SET updated_at = ? WHERE id = ?", (_now(), workspace_id))
        conn.commit()


def create_schema(workspace_id: str, schema_name: str) -> Dict[str, Any]:
    _ensure_schema()
    _workspace_db_path(workspace_id)
    name = _safe_ident(schema_name).lower()
    if name in ("main", "temp") or name.startswith("sqlite_"):
        raise ValueError("That schema name is reserved.")
    file_name = f"{workspace_id}__{name}.db"
    with db.get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO dm_workspace_schemas (workspace_id, schema_name, file_name, created_at) VALUES (?, ?, ?, ?)",
            (workspace_id, name, file_name, _now()),
        )
        conn.commit()
    conn2 = open_workspace_connection(workspace_id)
    conn2.close()
    invalidate_catalog()
    return {"workspace_id": workspace_id, "schema": name, "file": str(MODELING_DIR / file_name)}


# ----------------------------------------------------------------------------
# chat history & user state
# ----------------------------------------------------------------------------

def _message_signature(message: Dict[str, Any]) -> Tuple[str, str, str]:
    # The two stores stamp created_at independently, so it cannot be part of the
    # identity; role/content/sql plus multiset counts identify a stored message.
    return (
        str(message.get("role") or ""),
        str(message.get("content") or "").strip(),
        str(message.get("sql") or message.get("sql_text") or ""),
    )


def _mirror_to_duckdb(user: str, workspace_id: str, row: Dict[str, Any]) -> None:
    # History reads must never rewrite the caller's active chat state.
    try:
        duckdb_chat_store.add_message(
            user,
            workspace_id,
            row["role"],
            row["content"],
            row.get("sql_text") or row.get("sql") or "",
            row.get("meta") if isinstance(row.get("meta"), dict) else {},
            touch=False,
        )
    except Exception as exc:
        log_event(f"DuckDB history mirror error: {exc}", component="DataModeling", level="WARNING")


def get_messages(workspace_id: str, limit: int = 300, user: str = "") -> List[Dict[str, Any]]:
    """Returns chat history, healing drift between the SQLite write-ahead copy and
    the per-user DuckDB store. Assistant replies have been lost from DuckDB when a
    single write failed, which silently dropped them from the UI transcript."""
    _ensure_schema()
    from app.core.identity_resolver import resolve_canonical_username
    explicit_user = (user or "").strip()
    safe_user = resolve_canonical_username(explicit_user) if explicit_user else ""
    limit = max(1, min(limit, 500))

    with db.get_connection() as conn:
        rows = _table_rows(
            conn,
            "SELECT * FROM dm_messages WHERE workspace_id = ? ORDER BY id DESC LIMIT ?",
            (workspace_id, limit),
        )
    rows.reverse()
    for row in rows:
        try:
            row["meta"] = json.loads(row["meta"]) if row["meta"] else {}
        except Exception:
            row["meta"] = {}

    if not safe_user:
        return rows

    try:
        msgs = duckdb_chat_store.get_messages(safe_user, workspace_id, limit=limit)
    except Exception as exc:
        log_event(f"DuckDB get_messages fallback: {exc}", component="DataModeling", level="WARNING")
        msgs = []

    if not msgs:
        for row in rows:
            _mirror_to_duckdb(safe_user, workspace_id, row)
        return rows

    seen: Dict[Tuple[str, str, str], int] = {}
    for message in msgs:
        key = _message_signature(message)
        seen[key] = seen.get(key, 0) + 1

    missing = []
    for row in rows:
        key = _message_signature(row)
        if seen.get(key):
            seen[key] -= 1
            continue
        missing.append(row)

    if not missing:
        return msgs

    log_event(
        f"DataModeling history drift in {workspace_id}: mirroring {len(missing)} message(s) into DuckDB",
        component="DataModeling",
        level="WARNING",
    )
    for row in missing:
        _mirror_to_duckdb(safe_user, workspace_id, row)

    merged = list(rows)
    known = {_message_signature(row) for row in rows}
    extra = [message for message in msgs if _message_signature(message) not in known]
    if extra:
        merged = sorted(
            merged + extra,
            key=lambda message: (str(message.get("created_at") or ""), str(message.get("id") or "")),
        )
    return merged[-limit:]


def add_message(
    workspace_id: str,
    role: str,
    content: str,
    sql_text: str = "",
    meta: Optional[Dict[str, Any]] = None,
    user: str = "",
) -> Dict[str, Any]:
    _ensure_schema()
    stamp = _now()
    safe_user = (user or "").strip()

    # Save to SQLite
    with db.get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO dm_messages (workspace_id, role, content, sql_text, meta, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (workspace_id, role, content or "", sql_text or "", json.dumps(meta or {}), stamp),
        )
        conn.commit()
        msg_id = cur.lastrowid
    _touch_workspace(workspace_id)

    # Save to user's dedicated DuckDB
    if safe_user:
        try:
            duckdb_res = duckdb_chat_store.add_message(
                safe_user, workspace_id, role, content, sql_text, meta
            )
            return duckdb_res
        except Exception as exc:
            log_event(f"DuckDB add_message error: {exc}", component="DataModeling", level="WARNING")

    return {
        "id": msg_id,
        "workspace_id": workspace_id,
        "role": role,
        "content": content,
        "sql": sql_text,
        "meta": meta or {},
        "created_at": stamp,
    }


def save_user_state(user: str, active_workspace_id: str, active_project_id: str = "") -> None:
    safe_user = (user or "").strip()
    if safe_user:
        duckdb_chat_store.save_user_state(safe_user, active_workspace_id, active_project_id)


def get_user_state(user: str) -> Dict[str, str]:
    safe_user = (user or "").strip()
    if safe_user:
        return duckdb_chat_store.get_user_state(safe_user)
    return {"active_workspace_id": "", "active_project_id": ""}


def export_user_chat(user: str, workspace_id: str) -> Dict[str, Any]:
    safe_user = (user or "").strip()
    return duckdb_chat_store.export_user_chat_google_claude(safe_user, workspace_id)


# ----------------------------------------------------------------------------
# catalog
# ----------------------------------------------------------------------------

def _sqlite_table_names(conn: sqlite3.Connection, schema: str = "main") -> List[Dict[str, str]]:
    rows = conn.execute(
        f"SELECT name, type FROM {_quote(schema)}.sqlite_master "
        "WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [{"name": r[0], "type": r[1]} for r in rows]


def _discover_sqlite_files() -> List[Path]:
    found: Dict[str, Path] = {}
    roots = [ROOT / "app" / "database", DATA_DIR]
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.db"):
            parts = {p.lower() for p in path.parts}
            if "modeling" in parts or "backups" in parts or ".git" in parts:
                continue
            try:
                key = str(path.resolve()).lower()
            except OSError:
                key = str(path).lower()
            found.setdefault(key, path)
    primary = Path(SQLITE_DB_PATH)
    if primary.exists():
        found.setdefault(str(primary.resolve()).lower(), primary)
    return sorted(found.values(), key=lambda p: (p.name.lower() != "studio_memory.db", p.name.lower()))[:40]


def _discover_duckdb_files() -> List[Path]:
    files = []
    lakehouse = DATA_DIR / "lakehouse"
    if lakehouse.exists():
        files.extend(lakehouse.glob("*.duckdb"))
    files.extend(DATA_DIR.rglob("*.duckdb"))
    seen = {}
    for path in files:
        seen.setdefault(str(path.resolve()).lower(), path)
    return sorted(seen.values(), key=lambda p: p.name.lower())[:10]


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except Exception:
        return path.as_posix()


def _sqlite_entry(path: Path) -> Dict[str, Any]:
    entry: Dict[str, Any] = {
        "id": "sqlite:" + _rel(path),
        "name": path.name,
        "engine": "sqlite",
        "kind": "sqlite",
        "writable": False,
        "status": "live",
        "location": _rel(path),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "schemas": [],
    }
    if str(path.resolve()).lower() == str(Path(SQLITE_DB_PATH).resolve()).lower():
        entry["role"] = "primary"
        entry["name"] = "Studio Memory (Primary)"
    try:
        conn = sqlite3.connect(str(path), timeout=3.0)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA query_only = ON")
            entry["schemas"] = [{"name": "main", "tables": _sqlite_table_names(conn, "main")}]
        finally:
            conn.close()
    except Exception as exc:
        entry["status"] = "error"
        entry["error"] = str(exc)[:160]
    return entry


def _duckdb_entry(path: Path) -> Dict[str, Any]:
    entry: Dict[str, Any] = {
        "id": "duckdb:" + _rel(path),
        "name": path.name,
        "engine": "duckdb",
        "kind": "duckdb",
        "writable": False,
        "status": "live",
        "location": _rel(path),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "schemas": [],
    }
    try:
        import duckdb  # type: ignore

        con = duckdb.connect(str(path), read_only=True)
        try:
            tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
        finally:
            con.close()
        entry["schemas"] = [{"name": "main", "tables": [{"name": t, "type": "table"} for t in tables]}]
    except Exception as exc:
        entry["status"] = "unavailable"
        entry["error"] = str(exc)[:160]
    return entry


def _connection_entries() -> List[Dict[str, Any]]:
    """Every configured NanoPro database, introspected live (no demo metadata)."""
    try:
        from app.core import live_catalog

        return live_catalog.databases()
    except Exception as exc:
        log_event(f"Live catalog unavailable: {exc}", level="WARNING", component="DataModeling")
        return []


def _snowflake_databases() -> List[str]:
    """Database names that really exist in the live Snowflake account."""
    names: List[str] = []
    for entry in _connection_entries():
        if entry.get("engine") != "snowflake":
            continue
        for group in entry.get("schemas") or []:
            database = str(group.get("database") or "").strip()
            if not database:
                schema = str(group.get("schema") or group.get("name") or "")
                database = schema.split(".", 1)[0] if "." in schema else ""
            if database and database not in names:
                names.append(database)
    if not names:
        try:
            from app.core import snowflake_client

            configured = str(snowflake_client.load_config().get("database") or "").strip()
            if configured:
                names.append(configured)
        except Exception:
            pass
    return names


def _catalog_workspaces() -> List[Dict[str, Any]]:
    """Every workspace with live table lists, independent of the viewing user."""
    _ensure_schema()
    with db.get_connection() as conn:
        rows = _table_rows(conn, "SELECT * FROM dm_workspaces ORDER BY updated_at DESC")
    for row in rows:
        row["pinned"] = bool(row.get("pinned"))
        row["project_id"] = row.get("project_id") or ""
        schemas = [{"name": "main", "tables": []}]
        try:
            with open_workspace_connection(row["id"]) as wconn:
                schemas[0]["tables"] = _sqlite_table_names(wconn, "main")
                for schema in _workspace_schemas(row["id"]):
                    schemas.append({"name": schema["schema_name"], "tables": _sqlite_table_names(wconn, schema["schema_name"])})
        except Exception:
            pass
        row["schemas"] = schemas
        row["table_count"] = sum(len(s["tables"]) for s in schemas)
    return rows


def list_catalog() -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for ws in _catalog_workspaces():
        entries.append({
            "id": "workspace:" + ws["id"],
            "name": ws["name"],
            "engine": "sqlite",
            "kind": "workspace",
            "writable": True,
            "status": "live",
            "workspace_id": ws["id"],
            "schemas": ws.get("schemas", [{"name": "main", "tables": []}]),
            "updated_at": ws.get("updated_at"),
        })
    for path in _discover_sqlite_files():
        entries.append(_sqlite_entry(path))
    connections = _connection_entries()
    explicit_paths = {
        str(entry.get("detail") or "").replace("\\", "/").lower()
        for entry in connections
        if entry.get("engine") == "duckdb"
    }
    for path in _discover_duckdb_files():
        if _rel(path).lower() in explicit_paths or str(path).replace("\\", "/").lower() in explicit_paths:
            continue
        entries.append(_duckdb_entry(path))
    entries.extend(connections)
    return entries


def find_catalog_entry(db_id: str, catalog: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    for entry in catalog if catalog is not None else catalog_snapshot():
        if entry["id"] == db_id:
            return entry
    return None


def _readonly_conn(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn


def _count_rows(conn: sqlite3.Connection, qualified: str) -> Optional[int]:
    deadline = time.time() + 2.0
    conn.set_progress_handler(lambda: 1 if time.time() > deadline else 0, 20000)
    try:
        return int(conn.execute(f"SELECT COUNT(*) FROM {qualified}").fetchone()[0])
    except Exception:
        return None
    finally:
        conn.set_progress_handler(None, 0)


def get_table_details(
    db_id: str,
    schema: str,
    table: str,
    catalog: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    entry = find_catalog_entry(db_id, catalog)
    if not entry:
        raise ValueError("Database not found in catalog.")
    schema = (schema or "main").strip()
    table = (table or "").strip()
    if not table:
        raise ValueError("Table name is required.")
    result: Dict[str, Any] = {"db_id": db_id, "database": entry["name"], "schema": schema, "table": table, "columns": [], "row_count": None, "sample": []}

    if entry["kind"] == "workspace":
        conn = open_workspace_connection(entry["workspace_id"])
        try:
            cols = conn.execute(f"PRAGMA {_quote(schema)}.table_info({_quote(table)})").fetchall()
            result["columns"] = [
                {"name": c[1], "data_type": c[2] or "TEXT", "not_null": bool(c[3]), "is_pk": bool(c[5]), "default": c[4]}
                for c in cols
            ]
            try:
                result["foreign_keys"] = [dict(r) for r in conn.execute(f"PRAGMA {_quote(schema)}.foreign_key_list({_quote(table)})").fetchall()]
            except Exception:
                pass
            try:
                result["indexes"] = [dict(r) for r in conn.execute(f"PRAGMA {_quote(schema)}.index_list({_quote(table)})").fetchall()]
            except Exception:
                pass
            result["row_count"] = _count_rows(conn, f"{_quote(schema)}.{_quote(table)}")
            result["sample"] = [dict(r) for r in conn.execute(f"SELECT * FROM {_quote(schema)}.{_quote(table)} LIMIT 5").fetchall()]
            ddl = conn.execute(
                f"SELECT sql FROM {_quote(schema)}.sqlite_master WHERE type IN ('table','view') AND name = ?", (table,)
            ).fetchone()
            result["ddl"] = ddl[0] if ddl else ""
        finally:
            conn.close()
        return result

    if entry["kind"] == "sqlite":
        path = ROOT / entry["location"]
        conn = _readonly_conn(path)
        try:
            cols = conn.execute(f"PRAGMA {_quote(schema)}.table_info({_quote(table)})").fetchall()
            result["columns"] = [
                {"name": c[1], "data_type": c[2] or "TEXT", "not_null": bool(c[3]), "is_pk": bool(c[5]), "default": c[4]}
                for c in cols
            ]
            result["row_count"] = _count_rows(conn, f"{_quote(schema)}.{_quote(table)}")
            result["sample"] = [dict(r) for r in conn.execute(f"SELECT * FROM {_quote(schema)}.{_quote(table)} LIMIT 5").fetchall()]
            ddl = conn.execute("SELECT sql FROM sqlite_master WHERE type IN ('table','view') AND name = ?", (table,)).fetchone()
            result["ddl"] = ddl[0] if ddl else ""
        finally:
            conn.close()
        return result

    if entry["kind"] == "duckdb":
        try:
            import duckdb  # type: ignore

            con = duckdb.connect(str(ROOT / entry["location"]), read_only=True)
            try:
                desc = con.execute(f'DESCRIBE {_quote(table)}').fetchall()
                result["columns"] = [
                    {"name": d[0], "data_type": d[1], "not_null": str(d[2]).upper() == "NO", "is_pk": False} for d in desc
                ]
                result["row_count"] = int(con.execute(f'SELECT COUNT(*) FROM {_quote(table)}').fetchone()[0])
                rows = con.execute(f'SELECT * FROM {_quote(table)} LIMIT 5').fetchall()
                names = [c[0] for c in con.description]
                result["sample"] = [dict(zip(names, r)) for r in rows]
            finally:
                con.close()
        except Exception as exc:
            result["error"] = str(exc)[:200]
        return result

    if entry["kind"] == "connection" and entry.get("engine") == "snowflake":
        try:
            from app.core import snowflake_client

            if "." in schema:
                db_name, schema_name = schema.split(".", 1)
            else:
                db_name = str(snowflake_client.load_config().get("database") or "").strip()
                schema_name = schema
                if not db_name:
                    raise ValueError("This Snowflake schema is not qualified with a database name.")
            qualified = f'"{db_name}"."{schema_name}"."{table}"'
            conn = snowflake_client.open_connection()
            try:
                cur = conn.cursor()
                cur.execute(f"DESCRIBE TABLE {qualified}")
                desc_rows = cur.fetchall()
                desc_names = [d[0].lower() for d in cur.description]
                di = {n: i for i, n in enumerate(desc_names)}
                columns = []
                for row in desc_rows:
                    columns.append({
                        "name": row[di.get("name", 0)],
                        "data_type": row[di.get("type", 1)],
                        "not_null": str(row[di.get("null?", 3)] if "null?" in di else "").upper() in ("N", "NO", "NOT NULL"),
                        "is_pk": str(row[di.get("primary key", 5)] if "primary key" in di else "").upper() in ("Y", "YES"),
                        "default": row[di.get("default", 4)] if "default" in di else None,
                    })
                result["columns"] = columns
                cur.execute(f"SELECT COUNT(*) FROM {qualified}")
                result["row_count"] = int(cur.fetchone()[0] or 0)
                cur.execute(f"SELECT * FROM {qualified} LIMIT 5")
                sample_cols = [d[0] for d in cur.description]
                result["sample"] = [
                    {sample_cols[i]: snowflake_client.json_safe(row[i]) for i in range(len(sample_cols))}
                    for row in cur.fetchall()
                ]
                result["ddl"] = ""
                cur.close()
            finally:
                conn.close()
        except Exception as exc:
            result["error"] = str(exc)[:200]
        return result

    if entry["kind"] == "connection":
        try:
            from app.core import live_catalog

            details = live_catalog.table_details(entry["connection"], schema, table)
            result.update({
                "database": details.get("database") or entry["name"],
                "columns": details.get("columns") or [],
                "row_count": details.get("row_count"),
                "sample": details.get("sample") or [],
                "ddl": details.get("ddl") or "",
            })
            for key in ("size_bytes", "last_modified", "content_type", "error", "foreign_keys", "indexes"):
                if details.get(key) is not None:
                    result[key] = details[key]
        except Exception as exc:
            result["error"] = str(exc)[:300]
    return result


# ----------------------------------------------------------------------------
# SQL execution
# ----------------------------------------------------------------------------

def _assert_single_statement(sql: str) -> str:
    text = (sql or "").strip()
    if not text:
        raise ValueError("No SQL was generated.")
    if text.endswith(";"):
        text = text[:-1].rstrip()
    if ";" in text:
        raise ValueError("Only one SQL statement can run per message.")
    return text


def _qualified(schema: str, table: str) -> str:
    return f"{_quote(schema)}.{_quote(table)}"


def _strip_ident(token: str) -> str:
    token = (token or "").strip()
    if len(token) >= 2 and token[0] in '"`[':
        closer = "]" if token[0] == "[" else token[0]
        if token.endswith(closer):
            token = token[1:-1]
    return token.replace('""', '"')


def _split_qualified(ref: str) -> List[str]:
    return [_strip_ident(part) for part in re.findall(_IDENT, (ref or "").strip())]


def _assert_alter_allowed(statement: str) -> None:
    if not re.match(r"^\s*alter\b", statement, re.IGNORECASE):
        return
    if not re.match(r"^\s*alter\s+table\b", statement, re.IGNORECASE):
        raise ValueError("Only ALTER TABLE is allowed (add column, rename, or change a datatype).")
    if not any(pattern.match(statement) for pattern in _ALTER_ALLOWED):
        raise ValueError(
            "That ALTER is blocked. Chat supports ALTER TABLE ... ADD COLUMN, RENAME COLUMN / RENAME TO, "
            "and datatype changes only. Dropping columns or tables stays blocked."
        )


_TYPE_KEYWORD = re.compile(r"\b(default|not|null|primary|unique|references|check|collate|constraint)\b", re.IGNORECASE)


def _sqlite_rebuild_column(conn: sqlite3.Connection, table_ref: str, column: str, new_type: str) -> Dict[str, Any]:
    parts = _split_qualified(table_ref)
    if not parts:
        raise ValueError("Could not read the table name.")
    table = parts[-1]
    schema = parts[-2] if len(parts) > 1 else "main"
    new_type = (new_type or "").strip()
    if not new_type or not re.fullmatch(r"[A-Za-z0-9_(),\s]+", new_type) or _TYPE_KEYWORD.search(new_type):
        raise ValueError("Use only a datatype in a type change, e.g. ALTER TABLE t ALTER COLUMN c TYPE VARCHAR(80).")
    q_schema, q_table = _quote(schema), _quote(table)
    info = conn.execute(f"PRAGMA {q_schema}.table_info({q_table})").fetchall()
    if not info:
        raise ValueError(f"Table {schema}.{table} was not found.")
    target = next((row[1] for row in info if str(row[1]).lower() == column.lower()), None)
    if not target:
        raise ValueError(f"Column {column} was not found in {schema}.{table}.")
    ddl_row = conn.execute(
        f"SELECT sql FROM {q_schema}.sqlite_master WHERE type = 'table' AND name = ?", (table,)
    ).fetchone()
    original_ddl = (ddl_row[0] if ddl_row else "") or ""
    if re.search(r"\bgenerated\b", original_ddl, re.IGNORECASE):
        raise ValueError("This table has generated columns; SQLite cannot rebuild it automatically.")
    if re.search(r"\b(check|collate|without\s+rowid)\b", original_ddl, re.IGNORECASE):
        raise ValueError(
            "This table uses CHECK / COLLATE / WITHOUT ROWID options that SQLite cannot rebuild safely. "
            "Recreate the table instead."
        )
    autoincrement = bool(re.search(r"\bautoincrement\b", original_ddl, re.IGNORECASE))
    pk_count = sum(1 for row in info if row[5])
    defs: List[str] = []
    for _, name, ctype, notnull, default, pk in info:
        col_type = new_type if str(name).lower() == target.lower() else (ctype or "TEXT")
        piece = f"{_quote(name)} {col_type}"
        if pk and pk_count == 1:
            piece += " PRIMARY KEY"
            if autoincrement and "INT" in str(col_type).upper():
                piece += " AUTOINCREMENT"
        if notnull:
            piece += " NOT NULL"
        if default is not None:
            piece += f" DEFAULT {default}"
        defs.append(piece)
    if pk_count > 1:
        defs.append("PRIMARY KEY (" + ", ".join(_quote(row[1]) for row in info if row[5]) + ")")
    try:
        for index in conn.execute(f"PRAGMA {q_schema}.index_list({q_table})").fetchall():
            if not index[2] or index[3] != "u":
                continue
            index_cols = [
                row[2] for row in conn.execute(f"PRAGMA {q_schema}.index_info({_quote(index[1])})").fetchall()
            ]
            if index_cols:
                defs.append("UNIQUE (" + ", ".join(_quote(col) for col in index_cols) + ")")
    except sqlite3.Error:
        pass
    try:
        fk_groups: Dict[int, Dict[str, Any]] = {}
        for fk in conn.execute(f"PRAGMA {q_schema}.foreign_key_list({q_table})").fetchall():
            group = fk_groups.setdefault(
                fk[0],
                {"table": fk[2], "pairs": [], "on_update": fk[5], "on_delete": fk[6]},
            )
            group["pairs"].append((fk[1], fk[3], fk[4]))
        for group in fk_groups.values():
            pairs = sorted(group["pairs"])
            clause = (
                "FOREIGN KEY (" + ", ".join(_quote(pair[1]) for pair in pairs) + ")"
                f" REFERENCES {_quote(group['table'])} (" + ", ".join(_quote(pair[2]) for pair in pairs) + ")"
            )
            if group.get("on_update") and str(group["on_update"]).upper() != "NO ACTION":
                clause += f" ON UPDATE {group['on_update']}"
            if group.get("on_delete") and str(group["on_delete"]).upper() != "NO ACTION":
                clause += f" ON DELETE {group['on_delete']}"
            defs.append(clause)
    except sqlite3.Error:
        pass
    tmp = f"__dm_rebuild_{int(time.time() * 1000)}"
    q_tmp = _quote(tmp)
    cols = ", ".join(_quote(row[1]) for row in info)
    conn.execute(f"CREATE TABLE {q_schema}.{q_tmp} (" + ", ".join(defs) + ")")
    conn.execute(f"INSERT INTO {q_schema}.{q_tmp} ({cols}) SELECT {cols} FROM {q_schema}.{q_table}")
    conn.execute(f"DROP TABLE {q_schema}.{q_table}")
    conn.execute(f"ALTER TABLE {q_schema}.{q_tmp} RENAME TO {q_table}")
    extras = conn.execute(
        f"SELECT sql FROM {q_schema}.sqlite_master WHERE type IN ('index','trigger') AND tbl_name = ? AND sql IS NOT NULL",
        (table,),
    ).fetchall()
    for (sql_text,) in extras:
        try:
            conn.execute(sql_text)
        except sqlite3.Error:
            pass
    return {"table": f"{schema}.{table}", "column": target, "type": new_type}


def _execute_snowflake(statement: str, limit: int) -> Dict[str, Any]:
    from app.core import snowflake_client

    if re.search(r"or\s+replace\s+table", statement, re.IGNORECASE):
        raise ValueError("CREATE OR REPLACE TABLE is blocked because it overwrites data.")
    conn = snowflake_client.open_connection()
    started = time.time()
    try:
        cur = conn.cursor()
        cur.execute(statement)
        columns = [d[0] for d in cur.description] if cur.description else []
        rows_raw = cur.fetchmany(limit + 1) if cur.description else []
        truncated = len(rows_raw) > limit
        rows = [
            {columns[i]: snowflake_client.json_safe(row[i]) for i in range(len(columns))}
            for row in rows_raw[:limit]
        ]
        conn.commit()
        if not _READ_PREFIX.match(statement):
            invalidate_catalog()
            snowflake_client.clear_catalog_cache()
        return {
            "success": True,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "rows_affected": max(0, int(getattr(cur, "rowcount", 0) or 0)) if not cur.description else 0,
            "truncated": truncated,
            "execution_time_ms": round((time.time() - started) * 1000, 2),
        }
    finally:
        try:
            conn.close()
        except Exception:
            pass


def execute_sql(db_id: str, sql: str, limit: int = MAX_PREVIEW_ROWS, workspace_id: str = "") -> Dict[str, Any]:
    statement = _assert_single_statement(sql)
    _assert_alter_allowed(statement)
    in_workspace = db_id.startswith("workspace:")
    if _DESTRUCTIVE.search(statement):
        if not in_workspace:
            raise ValueError("Destructive SQL (DROP/DELETE/TRUNCATE/ATTACH/GRANT) is blocked on live databases.")
        if re.match(r"^\s*delete\b", statement, re.IGNORECASE) and not re.search(r"\bwhere\b", statement, re.IGNORECASE):
            raise ValueError("DELETE inside a workspace must include a WHERE clause.")
        if re.match(r"^\s*drop\b", statement, re.IGNORECASE) and not re.match(
            r"^\s*drop\s+(table|view|index)\b", statement, re.IGNORECASE
        ):
            raise ValueError("Only DROP TABLE / VIEW / INDEX is allowed inside a workspace.")
        if re.search(r"\b(attach|detach|vacuum|reindex|grant|revoke)\b", statement, re.IGNORECASE):
            raise ValueError("That statement is blocked even inside a workspace.")

    if db_id.startswith("workspace:"):
        wid = db_id.split(":", 1)[1]
        if workspace_id and workspace_id != wid:
            raise ValueError("Cross-workspace writes are not allowed.")
        conn = open_workspace_connection(wid)
        try:
            is_alter = bool(re.match(r"^\s*alter\s+table\b", statement, re.IGNORECASE))
            if not (_READ_PREFIX.match(statement) or _WRITE_PREFIX.match(statement) or is_alter):
                raise ValueError(
                    "Only SELECT, CREATE TABLE/VIEW/INDEX, INSERT, UPDATE and safe ALTER TABLE are allowed in a workspace."
                )
            started = time.time()
            rebuilt = None
            cur = None
            if is_alter:
                type_change = _SQLITE_TYPE_CHANGE.match(statement) or _SQLITE_MODIFY.match(statement)
                if type_change:
                    rebuilt = _sqlite_rebuild_column(
                        conn,
                        type_change.group("table"),
                        _strip_ident(type_change.group("column")),
                        type_change.group("type"),
                    )
                else:
                    cur = conn.execute(statement)
            else:
                cur = conn.execute(statement)
            columns: List[str] = [d[0] for d in cur.description] if cur is not None and cur.description else []
            rows_raw = cur.fetchmany(limit + 1) if cur is not None and cur.description else []
            truncated = len(rows_raw) > limit
            rows = [dict(r) for r in rows_raw[:limit]]
            conn.commit()
            if not _READ_PREFIX.match(statement):
                invalidate_catalog()
            result = {
                "success": True,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "rows_affected": max(0, int(cur.rowcount or 0)) if cur is not None and not cur.description else 0,
                "truncated": truncated,
                "execution_time_ms": round((time.time() - started) * 1000, 2),
            }
            if rebuilt:
                result["rebuilt"] = rebuilt
            return result
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    entry = find_catalog_entry(db_id)
    if not entry:
        raise ValueError("Database not found in catalog.")

    if entry["kind"] == "connection" and entry.get("engine") == "snowflake":
        if not (_READ_PREFIX.match(statement) or _SNOWFLAKE_WRITE.match(statement)):
            raise ValueError(
                "Snowflake allows SELECT, CREATE (database/schema/table/view), INSERT, MERGE, UPDATE "
                "and safe ALTER TABLE (add column, rename, datatype change). DROP, DELETE and TRUNCATE stay blocked."
            )
        return _execute_snowflake(statement, limit)

    if not _READ_PREFIX.match(statement):
        raise ValueError("This database is read-only. Only SELECT / WITH / PRAGMA queries are allowed.")

    started = time.time()
    if entry["kind"] == "sqlite":
        conn = _readonly_conn(ROOT / entry["location"])
        try:
            cur = conn.execute(statement)
            columns = [d[0] for d in cur.description] if cur.description else []
            rows_raw = cur.fetchmany(limit + 1)
            truncated = len(rows_raw) > limit
            return {
                "success": True,
                "columns": columns,
                "rows": [dict(r) for r in rows_raw[:limit]],
                "row_count": min(len(rows_raw), limit),
                "truncated": truncated,
                "execution_time_ms": round((time.time() - started) * 1000, 2),
            }
        finally:
            conn.close()

    if entry["kind"] == "duckdb":
        import duckdb  # type: ignore

        con = duckdb.connect(str(ROOT / entry["location"]), read_only=True)
        try:
            cur = con.execute(statement)
            columns = [d[0] for d in cur.description] if cur.description else []
            rows_raw = cur.fetchmany(limit + 1)
            names = columns
            return {
                "success": True,
                "columns": columns,
                "rows": [dict(zip(names, r)) for r in rows_raw[:limit]],
                "row_count": min(len(rows_raw), limit),
                "truncated": len(rows_raw) > limit,
                "execution_time_ms": round((time.time() - started) * 1000, 2),
            }
        finally:
            con.close()

    from app.core import live_catalog

    res = live_catalog.execute_read(entry["connection"], statement, limit)
    if not res.get("success"):
        raise ValueError(res.get("error") or "Query failed.")
    return res


def save_run(workspace_id: str, sql: str, result: Dict[str, Any]) -> str:
    run_id = "run_" + uuid.uuid4().hex[:12]
    rows = []
    for row in result.get("rows", [])[:5000]:
        rows.append({k: _clip(v, 2000) for k, v in row.items()})
    with db.get_connection() as conn:
        conn.execute(
            "INSERT INTO dm_runs (run_id, workspace_id, sql_text, columns, rows, row_count, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (run_id, workspace_id, sql, json.dumps(result.get("columns", [])), json.dumps(rows, default=str), result.get("row_count", len(rows)), _now()),
        )
        conn.commit()
    return run_id


def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    with db.get_connection() as conn:
        row = conn.execute("SELECT * FROM dm_runs WHERE run_id = ?", (run_id,)).fetchone()
    if not row:
        return None
    data = dict(row)
    try:
        data["columns"] = json.loads(data.get("columns") or "[]")
        data["rows"] = json.loads(data.get("rows") or "[]")
    except Exception:
        data["columns"], data["rows"] = [], []
    return data


MAX_EXPORT_ROWS = 50000

_EXPORT_FORMATS: Dict[str, Dict[str, str]] = {
    "csv": {"ext": ".csv", "media": "text/csv; charset=utf-8", "delimiter": ","},
    "xlsx": {
        "ext": ".xlsx",
        "media": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "delimiter": "",
    },
    "pipe": {"ext": ".txt", "media": "text/plain; charset=utf-8", "delimiter": "|"},
    "tab": {"ext": ".tsv", "media": "text/tab-separated-values; charset=utf-8", "delimiter": "\t"},
}

_EXPORT_ALIASES = {
    "csv": "csv",
    "xlsx": "xlsx",
    "excel": "xlsx",
    "xls": "xlsx",
    "txt": "pipe",
    "text": "pipe",
    "pipe": "pipe",
    "psv": "pipe",
    "tsv": "tab",
    "tab": "tab",
    "tsv-tab": "tab",
}


def _normalize_export_format(value: str) -> str:
    key = (value or "csv").strip().lower()
    fmt = _EXPORT_ALIASES.get(key)
    if not fmt:
        raise ValueError(f"Unsupported download format '{value}'. Use csv, excel, pipe or tab.")
    return fmt


def _export_filename(stem: str, fmt: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", (stem or "export").strip()).strip("._")
    if not clean:
        clean = "export"
    return clean[:80] + _EXPORT_FORMATS[fmt]["ext"]


def _cell_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, default=str)
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return str(value)


def _excel_cell(value: Any) -> Any:
    if value is None or isinstance(value, (int, float, bool, datetime, date)):
        return value
    text = _cell_text(value)
    # openpyxl rejects the C0 control characters Excel cannot store.
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", text)


def _serialize_rows(columns: List[str], rows: List[Dict[str, Any]], fmt: str) -> Any:
    if fmt == "xlsx":
        try:
            from openpyxl import Workbook  # type: ignore
        except Exception as exc:
            raise ValueError("Excel export needs the openpyxl package on the server.") from exc
        workbook = Workbook(write_only=True)
        sheet = workbook.create_sheet(title="Data")
        sheet.append([_excel_cell(column) for column in columns])
        for row in rows:
            sheet.append([_excel_cell(row.get(column)) for column in columns])
        buf = io.BytesIO()
        workbook.save(buf)
        return buf.getvalue()

    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=_EXPORT_FORMATS[fmt]["delimiter"], lineterminator="\r\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow([_cell_text(row.get(column)) for column in columns])
    text = buf.getvalue()
    # Excel needs a BOM to decode non-ASCII CSV correctly.
    return "\ufeff" + text if fmt == "csv" else text


def run_to_export(run_id: str, fmt: str = "csv") -> Tuple[str, Any, str]:
    run = get_run(run_id)
    if not run:
        raise ValueError("Result set not found.")
    fmt = _normalize_export_format(fmt)
    columns = run.get("columns") or []
    rows = run.get("rows") or []
    content = _serialize_rows(columns, rows, fmt)
    return _export_filename(run_id, fmt), content, _EXPORT_FORMATS[fmt]["media"]


def run_to_csv(run_id: str) -> Tuple[str, str]:
    filename, content, _media = run_to_export(run_id, "csv")
    return filename, content


def _export_table_ref(entry: Dict[str, Any], schema: str, table: str) -> str:
    schema = (schema or "main").strip() or "main"
    table = (table or "").strip()
    if not table:
        raise ValueError("Table name is required.")
    engine = str(entry.get("engine") or "")
    if engine == "snowflake":
        from app.core import snowflake_client

        if "." in schema:
            db_name, schema_name = schema.split(".", 1)
        else:
            db_name = str(snowflake_client.load_config().get("database") or "").strip()
            schema_name = schema
            if not db_name:
                raise ValueError("This Snowflake table is not qualified with a database name.")
        return f'"{db_name}"."{schema_name}"."{table}"'
    if engine == "bigquery":
        project = str(entry.get("project") or "").strip()
        dataset = schema.split(".", 1)[-1]
        return f"`{project}.{dataset}.{table}`" if project else f"`{dataset}.{table}`"
    if engine in ("postgres", "oracle", "duckdb", "sqlite"):
        return f"{_quote(schema)}.{_quote(table)}"
    raise ValueError(f"Download is not supported for engine '{engine or entry.get('kind')}'.")


def table_to_export(
    db_id: str, schema: str = "main", table: str = "", fmt: str = "csv", limit: int = MAX_EXPORT_ROWS
) -> Tuple[str, Any, str]:
    entry = find_catalog_entry(db_id)
    if not entry:
        raise ValueError("Database not found in catalog.")
    fmt = _normalize_export_format(fmt)
    ref = _export_table_ref(entry, schema, table)
    workspace_id = entry.get("workspace_id") or (db_id.split(":", 1)[1] if db_id.startswith("workspace:") else "")
    result = execute_sql(db_id, f"SELECT * FROM {ref}", limit=limit, workspace_id=workspace_id)
    columns = result.get("columns") or []
    rows = result.get("rows") or []
    content = _serialize_rows(columns, rows, fmt)
    stem = f"{(schema or 'main').replace('.', '_')}_{table}" if entry.get("engine") != "workspace" else table
    return _export_filename(stem, fmt), content, _EXPORT_FORMATS[fmt]["media"]


def _export_stem(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", (value or "").strip()).strip("_") or "extract"


def deliver_report(
    workspace_id: str,
    table: str = "",
    sql: str = "",
    db_id: str = "",
    schema: str = "main",
    fmt: str = "xlsx",
    limit: int = 100,
    channels: Any = None,
    recipient: str = "",
    phone: str = "",
    subject: str = "",
    user: str = "",
    project_key: str = "",
) -> Dict[str, Any]:
    """Exports a dataset to SFTP, then pushes it to email, Telegram and WhatsApp."""
    workspace = get_workspace(workspace_id)
    if not workspace:
        raise ValueError("Workspace not found.")
    fmt = _normalize_export_format(fmt)
    limit = max(1, min(int(limit or 100), MAX_EXPORT_ROWS))
    target = (db_id or "").strip() or ("workspace:" + workspace_id)
    if target in ("workspace", "active", workspace_id):
        target = "workspace:" + workspace_id
    entry = find_catalog_entry(target)
    if not entry:
        raise ValueError("Database not found in catalog.")
    ws_arg = workspace_id if target.startswith("workspace:") else ""

    table = (table or "").strip()
    if table and "." in table:
        schema, table = table.split(".", 1)
    if sql:
        statement = sql.strip()
        if not re.match(r"^\s*(select|with|pragma|explain)\b", statement, re.IGNORECASE):
            raise ValueError("Report delivery only runs read-only SELECT queries.")
        result = execute_sql(target, statement, limit=limit, workspace_id=ws_arg)
        stem_source = table or "query"
    elif table:
        ref = _export_table_ref(entry, schema or "main", table)
        result = execute_sql(target, f"SELECT * FROM {ref}", limit=limit, workspace_id=ws_arg)
        statement = f"SELECT * FROM {ref}"
        stem_source = table
    else:
        raise ValueError("Tell me which table or query to send.")

    columns = result.get("columns") or []
    rows = result.get("rows") or []
    if not columns:
        raise ValueError("That query returned no columns, so there is nothing to send.")
    content = _serialize_rows(columns, rows, fmt)
    stem = _export_stem(f"{workspace['name']}_{stem_source}")
    now = datetime.now(timezone.utc)
    from app.core.cloud_sftp_hub import SFTP_BASE_DIR, cloud_sftp_hub

    sftp_res = cloud_sftp_hub.export_report_to_sftp(stem, content, file_format=_EXPORT_FORMATS[fmt]["ext"].lstrip("."), project_key=project_key)
    local_path = sftp_res.get("sftp_local_path") or ""
    sftp_path = "/" + os.path.relpath(local_path, str(SFTP_BASE_DIR)).replace(os.sep, "/") if local_path else ""
    s3_uri = (sftp_res.get("s3_mirror") or {}).get("s3_uri") or ""
    size_kb = round((sftp_res.get("size_bytes") or 0) / 1024.0, 1)
    label = f"{limit if len(rows) >= limit else len(rows)} row(s)"
    summary = (
        f"NanoPro data extract: {workspace['name']} / {stem_source}\n"
        f"Rows: {len(rows)}{' (top ' + str(limit) + ')' if len(rows) >= limit else ''} | Columns: {len(columns)}\n"
        f"Format: {fmt.upper()} | Size: {size_kb} KB\n"
        f"Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"SFTP path: {sftp_path}\n"
        + (f"S3 mirror: {s3_uri}\n" if s3_uri else "")
        + f"Columns: {', '.join(str(c) for c in columns[:12])}{' …' if len(columns) > 12 else ''}"
    )

    want = channels if isinstance(channels, (list, tuple)) else ([channels] if channels else [])
    want = [str(c).strip().lower() for c in want if str(c).strip()]
    if not want:
        want = ["email", "telegram", "whatsapp"]

    delivery: Dict[str, Any] = {}
    subject = subject or f"{workspace['name']} extract — {stem_source} ({len(rows)} rows)"
    if "email" in want or "mail" in want:
        try:
            from app.core.smtp_client import smtp_client

            html_summary = "<pre style=\"font-family:Consolas,monospace;font-size:13px\">" + summary.replace("&", "&amp;").replace("<", "&lt;") + "</pre>"
            email_res = smtp_client.send_email(
                recipient=recipient or smtp_client.default_recipient,
                subject=subject,
                body=summary,
                html_body=html_summary,
                attachments=[local_path] if local_path else None,
                task_id="dm_delivery",
                report_name=stem,
                data_source=target,
            )
            provider = str(email_res.get("provider") or email_res.get("status") or "")
            telegram_fallback = "telegram" in provider.lower()
            delivery["email"] = {
                "status": "sent" if email_res.get("success") and not telegram_fallback else ("fallback" if email_res.get("success") else "failed"),
                "provider": provider,
                "recipient": recipient or smtp_client.default_recipient,
                "error": email_res.get("error") or ("" if not telegram_fallback else "No email provider configured; alert reached Telegram instead."),
            }
        except Exception as exc:
            delivery["email"] = {"status": "failed", "error": str(exc)[:300]}
    if "telegram" in want or "tg" in want:
        try:
            from app.core.telegram_router import send_telegram_routed_message

            tg_res = send_telegram_routed_message(
                category="reports",
                text=f"<b>{subject}</b>\n<pre>{summary}</pre>",
                document_path=local_path or None,
            )
            delivery["telegram"] = {
                "status": "sent" if (tg_res.get("success") or tg_res.get("status") in ("success", "sent")) else "failed",
                "detail": str(tg_res.get("error") or tg_res.get("status") or "")[:200],
            }
        except Exception as exc:
            delivery["telegram"] = {"status": "failed", "error": str(exc)[:300]}
    if "whatsapp" in want or "wa" in want:
        phone = (phone or os.environ.get("WHATSAPP_PHONE") or "").strip()
        if not phone:
            delivery["whatsapp"] = {"status": "skipped", "note": "No WhatsApp number configured (set WHATSAPP_PHONE or pass phone)."}
        else:
            try:
                from app.core.communication_center import communication_center

                wa_res = communication_center.send_whatsapp_free_message(phone, summary)
                delivery["whatsapp"] = {
                    "status": "sent" if wa_res.get("status") in ("success", "sent") or wa_res.get("success") else "link",
                    "detail": str(wa_res.get("whatsapp_web_link") or wa_res.get("message") or wa_res.get("error") or "")[:300],
                }
            except Exception as exc:
                delivery["whatsapp"] = {"status": "failed", "error": str(exc)[:300]}

    sent = [name for name, info in delivery.items() if info.get("status") == "sent"]
    missed = [f"{name} ({info.get('status')})" for name, info in delivery.items() if info.get("status") != "sent"]
    reply = (
        f"Prepared {len(rows)} {fmt.upper()} rows from {stem_source} and published them to SFTP {sftp_path or local_path}. "
        f"Delivered via {', '.join(sent) if sent else 'no channel'}"
        + (f". Not sent: {', '.join(missed)}." if missed else ".")
    )
    return {
        "status": "success" if sent else "partial",
        "table": stem_source,
        "sql": statement,
        "format": fmt,
        "rows": len(rows),
        "columns": columns,
        "file_name": sftp_res.get("file_name"),
        "local_path": local_path,
        "sftp_path": sftp_path,
        "size_kb": size_kb,
        "s3_mirror": sftp_res.get("s3_mirror") or {},
        "channels": delivery,
        "summary": summary,
        "reply": reply,
        "user": user,
    }


# ----------------------------------------------------------------------------
# schedules, batch windows and pipelines
# ----------------------------------------------------------------------------

_ALIAS_TIMES = {"bod": "00:15", "sod": "07:00", "eod": "22:00"}


def _parse_hhmm(value: str) -> Tuple[int, int]:
    match = re.fullmatch(r"\s*(\d{1,2}):(\d{2})\s*", value or "")
    if not match:
        raise ValueError("Time must look like HH:MM, for example 02:30.")
    hour, minute = int(match.group(1)), int(match.group(2))
    if not (0 <= hour < 24 and 0 <= minute < 60):
        raise ValueError("Time must be between 00:00 and 23:59.")
    return hour, minute


def _alias_time(frequency: str) -> str:
    text = (frequency or "").lower()
    for alias, value in _ALIAS_TIMES.items():
        if re.search(r"\b" + alias + r"\b", text):
            return value
    return ""


def _normalize_frequency(value: str) -> str:
    text = (value or "").strip().lower()
    if re.search(r"\b(adhoc|ad-hoc|manual|on[ -]?demand|trigger)\b", text):
        return "adhoc"
    if re.search(r"\b(once|one[ -]?time|single)\b", text):
        return "once"
    if "quarter" in text:
        return "quarterly"
    if "month" in text:
        return "monthly"
    if "week" in text:
        return "weekly"
    if "cron" in text or (len(text.split()) >= 5 and re.fullmatch(r"[\d*/,\-\s?]+", text)):
        return "cron"
    return "daily"


def _cron_set(spec: str, low: int, high: int) -> set:
    values = set()
    for part in (spec or "*").split(","):
        part = part.strip()
        if not part:
            continue
        step = 1
        if "/" in part:
            part, raw_step = part.split("/", 1)
            try:
                step = max(1, int(raw_step))
            except ValueError:
                step = 1
        if part in ("*", "?"):
            start, end = low, high
        elif "-" in part:
            left, right = part.split("-", 1)
            try:
                start, end = int(left), int(right)
            except ValueError:
                continue
        else:
            try:
                start = end = int(part)
            except ValueError:
                continue
        for value in range(start, end + 1, step):
            if low <= value <= high:
                values.add(value)
    return values


def _cron_next(expr: str, base: datetime) -> Optional[str]:
    fields = (expr or "").split()
    if len(fields) < 5:
        return _next_run_at("daily", "02:00", base=base)
    minutes = _cron_set(fields[0], 0, 59)
    hours = _cron_set(fields[1], 0, 23)
    doms = _cron_set(fields[2], 1, 31)
    months = _cron_set(fields[3], 1, 12)
    dows = {0 if value == 7 else value for value in _cron_set(fields[4], 0, 7)}
    dom_any = fields[2] in ("*", "?")
    dow_any = fields[4] in ("*", "?")
    start = base.replace(second=0, microsecond=0) + timedelta(minutes=1)
    for offset in range(0, 366 * 24 * 60):
        moment = start + timedelta(minutes=offset)
        if moment.month not in months or moment.hour not in hours or moment.minute not in minutes:
            continue
        day_ok = moment.day in doms
        dow_ok = ((moment.weekday() + 1) % 7) in dows
        if dom_any and dow_any:
            return moment.isoformat(timespec="seconds")
        if dom_any and dow_ok:
            return moment.isoformat(timespec="seconds")
        if dow_any and day_ok:
            return moment.isoformat(timespec="seconds")
        if not dom_any and not dow_any and (day_ok or dow_ok):
            return moment.isoformat(timespec="seconds")
    return None


def _next_run_at(
    frequency: str,
    at_time: str = "",
    weekday: Optional[int] = None,
    day_of_month: Optional[int] = None,
    cron_expr: str = "",
    base: Optional[datetime] = None,
) -> Optional[str]:
    base = (base or datetime.now(timezone.utc)).replace(second=0, microsecond=0)
    frequency = (frequency or "daily").lower()
    if frequency == "adhoc":
        return None
    if frequency == "cron":
        return _cron_next(cron_expr, base)
    hour, minute = _parse_hhmm(at_time or "02:00")
    if frequency in ("once", "daily"):
        candidate = base.replace(hour=hour, minute=minute)
        if candidate <= base:
            candidate += timedelta(days=1)
        return candidate.isoformat(timespec="seconds")
    if frequency == "weekly":
        target = 0 if weekday is None else int(weekday) % 7
        candidate = (base + timedelta(days=(target - base.weekday()) % 7)).replace(hour=hour, minute=minute)
        if candidate <= base:
            candidate += timedelta(days=7)
        return candidate.isoformat(timespec="seconds")
    if frequency == "quarterly":
        for add_year in range(0, 3):
            for month in (1, 4, 7, 10):
                year = base.year + add_year
                day = max(1, min(int(day_of_month or 1), calendar.monthrange(year, month)[1]))
                candidate = base.replace(year=year, month=month, day=day, hour=hour, minute=minute)
                if candidate > base:
                    return candidate.isoformat(timespec="seconds")
        return None
    # monthly
    for add in range(0, 25):
        total = base.month - 1 + add
        year = base.year + total // 12
        month = total % 12 + 1
        day = max(1, min(int(day_of_month or 1), calendar.monthrange(year, month)[1]))
        candidate = base.replace(year=year, month=month, day=day, hour=hour, minute=minute)
        if candidate > base:
            return candidate.isoformat(timespec="seconds")
    return None


def _schedule_row(row: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(row)
    try:
        data["steps"] = json.loads(data.get("steps") or "[]")
    except Exception:
        data["steps"] = []
    data["enabled"] = bool(data.get("enabled"))
    return data


def describe_schedule(schedule: Dict[str, Any]) -> str:
    frequency = schedule.get("frequency") or "daily"
    if frequency == "cron":
        when = f"cron {schedule.get('cron_expr')}"
    elif frequency == "adhoc":
        when = "on demand"
    else:
        when = frequency
        if schedule.get("at_time"):
            when += f" at {schedule['at_time']} UTC"
        if frequency == "weekly" and schedule.get("weekday") is not None:
            when += f" (weekday {schedule['weekday']})"
        if frequency in ("monthly", "quarterly") and schedule.get("day_of_month"):
            when += f" (day {schedule['day_of_month']})"
    if schedule.get("next_run_at"):
        when += f", next run {schedule['next_run_at']}"
    return when


def _clean_steps(statements: Any, allow_workspace_delete: bool = False) -> List[str]:
    if isinstance(statements, str):
        statements = [statements]
    cleaned: List[str] = []
    for statement in statements or []:
        text = _assert_single_statement(str(statement))
        _assert_alter_allowed(text)
        if _DESTRUCTIVE.search(text):
            delete_ok = allow_workspace_delete and re.match(r"^\s*delete\s+from\b", text, re.IGNORECASE)
            if not delete_ok:
                raise ValueError("Scheduled steps cannot be destructive (DROP/DELETE/TRUNCATE).")
            if not re.search(r"\bwhere\b", text, re.IGNORECASE):
                # Rebuild steps delete the whole workspace table on purpose; the
                # execute_sql guard still needs an explicit predicate.
                text = text.rstrip().rstrip(";") + " WHERE 1=1"
        cleaned.append(text)
    if not cleaned:
        raise ValueError("A schedule needs at least one SQL statement.")
    if len(cleaned) > 20:
        raise ValueError("A schedule can hold at most 20 steps.")
    return cleaned


def create_schedule(
    workspace_id: str,
    name: str = "",
    statements: Any = None,
    frequency: str = "daily",
    at_time: str = "",
    weekday: Optional[int] = None,
    day_of_month: Optional[int] = None,
    cron_expr: str = "",
    target: str = "",
    user: str = "",
    kind: str = "sql",
) -> Dict[str, Any]:
    _ensure_schema()
    if not get_workspace(workspace_id):
        raise ValueError("Workspace not found.")
    target = (target or "").strip()
    if target in ("", "workspace", "active", "workspace:" + workspace_id):
        target = "workspace:" + workspace_id
    elif not find_catalog_entry(target):
        raise ValueError("Target database was not found in the live catalog.")
    steps = _clean_steps(statements, allow_workspace_delete=target.startswith("workspace:"))
    label = (name or "").strip()[:80] or "Scheduled job"
    frequency_norm = _normalize_frequency(frequency)
    at_time = (at_time or "").strip() or _alias_time(frequency)
    if at_time:
        _parse_hhmm(at_time)
    if frequency_norm == "cron" and len((cron_expr or "").split()) < 5:
        raise ValueError("Cron schedules need a 5-field expression, for example '0 2 * * *'.")
    weekday_i = int(weekday) if weekday not in (None, "") else None
    day_i = int(day_of_month) if day_of_month not in (None, "") else None
    schedule_id = "sch_" + uuid.uuid4().hex[:10]
    next_run = _next_run_at(frequency_norm, at_time, weekday_i, day_i, cron_expr)
    with db.get_connection() as conn:
        conn.execute(
            "INSERT INTO dm_schedules (schedule_id, workspace_id, name, kind, steps, target, frequency,"
            " at_time, weekday, day_of_month, cron_expr, enabled, next_run_at, created_by, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)",
            (
                schedule_id,
                workspace_id,
                label,
                "pipeline" if kind == "pipeline" or len(steps) > 1 else "sql",
                json.dumps(steps),
                target,
                frequency_norm,
                at_time or None,
                weekday_i,
                day_i,
                (cron_expr or "").strip() or None,
                next_run,
                user or "",
                _now(),
            ),
        )
        conn.commit()
    log_event(f"Data modeling schedule created: {schedule_id} ({label}) {frequency_norm}", component="DataModeling")
    return get_schedule(schedule_id) or {}


def get_schedule(schedule_id: str) -> Optional[Dict[str, Any]]:
    _ensure_schema()
    with db.get_connection() as conn:
        rows = _table_rows(conn, "SELECT * FROM dm_schedules WHERE schedule_id = ?", (schedule_id,))
    return _schedule_row(rows[0]) if rows else None


def list_schedules(workspace_id: str = "", limit: int = 200) -> List[Dict[str, Any]]:
    _ensure_schema()
    with db.get_connection() as conn:
        if workspace_id:
            rows = _table_rows(
                conn,
                "SELECT * FROM dm_schedules WHERE workspace_id = ? ORDER BY created_at DESC LIMIT ?",
                (workspace_id, max(1, min(limit, 500))),
            )
        else:
            rows = _table_rows(
                conn, "SELECT * FROM dm_schedules ORDER BY created_at DESC LIMIT ?", (max(1, min(limit, 500)),)
            )
    return [_schedule_row(row) for row in rows]


def schedule_runs(schedule_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    _ensure_schema()
    with db.get_connection() as conn:
        return _table_rows(
            conn,
            "SELECT * FROM dm_schedule_runs WHERE schedule_id = ? ORDER BY started_at DESC LIMIT ?",
            (schedule_id, max(1, min(limit, 200))),
        )


def delete_schedule(schedule_id: str) -> Dict[str, Any]:
    _ensure_schema()
    with db.get_connection() as conn:
        cursor = conn.execute("DELETE FROM dm_schedules WHERE schedule_id = ?", (schedule_id,))
        conn.execute("DELETE FROM dm_schedule_runs WHERE schedule_id = ?", (schedule_id,))
        conn.commit()
    if not cursor.rowcount:
        raise ValueError("Schedule not found.")
    return {"schedule_id": schedule_id, "deleted": True}


def set_schedule_enabled(schedule_id: str, enabled: bool) -> Dict[str, Any]:
    schedule = get_schedule(schedule_id)
    if not schedule:
        raise ValueError("Schedule not found.")
    next_run = schedule.get("next_run_at")
    if enabled and not next_run and schedule["frequency"] not in ("adhoc", "once"):
        next_run = _next_run_at(
            schedule["frequency"],
            schedule.get("at_time") or "",
            schedule.get("weekday"),
            schedule.get("day_of_month"),
            schedule.get("cron_expr") or "",
        )
    with db.get_connection() as conn:
        conn.execute(
            "UPDATE dm_schedules SET enabled = ?, next_run_at = ? WHERE schedule_id = ?",
            (1 if enabled else 0, next_run if enabled else None, schedule_id),
        )
        conn.commit()
    return get_schedule(schedule_id) or schedule


def run_schedule(schedule_id: str) -> Dict[str, Any]:
    schedule = get_schedule(schedule_id)
    if not schedule:
        raise ValueError("Schedule not found.")
    if not _schedule_run_lock.acquire(blocking=False):
        raise ValueError("This schedule is already running.")
    try:
        started = _now()
        results: List[Dict[str, Any]] = []
        status = "success"
        message = ""
        rows_affected = 0
        for statement in schedule.get("steps") or []:
            try:
                result = execute_sql(schedule["target"], statement, workspace_id=schedule["workspace_id"])
                rows = int(result.get("rows_affected") or result.get("row_count") or 0)
                rows_affected += rows
                results.append({"sql": statement, "status": "ok", "row_count": rows})
            except Exception as exc:
                status = "failed"
                message = str(exc)[:400]
                results.append({"sql": statement, "status": "failed", "error": message})
                break
        finished = _now()
        enabled = 1 if schedule.get("enabled") else 0
        next_run = schedule.get("next_run_at")
        if status == "success":
            if schedule["frequency"] == "once":
                enabled = 0
                next_run = None
            elif schedule["frequency"] != "adhoc":
                next_run = _next_run_at(
                    schedule["frequency"],
                    schedule.get("at_time") or "",
                    schedule.get("weekday"),
                    schedule.get("day_of_month"),
                    schedule.get("cron_expr") or "",
                )
        elif schedule["frequency"] not in ("adhoc", "once"):
            next_run = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat(timespec="seconds")
        run_id = "srun_" + uuid.uuid4().hex[:10]
        with db.get_connection() as conn:
            conn.execute(
                "UPDATE dm_schedules SET last_run_at = ?, last_status = ?, next_run_at = ?, enabled = ? WHERE schedule_id = ?",
                (started, status, next_run, enabled, schedule_id),
            )
            conn.execute(
                "INSERT INTO dm_schedule_runs (run_id, schedule_id, started_at, finished_at, status, message, statements, rows_affected)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (run_id, schedule_id, started, finished, status, message, len(results), rows_affected),
            )
            conn.commit()
        return {
            "status": status,
            "run_id": run_id,
            "schedule": get_schedule(schedule_id) or schedule,
            "results": results,
            "rows_affected": rows_affected,
            "message": message,
            "next_run_at": next_run,
        }
    finally:
        _schedule_run_lock.release()


def _run_due_schedules() -> int:
    _ensure_schema()
    with db.get_connection() as conn:
        rows = _table_rows(
            conn,
            "SELECT schedule_id, name FROM dm_schedules WHERE enabled = 1 AND next_run_at IS NOT NULL AND next_run_at <= ?",
            (_now(),),
        )
    ran = 0
    for row in rows:
        try:
            result = run_schedule(row["schedule_id"])
            ran += 1
            log_event(
                f"Scheduled job {row['name']} finished with {result['status']}",
                component="DataModeling",
                level="INFO" if result["status"] == "success" else "WARNING",
            )
        except Exception as exc:
            log_event(f"Scheduled job {row['name']} failed: {exc}", component="DataModeling", level="WARNING")
    return ran


def _scheduler_loop() -> None:
    while True:
        try:
            _run_due_schedules()
        except Exception as exc:
            log_event(f"Data modeling scheduler tick failed: {exc}", component="DataModeling", level="WARNING")
        time.sleep(20.0)


def start_scheduler() -> bool:
    global _scheduler_thread
    with _scheduler_start_lock:
        if _scheduler_thread and _scheduler_thread.is_alive():
            return False
        thread = threading.Thread(target=_scheduler_loop, name="dm-scheduler", daemon=True)
        thread.start()
        _scheduler_thread = thread
        return True


# ----------------------------------------------------------------------------
# AI chat
# ----------------------------------------------------------------------------

def _catalog_for_prompt(
    workspace_id: str,
    question: str,
    context: Optional[Dict[str, Any]] = None,
    allowed_workspaces: Optional[set] = None,
) -> str:
    catalog = catalog_for_chat(workspace_id, allowed_workspaces)
    q = (question or "").lower()
    focus_db = str((context or {}).get("db_id") or "").strip()
    focus_schema = str((context or {}).get("schema") or "").strip()
    focus_table = str((context or {}).get("table") or "").strip()
    lines: List[str] = []
    total_tables = 0
    for entry in catalog:
        table_names = [t["name"] for s in entry.get("schemas", []) for t in s.get("tables", [])]
        total_tables += len(table_names)
        header = (
            f"DB {entry['id']} | {entry['name']} | engine={entry['engine']} | "
            f"writable={entry['writable']} | status={entry['status']}"
        )
        if entry.get("detail"):
            header += f" | detail={entry['detail']}"
        if entry.get("error"):
            header += f" | error={entry['error']}"
        lines.append(header)
        if entry.get("engine") == "s3" and entry.get("status") == "live":
            lines.append(
                "  S3 is an object store: query with read_parquet('s3://bucket/key') or "
                "read_csv('s3://bucket/key', header=true); never treat keys as SQL tables."
            )
        for schema in entry.get("schemas", []):
            names = [t["name"] for t in schema.get("tables", [])]
            if not names:
                continue
            # Workspace DBs always get full column detail. Other DBs get detail for
            # tables named in the question or explicitly selected in the UI, otherwise
            # the table list only.
            db_matches = not focus_db or entry["id"] == focus_db
            schema_name = str(schema.get("schema") or schema.get("name") or "")
            schema_matches = not focus_schema or schema_name.lower() == focus_schema.lower()
            detailed = (
                entry["kind"] == "workspace"
                or any(n.lower() in q for n in names)
                or bool(
                    focus_table
                    and db_matches
                    and schema_matches
                    and any(n.lower() == focus_table.lower() for n in names)
                )
            )
            if detailed:
                for name in names[:120]:
                    try:
                        details = get_table_details(entry["id"], schema.get("schema", schema["name"]), name, catalog)
                        cols = ", ".join(
                            f"{c['name']} {c['data_type']}" + (" PK" if c.get("is_pk") else "")
                            for c in details.get("columns", [])
                        )
                        line = f"  {schema['name']}.{name}({cols})"
                        keys = details.get("foreign_keys") or []
                        refs = [
                            f"{fk.get('from')}->{fk.get('table')}.{fk.get('to')}"
                            for fk in keys
                            if isinstance(fk, dict) and fk.get("from") and fk.get("table")
                        ]
                        if refs:
                            line += " FK[" + ", ".join(refs) + "]"
                        if details.get("row_count") is not None:
                            line += f" rows={details['row_count']}"
                        lines.append(line)
                    except Exception:
                        lines.append(f"  {schema['name']}.{name}")
            else:
                # Listing every table of every database produces a prompt large
                # enough to trip provider token-per-minute limits. Keep full names
                # only for databases the user named; summarize the rest.
                db_mentioned = (
                    entry["id"].lower() in q
                    or str(entry.get("name", "")).lower() in q
                )
                if db_mentioned:
                    suffix = f" … {len(names) - 60} more" if len(names) > 60 else ""
                    lines.append(f"  {schema['name']}: " + ", ".join(names[:60]) + suffix)
                else:
                    examples = ", ".join(names[:6])
                    line = f"  {schema['name']}: {len(names)} table(s)"
                    if examples:
                        line += f" — e.g. {examples}"
                    lines.append(line)
        if sum(len(x) for x in lines) > MAX_CONTEXT_CHARS:
            lines.append("  …catalog truncated…")
            break
    text = "\n".join(lines)
    if len(text) > MAX_CONTEXT_CHARS:
        text = text[:MAX_CONTEXT_CHARS] + "\n…catalog truncated…"
    focus_line = ""
    if focus_table:
        focus_line = (
            f"SELECTED_CONTEXT: db={focus_db or 'active workspace'} schema={focus_schema or 'main'} "
            f"table={focus_table}. When the user says \"this table\", \"it\" or omits the table name, "
            "use this table and its real columns from the catalog.\n"
        )
    return focus_line + f"TOTAL_TABLES={total_tables}\n" + text


def _system_prompt(workspace: Dict[str, Any], focus: Optional[Dict[str, Any]] = None) -> str:
    focus_note = ""
    if focus and focus.get("table"):
        focus_note = (
            f"FOCUS: the user has {focus.get('schema') or 'main'}.{focus['table']} selected in the UI "
            f"(db={focus.get('db_id') or 'active workspace'}). Follow-up questions such as \"this table\", "
            "\"its columns\" or \"insert a row\" refer to this table. Never swap in a different table "
            "unless the user names one.\n"
        )
    return (
        "You are NanoPro Data Copilot, a senior data engineer + data analyst + DBA embedded in a chat-first database studio. "
        "The user talks in plain language (English or Marathi/Hindi mixed) and NEVER writes SQL — you do everything for them. "
        "The catalog below was introspected live from the real servers: it is the single source of truth. "
        "Never invent a database, schema, table, column, key or row.\n"
        "RULES:\n"
        "1) Reply with STRICT JSON only: {\"reply\": string, \"sql\": string|null, \"target\": string, \"action\": string|null, "
        "\"name\": string|null, \"steps\": [string]|null, \"frequency\": string|null, \"at_time\": string|null, "
        "\"weekday\": number|null, \"day_of_month\": number|null, \"cron\": string|null, \"run_now\": boolean|null}.\n"
        "2) `reply` is the human answer, max 120 words, in the user's language. State exactly what you did.\n"
        "3) `sql` is ONE statement, no markdown, written in the target database's own dialect.\n"
        "4) `target` must be a DB id from the catalog, or \"workspace\" for the active workspace.\n"
        "5) You must handle, end to end and without the user writing SQL: database/workspace and schema creation; "
        "table, view and index creation; adding columns, renaming columns/tables and changing datatypes; "
        "fetching top records with LIMIT/FETCH FIRST; joins validated against the PK/FK relationships shown in the catalog; "
        "data append and ingestion (INSERT, CREATE TABLE ... AS SELECT, INSERT INTO ... SELECT); "
        "task scheduling (daily, weekly, monthly, quarterly, once, adhoc, cron, SOD/BOD/EOD batch windows); "
        "metadata introspection (columns, types, keys, row counts); and automated ETL/ELT pipelines.\n"
        "6) Writes (CREATE TABLE/VIEW/INDEX, INSERT, UPDATE, DELETE, DROP TABLE/VIEW/INDEX, MERGE) are allowed only on the "
        "workspace and the Snowflake connection. Every other live database is read-only.\n"
        "7) Inside a workspace you may use DELETE only with a WHERE clause, and DROP only as DROP TABLE / VIEW / INDEX when "
        "the user explicitly asks. Never use TRUNCATE, ATTACH, DETACH, GRANT or REVOKE. ALTER TABLE is allowed only for "
        "ADD COLUMN, RENAME COLUMN, RENAME TO and datatype changes.\n"
        "8) To schedule work return action=\"create_schedule\" with `name`, `frequency` (once|daily|weekly|monthly|quarterly|adhoc|cron), "
        "`at_time` as HH:MM UTC, optional `weekday` (0=Monday), `day_of_month`, `cron`, `target`, and either `sql` or `steps`. "
        "For multi-step ETL use action=\"create_pipeline\" with 2-20 `steps` that run in order. "
        "SOD/BOD/EOD mean daily at 07:00 / 00:15 / 22:00 UTC unless the user gives a time.\n"
        "9) To run an existing schedule now return action=\"run_schedule\" with its `name`. Do not put its SQL in `sql`.\n"
        "10) A workspace is a real SQLite database with schema `main` plus attached schemas. "
        "If the user asks for a NEW database/workspace return action=\"create_workspace\" with a short `name` and sql=null. "
        "If they ask for a new schema return action=\"create_schema\" with `name`.\n"
        "11) Dialects: Snowflake uses fully qualified DB.SCHEMA.TABLE; PostgreSQL, DuckDB and SQLite use quoted identifiers and LIMIT; "
        "Oracle uses unquoted uppercase names and FETCH FIRST n ROWS ONLY; BigQuery uses `project.dataset.table` with backticks and LIMIT; "
        "AWS S3 is queried through DuckDB read_parquet()/read_csv() over s3:// paths; MySQL uses backticks and LIMIT.\n"
        "12) If a database status is not \"live\", do not query it. Tell the user it is unreachable and quote the real error from the catalog.\n"
        "13) To send an extract to the user return action=\"deliver_report\" with `table` or a read-only `sql`, `format` "
        "(csv|xlsx|pipe|tab), `limit` (default 100), `channels` (email, telegram, whatsapp), optional `recipient`, `phone` "
        "and `subject`. The platform saves the file on SFTP and returns the real path; quote that path in `reply`.\n"
        "14) The platform executes your `sql` immediately and appends the real row count. Never say you cannot run SQL, "
        "never tell the user to run it themselves, and never call the active workspace read-only. With target=\"workspace\" "
        "your statement runs on the active writable workspace; describe the outcome in `reply`.\n"
        + DELIVERY_CONTRACT
        + focus_note
        + f"Active workspace: {workspace['id']} — {workspace['name']}.\n"
    )


def _split_sql_statements(text: str) -> List[str]:
    statements: List[str] = []
    buf: List[str] = []
    quote = ""
    i = 0
    while i < len(text):
        char = text[i]
        if quote:
            buf.append(char)
            if char == quote:
                if i + 1 < len(text) and text[i + 1] == quote:
                    buf.append(text[i + 1])
                    i += 1
                else:
                    quote = ""
        elif char in ("'", '"', "`"):
            quote = char
            buf.append(char)
        elif char == ";":
            statement = "".join(buf).strip()
            if statement:
                statements.append(statement)
            buf = []
        else:
            buf.append(char)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)
    return statements or [text.strip()]


def _json_string_field(raw: str, field: str) -> str:
    match = re.search(r'"' + re.escape(field) + r'"\s*:\s*"((?:\\.|[^"\\])*)"', raw, re.DOTALL)
    if not match:
        return ""
    try:
        return json.loads('"' + match.group(1) + '"')
    except Exception:
        return match.group(1)


def _parse_json_reply(text: str) -> Dict[str, Any]:
    raw = (text or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        try:
            data = json.loads(raw[start : end + 1])
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    if raw.startswith("{"):
        for suffix in ('"}', '"}}', '}', '"]}'):
            try:
                data = json.loads(raw.rstrip() + suffix)
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
        salvaged = {
            "reply": _json_string_field(raw, "reply"),
            "sql": _json_string_field(raw, "sql"),
            "target": _json_string_field(raw, "target"),
            "action": _json_string_field(raw, "action"),
            "name": _json_string_field(raw, "name"),
            "frequency": _json_string_field(raw, "frequency"),
            "at_time": _json_string_field(raw, "at_time"),
        }
        if salvaged["reply"] or salvaged["sql"]:
            return salvaged
    sql_match = re.search(r"```sql\s*(.*?)```", text or "", re.IGNORECASE | re.DOTALL)
    return {
        "reply": (text or "").strip()[:1200],
        "sql": sql_match.group(1).strip() if sql_match else None,
    }


def _looks_like_sql(message: str) -> bool:
    text = (message or "").strip()
    if re.match(r"^\s*(select|with|pragma|explain)\b", text, re.IGNORECASE):
        return bool(re.search(r"\b(from|where|limit|join|select)\b", text, re.IGNORECASE)) or text.endswith(";")
    return bool(
        re.match(
            r"^\s*("
            r"create\s+(?:or\s+replace\s+)?(?:temp(?:orary)?\s+)?(?:table|view|index)\s+(?:if\s+not\s+exists\s+)?[`\"\[]?\w|"
            r"insert\s+into\s+[`\"\[]?\w|"
            r"update\s+[`\"\[]?\w+\s+set\b|"
            r"delete\s+from\s+[`\"\[]?\w+|"
            r"drop\s+(?:table|view|index)\s+(?:if\s+exists\s+)?[`\"\[]?\w+|"
            r"alter\s+table\s+[`\"\[]?\w|"
            r"truncate\s+table\s+[`\"\[]?\w"
            r")",
            text,
            re.IGNORECASE,
        )
    )


def _extract_direct_sql(message: str) -> str:
    """Returns the SQL body when the user pastes or asks to run a statement."""
    text = (message or "").strip()
    marker = re.search(
        r"\b(?:run|execute)\s+(?:this\s+|the\s+|following\s+)?sql\s*(?:exactly|now|here)?\s*[:\-]?\s*(.+)$",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if marker:
        body = marker.group(1).strip()
        return body if _looks_like_sql(body) else ""
    return text if _looks_like_sql(text) else ""


def _fallback_answer(
    workspace_id: str,
    message: str,
    allowed_workspaces: Optional[set] = None,
) -> Dict[str, Any]:
    catalog = catalog_for_chat(workspace_id, allowed_workspaces)
    db_total = len(catalog)
    lower = (message or "").lower()
    table_total = sum(1 for e in catalog for s in e.get("schemas", []) for _ in s.get("tables", []))

    # Exact table lookup for column questions.
    for entry in catalog:
        for schema in entry.get("schemas", []):
            for t in schema.get("tables", []):
                name = t["name"]
                if name.lower() in lower:
                    try:
                        details = get_table_details(entry["id"], schema.get("schema", schema["name"]), name, catalog)
                        cols = ", ".join(f"{c['name']} ({c['data_type']})" for c in details.get("columns", []))
                        return {
                            "reply": f"{name} is in {entry['name']} · {schema['name']}. Columns: {cols}. Rows: {details.get('row_count')}. Ask me to query it or build a report.",
                            "sql": None,
                        }
                    except Exception:
                        pass

    if "table" in lower or "list" in lower:
        ws = get_workspace(workspace_id) or {}
        ws_tables = [t["name"] for s in ws.get("schemas", []) for t in s.get("tables", [])]
        return {
            "reply": f"NanoPro currently exposes {db_total} databases with about {table_total} tables. Your workspace has {len(ws_tables)} table(s): {', '.join(ws_tables) or 'none yet'}. The AI provider is temporarily busy, so I can only answer catalog questions right now — please retry in a moment for full natural-language SQL.",
            "sql": None,
        }
    return {
        "reply": "The AI provider is temporarily unavailable, so I cannot generate SQL for that request right now. I can still show the live catalog, table columns and workspace history. Ask 'list tables' or name a table to see its columns, and retry your request in a moment.",
        "sql": None,
    }


_IDENT_TOKEN = r"[A-Za-z_][\w$]*(?:\.[A-Za-z_][\w$]*){0,2}"


def _find_named_table(catalog: List[Dict[str, Any]], identifier: str):
    parts = [_strip_ident(part) for part in re.split(r"\.", (identifier or "").strip())]
    if not parts or not parts[-1]:
        return None
    table_name = parts[-1].lower()
    schema_name = parts[-2].lower() if len(parts) >= 2 else ""
    for entry in catalog:
        for schema in entry.get("schemas", []):
            schema_label = str(schema.get("schema") or schema.get("name") or "").lower()
            if schema_name and schema_label != schema_name and str(schema.get("name", "")).lower() != schema_name:
                continue
            for table in schema.get("tables", []):
                if str(table.get("name", "")).lower() == table_name:
                    return entry, schema, table
    return None


def _fast_query_source(entry: Dict[str, Any], schema: Dict[str, Any], table: Dict[str, Any]) -> Optional[str]:
    if entry.get("kind") not in ("workspace", "sqlite", "duckdb"):
        return None
    schema_name = schema.get("schema") or schema.get("name") or "main"
    return f"{_quote(schema_name)}.{_quote(table['name'])}"


def detect_chat_intent(message: str) -> str:
    """
    Dynamically classify user prompt to route to specialized AI models:
    - 'coding': Python, scripts, pandas, algorithms, code interpreter (Codestral, Qwen Coder)
    - 'research': Explanations, architectural comparisons, data science theory, deep reasoning (Cohere, GPT-OSS 120B, Gemini)
    - 'dialogue': Marathi/Hindi conversational dialogue, greetings, general chat, assistance (Groq GPT-OSS 120B, Cohere, Gemini)
    - 'data_analyst': SQL, queries, schemas, ETL, joins, aggregations (Codestral, Qwen, DeepSeek)
    """
    msg = (message or "").strip().lower()

    # Structured SQL wins over greetings: data values such as "hello" inside an
    # INSERT must not route the request to the dialogue model.
    if re.search(
        r"\b(create\s+(?:or\s+replace\s+)?(?:an?\s+|the\s+)?(?:table|view|index)\b|"
        r"insert\s+(?:into\s+|rows?\s+into\s+)?[`\"\[]?(?:\w|\()|"
        r"update\s+\w+\s+set\b|delete\s+from\b|alter\s+table\b|"
        r"drop\s+(?:table|view|index)\b|truncate\s+table\b|"
        r"select\b[^;\n]{0,300}\bfrom\b)",
        msg,
        re.IGNORECASE,
    ):
        return "data_analyst"

    # 1. Coding / Python / Scripting / Code Interpreter (Top priority if asking for code)
    code_patterns = [
        r"\b(python|py|pandas|dataframe|df|numpy|matplotlib|seaborn|scikit|sklearn|pytorch|tensorflow|torch|keras)\b",
        r"\b(def\s+|class\s+|import\s+|lambda|pip\s+install|function|script|code|algorithm|regex|unit\s*test)\b",
        r"\b(json\.loads|requests\.get|asyncio|fastapi|flask|pydantic|pytest|decorator|syntax)\b",
        r"\b(plot|histogram|scatter|heatmap|chart\s+script|generate\s+code)\b",
    ]
    if any(re.search(pat, msg, re.IGNORECASE) for pat in code_patterns):
        return "coding"

    # 2. Research / Conceptual Explanations / Architectural Comparisons / Deep Dives
    research_patterns = [
        r"\b(explain|why|difference\s+between|compare|comparison|architecture|tradeoff|pros\s+and\s+cons)\b",
        r"\b(how\s+does|what\s+is\s+the\s+best|deep\s+dive|analysis|methodology|theoretical|concept|paradigm)\b",
        r"\b(machine\s+learning|data\s+science|clustering|regression|classification|neural\s+network|deep\s+learning)\b",
        r"\b(star\s+schema|snowflake\s+schema|fact\s+table|dimension\s+table|olap|oltp|normalization)\b",
    ]
    if any(re.search(pat, msg, re.IGNORECASE) for pat in research_patterns):
        return "research"

    # 3. Dialogue / Conversational / Greetings / Marathi / Hindi
    dialogue_patterns = [
        r"\b(hi|hello|hey|namaskar|namaste|kasa|kay|kaise|kya|shubh|pranam)\b",
        r"\b(thanks|thank\s+you|dhanyawad|shukriya|great|awesome|cool|bye|goodbye)\b",
        r"\b(who\s+are\s+you|what\s+can\s+you\s+do|madat|help\s+me|kon\s+ahes|bol|sanga|koni)\b",
        r"[\u0900-\u097F]",  # Devanagari script (Marathi / Hindi)
    ]
    if any(re.search(pat, msg, re.IGNORECASE) for pat in dialogue_patterns):
        return "dialogue"

    # 4. SQL / Database / ETL / Modeling (Core Data Analyst)
    sql_patterns = [
        r"\b(select|insert|update|delete|create\s+table|alter\s+table|drop\s+table|truncate)\b",
        r"\b(join|inner\s+join|left\s+join|outer\s+join|group\s+by|order\s+by|having|window\s+function|partition\s+by)\b",
        r"\b(sql|query|queries|database|databases|table|tables|schema|schemas|column|columns|primary\s+key|foreign\s+key)\b",
        r"\b(snowflake|duckdb|sqlite|bigquery|postgres|postgresql|mysql|mssql|warehouse|lakehouse|etl|elt|dbt)\b",
        r"\b(count|sum|avg|min|max|distinct|where|limit|offset|view|views|index|indexes|rows?|records?)\b",
    ]
    if any(re.search(pat, msg, re.IGNORECASE) for pat in sql_patterns):
        return "data_analyst"

    # Default to data_analyst for studio context
    return "data_analyst"


def _active_workspace_table(
    workspace_id: str,
    focus: Optional[Dict[str, str]],
    catalog: List[Dict[str, Any]],
):
    """Resolves "this table" from the selected table context, or the workspace's
    only table when the question clearly refers to a single dataset."""
    if focus and focus.get("table"):
        want_db = focus.get("db_id") or ("workspace:" + workspace_id)
        for entry in catalog:
            if entry.get("id") != want_db:
                continue
            for schema in entry.get("schemas", []):
                schema_label = str(schema.get("schema") or schema.get("name") or "").lower()
                want_schema = str(focus.get("schema") or "").lower()
                if want_schema and schema_label != want_schema:
                    continue
                for table in schema.get("tables", []):
                    if str(table.get("name", "")).lower() == str(focus["table"]).lower():
                        return entry, schema, table
    entry = next((item for item in catalog if item.get("id") == "workspace:" + workspace_id), None)
    if not entry:
        return None
    found = [
        (entry, schema, table)
        for schema in entry.get("schemas", [])
        for table in schema.get("tables", [])
    ]
    return found[0] if len(found) == 1 else None


def _fast_intent(
    workspace_id: str,
    message: str,
    allowed_workspaces: Optional[set] = None,
    focus: Optional[Dict[str, str]] = None,
) -> Optional[Dict[str, Any]]:
    """Deterministic intent parser. Answers the most common questions with zero
    model latency while the LLM stays available for everything else."""
    text = (message or "").strip()
    if not text or len(text) > 200:
        return None
    low = re.sub(r"[^a-z\u0900-\u097F ]", "", text.lower()).strip()
    if low in {"hi", "hii", "hello", "hey", "yo", "namaste", "namaskar", "hola", "good morning", "good evening"}:
        return {
            "reply": "Namaskar! Mi NanoPro Data Copilot. Konti table, join, report, upload kinva schedule pahije? Udaharan: "
                     "\"sales_orders madhe top 5 rows dakhav\" kinva \"roj 7 vajta pipeline set kar\".",
            "sql": None,
            "target": "workspace",
            "action": None,
            "fast": True,
        }
    if low in {"help", "what can you do", "kay karu shakto", "kay karta", "kay karu shaktos", "options"}:
        return {
            "reply": "Mi SQL na lihita sagl karto: database/schema/table create, columns add-rename-type change, "
                     "top records, joins, CSV/Excel upload, data append, ETL pipelines ani daily/monthly/quarterly/cron schedules. "
                     "Fakt tumhi marathi, hindi kinva english madhe sanga.",
            "sql": None,
            "target": "workspace",
            "action": None,
            "fast": True,
        }
    catalog = catalog_for_chat(workspace_id, allowed_workspaces)

    if re.fullmatch(
        r"(?:please\s+)?(?:list|show|display|what\s+are)\s+(?:me\s+)?(?:all\s+)?(?:databases?|dbs?|data\s+sources)\s*[?.!]?",
        text,
        re.IGNORECASE,
    ):
        live = [entry for entry in catalog if entry.get("status") == "live"]
        parts = []
        for entry in live:
            tables = sum(len(schema.get("tables", [])) for schema in entry.get("schemas", []))
            parts.append(f"{entry['name']} ({entry['engine']}, {tables} tables)")
        unavailable = [f"{entry['name']} ({entry['status']})" for entry in catalog if entry.get("status") != "live"]
        reply = f"{len(live)} live database(s): " + ("; ".join(parts) if parts else "none")
        if unavailable:
            reply += f". Not available: {', '.join(unavailable)}"
        return {"reply": reply, "sql": None, "target": "workspace", "action": None, "fast": True}

    if re.fullmatch(
        r"(?:please\s+)?(?:list|show|display)\s+(?:me\s+)?(?:all\s+)?(?:the\s+)?tables\s*[?.!]?",
        text,
        re.IGNORECASE,
    ):
        workspace = get_workspace(workspace_id) or {}
        groups = []
        for schema in workspace.get("schemas", []):
            names = [table["name"] for table in schema.get("tables", [])]
            if names:
                groups.append(f"{schema['name']}: " + ", ".join(names))
        total = sum(len(schema.get("tables", [])) for schema in workspace.get("schemas", []))
        reply = f"This workspace has {total} table(s)" + (": " + "; ".join(groups) if groups else ".")
        return {"reply": reply, "sql": None, "target": "workspace", "action": None, "fast": True}

    columns_match = re.fullmatch(
        r"(?:show|list|display|what\s+are)\s+(?:me\s+)?(?:the\s+)?columns\s+(?:of|in|for)\s+(" + _IDENT_TOKEN + r")\s*[?.!]?",
        text,
        re.IGNORECASE,
    )
    if columns_match:
        found = _find_named_table(catalog, columns_match.group(1))
        if found:
            entry, schema, table = found
            try:
                details = get_table_details(
                    entry["id"], schema.get("schema") or schema.get("name") or "main", table["name"], catalog
                )
                cols = ", ".join(
                    f"{c['name']} {c['data_type']}" + (" PK" if c.get("is_pk") else "")
                    for c in details.get("columns", [])
                )
                reply = f"{table['name']}: {cols}."
                if details.get("row_count") is not None:
                    reply += f" Rows: {details['row_count']}."
                return {"reply": reply, "sql": None, "target": entry["id"], "action": None, "fast": True}
            except Exception:
                return None

    top_match = re.fullmatch(
        r"(?:please\s+)?(?:show|get|display|fetch|give|bring)\s+(?:me\s+)?(?:the\s+)?"
        r"(top|first|last)\s*(\d{1,4})?\s*(?:rows?|records?)?\s*"
        r"(?:from|of|in)\s*(this\s+table|the\s+table|" + _IDENT_TOKEN + r")"
        r"(?:\s+(?:ordered|order|sorted)\s+by\s+([A-Za-z_][\w$]*)\s*(asc|desc)?)?\s*[?.!]?",
        text,
        re.IGNORECASE,
    )
    if top_match:
        count = max(1, min(int(top_match.group(2) or 5), 100))
        table_token = (top_match.group(3) or "").strip()
        order_column = (top_match.group(4) or "").strip()
        direction = (top_match.group(5) or "").strip().upper()
        if not direction:
            direction = "ASC" if top_match.group(1).lower() == "first" else "DESC"
        if table_token.lower() in ("this table", "the table"):
            found = _active_workspace_table(workspace_id, focus, catalog)
        else:
            found = _find_named_table(catalog, table_token)
        if found:
            entry, schema, table = found
            source = _fast_query_source(entry, schema, table)
            if source:
                order_sql = ""
                if order_column:
                    schema_name = schema.get("schema") or schema.get("name") or "main"
                    try:
                        details = get_table_details(entry["id"], schema_name, table["name"], catalog)
                    except Exception:
                        details = {}
                    known = {str(column.get("name") or "").lower() for column in details.get("columns", [])}
                    if order_column.lower() not in known:
                        return None
                    order_sql = f" ORDER BY {_quote(order_column)} {direction}"
                origin = "your workspace" if entry.get("kind") == "workspace" else entry["name"]
                reply = f"Here are the {'top' if direction == 'DESC' else 'first'} {count} row(s) of {table['name']} in {origin}"
                if order_column:
                    reply += f", ordered by {order_column} ({'ascending' if direction == 'ASC' else 'descending'})"
                return {
                    "reply": reply + ".",
                    "sql": f"SELECT * FROM {source}{order_sql} LIMIT {count}",
                    "target": entry["id"],
                    "action": None,
                    "fast": True,
                }

    count_match = re.fullmatch(
        r"(?:how\s+many|count|kiti)\s+(?:of\s+)?(?:rows?|records?)\s+(?:are\s+)?(?:in|of|from|inside)?\s*(" + _IDENT_TOKEN + r")\s*[?.!]?",
        text,
        re.IGNORECASE,
    ) or re.fullmatch(
        r"(" + _IDENT_TOKEN + r")\s+(?:madhe|me)\s+(?:kiti|how\s+many)\s+(?:rows?|records?)\s*[?.!]?",
        text,
        re.IGNORECASE,
    )
    if count_match:
        found = _find_named_table(catalog, count_match.group(1))
        if found:
            entry, schema, table = found
            source = _fast_query_source(entry, schema, table)
            if source:
                return {
                    "reply": f"Counting rows in {table['name']} from {entry['name']}.",
                    "sql": f"SELECT COUNT(*) AS total_rows FROM {source}",
                    "target": entry["id"],
                    "action": None,
                    "fast": True,
                }
    return None


# Parsed AI replies are cached so a repeated question never pays model latency twice.
_AI_REPLY_CACHE: Dict[str, Dict[str, Any]] = {}
_AI_REPLY_LOCK = threading.Lock()
_AI_REPLY_TTL = 300.0
_AI_REPLY_MAX = 96


def _reply_cache_key(
    workspace_id: str,
    message: str,
    focus: Optional[Dict[str, Any]] = None,
) -> str:
    key = workspace_id + "|" + re.sub(r"\s+", " ", (message or "").strip().lower())
    if focus and focus.get("table"):
        key += "|" + ".".join(
            str(focus.get(part) or "") for part in ("db_id", "schema", "table")
        ).lower()
    return key


def _reply_cache_get(key: str) -> Optional[Dict[str, Any]]:
    with _AI_REPLY_LOCK:
        item = _AI_REPLY_CACHE.get(key)
        if not item:
            return None
        if time.time() - item["at"] > _AI_REPLY_TTL:
            _AI_REPLY_CACHE.pop(key, None)
            return None
        return dict(item["value"])


def _reply_cache_put(key: str, value: Dict[str, Any]) -> None:
    if value.get("action"):
        return
    if re.match(r"^\s*(insert|update|delete|drop|alter|create|truncate|merge)\b", str(value.get("sql") or ""), re.IGNORECASE):
        return
    with _AI_REPLY_LOCK:
        if len(_AI_REPLY_CACHE) >= _AI_REPLY_MAX:
            oldest = min(_AI_REPLY_CACHE, key=lambda k: _AI_REPLY_CACHE[k]["at"])
            _AI_REPLY_CACHE.pop(oldest, None)
        _AI_REPLY_CACHE[key] = {"at": time.time(), "value": dict(value)}


def _delivery_intent(workspace_id: str, message: str) -> Dict[str, Any]:
    text = message or ""
    low = text.lower()
    if not re.search(r"\b(mail|email|whatsapp|telegram|sftp)\b", low):
        return {}
    if not re.search(r"\b(top|rows?|data|table|file|report|attachment|extract|send|share|path|excel|csv)\b", low):
        return {}
    channels = []
    if re.search(r"\b(mail|email)\b", low):
        channels.append("email")
    if "whatsapp" in low:
        channels.append("whatsapp")
    if "telegram" in low:
        channels.append("telegram")
    if re.search(r"\bexcel\b|\bxlsx\b", low):
        fmt = "xlsx"
    elif re.search(r"\bpipe\b|\bpsv\b", low):
        fmt = "pipe"
    elif re.search(r"\btab\b|\btsv\b", low):
        fmt = "tab"
    elif "csv" in low:
        fmt = "csv"
    else:
        fmt = "xlsx"
    limit = 100
    match = re.search(r"\btop\s+(\d{1,5})\b|\b(\d{1,5})\s+rows?\b", low)
    if match:
        limit = int(match.group(1) or match.group(2))
    table = ""
    schema = "main"
    table_map = _workspace_table_map(workspace_id)
    for name in sorted(table_map, key=len, reverse=True):
        if re.search(r"\b" + re.escape(name) + r"\b", low):
            schema, table = table_map[name]
            break
    if not table:
        candidate = _table_name_from_text(text).lower()
        if candidate in table_map:
            schema, table = table_map[candidate]
    if not table:
        return {}
    phone = ""
    phone_match = re.search(r"(?<![\w.])(\+?\d[\d\s-]{8,16}\d)(?![\w.])", text)
    if phone_match:
        digits = re.sub(r"\D", "", phone_match.group(1))
        if 10 <= len(digits) <= 15:
            phone = ("+" if phone_match.group(1).strip().startswith("+") else "") + digits
    recipient = ""
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    if email_match:
        recipient = email_match.group(0)
    return {
        "table": table,
        "schema": schema,
        "fmt": fmt,
        "limit": limit,
        "channels": channels or ["email", "telegram", "whatsapp"],
        "phone": phone,
        "recipient": recipient,
    }


_SCALAR_NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?")
_ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def _single_value_result(result: Dict[str, Any]) -> Optional[Tuple[str, Any]]:
    """Return (alias, value) when the query resolves to one cell, else None."""
    columns = result.get("columns") or []
    rows = result.get("rows") or []
    if len(columns) != 1 or len(rows) != 1 or not isinstance(rows[0], dict):
        return None
    alias = str(columns[0])
    value = rows[0].get(alias)
    if value is None or isinstance(value, bool):
        return None
    return alias, value


def _format_scalar(value: Any) -> str:
    if isinstance(value, float):
        rounded = round(value, 2)
        if abs(value - rounded) < 1e-6:
            value = rounded
        if float(value).is_integer():
            return f"{int(value):,}"
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def _reply_mentions_value(reply: str, value: Any) -> bool:
    """True when the model's prose already states the executed result value."""
    text = reply or ""
    if isinstance(value, (int, float)):
        target = float(value)
        for raw in _SCALAR_NUMBER.findall(_ISO_DATE.sub(" ", text)):
            try:
                candidate = float(raw.replace(",", ""))
            except ValueError:
                continue
            if abs(candidate - target) <= max(0.005, abs(target) * 1e-9):
                return True
        return False
    needle = str(value).strip().lower()
    return bool(needle) and needle in text.lower()


_AML_TOPIC = re.compile(r"\baml\b|anti[- ]?money", re.IGNORECASE)
_AML_STATUS = re.compile(r"\bstatus\b|\bprogress\b|\bresult\b|\bcompleted\b", re.IGNORECASE)
_AML_ACTION = re.compile(r"\b(run|load|start|ingest|execute|reload|refresh|kara|karo|kra)\b", re.IGNORECASE)
# Instructions such as "do not execute anything yet" are negated: the action word
# must not be read as a command to start a pipeline run.
_AML_NEGATED_CLAUSE = re.compile(
    r"\b(?:do not|don't|dont|does not|doesn't|never|without|avoid|not to|no need to|not yet|not|"
    r"nako|nakos|nahi)\b",
    re.IGNORECASE,
)
_AML_CLAUSE_SPLIT = re.compile(r"(?<=[.!?;,\n])\s*|\s+[—–-]\s+")


def _aml_unnegated_text(text: str) -> str:
    """Drops clauses that forbid an action, so negated verbs never trigger a run."""
    clauses = [c for c in _AML_CLAUSE_SPLIT.split(text or "") if c]
    return " ".join(c for c in clauses if not _AML_NEGATED_CLAUSE.search(c))


def _detect_aml_action(message: str) -> Optional[str]:
    text = message or ""
    if not _AML_TOPIC.search(text):
        return None
    low = _aml_unnegated_text(text).lower()
    if re.search(r"\bincremental\b|\bappend\b|\bincrement\b", low):
        return "incremental"
    if re.search(r"\bfull\b|\breload\b|\bfresh\b|\binitial\b|\bfirst\b", low) and _AML_ACTION.search(low):
        return "full"
    if _AML_STATUS.search(low) and not re.search(r"\b(run|load|start)\b", low):
        return "status"
    if re.search(r"\breport\b", low) and re.search(r"\b(pathava|pathva|send|email|mail)\b", low):
        return "status"
    if _AML_ACTION.search(low):
        return "full"
    return None


def _aml_chat_reply(workspace_id: str, message: str, user: str, action: str,
                    started_at: float, is_first: bool) -> Dict[str, Any]:
    from app.core import aml_lakehouse_pipeline as aml

    run: Dict[str, Any] = {}
    if action == "status":
        run = aml.last_run() or {}
        if not run:
            reply = (
                "No AML pipeline run found yet.\n\n"
                "Send `run aml full load` to create the Snowflake L0/L1/L2 layers, land raw "
                "Parquet in AWS S3, build the daily surveillance report and deliver it by email, "
                "WhatsApp and Telegram."
            )
        else:
            reply = aml.summary_lines(run)
            if run.get("status") == "running":
                reply += "\n\nThe run is still in progress. Send `aml status` again in a few seconds."
    else:
        mode = "INCREMENTAL" if action == "incremental" else "FULL"
        run = aml.run_now(mode, user=user, wait_seconds=78.0)
        if run.get("status") == "busy":
            reply = (
                "An AML pipeline run is already in progress"
                + (f" ({run.get('active_run_id')})." if run.get("active_run_id") else ".")
                + " Send `aml status` to see progress."
            )
        elif run.get("status") == "running":
            reply = (
                f"AML {mode.title()} load is still running — the report and delivery steps are "
                f"finishing in the background.\n\n{aml.summary_lines(run)}\n\n"
                "Send `aml status` in a few seconds for the final status."
            )
        else:
            headline = "AML FULL LOAD completed" if mode == "FULL" else "AML INCREMENTAL LOAD completed"
            if run.get("status") != "success":
                headline = f"AML {mode.title()} load failed"
            delivery = run.get("delivery") or {}
            email = delivery.get("email") or {}
            wa = delivery.get("whatsapp") or {}
            tg = delivery.get("telegram") or {}
            report = run.get("report") or {}
            reply = (
                f"{headline}: {run.get('run_id')}\n\n"
                f"{aml.summary_lines(run)}\n\n"
                f"Snowflake: BANK_DB L0_STAGING → L1_HARMONIZED → L2_CURATED\n"
                f"Report: {report.get('report_day')} | email nanoproaistudio@gmail.com "
                f"{'delivered' if email.get('success') else 'not confirmed'} | "
                f"WhatsApp {'delivered' if wa.get('success') else 'not confirmed'} | "
                f"Telegram {'delivered' if tg.get('success') else 'not confirmed'}"
                + (f"\n\nError: {run.get('error')}" if run.get("error") else "")
            )
    meta = {
        "kind": "aml_pipeline",
        "aml_action": action,
        "aml_run_id": run.get("run_id"),
        "aml_status": run.get("status"),
        "aml_mode": run.get("mode"),
    }
    assistant = add_message(workspace_id, "assistant", reply, "", meta, user=user)
    if is_first:
        title = message.replace("\n", " ").strip()
        if len(title) > 48:
            title = title[:48].rstrip() + "…"
        try:
            rename_workspace(workspace_id, title, user=user)
        except Exception:
            pass
    return {
        "status": "success",
        "workspace": get_workspace(workspace_id, user=user),
        "message": assistant,
        "reply": reply,
        "sql": "",
        "target": "",
        "error": run.get("error"),
        "result": None,
        "model": "aml-pipeline",
        "latency_ms": round((time.time() - started_at) * 1000, 1),
        "pipeline": aml.public_run({k: run.get(k) for k in ("run_id", "mode", "status", "counts",
                                                            "s3_objects", "snowflake", "report",
                                                            "delivery", "error")}),
    }


def chat(
    workspace_id: str,
    message: str,
    user: str = "",
    attachments: Optional[List[Dict[str, Any]]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    _ensure_schema()
    workspace = get_workspace(workspace_id)
    if not workspace:
        raise ValueError("Workspace not found.")
    message = (message or "").strip()
    if len(message) > 4000:
        message = message[:4000]

    prepared: List[Tuple[Dict[str, Any], bytes]] = []
    for item in (attachments or [])[:MAX_ATTACHMENTS_PER_MESSAGE]:
        att_id = item.get("attachment_id") if isinstance(item, dict) else str(item or "")
        try:
            prepared.append(load_attachment(workspace_id, att_id))
        except Exception as exc:
            prepared.append(({"attachment_id": att_id, "filename": "attachment", "kind": "file", "error": str(exc)}, b""))
    if not message and not prepared:
        raise ValueError("Message cannot be empty.")

    is_first = not get_messages(workspace_id, limit=1, user=user)
    started_at = time.time()
    if prepared:
        names = ", ".join((info.get("filename") or "attachment") for info, _ in prepared)
        echo = [
            {
                "attachment_id": info.get("attachment_id"),
                "filename": info.get("filename"),
                "kind": info.get("kind"),
                "row_count": info.get("row_count"),
                "columns": info.get("columns") or [],
            }
            for info, _ in prepared
        ]
        add_message(workspace_id, "user", message or f"Attached: {names}", meta={"attachments": echo}, user=user)
        result = _attachment_reply(workspace_id, message, prepared, context, started_at, user=user)
        if is_first:
            title = (message or names).replace("\n", " ").strip()
            if len(title) > 48:
                title = title[:48].rstrip() + "…"
            try:
                rename_workspace(workspace_id, title, user=user)
            except Exception:
                pass
        return result

    add_message(workspace_id, "user", message, user=user)
    aml_action = _detect_aml_action(message)
    if aml_action:
        return _aml_chat_reply(workspace_id, message, user, aml_action, started_at, is_first)
    parsed: Dict[str, Any] = {}
    model_used = "fallback"
    focus: Dict[str, str] = {}
    if isinstance(context, dict):
        focus = {
            "db_id": str(context.get("db_id") or "").strip(),
            "schema": str(context.get("schema") or "").strip(),
            "table": str(context.get("table") or "").strip(),
        }
    allowed_workspaces: Optional[set] = None
    if user:
        try:
            allowed_workspaces = {w["id"] for w in list_workspaces(user=user, light=True)}
            allowed_workspaces.add(workspace_id)
        except Exception:
            allowed_workspaces = None
    task_type = detect_chat_intent(message)
    direct_sql = _extract_direct_sql(message)
    if direct_sql:
        parsed = {"reply": "Running your SQL now.", "sql": direct_sql, "target": "workspace", "action": None}
        model_used = "direct-sql"
    else:
        fast = _fast_intent(workspace_id, message, allowed_workspaces, focus)
        if fast:
            parsed = fast
            model_used = "fast-nlu"
        else:
            cache_key = _reply_cache_key(workspace_id, message, focus)
            cached = _reply_cache_get(cache_key)
            if cached:
                parsed = cached
                model_used = "cached-ai"
            else:
                catalog_text = _catalog_for_prompt(workspace_id, message, focus, allowed_workspaces)
                history_rows = get_messages(workspace_id, limit=12, user=user)[:-1]
                history = "\n".join(f"{m['role']}: {m['content'][:600]}" for m in history_rows)
                prompt = (
                    f"{catalog_text}\n\nCONVERSATION SO FAR:\n{history or '(new conversation)'}\n\n"
                    f"USER: {message}\n\nReturn the JSON object now."
                )
                try:
                    from app.core.model_adapter import model_manager

                    task_type = detect_chat_intent(message)
                    content, model_used, _, _ = model_manager.route_and_execute(
                        prompt,
                        task_type=task_type,
                        schema={"type": "json_object"},
                        system_prompt=_system_prompt(workspace, focus),
                        timeout=45.0,
                        temperature=0.2,
                        max_tokens=3000,
                    )
                    parsed = _parse_json_reply(content)
                    _reply_cache_put(cache_key, parsed)
                except Exception as exc:
                    log_event(f"Data modeling AI unavailable: {exc}", level="WARNING", component="DataModeling")
                    parsed = _fallback_answer(workspace_id, message, allowed_workspaces)
                    model_used = "fallback"

    action = (parsed.get("action") or "").strip().lower()
    sql = parsed.get("sql")
    if isinstance(sql, list):
        sql = " ".join(str(s) for s in sql)
    sql = (sql or "").strip() or None

    # A recurring schedule only makes sense when the user actually asked for
    # one; otherwise the model's "steps" are just the SQL to run now.
    if action in ("create_schedule", "create_pipeline") and not re.search(
        r"\b(schedule[sd]?|recurring|cron|daily|weekly|monthly|hourly|every\s+\w+|"
        r"pipeline|automat(?:e|ion|ically)|at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\b",
        message or "",
        re.IGNORECASE,
    ):
        steps = parsed.get("steps") or []
        salvaged = [str(step).strip() for step in steps if str(step).strip()] if isinstance(steps, list) else []
        if not salvaged and sql:
            salvaged = _split_sql_statements(sql)
        if salvaged:
            sql = ";\n".join(step.rstrip(";") for step in salvaged) + ";"
            parsed["sql"] = sql
        action = ""
        parsed["action"] = ""
    forced_delivery = bool(re.search(r"\b(sftp|attachment)\b", message or "", re.IGNORECASE))
    if not action or forced_delivery:
        intent = _delivery_intent(workspace_id, message)
        if intent:
            action = "deliver_report"
            parsed["table"] = intent["table"]
            parsed["schema"] = intent["schema"]
            parsed["format"] = parsed.get("format") or intent["fmt"]
            parsed["limit"] = intent["limit"]
            parsed["channels"] = parsed.get("channels") or intent["channels"]
            parsed["phone"] = str(parsed.get("phone") or intent.get("phone") or "")
            parsed["recipient"] = str(parsed.get("recipient") or intent.get("recipient") or "")
            parsed["sql"] = None
            sql = None
    target = (parsed.get("target") or "workspace").strip()
    reply = (parsed.get("reply") or "").strip()[:2000] or "Done."

    if target in ("", "active", workspace_id):
        target = "workspace:" + workspace_id
    if not target.startswith(("workspace:", "sqlite:", "duckdb:", "connection:")):
        target = "workspace:" + workspace_id
    if sql and target.startswith("workspace:"):
        snowflake_databases = _snowflake_databases()
        if snowflake_databases:
            pattern = r"\b(" + "|".join(re.escape(name) for name in snowflake_databases) + r")\."
            if re.search(pattern, sql, re.IGNORECASE):
                target = "connection:NANO_PRO_SNOWFLAKE"

    created_workspace = None
    created_schema = None
    created_schedule = None
    schedule_run = None
    delivery_result = None
    schedule_handled = False
    schedule_error = ""
    if action == "create_workspace" and not sql and re.search(r"\b(database|workspace|db)\b", message, re.IGNORECASE):
        created_workspace = create_workspace(parsed.get("name") or message[:40], user, project_id=workspace.get("project_id") or "")
        reply = reply or f"Created workspace {created_workspace['name']} ({created_workspace['id']})."
    elif action == "create_schema" and not sql:
        try:
            created_schema = create_schema(workspace_id, parsed.get("name") or "new_schema")
            reply = reply or f"Created schema {created_schema['schema']} in this workspace."
        except Exception as exc:
            reply = f"Could not create that schema: {exc}"
    elif action == "deliver_report":
        try:
            delivery_result = deliver_report(
                workspace_id,
                table=str(parsed.get("table") or ""),
                sql=str(parsed.get("sql") or ""),
                db_id=target,
                schema=str(parsed.get("schema") or "main"),
                fmt=str(parsed.get("format") or "xlsx"),
                limit=int(parsed.get("limit") or 100),
                channels=parsed.get("channels"),
                recipient=str(parsed.get("recipient") or ""),
                phone=str(parsed.get("phone") or ""),
                subject=str(parsed.get("subject") or ""),
                user=user,
            )
            reply = delivery_result["reply"]
            sql = delivery_result.get("sql")
            parsed["sql"] = sql
        except Exception as exc:
            reply = f"Could not deliver that report: {exc}"
        schedule_handled = True
    elif action in ("create_schedule", "create_pipeline"):
        steps = parsed.get("steps") or ([sql] if sql else [])
        if not parsed.get("steps") and len(steps) == 1 and steps[0]:
            steps = _split_sql_statements(str(steps[0]))
        try:
            created_schedule = create_schedule(
                workspace_id,
                name=parsed.get("name") or parsed.get("schedule_name") or message[:48],
                statements=steps,
                frequency=parsed.get("frequency") or "adhoc",
                at_time=parsed.get("at_time") or parsed.get("time") or "",
                weekday=parsed.get("weekday"),
                day_of_month=parsed.get("day_of_month"),
                cron_expr=parsed.get("cron") or parsed.get("cron_expr") or "",
                target=target,
                user=user,
                kind="pipeline" if action == "create_pipeline" else "sql",
            )
            reply = reply or f"Scheduled '{created_schedule['name']}' — {describe_schedule(created_schedule)}."
            if parsed.get("run_now"):
                schedule_run = run_schedule(created_schedule["schedule_id"])
                reply += f"\n\nFirst run: {schedule_run['status']}, {schedule_run['rows_affected']} row(s)."
                created_schedule = schedule_run["schedule"]
            schedule_handled = True
        except Exception as exc:
            schedule_error = str(exc)[:400]
            reply = f"Could not create that schedule: {schedule_error}"
            schedule_handled = True
    elif action == "run_schedule":
        wanted = str(parsed.get("name") or parsed.get("schedule_name") or "").strip().lower()
        picked = next(
            (
                schedule
                for schedule in list_schedules(workspace_id)
                if schedule["schedule_id"] == wanted or schedule["name"].lower() == wanted
            ),
            None,
        )
        if picked:
            try:
                schedule_run = run_schedule(picked["schedule_id"])
                reply = (
                    f"Ran '{picked['name']}': {schedule_run['status']}, "
                    f"{schedule_run['rows_affected']} row(s)."
                )
                if schedule_run.get("message"):
                    reply += f"\nError: {schedule_run['message']}"
            except Exception as exc:
                reply = f"Could not run that schedule: {exc}"
        else:
            reply = "I could not find a schedule with that name in this workspace."
        schedule_handled = True

    result = None
    run_id = None
    error = schedule_error or None
    wants_write = bool(
        re.search(
            r"\b(create\s+(?:or\s+replace\s+)?(?:an?\s+|the\s+)?(?:table|view|index)\b|"
            r"insert\s+(?:into\s+|rows?\s+into\s+)?[`\"\[]?(?:\w|\()|"
            r"update\s+\w+\s+set\b|delete\s+from\b|alter\s+table\b|"
            r"drop\s+(?:table|view|index)\b|truncate\s+table\b)",
            message or "",
            re.IGNORECASE,
        )
    )
    if (
        wants_write
        and model_used != "direct-sql"
        and not sql
        and not error
        and not schedule_handled
        and not created_schema
        and not created_workspace
    ):
        reply = (
            "I could not turn that request into executable SQL, so nothing was "
            "changed in your workspace. Please retry, or send the statement "
            "directly, e.g. CREATE TABLE ...; INSERT INTO ...;"
        )
    if sql and not created_schema and not schedule_handled:
        statements = _split_sql_statements(sql) if target.startswith("workspace:") else [sql]
        executed = 0
        try:
            for statement in statements:
                result = execute_sql(target, statement, workspace_id=workspace_id)
                executed += 1
            run_id = save_run(workspace_id, sql, result or {})
        except Exception as exc:
            error = str(exc)[:400]
            if executed:
                error = f"Statement {executed + 1} of {len(statements)} failed: {error}"

    latency_ms = round((time.time() - started_at) * 1000, 1)
    meta = {
        "sql": sql,
        "target": target,
        "run_id": run_id,
        "row_count": result.get("row_count") if result else 0,
        "rows_affected": result.get("rows_affected") if result else 0,
        "error": error,
        "model": model_used,
        "latency_ms": latency_ms,
        "task_type": task_type,
        "fast_path": bool(parsed.get("fast")),
        "workspace_created": created_workspace["id"] if created_workspace else None,
        "schema_created": created_schema["schema"] if created_schema else None,
        "schedule_created": created_schedule["schedule_id"] if created_schedule else None,
        "schedule_run": schedule_run["run_id"] if schedule_run else None,
    }
    if error:
        reply = (reply + f"\n\nSQL error: {error}").strip()
    elif result:
        scalar = _single_value_result(result)
        if scalar and not _reply_mentions_value(reply, scalar[1]):
            alias, value = scalar
            reply = f"{alias.replace('_', ' ').strip()} = {_format_scalar(value)}"
        if result.get("rows_affected") and not result.get("columns"):
            note = f"{result['rows_affected']} row(s) affected"
        else:
            note = f"Returned {result['row_count']} row(s)" + (" (preview truncated)" if result.get("truncated") else "")
        reply = (reply + f"\n\n{note}.").strip()

    if result is not None or created_schema or created_workspace or run_id:
        try:
            with _catalog_lock:
                _catalog_cache["at"] = 0.0
            _refresh_catalog_async()
        except Exception:
            pass

    assistant = add_message(workspace_id, "assistant", reply, sql or "", meta, user=user)
    if is_first:
        title = message.replace("\n", " ").strip()
        if len(title) > 48:
            title = title[:48].rstrip() + "…"
        try:
            rename_workspace(workspace_id, title, user=user)
        except Exception:
            pass

    return {
        "status": "success",
        "workspace": get_workspace(workspace_id, user=user),
        "workspace_created": created_workspace,
        "schema_created": created_schema,
        "message": assistant,
        "reply": reply,
        "sql": sql,
        "target": target,
        "error": error,
        "result": dict(result or {}, run_id=run_id) if result else None,
        "model": model_used,
        "latency_ms": latency_ms,
        "schedule_created": created_schedule,
        "schedule_run": schedule_run,
        "delivery": delivery_result,
    }


# ----------------------------------------------------------------------------
# tabular import / export
# ----------------------------------------------------------------------------

def _decode_rows(filename: str, content: bytes) -> Tuple[List[str], List[List[Any]]]:
    name = (filename or "").lower()
    if name.endswith((".xlsx", ".xlsm")):
        try:
            from openpyxl import load_workbook
        except Exception as exc:
            raise ValueError("Excel import needs openpyxl on the server.") from exc
        wb = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        sheet = wb.active
        rows = [list(r) for r in sheet.iter_rows(values_only=True)]
        wb.close()
    elif name.endswith(".json"):
        try:
            payload = json.loads(content.decode("utf-8-sig"))
        except UnicodeDecodeError:
            payload = json.loads(content.decode("latin-1"))
        if isinstance(payload, dict):
            for key in ("data", "rows", "records", "items", "results"):
                if isinstance(payload.get(key), list):
                    payload = payload[key]
                    break
            else:
                payload = [payload]
        if not isinstance(payload, list) or not payload:
            raise ValueError("JSON must be a list of records or an object with a data/rows list.")
        if all(isinstance(item, dict) for item in payload):
            header: List[Any] = []
            for item in payload:
                for key in item.keys():
                    if key not in header:
                        header.append(key)
            rows = [header] + [[item.get(key) for key in header] for item in payload]
        elif all(isinstance(item, (list, tuple)) for item in payload):
            rows = [list(item) for item in payload]
        else:
            raise ValueError("JSON records must all be objects or all be arrays.")
    else:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = content.decode("latin-1")
        delimiter = ""
        if name.endswith(".tsv"):
            delimiter = "\t"
        elif name.endswith(".csv"):
            delimiter = ","
        else:
            try:
                delimiter = csv.Sniffer().sniff(text[:4096], delimiters=",\t|;").delimiter
            except csv.Error:
                delimiter = ","
        rows = [r for r in csv.reader(io.StringIO(text), delimiter=delimiter)]
    rows = [r for r in rows if any(v is not None and str(v).strip() != "" for v in r)]
    if not rows:
        raise ValueError("The file has no data rows.")
    header = [str(v if v is not None else "").strip() for v in rows[0]]
    if not any(header):
        raise ValueError("The first row must contain column headers.")
    width = len(header)
    body = []
    for row in rows[1 : MAX_IMPORT_ROWS + 1]:
        padded = list(row[:width]) + [None] * max(0, width - len(row))
        body.append(padded)
    if len(rows) - 1 > MAX_IMPORT_ROWS:
        raise ValueError(f"File has more than {MAX_IMPORT_ROWS} rows. Split it first.")
    return header, body


def _dedupe_headers(header: List[str]) -> List[str]:
    seen: Dict[str, int] = {}
    result = []
    for raw in header:
        base = _safe_ident(raw) if raw else "column"
        key = base.lower()
        seen[key] = seen.get(key, 0) + 1
        result.append(base if seen[key] == 1 else f"{base}_{seen[key]}")
    return result


def _infer_type(values: List[Any]) -> str:
    samples = [v for v in values if v is not None and str(v).strip() != ""][:200]
    if not samples:
        return "TEXT"
    ints = floats = 0
    for v in samples:
        s = str(v).strip()
        try:
            int(s)
            ints += 1
            continue
        except Exception:
            pass
        try:
            float(s)
            floats += 1
        except Exception:
            return "TEXT"
    if ints == len(samples):
        return "INTEGER"
    if ints + floats == len(samples):
        return "REAL"
    return "TEXT"


def _coerce(value: Any, sql_type: str) -> Any:
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    if sql_type == "INTEGER":
        try:
            return int(float(str(value)))
        except Exception:
            return None
    if sql_type == "REAL":
        try:
            return float(str(value))
        except Exception:
            return None
    return str(value)


def import_table(workspace_id: str, filename: str, content: bytes, table_name: str = "", mode: str = "create", schema: str = "main") -> Dict[str, Any]:
    _ensure_schema()
    if not get_workspace(workspace_id):
        raise ValueError("Workspace not found.")
    header, body = _decode_rows(filename, content)
    columns = _dedupe_headers(header)
    table = _safe_ident(table_name or Path(filename or "imported_data").stem)
    schema = _safe_ident(schema or "main").lower()
    if schema != "main":
        existing = {s["schema_name"] for s in _workspace_schemas(workspace_id)}
        if schema not in existing:
            create_schema(workspace_id, schema)

    types = [_infer_type([row[i] for row in body]) for i in range(len(columns))]
    added_columns: List[str] = []
    conn = open_workspace_connection(workspace_id)
    try:
        exists = conn.execute(
            f"SELECT COUNT(*) FROM {_quote(schema)}.sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone()[0] > 0
        if exists and mode != "append":
            raise ValueError(f"Table {table} already exists in {schema}. Choose append mode or another name.")
        if not exists:
            col_defs = ", ".join(f"{_quote(c)} {t}" for c, t in zip(columns, types))
            conn.execute(f"CREATE TABLE {_qualified(schema, table)} ({col_defs})")
        else:
            current = {r[1].lower() for r in conn.execute(f"PRAGMA {_quote(schema)}.table_info({_quote(table)})").fetchall()}
            for c, t in zip(columns, types):
                if c.lower() not in current:
                    conn.execute(f"ALTER TABLE {_qualified(schema, table)} ADD COLUMN {_quote(c)} {t}")
                    added_columns.append(c)

        placeholders = ", ".join("?" for _ in columns)
        insert_sql = (
            f"INSERT INTO {_qualified(schema, table)} ({', '.join(_quote(c) for c in columns)}) VALUES ({placeholders})"
        )
        payload = [
            tuple(_coerce(row[i], types[i]) for i in range(len(columns)))
            for row in body
        ]
        for start in range(0, len(payload), 500):
            conn.executemany(insert_sql, payload[start : start + 500])
        conn.commit()
        total = conn.execute(f"SELECT COUNT(*) FROM {_qualified(schema, table)}").fetchone()[0]
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    _touch_workspace(workspace_id)
    invalidate_catalog()
    return {
        "status": "success",
        "workspace_id": workspace_id,
        "schema": schema,
        "table": table,
        "mode": "append" if exists else "create",
        "rows_inserted": len(body),
        "total_rows": total,
        "added_columns": added_columns,
        "columns": [{"name": c, "data_type": t} for c, t in zip(columns, types)],
    }


# ----------------------------------------------------------------------------
# chat attachments
# ----------------------------------------------------------------------------

_TABLE_STOPWORDS = {
    "a", "an", "and", "append", "bana", "banaun", "banav", "banavun", "called", "create",
    "csv", "data", "ek", "excel", "existing", "file", "from", "ghal", "ha", "he", "hi",
    "hyat", "in", "insert", "into", "it", "kar", "kara", "madhe", "madhye", "me", "my",
    "naam", "named", "nava", "navi", "navin", "new", "of", "pan", "pn", "same", "sheet",
    "table", "tak", "taka", "that", "the", "this", "to", "tyat", "using", "with", "ya",
    "hya", "tya",
}

_APPEND_RE = re.compile(
    r"\b(append|insert|merge|load|import)\b|"
    r"\b(add|put)\b[^.\n]{0,40}\b(to|into|in)\b|"
    r"(madhe|madhye|mathe)\s+(taka|tak|append|insert|ghal|add)|"
    r"\b(tyat|hyat|yat)\b|same table|existing table|(ya|hya|tya)\s+table",
    re.IGNORECASE,
)

_CREATE_RE = re.compile(
    r"\b(create|make|build|new)\b[^.\n]{0,30}\btable\b|"
    r"\b(nava|navin|navi)\b[^.\n]{0,24}\btable\b|"
    r"\btable\s+(bana|banav|create)",
    re.IGNORECASE,
)


def _clean_attachment_id(value: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9_]", "", value or "")
    if not clean.startswith("att_") or len(clean) < 8:
        raise ValueError("Invalid attachment id.")
    return clean


def _cleanup_attachments() -> None:
    cutoff = time.time() - ATTACHMENT_TTL_HOURS * 3600
    try:
        for path in ATTACHMENT_DIR.glob("*"):
            if path.is_file() and path.stat().st_mtime < cutoff:
                path.unlink(missing_ok=True)
    except Exception:
        pass


def save_attachment(workspace_id: str, filename: str, content: bytes) -> Dict[str, Any]:
    _ensure_schema()
    if not get_workspace(workspace_id):
        raise ValueError("Workspace not found.")
    raw_name = Path(filename or "attachment").name.replace("\\", "_").strip() or "attachment"
    ext = Path(raw_name).suffix.lower()
    if ext in TABLE_ATTACHMENT_EXTS:
        kind = "table"
    elif ext in IMAGE_ATTACHMENT_EXTS:
        kind = "image"
    else:
        raise ValueError("Attach a CSV, TSV, Excel (.xlsx), JSON file or an image (PNG/JPG/WEBP/GIF/BMP).")
    if not content:
        raise ValueError("The attached file is empty.")
    if len(content) > MAX_ATTACHMENT_BYTES:
        raise ValueError("Attachment is larger than 25 MB.")
    _cleanup_attachments()
    attachment_id = "att_" + uuid.uuid4().hex[:12]
    ATTACHMENT_DIR.mkdir(parents=True, exist_ok=True)
    path = ATTACHMENT_DIR / f"{attachment_id}{ext}"
    path.write_bytes(content)
    info: Dict[str, Any] = {
        "attachment_id": attachment_id,
        "workspace_id": workspace_id,
        "filename": raw_name,
        "kind": kind,
        "size_bytes": len(content),
        "created_at": _now(),
    }
    if kind == "table":
        try:
            header, body = _decode_rows(raw_name, content)
            columns = _dedupe_headers(header)
            info["columns"] = columns
            info["row_count"] = len(body)
            info["suggested_table"] = _safe_ident(Path(raw_name).stem or "imported_data")
            info["sample_rows"] = [
                {columns[i]: (row[i] if i < len(row) else None) for i in range(len(columns))}
                for row in body[:3]
            ]
        except Exception as exc:
            info["error"] = str(exc)[:300]
    else:
        try:
            from PIL import Image

            with Image.open(io.BytesIO(content)) as img:
                info["width"], info["height"] = img.size
                info["image_format"] = (img.format or "").lower()
        except Exception:
            pass
    meta = dict(info)
    meta["path"] = str(path)
    (ATTACHMENT_DIR / f"{attachment_id}.json").write_text(json.dumps(meta, default=str), encoding="utf-8")
    return info


def load_attachment(workspace_id: str, attachment_id: str) -> Tuple[Dict[str, Any], bytes]:
    clean = _clean_attachment_id(attachment_id)
    meta_path = ATTACHMENT_DIR / f"{clean}.json"
    if not meta_path.is_file():
        raise ValueError("Attachment expired or not found. Please attach the file again.")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if meta.get("workspace_id") != workspace_id:
        raise ValueError("That attachment belongs to another chat.")
    path = Path(meta.get("path") or "")
    if not path.is_file():
        raise ValueError("Attachment file is missing. Please attach it again.")
    return meta, path.read_bytes()


def _workspace_table_map(workspace_id: str) -> Dict[str, Tuple[str, str]]:
    result: Dict[str, Tuple[str, str]] = {}
    conn = open_workspace_connection(workspace_id)
    try:
        schemas = ["main"] + [s["schema_name"] for s in _workspace_schemas(workspace_id)]
        seen = set()
        for schema in schemas:
            if schema in seen:
                continue
            seen.add(schema)
            try:
                rows = conn.execute(
                    f"SELECT name FROM {_quote(schema)}.sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                ).fetchall()
            except sqlite3.Error:
                continue
            for row in rows:
                result[str(row[0]).lower()] = (schema, str(row[0]))
    finally:
        conn.close()
    return result


def _table_name_from_text(text: str) -> str:
    quoted = re.search(r"[`\"']([A-Za-z_][\w]{0,62}(?:\.[A-Za-z_][\w]{0,62})?)[`\"']", text or "")
    if quoted:
        return quoted.group(1)
    patterns = (
        r"\b(?:table|tbl)\s+(?:called|named|naam|name)\s+([A-Za-z_][\w]{0,62}(?:\.[A-Za-z_][\w]{0,62})?)",
        r"\b(?:create|make|build)\b[^.\n]{0,40}?\btable\s+([A-Za-z_][\w]{0,62}(?:\.[A-Za-z_][\w]{0,62})?)",
        r"\b(?:append|insert|load|add|import)\b[^.\n]{0,40}?\b(?:to|into|in)\s+([A-Za-z_][\w]{0,62}(?:\.[A-Za-z_][\w]{0,62})?)",
        r"\b(?:into|to)\s+([A-Za-z_][\w]{0,62}(?:\.[A-Za-z_][\w]{0,62})?)",
        r"\btable\s+([A-Za-z_][\w]{0,62}(?:\.[A-Za-z_][\w]{0,62})?)",
    )
    for pattern in patterns:
        match = re.search(pattern, text or "", re.IGNORECASE)
        if not match:
            continue
        candidate = match.group(1)
        if candidate.split(".")[-1].lower() in _TABLE_STOPWORDS:
            continue
        return candidate
    return ""


def _resolve_import_plan(
    workspace_id: str,
    info: Dict[str, Any],
    message: str,
    context: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    text = message or ""
    table_map = _workspace_table_map(workspace_id)
    context_schema = ""
    context_table = ""
    if isinstance(context, dict):
        ctx_table = str(context.get("table") or "").strip()
        ctx_schema = str(context.get("schema") or "main").strip() or "main"
        ctx_db = str(context.get("db_id") or "")
        if ctx_table and (not ctx_db or ctx_db in (workspace_id, "workspace:" + workspace_id)):
            if ctx_table.lower() in table_map:
                context_schema, context_table = table_map[ctx_table.lower()]
            else:
                context_schema, context_table = ctx_schema, ctx_table

    create_intent = bool(_CREATE_RE.search(text))
    append_intent = bool(_APPEND_RE.search(text))
    name = _table_name_from_text(text)
    schema = ""
    if "." in name:
        parts = [p for p in name.split(".") if p]
        if len(parts) >= 2:
            schema, name = parts[-2].lower(), _safe_ident(parts[-1])

    if not name and append_intent and context_table:
        name, schema = context_table, context_schema
    if not name and append_intent:
        mentioned = [tbl for tbl in table_map if re.search(r"\b" + re.escape(tbl) + r"\b", text, re.IGNORECASE)]
        if mentioned:
            name = sorted(mentioned, key=len, reverse=True)[0]
    if not name:
        name = _safe_ident(info.get("suggested_table") or "imported_data")

    existing = table_map.get(name.lower())
    if existing:
        target_schema, name = existing
        mode = "create" if (create_intent and not append_intent) else "append"
    else:
        target_schema = schema or "main"
        mode = "append" if (append_intent and not create_intent) else "create"
    if schema:
        target_schema = schema
    return {
        "schema": _safe_ident(target_schema or "main").lower(),
        "table": _safe_ident(name),
        "mode": mode,
    }


def _attachment_reply(
    workspace_id: str,
    message: str,
    prepared: List[Tuple[Dict[str, Any], bytes]],
    context: Optional[Dict[str, Any]],
    started_at: float,
    user: str = "",
) -> Dict[str, Any]:
    imports: List[Dict[str, Any]] = []
    notes: List[str] = []
    errors: List[str] = []
    for info, content in prepared:
        filename = info.get("filename") or "attachment"
        if info.get("error"):
            errors.append(f"{filename}: {info['error']}")
            continue
        if info.get("kind") == "image":
            dims = ""
            if info.get("width") and info.get("height"):
                dims = f" ({info['width']}x{info['height']}px)"
            notes.append(f"Image {filename}{dims} attached.")
            continue
        plan = _resolve_import_plan(workspace_id, info, message, context)
        try:
            result = import_table(
                workspace_id,
                filename,
                content,
                table_name=plan["table"],
                mode=plan["mode"],
                schema=plan["schema"],
            )
        except Exception as exc:
            errors.append(f"{filename}: {exc}")
            continue
        result["attachment_id"] = info.get("attachment_id")
        result["filename"] = filename
        imports.append(result)
        qualified = f"{result['schema']}.{result['table']}"
        if result["mode"] == "create":
            names = [c["name"] for c in result["columns"]]
            listed = ", ".join(names[:10]) + (" …" if len(names) > 10 else "")
            notes.append(
                f"Created table {qualified} from {filename} — {result['rows_inserted']} row(s), "
                f"{len(names)} column(s): {listed}."
            )
        else:
            extra = ""
            if result.get("added_columns"):
                extra = f" New column(s) added: {', '.join(result['added_columns'])}."
            notes.append(
                f"Appended {result['rows_inserted']} row(s) from {filename} to {qualified} — "
                f"total {result['total_rows']} row(s).{extra}"
            )
    for error in errors:
        notes.append(f"Could not import {error}")

    reply = "\n".join(notes) or "Attachments received."
    if imports:
        reply += "\n\nAsk about the imported data whenever you want — for example: show the first 10 rows."

    preview = None
    if len(imports) == 1:
        item = imports[0]
        try:
            details = get_table_details(
                "workspace:" + workspace_id,
                item["schema"],
                item["table"],
                catalog_for_chat(workspace_id),
            )
            preview = {
                "columns": [c["name"] for c in details.get("columns", [])],
                "rows": details.get("sample", []),
                "row_count": details.get("row_count") or item["total_rows"],
                "truncated": False,
            }
        except Exception:
            preview = None

    latency_ms = round((time.time() - started_at) * 1000, 1)
    meta = {
        "imports": imports,
        "model": "file-import",
        "latency_ms": latency_ms,
        "row_count": (preview or {}).get("row_count") or sum(int(i.get("rows_inserted") or 0) for i in imports) or 0,
    }
    if imports:
        try:
            with _catalog_lock:
                _catalog_cache["at"] = 0.0
            _refresh_catalog_async()
        except Exception:
            pass

    assistant = add_message(workspace_id, "assistant", reply, "", meta, user=user)
    return {
        "status": "success",
        "workspace": get_workspace(workspace_id, user=user),
        "workspace_created": None,
        "schema_created": None,
        "message": assistant,
        "reply": reply,
        "sql": None,
        "target": "workspace:" + workspace_id,
        "error": ("; ".join(errors)[:400] or None) if errors else None,
        "result": dict(preview, run_id=None) if preview else None,
        "model": "file-import",
        "latency_ms": latency_ms,
        "schedule_created": None,
        "schedule_run": None,
        "imports": imports,
    }
