"""Configured Oracle → AWS DMS → S3 → Snowflake pipeline runner.

The DMS replication task owns Oracle full-load/CDC delivery to S3. NanoPro then
loads that landing data and runs explicitly configured L0/L1/L2/report SQL.
No stage is reported successful unless its provider call actually succeeds.
"""
import csv
import os
import re
import uuid
from datetime import datetime, timedelta
import calendar
from pathlib import Path
from zoneinfo import ZoneInfo

from app.core.config import REPORTS_DIR

IST = ZoneInfo("Asia/Kolkata")
MAX_EMAIL_ATTACHMENT_BYTES = 5_000_000
REPORT_RECIPIENT = "nanoproaistudio@gmail.com"
SQL_ENV = {
    "snowflake_l0": "NANOPRO_SNOWFLAKE_COPY_SQL",
    "snowflake_l1": "NANOPRO_SNOWFLAKE_L1_SQL",
    "snowflake_l2": "NANOPRO_SNOWFLAKE_L2_SQL",
    "report": "NANOPRO_SNOWFLAKE_REPORT_SQL",
}


def _masked(key, value):
    if value is None:
        return ""
    text = str(value)
    field = key.upper()
    if "EMAIL" in field and "@" in text and "." in text:
        name, domain = text.split("@", 1)
        return (name[:1] + "***@" + domain) if name else "***@" + domain
    if any(term in field for term in ("PHONE", "MOBILE", "ACCOUNT", "PAN", "AADHAAR", "SSN")):
        digits = re.sub(r"\W", "", text)
        return ("*" * max(0, len(digits) - 4) + digits[-4:]) if digits else "***"
    if "ADDRESS" in field:
        return "***"
    if "NAME" in field:
        return " ".join(part[:1] + "***" for part in text.split())
    return "***"


def _report_rows(cursor):
    columns = [item[0] for item in (cursor.description or [])]
    rows = []
    pii_pattern = re.compile(r"(EMAIL|PHONE|MOBILE|ACCOUNT_ID|ACCOUNT_NUMBER|PAN|AADHAAR|ADDRESS|CUSTOMER_NAME|FULL_NAME|FIRST_NAME|LAST_NAME|SSN)", re.I)
    for values in cursor.fetchall():
        row = dict(zip(columns, values))
        for key in tuple(row):
            if pii_pattern.search(key):
                row[key] = _masked(key, row[key])
        upper_keys = {key.upper(): key for key in row}
        for upper_key, live_key in list(upper_keys.items()):
            if upper_key.startswith("LIVE_"):
                suffix = upper_key[5:]
                t1_key = upper_keys.get("T1_" + suffix) or upper_keys.get("T_1_" + suffix)
                if t1_key:
                    try:
                        row["DIFF_" + suffix] = float(row[live_key]) - float(row[t1_key])
                    except (TypeError, ValueError):
                        row["DIFF_" + suffix] = ""
        row.update({
            "DATE_OF_GENERATION": datetime.now(IST).isoformat(),
            "REPORT_DATE": _report_window("daily")["end"],
            "EXECUTION_DATE": datetime.now(IST).date().isoformat(),
        })
        rows.append(row)
    extra_diffs = [key for row in rows for key in row if key.startswith("DIFF_")]
    return list(dict.fromkeys([*columns, *extra_diffs, "DATE_OF_GENERATION", "REPORT_DATE", "EXECUTION_DATE"])), rows


def _report_window(period, now=None):
    now = now or datetime.now(IST)
    end = now.date() - timedelta(days=1)
    if period == "monthly":
        month = now.month - 1 or 12
        year = now.year if now.month > 1 else now.year - 1
        end = now.date().replace(year=year, month=month, day=calendar.monthrange(year, month)[1])
        start = end.replace(day=1)
    elif period == "fortnightly":
        start = end - timedelta(days=13)
    else:
        start = end
    return {"start": start.isoformat(), "end": end.isoformat()}


