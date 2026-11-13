"""FastAPI router for NanoPro Banking Orchestrator and SFTP Reports."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

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
    """Direct 1-click web download for business Excel reports."""
    report_file = banking_engine.sftp_outbound / filename
    if not report_file.exists():
        raise HTTPException(status_code=404, detail="Requested report file not found on SFTP storage.")

    return FileResponse(
        path=str(report_file),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
