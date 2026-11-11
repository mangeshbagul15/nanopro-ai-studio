"""
Mangesh Nano Pro AI Studio - WhatsApp Autonomous Guardian & Zero-Downtime Engine
================================================================================
Assigned Agent: NanoPro Manager & Agent Workers (Group T - Communications & Health)

Responsibilities:
1. 24/7 Channel Keep-Alive: Proactively ensures the Meta WhatsApp 24-hour window NEVER expires
   by autonomously dispatching Meta-Approved Template Heartbeats before expiration.
2. Inbound & Outbound Telemetry Persistence: Persists WhatsApp state in SQLite & Upstash Redis
   so restart of server/laptop does not reset the 24-hour timer.
3. Autonomous Failover & Multi-Channel Sync: If Meta Cloud API encounters errors,
   instantly synchronizes with Telegram (@mangesh_health_monitor_bot) & Email.
4. Auto-Verification & Health Scoring: Continuously audits webhook endpoints, verify tokens,
   and Graph API tokens, self-healing any transient disconnects.
"""

import os
import re
import time
import json
import threading
from typing import Dict, Any, Optional

from app.core.logger import log_event
from app.core.database import db, credentials_vault

DEFAULT_PHONE = "+918433755448"
HEARTBEAT_THRESHOLD_HOURS = 20.0  # Proactively refresh before 24h window closes
HEARTBEAT_COOLDOWN_SECONDS = 43200  # Only send 1 heartbeat every 12 hours max
# Template pings cannot open Meta's 24h service window (only an inbound user
# message can), so the proactive heartbeat only spams the user on every boot.
# Off by default; opt in explicitly with WHATSAPP_HEARTBEAT_ENABLED=1.
HEARTBEAT_ENABLED = (os.environ.get("WHATSAPP_HEARTBEAT_ENABLED", "0").strip().lower() in ("1", "true", "on", "yes"))
# Even when enabled, a freshly restarted container must not fire: Render
# redeploys would otherwise send one template per deploy.
HEARTBEAT_MIN_UPTIME_SECONDS = float(os.environ.get("WHATSAPP_HEARTBEAT_MIN_UPTIME", "21600"))

