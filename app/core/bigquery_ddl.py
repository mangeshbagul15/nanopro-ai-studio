"""CREATE-only BigQuery DDL requested from the AI Lab chat.

Executes schema/dataset/table creation and verifies each object with the
BigQuery client afterwards, so the chat reports real state instead of a
simulated result. Destructive statements stay blocked.
"""

import re
import time
from typing import Any, Dict, List, Optional

DEFAULT_LOCATION = "asia-south1"

_ALLOWED = re.compile(r"^\s*CREATE\s+(SCHEMA|DATASET|TABLE)\b", re.IGNORECASE)
_FORBIDDEN = re.compile(
    r"\b(DROP|TRUNCATE|DELETE|ALTER|MERGE|GRANT|REVOKE|UPDATE|INSERT)\b",
    re.IGNORECASE,
)
_SCHEMA_WITHOUT_OPTIONS = re.compile(r"^\s*CREATE\s+(SCHEMA|DATASET)\b", re.IGNORECASE)
_TABLE_TARGET = re.compile(
    r"^\s*CREATE\s+(?:TABLE\s+)?(?:IF\s+NOT\s+EXISTS\s+)?`?([A-Za-z0-9_\-\.]+)`?",
    re.IGNORECASE,
)


class DdlRejected(ValueError):
    """Raised when a statement is not a permitted CREATE-only operation."""


