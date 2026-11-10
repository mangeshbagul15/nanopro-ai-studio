"""
Mangesh Nano Pro AI Studio - Secure Gmail & SMTP Client Integration
Provides verified SMTP TLS/SSL connectivity, credential retrieval from the secure vault,
connection testing, delivery confirmation logging, and email reporting with attachments.
Never embeds passwords in source code, logs, or exports.
"""

import smtplib
import ssl
import time
import os
import re
import socket
import json
import base64
import requests
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from app.core.logger import log_event
from app.core.database import db, credentials_vault

DEFAULT_GMAIL_SENDER = "mangeshbagul15@gmail.com"
DEFAULT_GMAIL_RECIPIENT = "nanoproaistudio@gmail.com"
DEFAULT_MOBILE = "8433755448"

class SMTPClient:
    def __init__(self):
        self.default_host = "smtp.gmail.com"
        self.default_port = 587
        self.default_sender_name = "NanoPro AI Studio"
        self.default_sender_email = DEFAULT_GMAIL_SENDER
        self.default_recipient = os.environ.get("GMAIL_RECIPIENT") or DEFAULT_GMAIL_RECIPIENT
        self.registered_mobile = DEFAULT_MOBILE

    def get_configured_identity(self) -> Dict[str, str]:
        """Returns the configured sender identity and notification recipients."""
        config = self.get_configuration() or {}
        return {
            "sender_email": config.get("sender_email") or self.default_sender_email,
            "recipient_email": self.default_recipient,
            "registered_mobile": self.registered_mobile,
            "sender_name": config.get("sender_name") or self.default_sender_name,
            "host": config.get("host") or self.default_host,
            "port": str(config.get("port") or self.default_port),
            "security_mode": config.get("security_mode") or "STARTTLS",
            "has_credentials": bool(self.get_secret_password())
        }

    def get_secret_password(self) -> Optional[str]:
        """
        Securely retrieves the Gmail App Password or SMTP password from:
        1. Environment variable GMAIL_APP_PASSWORD or SMTP_PASSWORD
        2. Encrypted Credential Vault under service_name 'smtp' or 'gmail'
        Never prints or logs the retrieved secret.
        """
        env_pw = os.environ.get("GMAIL_APP_PASSWORD") or os.environ.get("SMTP_PASSWORD")
        if env_pw and env_pw.strip():
            return env_pw.strip()
        
        # Check vault
        for service_name in ["smtp", "gmail", "GMAIL_SMTP"]:
            cred = credentials_vault.get_credential(service_name)
            if cred and cred.get("secret_value"):
                return cred["secret_value"].strip()
                
        # Search all credentials of type 'email'
        for item in credentials_vault.list_credentials(mask=False):
            if item.get("credential_type") == "email" and item.get("secret_value"):
                return item["secret_value"].strip()
                
        return None

    def save_configuration(
        self,
        host: str = "smtp.gmail.com",
        port: int = 587,
        username: str = DEFAULT_GMAIL_SENDER,
        password: Optional[str] = None,
        sender_email: Optional[str] = None,
        sender_name: str = "NanoPro AI Studio",
        security_mode: str = "STARTTLS"
    ) -> str:
        """
        Saves or updates SMTP settings in the Credential Vault securely.
        If password is not provided, retains existing password in the vault.
        """
        existing_pw = self.get_secret_password() or ""
        effective_pw = password.strip() if password and password.strip() else existing_pw

        # Clean existing entries to prevent duplication
        for c in credentials_vault.list_credentials(mask=True):
            if c.get("service_name") in ["smtp", "GMAIL_SMTP", "gmail"]:
                try:
                    credentials_vault.delete_credential(c["id"])
                except Exception:
                    pass

        cred_id = credentials_vault.store_credential(
            service_name="GMAIL_SMTP",
            credential_type="email",
            username=username or DEFAULT_GMAIL_SENDER,
            secret_value=effective_pw,
            host=host or self.default_host,
            port=str(port or self.default_port),
            email=sender_email or username or DEFAULT_GMAIL_SENDER,
            mobile_number=self.registered_mobile,
            additional_info={
                "sender_name": sender_name,
                "security_mode": security_mode,
                "notification_recipient": DEFAULT_GMAIL_RECIPIENT,
                "registered_mobile": DEFAULT_MOBILE,
                "updated_at": time.time()
            }
        )
        log_event(f"Updated Gmail SMTP configuration in Vault [{cred_id}] for {sender_email or username}", component="SMTPClient")
        return cred_id

    def get_configuration(self) -> Optional[Dict[str, Any]]:
        """Retrieves masked SMTP configuration details."""
        for c in credentials_vault.list_credentials(mask=True):
            if c.get("service_name") in ["smtp", "GMAIL_SMTP", "gmail"] or c.get("credential_type") == "email":
                meta = c.get("additional_metadata") or {}
                if isinstance(meta, str):
                    try:
                        import json
                        meta = json.loads(meta)
                    except Exception:
                        meta = {}
                has_pw = bool(self.get_secret_password())
                return {
                    "id": c.get("id"),
                    "host": c.get("host") or self.default_host,
                    "port": int(c.get("port") or self.default_port),
                    "username": c.get("username") or self.default_sender_email,
                    "sender_email": c.get("email") or self.default_sender_email,
                    "notification_recipient": meta.get("notification_recipient", self.default_recipient),
                    "registered_mobile": c.get("mobile_number") or self.registered_mobile,
                    "sender_name": meta.get("sender_name", self.default_sender_name),
                    "security_mode": meta.get("security_mode", "STARTTLS"),
                    "has_password": has_pw,
                    "masked_password": "••••••••••••••••" if has_pw else ""
                }
        
        # If not explicitly in DB, return default template with env check
        has_pw = bool(self.get_secret_password())
        return {
            "id": "default_gmail",
            "host": self.default_host,
            "port": self.default_port,
            "username": self.default_sender_email,
            "sender_email": self.default_sender_email,
            "notification_recipient": self.default_recipient,
            "registered_mobile": self.registered_mobile,
            "sender_name": self.default_sender_name,
            "security_mode": "STARTTLS",
            "has_password": has_pw,
            "masked_password": "••••••••••••••••" if has_pw else ""
        }

    # =========================================================================
    # CLOUD HTTPS EMAIL CONFIGURATION (PORT 443 - ANTI-SPAM FIREWALL BYPASS)
    # =========================================================================

    def get_resend_config(self) -> Dict[str, Any]:
        """Returns Resend API key and sender email from environment or Vault."""
        api_key = (os.environ.get("RESEND_API_KEY") or "").strip()
        from_email = (os.environ.get("RESEND_FROM_EMAIL") or "Mangesh AI Studio <onboarding@resend.dev>").strip()

        if not api_key:
            for s in ["RESEND_EMAIL", "resend", "RESEND"]:
                c = credentials_vault.get_credential(s)
                if c and c.get("secret_value"):
                    api_key = c["secret_value"].strip()
                    if c.get("email"):
                        from_email = c["email"].strip()
                    break

        return {
            "api_key": api_key,
            "from_email": from_email,
            "has_credentials": bool(api_key),
            "masked_key": f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else ("••••••••" if api_key else "")
        }

    def save_resend_config(self, api_key: str, from_email: Optional[str] = None) -> str:
        """Stores Resend credentials encrypted in Vault."""
        return credentials_vault.store_credential(
            service_name="RESEND_EMAIL",
            credential_type="api_key",
            username=from_email or "onboarding@resend.dev",
            secret_value=api_key.strip(),
            host="api.resend.com",
            port="443",
            email=from_email or "onboarding@resend.dev",
            additional_info={
                "provider": "Resend",
                "quota": "3,000 emails/month free",
                "protocol": "HTTPS Port 443"
            }
        )

    def get_brevo_config(self) -> Dict[str, Any]:
        """Returns Brevo API key and sender email from environment or Vault."""
        api_key = (os.environ.get("BREVO_API_KEY") or "").strip()
        sender_email = (os.environ.get("BREVO_SENDER_EMAIL") or DEFAULT_GMAIL_SENDER).strip()
        sender_name = (os.environ.get("BREVO_SENDER_NAME") or "Mangesh AI Studio").strip()

        if not api_key:
            for s in ["BREVO_EMAIL", "brevo", "BREVO", "sendinblue"]:
                c = credentials_vault.get_credential(s)
                if c and c.get("secret_value"):
                    api_key = c["secret_value"].strip()
                    if c.get("email"):
                        sender_email = c["email"].strip()
                    meta = c.get("additional_metadata") or {}
                    if isinstance(meta, dict) and meta.get("sender_name"):
                        sender_name = meta["sender_name"]
                    break

        return {
            "api_key": api_key,
            "sender_email": sender_email,
            "sender_name": sender_name,
            "has_credentials": bool(api_key),
            "masked_key": f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else ("••••••••" if api_key else "")
        }

    def save_brevo_config(self, api_key: str, sender_email: Optional[str] = None, sender_name: Optional[str] = None) -> str:
        """Stores Brevo credentials encrypted in Vault."""
        return credentials_vault.store_credential(
            service_name="BREVO_EMAIL",
            credential_type="api_key",
            username=sender_email or DEFAULT_GMAIL_SENDER,
            secret_value=api_key.strip(),
            host="api.brevo.com",
            port="443",
            email=sender_email or DEFAULT_GMAIL_SENDER,
            additional_info={
                "provider": "Brevo (Sendinblue)",
                "quota": "300 emails/day free",
                "protocol": "HTTPS Port 443",
                "sender_name": sender_name or "Mangesh AI Studio"
            }
        )

    def get_relay_config(self) -> Dict[str, Any]:
        """Returns the Google Apps Script email relay endpoint and shared secret."""
        url = (os.environ.get("EMAIL_RELAY_URL") or "").strip()
        secret = (os.environ.get("EMAIL_RELAY_SECRET") or "").strip()
        relay_inbox = (os.environ.get("EMAIL_RELAY_TO") or self.default_recipient).strip()

        if not (url and secret):
            for s in ["EMAIL_RELAY", "email_relay", "GOOGLE_APPS_SCRIPT_RELAY"]:
                c = credentials_vault.get_credential(s)
                if c:
                    meta = c.get("additional_metadata") or {}
                    if isinstance(meta, str):
                        try:
                            meta = json.loads(meta)
                        except Exception:
                            meta = {}
                    if not url:
                        url = (meta.get("url") or c.get("host") or "").strip()
                    if not secret and c.get("secret_value"):
                        secret = c["secret_value"].strip()
                    if c.get("email"):
                        relay_inbox = c["email"].strip()
                    break

        return {
            "url": url,
            "secret": secret,
            "relay_inbox": relay_inbox,
            "has_credentials": bool(url and secret),
            "masked_secret": "••••••••" if secret else ""
        }

    def save_relay_config(self, url: str, secret: str, relay_inbox: Optional[str] = None) -> str:
        """Stores the Apps Script relay endpoint and secret encrypted in Vault."""
        return credentials_vault.store_credential(
            service_name="EMAIL_RELAY",
            credential_type="api_key",
            username="google-apps-script",
            secret_value=secret.strip(),
            host=url.strip(),
            port="443",
            email=relay_inbox or self.default_recipient,
            additional_info={
                "provider": "Google Apps Script Relay",
                "url": url.strip(),
                "protocol": "HTTPS Port 443"
            }
        )

    def get_gmail_api_config(self) -> Dict[str, Any]:
        """Returns Gmail REST API OAuth2 credentials from environment or Vault."""
        client_id = (os.environ.get("GMAIL_API_CLIENT_ID") or "").strip()
        client_secret = (os.environ.get("GMAIL_API_CLIENT_SECRET") or "").strip()
        refresh_token = (os.environ.get("GMAIL_API_REFRESH_TOKEN") or "").strip()
        access_token = (os.environ.get("GMAIL_API_ACCESS_TOKEN") or "").strip()
        account_email = (os.environ.get("GMAIL_API_EMAIL") or DEFAULT_GMAIL_SENDER).strip()

        if not (refresh_token or access_token):
            for s in ["GMAIL_API", "gmail_api", "GOOGLE_GMAIL_API"]:
                c = credentials_vault.get_credential(s)
                if c:
                    if c.get("secret_value"):
                        refresh_token = c["secret_value"].strip()
                    if c.get("username"):
                        client_id = c["username"].strip()
                    if c.get("email"):
                        account_email = c["email"].strip()
                    meta = c.get("additional_metadata") or {}
                    if isinstance(meta, dict):
                        client_secret = meta.get("client_secret", client_secret)
                        access_token = meta.get("access_token", access_token)
                    break

        has_creds = bool(access_token or (refresh_token and client_id))
        return {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "access_token": access_token,
            "account_email": account_email,
            "has_credentials": has_creds,
            "masked_token": f"{refresh_token[:6]}...{refresh_token[-4:]}" if len(refresh_token) > 10 else ("••••••••" if refresh_token else "")
        }

    def save_gmail_api_config(self, refresh_token: str, client_id: str = "", client_secret: str = "", access_token: str = "", account_email: str = "") -> str:
        """Stores Gmail REST API credentials encrypted in Vault."""
        return credentials_vault.store_credential(
            service_name="GMAIL_API",
            credential_type="api_key",
            username=client_id,
            secret_value=refresh_token or access_token,
            host="gmail.googleapis.com",
            port="443",
            email=account_email or DEFAULT_GMAIL_SENDER,
            additional_info={
                "client_secret": client_secret,
                "access_token": access_token,
                "provider": "Google Gmail REST API",
                "protocol": "HTTPS Port 443"
            }
        )

    def list_senders(self) -> List[Dict[str, Any]]:
        """
        Lists all registered email sender profiles stored in Vault.
        Includes default Mangesh AI Studio and any newly added sender accounts.
        """
        senders = []
        found_active = False
        for c in credentials_vault.list_credentials(mask=True):
            if (c.get("credential_type") in ["email", "email_sender"] or 
                c.get("service_name") in ["smtp", "GMAIL_SMTP", "gmail"] or 
                str(c.get("service_name", "")).startswith("EMAIL_SENDER_")):
                meta = c.get("additional_metadata") or {}
                if isinstance(meta, str):
                    try:
                        import json
                        meta = json.loads(meta)
                    except Exception:
                        meta = {}
                is_active = meta.get("is_active", False) or c.get("service_name") == "GMAIL_SMTP"
                if is_active and not found_active:
                    found_active = True
                    is_active = True
                
                senders.append({
                    "id": c.get("id"),
                    "service_name": c.get("service_name"),
                    "sender_email": c.get("email") or c.get("username") or self.default_sender_email,
                    "sender_name": meta.get("sender_name") or self.default_sender_name,
                    "host": c.get("host") or self.default_host,
                    "port": int(c.get("port") or self.default_port),
                    "username": c.get("username") or self.default_sender_email,
                    "security_mode": meta.get("security_mode", "STARTTLS"),
                    "is_active": is_active,
                    "masked_password": "••••••••••••••••"
                })
        
        # If no senders in vault, ensure default profile is returned
        if not senders:
            senders.append({
                "id": "default_gmail",
                "service_name": "GMAIL_SMTP",
                "sender_email": self.default_sender_email,
                "sender_name": self.default_sender_name,
                "host": self.default_host,
                "port": self.default_port,
                "username": self.default_sender_email,
                "security_mode": "STARTTLS",
                "is_active": True,
                "masked_password": "••••••••••••••••"
            })
        return senders

    def add_sender(
        self,
        sender_email: str,
        sender_name: str = "Mangesh AI Studio",
        host: str = "smtp.gmail.com",
        port: int = 587,
        username: Optional[str] = None,
        password: Optional[str] = None,
        security_mode: str = "STARTTLS",
        set_active: bool = False
    ) -> str:
        """Registers a new distinct sender email profile into Credentials Vault."""
        clean_email = sender_email.strip()
        svc_name = f"EMAIL_SENDER_{re.sub(r'[^a-zA-Z0-9_]', '_', clean_email.lower())}"
        effective_pw = password.strip() if password and password.strip() else (self.get_secret_password() or "")
        
        cred_id = credentials_vault.store_credential(
            service_name=svc_name,
            credential_type="email_sender",
            username=username or clean_email,
            secret_value=effective_pw,
            host=host or self.default_host,
            port=str(port or self.default_port),
            email=clean_email,
            mobile_number=self.registered_mobile,
            additional_info={
                "sender_name": sender_name,
                "security_mode": security_mode,
                "is_active": set_active,
                "created_at": time.time()
            }
        )
        if set_active:
            self.set_active_sender(cred_id)
        log_event(f"Added email sender [{cred_id}]: {clean_email} ({sender_name})", component="SMTPClient")
        return cred_id

    def set_active_sender(self, sender_id_or_email: str) -> bool:
        """Sets a sender profile as the active default for outbound email."""
        for c in credentials_vault.list_credentials(mask=False):
            if (c.get("credential_type") in ["email", "email_sender"] or 
                c.get("service_name") in ["smtp", "GMAIL_SMTP", "gmail"] or 
                str(c.get("service_name", "")).startswith("EMAIL_SENDER_")):
                is_match = (
                    c.get("id") == sender_id_or_email or 
                    c.get("email") == sender_id_or_email or 
                    c.get("username") == sender_id_or_email or 
                    c.get("service_name") == sender_id_or_email
                )
                meta = c.get("additional_metadata") or {}
                if isinstance(meta, str):
                    try:
                        import json
                        meta = json.loads(meta)
                    except Exception:
                        meta = {}
                meta["is_active"] = bool(is_match)
                
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE credentials SET additional_metadata = ? WHERE id = ?", (json.dumps(meta), c["id"]))
                    conn.commit()
        return True

    def delete_sender(self, sender_id: str) -> bool:
        """Removes a sender profile from Vault."""
        return credentials_vault.delete_credential(sender_id)

    def test_connection(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        security_mode: Optional[str] = None,
        timeout: float = 10.0,
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Executes a real SMTP connection and authentication verification.
        Accurately reports real connection status, network resolution, SSL handshakes,
        authentication responses, or diagnostic instructions if an app password is required.
        Does NOT send an email during connection test.
        Never exposes passwords or secret tokens in the returned dictionary or logs.
        """
        cfg = self.get_configuration() or {}
        if host is not None:
            target_host = host.strip()
        else:
            target_host = (cfg.get("host") or self.default_host).strip()
        
        if port is not None:
            try:
                target_port = int(port)
            except (ValueError, TypeError):
                target_port = 0
        else:
            target_port = int(cfg.get("port") or self.default_port)
            
        if username is not None:
            target_user = username.strip()
        else:
            target_user = (cfg.get("username") or self.default_sender_email).strip()

        if security_mode is not None:
            target_mode = security_mode.strip().upper()
        else:
            target_mode = (cfg.get("security_mode") or "STARTTLS").strip().upper()
        
        # Resolve password: provided in params, or fetched from Vault/env
        target_password = password.strip() if password and password.strip() else (self.get_secret_password() or "")

        start_time = time.time()
        test_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # 1. Field Validation
        if not target_host:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "success": False,
                "status": "Validation Failed",
                "error_code": "MISSING_HOST",
                "error_category": "VALIDATION_ERROR",
                "host": target_host,
                "port": target_port,
                "username": target_user,
                "security_mode": target_mode,
                "response_time_ms": duration,
                "timestamp": test_timestamp,
                "message": "SMTP Server Host is required.",
                "troubleshooting": "Enter a valid SMTP server hostname (e.g. smtp.gmail.com)."
            }
            self._record_connection_history("GMAIL_SMTP", "smtp", "Validation Failed", duration, res["message"], res)
            return res

        if not (1 <= target_port <= 65535):
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "success": False,
                "status": "Validation Failed",
                "error_code": "INVALID_PORT",
                "error_category": "VALIDATION_ERROR",
                "host": target_host,
                "port": target_port,
                "username": target_user,
                "security_mode": target_mode,
                "response_time_ms": duration,
                "timestamp": test_timestamp,
                "message": f"SMTP Port must be between 1 and 65535. Received: {target_port}",
                "troubleshooting": "Specify standard SMTP ports: 587 (STARTTLS), 465 (SSL/TLS), or 25."
            }
            self._record_connection_history("GMAIL_SMTP", "smtp", "Validation Failed", duration, res["message"], res)
            return res

        if not target_user:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "success": False,
                "status": "Validation Failed",
                "error_code": "MISSING_USERNAME",
                "error_category": "VALIDATION_ERROR",
                "host": target_host,
                "port": target_port,
                "username": target_user,
                "security_mode": target_mode,
                "response_time_ms": duration,
                "timestamp": test_timestamp,
                "message": "Authentication Username / Email is required.",
                "troubleshooting": "Enter your email username (e.g. mangeshbagul15@gmail.com)."
            }
            self._record_connection_history("GMAIL_SMTP", "smtp", "Validation Failed", duration, res["message"], res)
            return res

        # 2. Port & Security Mode Alignment Warnings
        warning_msg = None
        if target_mode == "STARTTLS" and target_port == 465:
            warning_msg = "Notice: Port 465 is typically reserved for SSL/TLS. Port 587 is standard for STARTTLS."
        elif target_mode in ["SSL", "SSL/TLS"] and target_port == 587:
            warning_msg = "Notice: Port 587 is typically used with STARTTLS. Port 465 is standard for SSL/TLS."
        elif target_mode == "PLAIN":
            if target_password:
                duration = round((time.time() - start_time) * 1000, 2)
                res = {
                    "success": False,
                    "status": "Security Violation",
                    "error_code": "UNENCRYPTED_CREDENTIALS_BLOCKED",
                    "error_category": "SECURITY_WARNING",
                    "host": target_host,
                    "port": target_port,
                    "username": target_user,
                    "security_mode": "Plain",
                    "response_time_ms": duration,
                    "timestamp": test_timestamp,
                    "message": "Security Warning: Plain unencrypted SMTP does not encrypt network traffic. Credentials will not be transmitted over an unencrypted connection to protect your secrets.",
                    "troubleshooting": "Select STARTTLS (port 587) or SSL/TLS (port 465) to enable encrypted authentication."
                }
                self._record_connection_history("GMAIL_SMTP", "smtp", "Security Violation", duration, res["message"], res)
                return res

        # 3. Credential Requirement Check
        if not target_password:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "success": False,
                "status": "Not Configured",
                "error_code": "MISSING_CREDENTIALS",
                "error_category": "MISSING_CREDENTIALS",
                "host": target_host,
                "port": target_port,
                "username": target_user,
                "security_mode": target_mode,
                "response_time_ms": duration,
                "timestamp": test_timestamp,
                "message": "Password / App Password is not configured in the Vault, request, or environment.",
                "troubleshooting": "1. Enable 2-Step Verification in Google Account -> Security.\n2. Generate a 16-character App Password at https://myaccount.google.com/apppasswords.\n3. Enter the password in the form and click Save & Encrypt in Vault."
            }
            self._record_connection_history("GMAIL_SMTP", "smtp", "Not Configured", duration, res["message"], res)
            return res

        # 4. Network Reachability & DNS Check
        try:
            sock = socket.create_connection((target_host, target_port), timeout=min(timeout, 5.0))
            sock.close()
        except socket.gaierror as e:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "success": False,
                "status": "Connection Failed",
                "error_code": "DNS_RESOLUTION_FAILURE",
                "error_category": "DNS_RESOLUTION_FAILURE",
                "host": target_host,
                "port": target_port,
                "username": target_user,
                "security_mode": target_mode,
                "response_time_ms": duration,
                "timestamp": test_timestamp,
                "message": f"Unable to resolve host '{target_host}': DNS resolution failed.",
                "troubleshooting": "Check internet connection and DNS settings. Verify outbound access to the SMTP host is permitted."
            }
            self._record_connection_history("GMAIL_SMTP", "smtp", "Connection Failed", duration, res["message"], res)
            return res
        except (socket.timeout, TimeoutError) as e:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "success": False,
                "status": "Connection Timed Out",
                "error_code": "CONNECTION_TIMEOUT",
                "error_category": "NETWORK_TIMEOUT",
                "host": target_host,
                "port": target_port,
                "username": target_user,
                "security_mode": target_mode,
                "response_time_ms": duration,
                "timestamp": test_timestamp,
                "message": f"Connection timed out while connecting to {target_host}:{target_port} (timeout={timeout}s).",
                "troubleshooting": f"Verify port {target_port} is open and not blocked by a local ISP, VPN, or firewall."
            }
            self._record_connection_history("GMAIL_SMTP", "smtp", "Connection Timed Out", duration, res["message"], res)
            return res
        except OSError as e:
            # Automatic fallback to SSL (port 465) if STARTTLS (port 587) is blocked by cloud provider firewall
            fallback_success = False
            if target_host == "smtp.gmail.com" and target_port == 587:
                try:
                    alt_sock = socket.create_connection((target_host, 465), timeout=min(timeout, 4.0))
                    alt_sock.close()
                    target_port = 465
                    target_mode = "SSL/TLS"
                    fallback_success = True
                except Exception:
                    pass
            if not fallback_success:
                duration = round((time.time() - start_time) * 1000, 2)
                is_cloud = bool(os.environ.get("RENDER") or os.environ.get("PORT"))
                cloud_note = " (Cloud Policy: Render Cloud blocks outbound SMTP ports 587 & 25. For instant alerts in cloud, Telegram Alerts is Connected ✅. Run locally on laptop for direct SMTP)." if is_cloud else ""
                res = {
                    "success": False,
                    "status": "Network Unreachable",
                    "error_code": "NETWORK_UNREACHABLE",
                    "error_category": "NETWORK_UNREACHABLE",
                    "host": target_host,
                    "port": target_port,
                    "username": target_user,
                    "security_mode": target_mode,
                    "response_time_ms": duration,
                    "timestamp": test_timestamp,
                    "message": f"Network error reaching {target_host}:{target_port}: {e}{cloud_note}",
                    "troubleshooting": f"Check port {target_port} connectivity. In cloud environments where outbound SMTP is blocked, use TELEGRAM_ALERTS (Online)."
                }
                self._record_connection_history("GMAIL_SMTP", "smtp", "Network Unreachable", duration, res["message"], res)
                return res

        # 5. SMTP Handshake & TLS/SSL Authentication
        server = None
        try:
            context = ssl.create_default_context()
            if target_port == 465 or target_mode in ["SSL", "SSL/TLS"]:
                server = smtplib.SMTP_SSL(target_host, target_port, context=context, timeout=timeout)
                ehlo_code, ehlo_resp = server.ehlo()
            else:
                server = smtplib.SMTP(target_host, target_port, timeout=timeout)
                server.ehlo()
                if target_mode == "STARTTLS":
                    if not server.has_extn("STARTTLS"):
                        duration = round((time.time() - start_time) * 1000, 2)
                        res = {
                            "success": False,
                            "status": "TLS Not Supported",
                            "error_code": "STARTTLS_UNSUPPORTED",
                            "error_category": "TLS_NEGOTIATION_ERROR",
                            "host": target_host,
                            "port": target_port,
                            "username": target_user,
                            "security_mode": target_mode,
                            "response_time_ms": duration,
                            "timestamp": test_timestamp,
                            "message": f"Server {target_host}:{target_port} does not advertise STARTTLS extension.",
                            "troubleshooting": "Use SSL/TLS mode on Port 465 or check SMTP server configuration."
                        }
                        self._record_connection_history("GMAIL_SMTP", "smtp", "TLS Not Supported", duration, res["message"], res)
                        return res
                    server.starttls(context=context)
                    server.ehlo()

            # Perform SMTP Authentication
            code, resp = server.login(target_user, target_password)
            resp_str = resp.decode("utf-8", errors="ignore") if isinstance(resp, bytes) else str(resp)
            duration = round((time.time() - start_time) * 1000, 2)

            res = {
                "success": True,
                "status": "Connected",
                "error_code": None,
                "host": target_host,
                "port": target_port,
                "username": target_user,
                "security_mode": target_mode,
                "response_time_ms": duration,
                "timestamp": test_timestamp,
                "provider_response": f"{code} {resp_str}",
                "warning": warning_msg,
                "message": "SMTP connection and authentication verified successfully.",
                "note": "SMTP handshake and authentication verified. Connection testing does not deliver an email."
            }
            self._record_connection_history("GMAIL_SMTP", "smtp", "Connected", duration, None, res)
            return res

        except smtplib.SMTPAuthenticationError as e:
            duration = round((time.time() - start_time) * 1000, 2)
            err_code = e.smtp_code
            err_msg = e.smtp_error.decode("utf-8", errors="ignore") if isinstance(e.smtp_error, bytes) else str(e.smtp_error)
            
            hint = "Authentication failed. Please verify username and password."
            if "535" in str(err_code) or "5.7.8" in str(err_msg):
                hint = "Gmail Error 535 5.7.8: Username and Password not accepted. Google requires a 16-character App Password (not your standard Google account password). Please generate an App Password at https://myaccount.google.com/apppasswords after enabling 2-Step Verification."
            elif "534" in str(err_code):
                hint = "Gmail Error 534: Additional verification required. Please check your Google security alerts or generate an App Password."

            res = {
                "success": False,
                "status": "Authentication Failed",
                "error_code": "SMTP_AUTH_FAILED",
                "error_category": "AUTHENTICATION_FAILURE",
                "smtp_code": err_code,
                "provider_response": f"{err_code} {err_msg}",
                "host": target_host,
                "port": target_port,
                "username": target_user,
                "security_mode": target_mode,
                "response_time_ms": duration,
                "timestamp": test_timestamp,
                "warning": warning_msg,
                "message": f"SMTP Authentication Error ({err_code}): {err_msg}",
                "troubleshooting": hint
            }
            self._record_connection_history("GMAIL_SMTP", "smtp", "Authentication Failed", duration, res["message"], res)
            return res

        except ssl.SSLError as e:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "success": False,
                "status": "TLS/SSL Handshake Failed",
                "error_code": "SSL_HANDSHAKE_ERROR",
                "error_category": "TLS_NEGOTIATION_ERROR",
                "host": target_host,
                "port": target_port,
                "username": target_user,
                "security_mode": target_mode,
                "response_time_ms": duration,
                "timestamp": test_timestamp,
                "message": f"TLS/SSL negotiation failed on {target_host}:{target_port}: {e}",
                "troubleshooting": "Check port and security mode alignment. Port 465 requires SSL/TLS, port 587 requires STARTTLS."
            }
            self._record_connection_history("GMAIL_SMTP", "smtp", "TLS/SSL Handshake Failed", duration, res["message"], res)
            return res

        except smtplib.SMTPConnectError as e:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "success": False,
                "status": "SMTP Connect Error",
                "error_code": "SMTP_CONNECT_ERROR",
                "error_category": "CONNECTION_ERROR",
                "host": target_host,
                "port": target_port,
                "username": target_user,
                "security_mode": target_mode,
                "response_time_ms": duration,
                "timestamp": test_timestamp,
                "message": f"Failed to establish SMTP connection: {e}",
                "troubleshooting": "Verify the host is running an active SMTP service."
            }
            self._record_connection_history("GMAIL_SMTP", "smtp", "SMTP Connect Error", duration, res["message"], res)
            return res

        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "success": False,
                "status": "Connection Failed",
                "error_code": "SMTP_HANDSHAKE_ERROR",
                "error_category": "GENERAL_SMTP_ERROR",
                "host": target_host,
                "port": target_port,
                "username": target_user,
                "security_mode": target_mode,
                "response_time_ms": duration,
                "timestamp": test_timestamp,
                "message": f"SMTP handshake error: {str(e)}",
                "troubleshooting": "Review SMTP configuration and ensure outbound network access is permitted."
            }
            self._record_connection_history("GMAIL_SMTP", "smtp", "Connection Failed", duration, res["message"], res)
            return res

        finally:
            if server:
                try:
                    server.quit()
                except Exception:
                    pass

    # =========================================================================
    # CLOUD HTTPS EMAIL CONNECTION TESTING (PORT 443)
    # =========================================================================

    def _resend_key_is_valid_for_sending(self, api_key: str, from_email: str) -> bool:
        """
        Quota-free validity check: POST /emails with no `to`. Resend authenticates the key
        first, so a real key answers 422 (missing field) while a bad key answers 401.
        Send-only keys cannot read /api-keys, so this is the only safe way to confirm them.
        """
        try:
            resp = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {api_key}", "User-Agent": "NanoProAI-Studio/2.0"},
                json={"from": from_email, "subject": "NanoPro key validation probe"},
                timeout=8.0,
            )
        except Exception:
            return False
        return resp.status_code == 422

    def test_resend_connection(self) -> Dict[str, Any]:
        """
        Tests Resend REST API connection and key validity over HTTPS Port 443.
        Does not consume monthly email quota (queries api-keys endpoint).
        """
        start_time = time.time()
        test_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        cfg = self.get_resend_config()
        api_key = cfg.get("api_key")

        if not api_key:
            res = {
                "success": False,
                "status": "Not Configured",
                "provider": "Resend API",
                "quota": "3,000 emails/month free",
                "host": "api.resend.com:443",
                "response_time_ms": 0,
                "timestamp": test_ts,
                "message": "Resend API key not configured. Add RESEND_API_KEY to Vault or .env (resend.com provides 3,000 free emails/month).",
                "troubleshooting": "1. Sign up at https://resend.com\n2. Generate an API Key under API Keys tab\n3. Save in Nano Pro Vault under service 'RESEND_EMAIL'."
            }
            self._record_connection_history("EMAIL_RESEND_API", "email_api", "Not Configured", 0, res["message"], res)
            return res

        try:
            url = "https://api.resend.com/api-keys"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "NanoProAI-Studio/2.0"
            }
            resp = requests.get(url, headers=headers, timeout=8.0)
            duration = round((time.time() - start_time) * 1000, 2)

            if resp.status_code == 200:
                data = resp.json()
                keys = data.get("data", [])
                res = {
                    "success": True,
                    "status": "Connected",
                    "provider": "Resend API",
                    "quota": "3,000 emails/month free",
                    "host": "api.resend.com:443 (HTTPS)",
                    "sender": cfg.get("from_email"),
                    "key_count": len(keys),
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "message": f"Resend API authentication verified successfully over HTTPS Port 443 ({duration} ms). Anti-spam firewall bypass active.",
                    "cloud_safe": True
                }
                self._record_connection_history("EMAIL_RESEND_API", "email_api", "Connected", duration, None, res)
                return res
            elif resp.status_code in [401, 403]:
                try:
                    deny_name = str((resp.json() or {}).get("name") or "")
                except Exception:
                    deny_name = ""
                if deny_name == "restricted_api_key" and self._resend_key_is_valid_for_sending(
                    api_key, cfg.get("from_email") or "onboarding@resend.dev"
                ):
                    duration = round((time.time() - start_time) * 1000, 2)
                    res = {
                        "success": True,
                        "status": "Connected (Send-Only Key)",
                        "provider": "Resend API",
                        "quota": "3,000 emails/month free",
                        "host": "api.resend.com:443 (HTTPS)",
                        "sender": cfg.get("from_email"),
                        "key_scope": "sending_access",
                        "response_time_ms": duration,
                        "timestamp": test_ts,
                        "message": f"Resend send-only key verified over HTTPS Port 443 ({duration} ms). Delivery works; dashboard read APIs need a full-access key.",
                        "cloud_safe": True
                    }
                    self._record_connection_history("EMAIL_RESEND_API", "email_api", "Connected", duration, None, res)
                    return res
                res = {
                    "success": False,
                    "status": "Authentication Failed",
                    "provider": "Resend API",
                    "quota": "3,000 emails/month free",
                    "host": "api.resend.com:443",
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "message": f"Resend API returned {resp.status_code}: Invalid or unauthorized API key.",
                    "troubleshooting": "Verify your API key at https://resend.com/api-keys. Keys typically start with 're_'."
                }
                self._record_connection_history("EMAIL_RESEND_API", "email_api", "Authentication Failed", duration, res["message"], res)
                return res
            else:
                res = {
                    "success": False,
                    "status": "API Error",
                    "provider": "Resend API",
                    "host": "api.resend.com:443",
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "message": f"Resend API returned HTTP {resp.status_code}: {resp.text[:150]}"
                }
                self._record_connection_history("EMAIL_RESEND_API", "email_api", "API Error", duration, res["message"], res)
                return res
        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "success": False,
                "status": "Network Error",
                "provider": "Resend API",
                "host": "api.resend.com:443",
                "response_time_ms": duration,
                "timestamp": test_ts,
                "message": f"Network error reaching api.resend.com: {str(e)}"
            }
            self._record_connection_history("EMAIL_RESEND_API", "email_api", "Network Error", duration, res["message"], res)
            return res

    def test_brevo_connection(self) -> Dict[str, Any]:
        """
        Tests Brevo (Sendinblue) REST API connection and account status over HTTPS Port 443.
        Does not consume email credits (queries /v3/account endpoint).
        Retrieves real-time remaining free credits (300/day).
        """
        start_time = time.time()
        test_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        cfg = self.get_brevo_config()
        api_key = cfg.get("api_key")

        if not api_key:
            res = {
                "success": False,
                "status": "Not Configured",
                "provider": "Brevo API (Sendinblue)",
                "quota": "300 emails/day free",
                "host": "api.brevo.com:443",
                "response_time_ms": 0,
                "timestamp": test_ts,
                "message": "Brevo API key not configured. Add BREVO_API_KEY to Vault or .env (brevo.com provides 300 free emails/day).",
                "troubleshooting": "1. Sign up at https://brevo.com\n2. Go to SMTP & API -> API Keys -> Generate a new API key\n3. Save in Nano Pro Vault under service 'BREVO_EMAIL'."
            }
            self._record_connection_history("EMAIL_BREVO_API", "email_api", "Not Configured", 0, res["message"], res)
            return res

        try:
            url = "https://api.brevo.com/v3/account"
            headers = {
                "api-key": api_key,
                "accept": "application/json",
                "User-Agent": "NanoProAI-Studio/2.0"
            }
            resp = requests.get(url, headers=headers, timeout=8.0)
            duration = round((time.time() - start_time) * 1000, 2)

            if resp.status_code == 200:
                data = resp.json()
                acct_email = data.get("email", "")
                plans = data.get("plan", [])
                credits_info = "300 daily"
                for p in plans:
                    if "credits" in p:
                        credits_info = f"{p['credits']} remaining ({p.get('type', 'free')})"
                res = {
                    "success": True,
                    "status": "Connected",
                    "provider": "Brevo (Sendinblue)",
                    "quota": "300 emails/day free",
                    "credits": credits_info,
                    "host": "api.brevo.com:443 (HTTPS)",
                    "account_email": acct_email,
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "message": f"Brevo API authentication verified successfully over HTTPS Port 443 ({duration} ms). Credits: {credits_info}. Anti-spam firewall bypass active.",
                    "cloud_safe": True
                }
                self._record_connection_history("EMAIL_BREVO_API", "email_api", "Connected", duration, None, res)
                return res
            elif resp.status_code in [401, 403]:
                res = {
                    "success": False,
                    "status": "Authentication Failed",
                    "provider": "Brevo API",
                    "quota": "300 emails/day free",
                    "host": "api.brevo.com:443",
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "message": f"Brevo API returned {resp.status_code}: Invalid or unauthorized API key.",
                    "troubleshooting": "Verify your API key at https://app.brevo.com/settings/keys/api. Keys typically start with 'xkeysib-'."
                }
                self._record_connection_history("EMAIL_BREVO_API", "email_api", "Authentication Failed", duration, res["message"], res)
                return res
            else:
                res = {
                    "success": False,
                    "status": "API Error",
                    "provider": "Brevo API",
                    "host": "api.brevo.com:443",
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "message": f"Brevo API returned HTTP {resp.status_code}: {resp.text[:150]}"
                }
                self._record_connection_history("EMAIL_BREVO_API", "email_api", "API Error", duration, res["message"], res)
                return res
        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "success": False,
                "status": "Network Error",
                "provider": "Brevo API",
                "host": "api.brevo.com:443",
                "response_time_ms": duration,
                "timestamp": test_ts,
                "message": f"Network error reaching api.brevo.com: {str(e)}"
            }
            self._record_connection_history("EMAIL_BREVO_API", "email_api", "Network Error", duration, res["message"], res)
            return res

    def _get_gmail_api_access_token(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Obtains a fresh OAuth2 access token for Google Gmail REST API.
        Returns (access_token, error_message).
        """
        cfg = self.get_gmail_api_config()
        if cfg.get("access_token") and not cfg.get("refresh_token"):
            return cfg["access_token"], None

        refresh_token = cfg.get("refresh_token")
        client_id = cfg.get("client_id")
        client_secret = cfg.get("client_secret")

        if not refresh_token:
            return None, "Gmail API Refresh Token not configured in Vault or environment (GMAIL_API_REFRESH_TOKEN)."
        if not client_id:
            return None, "Gmail API Client ID not configured in Vault or environment (GMAIL_API_CLIENT_ID)."

        try:
            token_url = "https://oauth2.googleapis.com/token"
            payload = {
                "client_id": client_id,
                "client_secret": client_secret or "",
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }
            resp = requests.post(token_url, data=payload, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                new_token = data.get("access_token")
                return new_token, None
            else:
                return None, f"Google OAuth2 token refresh failed ({resp.status_code}): {resp.text[:200]}"
        except Exception as e:
            return None, f"Network error during Google OAuth2 token refresh: {str(e)}"

    def test_gmail_api_connection(self) -> Dict[str, Any]:
        """
        Tests Google Gmail REST API connection over HTTPS Port 443.
        Does not use SMTP sockets (ports 25/465/587).
        Queries https://gmail.googleapis.com/gmail/v1/users/me/profile.
        """
        start_time = time.time()
        test_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        token, token_err = self._get_gmail_api_access_token()

        if not token:
            res = {
                "success": False,
                "status": "Not Configured",
                "provider": "Google Gmail REST API",
                "quota": "Unlimited / Standard Gmail Quota",
                "host": "gmail.googleapis.com:443",
                "response_time_ms": 0,
                "timestamp": test_ts,
                "message": token_err or "Gmail REST API credentials not configured.",
                "troubleshooting": "1. In Google Cloud Console, enable Gmail API\n2. Create OAuth2 credentials (Client ID & Client Secret)\n3. Generate a Refresh Token with https://mail.google.com/ scope\n4. Add GMAIL_API_REFRESH_TOKEN and GMAIL_API_CLIENT_ID to Vault or .env."
            }
            self._record_connection_history("EMAIL_GMAIL_API", "email_api", "Not Configured", 0, res["message"], res)
            return res

        try:
            url = "https://gmail.googleapis.com/gmail/v1/users/me/profile"
            headers = {
                "Authorization": f"Bearer {token}",
                "User-Agent": "NanoProAI-Studio/2.0"
            }
            resp = requests.get(url, headers=headers, timeout=8.0)
            duration = round((time.time() - start_time) * 1000, 2)

            if resp.status_code == 200:
                data = resp.json()
                email = data.get("emailAddress", DEFAULT_GMAIL_SENDER)
                total_msgs = data.get("messagesTotal", 0)
                threads = data.get("threadsTotal", 0)
                res = {
                    "success": True,
                    "status": "Connected",
                    "provider": "Google Gmail REST API",
                    "host": "gmail.googleapis.com:443 (HTTPS)",
                    "email": email,
                    "messages_total": total_msgs,
                    "threads_total": threads,
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "message": f"Gmail REST API verified over HTTPS Port 443 ({duration} ms). Active mailbox: {email}. Socket-free cloud delivery operational.",
                    "cloud_safe": True
                }
                self._record_connection_history("EMAIL_GMAIL_API", "email_api", "Connected", duration, None, res)
                return res
            elif resp.status_code in [401, 403]:
                res = {
                    "success": False,
                    "status": "Authentication Failed",
                    "provider": "Google Gmail REST API",
                    "host": "gmail.googleapis.com:443",
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "message": f"Gmail REST API returned {resp.status_code}: Token expired or insufficient OAuth2 permissions.",
                    "troubleshooting": "Ensure your token includes scope 'https://mail.google.com/' or 'https://www.googleapis.com/auth/gmail.send'."
                }
                self._record_connection_history("EMAIL_GMAIL_API", "email_api", "Authentication Failed", duration, res["message"], res)
                return res
            else:
                res = {
                    "success": False,
                    "status": "API Error",
                    "provider": "Google Gmail REST API",
                    "host": "gmail.googleapis.com:443",
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "message": f"Gmail REST API returned HTTP {resp.status_code}: {resp.text[:150]}"
                }
                self._record_connection_history("EMAIL_GMAIL_API", "email_api", "API Error", duration, res["message"], res)
                return res
        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "success": False,
                "status": "Network Error",
                "provider": "Google Gmail REST API",
                "host": "gmail.googleapis.com:443",
                "response_time_ms": duration,
                "timestamp": test_ts,
                "message": f"Network error reaching gmail.googleapis.com: {str(e)}"
            }
            self._record_connection_history("EMAIL_GMAIL_API", "email_api", "Network Error", duration, res["message"], res)
            return res

    def test_email_relay_connection(self) -> Dict[str, Any]:
        """
        Readiness check for the Google Apps Script email relay (HTTPS 443).
        Performs a non-sending GET on the deployment URL so no test mail is dispatched.
        """
        start_time = time.time()
        test_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        cfg = self.get_relay_config()

        if not cfg.get("has_credentials"):
            res = {
                "success": False,
                "status": "Not Configured",
                "provider": "Google Apps Script Relay",
                "host": "script.google.com:443",
                "response_time_ms": 0,
                "timestamp": test_ts,
                "message": "EMAIL_RELAY_URL / EMAIL_RELAY_SECRET not configured.",
                "troubleshooting": "Set EMAIL_RELAY_URL and EMAIL_RELAY_SECRET in Render env or Vault entry EMAIL_RELAY."
            }
            self._record_connection_history("EMAIL_RELAY", "email_relay", "Not Configured", 0, res["message"], res)
            return res

        try:
            resp = requests.get(cfg["url"], timeout=10.0, allow_redirects=True)
            duration = round((time.time() - start_time) * 1000, 2)
            if resp.status_code < 500:
                res = {
                    "success": True,
                    "status": "Connected",
                    "provider": "Google Apps Script Relay",
                    "host": "script.google.com:443 (HTTPS)",
                    "relay_inbox": cfg.get("relay_inbox"),
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "message": f"Relay deployment reachable (HTTP {resp.status_code}, {duration} ms). Delivers to {cfg.get('relay_inbox')}.",
                    "cloud_safe": True
                }
                self._record_connection_history("EMAIL_RELAY", "email_relay", "Connected", duration, None, res)
                return res
            res = {
                "success": False,
                "status": "API Error",
                "provider": "Google Apps Script Relay",
                "host": "script.google.com:443",
                "response_time_ms": duration,
                "timestamp": test_ts,
                "message": f"Relay returned HTTP {resp.status_code}."
            }
            self._record_connection_history("EMAIL_RELAY", "email_relay", "API Error", duration, res["message"], res)
            return res
        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "success": False,
                "status": "Network Error",
                "provider": "Google Apps Script Relay",
                "host": "script.google.com:443",
                "response_time_ms": duration,
                "timestamp": test_ts,
                "message": f"Network error reaching relay: {str(e)}"
            }
            self._record_connection_history("EMAIL_RELAY", "email_relay", "Network Error", duration, res["message"], res)
            return res

    def test_email_failover_cluster(self) -> Dict[str, Any]:
        """
        Tests the readiness of the complete multi-tier cascading email delivery cluster:
        Tier 1: Gmail REST API (HTTPS 443)
        Tier 2: Google Apps Script Relay (HTTPS 443)
        Tier 3: Resend API (HTTPS 443 - 3,000/mo)
        Tier 4: Brevo API (HTTPS 443 - 300/day)
        Tier 5: Gmail SMTP (STARTTLS 587)
        Tier 6: Telegram Emergency Alert Bot
        """
        start_time = time.time()
        test_ts = time.strftime("%Y-%m-%d %H:%M:%S")

        res_gmail_api = self.test_gmail_api_connection()
        res_relay = self.test_email_relay_connection()
        res_resend = self.test_resend_connection()
        res_brevo = self.test_brevo_connection()
        res_smtp = self.test_connection(timeout=3.0)

        # Test Telegram fallback
        telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN") or ""
        tg_ok = False
        if telegram_token:
            try:
                tg_resp = requests.get(f"https://api.telegram.org/bot{telegram_token}/getMe", timeout=3.0)
                tg_ok = tg_resp.status_code == 200 and tg_resp.json().get("ok", False)
            except Exception:
                tg_ok = False

        tiers = [
            {"tier": 1, "name": "Google Gmail REST API", "protocol": "HTTPS Port 443", "quota": "Standard", "status": res_gmail_api.get("status"), "ready": res_gmail_api.get("success", False)},
            {"tier": 2, "name": "Apps Script Relay", "protocol": "HTTPS Port 443", "quota": "Google Apps Script quota", "status": res_relay.get("status"), "ready": res_relay.get("success", False)},
            {"tier": 3, "name": "Resend API", "protocol": "HTTPS Port 443", "quota": "3,000 / month free", "status": res_resend.get("status"), "ready": res_resend.get("success", False)},
            {"tier": 4, "name": "Brevo API", "protocol": "HTTPS Port 443", "quota": "300 / day free", "status": res_brevo.get("status"), "ready": res_brevo.get("success", False)},
            {"tier": 5, "name": "Gmail SMTP", "protocol": "STARTTLS Port 587", "quota": "500 / day", "status": res_smtp.get("status"), "ready": res_smtp.get("success", False)},
            {"tier": 6, "name": "Telegram Emergency Dispatch", "protocol": "HTTPS Port 443", "quota": "Unlimited Alerts", "status": "Online" if tg_ok else "Offline", "ready": tg_ok}
        ]

        ready_count = sum(1 for t in tiers if t["ready"])
        first_ready = next((t["name"] for t in tiers if t["ready"]), "None")
        duration = round((time.time() - start_time) * 1000, 2)

        res = {
            "success": ready_count > 0,
            "status": "Cluster Operational" if ready_count > 0 else "Cluster Unconfigured",
            "active_tiers_count": ready_count,
            "total_tiers": len(tiers),
            "primary_active_tier": first_ready,
            "cascade_pipeline": "Gmail REST API ➔ Apps Script Relay ➔ Resend (3,000/mo) ➔ Brevo (300/day) ➔ Gmail SMTP ➔ Telegram Bot",
            "tiers": tiers,
            "response_time_ms": duration,
            "timestamp": test_ts,
            "message": f"Multi-Tier Email Failover Cluster active with {ready_count}/{len(tiers)} ready channels. Primary: {first_ready}."
        }
        self._record_connection_history("EMAIL_FAILOVER_CLUSTER", "failover_cluster", res["status"], duration, None if res["success"] else "No active tiers", res)
        return res

    # =========================================================================
    # MULTI-PROVIDER TRANSMISSION METHODS (RELAY, RESEND, BREVO, GMAIL API, SMTP, TELEGRAM)
    # =========================================================================

    def send_via_relay(
        self,
        recipient: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        task_id: Optional[str] = None,
        report_name: Optional[str] = None,
        data_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sends an email via the Google Apps Script relay (HTTPS Port 443). Binary attachments go as base64."""
        submission_time = time.time()
        log_id = f"email_relay_{int(submission_time * 1000)}"
        cfg = self.get_relay_config()

        if not cfg.get("has_credentials"):
            return {"success": False, "status": "Not Configured", "error": "EMAIL_RELAY_URL / EMAIL_RELAY_SECRET not configured.", "log_id": log_id, "provider": "Apps Script Relay"}

        relay_inbox = cfg.get("relay_inbox") or self.default_recipient
        payload: Dict[str, Any] = {
            "secret": cfg["secret"],
            "to": recipient or relay_inbox,
            "subject": subject,
            "text": body + (f"\n\nCC: {cc}" if cc else "") + (f"\nBCC: {bcc}" if bcc else "")
        }
        if html_body:
            payload["htmlBody"] = html_body

        if attachments:
            import mimetypes

            for filepath in attachments:
                p = Path(filepath)
                if not (p.exists() and p.is_file()):
                    continue
                mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
                is_text = mime.startswith("text/") or mime in ("application/json", "application/xml")
                try:
                    if is_text and p.stat().st_size <= 512_000:
                        payload["attachmentName"] = p.name
                        payload["attachmentText"] = p.read_text(encoding="utf-8", errors="replace")
                        break
                    if p.stat().st_size <= 5_000_000:
                        payload["attachmentName"] = p.name
                        payload["attachmentMime"] = mime
                        payload["attachmentBase64"] = base64.b64encode(p.read_bytes()).decode("ascii")
                        break
                except Exception as ex:
                    log_event(f"Relay attachment error {p.name}: {ex}", component="SMTPClient", level="WARNING")

        try:
            resp = requests.post(cfg["url"], json=payload, timeout=25.0)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                except Exception:
                    data = {}
                if data.get("ok"):
                    delivered_to = data.get("to") or recipient
                    provider_resp = f"HTTP 200 OK - relay accepted for {delivered_to}"
                    self._record_email_delivery(
                        log_id=log_id, task_id=task_id, report_name=report_name,
                        recipient=delivered_to, subject=subject, data_source=data_source or "Apps Script Relay",
                        report_file_path=(attachments[0] if attachments else None),
                        submission_time=submission_time, provider_response=provider_resp,
                        delivery_status="Delivered by Apps Script Relay", error_details=None
                    )
                    log_event(f"Email [{log_id}] sent via Apps Script Relay to {delivered_to}: Subject '{subject}'", component="SMTPClient")
                    res = {
                        "success": True,
                        "log_id": log_id,
                        "message_id": log_id,
                        "provider": "Apps Script Relay (Port 443)",
                        "status": "Delivered by Apps Script Relay",
                        "recipient": delivered_to,
                        "subject": subject,
                        "submission_time": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    if delivered_to != recipient:
                        res["note"] = f"Relay is pinned to {delivered_to}; message delivered there instead of {recipient}."
                    return res
                return {"success": False, "error": f"Relay rejected the message: {str(data)[:200]}", "status": "Delivery Failed", "log_id": log_id, "provider": "Apps Script Relay"}
            err_msg = f"Relay error (HTTP {resp.status_code}): {resp.text[:200]}"
            return {"success": False, "error": err_msg, "status": "Delivery Failed", "log_id": log_id, "provider": "Apps Script Relay"}
        except Exception as e:
            err_msg = f"Network error during relay dispatch: {str(e)}"
            return {"success": False, "error": err_msg, "status": "Network Error", "log_id": log_id, "provider": "Apps Script Relay"}

    def send_via_resend(
        self,
        recipient: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        task_id: Optional[str] = None,
        report_name: Optional[str] = None,
        data_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sends an email via Resend REST API (HTTPS Port 443)."""
        submission_time = time.time()
        log_id = f"email_resend_{int(submission_time * 1000)}"
        cfg = self.get_resend_config()
        api_key = cfg.get("api_key")

        if not api_key:
            return {"success": False, "status": "Not Configured", "error": "RESEND_API_KEY is not configured.", "log_id": log_id, "provider": "Resend"}

        from_sender = cfg.get("from_email") or "Mangesh AI Studio <onboarding@resend.dev>"
        to_list = [recipient]

        payload: Dict[str, Any] = {
            "from": from_sender,
            "to": to_list,
            "subject": subject,
            "text": body
        }
        if html_body:
            payload["html"] = html_body
        if cc:
            payload["cc"] = [c.strip() for c in cc.split(",") if c.strip()] if isinstance(cc, str) else cc
        if bcc:
            payload["bcc"] = [b.strip() for b in bcc.split(",") if b.strip()] if isinstance(bcc, str) else bcc

        # Attachments
        if attachments:
            att_list = []
            for filepath in attachments:
                p = Path(filepath)
                if p.exists() and p.is_file():
                    try:
                        with open(p, "rb") as f:
                            content_b64 = base64.b64encode(f.read()).decode("utf-8")
                        att_list.append({
                            "filename": p.name,
                            "content": content_b64
                        })
                    except Exception as ex:
                        log_event(f"Resend attachment error {p.name}: {ex}", component="SMTPClient", level="WARNING")
            if att_list:
                payload["attachments"] = att_list

        try:
            url = "https://api.resend.com/emails"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "NanoProAI-Studio/2.0"
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=12.0)

            if resp.status_code in [200, 201]:
                data = resp.json()
                msg_id = data.get("id", log_id)
                provider_resp = f"HTTP 200/201 OK - Message ID: {msg_id}"
                self._record_email_delivery(
                    log_id=log_id, task_id=task_id, report_name=report_name,
                    recipient=recipient, subject=subject, data_source=data_source or "Resend API",
                    report_file_path=(attachments[0] if attachments else None),
                    submission_time=submission_time, provider_response=provider_resp,
                    delivery_status="Accepted by Resend API", error_details=None
                )
                log_event(f"Email [{log_id}] sent via Resend API to {recipient}: Subject '{subject}'", component="SMTPClient")
                return {
                    "success": True,
                    "log_id": log_id,
                    "message_id": msg_id,
                    "provider": "Resend API (Port 443)",
                    "status": "Accepted by Resend API",
                    "recipient": recipient,
                    "subject": subject,
                    "submission_time": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            elif resp.status_code == 429:
                err_msg = f"Resend Quota Exceeded (HTTP 429): Monthly free limit reached."
                return {"success": False, "quota_exceeded": True, "error": err_msg, "status": "Quota Exceeded", "log_id": log_id, "provider": "Resend"}
            else:
                err_msg = f"Resend API error (HTTP {resp.status_code}): {resp.text[:200]}"
                return {"success": False, "error": err_msg, "status": "Delivery Failed", "log_id": log_id, "provider": "Resend"}
        except Exception as e:
            err_msg = f"Network error during Resend dispatch: {str(e)}"
            return {"success": False, "error": err_msg, "status": "Network Error", "log_id": log_id, "provider": "Resend"}

    def send_via_brevo(
        self,
        recipient: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        task_id: Optional[str] = None,
        report_name: Optional[str] = None,
        data_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sends an email via Brevo / Sendinblue REST API (HTTPS Port 443)."""
        submission_time = time.time()
        log_id = f"email_brevo_{int(submission_time * 1000)}"
        cfg = self.get_brevo_config()
        api_key = cfg.get("api_key")

        if not api_key:
            return {"success": False, "status": "Not Configured", "error": "BREVO_API_KEY is not configured.", "log_id": log_id, "provider": "Brevo"}

        sender_email = cfg.get("sender_email") or DEFAULT_GMAIL_SENDER
        sender_name = cfg.get("sender_name") or "Mangesh AI Studio"

        payload: Dict[str, Any] = {
            "sender": {"name": sender_name, "email": sender_email},
            "to": [{"email": recipient, "name": recipient.split("@")[0]}],
            "subject": subject,
            "textContent": body
        }
        if html_body:
            payload["htmlContent"] = html_body
        if cc:
            cc_list = [c.strip() for c in cc.split(",") if c.strip()] if isinstance(cc, str) else cc
            payload["cc"] = [{"email": c} for c in cc_list]
        if bcc:
            bcc_list = [b.strip() for b in bcc.split(",") if b.strip()] if isinstance(bcc, str) else bcc
            payload["bcc"] = [{"email": b} for b in bcc_list]

        if attachments:
            att_list = []
            for filepath in attachments:
                p = Path(filepath)
                if p.exists() and p.is_file():
                    try:
                        with open(p, "rb") as f:
                            content_b64 = base64.b64encode(f.read()).decode("utf-8")
                        att_list.append({
                            "name": p.name,
                            "content": content_b64
                        })
                    except Exception as ex:
                        log_event(f"Brevo attachment error {p.name}: {ex}", component="SMTPClient", level="WARNING")
            if att_list:
                payload["attachment"] = att_list

        try:
            url = "https://api.brevo.com/v3/smtp/email"
            headers = {
                "api-key": api_key,
                "Content-Type": "application/json",
                "accept": "application/json",
                "User-Agent": "NanoProAI-Studio/2.0"
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=12.0)

            if resp.status_code in [200, 201]:
                data = resp.json()
                msg_id = data.get("messageId", log_id)
                provider_resp = f"HTTP 200/201 OK - Message ID: {msg_id}"
                self._record_email_delivery(
                    log_id=log_id, task_id=task_id, report_name=report_name,
                    recipient=recipient, subject=subject, data_source=data_source or "Brevo API",
                    report_file_path=(attachments[0] if attachments else None),
                    submission_time=submission_time, provider_response=provider_resp,
                    delivery_status="Accepted by Brevo API", error_details=None
                )
                log_event(f"Email [{log_id}] sent via Brevo API to {recipient}: Subject '{subject}'", component="SMTPClient")
                return {
                    "success": True,
                    "log_id": log_id,
                    "message_id": msg_id,
                    "provider": "Brevo API (Port 443)",
                    "status": "Accepted by Brevo API",
                    "recipient": recipient,
                    "subject": subject,
                    "submission_time": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            elif resp.status_code in [400, 402, 429] and any(w in resp.text.lower() for w in ["limit", "quota", "credit"]):
                err_msg = f"Brevo Daily Quota Exceeded (HTTP {resp.status_code}): {resp.text[:150]}"
                return {"success": False, "quota_exceeded": True, "error": err_msg, "status": "Quota Exceeded", "log_id": log_id, "provider": "Brevo"}
            else:
                err_msg = f"Brevo API error (HTTP {resp.status_code}): {resp.text[:200]}"
                return {"success": False, "error": err_msg, "status": "Delivery Failed", "log_id": log_id, "provider": "Brevo"}
        except Exception as e:
            err_msg = f"Network error during Brevo dispatch: {str(e)}"
            return {"success": False, "error": err_msg, "status": "Network Error", "log_id": log_id, "provider": "Brevo"}

    def send_via_gmail_api(
        self,
        recipient: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        task_id: Optional[str] = None,
        report_name: Optional[str] = None,
        data_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sends an email via Google Gmail REST API (HTTPS Port 443)."""
        submission_time = time.time()
        log_id = f"email_gmail_api_{int(submission_time * 1000)}"

        token, token_err = self._get_gmail_api_access_token()
        if not token:
            return {"success": False, "status": "Not Configured", "error": token_err or "Gmail REST API not configured.", "log_id": log_id, "provider": "Gmail REST API"}

        msg = MIMEMultipart("mixed")
        msg["From"] = f"{self.default_sender_name} <{self.default_sender_email}>"
        msg["To"] = recipient
        if cc:
            msg["Cc"] = cc if isinstance(cc, str) else ", ".join(cc)
        if bcc:
            msg["Bcc"] = bcc if isinstance(bcc, str) else ", ".join(bcc)
        msg["Subject"] = subject
        msg["Date"] = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

        alt_part = MIMEMultipart("alternative")
        alt_part.attach(MIMEText(body, "plain", "utf-8"))
        if html_body:
            alt_part.attach(MIMEText(html_body, "html", "utf-8"))
        msg.attach(alt_part)

        if attachments:
            for filepath in attachments:
                p = Path(filepath)
                if p.exists() and p.is_file():
                    try:
                        with open(p, "rb") as f:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f'attachment; filename="{p.name}"')
                        msg.attach(part)
                    except Exception as ex:
                        log_event(f"Gmail API attachment error: {ex}", component="SMTPClient", level="WARNING")

        raw_b64 = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8").rstrip("=")

        try:
            url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "NanoProAI-Studio/2.0"
            }
            resp = requests.post(url, headers=headers, json={"raw": raw_b64}, timeout=12.0)

            if resp.status_code in [200, 201]:
                data = resp.json()
                msg_id = data.get("id", log_id)
                provider_resp = f"HTTP 200 OK - Gmail API ID: {msg_id}"
                self._record_email_delivery(
                    log_id=log_id, task_id=task_id, report_name=report_name,
                    recipient=recipient, subject=subject, data_source=data_source or "Gmail REST API",
                    report_file_path=(attachments[0] if attachments else None),
                    submission_time=submission_time, provider_response=provider_resp,
                    delivery_status="Accepted by Gmail REST API", error_details=None
                )
                log_event(f"Email [{log_id}] sent via Gmail REST API to {recipient}: Subject '{subject}'", component="SMTPClient")
                return {
                    "success": True,
                    "log_id": log_id,
                    "message_id": msg_id,
                    "provider": "Gmail REST API (Port 443)",
                    "status": "Accepted by Gmail REST API",
                    "recipient": recipient,
                    "subject": subject,
                    "submission_time": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            elif resp.status_code == 429:
                err_msg = f"Gmail API Quota Exceeded (HTTP 429): Rate limit reached."
                return {"success": False, "quota_exceeded": True, "error": err_msg, "status": "Quota Exceeded", "log_id": log_id, "provider": "Gmail REST API"}
            else:
                err_msg = f"Gmail REST API error (HTTP {resp.status_code}): {resp.text[:200]}"
                return {"success": False, "error": err_msg, "status": "Delivery Failed", "log_id": log_id, "provider": "Gmail REST API"}
        except Exception as e:
            err_msg = f"Network error during Gmail API dispatch: {str(e)}"
            return {"success": False, "error": err_msg, "status": "Network Error", "log_id": log_id, "provider": "Gmail REST API"}

    def send_via_telegram_fallback(
        self,
        recipient: str,
        subject: str,
        body: str,
        failover_trace: List[Dict[str, Any]],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Dispatches an emergency Telegram alert when all email tiers are exhausted or blocked."""
        submission_time = time.time()
        log_id = f"email_tg_fallback_{int(submission_time * 1000)}"
        chat_id = os.environ.get("TELEGRAM_CHAT_ID") or "1200023268"

        trace_summary = "\n".join([f"• {t.get('provider')}: {t.get('status')} - {t.get('error', 'Skipped')}" for t in failover_trace])
        clean_body = (body or "")[:400]

        msg_text = (
            f"🚨 <b>Mangesh Nano Pro AI Studio — Email Failover Alert</b>\n\n"
            f"⚠️ <b>Delivery Status:</b> All outbound email channels were unreachable or exhausted.\n\n"
            f"<b>Target Recipient:</b> {recipient}\n"
            f"<b>Subject:</b> {subject}\n"
            f"<b>Timestamp:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"<b>Failover Cascade Audit:</b>\n{trace_summary}\n\n"
            f"<b>Message Content:</b>\n{clean_body}"
        )

        try:
            from app.core.telegram_router import send_telegram_routed_message
            res = send_telegram_routed_message(category="health", text=msg_text, chat_id=chat_id)
            if res.get("success"):
                self._record_email_delivery(
                    log_id=log_id, task_id=task_id, report_name="Emergency Failover Alert",
                    recipient=recipient, subject=subject, data_source="Telegram Fallback",
                    report_file_path=None, submission_time=submission_time,
                    provider_response=f"Dispatched via {res.get('bot_used')}",
                    delivery_status="Emergency Telegram Fallback Delivered", error_details=None
                )
                return {
                    "success": True,
                    "emergency_dispatched": True,
                    "provider": res.get("bot_used", "Telegram Health Bot"),
                    "status": "Delivered via Telegram Fallback",
                    "recipient": recipient,
                    "subject": subject,
                    "timestamp": submission_time
                }
                return res_data
            else:
                return {"success": False, "error": res.get("error")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_via_smtp(
        self,
        recipient: Optional[str] = None,
        subject: str = '',
        body: str = '',
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        task_id: Optional[str] = None,
        report_name: Optional[str] = None,
        data_source: Optional[str] = None,
        to_email: Optional[str] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Direct SMTP email dispatch (smtp.gmail.com:587)."""
        target_recipient = recipient or to_email or self.default_recipient
        email_body = body or kwargs.get("body_text", "") or kwargs.get("content", "") or ""
        html_content = html_body or kwargs.get("body_html", None)
        if not html_content and email_body:
            escaped_body = email_body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
            html_content = f"""<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #1E293B; background: #FFFFFF; padding: 20px; border-radius: 8px;">{escaped_body}</div>"""

        custom_sender_id = kwargs.get("sender_id") or kwargs.get("from_sender_id")
        active_sender = None
        if custom_sender_id:
            for s in self.list_senders():
                if s["id"] == custom_sender_id or s["sender_email"] == custom_sender_id:
                    active_sender = s
                    break
        else:
            for s in self.list_senders():
                if s.get("is_active"):
                    active_sender = s
                    break

        cfg = self.get_configuration()
        host = active_sender.get("host") if active_sender else cfg.get("host", self.default_host)
        port = int(active_sender.get("port") if active_sender else cfg.get("port", self.default_port))
        user = active_sender.get("username") if active_sender else cfg.get("username", self.default_sender_email)
        sender_email = active_sender.get("sender_email") if active_sender else cfg.get("sender_email", user)
        sender_name = active_sender.get("sender_name") if active_sender else cfg.get("sender_name", self.default_sender_name)
        security_mode = active_sender.get("security_mode") if active_sender else cfg.get("security_mode", "STARTTLS")
        password = self.get_secret_password()

        submission_time = time.time()
        submission_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_id = f"email_{int(submission_time * 1000)}"

        if not password:
            err = "SMTP password not configured in Vault or environment variables."
            self._record_email_delivery(
                log_id=log_id, task_id=task_id, report_name=report_name,
                recipient=target_recipient, subject=subject, data_source=data_source,
                report_file_path=(attachments[0] if attachments else None),
                submission_time=submission_time, provider_response="Rejected: Missing Credentials",
                delivery_status="Delivery Failed", error_details=err
            )
            return {"success": False, "status": "Delivery Failed", "error": err, "log_id": log_id}

        msg = MIMEMultipart("mixed")
        msg["From"] = f"{sender_name} <{sender_email}>"
        msg["To"] = target_recipient
        if cc:
            msg["Cc"] = cc if isinstance(cc, str) else ", ".join(cc)
        msg["Subject"] = subject
        msg["Date"] = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

        alt_part = MIMEMultipart("alternative")
        alt_part.attach(MIMEText(email_body, "plain", "utf-8"))
        if html_content:
            alt_part.attach(MIMEText(html_content, "html", "utf-8"))
        msg.attach(alt_part)

        attached_files = []
        if attachments:
            for filepath in attachments:
                p = Path(filepath)
                if p.exists() and p.is_file():
                    try:
                        with open(p, "rb") as f:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f'attachment; filename="{p.name}"')
                        msg.attach(part)
                        attached_files.append(p.name)
                    except Exception as ex:
                        log_event(f"Failed to attach file {p.name}: {ex}", component="SMTPClient", level="WARNING")

        sendmail_recipients = [target_recipient]
        if cc:
            if isinstance(cc, list):
                sendmail_recipients.extend(cc)
            else:
                sendmail_recipients.extend([c.strip() for c in cc.split(",") if c.strip()])
        if bcc:
            if isinstance(bcc, list):
                sendmail_recipients.extend(bcc)
            else:
                sendmail_recipients.extend([b.strip() for b in bcc.split(",") if b.strip()])
        sendmail_recipients = list(dict.fromkeys(sendmail_recipients))

        server = None
        try:
            context = ssl.create_default_context()
            if port == 465 or security_mode == "SSL":
                server = smtplib.SMTP_SSL(host, port, context=context, timeout=12.0)
            else:
                server = smtplib.SMTP(host, port, timeout=12.0)
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()

            server.login(user, password)
            send_resp = server.sendmail(sender_email, sendmail_recipients, msg.as_string())

            provider_resp = "250 2.0.0 OK (Accepted by SMTP Server)"
            delivery_status = "Accepted by SMTP Server"

            self._record_email_delivery(
                log_id=log_id, task_id=task_id, report_name=report_name,
                recipient=target_recipient, subject=subject, data_source=data_source,
                report_file_path=(attachments[0] if attachments else None),
                submission_time=submission_time, provider_response=provider_resp,
                delivery_status=delivery_status, error_details=None
            )

            log_event(f"Email [{log_id}] submitted to {target_recipient}: Subject '{subject}' - Status: {delivery_status}", component="SMTPClient")

            return {
                "success": True,
                "log_id": log_id,
                "status": delivery_status,
                "recipient": target_recipient,
                "subject": subject,
                "submission_time": submission_timestamp,
                "provider_response": provider_resp,
                "attachments": attached_files,
                "note": "SMTP server accepted message for delivery."
            }

        except smtplib.SMTPAuthenticationError as e:
            err_msg = f"SMTP Authentication Failed: {e.smtp_error.decode('utf-8', errors='ignore') if isinstance(e.smtp_error, bytes) else str(e.smtp_error)}"
            self._record_email_delivery(
                log_id=log_id, task_id=task_id, report_name=report_name,
                recipient=target_recipient, subject=subject, data_source=data_source,
                report_file_path=(attachments[0] if attachments else None),
                submission_time=submission_time, provider_response="Authentication Error",
                delivery_status="Delivery Failed", error_details=err_msg
            )
            return {"success": False, "status": "Delivery Failed", "error": err_msg, "log_id": log_id}

        except Exception as e:
            err_msg = f"SMTP Transmission Error: {str(e)}"
            self._record_email_delivery(
                log_id=log_id, task_id=task_id, report_name=report_name,
                recipient=target_recipient, subject=subject, data_source=data_source,
                report_file_path=(attachments[0] if attachments else None),
                submission_time=submission_time, provider_response="Connection/Protocol Error",
                delivery_status="Delivery Failed", error_details=err_msg
            )
            return {"success": False, "status": "Delivery Failed", "error": err_msg, "log_id": log_id}

        finally:
            if server:
                try:
                    server.quit()
                except Exception:
                    pass

    # =========================================================================
    # MULTI-TIER CASCADING AUTO-FAILOVER DISPATCHER
    # =========================================================================

    def send_email_cascading(
        self,
        recipient: Optional[str] = None,
        subject: str = '',
        body: str = '',
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        preferred_provider: str = 'auto',
        allow_failover: bool = True,
        task_id: Optional[str] = None,
        report_name: Optional[str] = None,
        data_source: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Multi-Tier Cascading Email Delivery Engine:
        Tier 1: Google Gmail REST API (Port 443)
        Tier 2: Google Apps Script Relay (Port 443)
        Tier 3: Resend API (Port 443 - 3,000/mo)
        Tier 4: Brevo API (Port 443 - 300/day)
        Tier 5: Gmail SMTP (Port 587)
        Tier 6: Telegram Emergency Bot
        """
        extra_kwargs = dict(kwargs)
        target_recipient = recipient or extra_kwargs.pop("to_email", None) or extra_kwargs.pop("recipient", None) or self.default_recipient
        email_body = body or extra_kwargs.pop("body_text", "") or extra_kwargs.pop("content", "") or ""
        html_content = html_body or extra_kwargs.pop("body_html", None)
        if not html_content and email_body:
            escaped_body = email_body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
            html_content = f"""<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #1E293B; background: #FFFFFF; padding: 20px; border-radius: 8px;">{escaped_body}</div>"""

        cc = extra_kwargs.pop("cc", None)
        bcc = extra_kwargs.pop("bcc", None)
        failover_trace: List[Dict[str, Any]] = []

        prov = (preferred_provider or "auto").lower()
        if prov == "resend":
            providers = ["resend", "relay", "brevo", "gmail_api", "smtp"] if allow_failover else ["resend"]
        elif prov == "brevo":
            providers = ["brevo", "relay", "resend", "gmail_api", "smtp"] if allow_failover else ["brevo"]
        elif prov in ["relay", "apps_script", "appsscript"]:
            providers = ["relay", "resend", "brevo", "gmail_api", "smtp"] if allow_failover else ["relay"]
        elif prov in ["gmail_api", "gmailrest", "gmail_rest"]:
            providers = ["gmail_api", "relay", "resend", "brevo", "smtp"] if allow_failover else ["gmail_api"]
        elif prov in ["smtp", "gmail_smtp"]:
            providers = ["smtp", "relay", "resend", "brevo", "gmail_api"] if allow_failover else ["smtp"]
        else:
            providers = ["gmail_api", "relay", "resend", "brevo", "smtp"]

        for p_name in providers:
            if p_name == "gmail_api":
                g_cfg = self.get_gmail_api_config()
                if not g_cfg.get("has_credentials"):
                    failover_trace.append({"provider": "Gmail REST API", "status": "Skipped", "error": "Credentials not configured"})
                    continue
                log_event("Attempting email dispatch via Gmail REST API (Tier 1)...", component="SMTPClient")
                res = self.send_via_gmail_api(target_recipient, subject, email_body, html_content, attachments, cc, bcc, task_id, report_name, data_source)
                if res.get("success"):
                    res["failover_trace"] = failover_trace
                    return res
                failover_trace.append({"provider": "Gmail REST API", "status": "Failed", "error": res.get("error", "Unknown error")})

            elif p_name == "relay":
                rel_cfg = self.get_relay_config()
                if not rel_cfg.get("has_credentials"):
                    failover_trace.append({"provider": "Apps Script Relay", "status": "Skipped", "error": "EMAIL_RELAY_URL / EMAIL_RELAY_SECRET not configured"})
                    continue
                log_event("Attempting email dispatch via Apps Script Relay (Tier 2)...", component="SMTPClient")
                res = self.send_via_relay(target_recipient, subject, email_body, html_content, attachments, cc, bcc, task_id, report_name, data_source)
                if res.get("success"):
                    res["failover_trace"] = failover_trace
                    return res
                failover_trace.append({"provider": "Apps Script Relay", "status": "Failed", "error": res.get("error", "Unknown error")})

            elif p_name == "resend":
                r_cfg = self.get_resend_config()
                if not r_cfg.get("has_credentials"):
                    failover_trace.append({"provider": "Resend API", "status": "Skipped", "error": "RESEND_API_KEY not configured"})
                    continue
                log_event("Attempting email dispatch via Resend API (Tier 2 - 3,000/mo)...", component="SMTPClient")
                res = self.send_via_resend(target_recipient, subject, email_body, html_content, attachments, cc, bcc, task_id, report_name, data_source)
                if res.get("success"):
                    res["failover_trace"] = failover_trace
                    return res
                failover_trace.append({"provider": "Resend API", "status": "Failed", "error": res.get("error", "Unknown error")})

            elif p_name == "brevo":
                b_cfg = self.get_brevo_config()
                if not b_cfg.get("has_credentials"):
                    failover_trace.append({"provider": "Brevo API", "status": "Skipped", "error": "BREVO_API_KEY not configured"})
                    continue
                log_event("Attempting email dispatch via Brevo API (Tier 3 - 300/day)...", component="SMTPClient")
                res = self.send_via_brevo(target_recipient, subject, email_body, html_content, attachments, cc, bcc, task_id, report_name, data_source)
                if res.get("success"):
                    res["failover_trace"] = failover_trace
                    return res
                failover_trace.append({"provider": "Brevo API", "status": "Failed", "error": res.get("error", "Unknown error")})

            elif p_name == "smtp":
                log_event("Attempting email dispatch via Standard Gmail SMTP (Tier 4)...", component="SMTPClient")
                res = self.send_via_smtp(
                    recipient=target_recipient,
                    subject=subject,
                    body=email_body,
                    html_body=html_content,
                    attachments=attachments,
                    task_id=task_id,
                    report_name=report_name,
                    data_source=data_source,
                    cc=cc,
                    bcc=bcc,
                    **extra_kwargs
                )
                if res.get("success"):
                    res["failover_trace"] = failover_trace
                    res["provider"] = "Gmail SMTP (Port 587)"
                    return res
                failover_trace.append({"provider": "Gmail SMTP", "status": "Failed", "error": res.get("error", "SMTP error")})

        log_event(f"All email dispatch tiers failed for {target_recipient}. Triggering Telegram Emergency Fallback...", component="SMTPClient", level="WARNING")
        tg_res = self.send_via_telegram_fallback(target_recipient, subject, email_body, failover_trace, task_id)
        if tg_res.get("success"):
            return {
                "success": True,
                "status": "Delivered via Telegram Emergency Fallback",
                "provider": "Telegram Emergency Bot (Port 443)",
                "note": "All primary email APIs failed or were not configured. Alert was safely delivered to your Telegram bot.",
                "recipient": target_recipient,
                "subject": subject,
                "failover_trace": failover_trace
            }

        return {
            "success": False,
            "status": "Delivery Failed Across All Tiers",
            "error": "All email providers and Telegram fallback failed.",
            "recipient": target_recipient,
            "subject": subject,
            "failover_trace": failover_trace
        }

    def send_email(
        self,
        recipient: Optional[str] = None,
        subject: str = '',
        body: str = '',
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        task_id: Optional[str] = None,
        report_name: Optional[str] = None,
        data_source: Optional[str] = None,
        to_email: Optional[str] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        preferred_provider: str = 'auto',
        **kwargs
    ) -> Dict[str, Any]:
        """Dispatches an email with automatic multi-tier cloud failover."""
        return self.send_email_cascading(
            recipient=recipient,
            subject=subject,
            body=body,
            html_body=html_body,
            attachments=attachments,
            task_id=task_id,
            report_name=report_name,
            data_source=data_source,
            to_email=to_email,
            cc=cc,
            bcc=bcc,
            preferred_provider=preferred_provider,
            **kwargs
        )

    def send_test_email(self, recipient: Optional[str] = None, provider: str = "auto") -> Dict[str, Any]:
        """Sends an explicit test email with configuration confirmation and cascading failover."""
        target = recipient or self.default_recipient
        prov_label = provider.upper() if provider != "auto" else "Auto-Failover Cascade"
        subject = f"Mangesh Nano Pro AI Studio — Email Integration Test [{prov_label}] ({time.strftime('%Y-%m-%d %H:%M')})"
        body = (
            f"Hello Mangesh,\n\n"
            f"This is an automated test message from your Mangesh Nano Pro AI Studio.\n\n"
            f"Delivery Architecture Details:\n"
            f"- Requested Mode: {prov_label}\n"
            f"- Registered Recipient: {target}\n"
            f"- Mobile Notification: {self.registered_mobile}\n"
            f"- Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"- Cloud Safe Protocol: HTTPS Port 443 with Multi-Tier Cascading Failover\n\n"
            f"Active Tiers:\n"
            f"1. Google Gmail REST API (Direct Port 443)\n"
            f"2. Resend API (3,000 Free Emails / Month)\n"
            f"3. Brevo API (300 Free Emails / Day)\n"
            f"4. Gmail SMTP (TLS 587)\n"
            f"5. Telegram Emergency Alert Bot\n\n"
            f"This confirms your secure Credential Vault and multi-provider email pipeline is functional."
        )
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; padding: 20px; border: 1px solid #10b981; border-radius: 8px; background: #f0fdf4;">
            <h2 style="color: #047857; margin-top: 0;">Mangesh Nano Pro AI Studio</h2>
            <p><strong>Cloud Email Verification &amp; Failover Successful</strong></p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <tr><td style="padding: 6px 0; color: #475569;"><strong>Requested Provider:</strong></td><td><strong>{prov_label}</strong></td></tr>
                <tr><td style="padding: 6px 0; color: #475569;"><strong>Sender:</strong></td><td>{self.default_sender_email}</td></tr>
                <tr><td style="padding: 6px 0; color: #475569;"><strong>Recipient:</strong></td><td>{target}</td></tr>
                <tr><td style="padding: 6px 0; color: #475569;"><strong>Mobile:</strong></td><td>{self.registered_mobile}</td></tr>
                <tr><td style="padding: 6px 0; color: #475569;"><strong>Security:</strong></td><td>HTTPS Port 443 / TLS 587</td></tr>
                <tr><td style="padding: 6px 0; color: #475569;"><strong>Timestamp:</strong></td><td>{time.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
            </table>
            <p style="margin-top: 20px; font-size: 12px; color: #64748b;">Notice: This confirms delivery via Mangesh Nano Pro Multi-Tier Email Dispatcher.</p>
        </div>
        """
        return self.send_email(recipient=target, subject=subject, body=body, html_body=html, preferred_provider=provider, task_id="test_email")

    def _record_connection_history(self, conn_name: str, service_type: str, status: str, response_time: float, error: Optional[str], details: Dict[str, Any]):
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS connection_history (
                    id TEXT PRIMARY KEY,
                    connection_name TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    response_time_ms REAL,
                    active_user TEXT,
                    active_role TEXT,
                    active_database TEXT,
                    active_schema TEXT,
                    error_message TEXT,
                    tested_at REAL NOT NULL,
                    details_json TEXT
                )""")
                import json
                import uuid
                cursor.execute("""
                INSERT INTO connection_history (
                    id, connection_name, service_type, status, response_time_ms,
                    active_user, active_role, active_database, active_schema,
                    error_message, tested_at, details_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"hist_{int(time.time()*1000)}_{uuid.uuid4().hex[:8]}", conn_name, service_type, status, response_time,
                    details.get("username"), None, None, None, error, time.time(), json.dumps(details)
                ))
                conn.commit()
        except Exception as e:
            log_event(f"Failed to record connection history: {e}", component="SMTPClient", level="WARNING")

    def _record_email_delivery(
        self,
        log_id: str,
        task_id: Optional[str],
        report_name: Optional[str],
        recipient: str,
        subject: str,
        data_source: Optional[str],
        report_file_path: Optional[str],
        submission_time: float,
        provider_response: str,
        delivery_status: str,
        error_details: Optional[str]
    ):
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_delivery_ledger (
                    id TEXT PRIMARY KEY,
                    task_id TEXT,
                    report_name TEXT,
                    recipient TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    data_source TEXT,
                    report_file_path TEXT,
                    submission_time REAL NOT NULL,
                    provider_response TEXT,
                    delivery_status TEXT NOT NULL,
                    error_details TEXT,
                    created_at REAL NOT NULL
                )""")
                cursor.execute("""
                INSERT OR REPLACE INTO email_delivery_ledger (
                    id, task_id, report_name, recipient, subject, data_source,
                    report_file_path, submission_time, provider_response,
                    delivery_status, error_details, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log_id, task_id, report_name or "Ad-hoc Report", recipient, subject,
                    data_source or "Internal", report_file_path, submission_time,
                    provider_response, delivery_status, error_details, time.time()
                ))
                conn.commit()
        except Exception as e:
            log_event(f"Failed to record email delivery ledger: {e}", component="SMTPClient", level="WARNING")

        # Also log to communication_logs table for multi-channel history
        try:
            db.add_communication_log(
                log_id=log_id,
                channel="email",
                recipient=recipient,
                content=subject,
                subject=subject,
                status="sent" if "Accepted" in delivery_status else "failed",
                response_data=provider_response,
                error_message=error_details
            )
        except Exception:
            pass

    def list_delivery_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns email delivery history records."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_delivery_ledger (
                    id TEXT PRIMARY KEY,
                    task_id TEXT,
                    report_name TEXT,
                    recipient TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    data_source TEXT,
                    report_file_path TEXT,
                    submission_time REAL NOT NULL,
                    provider_response TEXT,
                    delivery_status TEXT NOT NULL,
                    error_details TEXT,
                    created_at REAL NOT NULL
                )""")
                cursor.execute("SELECT * FROM email_delivery_ledger ORDER BY submission_time DESC LIMIT ?", (limit,))
                return [dict(r) for r in cursor.fetchall()]
        except Exception:
            return []

smtp_client = SMTPClient()
