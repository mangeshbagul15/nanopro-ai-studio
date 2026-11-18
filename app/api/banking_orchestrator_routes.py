"""FastAPI router for the real NanoPro pipeline orchestrator."""
from __future__ import annotations

import threading
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/banking", tags=["Orchestrator"])


class OrchestratorRunRequest(BaseModel):
    dag_id: str
    mode: str = "incremental"


class OrchestratorPauseRequest(BaseModel):
    dag_id: str


class OrchestratorRollbackRequest(BaseModel):
    dag_id: str
    target_layer: str = ""
    confirm: bool = False


class OrchestratorScheduleRequest(BaseModel):
    cycle: str
    at: str


class SftpProcessRequest(BaseModel):
    force: bool = False


class SftpRollbackRequest(BaseModel):
    key: str
    confirm: bool = False
    delete_landing: bool = False


class AlertConfigRequest(BaseModel):
    recipients: Optional[List[str]] = None
    sender: Optional[str] = None
    telegram_channel: Optional[str] = None
    telegram_enabled: Optional[bool] = None
    whatsapp_number: Optional[str] = None
    whatsapp_enabled: Optional[bool] = None


class AlertTestRequest(BaseModel):
    channel: str


class ReportBuildRequest(BaseModel):
    cycle: str = "MANUAL"
    deliver: bool = False


# -------------------------------------------------------------
# Live DAG overview + controls
# -------------------------------------------------------------
@router.get("/orchestrator/overview")
def orchestrator_overview():
    """Live DAG status, batch cycles, SFTP landing/outbound and alert state."""
    from app.core import pipeline_orchestrator

    return JSONResponse(pipeline_orchestrator.overview())


@router.post("/orchestrator/dag/run")
def orchestrator_run(req: OrchestratorRunRequest):
    from app.core import pipeline_orchestrator

    try:
        return JSONResponse(pipeline_orchestrator.run(req.dag_id, mode=req.mode))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/orchestrator/dag/pause")
def orchestrator_pause(req: OrchestratorPauseRequest):
    from app.core import pipeline_orchestrator

    try:
        return JSONResponse(pipeline_orchestrator.pause(req.dag_id))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/orchestrator/dag/rollback")
def orchestrator_rollback(req: OrchestratorRollbackRequest):
    from app.core import pipeline_orchestrator

    try:
        return JSONResponse(pipeline_orchestrator.rollback(
            req.dag_id, target_layer=req.target_layer, confirm=req.confirm))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/orchestrator/schedule")
def orchestrator_schedule(req: OrchestratorScheduleRequest):
    from app.core import pipeline_orchestrator

    try:
        return JSONResponse(pipeline_orchestrator.set_schedule(req.cycle, req.at))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# -------------------------------------------------------------
# SFTP inbound (source files)
# -------------------------------------------------------------
@router.get("/orchestrator/sftp/status")
def orchestrator_sftp_status():
    from app.core import sftp_ingestion

    return JSONResponse(sftp_ingestion.status())


@router.post("/orchestrator/sftp/upload")
async def orchestrator_sftp_upload(file: UploadFile = File(...), partner: str = Query("manual")):
    from app.core import sftp_ingestion

    data = await file.read()
    try:
        result = sftp_ingestion.upload(file.filename or "upload.csv", data, partner=partner)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    processed = sftp_ingestion.ingest(result["key"])
    result["ingest"] = processed
    if processed.get("status") == "success":
        threading.Thread(target=sftp_ingestion.refresh_downstream, daemon=True,
                         name="sftp-downstream").start()
    return JSONResponse(result)


@router.post("/orchestrator/sftp/process")
def orchestrator_sftp_process(req: SftpProcessRequest):
    from app.core import sftp_ingestion

    return JSONResponse(sftp_ingestion.poll(force=req.force))


@router.post("/orchestrator/sftp/sample")
def orchestrator_sftp_sample(partner: str = Query("sample")):
    from app.core import sftp_ingestion

    result = sftp_ingestion.sample_file(partner=partner)
    result["ingest"] = sftp_ingestion.ingest(result["key"])
    if result["ingest"].get("status") == "success":
        threading.Thread(target=sftp_ingestion.refresh_downstream, daemon=True,
                         name="sftp-downstream").start()
    return JSONResponse(result)


@router.post("/orchestrator/sftp/rollback")
def orchestrator_sftp_rollback(req: SftpRollbackRequest):
    from app.core import sftp_ingestion

    if not req.confirm:
        raise HTTPException(status_code=400, detail="Rollback requires confirm=true.")
    return JSONResponse(sftp_ingestion.purge(req.key, delete_landing=req.delete_landing))


# -------------------------------------------------------------
# SFTP outbound (final reports)
# -------------------------------------------------------------
@router.get("/orchestrator/sftp/outbound")
def orchestrator_sftp_outbound(limit: int = Query(40, ge=1, le=200)):
    from app.core import report_delivery

    return JSONResponse(report_delivery.list_outbound(limit=limit))


@router.post("/orchestrator/report/build")
def orchestrator_report_build(req: ReportBuildRequest):
    from app.core import report_delivery

    if req.deliver:
        return JSONResponse(report_delivery.deliver(cycle=req.cycle))
    return JSONResponse(report_delivery.build(cycle=req.cycle))


# -------------------------------------------------------------
# Alerts
# -------------------------------------------------------------
@router.get("/orchestrator/alerts/config")
def orchestrator_alert_config():
    from app.core import pipeline_alerts

    return JSONResponse({"status": "success", "config": pipeline_alerts.config()})


@router.post("/orchestrator/alerts/config")
def orchestrator_alert_config_save(req: AlertConfigRequest):
    from app.core import pipeline_alerts

    conf = pipeline_alerts.save_config(
        recipients=req.recipients,
        sender=req.sender,
        telegram_channel=req.telegram_channel,
        telegram_enabled=req.telegram_enabled,
        whatsapp_number=req.whatsapp_number,
        whatsapp_enabled=req.whatsapp_enabled,
    )
    return JSONResponse({"status": "success", "config": conf})


@router.post("/orchestrator/alerts/test")
def orchestrator_alert_test(req: AlertTestRequest):
    from app.core import pipeline_alerts

    try:
        return JSONResponse(pipeline_alerts.test_channel(req.channel))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/orchestrator/logs")
def orchestrator_logs(limit: int = Query(80, ge=10, le=300)):
    from app.core import pipeline_orchestrator

    return JSONResponse(pipeline_orchestrator.logs(limit=limit))
