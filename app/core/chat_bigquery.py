"""Durable chat archive in Google BigQuery.

The BigQuery sandbox refuses DML (INSERT/UPDATE/DELETE/MERGE), so every write
here is a JSON load job with WRITE_APPEND. Rows are versioned by ``updated_ts``
and reads collapse duplicates with ROW_NUMBER(), so appends behave like upserts
and a delete is just a row with ``deleted = true``.
"""

import os
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

DATASET = os.getenv("NANOPRO_CHAT_BQ_DATASET", "nanopro_studio")
LOCATION = os.getenv("NANOPRO_CHAT_BQ_LOCATION", "US")

TABLES: Dict[str, Dict[str, Any]] = {
    "projects": {
        "table": "ai_chat_projects",
        "id": "project_id",
        "columns": [
            ("project_id", "STRING", "NULLABLE"),
            ("user_key", "STRING", "NULLABLE"),
            ("name", "STRING", "NULLABLE"),
            ("description", "STRING", "NULLABLE"),
            ("created_at", "FLOAT64", "NULLABLE"),
            ("updated_at", "FLOAT64", "NULLABLE"),
            ("deleted", "BOOL", "NULLABLE"),
            ("updated_ts", "TIMESTAMP", "NULLABLE"),
        ],
    },
    "chats": {
        "table": "ai_chat_sessions",
        "id": "chat_id",
        "columns": [
            ("chat_id", "STRING", "NULLABLE"),
            ("user_key", "STRING", "NULLABLE"),
            ("project_id", "STRING", "NULLABLE"),
            ("title", "STRING", "NULLABLE"),
            ("model", "STRING", "NULLABLE"),
            ("effort", "STRING", "NULLABLE"),
            ("is_pinned", "BOOL", "NULLABLE"),
            ("message_count", "INT64", "NULLABLE"),
            ("created_at", "FLOAT64", "NULLABLE"),
            ("updated_at", "FLOAT64", "NULLABLE"),
            ("deleted", "BOOL", "NULLABLE"),
            ("updated_ts", "TIMESTAMP", "NULLABLE"),
        ],
    },
    "messages": {
        "table": "ai_chat_messages",
        "id": "message_id",
        "columns": [
            ("message_id", "STRING", "NULLABLE"),
            ("chat_id", "STRING", "NULLABLE"),
            ("user_key", "STRING", "NULLABLE"),
            ("role", "STRING", "NULLABLE"),
            ("content", "STRING", "NULLABLE"),
            ("content_type", "STRING", "NULLABLE"),
            ("model_routed", "STRING", "NULLABLE"),
            ("model_executed", "STRING", "NULLABLE"),
            ("model_name", "STRING", "NULLABLE"),
            ("lab_name", "STRING", "NULLABLE"),
            ("flag", "STRING", "NULLABLE"),
            ("country", "STRING", "NULLABLE"),
            ("duration_ms", "FLOAT64", "NULLABLE"),
            ("routing_math", "STRING", "NULLABLE"),
            ("metadata", "STRING", "NULLABLE"),
            ("created_at", "FLOAT64", "NULLABLE"),
            ("deleted", "BOOL", "NULLABLE"),
            ("updated_ts", "TIMESTAMP", "NULLABLE"),
        ],
    },
    "attachments": {
        "table": "ai_chat_attachments",
        "id": "attachment_id",
        "columns": [
            ("attachment_id", "STRING", "NULLABLE"),
            ("chat_id", "STRING", "NULLABLE"),
            ("message_id", "STRING", "NULLABLE"),
            ("user_key", "STRING", "NULLABLE"),
            ("kind", "STRING", "NULLABLE"),
            ("name", "STRING", "NULLABLE"),
            ("mime_type", "STRING", "NULLABLE"),
            ("size_bytes", "INT64", "NULLABLE"),
            ("data", "STRING", "NULLABLE"),
            ("created_at", "FLOAT64", "NULLABLE"),
            ("deleted", "BOOL", "NULLABLE"),
            ("updated_ts", "TIMESTAMP", "NULLABLE"),
        ],
    },
}

_client_lock = threading.RLock()
_client_cache: Optional[Any] = None
_client_source = ""
_client_error = ""
_schema_ready = False
_schema_error = ""
_last_ok_at = 0.0


def _reset_client() -> None:
    global _client_cache, _schema_ready, _client_error, _client_source
    _client_cache = None
    _schema_ready = False
    _client_error = ""
    _client_source = ""


def get_client() -> Tuple[Any, str]:
    """Returns (bigquery.Client, auth source). Raises if credentials are absent."""
    global _client_cache, _client_source, _client_error
    with _client_lock:
        if _client_cache is not None:
            return _client_cache, _client_source
        try:
            from app.core.live_catalog import _bigquery_client

            client, source = _bigquery_client()
            _client_cache = client
            _client_source = source
            _client_error = ""
            return client, source
        except Exception as exc:
            _client_error = str(exc)[:300]
            raise


