"""Detects BigQuery CREATE DDL in an AI Lab chat prompt and executes it.

Only reached for prompts that mention BigQuery; the actual statement set is
re-validated by app.core.bigquery_ddl before anything runs.
"""

import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

_FENCE = re.compile(r"```(?:sql)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)
_CREATE = re.compile(r"CREATE\s+(SCHEMA|DATASET|TABLE)\b", re.IGNORECASE)
_DATASET_REQUEST = re.compile(
    r"create\s+(?:a\s+|an\s+)?(?:dataset|schema)\s+(?:named\s+|called\s+)?`?([A-Za-z0-9_\-\.]+)`?",
    re.IGNORECASE,
)
_CREATE_INTENT = re.compile(r"\b(create|build|make|banav\w*)\b|बनव|तयार", re.IGNORECASE)
_DOTTED_NAME = re.compile(r"\b([A-Za-z][A-Za-z0-9_\-]*)\.([A-Za-z][A-Za-z0-9_]*)\b")
_SPEC_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_SPEC_TYPES = {
    "STRING": "STRING",
    "INT64": "INT64",
    "INTEGER": "INT64",
    "NUMERIC": "NUMERIC",
    "BIGNUMERIC": "BIGNUMERIC",
    "FLOAT64": "FLOAT64",
    "BOOL": "BOOL",
    "BOOLEAN": "BOOL",
    "DATE": "DATE",
    "DATETIME": "DATETIME",
    "TIME": "TIME",
    "TIMESTAMP": "TIMESTAMP",
    "JSON": "JSON",
    "BYTES": "BYTES",
    "GEOGRAPHY": "GEOGRAPHY",
}
_SPEC_TYPE = re.compile(
    r"\b(" + "|".join(sorted(_SPEC_TYPES, key=len, reverse=True)) + r")\b",
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
        # Only trust a raw statement when it carries SQL syntax, otherwise
        # "Create dataset foo in BigQuery" is read as prose, not as DDL.
        if "`" in text or "(" in text or re.search(r"\bIF\s+NOT\s+EXISTS\b", text, re.IGNORECASE):
            return text
    # Natural-language dataset request, e.g. "create dataset foo in BigQuery".
    dataset = _DATASET_REQUEST.search(text)
    if dataset:
        name = dataset.group(1)
        if name.lower() not in {"in", "on", "for", "with", "named", "called", "at"}:
            return f"CREATE SCHEMA IF NOT EXISTS `{name}`"
    return ""


def _split_spec_cells(line: str) -> List[str]:
    if "|" in line:
        cells = [cell.strip() for cell in line.split("|")]
    else:
        cells = [cell.strip() for cell in re.split(r"\t+|\s{2,}", line)]
    while cells and not cells[0]:
        cells.pop(0)
    while cells and not cells[-1]:
        cells.pop()
    return cells


def _parse_spec_columns(prompt: str) -> List[Dict[str, Any]]:
    columns: List[Dict[str, Any]] = []
    for raw in (prompt or "").splitlines():
        line = raw.strip()
        if not line or set(line) <= set("-|: "):
            continue
        cells = _split_spec_cells(line)
        if len(cells) < 3:
            continue
        if re.fullmatch(r"[0-9०-९]+[.)]?", cells[0]):
            cells = cells[1:]
        if len(cells) < 3:
            continue
        name, type_cell, constraint = cells[0], cells[1], cells[2]
        if not _SPEC_NAME.match(name):
            continue
        match = _SPEC_TYPE.search(type_cell.upper())
        if not match:
            continue
        text = constraint.upper()
        columns.append({
            "name": name,
            "type": _SPEC_TYPES[match.group(1).upper()],
            "not_null": "NOT NULL" in text,
            "pk": "PRIMARY KEY" in text,
            "fk": "FK" in text or "FOREIGN KEY" in text,
            "unique": "UNIQUE" in text,
            "partition": "PARTITION" in text,
        })
    return columns


def _spec_table_target(prompt: str) -> Optional[Tuple[str, str]]:
    candidates = [
        (dataset, table)
        for dataset, table in _DOTTED_NAME.findall(prompt or "")
        if _SPEC_NAME.match(dataset) and _SPEC_NAME.match(table)
    ]
    if not candidates:
        return None
    preferred = [pair for pair in candidates if re.search(r"nanopro|bronze", pair[0], re.IGNORECASE)]
    return preferred[0] if preferred else candidates[0]


def build_spec_sql(prompt: str) -> Tuple[str, List[str]]:
    """Build CREATE TABLE DDL from a pasted row-wise column spec.

    Returns (sql, notes); sql is empty when the prompt is not a column spec.
    """
    text = prompt or ""
    if not _CREATE_INTENT.search(text):
        return "", []
    target = _spec_table_target(text)
    if not target:
        return "", []
    columns = _parse_spec_columns(text)
    if len(columns) < 2:
        return "", []

    dataset, table = target
    definitions: List[str] = []
    primary_key: List[str] = []
    partition_field = ""
    saw_unique = False
    saw_fk = False
    for column in columns:
        parts = [column["name"], column["type"]]
        if column["not_null"] or column["pk"]:
            parts.append("NOT NULL")
        if column["pk"]:
            primary_key.append(column["name"])
        if column["partition"]:
            partition_field = column["name"]
        saw_unique = saw_unique or column["unique"]
        saw_fk = saw_fk or column["fk"]
        definitions.append(" ".join(parts))
    if primary_key:
        definitions.append("PRIMARY KEY (" + ", ".join(primary_key) + ") NOT ENFORCED")

    sql = (
        f"CREATE TABLE IF NOT EXISTS `{dataset}.{table}` (\n  "
        + ",\n  ".join(definitions)
        + "\n)"
    )
    if partition_field:
        sql += f"\nPARTITION BY {partition_field}"

    notes: List[str] = []
    if saw_unique:
        notes.append(
            "UNIQUE constraints were skipped: BigQuery only supports primary and foreign keys."
        )
    if saw_fk:
        notes.append(
            "Foreign keys were skipped: BigQuery requires the referenced column to be the "
            "referenced table's PRIMARY KEY and only accepts constraints at table creation."
        )
    return sql, notes


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


def _markdown(result: Dict[str, Any], notes: Optional[List[str]] = None) -> str:
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
        partition = result.get("partition_field") or ""
        if partition:
            partition = f"{partition} ({result.get('partition_type') or 'DAY'})"
        rows.append(f"| **Partition** | {partition or '—'} |")
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
    if notes:
        body += "\n\n**Spec notes**\n\n" + "\n".join(f"- {note}" for note in notes)
    return body


def maybe_handle(prompt: str) -> Optional[Dict[str, Any]]:
    if "bigquery" not in (prompt or "").lower():
        return None
    sql = extract_sql(prompt)
    notes: List[str] = []
    if not sql:
        sql, notes = build_spec_sql(prompt)
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
        "response": _markdown(result, notes),
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
            "partition_field": result.get("partition_field") or "",
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
