"""Configured Oracle → S3 → Snowflake pipeline runner.

Use direct Oracle full-load/incremental extracts to S3 on Free-plan accounts;
AWS DMS remains an optional mode for accounts with verified DMS access.
"""
import csv
import json
import os
import re
import threading
import uuid
from datetime import datetime, timedelta
import calendar
from pathlib import Path
from zoneinfo import ZoneInfo

from app.core.config import REPORTS_DIR

IST = ZoneInfo("Asia/Kolkata")
MAX_EMAIL_ATTACHMENT_BYTES = 5_000_000
REPORT_RECIPIENT = "nanoproaistudio@gmail.com"
_DELIVERY_LEDGER_LOCK = threading.Lock()
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


def _report_rows(cursor, report_date, execution_date):
    columns = [item[0] for item in (cursor.description or [])]
    rows = []
    pii_pattern = re.compile(r"(EMAIL|PHONE|MOBILE|ACCOUNT_ID|ACCOUNT_NUMBER|CUSTOMER_ID|PAN|AADHAAR|ADDRESS|CUSTOMER_NAME|FULL_NAME|FIRST_NAME|LAST_NAME|SSN|DATE_OF_BIRTH|DOB|POSTAL_CODE|ZIP_CODE)", re.I)
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
            "REPORT_DATE": report_date,
            "EXECUTION_DATE": execution_date,
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
    if period == "daily":
        live_start = live_end = now.date()
        t1_start = t1_end = end
    else:
        live_start, live_end = start, end
        t1_end = start - timedelta(days=1)
        if period == "monthly":
            t1_start = t1_end.replace(day=1)
        else:
            t1_start = t1_end - timedelta(days=13)
    return {
        "start": start.isoformat(), "end": end.isoformat(),
        "live_start": live_start.isoformat(), "live_end": live_end.isoformat(),
        "t1_start": t1_start.isoformat(), "t1_end": t1_end.isoformat(),
    }


def _execute_configured_sql(cursor, sql):
    """Execute a configured stage containing one or more Snowflake statements."""
    statements = []
    current = []
    quote = None
    line_comment = False
    block_comment = False
    index = 0
    while index < len(sql):
        char = sql[index]
        nxt = sql[index + 1] if index + 1 < len(sql) else ""
        if line_comment:
            current.append(char)
            if char in "\r\n":
                line_comment = False
        elif block_comment:
            current.append(char)
            if char == "*" and nxt == "/":
                current.append(nxt)
                index += 1
                block_comment = False
        elif quote:
            current.append(char)
            if char == quote:
                if nxt == quote:
                    current.append(nxt)
                    index += 1
                else:
                    quote = None
        elif char == "-" and nxt == "-":
            current.extend((char, nxt))
            index += 1
            line_comment = True
        elif char == "/" and nxt == "*":
            current.extend((char, nxt))
            index += 1
            block_comment = True
        elif char in ("'", '"'):
            quote = char
            current.append(char)
        elif char == ";":
            statements.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    if current:
        statements.append("".join(current).strip())
    statements = [
        statement for statement in statements
        if re.sub(r"(?s)/\*.*?\*/|--[^\r\n]*", "", statement).strip()
    ]
    if not statements:
        raise RuntimeError("Configured SQL stage is empty.")
    affected = 0
    for statement in statements:
        cursor.execute(statement)
        affected += max(cursor.rowcount or 0, 0)
    return affected


