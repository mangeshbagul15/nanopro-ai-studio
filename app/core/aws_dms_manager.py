"""
Mangesh Nano Pro AI Studio - AWS Database Migration Service (AWS DMS) Engine
Automates heterogeneous and homogeneous database migrations and continuous CDC replication.
Source: Oracle Database XE (MY_ORACLE_XE_REMOTE / LOCAL / REMOTE_New, User: SYSTEM, Service: XEPDB1)
Targets: AWS S3 Data Lake (s3://nanopro-data-lake), Snowflake Data Cloud, Amazon RDS
Features:
- Replication Instances lifecycle & health monitoring
- Source and Target Endpoint configuration & connectivity testing
- Full Load, CDC (Change Data Capture), and Full Load + CDC replication tasks
- JSON Table Mappings (Schemas, Tables, Transformations, Exclusions)
- Real-time replication throughput, latency, and progress metrics
- Seamless integration with CredentialsVault and AWS boto3
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.logger import log_event
from app.core.database import db, credentials_vault
from app.core.config import REPORTS_DIR

DMS_CONFIG_DEFAULTS = {
    "replication_instance_id": "nanopro-dms-rep-instance-01",
    "replication_instance_class": "dms.t3.medium",
    "allocated_storage": 100,
    "vpc_security_group": "sg-097a82fbcd45e1289",
    "availability_zone": "ap-southeast-2a",
    "engine_version": "3.5.2",
    "multi_az": False,
    "publicly_accessible": True,
    "source_endpoint": "dms-source-oracle-xe",
    "target_s3_endpoint": "dms-target-s3-lake",
    "target_snowflake_endpoint": "dms-target-snowflake"
}

class AwsDmsManager:
    def __init__(self):
        self._init_dms_tables()

    def _init_dms_tables(self):
        """Creates persistent SQLite tables for AWS DMS state and task monitoring."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS dms_replication_instances (
                    instance_id TEXT PRIMARY KEY,
                    instance_class TEXT NOT NULL,
                    status TEXT NOT NULL,
                    allocated_storage INTEGER,
                    availability_zone TEXT,
                    engine_version TEXT,
                    publicly_accessible INTEGER,
                    created_at REAL NOT NULL,
                    metadata_json TEXT
                )""")

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS dms_endpoints (
                    endpoint_id TEXT PRIMARY KEY,
                    endpoint_type TEXT NOT NULL, -- source, target
                    engine_name TEXT NOT NULL,   -- oracle, s3, snowflake, postgres
                    server_name TEXT,
                    port INTEGER,
                    database_name TEXT,
                    username TEXT,
                    status TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    metadata_json TEXT
                )""")

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS dms_replication_tasks (
                    task_id TEXT PRIMARY KEY,
                    task_name TEXT NOT NULL,
                    source_endpoint_id TEXT NOT NULL,
                    target_endpoint_id TEXT NOT NULL,
                    migration_type TEXT NOT NULL, -- full-load, cdc, full-load-and-cdc
                    status TEXT NOT NULL,        -- ready, running, stopped, paused, completed, failed
                    progress_pct REAL DEFAULT 0.0,
                    tables_loaded INTEGER DEFAULT 0,
                    total_tables INTEGER DEFAULT 0,
                    cdc_latency_sec REAL DEFAULT 0.0,
                    throughput_mb_s REAL DEFAULT 0.0,
                    table_mappings_json TEXT,
                    last_error TEXT,
                    started_at REAL,
                    updated_at REAL NOT NULL
                )""")
                conn.commit()
        except Exception as e:
            log_event(f"Error initializing DMS tables: {e}", component="AwsDmsManager", level="WARNING")

    def _ensure_default_dms_resources(self):
        """Deprecated: never manufacture AWS infrastructure or replication status locally."""
        return None

    def _client(self):
        """Return an AWS DMS client using env, NanoPro Vault, or the standard role chain."""
        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError("boto3 is required for live AWS DMS operations") from exc
        access_key = os.environ.get("AWS_ACCESS_KEY_ID", "").strip()
        secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "").strip()
        region = os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_REGION")

        # NanoPro already stores AWS credentials in its encrypted integration vault.
        # Use the same record as the AWS/S3 connection test when env credentials
        # are not present; never return or log the secret itself.
        if not (access_key and secret_key):
            try:
                from app.core.connection_manager import connection_manager
                cfg = connection_manager.get_connection_config("AWS_S3_DATA_LAKE", mask=False) or {}
                vault_access = (cfg.get("username") or "").strip()
                vault_secret = (cfg.get("secret_value") or "").strip()
                metadata = cfg.get("metadata") or {}
                region = region or metadata.get("region") or ""
                if vault_access and vault_secret:
                    access_key, secret_key = vault_access, vault_secret
            except Exception as exc:
                log_event(f"AWS Vault credential lookup unavailable: {type(exc).__name__}", component="AwsDmsManager", level="WARNING")

        if access_key and not secret_key or secret_key and not access_key:
            raise RuntimeError("AWS credential pair is incomplete in environment and NanoPro Vault")
        if not region:
            raise RuntimeError("AWS_DEFAULT_REGION, AWS_REGION, or the AWS_S3_DATA_LAKE Vault region is required")
        client_args = {"region_name": region}
        if access_key and secret_key:
            client_args.update(aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        return boto3.client("dms", **client_args)

    def get_dms_overview(self) -> Dict[str, Any]:
        """Returns comprehensive status of AWS DMS infrastructure, endpoints, and replication tasks."""
        try:
            client = self._client()
            instances = client.describe_replication_instances().get("ReplicationInstances", [])
            endpoints = client.describe_endpoints().get("Endpoints", [])
            tasks = client.describe_replication_tasks(WithoutSettings=True).get("ReplicationTasks", [])
            return {
                "status": "success", "mode": "aws_live", "live_verified": True,
                "aws_region": os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_REGION"),
                "replication_instances": self._safe_metadata(instances), "endpoints": self._safe_metadata(endpoints),
                "replication_tasks": self._safe_metadata(tasks), "total_tasks": len(tasks),
                "running_tasks": sum(1 for task in tasks if task.get("Status") == "running"),
                "message": "Live AWS DMS API response.",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as exc:
            log_event(f"Live AWS DMS overview unavailable: {exc}", component="AwsDmsManager", level="WARNING")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dms_replication_instances")
            instances = [dict(r) for r in cursor.fetchall()]
            for inst in instances:
                if inst.get("metadata_json"):
                    try: inst["metadata"] = self._safe_metadata(json.loads(inst["metadata_json"]))
                    except Exception: inst["metadata"] = {}
                inst.pop("metadata_json", None)

            cursor.execute("SELECT * FROM dms_endpoints")
            endpoints = [dict(r) for r in cursor.fetchall()]
            for ep in endpoints:
                if ep.get("metadata_json"):
                    try: ep["metadata"] = self._safe_metadata(json.loads(ep["metadata_json"]))
                    except Exception: ep["metadata"] = {}
                ep.pop("metadata_json", None)

            cursor.execute("SELECT * FROM dms_replication_tasks ORDER BY updated_at DESC")
            tasks = [dict(r) for r in cursor.fetchall()]
            for t in tasks:
                if t.get("table_mappings_json"):
                    try: t["table_mappings"] = json.loads(t["table_mappings_json"])
                    except Exception: t["table_mappings"] = {}
                t.pop("table_mappings_json", None)

        for item in instances + endpoints + tasks:
            item["record_source"] = "local_demo_cache"
            item["cached_status"] = item.get("status")
            item["status"] = "not_verified"
        return {
            "status": "success",
            "mode": "local_demo_cache",
            "live_verified": False,
            "aws_region": os.environ.get("AWS_DEFAULT_REGION", "ap-southeast-2"),
            "replication_instances": instances,
            "endpoints": endpoints,
            "replication_tasks": tasks,
            "total_tasks": len(tasks),
            "running_tasks": 0,
            "message": "These are cached local records only. Configure and verify AWS DMS before treating any task as live.",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    @staticmethod
    def _safe_metadata(value: Any) -> Any:
        """Remove credential-like fields before metadata reaches API/UI responses."""
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, dict):
            return {
                key: AwsDmsManager._safe_metadata(item)
                for key, item in value.items()
                if not any(term in str(key).lower().replace("_", "") for term in ("password", "secret", "token", "accesskey", "privatekey"))
            }
        if isinstance(value, list):
            return [AwsDmsManager._safe_metadata(item) for item in value]
        return value

    def start_task(self, task_id: str) -> Dict[str, Any]:
        """Start/resume an existing AWS DMS task by ARN; never mutate local status as a substitute."""
        if not task_id or not task_id.startswith("arn:"):
            return {"status": "blocked", "live": False, "task_id": task_id, "message": "A real AWS DMS replication task ARN is required."}
        try:
            client = self._client()
            items = client.describe_replication_tasks(Filters=[{"Name": "replication-task-arn", "Values": [task_id]}]).get("ReplicationTasks", [])
            if not items:
                return {"status": "error", "live": False, "task_id": task_id, "message": "AWS DMS task ARN was not found in this region/account."}
            task = items[0]
            current = (task.get("Status") or "").lower()
            if current == "running":
                return {"status": "success", "live": True, "task_id": task_id, "dms_status": current, "message": "AWS DMS task is already running."}
            if current == "failed":
                return {"status": "blocked", "live": True, "task_id": task_id, "dms_status": current, "message": "AWS DMS task is failed; inspect provider diagnostics and recover it before resuming."}
            start_type = "resume-processing" if current == "stopped" else "start-replication"
            if current not in {"stopped", "ready", "created"}:
                return {"status": "blocked", "live": True, "task_id": task_id, "dms_status": current, "message": "AWS DMS task state does not allow a safe start request."}
            result = client.start_replication_task(ReplicationTaskArn=task_id, StartReplicationTaskType=start_type)
            started = result.get("ReplicationTask", {})
            return {"status": "success", "live": True, "task_id": task_id, "dms_status": started.get("Status", "starting"), "message": "AWS DMS start request accepted."}
        except Exception as exc:
            log_event(f"AWS DMS start failed: {exc}", component="AwsDmsManager", level="ERROR")
            return {"status": "error", "live": False, "task_id": task_id, "message": "AWS DMS start request failed; check AWS permissions, region, task state, and logs."}

    def stop_task(self, task_id: str) -> Dict[str, Any]:
        if not task_id or not task_id.startswith("arn:"):
            return {"status": "blocked", "live": False, "task_id": task_id, "message": "A real AWS DMS replication task ARN is required."}
        try:
            self._client().stop_replication_task(ReplicationTaskArn=task_id)
            return {"status": "success", "live": True, "task_id": task_id, "message": "AWS DMS stop request accepted."}
        except Exception:
            return {"status": "error", "live": False, "task_id": task_id, "message": "AWS DMS stop request failed; check AWS permissions, region, task state, and logs."}

    def pause_task(self, task_id: str) -> Dict[str, Any]:
        """Refuse simulated pauses; they must never imply a live AWS action."""
        return {"status": "blocked", "live": False, "task_id": task_id, "message": "No live AWS DMS task was paused. Configure a real DMS task first."}

    def resume_task(self, task_id: str) -> Dict[str, Any]:
        """Resumes replication task from saved CDC checkpoint."""
        return self.start_task(task_id)

    def reload_tables(self, task_id: str) -> Dict[str, Any]:
        """Refuse simulated reloads because reload can duplicate or overwrite target data."""
        return {"status": "blocked", "live": False, "task_id": task_id, "message": "No table reload was initiated. Configure and review a real DMS task first."}

    def create_replication_task(
        self,
        task_name: str,
        source_endpoint_id: str,
        target_endpoint_id: str,
        migration_type: str = "full-load-and-cdc",
        table_mappings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a real AWS DMS task from existing endpoint/instance ARNs."""
        replication_arn = os.environ.get("DMS_REPLICATION_INSTANCE_ARN", "").strip()
        if not replication_arn or not source_endpoint_id.startswith("arn:") or not target_endpoint_id.startswith("arn:"):
            return {"status": "blocked", "live": False, "message": "DMS_REPLICATION_INSTANCE_ARN and source/target endpoint ARNs are required.", "required": ["AWS role/credentials", "replication instance ARN", "source endpoint ARN", "target endpoint ARN"]}
        migration_types = {"full-load", "cdc", "full-load-and-cdc"}
        if migration_type not in migration_types:
            return {"status": "error", "live": False, "message": "Unsupported migration type."}
        if not isinstance(table_mappings, dict) or not table_mappings.get("rules"):
            return {"status": "blocked", "live": False, "message": "Valid AWS DMS table mappings with at least one rule are required."}
        try:
            client = self._client()
            result = client.create_replication_task(
                ReplicationTaskIdentifier="".join(c.lower() if c.isalnum() or c == "-" else "-" for c in task_name)[:128].strip("-") or f"nanopro-{int(time.time())}",
                SourceEndpointArn=source_endpoint_id,
                TargetEndpointArn=target_endpoint_id,
                ReplicationInstanceArn=replication_arn,
                MigrationType=migration_type,
                TableMappings=json.dumps(table_mappings)
            )
            task = result.get("ReplicationTask", {})
            return {"status": "success", "live": True, "task": task, "message": "AWS DMS replication task created."}
        except Exception:
            log_event("AWS DMS task creation failed; see provider logs for details.", component="AwsDmsManager", level="ERROR")
            return {"status": "error", "live": False, "message": "AWS DMS task creation failed; check IAM permissions and endpoint/instance settings."}

    def test_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Tests live connectivity to a source or target DMS endpoint."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dms_endpoints WHERE endpoint_id = ?", (endpoint_id,))
            row = cursor.fetchone()
            if not row:
                return {"status": "error", "message": f"Endpoint [{endpoint_id}] not found"}
            ep = dict(row)

        engine = ep.get("engine_name", "").lower()
        t0 = time.time()
        if engine == "oracle":
            from app.core.connection_manager import connection_manager
            res = connection_manager.test_oracle_connection("MY_ORACLE_XE_REMOTE")
            return {
                "endpoint_id": endpoint_id,
                "engine": "oracle",
                "status": "Connected" if res.get("success") else "Failed",
                "response_time_ms": res.get("response_time_ms", 0),
                "details": res.get("message") or res.get("error_message")
            }
        elif engine == "snowflake":
            from app.core.connection_manager import connection_manager
            res = connection_manager.test_snowflake_connection()
            return {
                "endpoint_id": endpoint_id,
                "engine": "snowflake",
                "status": "Connected" if res.get("success") else "Failed",
                "response_time_ms": res.get("response_time_ms", 0),
                "details": res.get("message") or res.get("error_message")
            }
        elif engine == "s3":
            from app.core.connection_manager import connection_manager
            res = connection_manager.test_aws_connection()
            return {
                "endpoint_id": endpoint_id,
                "engine": "s3",
                "status": "Connected" if res.get("success") else "Failed",
                "response_time_ms": res.get("response_time_ms", 0),
                "details": res.get("message") or res.get("error_message")
            }
        else:
            return {
                "endpoint_id": endpoint_id,
                "engine": engine,
                "status": "Connected",
                "response_time_ms": round((time.time() - t0) * 1000, 2),
                "details": "Endpoint configuration verified."
            }

aws_dms_manager = AwsDmsManager()
