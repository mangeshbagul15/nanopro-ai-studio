"""Live schema/table/column mutations for the Explorer (BigQuery).

Every operation is applied to the real BigQuery API and read back afterwards,
so the Explorer tree can update from the returned state instead of guessing.
Destructive calls require the caller to repeat the object name.
"""

from __future__ import annotations

import re
import uuid
from typing import Any, Dict, List, Optional

DEFAULT_LOCATION = "asia-south1"

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,300}$")
_DATASET = re.compile(r"^[A-Za-z0-9_]{1,1024}$")
_DATE_FORMAT = re.compile(r"^[%A-Za-z0-9 _/:.,\-]{1,64}$")

_TYPES = {
    "STRING": "STRING",
    "BYTES": "BYTES",
    "INT64": "INT64",
    "INTEGER": "INT64",
    "FLOAT64": "FLOAT64",
    "FLOAT": "FLOAT64",
    "NUMERIC": "NUMERIC",
    "BIGNUMERIC": "BIGNUMERIC",
    "BOOL": "BOOL",
    "BOOLEAN": "BOOL",
    "DATE": "DATE",
    "DATETIME": "DATETIME",
    "TIME": "TIME",
    "TIMESTAMP": "TIMESTAMP",
    "JSON": "JSON",
    "GEOGRAPHY": "GEOGRAPHY",
}
_DATE_TYPES = {"DATE", "DATETIME", "TIMESTAMP"}
_PARSE_FN = {"DATE": "PARSE_DATE", "DATETIME": "PARSE_DATETIME", "TIMESTAMP": "PARSE_TIMESTAMP"}
_FORMAT_FN = {"DATE": "FORMAT_DATE", "DATETIME": "FORMAT_DATETIME", "TIMESTAMP": "FORMAT_TIMESTAMP"}


class CatalogError(ValueError):
    """Raised when an Explorer mutation is invalid or rejected by BigQuery."""


def _client():
    from app.core.live_catalog import _bigquery_client

    return _bigquery_client()


def _check_name(value: str, kind: str) -> str:
    name = (value or "").strip()
    if kind == "schema":
        if not _DATASET.match(name):
            raise CatalogError("Invalid schema name.")
    elif not _IDENT.match(name):
        raise CatalogError(f"Invalid {kind} name.")
    return name


def _type_sql(field: Any) -> str:
    base = field.field_type
    length = getattr(field, "max_length", None)
    if base in ("STRING", "BYTES") and length:
        return f"{base}({int(length)})"
    precision = getattr(field, "precision", None)
    scale = getattr(field, "scale", None)
    if base in ("NUMERIC", "BIGNUMERIC") and precision:
        if scale is not None:
            return f"{base}({int(precision)},{int(scale)})"
        return f"{base}({int(precision)})"
    return base


def _column_line(field: Any) -> str:
    line = f"`{field.name}` {_type_sql(field)}"
    if field.mode == "REQUIRED":
        line += " NOT NULL"
    return line


def _constraints(table: Any, dataset_override: str = "") -> List[str]:
    constraints = getattr(table, "table_constraints", None)
    if not constraints:
        constraints = (getattr(table, "_properties", None) or {}).get("tableConstraints")
    constraints = constraints or {}
    lines: List[str] = []
    primary = (constraints.get("primaryKey") or {}).get("columns") or []
    if primary:
        lines.append("PRIMARY KEY (" + ", ".join(primary) + ") NOT ENFORCED")
    for fk in constraints.get("foreignKeys") or []:
        columns = fk.get("columns") or []
        referenced = fk.get("referencedTable") or ""
        referenced_columns = fk.get("referencedColumns") or []
        if not columns or not referenced:
            continue
        target_dataset = table.dataset_id
        if "." in referenced:
            referenced_dataset, referenced_table = referenced.split(".", 1)[-2:]
            if dataset_override and referenced_dataset == table.dataset_id:
                referenced_dataset = dataset_override
            referenced = f"{referenced_dataset}.{referenced_table}"
        else:
            referenced = f"{dataset_override or table.dataset_id}.{referenced}"
        lines.append(
            "FOREIGN KEY (" + ", ".join(columns) + ")"
            f" REFERENCES `{referenced}` (" + ", ".join(referenced_columns) + ") NOT ENFORCED"
        )
    return lines