def _delivery_ledger(run_id, report_file, report_period, report_date, execution_time, size_bytes, recipient, email_status):
    """Persist report delivery attempts so sent counts and recipients are auditable."""
    ledger = Path(REPORTS_DIR) / "data_pipeline_delivery_ledger.jsonl"
    entry = {
        "run_id": run_id,
        "report_file": report_file.name,
        "report_period": report_period,
        "report_date": report_date,
        "execution_time": execution_time.isoformat(),
        "size_bytes": size_bytes,
        "email_recipient": recipient,
        "email_status": email_status,
        "telegram_status": "pending",
    }
    with _DELIVERY_LEDGER_LOCK:
        ledger.parent.mkdir(parents=True, exist_ok=True)
        prior = []
        if ledger.exists():
            for line in ledger.read_text(encoding="utf-8").splitlines():
                try:
                    prior.append(json.loads(line))
                except (ValueError, TypeError):
                    continue
        entry["reports_attempted_total"] = len(prior) + 1
        entry["email_reports_sent_total"] = sum(1 for item in prior if item.get("email_status") == "sent") + (1 if email_status == "sent" else 0)
        entry["telegram_monitor_messages_sent_total"] = sum(1 for item in prior if item.get("telegram_status") == "sent")
        with ledger.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def _update_delivery_ledger(run_id, telegram_status):
    """Mark the most recent matching report's Telegram attempt outcome."""
    ledger = Path(REPORTS_DIR) / "data_pipeline_delivery_ledger.jsonl"
    with _DELIVERY_LEDGER_LOCK:
        if not ledger.exists():
            return
        lines = ledger.read_text(encoding="utf-8").splitlines()
        for index in range(len(lines) - 1, -1, -1):
            try:
                entry = json.loads(lines[index])
            except (ValueError, TypeError):
                continue
            if entry.get("run_id") == run_id:
                entry["telegram_status"] = telegram_status
                lines[index] = json.dumps(entry, ensure_ascii=False)
                ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
                return


