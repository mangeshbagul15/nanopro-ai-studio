"""Monthly outbound-byte guard for the free Render tier.

Render suspends services for the rest of the month when included bandwidth is
exceeded without a card on file. This module meters HTTP response bytes,
persists the counter locally and to Neon, and degrades the app before the cap
instead of letting one heavy user take the whole platform down.
"""

import json
import os
import threading
import time
from pathlib import Path

from starlette.responses import JSONResponse

STATE_PATH = Path("data/egress_state.json")
NEON_FLUSH_SECONDS = 60.0
RATE_LIMIT_PER_MINUTE = int(os.environ.get("NANOPRO_RATE_LIMIT_PER_MINUTE", "120"))


def _gb(value: float) -> int:
    return int(value * 1024 * 1024 * 1024)


SOFT_LIMIT = int(os.environ.get("NANOPRO_EGRESS_SOFT_BYTES", str(_gb(3.5))))
HARD_LIMIT = int(os.environ.get("NANOPRO_EGRESS_HARD_BYTES", str(_gb(4.4))))
MAX_UPLOAD_BYTES = int(os.environ.get("NANOPRO_MAX_UPLOAD_BYTES", str(25 * 1024 * 1024)))
MAX_BODY_SOFT = int(os.environ.get("NANOPRO_MAX_BODY_SOFT_BYTES", str(2 * 1024 * 1024)))

HARD_BLOCKED_PREFIXES = (
    "/api/video",
    "/api/sql_video",
    "/api/tech_video",
    "/api/apk",
    "/api/heygen",
    "/api/backup",
    "/api/books",
    "/api/reports",
    "/api/banking",
    "/api/data_analyst/report",
    "/api/lakehouse/dispatch",
    "/api/crypto/report",
    "/api/dms",
)

_lock = threading.Lock()
_state = {
    "month": "",
    "bytes": 0,
    "by_category": {},
    "dirty": False,
    "last_flush": 0.0,
    "soft_warned": False,
}
_rate = {}
_flusher_started = False


def _month_key() -> str:
    return time.strftime("%Y-%m")


def _load() -> None:
    try:
        if not STATE_PATH.exists():
            return
        data = json.loads(STATE_PATH.read_text(encoding="utf-8") or "{}")
        if data.get("month") == _month_key():
            _state["month"] = data["month"]
            _state["bytes"] = int(data.get("bytes") or 0)
            _state["by_category"] = dict(data.get("by_category") or {})
    except Exception:
        pass


def _write_local() -> None:
    try:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(
            json.dumps({
                "month": _state["month"],
                "bytes": _state["bytes"],
                "by_category": _state["by_category"],
            }),
            encoding="utf-8",
        )
    except Exception:
        pass


def _restore_from_neon() -> None:
    try:
        from app.core import dm_persistence

        conn = dm_persistence._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS nanopro_egress ("
                    " month TEXT PRIMARY KEY, bytes BIGINT NOT NULL DEFAULT 0,"
                    " by_category JSONB NOT NULL DEFAULT '{}'::jsonb,"
                    " updated_at TIMESTAMPTZ NOT NULL DEFAULT now())"
                )
                cur.execute("SELECT bytes, by_category FROM nanopro_egress WHERE month = %s", (_month_key(),))
                row = cur.fetchone()
                if row and int(row[0] or 0) > _state["bytes"]:
                    _state["bytes"] = int(row[0])
                    if isinstance(row[1], dict):
                        _state["by_category"] = row[1]
                    _write_local()
            conn.commit()
        finally:
            conn.close()
    except Exception:
        pass


def _flush_to_neon() -> None:
    try:
        from app.core import dm_persistence

        conn = dm_persistence._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS nanopro_egress ("
                    " month TEXT PRIMARY KEY, bytes BIGINT NOT NULL DEFAULT 0,"
                    " by_category JSONB NOT NULL DEFAULT '{}'::jsonb,"
                    " updated_at TIMESTAMPTZ NOT NULL DEFAULT now())"
                )
                cur.execute(
                    "INSERT INTO nanopro_egress (month, bytes, by_category, updated_at)"
                    " VALUES (%s, %s, %s::jsonb, now())"
                    " ON CONFLICT (month) DO UPDATE SET bytes = GREATEST(nanopro_egress.bytes, EXCLUDED.bytes),"
                    " by_category = EXCLUDED.by_category, updated_at = now()",
                    (_month_key(), _state["bytes"], json.dumps(_state["by_category"])),
                )
            conn.commit()
        finally:
            conn.close()
        _state["last_flush"] = time.monotonic()
        _state["dirty"] = False
    except Exception:
        pass


def _flusher_loop() -> None:
    while True:
        time.sleep(NEON_FLUSH_SECONDS)
        with _lock:
            dirty = _state["dirty"]
        if dirty:
            _flush_to_neon()


def _ensure_loaded() -> None:
    global _flusher_started
    with _lock:
        if _state["month"] == _month_key():
            return
        _state.update(month=_month_key(), bytes=0, by_category={}, dirty=False, soft_warned=False)
        _load()
        if not _state["by_category"]:
            _state["by_category"] = {}
    if not _flusher_started and (os.environ.get("RENDER") or os.environ.get("IS_CLOUD")):
        _flusher_started = True
        _restore_from_neon()
        threading.Thread(target=_flusher_loop, daemon=True, name="EgressFlusher").start()


