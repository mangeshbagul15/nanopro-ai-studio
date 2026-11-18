"""Bank-style batch cycles on top of the BigQuery → AWS → Snowflake pipeline.

Four checkpoints run once per business date, each one refreshing the whole
lake (BigQuery export → S3/Glue/Iceberg → Snowflake L0/L1/L2 → DuckDB report)
and recording the outcome in ``BANK_DB.L2_CURATED.BATCH_CONTROL``:

* ``BOD`` 06:00 IST — beginning of day, full load validation
* ``SOD`` 08:00 IST — start of day, opening positions
* ``T1``  10:00 IST — T-1 delta reconciliation
* ``EOD`` 18:00 IST — end of day, marts and reconciliation

The scheduler wakes on the same tick loop as the hourly export. When a cycle is
due it runs the cycle instead of the plain export, so a tick never exports
twice. Cycles missed while the host was asleep are recorded as ``MISSED`` — the
ledger never claims a cycle ran when it did not.
"""
from __future__ import annotations

import os
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from app.core.logger import log_event

IST = timezone(timedelta(hours=5, minutes=30))

CYCLES: Dict[str, Dict[str, Any]] = {
    "BOD": {"label": "Beginning of Day", "at": (6, 0),
            "purpose": "Full load validation and opening balances"},
    "SOD": {"label": "Start of Day", "at": (8, 0),
            "purpose": "Open the business day and refresh limits"},
    "T1": {"label": "T-1 Delta", "at": (10, 0),
           "purpose": "Daily delta reconciliation against T-1"},
    "EOD": {"label": "End of Day", "at": (18, 0),
            "purpose": "Close the day: marts, reconciliation and summary"},
}
CYCLE_ORDER = ("BOD", "SOD", "T1", "EOD")

STATE: Dict[str, Any] = {"last_result": None, "history": []}
_DONE: set = set()          # {(business_date, cycle)} attempted in this process
_INFLIGHT = threading.Lock()
_LEDGER_TTL_S = 240.0
_HISTORY = {"at": 0.0, "date": "", "value": {}}


def _as_ist(now: Optional[datetime] = None) -> datetime:
    current = now or datetime.now(IST)
    if current.tzinfo is None:
        current = current.replace(tzinfo=IST)
    return current.astimezone(IST)


def business_date(now: Optional[datetime] = None) -> str:
    return _as_ist(now).date().isoformat()


def _at(cycle: str) -> tuple:
    """Scheduled (hour, minute) IST, honouring an Orchestrator override."""
    try:
        from app.core.pipeline_orchestrator import cycle_schedules

        override = cycle_schedules().get(cycle)
        if override:
            hour, minute = (int(part) for part in str(override).split(":"))
            return hour, minute
    except Exception:
        pass
    return CYCLES[cycle]["at"]


def _scheduled_minutes(cycle: str) -> int:
    hour, minute = _at(cycle)
    return hour * 60 + minute


def _scheduled_at(cycle: str, bdate: str) -> datetime:
    hour, minute = _at(cycle)
    day = datetime.fromisoformat(bdate).replace(tzinfo=IST)
    return day.replace(hour=hour, minute=minute)


def _snowflake_statuses(bdate: str) -> Dict[str, str]:
    """Latest ledger status per cycle for the business date (best effort)."""
    now = time.time()
    if _HISTORY["date"] == bdate and now - _HISTORY["at"] < _LEDGER_TTL_S:
        return dict(_HISTORY["value"])
    value: Dict[str, str] = {}
    try:
        from app.core.snowflake_lakehouse import batch_history

        for row in batch_history(bdate):
            cycle = str(row.get("cycle") or "").upper()
            if cycle:
                value[cycle] = str(row.get("status") or "").upper()
    except Exception as exc:
        log_event(f"[BatchCycles] ledger read failed: {exc}", level="WARNING", component="BatchCycles")
    _HISTORY.update({"at": now, "date": bdate, "value": value})
    return dict(value)


