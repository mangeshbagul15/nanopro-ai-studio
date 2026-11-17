"""HTTP API for the Data Modeling by AI workspace."""

from __future__ import annotations

import concurrent.futures
import os

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

router = APIRouter(prefix="/api/data_modeling", tags=["DataModelingAI"])

MAX_UPLOAD_BYTES = 25 * 1024 * 1024


class WorkspaceCreateRequest(BaseModel):
    name: str = ""
    project_id: str = ""


class WorkspaceRenameRequest(BaseModel):
    name: str


class WorkspacePinRequest(BaseModel):
    pinned: bool = True


class WorkspaceProjectRequest(BaseModel):
    project_id: str = ""


class ProjectCreateRequest(BaseModel):
    name: str = ""


class ProjectRenameRequest(BaseModel):
    name: str


class SchemaCreateRequest(BaseModel):
    name: str


class ChatAttachmentRef(BaseModel):
    attachment_id: str


class ChatContext(BaseModel):
    db_id: str = ""
    schema: str = ""
    table: str = ""


class ChatRequest(BaseModel):
    workspace_id: str
    message: str = ""
    attachments: list[ChatAttachmentRef] = []
    context: ChatContext | None = None


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


class AmlRunRequest(BaseModel):
    mode: str = "FULL"
    wait_seconds: int = 60


class ScheduleToggleRequest(BaseModel):    enabled: bool


def _session_user(request: Request) -> dict:
    from app.core.api_auth import extract_session_token

    token = extract_session_token(request).strip()
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
    from app.core.identity_resolver import resolve_canonical_username
    uid = str(user.get("username") or user.get("id") or user.get("email") or "user")
    return resolve_canonical_username(uid)


def _error(message: str, status: int = 400) -> JSONResponse:
    return JSONResponse({"status": "error", "message": message}, status_code=status)


def _visible_databases(databases: list, user_label: str) -> list:
    """Hide other users' workspaces from the catalog while keeping shared DBs."""
    from app.core import data_modeling_ai as dm

    try:
        allowed = {w["id"] for w in dm.list_workspaces(user=user_label, light=True)}
    except Exception:
        return databases
    return [
        entry
        for entry in databases
        if entry.get("kind") != "workspace" or entry.get("workspace_id") in allowed
    ]


def _owned_workspace(db_id: str, user_label: str):
    from app.core import data_modeling_ai as dm

    if not db_id.startswith("workspace:"):
        return None
    return dm.get_workspace(db_id.split(":", 1)[1], user=user_label)


def _require_workspace(workspace_id: str, user_label: str) -> bool:
    from app.core import data_modeling_ai as dm

    return bool(workspace_id) and bool(dm.get_workspace(workspace_id, user=user_label))


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


@router.get("/selfcheck")
def api_dm_selfcheck(request: Request, live: int = 0, workspace_id: str = ""):
    _session_user(request)
    from app.core.manager_contract import run_selfcheck

    try:
        report = run_selfcheck(live=bool(live), workspace_id=workspace_id)
    except Exception as exc:
        return _error(f"Self-check failed: {exc}", 500)
    return JSONResponse({"status": "success", **report})


@router.get("/workspaces")
def api_dm_workspaces(request: Request, light: bool = True):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm

    return JSONResponse({"status": "success", "workspaces": dm.list_workspaces(user=_user_label(user), light=light)})


@router.post("/workspaces")
def api_dm_create_workspace(req: WorkspaceCreateRequest, request: Request):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        ws = dm.create_workspace(req.name, _user_label(user), project_id=req.project_id)
    except Exception as exc:
        return _error(str(exc))
    return JSONResponse({"status": "success", "workspace": ws})


@router.patch("/workspaces/{workspace_id}")
def api_dm_rename_workspace(workspace_id: str, req: WorkspaceRenameRequest, request: Request):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        ws = dm.rename_workspace(workspace_id, req.name, user=_user_label(user))
    except Exception as exc:
        return _error(str(exc))
    return JSONResponse({"status": "success", "workspace": ws})


@router.post("/workspaces/{workspace_id}/pin")
def api_dm_pin_workspace(workspace_id: str, req: WorkspacePinRequest, request: Request):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        ws = dm.set_workspace_pinned(workspace_id, req.pinned, user=_user_label(user))
    except ValueError as exc:
        return _error(str(exc), 404)
    return JSONResponse({"status": "success", "workspace": ws})


