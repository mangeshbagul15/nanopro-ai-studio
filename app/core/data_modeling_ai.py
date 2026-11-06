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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import SQLITE_DB_PATH
from app.core.database import db
from app.core.logger import log_event
from app.core.manager_contract import DELIVERY_CONTRACT

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
MODELING_DIR = DATA_DIR / "modeling"
MAX_PREVIEW_ROWS = 200
MAX_IMPORT_ROWS = 50000
MAX_CONTEXT_CHARS = 26000

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
    fresh = list_catalog()
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
_WRITE_PREFIX = re.compile(r"^\s*(create\s+(table|view|index|temp\s+table|temporary\s+table)|insert\s+into|update\s+\S+\s+set)\b", re.IGNORECASE)
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


def list_workspaces(light: bool = False) -> List[Dict[str, Any]]:
    _ensure_schema()
    with db.get_connection() as conn:
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


def get_workspace(workspace_id: str) -> Optional[Dict[str, Any]]:
    _ensure_schema()
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT w.*,"
            " (SELECT COUNT(*) FROM dm_messages m WHERE m.workspace_id = w.id) AS message_count,"
            " (SELECT MAX(m.created_at) FROM dm_messages m WHERE m.workspace_id = w.id) AS last_message_at"
            " FROM dm_workspaces w WHERE w.id = ?",
            (workspace_id,),
        ).fetchone()
    if not row:
        return None
    row = dict(row)
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
    with db.get_connection() as conn:
        project = (project_id or "").strip()
        if project and not conn.execute("SELECT 1 FROM dm_projects WHERE id = ?", (project,)).fetchone():
            project = ""
        conn.execute(
            "INSERT INTO dm_workspaces (id, name, created_by, created_at, updated_at, project_id, pinned)"
            " VALUES (?, ?, ?, ?, ?, ?, 0)",
            (wid, label, user or "", stamp, stamp, project),
        )
        conn.commit()
    open_workspace_connection(wid).close()
    invalidate_catalog()
    log_event(f"Data modeling chat created: {wid} ({label})", component="DataModeling")
    return get_workspace(wid) or {"id": wid, "name": label, "created_at": stamp, "updated_at": stamp, "schemas": []}


def set_workspace_pinned(workspace_id: str, pinned: bool) -> Dict[str, Any]:
    _ensure_schema()
    with db.get_connection() as conn:
        cur = conn.execute("UPDATE dm_workspaces SET pinned = ? WHERE id = ?", (1 if pinned else 0, workspace_id))
        conn.commit()
    if not cur.rowcount:
        raise ValueError("Chat not found.")
    return get_workspace(workspace_id) or {}


def set_workspace_project(workspace_id: str, project_id: str) -> Dict[str, Any]:
    _ensure_schema()
    target = (project_id or "").strip()
    with db.get_connection() as conn:
        if target and not conn.execute("SELECT 1 FROM dm_projects WHERE id = ?", (target,)).fetchone():
            raise ValueError("Project not found.")
        cur = conn.execute("UPDATE dm_workspaces SET project_id = ? WHERE id = ?", (target, workspace_id))
        conn.commit()
    if not cur.rowcount:
        raise ValueError("Chat not found.")
    return get_workspace(workspace_id) or {}


def delete_workspace(workspace_id: str) -> Dict[str, Any]:
    _ensure_schema()
    db_path = _workspace_db_path(workspace_id)
    with db.get_connection() as conn:
        exists = conn.execute("SELECT 1 FROM dm_workspaces WHERE id = ?", (workspace_id,)).fetchone()
        if not exists:
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
        except FileNotFoundError:
            pass
    invalidate_catalog()
    log_event(f"Data modeling chat deleted: {workspace_id}", component="DataModeling")
    return {"workspace_id": workspace_id, "deleted": True}


def list_projects() -> List[Dict[str, Any]]:
    _ensure_schema()
    with db.get_connection() as conn:
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
    with db.get_connection() as conn:
        conn.execute(
            "INSERT INTO dm_projects (id, name, created_by, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (pid, label, user or "", stamp, stamp),
        )
        conn.commit()
    return {"id": pid, "name": label, "created_by": user or "", "created_at": stamp, "updated_at": stamp, "chat_count": 0}


def rename_project(project_id: str, name: str) -> Dict[str, Any]:
    label = (name or "").strip()[:64]
    if not label:
        raise ValueError("Project name cannot be empty.")
    _ensure_schema()
    with db.get_connection() as conn:
        cur = conn.execute("UPDATE dm_projects SET name = ?, updated_at = ? WHERE id = ?", (label, _now(), project_id))
        conn.commit()
    if not cur.rowcount:
        raise ValueError("Project not found.")
    for project in list_projects():
        if project["id"] == project_id:
            return project
    return {"id": project_id, "name": label}


