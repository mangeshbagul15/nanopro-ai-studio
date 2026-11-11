import base64
import hashlib
import hmac
import os
import re
import time
import uuid
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlencode

import requests

from app.core.logger import log_event

RAZORPAY_BASE_URL = "https://api.razorpay.com/v1"
CURRENCY = "INR"
GST_RATE = 0.18

UPI_ID = (os.getenv("NANOPRO_UPI_ID") or "mangeshbagul15-2@okhdfcbank").strip()
UPI_PAYEE = (os.getenv("NANOPRO_UPI_NAME") or "Mangesh Bagul").strip()
RAZORPAY_ME_URL = (os.getenv("NANOPRO_RAZORPAY_ME_URL") or "https://razorpay.me/@mangeshvasantbagul").strip()

PLANS: Dict[str, Dict[str, Any]] = {
    "ai_awaaz_starter": {
        "id": "ai_awaaz_starter",
        "name": "Ai Awaaz Starter",
        "tagline": "Pay once. Lifetime access.",
        "base_price_paise": 29900,
        "gst_rate": GST_RATE,
        "monthly_characters": 30000,
        "chars_per_minute": 830,
        "features": [
            "About 36 minutes of voiceover every month",
            "30,000 characters, refilled every month",
            "Natural Indian-language narration",
            "UPI, cards and net banking via Razorpay",
        ],
    }
}


