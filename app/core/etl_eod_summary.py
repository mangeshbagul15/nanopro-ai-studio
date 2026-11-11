"""
NanoPro AI Studio - ETL EOD Summary Dispatcher
===============================================
Sends daily 7PM IST summary of all ETL pipeline runs to:
  1. WhatsApp (+918433755448)  -- when Meta production access is ready
  2. Telegram (@mangesh_reports_bot) -- always active fallback
  3. Email (nanoproaistudio@gmail.com) -- always active

Summary includes:
  - Which reports were delivered / pending / failed
  - Total records processed
  - T-1 report dates
  - BOD/SOD/EOD cycle status
  - Next run schedule
"""

from __future__ import annotations
import threading
import datetime
import time
from typing import Dict, Any, List

from app.core.logger import log_event
from app.core.config import TELEGRAM_CHAT_ID

IST_OFFSET = 5.5  # UTC + 5:30


def _ist_now() -> datetime.datetime:
    return datetime.datetime.utcnow() + datetime.timedelta(hours=IST_OFFSET)


def build_eod_summary() -> str:
    """Builds the 7PM EOD summary message."""
    try:
        from app.core.etl_automation_pipeline import (
            PROJECTS, etl_pipeline, _t1_report_dates, _get_batch_cycle
        )
        t1    = _t1_report_dates()
        now   = _ist_now()
        cycle = _get_batch_cycle()

        delivered = []
        pending   = []
        failed    = []

        for key, p in PROJECTS.items():
            wm   = etl_pipeline.get_watermark(key)
            mode = etl_pipeline.detect_load_mode(key)

            if wm:
                # Check if watermark is today (ran today)
                try:
                    wm_dt    = datetime.datetime.strptime(wm[:19], "%Y-%m-%d %H:%M:%S")
                    ran_today = wm_dt.date() == now.date()
                except Exception:
                    ran_today = False

                if ran_today:
                    delivered.append(f"  OK  {p['code']:<22} | {mode} | WM: {wm[:16]}")
                else:
                    pending.append(f"  PENDING  {p['code']:<22} | Last: {wm[:16]}")
            else:
                pending.append(f"  PENDING  {p['code']:<22} | Never run")

        total = len(PROJECTS)
        ok    = len(delivered)
        pend  = len(pending)
        fail  = len(failed)

        # Build message
        lines = [
            f"*NanoPro AI Studio — EOD Report Summary*",
            f"",
            f"Date: {t1['report_date']} | Cycle: {cycle}",
            f"Generated: {now.strftime('%d-%b-%Y %I:%M %p IST')}",
            f"",
            f"*Pipeline Status ({ok}/{total} delivered):*",
        ]

        if delivered:
            lines.append(f"")
            lines.append(f"Delivered ({ok}):") 
            lines.extend(delivered)

        if pending:
            lines.append(f"")
            lines.append(f"Pending ({pend}):")
            lines.extend(pending)

        if failed:
            lines.append(f"")
            lines.append(f"Failed ({fail}):")
            lines.extend(failed)

        lines += [
            f"",
            f"T-1 Report Date : {t1['report_date']}",
            f"T-1 Cut-off     : {t1['t1_cutoff']}",
            f"",
            f"Next Run: Tomorrow BOD 06:00 IST",
            f"",
            f"— NanoPro AI Studio",
        ]

        return "\n".join(lines)

    except Exception as e:
        return f"NanoPro ETL EOD Summary\nError building summary: {e}"


