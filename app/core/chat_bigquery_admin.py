"""Natural-language Explorer admin for the AI Lab chat.

Turns phrases like "VCT table rename करून VCT_TEST करा" into the same
app.core.catalog_admin operations the Explorer right-click menus call.
Detection is deliberately strict: an admin verb plus at least one name that
exists in the live catalog. Anything else returns None so normal chat
answering continues untouched.
"""

import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

_IDENT_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_TYPE_TOKEN = re.compile(
    r"\b(STRING|BYTES|INT64|INTEGER|BIGINT|SMALLINT|INT|FLOAT64|FLOAT|REAL|DOUBLE|"
    r"NUMERIC|BIGNUMERIC|DECIMAL|NUMBER|BOOL|BOOLEAN|DATE|DATETIME|TIME|TIMESTAMP|"
    r"JSON|GEOGRAPHY|VARCHAR2?|CHAR|TEXT)\s*(?:\(\s*([0-9]+)\s*(?:,\s*([0-9]+)\s*)?\))?",
    re.IGNORECASE,
)
_TYPE_ALIASES = {
    "VARCHAR": "STRING",
    "VARCHAR2": "STRING",
    "CHAR": "STRING",
    "TEXT": "STRING",
    "INT": "INT64",
    "BIGINT": "INT64",
    "SMALLINT": "INT64",
    "REAL": "FLOAT64",
    "DOUBLE": "FLOAT64",
    "DECIMAL": "NUMERIC",
    "NUMBER": "NUMERIC",
}
_DATE_TYPES = {"DATE", "DATETIME", "TIMESTAMP"}

_FORMAT_ALIASES = (
    ("DD-MM-YYYY HH:MM:SS", "%d-%m-%Y %H:%M:%S"),
    ("YYYY-MM-DD", "%Y-%m-%d"),
    ("DD-MM-YYYY", "%d-%m-%Y"),
    ("DD/MM/YYYY", "%d/%m/%Y"),
    ("YYYY/MM/DD", "%Y/%m/%d"),
    ("DD-MON-YYYY", "%d-%b-%Y"),
    ("MM/DD/YYYY", "%m/%d/%Y"),
)
_FORMAT_TOKENS = {"yyyy", "yy", "mm", "dd", "hh", "ss", "mon", "format"}

_DELETE = re.compile(r"\bdelete\b|\bdrop\b|\bremove\b|डिलीट|काढून|काढा|हटव", re.IGNORECASE)
_RENAME = re.compile(
    r"\brename\b|change\s+(?:the\s+)?(?:table|column|schema|dataset\s+)?name"
    r"|नाव\s*बदल|पुनर्नाम|बदला|नाव\s+[A-Za-z_]",
    re.IGNORECASE,
)
_ADD_COLUMN = re.compile(
    r"\badd\b[^.\n]{0,40}\bcolumn\b|\bcolumn\b[^.\n]{0,40}\badd\b"
    r"|column\s*जोड|कॉलम\s*जोड|नवीन\s+column|नवा\s+column",
    re.IGNORECASE,
)
_TYPE_CHANGE = re.compile(
    r"data\s*-?\s*type|\btype\b|प्रकार|डेटा\s*प्रकार", re.IGNORECASE
)
_COUNT = re.compile(r"\bcount\b|\bhow\s+many\b|किती|माहिती|\bstats?\b", re.IGNORECASE)
_CHANGE_VERB = re.compile(
    r"\bchange\b|\balter\b|\bmodify\b|बदल|बदला|करून\s*टाक|सेट\s*कर", re.IGNORECASE
)
_SCHEMA_WORD = re.compile(r"\bschema\b|\bdataset\b|स्कीमा|डेटासेट", re.IGNORECASE)
_DML_WORD = re.compile(
    r"\brows?\b|\brecords?\b|\bwhere\b|\bdata\b|\bduplicates?\b|ओळी|रेकॉर्ड", re.IGNORECASE
)
_COLUMN_WORD = re.compile(r"\bcolumn\b|कॉलम", re.IGNORECASE)
_NEGATION = re.compile(r"\b(don'?t|do\s+not|never)\b|नको|नका|करू\s+नका|न\s+करा", re.IGNORECASE)
_REVERT = re.compile(
    r"(?:परत|back\s+to|then\s+rename(?:\s+it)?\s+(?:to|back\s+to))\s+([A-Za-z_][A-Za-z0-9_]*)",
    re.IGNORECASE,
)

