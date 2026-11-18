"""BigQuery -> AWS S3 data plane, free-tier only.

Every dataset in the BigQuery sandbox is exported as Snappy Parquet to
``s3://<bucket>/bronze/bigquery/<dataset>/<table>/<table>.parquet`` with a
per-dataset ``_MANIFEST.json`` and ``_SUCCESS`` marker. After a successful
export the run is announced through the free-tier AWS services that need no
credit card: SQS (``nanopro-pipeline-events``), DynamoDB
(``nanopro_pipeline_runs``, 5/5 provisioned) and CloudWatch custom metrics in
the ``NanoPro/BigQueryAWS`` namespace.

Nothing here fabricates success: if IAM denies a service or BigQuery is not
authenticated, the returned payload carries the real error instead.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.chat_s3_export import _aws_config, _bq_client, _s3_client, export_tables
from app.core.logger import log_event

SQS_QUEUE_NAME = "nanopro-pipeline-events"
DDB_TABLE_NAME = "nanopro_pipeline_runs"
CW_NAMESPACE = "NanoPro/BigQueryAWS"
EXPORT_ROOT = "bronze/bigquery"
RUN_ID_FORMAT = "%Y%m%dT%H%M%SZ"

_CAPS_CACHE: Dict[str, Any] = {"at": 0.0, "value": None}
_CAPS_TTL = 300.0


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _run_id() -> str:
    return datetime.now(timezone.utc).strftime(RUN_ID_FORMAT)


def _aws_client(config: Dict[str, str], service: str):
    import boto3

    return boto3.Session(
        region_name=config["region"],
        aws_access_key_id=config["access_key"],
        aws_secret_access_key=config["secret_key"],
    ).client(service)


def _err(exc: Exception) -> str:
    text = str(exc) or type(exc).__name__
    return text[:240]


def _bq_datasets(client: Any) -> List[str]:
    names = []
    for item in client.list_datasets():
        name = getattr(item, "dataset_id", None)
        if not name and isinstance(item, dict):
            name = item.get("dataset_id") or item.get("datasetId")
        if name:
            names.append(str(name))
    return sorted(names)


def _bq_tables(client: Any, dataset: str) -> List[str]:
    return sorted(str(item.table_id) for item in client.list_tables(f"{client.project}.{dataset}"))


def _sqs_send(config: Dict[str, str], body: Dict[str, Any]) -> Dict[str, Any]:
    try:
        sqs = _aws_client(config, "sqs")
        try:
            url = sqs.get_queue_url(QueueName=SQS_QUEUE_NAME)["QueueUrl"]
        except Exception:
            url = sqs.create_queue(
                QueueName=SQS_QUEUE_NAME,
                Attributes={"MessageRetentionPeriod": "1209600", "VisibilityTimeout": "300"},
            )["QueueUrl"]
        res = sqs.send_message(QueueUrl=url, MessageBody=json.dumps(body, default=str)[:250000])
        return {"status": "sent", "queue": SQS_QUEUE_NAME, "message_id": res.get("MessageId")}
    except Exception as exc:
        return {"status": "unavailable", "queue": SQS_QUEUE_NAME, "error": _err(exc)}


def _dynamodb_record(config: Dict[str, str], run: Dict[str, Any]) -> Dict[str, Any]:
    try:
        ddb = _aws_client(config, "dynamodb")
        try:
            ddb.describe_table(TableName=DDB_TABLE_NAME)
        except Exception:
            ddb.create_table(
                TableName=DDB_TABLE_NAME,
                KeySchema=[{"AttributeName": "run_id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "run_id", "AttributeType": "S"}],
                BillingMode="PROVISIONED",
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
        ddb.put_item(
            TableName=DDB_TABLE_NAME,
            Item={
                "run_id": {"S": str(run.get("run_id") or _run_id())},
                "started_at": {"S": str(run.get("started_at") or "")},
                "status": {"S": str(run.get("status") or "")},
                "tables": {"N": str(len(run.get("tables") or []))},
                "rows": {"N": str(int(run.get("rows") or 0))},
                "bytes": {"N": str(int(run.get("bytes") or 0))},
                "summary": {"S": str(run.get("summary") or "")[:900]},
            },
        )
        return {"status": "recorded", "table": DDB_TABLE_NAME}
    except Exception as exc:
        return {"status": "unavailable", "table": DDB_TABLE_NAME, "error": _err(exc)}


def _cloudwatch_metrics(config: Dict[str, str], run: Dict[str, Any]) -> Dict[str, Any]:
    try:
        cw = _aws_client(config, "cloudwatch")
        cw.put_metric_data(
            Namespace=CW_NAMESPACE,
            MetricData=[
                {"MetricName": "TablesExported", "Unit": "Count", "Value": len(run.get("tables") or [])},
                {"MetricName": "RowsExported", "Unit": "Count", "Value": int(run.get("rows") or 0)},
                {"MetricName": "BytesExported", "Unit": "Bytes", "Value": int(run.get("bytes") or 0)},
                {"MetricName": "ExportDurationMs", "Unit": "Milliseconds", "Value": int(run.get("duration_ms") or 0)},
            ],
        )
        return {"status": "published", "namespace": CW_NAMESPACE, "metrics": 4}
    except Exception as exc:
        return {"status": "unavailable", "namespace": CW_NAMESPACE, "error": _err(exc)}


def capabilities(force: bool = False) -> Dict[str, Any]:
    """Best-effort free-tier capability probe (cached 5 minutes)."""
    now = time.time()
    if not force and _CAPS_CACHE["value"] and now - _CAPS_CACHE["at"] < _CAPS_TTL:
        return _CAPS_CACHE["value"]

    config = _aws_config()
    result: Dict[str, Any] = {
        "region": config["region"],
        "bucket": config["bucket"],
        "checked_at": _now(),
        "services": {},
    }
    if not config["access_key"] or not config["secret_key"] or not config["bucket"]:
        result["status"] = "not_configured"
        result["services"]["s3"] = {"status": "not_configured", "error": "AWS access key/secret/bucket missing."}
        _CAPS_CACHE.update({"at": now, "value": result})
        return result

    try:
        s3 = _s3_client(config)
        s3.head_bucket(Bucket=config["bucket"])
        result["services"]["s3"] = {"status": "available", "bucket": config["bucket"]}
        s3_ok = True
    except Exception as exc:
        result["services"]["s3"] = {"status": "unavailable", "bucket": config["bucket"], "error": _err(exc)}
        s3_ok = False

    probes = [
        ("sqs", lambda: _aws_client(config, "sqs").list_queues(MaxResults=10)),
        ("dynamodb", lambda: _aws_client(config, "dynamodb").list_tables(Limit=10)),
        ("cloudwatch", lambda: _aws_client(config, "cloudwatch").list_metrics(Namespace=CW_NAMESPACE, RecentlyActive="PT3H")),
        ("glue", lambda: _aws_client(config, "glue").get_databases(MaxResults=10)),
        ("athena", lambda: _aws_client(config, "athena").list_work_groups()),
        ("lambda", lambda: _aws_client(config, "lambda").list_functions(MaxItems=10)),
        ("sns", lambda: _aws_client(config, "sns").list_topics()),
    ]
    for name, call in probes:
        try:
            call()
            result["services"][name] = {"status": "available"}
        except Exception as exc:
            result["services"][name] = {"status": "unavailable", "error": _err(exc)}

    available = [name for name, item in result["services"].items() if item["status"] == "available"]
    result["status"] = "success" if s3_ok else "partial"
    result["available_services"] = available
    _CAPS_CACHE.update({"at": now, "value": result})
    return result


def run_pipeline(datasets: Optional[List[str]] = None) -> Dict[str, Any]:
    """Export every BigQuery dataset (or the given subset) to S3 as Parquet."""
    started = time.time()
    run_id = _run_id()
    config = _aws_config()
    payload: Dict[str, Any] = {
        "status": "error",
        "action": "bigquery_to_aws",
        "run_id": run_id,
        "started_at": _now(),
        "datasets": [],
        "tables": [],
        "rows": 0,
        "bytes": 0,
        "s3": {},
        "aws_services": {},
        "_http": 200,
    }

    if not config["bucket"]:
        payload["message"] = "AWS_S3_BUCKET is not configured."
        payload["summary"] = payload["message"]
        payload["_http"] = 400
        return payload

    try:
        client = _bq_client()
        s3 = _s3_client(config)
    except Exception as exc:
        payload["message"] = f"AWS/BigQuery client init failed: {_err(exc)}"
        payload["summary"] = payload["message"]
        payload["_http"] = 502
        return payload

    try:
        available = _bq_datasets(client)
    except Exception as exc:
        payload["message"] = f"BigQuery dataset listing failed: {_err(exc)}"
        payload["summary"] = payload["message"]
        payload["_http"] = 502
        return payload

    targets = [d for d in (datasets or available) if d in available] if datasets else available
    if not targets:
        payload["message"] = "No BigQuery datasets found to export."
        payload["summary"] = payload["message"]
        payload["_http"] = 404
        return payload

    all_files: List[Dict[str, Any]] = []
    failures: List[str] = []
    for dataset in targets:
        try:
            tables = _bq_tables(client, dataset)
        except Exception as exc:
            failures.append(f"{dataset}: table listing failed: {_err(exc)}")
            payload["datasets"].append({"dataset": dataset, "status": "error", "error": _err(exc), "tables": []})
            continue
        if not tables:
            payload["datasets"].append({"dataset": dataset, "status": "empty", "tables": []})
            continue
        try:
            manifest = export_tables(
                client, s3, config["bucket"], dataset, tables,
                prefix=f"{EXPORT_ROOT}/{dataset}",
            )
        except Exception as exc:
            failures.append(f"{dataset}: export failed: {_err(exc)}")
            payload["datasets"].append({"dataset": dataset, "status": "error", "error": _err(exc), "tables": []})
            continue

        all_files.extend(manifest["files"])
        failures.extend(manifest.get("failures") or [])
        payload["datasets"].append({
            "dataset": dataset,
            "status": "success" if not manifest.get("failures") else "partial",
            "prefix": f"s3://{config['bucket']}/{EXPORT_ROOT}/{dataset}/",
            "manifest": manifest.get("manifest_key"),
            "success_marker": manifest.get("success_marker"),
            "tables": manifest["files"],
        })

    payload["tables"] = all_files
    payload["rows"] = sum(int(item.get("rows") or 0) for item in all_files)
    payload["bytes"] = sum(int(item.get("bytes") or 0) for item in all_files)
    payload["s3"] = {
        "bucket": config["bucket"],
        "prefix": f"s3://{config['bucket']}/{EXPORT_ROOT}/",
        "objects": len(all_files) + len(payload["datasets"]),
    }
    payload["duration_ms"] = round((time.time() - started) * 1000)
    payload["failures"] = failures
    payload["status"] = "success" if all_files and not failures else ("partial" if all_files else "error")

    event = {
        "event": "bigquery_to_aws",
        "run_id": run_id,
        "status": payload["status"],
        "datasets": targets,
        "tables": len(all_files),
        "rows": payload["rows"],
        "bytes": payload["bytes"],
        "at": _now(),
    }
    payload["aws_services"]["sqs"] = _sqs_send(config, event)
    payload["aws_services"]["dynamodb"] = _dynamodb_record(config, payload)
    payload["aws_services"]["cloudwatch"] = _cloudwatch_metrics(config, payload)

    payload["summary"] = (
        f"{len(all_files)} tables exported from {len(targets)} dataset(s) — "
        f"{payload['rows']} rows, {payload['bytes']} bytes to {payload['s3']['prefix']}"
        + (f"; {len(failures)} failure(s)" if failures else "")
    )
    payload["message"] = payload["summary"]
    payload["_http"] = 200 if payload["status"] != "error" else 502
    log_event(f"BigQuery→AWS pipeline {run_id}: {payload['summary']}", component="BigQueryAWSPipeline")
    return payload