@router.post("/workspaces/{workspace_id}/project")
def api_dm_move_workspace(workspace_id: str, req: WorkspaceProjectRequest, request: Request):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        ws = dm.set_workspace_project(workspace_id, req.project_id, user=_user_label(user))
    except ValueError as exc:
        return _error(str(exc), 404)
    return JSONResponse({"status": "success", "workspace": ws})


@router.delete("/workspaces/{workspace_id}")
def api_dm_delete_workspace(workspace_id: str, request: Request):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        result = dm.delete_workspace(workspace_id, user=_user_label(user))
    except ValueError as exc:
        return _error(str(exc), 404)
    except Exception as exc:
        return _error(f"Could not delete the chat: {exc}", 500)
    return JSONResponse({"status": "success", **result})


@router.get("/projects")
def api_dm_projects(request: Request):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm

    return JSONResponse({"status": "success", "projects": dm.list_projects(user=_user_label(user))})


@router.post("/projects")
def api_dm_create_project(req: ProjectCreateRequest, request: Request):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        project = dm.create_project(req.name, _user_label(user))
    except Exception as exc:
        return _error(str(exc))
    return JSONResponse({"status": "success", "project": project})


@router.patch("/projects/{project_id}")
def api_dm_rename_project(project_id: str, req: ProjectRenameRequest, request: Request):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        project = dm.rename_project(project_id, req.name, user=_user_label(user))
    except ValueError as exc:
        return _error(str(exc), 404)
    return JSONResponse({"status": "success", "project": project})


@router.delete("/projects/{project_id}")
def api_dm_delete_project(project_id: str, request: Request, delete_chats: bool = False):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        result = dm.delete_project(project_id, delete_chats=delete_chats, user=_user_label(user))
    except ValueError as exc:
        return _error(str(exc), 404)
    return JSONResponse({"status": "success", **result})


@router.get("/workspaces/{workspace_id}/messages")
def api_dm_messages(workspace_id: str, request: Request, limit: int = 300):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm
    user_label = _user_label(user)

    if not dm.get_workspace(workspace_id, user=user_label):
        return _error("Workspace not found.", 404)
    return JSONResponse({"status": "success", "messages": dm.get_messages(workspace_id, limit, user=user_label)})


@router.get("/active_state")
def api_dm_get_active_state(request: Request):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm
    state = dm.get_user_state(_user_label(user))
    return JSONResponse({"status": "success", **state})


@router.post("/workspaces/{workspace_id}/active")
def api_dm_set_active_workspace(workspace_id: str, request: Request):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm
    user_label = _user_label(user)
    ws = dm.get_workspace(workspace_id, user=user_label)
    if not ws:
        return _error("Workspace not found.", 404)
    dm.save_user_state(user_label, workspace_id, ws.get("project_id", ""))
    return JSONResponse({"status": "success", "active_workspace_id": workspace_id})


@router.get("/workspaces/{workspace_id}/export")
def api_dm_export_chat(workspace_id: str, request: Request):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm
    user_label = _user_label(user)
    if not _require_workspace(workspace_id, user_label):
        return _error("Workspace not found.", 404)
    export_data = dm.export_user_chat(user_label, workspace_id)
    return JSONResponse({"status": "success", "export": export_data})


@router.post("/workspaces/{workspace_id}/schemas")
def api_dm_create_schema(workspace_id: str, req: SchemaCreateRequest, request: Request):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm
    user_label = _user_label(user)
    if not _require_workspace(workspace_id, user_label):
        return _error("Workspace not found.", 404)

    try:
        schema = dm.create_schema(workspace_id, req.name)
    except Exception as exc:
        return _error(str(exc))
    return JSONResponse({"status": "success", "schema": schema, "workspace": dm.get_workspace(workspace_id, user=user_label)})


