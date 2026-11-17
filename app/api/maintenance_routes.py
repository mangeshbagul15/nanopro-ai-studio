"""Owner-only maintenance purge for the NanoPro lakehouse.

Temporary operational endpoint: permanently drops the demo/lakehouse tables in
Snowflake, BigQuery, S3 and DuckDB while keeping AI chat history. It is gated on
an admin session plus an explicit confirmation phrase.
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])

CONFIRM_PHRASE = "PURGE-LAKEHOUSE-2026-11-18"
KEEP_BIGQUERY_TABLE = re.compile(r"^ai_chat_", re.IGNORECASE)
KEEP_DUCKDB_FILES = {"nanopro_chats.duckdb", "global_ai_history.duckdb"}
SNOWFLAKE_SCHEMAS = ("L0_STAGING", "L1_HARMONIZED", "L2_CURATED")


class PurgeRequest(BaseModel):
    confirm: str
    scopes: List[str] = ["snowflake", "bigquery", "s3", "duckdb"]


def _require_owner(request: Request) -> Dict[str, Any]:
    from app.core.api_auth import require_session

    user = require_session(request)
    if str(user.get("role") or "").lower() != "admin":
        raise HTTPException(status_code=403, detail="Owner/admin session required.")
    return user


def _purge_snowflake() -> Dict[str, Any]:
    from app.core import snowflake_client

    started = time.time()
    out: Dict[str, Any] = {"engine": "snowflake", "schemas": [], "dropped": [], "failed": []}
    conn = snowflake_client.open_connection()
    try:
        cur = conn.cursor()
        for schema in SNOWFLAKE_SCHEMAS:
            cur.execute(f"SHOW TABLES IN SCHEMA BANK_DB.{schema}")
            columns = [d[0].lower() for d in (cur.description or [])]
            name_idx = columns.index("name") if "name" in columns else 1
            tables = [row[name_idx] for row in cur.fetchall()]

            cur.execute(f"SHOW VIEWS IN SCHEMA BANK_DB.{schema}")
            vcols = [d[0].lower() for d in (cur.description or [])]
            vname_idx = vcols.index("name") if "name" in vcols else 1
            views = [row[vname_idx] for row in cur.fetchall()]

            dropped_here = 0
            for kind, names in (("TABLE", tables), ("VIEW", views)):
                for name in names:
                    try:
                        cur.execute(f'DROP {kind} IF EXISTS "BANK_DB"."{schema}"."{name}"')
                        out["dropped"].append(f"BANK_DB.{schema}.{name}")
                        dropped_here += 1
                    except Exception as exc:
                        out["failed"].append({"object": f"BANK_DB.{schema}.{name}", "error": str(exc)[:300]})
            out["schemas"].append({"schema": schema, "tables": len(tables), "views": len(views), "dropped": dropped_here})
        conn.commit()
    finally:
        conn.close()
    out["dropped_count"] = len(out["dropped"])
    out["elapsed_s"] = round(time.time() - started, 2)
    return out


def _purge_bigquery() -> Dict[str, Any]:
    from app.core import live_catalog as lc

    started = time.time()
    out: Dict[str, Any] = {"engine": "bigquery", "datasets": [], "dropped": [], "failed": []}
    client, auth_source = lc._bigquery_client()
    out["auth_source"] = auth_source
    project = client.project

    for dataset in client.list_datasets():
        dataset_id = dataset.dataset_id
        tables = [t.table_id for t in client.list_tables(dataset.reference)]
        kept = [t for t in tables if KEEP_BIGQUERY_TABLE.match(t)]
        dropped_here = 0
        for table_id in tables:
            if KEEP_BIGQUERY_TABLE.match(table_id):
                continue
            try:
                client.delete_table(f"{project}.{dataset_id}.{table_id}", not_found_ok=True)
                out["dropped"].append(f"{project}.{dataset_id}.{table_id}")
                dropped_here += 1
            except Exception as exc:
                out["failed"].append({"object": f"{project}.{dataset_id}.{table_id}", "error": str(exc)[:300]})

        remaining = [t.table_id for t in client.list_tables(dataset.reference)]
        if not remaining and dataset_id != "nanopro_studio":
            try:
                client.delete_dataset(f"{project}.{dataset_id}", delete_contents=True, not_found_ok=True)
                out["datasets"].append({"dataset": dataset_id, "dropped_tables": dropped_here, "dataset_deleted": True})
                continue
            except Exception as exc:
                out["failed"].append({"object": f"{project}.{dataset_id}", "error": str(exc)[:300]})
        out["datasets"].append({"dataset": dataset_id, "tables": len(tables), "kept_chat_tables": kept, "dropped_tables": dropped_here})

    out["dropped_count"] = len(out["dropped"])
    out["elapsed_s"] = round(time.time() - started, 2)
    return out


def _purge_s3() -> Dict[str, Any]:
    from app.core import live_catalog as lc

    started = time.time()
    out: Dict[str, Any] = {"engine": "s3", "buckets": [], "deleted_objects": 0, "failed": []}
    params = lc._aws_params({"connection": "AWS S3 Data Lake", "config": lc._credential("AWS S3 Data Lake")})
    client = lc._s3_client(params)

    buckets = [params["bucket"]] if params.get("bucket") else []
    if not buckets:
        buckets = [b["Name"] for b in client.list_buckets().get("Buckets", []) if "nanopro" in b["Name"]]

    for bucket in buckets:
        deleted_here = 0
        paginator = client.get_paginator("list_objects_v2")
        batch: List[Dict[str, str]] = []
        for page in paginator.paginate(Bucket=bucket):
            for obj in page.get("Contents", []):
                batch.append({"Key": obj["Key"]})
                if len(batch) >= 1000:
                    client.delete_objects(Bucket=bucket, Delete={"Objects": batch, "Quiet": True})
                    deleted_here += len(batch)
                    batch = []
        if batch:
            client.delete_objects(Bucket=bucket, Delete={"Objects": batch, "Quiet": True})
            deleted_here += len(batch)

        versioned = 0
        try:
            for page in client.get_paginator("list_object_versions").paginate(Bucket=bucket):
                vbatch = [{"VersionId": v["VersionId"], "Key": v["Key"]} for v in page.get("Versions", [])]
                mbatch = [{"VersionId": v["VersionId"], "Key": v["Key"]} for v in page.get("DeleteMarkers", [])]
                combined = vbatch + mbatch
                for i in range(0, len(combined), 1000):
                    client.delete_objects(Bucket=bucket, Delete={"Objects": combined[i:i + 1000], "Quiet": True})
                    versioned += len(combined[i:i + 1000])
        except Exception as exc:
            out["failed"].append({"bucket": bucket, "versions": str(exc)[:200]})

        remaining = client.list_objects_v2(Bucket=bucket, MaxKeys=5).get("KeyCount", 0)
        out["buckets"].append({"bucket": bucket, "deleted_objects": deleted_here, "deleted_versions": versioned, "remaining_objects": remaining})
        out["deleted_objects"] += deleted_here
    out["elapsed_s"] = round(time.time() - started, 2)
    return out


def _purge_duckdb() -> Dict[str, Any]:
    import duckdb

    started = time.time()
    root = Path(__file__).resolve().parents[2]
    out: Dict[str, Any] = {"engine": "duckdb", "files": [], "failed": []}

    candidates = set()
    for pattern in ("data/lakehouse/*.duckdb", "data/*.duckdb", "app/database/*.duckdb"):
        candidates.update(p for p in root.glob(pattern) if p.is_file())
    try:
        from app.core import live_catalog as lc

        gold = lc._duckdb_params({"connection": "DuckDB Gold Lakehouse", "config": lc._credential("DuckDB Gold Lakehouse")})
        if Path(gold).is_file():
            candidates.add(Path(gold))
    except Exception:
        pass

    for path in sorted(candidates):
        if path.name in KEEP_DUCKDB_FILES:
            out["files"].append({"file": str(path.relative_to(root)), "skipped": "chat history"})
            continue
        dropped = []
        try:
            con = duckdb.connect(str(path))
            try:
                rows = con.execute(
                    "SELECT table_schema, table_name FROM information_schema.tables "
                    "WHERE table_schema NOT IN ('information_schema', 'pg_catalog')"
                ).fetchall()
                for schema_name, table_name in rows:
                    con.execute(f'DROP TABLE IF EXISTS "{schema_name}"."{table_name}"')
                    dropped.append(f"{schema_name}.{table_name}")
            finally:
                con.close()
        except Exception as exc:
            out["failed"].append({"file": str(path), "error": str(exc)[:300]})
        out["files"].append({"file": str(path.relative_to(root)), "dropped": dropped})

    out["elapsed_s"] = round(time.time() - started, 2)
    return out


@router.post("/purge-lakehouse")
async def api_purge_lakehouse(req: PurgeRequest, request: Request):
    """Permanently deletes lakehouse tables/objects in the requested scopes."""
    user = _require_owner(request)
    if (req.confirm or "").strip() != CONFIRM_PHRASE:
        raise HTTPException(status_code=400, detail="Confirmation phrase mismatch.")

    report: Dict[str, Any] = {"status": "success", "operator": user.get("username"), "scopes": {}}
    handlers = {
        "snowflake": _purge_snowflake,
        "bigquery": _purge_bigquery,
        "s3": _purge_s3,
        "duckdb": _purge_duckdb,
    }
    for scope in req.scopes:
        handler = handlers.get(scope)
        if not handler:
            report["scopes"][scope] = {"error": "unknown scope"}
            continue
        try:
            report["scopes"][scope] = handler()
        except Exception as exc:
            report["scopes"][scope] = {"error": str(exc)[:500]}
    return JSONResponse(report)