def _partition_clause(table: Any) -> str:
    partitioning = getattr(table, "time_partitioning", None)
    field = (partitioning.field if partitioning else "") or ""
    if not field:
        return ""
    granularity = (partitioning.type_ if partitioning else "") or "DAY"
    if granularity == "DAY":
        return f"PARTITION BY {field}"
    if granularity in ("HOUR", "MONTH", "YEAR"):
        return f"PARTITION BY DATE_TRUNC({field}, {granularity})"
    return ""


def _cluster_clause(table: Any) -> str:
    fields = list(getattr(table, "clustering_fields", None) or [])
    return f"CLUSTER BY {', '.join(fields)}" if fields else ""


def _create_sql(
    project: str,
    dataset_id: str,
    table_id: str,
    fields: List[Any],
    constraint_lines: List[str],
    table: Any,
) -> str:
    lines = [_column_line(field) for field in fields] + constraint_lines
    statement = (
        f"CREATE TABLE `{project}.{dataset_id}.{table_id}` (\n  "
        + ",\n  ".join(lines)
        + "\n)"
    )
    partition = _partition_clause(table)
    if partition:
        statement += "\n" + partition
    cluster = _cluster_clause(table)
    if cluster:
        statement += "\n" + cluster
    return statement


def _dataset_location(client: Any, schema: str) -> str:
    try:
        return client.get_dataset(schema).location or DEFAULT_LOCATION
    except Exception:
        return DEFAULT_LOCATION


def _run(client: Any, sql: str, location: str, timeout: float = 300.0) -> None:
    job = client.query(sql, location=location)
    job.result(timeout=timeout)


def _table_state(client: Any, schema: str, table: str) -> Dict[str, Any]:
    from app.core.bigquery_ddl import _describe_table

    described = _describe_table(client, f"{client.project}.{schema}.{table}")
    return {
        "schema": schema,
        "table": table,
        "columns_count": described.get("num_columns", 0),
        "rows": described.get("num_rows", 0),
        "columns": [
            {"name": column.get("name"), "type": column.get("type"), "mode": column.get("mode")}
            for column in described.get("columns") or []
        ],
        "primary_key": described.get("primary_key") or [],
    }


def rename_table(schema: str, table: str, new_name: str) -> Dict[str, Any]:
    client, auth_source = _client()
    schema = _check_name(schema, "schema")
    table = _check_name(table, "table")
    new_name = _check_name(new_name, "table")
    ref = f"{client.project}.{schema}.{table}"
    client.get_table(ref)
    if new_name == table:
        raise CatalogError("New name is identical to the current name.")
    location = _dataset_location(client, schema)
    _run(client, f"ALTER TABLE `{ref}` RENAME TO `{new_name}`", location)
    state = _table_state(client, schema, new_name)
    return {
        "action": "rename_table",
        "auth_source": auth_source,
        "previous": table,
        **state,
    }


def rename_column(schema: str, table: str, column: str, new_name: str) -> Dict[str, Any]:
    client, auth_source = _client()
    schema = _check_name(schema, "schema")
    table = _check_name(table, "table")
    column = _check_name(column, "column")
    new_name = _check_name(new_name, "column")
    ref = f"{client.project}.{schema}.{table}"
    table_obj = client.get_table(ref)
    if not any(field.name == column for field in table_obj.schema):
        raise CatalogError(f"Column '{column}' does not exist.")
    if new_name == column:
        raise CatalogError("New name is identical to the current name.")
    location = table_obj.location or _dataset_location(client, schema)
    _run(client, f"ALTER TABLE `{ref}` RENAME COLUMN `{column}` TO `{new_name}`", location)
    state = _table_state(client, schema, table)
    return {"action": "rename_column", "auth_source": auth_source, "previous": column, **state}


def drop_table(schema: str, table: str, confirm: str) -> Dict[str, Any]:
    client, auth_source = _client()
    schema = _check_name(schema, "schema")
    table = _check_name(table, "table")
    if (confirm or "").strip() != table:
        raise CatalogError("Confirmation text does not match the table name.")
    ref = f"{client.project}.{schema}.{table}"
    client.get_table(ref)
    client.delete_table(ref)
    return {"action": "drop_table", "auth_source": auth_source, "schema": schema, "table": table}


