"""
Mangesh Nano Pro AI Studio - Core Task Scheduler & Automation Center
Windows Task Scheduler Alternative with AI-Powered Job Orchestration
Supports:
- Python scripts & script files (.py)
- SQL queries & SQL script files (.sql) on Oracle XE, Snowflake, SQLite
- Windows Batch files (.bat) & PowerShell scripts (.ps1)
- Scheduled Studio application jobs
- Granular recurrence: Once, Minutes interval, Hourly, Daily, Weekly, Monthly, Selected Weekdays, Cron expressions
- Full execution tracking: stdout, stderr, exit codes, durations, bounded retries, timeouts, and restart recovery
"""

import os
import sys
import time
import json
import subprocess
import threading
from datetime import datetime, timedelta, timezone
from calendar import monthrange
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.core.logger import log_event
from app.core.database import db
from app.core.config import BASE_DIR

class AutomationScheduler:
    def __init__(self):
        self.is_running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._running_jobs: Dict[str, Dict[str, Any]] = {}
        self._disable_legacy_demo_tasks()
        self._ensure_pipeline_tasks_seeded()
        self._reconcile_cloud_profile()

    CLOUD_LOCAL_LANE_TASKS = {
        # All banking data pipelines (BOD, SOD, T-1, EOD, S3 Mirror) are 100% Cloud-Native
        # and execute 24/7 autonomously on Render Cloud without requiring the user's laptop.
    }

    def _reconcile_cloud_profile(self):
        """On the free cloud host, keep only schedules that do not depend on the laptop lane."""
        try:
            from app.core.runtime_profile import cloud_safe_mode
            if not cloud_safe_mode():
                return
            opt_in = os.environ.get("NANOPRO_CLOUD_PIPELINE_JOBS", "0").strip().lower() in ("1", "true", "yes", "on")
            blocked = dict(self.CLOUD_LOCAL_LANE_TASKS)
            if opt_in:
                blocked = {name: reason for name, reason in blocked.items() if "PIPELINE" not in name}
            for task in db.list_automation_tasks():
                name = task.get("name")
                if name in blocked and task.get("is_enabled"):
                    db.update_automation_task(task["id"], {
                        "is_enabled": 0,
                        "status": "Disabled",
                        "last_status": "Cloud profile: local lane only",
                        "next_run_at": "",
                        "description": f"{task.get('description') or ''} [Cloud-safe: {blocked[name]}]",
                    })
                    log_event(
                        f"Cloud profile disabled [{name}]: {blocked[name]}.",
                        component="AutomationScheduler",
                    )
        except Exception as exc:
            log_event(f"Cloud schedule reconciliation failed: {exc}", level="WARNING", component="AutomationScheduler")

    def _disable_legacy_demo_tasks(self):
        """Disable only the two known auto-seeded inline scripts that print mock transfer success."""
        demo_markers = {
            "Oracle XE Staging Buffer Sync": "248 records extracted.",
            "Weekly Studio Database Vacuum & Ledger Backup": "32 tables verified.",
        }
        try:
            for task in db.list_automation_tasks():
                marker = demo_markers.get(task.get("name"))
                if task.get("is_enabled") and task.get("task_type") == "python" and marker and marker in task.get("script_content", ""):
                    db.update_automation_task(task["id"], {
                        "is_enabled": 0, "status": "Disabled", "last_status": "Blocked: demo placeholder",
                        "next_run_at": "",
                        "description": "Disabled automatically: this legacy example only printed mock success and performed no data transfer. Configure the real Oracle/DMS/S3/Snowflake pipeline instead."
                    })
                    log_event(f"Disabled legacy mock scheduler task [{task['name']}].", level="WARNING", component="AutomationScheduler")
        except Exception as exc:
            log_event(f"Could not disable legacy demo jobs: {exc}", level="WARNING", component="AutomationScheduler")

    def _ensure_pipeline_tasks_seeded(self):
        """Register the direct Oracle→S3 schedule; keep DMS as an optional mode."""
        try:
            tasks = db.list_automation_tasks()
            existing = {task.get("name") for task in tasks}
            legacy_to_s3 = {
                "ORACLE_DMS_SNOWFLAKE_PIPELINE_DAILY": "ORACLE_S3_SNOWFLAKE_PIPELINE_DAILY",
                "ORACLE_DMS_SNOWFLAKE_PIPELINE_FORTNIGHTLY": "ORACLE_S3_SNOWFLAKE_PIPELINE_FORTNIGHTLY",
                "ORACLE_DMS_SNOWFLAKE_PIPELINE_MONTHLY": "ORACLE_S3_SNOWFLAKE_PIPELINE_MONTHLY",
            }
            for task in tasks:
                old_name = task.get("name")
                new_name = legacy_to_s3.get(old_name)
                if new_name and new_name not in existing:
                    db.update_automation_task(task["id"], {
                        "name": new_name,
                        "description": "Daily Snowflake T-1/live comparison report at 10:00 IST; ingestion runs in the separate 15-minute Oracle→S3 job.",
                    })
                    existing.discard(old_name)
                    existing.add(new_name)
            schedules = [
                ("BOD_PIPELINE_CYCLE", "daily", "06:00", "Beginning of Day (06:00 AM IST) — System validation & 91-Table Full Load into AWS S3, Snowflake L0-L1-L2, and DuckDB Gold Marts.", True),
                ("SOD_PIPELINE_CYCLE", "daily", "08:00", "Start of Day (08:00 AM IST) — Account limits, opening positions, and intraday delta synchronization.", True),
                ("DAILY_T1_INCREMENTAL_PIPELINE", "daily", "10:00", "Daily T-1 Incremental Pipeline — Watermark delta transaction ingestion across all 9 Banking Projects.", True),
                ("EOD_PIPELINE_CYCLE", "daily", "18:00", "End of Day (06:00 PM IST) — Daily reconciliation, trial balance verification, and multi-channel executive reports.", True),
                ("SFTP_INBOUND_AUTO_INGEST", "minutes", "15", "Autonomous Cloud SFTP Inbound Poll — Scans /inbound/ for Pipe (|), CSV, and Excel (.xlsx) feeds and loads pipeline.", True),
                ("SFTP_20DAY_RETENTION_PURGE", "daily", "00:00", "Autonomous 20-Day Storage Limit Sentinel — Automatically purges SFTP files, folders, and S3 mirror objects older than 20 days.", True),
                ("STORAGE_RETENTION_OPTIMIZER", "daily", "01:30", "Disk Pressure Guard — Prunes reports/logs/caches older than 14 days, keeps only the latest 3 backups, checkpoints and vacuums SQLite, and re-enforces SFTP retention.", True),
                ("DUCKDB_S3_CLOUD_BACKUP", "daily", "23:30", "Cloud Lakehouse Durability Sync — Mirrors local DuckDB Gold Marts to AWS S3 (s3://nanopro-data-lake-765865641438-ap-southeast-2-an/lakehouse/gold_marts.duckdb).", True),
                ("DAG_AML_PIPELINE", "daily", "20:00", "Airflow DAG — Anti-Money Laundering (AML) T-1 Ingestion, L1 Quality Gate, STR Curated Marts & EOD Report.", True),
                ("DAG_ALM_PIPELINE", "daily", "20:00", "Airflow DAG — Asset Liability Management (ALM) Liquidity Gap & Interest Rate Sensitivity Analysis.", True),
                ("DAG_CREDIT_CARD_PIPELINE", "daily", "20:00", "Airflow DAG — Credit Card Delinquency (30/60/90 DPD), Revolving Balances & Chargeback Reconciliation.", True),
                ("DAG_BUREAU_MART_PIPELINE", "daily", "08:30", "Airflow DAG — Bureau Mart (CIBIL/Experian) Credit Score Migration & Default Risk Rating.", True),
                ("DAG_ADF_CIMS_PIPELINE", "daily", "20:00", "Airflow DAG — RBI Automated Data Flow (ADF CIMS) Basel-III & CRR/SLR Regulatory Returns.", True),
                ("DAG_UPI_SETTLEMENT_PIPELINE", "daily", "08:30", "Airflow DAG — UPI Real-Time NPCI Switch Settlement & Dispute Clearing.", True),
                ("DAG_JLG_COLLECTION_PIPELINE", "daily", "20:00", "Airflow DAG — JLG/SHG Microfinance Group Collections & Portfolio at Risk (PAR) Recovery.", True),
                ("DAG_LOS_LMS_PIPELINE", "daily", "06:00", "Airflow DAG — Loan Origination (LOS) & Loan Management (LMS) NPA Provisioning & Servicing.", True),
                ("TELEGRAM_APK_DISPATCHER", "hourly", "4", "Autonomous Telegram APK Dispatcher (@mangesh_apk_bot) — Discovers and delivers verified open-source APKs with configurable quantity & interval.", False),
                ("ORACLE_S3_SNOWFLAKE_PIPELINE_INCREMENTAL", "minutes", "15", "Oracle watermark incremental polling every 15 minutes → S3 → Snowflake L0/L1/L2.", False),
                ("ORACLE_S3_SNOWFLAKE_PIPELINE_DAILY", "daily", "10:00", "Snowflake daily T-1/live comparison report at 10:00 IST.", False),
            ]
            for name, kind, expression, description, enabled in schedules:
                if name in existing:
                    continue
                self.create_task({
                    "name": name,
                    "description": description,
                    "task_type": "scheduled_job", "schedule_type": kind,
                    "recurrence_expr": expression, "timezone": "Asia/Kolkata",
                    "timeout_sec": 7200,
                    "retry_policy": {"max_retries": 1, "retry_interval_sec": 300},
                    "notification_pref": {"email": True, "telegram": True},
                    "is_enabled": enabled,
                })
            if os.environ.get("RENDER") and not any(str(name).lower() == "render_daily_whatsapp_report" for name in existing):
                self.create_task({
                    "name": "RENDER_DAILY_WHATSAPP_REPORT",
                    "description": "Daily 10:00 IST Render details via text or the approved NanoPro Utility template; one attempt, no generic ping or Telegram fallback.",
                    "task_type": "scheduled_job",
                    "script_content": json.dumps({"recipient": "+918433755448"}),
                    "schedule_type": "daily",
                    "recurrence_expr": "10:00",
                    "timezone": "Asia/Kolkata",
                    "timeout_sec": 90,
                    "retry_policy": {"max_retries": 0, "retry_interval_sec": 60},
                    "notification_pref": {"email": False, "telegram": False, "whatsapp": False},
                    "is_enabled": True,
                    "is_paused": False,
                })
        except Exception as exc:
            log_event(f"Could not register pipeline schedules: {exc}", level="WARNING", component="AutomationScheduler")

    def calculate_next_run(self, schedule_type: str, recurrence_expr: str, from_dt: Optional[datetime] = None, timezone_name: str = "Asia/Kolkata") -> str:
        """Calculate calendar-aware local timestamps in the task's configured timezone."""
        try:
            zone = ZoneInfo(timezone_name or "Asia/Kolkata")
        except ZoneInfoNotFoundError:
            zone = ZoneInfo("Asia/Kolkata")
        base = from_dt or datetime.now(zone)
        base = base.replace(tzinfo=zone) if base.tzinfo is None else base.astimezone(zone)
        kind = (schedule_type or "daily").lower()
        if kind == "once":
            return ""
        if kind == "minutes":
            mins = int(recurrence_expr) if recurrence_expr and recurrence_expr.isdigit() else 15
            return (base + timedelta(minutes=mins)).strftime("%Y-%m-%d %H:%M:%S")
        if kind == "hourly":
            return (base + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        if kind == "daily":
            try:
                hh, mm = map(int, (recurrence_expr or "08:00").split(":")[:2])
            except ValueError:
                hh, mm = 8, 0
            candidate = base.replace(hour=hh, minute=mm, second=0, microsecond=0)
            if candidate <= base:
                candidate += timedelta(days=1)
            return candidate.strftime("%Y-%m-%d %H:%M:%S")
        if kind == "weekly":
            parts = (recurrence_expr or "").upper().split("@", 1)
            days = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4, "SAT": 5, "SUN": 6}
            day = days.get(parts[0][:3], base.weekday())
            try:
                hh, mm = map(int, (parts[1] if len(parts) > 1 else base.strftime("%H:%M")).split(":"))
            except ValueError:
                hh, mm = base.hour, base.minute
            candidate = (base + timedelta(days=(day - base.weekday()) % 7)).replace(hour=hh, minute=mm, second=0, microsecond=0)
            if candidate <= base:
                candidate += timedelta(days=7)
            return candidate.strftime("%Y-%m-%d %H:%M:%S")
        if kind in {"fortnightly", "biweekly", "every_14_days"}:
            try:
                hh, mm = map(int, recurrence_expr.split(":")[:2]) if recurrence_expr and ":" in recurrence_expr else (base.hour, base.minute)
            except ValueError:
                hh, mm = base.hour, base.minute
            return (base + timedelta(days=14)).replace(hour=hh, minute=mm, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
        if kind == "monthly":
            parts = (recurrence_expr or "").split("@", 1)
            try:
                day = int(parts[0]) if len(parts) == 2 else base.day
            except ValueError:
                day = base.day
            try:
                time_expr = parts[1] if len(parts) == 2 else recurrence_expr
                hh, mm = map(int, time_expr.split(":")[:2]) if time_expr and ":" in time_expr else (base.hour, base.minute)
            except ValueError:
                hh, mm = base.hour, base.minute
            year, month = (base.year, base.month)
            while True:
                month_last_day = monthrange(year, month)[1]
                candidate = base.replace(year=year, month=month, day=min(max(day, 1), month_last_day), hour=hh, minute=mm, second=0, microsecond=0)
                if candidate > base:
                    return candidate.strftime("%Y-%m-%d %H:%M:%S")
                year, month = (year + 1, 1) if month == 12 else (year, month + 1)
        if kind == "cron":
            return (base + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        return (base + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new persistent scheduled automation task."""
        schedule_type = task_data.get("schedule_type", "daily")
        recurrence_expr = task_data.get("recurrence_expr", "")
        start_time = task_data.get("start_time") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate next_run_at
        timezone_name = task_data.get("timezone", "Asia/Kolkata")
        next_run_at = task_data.get("next_run_at") or self.calculate_next_run(schedule_type, recurrence_expr, timezone_name=timezone_name)

        task_payload = {
            "name": task_data.get("name", "New Automation Job"),
            "description": task_data.get("description", ""),
            "task_type": task_data.get("task_type", "python").lower(),
            "script_content": task_data.get("script_content", ""),
            "file_path": task_data.get("file_path", ""),
            "db_connection": task_data.get("db_connection", ""),
            "schedule_type": schedule_type,
            "recurrence_expr": recurrence_expr,
            "start_time": start_time,
            "end_time": task_data.get("end_time", ""),
            "timezone": timezone_name,
            "timeout_sec": int(task_data.get("timeout_sec", 300)),
            "retry_policy": task_data.get("retry_policy", {"max_retries": 2, "retry_interval_sec": 60}),
            "working_dir": task_data.get("working_dir", ""),
            "env_vars": task_data.get("env_vars", {}),
            "notification_pref": task_data.get("notification_pref", {"email": True, "telegram": True}),
            "is_enabled": bool(task_data.get("is_enabled", True)),
            "is_paused": bool(task_data.get("is_paused", False)),
            "status": "Ready",
            "next_run_at": next_run_at,
            "last_run_at": "",
            "last_status": "Not Run"
        }
        tid = db.create_automation_task(task_payload)
        task_payload["id"] = tid
        log_event(f"Scheduled automation task created [{tid}]: {task_payload['name']} ({task_payload['task_type']})", component="AutomationScheduler")
        return task_payload

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Updates an existing automation task."""
        task = db.get_automation_task(task_id)
        if not task:
            return False
        
        if "schedule_type" in updates or "recurrence_expr" in updates or "timezone" in updates:
            stype = updates.get("schedule_type", task.get("schedule_type", "daily"))
            rexpr = updates.get("recurrence_expr", task.get("recurrence_expr", ""))
            updates["next_run_at"] = self.calculate_next_run(stype, rexpr, timezone_name=updates.get("timezone", task.get("timezone", "Asia/Kolkata")))

        ok = db.update_automation_task(task_id, updates)
        log_event(f"Scheduled automation task updated [{task_id}]", component="AutomationScheduler")
        return ok

    def delete_task(self, task_id: str) -> bool:
        """Permanently removes a task and its execution history."""
        ok = db.delete_automation_task(task_id)
        log_event(f"Deleted scheduled automation task [{task_id}]", component="AutomationScheduler")
        return ok

    def duplicate_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Duplicates an existing task definition."""
        task = db.get_automation_task(task_id)
        if not task:
            return None
        clone_data = dict(task)
        clone_data.pop("id", None)
        clone_data["name"] = f"Copy of {task['name']}"
        clone_data["created_at"] = time.time()
        return self.create_task(clone_data)

    def pause_task(self, task_id: str) -> bool:
        return self.update_task(task_id, {"is_paused": 1, "status": "Paused"})

    def resume_task(self, task_id: str) -> bool:
        return self.update_task(task_id, {"is_paused": 0, "status": "Ready"})

    def toggle_task(self, task_id: str, is_enabled: bool) -> bool:
        status = "Ready" if is_enabled else "Disabled"
        return self.update_task(task_id, {"is_enabled": 1 if is_enabled else 0, "status": status})

    def execute_task_now(self, task_id: str, trigger_type: str = "Manual") -> Dict[str, Any]:
        """
        Executes a task immediately in a separate thread.
        Captures stdout, stderr, execution duration, and exit code.
        """
        task = db.get_automation_task(task_id)
        if not task:
            return {"status": "error", "error": f"Task [{task_id}] not found"}

        with self._lock:
            if task_id in self._running_jobs:
                return {"status": "already_running", "message": f"Task [{task_id}] is currently executing."}
            self._running_jobs[task_id] = {"start_time": time.time()}

        # Spawn background runner thread
        t = threading.Thread(target=self._run_job_worker, args=(task, trigger_type), daemon=True)
        t.start()
        return {"status": "started", "task_id": task_id, "task_name": task["name"], "trigger_type": trigger_type}

    def _run_job_worker(self, task: Dict[str, Any], trigger_type: str):
        """Worker thread executing the real Python, SQL, BAT, or App job."""
        task_id = task["id"]
        task_name = task["name"]
        task_type = task.get("task_type", "python").lower()
        timeout_sec = task.get("timeout_sec", 300)
        try:
            start_ts = datetime.now(ZoneInfo(task.get("timezone") or "Asia/Kolkata"))
        except ZoneInfoNotFoundError:
            start_ts = datetime.now(ZoneInfo("Asia/Kolkata"))
        start_time_str = start_ts.strftime("%Y-%m-%d %H:%M:%S")

        db.update_automation_task(task_id, {"status": "Running", "last_run_at": start_time_str})

        run_id = db.record_task_run({
            "task_id": task_id,
            "task_name": task_name,
            "trigger_type": trigger_type,
            "start_time": start_time_str,
            "status": "Running"
        })

        stdout = ""
        stderr = ""
        exit_code = 0
        final_status = "Success"
        error_details = ""
        t0 = time.time()

        try:
            if task_type == "python":
                stdout, stderr, exit_code = self._execute_python(task, timeout_sec)
            elif task_type == "sql":
                stdout, stderr, exit_code = self._execute_sql(task)
            elif task_type in ["bat", "batch", "powershell", "ps1"]:
                stdout, stderr, exit_code = self._execute_script_file(task, timeout_sec)
            elif task_type == "scheduled_job":
                stdout, stderr, exit_code = self._execute_app_job(task)
            else:
                stdout, stderr, exit_code = f"Unknown task type: {task_type}", "", 1

            if exit_code != 0:
                final_status = "Failed"
                error_details = stderr or f"Process exited with non-zero return code: {exit_code}"

        except subprocess.TimeoutExpired:
            final_status = "Timeout"
            exit_code = 124
            error_details = f"Task execution exceeded timeout limit of {timeout_sec}s."
            stderr = error_details
        except Exception as e:
            final_status = "Failed"
            exit_code = 1
            error_details = str(e)
            stderr = str(e)
        finally:
            duration = round(time.time() - t0, 3)
            try:
                end_time_str = datetime.now(ZoneInfo(task.get("timezone") or "Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")
            except ZoneInfoNotFoundError:
                end_time_str = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")

            # Update run history
            db.update_task_run(run_id, {
                "end_time": end_time_str,
                "duration_sec": duration,
                "status": final_status,
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "error_details": error_details
            })

            # Calculate next run timestamp
            next_run = self.calculate_next_run(
                task.get("schedule_type", "daily"),
                task.get("recurrence_expr", ""),
                timezone_name=task.get("timezone", "Asia/Kolkata")
            )

            # Update parent task state
            task_status = "Ready" if task.get("is_enabled", True) and not task.get("is_paused", False) else task.get("status", "Ready")
            db.update_automation_task(task_id, {
                "status": task_status,
                "last_status": final_status,
                "next_run_at": next_run
            })

            with self._lock:
                self._running_jobs.pop(task_id, None)

            log_event(f"Task [{task_name}] finished with status [{final_status}] in {duration}s", component="AutomationScheduler")

    def _execute_python(self, task: Dict[str, Any], timeout_sec: int) -> (str, str, int):
        """Executes a Python script string or local file."""
        script_content = task.get("script_content", "")
        file_path = task.get("file_path", "")

        if file_path and os.path.isfile(file_path):
            cmd = [sys.executable, file_path]
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
            return p.stdout, p.stderr, p.returncode

        if script_content.strip():
            cmd = [sys.executable, "-c", script_content]
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
            return p.stdout, p.stderr, p.returncode

        return "", "No valid Python code or file path provided.", 1

    def _execute_sql(self, task: Dict[str, Any]) -> (str, str, int):
        """Executes an approved SQL query on configured DB target."""
        query = task.get("script_content", "").strip()
        db_conn = task.get("db_connection", "STUDIO_MEMORY_DB")

        if not query:
            return "", "Empty SQL query provided.", 1

        # Check dangerous SQL
        q_upper = query.upper()
        if any(w in q_upper for w in ["DROP DATABASE", "FORMAT DISK"]):
            return "", "Execution rejected: Destructive database action prohibited.", 1

        try:
            from app.core.connection_manager import connection_manager
            t0 = time.time()
            if db_conn == "STUDIO_MEMORY_DB" or not db_conn:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    if cursor.description:
                        cols = [d[0] for d in cursor.description]
                        rows = cursor.fetchall()[:100]
                        elapsed = round((time.time() - t0)*1000, 2)
                        output = f"Executed on SQLite ({db_conn}) in {elapsed} ms\nColumns: {cols}\nRows returned: {len(rows)}\nSample:\n"
                        for r in rows[:5]:
                            output += f"{dict(r)}\n"
                        return output, "", 0
                    else:
                        conn.commit()
                        return f"Query executed successfully on SQLite ({db_conn}). Rows affected: {cursor.rowcount}", "", 0
            else:
                # Target external database (Snowflake / Oracle XE)
                res = connection_manager.execute_query(db_conn, query)
                if res.get("status") == "success":
                    cols = res.get("columns", [])
                    data = res.get("data", [])
                    output = (
                        f"Target: {db_conn}\n"
                        f"Execution Time: {res.get('execution_time_ms', 0)} ms\n"
                        f"Columns: {cols}\n"
                        f"Total Rows: {len(data)}\n"
                    )
                    return output, "", 0
                else:
                    return "", f"SQL Execution Failed on {db_conn}: {res.get('error')}", 1
        except Exception as e:
            return "", f"SQL Exception: {e}", 1

    def _execute_script_file(self, task: Dict[str, Any], timeout_sec: int) -> (str, str, int):
        """Controlled execution of batch file or powershell script."""
        file_path = task.get("file_path", "")
        script_content = task.get("script_content", "")

        return "", "Batch/PowerShell execution is not implemented; refusing to report a simulated success.", 1

    def _execute_app_job(self, task: Dict[str, Any]) -> (str, str, int):
        """Executes native Nano Pro studio application maintenance jobs."""
        name = task.get("name", "").lower()
        
        if name == "render_daily_whatsapp_report":
            from app.core.render_status import send_daily_render_report

            recipient = json.loads(task.get("script_content") or "{}").get("recipient", "+918433755448")
            result = send_daily_render_report(recipient)
            return json.dumps(result), "", 0 if result.get("status") in {"accepted", "pending", "sending", "skipped"} else 1

        # Enterprise Cloud Lakehouse & SFTP Scheduled Pipelines
        if name in ("bod_pipeline_cycle", "bod"):
            from app.core.etl_automation_pipeline import etl_pipeline
            res = etl_pipeline.run_bod_cycle()
            return json.dumps(res, default=str), "", 0 if res.get("success") else 1
        elif name in ("sod_pipeline_cycle", "sod"):
            from app.core.etl_automation_pipeline import etl_pipeline
            res = etl_pipeline.run_sod_cycle()
            return json.dumps(res, default=str), "", 0 if res.get("success") else 1
        elif name in ("daily_t1_incremental_pipeline", "incremental"):
            from app.core.etl_automation_pipeline import etl_pipeline
            res = etl_pipeline.run_incremental_cycle()
            return json.dumps(res, default=str), "", 0 if res.get("success") else 1
        elif name in ("eod_pipeline_cycle", "eod"):
            from app.core.etl_automation_pipeline import etl_pipeline
            res = etl_pipeline.run_eod_cycle()
            return json.dumps(res, default=str), "", 0 if res.get("success") else 1
        elif name in ("sftp_inbound_auto_ingest", "sftp_ingest"):
            from app.core.cloud_sftp_hub import cloud_sftp_hub
            res = cloud_sftp_hub.process_all_inbound_files()
            return json.dumps(res, default=str), "", 0 if res.get("success") else 1
        elif name in ("sftp_20day_retention_purge", "sftp_cleanup"):
            from app.core.cloud_sftp_hub import cloud_sftp_hub
            res = cloud_sftp_hub.enforce_retention_policy(retention_days=20, purge_s3=True)
            return json.dumps(res, default=str), "", 0 if res.get("success") else 1
        elif name in ("storage_retention_optimizer", "storage_housekeeping", "disk_cleanup"):
            from app.core.storage_inspector import storage_inspector
            res = storage_inspector.run_housekeeping()
            return json.dumps(res, default=str), "", 0 if res.get("status") == "success" else 1
        elif name in ("duckdb_s3_cloud_backup", "lakehouse_backup"):
            from app.core.etl_automation_pipeline import etl_pipeline
            res = etl_pipeline.backup_duckdb_to_s3()
            return json.dumps(res, default=str), "", 0 if res.get("success") else 1
        elif name in ("telegram_apk_dispatcher", "apk_dispatcher", "apk_bot", "apk"):
            from app.core.apk_dispatcher import discover_and_send_apks, get_apk_config
            cfg = get_apk_config()
            count = cfg.get("count", 5)
            content_str = task.get("script_content") or ""
            if content_str:
                try:
                    p = json.loads(content_str)
                    if "count" in p:
                        count = int(p["count"])
                except Exception:
                    pass
            res = discover_and_send_apks(count=count)
            return json.dumps(res, default=str), "", 0 if res.get("status") == "success" else 1
        pipeline_periods = {
            "oracle_dms_snowflake_pipeline_daily": "daily",
            "oracle_dms_snowflake_pipeline_fortnightly": "fortnightly",
            "oracle_dms_snowflake_pipeline_monthly": "monthly",
            "oracle_s3_snowflake_pipeline_daily": "daily",
            "oracle_s3_snowflake_pipeline_fortnightly": "fortnightly",
            "oracle_s3_snowflake_pipeline_monthly": "monthly",
            "oracle_s3_snowflake_pipeline_incremental": "incremental",
        }
        if name in pipeline_periods:
            from app.core.data_pipeline_runner import run_configured_pipeline
            period = pipeline_periods[name]
            result = run_configured_pipeline(
                report_period="daily" if period == "incremental" else period,
                include_ingestion=(period == "incremental"),
                include_report=(period != "incremental"),
            )
            if result.get("status") == "success":
                return json.dumps(result, default=str), "", 0
            notifications = self._notify_pipeline_failure(result)
            result["failure_notifications"] = notifications
            return "", json.dumps(result, default=str), 1
        if name == "connection_interoperability_test":
            from app.core.connection_manager import connection_manager
            res = connection_manager.test_cross_pipeline_interoperability()
            if res.get("success"):
                return f"Connection checks passed (no data transfer performed): {res.get('message', '')}", "", 0
            return "", f"Connection interoperability check failed: {res.get('message', 'one or more providers are unavailable')}", 1
        elif "backup" in name:
            from app.core.backup_manager import backup_manager
            res = backup_manager.create_full_backup()
            return f"Full Backup created: {res.get('backup_id')} ({res.get('size_bytes')} bytes)", "", 0
        else:
            return "", f"Unsupported scheduled application job: {task.get('name', 'unnamed task')}", 1

    @staticmethod
    def _notify_pipeline_failure(result: Dict[str, Any]) -> Dict[str, Any]:
        """Send run failure and RCA details through configured alert providers."""
        run_id = result.get("run_id", "unknown")
        failed = [stage for stage in result.get("stages", []) if stage.get("status") == "failed"]
        rca_lines = [
            f"- {stage.get('stage', 'unknown')}: {stage.get('error') or stage.get('delivery_status') or 'failure reported; inspect run record'}"
            for stage in failed
        ] or [f"- Preflight/configuration: {', '.join(result.get('missing_configuration', [])) or result.get('message', 'unknown cause')}" ]
        message = (
            f"NanoPro pipeline FAILURE / RCA\nRun ID: {run_id}\n"
            f"Cause: {result.get('message', 'Pipeline execution failed')}\n"
            f"Failed stages:\n" + "\n".join(rca_lines) +
            "\nAction: check NanoPro Task Scheduler run history and restore the failed provider/configuration before re-running."
        )
        outcomes = {}
        try:
            from app.core.smtp_client import smtp_client
            mail = smtp_client.send_email(recipient="nanoproaistudio@gmail.com", subject="NanoPro data pipeline failure", body=message, task_id=run_id, data_source="Oracle S3 Snowflake")
            outcomes["email"] = "sent" if mail.get("success") and "telegram" not in str(mail.get("provider", "")).lower() else "not_verified"
        except Exception:
            outcomes["email"] = "failed"
        try:
            from app.core.telegram_router import send_telegram_routed_message
            telegram = send_telegram_routed_message(category="reports", text=message)
            outcomes["telegram_rca_recipient"] = "@mangesh_reports_bot"
            outcomes["telegram_rca"] = "sent" if telegram.get("success") else "not_configured_or_failed"
        except Exception:
            outcomes["telegram_rca"] = "failed"
        try:
            from app.core.communication_center import communication_center
            whatsapp = communication_center.send_whatsapp_cloud_api(phone="918433755448", message=message)
            outcomes["whatsapp"] = "sent" if whatsapp.get("success") else "not_configured"
        except Exception:
            outcomes["whatsapp"] = "failed"
        return outcomes

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Calculates dashboard health metrics for the Task Scheduler UI."""
        tasks = db.list_automation_tasks()
        runs = db.list_task_runs(limit=100)

        total_tasks = len(tasks)
        enabled_tasks = sum(1 for t in tasks if t.get("is_enabled") and not t.get("is_paused"))
        paused_tasks = sum(1 for t in tasks if t.get("is_paused"))
        running_tasks = len(self._running_jobs)

        successful_runs = sum(1 for r in runs if r.get("status") == "Success")
        failed_runs = sum(1 for r in runs if r.get("status") == "Failed")

        # Upcoming runs
        upcoming = [
            {"id": t["id"], "name": t["name"], "next_run_at": t.get("next_run_at", ""), "task_type": t.get("task_type", "")}
            for t in tasks if t.get("is_enabled") and not t.get("is_paused") and t.get("next_run_at")
        ]
        upcoming.sort(key=lambda x: x["next_run_at"])

        recent_errors = [
            {"run_id": r["run_id"], "task_name": r["task_name"], "error": r.get("error_details") or r.get("stderr"), "time": r.get("start_time")}
            for r in runs if r.get("status") in ["Failed", "Timeout"]
        ][:5]

        return {
            "total_tasks": total_tasks,
            "enabled_tasks": enabled_tasks,
            "paused_tasks": paused_tasks,
            "running_tasks": running_tasks,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "upcoming_runs": upcoming[:5],
            "recent_errors": recent_errors,
            "last_heartbeat": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def start(self):
        """Starts background scheduler daemon."""
        if self.is_running:
            return
        try:
            stale = db.mark_interrupted_task_runs()
            if stale:
                log_event(f"Marked {stale} stale task run(s) as Interrupted after restart.", component="AutomationScheduler")
        except Exception as exc:
            log_event(f"Stale run cleanup failed: {exc}", level="WARNING", component="AutomationScheduler")
        self.is_running = True
        self._worker_thread = threading.Thread(target=self._daemon_loop, daemon=True)
        self._worker_thread.start()
        log_event("AutomationScheduler daemon started successfully.", component="AutomationScheduler")

    def stop(self):
        """Gracefully halts scheduler background thread."""
        self.is_running = False
        log_event("AutomationScheduler daemon stopped.", component="AutomationScheduler")

    def _daemon_loop(self):
        """Continuous polling loop evaluating scheduled tasks every 10 seconds."""
        while self.is_running:
            try:
                from app.core.runtime_profile import cloud_safe_mode
                from app.core.scheduler_lease import is_leader
                # The cloud lane only owns cloud-safe jobs; pipeline tasks are
                # disabled there, so it must not hold the local lane's lease.
                if not is_leader("cloud" if cloud_safe_mode() else "local"):
                    time.sleep(10)
                    continue
                from app.core.egress_guard import egress_daily_check
                egress_daily_check()
                now_utc = datetime.now(timezone.utc)
                tasks = db.list_automation_tasks()
                for task in tasks:
                    if not task.get("is_enabled") or task.get("is_paused"):
                        continue
                    next_run = task.get("next_run_at")
                    try:
                        zone = ZoneInfo(task.get("timezone") or "Asia/Kolkata")
                        due_at = datetime.strptime(next_run, "%Y-%m-%d %H:%M:%S").replace(tzinfo=zone) if next_run else None
                    except (ValueError, ZoneInfoNotFoundError):
                        due_at = None
                    if due_at and due_at.astimezone(timezone.utc) <= now_utc:
                        # Task is due for execution
                        task_id = task["id"]
                        with self._lock:
                            if task_id not in self._running_jobs:
                                # Reserve the task while still holding the lock. Otherwise each
                                # daemon poll can start another worker before the first runs.
                                self._running_jobs[task_id] = {"start_time": time.time()}
                                log_event(f"Triggering scheduled execution for task [{task['name']}]", component="AutomationScheduler")
                                worker = threading.Thread(target=self._run_job_worker, args=(task, "Scheduled"), daemon=True)
                                try:
                                    worker.start()
                                except Exception:
                                    self._running_jobs.pop(task_id, None)
                                    raise
            except Exception as e:
                log_event(f"Error in AutomationScheduler daemon loop: {e}", level="ERROR", component="AutomationScheduler")
            time.sleep(10)

automation_scheduler = AutomationScheduler()