def _attempted(bdate: str) -> Dict[str, str]:
    done = _snowflake_statuses(bdate)
    for day, cycle in _DONE:
        if day == bdate:
            done.setdefault(cycle, "SUCCESS")
    return done


def _record(cycle: str, bdate: str, status: str, **kwargs: Any) -> Dict[str, Any]:
    try:
        from app.core.snowflake_lakehouse import record_batch

        result = record_batch(cycle, bdate, status, **kwargs)
        _HISTORY["at"] = 0.0  # force the next read to see this row
        return result
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:240]}


def _audit(cycle: str, status: str, details: Dict[str, Any]) -> None:
    try:
        from app.core.cron_gateway_router import _record_cron_run

        _record_cron_run(f"{cycle}_BATCH", status, details)
    except Exception:
        pass


def is_running() -> bool:
    return _INFLIGHT.locked()


def _deliver_report(cycle: str, bdate: str, status: str, details: Dict[str, Any]) -> None:
    """Build the outbound Excel report and notify; never breaks the cycle."""
    if (os.environ.get("NANOPRO_REPORT_DELIVERY") or "1").strip().lower() in ("0", "false", "no", "off"):
        return
    try:
        from app.core import report_delivery

        report_delivery.deliver(cycle=cycle, business_date=bdate, status=status,
                                details=details, async_send=True)
    except Exception as exc:
        log_event(f"[BatchCycles] report delivery failed: {exc}", level="WARNING", component="BatchCycles")


def run(cycle: str, trigger: str = "manual", now: Optional[datetime] = None,
        business_date_override: str = "") -> Dict[str, Any]:
    """Run one cycle: refresh the lake, then upsert the batch ledger row."""
    cycle = str(cycle or "").upper()
    if cycle not in CYCLES:
        raise ValueError(f"Unknown cycle '{cycle}'. Expected one of {', '.join(CYCLE_ORDER)}.")
    if not _INFLIGHT.acquire(blocking=False):
        return {"status": "busy", "message": "A batch cycle is already running."}
    try:
        return _run_locked(cycle, trigger, now, business_date_override)
    finally:
        _INFLIGHT.release()


def _run_locked(cycle: str, trigger: str, now: Optional[datetime], business_date_override: str) -> Dict[str, Any]:
    now_ist = _as_ist(now)
    bdate = business_date_override or business_date(now_ist)
    started = datetime.now(timezone.utc)
    details: Dict[str, Any] = {
        "cycle_label": CYCLES[cycle]["label"],
        "purpose": CYCLES[cycle]["purpose"],
        "trigger": trigger,
        "business_date": bdate,
    }
    status = "ERROR"
    try:
        from app.core import bq_export_scheduler

        result = bq_export_scheduler.run_once()
        pipeline_status = str(result.get("status") or "error").lower()
        status = {"success": "SUCCESS", "partial": "PARTIAL"}.get(pipeline_status, "ERROR")
        sf = bq_export_scheduler.STATE.get("snowflake") or {}
        duck = bq_export_scheduler.STATE.get("duckdb") or {}
        details.update({
            "pipeline_status": pipeline_status,
            "run_id": result.get("run_id"),
            "exported_tables": len(result.get("tables") or []),
            "exported_rows": result.get("rows"),
            "exported_bytes": result.get("bytes"),
            "snowflake_status": sf.get("status"),
            "snowflake_duplicates_removed": (sf.get("l1") or {}).get("duplicates_removed"),
            "duckdb_status": duck.get("status"),
            "summary": result.get("summary"),
        })
        run_id = str(result.get("run_id") or "")
        tables = int(len(result.get("tables") or []))
        rows = int(result.get("rows") or 0)
    except Exception as exc:
        details["error"] = str(exc)[:240]
        run_id, tables, rows = "", 0, 0

    finished = datetime.now(timezone.utc)
    recorded = _record(cycle, bdate, status, trigger=trigger, run_id=run_id,
                       tables=tables, rows=rows, details=details,
                       started_at=started, finished_at=finished)
    _DONE.add((bdate, cycle))
    record = {
        "cycle": cycle,
        "business_date": bdate,
        "status": status,
        "run_id": run_id,
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": finished.isoformat(timespec="seconds"),
        "details": details,
        "batch": recorded,
    }
    STATE["last_result"] = record
    STATE["history"].insert(0, record)
    del STATE["history"][20:]
    _audit(cycle, status, details)
    _deliver_report(cycle, bdate, status, details)
    log_event(
        f"[BatchCycles] {cycle} {bdate} {status} ({details.get('exported_rows')} rows, "
        f"run {run_id or 'n/a'})",
        component="BatchCycles",
    )
    return record


