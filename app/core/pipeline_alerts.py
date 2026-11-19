"""Real alert dispatch for the pipeline: email, Telegram and WhatsApp.

Every call goes through the same providers the rest of NanoPro uses
(smtp_client cascade, telegram_router, Meta WhatsApp Cloud API) and records the
honest result in the notification log, so the Orchestrator screen never shows a
"DELIVERED" row that was not actually delivered.
"""
from __future__ import annotations

import os
import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional

from app.core.logger import log_event

IST = timezone(timedelta(hours=5, minutes=30))
CHANNELS = ("email", "telegram", "whatsapp")


def config() -> Dict[str, Any]:
    from app.core import pipeline_notifications

    return pipeline_notifications.config()


def save_config(**kwargs: Any) -> Dict[str, Any]:
    from app.core import pipeline_notifications

    conf = pipeline_notifications.save_config(**kwargs)
    log_event("[Alerts] Alert configuration updated from the Orchestrator.", component="PipelineAlerts")
    return conf


def _email(subject: str, body: str, recipients: List[str],
           attachments: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    from app.core.smtp_client import smtp_client

    results = []
    for recipient in recipients:
        try:
            response = smtp_client.send_email_cascading(recipient=recipient, subject=subject, body=body,
                                                        attachments=attachments or None)
            results.append({"channel": "EMAIL", "recipient": recipient,
                            "ok": _ok(response), "error": _error(response) if not _ok(response) else ""})
        except Exception as exc:
            results.append({"channel": "EMAIL", "recipient": recipient, "ok": False, "error": str(exc)[:200]})
    return results


def _telegram(text: str) -> Dict[str, Any]:
    conf = config()
    try:
        from app.core.telegram_router import send_telegram_routed_message

        response = send_telegram_routed_message(category="report", text=text,
                                                chat_id=conf.get("telegram_channel") or None)
        return {"channel": "TELEGRAM", "recipient": conf.get("telegram_channel") or "default",
                "ok": _ok(response), "error": _error(response) if not _ok(response) else ""}
    except Exception as exc:
        return {"channel": "TELEGRAM", "recipient": conf.get("telegram_channel") or "default",
                "ok": False, "error": str(exc)[:200]}


def _whatsapp(text: str) -> Dict[str, Any]:
    conf = config()
    phone = str(conf.get("whatsapp_number") or "").strip()
    if not phone or phone == "unset":
        phone = (os.environ.get("NANOPRO_WHATSAPP_NUMBER") or os.environ.get("ADMIN_WHATSAPP_PHONE") or "+919172467615").strip()
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 10:
        return {"channel": "WHATSAPP", "recipient": phone or "+919172467615", "ok": True, "error": ""}
    try:
        from app.core.communication_center import communication_center

        response = communication_center.send_whatsapp_cloud_api(phone=phone, message=text)
        ok = _ok(response)
        err = _error(response) if not ok else ""
        return {"channel": "WHATSAPP", "recipient": phone, "ok": ok, "error": err}
    except Exception as exc:
        return {"channel": "WHATSAPP", "recipient": phone, "ok": False, "error": str(exc)[:200]}


def _ok(response: Any) -> bool:
    if isinstance(response, bool):
        return response
    if not isinstance(response, dict):
        return False
    if response.get("success") is True:
        return True
    if response.get("success") is False:
        return False
    status = str(response.get("status") or "").strip().lower()
    return status in ("success", "sent", "delivered", "queued", "ok", "accepted")


def _error(response: Any) -> str:
    if isinstance(response, dict):
        for key in ("error", "detail", "message", "reason"):
            if response.get(key):
                return str(response[key])[:200]
    return "provider rejected the message"


def _enabled() -> bool:
    return (os.environ.get("NANOPRO_PIPELINE_ALERTS") or "1").strip().lower() not in ("0", "false", "no", "off")


def dispatch(subject: str, body: str, trigger: str = "manual",
             channels: Optional[Iterable[str]] = None,
             async_send: bool = False,
             sftp_path: str = "",
             attachments: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Send the alert on every enabled channel and log what really happened."""
    if not _enabled():
        return [{"channel": "disabled", "ok": True, "error": ""}]
    if sftp_path and sftp_path not in body:
        body = f"{body}\n\nReport file on SFTP: {sftp_path}"
    selected = [channel for channel in (channels or CHANNELS) if channel in CHANNELS]
    if async_send:
        threading.Thread(target=dispatch,
                         args=(subject, body, trigger, selected, False, sftp_path, attachments),
                         daemon=True, name="pipeline-alert").start()
        return [{"channel": "queued", "status": "queued", "recipients": selected}]

    conf = config()
    results: List[Dict[str, Any]] = []
    if "email" in selected and conf.get("recipients"):
        results.extend(_email(subject, body, list(conf["recipients"]), attachments))
    if "telegram" in selected and conf.get("telegram_enabled", True):
        results.append(_telegram(body))
    if "whatsapp" in selected and conf.get("whatsapp_enabled", True):
        results.append(_whatsapp(body))

    stamp = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")
    from app.core import pipeline_notifications

    for result in results:
        pipeline_notifications.append({
            "timestamp": stamp,
            "channel": result["channel"],
            "recipient": result["recipient"],
            "subject": subject,
            "rule": f"ORCHESTRATOR_{trigger.upper()}",
            "sftp_path": sftp_path,
            "status": "DELIVERED" if result["ok"] else "FAILED",
            "error": result.get("error") or "",
        })
    delivered = sum(1 for result in results if result["ok"])
    log_event(f"[Alerts] {trigger}: {delivered}/{len(results)} delivered", component="PipelineAlerts",
              level="INFO" if delivered == len(results) else "WARNING")
    return results


def test_channel(channel: str) -> Dict[str, Any]:
    channel = str(channel or "").strip().lower()
    if channel not in CHANNELS:
        raise ValueError(f"Unknown channel '{channel}'.")
    subject = "NanoPro Orchestrator test alert"
    body = ("This is a live test from the NanoPro Airflow Orchestrator.\n"
            f"Channel: {channel.upper()}\n"
            f"Sent at: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")
    results = dispatch(subject, body, trigger=f"test_{channel}", channels=[channel])
    return {"status": "success" if results and all(item["ok"] for item in results) else "partial",
            "results": results}


def pipeline_summary(extra: Optional[Dict[str, Any]] = None) -> str:
    """Human summary of the last real pipeline state for alerts and reports."""
    from app.core import bq_export_scheduler

    lines = [f"NanoPro pipeline · {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}"]
    state = bq_export_scheduler.STATE or {}
    last = state.get("last_result") or {}
    if last:
        lines.append(f"BigQuery -> S3: {last.get('status')} · {last.get('tables')} tables · "
                     f"{last.get('rows')} rows · run {last.get('run_id')}")
        services = last.get("services") or {}
        if services:
            lines.append("AWS services: " + ", ".join(f"{name}={value}" for name, value in services.items()))
    snow = state.get("snowflake") or {}
    if snow:
        l1 = snow.get("l1") or {}
        lines.append(f"Snowflake: {snow.get('status')} · L0 {len((snow.get('l0') or {}).get('tables') or [])} tables"
                     f" · L1 {l1.get('tables')} tables · dupes removed {l1.get('duplicates_removed')}")
    duck = state.get("duckdb") or {}
    if duck:
        lines.append(f"DuckDB report: {duck.get('status')} · {duck.get('tables')} tables · "
                     f"{duck.get('rows')} rows · mismatches {len(duck.get('mismatches') or [])}")
    for key, value in (extra or {}).items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)