_STOPWORDS = {
    "table", "tables", "column", "columns", "schema", "schemas", "dataset",
    "datasets", "bigquery", "bq", "type", "data", "datatype", "format", "name",
    "rename", "delete", "drop", "remove", "add", "change", "alter", "modify",
    "update", "create", "to", "as", "into", "from", "in", "on", "of", "the",
    "and", "or", "with", "without", "new", "old", "count", "counts", "rows",
    "row", "how", "many", "please", "all", "live", "now", "then", "back",
    "karo", "kara", "karun", "kar", "karta", "madhe", "chya", "cha", "chi",
    "la", "te", "tar", "pan", "he", "ha", "hi", "aahe", "ahet", "nav",
    "badal", "badla", "joda", "jod", "kadha", "kadhun", "tak", "parat",
    "pudhe", "var", "varun", "madhi", "madhiL", "kiva", "ani", "ek", "zala",
}
_STOPWORDS.update(_FORMAT_TOKENS)
_TYPE_WORDS = set(_TYPE_ALIASES) | {
    "string", "bytes", "int64", "integer", "bigint", "smallint", "int",
    "float64", "float", "real", "double", "numeric", "bignumeric", "decimal",
    "number", "bool", "boolean", "date", "datetime", "time", "timestamp",
    "json", "geography", "char", "text", "varchar",
}

_INDEX: Dict[str, Any] = {"at": 0.0, "schemas": {}, "tables": {}}
_INDEX_TTL = 20.0


class _Nothing(Exception):
    """Signals that the prompt is not an admin instruction after all."""


def _catalog_index(force: bool = False) -> Tuple[Dict[str, str], Dict[str, Tuple[str, str]]]:
    now = time.time()
    if not force and _INDEX["tables"] and now - _INDEX["at"] < _INDEX_TTL:
        return _INDEX["schemas"], _INDEX["tables"]
    from app.core.catalog_admin import _client

    client, _ = _client()
    schemas: Dict[str, str] = {}
    tables: Dict[str, Tuple[str, str]] = {}
    for dataset in client.list_datasets():
        dataset_id = dataset.dataset_id
        schemas[dataset_id.lower()] = dataset_id
        try:
            for item in client.list_tables(dataset_id):
                tables[item.table_id.lower()] = (dataset_id, item.table_id)
        except Exception:
            continue
    _INDEX.update({"at": now, "schemas": schemas, "tables": tables})
    return schemas, tables


def invalidate_index() -> None:
    _INDEX["at"] = 0.0


def _tokens(text: str) -> List[Tuple[str, int]]:
    return [(match.group(0), match.start()) for match in _IDENT_TOKEN.finditer(text)]


def _existing(text: str) -> List[Tuple[str, str, str, str, int]]:
    schemas, tables = _catalog_index()
    found: List[Tuple[str, str, str, str, int]] = []
    for token, pos in _tokens(text):
        low = token.lower()
        if low in tables:
            schema, table = tables[low]
            found.append(("table", schema, table, token, pos))
        elif low in schemas:
            name = schemas[low]
            found.append(("schema", name, name, token, pos))
    return found


def _candidate_after(text: str, pos: int, exclude: set) -> str:
    for token, start in _tokens(text):
        if start <= pos:
            continue
        low = token.lower()
        if low in _STOPWORDS or low in _TYPE_WORDS or low in exclude:
            continue
        return token
    return ""