@router.get("/catalog")
def api_dm_catalog(request: Request, refresh: bool = False, fast: bool = False):
    user = _session_user(request)
    user_label = _user_label(user)
    from app.core import data_modeling_ai as dm

    if refresh:
        databases, scanning = dm.refresh_catalog_async()
        if not scanning:
            databases = dm.catalog_snapshot(ttl=0)
        return JSONResponse({"status": "success", "databases": _visible_databases(databases, user_label), "scanning": scanning})
    if fast:
        databases, scanning = dm.catalog_cached()
        return JSONResponse({"status": "success", "databases": _visible_databases(databases, user_label), "scanning": scanning})
    databases = dm.catalog_snapshot(ttl=0 if refresh else 8.0)
    return JSONResponse({"status": "success", "databases": _visible_databases(databases, user_label)})


@router.get("/table")
def api_dm_table(request: Request, db_id: str, table: str, schema: str = "main"):
    user = _session_user(request)
    user_label = _user_label(user)
    from app.core import data_modeling_ai as dm

    if db_id.startswith("workspace:") and not _owned_workspace(db_id, user_label):
        return _error("Database not found in catalog.", 404)
    try:
        details = dm.get_table_details(db_id, schema, table)
    except Exception as exc:
        return _error(str(exc))
    return JSONResponse({"status": "success", "table": details})


CHAT_DEADLINE_SECONDS = 90.0


@router.post("/chat")
def api_dm_chat(req: ChatRequest, request: Request):
    user = _session_user(request)
    from app.core import data_modeling_ai as dm

    user_label = _user_label(user)
    if req.workspace_id and not _require_workspace(req.workspace_id, user_label):
        return _error("Workspace not found.", 404)

    # A degraded provider must never hold the request open indefinitely: the
    # user message is already persisted, so the UI can recover the eventual
    # assistant reply by polling the workspace messages endpoint.
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="dm-chat")
    future = executor.submit(
        dm.chat,
        req.workspace_id,
        req.message,
        user_label,
        [item.dict() for item in req.attachments],
        req.context.dict() if req.context else None,
    )
    try:
        result = future.result(timeout=CHAT_DEADLINE_SECONDS)
    except concurrent.futures.TimeoutError:
        return _error(
            "The data copilot is taking longer than usual. Your message is saved and the reply will appear here when it finishes.",
            504,
        )
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:
        return _error(f"Data copilot failed: {exc}", 500)
    finally:
        executor.shutdown(wait=False, cancel_futures=True)
    return JSONResponse(result)


@router.post("/aml/run")
def api_aml_run(req: AmlRunRequest, request: Request):
    user = _session_user(request)
    from app.core import aml_lakehouse_pipeline as aml

    run = aml.start_run(req.mode, user=_user_label(user))
    if run.get("status") == "busy":
        return JSONResponse(run, status_code=409)
    if req.wait_seconds > 0:
        run = aml.wait_run(run["run_id"], timeout=min(float(req.wait_seconds), 85.0))
    run = aml.public_run(run) or {}
    return JSONResponse({"status": "success" if run.get("status") == "success" else run.get("status"), "run": run})


@router.get("/aml/status/{run_id}")
def api_aml_status(run_id: str, request: Request):
    _session_user(request)
    from app.core import aml_lakehouse_pipeline as aml

    run = aml.public_run(aml.get_run(run_id))
    if not run:
        return _error("AML pipeline run not found.", 404)
    return JSONResponse({"status": "success", "run": run})


@router.get("/aml/runs")
def api_aml_runs(request: Request, limit: int = 10):
    _session_user(request)
    from app.core import aml_lakehouse_pipeline as aml

    runs = [aml.public_run(r) for r in aml.list_runs(max(1, min(limit, 50)))]
    return JSONResponse({"status": "success", "runs": runs})


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
    user = _session_user(request)
    user_label = _user_label(user)
    if not _require_workspace(workspace_id, user_label):
        return _error("Workspace not found.", 404)
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


@router.post("/attachments")
async def api_dm_attachment(
    request: Request,
    file: UploadFile = File(...),
    workspace_id: str = Form(...),
):
    user = _session_user(request)
    user_label = _user_label(user)
    if not _require_workspace(workspace_id, user_label):
        return _error("Workspace not found.", 404)
    from app.core import data_modeling_ai as dm

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        return _error("File is larger than 25 MB.")
    try:
        info = dm.save_attachment(workspace_id, file.filename or "attachment", content)
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:
        return _error(f"Attachment failed: {exc}", 500)
    return JSONResponse({"status": "success", "attachment": info})


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
def api_dm_download(run_id: str, request: Request, format: str = "csv"):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        filename, content, media_type = dm.run_to_export(run_id, format)
    except Exception as exc:
        return _error(str(exc), 404)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/table/download")