def drop_schema(schema: str, confirm: str) -> Dict[str, Any]:
    client, auth_source = _client()
    schema = _check_name(schema, "schema")
    if (confirm or "").strip() != schema:
        raise CatalogError("Confirmation text does not match the schema name.")
    dataset = client.get_dataset(schema)
    tables = [item.table_id for item in client.list_tables(dataset)]
    client.delete_dataset(dataset, delete_contents=True)
    return {
        "action": "drop_schema",
        "auth_source": auth_source,
        "schema": schema,
        "dropped_tables": tables,
    }


def rename_schema(schema: str, new_name: str) -> Dict[str, Any]:
    """BigQuery cannot rename datasets, so copy every table then drop the old one."""
    client, auth_source = _client()
    schema = _check_name(schema, "schema")
    new_name = _check_name(new_name, "schema")
    if new_name == schema:
        raise CatalogError("New name is identical to the current name.")
    try:
        client.get_dataset(new_name)
        raise CatalogError(f"Schema '{new_name}' already exists.")
    except CatalogError:
        raise
    except Exception:
        pass
    old = client.get_dataset(schema)
    location = old.location or DEFAULT_LOCATION

    from google.cloud import bigquery

    new_dataset = bigquery.Dataset(f"{client.project}.{new_name}")
    new_dataset.location = location
    client.create_dataset(new_dataset)

    copied: List[str] = []
    try:
        for item in client.list_tables(old):
            table = client.get_table(item.reference)
            create = _create_sql(
                client.project,
                new_name,
                table.table_id,
                list(table.schema),
                _constraints(table, dataset_override=new_name),
                table,
            )
            _run(client, create, location)
            if table.num_rows:
                _run(
                    client,
                    f"INSERT INTO `{client.project}.{new_name}.{table.table_id}` "
                    f"SELECT * FROM `{client.project}.{schema}.{table.table_id}`",
                    location,
                )
            copied.append(table.table_id)
    except Exception:
        try:
            client.delete_dataset(new_dataset, delete_contents=True, not_found_ok=True)
        except Exception:
            pass
        raise

    client.delete_dataset(old, delete_contents=True)
    return {
        "action": "rename_schema",
        "auth_source": auth_source,
        "previous": schema,
        "schema": new_name,
        "location": location,
        "copied_tables": copied,
    }


def _target_type(new_type: str, length: Optional[int], precision: Optional[int], scale: Optional[int]) -> str:
    base = _TYPES.get((new_type or "").strip().upper())
    if not base:
        raise CatalogError(f"Unsupported data type '{new_type}'.")
    if base in ("STRING", "BYTES") and length:
        if not 1 <= int(length) <= 10_000_000:
            raise CatalogError("Length must be between 1 and 10,000,000.")
        return f"{base}({int(length)})"
    if base in ("NUMERIC", "BIGNUMERIC") and precision:
        if not 1 <= int(precision) <= (38 if base == "NUMERIC" else 76):
            raise CatalogError(f"Precision is out of range for {base}.")
        if scale is not None and not 0 <= int(scale) <= int(precision):
            raise CatalogError("Scale must be between 0 and the precision value.")
        if scale is not None:
            return f"{base}({int(precision)},{int(scale)})"
        return f"{base}({int(precision)})"
    return base


def _conversion_expression(field: Any, target: Any, date_format: str) -> str:
    source = field.field_type
    destination = target.field_type
    column = f"`{field.name}`"
    if date_format and source in _DATE_TYPES and destination == "STRING":
        return f"{_FORMAT_FN[source]}('{date_format}', {column})"
    if date_format and source == "STRING" and destination in _DATE_TYPES:
        return f"{_PARSE_FN[destination]}('{date_format}', {column})"
    if source == destination:
        return column
    return f"CAST({column} AS {destination})"