def _candidate_before(text: str, pos: int) -> str:
    previous = ""
    for token, start in _tokens(text):
        if start >= pos:
            break
        previous = token
    if previous.lower() in _STOPWORDS or previous.lower() in _TYPE_WORDS:
        return ""
    return previous


def _strip_name(text: str, names: List[str]) -> str:
    for name in sorted(set(names), key=len, reverse=True):
        if not name:
            continue
        text = re.sub(r"\b" + re.escape(name) + r"\b", " ", text, flags=re.IGNORECASE)
    return text


def _type_spec(match: "re.Match") -> Dict[str, Any]:
    raw = match.group(1).upper()
    base = _TYPE_ALIASES.get(raw, raw)
    length = match.group(2)
    scale = match.group(3)
    spec: Dict[str, Any] = {"type": base, "length": None, "precision": None, "scale": None}
    if raw in ("VARCHAR", "VARCHAR2", "CHAR", "TEXT"):
        base = "STRING"
    if base in ("STRING", "BYTES") and length:
        spec["length"] = int(length)
    if base in ("NUMERIC", "BIGNUMERIC") and length:
        spec["precision"] = int(length)
        spec["scale"] = int(scale) if scale is not None else None
    return spec


def _date_format(text: str) -> str:
    upper = text.upper()
    for alias, bq_format in _FORMAT_ALIASES:
        if re.search(re.escape(alias).replace(r"\ ", r"\s*"), upper):
            return bq_format
    direct = re.search(
        r"%[YymdMDHMSb]{1,4}(?:[-/ :.,]%[YymdMDHMSb]{1,4})+(?:\s+%[HMS]{1,2}(?::%[MS]{1,2})*)?",
        text,
    )
    return direct.group(0).strip() if direct else ""


def _table_columns(schema: str, table: str) -> List[str]:
    from app.core.catalog_admin import _client

    client, _ = _client()
    table_obj = client.get_table(f"{client.project}.{schema}.{table}")
    return [field.name for field in table_obj.schema]


def _report(title: str, rows: List[Tuple[str, str]], notes: Optional[List[str]] = None) -> str:
    lines = [f"### {title}", "", "| Field | Value |", "| --- | --- |"]
    lines.extend(f"| {label} | {value} |" for label, value in rows)
    if notes:
        lines.extend(["", "**Notes**", ""] + [f"- {note}" for note in notes])
    lines.extend(["", "_Explorer tree updated live — refresh गरज नाही._"])
    return "\n".join(lines)


def _payload(action: str, markdown: str, summary: str, detail: Dict[str, Any], started: float) -> Dict[str, Any]:
    duration_ms = round((time.time() - started) * 1000)
    return {
        "status": "success",
        "response": markdown,
        "summary": summary,
        "message": "",
        "action": action,
        "catalog": detail,
        "model_routed": "nanopro/explorer-admin",
        "model_executed": "google-cloud/bigquery-admin",
        "model_name": "NanoPro Explorer Admin",
        "lab_name": "NanoPro Data Plane",
        "country": "India",
        "flag": "🛠️",
        "date_formatted": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
        "duration_ms": duration_ms,
        "routing_decision": {
            "selected_model": "nanopro/explorer-admin",
            "task_domain": "BigQuery schema management (rename / delete / type / add / counts)",
            "sla_target_ms": 3000,
            "sla_met": duration_ms <= 3000,
        },
    }


def _error(message: str, started: float) -> Dict[str, Any]:
    duration_ms = round((time.time() - started) * 1000)
    return {
        "status": "error",
        "response": f"❌ {message}\n\n**काहीही बदलले नाही.**",
        "summary": message,
        "message": message,
        "model_routed": "nanopro/explorer-admin",
        "model_executed": "google-cloud/bigquery-admin",
        "model_name": "NanoPro Explorer Admin",
        "lab_name": "NanoPro Data Plane",
        "country": "India",
        "flag": "🛠️",
        "date_formatted": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
        "duration_ms": duration_ms,
        "routing_decision": {"selected_model": "nanopro/explorer-admin"},
    }