def _schema_objects(client) -> Dict[str, List[Any]]:
    from google.cloud import bigquery

    return {
        entity: [bigquery.SchemaField(f, t, mode=m) for f, t, m in spec["columns"]]
        for entity, spec in TABLES.items()
    }


def ensure_schema() -> Dict[str, Any]:
    """Creates the dataset and tables when missing. Safe to call repeatedly."""
    global _schema_ready, _schema_error
    with _client_lock:
        if _schema_ready:
            return {"status": "ready", "dataset": DATASET, "location": LOCATION}
        try:
            from google.cloud import bigquery

            client, _source = get_client()
            dataset_ref = bigquery.Dataset(f"{client.project}.{DATASET}")
            dataset_ref.location = LOCATION
            try:
                client.create_dataset(dataset_ref, exists_ok=True)
            except Exception:
                client.get_dataset(dataset_ref)  # surfaces a clearer permission error
            schemas = _schema_objects(client)
            for name, spec in TABLES.items():
                table = bigquery.Table(f"{client.project}.{DATASET}.{spec['table']}", schema=schemas[name])
                try:
                    client.create_table(table, exists_ok=True)
                except Exception:
                    client.get_table(table.reference)
            _schema_ready = True
            _schema_error = ""
            return {"status": "ready", "dataset": DATASET, "location": LOCATION}
        except Exception as exc:
            _schema_error = str(exc)[:400]
            raise


def _timestamp(ts: Optional[float]) -> str:
    value = float(ts or time.time())
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()


def _normalize_row(entity: str, row: Dict[str, Any]) -> Dict[str, Any]:
    spec = TABLES[entity]
    allowed = {field for field, _t, _m in spec["columns"]}
    clean = {}
    for key, value in row.items():
        if key not in allowed:
            continue
        if value is None:
            clean[key] = None
        elif key == "updated_ts":
            clean[key] = _timestamp(value) if not isinstance(value, str) else value
        elif isinstance(value, float) and value != value:  # NaN
            clean[key] = None
        else:
            clean[key] = value
    if "deleted" not in clean:
        clean["deleted"] = False
    if "updated_ts" not in clean or not clean["updated_ts"]:
        clean["updated_ts"] = _timestamp(None)
    return clean


def load_rows(entity: str, rows: List[Dict[str, Any]]) -> int:
    """Appends rows with a load job (sandbox-compatible). Returns rows accepted."""
    if not rows:
        return 0
    from google.cloud import bigquery

    ensure_schema()
    client, _source = get_client()
    spec = TABLES[entity]
    payload = [_normalize_row(entity, row) for row in rows]
    job_config = bigquery.LoadJobConfig(
        schema=[bigquery.SchemaField(f, t, mode=m) for f, t, m in spec["columns"]],
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    table_ref = f"{client.project}.{DATASET}.{spec['table']}"
    job = client.load_table_from_json(payload, table_ref, job_config=job_config)
    job.result(timeout=25)
    if getattr(job, "errors", None):
        raise RuntimeError(str(job.errors)[:400])
    global _last_ok_at
    _last_ok_at = time.time()
    return len(payload)


def fetch_rows(entity: str, user_key: str, limit: int = 5000) -> List[Dict[str, Any]]:
    """Latest version per id for one user, tombstones included."""
    from google.cloud import bigquery

    ensure_schema()
    client, _source = get_client()
    spec = TABLES[entity]
    table_ref = f"`{client.project}.{DATASET}.{spec['table']}`"
    id_col = spec["id"]
    query = (
        f"SELECT * EXCEPT(rn) FROM ("
        f"  SELECT *, ROW_NUMBER() OVER (PARTITION BY {id_col} ORDER BY updated_ts DESC) AS rn"
        f"  FROM {table_ref} WHERE user_key = @user_key"
        f") WHERE rn = 1"
    )
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("user_key", "STRING", user_key)],
        maximum_bytes_billed=2 * 1024 ** 3,
    )
    job = client.query(query, job_config=job_config)
    rows = [dict(row.items()) for row in job.result(timeout=25)][:limit]
    global _last_ok_at
    _last_ok_at = time.time()
    return rows


def status() -> Dict[str, Any]:
    state: Dict[str, Any] = {
        "dataset": DATASET,
        "location": LOCATION,
        "schema_ready": _schema_ready,
        "last_ok_at": _last_ok_at or None,
    }
    try:
        client, source = get_client()
        state.update({"configured": True, "auth_source": source, "project": client.project})
    except Exception as exc:
        state.update({"configured": False, "auth_source": "", "error": str(exc)[:300]})
        return state
    if _schema_error:
        state["schema_error"] = _schema_error
    return state
