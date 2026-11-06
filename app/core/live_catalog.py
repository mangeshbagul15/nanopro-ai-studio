"""
Live, dynamic database catalog for NanoPro.

Every database shown in Data Modeling by AI is discovered from the Credential
Vault (plus the built-in connection profiles) and introspected with its real
driver. Nothing here fabricates schemas, tables or rows: when a database is
unreachable the entry carries the real error instead of demo metadata.

Engines covered
  * Snowflake
  * PostgreSQL (Neon, Render, local, Supabase when a PG URL is stored)
  * Oracle (XE local / LAN / Tailscale, APEX ORDS metadata when available)
  * DuckDB lakehouse files
  * Google BigQuery (Application Default Credentials)
  * AWS S3 data lake (objects, with DuckDB preview/query support)
"""

from __future__ import annotations

import copy
import json
import os
import re
import sqlite3
import threading
import time
import urllib.parse
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, time as dt_time
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from app.core.logger import log_event

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TTL = 45.0
BUILD_DEADLINE = 22.0
MAX_TABLES_PER_SCHEMA = 250
MAX_SCHEMAS = 60

_lock = threading.RLock()
_state: Dict[str, Any] = {"at": 0.0, "databases": [], "summary": {}}

_KNOWN_SPECS: List[Tuple[str, str, str]] = [
    ("NANO_PRO_SNOWFLAKE", "Snowflake Warehouse", "snowflake"),
    ("POSTGRES_CLOUD_FREE", "PostgreSQL (Neon Cloud)", "postgres"),
    ("POSTGRES_RENDER_CLOUD", "PostgreSQL (Render Cloud)", "postgres"),
    ("MY_POSTGRES_LOCAL", "PostgreSQL (Local)", "postgres"),
    ("ORACLE_APEX_23AI_CLOUD", "Oracle 23ai (APEX Cloud)", "oracle"),
    ("MY_ORACLE_XE_REMOTE", "Oracle XE (Remote LAN)", "oracle"),
    ("MY_ORACLE_XE_REMOTE_New", "Oracle XE (Tailscale)", "oracle"),
    ("MY_ORACLE_XE_LOCAL", "Oracle XE (Local)", "oracle"),
    ("DUCKDB_GOLD_LAKEHOUSE", "DuckDB Gold Lakehouse", "duckdb"),
    ("GOOGLE_BIGQUERY_SANDBOX", "Google BigQuery", "bigquery"),
    ("AWS_S3_DATA_LAKE", "AWS S3 Data Lake", "s3"),
]

_NON_DATABASE_TYPES = {
    "ai_service", "api_key", "token", "oauth", "webhook", "messaging",
    "smtp", "imap", "sftp", "ssh", "ftp", "cloud_observability", "observability",
}

_SYSTEM_ORACLE_OWNERS = {
    "SYS", "SYSTEM", "XDB", "MDSYS", "CTXSYS", "ORDS_METADATA", "OLAPSYS", "WMSYS",
    "LBACSYS", "DBSNMP", "OUTLN", "AUDSYS", "GSMADMIN_INTERNAL", "REMOTE_SCHEDULER_AGENT",
    "APPQOSSYS", "DVF", "DVSYS", "ORDDATA", "ORDPLUGINS", "SI_INFORMTN_SCHEMA",
    "APEX_PUBLIC_USER", "FLOWS_FILES", "MGMT_VIEW", "RDSADMIN", "PUBLIC",
}
_SKIP_SCHEMAS = {"information_schema", "pg_catalog", "pg_toast", "crdb_internal"}


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date, dt_time)):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", "replace")
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    return str(value)


def _quote(name: str, char: str = '"') -> str:
    return char + str(name).replace(char, char + char) + char


def _humanize(name: str) -> str:
    label = str(name or "").replace("_", " ").strip()
    return label.title() if label.isupper() or label.islower() else label


def _resolve_path(raw: str, fallback: str = "") -> Path:
    text = str(raw or fallback or "").strip()
    path = Path(text)
    return path if path.is_absolute() else (ROOT / path)


def _credential(name: str) -> Dict[str, Any]:
    try:
        from app.core.connection_manager import connection_manager

        return connection_manager.get_connection_config(name, mask=False) or {}
    except Exception:
        return {}


def _env(*keys: str) -> str:
    for key in keys:
        value = os.environ.get(key)
        if value:
            return str(value).strip()
    return ""


