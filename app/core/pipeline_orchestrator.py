"""Real Airflow-style orchestrator for the NanoPro data pipeline.

The eight DAGs below are the actual stages of the live pipeline, not a mock:

    1. bq_to_s3          BigQuery nanopro_cbs_bronze -> S3 bronze Parquet
    2. sftp_to_s3        SFTP landing (sftp/inbound) -> S3 bronze Parquet
    3. glue_catalog      Glue tables + Iceberg publish
    4. snowflake_l0      S3 bronze -> BANK_DB.L0_STAGING
    5. snowflake_l1      L0 -> L1_HARMONIZED (dedupe + quality gate)
    6. snowflake_l2      L1 -> L2_CURATED marts
    7. duckdb_report     Parquet -> DuckDB report + Snowflake parity
    8. alerts            Email / Telegram / WhatsApp dispatch

Status shown in the UI is read from the scheduler state, the Snowflake batch
ledger and S3 metadata — never invented. Pause flags and cycle-time overrides
are stored in ``s3://<bucket>/config/orchestrator_control.json`` so they survive
a Render redeploy.
"""
from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.core.logger import log_event

IST = timezone(timedelta(hours=5, minutes=30))
CONTROL_KEY = "config/orchestrator_control.json"
CONTROL_TTL_S = 30.0
OVERVIEW_TTL_S = 15.0

DAGS: List[Dict[str, Any]] = [
    {"id": "bq_to_s3", "name": "BigQuery -> S3 Bronze", "stage": "SOURCE",
     "schedule": "Every 60 min + BOD 06:00 / SOD 08:00 / T1 10:00 / EOD 18:00 IST",
     "description": "Exports nanopro_cbs_bronze tables to s3://.../bronze/bigquery/ as Parquet with manifest."},
    {"id": "sftp_to_s3", "name": "SFTP Landing -> S3 Bronze", "stage": "SOURCE",
     "schedule": "Every 60 min and immediately after upload",
     "description": "Converts CSV/TXT/XLSX dropped in sftp/inbound into Parquet under sftp/bronze and registers Glue."},
    {"id": "glue_catalog", "name": "Glue + Iceberg Catalog", "stage": "CATALOG",
     "schedule": "After every BigQuery export",
     "description": "Registers bronze Parquet in Glue (nanopro_bronze) and publishes Iceberg metadata."},
    {"id": "snowflake_l0", "name": "Snowflake L0 Staging", "stage": "L0",
     "schedule": "After each export",
     "description": "Loads every bronze file into BANK_DB.L0_STAGING with _RUN_ID/_LOADED_AT audit columns."},
    {"id": "snowflake_l1", "name": "Snowflake L1 + Quality Gate", "stage": "L1",
     "schedule": "After L0",
     "description": "Trims/normalises and dedupes on business keys; duplicate counts land in DATA_QUALITY_MART."},
    {"id": "snowflake_l2", "name": "Snowflake L2 Curated Marts", "stage": "L2",
     "schedule": "After L1",
     "description": "Publishes CUSTOMER_360, BRANCH_NETWORK and the other L2 marts plus MART_CATALOG."},
    {"id": "bank_raw_history", "name": "Bank Raw Zone -> L0 History", "stage": "RAW",
     "schedule": "After each export (immutable CDC batches)",
     "description": "Appends every raw/cdc batch (SCN order, I/U/D) to BANK_DB.L0_HIST once per batch."},
    {"id": "bank_l1_scd2", "name": "Bank L1 Current + SCD2", "stage": "L1",
     "schedule": "After L0 history",
     "description": "Latest row per business key (deletes removed) plus type-2 history for the SCD tables."},
    {"id": "bank_l2_star", "name": "Bank L2 Star (Dims + Facts)", "stage": "L2",
     "schedule": "After L1",
     "description": "Conformed DIM_CUSTOMER/ACCOUNT/BRANCH/GL and FACT_TRANSACTION/LOAN/UPI/CARD/ATM."},
    {"id": "bank_rpt", "name": "RBI / FIU / ALM / UPI Reports", "stage": "REPORT",
     "schedule": "After L2 star",
     "description": "Builds the report-shaped marts in RPT_FIU, RPT_RBI, RPT_ALM and RPT_UPI."},
    {"id": "duckdb_report", "name": "DuckDB Report + Parity", "stage": "REPORT",
     "schedule": "After L2",
     "description": "Counts bronze Parquet in DuckDB and reconciles each table against Snowflake L0."},
    {"id": "alerts", "name": "Email / Telegram / WhatsApp", "stage": "ALERTS",
     "schedule": "Every batch cycle and on failure",
     "description": "Sends the cycle summary through the real SMTP, Telegram and Meta WhatsApp providers."},
]
DAG_IDS = tuple(dag["id"] for dag in DAGS)
CYCLE_DAGS = ("bq_to_s3", "sftp_to_s3")

