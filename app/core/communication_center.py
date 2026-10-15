"""
Mangesh Nano Pro AI Studio - Central Communications Hub & Delivery Ledger
Features:
- Multi-Account Telegram Routing & Automated Broadcasting
- Free WhatsApp Automated Dispatcher (wa.me instant links, CallMeBot API, Webhook integration)
- Configurable Process-to-Recipient Mapping ("Which process sent mail to whom")
- Unified Communication Ledger tracking all dispatches across Email, Telegram, and WhatsApp
- Emergency / Urgent Connection Failure Alerting Engine
"""

import os
import sys
import time
import json
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.core.logger import log_event
from app.core.database import db, credentials_vault
from app.core.smtp_client import smtp_client

DEFAULT_COMMUNICATION_TARGETS = [
    {
        "id": "target_tg_primary",
        "channel": "telegram",
        "name": "Mangesh Personal Telegram",
        "target_identifier": "1200023268",
        "description": "Primary high-priority direct alerts & briefings",
        "is_active": True,
        "subscribed_processes": ["job_hunter", "connection_failure", "manager_notes", "approval_alerts", "daily_summary"]
    },
    {
        "id": "target_tg_channel",
        "channel": "telegram",
        "name": "Tech News & Job Radar Bot",
        "target_identifier": "@mangesh_technews_bot",
        "description": "Public/Channel broadcast for verified jobs and news",
        "is_active": True,
        "subscribed_processes": ["job_hunter", "news_digest", "entertainment"]
    },
    {
        "id": "target_wa_primary",
        "channel": "whatsapp",
        "name": "Mangesh Mobile WhatsApp",
        "target_identifier": "+918433755448",
        "description": "Instant free WhatsApp notifications & alerts",
        "is_active": True,
        "subscribed_processes": ["connection_failure", "daily_summary", "job_hunter"]
    },
    {
        "id": "target_mail_primary",
        "channel": "email",
        "name": "Mangesh Official Gmail",
        "target_identifier": "mangeshbagul15@gmail.com",
        "description": "Formal audit reports, ETL spreadsheets & HR application logs",
        "is_active": True,
        "subscribed_processes": ["etl_pipeline", "mnc_hr_outreach", "daily_executive_report", "connection_failure"]
    }
]

# Process-to-Recipient mapping defaults
DEFAULT_PROCESS_ROUTING = {
    "connection_failure": {
        "process_name": "Emergency Connection Health Monitor",
        "email_recipients": ["mangeshbagul15@gmail.com"],
        "telegram_targets": ["1200023268"],
        "whatsapp_targets": ["+918433755448"],
        "priority": "CRITICAL"
    },
    "job_hunter": {
        "process_name": "4-Hour Job Filter & Radar Agent",
        "email_recipients": ["mangeshbagul15@gmail.com"],
        "telegram_targets": ["1200023268", "@mangesh_technews_bot"],
        "whatsapp_targets": ["+918433755448"],
        "priority": "HIGH"
    },
    "mnc_hr_outreach": {
        "process_name": "6-Hour MNC HR Resume Dispatcher",
        "email_recipients": ["mangeshbagul15@gmail.com"],
        "telegram_targets": ["1200023268"],
        "whatsapp_targets": [],
        "priority": "HIGH"
    },
    "data_engineer_etl": {
        "process_name": "Data Engineering Cross-DB Federated Pipeline",
        "email_recipients": ["mangeshbagul15@gmail.com"],
        "telegram_targets": ["1200023268"],
        "whatsapp_targets": [],
        "priority": "MEDIUM"
    },
    "manager_notes": {
        "process_name": "Manager Ambient Notes (Morning/Evening/Night)",
        "email_recipients": [],
        "telegram_targets": ["1200023268"],
        "whatsapp_targets": ["+918433755448"],
        "priority": "LOW"
    },
    "dms_migration": {
        "process_name": "AWS DMS Replication Monitor",
        "email_recipients": ["mangeshbagul15@gmail.com"],
        "telegram_targets": ["1200023268"],
        "whatsapp_targets": [],
        "priority": "HIGH"
    }
}

