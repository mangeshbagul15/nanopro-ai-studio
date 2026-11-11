"""Exercise payment verification without importing app or contacting any services."""

import ast
import base64
import builtins
import hashlib
import hmac
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict
import unittest
from unittest.mock import Mock


GATEWAY_PATH = Path(__file__).resolve().parents[1] / "app" / "payments" / "razorpay_gateway.py"


class RequestException(Exception):
    pass


class ConnectionError(RequestException):
    pass


class Timeout(RequestException):
    pass


class JSONDecodeError(RequestException, ValueError):
    """Model requests' JSON error, which is also a RequestException."""


class RazorpayVerificationBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = ast.parse(GATEWAY_PATH.read_text(encoding="utf-8"), filename=str(GATEWAY_PATH))
        names = {"PaymentError", "_money", "_auth_header", "verify_payment"}
        nodes = [
            node for node in source.body
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in names
        ]
        if {node.name for node in nodes} != names:
            raise AssertionError("Required verification definitions were not found")
        # Compile only these definitions: no module imports, vault, database or startup code.
        cls.gateway_code = compile(ast.Module(body=nodes, type_ignores=[]), str(GATEWAY_PATH), "exec")

    def setUp(self):
        self.order_id = "order_boundary"
        self.payment_id = "pay_boundary"
        self.key_id = "rzp_test_stub"
        self.key_secret = "synthetic-unit-test-secret"
        self.row = {
            "order_id": self.order_id,
            "status": "created",
            "plan_id": "ai_awaaz_starter",
            "amount_paise": 35282,
            "currency": "INR",
        }
        self.plan = {"id": self.row["plan_id"], "name": "Stub plan"}
        self.get = Mock(return_value=self.response())
        self.mark_paid = Mock(side_effect=self.record_paid)
        self.credentials = Mock(return_value=(self.key_id, self.key_secret))
        self.namespace = {
            "Any": Any,
            "Dict": Dict,
            "base64": base64,
            "hashlib": hashlib,
            "hmac": hmac,
            "requests": SimpleNamespace(get=self.get, RequestException=RequestException),
            "RAZORPAY_BASE_URL": "https://api.razorpay.com/v1",
            "CURRENCY": "INR",
            "_get_order_row": Mock(side_effect=lambda order_id: self.row),
            "_mark_paid": self.mark_paid,
            "get_credentials": self.credentials,
            "log_event": Mock(),
            "PLANS": {self.row["plan_id"]: self.plan},
            "plan_summary": Mock(return_value=self.plan),
        }
        exec(self.gateway_code, self.namespace)
        self.verify_payment = self.namespace["verify_payment"]
        self.PaymentError = self.namespace["PaymentError"]
        self.signature = hmac.new(
            self.key_secret.encode("utf-8"),
            f"{self.order_id}|{self.payment_id}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def record_paid(self, order_id, payment_id, mode):
        self.row.update(status="paid", payment_id=payment_id, gateway_mode=mode)

    def response(self, status_code=200, **changes):
        payload = {
            "order_id": self.order_id,
            "amount": self.row["amount_paise"],
            "currency": self.row.get("currency") or "INR",
            "status": "captured",
        }
        payload.update(changes)
        return SimpleNamespace(status_code=status_code, json=Mock(return_value=payload))

    def verify(self):
        return self.verify_payment(self.order_id, self.payment_id, self.signature)

    def assert_rejected(self, code, status_code):
        with self.assertRaises(self.PaymentError) as caught:
            self.verify()
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(caught.exception.status_code, status_code)
        self.mark_paid.assert_not_called()
        self.assertEqual(self.row["status"], "created")
        self.assertNotIn("payment_id", self.row)

    def test_captured_success_preserves_response_and_marks_once(self):
        result = self.verify()
        self.assertEqual(result, {
            "status": "success",
            "already_verified": False,
            "order_id": self.order_id,
            "payment_id": self.payment_id,
            "plan": self.plan,
            "amount_display": "₹352.82",
            "mode": "test",
            "activated": True,
        })
        self.mark_paid.assert_called_once_with(self.order_id, self.payment_id, "test")
        expected_auth = base64.b64encode(f"{self.key_id}:{self.key_secret}".encode()).decode("ascii")
        self.get.assert_called_once_with(
            f"https://api.razorpay.com/v1/payments/{self.payment_id}",
            headers={"Authorization": f"Basic {expected_auth}"},
            timeout=15,
        )

    def test_captured_success_uses_recorded_currency(self):
        self.row["currency"] = "USD"
        self.get.return_value = self.response(currency="USD")
        self.assertTrue(self.verify()["activated"])
        self.mark_paid.assert_called_once()

    def test_legacy_row_without_currency_defaults_to_inr(self):
        del self.row["currency"]
        self.assertTrue(self.verify()["activated"])
        self.mark_paid.assert_called_once()

    def test_invalid_signature_never_fetches(self):
        self.signature = "0" * 64
        self.assert_rejected("signature_mismatch", 400)
        self.get.assert_not_called()

    def test_http_errors_fail_closed_without_parsing(self):
        for status_code in (400, 401, 404, 429, 500, 502, 503):
            with self.subTest(status_code=status_code):
                response = self.response(status_code=status_code)
                response.json.side_effect = AssertionError("HTTP error body must not be parsed")
                self.get.return_value = response
                self.assert_rejected("gateway_rejected", 502)
                response.json.assert_not_called()

    def test_network_errors_fail_closed(self):
        for exception in (RequestException, ConnectionError, Timeout):
            with self.subTest(exception=exception.__name__):
                self.get.side_effect = exception("temporary failure")
                self.assert_rejected("gateway_unreachable", 502)

    def test_json_errors_are_invalid_responses_not_network_errors(self):
        for exception in (ValueError, TypeError, JSONDecodeError):
            with self.subTest(exception=exception.__name__):
                self.get.return_value = self.response()
                self.get.return_value.json.side_effect = exception("invalid JSON")
                self.assert_rejected("invalid_gateway_response", 502)

    def test_non_object_json_is_invalid(self):
        for payload in (None, [], ["captured"], "captured", 35282, True):
            with self.subTest(payload=payload):
                self.get.return_value.json.return_value = payload
                self.assert_rejected("invalid_gateway_response", 502)

    def test_invalid_amount_values_fail_closed_without_coercion(self):
        for amount in (None, "not-a-number", "35282", [], {}, True, 35282.0, 35282.9, float("inf")):
            with self.subTest(amount=amount):
                self.get.return_value = self.response(amount=amount)
                self.assert_rejected("invalid_gateway_response", 502)

    def test_missing_amount_is_invalid(self):
        del self.get.return_value.json.return_value["amount"]
        self.assert_rejected("invalid_gateway_response", 502)

    def test_invalid_stored_amount_conversion_is_invalid_response(self):
        self.row["amount_paise"] = "invalid"
        self.assert_rejected("invalid_gateway_response", 502)

    def test_amount_mismatches_preserve_error(self):
        for amount in (0, -1, 35281, 35283):
            with self.subTest(amount=amount):
                self.get.return_value = self.response(amount=amount)
                self.assert_rejected("amount_mismatch", 400)

    def test_order_mismatch_preserves_error(self):
        for order_id in ("order_other", None, ""):
            with self.subTest(order_id=order_id):
                self.get.return_value = self.response(order_id=order_id)
                self.assert_rejected("payment_order_mismatch", 400)

    def test_currency_mismatch_fails_closed(self):
        for currency in ("USD", "inr", "", None):
            with self.subTest(currency=currency):
                self.get.return_value = self.response(currency=currency)
                self.assert_rejected("currency_mismatch", 400)
        self.row["currency"] = "USD"
        self.get.return_value = self.response(currency="INR")
        self.assert_rejected("currency_mismatch", 400)

    def test_missing_currency_fails_closed(self):
        del self.get.return_value.json.return_value["currency"]
        self.assert_rejected("currency_mismatch", 400)

    def test_authorized_and_other_uncaptured_statuses_never_mark_paid(self):
        for status in ("authorized", "created", "failed", "refunded", "Captured", None, ""):
            with self.subTest(status=status):
                self.get.return_value = self.response(status=status)
                self.assert_rejected("payment_not_captured", 409)

    def test_retry_after_temporary_failure_can_activate(self):
        for failure, code in (
            (Timeout("temporary failure"), "gateway_unreachable"),
            (self.response(status_code=503), "gateway_rejected"),
        ):
            with self.subTest(code=code):
                self.row.pop("payment_id", None)
                self.row["status"] = "created"
                self.mark_paid.reset_mock()
                self.get.reset_mock()
                self.get.side_effect = [failure, self.response()]
                self.assert_rejected(code, 502)
                result = self.verify()
                self.assertTrue(result["activated"])
                self.assertFalse(result["already_verified"])
                self.assertEqual(self.get.call_count, 2)
                self.mark_paid.assert_called_once_with(self.order_id, self.payment_id, "test")

    def test_already_paid_preserves_idempotent_api_without_fetching(self):
        self.row.update(status="paid", payment_id="pay_existing")
        self.assertEqual(self.verify(), {
            "status": "success",
            "already_verified": True,
            "order_id": self.order_id,
            "payment_id": "pay_existing",
            "plan_id": self.row["plan_id"],
            "amount_display": "₹352.82",
        })
        self.get.assert_not_called()
        self.credentials.assert_not_called()
        self.mark_paid.assert_not_called()


class CredentialVaultStub:
    def __init__(self):
        self.records = {}

    def store_credential(
        self,
        service_name: str,
        credential_type: str,
        username: str = "",
        secret_value: str = "",
        host: str = "",
        port: str = "",
        database_name: str = "",
        email: str = "",
        mobile_number: str = "",
        additional_info: Dict[str, Any] = None,
    ) -> str:
        self.records[service_name] = {
            "credential_type": credential_type,
            "secret_value": secret_value,
            "additional_metadata": dict(additional_info or {}),
        }
        return "cred_synthetic"

    def get_credential(self, service_name):
        return self.records.get(service_name)


class RazorpayCredentialsBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = ast.parse(GATEWAY_PATH.read_text(encoding="utf-8"), filename=str(GATEWAY_PATH))
        names = {"PaymentError", "save_credentials", "get_credentials", "_credentials_from_vault"}
        nodes = [
            node for node in source.body
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in names
        ]
        if {node.name for node in nodes} != names:
            raise AssertionError("Required credential definitions were not found")
        cls.gateway_code = compile(ast.Module(body=nodes, type_ignores=[]), str(GATEWAY_PATH), "exec")

    def setUp(self):
        self.key_id = "rzp_test_synthetic123"
        self.key_secret = "synthetic-unit-test-secret"
        self.environ = {}
        self.vault = CredentialVaultStub()
        self.vault.get_credential = Mock(wraps=self.vault.get_credential)
        self.config = Mock(return_value={"status": "success"})
        self.log_event = Mock()

        def import_stub(name, globals=None, locals=None, fromlist=(), level=0):
            if name != "app.core.database" or fromlist != ("credentials_vault",) or level != 0:
                raise AssertionError(f"Unexpected import: {name}")
            return SimpleNamespace(credentials_vault=self.vault)

        namespace = {
            "__builtins__": dict(vars(builtins), __import__=import_stub),
            "Any": Any,
            "Dict": Dict,
            "re": re,
            "os": SimpleNamespace(environ=self.environ, getenv=self.environ.get),
            "config": self.config,
            "log_event": self.log_event,
        }
        exec(self.gateway_code, namespace)
        self.save_credentials = namespace["save_credentials"]
        self.get_credentials = namespace["get_credentials"]

    def test_save_credentials_persists_secret_and_key_id_metadata(self):
        result = self.save_credentials(f" {self.key_id} ", f" {self.key_secret} ")
        self.assertEqual(self.vault.records, {
            "RAZORPAY": {
                "credential_type": "payment_gateway",
                "secret_value": self.key_secret,
                "additional_metadata": {"key_id": self.key_id},
            },
        })
        self.assertEqual(self.environ, {
            "RAZORPAY_KEY_ID": self.key_id,
            "RAZORPAY_KEY_SECRET": self.key_secret,
        })
        self.assertEqual(result, {"status": "success"})
        self.config.assert_called_once_with()
        self.assertEqual(self.get_credentials(), (self.key_id, self.key_secret))
        self.vault.get_credential.assert_not_called()
        self.assertFalse(any(call.kwargs.get("level") == "WARNING" for call in self.log_event.call_args_list))

    def test_get_credentials_loads_saved_pair_after_stub_environment_cleared(self):
        self.save_credentials(self.key_id, self.key_secret)
        self.environ.clear()
        self.assertEqual(self.get_credentials(), (self.key_id, self.key_secret))
        self.vault.get_credential.assert_called_once_with("RAZORPAY")
        self.assertEqual(self.environ, {})


if __name__ == "__main__":
    unittest.main()
