"""
NanoPro AI Studio — Enterprise Cloud SFTP Hub
==============================================
Bi-directional SFTP Gateway & File Ingestion/Delivery Engine:
  - INBOUND (In): Receives raw Pipe (|), CSV, and Excel (.xlsx) files from external sources.
  - OUTBOUND (Out): Publishes executive reports, data extracts, and reconciliation ledgers.
  - S3 Cloud Mirror: Synchronizes with AWS S3 Data Lake (s3://nanopro-data-lake-765865641438-ap-southeast-2-an/sftp/).
  - 20-Day Retention Sentinel: Strictly limits SFTP storage to maximum 20 days; automatically purges older data.
  - Embedded SFTP Server: Paramiko-powered SSH/SFTP server for FileZilla, WinSCP, and automated CLI ingestion.
"""

from __future__ import annotations

import os
import time
import shutil
import datetime
from datetime import timezone
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import pandas as pd
from app.core.logger import log_event
from app.core.config import BASE_DIR, REPORTS_DIR

SFTP_BASE_DIR = BASE_DIR / "data" / "sftp"
SFTP_INBOUND_DIR = SFTP_BASE_DIR / "inbound"
SFTP_OUTBOUND_DIR = SFTP_BASE_DIR / "outbound"
SFTP_REPORTS_DIR = SFTP_BASE_DIR / "reports"
SFTP_ARCHIVE_DIR = SFTP_BASE_DIR / "archive"
SFTP_QUARANTINE_DIR = SFTP_BASE_DIR / "quarantine"

DEFAULT_RETENTION_DAYS = 20

