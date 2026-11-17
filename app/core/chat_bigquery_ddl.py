"""Detects BigQuery CREATE DDL in an AI Lab chat prompt and executes it.

Only reached for prompts that mention BigQuery; the actual statement set is
re-validated by app.core.bigquery_ddl before anything runs.
"""

import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

_FENCE = re.compile(r"```(?:sql)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)
_CREATE = re.compile(r"CREATE\s+(SCHEMA|DATASET|TABLE)\b", re.IGNORECASE)
_DATASET_REQUEST = re.compile(
    r"create\s+(?:a\s+|an\s+)?(?:dataset|schema)\s+(?:named\s+|called\s+)?`?([A-Za-z0-9_\-\.]+)`?",
    re.IGNORECASE,
)


def extract_sql(prompt: str) -> str:
    for block in _FENCE.findall(prompt or ""):
        if _CREATE.search(block):
            return block.strip()
    text = (prompt or "").strip()
    marker = "execute bigquery ddl:"
    if text.lower().startswith(marker):
        return text[len(marker):].strip()
    if _CREATE.match(text):
        return text
    # Natural-language dataset request, e.g. "create dataset foo in BigQuery".
    dataset = _DATASET_REQUEST.search(text)
    if dataset:
        name = dataset.group(1)
        if name.lower() not in {"in", "on", "for", "with", "named", "called", "at"}:
            return f"CREATE SCHEMA IF NOT EXISTS `{name}`"
    return ""


def _column_lines(result: Dict[str, Any]) -> str:
    primary_key = {name.upper() for name in result.get("primary_key") or []}
    lines = []
    for column in result.get("columns") or []:
        flags = []
        if column.get("name", "").upper() in primary_key:
            flags.append("PRIMARY KEY")
        if column.get("mode") == "REQUIRED":
            flags.append("NOT NULL")
        suffix = " " + " ".join(flags) if flags else ""
        lines.append(f"{column.get('name')} {column.get('type')}{suffix}")
    return "\n".join(lines)


def _markdown(result: Dict[str, Any]) -> str:
    if result.get("status") != "success":
        executed = "\n".join(f"- `{stmt}`" for stmt in result.get("executed") or [])
        return (
            "### ☁️ Google BigQuery — DDL failed\n\n"
            f"**Error:** {result.get('error') or 'Unknown error'}\n\n"
            + (f"**Statements that already ran**\n\n{executed}\n" if executed else "")
        )

    table_id = result.get("table_id")
    dataset_id = result.get("dataset_id") or ""
    objects = result.get("objects") or []
    dataset = next((obj for obj in objects if obj.get("kind") == "dataset"), None)
    rows = [
        "| Field | Value |",
        "| :--- | :--- |",
        f"| **Project** | `{result.get('project')}` |",
        f"| **Auth source** | {result.get('auth_source')} |",
        f"| **Statements executed** | {result.get('statements_executed')} |",
    ]
    if dataset:
        rows.append(f"| **Dataset** | `{dataset.get('id')}` ({dataset.get('location')}) |")
    elif dataset_id:
        rows.append(f"| **Dataset** | `{dataset_id}` |")
    if table_id:
        rows.append(f"| **Table** | `{dataset_id}.{table_id}` |")
        rows.append(f"| **Columns** | {(len(result.get('columns') or []))} |")
        cluster = ", ".join(result.get("cluster_fields") or []) or "—"
        rows.append(f"| **Cluster keys** | {cluster} |")
        primary = ", ".join(result.get("primary_key") or []) or "—"
        rows.append(f"| **Primary key** | {primary} |")
        rows.append(f"| **Rows** | {result.get('rows', 0)} |")

    body = (
        "### ☁️ Google BigQuery — DDL executed and verified\n\n"
        "The statements ran on **Google Cloud BigQuery** and each object was read back "
        "from the live API.\n\n" + "\n".join(rows)
    )
    if result.get("columns"):
        body += "\n\n**Verified schema**\n\n```sql\n" + _column_lines(result) + "\n```"
    return body


def maybe_handle(prompt: str) -> Optional[Dict[str, Any]]:
    if "bigquery" not in (prompt or "").lower():
        return None
    sql = extract_sql(prompt)
    if not sql:
        return None

    started = time.time()
    from app.core.bigquery_ddl import DdlRejected, execute

    try:
        result = execute(sql)
    except DdlRejected as exc:
        result = {"status": "rejected", "error": str(exc)}
    except Exception as exc:
        result = {"status": "error", "error": str(exc)[:500]}

    duration_ms = round((time.time() - started) * 1000)
    ok = result.get("status") == "success"
    payload: Dict[str, Any] = {
        "status": "success" if ok else "error",
        "response": _markdown(result),
        "message": result.get("error") or "",
        "model_routed": "google-cloud/bigquery",
        "model_executed": "google-cloud/bigquery-ddl",
        "model_name": "Google Cloud BigQuery — DDL Agent",
        "lab_name": "Google Cloud",
        "country": "United States",
        "flag": "☁️",
        "date_formatted": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
        "duration_ms": duration_ms,
        "routing_decision": {
            "selected_model": "google-cloud/bigquery-ddl",
            "task_domain": "Google BigQuery schema management (CREATE-only)",
            "sla_target_ms": 3000,
            "sla_met": duration_ms <= 3000,
        },
        "bigquery": {
            "project": result.get("project"),
            "dataset": result.get("dataset_id"),
            "table": result.get("table_id"),
            "cluster_fields": result.get("cluster_fields") or [],
            "objects": result.get("objects") or [],
        },
    }
    if ok and result.get("table_id"):
        payload["action"] = "CREATE_TABLE"
        payload["schema_name"] = result.get("dataset_id")
        payload["table_name"] = result.get("table_id")
        payload["rows"] = result.get("rows", 0)
        primary_key = {name.upper() for name in result.get("primary_key") or []}
        payload["columns"] = [
            {
                "name": column.get("name"),
                "type": column.get("type")
                + (" PRIMARY KEY" if column.get("name", "").upper() in primary_key else "")
                + (" NOT NULL" if column.get("mode") == "REQUIRED" else ""),
            }
            for column in result.get("columns") or []
        ]
    elif ok:
        payload["action"] = "CREATE_SCHEMA"
        payload["schema_name"] = result.get("dataset_id")
    return payload