def delete_project(project_id: str, delete_chats: bool = False) -> Dict[str, Any]:
    _ensure_schema()
    with db.get_connection() as conn:
        exists = conn.execute("SELECT 1 FROM dm_projects WHERE id = ?", (project_id,)).fetchone()
        if not exists:
            raise ValueError("Project not found.")
        chat_ids = [r["id"] for r in _table_rows(conn, "SELECT id FROM dm_workspaces WHERE project_id = ?", (project_id,))]
    if delete_chats:
        for chat_id in chat_ids:
            delete_workspace(chat_id)
    with db.get_connection() as conn:
        conn.execute("DELETE FROM dm_projects WHERE id = ?", (project_id,))
        if not delete_chats:
            conn.execute("UPDATE dm_workspaces SET project_id = '' WHERE project_id = ?", (project_id,))
        conn.commit()
    invalidate_catalog()
    return {"project_id": project_id, "deleted": True, "chats": len(chat_ids), "chats_deleted": bool(delete_chats)}


def rename_workspace(workspace_id: str, name: str) -> Dict[str, Any]:
    label = (name or "").strip()[:64]
    if not label:
        raise ValueError("Workspace name cannot be empty.")
    _ensure_schema()
    with db.get_connection() as conn:
        conn.execute("UPDATE dm_workspaces SET name = ?, updated_at = ? WHERE id = ?", (label, _now(), workspace_id))
        conn.commit()
    ws = get_workspace(workspace_id)
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
# chat history
# ----------------------------------------------------------------------------

def get_messages(workspace_id: str, limit: int = 300) -> List[Dict[str, Any]]:
    _ensure_schema()
    with db.get_connection() as conn:
        rows = _table_rows(
            conn,
            "SELECT * FROM dm_messages WHERE workspace_id = ? ORDER BY id DESC LIMIT ?",
            (workspace_id, max(1, min(limit, 500))),
        )
    rows.reverse()
    for row in rows:
        try:
            row["meta"] = json.loads(row["meta"]) if row["meta"] else {}
        except Exception:
            row["meta"] = {}
    return rows