_LOCK = threading.RLock()
_CONTROL_CACHE: Dict[str, Any] = {"at": 0.0, "value": None}
_OVERVIEW_CACHE: Dict[str, Any] = {"at": 0.0, "value": None}
RUNS: List[Dict[str, Any]] = []
_INFLIGHT: set = set()


# ----------------------------------------------------------------------------
# Control plane (S3-backed)
# ----------------------------------------------------------------------------
def _s3():
    from app.core.sftp_ingestion import _s3 as sftp_s3

    return sftp_s3()


def _bucket() -> str:
    from app.core.sftp_ingestion import _bucket as sftp_bucket

    return sftp_bucket()


def _default_control() -> Dict[str, Any]:
    return {"paused": [], "schedules": {}, "runs": [], "updated_at": ""}


def control(force: bool = False) -> Dict[str, Any]:
    now = time.time()
    if not force and _CONTROL_CACHE["value"] is not None and now - _CONTROL_CACHE["at"] < CONTROL_TTL_S:
        return _CONTROL_CACHE["value"]
    value = _default_control()
    try:
        body = _s3().get_object(Bucket=_bucket(), Key=CONTROL_KEY)["Body"].read()
        stored = json.loads(body)
        if isinstance(stored, dict):
            value.update({key: stored[key] for key in value if key in stored})
            if isinstance(stored.get("runs"), list):
                value["runs"] = stored["runs"][:40]
    except Exception:
        pass
    value["paused"] = [str(item) for item in value.get("paused") or [] if item]
    value["schedules"] = {str(k).upper(): str(v) for k, v in (value.get("schedules") or {}).items()}
    _CONTROL_CACHE.update({"at": now, "value": value})
    return value


def _save_control(value: Dict[str, Any]) -> None:
    with _LOCK:
        value["updated_at"] = datetime.now(IST).isoformat(timespec="seconds")
        body = json.dumps(value, indent=2, default=str).encode("utf-8")
        _s3().put_object(Bucket=_bucket(), Key=CONTROL_KEY, Body=body, ContentType="application/json")
        _CONTROL_CACHE.update({"at": time.time(), "value": value})


def is_paused(dag_id: str) -> bool:
    return dag_id in (control().get("paused") or [])


def cycle_schedules() -> Dict[str, str]:
    """HH:MM IST overrides for BOD/SOD/T1/EOD set from the Orchestrator screen."""
    return dict(control().get("schedules") or {})


def set_schedule(cycle: str, at: str, actor: str = "ui") -> Dict[str, Any]:
    cycle = str(cycle or "").upper()
    from app.core.bank_batch_cycles import CYCLES

    if cycle not in CYCLES:
        raise ValueError(f"Unknown cycle '{cycle}'.")
    at = str(at or "").strip()
    try:
        hour, minute = (int(part) for part in at.split(":"))
    except Exception:
        raise ValueError("Time must be HH:MM in 24h format (IST).")
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("Time must be between 00:00 and 23:59.")
    value = control(force=True)
    with _LOCK:
        value["schedules"][cycle] = f"{hour:02d}:{minute:02d}"
        _save_control(value)
    _record_run("schedule", cycle, "SUCCESS", f"Cycle time changed to {hour:02d}:{minute:02d} IST", actor)
    log_event(f"[Orchestrator] {cycle} rescheduled to {hour:02d}:{minute:02d} IST by {actor}",
              component="Orchestrator")
    return {"status": "success", "cycle": cycle, "scheduled_ist": value["schedules"][cycle]}


