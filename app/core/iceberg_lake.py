"""Publishes the bronze Parquet exports as Apache Iceberg tables in Glue.

The open-table layer lives under ``s3://<bucket>/gold/iceberg`` and is
registered in the ``nanopro_iceberg`` Glue database, so Athena and any
Iceberg-compatible engine can query it. Everything runs inside the app (no
Glue ETL job, no Athena scans), which keeps it inside the free tier.
"""
from __future__ import annotations

import io
import os
from typing import Any, Dict, List

ICEBERG_DATABASE = "nanopro_iceberg"
ICEBERG_PREFIX = "gold/iceberg"


def _table_name(dataset: str, table: str) -> str:
    return f"{dataset}_{table}".lower().replace("-", "_")


def publish(config: Dict[str, str], files: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Rewrite each exported Parquet file into an Iceberg table."""
    try:
        import pyarrow.parquet as pq
        from pyiceberg.catalog.glue import GlueCatalog
    except Exception as exc:
        return {"status": "unavailable", "error": f"pyiceberg/pyarrow missing: {str(exc)[:180]}"}

    if not files:
        return {"status": "skipped", "reason": "no exported tables"}

    os.environ["AWS_ACCESS_KEY_ID"] = config["access_key"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = config["secret_key"]
    os.environ.setdefault("AWS_DEFAULT_REGION", config["region"])

    try:
        import boto3

        s3 = boto3.Session(region_name=config["region"]).client("s3")
        catalog = GlueCatalog("glue", **{
            "type": "glue",
            "warehouse": f"s3://{config['bucket']}/{ICEBERG_PREFIX}",
            "glue.region": config["region"],
            "py-io-impl": "pyiceberg.io.pyarrow.PyArrowFileIO",
        })
        catalog.create_namespace_if_not_exists(ICEBERG_DATABASE)
    except Exception as exc:
        return {"status": "unavailable", "database": ICEBERG_DATABASE, "error": str(exc)[:240]}

    published, errors = 0, []
    for item in files:
        key = str(item.get("key") or "")
        dataset = str(item.get("dataset") or "")
        if not key or not dataset:
            continue
        name = _table_name(dataset, str(item.get("table") or ""))
        ident = f"{ICEBERG_DATABASE}.{name}"
        try:
            body = s3.get_object(Bucket=config["bucket"], Key=key)["Body"].read()
            arrow = pq.read_table(io.BytesIO(body))
            if not arrow.num_rows:
                errors.append(f"{name}: empty table")
                continue
            try:
                catalog.purge_table(ident)
            except Exception:
                pass
            table = catalog.create_table(
                ident,
                schema=arrow.schema,
                location=f"s3://{config['bucket']}/{ICEBERG_PREFIX}/{name}",
            )
            table.append(arrow)
            published += 1
        except Exception as exc:
            errors.append(f"{name}: {str(exc)[:160]}")

    result: Dict[str, Any] = {
        "status": "published" if published and not errors else ("partial" if published else "unavailable"),
        "database": ICEBERG_DATABASE,
        "warehouse": f"s3://{config['bucket']}/{ICEBERG_PREFIX}",
        "tables": published,
    }
    if errors:
        result["errors"] = errors[:5]
    return result
