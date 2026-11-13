"""Live storage telemetry for the Global AI Lab storage answers.

Every engine is measured on demand. A source that is unconfigured, unreachable
or too slow reports that state and its reason - never a guessed size.
"""

import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import TimeoutError as FuturesTimeout
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import BASE_DIR, SQLITE_DB_PATH

CACHE_TTL_SECONDS = 45.0
BIGQUERY_SANDBOX_CAP_BYTES = 10 * 1024 ** 3  # documented Always Free Sandbox storage quota
SOURCE_DEADLINE_SECONDS = 9.0

_cache: Dict[str, Any] = {"at": 0.0, "data": None}


def format_bytes(value: Optional[float]) -> str:
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        number = 0.0
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    index = 0
    while abs(number) >= 1024 and index < len(units) - 1:
        number /= 1024.0
        index += 1
    return f"{number:.2f} {units[index]}"


def _source(
    source_id: str,
    name: str,
    engine: str,
    tier: str,
    status: str = "live",
    used_bytes: Optional[float] = None,
    total_bytes: Optional[float] = None,
    free_bytes: Optional[float] = None,
    detail: str = "",
    reason: str = "",
    latency_ms: Optional[float] = None,
    **extra: Any,
) -> Dict[str, Any]:
    entry: Dict[str, Any] = {
        "id": source_id,
        "name": name,
        "engine": engine,
        "tier": tier,
        "status": status,
        "used_bytes": int(used_bytes) if used_bytes is not None else None,
        "total_bytes": int(total_bytes) if total_bytes is not None else None,
        "free_bytes": int(free_bytes) if free_bytes is not None else None,
        "used_formatted": format_bytes(used_bytes) if used_bytes is not None else None,
        "total_formatted": format_bytes(total_bytes) if total_bytes is not None else None,
        "free_formatted": format_bytes(free_bytes) if free_bytes is not None else None,
        "detail": detail,
        "reason": reason,
        "latency_ms": round(latency_ms, 1) if latency_ms is not None else None,
    }
    entry.update(extra)
    return entry