class PaymentError(Exception):
    def __init__(self, message: str, code: str = "payment_error", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


def _money(paise: int) -> str:
    return f"₹{paise / 100:,.2f}"


def plan_summary(plan: Dict[str, Any]) -> Dict[str, Any]:
    base = int(plan["base_price_paise"])
    gst = round(base * float(plan["gst_rate"]))
    total = base + gst
    minutes = round(int(plan["monthly_characters"]) / int(plan["chars_per_minute"]), 1)
    return {
        "id": plan["id"],
        "name": plan["name"],
        "tagline": plan["tagline"],
        "currency": CURRENCY,
        "base_price_paise": base,
        "gst_rate": float(plan["gst_rate"]),
        "gst_paise": gst,
        "total_paise": total,
        "base_price_display": _money(base),
        "gst_display": _money(gst),
        "total_display": _money(total),
        "monthly_characters": int(plan["monthly_characters"]),
        "monthly_minutes": minutes,
        "chars_per_minute": int(plan["chars_per_minute"]),
        "features": list(plan["features"]),
    }


def list_plans() -> List[Dict[str, Any]]:
    return [plan_summary(plan) for plan in PLANS.values()]


def direct_upi_payload(plan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Key-free payment path: UPI intent QR plus the Razorpay.me payment page."""
    plan = plan or PLANS["ai_awaaz_starter"]
    summary = plan_summary(plan)
    amount = f"{summary['total_paise'] / 100:.2f}"
    params = {
        "pa": UPI_ID,
        "pn": UPI_PAYEE,
        "am": amount,
        "cu": CURRENCY,
        "tn": f"{plan['name']} - NanoPro",
    }
    return {
        "upi_id": UPI_ID,
        "payee": UPI_PAYEE,
        "upi_uri": "upi://pay?" + urlencode(params, quote_via=quote),
        "qr_image_url": "/assets/payment/razorpay_upi_qr.png",
        "razorpay_me_url": RAZORPAY_ME_URL,
        "plan_id": plan["id"],
        "amount_paise": summary["total_paise"],
        "amount_display": summary["total_display"],
        "note": f"{plan['name']} - NanoPro AI Studio",
    }


def _clean_text(value: str, field: str, min_len: int, max_len: int) -> str:
    text = re.sub(r"\s+", " ", (value or "")).strip()
    if len(text) < min_len:
        raise PaymentError(f"{field} is required.", code=f"invalid_{field.lower()}", status_code=422)
    if len(text) > max_len:
        raise PaymentError(f"{field} is too long.", code=f"invalid_{field.lower()}", status_code=422)
    return text


def _clean_mobile(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if not re.fullmatch(r"[6-9]\d{9}", digits):
        raise PaymentError(
            "Enter a valid 10-digit Indian mobile number.",
            code="invalid_mobile",
            status_code=422,
        )
    return digits


def _clean_email(value: str) -> str:
    email = (value or "").strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}", email):
        raise PaymentError("Enter a valid email address.", code="invalid_email", status_code=422)
    return email


def _credentials_from_vault() -> tuple:
    try:
        from app.core.database import credentials_vault

        cred = credentials_vault.get_credential("RAZORPAY")
        if cred:
            secret = (cred.get("secret_value") or "").strip()
            key_id = ((cred.get("additional_metadata") or {}).get("key_id") or "").strip()
            if key_id and secret:
                return key_id, secret
    except Exception as exc:
        log_event(f"Razorpay vault lookup skipped: {exc}", level="DEBUG", component="Payments")
    return "", ""


def get_credentials() -> tuple:
    key_id = (os.getenv("RAZORPAY_KEY_ID") or "").strip()
    key_secret = (os.getenv("RAZORPAY_KEY_SECRET") or "").strip()
    if key_id and key_secret:
        return key_id, key_secret
    return _credentials_from_vault()


def config() -> Dict[str, Any]:
    key_id, key_secret = get_credentials()
    configured = bool(key_id and key_secret and key_id.startswith("rzp_"))
    mode = "test" if key_id.startswith("rzp_test_") else ("live" if key_id.startswith("rzp_live_") else "unconfigured")
    return {
        "status": "success",
        "configured": configured,
        "mode": mode,
        "key_id": key_id if configured else "",
        "currency": CURRENCY,
        "gateway": "Razorpay",
        "methods": ["UPI", "Cards", "Net Banking"],
        "plans": list_plans(),
        "direct_upi": direct_upi_payload(),
        "setup_env": ["RAZORPAY_KEY_ID", "RAZORPAY_KEY_SECRET"],
    }


def save_credentials(key_id: str, key_secret: str) -> Dict[str, Any]:
    key_id = (key_id or "").strip()
    key_secret = (key_secret or "").strip()
    if not re.fullmatch(r"rzp_(test|live)_[A-Za-z0-9]{6,}", key_id):
        raise PaymentError(
            "Invalid Razorpay Key ID. It must start with rzp_test_ or rzp_live_.",
            code="invalid_key_id",
            status_code=422,
        )
    if not (12 <= len(key_secret) <= 128) or not re.fullmatch(r"[A-Za-z0-9_\-]+", key_secret):
        raise PaymentError("Invalid Razorpay Key Secret.", code="invalid_key_secret", status_code=422)

    os.environ["RAZORPAY_KEY_ID"] = key_id
    os.environ["RAZORPAY_KEY_SECRET"] = key_secret
    try:
        from app.core.database import credentials_vault

        credentials_vault.store_credential(
            service_name="RAZORPAY",
            credential_type="payment_gateway",
            secret_value=key_secret,
            additional_info={"key_id": key_id},
        )
    except Exception as exc:
        log_event(f"Razorpay key stored in memory only: {exc}", level="WARNING", component="Payments")

    log_event(f"Razorpay credentials updated for key {key_id[:12]}…", component="Payments")
    return config()


def _conn():
    from app.core.database import db

    return db.get_connection()


def _ensure_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS payment_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE NOT NULL,
            payment_id TEXT,
            plan_id TEXT NOT NULL,
            amount_paise INTEGER NOT NULL,
            currency TEXT NOT NULL,
            status TEXT NOT NULL,
            customer_name TEXT,
            customer_email TEXT,
            customer_mobile TEXT,
            signature_verified INTEGER NOT NULL DEFAULT 0,
            gateway_mode TEXT,
            created_at REAL NOT NULL,
            paid_at REAL
        )
        """
    )
    conn.commit()


def _record_order(order: Dict[str, Any], customer: Dict[str, str], mode: str) -> None:
    with _conn() as conn:
        _ensure_table(conn)
        conn.execute(
            """
            INSERT OR REPLACE INTO payment_orders
            (order_id, plan_id, amount_paise, currency, status, customer_name, customer_email,
             customer_mobile, gateway_mode, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order["id"],
                customer["plan_id"],
                int(order["amount"]),
                order.get("currency", CURRENCY),
                "created",
                customer["name"],
                customer["email"],
                customer["mobile"],
                mode,
                time.time(),
            ),
        )
        conn.commit()


def _mark_paid(order_id: str, payment_id: str, mode: str) -> None:
    with _conn() as conn:
        _ensure_table(conn)
        conn.execute(
            """
            UPDATE payment_orders
            SET status = 'paid', payment_id = ?, signature_verified = 1, paid_at = ?, gateway_mode = ?
            WHERE order_id = ?
            """,
            (payment_id, time.time(), mode, order_id),
        )
        conn.commit()


def _get_order_row(order_id: str) -> Optional[Dict[str, Any]]:
    with _conn() as conn:
        _ensure_table(conn)
        cursor = conn.execute("SELECT * FROM payment_orders WHERE order_id = ? LIMIT 1", (order_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_payment_status(order_id: str) -> Dict[str, Any]:
    order_id = (order_id or "").strip()
    if not order_id:
        raise PaymentError("order_id is required.", code="missing_order_id", status_code=422)
    row = _get_order_row(order_id)
    if not row:
        raise PaymentError("Payment order not found.", code="order_not_found", status_code=404)
    return {
        "status": "success",
        "order_id": row["order_id"],
        "payment_id": row.get("payment_id"),
        "state": row["status"],
        "amount_paise": row["amount_paise"],
        "amount_display": _money(int(row["amount_paise"])),
        "plan_id": row["plan_id"],
        "created_at": row["created_at"],
        "paid_at": row.get("paid_at"),
    }


def payment_history(limit: int = 20) -> List[Dict[str, Any]]:
    limit = max(1, min(int(limit or 20), 100))
    with _conn() as conn:
        _ensure_table(conn)
        rows = conn.execute(
            "SELECT * FROM payment_orders ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [
        {
            "order_id": row["order_id"],
            "payment_id": row["payment_id"],
            "plan_id": row["plan_id"],
            "amount_display": _money(int(row["amount_paise"])),
            "status": row["status"],
            "mode": row["gateway_mode"],
            "customer_name": row["customer_name"],
            "customer_email": row["customer_email"],
            "created_at": row["created_at"],
            "paid_at": row["paid_at"],
        }
        for row in rows
    ]


def _auth_header(key_id: str, key_secret: str) -> str:
    token = base64.b64encode(f"{key_id}:{key_secret}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def _razorpay_error(response) -> str:
    try:
        payload = response.json()
        return (payload.get("error") or {}).get("description") or payload.get("message") or response.text[:200]
    except Exception:
        return response.text[:200] or f"HTTP {response.status_code}"


def create_order(plan_id: str, name: str, email: str, mobile: str, client_ip: str = "") -> Dict[str, Any]:
    plan = PLANS.get((plan_id or "ai_awaaz_starter").strip())
    if not plan:
        raise PaymentError("Unknown plan.", code="unknown_plan", status_code=404)

    customer = {
        "plan_id": plan["id"],
        "name": _clean_text(name, "Name", 2, 80),
        "email": _clean_email(email),
        "mobile": _clean_mobile(mobile),
    }
    summary = plan_summary(plan)
    amount = int(summary["total_paise"])

    key_id, key_secret = get_credentials()
    if not (key_id and key_secret):
        raise PaymentError(
            "Razorpay is not connected yet. Add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in the server environment or connect the gateway from this page as admin.",
            code="gateway_not_configured",
            status_code=503,
        )
    if not key_id.startswith("rzp_"):
        raise PaymentError("Razorpay Key ID is invalid.", code="invalid_key_id", status_code=503)

    mode = "test" if key_id.startswith("rzp_test_") else "live"
    receipt = f"np_{plan['id'][:10]}_{int(time.time())}_{uuid.uuid4().hex[:6]}"[:40]
    payload = {
        "amount": amount,
        "currency": CURRENCY,
        "receipt": receipt,
        "notes": {
            "plan_id": plan["id"],
            "plan_name": plan["name"],
            "customer_name": customer["name"],
            "customer_mobile": customer["mobile"],
            "customer_email": customer["email"],
            "source": "nanopro_payment_gateway",
        },
    }
    try:
        response = requests.post(
            f"{RAZORPAY_BASE_URL}/orders",
            json=payload,
            headers={"Authorization": _auth_header(key_id, key_secret), "Content-Type": "application/json"},
            timeout=15,
        )
    except requests.RequestException as exc:
        log_event(f"Razorpay order network error: {exc}", level="ERROR", component="Payments")
        raise PaymentError("Could not reach Razorpay. Please retry.", code="gateway_unreachable", status_code=502)

    if response.status_code >= 400:
        detail = _razorpay_error(response)
        log_event(f"Razorpay order failed ({response.status_code}): {detail}", level="ERROR", component="Payments")
        raise PaymentError(f"Razorpay rejected the order: {detail}", code="gateway_rejected", status_code=502)

    order = response.json()
    _record_order(order, customer, mode)
    log_event(
        f"Razorpay order {order.get('id')} created for {summary['total_display']} ({mode}) from {client_ip or 'unknown IP'}",
        component="Payments",
    )
    return {
        "status": "success",
        "order_id": order["id"],
        "amount": amount,
        "amount_display": summary["total_display"],
        "currency": CURRENCY,
        "key_id": key_id,
        "mode": mode,
        "plan": summary,
        "customer": customer,
        "checkout": {
            "name": "NanoPro AI Studio",
            "description": f"{plan['name']} — {plan['tagline']}",
            "image": "https://mangesh-nanopro.mangeshbagul15.workers.dev/static/nanopro_logo.png",
            "prefill": {"name": customer["name"], "email": customer["email"], "contact": customer["mobile"]},
            "notes": payload["notes"],
            "theme": {"color": "#38BDF8"},
        },
    }


def claim_upi_payment(plan_id: str, name: str, email: str, mobile: str, reference: str) -> Dict[str, Any]:
    """Records a direct-UPI payment claim so the admin can confirm the UTR manually."""
    plan = PLANS.get((plan_id or "ai_awaaz_starter").strip())
    if not plan:
        raise PaymentError("Unknown plan.", code="unknown_plan", status_code=404)

    customer = {
        "plan_id": plan["id"],
        "name": _clean_text(name, "Name", 2, 80),
        "email": _clean_email(email),
        "mobile": _clean_mobile(mobile),
    }
    reference = re.sub(r"\s+", "", reference or "").upper()
    if not re.fullmatch(r"[A-Z0-9]{6,40}", reference):
        raise PaymentError(
            "Enter the UPI transaction reference / UTR (6-40 letters or digits) shown in your UPI app.",
            code="invalid_reference",
            status_code=422,
        )

    summary = plan_summary(plan)
    order_id = "upi_" + uuid.uuid4().hex[:16]
    with _conn() as conn:
        _ensure_table(conn)
        conn.execute(
            """
            INSERT INTO payment_orders
            (order_id, payment_id, plan_id, amount_paise, currency, status, customer_name,
             customer_email, customer_mobile, signature_verified, gateway_mode, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
            """,
            (
                order_id,
                reference,
                plan["id"],
                int(summary["total_paise"]),
                CURRENCY,
                "awaiting_confirmation",
                customer["name"],
                customer["email"],
                customer["mobile"],
                "upi_direct",
                time.time(),
            ),
        )
        conn.commit()

    log_event(f"UPI payment claim {order_id} recorded for {summary['total_display']} (ref {reference})", component="Payments")
    return {
        "status": "success",
        "order_id": order_id,
        "reference": reference,
        "state": "awaiting_confirmation",
        "amount_display": summary["total_display"],
        "plan": summary,
        "message": "Payment reference received. Access activates as soon as the admin confirms it.",
    }


def verify_payment(order_id: str, payment_id: str, signature: str) -> Dict[str, Any]:
    order_id = (order_id or "").strip()
    payment_id = (payment_id or "").strip()
    signature = (signature or "").strip()
    if not order_id or not payment_id or not signature:
        raise PaymentError("order_id, payment_id and signature are required.", code="missing_fields", status_code=422)

    row = _get_order_row(order_id)
    if not row:
        raise PaymentError("Payment order not found.", code="order_not_found", status_code=404)
    if row["status"] == "paid":
        return {
            "status": "success",
            "already_verified": True,
            "order_id": order_id,
            "payment_id": row.get("payment_id"),
            "plan_id": row["plan_id"],
            "amount_display": _money(int(row["amount_paise"])),
        }

    key_id, key_secret = get_credentials()
    if not (key_id and key_secret):
        raise PaymentError("Razorpay is not configured.", code="gateway_not_configured", status_code=503)

    expected = hmac.new(
        key_secret.encode("utf-8"),
        f"{order_id}|{payment_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        log_event(f"Razorpay signature mismatch for order {order_id}", level="ERROR", component="Payments")
        raise PaymentError("Payment signature verification failed.", code="signature_mismatch", status_code=400)

    try:
        response = requests.get(
            f"{RAZORPAY_BASE_URL}/payments/{payment_id}",
            headers={"Authorization": _auth_header(key_id, key_secret)},
            timeout=15,
        )
    except requests.RequestException as exc:
        log_event(f"Razorpay verification network error: {exc}", level="ERROR", component="Payments")
        raise PaymentError("Could not reach Razorpay. Please retry.", code="gateway_unreachable", status_code=502) from exc

    if response.status_code >= 400:
        raise PaymentError("Razorpay rejected payment verification.", code="gateway_rejected", status_code=502)

    try:
        payment = response.json()
        if not isinstance(payment, dict):
            raise ValueError("Payment response must be an object.")
        amount = payment.get("amount")
        if type(amount) is not int:
            raise ValueError("Payment amount must be an integer in paise.")
        expected_amount = int(row["amount_paise"])
    except (TypeError, ValueError, OverflowError) as exc:
        raise PaymentError("Invalid response from Razorpay.", code="invalid_gateway_response", status_code=502) from exc

    if payment.get("order_id") != order_id:
        raise PaymentError("Payment does not belong to this order.", code="payment_order_mismatch", status_code=400)
    if amount != expected_amount:
        raise PaymentError("Paid amount does not match the order.", code="amount_mismatch", status_code=400)
    if payment.get("currency") != (row.get("currency") or CURRENCY):
        raise PaymentError("Paid currency does not match the order.", code="currency_mismatch", status_code=400)
    if payment.get("status") != "captured":
        raise PaymentError(
            f"Payment is not captured yet (status: {payment.get('status')}).",
            code="payment_not_captured",
            status_code=409,
        )

    _mark_paid(order_id, payment_id, "test" if key_id.startswith("rzp_test_") else "live")
    plan = plan_summary(PLANS.get(row["plan_id"]) or PLANS["ai_awaaz_starter"])
    log_event(f"Payment {payment_id} verified for order {order_id}", component="Payments")
    return {
        "status": "success",
        "already_verified": False,
        "order_id": order_id,
        "payment_id": payment_id,
        "plan": plan,
        "amount_display": _money(int(row["amount_paise"])),
        "mode": "test" if key_id.startswith("rzp_test_") else "live",
        "activated": True,
    }