def current_mode() -> str:
    _ensure_loaded()
    with _lock:
        used = _state["bytes"]
    if used >= HARD_LIMIT:
        return "hard"
    if used >= SOFT_LIMIT:
        return "soft"
    return "normal"


def record_egress(num_bytes: int, category: str = "http") -> None:
    if num_bytes <= 0:
        return
    _ensure_loaded()
    with _lock:
        _state["bytes"] += int(num_bytes)
        cats = _state["by_category"]
        cats[category] = int(cats.get(category, 0)) + int(num_bytes)
        _state["dirty"] = True
        now = time.monotonic()
        should_write = (now - _state["last_flush"]) > 10.0
        if should_write:
            _state["last_flush"] = now
    if should_write:
        _write_local()


def egress_status() -> dict:
    _ensure_loaded()
    with _lock:
        used = _state["bytes"]
        cats = dict(_state["by_category"])
    mode = current_mode()
    return {
        "month": _month_key(),
        "used_bytes": used,
        "used_gb": round(used / (1024 ** 3), 3),
        "limit_gb": 5.0,
        "remaining_gb": round(max(0, 5 * 1024 ** 3 - used) / (1024 ** 3), 3),
        "soft_limit_gb": round(SOFT_LIMIT / (1024 ** 3), 2),
        "hard_limit_gb": round(HARD_LIMIT / (1024 ** 3), 2),
        "mode": mode,
        "by_category": cats,
    }


_audit_day_marker = None


def egress_audit() -> dict:
    """Projects month-end usage from the app meter and grades the risk."""
    from datetime import datetime, timedelta, timezone

    status = egress_status()
    used = status["used_bytes"]
    now = datetime.now(timezone.utc)
    next_month = datetime(now.year + (1 if now.month == 12 else 0), (now.month % 12) + 1, 1)
    days_in_month = (next_month - timedelta(days=1)).day
    elapsed = max(now.day, 1)
    projected = int(used / elapsed * days_in_month)
    if projected >= HARD_LIMIT:
        verdict = "critical"
    elif projected >= SOFT_LIMIT:
        verdict = "risk"
    elif projected >= SOFT_LIMIT * 0.8:
        verdict = "watch"
    else:
        verdict = "ok"
    return {
        **status,
        "day_of_month": now.day,
        "days_in_month": days_in_month,
        "days_left": max(days_in_month - now.day, 0),
        "avg_per_day_gb": round(used / (1024 ** 3) / elapsed, 3),
        "projected_month_gb": round(projected / (1024 ** 3), 2),
        "verdict": verdict,
        "note": "App-side meter only; reconcile against the Render billing CSV (no Render API key is configured).",
    }


def egress_daily_check() -> None:
    """Logs one audit line per UTC day from whichever node holds the scheduler lease."""
    global _audit_day_marker
    from datetime import datetime, timezone

    from app.core.logger import log_event

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if _audit_day_marker == today:
        return
    _audit_day_marker = today
    audit = egress_audit()
    level = "WARNING" if audit["verdict"] in ("risk", "critical") else "INFO"
    log_event(
        f"Daily egress audit [{audit['month']}]: used={audit['used_gb']} GB, "
        f"avg/day={audit['avg_per_day_gb']} GB, projected={audit['projected_month_gb']} GB, "
        f"verdict={audit['verdict']}",
        level=level,
        component="EgressGuard",
    )


def _allow(client_ip: str) -> bool:
    if RATE_LIMIT_PER_MINUTE <= 0:
        return True
    now = time.time()
    window = int(now // 60)
    key = (client_ip or "unknown", window)
    with _lock:
        count = int(_rate.get(key, 0)) + 1
        _rate[key] = count
        if len(_rate) > 4096:
            for old in [k for k in _rate if k[1] < window - 2]:
                _rate.pop(old, None)
    return count <= RATE_LIMIT_PER_MINUTE


def _is_hard_blocked(path: str) -> bool:
    return any(path == p or path.startswith(p + "/") for p in HARD_BLOCKED_PREFIXES)


def _content_length(scope) -> int:
    for name, value in scope.get("headers", []):
        if name == b"content-length":
            try:
                return int(value)
            except ValueError:
                return 0
    return 0


class EgressGuardMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        path = scope.get("path", "")
        mode = current_mode()
        client = scope.get("client") or ("unknown", 0)

        if mode == "hard" and _is_hard_blocked(path):
            return await JSONResponse(
                status_code=429,
                content={
                    "status": "egress_budget_protected",
                    "mode": mode,
                    "message": "Monthly bandwidth is nearly exhausted. Heavy features are paused until next month to keep NanoPro online.",
                },
            )(scope, receive, send)

        size = _content_length(scope)
        if size > MAX_UPLOAD_BYTES or (mode != "normal" and size > MAX_BODY_SOFT):
            return await JSONResponse(
                status_code=413,
                content={
                    "status": "payload_too_large",
                    "mode": mode,
                    "message": "Upload rejected to protect the free bandwidth budget. Use the laptop lane for large files.",
                },
            )(scope, receive, send)

        if not _allow(client[0] if client else "unknown"):
            return await JSONResponse(
                status_code=429,
                content={"status": "rate_limited", "message": "Too many requests. Please slow down."},
            )(scope, receive, send)

        async def send_wrapper(message):
            if message["type"] == "http.response.body":
                body = message.get("body", b"")
                if body:
                    record_egress(len(body), "http")
            await send(message)

        await self.app(scope, receive, send_wrapper)
