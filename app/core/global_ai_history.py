"""Global AI Lab chat history: DuckDB working set + BigQuery durable archive.

Render's disk is ephemeral, so DuckDB alone loses every chat on each deploy.
DuckDB stays the fast local working set; every mutation is mirrored to BigQuery
through an outbox (see ``app/core/chat_bigquery.py``) and rebuilt from BigQuery
per user on first use, which is what makes history survive restarts.

Each row carries ``user_key``, so a chat or project is only ever visible to the
account that created it. Deletes become tombstones in BigQuery, so a restore can
never resurrect a deleted chat.
"""

import hashlib
import json
import os
import threading
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

import duckdb

from app.core import chat_bigquery

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "global_ai_history.duckdb")
ATTACHMENT_MAX_BYTES = int(os.getenv("NANOPRO_CHAT_ATTACHMENT_MAX_BYTES", str(4 * 1024 * 1024)))
MESSAGE_METADATA_FIELDS = ("model_name", "lab_name", "flag", "country", "date_formatted")


def user_fingerprint(user_key: str) -> str:
    return hashlib.sha256((user_key or "").encode("utf-8")).hexdigest()[:12]


class GlobalAIHistoryEngine:
    _instance = None
    _inst_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._inst_lock:
                if cls._instance is None:
                    cls._instance = super(GlobalAIHistoryEngine, cls).__new__(cls)
                    cls._instance._init_db()
        return cls._instance

    # -------------------------------------------------------------------------
    # CONNECTION & SCHEMA
    # -------------------------------------------------------------------------
    def _get_connection(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        return duckdb.connect(DB_PATH)

    def _init_db(self):
        self._write_lock = threading.RLock()
        self._restore_lock = threading.Lock()
        self._restore_events: Dict[str, threading.Event] = {}
        self._restore_results: Dict[str, Dict[str, Any]] = {}
        self._flush_wakeup = threading.Event()
        self._cloud_status_cache: Tuple[float, Dict[str, Any]] = (0.0, {})
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id VARCHAR PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    description VARCHAR,
                    created_at DOUBLE,
                    updated_at DOUBLE
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    id VARCHAR PRIMARY KEY,
                    project_id VARCHAR,
                    title VARCHAR NOT NULL,
                    model VARCHAR DEFAULT 'auto',
                    effort VARCHAR DEFAULT 'default',
                    is_pinned BOOLEAN DEFAULT FALSE,
                    message_count INTEGER DEFAULT 0,
                    created_at DOUBLE,
                    updated_at DOUBLE
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id VARCHAR PRIMARY KEY,
                    chat_id VARCHAR NOT NULL,
                    role VARCHAR NOT NULL,
                    content VARCHAR NOT NULL,
                    model_routed VARCHAR,
                    model_executed VARCHAR,
                    duration_ms DOUBLE,
                    routing_math VARCHAR,
                    created_at DOUBLE
                )
            """)
            conn.execute("CREATE TABLE IF NOT EXISTS bq_sync_log (message_id VARCHAR PRIMARY KEY, synced_at DOUBLE, status VARCHAR)")
            self._migrate(conn)
        finally:
            conn.close()
        threading.Thread(target=self._sync_worker, daemon=True, name="chat-history-sync").start()

    def _migrate(self, conn) -> None:
        migrations = (
            "ALTER TABLE projects ADD COLUMN IF NOT EXISTS user_key VARCHAR",
            "ALTER TABLE projects ADD COLUMN IF NOT EXISTS deleted BOOLEAN DEFAULT FALSE",
            "ALTER TABLE chats ADD COLUMN IF NOT EXISTS user_key VARCHAR",
            "ALTER TABLE chats ADD COLUMN IF NOT EXISTS deleted BOOLEAN DEFAULT FALSE",
            "ALTER TABLE messages ADD COLUMN IF NOT EXISTS user_key VARCHAR",
            "ALTER TABLE messages ADD COLUMN IF NOT EXISTS content_type VARCHAR DEFAULT 'markdown'",
            "ALTER TABLE messages ADD COLUMN IF NOT EXISTS metadata VARCHAR",
            "ALTER TABLE messages ADD COLUMN IF NOT EXISTS deleted BOOLEAN DEFAULT FALSE",
            """
            CREATE TABLE IF NOT EXISTS attachments (
                id VARCHAR PRIMARY KEY,
                chat_id VARCHAR,
                message_id VARCHAR,
                user_key VARCHAR,
                kind VARCHAR,
                name VARCHAR,
                mime_type VARCHAR,
                size_bytes BIGINT,
                data VARCHAR,
                created_at DOUBLE,
                deleted BOOLEAN DEFAULT FALSE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS bq_outbox (
                seq BIGINT PRIMARY KEY,
                entity VARCHAR,
                row_id VARCHAR,
                user_key VARCHAR,
                payload VARCHAR,
                created_at DOUBLE,
                attempts INTEGER DEFAULT 0,
                last_error VARCHAR,
                synced_at DOUBLE
            )
            """,
            "ALTER TABLE bq_outbox ADD COLUMN IF NOT EXISTS user_key VARCHAR",
            "CREATE TABLE IF NOT EXISTS sync_state (key VARCHAR PRIMARY KEY, value VARCHAR)",
        )
        for statement in migrations:
            try:
                conn.execute(statement)
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # INTERNAL HELPERS
    # -------------------------------------------------------------------------
    @staticmethod
    def _claim_legacy(conn, table: str, user_key: str, extra_where: str = "", extra_params: Optional[List[Any]] = None) -> None:
        """Adopts pre-multi-user rows for the first account that signs in."""
        where = "user_key IS NULL" + (f" AND {extra_where}" if extra_where else "")
        try:
            conn.execute(f"UPDATE {table} SET user_key = ? WHERE {where}", [user_key] + list(extra_params or []))
        except Exception:
            pass

    def _enqueue(self, conn, entity: str, row: Dict[str, Any]) -> None:
        try:
            seq = int((conn.execute("SELECT COALESCE(MAX(seq), 0) + 1 FROM bq_outbox").fetchone() or [1])[0])
            conn.execute(
                "INSERT INTO bq_outbox (seq, entity, row_id, user_key, payload, created_at, attempts) VALUES (?, ?, ?, ?, ?, ?, 0)",
                [
                    seq,
                    entity,
                    str(row.get("project_id") or row.get("chat_id") or row.get("message_id") or row.get("attachment_id") or ""),
                    row.get("user_key"),
                    json.dumps(row, default=str),
                    time.time(),
                ],
            )
        except Exception:
            return
        self._flush_wakeup.set()

    @staticmethod
    def _cloud_row(entity: str, record: Dict[str, Any], user_key: str, deleted: bool = False) -> Dict[str, Any]:
        now = float(record.get("updated_at") or record.get("created_at") or time.time())
        base = {"user_key": user_key, "deleted": bool(deleted), "updated_ts": record.get("updated_ts") or now}
        if entity == "projects":
            return {
                "project_id": record.get("id"),
                "name": record.get("name"),
                "description": record.get("description"),
                "created_at": record.get("created_at"),
                "updated_at": record.get("updated_at"),
                **base,
            }
        if entity == "chats":
            return {
                "chat_id": record.get("id"),
                "project_id": record.get("project_id"),
                "title": record.get("title"),
                "model": record.get("model"),
                "effort": record.get("effort"),
                "is_pinned": bool(record.get("is_pinned")),
                "message_count": int(record.get("message_count") or 0),
                "created_at": record.get("created_at"),
                "updated_at": record.get("updated_at"),
                **base,
            }
        if entity == "messages":
            return {
                "message_id": record.get("id"),
                "chat_id": record.get("chat_id"),
                "role": record.get("role"),
                "content": record.get("content"),
                "content_type": record.get("content_type") or "markdown",
                "model_routed": record.get("model_routed"),
                "model_executed": record.get("model_executed"),
                "model_name": record.get("model_name"),
                "lab_name": record.get("lab_name"),
                "flag": record.get("flag"),
                "country": record.get("country"),
                "duration_ms": float(record.get("duration_ms") or 0.0),
                "routing_math": json.dumps(record["routing_math"]) if isinstance(record.get("routing_math"), dict) else record.get("routing_math"),
                "metadata": record.get("metadata"),
                "created_at": record.get("created_at"),
                **base,
            }
        return {
            "attachment_id": record.get("id"),
            "chat_id": record.get("chat_id"),
            "message_id": record.get("message_id"),
            "kind": record.get("kind"),
            "name": record.get("name"),
            "mime_type": record.get("mime_type"),
            "size_bytes": int(record.get("size_bytes") or 0),
            "data": record.get("data"),
            "created_at": record.get("created_at"),
            **base,
        }

    # -------------------------------------------------------------------------
    # PROJECTS
    # -------------------------------------------------------------------------
    def list_projects(self, user_key: str) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            self._claim_legacy(conn, "projects", user_key)
            rows = conn.execute(
                "SELECT id, name, description, created_at, updated_at FROM projects WHERE user_key = ? AND COALESCE(deleted, FALSE) = FALSE ORDER BY updated_at DESC",
                [user_key],
            ).fetchall()
            return [{"id": r[0], "name": r[1], "description": r[2], "created_at": r[3], "updated_at": r[4]} for r in rows]
        finally:
            conn.close()

    def create_project(self, name: str, description: str = "", user_key: str = "") -> Dict[str, Any]:
        p_id = f"proj_{uuid.uuid4().hex[:8]}"
        now = time.time()
        record = {"id": p_id, "name": (name or "").strip() or "Untitled Project", "description": description, "created_at": now, "updated_at": now}
        with self._write_lock:
            conn = self._get_connection()
            try:
                conn.execute(
                    "INSERT INTO projects (id, name, description, created_at, updated_at, user_key, deleted) VALUES (?, ?, ?, ?, ?, ?, FALSE)",
                    [p_id, record["name"], description, now, now, user_key],
                )
                self._enqueue(conn, "projects", self._cloud_row("projects", record, user_key))
            finally:
                conn.close()
        return record

    def rename_project(self, project_id: str, name: str, user_key: str) -> bool:
        now = time.time()
        with self._write_lock:
            conn = self._get_connection()
            try:
                current = conn.execute(
                    "SELECT name, description, created_at FROM projects WHERE id = ? AND user_key = ? AND COALESCE(deleted, FALSE) = FALSE",
                    [project_id, user_key],
                ).fetchone()
                if not current:
                    return False
                new_name = (name or "").strip() or current[0]
                conn.execute("UPDATE projects SET name = ?, updated_at = ? WHERE id = ? AND user_key = ?", [new_name, now, project_id, user_key])
                record = {"id": project_id, "name": new_name, "description": current[1], "created_at": current[2], "updated_at": now}
                self._enqueue(conn, "projects", self._cloud_row("projects", record, user_key))
                return True
            finally:
                conn.close()

    def delete_project(self, project_id: str, delete_chats: bool = False, user_key: str = "") -> bool:
        now = time.time()
        with self._write_lock:
            conn = self._get_connection()
            try:
                current = conn.execute(
                    "SELECT name, description, created_at FROM projects WHERE id = ? AND user_key = ? AND COALESCE(deleted, FALSE) = FALSE",
                    [project_id, user_key],
                ).fetchone()
                if not current:
                    return False
                chat_ids = [r[0] for r in conn.execute(
                    "SELECT id FROM chats WHERE project_id = ? AND user_key = ? AND COALESCE(deleted, FALSE) = FALSE",
                    [project_id, user_key],
                ).fetchall()]
                conn.execute("UPDATE projects SET deleted = TRUE, updated_at = ? WHERE id = ? AND user_key = ?", [now, project_id, user_key])
                self._enqueue(conn, "projects", self._cloud_row("projects", {"id": project_id, "name": current[0], "description": current[1], "created_at": current[2], "updated_at": now}, user_key, deleted=True))
                for chat_id in chat_ids:
                    if delete_chats:
                        self._tombstone_chat(conn, chat_id, user_key, now)
                    else:
                        conn.execute("UPDATE chats SET project_id = NULL, updated_at = ? WHERE id = ?", [now, chat_id])
                        row = conn.execute("SELECT id, project_id, title, model, effort, is_pinned, message_count, created_at, updated_at FROM chats WHERE id = ?", [chat_id]).fetchone()
                        self._enqueue(conn, "chats", self._cloud_row("chats", self._chat_record(row), user_key))
                return True
            finally:
                conn.close()

    # -------------------------------------------------------------------------
    # CHATS
    # -------------------------------------------------------------------------
    @staticmethod
    def _chat_record(row) -> Dict[str, Any]:
        return {
            "id": row[0], "project_id": row[1], "title": row[2], "model": row[3], "effort": row[4],
            "is_pinned": bool(row[5]), "message_count": row[6], "created_at": row[7], "updated_at": row[8],
        }

    def list_chats(self, user_key: str) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            self._claim_legacy(conn, "chats", user_key)
            self._claim_legacy(
                conn,
                "messages",
                user_key,
                "chat_id IN (SELECT id FROM chats WHERE user_key = ?)",
                [user_key],
            )
            rows = conn.execute(
                """
                SELECT id, project_id, title, model, effort, is_pinned, message_count, created_at, updated_at
                FROM chats
                WHERE user_key = ? AND COALESCE(deleted, FALSE) = FALSE
                ORDER BY is_pinned DESC, updated_at DESC
                """,
                [user_key],
            ).fetchall()
            return [self._chat_record(r) for r in rows]
        finally:
            conn.close()

    def get_chat(self, chat_id: str, user_key: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            row = conn.execute(
                "SELECT id, project_id, title, model, effort, is_pinned, message_count, created_at, updated_at FROM chats WHERE id = ? AND user_key = ? AND COALESCE(deleted, FALSE) = FALSE",
                [chat_id, user_key],
            ).fetchone()
            return self._chat_record(row) if row else None
        finally:
            conn.close()

    def _project_owned(self, conn, project_id: str, user_key: str) -> bool:
        row = conn.execute(
            "SELECT 1 FROM projects WHERE id = ? AND user_key = ? AND COALESCE(deleted, FALSE) = FALSE",
            [project_id, user_key],
        ).fetchone()
        return row is not None

    def create_chat(self, title: str = "", project_id: Optional[str] = None, model: str = "auto", effort: str = "default", user_key: str = "") -> Dict[str, Any]:
        c_id = f"chat_{uuid.uuid4().hex[:8]}"
        now = time.time()
        project_id = project_id or None
        record = {
            "id": c_id, "project_id": project_id, "title": (title or "").strip() or "New AI Chat Session",
            "model": model, "effort": effort, "is_pinned": False, "message_count": 0,
            "created_at": now, "updated_at": now,
        }
        with self._write_lock:
            conn = self._get_connection()
            try:
                if project_id and not self._project_owned(conn, project_id, user_key):
                    raise ValueError("Project not found for this user")
                conn.execute(
                    "INSERT INTO chats (id, project_id, title, model, effort, is_pinned, message_count, created_at, updated_at, user_key, deleted) VALUES (?, ?, ?, ?, ?, FALSE, 0, ?, ?, ?, FALSE)",
                    [c_id, project_id, record["title"], model, effort, now, now, user_key],
                )
                self._enqueue(conn, "chats", self._cloud_row("chats", record, user_key))
            finally:
                conn.close()
        return record

    def update_chat(self, chat_id: str, user_key: str, title: Optional[str] = None, is_pinned: Optional[bool] = None, model: Optional[str] = None, effort: Optional[str] = None, project_id: Optional[str] = None, move_to_project: bool = False) -> bool:
        with self._write_lock:
            conn = self._get_connection()
            try:
                row = conn.execute(
                    "SELECT id, project_id, title, model, effort, is_pinned, message_count, created_at, updated_at FROM chats WHERE id = ? AND user_key = ? AND COALESCE(deleted, FALSE) = FALSE",
                    [chat_id, user_key],
                ).fetchone()
                if not row:
                    return False
                record = self._chat_record(row)
                if title is not None:
                    record["title"] = (title or "").strip() or record["title"]
                if is_pinned is not None:
                    record["is_pinned"] = bool(is_pinned)
                if model is not None:
                    record["model"] = model
                if effort is not None:
                    record["effort"] = effort
                if move_to_project:
                    target = project_id or None
                    if target and not self._project_owned(conn, target, user_key):
                        raise ValueError("Project not found for this user")
                    record["project_id"] = target
                record["updated_at"] = time.time()
                conn.execute(
                    "UPDATE chats SET project_id = ?, title = ?, model = ?, effort = ?, is_pinned = ?, updated_at = ? WHERE id = ? AND user_key = ?",
                    [record["project_id"], record["title"], record["model"], record["effort"], record["is_pinned"], record["updated_at"], chat_id, user_key],
                )
                self._enqueue(conn, "chats", self._cloud_row("chats", record, user_key))
                return True
            finally:
                conn.close()

    def _tombstone_chat(self, conn, chat_id: str, user_key: str, now: float) -> None:
        row = conn.execute(
            "SELECT id, project_id, title, model, effort, is_pinned, message_count, created_at FROM chats WHERE id = ? AND user_key = ?",
            [chat_id, user_key],
        ).fetchone()
        conn.execute("DELETE FROM messages WHERE chat_id = ?", [chat_id])
        conn.execute("DELETE FROM attachments WHERE chat_id = ?", [chat_id])
        conn.execute("DELETE FROM chats WHERE id = ?", [chat_id])
        if row:
            record = {
                "id": row[0], "project_id": row[1], "title": row[2], "model": row[3], "effort": row[4],
                "is_pinned": bool(row[5]), "message_count": row[6], "created_at": row[7], "updated_at": now,
            }
            self._enqueue(conn, "chats", self._cloud_row("chats", record, user_key, deleted=True))

    def delete_chat(self, chat_id: str, user_key: str) -> bool:
        with self._write_lock:
            conn = self._get_connection()
            try:
                exists = conn.execute("SELECT 1 FROM chats WHERE id = ? AND user_key = ?", [chat_id, user_key]).fetchone()
                if not exists:
                    return False
                self._tombstone_chat(conn, chat_id, user_key, time.time())
                return True
            finally:
                conn.close()

    # -------------------------------------------------------------------------
    # MESSAGES
    # -------------------------------------------------------------------------
    @staticmethod
    def _message_dict(row) -> Dict[str, Any]:
        try:
            routing_math = json.loads(row[8]) if row[8] else None
        except Exception:
            routing_math = None
        record = {
            "id": row[0], "chat_id": row[1], "role": row[2], "content": row[3],
            "model_routed": row[4], "model_executed": row[5], "duration_ms": row[6],
            "routing_math": routing_math, "created_at": row[7], "content_type": row[9] or "markdown",
        }
        metadata = row[10]
        if metadata:
            try:
                extra = json.loads(metadata) if isinstance(metadata, str) else metadata
                if isinstance(extra, dict):
                    record.update({k: v for k, v in extra.items() if k not in record})
            except Exception:
                pass
        return record

    def get_messages(self, chat_id: str, user_key: str) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            rows = conn.execute(
                """
                SELECT id, chat_id, role, content, model_routed, model_executed, duration_ms, created_at, routing_math, content_type, metadata
                FROM messages WHERE chat_id = ? AND user_key = ? AND COALESCE(deleted, FALSE) = FALSE
                ORDER BY created_at ASC
                """,
                [chat_id, user_key],
            ).fetchall()
            return [self._message_dict(r) for r in rows]
        finally:
            conn.close()

    def save_message(
        self,
        chat_id: str,
        role: str,
        content: str,
        model_routed: Optional[str] = None,
        model_executed: Optional[str] = None,
        duration_ms: float = 0.0,
        routing_math: Optional[Dict[str, Any]] = None,
        user_key: str = "",
        content_type: str = "markdown",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        chat = self.get_chat(chat_id, user_key)
        if not chat:
            raise ValueError("Chat not found for this user")
        m_id = f"msg_{uuid.uuid4().hex[:10]}"
        now = time.time()
        extra = {k: v for k, v in (metadata or {}).items() if k in MESSAGE_METADATA_FIELDS and v}
        record = {
            "id": m_id, "chat_id": chat_id, "role": role, "content": content,
            "model_routed": model_routed, "model_executed": model_executed,
            "duration_ms": float(duration_ms or 0.0), "routing_math": routing_math,
            "created_at": now, "content_type": content_type,
        }
        with self._write_lock:
            conn = self._get_connection()
            try:
                conn.execute(
                    "INSERT INTO messages (id, chat_id, role, content, model_routed, model_executed, duration_ms, routing_math, created_at, user_key, content_type, metadata, deleted) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, FALSE)",
                    [m_id, chat_id, role, content, model_routed, model_executed, record["duration_ms"], json.dumps(routing_math) if routing_math else None, now, user_key, content_type, json.dumps(extra) if extra else None],
                )
                count = int(conn.execute("SELECT COUNT(*) FROM messages WHERE chat_id = ?", [chat_id]).fetchone()[0])
                title = chat["title"]
                if role == "user" and (title.startswith("New AI Chat") or int(chat.get("message_count") or 0) == 0):
                    title = (content or "").strip().split("\n")[0][:45] or title
                conn.execute(
                    "UPDATE chats SET title = ?, updated_at = ?, message_count = ? WHERE id = ? AND user_key = ?",
                    [title, now, count, chat_id, user_key],
                )
                updated_chat = dict(chat)
                updated_chat.update({"title": title, "updated_at": now, "message_count": count})
                self._enqueue(conn, "messages", self._cloud_row("messages", {**record, **extra}, user_key))
                self._enqueue(conn, "chats", self._cloud_row("chats", updated_chat, user_key))
                return {**record, **extra, "chat_title": title}
            finally:
                conn.close()

    # -------------------------------------------------------------------------
    # ATTACHMENTS
    # -------------------------------------------------------------------------
    def add_attachment(self, chat_id: str, user_key: str, name: str, mime_type: str, data_base64: str, kind: str = "image", message_id: Optional[str] = None) -> Dict[str, Any]:
        chat = self.get_chat(chat_id, user_key)
        if not chat:
            raise ValueError("Chat not found for this user")
        raw_size = len(data_base64 or "")
        if not raw_size:
            raise ValueError("Attachment is empty")
        if raw_size > ATTACHMENT_MAX_BYTES:
            raise ValueError(f"Attachment too large ({raw_size} bytes); limit is {ATTACHMENT_MAX_BYTES} bytes")
        a_id = f"att_{uuid.uuid4().hex[:10]}"
        now = time.time()
        record = {
            "id": a_id, "chat_id": chat_id, "message_id": message_id, "kind": kind,
            "name": (name or "attachment")[:200], "mime_type": mime_type or "application/octet-stream",
            "size_bytes": raw_size, "data": data_base64, "created_at": now,
        }
        with self._write_lock:
            conn = self._get_connection()
            try:
                conn.execute(
                    "INSERT INTO attachments (id, chat_id, message_id, user_key, kind, name, mime_type, size_bytes, data, created_at, deleted) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, FALSE)",
                    [a_id, chat_id, message_id, user_key, kind, record["name"], record["mime_type"], raw_size, data_base64, now],
                )
                self._enqueue(conn, "attachments", self._cloud_row("attachments", record, user_key))
            finally:
                conn.close()
        return {
            "id": a_id, "chat_id": chat_id, "kind": kind, "name": record["name"],
            "mime_type": record["mime_type"], "size_bytes": raw_size, "created_at": now,
            "url": f"/api/ai/history/attachments/{a_id}",
        }

    def get_attachment(self, attachment_id: str, user_key: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            row = conn.execute(
                "SELECT id, chat_id, kind, name, mime_type, data FROM attachments WHERE id = ? AND user_key = ? AND COALESCE(deleted, FALSE) = FALSE",
                [attachment_id, user_key],
            ).fetchone()
            if not row:
                return None
            return {"id": row[0], "chat_id": row[1], "kind": row[2], "name": row[3], "mime_type": row[4], "data": row[5]}
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # BIGQUERY SYNC & RESTORE
    # -------------------------------------------------------------------------
    def _cloud_status(self) -> Dict[str, Any]:
        cached_at, cached = self._cloud_status_cache
        if cached and time.time() - cached_at < 15:
            return cached
        try:
            status = chat_bigquery.status()
        except Exception as exc:
            status = {"configured": False, "error": str(exc)[:300]}
        self._cloud_status_cache = (time.time(), status)
        return status

    def _state_get(self, conn, key: str) -> Optional[str]:
        try:
            row = conn.execute("SELECT value FROM sync_state WHERE key = ?", [key]).fetchone()
            return row[0] if row else None
        except Exception:
            return None

    def _state_set(self, conn, key: str, value: str) -> None:
        try:
            conn.execute("INSERT OR REPLACE INTO sync_state (key, value) VALUES (?, ?)", [key, value])
        except Exception:
            pass

    def _pending_count(self, conn, user_key: Optional[str] = None) -> int:
        try:
            if user_key is None:
                return int(conn.execute("SELECT COUNT(*) FROM bq_outbox WHERE synced_at IS NULL").fetchone()[0])
            return int(
                conn.execute(
                    "SELECT COUNT(*) FROM bq_outbox WHERE synced_at IS NULL AND user_key = ?",
                    [user_key],
                ).fetchone()[0]
            )
        except Exception:
            return 0

    def _flush_once(self, max_rows: int = 300) -> Dict[str, Any]:
        result = {"synced": 0, "pending": 0, "error": ""}
        with self._write_lock:
            conn = self._get_connection()
            try:
                rows = conn.execute(
                    "SELECT seq, entity, payload FROM bq_outbox WHERE synced_at IS NULL ORDER BY seq LIMIT ?",
                    [max_rows],
                ).fetchall()
                if not rows:
                    result["pending"] = self._pending_count(conn)
                    return result
                grouped: Dict[str, List[Dict[str, Any]]] = {}
                seqs: Dict[str, List[int]] = {}
                for seq, entity, payload in rows:
                    try:
                        grouped.setdefault(entity, []).append(json.loads(payload))
                        seqs.setdefault(entity, []).append(int(seq))
                    except Exception:
                        conn.execute("UPDATE bq_outbox SET synced_at = ?, last_error = 'invalid payload' WHERE seq = ?", [time.time(), int(seq)])
                for entity, payloads in grouped.items():
                    placeholders = ",".join("?" for _ in seqs[entity])
                    try:
                        chat_bigquery.load_rows(entity, payloads)
                        conn.execute(
                            f"UPDATE bq_outbox SET synced_at = ?, last_error = NULL WHERE seq IN ({placeholders})",
                            [time.time()] + seqs[entity],
                        )
                        result["synced"] += len(payloads)
                        self._state_set(conn, "last_sync_at", json.dumps(time.time()))
                        self._state_set(conn, "last_error", json.dumps(""))
                    except Exception as exc:
                        message = str(exc)[:400]
                        result["error"] = message
                        conn.execute(
                            f"UPDATE bq_outbox SET attempts = attempts + 1, last_error = ? WHERE seq IN ({placeholders})",
                            [message] + seqs[entity],
                        )
                        self._state_set(conn, "last_error", json.dumps(message))
                result["pending"] = self._pending_count(conn)
                return result
            finally:
                conn.close()

    def _sync_worker(self) -> None:
        while True:
            try:
                self._flush_wakeup.wait(timeout=25)
                self._flush_wakeup.clear()
                self._flush_once()
            except Exception:
                time.sleep(5)

    def sync_now(self, loops: int = 6) -> Dict[str, Any]:
        total = {"synced": 0, "pending": 0, "error": "", "loops": 0}
        for _ in range(loops):
            result = self._flush_once()
            total["loops"] += 1
            total["synced"] += result["synced"]
            total["pending"] = result["pending"]
            total["error"] = result["error"]
            if result["synced"] == 0:
                break
        total.update(
            {
                "status": "success" if not total["error"] else "pending",
                "cloud": self._cloud_status(),
                "storage": "DuckDB (working set) + Google BigQuery (durable archive)",
            }
        )
        return total

    def sync_to_bigquery_archive(self, max_records: int = 25) -> Dict[str, Any]:
        result = self.sync_now(loops=4)
        result["synced_count"] = result.get("synced", 0)
        return result

    def _apply_cloud_rows(self, entity: str, rows: List[Dict[str, Any]], user_key: str) -> Dict[str, int]:
        stats = {"inserted": 0, "updated": 0, "deleted": 0}
        conn = self._get_connection()
        try:
            for row in rows:
                deleted = bool(row.get("deleted"))
                if entity == "projects":
                    pid = row.get("project_id")
                    if not pid:
                        continue
                    local = conn.execute("SELECT updated_at FROM projects WHERE id = ?", [pid]).fetchone()
                    if deleted:
                        if local:
                            conn.execute("DELETE FROM projects WHERE id = ?", [pid])
                            stats["deleted"] += 1
                    elif not local:
                        conn.execute(
                            "INSERT INTO projects (id, name, description, created_at, updated_at, user_key, deleted) VALUES (?, ?, ?, ?, ?, ?, FALSE)",
                            [pid, row.get("name"), row.get("description"), row.get("created_at"), row.get("updated_at"), user_key],
                        )
                        stats["inserted"] += 1
                    elif float(row.get("updated_at") or 0) > float(local[0] or 0):
                        conn.execute(
                            "UPDATE projects SET name = ?, description = ?, updated_at = ? WHERE id = ?",
                            [row.get("name"), row.get("description"), row.get("updated_at"), pid],
                        )
                        stats["updated"] += 1
                elif entity == "chats":
                    cid = row.get("chat_id")
                    if not cid:
                        continue
                    local = conn.execute("SELECT updated_at FROM chats WHERE id = ?", [cid]).fetchone()
                    if deleted:
                        if local:
                            conn.execute("DELETE FROM messages WHERE chat_id = ?", [cid])
                            conn.execute("DELETE FROM attachments WHERE chat_id = ?", [cid])
                            conn.execute("DELETE FROM chats WHERE id = ?", [cid])
                            stats["deleted"] += 1
                    elif not local:
                        conn.execute(
                            "INSERT INTO chats (id, project_id, title, model, effort, is_pinned, message_count, created_at, updated_at, user_key, deleted) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, FALSE)",
                            [cid, row.get("project_id"), row.get("title") or "AI Session", row.get("model") or "auto", row.get("effort") or "default", bool(row.get("is_pinned")), int(row.get("message_count") or 0), row.get("created_at"), row.get("updated_at"), user_key],
                        )
                        stats["inserted"] += 1
                    elif float(row.get("updated_at") or 0) > float(local[0] or 0):
                        conn.execute(
                            "UPDATE chats SET project_id = ?, title = ?, model = ?, effort = ?, is_pinned = ?, message_count = ?, updated_at = ? WHERE id = ?",
                            [row.get("project_id"), row.get("title"), row.get("model"), row.get("effort"), bool(row.get("is_pinned")), int(row.get("message_count") or 0), row.get("updated_at"), cid],
                        )
                        stats["updated"] += 1
                elif entity == "messages":
                    mid = row.get("message_id")
                    if not mid:
                        continue
                    if deleted:
                        conn.execute("DELETE FROM messages WHERE id = ?", [mid])
                        stats["deleted"] += 1
                        continue
                    exists = conn.execute("SELECT 1 FROM messages WHERE id = ?", [mid]).fetchone()
                    if not exists:
                        metadata = row.get("metadata")
                        if not metadata:
                            extras = {k: row.get(k) for k in ("model_name", "lab_name", "flag", "country") if row.get(k)}
                            metadata = json.dumps(extras) if extras else None
                        conn.execute(
                            "INSERT INTO messages (id, chat_id, role, content, model_routed, model_executed, duration_ms, routing_math, created_at, user_key, content_type, metadata, deleted) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, FALSE)",
                            [mid, row.get("chat_id"), row.get("role") or "user", row.get("content") or "", row.get("model_routed"), row.get("model_executed"), float(row.get("duration_ms") or 0), row.get("routing_math"), row.get("created_at"), user_key, row.get("content_type") or "markdown", metadata],
                        )
                        stats["inserted"] += 1
                else:
                    aid = row.get("attachment_id")
                    if not aid:
                        continue
                    if deleted:
                        conn.execute("DELETE FROM attachments WHERE id = ?", [aid])
                        stats["deleted"] += 1
                        continue
                    exists = conn.execute("SELECT 1 FROM attachments WHERE id = ?", [aid]).fetchone()
                    if not exists:
                        conn.execute(
                            "INSERT INTO attachments (id, chat_id, message_id, user_key, kind, name, mime_type, size_bytes, data, created_at, deleted) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, FALSE)",
                            [aid, row.get("chat_id"), row.get("message_id"), user_key, row.get("kind"), row.get("name"), row.get("mime_type"), int(row.get("size_bytes") or 0), row.get("data"), row.get("created_at")],
                        )
                        stats["inserted"] += 1
            if stats["inserted"] or stats["updated"] or stats["deleted"]:
                conn.execute(
                    "UPDATE chats SET message_count = (SELECT COUNT(*) FROM messages m WHERE m.chat_id = chats.id AND COALESCE(m.deleted, FALSE) = FALSE) WHERE user_key = ?",
                    [user_key],
                )
            return stats
        finally:
            conn.close()

    def _restore_worker(self, user_key: str, event: threading.Event) -> None:
        result: Dict[str, Any] = {"status": "failed", "user": user_fingerprint(user_key), "counts": {}, "error": "", "finished_at": None}
        try:
            chat_bigquery.ensure_schema()
            counts: Dict[str, Dict[str, int]] = {}
            for entity in ("projects", "chats", "messages", "attachments"):
                rows = chat_bigquery.fetch_rows(entity, user_key)
                counts[entity] = self._apply_cloud_rows(entity, rows, user_key)
            result.update({"status": "ok", "counts": counts, "finished_at": time.time()})
        except Exception as exc:
            result.update({"status": "failed", "error": str(exc)[:400], "finished_at": time.time()})
        with self._restore_lock:
            self._restore_results[user_key] = result
        event.set()

    def restore_user(self, user_key: str, wait_seconds: float = 8.0) -> Dict[str, Any]:
        """Rebuilds this user's chats from BigQuery once per process."""
        event = self._restore_events.get(user_key)
        if event is None:
            event = threading.Event()
            self._restore_events[user_key] = event
            threading.Thread(target=self._restore_worker, args=(user_key, event), daemon=True, name="chat-history-restore").start()
        event.wait(timeout=max(0.0, wait_seconds))
        if not event.is_set():
            return {"status": "pending", "user": user_fingerprint(user_key)}
        return self._restore_results.get(user_key, {"status": "pending", "user": user_fingerprint(user_key)})

    def storage_status(self, user_key: str) -> Dict[str, Any]:
        conn = self._get_connection()
        try:
            pending = self._pending_count(conn, user_key)
            last_sync_raw = self._state_get(conn, "last_sync_at")
            last_error_raw = self._state_get(conn, "last_error")
            local = {"chats": 0, "messages": 0, "attachments": 0}
            try:
                local["chats"] = int(conn.execute("SELECT COUNT(*) FROM chats WHERE user_key = ? AND COALESCE(deleted, FALSE) = FALSE", [user_key]).fetchone()[0])
                local["messages"] = int(conn.execute("SELECT COUNT(*) FROM messages WHERE user_key = ? AND COALESCE(deleted, FALSE) = FALSE", [user_key]).fetchone()[0])
                local["attachments"] = int(conn.execute("SELECT COUNT(*) FROM attachments WHERE user_key = ? AND COALESCE(deleted, FALSE) = FALSE", [user_key]).fetchone()[0])
            except Exception:
                pass
        finally:
            conn.close()
        try:
            last_sync = float(json.loads(last_sync_raw)) if last_sync_raw else None
        except Exception:
            last_sync = None
        try:
            last_error = json.loads(last_error_raw) if last_error_raw else ""
        except Exception:
            last_error = str(last_error_raw or "")
        restore = self._restore_results.get(user_key, {})
        return {
            "engine": "DuckDB (working set) + Google BigQuery (durable archive)",
            "user": user_fingerprint(user_key),
            "local": local,
            "pending_sync_rows": pending,
            "last_sync_at": last_sync,
            "last_error": last_error,
            "restored": restore.get("status", "not_started"),
            "restore_counts": restore.get("counts", {}),
            "cloud": self._cloud_status(),
        }


global_ai_history = GlobalAIHistoryEngine()
