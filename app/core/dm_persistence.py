"""
Durable Data Modeling storage on the free Neon Postgres instance.

The Render container disk is ephemeral, so every restart or redeploy wipes the
workspace databases, attachments and the dm_* rows in the studio SQLite file.
This module keeps one compressed snapshot of both in POSTGRES_CLOUD_FREE
(Neon free tier, no expiry) and restores it when a fresh container boots.
"""

from __future__ import annotations

import atexit
import gzip
import hashlib
import io
import json
import os
import shutil
import sqlite3
import tarfile
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from app.core.database import db
from app.core.logger import log_event

DM_TABLES = (
    "dm_projects",
    "dm_workspaces",
    "dm_workspace_schemas",
    "dm_messages",
    "dm_runs",
    "dm_schedules",
    "dm_schedule_runs",
)
STATE_KIND = "dm_state"
FILES_KIND = "dm_files"
KEEP_SNAPSHOTS = 2
CONNECT_TIMEOUT = 10
SYNC_INTERVAL = max(2.0, float(os.environ.get("DM_SYNC_INTERVAL", "5")))
MAX_SNAPSHOT_BYTES = int(os.environ.get("DM_SNAPSHOT_MAX_BYTES", str(120 * 1024 * 1024)))
MAX_SNAPSHOT_FILES = 5000
SKIP_SUFFIXES = (".duckdb", ".duckdb.wal", "-wal", "-shm", "-journal", ".tmp", ".lock")
SKIP_DIRS = {"__pycache__", ".pytest_cache"}

_lock = threading.RLock()
_thread: Optional[threading.Thread] = None
_stop = threading.Event()
_last_signature: Optional[Tuple[Optional[str], Optional[str]]] = None
_state: Dict[str, Any] = {
    "enabled": False,
    "restored_state_rows": 0,
    "restored_files": 0,
    "last_sync_at": None,
    "last_sync_bytes": 0,
    "last_error": "",
}


def enabled() -> bool:
    flag = (os.environ.get("DM_PERSISTENCE") or "").strip().lower()
    if flag in ("0", "false", "off", "no"):
        return False
    if flag in ("1", "true", "on", "yes"):
        return True
    return bool(os.environ.get("RENDER"))


def _modeling_dir() -> Path:
    from app.core import data_modeling_ai as dm

    return dm.MODELING_DIR


def _connect():
    import psycopg2
    from urllib.parse import urlparse

    from app.core.connection_manager import POSTGRES_CONFIGS

    defaults = POSTGRES_CONFIGS.get("POSTGRES_CLOUD_FREE", {})
    host = str(defaults.get("hostname") or "")
    port = int(defaults.get("port") or 5432)
    user = str(defaults.get("username") or "")
    dbname = str(defaults.get("database") or "neondb")
    sslmode = str(defaults.get("sslmode") or "require")
    password = os.environ.get("NEON_POSTGRES_PASSWORD", "")

    url = os.environ.get("NEON_DATABASE_URL", "")
    if url.startswith(("postgres://", "postgresql://")):
        parsed = urlparse(url)
        host = parsed.hostname or host
        port = parsed.port or port
        user = parsed.username or user
        password = parsed.password or password
        dbname = (parsed.path or "").lstrip("/") or dbname

    try:
        from app.core.connection_manager import connection_manager

        cfg = connection_manager.get_connection_config("POSTGRES_CLOUD_FREE", mask=False) or {}
        host = cfg.get("host") or host
        port = int(cfg.get("port") or port)
        user = cfg.get("username") or user
        dbname = cfg.get("database_name") or dbname
        password = cfg.get("secret_value") or password
    except Exception:
        pass

    if not (host and user and password):
        raise RuntimeError("Neon free Postgres credentials are not configured.")
    return psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname,
        sslmode=sslmode,
        connect_timeout=CONNECT_TIMEOUT,
    )


