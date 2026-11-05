"""HTTP API for the Data Modeling by AI workspace."""

from __future__ import annotations

import os

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

router = APIRouter(prefix="/api/data_modeling", tags=["DataModelingAI"])

MAX_UPLOAD_BYTES = 25 * 1024 * 1024


class WorkspaceCreateRequest(BaseModel):
    name: str = ""


class WorkspaceRenameRequest(BaseModel):
    name: str


class SchemaCreateRequest(BaseModel):
    name: str


class ChatRequest(BaseModel):
    workspace_id: str
    message: str


class SnowflakeCredentialsRequest(BaseModel):
    password: str


class ScheduleCreateRequest(BaseModel):
    workspace_id: str
    name: str = ""
    sql: str = ""
    steps: list = []
    frequency: str = "daily"
    at_time: str = ""
    weekday: int | None = None
    day_of_month: int | None = None
    cron: str = ""
    target: str = ""


class ScheduleToggleRequest(BaseModel):
    enabled: bool


def _session_user(request: Request) -> dict:
    token = (request.cookies.get("nanopro_session") or "").strip()
    if not token:
        auth_header = (request.headers.get("Authorization") or "").strip()
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Login required.")
    try:
        from app.core.auth_manager import auth_manager

        session = auth_manager.validate_session(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Session check failed: {exc}")
    if not session.get("is_valid") or not session.get("user"):
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    return session.get("user") or {}


def _user_label(user: dict) -> str:
    return str(user.get("username") or user.get("email") or "user")


def _error(message: str, status: int = 400) -> JSONResponse:
    return JSONResponse({"status": "error", "message": message}, status_code=status)


@router.get("/status")
def api_dm_status(request: Request):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    ai_ready = False
    model = "fallback"
    try:
        from app.core.model_adapter import model_manager

        ai_ready = bool(model_manager.groq.is_available() or model_manager.gemini.is_available())
        model = model_manager.get_primary_model()
    except Exception:
        pass
    return JSONResponse({
        "status": "success",
        "ai_ready": ai_ready,
        "model": model,
        "workspaces": len(dm.list_workspaces()),
        "databases": len(dm.catalog_snapshot()),
        "schedules": len(dm.list_schedules()),
        "fast_nlu": True,
    })


@router.get("/workspaces")
def api_dm_workspaces(request: Request):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    return JSONResponse({"status": "success", "workspaces": dm.list_workspaces()})


@router.post("/workspaces")
def api_dm_create_workspace(req: WorkspaceCreateRequest, request: Request):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        ws = dm.create_workspace(req.name, _user_label(user))
    except Exception as exc:
        return _error(str(exc))
    return JSONResponse({"status": "success", "workspace": ws})


@router.patch("/workspaces/{workspace_id}")
def api_dm_rename_workspace(workspace_id: str, req: WorkspaceRenameRequest, request: Request):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        ws = dm.rename_workspace(workspace_id, req.name)
    except Exception as exc:
        return _error(str(exc))
    return JSONResponse({"status": "success", "workspace": ws})


@router.get("/workspaces/{workspace_id}/messages")
def api_dm_messages(workspace_id: str, request: Request, limit: int = 300):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    if not dm.get_workspace(workspace_id):
        return _error("Workspace not found.", 404)
    return JSONResponse({"status": "success", "messages": dm.get_messages(workspace_id, limit)})


@router.post("/workspaces/{workspace_id}/schemas")
def api_dm_create_schema(workspace_id: str, req: SchemaCreateRequest, request: Request):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        schema = dm.create_schema(workspace_id, req.name)
    except Exception as exc:
        return _error(str(exc))
    return JSONResponse({"status": "success", "schema": schema, "workspace": dm.get_workspace(workspace_id)})


@router.get("/catalog")
def api_dm_catalog(request: Request, refresh: bool = False):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    if refresh:
        dm.invalidate_catalog()
    return JSONResponse({"status": "success", "databases": dm.catalog_snapshot(ttl=0 if refresh else 8.0)})


@router.get("/table")
def api_dm_table(request: Request, db_id: str, table: str, schema: str = "main"):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        details = dm.get_table_details(db_id, schema, table)
    except Exception as exc:
        return _error(str(exc))
    return JSONResponse({"status": "success", "table": details})


@router.post("/chat")
def api_dm_chat(req: ChatRequest, request: Request):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        result = dm.chat(req.workspace_id, req.message, _user_label(user))
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:
        return _error(f"Data copilot failed: {exc}", 500)
    return JSONResponse(result)


@router.get("/schedules")
def api_dm_schedules(request: Request, workspace_id: str = ""):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    return JSONResponse({"status": "success", "schedules": dm.list_schedules(workspace_id)})


@router.post("/schedules")
def api_dm_create_schedule(req: ScheduleCreateRequest, request: Request):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm

    steps = req.steps or ([req.sql] if req.sql else [])
    try:
        schedule = dm.create_schedule(
            req.workspace_id,
            name=req.name,
            statements=steps,
            frequency=req.frequency,
            at_time=req.at_time,
            weekday=req.weekday,
            day_of_month=req.day_of_month,
            cron_expr=req.cron,
            target=req.target,
            user=_user_label(user),
        )
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:
        return _error(f"Could not create the schedule: {exc}", 500)
    return JSONResponse({"status": "success", "schedule": schedule, "summary": dm.describe_schedule(schedule)})


@router.patch("/schedules/{schedule_id}")
def api_dm_toggle_schedule(schedule_id: str, req: ScheduleToggleRequest, request: Request):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        schedule = dm.set_schedule_enabled(schedule_id, req.enabled)
    except ValueError as exc:
        return _error(str(exc), 404)
    return JSONResponse({"status": "success", "schedule": schedule})


@router.post("/schedules/{schedule_id}/run")
def api_dm_run_schedule(schedule_id: str, request: Request):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        result = dm.run_schedule(schedule_id)
    except ValueError as exc:
        return _error(str(exc), 404)
    except Exception as exc:
        return _error(f"Scheduled job failed: {exc}", 500)
    return JSONResponse(result)


@router.get("/schedules/{schedule_id}/runs")
def api_dm_schedule_runs(schedule_id: str, request: Request, limit: int = 50):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    return JSONResponse({"status": "success", "runs": dm.schedule_runs(schedule_id, limit)})


@router.delete("/schedules/{schedule_id}")
def api_dm_delete_schedule(schedule_id: str, request: Request):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        result = dm.delete_schedule(schedule_id)
    except ValueError as exc:
        return _error(str(exc), 404)
    return JSONResponse({"status": "success", **result})


@router.post("/upload")
async def api_dm_upload(
    request: Request,
    file: UploadFile = File(...),
    workspace_id: str = Form(...),
    table_name: str = Form(""),
    mode: str = Form("create"),
    schema: str = Form("main"),
):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        return _error("File is larger than 25 MB.")
    try:
        result = dm.import_table(workspace_id, file.filename or "data.csv", content, table_name, mode, schema)
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:
        return _error(f"Import failed: {exc}", 500)
    return JSONResponse(result)


@router.get("/runs/{run_id}")
def api_dm_get_run(run_id: str, request: Request):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    run = dm.get_run(run_id)
    if not run:
        return _error("Result set not found.", 404)
    return JSONResponse({"status": "success", "run": run})


@router.get("/snowflake/status")
def api_dm_snowflake_status(request: Request):
    _session_user(request)
    from app.core import snowflake_client

    try:
        return JSONResponse({"status": "success", "snowflake": snowflake_client.status()})
    except Exception as exc:
        return JSONResponse({"status": "success", "snowflake": {"configured": False, "error": str(exc)[:200]}})


@router.post("/snowflake/credentials")
def api_dm_snowflake_credentials(req: SnowflakeCredentialsRequest, request: Request):
    _session_user(request)
    password = (req.password or "").strip()
    if not password:
        return _error("Snowflake password cannot be empty.")
    try:
        from app.core.connection_manager import connection_manager

        cfg = connection_manager.get_connection_config("NANO_PRO_SNOWFLAKE", mask=False) or {}
        meta = cfg.get("metadata") or {}
        connection_manager.save_connection_config(
            connection_name="NANO_PRO_SNOWFLAKE",
            service_type="database",
            username=cfg.get("username") or "",
            password=password,
            host=cfg.get("host") or "",
            port=str(cfg.get("port") or "443"),
            database_name=cfg.get("database_name") or "BANK_DB",
            metadata=meta,
        )
    except Exception as exc:
        return _error(f"Could not store the Snowflake password: {exc}", 500)
    from app.core import data_modeling_ai as dm
    from app.core import snowflake_client

    snowflake_client.clear_catalog_cache()
    dm.invalidate_catalog()
    return JSONResponse({"status": "success", "message": "Snowflake password saved in the Credential Vault."})


@router.post("/snowflake/setup")
def api_dm_snowflake_setup(request: Request):
    _session_user(request)
    from app.core import data_modeling_ai as dm
    from app.core import snowflake_bootstrap, snowflake_client

    try:
        result = snowflake_bootstrap.ensure_structure()
    except snowflake_client.SnowflakeUnavailable as exc:
        return _error(str(exc), 400)
    except Exception as exc:
        return _error(f"Snowflake setup failed: {exc}", 500)
    dm.invalidate_catalog()
    snowflake_client.clear_catalog_cache()
    return JSONResponse(result)


@router.get("/runs/{run_id}/download")
def api_dm_download(run_id: str, request: Request):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        filename, text = dm.run_to_csv(run_id)
    except Exception as exc:
        return _error(str(exc), 404)
    return Response(
        content=text,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _start_dm_scheduler() -> None:
    if os.environ.get("DM_SCHEDULER", "1").strip().lower() in ("0", "false", "off", "no"):
        return
    try:
        from app.core import data_modeling_ai as dm

        dm.start_scheduler()
    except Exception:
        pass


_start_dm_scheduler()