def run_configured_pipeline(report_period="daily", include_ingestion=True, include_report=True):
    """Run incremental ingestion, a daily ingest/report, or report-only period flow."""
    run_id = str(uuid.uuid4())
    execution_time = datetime.now(IST)
    date_window = _report_window(report_period, execution_time)
    report_date = date_window["end"]
    stages = []
    ingestion_mode = (os.environ.get("NANOPRO_INGESTION_MODE", "s3") or "s3").strip().lower()
    if ingestion_mode not in {"s3", "dms"}:
        return {"status": "blocked", "live": False, "run_id": run_id, "stages": stages, "message": "NANOPRO_INGESTION_MODE must be s3 or dms."}
    s3_ingestion = None
    ingestion_result = None
    if not include_ingestion and not include_report:
        return {"status": "blocked", "live": False, "run_id": run_id, "stages": stages, "message": "At least ingestion or a report stage must be enabled."}
    required = [SQL_ENV["report"]] if include_report else []
    if include_ingestion:
        required.extend([SQL_ENV["snowflake_l0"], SQL_ENV["snowflake_l1"], SQL_ENV["snowflake_l2"]])
        if ingestion_mode == "dms":
            required.append("NANOPRO_DMS_TASK_ARN")
        else:
            source_connection = os.environ.get("NANOPRO_ORACLE_CONNECTION", "ORACLE_APEX_23AI_CLOUD").strip()
            is_ords = source_connection == "ORACLE_APEX_23AI_CLOUD"
            if not is_ords:
                from app.core.connection_manager import connection_manager
                source_cfg = connection_manager.get_connection_config(source_connection, mask=True) or {}
                is_ords = (source_cfg.get("metadata") or {}).get("connection_type") == "ORDS_REST"
            if not is_ords:
                required.extend([
                    "NANOPRO_ORACLE_SOURCE_TABLE", "NANOPRO_ORACLE_WATERMARK_COLUMN",
                ])
    missing = [key for key in required if not os.environ.get(key, "").strip()]
    if include_ingestion and ingestion_mode == "s3" and "{snowflake_stage_path}" not in os.environ.get("NANOPRO_SNOWFLAKE_COPY_SQL", ""):
        missing.append("NANOPRO_SNOWFLAKE_COPY_SQL (must include {snowflake_stage_path})")
    if missing:
        return {
            "status": "blocked", "live": False, "run_id": run_id,
            "missing_configuration": missing, "stages": stages,
            "message": "Pipeline did not run. Configure each provider and SQL stage before enabling this scheduled task."
        }

    if include_ingestion and ingestion_mode == "dms":
        task_arn = os.environ["NANOPRO_DMS_TASK_ARN"].strip()
        from app.core.aws_dms_manager import aws_dms_manager
        dms_result = aws_dms_manager.start_task(task_arn)
        stages.append({"stage": "oracle_dms_s3", "status": dms_result.get("status"), "live": dms_result.get("live", False), "dms_status": dms_result.get("dms_status")})
        if dms_result.get("status") != "success" or not dms_result.get("live"):
            return {"status": "failed", "live": False, "run_id": run_id, "stages": stages, "message": "AWS DMS task did not reach a verified running state."}
        load_result = aws_dms_manager.wait_for_full_load(task_arn)
        stages.append({
            "stage": "oracle_full_load_ready", "status": load_result.get("status"),
            "live": load_result.get("live", False), "dms_status": load_result.get("dms_status"),
            "full_load_progress_pct": load_result.get("full_load_progress_pct"),
            "tables_loaded": load_result.get("tables_loaded"),
            "tables_errored": load_result.get("tables_errored"),
        })
        if load_result.get("status") != "success" or not load_result.get("live"):
            return {
                "status": "failed", "live": False, "run_id": run_id, "stages": stages,
                "message": "AWS DMS full-load completion was not verified; Snowflake stages were not run.",
            }
    elif include_ingestion:
        try:
            from app.core.oracle_s3_ingestion import OracleS3Ingestion
            s3_ingestion = OracleS3Ingestion()
            ingestion_result = s3_ingestion.extract_and_upload(run_id)
            stages.append({
                "stage": "oracle_s3_" + ingestion_result["mode"], "status": "success",
                "live": True, "rows": ingestion_result["rows"], "s3_uri": ingestion_result["s3_uri"],
            })
        except Exception as exc:
            stages.append({"stage": "oracle_s3_ingestion", "status": "failed", "error": type(exc).__name__})
            return {"status": "failed", "live": False, "run_id": run_id, "stages": stages, "message": "Oracle-to-S3 ingestion failed; Snowflake stages were not run."}

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
        if ingestion_result:
            Path(ingestion_result["local_path"]).unlink(missing_ok=True)
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
                    if stage == "report" and not include_report:
                        continue
                    sql = os.environ[env_key].strip()
                    if stage == "snowflake_l0" and ingestion_result:
                        stage_name = os.environ.get("NANOPRO_SNOWFLAKE_INTERNAL_STAGE", "@~/nanopro_landing").strip()
                        s3_ingestion.upload_to_snowflake_stage(cursor, ingestion_result, stage_name)
                        sql = sql.replace("{snowflake_stage_path}", ingestion_result["snowflake_stage_path"])
                    if stage == "report":
                        for placeholder, value in {
                            "{report_start}": date_window["start"],
                            "{report_end}": date_window["end"],
                            "{execution_date}": execution_time.date().isoformat(),
                            "{live_start}": date_window["live_start"],
                            "{live_end}": date_window["live_end"],
                            "{t1_start}": date_window["t1_start"],
                            "{t1_end}": date_window["t1_end"],
                        }.items():
                            sql = sql.replace(placeholder, value)
                    try:
                        row_count = _execute_configured_sql(cursor, sql)
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
                            columns, rows = _report_rows(
                                cursor,
                                report_date=date_window["end"],
                                execution_date=execution_time.date().isoformat(),
                            )
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
                        elif stage == "snowflake_l2" and ingestion_result:
                            s3_ingestion.commit_checkpoint(ingestion_result)
                            stages.append({"stage": "s3_checkpoint", "status": "success", "live": True})
                    except Exception as exc:
                        stages.append({"stage": stage, "status": "failed", "error": str(exc)[:400]})
                        return {"status": "failed", "live": False, "run_id": run_id, "stages": stages, "message": f"{stage} failed; remaining stages were not run."}

        if not include_report:
            return {
                "status": "success", "live": True, "run_id": run_id,
                "execution_time": execution_time.isoformat(), "stages": stages,
                "message": "Configured incremental Oracle-to-S3-to-Snowflake stages completed.",
            }
        if not report_file or not report_file.exists():
            raise RuntimeError("Report artifact was not produced by the verified report query.")
        size_bytes = report_file.stat().st_size
        attachment = [str(report_file)] if size_bytes < MAX_EMAIL_ATTACHMENT_BYTES else []
        stage_summary = f"Oracle → {ingestion_mode.upper()} → S3 → Snowflake L0 → L1 → L2 → report" if include_ingestion else "Snowflake period report only"
        summary = (
            f"NanoPro pipeline report\nReport period: {report_period}\nData/report date range (IST): {date_window['start']} through {date_window['end']}\n"
            f"Execution date/time (IST): {execution_time.isoformat()}\nRun ID: {run_id}\n"
            f"Stages: {stage_summary}\n"
            f"Report artifact: {size_bytes} bytes; rows: {len(rows)}\nRecipient: {REPORT_RECIPIENT}\n"
            + ("The report is attached." if attachment else "The report exceeds 5,000,000 bytes; summary only as requested.")
        )
        from app.core.smtp_client import smtp_client
        email_result = smtp_client.send_email(
            recipient=REPORT_RECIPIENT,
            subject=f"NanoPro {report_period.title()} Data Pipeline Report — {report_date}",
            body=summary, attachments=attachment, task_id=run_id,
            report_name=report_file.name, data_source=f"Oracle {ingestion_mode.upper()} S3 Snowflake",
        )
        email_ok = bool(email_result.get("success")) and "telegram" not in str(email_result.get("provider", "")).lower()
        delivery = _delivery_ledger(
            run_id, report_file, report_period, report_date, execution_time, size_bytes,
            REPORT_RECIPIENT, "sent" if email_ok else "failed_or_unverified",
        )
        telegram_result = {"success": False, "error": "not_attempted"}
        try:
            from app.core.telegram_router import send_telegram_routed_message
            monitoring = (
                f"NanoPro report delivery monitor\nReports attempted: {delivery['reports_attempted_total']}\n"
                f"Reports successfully emailed: {delivery['email_reports_sent_total']}\n"
                f"Prior confirmed Telegram monitor deliveries: {delivery['telegram_monitor_messages_sent_total']}\n"
                f"This run: {report_period} {report_date}; {len(rows)} rows; {size_bytes} bytes\n"
                f"Email recipient: {REPORT_RECIPIENT} ({'sent' if email_ok else 'failed/unverified'} this run)\n"
                "Telegram destination: @mangesh_reports_bot\n"
                f"Attachment: {'included' if attachment else 'omitted (>5 MB)'}\nRun ID: {run_id}"
            )
            telegram_result = send_telegram_routed_message(
                category="reports", text=monitoring,
            )
        except Exception as exc:
            telegram_result = {"success": False, "error": type(exc).__name__}
        _update_delivery_ledger(run_id, "sent" if telegram_result.get("success") else "failed_or_unverified")
        if not email_result.get("success") or "telegram" in str(email_result.get("provider", "")).lower():
            stages.append({"stage": "email_report", "status": "failed", "provider": email_result.get("provider"), "delivery_status": email_result.get("status")})
            return {"status": "failed", "live": False, "run_id": run_id, "stages": stages, "report_file": str(report_file), "delivery_monitor": {"email_recipient": REPORT_RECIPIENT, "email_status": "failed_or_unverified", "telegram_recipient": "@mangesh_reports_bot", "telegram_status": "sent" if telegram_result.get("success") else "failed_or_unverified", "reports_attempted_total": delivery["reports_attempted_total"]}, "message": "Pipeline data stages completed, but email delivery was not verified."}
        stages.append({"stage": "email_report", "status": "success", "provider": email_result.get("provider"), "attachment_bytes": size_bytes if attachment else 0})
        stages.append({"stage": "telegram_report_monitor", "status": "success" if telegram_result.get("success") else "failed", "recipient": "@mangesh_reports_bot", "delivery_status": telegram_result.get("status") or telegram_result.get("error")})
        telegram_ok = bool(telegram_result.get("success"))
        return {"status": "success", "live": True, "run_id": run_id, "report_date": report_date, "execution_time": execution_time.isoformat(), "report_period": report_period, "report_file": str(report_file), "delivery_monitor": {"email_recipient": REPORT_RECIPIENT, "email_status": "sent", "telegram_recipient": "@mangesh_reports_bot", "telegram_status": "sent" if telegram_ok else "failed_or_unverified", "reports_attempted_total": delivery["reports_attempted_total"], "email_reports_sent_total": delivery["email_reports_sent_total"], "telegram_monitor_messages_sent_total": delivery["telegram_monitor_messages_sent_total"] + (1 if telegram_ok else 0), "ledger_file": str(Path(REPORTS_DIR) / "data_pipeline_delivery_ledger.jsonl")}, "stages": stages, "message": "Configured report email and Telegram delivery monitoring completed."}
    except Exception as exc:
        stages.append({"stage": "report_delivery", "status": "failed", "error": str(exc)[:400]})
        return {"status": "failed", "live": False, "run_id": run_id, "stages": stages, "message": "Pipeline report or delivery failed."}
    finally:
        if ingestion_result:
            Path(ingestion_result["local_path"]).unlink(missing_ok=True)