def run_configured_pipeline(report_period="daily", include_ingestion=True):
    """Run the daily ingest flow or a report-only fortnightly/monthly flow."""
    run_id = str(uuid.uuid4())
    execution_time = datetime.now(IST)
    date_window = _report_window(report_period, execution_time)
    report_date = date_window["end"]
    stages = []
    required = [SQL_ENV["report"]]
    if include_ingestion:
        required.extend(["NANOPRO_DMS_TASK_ARN", SQL_ENV["snowflake_l0"], SQL_ENV["snowflake_l1"], SQL_ENV["snowflake_l2"]])
    missing = [key for key in required if not os.environ.get(key, "").strip()]
    if missing:
        return {
            "status": "blocked", "live": False, "run_id": run_id,
            "missing_configuration": missing, "stages": stages,
            "message": "Pipeline did not run. Configure each provider and SQL stage before enabling this scheduled task."
        }

    if include_ingestion:
        task_arn = os.environ["NANOPRO_DMS_TASK_ARN"].strip()
        from app.core.aws_dms_manager import aws_dms_manager
        dms_result = aws_dms_manager.start_task(task_arn)
        stages.append({"stage": "oracle_dms_s3", "status": dms_result.get("status"), "live": dms_result.get("live", False), "dms_status": dms_result.get("dms_status")})
        if dms_result.get("status") != "success" or not dms_result.get("live"):
            return {"status": "failed", "live": False, "run_id": run_id, "stages": stages, "message": "AWS DMS task did not reach a verified running state."}

    try:
        import snowflake.connector
        from app.core.connection_manager import connection_manager
        cfg = connection_manager.get_connection_config("NANO_PRO_SNOWFLAKE", mask=False)
        if not cfg or not cfg.get("secret_value"):
            raise RuntimeError("Snowflake credentials are not configured in NanoPro's vault/environment.")
        meta = cfg.get("metadata") or {}
        account = meta.get("account_identifier")
        user = meta.get("username") or cfg.get("username")
        password = cfg.get("secret_value")
        if not account or not user:
            raise RuntimeError("Snowflake account identifier and username must be configured.")
        conn = snowflake.connector.connect(
            account=account, user=user, password=password,
            warehouse=meta.get("warehouse"), database=meta.get("database"),
            schema=meta.get("schema"), role=meta.get("role"), login_timeout=20,
        )
    except Exception as exc:
        stages.append({"stage": "snowflake_connect", "status": "failed", "error": str(exc)[:400]})
        return {"status": "failed", "live": False, "run_id": run_id, "stages": stages, "message": "Snowflake connection failed; later stages were not run."}

    report_file = None
    email_result = None
    try:
        with conn:
            with conn.cursor() as cursor:
                for stage, env_key in SQL_ENV.items():
                    if not include_ingestion and stage != "report":
                        continue
                    sql = os.environ[env_key].strip()
                    if stage == "report":
                        sql = sql.replace("{report_start}", date_window["start"]).replace("{report_end}", date_window["end"]).replace("{execution_date}", execution_time.date().isoformat())
                    try:
                        cursor.execute(sql)
                        row_count = max(cursor.rowcount or 0, 0)
                        stage_result = {"stage": stage, "status": "success", "rows_affected": row_count}
                        stages.append(stage_result)
                        if stage == "report":
                            result_columns = {str(item[0]).upper() for item in (cursor.description or [])}
                            compared = {
                                column[5:]
                                for column in result_columns
                                if column.startswith("LIVE_") and ("T1_" + column[5:] in result_columns or "T_1_" + column[5:] in result_columns)
                            }
                            if not compared:
                                raise RuntimeError("Report SQL must return at least one paired LIVE_* and T1_* (or T_1_*) metric.")
                            columns, rows = _report_rows(cursor)
                            for row in rows:
                                row["REPORT_DATE"] = date_window["end"]
                                row["EXECUTION_DATE"] = execution_time.date().isoformat()
                                row["DATE_OF_GENERATION"] = datetime.now(IST).isoformat()
                            result_dir = Path(REPORTS_DIR)
                            result_dir.mkdir(parents=True, exist_ok=True)
                            report_file = result_dir / f"data_pipeline_{report_period}_{report_date}_{run_id[:8]}.csv"
                            with report_file.open("w", encoding="utf-8-sig", newline="") as handle:
                                writer = csv.DictWriter(handle, fieldnames=columns or ["message"])
                                writer.writeheader()
                                if rows:
                                    writer.writerows(rows)
                                else:
                                    writer.writerow({"message": "No report rows"})
                    except Exception as exc:
                        stages.append({"stage": stage, "status": "failed", "error": str(exc)[:400]})
                        return {"status": "failed", "live": False, "run_id": run_id, "stages": stages, "message": f"{stage} failed; remaining stages were not run."}

        if not report_file or not report_file.exists():
            raise RuntimeError("Report artifact was not produced by the verified report query.")
        size_bytes = report_file.stat().st_size
        attachment = [str(report_file)] if size_bytes < MAX_EMAIL_ATTACHMENT_BYTES else []
        stage_summary = "Oracle → AWS DMS → S3 → Snowflake L0 → L1 → L2 → report" if include_ingestion else "Snowflake period report only"
        summary = (
            f"NanoPro pipeline report\nReport period: {report_period}\nData/report date range (IST): {date_window['start']} through {date_window['end']}\n"
            f"Execution date/time (IST): {execution_time.isoformat()}\nRun ID: {run_id}\n"
            f"Stages: {stage_summary}\n"
            f"Report artifact: {size_bytes} bytes; rows: {len(rows)}\n"
            + ("The report is attached." if attachment else "The report exceeds 5 MiB; summary only as requested.")
        )
        from app.core.smtp_client import smtp_client
        email_result = smtp_client.send_email(
            recipient=REPORT_RECIPIENT,
            subject=f"NanoPro {report_period.title()} Data Pipeline Report — {report_date}",
            body=summary, attachments=attachment, task_id=run_id,
            report_name=report_file.name, data_source="Oracle AWS DMS S3 Snowflake",
        )
        if not email_result.get("success") or "telegram" in str(email_result.get("provider", "")).lower():
            stages.append({"stage": "email_report", "status": "failed", "provider": email_result.get("provider"), "delivery_status": email_result.get("status")})
            return {"status": "failed", "live": False, "run_id": run_id, "stages": stages, "report_file": str(report_file), "message": "Pipeline data stages completed, but email delivery was not verified."}
        stages.append({"stage": "email_report", "status": "success", "provider": email_result.get("provider"), "attachment_bytes": size_bytes if attachment else 0})
        return {"status": "success", "live": True, "run_id": run_id, "report_date": report_date, "execution_time": execution_time.isoformat(), "report_period": report_period, "report_file": str(report_file), "stages": stages, "message": "All configured cloud stages and email dispatch completed."}
    except Exception as exc:
        stages.append({"stage": "report_delivery", "status": "failed", "error": str(exc)[:400]})
        return {"status": "failed", "live": False, "run_id": run_id, "stages": stages, "message": "Pipeline report or delivery failed."}