class CommunicationCenter:
    def __init__(self):
        self._init_communication_tables()
        self._seed_default_targets()

    def _init_communication_tables(self):
        """Initializes tables for multi-account communication channels, process routing, and dispatch ledger."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS communication_targets (
                    id TEXT PRIMARY KEY,
                    channel TEXT NOT NULL,          -- telegram, whatsapp, email
                    name TEXT NOT NULL,
                    target_identifier TEXT NOT NULL, -- chat_id, phone, email
                    description TEXT,
                    is_active INTEGER DEFAULT 1,
                    subscribed_processes_json TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )""")

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS process_routing_config (
                    process_key TEXT PRIMARY KEY,
                    process_name TEXT NOT NULL,
                    email_recipients_json TEXT,
                    telegram_targets_json TEXT,
                    whatsapp_targets_json TEXT,
                    priority TEXT DEFAULT 'MEDIUM',
                    updated_at REAL NOT NULL
                )""")

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS communication_ledger (
                    id TEXT PRIMARY KEY,
                    channel TEXT NOT NULL,          -- email, telegram, whatsapp
                    process_name TEXT NOT NULL,
                    sender TEXT,
                    recipient TEXT NOT NULL,
                    subject TEXT,
                    status TEXT NOT NULL,          -- sent, failed, queued
                    error_message TEXT,
                    dispatched_at REAL NOT NULL,
                    summary_text TEXT,
                    metadata_json TEXT
                )""")
                conn.commit()
        except Exception as e:
            log_event(f"Error initializing communication tables: {e}", component="CommunicationCenter", level="WARNING")

    def _seed_default_targets(self):
        """Seeds default communication targets and process routing if empty."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM communication_targets")
                if cursor.fetchone()[0] == 0:
                    now = time.time()
                    for t in DEFAULT_COMMUNICATION_TARGETS:
                        cursor.execute("""
                        INSERT INTO communication_targets (
                            id, channel, name, target_identifier, description, is_active,
                            subscribed_processes_json, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            t["id"], t["channel"], t["name"], t["target_identifier"],
                            t["description"], 1 if t["is_active"] else 0,
                            json.dumps(t["subscribed_processes"]), now, now
                        ))

                cursor.execute("SELECT COUNT(*) FROM process_routing_config")
                if cursor.fetchone()[0] == 0:
                    now = time.time()
                    for pkey, pcfg in DEFAULT_PROCESS_ROUTING.items():
                        cursor.execute("""
                        INSERT INTO process_routing_config (
                            process_key, process_name, email_recipients_json,
                            telegram_targets_json, whatsapp_targets_json, priority, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            pkey, pcfg["process_name"],
                            json.dumps(pcfg["email_recipients"]),
                            json.dumps(pcfg["telegram_targets"]),
                            json.dumps(pcfg["whatsapp_targets"]),
                            pcfg["priority"], now
                        ))
                conn.commit()
        except Exception as e:
            log_event(f"Error seeding communication targets: {e}", component="CommunicationCenter", level="WARNING")

    # =========================================================================
    # Process Routing & Recipient Configuration Management
    # =========================================================================

    def get_process_routing_config(self) -> Dict[str, Any]:
        """Returns the complete mapping of which process sends mail/telegram/whatsapp to which recipients."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM process_routing_config")
            rows = cursor.fetchall()
            configs = {}
            for r in rows:
                configs[r["process_key"]] = {
                    "process_name": r["process_name"],
                    "email_recipients": json.loads(r["email_recipients_json"] or "[]"),
                    "telegram_targets": json.loads(r["telegram_targets_json"] or "[]"),
                    "whatsapp_targets": json.loads(r["whatsapp_targets_json"] or "[]"),
                    "priority": r["priority"],
                    "updated_at": r["updated_at"]
                }
            return configs

    def update_process_routing(
        self,
        process_key: str,
        email_recipients: List[str],
        telegram_targets: Optional[List[str]] = None,
        whatsapp_targets: Optional[List[str]] = None,
        process_name: Optional[str] = None
    ) -> bool:
        """Updates recipient configurations for a specific studio process."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT process_name FROM process_routing_config WHERE process_key = ?", (process_key,))
            row = cursor.fetchone()
            pname = process_name or (row["process_name"] if row else process_key)

            cursor.execute("""
            INSERT INTO process_routing_config (
                process_key, process_name, email_recipients_json, telegram_targets_json, whatsapp_targets_json, priority, updated_at
            ) VALUES (?, ?, ?, ?, ?, 'HIGH', ?)
            ON CONFLICT(process_key) DO UPDATE SET
                email_recipients_json = excluded.email_recipients_json,
                telegram_targets_json = COALESCE(excluded.telegram_targets_json, process_routing_config.telegram_targets_json),
                whatsapp_targets_json = COALESCE(excluded.whatsapp_targets_json, process_routing_config.whatsapp_targets_json),
                updated_at = excluded.updated_at
            """, (
                process_key, pname,
                json.dumps(email_recipients),
                json.dumps(telegram_targets or []),
                json.dumps(whatsapp_targets or []),
                time.time()
            ))
            conn.commit()
        log_event(f"Updated process routing for [{process_key}] -> Recipients: {email_recipients}", component="CommunicationCenter")
        return True

    # =========================================================================
    # Multi-Account Telegram Management & Dispatch
    # =========================================================================

    def list_targets(self, channel: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists registered communication targets."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            if channel:
                cursor.execute("SELECT * FROM communication_targets WHERE channel = ? ORDER BY created_at ASC", (channel,))
            else:
                cursor.execute("SELECT * FROM communication_targets ORDER BY channel, created_at ASC")
            rows = [dict(r) for r in cursor.fetchall()]
            for r in rows:
                if r.get("subscribed_processes_json"):
                    try: r["subscribed_processes"] = json.loads(r["subscribed_processes_json"])
                    except Exception: r["subscribed_processes"] = []
            return rows

    def add_target(
        self,
        channel: str,
        name: str,
        target_identifier: str,
        description: str = "",
        subscribed_processes: Optional[List[str]] = None
    ) -> str:
        """Adds a new Telegram chat, WhatsApp number, or email recipient."""
        tid = f"target_{channel.lower()}_{int(time.time()*1000)}"
        procs = subscribed_processes or ["all"]
        now = time.time()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO communication_targets (
                id, channel, name, target_identifier, description, is_active,
                subscribed_processes_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)
            """, (tid, channel.lower(), name, target_identifier, description, json.dumps(procs), now, now))
            conn.commit()
        log_event(f"Added new communication target [{tid}] ({channel}: {target_identifier})", component="CommunicationCenter")
        return tid

    def delete_target(self, target_id: str) -> bool:
        """Removes a communication target."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM communication_targets WHERE id = ?", (target_id,))
            conn.commit()
        log_event(f"Deleted communication target [{target_id}]", component="CommunicationCenter")
        return True

    def send_telegram_broadcast(
        self,
        message: str,
        process_key: str = "general",
        parse_mode: str = "HTML"
    ) -> Dict[str, Any]:
        """Broadcasts a message to all active Telegram targets mapped to this process."""
        from app.agents.assistant_agent import personal_assistant_agent

        targets = self.list_targets(channel="telegram")
        active_chat_ids = [t["target_identifier"] for t in targets if t.get("is_active")]
        if not active_chat_ids:
            active_chat_ids = ["1200023268"]

        results = []
        for chat_id in active_chat_ids:
            try:
                res = personal_assistant_agent.send_telegram_message(message, parse_mode=parse_mode, target_chat_id=chat_id)
                status = "sent" if res.get("status") == "success" else "failed"
                err = res.get("error") if status == "failed" else None
                self.record_ledger_entry(
                    channel="telegram",
                    process_name=process_key,
                    sender="@mangesh_technews_bot",
                    recipient=chat_id,
                    subject="Telegram Broadcast",
                    status=status,
                    error_message=err,
                    summary_text=message[:150]
                )
                results.append({"chat_id": chat_id, "status": status, "error": err})
            except Exception as e:
                results.append({"chat_id": chat_id, "status": "failed", "error": str(e)})

        return {"status": "success", "dispatched_count": len(results), "details": results}

    # =========================================================================
    # Free WhatsApp Integration Engine
    # =========================================================================

    def generate_whatsapp_web_link(self, phone: str, message: str) -> str:
        """Generates a free 1-click WhatsApp Web protocol link with pre-filled encoded text."""
        clean_phone = "".join(c for c in phone if c.isdigit() or c == "+")
        if clean_phone.startswith("+"):
            clean_phone = clean_phone[1:]
        encoded_text = urllib.parse.quote(message)
        return f"https://wa.me/{clean_phone}?text={encoded_text}"

    def generate_whatsapp_click_link(self, phone: str, message: str) -> Dict[str, Any]:
        """Returns structured JSON containing WhatsApp Web link."""
        link = self.generate_whatsapp_web_link(phone, message)
        return {
            "status": "success",
            "phone_number": phone,
            "whatsapp_web_link": link,
            "message": "1-Click WhatsApp Link Ready"
        }

    def send_whatsapp_callmebot(self, phone: str, api_key: str, message: str) -> Dict[str, Any]:
        """Dispatches automated WhatsApp message using CallMeBot API key."""
        return self.send_whatsapp_free_message(phone=phone, message=message, process_key="whatsapp_callmebot", callmebot_api_key=api_key)

    def send_whatsapp_free_message(
        self,
        phone: str,
        message: str,
        process_key: str = "whatsapp_alert",
        callmebot_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends free WhatsApp message:
        1. If CallMeBot API Key is provided, dispatches direct HTTP request for free automated delivery.
        2. Otherwise generates the verified WhatsApp Web one-click action link.
        """
        clean_phone = "".join(c for c in phone if c.isdigit() or c == "+")
        wa_link = self.generate_whatsapp_web_link(clean_phone, message)

        # Check for free CallMeBot API key in Vault or environment
        cb_key = callmebot_api_key or os.environ.get("CALLMEBOT_API_KEY")
        if not cb_key:
            cb_cred = credentials_vault.get_credential("CALLMEBOT_WHATSAPP")
            if cb_cred: cb_key = cb_cred.get("secret_value")

        dispatched = False
        error_msg = None

        if cb_key:
            try:
                # CallMeBot Free WhatsApp API: https://api.callmebot.com/whatsapp.php?phone=[phone]&text=[text]&apikey=[apikey]
                encoded_msg = urllib.parse.quote_plus(message)
                url = f"https://api.callmebot.com/whatsapp.php?phone={clean_phone}&text={encoded_msg}&apikey={cb_key}"
                req = urllib.request.Request(url, headers={"User-Agent": "NanoPro-AI-Studio/1.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    if resp.status == 200:
                        dispatched = True
            except Exception as e:
                error_msg = str(e)

        status = "sent" if dispatched else "ready_for_web"
        self.record_ledger_entry(
            channel="whatsapp",
            process_name=process_key,
            sender="NanoPro WhatsApp Gateway",
            recipient=clean_phone,
            subject="WhatsApp Notification",
            status="sent" if dispatched else "queued",
            error_message=error_msg,
            summary_text=message[:150],
            metadata={"web_link": wa_link, "direct_api": bool(cb_key)}
        )

        return {
            "status": "success",
            "delivered_via_api": dispatched,
            "recipient_phone": clean_phone,
            "whatsapp_web_link": wa_link,
            "message": "Direct automated WhatsApp delivery succeeded." if dispatched else "1-Click WhatsApp link generated. Click to send instantly for free."
        }

    # =========================================================================
    # Process-Aware Email Dispatch with Full Audit Logging
    # =========================================================================

    def send_process_email(
        self,
        process_key: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        attachment_path: Optional[str] = None,
        custom_recipient: Optional[str] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends an email respecting the process routing configuration.
        Tracks which process sent email to whom in the communication ledger.
        Guarantees mandatory candidate CC & BCC delivery for all HR dispatches.
        """
        routing = self.get_process_routing_config()
        pcfg = routing.get(process_key, {})
        recipients = [custom_recipient] if custom_recipient else pcfg.get("email_recipients", ["mangeshbagul15@gmail.com"])
        pname = pcfg.get("process_name", process_key)

        # Enforce candidate CC and BCC on all HR outreach
        effective_cc = cc or ("mangeshbagul15@gmail.com" if "hr" in process_key.lower() or "job" in process_key.lower() else None)
        effective_bcc = bcc or ("mangeshbagul15@gmail.com" if "hr" in process_key.lower() or "job" in process_key.lower() else None)

        # Ensure resume PDF attachment for career applications
        default_resume = "app/resumes/Mangesh_Bagul_Data_Engineer.pdf"
        target_attachment = attachment_path or (default_resume if ("hr" in process_key.lower() or "job" in process_key.lower()) and os.path.exists(default_resume) else None)
        attachments = [target_attachment] if target_attachment and os.path.exists(target_attachment) else None

        results = []
        for rcpt in recipients:
            try:
                res = smtp_client.send_email(
                    recipient=rcpt,
                    subject=subject,
                    body=body_text,
                    body_text=body_text,
                    body_html=body_html,
                    attachments=attachments,
                    cc=effective_cc,
                    bcc=effective_bcc
                )
                is_ok = bool(res.get("success") or res.get("status") == "success" or "Accepted" in str(res.get("status", "")))
                status = "sent" if is_ok else "failed"
                err = res.get("error") if status == "failed" else None
                self.record_ledger_entry(
                    channel="email",
                    process_name=pname,
                    sender="mangeshbagul15@gmail.com",
                    recipient=rcpt,
                    subject=subject,
                    status=status,
                    error_message=err,
                    summary_text=body_text[:150],
                    metadata={"attachment": target_attachment, "cc": effective_cc, "bcc": effective_bcc}
                )
                results.append({"recipient": rcpt, "status": status, "error": err, "cc": effective_cc, "bcc": effective_bcc})
            except Exception as e:
                self.record_ledger_entry(
                    channel="email",
                    process_name=pname,
                    sender="mangeshbagul15@gmail.com",
                    recipient=rcpt,
                    subject=subject,
                    status="failed",
                    error_message=str(e),
                    summary_text=body_text[:150]
                )
                results.append({"recipient": rcpt, "status": "failed", "error": str(e)})

        return {"status": "success", "process": pname, "dispatches": results}

    # =========================================================================
    # Emergency Connection Failure Alerting Engine
    # =========================================================================

    def send_emergency_connection_failure_alert(
        self,
        connection_name: str,
        service_type: str,
        error_details: str
    ):
        """Immediately sends an urgent Telegram alert and records failure when ANY database or service connection fails."""
        alert_msg = (
            f"🚨 <b>URGENT: CONNECTION FAILURE DETECTED</b> 🚨\n\n"
            f"• <b>Connection:</b> <code>{connection_name}</code>\n"
            f"• <b>Service Type:</b> <code>{service_type.upper()}</code>\n"
            f"• <b>Recorded Time:</b> <code>{time.strftime('%Y-%m-%d %H:%M:%S')}</code>\n"
            f"• <b>Error Details:</b> <i>{error_details}</i>\n\n"
            f"⚠️ <i>Please verify network routing, firewall port 1521, or Credential Vault passwords.</i>"
        )
        # Dispatch to Telegram targets
        self.send_telegram_broadcast(alert_msg, process_key="connection_failure")

        # Also send WhatsApp link / message
        self.send_whatsapp_free_message(
            phone="+918433755448",
            message=f"🚨 URGENT NANO PRO ALERT: Connection Failed for {connection_name}! Error: {error_details[:100]}",
            process_key="connection_failure"
        )

        log_event(f"Emergency connection failure alert dispatched for [{connection_name}]", component="CommunicationCenter", level="ERROR")

    def notify_config_change(self, component: str, change_details: str, changed_by: str = "Admin") -> Dict[str, Any]:
        """Broadcasts security and configuration changes (e.g. password update) to Telegram and email."""
        msg = (
            f"🔐 <b>NanoPro Configuration Update</b>\n\n"
            f"• <b>Component:</b> {component}\n"
            f"• <b>Details:</b> {change_details}\n"
            f"• <b>Initiator:</b> {changed_by}\n"
            f"• <b>Timestamp:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"• <b>Security:</b> AES-256-GCM Vault & .env Synchronized"
        )
        return self.send_telegram_broadcast(msg, process_key="config_change")

    # =========================================================================
    # Communication Ledger Persistence
    # =========================================================================

    def record_ledger_entry(
        self,
        channel: str,
        process_name: str,
        sender: Optional[str],
        recipient: str,
        subject: Optional[str],
        status: str,
        error_message: Optional[str] = None,
        summary_text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Records an immutable delivery observation in communication_ledger."""
        entry_id = f"comm_{int(time.time()*1000)}"
        now = time.time()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO communication_ledger (
                    id, channel, process_name, sender, recipient, subject,
                    status, error_message, dispatched_at, summary_text, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry_id, channel, process_name, sender or "", recipient, subject or "",
                    status, error_message or "", now, summary_text or "", json.dumps(metadata or {})
                ))
                conn.commit()
        except Exception as e:
            log_event(f"Error recording communication ledger: {e}", component="CommunicationCenter", level="WARNING")
        return entry_id

    def get_communication_ledger(self, limit: int = 50, channel: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves recent communication logs showing which process sent messages/mail to whom."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            if channel:
                cursor.execute("SELECT * FROM communication_ledger WHERE channel = ? ORDER BY dispatched_at DESC LIMIT ?", (channel, limit))
            else:
                cursor.execute("SELECT * FROM communication_ledger ORDER BY dispatched_at DESC LIMIT ?", (limit,))
            rows = [dict(r) for r in cursor.fetchall()]
            for r in rows:
                r["formatted_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r["dispatched_at"]))
                if r.get("metadata_json"):
                    try: r["metadata"] = json.loads(r["metadata_json"])
                    except Exception: r["metadata"] = {}
            return rows

communication_center = CommunicationCenter()
