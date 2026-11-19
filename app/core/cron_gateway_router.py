"""
Mangesh Nano Pro AI Studio - Unified cron-job.org Webhook Engine & Scheduler Gateway
=====================================================================================
Integrates directly with https://console.cron-job.org/dashboard
Provides 100% Lifetime Free (No Card Ever) cloud-triggered automation:
  1. /api/cron/keepalive -> Ultra-lightweight (200 bytes) keep-alive heartbeat every 14 mins
  2. /api/cron/bod       -> BOD 06:00 AM Full Load & Validation
  3. /api/cron/sod       -> SOD 08:00 AM Incremental Start of Day
  4. /api/cron/t1        -> Daily T-1 10:00 AM Delta Processing
  5. /api/cron/eod       -> EOD 06:00 PM Reconciliation & EOD Summary
  6. /api/cron/status    -> Execution audit & health ledger
"""

from __future__ import annotations

import hmac
import os
import time
from typing import Dict, Any
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.logger import log_event
from app.core.cluster_mesh_engine import cluster_mesh
from app.core.etl_automation_pipeline import etl_pipeline

router = APIRouter(prefix="/api/cron", tags=["CronJobOrgGateway"])

CRON_AUDIT_LOGS = []

import threading

_AUTO_LOCK = {"at": 0.0}
AUTO_MIN_SECONDS = 600


def _automation_authorised(request: Request) -> bool:
    """Pipeline automation accepts the configured cron secret or a live session token."""
    expected = (os.environ.get("NANOPRO_CRON_SECRET") or "").strip()
    supplied = (request.headers.get("X-Cron-Secret") or request.query_params.get("secret") or "").strip()
    if expected and supplied and hmac.compare_digest(supplied, expected):
        return True
    from app.core.api_auth import session_user_from_headers

    return bool(session_user_from_headers(
        cookie_header=request.headers.get("cookie", ""),
        x_session_token=request.headers.get("X-Session-Token", ""),
        authorization=request.headers.get("Authorization", ""),
    ))


def _cycle_refusal(request: Request):
    """Heavy EOD/BOD cycles and their message dispatch belong to the local lane.

    The public cron URLs are callable by anyone, so the free cloud host must
    refuse them: a stranger could otherwise burn CPU/bandwidth and trigger
    email/Telegram/WhatsApp sends. When NANOPRO_CRON_SECRET is configured the
    caller must also present it, which keeps the laptop lane closed as well.
    """
    from app.core.runtime_profile import cloud_safe_mode

    if cloud_safe_mode():
        return JSONResponse(status_code=409, content={
            "success": False,
            "status": "LOCAL_LANE_ONLY",
            "error": "Heavy pipeline cycles run on the laptop lane, not the free cloud host.",
        })
    expected = (os.environ.get("NANOPRO_CRON_SECRET") or "").strip()
    if expected:
        supplied = (request.headers.get("X-Cron-Secret") or request.query_params.get("secret") or "").strip()
        if not hmac.compare_digest(supplied, expected):
            return JSONResponse(status_code=403, content={
                "success": False,
                "error": "Invalid or missing cron secret.",
            })
    return None

def _run_in_background(target_func, cron_key, task_id, start_time):
    def worker():
        try:
            res = target_func()
            duration = round(time.time() - start_time, 2)
            _record_cron_run(cron_key, "SUCCESS", {"task_id": task_id, "duration_s": duration, "result": str(res)})
            log_event(f"[CronGateway] {cron_key} background task {task_id} completed in {duration}s.", component="CronGateway")
        except Exception as e:
            _record_cron_run(cron_key, "ERROR", {"task_id": task_id, "error": str(e)})
            log_event(f"[CronGateway] {cron_key} background task {task_id} failed: {e}", component="CronGateway")
    
    t = threading.Thread(target=worker, daemon=True)
    t.start()