def api_dm_table_download(
    request: Request,
    db_id: str,
    table: str,
    schema: str = "main",
    format: str = "csv",
):
    user = _session_user(request)
    user_label = _user_label(user)
    from app.core import data_modeling_ai as dm

    if db_id.startswith("workspace:") and not _owned_workspace(db_id, user_label):
        return _error("Database not found in catalog.", 404)
    try:
        filename, content, media_type = dm.table_to_export(db_id, schema, table, format)
    except Exception as exc:
        return _error(str(exc), 400)
    return Response(
        content=content,
        media_type=media_type,
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


@router.get("/persistence/status")
def persistence_status(request: Request):
    _session_user(request)
    from app.core import dm_persistence

    return {"status": "success", **dm_persistence.status()}


@router.post("/persistence/flush")
def persistence_flush(request: Request):
    _session_user(request)
    from app.core import dm_persistence

    return {"status": "success", **dm_persistence.snapshot_now()}


# ---------------------------------------------------------------------------
# Global AI Lab Explorer catalog
#
# The Explorer used to be answered with a hardcoded demo catalog. It now reads
# the same live introspection the Data Modeling catalog uses, so it can never
# show tables that do not exist.
# ---------------------------------------------------------------------------

explorer_router = APIRouter(prefix="/api/ai/explorer", tags=["Explorer"])

_EXPLORER_ENGINES = {
    "snowflake": "❄️",
    "bigquery": "☁️",
    "s3": "🪣",
    "duckdb": "🦆",
}

_HIDDEN_SCHEMA_NAMES = {"INFORMATION_SCHEMA", "SNOWFLAKE", "SNOWFLAKE_SAMPLE_DATA", "TELEMETRY"}


def _explorer_databases(catalog: list) -> list:
    databases = []
    for entry in catalog:
        engine = str(entry.get("engine") or "").lower()
        if engine not in _EXPLORER_ENGINES:
            continue
        schemas = []
        for schema in entry.get("schemas") or []:
            name = str(schema.get("name") or "").strip()
            if not name or any(part.strip().upper() in _HIDDEN_SCHEMA_NAMES for part in name.split(".")):
                continue
            tables = [
                {"name": str(table.get("name") or ""), "type": table.get("type") or "table", "rows": 0, "columns": []}
                for table in schema.get("tables") or []
                if str(table.get("name") or "").strip()
            ]
            schemas.append({"name": name, "tables": tables})
        databases.append({
            "id": entry.get("id") or engine,
            "name": entry.get("name") or engine.upper(),
            "kind": engine,
            "icon": _EXPLORER_ENGINES[engine],
            "status": entry.get("status") or "",
            "error": entry.get("error") or "",
            "schemas": schemas,
        })
    return databases


@explorer_router.get("/catalog")
def api_explorer_catalog(request: Request):
    _session_user(request)
    from app.core import data_modeling_ai as dm

    try:
        catalog = dm.catalog_snapshot(ttl=8.0)
    except Exception as exc:
        return JSONResponse({"status": "error", "message": str(exc)[:300]}, status_code=500)
    return JSONResponse({"status": "success", "databases": _explorer_databases(catalog)})


@explorer_router.get("/table")
def api_explorer_table(request: Request, database: str = "", schema: str = "main", table: str = ""):
    _session_user(request)
    if not table.strip():
        return JSONResponse({"status": "error", "message": "table is required"}, status_code=400)
    from app.core import data_modeling_ai as dm

    try:
        details = dm.get_table_details(database, schema, table)
    except Exception as exc:
        return JSONResponse({"status": "error", "message": str(exc)[:300]}, status_code=400)
    columns = [
        {
            "name": str(column.get("name") or ""),
            "type": str(column.get("data_type") or ""),
            "not_null": bool(column.get("not_null")),
            "key": "PK" if column.get("is_pk") else ("FK" if column.get("is_fk") else ""),
        }
        for column in details.get("columns") or []
    ]
    return JSONResponse({
        "status": "success",
        "columns": columns,
        "foreign_keys": details.get("foreign_keys") or [],
        "row_count": details.get("row_count"),
        "error": details.get("error") or "",
    })


class ExplorerRenameRequest(BaseModel):
    database: str = ""
    schema_name: str = ""
    table: str = ""
    column: str = ""
    new_name: str = ""


class ExplorerDeleteRequest(BaseModel):
    database: str = ""
    schema_name: str = ""
    table: str = ""
    confirm: str = ""


class ExplorerColumnTypeRequest(BaseModel):
    database: str = ""
    schema_name: str = ""
    table: str = ""
    column: str = ""
    column_type: str = ""
    length: int | None = None
    precision: int | None = None
    scale: int | None = None
    date_format: str = ""


class ExplorerAddColumnRequest(BaseModel):
    database: str = ""
    schema_name: str = ""
    table: str = ""
    column: str = ""
    column_type: str = "STRING"
    length: int | None = None
    precision: int | None = None
    scale: int | None = None
    mode: str = "NULLABLE"


def _require_bigquery_mutation(database: str) -> None:
    from app.core import catalog_admin as ca
    from app.core import data_modeling_ai as dm

    entry = dm.find_catalog_entry(database)
    if not entry:
        raise ca.CatalogError("Database not found in catalog.")
    if str(entry.get("engine") or "").lower() != "bigquery":
        raise ca.CatalogError("Live schema edits are currently supported for BigQuery only.")


def _mutation_response(call) -> JSONResponse:
    from app.core import catalog_admin as ca
    from app.core import data_modeling_ai as dm

    try:
        result = call()
    except ca.CatalogError as exc:
        return JSONResponse({"status": "error", "message": str(exc)[:400]}, status_code=400)
    except Exception as exc:
        return JSONResponse({"status": "error", "message": str(exc)[:500]}, status_code=500)
    try:
        dm.invalidate_catalog()
    except Exception:
        pass
    return JSONResponse({"status": "success", **result})


@explorer_router.get("/schema")
def api_explorer_schema(request: Request, database: str = "", schema: str = "main"):
    _session_user(request)
    from app.core import catalog_admin as ca

    def call():
        _require_bigquery_mutation(database)
        return ca.schema_info(schema)

    return _mutation_response(call)


@explorer_router.post("/rename")
def api_explorer_rename(req: ExplorerRenameRequest, request: Request):
    _session_user(request)
    from app.core import catalog_admin as ca

    def call():
        _require_bigquery_mutation(req.database)
        if req.table:
            return ca.rename_table(req.schema_name, req.table, req.new_name)
        return ca.rename_schema(req.schema_name, req.new_name)

    return _mutation_response(call)


@explorer_router.post("/delete")
def api_explorer_delete(req: ExplorerDeleteRequest, request: Request):
    _session_user(request)
    from app.core import catalog_admin as ca

    def call():
        _require_bigquery_mutation(req.database)
        if req.table:
            return ca.drop_table(req.schema_name, req.table, req.confirm)
        return ca.drop_schema(req.schema_name, req.confirm)

    return _mutation_response(call)


@explorer_router.post("/column-type")
def api_explorer_column_type(req: ExplorerColumnTypeRequest, request: Request):
    _session_user(request)
    from app.core import catalog_admin as ca

    def call():
        _require_bigquery_mutation(req.database)
        return ca.alter_column(
            req.schema_name,
            req.table,
            req.column,
            req.column_type,
            length=req.length,
            precision=req.precision,
            scale=req.scale,
            date_format=req.date_format,
        )

    return _mutation_response(call)


@explorer_router.post("/column-add")
def api_explorer_column_add(req: ExplorerAddColumnRequest, request: Request):
    _session_user(request)
    from app.core import catalog_admin as ca

    def call():
        _require_bigquery_mutation(req.database)
        return ca.add_column(
            req.schema_name,
            req.table,
            req.column,
            req.column_type,
            length=req.length,
            precision=req.precision,
            scale=req.scale,
            mode=req.mode,
        )

    return _mutation_response(call)


@explorer_router.post("/column-rename")
def api_explorer_column_rename(req: ExplorerRenameRequest, request: Request):
    _session_user(request)
    from app.core import catalog_admin as ca

    def call():
        _require_bigquery_mutation(req.database)
        return ca.rename_column(req.schema_name, req.table, req.column, req.new_name)

    return _mutation_response(call)