def _dir_size(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    total = 0
    for root, _dirs, files in os.walk(path):
        for filename in files:
            try:
                total += (Path(root) / filename).stat().st_size
            except OSError:
                continue
    return total


def _host_disk() -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        usage = shutil.disk_usage(str(BASE_DIR))
        used = usage.total - usage.free
        return _source(
            "render_disk",
            "Render Host Disk",
            "Shared Render disk (host-wide)",
            "host",
            used_bytes=used,
            total_bytes=usage.total,
            free_bytes=usage.free,
            detail=f"{round((used / usage.total) * 100, 1)}% of host disk used; shared with PostgreSQL and builds",
            latency_ms=(time.perf_counter() - started) * 1000,
        )
    except Exception as exc:  # pragma: no cover - host dependent
        return _source(
            "render_disk",
            "Render Host Disk",
            "Shared Render disk (host-wide)",
            "host",
            status="unreachable",
            reason=str(exc)[:300],
        )


def _sqlite_usage() -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        paths = [
            Path(SQLITE_DB_PATH),
            Path(str(SQLITE_DB_PATH) + "-wal"),
            Path(str(SQLITE_DB_PATH) + "-shm"),
        ]
        used = 0
        present = []
        for path in paths:
            if path.exists():
                used += path.stat().st_size
                present.append(path.name)
        return _source(
            "sqlite",
            "SQLite Studio DB",
            "studio_memory.db (WAL)",
            "local",
            used_bytes=used,
            detail=", ".join(present) or "database file not created yet",
            latency_ms=(time.perf_counter() - started) * 1000,
        )
    except Exception as exc:
        return _source("sqlite", "SQLite Studio DB", "studio_memory.db (WAL)", "local", status="error", reason=str(exc)[:300])


def _duckdb_usage() -> Dict[str, Any]:
    started = time.perf_counter()
    lakehouse = Path(BASE_DIR) / "data" / "lakehouse"
    try:
        database_files = sorted(lakehouse.glob("**/*.duckdb")) if lakehouse.exists() else []
        database_bytes = sum(_dir_size(path) for path in database_files)
        parquet_bytes = sum(_dir_size(path) for path in lakehouse.glob("**/*.parquet")) if lakehouse.exists() else 0
        used = database_bytes + parquet_bytes
        return _source(
            "duckdb",
            "DuckDB Lakehouse",
            "Local gold_marts + Parquet staging",
            "local",
            used_bytes=used,
            detail=f"{len(database_files)} database file(s), {format_bytes(parquet_bytes)} Parquet staging",
            latency_ms=(time.perf_counter() - started) * 1000,
        )
    except Exception as exc:
        return _source("duckdb", "DuckDB Lakehouse", "Local gold_marts + Parquet staging", "local", status="error", reason=str(exc)[:300])


def _app_footprint() -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        from app.core.storage_inspector import storage_inspector

        footprint = storage_inspector.measure_footprint()
        categories = footprint.get("categories") or {}
        top = sorted(categories.items(), key=lambda item: item[1], reverse=True)[:4]
        detail = ", ".join(f"{key.replace('app_', '')} {value}" for key, value in top if value not in ("0.00 B",))
        return _source(
            "app_footprint",
            "NanoPro App Footprint",
            "Writable app data on Render disk",
            "local",
            used_bytes=footprint.get("bytes") or 0,
            detail=detail or "no writable app data",
            latency_ms=(time.perf_counter() - started) * 1000,
        )
    except Exception as exc:
        return _source("app_footprint", "NanoPro App Footprint", "Writable app data on Render disk", "local", status="error", reason=str(exc)[:300])


def _snowflake_usage() -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        from app.core import snowflake_client

        if not snowflake_client.driver_available():
            return _source(
                "snowflake", "Snowflake DW", "BANK_DB (INFORMATION_SCHEMA)", "cloud",
                status="driver_missing", reason="snowflake-connector-python is not installed on this server.",
            )
        config = snowflake_client.load_config()
        if not config.get("password"):
            return _source(
                "snowflake", "Snowflake DW", "BANK_DB (INFORMATION_SCHEMA)", "cloud",
                status="not_configured", reason="Snowflake password is not present in the Credential Vault or environment.",
            )
        database = str(config.get("database") or "BANK_DB").strip()
        connection = snowflake_client.open_connection(timeout=8)
        try:
            cursor = connection.cursor()
            try:
                cursor.execute(f"ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 6")
            except Exception:
                pass
            cursor.execute(
                f"SELECT COALESCE(SUM(BYTES), 0), COALESCE(SUM(ROW_COUNT), 0), COUNT(*) "
                f"FROM {database}.INFORMATION_SCHEMA.TABLES "
                f"WHERE TABLE_SCHEMA <> 'INFORMATION_SCHEMA'"
            )
            row = cursor.fetchone() or (0, 0, 0)
            used = int(row[0] or 0)
            rows = int(row[1] or 0)
            tables = int(row[2] or 0)
            cursor.close()
        finally:
            connection.close()
        return _source(
            "snowflake", "Snowflake DW", f"{database} (INFORMATION_SCHEMA)", "cloud",
            used_bytes=used,
            detail=f"{tables} tables, {rows:,} rows (compressed table bytes)",
            latency_ms=(time.perf_counter() - started) * 1000,
            no_fixed_quota=True,
        )
    except Exception as exc:
        return _source(
            "snowflake", "Snowflake DW", "BANK_DB (INFORMATION_SCHEMA)", "cloud",
            status="unreachable", reason=str(exc)[:300],
            latency_ms=(time.perf_counter() - started) * 1000,
        )


def _bigquery_usage() -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        from app.core.live_catalog import _bigquery_client

        client, auth_source = _bigquery_client()
        project = client.project
        used = 0
        tables = 0
        datasets = 0
        last_error = ""
        for region in ("region-us", "region-eu", "region-asia-south1"):
            try:
                query = (
                    f"SELECT COALESCE(SUM(total_logical_bytes), 0) AS bytes, COUNT(*) AS tables "
                    f"FROM `{region}`.INFORMATION_SCHEMA.TABLE_STORAGE"
                )
                rows = list(client.query(query).result(timeout=6))
                if rows:
                    used = int(rows[0]["bytes"] or 0)
                    tables = int(rows[0]["tables"] or 0)
                    datasets = int(client.query(
                        f"SELECT COUNT(DISTINCT table_schema) AS n FROM `{region}`.INFORMATION_SCHEMA.TABLE_STORAGE"
                    ).result(timeout=6)[0]["n"] or 0)
                    return _source(
                        "bigquery", "BigQuery", f"{project} ({region})", "cloud",
                        used_bytes=used,
                        detail=f"{datasets} datasets, {tables} tables (logical bytes)",
                        latency_ms=(time.perf_counter() - started) * 1000,
                        no_fixed_quota=True,
                        auth_source=auth_source,
                    )
            except Exception as exc:
                last_error = str(exc)[:200]
                if "hasn't been enabled" in last_error:
                    break
                continue

        # TABLE_STORAGE is not enabled on every project. Fall back to per-dataset
        # __TABLES__ metadata, which still reports real size_bytes.
        list_failed = False
        try:
            dataset_ids = [dataset.dataset_id for dataset in client.list_datasets(max_results=10)]
        except Exception as exc:
            list_failed = True
            dataset_ids = []
            last_error = f"{last_error}; dataset list failed: {str(exc)[:160]}"
        if not dataset_ids:
            if list_failed:
                return _source(
                    "bigquery", "BigQuery", f"{project} (dataset list)", "cloud",
                    status="unreachable", reason=last_error or "Could not list BigQuery datasets.",
                    latency_ms=(time.perf_counter() - started) * 1000,
                )
            return _source(
                "bigquery", "BigQuery", f"{project} (__TABLES__ metadata)", "cloud",
                used_bytes=0,
                total_bytes=BIGQUERY_SANDBOX_CAP_BYTES,
                free_bytes=BIGQUERY_SANDBOX_CAP_BYTES,
                detail="Service account is connected but the project holds 0 datasets; measured 0 B of the 10 GB sandbox cap",
                latency_ms=(time.perf_counter() - started) * 1000,
                no_fixed_quota=True,
                auth_source=auth_source,
            )
        failures = []
        for dataset_id in dataset_ids:
            try:
                query = (
                    f"SELECT COALESCE(SUM(size_bytes), 0) AS bytes, COUNT(*) AS tables "
                    f"FROM `{project}.{dataset_id}.__TABLES__`"
                )
                rows = list(client.query(query).result(timeout=5))
                if rows:
                    used += int(rows[0]["bytes"] or 0)
                    tables += int(rows[0]["tables"] or 0)
                    datasets += 1
            except Exception as exc:
                failures.append(f"{dataset_id}: {str(exc)[:80]}")
        if datasets:
            return _source(
                "bigquery", "BigQuery", f"{project} (__TABLES__ metadata)", "cloud",
                used_bytes=used,
                total_bytes=BIGQUERY_SANDBOX_CAP_BYTES,
                free_bytes=max(0, BIGQUERY_SANDBOX_CAP_BYTES - used),
                detail=f"{datasets} datasets, {tables} tables by size_bytes; 10 GB sandbox cap"
                       + (f"; {len(failures)} dataset(s) unreadable" if failures else ""),
                latency_ms=(time.perf_counter() - started) * 1000,
                no_fixed_quota=True,
                auth_source=auth_source,
            )
        last_error = "; ".join(failures)[:300] or last_error

        return _source(
            "bigquery", "BigQuery", f"{project} (INFORMATION_SCHEMA)", "cloud",
            status="unreachable", reason=last_error or "TABLE_STORAGE view returned no rows.",
            latency_ms=(time.perf_counter() - started) * 1000,
        )
    except Exception as exc:
        return _source(
            "bigquery", "BigQuery", "INFORMATION_SCHEMA.TABLE_STORAGE", "cloud",
            status="unreachable", reason=str(exc)[:300],
            latency_ms=(time.perf_counter() - started) * 1000,
        )


def _aws_credentials() -> Dict[str, str]:
    keys = {
        "access_key": os.environ.get("AWS_ACCESS_KEY_ID", ""),
        "secret_key": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
        "region": os.environ.get("AWS_DEFAULT_REGION", "ap-southeast-2"),
        "bucket": os.environ.get("AWS_S3_BUCKET", "nanopro-data-lake"),
    }
    if keys["access_key"] and keys["secret_key"]:
        return keys
    try:
        from app.core.connection_manager import connection_manager

        config = connection_manager.get_connection_config("AWS_S3_DATA_LAKE", mask=False) or {}
        metadata = config.get("metadata") or {}
        if isinstance(metadata, str):
            metadata = {}
        keys["access_key"] = keys["access_key"] or str(config.get("secret_value") or "")
        keys["secret_key"] = keys["secret_key"] or str(metadata.get("secret_key") or "")
        keys["region"] = keys["region"] or str(metadata.get("region") or "")
        keys["bucket"] = keys["bucket"] or str(metadata.get("bucket") or "")
    except Exception:
        pass
    return keys


def _s3_usage() -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        import boto3
        from botocore.config import Config

        credentials = _aws_credentials()
        if not (credentials["access_key"] and credentials["secret_key"]):
            return _source(
                "s3", "AWS S3 Data Lake", "nanopro-data-lake", "cloud",
                status="not_configured", reason="AWS access key and secret are not present in the Credential Vault or environment.",
            )
        client = boto3.client(
            "s3",
            region_name=credentials["region"] or "ap-southeast-2",
            aws_access_key_id=credentials["access_key"],
            aws_secret_access_key=credentials["secret_key"],
            config=Config(connect_timeout=4, read_timeout=6, retries={"max_attempts": 1}),
        )
        used = 0
        objects = 0
        pages = 0
        truncated = False
        paginator = client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=credentials["bucket"]):
            pages += 1
            for item in page.get("Contents") or []:
                used += int(item.get("Size") or 0)
                objects += 1
            if pages >= 50:
                truncated = True
                break
        return _source(
            "s3", "AWS S3 Data Lake", credentials["bucket"], "cloud",
            used_bytes=used,
            detail=f"{objects:,} objects{'; list truncated at 50 pages' if truncated else ''}",
            latency_ms=(time.perf_counter() - started) * 1000,
            no_fixed_quota=True,
            truncated=truncated,
        )
    except Exception as exc:
        return _source(
            "s3", "AWS S3 Data Lake", "nanopro-data-lake", "cloud",
            status="unreachable", reason=str(exc)[:300],
            latency_ms=(time.perf_counter() - started) * 1000,
        )


