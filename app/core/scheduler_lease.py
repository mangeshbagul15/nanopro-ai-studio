"""Shared scheduler lease so only one host executes scheduled work.

The laptop tunnel and the Render service share the same Neon database. Without
a lease both run BOD/SOD/EOD and discovery jobs, duplicating emails and
bandwidth. Render normally wins; if it stops heartbeating the laptop takes over.
"""

import os
import socket
import threading
import time

from app.core.logger import log_event

TTL_SECONDS = int(os.environ.get("NANOPRO_LEASE_TTL_SECONDS", "180"))
CACHE_SECONDS = 20.0

_lock = threading.Lock()
_cache = {"leader": True, "checked": 0.0, "holder": ""}


def node_id() -> str:
    explicit = os.environ.get("NANOPRO_NODE_ID", "").strip()
    if explicit:
        return explicit
    if os.environ.get("RENDER"):
        return "render"
    return socket.gethostname() or "laptop"


def _ensure_table(cur) -> None:
    cur.execute(
        "CREATE TABLE IF NOT EXISTS nanopro_scheduler_leader ("
        " id INT PRIMARY KEY, holder TEXT NOT NULL,"
        " heartbeat TIMESTAMPTZ NOT NULL DEFAULT now())"
    )


def _acquire_remote(holder: str) -> bool:
    from app.core import dm_persistence

    conn = dm_persistence._connect()
    try:
        with conn.cursor() as cur:
            _ensure_table(cur)
            cur.execute(
                "INSERT INTO nanopro_scheduler_leader (id, holder, heartbeat)"
                " VALUES (1, %s, now())"
                " ON CONFLICT (id) DO UPDATE SET holder = EXCLUDED.holder, heartbeat = now()"
                " WHERE nanopro_scheduler_leader.holder = EXCLUDED.holder"
                " OR nanopro_scheduler_leader.heartbeat < now() - (%s || ' seconds')::interval"
                " RETURNING holder",
                (holder, TTL_SECONDS),
            )
            row = cur.fetchone()
        conn.commit()
        return bool(row and row[0] == holder)
    finally:
        conn.close()


def is_leader() -> bool:
    """True when this host currently owns the scheduler lease (fail-open on DB errors)."""
    now = time.monotonic()
    with _lock:
        if now - _cache["checked"] < CACHE_SECONDS:
            return _cache["leader"]
    holder = node_id()
    try:
        leader = _acquire_remote(holder)
    except Exception as exc:
        leader = True
        if now - _cache["checked"] > 600:
            log_event(f"Scheduler lease unavailable ({exc}); running locally.", level="WARNING", component="SchedulerLease")
    with _lock:
        changed = leader != _cache["leader"] or holder != _cache["holder"]
        _cache.update(leader=leader, checked=now, holder=holder)
    if changed:
        log_event(
            f"Scheduler lease: node '{holder}' is {'LEADER' if leader else 'STANDBY'}.",
            component="SchedulerLease",
        )
    return leader
