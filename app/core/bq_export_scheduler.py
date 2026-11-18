"""Periodic BigQuery -> AWS export while the app is awake.

The external scheduler (EventBridge / cron-job.org) only wakes the host; this
loop is what keeps the bronze lake current without anyone pressing a button.
"""
from __future__ import annotations

import os
import threading
import time

from app.core.logger import log_event

_STARTED = threading.Event()
DEFAULT_INTERVAL_MIN = 60
STATE: dict = {"armed": False, "interval_min": DEFAULT_INTERVAL_MIN, "last_attempt": None,
               "snowflake": {}, "duckdb": {}}


def _enabled() -> bool:
    return (os.environ.get("NANOPRO_BQ_AUTO_EXPORT") or "1").strip().lower() not in ("0", "false", "no", "off")


def _interval_seconds() -> int:
    try:
        minutes = int(os.environ.get("NANOPRO_BQ_EXPORT_INTERVAL_MIN") or DEFAULT_INTERVAL_MIN)
    except ValueError:
        minutes = DEFAULT_INTERVAL_MIN
    return max(5, minutes) * 60


def run_once() -> dict:
    """Export to S3, then refresh Snowflake layers and the DuckDB report."""
    from app.core.bigquery_aws_pipeline import run_pipeline

    result = run_pipeline()
    STATE["last_attempt"] = time.time()
    STATE["last_result"] = {
        "run_id": result.get("run_id"),
        "status": result.get("status"),
        "summary": result.get("summary"),
        "tables": len(result.get("tables") or []),
        "rows": result.get("rows"),
        "bytes": result.get("bytes"),
        "services": {
            name: item.get("status")
            for name, item in (result.get("aws_services") or {}).items()
            if isinstance(item, dict)
        },
        "finished_at": result.get("finished_at"),
        "duration_ms": result.get("duration_ms"),
    }
    log_event(
        f"[BQExport] {result.get('status')}: {result.get('summary')}",
        component="BQExportScheduler",
    )
    if result.get("tables"):
        try:
            from app.core.snowflake_lakehouse import sync as sync_snowflake

            STATE["snowflake"] = sync_snowflake(result["tables"], str(result.get("run_id") or ""))
        except Exception as exc:
            STATE["snowflake"] = {"status": "error", "error": str(exc)[:240]}
        try:
            from app.core.duckdb_report_engine import build as build_duckdb_report

            STATE["duckdb"] = build_duckdb_report(result["tables"], str(result.get("run_id") or ""))
        except Exception as exc:
            STATE["duckdb"] = {"status": "error", "error": str(exc)[:240]}
    return result


def _loop() -> None:
    time.sleep(90)  # let the boot sequence finish first
    while True:
        if _enabled() and not _paused():
            handled = False
            try:
                from app.core import bank_batch_cycles

                handled = bank_batch_cycles.poll() is not None
            except Exception as exc:
                log_event(f"[BQExport] batch poll failed: {exc}", level="WARNING", component="BQExportScheduler")
            if not handled:
                try:
                    result = run_once()
                    try:
                        from app.core.cron_gateway_router import _record_cron_run

                        job_key = "BQ2AWS_SCHED_" + str(result.get("run_id") or "")
                        _record_cron_run(job_key, str(result.get("status") or "").upper(), {
                            "summary": result.get("summary"),
                            "tables": len(result.get("tables") or []),
                            "rows": result.get("rows"),
                        })
                    except Exception:
                        pass
                except Exception as exc:
                    STATE["last_attempt"] = time.time()
                    log_event(f"[BQExport] run failed: {exc}", level="WARNING", component="BQExportScheduler")
            try:
                from app.core.sftp_ingestion import poll as sftp_poll

                STATE["sftp"] = sftp_poll()
            except Exception as exc:
                log_event(f"[BQExport] SFTP poll failed: {exc}", level="WARNING", component="BQExportScheduler")
        time.sleep(_interval_seconds())


def _paused() -> bool:
    try:
        from app.core.pipeline_orchestrator import is_paused

        return is_paused("bq_to_s3")
    except Exception:
        return False


def start() -> None:
    if not _enabled() or _STARTED.is_set():
        return
    _STARTED.set()
    STATE["armed"] = True
    STATE["interval_min"] = _interval_seconds() // 60
    threading.Thread(target=_loop, daemon=True, name="bq-export-scheduler").start()
    log_event(f"[BQExport] scheduler armed, every {_interval_seconds() // 60} minutes.", component="BQExportScheduler")