_MEASURERS: List[tuple] = [
    ("render_disk", "Render Host Disk", "Shared Render disk (host-wide)", "host", _host_disk),
    ("sqlite", "SQLite Studio DB", "studio_memory.db (WAL)", "local", _sqlite_usage),
    ("duckdb", "DuckDB Lakehouse", "Local gold_marts + Parquet staging", "local", _duckdb_usage),
    ("app_footprint", "NanoPro App Footprint", "Writable app data on Render disk", "local", _app_footprint),
    ("snowflake", "Snowflake DW", "BANK_DB (INFORMATION_SCHEMA)", "cloud", _snowflake_usage),
    ("bigquery", "BigQuery", "INFORMATION_SCHEMA.TABLE_STORAGE", "cloud", _bigquery_usage),
    ("s3", "AWS S3 Data Lake", "nanopro-data-lake", "cloud", _s3_usage),
]


def measure_storage_estate(force: bool = False) -> Dict[str, Any]:
    now = time.time()
    if not force and _cache["data"] is not None and now - _cache["at"] < CACHE_TTL_SECONDS:
        cached = dict(_cache["data"])
        cached["cached"] = True
        cached["cache_age_seconds"] = round(now - _cache["at"], 1)
        return cached

    sources: List[Dict[str, Any]] = []
    pool = ThreadPoolExecutor(max_workers=len(_MEASURERS))
    futures = {
        pool.submit(measurer): (source_id, name, engine, tier)
        for source_id, name, engine, tier, measurer in _MEASURERS
    }
    done: Dict[str, Dict[str, Any]] = {}
    try:
        for future in as_completed(futures, timeout=SOURCE_DEADLINE_SECONDS):
            source_id, name, engine, tier = futures[future]
            try:
                done[source_id] = future.result()
            except Exception as exc:
                done[source_id] = _source(
                    source_id, name, engine, tier,
                    status="error", reason=str(exc)[:300],
                )
    except FuturesTimeout:
        pass
    finally:
        pool.shutdown(wait=False, cancel_futures=True)

    for source_id, name, engine, tier, _measurer in _MEASURERS:
        sources.append(done.get(source_id) or _source(
            source_id, name, engine, tier,
            status="timeout",
            reason=f"No response within {int(SOURCE_DEADLINE_SECONDS)}s.",
        ))

    local_used = sum(source["used_bytes"] or 0 for source in sources if source.get("tier") == "local" and source.get("status") == "live")
    cloud_used = sum(source["used_bytes"] or 0 for source in sources if source.get("tier") == "cloud" and source.get("status") == "live")
    available = sum(1 for source in sources if source.get("status") == "live")

    result = {
        "status": "success",
        "code_revision": "storage-estate-5",
        "generated_at": now,
        "generated_at_iso": datetime.now().astimezone().isoformat(timespec="seconds"),
        "sources": sources,
        "summary": {
            "live_sources": available,
            "total_sources": len(sources),
            "local_used_bytes": local_used,
            "local_used_formatted": format_bytes(local_used),
            "cloud_used_bytes": cloud_used,
            "cloud_used_formatted": format_bytes(cloud_used),
        },
        "notes": [
            "Every value is measured live on the Render host at request time; unavailable engines report the reason instead of an estimate.",
            "Snowflake, BigQuery and S3 are usage-based; they have no fixed storage quota, so only used bytes are reported.",
            "The Render host disk is shared with other workspace processes, so its free space is host-wide, not exclusive to NanoPro.",
        ],
        "cached": False,
    }
    _cache["at"] = now
    _cache["data"] = result
    return result
