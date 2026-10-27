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

import time
from typing import Dict, Any
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.logger import log_event
from app.core.cluster_mesh_engine import cluster_mesh
from app.core.etl_automation_pipeline import etl_pipeline

router = APIRouter(prefix="/api/cron", tags=["CronJobOrgGateway"])

CRON_AUDIT_LOGS = []

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
    log_event("[CronGateway] External BOD Webhook triggered from cron-job.org.", component="CronGateway")
    start = time.time()
    try:
        # Enqueue into cluster mesh for distributed execution
        task_id = cluster_mesh.enqueue_task("BOD_CYCLE", {"source": "cron-job.org", "timestamp": start}, priority=10)
        res = etl_pipeline.run_bod_cycle()
        _record_cron_run("BOD_06AM", "SUCCESS", {"task_id": task_id, "duration_s": round(time.time() - start, 2)})
        return JSONResponse(content={
            "success": True,
            "cycle": "BOD (Beginning of Day)",
            "task_id": task_id,
            "result": res
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
    log_event("[CronGateway] External SOD Webhook triggered from cron-job.org.", component="CronGateway")
    start = time.time()
    try:
        task_id = cluster_mesh.enqueue_task("SOD_CYCLE", {"source": "cron-job.org", "timestamp": start}, priority=8)
        res = etl_pipeline.run_sod_cycle()
        _record_cron_run("SOD_08AM", "SUCCESS", {"task_id": task_id, "duration_s": round(time.time() - start, 2)})
        return JSONResponse(content={
            "success": True,
            "cycle": "SOD (Start of Day)",
            "task_id": task_id,
            "result": res
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
    log_event("[CronGateway] External T-1 Webhook triggered from cron-job.org.", component="CronGateway")
    start = time.time()
    try:
        task_id = cluster_mesh.enqueue_task("T1_CYCLE", {"source": "cron-job.org", "timestamp": start}, priority=7)
        res = etl_pipeline.run_incremental_cycle()
        _record_cron_run("T1_10AM", "SUCCESS", {"task_id": task_id, "duration_s": round(time.time() - start, 2)})
        return JSONResponse(content={
            "success": True,
            "cycle": "T-1 (Daily Delta)",
            "task_id": task_id,
            "result": res
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
    log_event("[CronGateway] External EOD Webhook triggered from cron-job.org.", component="CronGateway")
    start = time.time()
    try:
        task_id = cluster_mesh.enqueue_task("EOD_CYCLE", {"source": "cron-job.org", "timestamp": start}, priority=10)
        res = etl_pipeline.run_eod_cycle()
        _record_cron_run("EOD_06PM", "SUCCESS", {"task_id": task_id, "duration_s": round(time.time() - start, 2)})
        return JSONResponse(content={
            "success": True,
            "cycle": "EOD (End of Day)",
            "task_id": task_id,
            "result": res
        })
    except Exception as e:
        _record_cron_run("EOD_06PM", "ERROR", {"error": str(e)})
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

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
            }
        ],
        "recent_executions": CRON_AUDIT_LOGS
    })