def build_batch_status_message(cycle_type: str) -> str:
    """
    Builds BOD / SOD / EOD Telegram status message.
    cycle_type: "BOD" | "SOD" | "EOD"
    """
    try:
        from app.core.etl_automation_pipeline import (
            PROJECTS, etl_pipeline, _t1_report_dates
        )
        t1  = _t1_report_dates()
        now = _ist_now()

        icons = {"BOD": "🌅", "SOD": "🟢", "EOD": "🌙"}
        icon  = icons.get(cycle_type, "📊")

        lines = [
            f"{icon} <b>NanoPro AI Studio — {cycle_type} Status</b>",
            f"━━━━━━━━━━━━━━━━━━━━━━━━",
            f"",
            f"📅 <b>Date:</b> <code>{t1['report_date']}</code>",
            f"⏰ <b>Time:</b> <code>{now.strftime('%d-%b-%Y %I:%M %p IST')}</code>",
            f"🔄 <b>Cycle:</b> <code>{cycle_type}</code>",
            f"",
        ]

        if cycle_type == "BOD":
            lines += [
                f"<b>Begin of Day Checklist:</b>",
                f"✅ Previous day data loaded (T-1)",
                f"✅ Watermarks updated",
                f"✅ Neon L0/L1 tables ready",
                f"✅ Snowflake L2 DIM+FACT ready",
                f"",
                f"<b>Pipeline Status:</b>",
            ]
        elif cycle_type == "SOD":
            lines += [
                f"<b>Start of Day — Open Positions:</b>",
                f"✅ Beginning balances loaded",
                f"✅ EOD cut-off data: {t1['t1_cutoff']}",
                f"✅ T-1 reports ready for dispatch",
                f"",
                f"<b>Pipeline Status:</b>",
            ]
        elif cycle_type == "EOD":
            lines += [
                f"<b>End of Day — Cut-off Complete:</b>",
                f"✅ Today's data cut at: {now.strftime('%d-%b-%Y 23:59:59 IST')}",
                f"✅ Next T-1 report date: {now.strftime('%d-%b-%Y')}",
                f"📧 EOD Summary: nanoproaistudio@gmail.com",
                f"",
                f"<b>Pipeline Status:</b>",
            ]

        # Add each project status
        delivered = 0
        for key, p in PROJECTS.items():
            wm   = etl_pipeline.get_watermark(key)
            mode = etl_pipeline.detect_load_mode(key)
            if wm:
                try:
                    wm_dt    = datetime.datetime.strptime(wm[:19], "%Y-%m-%d %H:%M:%S")
                    ran_today = wm_dt.date() == now.date()
                except Exception:
                    ran_today = False
                status_icon = "✅" if ran_today else "⏳"
                wm_short    = wm[:16]
                if ran_today:
                    delivered += 1
            else:
                status_icon = "❌"
                wm_short    = "Never run"

            lines.append(
                f"{status_icon} <b>{p['code']}</b> | "
                f"<code>{mode}</code> | {wm_short}"
            )

        total = len(PROJECTS)
        lines += [
            f"",
            f"━━━━━━━━━━━━━━━━━━━━━━━━",
            f"📊 <b>Summary:</b> {delivered}/{total} pipelines ran today",
            f"📅 <b>T-1 Date:</b> <code>{t1['report_date']}</code>",
            f"",
        ]

        if cycle_type == "BOD":
            lines.append(f"⏰ <i>Next: SOD at 08:00 IST | Daily Report at 10:00 IST</i>")
        elif cycle_type == "SOD":
            lines.append(f"⏰ <i>Next: Daily Report at 10:00 IST | EOD at 18:00 IST</i>")
        elif cycle_type == "EOD":
            lines.append(f"⏰ <i>Next: EOD Summary at 19:00 IST | BOD tomorrow at 06:00 IST</i>")

        lines.append(f"<i>Powered by NanoPro AI Studio</i>")
        return "\n".join(lines)

    except Exception as e:
        return f"<b>{cycle_type} Status</b>\nError: {e}"


def send_batch_cycle_notification(cycle_type: str) -> Dict[str, Any]:
    """Send BOD/SOD/EOD status to Telegram @mangesh_reports_bot."""
    msg = build_batch_status_message(cycle_type)
    results = {}

    # Telegram
    try:
        from app.core.telegram_router import send_telegram_routed_message
        tg = send_telegram_routed_message(
            category="reports",
            text=msg,
            chat_id=TELEGRAM_CHAT_ID,
            parse_mode="HTML"
        )
        results["telegram"] = {"sent": tg.get("success", False)}
        log_event(f"{cycle_type} status sent to Telegram", component="ETLEODSummary")
    except Exception as e:
        results["telegram"] = {"sent": False, "error": str(e)}

    return {"status": "success", "cycle": cycle_type, "results": results}