def _record_cron_run(job_name: str, status: str, details: Dict[str, Any]):
    global CRON_AUDIT_LOGS
    CRON_AUDIT_LOGS.insert(0, {
        "job_name": job_name,
        "status": status,
        "timestamp": time.time(),
        "time_str": time.strftime("%Y-%m-%d %H:%M:%S IST"),
        "details": details
    })
    CRON_AUDIT_LOGS = CRON_AUDIT_LOGS[:50]  # Keep last 50

@router.get("/keepalive")
@router.post("/keepalive")
async def cron_keepalive(request: Request):
    """
    Ultra-lightweight keep-alive ping for cron-job.org.
    Keeps cloud nodes (Render / Zeabur / Northflank) awake without cold starts.
    Bandwidth: < 200 bytes per call (~1 MB per month).
    """
    now = time.time()
    cluster_mesh.send_heartbeat()
    return JSONResponse(content={
        "status": "ALIVE",
        "node_id": cluster_mesh.node_id,
        "node_role": cluster_mesh.node_role,
        "timestamp": now,
        "message": "NanoPro AI Studio active and healthy."
    })

@router.get("/bod")
@router.post("/bod")
async def cron_bod_trigger(request: Request):
    """
    Beginning of Day (06:00 AM IST) cron-job.org trigger.
    Enqueues or runs full load validation across the cluster.
    """
    refusal = _cycle_refusal(request)
    if refusal:
        return refusal
    log_event("[CronGateway] External BOD Webhook triggered from cron-job.org.", component="CronGateway")
    start = time.time()
    try:
        # Enqueue into cluster mesh for distributed execution
        task_id = cluster_mesh.enqueue_task("BOD_CYCLE", {"source": "cron-job.org", "timestamp": start}, priority=10)
        _run_in_background(etl_pipeline.run_bod_cycle, "BOD_06AM", task_id, start)
        return JSONResponse(content={
            "success": True,
            "status": "DISPATCHED_IN_BACKGROUND",
            "cycle": "BOD (Beginning of Day)",
            "task_id": task_id,
            "message": "BOD cycle initiated asynchronously across cluster."
        })
    except Exception as e:
        _record_cron_run("BOD_06AM", "ERROR", {"error": str(e)})
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/sod")
@router.post("/sod")
async def cron_sod_trigger(request: Request):
    """
    Start of Day (08:00 AM IST) cron-job.org trigger.
    Incremental update for day's opening positions.
    """
    refusal = _cycle_refusal(request)
    if refusal:
        return refusal
    log_event("[CronGateway] External SOD Webhook triggered from cron-job.org.", component="CronGateway")
    start = time.time()
    try:
        task_id = cluster_mesh.enqueue_task("SOD_CYCLE", {"source": "cron-job.org", "timestamp": start}, priority=8)
        _run_in_background(etl_pipeline.run_sod_cycle, "SOD_08AM", task_id, start)
        return JSONResponse(content={
            "success": True,
            "status": "DISPATCHED_IN_BACKGROUND",
            "cycle": "SOD (Start of Day)",
            "task_id": task_id,
            "message": "SOD cycle initiated asynchronously across cluster."
        })
    except Exception as e:
        _record_cron_run("SOD_08AM", "ERROR", {"error": str(e)})
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/t1")
@router.post("/t1")
async def cron_t1_trigger(request: Request):
    """
    Daily T-1 (10:00 AM IST) cron-job.org trigger.
    Incremental delta transaction ingestion and audit ledger updates.
    """
    refusal = _cycle_refusal(request)
    if refusal:
        return refusal
    log_event("[CronGateway] External T-1 Webhook triggered from cron-job.org.", component="CronGateway")
    start = time.time()
    try:
        task_id = cluster_mesh.enqueue_task("T1_CYCLE", {"source": "cron-job.org", "timestamp": start}, priority=7)
        _run_in_background(etl_pipeline.run_incremental_cycle, "T1_10AM", task_id, start)
        return JSONResponse(content={
            "success": True,
            "status": "DISPATCHED_IN_BACKGROUND",
            "cycle": "T-1 (Daily Delta)",
            "task_id": task_id,
            "message": "T-1 delta cycle initiated asynchronously across cluster."
        })
    except Exception as e:
        _record_cron_run("T1_10AM", "ERROR", {"error": str(e)})
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/eod")
@router.post("/eod")
async def cron_eod_trigger(request: Request):
    """
    End of Day (06:00 PM IST) cron-job.org trigger.
    Reconciles all 9 banking projects, generates summary, and dispatches email/telegram.
    """
    refusal = _cycle_refusal(request)
    if refusal:
        return refusal
    log_event("[CronGateway] External EOD Webhook triggered from cron-job.org.", component="CronGateway")
    start = time.time()
    try:
        task_id = cluster_mesh.enqueue_task("EOD_CYCLE", {"source": "cron-job.org", "timestamp": start}, priority=10)
        _run_in_background(etl_pipeline.run_eod_cycle, "EOD_06PM", task_id, start)
        return JSONResponse(content={
            "success": True,
            "status": "DISPATCHED_IN_BACKGROUND",
            "cycle": "EOD (End of Day)",
            "task_id": task_id,
            "message": "EOD cycle initiated asynchronously across cluster."
        })
    except Exception as e:
        _record_cron_run("EOD_06PM", "ERROR", {"error": str(e)})
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/bank_core_seed/status")
async def cron_bank_core_seed_status():
    """Read-only proof of the bank source seed and the bank layer builds."""
    from app.core import bank_core_seed, bank_layers
    from app.core.bigquery_aws_pipeline import last_run

    try:
        seed_state = bank_core_seed.status()
    except Exception as exc:
        seed_state = {"status": "error", "error": str(exc)[:200]}
    try:
        layers = bank_layers.status()
    except Exception as exc:
        layers = {"status": "error", "error": str(exc)[:200]}
    return JSONResponse(content={
        "status": "ONLINE",
        "seed": seed_state,
        "layers": layers,
        "last_run": last_run(),
    })