def _pick_table(text: str, found: List[Tuple[str, str, str, str, int]]) -> Tuple[str, str, str, int]:
    for kind, schema, name, raw, pos in found:
        if kind == "table":
            return schema, name, raw, pos
    raise _Nothing()


def _pick_schema(text: str, found: List[Tuple[str, str, str, str, int]]) -> Tuple[str, str, int]:
    for kind, schema, name, raw, pos in found:
        if kind == "schema":
            return schema, raw, pos
    raise _Nothing()


def _handle_rename(text: str, found: List[Tuple[str, str, str, str, int]]) -> Dict[str, Any]:
    from app.core import catalog_admin as admin

    started = time.time()

    def rename_schema_op(schema: str, raw: str, pos: int) -> Dict[str, Any]:
        new_name = _candidate_after(text, pos, {raw.lower(), schema.lower()})
        if not new_name:
            raise _Nothing()
        result = admin.rename_schema(schema, new_name)
        invalidate_index()
        rows = [
            ("Previous schema", f"`{schema}`"),
            ("New schema", f"`{result['schema']}`"),
            ("Tables copied", str(len(result.get("copied_tables") or []))),
            ("Location", result.get("location") or "—"),
        ]
        notes = ["BigQuery dataset rename नसतो, म्हणून सर्व tables नवीन dataset मध्ये copy होऊन जुना dataset drop झाला."]
        markdown = _report(f"✅ Schema renamed — `{schema}` → `{result['schema']}`", rows, notes)
        summary = f"Schema {schema} → {result['schema']} ({len(result.get('copied_tables') or [])} tables)"
        return _payload("rename_schema", markdown, summary, result, started)

    if _SCHEMA_WORD.search(text):
        return rename_schema_op(*_pick_schema(text, found))
    if not any(item[0] == "table" for item in found):
        return rename_schema_op(*_pick_schema(text, found))

    schema, table, raw, pos = _pick_table(text, found)
    exclude = {raw.lower(), table.lower(), schema.lower()}
    new_name = _candidate_after(text, pos, exclude)
    if not new_name:
        return _error("नवीन table name सापडले नाही. उदा. \"VCT table rename करून VCT_TEST करा\"", started)
    result = admin.rename_table(schema, table, new_name)
    invalidate_index()

    reverted = None
    revert = _REVERT.search(text)
    if revert and revert.group(1).lower() == table.lower() and new_name != table:
        reverted = admin.rename_table(schema, new_name, table)
        invalidate_index()

    rows = [
        ("Schema", f"`{schema}`"),
        ("Previous name", f"`{table}`"),
        ("New name", f"`{result['table']}`"),
        ("Columns", str(result.get("columns_count", "—"))),
        ("Rows", str(result.get("rows", 0))),
        ("Method", "recreate (constraints re-applied)" if result.get("applied") == "recreate" else "native RENAME"),
    ]
    notes = list(result.get("notes") or [])
    if reverted:
        rows.append(("Reverted", f"`{result['table']}` → `{table}` (परत rename केले)"))
        notes.append("मागितल्याप्रमाणे table परत मूळ नावावर rename झाले.")
    markdown = _report(f"✅ Table renamed — `{schema}.{table}` → `{result['table']}`", rows, notes)
    summary = f"Table {table} → {result['table']}" + (f", then back to {table}" if reverted else "")
    return _payload("rename_table", markdown, summary, {"first": result, "reverted": reverted}, started)


