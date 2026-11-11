import ast
import asyncio
import hashlib
import hmac
import json
import os
import re
import sqlite3
import sys
import threading
import time
import unittest
import uuid
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]


def extract_class(path, name, methods, **namespace):
    source = ast.parse((ROOT / path).read_text(encoding="utf-8-sig"))
    cls = next(node for node in source.body if isinstance(node, ast.ClassDef) and node.name == name)
    cls.body = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name in methods]
    scope = {
        "Any": Any, "Dict": Dict, "List": List, "Optional": Optional, "Tuple": Tuple,
        "os": os, "re": re, "time": time, "uuid": uuid, "json": json,
        "hashlib": hashlib, "hmac": hmac, "log_event": Mock(), **namespace,
    }
    exec(compile(ast.Module(body=[cls], type_ignores=[]), path, "exec"), scope)
    return scope[name]


class WhatsAppOtpBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            "WHATSAPP_APP_SECRET": "synthetic-webhook-secret",
            "WHATSAPP_CLOUD_ACCESS_TOKEN": "synthetic-access-token",
            "WHATSAPP_CLOUD_PHONE_ID": "synthetic-phone-id",
        }, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.conn = sqlite3.connect(":memory:")
        self.addCleanup(self.conn.close)
        self.conn.executescript("""
            CREATE TABLE auth_otps (
                id TEXT, identifier TEXT, otp_code TEXT, channel TEXT,
                created_at REAL, expires_at REAL, is_used INTEGER
            );
            CREATE TABLE whatsapp_channel_state (key TEXT PRIMARY KEY, value TEXT, updated_at REAL);
        """)
        auth = extract_class("app/core/auth_manager.py", "AuthManager", {
            "_normalize_phone", "_whatsapp_otp_text", "_whatsapp_login_link", "_issue_otp",
            "send_otp_on_whatsapp_request", "generate_and_send_otp", "verify_otp_and_login",
        })
        self.auth = auth()
        self.auth._get_connection = lambda: self.conn
        self.auth._notify_telegram = Mock()
        guardian_cls = extract_class("app/core/whatsapp_guardian.py", "WhatsAppAutonomousGuardian", {
            "_save_state", "record_inbound", "is_window_open_for",
        }, db=SimpleNamespace(get_connection=lambda: self.conn))
        self.guardian = guardian_cls()
        self.guardian._lock = threading.Lock()
        self.sender = Mock(return_value={"success": True, "status": "accepted"})
        self.communication = SimpleNamespace(send_whatsapp_cloud_api=self.sender)
        modules = {}
        for name, member, obj in [
            ("app.core.communication_center", "communication_center", self.communication),
            ("app.core.whatsapp_guardian", "whatsapp_guardian", self.guardian),
        ]:
            module = ModuleType(name)
            setattr(module, member, obj)
            modules[name] = module
        self.modules = patch.dict(sys.modules, modules)
        self.modules.start()
        self.addCleanup(self.modules.stop)
        webhook_cls = extract_class("app/core/whatsapp_webhook_handler.py", "WhatsAppWebhookHandler", {
            "verify_payload_signature", "verify_webhook",
        }, credentials_vault=SimpleNamespace(get_credential=lambda name: None))
        self.webhook = webhook_cls()
        self.webhook.verify_token = ""

    def test_normalization_matches_formatted_phone(self):
        self.assertEqual(self.auth._normalize_phone("+91 84337-55448"), "+918433755448")
        self.assertEqual(self.auth._normalize_phone("8433755448"), "+918433755448")

    def test_invalid_phone_boundaries(self):
        for value in ["", "12345", "+" + "1" * 16, "letters8433755448", "+000000000000"]:
            with self.subTest(value=value):
                self.assertIsNone(self.auth._normalize_phone(value))

    def test_closed_window_requests_login_without_issuing_code(self):
        result = self.auth.generate_and_send_otp("8433755448")
        self.assertEqual(result["status"], "pending")
        self.assertEqual(result["delivery"], "reply_required")
        self.assertTrue(result["whatsapp_link"].endswith("?text=LOGIN"))
        self.assertNotIn("otp_code", result)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM auth_otps").fetchone()[0], 0)
        self.sender.assert_not_called()

    def test_user_window_is_not_shared_between_numbers(self):
        self.guardian.record_inbound("918433755448", "User", "LOGIN")
        self.assertTrue(self.guardian.is_window_open_for("+918433755448"))
        self.assertFalse(self.guardian.is_window_open_for("+919876543210"))
        self.assertEqual(self.auth.generate_and_send_otp("9876543210")["status"], "pending")

    def test_expired_window_requires_new_login_message(self):
        self.guardian._save_state("inbound:918433755448", str(time.time() - 86401))
        self.assertFalse(self.guardian.is_window_open_for("+918433755448"))

    def test_inbound_login_sends_sensitive_code_only_to_sender(self):
        result = self.auth.send_otp_on_whatsapp_request("918433755448")
        self.assertEqual(result["status"], "success")
        record = self.conn.execute("SELECT otp_code, expires_at-created_at FROM auth_otps").fetchone()
        self.assertRegex(record[0], r"^[0-9]{6}$")
        self.assertEqual(record[1], 300)
        sent = self.sender.call_args.kwargs
        self.assertEqual(sent["phone"], "+918433755448")
        self.assertIn(record[0], sent["message"])
        self.assertTrue(sent["sensitive"])
        self.assertNotIn(record[0], json.dumps(result))
        self.auth._notify_telegram.assert_not_called()

    def test_open_window_accepted_is_not_claimed_delivered(self):
        self.guardian.record_inbound("918433755448", "User", "Hi")
        result = self.auth.generate_and_send_otp("8433755448")
        self.assertEqual(result["delivery"], "accepted")
        self.assertTrue(self.sender.call_args.kwargs["sensitive"])
        self.auth._notify_telegram.assert_not_called()

    def test_template_sends_sensitive_parameters(self):
        with patch.dict(os.environ, {"WHATSAPP_CLOUD_OTP_TEMPLATE": "test_otp"}):
            result = self.auth.generate_and_send_otp("8433755448")
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.sender.call_args.kwargs["template_name"], "test_otp")
        self.assertTrue(self.sender.call_args.kwargs["sensitive"])
        self.assertNotIn("otp_code", result)

    def test_otp_rotation_and_rate_limit(self):
        for _ in range(5):
            self.assertEqual(self.auth.send_otp_on_whatsapp_request("918433755448")["status"], "success")
        self.assertEqual(self.auth.send_otp_on_whatsapp_request("918433755448")["status"], "error")
        self.assertEqual(self.sender.call_count, 5)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM auth_otps WHERE is_used=0").fetchone()[0], 1)

    def test_dispatch_error_does_not_expose_code(self):
        self.sender.return_value = {"success": False}
        self.guardian.record_inbound("918433755448", "User", "Hi")
        result = self.auth.generate_and_send_otp("8433755448")
        self.assertEqual(result["status"], "error")
        self.assertNotIn("otp_code", result)
        self.auth._notify_telegram.assert_not_called()

    def test_malformed_verification_code_rejected_before_lookup(self):
        for code in ["123", "1234567", "abcdef", "１２３４５６"]:
            with self.subTest(code=code):
                self.assertEqual(self.auth.verify_otp_and_login("8433755448", code)["status"], "error")

    def signature(self, body):
        return "sha256=" + hmac.new(b"synthetic-webhook-secret", body, hashlib.sha256).hexdigest()

    def test_signature_requires_exact_raw_body_and_app_secret(self):
        body = b'{"entry": []}'
        signature = self.signature(body)
        self.assertTrue(self.webhook.verify_payload_signature(body, signature))
        self.assertFalse(self.webhook.verify_payload_signature(body + b" ", signature))
        self.assertFalse(self.webhook.verify_payload_signature(body, ""))
        self.assertFalse(self.webhook.verify_payload_signature(body, "sha256=" + "0" * 64))
        with patch.dict(os.environ, {"WHATSAPP_APP_SECRET": ""}):
            self.assertFalse(self.webhook.verify_payload_signature(body, signature))

    def test_empty_handshake_token_cannot_subscribe(self):
        self.assertEqual(self.webhook.verify_webhook("subscribe", "", "123"), (False, None))

    def test_http_boundary_does_not_dispatch_unsigned_payload(self):
        source = ast.parse((ROOT / "main.py").read_text(encoding="utf-8-sig"))
        route = next(node for node in source.body if isinstance(node, ast.AsyncFunctionDef) and node.name == "api_whatsapp_webhook_receive")
        route.decorator_list = []
        self.webhook.process_incoming_payload = Mock(return_value={"status": "accepted"})
        module = ModuleType("app.core.whatsapp_webhook_handler")
        module.whatsapp_webhook_handler = self.webhook
        scope = {
            "Request": Any,
            "JSONResponse": lambda content, status_code=200: SimpleNamespace(content=content, status_code=status_code),
        }
        exec(compile(ast.Module(body=[route], type_ignores=[]), "main.py", "exec"), scope)
        body = b'{"entry": []}'
        with patch.dict(sys.modules, {module.__name__: module}):
            for signature, expected in [("", 403), (self.signature(body), 200)]:
                async def read_body():
                    return body
                request = SimpleNamespace(body=read_body, headers={"X-Hub-Signature-256": signature})
                response = asyncio.run(scope[route.name](request))
                self.assertEqual(response.status_code, expected)
        self.webhook.process_incoming_payload.assert_called_once_with({"entry": []})

    def test_sensitive_sender_never_mirrors_or_records_otp(self):
        post = Mock(return_value=SimpleNamespace(
            status_code=200, content=True,
            json=lambda: {"messages": [{"id": "synthetic-message-id"}], "contacts": [{"wa_id": "918433755448"}]},
        ))
        sender_cls = extract_class("app/core/communication_center.py", "CommunicationCenter", {
            "send_whatsapp_cloud_api",
        }, requests=SimpleNamespace(Session=lambda: SimpleNamespace(post=post)))
        sender = sender_cls()
        sender.record_ledger_entry = Mock()
        text = "synthetic authentication code"
        result = sender.send_whatsapp_cloud_api("918433755448", text, sensitive=True, template_name="test_otp", template_params=["123456"])
        self.assertEqual(result["status"], "accepted")
        components = post.call_args.kwargs["json"]["template"]["components"]
        self.assertEqual(components[0]["parameters"], components[1]["parameters"])
        self.assertEqual(components[1]["sub_type"], "url")
        self.assertNotIn(text, json.dumps(sender.record_ledger_entry.call_args.kwargs))
        self.assertNotIn("response", sender.record_ledger_entry.call_args.kwargs["metadata"])
        post.return_value = SimpleNamespace(status_code=400, content=True, json=lambda: {"error": {"code": 131047, "message": text}})
        result = sender.send_whatsapp_cloud_api("918433755448", text, sensitive=True)
        self.assertFalse(result["success"])
        self.assertNotIn(text, json.dumps(result))
        self.assertEqual(post.call_count, 2)
        post.side_effect = RuntimeError(text)
        result = sender.send_whatsapp_cloud_api("918433755448", text, sensitive=True)
        self.assertFalse(result["success"])
        self.assertNotIn(text, json.dumps(result))


if __name__ == "__main__":
    unittest.main()