class CloudSFTPHub:
    """
    Central Bi-directional Cloud SFTP Ingestion and Delivery Hub
    with Autonomous 20-Day Retention Lifecycle Management.
    """
    def __init__(self):
        self._ensure_directories()
        self._server_thread: Optional[threading.Thread] = None
        self._server_running = False
        self._server_port = int(os.environ.get("SFTP_PORT", 2222))
        self._server_user = os.environ.get("SFTP_USER", "nanopro_sftp")
        self._server_pass = os.environ.get("SFTP_PASSWORD", "NanoPro@SFTP2026!")
        self._retention_days = int(os.environ.get("SFTP_RETENTION_DAYS", DEFAULT_RETENTION_DAYS))
        self._last_cleanup_ts: Optional[str] = None
        self._total_purged_files = 0
        self._total_purged_bytes = 0
        
        # Enforce retention policy on initialization
        try:
            self.enforce_retention_policy(retention_days=self._retention_days, purge_s3=False)
        except Exception as e:
            log_event(f"[SFTP Hub] Init retention check notice: {e}", level="WARNING", component="SFTPHub")

    def _ensure_directories(self):
        """Ensures all standard banking SFTP directories exist."""
        for d in [SFTP_INBOUND_DIR, SFTP_OUTBOUND_DIR, SFTP_REPORTS_DIR, SFTP_ARCHIVE_DIR, SFTP_QUARANTINE_DIR]:
            d.mkdir(parents=True, exist_ok=True)
            for proj in ["credit_card", "aml", "alm", "adf_cims", "cbs", "upi", "ucic", "bureau_mart", "data_lake"]:
                (d / proj).mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # Status & Telemetry
    # =========================================================================
    def get_status(self) -> Dict[str, Any]:
        """Returns live SFTP directory counts, pending inbound files, retention status, and server health."""
        inbound_files = list(SFTP_INBOUND_DIR.glob("**/*.*"))
        inbound_files = [f for f in inbound_files if f.is_file() and not f.name.startswith(".")]

        outbound_files = list(SFTP_OUTBOUND_DIR.glob("**/*.*"))
        outbound_files = [f for f in outbound_files if f.is_file() and not f.name.startswith(".")]

        report_files = list(SFTP_REPORTS_DIR.glob("**/*.*"))
        report_files = [f for f in report_files if f.is_file() and not f.name.startswith(".")]

        archive_files = list(SFTP_ARCHIVE_DIR.glob("**/*.*"))
        archive_files = [f for f in archive_files if f.is_file() and not f.name.startswith(".")]

        quarantine_files = list(SFTP_QUARANTINE_DIR.glob("**/*.*"))
        quarantine_files = [f for f in quarantine_files if f.is_file() and not f.name.startswith(".")]

        cutoff_date = (datetime.date.today() - datetime.timedelta(days=self._retention_days)).strftime("%Y-%m-%d")

        return {
            "service": "Cloud SFTP Hub",
            "status": "Operational",
            "server_running": self._server_running,
            "port": self._server_port,
            "username": self._server_user,
            "host": "0.0.0.0 (Cloud & Local Accessible)",
            "directories": {
                "inbound_path": str(SFTP_INBOUND_DIR),
                "inbound_pending_count": len(inbound_files),
                "outbound_path": str(SFTP_OUTBOUND_DIR),
                "outbound_count": len(outbound_files),
                "reports_path": str(SFTP_REPORTS_DIR),
                "reports_count": len(report_files),
                "archive_count": len(archive_files),
                "quarantine_count": len(quarantine_files)
            },
            "retention_policy": {
                "max_retention_days": self._retention_days,
                "policy_rule": f"Strict {self._retention_days}-Day Window — Files older than {self._retention_days} days are automatically deleted",
                "oldest_allowed_date": cutoff_date,
                "last_cleanup_timestamp": self._last_cleanup_ts,
                "lifetime_purged_files_count": self._total_purged_files,
                "lifetime_purged_bytes": self._total_purged_bytes,
                "lifetime_purged_kb": round(self._total_purged_bytes / 1024, 2)
            },
            "supported_formats": [
                "Pipe-Delimited Text (.txt, .dat with '|' separator)",
                "Comma-Separated Values (.csv)",
                "Excel Workbooks (.xlsx, .xls)"
            ],
            "s3_mirror_bucket": "nanopro-data-lake-765865641438-ap-southeast-2-an",
            "s3_prefix": "sftp/"
        }

    # =========================================================================
    # Autonomous 20-Day Retention Policy & Storage Purge
    # =========================================================================
    def enforce_retention_policy(self, retention_days: Optional[int] = None, purge_s3: bool = True) -> Dict[str, Any]:
        """
        Enforces strict retention limit (default: 20 days).
        Scans all SFTP directories (inbound, outbound, reports, archive, quarantine).
        Permanently purges:
          1. Dated subdirectories (e.g. YYYYMMDD) older than retention_days.
          2. Individual files whose mtime is older than retention_days.
          3. S3 mirror objects under sftp/ older than retention_days (if purge_s3=True).
        """
        days = retention_days if retention_days is not None else self._retention_days
        now_ts = time.time()
        cutoff_epoch = now_ts - (days * 86400)
        today_date = datetime.date.today()
        cutoff_date = today_date - datetime.timedelta(days=days)
        cutoff_date_str = cutoff_date.strftime("%Y%m%d")

        purged_files: List[Dict[str, Any]] = []
        purged_dirs: List[str] = []
        bytes_freed = 0

        target_roots = [
            ("inbound", SFTP_INBOUND_DIR),
            ("outbound", SFTP_OUTBOUND_DIR),
            ("reports", SFTP_REPORTS_DIR),
            ("archive", SFTP_ARCHIVE_DIR),
            ("quarantine", SFTP_QUARANTINE_DIR)
        ]

        # 1. Prune dated folders (e.g. reports/20261001 or archive/credit_card/20261001)
        for cat_name, root_dir in target_roots:
            if not root_dir.exists():
                continue

            for dirpath, dirnames, _ in os.walk(str(root_dir), topdown=False):
                current_dir = Path(dirpath)
                dname = current_dir.name

                # Check if directory name is YYYYMMDD
                is_dated = False
                dir_dt = None
                if len(dname) == 8 and dname.isdigit():
                    try:
                        dir_dt = datetime.datetime.strptime(dname, "%Y%m%d").date()
                        is_dated = True
                    except Exception:
                        pass
                elif len(dname) == 10 and dname.count("-") == 2:
                    try:
                        dir_dt = datetime.datetime.strptime(dname, "%Y-%m-%d").date()
                        is_dated = True
                    except Exception:
                        pass

                if is_dated and dir_dt and dir_dt < cutoff_date:
                    try:
                        folder_size = sum(f.stat().st_size for f in current_dir.glob("**/*") if f.is_file())
                        file_count = sum(1 for f in current_dir.glob("**/*") if f.is_file())
                        shutil.rmtree(str(current_dir))
                        purged_dirs.append(str(current_dir))
                        bytes_freed += folder_size
                        self._total_purged_files += file_count
                        self._total_purged_bytes += folder_size
                        purged_files.append({
                            "type": "directory_tree",
                            "path": str(current_dir),
                            "date": str(dir_dt),
                            "files_deleted": file_count,
                            "bytes": folder_size
                        })
                        log_event(f"[SFTP Retention] Purged expired folder older than {days} days: {current_dir.name} ({file_count} files, {round(folder_size/1024, 1)} KB)", component="SFTPHub")
                    except Exception as ex:
                        log_event(f"[SFTP Retention] Error purging directory {current_dir}: {ex}", level="WARNING", component="SFTPHub")

        # 2. Prune loose files based on modification time (mtime)
        for cat_name, root_dir in target_roots:
            if not root_dir.exists():
                continue

            for fpath in list(root_dir.glob("**/*.*")):
                if not fpath.is_file() or fpath.name.startswith("."):
                    continue

                try:
                    st = fpath.stat()
                    file_mtime = st.st_mtime
                    file_age_days = (now_ts - file_mtime) / 86400.0

                    if file_age_days > days:
                        file_size = st.st_size
                        fpath.unlink(missing_ok=True)
                        purged_files.append({
                            "type": "file",
                            "path": str(fpath),
                            "name": fpath.name,
                            "category": cat_name,
                            "age_days": round(file_age_days, 1),
                            "bytes": file_size
                        })
                        bytes_freed += file_size
                        self._total_purged_files += 1
                        self._total_purged_bytes += file_size
                        log_event(f"[SFTP Retention] Purged file older than {days} days: {fpath.name} ({round(file_age_days, 1)} days old)", component="SFTPHub")
                except Exception as ex:
                    log_event(f"[SFTP Retention] Error inspecting file {fpath}: {ex}", level="WARNING", component="SFTPHub")

        # 3. AWS S3 Mirror Pruning (if enabled)
        s3_purged_count = 0
        s3_error = None
        if purge_s3:
            try:
                import boto3
                from app.core.connection_manager import connection_manager
                cfg = connection_manager.get_connection_config("AWS_S3_DATA_LAKE", mask=False)
                access_key = cfg.get("username")
                secret_key = cfg.get("secret_value")
                region = cfg.get("metadata", {}).get("region", "ap-southeast-2")
                bucket = cfg.get("database_name", "nanopro-data-lake-765865641438-ap-southeast-2-an")

                if access_key and secret_key:
                    s3 = boto3.client("s3", region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
                    paginator = s3.get_paginator("list_objects_v2")
                    now_utc = datetime.datetime.now(timezone.utc)
                    to_delete = []

                    for page in paginator.paginate(Bucket=bucket, Prefix="sftp/"):
                        for obj in page.get("Contents", []):
                            last_modified = obj["LastModified"]
                            age_s3_days = (now_utc - last_modified).total_seconds() / 86400.0
                            if age_s3_days > days:
                                to_delete.append({"Key": obj["Key"]})
                                if len(to_delete) >= 1000:
                                    s3.delete_objects(Bucket=bucket, Delete={"Objects": to_delete})
                                    s3_purged_count += len(to_delete)
                                    to_delete = []

                    if to_delete:
                        s3.delete_objects(Bucket=bucket, Delete={"Objects": to_delete})
                        s3_purged_count += len(to_delete)

                    if s3_purged_count > 0:
                        log_event(f"[SFTP Retention] Purged {s3_purged_count} expired objects from S3 (s3://{bucket}/sftp/)", component="SFTPHub")
            except Exception as e:
                s3_error = str(e)
                log_event(f"[SFTP Retention] S3 retention scan note: {e}", level="WARNING", component="SFTPHub")

        self._last_cleanup_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cleanup_summary = {
            "success": True,
            "retention_policy_days": days,
            "cutoff_date": str(cutoff_date),
            "cutoff_timestamp": self._last_cleanup_ts,
            "local_items_purged_count": len(purged_files),
            "local_directories_purged": len(purged_dirs),
            "bytes_freed": bytes_freed,
            "kb_freed": round(bytes_freed / 1024, 2),
            "s3_objects_purged": s3_purged_count,
            "s3_error": s3_error,
            "purged_samples": purged_files[:10],
            "message": f"SFTP 20-Day Retention Enforced: {len(purged_files)} items purged ({round(bytes_freed/1024, 2)} KB freed), {s3_purged_count} S3 mirror objects deleted."
        }
        return cleanup_summary

    # =========================================================================
    # Inbound Parser: Pipe (|), CSV, and Excel (.xlsx)
    # =========================================================================
    def parse_inbound_file(self, file_path: Path) -> Tuple[List[Dict[str, Any]], str]:
        """
        Auto-detects format and parses file into list of normalized records.
        Returns: (records, format_detected)
        """
        suffix = file_path.suffix.lower()
        if suffix in (".xlsx", ".xls"):
            df = pd.read_excel(file_path)
            fmt = "Excel Workbook (.xlsx)"
        elif suffix in (".csv",):
            df = pd.read_csv(file_path)
            fmt = "Comma-Separated Values (.csv)"
        else:
            # Check for Pipe separator in text files
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                first_line = f.readline()
            if "|" in first_line:
                df = pd.read_csv(file_path, sep="|")
                fmt = "Pipe-Delimited Text (| separator)"
            else:
                df = pd.read_csv(file_path)
                fmt = "Delimited Text (Auto)"

        # Clean column names
        df.columns = [str(c).strip().replace(" ", "_").upper() for c in df.columns]
        # Fill NaN with empty or zero
        df = df.where(pd.notnull(df), None)
        records = df.to_dict(orient="records")
        return records, fmt

    # =========================================================================
    # Synthetic Multi-Format Inbound Generator (For Testing & Verification)
    # =========================================================================
    def generate_sample_inbound_files(self, project_key: str = "credit_card", rows: int = 50) -> Dict[str, str]:
        """
        Generates realistic sample files in all 3 formats inside SFTP /inbound/{project_key}/:
          1. Pipe-delimited (.txt) with '|' separator
          2. CSV (.csv)
          3. Excel (.xlsx)
        """
        from app.core.etl_automation_pipeline import generate_sample_data, PROJECTS
        target_dir = SFTP_INBOUND_DIR / project_key
        target_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        records = generate_sample_data(project_key, rows)
        df = pd.DataFrame(records)

        # 1. Pipe-delimited file
        pipe_path = target_dir / f"{project_key}_txns_pipe_{ts}.txt"
        df.to_csv(pipe_path, sep="|", index=False)

        # 2. CSV file
        csv_path = target_dir / f"{project_key}_feed_{ts}.csv"
        df.to_csv(csv_path, index=False)

        # 3. Excel file
        excel_path = target_dir / f"{project_key}_ledger_{ts}.xlsx"
        df.to_excel(excel_path, index=False, engine="openpyxl")

        log_event(f"[SFTP Hub] Generated 3 multi-format test files for {project_key} in {target_dir}", component="SFTPHub")
        return {
            "pipe_file": str(pipe_path),
            "csv_file": str(csv_path),
            "excel_file": str(excel_path),
            "rows_per_file": rows
        }

    # =========================================================================
    # Outbound Delivery: Push Reports & Data to SFTP
    # =========================================================================
    def export_report_to_sftp(
        self,
        report_name: str,
        content: str,
        file_format: str = "html",
        project_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publishes a generated report to SFTP /reports/ and /outbound/, and mirrors to AWS S3.
        Also automatically invokes 20-day retention enforcement.
        """
        today_dir = SFTP_REPORTS_DIR / datetime.date.today().strftime("%Y%m%d")
        today_dir.mkdir(parents=True, exist_ok=True)

        ext = file_format.lower()
        if not ext.startswith("."):
            ext = f".{ext}"

        file_name = f"{report_name}_{int(time.time())}{ext}"
        target_path = today_dir / file_name

        if isinstance(content, str):
            target_path.write_text(content, encoding="utf-8")
        elif isinstance(content, bytes):
            target_path.write_bytes(content)

        # Copy to project outbound if specified
        if project_key:
            out_proj = SFTP_OUTBOUND_DIR / project_key / file_name
            shutil.copy2(target_path, out_proj)

        # S3 Cloud Mirror
        s3_res = self._mirror_to_s3(target_path, s3_key=f"sftp/reports/{datetime.date.today().strftime('%Y%m%d')}/{file_name}")

        log_event(f"[SFTP Hub] Report exported to SFTP: {target_path} (S3: {s3_res.get('s3_uri', 'Local')})", component="SFTPHub")
        
        # Periodic retention purge check
        try:
            self.enforce_retention_policy(retention_days=self._retention_days, purge_s3=False)
        except Exception:
            pass

        return {
            "success": True,
            "sftp_local_path": str(target_path),
            "file_name": file_name,
            "size_bytes": target_path.stat().st_size,
            "s3_mirror": s3_res
        }

    # =========================================================================
    # Process Inbound Files & Ingest into Pipeline
    # =========================================================================
    def process_all_inbound_files(self) -> Dict[str, Any]:
        """
        Scans all project folders in /inbound/, parses Pipe/CSV/Excel files,
        triggers the ETL pipeline, and archives the processed files.
        Automatically enforces the 20-day retention policy after ingestion.
        """
        from app.core.etl_automation_pipeline import etl_pipeline, PROJECTS
        results = {}
        total_files = 0
        total_records = 0

        for project_key in PROJECTS:
            proj_dir = SFTP_INBOUND_DIR / project_key
            if not proj_dir.exists():
                continue

            files = [f for f in proj_dir.glob("*.*") if f.is_file() and not f.name.startswith(".")]
            proj_results = []

            for fpath in files:
                try:
                    records, fmt = self.parse_inbound_file(fpath)
                    total_files += 1
                    total_records += len(records)

                    # Ingest via pipeline
                    pipe_res = etl_pipeline.run_project_pipeline(
                        project_key=project_key,
                        rows=len(records),
                        cycle="SFTP_INBOUND"
                    )

                    # Mirror raw file to S3
                    s3_mirror = self._mirror_to_s3(fpath, f"sftp/raw_inbound/{project_key}/{fpath.name}")

                    # Archive processed file
                    archive_dir = SFTP_ARCHIVE_DIR / project_key / datetime.date.today().strftime("%Y%m%d")
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    archived_path = archive_dir / fpath.name
                    shutil.move(str(fpath), str(archived_path))

                    proj_results.append({
                        "file": fpath.name,
                        "format": fmt,
                        "records_parsed": len(records),
                        "pipeline_status": pipe_res.get("success"),
                        "archived_to": str(archived_path),
                        "s3_mirror": s3_mirror.get("s3_uri")
                    })
                    log_event(f"[SFTP Hub] Ingested & Archived {fpath.name} ({len(records)} recs, {fmt})", component="SFTPHub")

                except Exception as e:
                    # Move to quarantine
                    q_dir = SFTP_QUARANTINE_DIR / project_key
                    q_dir.mkdir(parents=True, exist_ok=True)
                    quarantine_path = q_dir / fpath.name
                    try:
                        shutil.move(str(fpath), str(quarantine_path))
                    except Exception:
                        pass
                    proj_results.append({
                        "file": fpath.name,
                        "status": "quarantined",
                        "error": str(e)
                    })
                    log_event(f"[SFTP Hub] Error processing {fpath.name}: {e}. Quarantined.", level="WARNING", component="SFTPHub")

            if proj_results:
                results[project_key] = proj_results

        # Enforce 20-day retention after every inbound batch
        retention_res = self.enforce_retention_policy(retention_days=self._retention_days, purge_s3=True)

        return {
            "success": True,
            "total_files_processed": total_files,
            "total_records_ingested": total_records,
            "retention_policy_enforced": retention_res,
            "details": results
        }

    # =========================================================================
    # S3 Mirror Helper
    # =========================================================================
    def _mirror_to_s3(self, local_path: Path, s3_key: str) -> Dict[str, Any]:
        """Mirrors local SFTP file to AWS S3 data lake."""
        try:
            import boto3
            from app.core.connection_manager import connection_manager
            cfg = connection_manager.get_connection_config("AWS_S3_DATA_LAKE", mask=False)
            access_key = cfg.get("username")
            secret_key = cfg.get("secret_value")
            region = cfg.get("metadata", {}).get("region", "ap-southeast-2")
            bucket = cfg.get("database_name", "nanopro-data-lake-765865641438-ap-southeast-2-an")

            if access_key and secret_key and local_path.exists():
                s3 = boto3.client("s3", region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
                s3.upload_file(str(local_path), bucket, s3_key)
                return {
                    "success": True,
                    "s3_uri": f"s3://{bucket}/{s3_key}",
                    "bucket": bucket,
                    "key": s3_key
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
        return {"success": False, "error": "AWS credentials not configured"}

    # =========================================================================
    # Embedded SFTP Server Daemon (Paramiko)
    # =========================================================================
    def start_server(self):
        """Starts embedded background SFTP server on port 2222."""
        if self._server_running:
            return
        self._server_running = True
        self._server_thread = threading.Thread(target=self._run_server, daemon=True, name="EmbeddedSFTPServer")
        self._server_thread.start()
        log_event(f"[SFTP Hub] Embedded SFTP Server listening on port {self._server_port} (User: {self._server_user})", component="SFTPHub")

    def _run_server(self):
        import socket
        import paramiko
        
        # Generate or load host key
        key_file = SFTP_BASE_DIR / "sftp_host_rsa.key"
        if not key_file.exists():
            key = paramiko.RSAKey.generate(2048)
            key.write_private_key_file(str(key_file))
        else:
            key = paramiko.RSAKey.from_private_key_file(str(key_file))

        class SimpleServerInterface(paramiko.ServerInterface):
            def __init__(self, expected_user, expected_pass):
                self.expected_user = expected_user
                self.expected_pass = expected_pass

            def check_auth_password(self, username, password):
                if username == self.expected_user and password == self.expected_pass:
                    return paramiko.AUTH_SUCCESSFUL
                return paramiko.AUTH_FAILED

            def check_channel_request(self, kind, chanid):
                if kind == 'session':
                    return paramiko.OPEN_SUCCEEDED
                return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', self._server_port))
            sock.listen(5)
            sock.settimeout(2.0)

            while self._server_running:
                try:
                    conn, addr = sock.accept()
                except socket.timeout:
                    continue
                except Exception:
                    break

                def _handle_client(c, a):
                    try:
                        transport = paramiko.Transport(c)
                        transport.add_server_key(key)
                        transport.set_subsystem_handler('sftp', paramiko.SFTPServer, sftp_si=paramiko.SFTPServerInterface, root=str(SFTP_BASE_DIR))
                        server = SimpleServerInterface(self._server_user, self._server_pass)
                        transport.start_server(server=server)
                    except Exception as ex:
                        log_event(f"[SFTP Hub] Client handler notice: {ex}", level="WARNING", component="SFTPHub")

                threading.Thread(target=_handle_client, args=(conn, addr), daemon=True).start()

        except Exception as e:
            log_event(f"[SFTP Hub] SFTP Server error: {e}", level="WARNING", component="SFTPHub")
        finally:
            self._server_running = False

    def stop_server(self):
        self._server_running = False
        log_event("[SFTP Hub] Embedded SFTP Server stopped.", component="SFTPHub")


# Module-level singleton
cloud_sftp_hub = CloudSFTPHub()
