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


class CycleRunRequest(BaseModel):
    cycle: str = "EOD"


class BankCoreSeedRequest(BaseModel):
    rows: int = 100
    include_sftp: bool = True
    confirm: bool = False


class BankLayersBuildRequest(BaseModel):
    stage: str = "all"
    confirm: bool = False


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


@router.post("/orchestrator/cycle/run")
def orchestrator_cycle_run(req: CycleRunRequest):
    """Runs one BOD/SOD/T1/EOD batch cycle (BQ -> S3 -> Snowflake -> DuckDB -> report/alerts)."""
    from app.core import bank_batch_cycles

    cycle = str(req.cycle or "").upper()
    if cycle not in bank_batch_cycles.CYCLES:
        raise HTTPException(status_code=400,
                            detail=f"Unknown cycle '{cycle}'. Expected {', '.join(bank_batch_cycles.CYCLES)}.")
    if bank_batch_cycles.is_running():
        raise HTTPException(status_code=409, detail="A batch cycle is already running.")

    threading.Thread(target=bank_batch_cycles.run, args=(cycle,), kwargs={"trigger": "ui"},
                     daemon=True, name=f"batch-{cycle.lower()}").start()
    return JSONResponse({
        "status": "dispatched",
        "cycle": cycle,
        "label": bank_batch_cycles.CYCLES[cycle]["label"],
        "message": f"{cycle} cycle started in the background. Refresh the orchestrator in a few minutes.",
    })


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


# -------------------------------------------------------------
# Bank core source model (BigQuery + SFTP)
# -------------------------------------------------------------
@router.get("/bank_core/model")
def bank_core_model():
    """Every source table/column the 43 bank reports need, with lane and keys."""
    from app.core import bank_core_model

    return JSONResponse(bank_core_model.summary())


@router.get("/bank_core/status")
def bank_core_status():
    from app.core import bank_core_seed

    return JSONResponse(bank_core_seed.status())


@router.post("/bank_core/seed")
def bank_core_seed(req: BankCoreSeedRequest):
    from app.core import bank_core_seed

    if not req.confirm:
        raise HTTPException(status_code=400,
                            detail="Seeding rewrites the bank-core tables; send confirm=true.")
    if req.rows < 1 or req.rows > 1000:
        raise HTTPException(status_code=400, detail="rows must be between 1 and 1000.")
    return JSONResponse(bank_core_seed.start(rows=req.rows, include_sftp=req.include_sftp))


@router.get("/bank_core/layers")
def bank_core_layers():
    """Static catalogue + last build status for the bank warehouse layers."""
    from app.core import bank_layers

    return JSONResponse({"layers": bank_layers.status(),
                         "catalogue": bank_layers.catalogue()})


@router.post("/bank_core/layers/build")
def bank_core_layers_build(req: BankLayersBuildRequest):
    from app.core import bank_layers

    if not req.confirm:
        raise HTTPException(status_code=400,
                            detail="Layer builds replace L1/L2/RPT tables; send confirm=true.")
    stage = str(req.stage or "all").lower()
    if stage not in ("all", "raw", "l1", "star", "rpt"):
        raise HTTPException(status_code=400,
                            detail="stage must be one of all, raw, l1, star, rpt.")
    threading.Thread(target=bank_layers.build, args=(stage, "api"), daemon=True,
                     name=f"bank-layers-{stage}").start()
    return JSONResponse({"status": "started", "stage": stage})