def _mark_missed(cycle: str, bdate: str, noticed_at: datetime) -> None:
    scheduled = _scheduled_at(cycle, bdate).astimezone(timezone.utc)
    details = {
        "cycle_label": CYCLES[cycle]["label"],
        "purpose": CYCLES[cycle]["purpose"],
        "trigger": "scheduler",
        "business_date": bdate,
        "reason": "Host was asleep at the scheduled time; the next due cycle ran instead.",
    }
    status = "MISSED"
    _record(cycle, bdate, status, trigger="scheduler", details=details,
            started_at=scheduled, finished_at=noticed_at)
    _DONE.add((bdate, cycle))
    record = {
        "cycle": cycle, "business_date": bdate, "status": status, "run_id": "",
        "started_at": scheduled.isoformat(timespec="seconds"),
        "finished_at": noticed_at.astimezone(timezone.utc).isoformat(timespec="seconds"),
        "details": details,
    }
    STATE["history"].insert(0, record)
    del STATE["history"][20:]
    _audit(cycle, status, details)


def poll(now: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
    """Called by the scheduler tick: run the latest due cycle, mark earlier ones MISSED."""
    now_ist = _as_ist(now)
    bdate = business_date(now_ist)
    minutes = now_ist.hour * 60 + now_ist.minute
    attempted = _attempted(bdate)
    pending = [
        cycle for cycle in CYCLE_ORDER
        if minutes >= _scheduled_minutes(cycle) and attempted.get(cycle) not in ("SUCCESS", "PARTIAL", "MISSED")
    ]
    if not pending:
        return None
    latest = pending[-1]
    for cycle in pending[:-1]:
        _mark_missed(cycle, bdate, now_ist)
    return run(latest, trigger="scheduler", now=now_ist, business_date_override=bdate)


def status(now: Optional[datetime] = None) -> Dict[str, Any]:
    """Cycle timetable with today's ledger state."""
    now_ist = _as_ist(now)
    bdate = business_date(now_ist)
    attempted = _attempted(bdate)
    minutes = now_ist.hour * 60 + now_ist.minute
    cycles = []
    for cycle in CYCLE_ORDER:
        state = attempted.get(cycle)
        if state in ("SUCCESS", "PARTIAL", "MISSED"):
            pass
        elif state == "ERROR":
            state = "ERROR_RETRY"
        elif minutes >= _scheduled_minutes(cycle):
            state = "DUE"
        else:
            state = "PENDING"
        hour, minute = _at(cycle)
        cycles.append({
            "cycle": cycle,
            "label": CYCLES[cycle]["label"],
            "scheduled_ist": f"{hour:02d}:{minute:02d}",
            "purpose": CYCLES[cycle]["purpose"],
            "state": state,
        })
    return {
        "timezone": "Asia/Kolkata",
        "now_ist": now_ist.astimezone(IST).isoformat(timespec="seconds"),
        "business_date": bdate,
        "in_flight": is_running(),
        "cycles": cycles,
        "last_result": STATE["last_result"],
        "history": STATE["history"][:10],
    }
