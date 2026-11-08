"""
DuckDB Per-User Chat & Workspace Store
======================================
Provides dedicated, high-performance, ACID-compliant persistence for:
  - User Workspaces (Chats)
  - User Projects
  - User Chat Messages (Prompts, SQL, AI Copilot responses, attachments)
  - User Active Chat & Session State (preserved across URL refresh & reloads)
  - Export in Claude / Google Cloud format

Each user gets their own isolated DuckDB database file in:
  data/modeling/users/{username}_chats.duckdb
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import duckdb
from app.core.logger import log_event

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
MODELING_DIR = DATA_DIR / "modeling"
USERS_DIR = MODELING_DIR / "users"

_locks: Dict[str, threading.RLock] = {}
_global_lock = threading.Lock()


def _get_user_lock(username: str) -> threading.RLock:
    safe = _sanitize_username(username)
    with _global_lock:
        if safe not in _locks:
            _locks[safe] = threading.RLock()
        return _locks[safe]


def _sanitize_username(username: str) -> str:
    try:
        from app.core.identity_resolver import resolve_canonical_username
        canon = resolve_canonical_username(username)
    except Exception:
        canon = username
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", (canon or "user").strip().lower()).strip("_")
    return cleaned or "user"


def _user_db_path(username: str) -> Path:
    USERS_DIR.mkdir(parents=True, exist_ok=True)
    safe = _sanitize_username(username)
    return USERS_DIR / f"{safe}_chats.duckdb"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_connection(username: str) -> duckdb.DuckDBPyConnection:
    path = _user_db_path(username)
    conn = duckdb.connect(str(path))
    _ensure_schema(conn)
    return conn


def _ensure_schema(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS dm_workspaces (
        id VARCHAR PRIMARY KEY,
        name VARCHAR NOT NULL,
        created_by VARCHAR DEFAULT '',
        created_at VARCHAR NOT NULL,
        updated_at VARCHAR NOT NULL,
        project_id VARCHAR DEFAULT '',
        pinned BOOLEAN DEFAULT FALSE
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS dm_projects (
        id VARCHAR PRIMARY KEY,
        name VARCHAR NOT NULL,
        created_by VARCHAR DEFAULT '',
        created_at VARCHAR NOT NULL,
        updated_at VARCHAR NOT NULL
    );
    """)

    conn.execute("""
    CREATE SEQUENCE IF NOT EXISTS dm_msg_seq START 1;
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS dm_messages (
        id BIGINT PRIMARY KEY,
        workspace_id VARCHAR NOT NULL,
        role VARCHAR NOT NULL,
        content VARCHAR NOT NULL,
        sql_text VARCHAR DEFAULT '',
        meta VARCHAR DEFAULT '{}',
        created_at VARCHAR NOT NULL
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS dm_user_state (
        user_id VARCHAR PRIMARY KEY,
        active_workspace_id VARCHAR DEFAULT '',
        active_project_id VARCHAR DEFAULT '',
        updated_at VARCHAR NOT NULL
    );
    """)


