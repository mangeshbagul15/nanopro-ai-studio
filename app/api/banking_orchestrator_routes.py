"""FastAPI router for NanoPro Banking Orchestrator and SFTP Reports."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app.core.banking_lakehouse_engine import banking_engine

router = APIRouter(prefix="/api/banking", tags=["BankingOrchestrator"])


class TriggerDagRequest(BaseModel):
    project_id: str
    load_type: str = "INCREMENTAL_LOAD"  # FULL_LOAD, INCREMENTAL_LOAD, CUT_PARTITION
    mode: str = "APPEND"  # APPEND, TRUNCATE_RELOAD


class RollbackLayerRequest(BaseModel):
    project_id: str
    target_layer: str = "L1_HARMONIZED"  # L1_HARMONIZED, L0_STAGING


class UpdateDagRequest(BaseModel):
    project_id: str
    schedule_time: Optional[str] = None
    schedule_period: Optional[str] = None
    load_type: Optional[str] = None
    status: Optional[str] = None


class PauseDagRequest(BaseModel):
    project_id: str


class DeleteDagRequest(BaseModel):
    project_id: str


class AddRecipientRequest(BaseModel):
    email: str


class RemoveRecipientRequest(BaseModel):
    email: str


# -------------------------------------------------------------
# DAG Endpoints
# -------------------------------------------------------------
@router.get("/dag/list")
async def list_banking_dags():
    """Lists all 8 Banking DAGs with Medallion task status and execution metrics."""
    return JSONResponse({
        "status": "success",
        "dags": banking_engine.list_dags(),
        "schedules": {
            "BOD": "06:00 IST (Sanity & Full Load)",
            "SOD": "08:30 IST (Intraday & Limit Sync)",
            "EOD": "20:00 IST (Daily T-1 Reconciliation & Reports)"
        }
    })


@router.post("/dag/update")
async def update_banking_dag(req: UpdateDagRequest):
    """Edits DAG schedule, execution time, mode, or status."""
    try:
        res = banking_engine.update_dag(
            project_id=req.project_id,
            schedule_time=req.schedule_time,
            schedule_period=req.schedule_period,
            load_type=req.load_type,
            status=req.status
        )
        return JSONResponse({"status": "success", "result": res})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/dag/pause")
async def pause_banking_dag(req: PauseDagRequest):
    """Toggles pause/resume state of a DAG."""
    try:
        res = banking_engine.pause_dag(project_id=req.project_id)
        return JSONResponse({"status": "success", "result": res})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/dag/delete")
async def delete_banking_dag(req: DeleteDagRequest):
    """Deletes a DAG from active schedule."""
    try:
        res = banking_engine.delete_dag(project_id=req.project_id)
        return JSONResponse({"status": "success", "result": res})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/dag/reset_defaults")
async def reset_default_dags():
    """Resets all 8 Banking DAGs to default configuration."""
    res = banking_engine.reset_default_dags()
    return JSONResponse({"status": "success", "result": res})


@router.post("/dag/trigger")
async def trigger_banking_dag(req: TriggerDagRequest):
    """Manually triggers a banking pipeline DAG run."""
    try:
        result = banking_engine.trigger_dag(
            project_id=req.project_id,
            load_type=req.load_type,
            mode=req.mode
        )
        return JSONResponse({"status": "success", "result": result})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/dag/rollback")
async def rollback_banking_layer(req: RollbackLayerRequest):
    """Rolls back project state to a clean layer watermark."""
    try:
        result = banking_engine.rollback_layer(
            project_id=req.project_id,
            target_layer=req.target_layer
        )
        return JSONResponse({"status": "success", "result": result})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# -------------------------------------------------------------
# Dynamic Email Recipient Management
# -------------------------------------------------------------
@router.get("/recipients")
async def get_recipients():
    """Gets configured email recipients, telegram handle, and whatsapp dispatch status."""
    return JSONResponse({
        "status": "success",
        "config": banking_engine.get_recipients()
    })


@router.post("/recipients/add")
async def add_recipient(req: AddRecipientRequest):
    """Dynamically adds an email recipient for EOD Excel reports."""
    try:
        conf = banking_engine.add_recipient(req.email)
        return JSONResponse({"status": "success", "config": conf})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/recipients/remove")
async def remove_recipient(req: RemoveRecipientRequest):
    """Dynamically removes an email recipient."""
    try:
        conf = banking_engine.remove_recipient(req.email)
        return JSONResponse({"status": "success", "config": conf})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/notifications/logs")
async def get_notification_logs():
    """Gets chronological audit trail of dispatched emails, WhatsApp alerts, and Telegram bots."""
    return JSONResponse({
        "status": "success",
        "logs": banking_engine.get_notification_logs()
    })


# -------------------------------------------------------------
# Multi-Platform Dynamic Live Logs Stream
# -------------------------------------------------------------
@router.get("/logs/stream")
async def get_platform_logs(platform: str = Query("all", description="aws_s3, snowflake, bigquery, duckdb, notifications, or all")):
    """Gets live stream of platform execution logs."""
    return JSONResponse({
        "status": "success",
        "platform": platform,
        "logs": banking_engine.get_platform_logs(platform=platform)
    })


# -------------------------------------------------------------
# SFTP Reports & Downloads
# -------------------------------------------------------------
@router.get("/sftp/reports/list")
async def list_sftp_reports():
    """Lists all generated business reports in the outbound SFTP folder."""
    return JSONResponse({
        "status": "success",
        "reports": banking_engine.list_sftp_reports(),
        "sftp_connection": {
            "protocol": "SFTP",
            "host": "nanopro-studio.onrender.com",
            "port": 22,
            "username": "mangeshbagul15",
            "inbound_path": "/data/sftp/inbound/",
            "outbound_path": "/data/sftp/outbound/reports/"
        }
    })


@router.get("/sftp/reports/download")
async def download_sftp_report(filename: str = Query(..., description="Report filename")):
    """Direct 1-click web download for genuine business Excel (.xlsx) reports."""
    report_file = banking_engine.sftp_outbound / filename
    if not report_file.exists():
        # Fallback to default date
        alt_name = filename.split("_EOD")[0] + "_EOD_T1_20261112.xlsx"
        alt_file = banking_engine.sftp_outbound / alt_name
        if alt_file.exists():
            report_file = alt_file
        else:
            raise HTTPException(status_code=404, detail="Requested report file not found on SFTP storage.")

    return FileResponse(
        path=str(report_file),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