def _handle_delete(text: str, found: List[Tuple[str, str, str, str, int]]) -> Dict[str, Any]:
    from app.core import catalog_admin as admin

    started = time.time()
    if _SCHEMA_WORD.search(text):
        try:
            schema, raw, _pos = _pick_schema(text, found)
        except _Nothing:
            raise _Nothing()
        result = admin.drop_schema(schema, schema)
        invalidate_index()
        dropped = result.get("dropped_tables") or []
        rows = [
            ("Schema", f"`{schema}`"),
            ("Tables dropped", str(len(dropped))),
            ("Status", "deleted"),
        ]
        notes = ["सर्व tables सह dataset पूर्णपणे delete झाला."] if dropped else []
        markdown = _report(f"🗑️ Schema deleted — `{schema}`", rows, notes)
        return _payload(
            "drop_schema",
            markdown,
            f"Schema {schema} deleted ({len(dropped)} tables)",
            result,
            started,
        )

    schema, table, raw, pos = _pick_table(text, found)
    result = admin.drop_table(schema, table, table)
    invalidate_index()
    rows = [
        ("Schema", f"`{schema}`"),
        ("Table", f"`{table}`"),
        ("Status", "deleted"),
    ]
    markdown = _report(f"🗑️ Table deleted — `{schema}.{table}`", rows)
    return _payload("drop_table", markdown, f"Table {table} deleted", result, started)


def _handle_add_column(text: str, found: List[Tuple[str, str, str, str, int]]) -> Dict[str, Any]:
    from app.core import catalog_admin as admin

    started = time.time()
    schema, table, raw, pos = _pick_table(text, found)
    stripped = _strip_name(text, [raw, table])
    type_match = _TYPE_TOKEN.search(stripped)
    if not type_match:
        return _error("Data type सापडला नाही. उदा. \"VCT मध्ये TEST_NOTE STRING(50) column add करा\"", started)
    spec = _type_spec(type_match)
    column = _candidate_before(stripped, type_match.start())
    if not column:
        for token, start in _tokens(stripped[type_match.end():]):
            if token.lower() not in _STOPWORDS and token.lower() not in _TYPE_WORDS:
                column = token
                break
    if not column:
        return _error("नवीन column चे नाव सापडले नाही.", started)
    result = admin.add_column(
        schema,
        table,
        column,
        spec["type"],
        length=spec["length"],
        precision=spec["precision"],
        scale=spec["scale"],
    )
    invalidate_index()
    rows = [
        ("Schema", f"`{schema}`"),
        ("Table", f"`{table}`"),
        ("Column", f"`{result['column']}`"),
        ("Type", f"`{result['type']}`"),
        ("Total columns", str(result.get("columns_count", "—"))),
        ("Rows", str(result.get("rows", 0))),
    ]
    markdown = _report(f"✅ Column added — `{schema}.{table}.{result['column']}`", rows)
    return _payload(
        "add_column",
        markdown,
        f"Column {result['column']} {result['type']} added to {table}",
        result,
        started,
    )