def split_statements(sql: str) -> List[str]:
    statements: List[str] = []
    buf: List[str] = []
    quote: Optional[str] = None
    depth = 0
    for ch in sql:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"', "`"):
            quote = ch
            buf.append(ch)
            continue
        if ch == "(":
            depth += 1
        elif ch == ")" and depth:
            depth -= 1
        if ch == ";" and depth == 0:
            statement = "".join(buf).strip()
            if statement:
                statements.append(statement)
            buf = []
            continue
        buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)
    return statements


def _with_default_location(statement: str) -> str:
    if "options" in statement.lower():
        return statement
    return f"{statement}\nOPTIONS(location='{DEFAULT_LOCATION}')"


def validate(statements: List[str]) -> List[str]:
    if not statements:
        raise DdlRejected("No CREATE statement was found.")
    clean: List[str] = []
    for statement in statements:
        if not _ALLOWED.match(statement):
            raise DdlRejected(
                "Only CREATE SCHEMA / DATASET / TABLE are allowed from chat."
            )
        if _FORBIDDEN.search(statement):
            raise DdlRejected("Destructive SQL keywords are blocked.")
        if _SCHEMA_WITHOUT_OPTIONS.match(statement):
            statement = _with_default_location(statement)
        clean.append(statement)
    return clean


def _dataset_and_table(target: str) -> tuple:
    parts = [part for part in target.split(".") if part]
    if len(parts) < 2:
        return None, parts[-1] if parts else ""
    return parts[-2], parts[-1]


def _primary_key(client: Any, dataset_id: str, table_id: str) -> List[str]:
    try:
        from google.cloud import bigquery

        sql = (
            f"SELECT column_name FROM `{dataset_id}.INFORMATION_SCHEMA.KEY_COLUMN_USAGE` "
            "WHERE table_name = @table AND constraint_name IN ("
            f"SELECT constraint_name FROM `{dataset_id}.INFORMATION_SCHEMA.TABLE_CONSTRAINTS` "
            "WHERE table_name = @table AND constraint_type = 'PRIMARY KEY')"
        )
        job = client.query(
            sql,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("table", "STRING", table_id)]
            ),
        )
        return [row[0] for row in job.result(timeout=30)]
    except Exception:
        return []


def _describe_table(client: Any, table_ref: str) -> Dict[str, Any]:
    table = client.get_table(table_ref)
    columns = [
        {"name": field.name, "type": field.field_type, "mode": field.mode}
        for field in table.schema
    ]
    primary_key: List[str] = []
    try:
        constraints = getattr(table, "table_constraints", None)
        if not constraints:
            constraints = (getattr(table, "_properties", None) or {}).get("tableConstraints")
        pk = (constraints or {}).get("primaryKey") or {}
        primary_key = list(pk.get("columns") or [])
    except Exception:
        primary_key = []
    if not primary_key:
        primary_key = _primary_key(client, table.dataset_id, table.table_id)
    partitioning = getattr(table, "time_partitioning", None)
    return {
        "kind": "table",
        "id": f"{table.dataset_id}.{table.table_id}",
        "dataset_id": table.dataset_id,
        "table_id": table.table_id,
        "num_columns": len(columns),
        "num_rows": int(table.num_rows or 0),
        "columns": columns,
        "cluster_fields": list(table.clustering_fields or []),
        "primary_key": primary_key,
        "partition_field": (partitioning.field if partitioning else "") or "",
        "partition_type": (partitioning.type_ if partitioning else "") or "",
    }


def execute(sql: str) -> Dict[str, Any]:
    started = time.time()
    statements = validate(split_statements(sql))
    try:
        from app.core.live_catalog import _bigquery_client
    except Exception as exc:
        return {"status": "error", "error": f"BigQuery driver unavailable: {exc}"}

    try:
        client, auth_source = _bigquery_client()
    except Exception as exc:
        return {
            "status": "error",
            "error": f"BigQuery credentials unavailable: {str(exc)[:300]}",
        }

    objects: List[Dict[str, Any]] = []
    executed: List[str] = []
    for statement in statements:
        try:
            job = client.query(statement)
            job.result(timeout=120)
        except Exception as exc:
            return {
                "status": "error",
                "error": str(exc)[:600],
                "executed": executed,
                "objects": objects,
                "auth_source": auth_source,
            }
        executed.append(statement.splitlines()[0][:200])
        if _ALLOWED.match(statement).group(1).upper() in ("SCHEMA", "DATASET"):
            match = re.search(
                r"CREATE\s+(?:SCHEMA|DATASET)\s+(?:IF\s+NOT\s+EXISTS\s+)?`?([A-Za-z0-9_\-\.]+)`?",
                statement,
                re.IGNORECASE,
            )
            dataset_id = match.group(1).split(".")[-1] if match else ""
            try:
                dataset = client.get_dataset(dataset_id)
                objects.append(
                    {
                        "kind": "dataset",
                        "id": dataset.dataset_id,
                        "location": dataset.location,
                    }
                )
            except Exception as exc:
                objects.append(
                    {"kind": "dataset", "id": dataset_id, "verify_error": str(exc)[:200]}
                )
        else:
            match = _TABLE_TARGET.match(statement)
            target = match.group(1) if match else ""
            dataset_id, table_id = _dataset_and_table(target)
            ref = f"{client.project}.{dataset_id}.{table_id}" if dataset_id else target
            try:
                objects.append(_describe_table(client, ref))
            except Exception as exc:
                objects.append(
                    {"kind": "table", "id": ref, "verify_error": str(exc)[:300]}
                )

    table = next((obj for obj in objects if obj.get("kind") == "table"), None)
    dataset = next((obj for obj in objects if obj.get("kind") == "dataset"), None)
    return {
        "status": "success",
        "engine": "Google Cloud BigQuery",
        "project": client.project,
        "auth_source": auth_source,
        "statements_executed": len(executed),
        "executed": executed,
        "objects": objects,
        "dataset_id": (table or dataset or {}).get(
            "dataset_id", (dataset or {}).get("id")
        ),
        "table_id": (table or {}).get("table_id"),
        "columns": (table or {}).get("columns", []),
        "cluster_fields": (table or {}).get("cluster_fields", []),
        "primary_key": (table or {}).get("primary_key", []),
        "partition_field": (table or {}).get("partition_field", ""),
        "partition_type": (table or {}).get("partition_type", ""),
        "duration_ms": round((time.time() - started) * 1000),
    }