class DuckDBChatStore:
    def __init__(self):
        USERS_DIR.mkdir(parents=True, exist_ok=True)

    def _sync_from_sqlite_if_empty(self, user: str, conn: duckdb.DuckDBPyConnection) -> None:
        """One-time migration: copies user's existing SQLite records to DuckDB if DuckDB has 0 workspaces."""
        count = conn.execute("SELECT COUNT(*) FROM dm_workspaces").fetchone()[0]
        if count > 0:
            return

        try:
            from app.core.database import db

            with db.get_connection() as sconn:
                safe_user = (user or "").strip()

                # Personal chats stay personal for every account, admin included.
                cur = sconn.execute(
                    "SELECT id, name, created_by, created_at, updated_at, project_id, pinned FROM dm_workspaces WHERE created_by = ?",
                    (safe_user,),
                )
                ws_rows = cur.fetchall()

                for row in ws_rows:
                    conn.execute(
                        "INSERT OR IGNORE INTO dm_workspaces VALUES (?, ?, ?, ?, ?, ?, ?)",
                        [row[0], row[1], row[2] or safe_user, row[3], row[4], row[5] or "", bool(row[6])],
                    )

                # Fetch projects
                p_rows = sconn.execute(
                    "SELECT id, name, created_by, created_at, updated_at FROM dm_projects WHERE created_by = ?",
                    (safe_user,),
                ).fetchall()

                for prow in p_rows:
                    conn.execute(
                        "INSERT OR IGNORE INTO dm_projects VALUES (?, ?, ?, ?, ?)",
                        [prow[0], prow[1], prow[2] or safe_user, prow[3], prow[4]],
                    )

                # Fetch messages
                ws_ids = [r[0] for r in ws_rows]
                if ws_ids:
                    placeholders = ",".join(["?"] * len(ws_ids))
                    m_rows = sconn.execute(
                        f"SELECT id, workspace_id, role, content, sql_text, meta, created_at FROM dm_messages WHERE workspace_id IN ({placeholders})",
                        tuple(ws_ids),
                    ).fetchall()
                    for mrow in m_rows:
                        conn.execute(
                            "INSERT OR IGNORE INTO dm_messages VALUES (nextval('dm_msg_seq'), ?, ?, ?, ?, ?, ?)",
                            [mrow[1], mrow[2], mrow[3] or "", mrow[4] or "", mrow[5] or "{}", mrow[6]],
                        )

            log_event(f"Migrated {len(ws_rows)} workspaces to DuckDB for user [{user}]", component="DuckDBChatStore")
        except Exception as e:
            log_event(f"Migration from SQLite skipped: {e}", component="DuckDBChatStore", level="WARNING")

    def list_workspaces(self, user: str, light: bool = False) -> List[Dict[str, Any]]:
        lock = _get_user_lock(user)
        with lock:
            conn = get_connection(user)
            try:
                self._sync_from_sqlite_if_empty(user, conn)
                query = """
                SELECT w.id, w.name, w.created_by, w.created_at, w.updated_at, w.project_id, w.pinned,
                       (SELECT COUNT(*) FROM dm_messages m WHERE m.workspace_id = w.id) AS message_count,
                       (SELECT MAX(m.created_at) FROM dm_messages m WHERE m.workspace_id = w.id) AS last_message_at
                FROM dm_workspaces w
                ORDER BY w.updated_at DESC
                """
                rows = conn.execute(query).fetchall()
                result = []
                for r in rows:
                    ws_id, name, created_by, created_at, updated_at, project_id, pinned, msg_count, last_msg = r
                    item: Dict[str, Any] = {
                        "id": ws_id,
                        "name": name,
                        "created_by": created_by,
                        "created_at": created_at,
                        "updated_at": updated_at,
                        "project_id": project_id or "",
                        "pinned": bool(pinned),
                        "message_count": int(msg_count or 0),
                        "last_message_at": last_msg,
                        "table_count": 0,
                        "schemas": [],
                    }
                    result.append(item)
                return result
            finally:
                conn.close()

    def get_workspace(self, user: str, workspace_id: str) -> Optional[Dict[str, Any]]:
        lock = _get_user_lock(user)
        with lock:
            conn = get_connection(user)
            try:
                self._sync_from_sqlite_if_empty(user, conn)
                row = conn.execute(
                    """
                    SELECT w.id, w.name, w.created_by, w.created_at, w.updated_at, w.project_id, w.pinned,
                           (SELECT COUNT(*) FROM dm_messages m WHERE m.workspace_id = w.id) AS message_count,
                           (SELECT MAX(m.created_at) FROM dm_messages m WHERE m.workspace_id = w.id) AS last_message_at
                    FROM dm_workspaces w WHERE w.id = ?
                    """,
                    [workspace_id],
                ).fetchone()
                if not row:
                    return None
                ws_id, name, created_by, created_at, updated_at, project_id, pinned, msg_count, last_msg = row
                return {
                    "id": ws_id,
                    "name": name,
                    "created_by": created_by,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "project_id": project_id or "",
                    "pinned": bool(pinned),
                    "message_count": int(msg_count or 0),
                    "last_message_at": last_msg,
                    "table_count": 0,
                    "schemas": [],
                }
            finally:
                conn.close()

    def save_workspace(self, user: str, ws: Dict[str, Any]) -> Dict[str, Any]:
        lock = _get_user_lock(user)
        with lock:
            conn = get_connection(user)
            try:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO dm_workspaces (id, name, created_by, created_at, updated_at, project_id, pinned)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        ws["id"],
                        ws.get("name", "New chat"),
                        ws.get("created_by", user),
                        ws.get("created_at", _now()),
                        ws.get("updated_at", _now()),
                        ws.get("project_id", ""),
                        bool(ws.get("pinned", False)),
                    ],
                )
                return ws
            finally:
                conn.close()

    def rename_workspace(self, user: str, workspace_id: str, new_name: str) -> Optional[Dict[str, Any]]:
        lock = _get_user_lock(user)
        with lock:
            conn = get_connection(user)
            try:
                now_str = _now()
                conn.execute(
                    "UPDATE dm_workspaces SET name = ?, updated_at = ? WHERE id = ?",
                    [new_name, now_str, workspace_id],
                )
                return self.get_workspace(user, workspace_id)
            finally:
                conn.close()

    def pin_workspace(self, user: str, workspace_id: str, pinned: bool) -> Optional[Dict[str, Any]]:
        lock = _get_user_lock(user)
        with lock:
            conn = get_connection(user)
            try:
                now_str = _now()
                conn.execute(
                    "UPDATE dm_workspaces SET pinned = ?, updated_at = ? WHERE id = ?",
                    [bool(pinned), now_str, workspace_id],
                )
                return self.get_workspace(user, workspace_id)
            finally:
                conn.close()

    def set_workspace_project(self, user: str, workspace_id: str, project_id: str) -> Optional[Dict[str, Any]]:
        lock = _get_user_lock(user)
        with lock:
            conn = get_connection(user)
            try:
                now_str = _now()
                conn.execute(
                    "UPDATE dm_workspaces SET project_id = ?, updated_at = ? WHERE id = ?",
                    [project_id or "", now_str, workspace_id],
                )
                return self.get_workspace(user, workspace_id)
            finally:
                conn.close()

    def delete_workspace(self, user: str, workspace_id: str) -> bool:
        lock = _get_user_lock(user)
        with lock:
            conn = get_connection(user)
            try:
                conn.execute("DELETE FROM dm_messages WHERE workspace_id = ?", [workspace_id])
                conn.execute("DELETE FROM dm_workspaces WHERE id = ?", [workspace_id])
                # Clear active chat state if it was this one
                conn.execute(
                    "UPDATE dm_user_state SET active_workspace_id = '' WHERE active_workspace_id = ?",
                    [workspace_id],
                )
                return True
            finally:
                conn.close()

    def list_projects(self, user: str) -> List[Dict[str, Any]]:
        lock = _get_user_lock(user)
        with lock:
            conn = get_connection(user)
            try:
                self._sync_from_sqlite_if_empty(user, conn)
                rows = conn.execute(
                    """
                    SELECT p.id, p.name, p.created_by, p.created_at, p.updated_at,
                           (SELECT COUNT(*) FROM dm_workspaces w WHERE w.project_id = p.id) AS chat_count
                    FROM dm_projects p
                    ORDER BY p.updated_at DESC
                    """
                ).fetchall()
                result = []
                for r in rows:
                    p_id, name, created_by, created_at, updated_at, chat_count = r
                    result.append({
                        "id": p_id,
                        "name": name,
                        "created_by": created_by,
                        "created_at": created_at,
                        "updated_at": updated_at,
                        "chat_count": int(chat_count or 0),
                    })
                return result
            finally:
                conn.close()

    def create_project(self, user: str, project_id: str, name: str) -> Dict[str, Any]:
        lock = _get_user_lock(user)
        with lock:
            conn = get_connection(user)
            try:
                stamp = _now()
                conn.execute(
                    "INSERT INTO dm_projects (id, name, created_by, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    [project_id, name, user, stamp, stamp],
                )
                return {
                    "id": project_id,
                    "name": name,
                    "created_by": user,
                    "created_at": stamp,
                    "updated_at": stamp,
                    "chat_count": 0,
                }
            finally:
                conn.close()

    def rename_project(self, user: str, project_id: str, new_name: str) -> Optional[Dict[str, Any]]:
        lock = _get_user_lock(user)
        with lock:
            conn = get_connection(user)
            try:
                stamp = _now()
                conn.execute(
                    "UPDATE dm_projects SET name = ?, updated_at = ? WHERE id = ?",
                    [new_name, stamp, project_id],
                )
                row = conn.execute(
                    "SELECT id, name, created_by, created_at, updated_at FROM dm_projects WHERE id = ?",
                    [project_id],
                ).fetchone()
                if not row:
                    return None
                return {
                    "id": row[0],
                    "name": row[1],
                    "created_by": row[2],
                    "created_at": row[3],
                    "updated_at": row[4],
                }
            finally:
                conn.close()

    def delete_project(self, user: str, project_id: str, delete_chats: bool = False) -> Dict[str, Any]:
        lock = _get_user_lock(user)
        with lock:
            conn = get_connection(user)
            try:
                chats = conn.execute("SELECT id FROM dm_workspaces WHERE project_id = ?", [project_id]).fetchall()
                chat_ids = [c[0] for c in chats]
                if delete_chats:
                    for cid in chat_ids:
                        conn.execute("DELETE FROM dm_messages WHERE workspace_id = ?", [cid])
                        conn.execute("DELETE FROM dm_workspaces WHERE id = ?", [cid])
                else:
                    conn.execute("UPDATE dm_workspaces SET project_id = '' WHERE project_id = ?", [project_id])

                conn.execute("DELETE FROM dm_projects WHERE id = ?", [project_id])
                return {"project_id": project_id, "deleted": True, "chats": len(chat_ids)}
            finally:
                conn.close()

    def get_messages(self, user: str, workspace_id: str, limit: int = 300) -> List[Dict[str, Any]]:
        lock = _get_user_lock(user)
        with lock:
            conn = get_connection(user)
            try:
                self._sync_from_sqlite_if_empty(user, conn)
                rows = conn.execute(
                    """
                    SELECT id, workspace_id, role, content, sql_text, meta, created_at
                    FROM dm_messages
                    WHERE workspace_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    [workspace_id, max(1, min(limit, 500))],
                ).fetchall()
                rows.reverse()
                result = []
                for r in rows:
                    msg_id, ws_id, role, content, sql_text, meta_raw, created_at = r
                    meta = {}
                    if meta_raw:
                        try:
                            meta = json.loads(meta_raw)
                        except Exception:
                            meta = {}
                    result.append({
                        "id": msg_id,
                        "workspace_id": ws_id,
                        "role": role,
                        "content": content,
                        "sql": sql_text or "",
                        "meta": meta,
                        "created_at": created_at,
                    })
                return result
            finally:
                conn.close()

    def add_message(
        self,
        user: str,
        workspace_id: str,
        role: str,
        content: str,
        sql_text: str = "",
        meta: Optional[Dict[str, Any]] = None,
        touch: bool = True,
    ) -> Dict[str, Any]:
        lock = _get_user_lock(user)
        with lock:
            conn = get_connection(user)
            try:
                stamp = _now()
                meta_json = json.dumps(meta or {})
                conn.execute(
                    """
                    INSERT INTO dm_messages (id, workspace_id, role, content, sql_text, meta, created_at)
                    VALUES (nextval('dm_msg_seq'), ?, ?, ?, ?, ?, ?)
                    """,
                    [workspace_id, role, content or "", sql_text or "", meta_json, stamp],
                )
                msg_id = conn.execute("SELECT MAX(id) FROM dm_messages WHERE workspace_id = ?", [workspace_id]).fetchone()[0]

                if touch:
                    conn.execute("UPDATE dm_workspaces SET updated_at = ? WHERE id = ?", [stamp, workspace_id])
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO dm_user_state (user_id, active_workspace_id, active_project_id, updated_at)
                        VALUES (?, ?, COALESCE((SELECT project_id FROM dm_workspaces WHERE id = ?), ''), ?)
                        """,
                        [user, workspace_id, workspace_id, stamp],
                    )

                return {
                    "id": msg_id,
                    "workspace_id": workspace_id,
                    "role": role,
                    "content": content,
                    "sql": sql_text or "",
                    "meta": meta or {},
                    "created_at": stamp,
                }
            finally:
                conn.close()

    def save_user_state(self, user: str, active_workspace_id: str, active_project_id: str = "") -> None:
        lock = _get_user_lock(user)
        with lock:
            conn = get_connection(user)
            try:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO dm_user_state (user_id, active_workspace_id, active_project_id, updated_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    [user, active_workspace_id or "", active_project_id or "", _now()],
                )
            finally:
                conn.close()

    def get_user_state(self, user: str) -> Dict[str, str]:
        lock = _get_user_lock(user)
        with lock:
            conn = get_connection(user)
            try:
                row = conn.execute(
                    "SELECT active_workspace_id, active_project_id FROM dm_user_state WHERE user_id = ?",
                    [user],
                ).fetchone()
                if row:
                    return {"active_workspace_id": row[0] or "", "active_project_id": row[1] or ""}
                # Fallback: pick the latest workspace if any
                latest = conn.execute("SELECT id, project_id FROM dm_workspaces ORDER BY updated_at DESC LIMIT 1").fetchone()
                if latest:
                    return {"active_workspace_id": latest[0] or "", "active_project_id": latest[1] or ""}
                return {"active_workspace_id": "", "active_project_id": ""}
            finally:
                conn.close()

    def export_user_chat_google_claude(self, user: str, workspace_id: str) -> Dict[str, Any]:
        """Exports the chat in standard Claude / Google Gemini dialogue transcript format."""
        ws = self.get_workspace(user, workspace_id)
        messages = self.get_messages(user, workspace_id)
        transcript = []
        for m in messages:
            author = "Human" if m["role"] == "user" else "Assistant"
            transcript.append({
                "role": m["role"],
                "author": author,
                "content": m["content"],
                "sql": m.get("sql", ""),
                "timestamp": m["created_at"],
                "meta": m.get("meta", {}),
            })
        return {
            "format": "google_claude_dialogue_v1",
            "exported_at": _now(),
            "user": user,
            "workspace": ws,
            "total_messages": len(transcript),
            "transcript": transcript,
        }


duckdb_chat_store = DuckDBChatStore()