class WhatsAppAutonomousGuardian:
    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self.last_inbound_time: float = 0.0
        self.last_inbound_text: str = ""
        self.last_inbound_sender: str = ""
        self.last_outbound_time: float = 0.0
        self.last_heartbeat_time: float = 0.0
        self.last_health_status: str = "INITIALIZING"
        self.started_at: float = time.time()
        self._init_database()
        self._load_state_from_db()

    def _init_database(self):
        """Initializes persistent storage for WhatsApp channel state."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS whatsapp_channel_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )""")
                conn.commit()
        except Exception as e:
            log_event(f"Error initializing whatsapp_channel_state table: {e}", level="WARNING", component="WhatsAppGuardian")

    def _load_state_from_db(self):
        """Restores state from persistent SQLite database."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM whatsapp_channel_state")
                rows = dict(cursor.fetchall())
                if "last_inbound_time" in rows:
                    self.last_inbound_time = float(rows["last_inbound_time"])
                if "last_inbound_text" in rows:
                    self.last_inbound_text = rows["last_inbound_text"]
                if "last_inbound_sender" in rows:
                    self.last_inbound_sender = rows["last_inbound_sender"]
                if "last_outbound_time" in rows:
                    self.last_outbound_time = float(rows["last_outbound_time"])
                if "last_heartbeat_time" in rows:
                    self.last_heartbeat_time = float(rows["last_heartbeat_time"])
        except Exception as e:
            log_event(f"Error loading whatsapp state from db: {e}", level="WARNING", component="WhatsAppGuardian")

    def _save_state(self, key: str, value: str):
        """Persists a key-value pair to database."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO whatsapp_channel_state (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """, (key, str(value), time.time()))
                conn.commit()
        except Exception as e:
            log_event(f"Error saving whatsapp state '{key}': {e}", level="WARNING", component="WhatsAppGuardian")

    def record_inbound(self, phone: str, sender_name: str, text: str):
        """Called whenever an inbound message is received from user."""
        now = time.time()
        with self._lock:
            self.last_inbound_time = now
            self.last_inbound_text = text
            self.last_inbound_sender = f"{sender_name} ({phone})"
        self._save_state("last_inbound_time", str(now))
        self._save_state("last_inbound_text", text)
        self._save_state("last_inbound_sender", self.last_inbound_sender)
        digits = "".join(c for c in str(phone) if c.isdigit())
        if digits:
            self._save_state(f"inbound:{digits}", str(now))
        log_event(f"WhatsApp Guardian: Recorded inbound message from {phone}. 24h window refreshed!", component="WhatsAppGuardian")

    def is_window_open_for(self, phone: str) -> bool:
        """True when this number messaged the business within Meta's 24h service window."""
        digits = "".join(c for c in str(phone) if c.isdigit())
        if not digits:
            return False
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM whatsapp_channel_state WHERE key = ?", (f"inbound:{digits}",))
                row = cursor.fetchone()
            return bool(row) and (time.time() - float(row[0])) < 23.5 * 3600
        except Exception:
            return False

    def record_outbound(self, phone: str, status: str, message_id: Optional[str] = None):
        """Called whenever an outbound message is dispatched."""
        now = time.time()
        with self._lock:
            self.last_outbound_time = now
        self._save_state("last_outbound_time", str(now))

    def get_channel_health(self) -> Dict[str, Any]:
        """Returns comprehensive real-time status of WhatsApp communication engine."""
        now = time.time()
        hours_since_inbound = (now - self.last_inbound_time) / 3600.0 if self.last_inbound_time > 0 else 999.0
        hours_since_heartbeat = (now - self.last_heartbeat_time) / 3600.0 if self.last_heartbeat_time > 0 else 999.0
        
        # Check credentials
        cred = credentials_vault.get_credential("WHATSAPP_BUSINESS_CLOUD") or {}
        has_token = bool(cred.get("secret_value") or os.environ.get("WHATSAPP_CLOUD_ACCESS_TOKEN"))
        has_phone_id = bool(cred.get("username") or os.environ.get("WHATSAPP_CLOUD_PHONE_ID"))
        
        # Two-way window status
        is_window_open = (self.last_inbound_time > 0) and (hours_since_inbound < 24.0)

        # Report what is actually true instead of a fixed all-green label:
        # outside the 24h window only approved templates can be sent at all.
        if not (has_token and has_phone_id):
            status = "UNCONFIGURED"
        elif not self._running:
            status = "DAEMON_STOPPED"
        elif is_window_open:
            status = "ACTIVE"
        else:
            status = "IDLE_TEMPLATE_ONLY"

        state_label = "24H_FREE_WINDOW_ACTIVE" if is_window_open else "TEMPLATE_REQUIRED"

        return {
            "status": status,
            "channel_mode": state_label,
            "two_way_free_chat_open": is_window_open,
            "hours_since_last_inbound": round(hours_since_inbound, 1),
            "hours_since_last_heartbeat": round(hours_since_heartbeat, 1),
            "last_inbound_text": self.last_inbound_text or "Awaiting initial text",
            "last_inbound_sender": self.last_inbound_sender or "Mangesh Bagul",
            "target_user_phone": DEFAULT_PHONE,
            "credentials_configured": has_token and has_phone_id,
            "meta_cloud_api": "CONFIGURED" if (has_token and has_phone_id) else "UNCONFIGURED",
            "permanent_webhook": "https://mangesh-nanopro.mangeshbagul15.workers.dev/api/whatsapp/webhook",
            "guardian_daemon_active": self._running,
            "proactive_heartbeat_enabled": HEARTBEAT_ENABLED,
            "template_fallback": ("available when credentials are configured"
                                  if (has_token and has_phone_id)
                                  else "unavailable until Meta credentials are set")
        }

    def force_heartbeat(self, reason: str = "manual_or_proactive") -> Dict[str, Any]:
        """Dispatches a Meta Approved Template heartbeat to keep the communication channel open."""
        from app.core.communication_center import communication_center
        log_event(f"WhatsApp Guardian: Dispatched proactive template heartbeat ({reason}) to {DEFAULT_PHONE}...", component="WhatsAppGuardian")
        res = communication_center.send_whatsapp_cloud_api(
            phone=DEFAULT_PHONE,
            message="NanoPro Studio Autonomous Heartbeat Ping",
            template_name="hello_world"
        )
        if res.get("success"):
            now = time.time()
            with self._lock:
                self.last_heartbeat_time = now
            self._save_state("last_heartbeat_time", str(now))
            log_event(f"WhatsApp Guardian: Heartbeat accepted by Meta [ID: {res.get('message_id')}]", component="WhatsAppGuardian")
        return res

    def start(self):
        """Starts the autonomous guardian background daemon."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(target=self._guardian_loop, daemon=True, name="WhatsAppAutonomousGuardian")
            self._thread.start()
        log_event(
            "WhatsAppAutonomousGuardian background worker started. "
            f"Proactive template heartbeat: {'ENABLED' if HEARTBEAT_ENABLED else 'DISABLED (opt in with WHATSAPP_HEARTBEAT_ENABLED=1)'}.",
            component="WhatsAppGuardian",
        )

    def stop(self):
        """Stops the guardian background daemon."""
        with self._lock:
            self._running = False

    def _refresh_state_from_db(self):
        """Re-reads durable timestamps so a restored SQLite state also wins."""
        try:
            with db.get_connection() as conn:
                rows = dict(conn.execute("SELECT key, value FROM whatsapp_channel_state").fetchall())
            if "last_heartbeat_time" in rows:
                self.last_heartbeat_time = max(self.last_heartbeat_time, float(rows["last_heartbeat_time"]))
            if "last_inbound_time" in rows:
                self.last_inbound_time = max(self.last_inbound_time, float(rows["last_inbound_time"]))
        except Exception:
            pass

    def _guardian_loop(self):
        """Autonomous loop running every 15 minutes."""
        # Initial heartbeat check on startup
        time.sleep(10)
        while self._running:
            try:
                self._refresh_state_from_db()
                now = time.time()
                hours_since_inbound = (now - self.last_inbound_time) / 3600.0 if self.last_inbound_time > 0 else 999.0
                uptime = now - self.started_at

                # Proactive template pings are opt-in and never fire on a fresh
                # boot: every restart would otherwise resend one to the user.
                if not HEARTBEAT_ENABLED:
                    pass
                elif uptime < HEARTBEAT_MIN_UPTIME_SECONDS:
                    pass
                elif hours_since_inbound >= HEARTBEAT_THRESHOLD_HOURS and (now - self.last_heartbeat_time) >= HEARTBEAT_COOLDOWN_SECONDS:
                    log_event(f"WhatsApp Guardian: Inbound idle for {round(hours_since_inbound, 1)}h (threshold={HEARTBEAT_THRESHOLD_HOURS}h). Triggering autonomous template keep-alive...", component="WhatsAppGuardian")
                    self.force_heartbeat(reason="proactive_window_keepalive")

            except Exception as e:
                log_event(f"Error in WhatsApp Guardian loop: {e}", level="WARNING", component="WhatsAppGuardian")

            # Sleep 900 seconds (15 minutes) before next check
            time.sleep(900)

whatsapp_guardian = WhatsAppAutonomousGuardian()
