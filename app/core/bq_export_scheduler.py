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
_RUN_LOCK = threading.Lock()
DEFAULT_INTERVAL_MIN = 60
STATE: dict = {"armed": False, "running": False, "interval_min": DEFAULT_INTERVAL_MIN,
               "last_attempt": None, "snowflake": {}, "duckdb": {}}


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
    files = list(result.get("tables") or [])
    try:
        from app.core import sftp_ingestion

        known = {str(item.get("table") or "").upper() for item in files}
        for item in sftp_ingestion.bronze_files():
            table = str(item.get("table") or "").upper()
            if table and table not in known:
                files.append({
                    "key": item.get("key"), "table": table, "dataset": item.get("dataset"),
                    "rows": item.get("rows"), "bytes": item.get("bytes"),
                })
                known.add(table)
    except Exception as exc:
        log_event(f"[BQExport] SFTP bronze merge failed: {exc}", level="WARNING",
                  component="BQExportScheduler")
    if files:
        try:
            from app.core.snowflake_lakehouse import sync as sync_snowflake

            STATE["snowflake"] = sync_snowflake(files, str(result.get("run_id") or ""))
        except Exception as exc:
            STATE["snowflake"] = {"status": "error", "error": str(exc)[:240]}
        try:
            from app.core import bank_layers

            STATE["bank"] = bank_layers.build("all", str(result.get("run_id") or ""))
        except Exception as exc:
            STATE["bank"] = {"status": "error", "error": str(exc)[:240]}
        try:
            from app.core.duckdb_report_engine import build as build_duckdb_report

            STATE["duckdb"] = build_duckdb_report(files, str(result.get("run_id") or ""))
        except Exception as exc:
            STATE["duckdb"] = {"status": "error", "error": str(exc)[:240]}
    return result


def is_running() -> bool:
    return bool(STATE.get("running"))


def trigger(actor: str = "auto") -> dict:
    """Starts the BigQuery -> AWS -> Snowflake -> DuckDB chain in the background.

    Called by the AI Lab chat right after rows land in BigQuery, so the lake
    catches up immediately instead of waiting for the hourly tick.
    """
    if not _enabled():
        return {"status": "disabled", "message": "NANOPRO_BQ_AUTO_EXPORT is off."}
    try:
        from app.core.pipeline_orchestrator import is_paused

        if is_paused("bq_to_s3"):
            return {"status": "paused",
                    "message": "bq_to_s3 DAG is paused in the Orchestrator; resume it to run the lake automatically."}
    except Exception:
        pass
    if is_running():
        return {"status": "running", "message": "An export chain is already in progress; it will pick these rows up."}
    threading.Thread(target=_run_chain, args=(actor,), daemon=True,
                     name=f"bq-export-{actor}").start()
    return {"status": "started",
            "message": "BigQuery -> S3 -> Glue -> Snowflake L0/L1/L2 -> DuckDB chain started."}


def _record_orchestrator(actor: str, dag_id: str, status: str, message: str) -> None:
    try:
        from app.core.pipeline_orchestrator import _record_run

        _record_run("run", dag_id, status, str(message or "")[:280], actor)
    except Exception:
        pass


def _record_chain(actor: str, result: dict) -> None:
    """One run entry for the DAG card plus per-stage entries for anything broken."""
    from app.core.pipeline_orchestrator import FAIL_STATES

    status = str((result or {}).get("status") or "error").upper()
    summary = str((result or {}).get("summary") or "")
    _record_orchestrator(actor, "bq_to_s3", status, summary or status)
    if status in FAIL_STATES:
        try:
            from app.core.pipeline_orchestrator import _notify_failure

            _notify_failure("bq_to_s3", status, summary, 0.0)
        except Exception:
            pass

    sf = STATE.get("snowflake") or {}
    sf_status = str(sf.get("status") or "")
    if sf_status in ("error", "unavailable", "partial"):
        sf_state = "PARTIAL" if sf_status == "partial" else "ERROR"
        reason = str(sf.get("error") or sf.get("summary") or sf_status)
        for dag in ("snowflake_l0", "snowflake_l1", "snowflake_l2"):
            _record_orchestrator(actor, dag, sf_state, reason)

    duck = STATE.get("duckdb") or {}
    duck_status = str(duck.get("status") or "")
    if duck_status == "error":
        _record_orchestrator(actor, "duckdb_report", "ERROR",
                             str(duck.get("error") or "DuckDB report failed"))
    elif duck.get("mismatches"):
        _record_orchestrator(actor, "duckdb_report", "PARTIAL",
                             f"{len(duck['mismatches'])} parity mismatch(es): "
                             + ", ".join(str(item) for item in duck["mismatches"][:5]))

    bank = STATE.get("bank") or {}
    stage_status = bank.get("stage_status") or {}
    dag_of = {
        "l0_hist": "bank_raw_history", "l1_current": "bank_l1_scd2",
        "l1_scd2": "bank_l1_scd2", "l2_star": "bank_l2_star", "reports": "bank_rpt",
    }
    detail = (f"L0_HIST {bank.get('l0_hist') or 0} events · L1 {bank.get('l1') or 0} tables · "
              f"SCD2 {bank.get('scd2') or 0} · star {bank.get('star') or 0} · "
              f"reports {bank.get('reports') or 0}")
    for stage, dag in dag_of.items():
        state = str(stage_status.get(stage) or "").upper()
        if state in ("LOADED", "BUILT"):
            _record_orchestrator(actor, dag, "SUCCESS", detail)
        elif state == "PARTIAL":
            _record_orchestrator(actor, dag, "PARTIAL", detail)
        elif state:
            _record_orchestrator(actor, dag, "ERROR", detail)


def _run_chain(actor: str = "auto") -> dict:
    """Runs one full chain with a single-writer guard and orchestrator visibility."""
    with _RUN_LOCK:
        if STATE.get("running"):
            return {"status": "running", "summary": "An export chain is already in progress."}
        STATE["running"] = True
    try:
        from app.core import pipeline_orchestrator as orch

        orch._INFLIGHT.add("bq_to_s3")
        orch._OVERVIEW_CACHE["at"] = 0.0
    except Exception:
        orch = None
    try:
        result = run_once()
        _record_chain(actor, result)
        return result
    except Exception as exc:
        STATE["last_attempt"] = time.time()
        log_event(f"[BQExport] {actor} run failed: {exc}", level="ERROR", component="BQExportScheduler")
        _record_orchestrator(actor, "bq_to_s3", "ERROR", f"{type(exc).__name__}: {exc}")
        try:
            from app.core.pipeline_orchestrator import _notify_failure

            _notify_failure("bq_to_s3", "ERROR", str(exc), 0.0)
        except Exception:
            pass
        return {"status": "error", "summary": str(exc)[:280]}
    finally:
        STATE["running"] = False
        if orch is not None:
            try:
                orch._INFLIGHT.discard("bq_to_s3")
                orch._OVERVIEW_CACHE["at"] = 0.0
            except Exception:
                pass


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
                result = _run_chain("scheduler")
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