@router.get("/bank_core_seed")
@router.post("/bank_core_seed")
async def cron_bank_core_seed(request: Request):
    """Seed the bank source tables (49 tables x rows) into BigQuery and SFTP.

    Writes to GCP, S3 and Snowflake, so it needs the automation secret exactly
    like the batch cycles do.
    """
    if not _automation_authorised(request):
        return JSONResponse(status_code=403, content={
            "success": False,
            "error": "Automation credentials required.",
        })
    from app.core import bank_core_seed

    try:
        rows = int(request.query_params.get("rows") or bank_core_seed.model.ROWS_PER_TABLE)
    except ValueError:
        return JSONResponse(status_code=400, content={"success": False, "error": "rows must be an integer."})
    if rows < 1 or rows > 1000:
        return JSONResponse(status_code=400, content={"success": False, "error": "rows must be between 1 and 1000."})
    include_sftp = (request.query_params.get("sftp") or "1").lower() in ("1", "true", "yes")

    result = bank_core_seed.start(rows=rows, include_sftp=include_sftp)
    _record_cron_run("BANK_CORE_SEED", result.get("status", "").upper(),
                     {"rows": rows, "include_sftp": include_sftp, "message": result.get("message")})
    return JSONResponse(
        status_code=202 if result.get("status") == "started" else 200,
        content={
            "success": result.get("status") == "started",
            "status": result.get("status"),
            "rows_per_table": rows,
            "include_sftp": include_sftp,
            "message": result.get("message") or "Bank core seed started; poll /api/cron/bank_core_seed/status.",
        },
    )