def add_message(workspace_id: str, role: str, content: str, sql_text: str = "", meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    _ensure_schema()
    stamp = _now()
    with db.get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO dm_messages (workspace_id, role, content, sql_text, meta, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (workspace_id, role, content or "", sql_text or "", json.dumps(meta or {}), stamp),
        )
        conn.commit()
        msg_id = cur.lastrowid
    _touch_workspace(workspace_id)
    return {"id": msg_id, "workspace_id": workspace_id, "role": role, "content": content, "sql": sql_text, "meta": meta or {}, "created_at": stamp}


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
        "status": "online",
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
        "status": "online",
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


def list_catalog() -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for ws in list_workspaces():
        entries.append({
            "id": "workspace:" + ws["id"],
            "name": ws["name"],
            "engine": "sqlite",
            "kind": "workspace",
            "writable": True,
            "status": "online",
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


def get_table_details(db_id: str, schema: str, table: str) -> Dict[str, Any]:
    entry = find_catalog_entry(db_id)
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
    if _DESTRUCTIVE.search(statement):
        raise ValueError("Destructive SQL (DROP/DELETE/TRUNCATE/ATTACH/GRANT) is blocked. Ask for a safe alternative.")

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


def run_to_csv(run_id: str) -> Tuple[str, str]:
    run = get_run(run_id)
    if not run:
        raise ValueError("Result set not found.")
    buf = io.StringIO()
    writer = csv.writer(buf)
    columns = run.get("columns") or []
    writer.writerow(columns)
    for row in run.get("rows") or []:
        writer.writerow([row.get(c, "") for c in columns])
    return f"{run_id}.csv", buf.getvalue()


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


def _clean_steps(statements: Any) -> List[str]:
    if isinstance(statements, str):
        statements = [statements]
    cleaned: List[str] = []
    for statement in statements or []:
        text = _assert_single_statement(str(statement))
        _assert_alter_allowed(text)
        if _DESTRUCTIVE.search(text):
            raise ValueError("Scheduled steps cannot be destructive (DROP/DELETE/TRUNCATE).")
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
    steps = _clean_steps(statements)
    target = (target or "").strip()
    if target in ("", "workspace", "active", "workspace:" + workspace_id):
        target = "workspace:" + workspace_id
    elif not find_catalog_entry(target):
        raise ValueError("Target database was not found in the live catalog.")
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

def _catalog_for_prompt(workspace_id: str, question: str) -> str:
    catalog = catalog_snapshot()
    q = (question or "").lower()
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
            # tables named in the question, otherwise the table list only.
            detailed = entry["kind"] == "workspace" or any(n.lower() in q for n in names)
            if detailed:
                for name in names[:120]:
                    try:
                        details = get_table_details(entry["id"], schema.get("schema", schema["name"]), name)
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
                lines.append(f"  {schema['name']}: " + ", ".join(names[:200]))
        if sum(len(x) for x in lines) > MAX_CONTEXT_CHARS:
            lines.append("  …catalog truncated…")
            break
    text = "\n".join(lines)
    if len(text) > MAX_CONTEXT_CHARS:
        text = text[:MAX_CONTEXT_CHARS] + "\n…catalog truncated…"
    return f"TOTAL_TABLES={total_tables}\n" + text


def _system_prompt(workspace: Dict[str, Any]) -> str:
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
        "6) Writes (CREATE TABLE/VIEW/INDEX, INSERT, UPDATE, MERGE) are allowed only on the workspace and the Snowflake connection. "
        "Every other live database is read-only.\n"
        "7) Never use DROP, DELETE, TRUNCATE, ATTACH, GRANT or REVOKE. ALTER TABLE is allowed only for ADD COLUMN, "
        "RENAME COLUMN, RENAME TO and datatype changes.\n"
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
        + DELIVERY_CONTRACT
        + f"Active workspace: {workspace['id']} — {workspace['name']}.\n"
    )


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
    sql_match = re.search(r"```sql\s*(.*?)```", text or "", re.IGNORECASE | re.DOTALL)
    return {
        "reply": (text or "").strip()[:1200],
        "sql": sql_match.group(1).strip() if sql_match else None,
    }


def _looks_like_sql(message: str) -> bool:
    text = message or ""
    if re.match(r"^\s*(select|with|pragma|explain)\b", text, re.IGNORECASE):
        return True
    return bool(
        re.match(r"^\s*(create|insert|update|delete|drop|alter|truncate)\b", text, re.IGNORECASE)
        and re.search(r"\b(table|view|index|into|from|set)\b", text, re.IGNORECASE)
    )


def _fallback_answer(workspace_id: str, message: str) -> Dict[str, Any]:
    catalog = catalog_snapshot()
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
                        details = get_table_details(entry["id"], schema.get("schema", schema["name"]), name)
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
            "reply": f"NanoPro currently exposes {db_total} databases with about {table_total} tables. Your workspace has {len(ws_tables)} table(s): {', '.join(ws_tables) or 'none yet'}. The AI model is not connected right now, so I can only answer catalog questions — configure GROQ_API_KEY to enable full natural-language SQL.",
            "sql": None,
        }
    return {
        "reply": "The AI model is not connected yet, so I cannot generate SQL for that request. I can still show the live catalog, table columns and workspace history. Ask 'list tables' or name a table to see its columns.",
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


def _fast_intent(workspace_id: str, message: str) -> Optional[Dict[str, Any]]:
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
    catalog = catalog_snapshot(ttl=30.0)

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
                    entry["id"], schema.get("schema") or schema.get("name") or "main", table["name"]
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
        r"(?:please\s+)?(?:show|get|display|fetch|give|bring)\s+(?:me\s+)?(?:the\s+)?(?:top|first|last)\s*(\d{1,4})?\s*"
        r"(?:rows?|records?)?\s*(?:from|of|in)\s+(" + _IDENT_TOKEN + r")\s*[?.!]?",
        text,
        re.IGNORECASE,
    )
    if top_match:
        count = max(1, min(int(top_match.group(1) or 5), 100))
        found = _find_named_table(catalog, top_match.group(2))
        if found:
            entry, schema, table = found
            source = _fast_query_source(entry, schema, table)
            if source:
                return {
                    "reply": f"Here are the first {count} row(s) of {table['name']} from {entry['name']}.",
                    "sql": f"SELECT * FROM {source} LIMIT {count}",
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


def _reply_cache_key(workspace_id: str, message: str) -> str:
    return workspace_id + "|" + re.sub(r"\s+", " ", (message or "").strip().lower())


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
    with _AI_REPLY_LOCK:
        if len(_AI_REPLY_CACHE) >= _AI_REPLY_MAX:
            oldest = min(_AI_REPLY_CACHE, key=lambda k: _AI_REPLY_CACHE[k]["at"])
            _AI_REPLY_CACHE.pop(oldest, None)
        _AI_REPLY_CACHE[key] = {"at": time.time(), "value": dict(value)}


def chat(workspace_id: str, message: str, user: str = "") -> Dict[str, Any]:
    _ensure_schema()
    workspace = get_workspace(workspace_id)
    if not workspace:
        raise ValueError("Workspace not found.")
    message = (message or "").strip()
    if not message:
        raise ValueError("Message cannot be empty.")
    if len(message) > 4000:
        message = message[:4000]

    is_first = not get_messages(workspace_id, limit=1)
    add_message(workspace_id, "user", message)

    started_at = time.time()
    parsed: Dict[str, Any] = {}
    model_used = "fallback"
    if _looks_like_sql(message):
        parsed = {"reply": "Running your SQL now.", "sql": message, "target": "workspace", "action": None}
        model_used = "direct-sql"
    else:
        fast = _fast_intent(workspace_id, message)
        if fast:
            parsed = fast
            model_used = "fast-nlu"
        else:
            cache_key = _reply_cache_key(workspace_id, message)
            cached = _reply_cache_get(cache_key)
            if cached:
                parsed = cached
                model_used = "cached-ai"
            else:
                catalog_text = _catalog_for_prompt(workspace_id, message)
                history_rows = get_messages(workspace_id, limit=12)[:-1]
                history = "\n".join(f"{m['role']}: {m['content'][:600]}" for m in history_rows)
                prompt = (
                    f"{catalog_text}\n\nCONVERSATION SO FAR:\n{history or '(new conversation)'}\n\n"
                    f"USER: {message}\n\nReturn the JSON object now."
                )
                try:
                    from app.core.model_adapter import model_manager

                    content, model_used, _, _ = model_manager.route_and_execute(
                        prompt,
                        task_type="data_analyst",
                        schema={"type": "json_object"},
                        system_prompt=_system_prompt(workspace),
                        timeout=30.0,
                        temperature=0.2,
                        max_tokens=900,
                    )
                    parsed = _parse_json_reply(content)
                    _reply_cache_put(cache_key, parsed)
                except Exception as exc:
                    log_event(f"Data modeling AI unavailable: {exc}", level="WARNING", component="DataModeling")
                    parsed = _fallback_answer(workspace_id, message)
                    model_used = "fallback"

    action = (parsed.get("action") or "").strip().lower()
    sql = parsed.get("sql")
    if isinstance(sql, list):
        sql = " ".join(str(s) for s in sql)
    sql = (sql or "").strip() or None
    target = (parsed.get("target") or "workspace").strip()
    reply = (parsed.get("reply") or "").strip()[:2000] or "Done."

    created_workspace = None
    created_schema = None
    created_schedule = None
    schedule_run = None
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
    elif action in ("create_schedule", "create_pipeline"):
        steps = parsed.get("steps") or ([sql] if sql else [])
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
                target=parsed.get("target") or "",
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

    result = None
    run_id = None
    error = schedule_error or None
    if sql and not created_schema and not schedule_handled:
        try:
            result = execute_sql(target, sql, workspace_id=workspace_id)
            run_id = save_run(workspace_id, sql, result)
        except Exception as exc:
            error = str(exc)[:400]

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
        "fast_path": bool(parsed.get("fast")),
        "workspace_created": created_workspace["id"] if created_workspace else None,
        "schema_created": created_schema["schema"] if created_schema else None,
        "schedule_created": created_schedule["schedule_id"] if created_schedule else None,
        "schedule_run": schedule_run["run_id"] if schedule_run else None,
    }
    if error:
        reply = (reply + f"\n\nSQL error: {error}").strip()
    elif result:
        if result.get("rows_affected") and not result.get("columns"):
            note = f"{result['rows_affected']} row(s) affected"
        else:
            note = f"Returned {result['row_count']} row(s)" + (" (preview truncated)" if result.get("truncated") else "")
        reply = (reply + f"\n\n{note}.").strip()

    assistant = add_message(workspace_id, "assistant", reply, sql or "", meta)
    if is_first:
        title = message.replace("\n", " ").strip()
        if len(title) > 48:
            title = title[:48].rstrip() + "…"
        try:
            rename_workspace(workspace_id, title)
        except Exception:
            pass

    return {
        "status": "success",
        "workspace": get_workspace(workspace_id),
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
    else:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = content.decode("latin-1")
        rows = [r for r in csv.reader(io.StringIO(text))]
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
        "columns": [{"name": c, "data_type": t} for c, t in zip(columns, types)],
    }