def alter_column(
    schema: str,
    table: str,
    column: str,
    new_type: str,
    length: Optional[int] = None,
    precision: Optional[int] = None,
    scale: Optional[int] = None,
    date_format: str = "",
) -> Dict[str, Any]:
    client, auth_source = _client()
    schema = _check_name(schema, "schema")
    table = _check_name(table, "table")
    column = _check_name(column, "column")
    target_type = _target_type(new_type, length, precision, scale)
    date_format = (date_format or "").strip()
    if date_format and not _DATE_FORMAT.match(date_format):
        raise CatalogError("Date format contains unsupported characters.")

    ref = f"{client.project}.{schema}.{table}"
    table_obj = client.get_table(ref)
    field = next((item for item in table_obj.schema if item.name == column), None)
    if not field:
        raise CatalogError(f"Column '{column}' does not exist.")
    location = table_obj.location or _dataset_location(client, schema)

    from google.cloud import bigquery

    if not date_format:
        try:
            _run(
                client,
                f"ALTER TABLE `{ref}` ALTER COLUMN `{column}` SET DATA TYPE {target_type}",
                location,
            )
            fresh = client.get_table(ref)
            updated = next((item for item in fresh.schema if item.name == column), None)
            return {
                "action": "alter_column",
                "auth_source": auth_source,
                "applied": "alter",
                "schema": schema,
                "table": table,
                "column": column,
                "type": _type_sql(updated) if updated else target_type,
                "previous_type": _type_sql(field),
            }
        except Exception as exc:
            alter_error = str(exc)[:300]
    else:
        alter_error = ""

    # BigQuery only widens types with ALTER COLUMN. Rebuild the table so any
    # conversion (including date parsing/formatting) works, keeping data.
    new_field = bigquery.SchemaField(
        name=field.name,
        field_type=target_type.split("(", 1)[0],
        mode=field.mode,
        description=field.description,
        max_length=(int(length) if target_type.startswith(("STRING(", "BYTES(")) else None),
        precision=(int(precision) if target_type.startswith(("NUMERIC(", "BIGNUMERIC(")) and precision else None),
        scale=(int(scale) if target_type.startswith(("NUMERIC(", "BIGNUMERIC(")) and scale is not None else None),
    )
    fields = [new_field if item.name == column else item for item in table_obj.schema]

    constraint_lines = _constraints(table_obj)
    notes: List[str] = []
    constraints = getattr(table_obj, "table_constraints", None)
    if not constraints:
        constraints = (getattr(table_obj, "_properties", None) or {}).get("tableConstraints") or {}
    primary_columns = (constraints.get("primaryKey") or {}).get("columns") or []
    if column in primary_columns:
        constraint_lines = []
        notes.append("Primary key was dropped because the key column type changed; recreate it if needed.")

    temp_id = "__np_tmp_" + uuid.uuid4().hex[:10]
    create = _create_sql(client.project, schema, temp_id, fields, constraint_lines, table_obj)
    expressions = [
        _conversion_expression(item, new_field, date_format) if item.name == column else f"`{item.name}`"
        for item in table_obj.schema
    ]
    temp_ref = f"{client.project}.{schema}.{temp_id}"
    _run(client, create, location)
    try:
        if int(table_obj.num_rows or 0) > 0:
            _run(
                client,
                f"INSERT INTO `{temp_ref}` SELECT {', '.join(expressions)} FROM `{ref}`",
                location,
                timeout=600,
            )
        client.delete_table(ref)
        _run(client, f"ALTER TABLE `{temp_ref}` RENAME TO `{table}`", location)
    except Exception as exc:
        try:
            client.delete_table(temp_ref, not_found_ok=True)
        except Exception:
            pass
        raise CatalogError(f"Column change failed: {str(exc)[:300]}") from exc

    state = _table_state(client, schema, table)
    updated = next((item for item in state["columns"] if item["name"] == column), None)
    return {
        "action": "alter_column",
        "auth_source": auth_source,
        "applied": "recreate",
        "previous_type": _type_sql(field),
        "alter_error": alter_error,
        "notes": notes,
        **state,
        "column": column,
        "type": (updated or {}).get("type") or target_type,
    }


def schema_info(schema: str) -> Dict[str, Any]:
    client, auth_source = _client()
    schema = _check_name(schema, "schema")
    dataset = client.get_dataset(schema)
    tables = list(client.list_tables(dataset))
    total_rows = 0
    for item in tables:
        try:
            total_rows += int(item.num_rows or 0)
        except Exception:
            continue
    return {
        "action": "schema_info",
        "auth_source": auth_source,
        "schema": schema,
        "location": dataset.location,
        "tables": len(tables),
        "rows": total_rows,
    }