@router.get("/bigquery_to_aws/status")
async def cron_bigquery_to_aws_status():
    """Read-only proof of the automation: last export run and scheduler state."""
    from app.core.bigquery_aws_pipeline import last_run
    from app.core.bq_export_scheduler import STATE, _enabled, _interval_seconds

    return JSONResponse(content={
        "status": "ONLINE",
        "scheduler": {
            "armed": bool(STATE.get("armed")),
            "enabled": _enabled(),
            "interval_min": _interval_seconds() // 60,
            "last_attempt": STATE.get("last_attempt"),
        },
        "last_run": last_run(),
        "snowflake": STATE.get("snowflake") or {},
        "duckdb": STATE.get("duckdb") or {},
        "recent_executions": [r for r in CRON_AUDIT_LOGS if str(r.get("job_name", "")).startswith("BQ2AWS")][:10],
    })


@router.get("/bigquery_to_aws")
@router.post("/bigquery_to_aws")
async def cron_bigquery_to_aws(request: Request):
    """Automation trigger: export every BigQuery dataset (minus nanopro_studio) to AWS.

    Dispatches in the background so an external scheduler (EventBridge, cron-job.org,
    Cloudflare Worker) gets an immediate 202 and never hits a gateway timeout.
    Unauthenticated callers may use ``?auto=1`` at most once every 10 minutes; the
    export is idempotent, so this only bounds CPU abuse.
    """
    if not _automation_authorised(request):
        auto = (request.query_params.get("auto") or "").lower() in ("1", "true", "yes")
        now = time.time()
        with _AUTO_LOCK:
            if not auto:
                return JSONResponse(status_code=403, content={"success": False, "error": "Automation credentials required."})
            if now - _AUTO_LOCK["at"] < AUTO_MIN_SECONDS:
                return JSONResponse(status_code=429, content={"success": False, "error": "Automated export already ran recently."})
            _AUTO_LOCK["at"] = now

    from app.core.bq_export_scheduler import run_once

    start = time.time()
    job_key = "BQ2AWS_" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())

    def worker():
        try:
            result = run_once()
            _record_cron_run(job_key, str(result.get("status") or "").upper(), {
                "summary": result.get("summary"),
                "tables": len(result.get("tables") or []),
                "rows": result.get("rows"),
                "duration_s": round(time.time() - start, 2),
            })
            log_event(f"[CronGateway] {job_key}: {result.get('summary')}", component="CronGateway")
        except Exception as exc:
            _record_cron_run(job_key, "ERROR", {"error": str(exc)[:300]})
            log_event(f"[CronGateway] {job_key} failed: {exc}", component="CronGateway")

    threading.Thread(target=worker, daemon=True).start()
    return JSONResponse(status_code=202, content={
        "success": True,
        "status": "DISPATCHED_IN_BACKGROUND",
        "job": job_key,
        "message": "BigQuery to AWS export started; results land in the cron audit ledger.",
    })

@router.get("/pipeline/status")
async def pipeline_batch_status():
    """Batch ledger: today's BOD/SOD/T1/EOD state plus the last export run."""
    from app.core import bank_batch_cycles
    from app.core.bigquery_aws_pipeline import last_run
    from app.core.bq_export_scheduler import STATE as SCHED_STATE, _interval_seconds

    try:
        batch = bank_batch_cycles.status()
    except Exception as exc:
        batch = {"status": "error", "error": str(exc)[:200]}
    return JSONResponse(content={
        "status": "ONLINE",
        "batch": batch,
        "scheduler": {
            "armed": bool(SCHED_STATE.get("armed")),
            "interval_min": _interval_seconds() // 60,
            "last_attempt": SCHED_STATE.get("last_attempt"),
        },
        "last_export": last_run(),
        "recent_executions": [r for r in CRON_AUDIT_LOGS if str(r.get("job_name", "")).endswith("_BATCH")][:10],
    })