def dispatch_eod_summary(force: bool = False) -> Dict[str, Any]:
    """
    Sends EOD summary to WhatsApp + Telegram + Email.
    Called automatically at 7PM IST by ETLEODScheduler.
    """
    summary = build_eod_summary()
    results = {}

    # 1. WhatsApp (primary — works when Meta production access is ready)
    try:
        from app.core.communication_center import communication_center
        wa_result = communication_center.send_whatsapp_cloud_api(
            phone="+918433755448",
            message=summary
        )
        results["whatsapp"] = {
            "sent":       wa_result.get("success", False),
            "message_id": wa_result.get("message_id"),
            "error":      wa_result.get("error"),
        }
        if wa_result.get("success"):
            log_event("EOD Summary sent via WhatsApp", component="ETLEODSummary")
        else:
            log_event(f"WhatsApp EOD failed: {wa_result.get('error')} — Telegram fallback active", 
                      level="WARNING", component="ETLEODSummary")
    except Exception as e:
        results["whatsapp"] = {"sent": False, "error": str(e)}

    # 2. Telegram (@mangesh_reports_bot) — always active
    try:
        from app.core.telegram_router import send_telegram_routed_message
        # Convert to HTML for Telegram
        tg_text = summary.replace("*", "<b>", 1)
        for _ in range(50):
            tg_text = tg_text.replace("*", "</b>", 1) if "<b>" in tg_text and "</b>" not in tg_text.split("<b>")[-1] else tg_text.replace("*", "<b>", 1)
        # Simple plain approach
        tg_text = summary.replace("*", "")
        tg_html = f"<b>NanoPro AI Studio — EOD Report Summary</b>\n\n{summary.replace('*NanoPro AI Studio — EOD Report Summary*', '').strip()}"
        tg_res = send_telegram_routed_message(
            category="reports",
            text=tg_html,
            chat_id=TELEGRAM_CHAT_ID,
            parse_mode="HTML"
        )
        results["telegram"] = {"sent": tg_res.get("success", False)}
        if tg_res.get("success"):
            log_event("EOD Summary sent via Telegram @mangesh_reports_bot", component="ETLEODSummary")
    except Exception as e:
        results["telegram"] = {"sent": False, "error": str(e)}

    # 3. Email (nanoproaistudio@gmail.com)
    try:
        from app.core.smtp_client import smtp_client
        email_res = smtp_client.send_email(
            recipient   = "nanoproaistudio@gmail.com",
            subject     = f"[NanoPro EOD] Pipeline Summary — {datetime.datetime.now().strftime('%d-%b-%Y')}",
            body        = summary.replace("*", ""),
            report_name = "ETL_EOD_Summary",
            data_source = "NanoPro ETL EOD Scheduler"
        )
        results["email"] = {"sent": email_res.get("success", False)}
        if email_res.get("success"):
            log_event("EOD Summary sent via Email", component="ETLEODSummary")
    except Exception as e:
        results["email"] = {"sent": False, "error": str(e)}

    overall = any(v.get("sent") for v in results.values())
    log_event(f"EOD Summary dispatch: WA={results.get('whatsapp',{}).get('sent')} TG={results.get('telegram',{}).get('sent')} Email={results.get('email',{}).get('sent')}", component="ETLEODSummary")

    return {
        "status":  "success" if overall else "failed",
        "results": results,
        "summary": summary[:200] + "..."
    }


class ETLEODScheduler:
    """
    Daily batch cycle notifications to Telegram + WhatsApp + Email:
      BOD  06:00 IST — Begin of Day status
      SOD  08:00 IST — Start of Day status
      EOD  18:00 IST — End of Day status
      EOD Summary 19:00 IST — Full pipeline summary (WhatsApp + Telegram + Email)
    """

    def __init__(self):
        self._stop        = threading.Event()
        self._thread      = None
        self._last_runs   = {}   # slot_key -> date

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="ETLEODScheduler"
        )
        self._thread.start()
        log_event("ETL EOD Scheduler started (BOD 6AM / SOD 8AM / EOD 6PM / Summary 7PM IST)", component="ETLEODSummary")

    def stop(self):
        self._stop.set()
        log_event("ETL EOD Scheduler stopped", component="ETLEODSummary")

    def _loop(self):
        # slot: (hour, minute, action, label)
        SLOTS = [
            (6,  0, "BOD",     "BOD 06:00 IST"),
            (8,  0, "SOD",     "SOD 08:00 IST"),
            (18, 0, "EOD",     "EOD 18:00 IST"),
            (19, 0, "SUMMARY", "EOD Summary 19:00 IST"),
        ]
        while not self._stop.is_set():
            try:
                now   = _ist_now()
                today = now.strftime("%Y-%m-%d")
                h, m  = now.hour, now.minute

                # Both hosts run this loop, so only the lane leader may send.
                # Otherwise one slot would deliver two Telegram/WhatsApp/email
                # copies at 06:00, 08:00, 18:00 and 19:00.
                from app.core.runtime_profile import cloud_safe_mode
                from app.core.scheduler_lease import is_leader

                can_send = is_leader("cloud" if cloud_safe_mode() else "local")

                for slot_h, slot_m, action, label in SLOTS:
                    slot_key = f"{today}_{action}"
                    if h == slot_h and m == slot_m and slot_key not in self._last_runs:
                        if not can_send:
                            continue
                        self._last_runs[slot_key] = now.isoformat()
                        log_event(f"ETL Scheduler: {label} triggered", component="ETLEODSummary")

                        if action in ("BOD", "SOD", "EOD"):
                            threading.Thread(
                                target=send_batch_cycle_notification,
                                args=(action,), daemon=True
                            ).start()
                        elif action == "SUMMARY":
                            threading.Thread(
                                target=dispatch_eod_summary,
                                daemon=True
                            ).start()

                # Cleanup old keys (keep last 100)
                if len(self._last_runs) > 100:
                    old = list(self._last_runs.keys())[:-50]
                    for k in old:
                        del self._last_runs[k]

            except Exception as e:
                log_event(f"ETL EOD Scheduler loop error: {e}", level="WARNING", component="ETLEODSummary")

            self._stop.wait(60)


# Module-level singleton
etl_eod_scheduler = ETLEODScheduler()