def _handle_type_change(text: str, found: List[Tuple[str, str, str, str, int]]) -> Dict[str, Any]:
    from app.core import catalog_admin as admin

    started = time.time()
    schema, table, raw, pos = _pick_table(text, found)
    matches = list(_TYPE_TOKEN.finditer(text))
    if not matches:
        raise _Nothing()
    spec = _type_spec(matches[-1])
    columns = _table_columns(schema, table)
    by_lower = {name.lower(): name for name in columns}
    source_names = {raw.lower(), table.lower(), schema.lower()}
    column = ""
    for token, start in _tokens(text):
        low = token.lower()
        if low in source_names or low in _STOPWORDS or low in _TYPE_WORDS:
            continue
        if low in by_lower:
            column = by_lower[low]
            break
    if not column:
        fallback = _candidate_after(text, pos, source_names | set(_TYPE_WORDS))
        if fallback:
            return _error(
                f"Column `{fallback}` `{schema}.{table}` मध्ये सापडला नाही. उपलब्ध columns: "
                + ", ".join(f"`{name}`" for name in columns[:12])
                + (" …" if len(columns) > 12 else ""),
                started,
            )
        return _error("कोणता column बदलायचा ते सांगा.", started)

    date_format = _date_format(text)
    notes: List[str] = []
    current = next((field for field in _current_fields(schema, table) if field["name"] == column), None)
    current_type = (current or {}).get("type", "").split("(", 1)[0].upper()
    if not date_format and (
        (spec["type"] in _DATE_TYPES and current_type == "STRING")
        or (current_type in _DATE_TYPES and spec["type"] == "STRING")
    ):
        date_format = "%Y-%m-%d"
        notes.append("Format सांगितला नव्हता, म्हणून default `%Y-%m-%d` वापरला.")

    result = admin.alter_column(
        schema,
        table,
        column,
        spec["type"],
        length=spec["length"],
        precision=spec["precision"],
        scale=spec["scale"],
        date_format=date_format,
    )
    invalidate_index()
    rows = [
        ("Schema", f"`{schema}`"),
        ("Table", f"`{table}`"),
        ("Column", f"`{result['column']}`"),
        ("Previous type", f"`{result.get('previous_type')}`"),
        ("New type", f"`{result['type']}`"),
        ("Date format", f"`{date_format}`" if date_format else "—"),
        ("Method", result.get("applied") or "alter"),
        ("Rows", str(result.get("rows", 0))),
    ]
    notes.extend(result.get("notes") or [])
    markdown = _report(f"✅ Column type changed — `{schema}.{table}.{column}`", rows, notes)
    return _payload(
        "alter_column",
        markdown,
        f"{table}.{column}: {result.get('previous_type')} → {result['type']}",
        result,
        started,
    )


def _handle_column_rename(text: str, found: List[Tuple[str, str, str, str, int]]) -> Dict[str, Any]:
    from app.core import catalog_admin as admin

    started = time.time()
    schema, table, raw, pos = _pick_table(text, found)
    columns = _table_columns(schema, table)
    by_lower = {name.lower(): name for name in columns}
    source_names = {raw.lower(), table.lower(), schema.lower()}
    column = ""
    column_pos = -1
    for token, start in _tokens(text):
        low = token.lower()
        if low in source_names or low in _STOPWORDS or low in _TYPE_WORDS:
            continue
        if low in by_lower:
            column = by_lower[low]
            column_pos = start
            break
    if not column:
        return _error(
            "Rename करायचा column सापडला नाही. उदा. \"VCT मधील LOG_TIME चे नाव EVENT_TS करा\"",
            started,
        )
    new_name = _candidate_after(text, column_pos, source_names | {column.lower()})
    if not new_name:
        return _error("Column चे नवीन नाव सापडले नाही.", started)
    result = admin.rename_column(schema, table, column, new_name)
    invalidate_index()
    rows = [
        ("Schema", f"`{schema}`"),
        ("Table", f"`{table}`"),
        ("Previous column", f"`{column}`"),
        ("New column", f"`{new_name}`"),
        ("Total columns", str(result.get("columns_count", "—"))),
    ]
    markdown = _report(f"✅ Column renamed — `{schema}.{table}.{column}` → `{new_name}`", rows)
    return _payload(
        "rename_column",
        markdown,
        f"{table}.{column} → {new_name}",
        result,
        started,
    )


def _current_fields(schema: str, table: str) -> List[Dict[str, Any]]:
    from app.core import catalog_admin as admin

    return admin._table_state(admin._client()[0], schema, table)["columns"]


