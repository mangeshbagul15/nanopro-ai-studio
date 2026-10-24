"""Direct Oracle-to-S3 batch ingestion for accounts where AWS DMS is unavailable.

The worker keeps the S3 checkpoint unchanged until Snowflake L0/L1/L2 finish,
so a failed run can safely replay the same watermark range. Oracle identifiers
are validated before they are interpolated into SQL; all credentials come from
NanoPro's vault or the normal AWS credential chain.
"""
from __future__ import annotations

import gzip
import json
import os
import re
import tempfile
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import quote
from uuid import uuid4


IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_$#]*(?:\.[A-Za-z][A-Za-z0-9_$#]*)?$")
STAGE_NAME = re.compile(r"^@(?:~|[A-Za-z][A-Za-z0-9_$#]*)(?:/[A-Za-z0-9_./-]+)?$")


def _json_value(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if hasattr(value, "read"):
        return _json_value(value.read())
    return str(value)


def _encode_watermark(value: Any) -> dict[str, str]:
    if isinstance(value, datetime):
        return {"kind": "datetime", "value": value.isoformat()}
    if isinstance(value, date):
        return {"kind": "date", "value": value.isoformat()}
    if isinstance(value, (int, float, Decimal)):
        return {"kind": "number", "value": str(value)}
    return {"kind": "string", "value": str(value)}


def _decode_watermark(value: Any) -> Any:
    if not isinstance(value, dict) or "value" not in value:
        raise RuntimeError("S3 checkpoint watermark has an unsupported format.")
    if value.get("kind") == "datetime":
        return datetime.fromisoformat(value["value"])
    if value.get("kind") == "date":
        return date.fromisoformat(value["value"])
    if value.get("kind") == "number":
        return Decimal(value["value"])
    return value["value"]


def _aws_session(region: str, vault: dict[str, Any] | None = None):
    import boto3

    from app.core.connection_manager import connection_manager

    access = os.environ.get("AWS_ACCESS_KEY_ID", "").strip()
    secret = os.environ.get("AWS_SECRET_ACCESS_KEY", "").strip()
    token = os.environ.get("AWS_SESSION_TOKEN", "").strip()
    vault = vault or connection_manager.get_connection_config("AWS_S3_DATA_LAKE", mask=False) or {}
    metadata = vault.get("metadata") or {}
    if not (access and secret):
        access = (vault.get("username") or "").strip()
        secret = (vault.get("secret_value") or "").strip()
        token = (metadata.get("session_token") or metadata.get("aws_session_token") or token).strip()
    if bool(access) != bool(secret):
        raise RuntimeError("AWS credential pair is incomplete in NanoPro Vault/environment.")
    args = {"region_name": region}
    if access and secret:
        args.update(aws_access_key_id=access, aws_secret_access_key=secret)
        if token:
            args["aws_session_token"] = token
    return boto3.Session(**args)


def _oracle_session(connection_name: str):
    import oracledb

    from app.core.connection_manager import connection_manager

    # Candidate failover connection chain: Primary -> Tailscale VPN -> Remote LAN
    candidates = [connection_name, "MY_ORACLE_XE_REMOTE_New", "MY_ORACLE_XE_REMOTE", "MY_ORACLE_XE_LOCAL"]
    last_err = None

    for candidate in candidates:
        cfg = connection_manager.get_connection_config(candidate, mask=False)
        if not cfg or not cfg.get("secret_value"):
            continue
        meta = cfg.get("metadata") or {}
        if meta.get("connection_type") == "ORDS_REST":
            continue
        host = meta.get("hostname") or cfg.get("host")
        port = int(meta.get("port") or cfg.get("port") or 1521)
        service = meta.get("service_name") or cfg.get("database_name")
        user = meta.get("username") or cfg.get("username")
        if not all((host, service, user)):
            continue
        try:
            dsn = oracledb.makedsn(host, port, service_name=service)
            conn = oracledb.connect(user=user, password=cfg["secret_value"], dsn=dsn)
            return conn
        except Exception as e:
            last_err = e

    # If all physical network listeners are offline, raise structured message
    # so data_pipeline_runner engages the Autonomous CDC Staging Buffer instead of failing
    raise RuntimeError(f"Oracle Listener offline across all endpoints ({last_err}). NanoPro Autonomous CDC Staging Buffer engaged.")


class OracleS3Ingestion:
    """Extract one configured Oracle table to gzipped NDJSON in S3."""

    def __init__(self):
        self.connection_name = os.environ.get("NANOPRO_ORACLE_CONNECTION", "ORACLE_APEX_23AI_CLOUD").strip()
        self.table = os.environ.get("NANOPRO_ORACLE_SOURCE_TABLE", "NP_DEMO_L1_CLEAN_TXNS").strip()
        self.watermark_column = os.environ.get("NANOPRO_ORACLE_WATERMARK_COLUMN", "TXN_TIMESTAMP").strip()
        self.ords_path = os.environ.get("NANOPRO_ORACLE_ORDS_PATH", "nanopro/v1/l1").strip("/")
        from app.core.connection_manager import connection_manager
        self.aws_vault = connection_manager.get_connection_config("AWS_S3_DATA_LAKE", mask=False) or {}
        aws_meta = self.aws_vault.get("metadata") or {}
        self.bucket = (os.environ.get("AWS_S3_BUCKET") or aws_meta.get("bucket") or self.aws_vault.get("database_name") or "").strip()
        self.region = (os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_REGION") or aws_meta.get("region") or "ap-southeast-2").strip()
        self.prefix = os.environ.get("AWS_S3_PREFIX", "nanopro/oracle").strip("/")
        if not self.table or not IDENTIFIER.fullmatch(self.table):
            raise RuntimeError("Set NANOPRO_ORACLE_SOURCE_TABLE to a validated OWNER.TABLE or TABLE identifier.")
        if not self.watermark_column or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_$#]*", self.watermark_column):
            raise RuntimeError("Set NANOPRO_ORACLE_WATERMARK_COLUMN to a source column used for incremental loads.")
        if not self.bucket:
            raise RuntimeError("Set AWS_S3_BUCKET to the existing S3 bucket name.")
        if not re.fullmatch(r"[A-Za-z0-9.-]{3,63}", self.bucket):
            raise RuntimeError("AWS_S3_BUCKET is not a valid bucket name.")
        self.table_key = re.sub(r"[^a-z0-9]+", "_", self.table.lower()).strip("_")
        self.checkpoint_key = f"{self.prefix}/_control/checkpoints/{self.table_key}.json"
        self.s3 = _aws_session(self.region, self.aws_vault).client("s3")

    def extract_and_upload(self, run_id: str) -> dict[str, Any]:
        checkpoint = self._read_checkpoint()
        full_load = not bool(checkpoint.get("full_load_complete"))
        watermark = checkpoint.get("watermark")
        suffix = "full-load" if full_load else "incremental"
        key = f"{self.prefix}/{suffix}/{self.table_key}/{datetime.now().strftime('%Y/%m/%d')}/{run_id}.json.gz"
        local_path = Path(tempfile.gettempdir()) / f"nanopro_{self.table_key}_{run_id}.json.gz"
        count = 0
        max_watermark = _decode_watermark(watermark) if watermark is not None else None

        try:
            from app.core.connection_manager import connection_manager
            cfg = connection_manager.get_connection_config(self.connection_name, mask=False) or {}
            meta = cfg.get("metadata") or {}
            is_ords = meta.get("connection_type") == "ORDS_REST" or self.connection_name == "ORACLE_APEX_23AI_CLOUD"
            if is_ords:
                from app.core.ords_client import ORDSClient
                rows = ORDSClient(self.connection_name).get_items(self.ords_path)
                columns = list(rows[0]) if rows else []
                if self.watermark_column.upper() not in {str(name).upper() for name in columns}:
                    raise RuntimeError("Configured watermark column is not present in the clean L1 REST response.")
                watermark_key = next(name for name in columns if str(name).upper() == self.watermark_column.upper())
                pii_pattern = re.compile(r"^(EMAIL|PHONE|MOBILE|ACCOUNT_NUMBER|PAN|AADHAAR|ADDRESS|CUSTOMER_NAME|FULL_NAME|FIRST_NAME|LAST_NAME|SSN|DATE_OF_BIRTH|DOB|POSTAL_CODE|ZIP_CODE)$", re.I)
                if any(pii_pattern.search(str(name)) for name in columns):
                    raise RuntimeError("PII column detected in the ORDS L1 payload; refusing to upload it to S3.")
                if not full_load and watermark is None:
                    raise RuntimeError("S3 checkpoint has no watermark; refusing an unsafe incremental run.")
                with gzip.open(local_path, "wt", encoding="utf-8", newline="\n") as handle:
                    for row in rows:
                        current = row.get(watermark_key)
                        if current is None:
                            continue
                        if not full_load and str(current) < str(max_watermark):
                            continue
                        if max_watermark is None or str(current) > str(max_watermark):
                            max_watermark = current
                        handle.write(json.dumps(row, default=_json_value, ensure_ascii=False, separators=(",", ":")))
                        handle.write("\n")
                        count += 1
            else:
                query = f"SELECT * FROM {self.table}"
                binds = None
                if not full_load:
                    if watermark is None:
                        raise RuntimeError("S3 checkpoint has no watermark; refusing an unsafe incremental run.")
                    query += f" WHERE {self.watermark_column} >= :last_watermark ORDER BY {self.watermark_column}"
                    binds = {"last_watermark": max_watermark}
                oracle = _oracle_session(self.connection_name)
                try:
                    cursor = oracle.cursor()
                    try:
                        cursor.arraysize = 1000
                        cursor.execute(query, binds or {})
                        columns = [str(desc[0]) for desc in cursor.description or []]
                        if self.watermark_column.upper() not in {name.upper() for name in columns}:
                            raise RuntimeError("Configured Oracle watermark column is not present in the selected table.")
                        watermark_index = next(i for i, name in enumerate(columns) if name.upper() == self.watermark_column.upper())
                        with gzip.open(local_path, "wt", encoding="utf-8", newline="\n") as handle:
                            while True:
                                batch = cursor.fetchmany(1000)
                                if not batch:
                                    break
                                for values in batch:
                                    row = dict(zip(columns, values))
                                    current = values[watermark_index]
                                    if current is not None and (max_watermark is None or current > max_watermark):
                                        max_watermark = current
                                    handle.write(json.dumps(row, default=_json_value, ensure_ascii=False, separators=(",", ":")))
                                    handle.write("\n")
                                    count += 1
                    finally:
                        cursor.close()
                finally:
                    oracle.close()
        except Exception:
            local_path.unlink(missing_ok=True)
            raise

        if max_watermark is None:
            local_path.unlink(missing_ok=True)
            raise RuntimeError("Oracle extract returned no usable watermark; checkpoint was not advanced.")
        watermark_value = _encode_watermark(max_watermark)
        try:
            self.s3.upload_file(
                str(local_path), self.bucket, key,
                ExtraArgs={"ServerSideEncryption": "AES256", "ContentType": "application/x-ndjson", "ContentEncoding": "gzip"},
            )
        except Exception:
            local_path.unlink(missing_ok=True)
            raise
        return {
            "mode": suffix, "rows": count, "s3_uri": f"s3://{self.bucket}/{key}",
            "s3_key": key, "local_path": str(local_path), "watermark": watermark_value,
            "full_load_complete": True, "checkpoint_key": self.checkpoint_key,
        }

    def commit_checkpoint(self, result: dict[str, Any]) -> None:
        body = {
            "source_table": self.table,
            "watermark_column": self.watermark_column,
            "watermark": result["watermark"],
            "full_load_complete": True,
            "last_s3_key": result["s3_key"],
            "updated_at_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }
        self.s3.put_object(
            Bucket=self.bucket, Key=self.checkpoint_key,
            Body=json.dumps(body, separators=(",", ":")).encode("utf-8"),
            ContentType="application/json", ServerSideEncryption="AES256",
        )

    def upload_to_snowflake_stage(self, cursor, result: dict[str, Any], stage_path: str) -> None:
        if not STAGE_NAME.fullmatch(stage_path):
            raise RuntimeError("NANOPRO_SNOWFLAKE_INTERNAL_STAGE must be an internal stage such as @~/nanopro_landing.")
        destination = f"{stage_path.rstrip('/')}/{uuid4().hex}"
        local_uri = Path(result["local_path"]).resolve().as_uri()
        cursor.execute(
            f"PUT '{local_uri}' {destination} AUTO_COMPRESS=FALSE OVERWRITE=FALSE PARALLEL=1"
        )
        result["snowflake_stage_path"] = destination

    def _read_checkpoint(self) -> dict[str, Any]:
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=self.checkpoint_key)
            value = json.loads(response["Body"].read().decode("utf-8"))
            if value.get("source_table", "").upper() != self.table.upper():
                raise RuntimeError("S3 checkpoint belongs to a different source table.")
            return value
        except self.s3.exceptions.NoSuchKey:
            return {}
        except Exception as exc:
            if getattr(exc, "response", {}).get("Error", {}).get("Code") in {"404", "NoSuchKey", "NotFound"}:
                return {}
            raise RuntimeError("Unable to read the S3 pipeline checkpoint; stopping before Oracle extraction.") from exc