@router.get("/pipeline/{cycle}")
@router.post("/pipeline/{cycle}")
async def pipeline_batch_trigger(cycle: str, request: Request):
    """Run one bank batch cycle (BOD/SOD/T1/EOD) in the background.

    Each cycle refreshes BigQuery → S3/Glue/Iceberg → Snowflake L0/L1/L2 → DuckDB
    and writes its outcome to BANK_DB.L2_CURATED.BATCH_CONTROL.
    """
    from app.core import bank_batch_cycles

    cycle = str(cycle or "").upper()
    if cycle not in bank_batch_cycles.CYCLES:
        return JSONResponse(status_code=404, content={
            "success": False,
            "error": f"Unknown cycle '{cycle}'. Expected BOD, SOD, T1 or EOD.",
        })
    if not _automation_authorised(request):
        return JSONResponse(status_code=403, content={
            "success": False,
            "error": "Automation credentials required.",
        })
    if bank_batch_cycles.is_running():
        return JSONResponse(status_code=429, content={
            "success": False,
            "error": "A batch cycle is already running.",
        })

    def worker():
        try:
            bank_batch_cycles.run(cycle, trigger="api")
        except Exception as exc:
            _record_cron_run(f"{cycle}_BATCH", "ERROR", {"error": str(exc)[:300]})
            log_event(f"[CronGateway] {cycle} batch failed: {exc}", component="CronGateway")

    threading.Thread(target=worker, daemon=True).start()
    return JSONResponse(status_code=202, content={
        "success": True,
        "status": "DISPATCHED_IN_BACKGROUND",
        "cycle": cycle,
        "label": bank_batch_cycles.CYCLES[cycle]["label"],
        "message": f"{cycle} cycle started; the ledger row lands in L2_CURATED.BATCH_CONTROL.",
    })


@router.get("/status")
async def cron_gateway_status():
    """Returns status and configuration guide for cron-job.org console."""
    base_url = "https://mangesh-nanopro.workers.dev"  # Master Cloudflare Gateway URL
    return JSONResponse(content={
        "status": "ONLINE",
        "current_node": cluster_mesh.node_id,
        "cron_console": "https://console.cron-job.org/dashboard",
        "suggested_schedules": [
            {
                "title": "NanoPro 24/7 Keep-Alive",
                "url": f"{base_url}/api/cron/keepalive",
                "schedule": "Every 14 minutes",
                "method": "GET",
                "purpose": "Prevents cloud sleep & cold start with zero bandwidth penalty"
            },
            {
                "title": "NanoPro BOD 06:00 AM IST",
                "url": f"{base_url}/api/cron/bod",
                "schedule": "0 6 * * * (06:00 AM IST)",
                "method": "POST",
                "purpose": "Autonomous Full Load & Opening Position Check"
            },
            {
                "title": "NanoPro SOD 08:00 AM IST",
                "url": f"{base_url}/api/cron/sod",
                "schedule": "0 8 * * * (08:00 AM IST)",
                "method": "POST",
                "purpose": "Start of Day Incremental Limits & Feeds"
            },
            {
                "title": "NanoPro T-1 10:00 AM IST",
                "url": f"{base_url}/api/cron/t1",
                "schedule": "0 10 * * * (10:00 AM IST)",
                "method": "POST",
                "purpose": "Daily T-1 Transaction Reconciliation"
            },
            {
                "title": "NanoPro EOD 06:00 PM IST",
                "url": f"{base_url}/api/cron/eod",
                "schedule": "0 18 * * * (06:00 PM IST)",
                "method": "POST",
                "purpose": "Daily Trial Balance & Executive Multi-Channel Dispatch"
            },
            {
                "title": "NanoPro BigQuery → AWS Bronze Export",
                "url": f"{base_url}/api/cron/bigquery_to_aws",
                "schedule": "Every 15 minutes",
                "method": "POST",
                "purpose": "Automatic BigQuery → S3/Glue/Iceberg export for every dataset except nanopro_studio"
            }
        ],
        "recent_executions": CRON_AUDIT_LOGS
    })