def _record_run(dag_id: str, target: str, status: str, message: str, actor: str = "ui") -> None:
    entry = {"at": datetime.now(IST).isoformat(timespec="seconds"), "dag": dag_id,
             "target": target, "status": status, "message": message, "actor": actor}
    RUNS.insert(0, entry)
    del RUNS[60:]
    try:
        from app.core.cron_gateway_router import _record_cron_run

        _record_cron_run(f"ORCH_{dag_id.upper()}", status, {"target": target, "message": message,
                                                           "actor": actor})
    except Exception:
        pass
    try:
        value = control(force=True)
        seen = {(run.get("at"), run.get("dag"), run.get("target"), run.get("message")) for run in RUNS}
        merged = RUNS + [run for run in (value.get("runs") or [])
                         if (run.get("at"), run.get("dag"), run.get("target"), run.get("message")) not in seen]
        value["runs"] = merged[:40]
        _save_control(value)
    except Exception:
        pass


# ----------------------------------------------------------------------------
# Live status
# ----------------------------------------------------------------------------
def _fmt(value: Any) -> str:
    if not value:
        return ""
    return str(value)


def _dag_statuses(sftp: Dict[str, Any], notifications: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    from app.core import bq_export_scheduler

    state = bq_export_scheduler.STATE or {}
    last = state.get("last_result") or {}
    sf = state.get("snowflake") or {}
    duck = state.get("duckdb") or {}
    paused = set(control().get("paused") or [])

    statuses: Dict[str, Dict[str, Any]] = {}

    bq_status = str(last.get("status") or "not_run").upper()
    statuses["bq_to_s3"] = {
        "status": bq_status if bq_status != "NOT_RUN" else "NOT_RUN",
        "rows": last.get("rows"), "tables": last.get("tables"),
        "detail": last.get("summary") or "No export recorded in this process yet.",
        "run_id": last.get("run_id"), "finished_at": last.get("finished_at") or "",
        "duration_s": last.get("duration_s"),
    }

    files = sftp.get("files") or []
    failed = [item for item in files if item.get("status") == "error"]
    new = [item for item in files if item.get("status") == "new"]
    statuses["sftp_to_s3"] = {
        "status": "ERROR" if failed else ("SUCCESS" if sftp.get("tables") else "IDLE"),
        "rows": sum(int(item.get("rows") or 0) for item in sftp.get("tables") or []),
        "tables": len(sftp.get("tables") or []),
        "detail": (f"{len(files)} file(s) in landing · {len(new)} awaiting ingest · "
                   f"{len(sftp.get('tables') or [])} table(s) in bronze"),
        "files_failed": len(failed), "files_new": len(new),
        "errors": [{"file": item.get("name"), "error": item.get("error") or "ingest failed"}
                   for item in failed][:5],
        "last_batch": (sftp.get("batches") or [{}])[0],
    }

    glue = ((last.get("services") or {}).get("glue")) if last else None
    statuses["glue_catalog"] = {
        "status": "SUCCESS" if glue in ("registered", "partial") else ("NOT_RUN" if not glue else "ERROR"),
        "detail": f"Glue nanopro_bronze: {glue or 'not run yet'}" +
                  (f" · nanopro_sftp: {sftp.get('tables') and len(sftp.get('tables')) or 0} table(s)" if sftp else ""),
        "tables": sftp.get("tables") and len(sftp.get("tables")) or 0,
    }

    sf_status = str(sf.get("status") or "not_run")
    l0 = sf.get("l0") or {}
    l1 = sf.get("l1") or {}
    l2 = sf.get("l2") or {}
    sf_map = {"synced": "SUCCESS", "partial": "PARTIAL", "unavailable": "ERROR",
              "error": "ERROR", "skipped": "IDLE", "not_run": "NOT_RUN"}
    statuses["snowflake_l0"] = {
        "status": sf_map.get(sf_status, sf_status.upper()),
        "rows": l0.get("rows"), "tables": l0.get("tables"),
        "detail": f"L0_STAGING · {l0.get('tables') or 0} table(s) · {l0.get('rows') or 0} rows",
    }
    statuses["snowflake_l1"] = {
        "status": sf_map.get(sf_status, sf_status.upper()),
        "tables": l1.get("tables"), "duplicates_removed": l1.get("duplicates_removed"),
        "detail": (f"L1_HARMONIZED · {l1.get('tables') or 0} table(s) · "
                   f"{l1.get('duplicates_removed') or 0} duplicates removed"),
    }
    statuses["snowflake_l2"] = {
        "status": sf_map.get(sf_status, sf_status.upper()),
        "tables": l2.get("tables"),
        "detail": f"L2_CURATED · {l2.get('tables') or 0} mart(s): " +
                  ", ".join(sorted((l2.get('marts') or {}).keys())[:6]),
    }

    bank = state.get("bank") or {}
    bank_stages = bank.get("stage_status") or {}
    bank_map = {"LOADED": "SUCCESS", "BUILT": "SUCCESS", "PARTIAL": "PARTIAL", "ERROR": "ERROR"}
    bank_detail = (f"L0_HIST {bank.get('l0_hist') or 0} events · L1 {bank.get('l1') or 0} tables · "
                   f"SCD2 {bank.get('scd2') or 0} tables · star {bank.get('star') or 0} · "
                   f"reports {bank.get('reports') or 0}")
    statuses["bank_raw_history"] = {
        "status": bank_map.get(str(bank_stages.get("l0_hist") or "").upper(), "NOT_RUN"),
        "rows": bank.get("l0_hist"), "tables": 1, "detail": bank_detail,
    }
    statuses["bank_l1_scd2"] = {
        "status": bank_map.get(str(bank_stages.get("l1_current") or "").upper(), "NOT_RUN"),
        "tables": bank.get("l1"), "scd2_tables": bank.get("scd2"), "detail": bank_detail,
    }
    statuses["bank_l2_star"] = {
        "status": bank_map.get(str(bank_stages.get("l2_star") or "").upper(), "NOT_RUN"),
        "tables": bank.get("star"), "detail": bank_detail,
    }
    statuses["bank_rpt"] = {
        "status": bank_map.get(str(bank_stages.get("reports") or "").upper(), "NOT_RUN"),
        "tables": bank.get("reports"), "detail": bank_detail,
    }

    duck_status = str(duck.get("status") or "not_run")
    statuses["duckdb_report"] = {
        "status": {"reconciled": "SUCCESS", "built": "SUCCESS", "empty": "IDLE",
                   "error": "ERROR", "skipped": "IDLE"}.get(duck_status, duck_status.upper()),
        "rows": duck.get("rows"), "tables": duck.get("tables"),
        "detail": (f"report_{duck.get('run_id') or 'manual'} · {duck.get('tables') or 0} table(s) · "
                   f"{len(duck.get('mismatches') or [])} parity mismatch(es)"),
        "mismatches": duck.get("mismatches") or [],
    }

    latest = (notifications or [{}])[0]
    delivered = [item for item in notifications[:20] if item.get("status") == "DELIVERED"]
    failed_alerts = [item for item in notifications[:20] if item.get("status") == "FAILED"]
    statuses["alerts"] = {
        "status": "ERROR" if failed_alerts and not delivered else ("SUCCESS" if delivered else "NOT_RUN"),
        "detail": (f"{len(delivered)} delivered / {len(failed_alerts)} failed in the last 20 attempts"
                   + (f" · last: {latest.get('channel')} {latest.get('status')}" if latest else "")),
        "last": latest or None,
    }

    for dag in DAGS:
        entry = statuses[dag["id"]]
        entry["paused"] = dag["id"] in paused
        if entry["paused"]:
            entry["status"] = "PAUSED"
        entry["in_flight"] = dag["id"] in _INFLIGHT
        if entry["in_flight"]:
            entry["status"] = "RUNNING"
    return statuses


def overview(force: bool = False) -> Dict[str, Any]:
    now = time.time()
    if not force and _OVERVIEW_CACHE["value"] and now - _OVERVIEW_CACHE["at"] < OVERVIEW_TTL_S:
        return _OVERVIEW_CACHE["value"]

    from app.core import bank_batch_cycles, bq_export_scheduler, pipeline_notifications, sftp_ingestion

    try:
        sftp = sftp_ingestion.status()
    except Exception as exc:
        sftp = {"status": "error", "error": str(exc)[:200], "files": [], "tables": []}
    try:
        from app.core import report_delivery

        outbound = report_delivery.list_outbound(limit=10)
    except Exception as exc:
        outbound = {"status": "error", "error": str(exc)[:200], "reports": []}
    notifications = pipeline_notifications.logs(50)
    statuses = _dag_statuses(sftp, notifications)
    cycles = bank_batch_cycles.status()
    runs = _merged_runs(40)

    last_errors: Dict[str, Dict[str, Any]] = {}
    incidents: List[Dict[str, Any]] = []
    for run in runs:
        # _record_run stores the action in "dag" and the DAG id in "target".
        dag_key = str(run.get("target") or "") if run.get("dag") == "run" else ""
        status = str(run.get("status") or "").upper()
        if dag_key and status in FAIL_STATES:
            incidents.append({"at": run.get("at"), "kind": "DAG_FAILURE", "dag": dag_key,
                              "level": "ERROR", "message": f"{status}: {run.get('message')}"})
            if dag_key and dag_key not in last_errors:
                last_errors[dag_key] = {"at": run.get("at"), "status": status,
                                        "message": run.get("message")}
    for item in sftp.get("files") or []:
        if item.get("status") == "error":
            incidents.append({"at": item.get("modified") or "", "kind": "SFTP_FILE",
                              "dag": "sftp_to_s3", "level": "ERROR",
                              "message": f"{item.get('name')}: {item.get('error') or 'ingest failed'}"})
    for table in (bq_export_scheduler.STATE.get("duckdb") or {}).get("mismatches") or []:
        incidents.append({"at": "", "kind": "PARITY", "dag": "duckdb_report", "level": "WARNING",
                          "message": f"{table}: DuckDB row count differs from Snowflake L0"})
    for item in notifications[:20]:
        if item.get("status") == "FAILED":
            incidents.append({"at": item.get("timestamp") or "", "kind": "ALERT", "dag": "alerts",
                              "level": "WARNING",
                              "message": f"{item.get('channel')} -> {item.get('recipient')}: "
                                         f"{item.get('error') or 'delivery failed'}"})
    incidents.sort(key=lambda item: str(item.get("at") or ""), reverse=True)

    scheduler = {
        "armed": bool(bq_export_scheduler.STATE.get("armed")),
        "interval_min": bq_export_scheduler.STATE.get("interval_min"),
        "last_attempt": bq_export_scheduler.STATE.get("last_attempt"),
        "paused": is_paused("bq_to_s3"),
    }
    paused_count = len(control().get("paused") or [])
    healthy = sum(1 for item in statuses.values() if item["status"] == "SUCCESS")
    result = {
        "generated_at": datetime.now(IST).isoformat(timespec="seconds"),
        "dags": [{**dag, **statuses[dag["id"]], "last_error": last_errors.get(dag["id"])}
                 for dag in DAGS],
        "scheduler": scheduler,
        "cycles": cycles,
        "cycle_schedules": {cycle: _cycle_time(cycle, cycles) for cycle in ("BOD", "SOD", "T1", "EOD")},
        "summary": {
            "total": len(DAGS), "success": healthy, "paused": paused_count,
            "business_date": cycles.get("business_date"),
            "rows": (scheduler and (bq_export_scheduler.STATE.get("last_result") or {}).get("rows")) or 0,
        },
        "sftp": {key: sftp.get(key) for key in
                 ("status", "landing_prefix", "bronze_prefix", "glue_database", "files", "tables",
                  "batches", "supported", "max_mb", "error")},
        "sftp_outbound": {
            "prefix": outbound.get("prefix") or "s3://.../sftp/outbound/reports/",
            "sftp_path": outbound.get("sftp_path") or "/sftp/outbound/reports/",
            "reports": outbound.get("reports") or [],
            "error": outbound.get("error") or "",
        },
        "alerts": {
            "config": _masked_config(notifications),
            "logs": notifications[:20],
        },
        "runs": runs,
        "incidents": incidents[:25],
        "snowflake": bq_export_scheduler.STATE.get("snowflake") or {},
        "bank": bq_export_scheduler.STATE.get("bank") or {},
        "duckdb": bq_export_scheduler.STATE.get("duckdb") or {},
    }
    _OVERVIEW_CACHE.update({"at": now, "value": result})
    return result


def _cycle_time(cycle: str, cycles: Dict[str, Any]) -> str:
    for item in cycles.get("cycles") or []:
        if item.get("cycle") == cycle:
            return item.get("scheduled_ist") or ""
    return ""


def _masked_config(notifications: List[Dict[str, Any]]) -> Dict[str, Any]:
    from app.core.pipeline_alerts import config

    conf = config()
    phone = str(conf.get("whatsapp_number") or "")
    return {
        "sender": conf.get("sender"),
        "recipients": conf.get("recipients") or [],
        "telegram_channel": conf.get("telegram_channel"),
        "telegram_enabled": bool(conf.get("telegram_enabled", True)),
        "whatsapp_number": (phone[:4] + "****" + phone[-3:]) if len(phone) > 8 else phone,
        "whatsapp_enabled": bool(conf.get("whatsapp_enabled", True)),
        "last_delivery": (notifications or [{}])[0].get("timestamp") if notifications else "",
    }


# ----------------------------------------------------------------------------
# Controls
# ----------------------------------------------------------------------------
def pause(dag_id: str, actor: str = "ui") -> Dict[str, Any]:
    dag_id = _require_dag(dag_id)
    value = control(force=True)
    with _LOCK:
        paused = set(value.get("paused") or [])
        if dag_id in paused:
            paused.discard(dag_id)
            state = "RESUMED"
        else:
            paused.add(dag_id)
            state = "PAUSED"
        value["paused"] = sorted(paused)
        _save_control(value)
    _record_run("pause", dag_id, state, f"DAG {dag_id} {state.lower()}", actor)
    log_event(f"[Orchestrator] {dag_id} {state.lower()} by {actor}", component="Orchestrator",
              level="WARNING" if state == "PAUSED" else "INFO")
    return {"status": "success", "dag_id": dag_id, "state": state}


def _require_dag(dag_id: str) -> str:
    dag_id = str(dag_id or "").strip()
    if dag_id not in DAG_IDS:
        raise ValueError(f"Unknown DAG '{dag_id}'. Expected one of {', '.join(DAG_IDS)}.")
    return dag_id


FAIL_STATES = ("ERROR", "FAILED", "PARTIAL", "ERROR_RETRY")


def _merged_runs(limit: int = 40) -> List[Dict[str, Any]]:
    try:
        stored = control().get("runs") or []
    except Exception:
        stored = []
    seen = {(r.get("at"), r.get("dag"), r.get("target"), r.get("message")) for r in RUNS}
    return (RUNS + [r for r in stored
                    if (r.get("at"), r.get("dag"), r.get("target"), r.get("message")) not in seen])[:limit]


def _notify_failure(dag_id: str, status: str, message: str, elapsed: float) -> None:
    try:
        from app.core import pipeline_alerts

        pipeline_alerts.dispatch(
            subject=f"NanoPro pipeline {status}: {dag_id}",
            body=f"DAG {dag_id} finished {status.lower()} after {round(elapsed, 1)}s.\n\n"
                 f"Reason: {message[:280]}\n\n"
                 + pipeline_alerts.pipeline_summary({"error": message[:280]}),
            trigger="dag_failure",
            async_send=True,
        )
    except Exception as exc:
        log_event(f"[Orchestrator] failure alert could not be sent: {exc}", level="WARNING",
                  component="Orchestrator")


def _background(dag_id: str, target, actor: str) -> None:
    _INFLIGHT.add(dag_id)

    def worker():
        started = time.time()
        try:
            result = target()
            status = str(result.get("status") or "success").upper() if isinstance(result, dict) else "SUCCESS"
            message = (result.get("summary") if isinstance(result, dict) else str(result)) or "completed"
            _record_run("run", dag_id, status, str(message)[:280], actor)
            if status in FAIL_STATES:
                log_event(f"[Orchestrator] {dag_id} {status}: {message}", level="ERROR",
                          component="Orchestrator")
                _notify_failure(dag_id, status, str(message), time.time() - started)
        except Exception as exc:
            _record_run("run", dag_id, "ERROR", str(exc)[:280], actor)
            log_event(f"[Orchestrator] {dag_id} failed: {exc}", level="ERROR", component="Orchestrator")
            _notify_failure(dag_id, "ERROR", str(exc), time.time() - started)
        finally:
            _INFLIGHT.discard(dag_id)
            _OVERVIEW_CACHE["at"] = 0.0

    threading.Thread(target=worker, daemon=True, name=f"orch-{dag_id}").start()


def run(dag_id: str, mode: str = "incremental", actor: str = "ui") -> Dict[str, Any]:
    dag_id = _require_dag(dag_id)
    if is_paused(dag_id):
        return {"status": "paused", "dag_id": dag_id, "message": "DAG is paused. Resume it first."}
    if dag_id in _INFLIGHT:
        return {"status": "busy", "dag_id": dag_id, "message": "This DAG is already running."}

    if dag_id == "bq_to_s3":
        from app.core import bq_export_scheduler

        target = bq_export_scheduler.run_once
    elif dag_id == "sftp_to_s3":
        from app.core import sftp_ingestion

        target = lambda: sftp_ingestion.poll(force=str(mode).lower() == "full")
    elif dag_id == "glue_catalog":
        from app.core.bigquery_aws_pipeline import run_pipeline

        target = run_pipeline
    elif dag_id in ("snowflake_l0", "snowflake_l1", "snowflake_l2"):
        from app.core import sftp_ingestion

        target = sftp_ingestion.refresh_downstream
    elif dag_id in ("bank_raw_history", "bank_l1_scd2", "bank_l2_star", "bank_rpt"):
        from app.core import bank_layers

        stage = {"bank_raw_history": "raw", "bank_l1_scd2": "l1",
                 "bank_l2_star": "star", "bank_rpt": "rpt"}[dag_id]
        target = lambda s=stage: bank_layers.build(s)
    elif dag_id == "duckdb_report":
        from app.core import sftp_ingestion
        from app.core.duckdb_report_engine import build

        target = lambda: build(sftp_ingestion.bronze_files(), f"orc_{datetime.now(IST).strftime('%Y%m%dT%H%M%S')}")
    elif dag_id == "alerts":
        from app.core import report_delivery

        target = lambda: report_delivery.deliver(cycle="MANUAL", async_send=False)
    else:
        raise ValueError(f"Unknown DAG '{dag_id}'.")

    _background(dag_id, target, actor)
    _record_run("dispatch", dag_id, "DISPATCHED", f"Run requested ({mode})", actor)
    return {"status": "dispatched", "dag_id": dag_id, "mode": mode,
            "message": f"{dag_id} started in the background. Refresh in a few seconds for the result."}


def rollback(dag_id: str, target_layer: str = "", confirm: bool = False, actor: str = "ui") -> Dict[str, Any]:
    """Rebuild (or purge) from the source of truth; no fabricated 'watermark'."""
    dag_id = _require_dag(dag_id)
    if not confirm:
        raise ValueError("Rollback needs explicit confirmation.")
    layer = str(target_layer or "").upper()

    if dag_id == "sftp_to_s3":
        from app.core import sftp_ingestion

        batches = sftp_ingestion.status().get("batches") or []
        if not batches:
            return {"status": "nothing_to_rollback", "dag_id": dag_id,
                    "message": "No SFTP batch has been ingested yet."}
        latest = batches[0]
        result = sftp_ingestion.purge(str(latest.get("key")))
        _record_run("rollback", dag_id, "SUCCESS",
                    f"Purged {latest.get('table')} (batch {latest.get('batch_id')})", actor)
        return {"status": "success", "dag_id": dag_id, "purged": result,
                "message": f"Removed SFTP table {latest.get('table')} from bronze and Snowflake."}

    if dag_id in ("snowflake_l1", "snowflake_l2") or layer in ("L0", "L1", "L2"):
        from app.core import sftp_ingestion

        _record_run("rollback", dag_id, "RUNNING",
                    f"Rebuilding Snowflake layers from bronze (target {layer or dag_id})", actor)
        result = sftp_ingestion.refresh_downstream()
        _record_run("rollback", dag_id, str(result.get("status") or "").upper(),
                    f"Rebuild finished: {result.get('summary')}", actor)
        return {"status": "success", "dag_id": dag_id, "layer": layer or "ALL",
                "message": "Snowflake layers rebuilt from the S3 bronze source of truth (CREATE OR REPLACE).",
                "result": result}

    if dag_id in ("bq_to_s3", "glue_catalog", "snowflake_l0"):
        from app.core import bq_export_scheduler

        _record_run("rollback", dag_id, "RUNNING", "Re-exporting from BigQuery and rebuilding layers", actor)
        result = bq_export_scheduler.run_once()
        _record_run("rollback", dag_id, str(result.get("status") or "").upper(),
                    f"Re-export finished: {result.get('summary')}", actor)
        return {"status": "success", "dag_id": dag_id,
                "message": "Re-exported from BigQuery (the source of truth) and rebuilt every downstream layer.",
                "result": {"run_id": result.get("run_id"), "status": result.get("status"),
                           "summary": result.get("summary")}}

    if dag_id in ("bank_raw_history", "bank_l1_scd2", "bank_l2_star", "bank_rpt"):
        from app.core import bank_layers

        _record_run("rollback", dag_id, "RUNNING", "Rebuilding bank layers from the raw zone", actor)
        result = bank_layers.build("all")
        _record_run("rollback", dag_id, str(result.get("status") or "").upper(),
                    f"Bank layers rebuilt: {result.get('status')}", actor)
        return {"status": "success", "dag_id": dag_id,
                "message": "Bank layers rebuilt from the immutable raw CDC zone.", "result": result}

    if dag_id == "duckdb_report":
        from app.core import sftp_ingestion
        from app.core.duckdb_report_engine import build

        result = build(sftp_ingestion.bronze_files(), f"rollback_{datetime.now(IST).strftime('%Y%m%dT%H%M%S')}")
        _record_run("rollback", dag_id, "SUCCESS", "DuckDB report rebuilt", actor)
        return {"status": "success", "dag_id": dag_id, "message": "DuckDB report rebuilt from bronze.",
                "result": result}

    return {"status": "not_applicable", "dag_id": dag_id,
            "message": "This DAG has no stored data to roll back; use Run to replay it."}


def logs(limit: int = 80) -> Dict[str, Any]:
    from app.core.logger import get_recent_logs

    entries = []
    for line in reversed(get_recent_logs(400)):
        entries.append({"source": "runtime", "text": line})
        if len(entries) >= limit:
            break
    try:
        from app.core.cron_gateway_router import CRON_AUDIT_LOGS

        for item in CRON_AUDIT_LOGS[:20]:
            entries.insert(0, {
                "source": "audit",
                "text": (f"[{item.get('time_str')}] [{item.get('job_name')}] {item.get('status')} "
                         f"{json.dumps(item.get('details') or {})[:220]}"),
            })
    except Exception:
        pass
    for run in (control().get("runs") or [])[:20]:
        entries.insert(0, {
            "source": "orchestrator",
            "text": f"[{run.get('at')}] [{run.get('actor')}] {run.get('target')}/{run.get('dag')} "
                    f"{run.get('status')} - {run.get('message')}",
        })
    return {"status": "success", "logs": entries[:limit]}