def _ensure_remote(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS dm_storage_snapshots ("
            " id BIGSERIAL PRIMARY KEY,"
            " kind TEXT NOT NULL,"
            " sha256 TEXT NOT NULL,"
            " size_bytes BIGINT NOT NULL,"
            " payload BYTEA NOT NULL,"
            " created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())"
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_dm_snapshots_kind"
            " ON dm_storage_snapshots(kind, id DESC)"
        )
    conn.commit()


# ---------------------------------------------------------------------------
# state (dm_* tables)
# ---------------------------------------------------------------------------

def _state_signature() -> Optional[str]:
    from app.core import data_modeling_ai as dm

    dm._ensure_schema()
    parts = []
    with db.get_connection() as conn:
        for table in DM_TABLES:
            count, max_rowid = conn.execute(
                f"SELECT COUNT(*), COALESCE(MAX(rowid), 0) FROM {table}"
            ).fetchone()
            stamp = ""
            if table in ("dm_workspaces", "dm_projects"):
                stamp = conn.execute(f"SELECT COALESCE(MAX(updated_at), '') FROM {table}").fetchone()[0] or ""
            parts.append(f"{table}:{count}:{max_rowid}:{stamp}")
    return "|".join(parts)


def _export_state() -> bytes:
    from app.core import data_modeling_ai as dm

    dm._ensure_schema()
    payload: Dict[str, Any] = {}
    with db.get_connection() as conn:
        for table in DM_TABLES:
            payload[table] = [dict(row) for row in conn.execute(f"SELECT * FROM {table}").fetchall()]
    # Upload even an empty payload: otherwise deleting the last workspace never
    # reaches Neon and the previous snapshot resurrects it on the next boot.
    return gzip.compress(json.dumps(payload, ensure_ascii=False).encode("utf-8"), 6)


def _restore_state(blob: bytes) -> int:
    data = json.loads(gzip.decompress(blob).decode("utf-8"))
    from app.core import data_modeling_ai as dm

    dm._ensure_schema()
    restored = 0
    with db.get_connection() as conn:
        if conn.execute("SELECT COUNT(*) FROM dm_workspaces").fetchone()[0]:
            return 0
        for table in DM_TABLES:
            for row in data.get(table) or []:
                cols = list(row.keys())
                if not cols:
                    continue
                sql = f"INSERT OR REPLACE INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})"
                conn.execute(sql, [row[c] for c in cols])
                restored += 1
        conn.commit()
    return restored


# ---------------------------------------------------------------------------
# files (data/modeling)
# ---------------------------------------------------------------------------

def _skip_file(path: Path) -> bool:
    name = path.name.lower()
    if name in SKIP_DIRS or any(name.endswith(suffix) for suffix in SKIP_SUFFIXES):
        return True
    return any(part in SKIP_DIRS for part in path.parts)


def _files_signature() -> Optional[str]:
    root = _modeling_dir()
    if not root.exists():
        return None
    items = []
    checked = 0
    for path in sorted(root.rglob("*")):
        checked += 1
        if checked > MAX_SNAPSHOT_FILES:
            break
        if not path.is_file() or _skip_file(path):
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        items.append(f"{path.relative_to(root).as_posix()}:{stat.st_size}:{int(stat.st_mtime)}")
    return hashlib.sha256("\n".join(items).encode("utf-8")).hexdigest()


def _sqlite_backup(source: Path, target: Path) -> None:
    src = sqlite3.connect(str(source), timeout=15.0)
    try:
        dest = sqlite3.connect(str(target))
        try:
            src.backup(dest)
        finally:
            dest.close()
    finally:
        src.close()


def _workspace_files_present() -> bool:
    root = _modeling_dir()
    return root.exists() and any(root.glob("ws_*.db"))


def _export_files() -> Optional[bytes]:
    root = _modeling_dir()
    if not root.exists():
        return None
    tmpdir = Path(tempfile.mkdtemp(prefix="dm_snapshot_"))
    buffer = tempfile.SpooledTemporaryFile(max_size=32 * 1024 * 1024)
    try:
        with tarfile.open(fileobj=buffer, mode="w:gz", compresslevel=6) as tar:
            index = 0
            for path in sorted(root.rglob("*")):
                if not path.is_file() or _skip_file(path):
                    continue
                rel = path.relative_to(root).as_posix()
                if path.suffix.lower() == ".db":
                    index += 1
                    copy = tmpdir / f"{index}.db"
                    try:
                        _sqlite_backup(path, copy)
                    except Exception as exc:
                        log_event(
                            f"DM snapshot skipped busy file {rel}: {exc}",
                            level="WARNING",
                            component="DMPersistence",
                        )
                        continue
                    tar.add(str(copy), arcname=rel)
                else:
                    tar.add(str(path), arcname=rel)
                if tar.offset > MAX_SNAPSHOT_BYTES:
                    log_event(
                        "DM snapshot exceeds size budget; stopping at the current file",
                        level="WARNING",
                        component="DMPersistence",
                    )
                    break
        buffer.seek(0)
        return buffer.read()
    finally:
        buffer.close()
        shutil.rmtree(tmpdir, ignore_errors=True)


def _restore_files(blob: bytes) -> int:
    root = _modeling_dir()
    root.mkdir(parents=True, exist_ok=True)
    extracted = 0
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            name = Path(member.name)
            if name.is_absolute() or ".." in name.parts:
                continue
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            source = tar.extractfile(member)
            if source is None:
                continue
            with open(target, "wb") as handle:
                shutil.copyfileobj(source, handle)
            extracted += 1
    return extracted


# ---------------------------------------------------------------------------
# remote snapshot I/O
# ---------------------------------------------------------------------------

def _latest_snapshot(conn, kind: str):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT payload FROM dm_storage_snapshots WHERE kind = %s ORDER BY id DESC LIMIT 1",
            (kind,),
        )
        row = cur.fetchone()
    return row[0] if row else None


