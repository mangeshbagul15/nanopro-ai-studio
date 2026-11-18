"""Chat-driven data operations for the AI Lab.

Handles two kinds of prompts that the Explorer admin path does not:

* "सगळ्या table मध्ये 50 sample records टाका" — generates schema-faithful rows
  for every requested table (foreign keys follow the parent keys) and runs the
  INSERT against BigQuery.
* A fenced ```sql block (or "execute bigquery query: ...") — runs one
  statement. SELECT/WITH are read-only; INSERT/UPDATE/DELETE are accepted only
  inside nanopro_cbs_bronze and UPDATE/DELETE must carry a WHERE clause.

Anything else returns None so the normal chat answering continues.
"""

import re
import time
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_SCHEMA = "nanopro_cbs_bronze"

_SQL_FENCE = re.compile(r"```(?:sql)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)
_INSERT_VERB = re.compile(r"\binsert\b|भरा|भरून|टाका|घाला|\btak\w*\b", re.IGNORECASE)
_SAMPLE_WORD = re.compile(
    r"sample|records?|rows?|data|नमुना|डेटा|रिकॉर्ड|ओळी", re.IGNORECASE
)
_ALL_TABLES = re.compile(r"\ball\b|saglya|सगळ्या|सर्व|pratyek|प्रत्येक|each", re.IGNORECASE)
_COUNT = re.compile(r"(\d{1,4})\s*(?:sample\s+)?(?:records?|rows?|रिकॉर्ड|ओळी)", re.IGNORECASE)

# Schema changes belong to the DDL handler; returning None keeps them on that path.
_SCHEMA_CHANGE = re.compile(r"^\s*(create|alter|drop|truncate|merge|grant|revoke)\b", re.IGNORECASE)

# Relations documented in the Bronze specs. They also order the inserts so a
# child table's foreign keys point at rows that already exist.
KNOWN_REFS: Dict[Tuple[str, str], Tuple[str, str]] = {
    ("VCT", "TRAN_ID"): ("HTD", "TRAN_ID"),
    ("VCT", "FORACID"): ("GAM", "ACID"),
    ("VCT", "SOL_ID"): ("SOL", "SOL_ID"),
    ("TAM_LAM", "FORACID"): ("GAM", "ACID"),
    ("TAM_LAM", "CUST_ID"): ("CMG", "CUST_ID"),
    ("TAM_LAM", "SOL_ID"): ("SOL", "SOL_ID"),
    ("GAM", "CUST_ID"): ("CMG", "CUST_ID"),
    ("GAM", "SOL_ID"): ("SOL", "SOL_ID"),
    ("HTD", "FORACID"): ("GAM", "ACID"),
    ("UBO", "CUST_ID"): ("CMG", "CUST_ID"),
    ("SWIFT_MSG", "FORACID"): ("GAM", "ACID"),
    ("CMG", "HOME_BRANCH_SOL_ID"): ("SOL", "SOL_ID"),
}

_INT_TYPES = {"INT64", "INTEGER", "BIGINT", "SMALLINT", "INT"}
_NUM_TYPES = {"NUMERIC", "BIGNUMERIC", "FLOAT64", "FLOAT", "REAL", "DECIMAL", "NUMBER"}
_BOOL_TYPES = {"BOOL", "BOOLEAN"}

_NAMES = [
    "Rahul Sharma", "Priya Patil", "Amit Deshmukh", "Sneha Joshi",
    "Vikram Rao", "Anjali Kulkarni", "Rohit Mehta", "Kavita Nair",
    "Suresh Iyer", "Meera Gupta", "Arjun Singh", "Pooja Bhosale",
]
_CITIES = ["Mumbai", "Pune", "Nagpur", "Nashik", "Thane", "Kolhapur"]
_STATES = ["Maharashtra", "Karnataka", "Gujarat", "Delhi"]
_KINDS = ["CASH", "TRANSFER", "CHEQUE", "UPI", "NEFT"]


def _client():
    from app.core.catalog_admin import _client as catalog_client

    return catalog_client()


def _base_type(type_sql: str) -> str:
    return (type_sql or "STRING").split("(", 1)[0].upper()


def _scale(type_sql: str) -> int:
    match = re.search(r"\(\s*\d+\s*,\s*(\d+)\s*\)", type_sql or "")
    return int(match.group(1)) if match else 2


def _key_value(column: str, index: int) -> str:
    base = column[:-3] if column.upper().endswith("_ID") else column
    prefix = re.sub(r"[^A-Z0-9]", "", base.upper())[:6] or "KEY"
    return f"{prefix}{index:08d}"


def _scalar(name: str, type_sql: str, index: int) -> Any:
    upper = name.upper()
    base = _base_type(type_sql)
    if base in _BOOL_TYPES:
        return index % 2 == 0
    if base in _INT_TYPES:
        if "COUNT" in upper or "QTY" in upper:
            return (index % 7) + 1
        if "AGE" in upper:
            return 21 + (index % 45)
        return index
    if base in _NUM_TYPES:
        return round(Decimal(250) + Decimal(index * 137) + Decimal("0.25"), _scale(type_sql))
    if base == "DATE":
        if "DOB" in upper or "BIRTH" in upper:
            return (date(1980, 1, 1) + timedelta(days=index * 97)).isoformat()
        # Bronze tables can be date-partitioned with 60-day expiry, so rows
        # dated months back land in partitions that are already gone.
        return (date.today() - timedelta(days=index % 20)).isoformat()
    if base == "DATETIME":
        return (datetime.now(timezone.utc) - timedelta(minutes=index)).strftime("%Y-%m-%d %H:%M:%S")
    if base == "TIMESTAMP":
        return (datetime.now(timezone.utc) - timedelta(minutes=index)).strftime("%Y-%m-%d %H:%M:%S+00:00")
    if base == "TIME":
        return f"{(9 + index % 8):02d}:{(index * 7) % 60:02d}:00"
    if base == "JSON":
        return '{"row": %d}' % index
    if base == "BYTES":
        return "row-%05d" % index
    if base == "GEOGRAPHY":
        return (72.8777 + (index % 10) / 1000, 19.0760 + (index % 10) / 1000)

    if "EMAIL" in upper:
        return f"user{index:04d}@example.com"
    if "PHONE" in upper or "MOBILE" in upper:
        return f"98{70000000 + index:08d}"
    if "IFSC" in upper:
        return f"SBIN0{index:06d}"
    if upper.endswith("PIN") or "PINCODE" in upper or "POSTAL" in upper:
        return f"4000{index % 100:02d}"
    if "NAME" in upper:
        return _NAMES[(index - 1) % len(_NAMES)]
    if "CITY" in upper:
        return _CITIES[(index - 1) % len(_CITIES)]
    if "STATE" in upper:
        return _STATES[(index - 1) % len(_STATES)]
    if "ADDRESS" in upper:
        return f"Flat {index}, MG Road"
    if "GENDER" in upper:
        return "M" if index % 2 else "F"
    if "STATUS" in upper:
        return ["ACTIVE", "ACTIVE", "CLOSED", "DORMANT"][index % 4]
    if "CURRENCY" in upper:
        return "INR"
    if "DATE" in upper:
        return (date.today() - timedelta(days=index % 20)).isoformat()
    if "NATURE" in upper or "TYPE" in upper or "CATEGORY" in upper or "MODE" in upper:
        return _KINDS[(index - 1) % len(_KINDS)]
    if "BRANCH" in upper:
        return f"BR{index:04d}"
    if "CODE" in upper:
        return f"C{index:05d}"
    if "FLAG" in upper or upper.startswith("IS_") or upper.endswith("_YN"):
        return "Y" if index % 2 else "N"
    return f"{re.sub(r'[^A-Z0-9]', '', upper)[:8] or 'VAL'}{index:05d}"


def _table_list(client: Any, schema: str) -> List[str]:
    try:
        return sorted(item.table_id for item in client.list_tables(schema))
    except Exception:
        from app.core.catalog_admin import CatalogError

        raise CatalogError(f"Schema '{schema}' not found or unreachable.")


def _schema_from_prompt(prompt: str, client: Any) -> str:
    try:
        datasets = {item.dataset_id.lower(): item.dataset_id for item in client.list_datasets()}
    except Exception:
        datasets = {DEFAULT_SCHEMA.lower(): DEFAULT_SCHEMA}
    for token in re.findall(r"[A-Za-z0-9_]{3,}", prompt):
        if token.lower() in datasets:
            return datasets[token.lower()]
    return DEFAULT_SCHEMA if DEFAULT_SCHEMA.lower() in datasets else next(iter(datasets.values()), DEFAULT_SCHEMA)


def _target_tables(prompt: str, schema: str, client: Any) -> List[str]:
    available = _table_list(client, schema)
    if _ALL_TABLES.search(prompt):
        return available
    picked = [
        name for name in available
        if re.search(r"\b" + re.escape(name) + r"\b", prompt, re.IGNORECASE)
    ]
    return picked


def _relations(client: Any, schema: str, tables: List[str]) -> Dict[Tuple[str, str], Tuple[str, str]]:
    """FK column -> (parent table, parent column) for the tables being filled."""
    from app.core.catalog_admin import _constraint_specs

    relations: Dict[Tuple[str, str], Tuple[str, str]] = {}
    for table in tables:
        table_obj = client.get_table(f"{client.project}.{schema}.{table}")
        for spec in _constraint_specs(table_obj):
            if spec["kind"] != "fk":
                continue
            referenced_table = spec["referenced"].split(".")[-1]
            if referenced_table not in tables:
                continue
            ref_columns = spec["referenced_columns"] or spec["columns"]
            for column, ref_column in zip(spec["columns"], ref_columns):
                relations[(table, column)] = (referenced_table, ref_column)
    for (table, column), target in KNOWN_REFS.items():
        if table in tables and target[0] in tables:
            relations.setdefault((table, column), target)
    return relations


def _parents(table: str, relations: Dict[Tuple[str, str], Tuple[str, str]]) -> set:
    return {target[0] for (child, _), target in relations.items() if child == table}


def _insert_order(tables: List[str], relations: Dict[Tuple[str, str], Tuple[str, str]]) -> List[str]:
    pending = list(tables)
    ordered: List[str] = []
    while pending:
        ready = [table for table in pending if _parents(table, relations) <= set(ordered)]
        if not ready:
            ready = [pending[0]]
        ordered.extend(sorted(ready))
        pending = [table for table in pending if table not in ready]
    return ordered


def _table_rows(client: Any, schema: str, table: str, count: int,
                relations: Dict[Tuple[str, str], Tuple[str, str]],
                key_store: Dict[Tuple[str, str], List[Any]],
                offset: int = 0) -> List[Dict[str, Any]]:
    from app.core.catalog_admin import _table_state

    state = _table_state(client, schema, table)
    columns = state["columns"]
    primary = set(state.get("primary_key") or [])
    fk_columns = {column for (child, column) in relations if child == table}
    key_columns = primary or {
        column["name"] for column in columns
        if column["name"].upper().endswith("_ID") and column["name"] not in fk_columns
    }

    rows: List[Dict[str, Any]] = []
    keys: Dict[str, List[Any]] = {column: [] for column in key_columns}
    for index in range(offset + 1, offset + count + 1):
        row: Dict[str, Any] = {}
        for column in columns:
            name = column["name"]
            type_sql = column["type"]
            if name in fk_columns:
                parent_table, parent_column = relations[(table, name)]
                parent_values = key_store.get((parent_table, parent_column)) or []
                if parent_values:
                    row[name] = parent_values[(index - 1) % len(parent_values)]
                else:
                    row[name] = _key_value(parent_column, index)
            elif name in key_columns:
                row[name] = _key_value(name, index)
                keys[name].append(row[name])
            else:
                row[name] = _scalar(name, type_sql, index)
        rows.append(row)
    for column, values in keys.items():
        key_store[(table, column)] = values
    # Children copy the parent's real values, whichever column they live in
    # (ACID, CUST_ID, ...), so a later JOIN on that column actually matches.
    for (child, _), (parent_table, parent_column) in relations.items():
        if child == table or parent_table != table:
            continue
        if parent_column in rows[0]:
            key_store[(table, parent_column)] = [row[parent_column] for row in rows]
    return rows


def _json_value(value: Any, type_sql: str) -> Any:
    base = _base_type(type_sql)
    if isinstance(value, Decimal):
        # The load-job encoder in this client version has no Decimal branch.
        return float(value)
    if base == "GEOGRAPHY" and isinstance(value, (tuple, list)):
        return f"POINT({value[0]} {value[1]})"
    if base == "BYTES" and isinstance(value, str):
        import base64

        return base64.b64encode(value.encode()).decode()
    return value


def _insert(client: Any, schema: str, table: str, rows: List[Dict[str, Any]],
            column_types: Dict[str, str]) -> None:
    from google.cloud import bigquery

    payload = [
        {name: _json_value(value, column_types[name]) for name, value in row.items()}
        for row in rows
    ]
    # The sandbox project rejects INSERT/UPDATE/DELETE (billing not enabled),
    # so rows go in through a load job instead of DML.
    job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
    job = client.load_table_from_json(
        payload, f"{client.project}.{schema}.{table}", job_config=job_config
    )
    try:
        job.result(timeout=600)
    except Exception as exc:
        detail = "; ".join(
            str(item.get("message") or item) for item in (job.errors or [])[:2]
        )
        head = str(payload[0])[:400] if payload else "empty"
        raise RuntimeError(
            f"{table}: {exc}{(' | ' + detail) if detail else ''} | first row: {head}"
        ) from None
    if job.errors:
        detail = "; ".join(str(item.get("message") or item) for item in job.errors[:2])
        raise RuntimeError(f"{table}: load reported errors: {detail}")
    if (job.output_rows or 0) != len(payload):
        raise RuntimeError(
            f"{table}: load accepted {job.output_rows or 0} of {len(payload)} rows; "
            f"first row was {str(payload[0])[:300] if payload else 'empty'}"
        )


def _column_types(client: Any, schema: str, table: str) -> Dict[str, str]:
    from app.core.catalog_admin import _table_state

    return {
        column["name"]: column["type"]
        for column in _table_state(client, schema, table)["columns"]
    }


def _count_rows(client: Any, schema: str, table: str) -> int:
    job = client.query(f"SELECT COUNT(*) AS c FROM `{client.project}.{schema}.{table}`")
    for row in job.result(timeout=120):
        return int(row["c"])
    return 0


def _payload(action: str, markdown: str, summary: str, detail: Dict[str, Any],
             started: float) -> Dict[str, Any]:
    duration_ms = round((time.time() - started) * 1000)
    return {
        "status": "success",
        "response": markdown,
        "summary": summary,
        "message": "",
        "action": action,
        "data": detail,
        "model_routed": "nanopro/bigquery-data",
        "model_executed": "google-cloud/bigquery-data",
        "model_name": "NanoPro BigQuery Data Agent",
        "lab_name": "NanoPro Data Plane",
        "country": "India",
        "flag": "🗃️",
        "date_formatted": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
        "duration_ms": duration_ms,
        "routing_decision": {
            "selected_model": "nanopro/bigquery-data",
            "task_domain": "BigQuery data loading and SQL execution",
            "sla_target_ms": 5000,
            "sla_met": duration_ms <= 5000,
        },
    }


def _error(message: str, started: float) -> Dict[str, Any]:
    duration_ms = round((time.time() - started) * 1000)
    return {
        "status": "error",
        "response": f"❌ {message}\n\n**काहीही बदलले नाही.**",
        "summary": message,
        "message": message,
        "model_routed": "nanopro/bigquery-data",
        "model_executed": "google-cloud/bigquery-data",
        "model_name": "NanoPro BigQuery Data Agent",
        "lab_name": "NanoPro Data Plane",
        "country": "India",
        "flag": "🗃️",
        "date_formatted": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
        "duration_ms": duration_ms,
        "routing_decision": {"selected_model": "nanopro/bigquery-data"},
    }


def _insert_samples(prompt: str) -> Dict[str, Any]:
    from app.core.catalog_admin import CatalogError

    started = time.time()
    client, _ = _client()
    schema = _schema_from_prompt(prompt, client)
    tables = _target_tables(prompt, schema, client)
    if not tables:
        return _error(
            f"`{schema}` मध्ये उल्लेख केलेले table सापडले नाही. उदा. \"nanopro_cbs_bronze मधील सगळ्या tables मध्ये 50 sample records टाका\"",
            started,
        )
    count_match = _COUNT.search(prompt)
    count = max(1, min(int(count_match.group(1)) if count_match else 50, 500))

    try:
        relations = _relations(client, schema, tables)
        ordered = _insert_order(tables, relations)
        key_store: Dict[Tuple[str, str], List[Any]] = {}
        inserted: List[Tuple[str, int]] = []
        for table in ordered:
            offset = _count_rows(client, schema, table)
            rows = _table_rows(client, schema, table, count, relations, key_store, offset)
            _insert(client, schema, table, rows, _column_types(client, schema, table))
            inserted.append((table, len(rows)))
        totals = {table: _count_rows(client, schema, table) for table in ordered}
    except CatalogError as exc:
        return _error(str(exc), started)
    except Exception as exc:
        return _error(f"Insert failed: {type(exc).__name__}: {str(exc)[:400]}", started)

    lines = [
        f"### ✅ {count} sample rows inserted into `{schema}`",
        "",
        "| Table | Inserted | Total rows |",
        "| --- | --- | --- |",
    ]
    lines.extend(f"| `{table}` | {rows} | {totals.get(table, 0)} |" for table, rows in inserted)
    if relations:
        lines.extend([
            "",
            "**Foreign keys**",
            "",
            "Rows are inserted parents-first, so every FK column points at a real parent key.",
        ])
    lines.extend(["", "_Explorer counts reload live — refresh गरज नाही._"])
    return _payload(
        "insert_samples",
        "\n".join(lines),
        f"{count} sample rows inserted into {len(inserted)} tables of {schema}",
        {"schema": schema, "count": count, "tables": dict(inserted), "totals": totals},
        started,
    )


def _render_rows(columns: List[str], rows: List[Dict[str, Any]], truncated: bool) -> str:
    if not columns:
        return "_Query returned no columns._"
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows:
        cells = []
        for name in columns:
            value = row.get(name)
            text = "NULL" if value is None else str(value)
            cells.append(text.replace("|", "\\|"))
        body.append("| " + " | ".join(cells) + " |")
    lines = [header, divider] + body
    if truncated:
        lines.append(f"\n_Showing first {len(rows)} rows._")
    return "\n".join(lines)


def _run_statement(sql: str, limit: int = 15) -> Dict[str, Any]:
    from app.core.catalog_admin import CatalogError

    client, _ = _client()
    statement = sql.strip().rstrip(";")
    if not statement:
        raise CatalogError("Empty SQL statement.")
    if ";" in statement:
        raise CatalogError("One statement at a time, कृपया.")
    head = statement.split(None, 1)[0].upper()
    if head in ("UPDATE", "DELETE", "INSERT"):
        if DEFAULT_SCHEMA.lower() not in statement.lower():
            raise CatalogError("Data changes are allowed only inside nanopro_cbs_bronze.")
        if head in ("UPDATE", "DELETE") and not re.search(r"\bwhere\b", statement, re.IGNORECASE):
            raise CatalogError("UPDATE/DELETE requires a WHERE clause.")
    elif head not in ("SELECT", "WITH"):
        raise CatalogError(f"`{head}` is not supported in chat. Supported: SELECT, WITH, INSERT, UPDATE, DELETE.")

    started = time.time()
    job = client.query(statement)
    if head in ("SELECT", "WITH"):
        result = job.result(max_results=limit + 1)
        columns = [field.name for field in result.schema]
        rows = []
        for row in result:
            rows.append({key: value for key, value in dict(row.items()).items()})
            if len(rows) > limit:
                break
        return {
            "kind": "rows",
            "columns": columns,
            "rows": rows[:limit],
            "row_count": len(rows[:limit]),
            "truncated": len(rows) > limit,
            "duration_ms": round((time.time() - started) * 1000),
            "statement": statement,
        }
    job.result(timeout=600)
    return {
        "kind": "dml",
        "statement_type": job.statement_type,
        "affected": job.num_dml_affected_rows,
        "duration_ms": round((time.time() - started) * 1000),
        "statement": statement,
    }


def _handle_sql(sql: str) -> Dict[str, Any]:
    from app.core.catalog_admin import CatalogError

    started = time.time()
    try:
        result = _run_statement(sql)
    except CatalogError as exc:
        return _error(str(exc), started)
    except Exception as exc:
        text = str(exc)
        if "Billing has not been enabled" in text or "billingNotEnabled" in text:
            return _error(
                "हा BigQuery project sandbox आहे: Google ने INSERT/UPDATE/DELETE बंद ठेवले आहेत. "
                "SELECT विचारता येतात, आणि sample rows load job ने टाकली जातात.",
                started,
            )
        return _error(f"BigQuery error: {text[:400]}", started)

    if result["kind"] == "rows":
        markdown = "\n".join([
            "### 📄 Query result",
            "",
            _render_rows(result["columns"], result["rows"], result["truncated"]),
            "",
            f"_Completed in {result['duration_ms']} ms._",
        ])
        return _payload(
            "run_query",
            markdown,
            f"Query returned {result['row_count']} rows",
            result,
            started,
        )
    markdown = "\n".join([
        f"### ✅ {result['statement_type']} executed",
        "",
        f"| Field | Value |",
        f"| --- | --- |",
        f"| Statement | `{result['statement_type']}` |",
        f"| Rows affected | {result['affected'] if result['affected'] is not None else '—'} |",
        f"| Duration | {result['duration_ms']} ms |",
    ])
    return _payload(
        "mutate_rows",
        markdown,
        f"{result['statement_type']} affected {result['affected']} rows",
        result,
        started,
    )


def maybe_handle(prompt: str) -> Optional[Dict[str, Any]]:
    text = (prompt or "").strip()
    if not text:
        return None

    block = _SQL_FENCE.search(text)
    if block:
        if _SCHEMA_CHANGE.match(block.group(1)):
            return None
        return _handle_sql(block.group(1))

    lowered = text.lower()
    if lowered.startswith("execute bigquery query:"):
        statement = text.split(":", 1)[1]
        if _SCHEMA_CHANGE.match(statement):
            return None
        return _handle_sql(statement)

    if _INSERT_VERB.search(text) and _SAMPLE_WORD.search(text):
        return _insert_samples(text)

    if re.match(r"^(select|with)\b", lowered) and (
        "bigquery" in lowered or DEFAULT_SCHEMA in lowered or "```" in text
    ):
        return _handle_sql(text)

    return None