def _handle_info(text: str, found: List[Tuple[str, str, str, str, int]]) -> Dict[str, Any]:
    from app.core import catalog_admin as admin

    started = time.time()
    if _SCHEMA_WORD.search(text):
        try:
            schema, raw, _pos = _pick_schema(text, found)
        except _Nothing:
            raise _Nothing()
        info = admin.schema_info(schema)
        rows = [
            ("Schema", f"`{schema}`"),
            ("Location", info.get("location") or "—"),
            ("Tables", str(info.get("tables", 0))),
            ("Rows (total)", str(info.get("rows", 0))),
        ]
        markdown = _report(f"📊 Schema counts — `{schema}`", rows)
        return _payload(
            "schema_info",
            markdown,
            f"{schema}: {info.get('tables', 0)} tables · {info.get('rows', 0)} rows",
            info,
            started,
        )

    schema, table, raw, pos = _pick_table(text, found)
    state = admin._table_state(admin._client()[0], schema, table)
    rows = [
        ("Schema", f"`{schema}`"),
        ("Table", f"`{table}`"),
        ("Columns", str(state.get("columns_count", len(state.get("columns") or [])))),
        ("Rows", str(state.get("rows", 0))),
        ("Primary key", ", ".join(state.get("primary_key") or []) or "—"),
    ]
    markdown = _report(f"📊 Table counts — `{schema}.{table}`", rows)
    return _payload(
        "table_info",
        markdown,
        f"{table}: {state.get('columns_count', 0)} columns · {state.get('rows', 0)} rows",
        state,
        started,
    )


def _column_mentioned(text: str, found: List[Tuple[str, str, str, str, int]]) -> bool:
    try:
        schema, table, raw, _pos = _pick_table(text, found)
        columns = {name.lower() for name in _table_columns(schema, table)}
    except Exception:
        return False
    skip = {raw.lower(), table.lower(), schema.lower()} | _STOPWORDS | _TYPE_WORDS
    for token, _start in _tokens(text):
        low = token.lower()
        if low in skip:
            continue
        if low in columns:
            return True
    return False


def maybe_handle(prompt: str) -> Optional[Dict[str, Any]]:
    text = (prompt or "").strip()
    if not text:
        return None

    type_matches = list(_TYPE_TOKEN.finditer(text))
    is_delete = bool(_DELETE.search(text))
    is_rename = bool(_RENAME.search(text))
    is_add = bool(_ADD_COLUMN.search(text)) or (
        bool(re.search(r"जोडा", text)) and bool(type_matches)
    )
    is_type = bool(type_matches) and (bool(_TYPE_CHANGE.search(text)) or len(type_matches) >= 2)
    is_count = bool(_COUNT.search(text))

    # A CREATE spec pasted into chat carries many type tokens; it belongs to the
    # DDL path, never to these in-place admin operations.
    if re.search(r"\bcreate\b|\bbanav|बनव|तयार|```", text, re.IGNORECASE):
        return None

    if not any((is_delete, is_rename, is_add, is_type, is_count)):
        return None

    if _NEGATION.search(text) and (is_delete or is_rename):
        started = time.time()
        return _payload(
            "noop",
            "👍 समजले — कोणतीही rename/delete क्रिया केली नाही. काहीही बदलले नाही.",
            "No change (prompt says not to rename/delete)",
            {},
            started,
        )

    try:
        found = _existing(text)
    except Exception:
        return None
    if not found:
        return None

    # "delete rows / data ..." and "drop column" are DML or unsupported schema
    # edits; they must never be resolved into DROP TABLE / DROP SCHEMA.
    if is_delete and (_DML_WORD.search(text) or _COLUMN_WORD.search(text)):
        return None

    try:
        if is_delete:
            return _handle_delete(text, found)
        if is_add:
            return _handle_add_column(text, found)
        if is_count and not _CHANGE_VERB.search(text):
            return _handle_info(text, found)
        if is_rename and (
            re.search(r"\bcolumn\b|कॉलम", text, re.IGNORECASE)
            or _column_mentioned(text, found)
        ):
            return _handle_column_rename(text, found)
        if is_type:
            return _handle_type_change(text, found)
        if is_rename:
            return _handle_rename(text, found)
        if is_count:
            return _handle_info(text, found)
    except _Nothing:
        return None
    except Exception as exc:
        from app.core.catalog_admin import CatalogError

        if isinstance(exc, CatalogError):
            return _error(str(exc), time.time())
        return _error(f"{type(exc).__name__}: {str(exc)[:300]}", time.time())
    return None