def _upload(conn, kind: str, blob: bytes) -> bool:
    import psycopg2

    if not blob:
        return False
    if len(blob) > MAX_SNAPSHOT_BYTES:
        _state["last_error"] = f"{kind} snapshot is {len(blob)} bytes, above the configured budget"
        log_event(f"DM {kind} snapshot too large: {len(blob)} bytes", level="WARNING", component="DMPersistence")
        return False
    digest = hashlib.sha256(blob).hexdigest()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT sha256 FROM dm_storage_snapshots WHERE kind = %s ORDER BY id DESC LIMIT 1",
            (kind,),
        )
        row = cur.fetchone()
        if row and row[0] == digest:
            return False
        cur.execute(
            "INSERT INTO dm_storage_snapshots (kind, sha256, size_bytes, payload)"
            " VALUES (%s, %s, %s, %s)",
            (kind, digest, len(blob), psycopg2.Binary(blob)),
        )
        cur.execute(
            "DELETE FROM dm_storage_snapshots WHERE kind = %s AND id NOT IN ("
            " SELECT id FROM dm_storage_snapshots WHERE kind = %s ORDER BY id DESC LIMIT %s)",
            (kind, kind, KEEP_SNAPSHOTS),
        )
    conn.commit()
    return True


def snapshot_now() -> Dict[str, Any]:
    if not enabled():
        return {"status": "disabled"}
    with _lock:
        conn = None
        try:
            files = _export_files()
            state_blob = _export_state()
            conn = _connect()
            _ensure_remote(conn)
            files_uploaded = _upload(conn, FILES_KIND, files) if files else False
            state_uploaded = _upload(conn, STATE_KIND, state_blob) if state_blob else False
            total = len(files or b"") + len(state_blob or b"")
            _state.update(
                last_sync_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                last_sync_bytes=total,
                last_error="",
            )
            return {
                "status": "ok",
                "files_uploaded": files_uploaded,
                "state_uploaded": state_uploaded,
                "bytes": total,
            }
        except Exception as exc:
            _state["last_error"] = str(exc)[:300]
            log_event(f"DM snapshot upload failed: {exc}", level="WARNING", component="DMPersistence")
            return {"status": "error", "message": str(exc)[:300]}
        finally:
            if conn is not None:
                conn.close()


# ---------------------------------------------------------------------------
# boot restore + background sync
# ---------------------------------------------------------------------------

def restore() -> Dict[str, Any]:
    if not enabled():
        return {"status": "disabled"}
    conn = None
    try:
        conn = _connect()
        _ensure_remote(conn)
        state_blob = _latest_snapshot(conn, STATE_KIND)
        files_blob = _latest_snapshot(conn, FILES_KIND)
        restored_rows = 0
        restored_files = 0
        if state_blob:
            restored_rows = _restore_state(state_blob)
        if restored_rows and files_blob and not _workspace_files_present():
            restored_files = _restore_files(files_blob)
        _state.update(
            restored_state_rows=restored_rows,
            restored_files=restored_files,
            last_error="",
        )
        if restored_rows or restored_files:
            log_event(
                f"DM storage restored from Neon: {restored_rows} row(s), {restored_files} file(s)",
                component="DMPersistence",
            )
        return {"status": "ok", "rows": restored_rows, "files": restored_files}
    except Exception as exc:
        _state["last_error"] = str(exc)[:300]
        log_event(f"DM storage restore failed: {exc}", level="WARNING", component="DMPersistence")
        return {"status": "error", "message": str(exc)[:300]}
    finally:
        if conn is not None:
            conn.close()


def _loop() -> None:
    global _last_signature
    while not _stop.is_set():
        try:
            signature = (_state_signature(), _files_signature())
            if signature != _last_signature:
                _stop.wait(SYNC_INTERVAL)
                settled = (_state_signature(), _files_signature())
                if settled != signature:
                    _last_signature = settled
                    continue
                snapshot_now()
                _last_signature = settled
        except Exception as exc:
            _state["last_error"] = str(exc)[:300]
            log_event(f"DM persistence sync error: {exc}", level="WARNING", component="DMPersistence")
        _stop.wait(SYNC_INTERVAL)


def init() -> Dict[str, Any]:
    global _thread, _last_signature
    if not enabled():
        return {"status": "disabled"}
    _state["enabled"] = True
    result = restore()
    _last_signature = (_state_signature(), _files_signature())
    if _thread is None or not _thread.is_alive():
        _stop.clear()
        _thread = threading.Thread(target=_loop, daemon=True, name="DMPersistence")
        _thread.start()
    return result


def flush() -> None:
    if not enabled():
        return
    try:
        snapshot_now()
    except Exception as exc:
        log_event(f"DM persistence flush failed: {exc}", level="WARNING", component="DMPersistence")


def status() -> Dict[str, Any]:
    return {
        "enabled": enabled(),
        "running": bool(_thread and _thread.is_alive()),
        "initialized": bool(_state.get("enabled")),
        "last_sync_at": _state.get("last_sync_at"),
        "last_sync_bytes": _state.get("last_sync_bytes"),
        "last_error": _state.get("last_error") or "",
        "restored_state_rows": _state.get("restored_state_rows"),
        "restored_files": _state.get("restored_files"),
    }


atexit.register(flush)