def _engine_for(name: str, service_type: str = "", metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
    meta = metadata or {}
    blob = " ".join(
        str(x or "") for x in (
            name,
            service_type,
            meta.get("engine"),
            meta.get("engine_full"),
            meta.get("connection_type"),
            meta.get("tier"),
        )
    ).upper()
    if "SNOWFLAKE" in blob:
        return "snowflake"
    if any(token in blob for token in ("ORACLE", "ORCL", "ORDS", "APEX_23AI", "XEPDB")):
        return "oracle"
    if any(token in blob for token in ("POSTGRES", "POSTGRESQL", "NEON", "SUPABASE", "REDSHIFT")):
        return "postgres"
    if "DUCKDB" in blob:
        return "duckdb"
    if any(token in blob for token in ("BIGQUERY", "BIG_QUERY", "GOOGLE CLOUD", "BQ ")):
        return "bigquery"
    if any(token in blob for token in ("S3", "ATHENA", "GLUE", "LAKEHOUSE", "DATA LAKE", "DATA_LAKE")) and "DUCKDB" not in blob:
        return "s3"
    if "MYSQL" in blob or "MARIADB" in blob:
        return "mysql"
    if any(token in blob for token in ("SQLSERVER", "SQL SERVER", "MSSQL")):
        return "sqlserver"
    if any(token in blob for token in ("MONGODB", "MONGO")):
        return "mongodb"
    if any(token in blob for token in ("TURSO", "LIBSQL")):
        return "turso"
    if "SQLITE" in blob:
        return "sqlite"
    return None


def _specs() -> List[Dict[str, Any]]:
    specs: Dict[str, Dict[str, Any]] = {}
    labels = {name: label for name, label, _ in _KNOWN_SPECS}
    engines = {name: engine for name, _, engine in _KNOWN_SPECS}

    for name, label, engine in _KNOWN_SPECS:
        specs[name] = {
            "connection": name,
            "label": label,
            "engine": engine,
            "config": _credential(name),
        }

    try:
        from app.core.database import credentials_vault

        for cred in credentials_vault.list_credentials(mask=False):
            name = str(cred.get("service_name") or "").strip()
            if not name or name in specs:
                continue
            service_type = str(cred.get("credential_type") or "")
            metadata = cred.get("additional_metadata") or {}
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except Exception:
                    metadata = {}
            engine = engines.get(name) or _engine_for(name, service_type, metadata)
            if service_type.strip().lower() in _NON_DATABASE_TYPES or metadata.get("kind") == "api_key":
                continue
            if not engine:
                continue
            specs[name] = {
                "connection": name,
                "label": labels.get(name) or _humanize(name),
                "engine": engine,
                "config": {
                    "connection_name": name,
                    "service_type": service_type,
                    "username": cred.get("username") or "",
                    "host": cred.get("host") or "",
                    "port": cred.get("port") or "",
                    "database_name": cred.get("database_name") or "",
                    "secret_value": cred.get("secret_value") or "",
                    "metadata": metadata,
                },
            }
    except Exception as exc:
        log_event(f"Live catalog: credential enumeration failed: {exc}", level="WARNING", component="LiveCatalog")

    return sorted(specs.values(), key=lambda s: (s["engine"], s["label"].lower()))


def _entry(spec: Dict[str, Any], status: str, schemas: Optional[List[Dict[str, Any]]] = None, error: str = "", detail: str = "") -> Dict[str, Any]:
    engine = spec["engine"]
    return {
        "id": "connection:" + spec["connection"],
        "name": spec["label"],
        "engine": engine,
        "kind": "connection",
        "connection": spec["connection"],
        "writable": engine == "snowflake",
        "status": status,
        "configured": status not in ("not_configured",),
        "schemas": schemas or [],
        "error": error,
        "detail": detail,
    }


def _table_name_list(rows: Iterable[Iterable[Any]]) -> List[Dict[str, str]]:
    tables: List[Dict[str, str]] = []
    seen = set()
    for row in rows:
        name = str(row[0] or "").strip()
        if not name:
            continue
        kind = str(row[1] or "TABLE").upper() if len(row) > 1 else "TABLE"
        key = name.upper()
        if key in seen:
            continue
        seen.add(key)
        tables.append({"name": name, "type": "view" if "VIEW" in kind else "table"})
    return tables


# ----------------------------------------------------------------------------
# Snowflake
# ----------------------------------------------------------------------------

def _introspect_snowflake(spec: Dict[str, Any]) -> Dict[str, Any]:
    from app.core import snowflake_client

    if not snowflake_client.driver_available():
        return _entry(spec, "driver_missing", error="snowflake-connector-python is not installed on the server.")
    cfg = snowflake_client.load_config()
    if not cfg.get("password"):
        return _entry(spec, "not_configured", error="Snowflake password is not in the Credential Vault or SNOWFLAKE_PASSWORD.")
    groups = snowflake_client.live_catalog()
    schemas = [
        {
            "name": f"{group['database']}.{group['schema']}",
            "database": group["database"],
            "schema": group["schema"],
            "tables": group["tables"],
        }
        for group in groups
    ]
    detail = f"{cfg.get('account_identifier') or ''} · {cfg.get('role') or ''} · {cfg.get('warehouse') or ''}".strip(" ·")
    return _entry(spec, "live", schemas, detail=detail)


# ----------------------------------------------------------------------------
# PostgreSQL
# ----------------------------------------------------------------------------

def _postgres_params(spec: Dict[str, Any]) -> Dict[str, Any]:
    cfg = spec.get("config") or {}
    meta = cfg.get("metadata") or {}
    if isinstance(meta, str):
        meta = {}
    name = spec["connection"].upper()

    url = str(meta.get("connection_url") or meta.get("connection_url_external") or "").strip()
    url_key = {
        "POSTGRES_CLOUD_FREE": "NEON_DATABASE_URL",
        "POSTGRES_RENDER_CLOUD": "RENDER_DATABASE_URL",
        "SUPABASE_CLOUD_DB": "SUPABASE_DB_URL",
    }.get(name)
    if not url and url_key:
        url = _env(url_key)
    parsed: Dict[str, Any] = {}
    if url.startswith(("postgres://", "postgresql://")):
        try:
            u = urllib.parse.urlparse(url)
            parsed = {
                "host": u.hostname,
                "port": u.port or 5432,
                "user": u.username,
                "password": u.password,
                "dbname": (u.path or "").lstrip("/"),
                "sslmode": "require" if "sslmode=require" in url else None,
            }
        except Exception:
            parsed = {}

    host = parsed.get("host") or meta.get("hostname") or cfg.get("host") or ""
    if str(host).startswith(("postgres://", "postgresql://")):
        host = urllib.parse.urlparse(str(host)).hostname or ""
    port = parsed.get("port") or meta.get("port") or cfg.get("port") or 5432
    user = parsed.get("user") or meta.get("username") or cfg.get("username") or ""
    password = parsed.get("password") or cfg.get("secret_value") or ""
    dbname = parsed.get("dbname") or meta.get("database") or cfg.get("database_name") or ""
    sslmode = parsed.get("sslmode") or meta.get("sslmode") or ("require" if ("neon.tech" in str(host) or "render.com" in str(host)) else "prefer")
    if not password:
        password = _env("POSTGRES_PASSWORD", "NEON_POSTGRES_PASSWORD", "RENDER_POSTGRES_PASSWORD") if not name.startswith("POSTGRES_CLOUD") else _env("NEON_POSTGRES_PASSWORD")
    return {
        "host": str(host or "").strip(),
        "port": int(port or 5432),
        "user": str(user or "").strip(),
        "password": str(password or "").strip(),
        "dbname": str(dbname or "").strip(),
        "sslmode": str(sslmode or "prefer"),
    }


def _introspect_postgres(spec: Dict[str, Any]) -> Dict[str, Any]:
    try:
        import psycopg2  # type: ignore
        import psycopg2.extras  # type: ignore
    except Exception:
        return _entry(spec, "driver_missing", error="psycopg2-binary is not installed on the server.")
    params = _postgres_params(spec)
    if not params["host"] or not params["user"] or not params["dbname"]:
        return _entry(spec, "not_configured", error="Host, user or database name is missing for this PostgreSQL connection.")
    if not params["password"] and params["sslmode"] in ("require",):
        return _entry(spec, "not_configured", error="PostgreSQL password/URL is not configured.")
    try:
        conn = psycopg2.connect(
            host=params["host"],
            port=params["port"],
            user=params["user"],
            password=params["password"],
            dbname=params["dbname"],
            sslmode=params["sslmode"],
            connect_timeout=7,
            options="-c statement_timeout=15000",
        )
    except Exception as exc:
        return _entry(spec, "unreachable", error=str(exc)[:300], detail=f"{params['host']}:{params['port']}/{params['dbname']}")
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT table_schema, table_name, table_type FROM information_schema.tables "
                "WHERE table_schema NOT IN ('pg_catalog','information_schema') "
                "ORDER BY table_schema, table_name LIMIT 2000"
            )
            grouped: Dict[str, List[Dict[str, str]]] = {}
            for schema_name, table_name, table_type in cur.fetchall():
                sch = str(schema_name or "public")
                if sch in _SKIP_SCHEMAS:
                    continue
                grouped.setdefault(sch, []).append({
                    "name": str(table_name),
                    "type": "view" if "VIEW" in str(table_type).upper() else "table",
                })
        schemas = [
            {"name": sch, "database": params["dbname"], "schema": sch, "tables": tables[:MAX_TABLES_PER_SCHEMA]}
            for sch, tables in sorted(grouped.items())[:MAX_SCHEMAS]
        ]
        return _entry(spec, "live", schemas, detail=f"{params['host']}:{params['port']}/{params['dbname']} · {params['user']}")
    except Exception as exc:
        return _entry(spec, "unreachable", error=str(exc)[:300], detail=f"{params['host']}:{params['port']}/{params['dbname']}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


# ----------------------------------------------------------------------------
# Oracle
# ----------------------------------------------------------------------------

def _oracle_params(spec: Dict[str, Any]) -> Dict[str, Any]:
    cfg = spec.get("config") or {}
    meta = cfg.get("metadata") or {}
    if isinstance(meta, str):
        meta = {}
    return {
        "host": str(meta.get("hostname") or cfg.get("host") or "").strip(),
        "port": int(meta.get("port") or cfg.get("port") or 1521),
        "user": str(meta.get("username") or cfg.get("username") or "").strip(),
        "password": str(cfg.get("secret_value") or _env("ORACLE_PASSWORD", "ORACLE_APEX_PASSWORD") or "").strip(),
        "service": str(meta.get("service_name") or cfg.get("database_name") or "XEPDB1").strip(),
        "ords": str(meta.get("connection_type") or "").upper() == "ORDS_REST" or spec["connection"] == "ORACLE_APEX_23AI_CLOUD",
    }


def _introspect_oracle(spec: Dict[str, Any]) -> Dict[str, Any]:
    params = _oracle_params(spec)
    if params["ords"]:
        return _introspect_ords(spec)
    if not params["host"] or not params["user"]:
        return _entry(spec, "not_configured", error="Oracle host or user is missing.")
    if not params["password"]:
        return _entry(spec, "not_configured", error="Oracle password is not in the Credential Vault or ORACLE_PASSWORD.")
    try:
        import oracledb  # type: ignore
    except Exception:
        try:
            import cx_Oracle as oracledb  # type: ignore
        except Exception:
            return _entry(spec, "driver_missing", error="oracledb is not installed on the server.")
    try:
        conn = oracledb.connect(
            user=params["user"],
            password=params["password"],
            dsn=f"{params['host']}:{params['port']}/{params['service']}",
            tcp_connect_timeout=5,
        )
    except Exception as exc:
        return _entry(spec, "unreachable", error=str(exc)[:300], detail=f"{params['host']}:{params['port']}/{params['service']}")
    try:
        cur = conn.cursor()
        owners = ", ".join("'" + o.replace("'", "''") + "'" for o in sorted(_SYSTEM_ORACLE_OWNERS))
        cur.execute(
            f"SELECT owner, table_name, 'TABLE' FROM all_tables WHERE owner NOT IN ({owners}) "
            f"UNION ALL SELECT owner, view_name, 'VIEW' FROM all_views WHERE owner NOT IN ({owners}) "
            f"ORDER BY 1, 2"
        )
        grouped: Dict[str, List[Dict[str, str]]] = {}
        for owner, name, kind in cur.fetchall()[:4000]:
            grouped.setdefault(str(owner), []).append({
                "name": str(name),
                "type": "view" if "VIEW" in str(kind).upper() else "table",
            })
        cur.close()
        schemas = [
            {"name": sch, "database": params["service"], "schema": sch, "tables": tables[:MAX_TABLES_PER_SCHEMA]}
            for sch, tables in sorted(grouped.items())[:MAX_SCHEMAS]
        ]
        return _entry(spec, "live", schemas, detail=f"{params['host']}:{params['port']}/{params['service']} · {params['user']}")
    except Exception as exc:
        return _entry(spec, "unreachable", error=str(exc)[:300], detail=f"{params['host']}:{params['port']}/{params['service']}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


def _introspect_ords(spec: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from app.core.ords_client import ORDSClient

        client = ORDSClient(spec["connection"])
        token = client.token()
        url = f"{client.schema_url}/metadata-catalog/"
        payload = client._request(
            url,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            phase="ORDS metadata catalog request",
        )
        items = payload.get("items") if isinstance(payload, dict) else None
        grouped: Dict[str, List[Dict[str, str]]] = {}
        if isinstance(items, list):
            for item in items:
                if not isinstance(item, dict):
                    continue
                schema = str(item.get("schema") or spec["connection"])
                name = str(item.get("name") or item.get("table") or "").strip()
                if not name:
                    continue
                grouped.setdefault(schema, []).append({
                    "name": name,
                    "type": "view" if "view" in str(item.get("type") or "").lower() else "table",
                })
        if not grouped:
            return _entry(spec, "unreachable", error="ORDS metadata catalog returned no tables for this workspace.")
        schemas = [
            {"name": sch, "database": "ORDS", "schema": sch, "tables": tables[:MAX_TABLES_PER_SCHEMA]}
            for sch, tables in sorted(grouped.items())[:MAX_SCHEMAS]
        ]
        return _entry(spec, "live", schemas, detail=f"{client.schema_url} · ORDS REST")
    except Exception as exc:
        return _entry(spec, "unreachable", error=str(exc)[:300], detail="ORDS REST")


# ----------------------------------------------------------------------------
# BigQuery
# ----------------------------------------------------------------------------

def _bq_service_account_json() -> str:
    """Service-account JSON for BigQuery, preferring the explicit env var over the Vault entry."""
    sa_json = (_env("GCP_SERVICE_ACCOUNT_JSON") or "").strip()
    if sa_json:
        return sa_json
    try:
        cfg = _credential("GOOGLE_BIGQUERY_SANDBOX") or {}
        meta = cfg.get("metadata") or {}
        if isinstance(meta, str):
            meta = json.loads(meta)
        stored = str(meta.get("service_account_json") or "").strip()
        if stored:
            return stored
        secret = str(cfg.get("secret_value") or "").strip()
        return secret if secret.startswith("{") else ""
    except Exception:
        return ""


def _bq_project_hint() -> str:
    project = _env("GOOGLE_CLOUD_PROJECT", "GCP_PROJECT", "BIGQUERY_PROJECT")
    if project:
        return project
    try:
        meta = (_credential("GOOGLE_BIGQUERY_SANDBOX") or {}).get("metadata") or {}
        if isinstance(meta, str):
            meta = json.loads(meta)
        return str(meta.get("project") or "").strip()
    except Exception:
        return ""


def _bigquery_client() -> Tuple[Any, str]:
    from google.cloud import bigquery  # type: ignore

    project = _bq_project_hint()
    sa_json = _bq_service_account_json()
    if sa_json:
        import base64
        from google.oauth2 import service_account  # type: ignore

        info = json.loads(base64.b64decode(sa_json).decode("utf-8")) if not sa_json.startswith("{") else json.loads(sa_json)
        creds = service_account.Credentials.from_service_account_info(info)
        return bigquery.Client(project=project or info.get("project_id"), credentials=creds), "Credential Vault service account"
    client = bigquery.Client(project=project) if project else bigquery.Client()
    return client, "Application Default Credentials"


def _introspect_bigquery(spec: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from google.cloud import bigquery  # type: ignore
    except Exception:
        return _entry(spec, "driver_missing", error="google-cloud-bigquery is not installed on the server.")
    try:
        client, auth_source = _bigquery_client()
        project = client.project
        schemas: List[Dict[str, Any]] = []
        for dataset in list(client.list_datasets(max_results=40)):
            dataset_id = dataset.dataset_id
            tables: List[Dict[str, str]] = []
            for table in client.list_tables(dataset.dataset_id, max_results=MAX_TABLES_PER_SCHEMA):
                tables.append({"name": table.table_id, "type": "view" if table.table_type == "VIEW" else "table"})
            schemas.append({
                "name": dataset_id,
                "database": project,
                "schema": dataset_id,
                "tables": tables,
            })
        return _entry(spec, "live", schemas, detail=f"project {project} · {auth_source}")
    except Exception as exc:
        return _entry(spec, "unreachable", error=str(exc)[:300], detail="Credential Vault service account or Application Default Credentials")


# ----------------------------------------------------------------------------
# DuckDB
# ----------------------------------------------------------------------------

def _duckdb_params(spec: Dict[str, Any]) -> Path:
    cfg = spec.get("config") or {}
    meta = cfg.get("metadata") or {}
    raw = meta.get("path") or meta.get("database_path") or cfg.get("host") or "data/lakehouse/gold_marts.duckdb"
    return _resolve_path(str(raw))


def _introspect_duckdb(spec: Dict[str, Any]) -> Dict[str, Any]:
    path = _duckdb_params(spec)
    if not path.exists():
        return _entry(spec, "not_configured", error=f"DuckDB file not found: {path}", detail=str(path))
    try:
        import duckdb  # type: ignore

        con = duckdb.connect(str(path), read_only=True)
        try:
            rows = con.execute("SELECT table_schema, table_name FROM information_schema.tables ORDER BY 1, 2").fetchall()
            grouped: Dict[str, List[Dict[str, str]]] = {}
            for schema_name, table_name in rows:
                grouped.setdefault(str(schema_name or "main"), []).append({"name": str(table_name), "type": "table"})
        finally:
            con.close()
        schemas = [
            {"name": sch, "database": path.name, "schema": sch, "tables": tables[:MAX_TABLES_PER_SCHEMA]}
            for sch, tables in sorted(grouped.items())[:MAX_SCHEMAS]
        ]
        return _entry(spec, "live", schemas, detail=str(path))
    except Exception as exc:
        return _entry(spec, "unreachable", error=str(exc)[:300], detail=str(path))


# ----------------------------------------------------------------------------
# AWS S3
# ----------------------------------------------------------------------------

def _aws_params(spec: Dict[str, Any]) -> Dict[str, Any]:
    cfg = spec.get("config") or {}
    meta = cfg.get("metadata") or {}
    if isinstance(meta, str):
        meta = {}
    return {
        "access_key": _env("AWS_ACCESS_KEY_ID") or str(cfg.get("username") or "").strip(),
        "secret_key": _env("AWS_SECRET_ACCESS_KEY") or str(cfg.get("secret_value") or "").strip(),
        "region": _env("AWS_DEFAULT_REGION", "AWS_REGION") or str(meta.get("region") or "ap-southeast-2"),
        "bucket": _env("AWS_S3_BUCKET") or str(cfg.get("database_name") or meta.get("bucket") or "").strip(),
    }


def _s3_client(params: Dict[str, Any]):
    import boto3  # type: ignore
    from botocore.config import Config  # type: ignore

    kwargs: Dict[str, Any] = {
        "region_name": params["region"],
        "config": Config(connect_timeout=6, read_timeout=20, retries={"max_attempts": 1}),
    }
    if params["access_key"] and params["secret_key"]:
        kwargs["aws_access_key_id"] = params["access_key"]
        kwargs["aws_secret_access_key"] = params["secret_key"]
    return boto3.client("s3", **kwargs)


def _introspect_s3(spec: Dict[str, Any]) -> Dict[str, Any]:
    try:
        import boto3  # noqa: F401
    except Exception:
        return _entry(spec, "driver_missing", error="boto3 is not installed on the server.")
    params = _aws_params(spec)
    if not params["bucket"]:
        return _entry(spec, "not_configured", error="AWS_S3_BUCKET is not configured.")
    try:
        client = _s3_client(params)
        grouped: Dict[str, List[Dict[str, str]]] = {}
        paginator = client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=params["bucket"], PaginationConfig={"MaxItems": 400}):
            for obj in page.get("Contents", []) or []:
                key = str(obj.get("Key") or "")
                if not key or key.endswith("/"):
                    continue
                parts = key.split("/")
                schema = parts[0] if len(parts) > 1 else "(root)"
                grouped.setdefault(schema, []).append({"name": key, "type": "object"})
        schemas = [
            {"name": sch, "database": params["bucket"], "schema": sch, "tables": tables[:MAX_TABLES_PER_SCHEMA]}
            for sch, tables in sorted(grouped.items())[:MAX_SCHEMAS]
        ]
        return _entry(spec, "live", schemas, detail=f"s3://{params['bucket']} · {params['region']}")
    except Exception as exc:
        return _entry(spec, "unreachable", error=str(exc)[:300], detail=f"s3://{params['bucket']} · {params['region']}")


# ----------------------------------------------------------------------------
# other engines
# ----------------------------------------------------------------------------

def _introspect_mysql(spec: Dict[str, Any]) -> Dict[str, Any]:
    try:
        import pymysql  # type: ignore
    except Exception:
        return _entry(spec, "driver_missing", error="pymysql is not installed on the server.")
    cfg = spec.get("config") or {}
    try:
        conn = pymysql.connect(
            host=cfg.get("host") or "127.0.0.1",
            port=int(cfg.get("port") or 3306),
            user=cfg.get("username") or "root",
            password=cfg.get("secret_value") or "",
            database=cfg.get("database_name") or None,
            connect_timeout=6,
        )
        with conn.cursor() as cur:
            cur.execute(
                "SELECT table_schema, table_name, table_type FROM information_schema.tables "
                "WHERE table_schema NOT IN ('mysql','information_schema','performance_schema','sys') "
                "ORDER BY 1,2 LIMIT 2000"
            )
            grouped: Dict[str, List[Dict[str, str]]] = {}
            for schema_name, table_name, table_type in cur.fetchall():
                grouped.setdefault(str(schema_name), []).append({
                    "name": str(table_name),
                    "type": "view" if "VIEW" in str(table_type).upper() else "table",
                })
        schemas = [
            {"name": sch, "database": sch, "schema": sch, "tables": tables[:MAX_TABLES_PER_SCHEMA]}
            for sch, tables in sorted(grouped.items())[:MAX_SCHEMAS]
        ]
        return _entry(spec, "live", schemas, detail=f"{cfg.get('host')}:{cfg.get('port')}")
    except Exception as exc:
        return _entry(spec, "unreachable", error=str(exc)[:300])


def _introspect_unsupported(spec: Dict[str, Any]) -> Dict[str, Any]:
    return _entry(spec, "driver_missing", error=f"Live table introspection is not implemented for engine '{spec['engine']}' yet.")


_INTROSPECTORS = {
    "snowflake": _introspect_snowflake,
    "postgres": _introspect_postgres,
    "oracle": _introspect_oracle,
    "bigquery": _introspect_bigquery,
    "duckdb": _introspect_duckdb,
    "s3": _introspect_s3,
    "mysql": _introspect_mysql,
}


# ----------------------------------------------------------------------------
# snapshot
# ----------------------------------------------------------------------------

def _build() -> List[Dict[str, Any]]:
    specs = _specs()
    results: Dict[str, Dict[str, Any]] = {}
    if not specs:
        return []
    executor = ThreadPoolExecutor(max_workers=min(8, len(specs)), thread_name_prefix="live-catalog")
    futures = {}
    for spec in specs:
        fn = _INTROSPECTORS.get(spec["engine"], _introspect_unsupported)
        futures[executor.submit(fn, spec)] = spec
    deadline = time.time() + BUILD_DEADLINE
    try:
        for future in as_completed(futures, timeout=max(1.0, deadline - time.time())):
            spec = futures[future]
            try:
                results[spec["connection"]] = future.result()
            except Exception as exc:
                results[spec["connection"]] = _entry(spec, "unreachable", error=str(exc)[:300])
    except Exception:
        pass
    finally:
        for future, spec in futures.items():
            if spec["connection"] not in results:
                results[spec["connection"]] = _entry(spec, "unreachable", error="Live introspection timed out.")
        executor.shutdown(wait=False, cancel_futures=True)
    ordered = []
    for spec in specs:
        entry = results.get(spec["connection"])
        if entry:
            ordered.append(entry)
    return ordered


def _summary(databases: List[Dict[str, Any]]) -> Dict[str, Any]:
    live = sum(1 for d in databases if d["status"] == "live")
    tables = sum(len(s.get("tables") or []) for d in databases for s in d.get("schemas") or [])
    return {
        "databases": len(databases),
        "live": live,
        "tables": tables,
        "not_configured": sum(1 for d in databases if d["status"] == "not_configured"),
        "unreachable": sum(1 for d in databases if d["status"] == "unreachable"),
        "driver_missing": sum(1 for d in databases if d["status"] == "driver_missing"),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def snapshot(force: bool = False, ttl: float = DEFAULT_TTL) -> Dict[str, Any]:
    now = time.time()
    with _lock:
        if not force and _state["databases"] and (now - _state["at"]) < ttl:
            return {"databases": copy.deepcopy(_state["databases"]), "stats": copy.deepcopy(_state["summary"])}
        databases = _build()
        summary = _summary(databases)
        _state["databases"] = databases
        _state["at"] = now
        _state["summary"] = summary
        return {"databases": copy.deepcopy(databases), "stats": copy.deepcopy(summary)}


def databases(force: bool = False, ttl: float = DEFAULT_TTL) -> List[Dict[str, Any]]:
    return snapshot(force=force, ttl=ttl)["databases"]


def invalidate() -> None:
    with _lock:
        _state["at"] = 0.0
        _state["databases"] = []
        _state["summary"] = {}


def find(connection_name: str) -> Optional[Dict[str, Any]]:
    for entry in databases():
        if entry.get("connection") == connection_name:
            return entry
    return None


def connection_names() -> List[str]:
    return [entry["connection"] for entry in databases()]


# ----------------------------------------------------------------------------
# table details
# ----------------------------------------------------------------------------

def _find_table(entry: Dict[str, Any], schema: str, table: str) -> Optional[Dict[str, Any]]:
    for group in entry.get("schemas") or []:
        if str(group.get("schema") or group.get("name")) != str(schema):
            continue
        for item in group.get("tables") or []:
            if str(item.get("name")) == str(table):
                return item
    return None


def _details_postgres(entry: Dict[str, Any], schema: str, table: str) -> Dict[str, Any]:
    import psycopg2  # type: ignore
    import psycopg2.extras  # type: ignore

    params = _postgres_params({"connection": entry["connection"], "config": _credential(entry["connection"])})
    conn = psycopg2.connect(
        host=params["host"], port=params["port"], user=params["user"], password=params["password"],
        dbname=params["dbname"], sslmode=params["sslmode"], connect_timeout=8,
        options="-c statement_timeout=20000",
    )
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT column_name, data_type, is_nullable, column_default "
                "FROM information_schema.columns WHERE table_schema=%s AND table_name=%s ORDER BY ordinal_position",
                (schema, table),
            )
            columns = [
                {
                    "name": str(r["column_name"]),
                    "data_type": str(r["data_type"]),
                    "not_null": str(r["is_nullable"]).upper() == "NO",
                    "is_pk": False,
                    "default": r.get("column_default"),
                }
                for r in cur.fetchall()
            ]
            cur.execute(
                "SELECT kcu.column_name FROM information_schema.table_constraints tc "
                "JOIN information_schema.key_column_usage kcu "
                "ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema "
                "WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_schema=%s AND tc.table_name=%s",
                (schema, table),
            )
            pks = {str(r["column_name"]) for r in cur.fetchall()}
            for col in columns:
                col["is_pk"] = col["name"] in pks
            qualified = f"{_quote(schema)}.{_quote(table)}"
            cur.execute(f"SELECT COUNT(*) AS n FROM {qualified}")
            row_count = int((cur.fetchone() or {}).get("n") or 0)
            cur.execute(f"SELECT * FROM {qualified} LIMIT 5")
            sample = [{k: _jsonable(v) for k, v in dict(r).items()} for r in cur.fetchall()]
            return {
                "database": entry["name"], "schema": schema, "table": table,
                "columns": columns, "row_count": row_count, "sample": sample, "ddl": "",
            }
    finally:
        conn.close()


def _details_oracle(entry: Dict[str, Any], schema: str, table: str) -> Dict[str, Any]:
    import oracledb  # type: ignore

    params = _oracle_params({"connection": entry["connection"], "config": _credential(entry["connection"])})
    conn = oracledb.connect(
        user=params["user"], password=params["password"],
        dsn=f"{params['host']}:{params['port']}/{params['service']}", tcp_connect_timeout=6,
    )
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT column_name, data_type, data_length, data_precision, data_scale, nullable, data_default "
            "FROM all_tab_columns WHERE owner=:1 AND table_name=:2 ORDER BY column_id",
            [schema, table],
        )
        columns = []
        for name, dtype, length, precision, scale, nullable, default in cur.fetchall():
            if dtype in ("VARCHAR2", "CHAR", "NVARCHAR2", "NCHAR") and length:
                text = f"{dtype}({int(length)})"
            elif dtype == "NUMBER" and precision:
                text = f"NUMBER({int(precision)},{int(scale or 0)})" if scale else f"NUMBER({int(precision)})"
            else:
                text = str(dtype)
            columns.append({
                "name": str(name), "data_type": text,
                "not_null": str(nullable).upper() == "N",
                "is_pk": False, "default": _jsonable(default),
            })
        cur.execute(
            "SELECT acc.column_name FROM all_constraints ac "
            "JOIN all_cons_columns acc ON ac.owner = acc.owner AND ac.constraint_name = acc.constraint_name "
            "WHERE ac.constraint_type = 'P' AND ac.owner=:1 AND ac.table_name=:2",
            [schema, table],
        )
        pks = {str(r[0]) for r in cur.fetchall()}
        for col in columns:
            col["is_pk"] = col["name"] in pks
        qualified = f"{_quote(schema)}.{_quote(table)}"
        cur.execute(f"SELECT COUNT(*) FROM {qualified}")
        row_count = int(cur.fetchone()[0] or 0)
        cur.execute(f"SELECT * FROM {qualified} FETCH FIRST 5 ROWS ONLY")
        cols = [d[0] for d in cur.description]
        sample = [
            {cols[i]: _jsonable(row[i]) for i in range(len(cols))}
            for row in cur.fetchall()
        ]
        cur.close()
        return {
            "database": entry["name"], "schema": schema, "table": table,
            "columns": columns, "row_count": row_count, "sample": sample, "ddl": "",
        }
    finally:
        conn.close()


def _details_bigquery(entry: Dict[str, Any], schema: str, table: str) -> Dict[str, Any]:
    client, _ = _bigquery_client()
    ref = f"{client.project}.{schema}.{table}"
    table_obj = client.get_table(ref)
    columns = [
        {
            "name": f.name,
            "data_type": f.field_type,
            "not_null": f.mode == "REQUIRED",
            "is_pk": False,
            "default": None,
        }
        for f in table_obj.schema
    ]
    sample = [
        {k: _jsonable(v) for k, v in dict(row.items()).items()}
        for row in client.list_rows(table_obj, max_results=5)
    ]
    return {
        "database": entry["name"], "schema": schema, "table": table,
        "columns": columns, "row_count": int(table_obj.num_rows or 0),
        "sample": sample, "ddl": "",
    }


def _details_duckdb(entry: Dict[str, Any], schema: str, table: str) -> Dict[str, Any]:
    import duckdb  # type: ignore

    path = _duckdb_params({"connection": entry["connection"], "config": _credential(entry["connection"])})
    con = duckdb.connect(str(path), read_only=True)
    try:
        qualified = f"{_quote(schema)}.{_quote(table)}"
        desc = con.execute(f"DESCRIBE {qualified}").fetchall()
        columns = [
            {"name": d[0], "data_type": d[1], "not_null": str(d[2]).upper() == "NO", "is_pk": False, "default": None}
            for d in desc
        ]
        row_count = int(con.execute(f"SELECT COUNT(*) FROM {qualified}").fetchone()[0])
        cur = con.execute(f"SELECT * FROM {qualified} LIMIT 5")
        names = [c[0] for c in cur.description]
        sample = [{names[i]: _jsonable(row[i]) for i in range(len(names))} for row in cur.fetchall()]
        return {
            "database": entry["name"], "schema": schema, "table": table,
            "columns": columns, "row_count": row_count, "sample": sample, "ddl": "",
        }
    finally:
        con.close()


def _details_s3(entry: Dict[str, Any], schema: str, table: str) -> Dict[str, Any]:
    params = _aws_params({"connection": entry["connection"], "config": _credential(entry["connection"])})
    client = _s3_client(params)
    head = client.head_object(Bucket=params["bucket"], Key=table)
    result: Dict[str, Any] = {
        "database": entry["name"], "schema": schema, "table": table,
        "columns": [], "row_count": None, "sample": [],
        "ddl": f"s3://{params['bucket']}/{table}",
        "size_bytes": head.get("ContentLength"),
        "last_modified": _jsonable(head.get("LastModified")),
        "content_type": head.get("ContentType"),
    }
    lower = table.lower()
    if head.get("ContentLength", 0) <= 30 * 1024 * 1024 and lower.endswith((".csv", ".tsv", ".parquet", ".json", ".jsonl")):
        try:
            import duckdb  # type: ignore
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(table).suffix) as tmp:
                client.download_fileobj(params["bucket"], table, tmp)
                tmp_path = tmp.name
            try:
                con = duckdb.connect()
                try:
                    if lower.endswith((".parquet",)):
                        scan = f"read_parquet({tmp_path!r})"
                    elif lower.endswith((".json", ".jsonl")):
                        scan = f"read_json_auto({tmp_path!r})"
                    else:
                        scan = f"read_csv_auto({tmp_path!r})"
                    desc = con.execute(f"DESCRIBE SELECT * FROM {scan}").fetchall()
                    result["columns"] = [
                        {"name": d[0], "data_type": d[1], "not_null": False, "is_pk": False, "default": None}
                        for d in desc
                    ]
                    result["row_count"] = int(con.execute(f"SELECT COUNT(*) FROM {scan}").fetchone()[0])
                    cur = con.execute(f"SELECT * FROM {scan} LIMIT 5")
                    names = [c[0] for c in cur.description]
                    result["sample"] = [
                        {names[i]: _jsonable(row[i]) for i in range(len(names))}
                        for row in cur.fetchall()
                    ]
                finally:
                    con.close()
            finally:
                Path(tmp_path).unlink(missing_ok=True)
        except Exception as exc:
            result["error"] = f"Object metadata loaded, but the preview failed: {str(exc)[:200]}"
    return result


def _details_sqlite_connection(entry: Dict[str, Any], schema: str, table: str) -> Dict[str, Any]:
    from app.core.database import SQLITE_DB_PATH

    conn = sqlite3.connect(str(SQLITE_DB_PATH), timeout=5)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only = ON")
        cols = conn.execute(f"PRAGMA {_quote(schema)}.table_info({_quote(table)})").fetchall()
        columns = [
            {"name": c[1], "data_type": c[2] or "TEXT", "not_null": bool(c[3]), "is_pk": bool(c[5]), "default": c[4]}
            for c in cols
        ]
        row_count = int(conn.execute(f"SELECT COUNT(*) FROM {_quote(schema)}.{_quote(table)}").fetchone()[0])
        sample = [dict(r) for r in conn.execute(f"SELECT * FROM {_quote(schema)}.{_quote(table)} LIMIT 5").fetchall()]
        return {
            "database": entry["name"], "schema": schema, "table": table,
            "columns": columns, "row_count": row_count, "sample": sample, "ddl": "",
        }
    finally:
        conn.close()


def table_details(connection_name: str, schema: str, table: str) -> Dict[str, Any]:
    entry = find(connection_name)
    if not entry:
        raise ValueError("Database not found in the live catalog.")
    if entry["status"] != "live":
        raise ValueError(entry.get("error") or f"{entry['name']} is not reachable right now.")
    engine = entry["engine"]
    handlers = {
        "postgres": _details_postgres,
        "oracle": _details_oracle,
        "bigquery": _details_bigquery,
        "duckdb": _details_duckdb,
        "s3": _details_s3,
        "sqlite": _details_sqlite_connection,
    }
    handler = handlers.get(engine)
    if not handler:
        raise ValueError(f"Table details are not supported for engine '{engine}'.")
    return handler(entry, schema, table)


# ----------------------------------------------------------------------------
# read-only execution
# ----------------------------------------------------------------------------

def _execute_postgres(connection_name: str, statement: str, limit: int) -> Dict[str, Any]:
    import psycopg2  # type: ignore
    import psycopg2.extras  # type: ignore

    params = _postgres_params({"connection": connection_name, "config": _credential(connection_name)})
    conn = psycopg2.connect(
        host=params["host"], port=params["port"], user=params["user"], password=params["password"],
        dbname=params["dbname"], sslmode=params["sslmode"], connect_timeout=8,
        options="-c statement_timeout=30000",
    )
    started = time.time()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(statement)
            if cur.description:
                raw = cur.fetchmany(limit + 1)
                columns = [d[0] for d in cur.description]
                rows = [{k: _jsonable(v) for k, v in dict(r).items()} for r in raw[:limit]]
            else:
                raw, columns, rows = [], [], []
        conn.rollback()
        return {
            "success": True, "columns": columns, "rows": rows,
            "row_count": len(rows), "truncated": len(raw) > limit,
            "execution_time_ms": round((time.time() - started) * 1000, 2),
        }
    finally:
        conn.close()


def _execute_oracle(connection_name: str, statement: str, limit: int) -> Dict[str, Any]:
    import oracledb  # type: ignore

    params = _oracle_params({"connection": connection_name, "config": _credential(connection_name)})
    conn = oracledb.connect(
        user=params["user"], password=params["password"],
        dsn=f"{params['host']}:{params['port']}/{params['service']}", tcp_connect_timeout=6,
    )
    started = time.time()
    try:
        cur = conn.cursor()
        cur.execute(statement)
        columns = [d[0] for d in cur.description] if cur.description else []
        raw = cur.fetchmany(limit + 1) if cur.description else []
        rows = [
            {columns[i]: _jsonable(row[i]) for i in range(len(columns))}
            for row in raw[:limit]
        ]
        cur.close()
        conn.rollback()
        return {
            "success": True, "columns": columns, "rows": rows,
            "row_count": len(rows), "truncated": len(raw) > limit,
            "execution_time_ms": round((time.time() - started) * 1000, 2),
        }
    finally:
        conn.close()


def _execute_bigquery(connection_name: str, statement: str, limit: int) -> Dict[str, Any]:
    client, _ = _bigquery_client()
    started = time.time()
    job = client.query(statement)
    result = job.result(max_results=limit + 1)
    columns = [field.name for field in result.schema]
    rows = []
    for row in result:
        rows.append({k: _jsonable(v) for k, v in dict(row.items()).items()})
        if len(rows) > limit:
            break
    return {
        "success": True, "columns": columns, "rows": rows[:limit],
        "row_count": min(len(rows), limit), "truncated": len(rows) > limit,
        "execution_time_ms": round((time.time() - started) * 1000, 2),
    }


def _execute_duckdb(connection_name: str, statement: str, limit: int) -> Dict[str, Any]:
    import duckdb  # type: ignore

    path = _duckdb_params({"connection": connection_name, "config": _credential(connection_name)})
    con = duckdb.connect(str(path), read_only=True)
    started = time.time()
    try:
        cur = con.execute(statement)
        columns = [d[0] for d in cur.description] if cur.description else []
        raw = cur.fetchmany(limit + 1) if cur.description else []
        rows = [
            {columns[i]: _jsonable(row[i]) for i in range(len(columns))}
            for row in raw[:limit]
        ]
        return {
            "success": True, "columns": columns, "rows": rows,
            "row_count": len(rows), "truncated": len(raw) > limit,
            "execution_time_ms": round((time.time() - started) * 1000, 2),
        }
    finally:
        con.close()


def _execute_s3(connection_name: str, statement: str, limit: int) -> Dict[str, Any]:
    import duckdb  # type: ignore

    params = _aws_params({"connection": connection_name, "config": _credential(connection_name)})
    con = duckdb.connect()
    started = time.time()
    try:
        try:
            con.execute("LOAD httpfs")
        except Exception:
            con.execute("INSTALL httpfs")
            con.execute("LOAD httpfs")
        def _lit(value: Any) -> str:
            return str(value).replace("'", "''")

        con.execute(f"SET s3_region='{_lit(params['region'])}'")
        if params["access_key"] and params["secret_key"]:
            con.execute(f"SET s3_access_key_id='{_lit(params['access_key'])}'")
            con.execute(f"SET s3_secret_access_key='{_lit(params['secret_key'])}'")
        cur = con.execute(statement)
        columns = [d[0] for d in cur.description] if cur.description else []
        raw = cur.fetchmany(limit + 1) if cur.description else []
        rows = [
            {columns[i]: _jsonable(row[i]) for i in range(len(columns))}
            for row in raw[:limit]
        ]
        return {
            "success": True, "columns": columns, "rows": rows,
            "row_count": len(rows), "truncated": len(raw) > limit,
            "execution_time_ms": round((time.time() - started) * 1000, 2),
        }
    finally:
        con.close()


_READ_ONLY = re.compile(r"^\s*(select|with|explain|show|describe|desc|pragma)\b", re.IGNORECASE)


def execute_read(connection_name: str, statement: str, limit: int = 200) -> Dict[str, Any]:
    text = (statement or "").strip()
    if not _READ_ONLY.match(text):
        raise ValueError("Only read-only SELECT / WITH queries are allowed on this database.")
    if ";" in text.rstrip(";"):
        raise ValueError("Only one SQL statement can run at a time.")
    entry = find(connection_name)
    if not entry:
        raise ValueError("Database not found in the live catalog.")
    if entry["status"] != "live":
        raise ValueError(entry.get("error") or f"{entry['name']} is not reachable right now.")
    engine = entry["engine"]
    handlers = {
        "postgres": _execute_postgres,
        "oracle": _execute_oracle,
        "bigquery": _execute_bigquery,
        "duckdb": _execute_duckdb,
        "s3": _execute_s3,
    }
    handler = handlers.get(engine)
    if not handler:
        raise ValueError(f"Read-only SQL execution is not supported for engine '{engine}'.")
    return handler(connection_name, statement, limit)


def s3_query_hint(connection_name: str) -> str:
    entry = find(connection_name)
    if not entry:
        return ""
    bucket = ""
    detail = str(entry.get("detail") or "")
    if detail.startswith("s3://"):
        bucket = detail[5:].split(" · ")[0].strip()
    return (
        f"AWS S3 is an object store. Query files with DuckDB functions, e.g. "
        f"SELECT * FROM read_parquet('s3://{bucket or 'bucket/key.parquet'}') LIMIT 200 or "
        f"read_csv('s3://{bucket or 'bucket/key.csv'}', header=true)."
    )
