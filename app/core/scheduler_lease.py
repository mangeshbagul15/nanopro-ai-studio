"""Shared scheduler lease so only one host executes scheduled work.

The laptop tunnel and the Render service share the same Neon database. Without
a lease both run BOD/SOD/EOD and discovery jobs, duplicating emails and
bandwidth.

Leases are separate per lane because the two hosts run different task sets: the
cloud host executes only cloud-safe jobs (pipeline tasks are disabled there),
while the laptop owns BOD/SOD/T1/EOD. A single shared lease let the cloud hold
leadership forever and starve the pipeline lane, so the automation scheduler
asks for the lease matching its own profile. Discovery and other host-agnostic
work use the "shared" lease, which keeps exactly one host sending each summary.
"""

import os
import socket
import threading
import time

from app.core.logger import log_event

TTL_SECONDS = int(os.environ.get("NANOPRO_LEASE_TTL_SECONDS", "180"))
CACHE_SECONDS = 20.0
# "shared" keeps a single discovery sender across hosts; the lane rows let the
# laptop own pipeline work while the cloud keeps its own cloud-safe jobs.
LEASE_ROWS = {"shared": 1, "cloud": 2, "local": 3}

_lock = threading.Lock()
_cache = {
    scope: {"leader": True, "checked": 0.0, "holder": ""} for scope in LEASE_ROWS
}


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


def _acquire_remote(holder: str, row_id: int) -> bool:
    from app.core import dm_persistence

    conn = dm_persistence._connect()
    try:
        with conn.cursor() as cur:
            _ensure_table(cur)
            cur.execute(
                "INSERT INTO nanopro_scheduler_leader (id, holder, heartbeat)"
                " VALUES (%s, %s, now())"
                " ON CONFLICT (id) DO UPDATE SET holder = EXCLUDED.holder, heartbeat = now()"
                " WHERE nanopro_scheduler_leader.holder = EXCLUDED.holder"
                " OR nanopro_scheduler_leader.heartbeat < now() - (%s || ' seconds')::interval"
                " RETURNING holder",
                (row_id, holder, TTL_SECONDS),
            )
            row = cur.fetchone()
        conn.commit()
        return bool(row and row[0] == holder)
    finally:
        conn.close()


def is_leader(scope: str = "shared") -> bool:
    """True when this host owns the lease for that lane (fail-open on DB errors)."""
    row_id = LEASE_ROWS.get(scope, LEASE_ROWS["shared"])
    now = time.monotonic()
    state = _cache.setdefault(scope, {"leader": True, "checked": 0.0, "holder": ""})
    with _lock:
        if now - state["checked"] < CACHE_SECONDS:
            return state["leader"]
    holder = node_id()
    try:
        leader = _acquire_remote(holder, row_id)
    except Exception as exc:
        leader = True
        if now - state["checked"] > 600:
            log_event(f"Scheduler lease unavailable ({exc}); running locally.", level="WARNING", component="SchedulerLease")
    with _lock:
        changed = leader != state["leader"] or holder != state["holder"]
        state.update(leader=leader, checked=now, holder=holder)
    if changed:
        log_event(
            f"Scheduler lease [{scope}]: node '{holder}' is {'LEADER' if leader else 'STANDBY'}.",
            component="SchedulerLease",
        )
    return leader
