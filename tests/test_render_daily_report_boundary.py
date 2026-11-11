"""Exercise extracted report/scheduler code without initializing any app module."""

import ast
import builtins
import io
import json
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


ROOT = Path(__file__).resolve().parents[1]
PHONE = "918433755448"
OTHER_PHONE = "919876543210"
SECRET = "synthetic-secret-never-disclose"
IST = timezone(timedelta(hours=5, minutes=30))
TEMPLATE_ID = "1443140931240355"
TEMPLATE_NAME = "nanopro_render_daily_report_v1"
TEMPLATE_BODY = (
    "Your requested daily NanoPro Render service report for {{1}}.\n"
    "Service and deployment: {{2}}.\n"
    "Bandwidth and protection (app estimates): {{3}}.\n"
    "Runtime and account limits: {{4}}.\n"
    "CPU/RAM are not collected by this report."
)
TEMPLATE_FOOTER = "App estimates; Render billing is authoritative."
TEMPLATE_CONSTANTS = {
    "REPORT_TEMPLATE_ID", "REPORT_TEMPLATE_NAME", "REPORT_TEMPLATE_LANGUAGE",
    "REPORT_TEMPLATE_BODY", "REPORT_TEMPLATE_FOOTER",
}
REVIEW_SAMPLES = ["meta-review-date", "meta-review-service", "meta-review-bandwidth", "meta-review-runtime"]
EXPECTED_PARAMS = [
    "2026-11-06 10:00 IST",
    "Service: boundary-studio; App process: running on Render; Plan: Free - no card; "
    "Suspended: no; Latest deploy: live - commit abcdef12",
    "Bandwidth (app meter): 1 GB of 5 GB (20%); Bandwidth remaining (estimate): 4.00 GB; "
    "Month-end projection: 2 GB by month end; Usage risk: ok; Protection mode: normal; "
    "HTTP responses: 100 MB; Service-initiated traffic: 200 MB; Average daily traffic: 0.1 GB/day",
    "Process uptime: 12 h since this boot; Instance-hour limit: 750 h/month; "
    "Build time estimate: 42 of 500 min (approx.); Heavy-feature throttle: 3 GB - throttle; "
    "Heavy-feature pause: 4 GB - pause; Free bandwidth limit: 5 GB - suspended; "
    "Sources: app meter + Render API",
]


def approved_template():
    return {
        "id": TEMPLATE_ID, "name": TEMPLATE_NAME, "status": "APPROVED",
        "category": "UTILITY", "language": "en",
        "components": [
            {"type": "BODY", "text": TEMPLATE_BODY, "example": {"body_text": [list(REVIEW_SAMPLES)]}},
            {"type": "FOOTER", "text": TEMPLATE_FOOTER},
        ],
    }


def extract_definitions(relative_path, names, namespace, class_name=None, literal_names=()):
    """Compile only selected definitions, never module imports or initialization."""
    path = ROOT / relative_path
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    if class_name:
        cls = next(node for node in tree.body
                   if isinstance(node, ast.ClassDef) and node.name == class_name)
        cls.body = [node for node in cls.body
                    if isinstance(node, ast.FunctionDef) and node.name in names]
        assert {node.name for node in cls.body} == set(names)
        nodes = [cls]
    else:
        nodes = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name in names]
        assert {node.name for node in nodes} == set(names)
    literals = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in literal_names:
                value = ast.literal_eval(node.value)
                assert isinstance(value, str), "Only literal report strings may be extracted"
                assert target.id not in literals
                literals[target.id] = value
    assert set(literals) == set(literal_names)
    scope = {"Any": Any, "Dict": Dict, "List": List, "Optional": Optional, **namespace, **literals}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), scope)
    return scope


def scheduler_zone(name):
    # Windows may lack tzdata. IST has no DST, so this exact fixed-offset
    # fallback keeps the calendar boundary test deterministic without installing it.
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        if name == "Asia/Kolkata":
            return IST
        if name == "UTC":
            return timezone.utc
        raise


class FakeNeon:
    """Model durable transactional rows and atomic claims shared by workers."""

    def __init__(self):
        self.rows = {}
        self.lock = threading.RLock()
        self.events = []
        self.connections = []
        self.failure = None
        self.claim_barrier = None
        self.lose_claim = False

    def check(self, phase):
        if self.failure == phase:
            raise RuntimeError(SECRET)

    def connect(self):
        self.check("connect")
        conn = FakeConnection(self)
        self.connections.append(conn)
        return conn


class FakeConnection:
    def __init__(self, database):
        self.database = database
        self.writes = {}
        self.locked = False
        self.closed = False
        self.phase = None

    def cursor(self):
        if self.closed:
            raise AssertionError("Connection was already closed")
        return FakeCursor(self)

    def begin_write(self):
        if not self.locked:
            self.database.lock.acquire()
            self.locked = True

    def row(self, key):
        return self.writes.get(key, self.database.rows.get(key))

    def commit(self):
        self.database.check("commit_" + self.phase)
        with self.database.lock:
            self.database.rows.update(self.writes)
            self.database.events.append(("commit", self.phase))
        self.writes.clear()
        self.release()

    def release(self):
        if self.locked:
            self.locked = False
            self.database.lock.release()

    def close(self):
        self.writes.clear()  # Roll back uncommitted work, never undo committed claims.
        self.release()
        self.closed = True
        self.database.events.append(("close",))


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection
        self.result = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=()):
        sql = " ".join(sql.split())
        conn, db = self.connection, self.connection.database
        self.result = None
        if sql.startswith("CREATE TABLE IF NOT EXISTS nanopro_render_report_delivery"):
            phase = "create"
        elif sql.startswith("SELECT state FROM nanopro_render_report_delivery"):
            phase = "select"
        elif sql.startswith("INSERT INTO nanopro_render_report_delivery"):
            assert "ON CONFLICT (report_date, recipient) DO NOTHING" in sql
            phase = "insert"
        elif sql.startswith("UPDATE nanopro_render_report_delivery SET state = 'sending'"):
            assert "AND state = 'pending' RETURNING report_text" in sql
            phase = "claim"
        elif sql.startswith("UPDATE nanopro_render_report_delivery SET state = %s"):
            phase = "final"
        else:
            raise AssertionError("Unexpected SQL: " + sql)
        conn.phase = phase
        db.check(phase)
        if phase == "claim" and db.claim_barrier:
            db.claim_barrier.wait(timeout=5)
        with db.lock:
            db.events.append(("sql", phase, params))
        if phase == "create":
            assert "PRIMARY KEY (report_date, recipient)" in sql
        elif phase == "select":
            with db.lock:
                row = conn.row(tuple(params))
                self.result = (row["state"],) if row else None
        elif phase == "insert":
            conn.begin_write()
            key = tuple(params[:2])
            if conn.row(key) is None:
                conn.writes[key] = {"state": "pending", "report_text": params[2]}
        elif phase == "claim":
            conn.begin_write()
            key = tuple(params)
            row = conn.row(key)
            if row and row["state"] == "pending":
                conn.writes[key] = {**row, "state": "sending"}
                if not db.lose_claim:
                    self.result = (row["report_text"],)
                    db.events.append(("claimed", key))
                # With lose_claim, simulate another worker winning this claim.
        elif phase == "final":
            conn.begin_write()
            state, day, phone = params
            key = (day, phone)
            row = conn.row(key)
            assert row is not None and row["state"] == "sending"
            conn.writes[key] = {**row, "state": state}

    def fetchone(self):
        return self.result


class ReportBoundary:
    def __init__(self, database=None):
        self.database = database if database is not None else FakeNeon()
        self.clock = SimpleNamespace(instant=datetime(2026, 11, 6, 4, 30, tzinfo=timezone.utc))
        clock = self.clock

        class FrozenDatetime(datetime):
            @classmethod
            def now(cls, tz=None):
                return clock.instant.astimezone(tz) if tz else clock.instant.replace(tzinfo=None)

        self.env = {
            "RENDER": "true", "RENDER_SERVICE_NAME": "boundary-studio",
            "RENDER_API_KEY": SECRET, "WHATSAPP_CLOUD_ACCESS_TOKEN": SECRET,
        }
        self.data = {
            "plan": "Free - no card", "suspended": "no",
            "latest_deploy": "live - commit abcdef12", "bandwidth": "1 GB of 5 GB (20%)",
            "bandwidth_remaining": "4.00 GB",
            "projected": "2 GB by month end", "bt_verdict": "ok", "bt_mode": "normal",
            "http_responses": "100 MB", "service_initiated": "200 MB",
            "avg_per_day": "0.1 GB/day", "instance_uptime": "12 h since this boot",
            "instance_limit": "750 h/month", "pipeline_minutes": "42 of 500 min (approx.)",
            "soft_warn_at": "3 GB - throttle", "heavy_pause_at": "4 GB - pause",
            "suspend_at": "5 GB - suspended", "api_source": "app meter + Render API",
            "api_key": SECRET, "credentials": {"token": SECRET},
            "cpu": SECRET, "ram": SECRET, "note": SECRET,
        }
        self.open_numbers = {PHONE}
        self.render_status = Mock(side_effect=lambda force=False: dict(self.data))
        self.connect = Mock(side_effect=self.database.connect)
        self.guardian = Mock(side_effect=lambda phone: phone in self.open_numbers)
        self.provider_result = {
            "success": True, "status": "accepted", "message_id": "synthetic-message-id",
        }
        self.sender = Mock(side_effect=self.provider_send)
        self.template_metadata = approved_template()
        self.template_metadata["status"] = "PENDING"
        self.template_getter = Mock(side_effect=self.get_template)
        self.native_sender = Mock()
        self.imports = []
        self.stubs = {
            "app.core": SimpleNamespace(dm_persistence=SimpleNamespace(_connect=self.connect)),
            "app.core.communication_center": SimpleNamespace(
                communication_center=SimpleNamespace(
                    send_whatsapp_cloud_api=self.sender, get_whatsapp_template=self.template_getter)),
            "app.core.whatsapp_guardian": SimpleNamespace(
                whatsapp_guardian=SimpleNamespace(is_window_open_for=self.guardian)),
            "app.core.render_status": SimpleNamespace(send_daily_render_report=self.native_sender),
        }

        def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "app" or name.startswith("app."):
                self.imports.append(name)
                if level or name not in self.stubs:
                    raise AssertionError("Real app imports are forbidden: " + name)
                return self.stubs[name]
            return builtins.__import__(name, globals, locals, fromlist, level)

        self.namespace = {
            "__builtins__": {**vars(builtins), "__import__": safe_import},
            "os": SimpleNamespace(environ=self.env), "datetime": FrozenDatetime,
            "timedelta": timedelta, "timezone": timezone, "json": json,
            "ZoneInfo": scheduler_zone, "ZoneInfoNotFoundError": ZoneInfoNotFoundError,
            "render_status": self.render_status,
        }
        self.scope = self.new_scope()
        self.native_sender.side_effect = self.scope["send_daily_render_report"]
        scheduler_scope = extract_definitions(
            "app/core/automation_scheduler.py", {"_execute_app_job", "calculate_next_run"},
            self.namespace, class_name="AutomationScheduler",
        )
        # __init__ and all its persistence/worker startup methods are excluded.
        self.scheduler = scheduler_scope["AutomationScheduler"]()

    def new_scope(self):
        return extract_definitions(
            "app/core/render_status.py", {
                "build_render_daily_report", "send_daily_render_report",
                "render_report_template_approved", "build_render_report_template_params",
            },
            self.namespace, literal_names=TEMPLATE_CONSTANTS,
        )

    def get_template(self, template_id):
        assert template_id == TEMPLATE_ID
        with self.database.lock:
            self.database.events.append(("metadata", template_id))
        return self.template_metadata

    def day(self):
        return self.clock.instant.astimezone(IST).date().isoformat()

    def provider_send(self, **kwargs):
        with self.database.lock:
            row = self.database.rows[(self.day(), kwargs["phone"])]
            assert row["state"] == "sending", "Provider called before durable claim commit"
            expected = {"phone": kwargs["phone"], "message": row["report_text"], "sensitive": True}
            if kwargs["phone"] not in self.open_numbers:
                assert self.scope["render_report_template_approved"](self.template_metadata)
                expected.update({
                    "template_name": TEMPLATE_NAME, "language_code": "en",
                    "template_params": self.scope["build_render_report_template_params"](row["report_text"]),
                })
            assert kwargs == expected, "Only the exact saved sensitive report may be sent"
            self.database.events.append(("provider", kwargs["phone"]))
        return self.provider_result


class CommunicationBoundary:
    def __init__(self):
        self.env = {
            "WHATSAPP_CLOUD_ACCESS_TOKEN": SECRET,
            "WHATSAPP_CLOUD_PHONE_ID": "synthetic-phone-id",
        }
        self.vault = Mock(spec=["get_credential"])
        self.vault.get_credential.return_value = {"secret_value": SECRET, "username": "synthetic-phone-id"}
        self.response = SimpleNamespace(
            status_code=200, content=b"synthetic-response", text=SECRET,
            json=Mock(return_value=approved_template()),
        )
        self.session = Mock(spec=["get", "post", "close"])
        self.session.get.return_value = self.response
        self.session.post.return_value = self.response
        self.requests = SimpleNamespace(Session=Mock(return_value=self.session), get=Mock(), post=Mock())
        self.log = Mock()
        self.imports = []

        def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "app" or name.startswith("app."):
                self.imports.append(name)
                raise AssertionError("Real app imports are forbidden: " + name)
            return builtins.__import__(name, globals, locals, fromlist, level)

        scope = extract_definitions(
            "app/core/communication_center.py", {"get_whatsapp_template", "send_whatsapp_cloud_api"},
            {"__builtins__": {**vars(builtins), "__import__": safe_import},
             "os": SimpleNamespace(environ=self.env), "requests": self.requests,
             "credentials_vault": self.vault, "log_event": self.log},
            class_name="CommunicationCenter",
        )
        self.center = scope["CommunicationCenter"]()
        self.center.record_ledger_entry = Mock()


class RenderDailyReportBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.boundary = ReportBoundary()

    def call_report(self, boundary=None, recipient="+" + PHONE, restart=False):
        boundary = boundary or self.boundary
        scope = boundary.new_scope() if restart else boundary.scope
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = scope["send_daily_render_report"](recipient)
        self.assertNotIn(SECRET, json.dumps(result) + stdout.getvalue() + stderr.getvalue())
        self.assertTrue(all(conn.closed for conn in boundary.database.connections))
        return result

    def test_render_unset_skips_before_import_validation_or_any_work(self):
        h = self.boundary
        h.env.pop("RENDER")
        h.stubs.clear()  # Even attempting a stub import now fails the skip assertion.
        self.assertEqual(self.call_report(recipient="invalid"), {
            "status": "skipped", "reason": "render_only",
        })
        self.assertEqual(h.imports, [])
        h.connect.assert_not_called()
        h.render_status.assert_not_called()
        h.guardian.assert_not_called()
        h.sender.assert_not_called()

    def test_ascii_phone_length_and_optional_plus_boundaries(self):
        h = self.boundary
        invalid = ["", "1" * 10, "1" * 16, "+" + "1" * 16, "++" + PHONE,
                   "91 8433755448", "91-8433755448", "letters" + PHONE,
                   "９１８４３３７５５４４８", "٩١٨٤٣٣٧٥٥٤٤٨", None]
        for phone in invalid:
            with self.subTest(phone=phone):
                self.assertEqual(self.call_report(recipient=phone), {
                    "status": "error", "reason": "invalid_recipient",
                })
        h.connect.assert_not_called()
        h.render_status.assert_not_called()
        h.guardian.assert_not_called()
        h.sender.assert_not_called()
        for raw in ["1" * 11, "+" + "2" * 15, "  +" + PHONE + "  "]:
            with self.subTest(phone=raw):
                digits = raw.strip().removeprefix("+")
                h.open_numbers.add(digits)
                result = self.call_report(recipient=raw)
                self.assertEqual((result["status"], result["recipient"]), ("accepted", digits))
                self.assertEqual(h.sender.call_args.kwargs["phone"], digits)

    def test_report_date_is_ist_at_utc_month_boundary(self):
        h = self.boundary
        h.clock.instant = datetime(2026, 10, 31, 18, 30, tzinfo=timezone.utc)
        result = self.call_report()
        self.assertEqual(result["report_date"], "2026-11-01")
        self.assertEqual(set(h.database.rows), {("2026-11-01", PHONE)})
        self.assertIn("2026-11-01 00:00 IST", h.sender.call_args.kwargs["message"])

    def test_formatter_labels_estimates_limits_and_ignores_secret_fields(self):
        h = self.boundary
        text = h.scope["build_render_daily_report"](h.data)
        expected = {
            "Plan": "plan", "Suspended": "suspended", "Latest deploy": "latest_deploy",
            "Bandwidth (app meter)": "bandwidth", "Bandwidth remaining (estimate)": "bandwidth_remaining",
            "Month-end projection": "projected",
            "Usage risk": "bt_verdict", "Protection mode": "bt_mode",
            "HTTP responses": "http_responses", "Service-initiated traffic": "service_initiated",
            "Average daily traffic": "avg_per_day", "Process uptime": "instance_uptime",
            "Instance-hour limit": "instance_limit", "Build time estimate": "pipeline_minutes",
            "Heavy-feature throttle": "soft_warn_at", "Heavy-feature pause": "heavy_pause_at",
            "Free bandwidth limit": "suspend_at", "Sources": "api_source",
        }
        for label, key in expected.items():
            with self.subTest(label=label):
                self.assertIn(f"{label}: {h.data[key]}", text)
        self.assertIn("Service: boundary-studio", text)
        self.assertIn("App process: running on Render", text)
        self.assertIn("2026-11-06 10:00 IST", text)
        self.assertIn("CPU/RAM: not collected by this report; check the Render dashboard.", text)
        self.assertIn("App bandwidth and build-time figures are estimates; Render billing is authoritative.", text)
        self.assertNotIn(SECRET, text)
        self.assertNotIn("credentials", text)
        h.connect.assert_not_called()
        h.render_status.assert_not_called()

    def test_formatter_missing_values_are_explicit_not_fabricated(self):
        h = self.boundary
        h.env.pop("RENDER_SERVICE_NAME")
        text = h.scope["build_render_daily_report"]({"plan": None, "bandwidth": ""})
        self.assertIn("Service: nanopro-studio", text)
        for label in ["Plan", "Bandwidth (app meter)", "Latest deploy", "Process uptime",
                      "Build time estimate", "Sources"]:
            self.assertIn(label + ": not available", text)
        self.assertNotIn(SECRET, text)

    def test_closed_window_saves_pending_without_provider_or_hello_world(self):
        h = self.boundary
        h.open_numbers.clear()
        result = self.call_report()
        self.assertEqual(result["status"], "pending")
        self.assertEqual(result["reason"], "report_template_not_approved")
        row = h.database.rows[(h.day(), PHONE)]
        self.assertEqual(row["state"], "pending")
        self.assertIn("Render Daily Report", row["report_text"])
        self.assertNotIn("hello_world", row["report_text"] + json.dumps(result))
        h.guardian.assert_called_once_with(PHONE)
        h.render_status.assert_called_once_with(force=True)
        h.sender.assert_not_called()
        self.assertFalse(any(event[:2] == ("sql", "claim") for event in h.database.events))

    def test_window_is_per_number_not_shared_with_other_recipient(self):
        h = self.boundary
        self.assertEqual(self.call_report()["status"], "accepted")
        self.assertEqual(self.call_report(recipient="+" + OTHER_PHONE)["status"], "pending")
        self.assertEqual([call.args for call in h.guardian.call_args_list], [(PHONE,), (OTHER_PHONE,)])
        h.sender.assert_called_once()
        self.assertEqual(h.database.rows[(h.day(), OTHER_PHONE)]["state"], "pending")

    def test_open_window_commits_claim_then_sends_sensitive_saved_report(self):
        h = self.boundary
        h.provider_result.update({"response": SECRET, "access_token": SECRET})
        result = self.call_report()
        row = h.database.rows[(h.day(), PHONE)]
        self.assertEqual(result, {"report_date": h.day(), "recipient": PHONE, "status": "accepted"})
        self.assertEqual(row["state"], "accepted")
        h.sender.assert_called_once_with(phone=PHONE, message=row["report_text"], sensitive=True)
        h.template_getter.assert_not_called()
        events = h.database.events
        self.assertLess(events.index(("commit", "claim")), events.index(("provider", PHONE)))
        self.assertLess(events.index(("provider", PHONE)), events.index(("commit", "final")))
        self.assertNotIn("delivered", json.dumps(result))
        self.assertNotIn("message_id", result)
        self.assertNotIn(SECRET, row["report_text"])

    def test_terminal_states_survive_new_function_instances_without_attempts(self):
        for state in ["accepted", "sending", "failed"]:
            with self.subTest(state=state):
                h = ReportBoundary()
                h.database.rows[(h.day(), PHONE)] = {"state": state, "report_text": "saved report"}
                for _ in range(2):
                    result = self.call_report(h, restart=True)
                    self.assertEqual(result["status"], state)
                    self.assertTrue(result["already_attempted"])
                h.render_status.assert_not_called()
                h.guardian.assert_not_called()
                h.sender.assert_not_called()
                self.assertFalse(any(event[0] == "sql" and event[1] in {"insert", "claim", "final"}
                                     for event in h.database.events))

    def test_daily_recipient_key_allows_only_one_attempt_each_across_restarts(self):
        h = self.boundary
        first_day = h.day()
        self.assertEqual(self.call_report()["status"], "accepted")
        self.assertTrue(self.call_report(restart=True)["already_attempted"])
        h.open_numbers.add(OTHER_PHONE)
        self.assertEqual(self.call_report(recipient=OTHER_PHONE, restart=True)["status"], "accepted")
        h.clock.instant += timedelta(days=1)
        self.assertEqual(self.call_report(restart=True)["status"], "accepted")
        self.assertTrue(self.call_report(restart=True)["already_attempted"])
        self.assertEqual(h.sender.call_count, 3)
        self.assertEqual(set(h.database.rows), {
            (first_day, PHONE), (first_day, OTHER_PHONE), (h.day(), PHONE),
        })

    def test_pending_text_is_reused_when_window_opens_after_restart(self):
        h = self.boundary
        h.open_numbers.clear()
        self.assertEqual(self.call_report()["status"], "pending")
        saved = h.database.rows[(h.day(), PHONE)]["report_text"]
        h.data["latest_deploy"] = "new deployment must not replace saved text"
        h.clock.instant += timedelta(minutes=30)
        self.assertEqual(self.call_report(restart=True)["status"], "pending")
        self.assertEqual(h.database.rows[(h.day(), PHONE)]["report_text"], saved)
        h.sender.assert_not_called()
        h.open_numbers.add(PHONE)
        self.assertEqual(self.call_report(restart=True)["status"], "accepted")
        h.sender.assert_called_once_with(phone=PHONE, message=saved, sensitive=True)
        self.assertNotIn("new deployment", h.sender.call_args.kwargs["message"])
        self.assertTrue(self.call_report(restart=True)["already_attempted"])

    def test_provider_requires_success_accepted_and_message_id_no_generic_fallback(self):
        responses = [
            {}, {"success": True, "status": "accepted"},
            {"success": True, "status": "accepted", "message_id": ""},
            {"success": True, "status": "accepted", "message_id": None},
            {"success": False, "status": "accepted", "message_id": "id"},
            {"success": True, "status": "success", "message_id": "id"},
            {"success": True, "status": "delivered", "message_id": "id"},
            {"success": True, "status": "fallback", "message_id": "hello_world"},
        ]
        for response in responses:
            with self.subTest(response=response):
                h = ReportBoundary()
                h.provider_result = {**response, "response": SECRET, "error": SECRET}
                self.assertEqual(self.call_report(h)["status"], "failed")
                self.assertEqual(h.database.rows[(h.day(), PHONE)]["state"], "failed")
                retry = self.call_report(h, restart=True)
                self.assertEqual(retry["status"], "failed")
                self.assertTrue(retry["already_attempted"])
                h.sender.assert_called_once()
                self.assertEqual(set(h.sender.call_args.kwargs), {"phone", "message", "sensitive"})

    def test_db_unavailable_or_preclaim_exceptions_fail_closed_without_secrets(self):
        phases = ["connect", "null_connection", "create", "select", "commit_select",
                  "report", "insert", "commit_insert", "window", "claim", "commit_claim"]
        for phase in phases:
            with self.subTest(phase=phase):
                h = ReportBoundary()
                if phase == "null_connection":
                    h.connect.side_effect = None
                    h.connect.return_value = None
                elif phase == "report":
                    h.render_status.side_effect = RuntimeError(SECRET)
                elif phase == "window":
                    h.guardian.side_effect = RuntimeError(SECRET)
                else:
                    h.database.failure = phase
                for restart in [False, True]:
                    result = self.call_report(h, restart=restart)
                    self.assertEqual(result["status"], "error")
                    self.assertEqual(result["reason"], "report_dispatch_failed")
                h.sender.assert_not_called()
                self.assertFalse(any(row["state"] == "accepted" for row in h.database.rows.values()))

    def test_lost_atomic_claim_does_not_send_and_remains_terminal(self):
        h = self.boundary
        h.database.lose_claim = True
        result = self.call_report()
        self.assertEqual(result["status"], "sending")
        self.assertTrue(result["already_attempted"])
        self.assertEqual(h.database.rows[(h.day(), PHONE)]["state"], "sending")
        self.assertEqual(self.call_report(restart=True)["status"], "sending")
        h.sender.assert_not_called()
        h.render_status.assert_called_once_with(force=True)

    def test_postclaim_exceptions_keep_sending_terminal_and_never_resend(self):
        for phase in ["provider", "malformed_provider", "final", "commit_final"]:
            with self.subTest(phase=phase):
                h = ReportBoundary()
                if phase == "provider":
                    h.sender.side_effect = RuntimeError(SECRET)
                elif phase == "malformed_provider":
                    h.provider_result = None
                else:
                    h.database.failure = phase
                result = self.call_report(h)
                self.assertEqual(result["status"], "error")
                self.assertEqual(result["reason"], "report_dispatch_failed")
                self.assertEqual(h.database.rows[(h.day(), PHONE)]["state"], "sending")
                for _ in range(2):
                    retry = self.call_report(h, restart=True)
                    self.assertEqual(retry["status"], "sending")
                    self.assertTrue(retry["already_attempted"])
                h.sender.assert_called_once()
                h.render_status.assert_called_once_with(force=True)

    def test_concurrent_instances_share_atomic_claim_and_attempt_provider_once(self):
        h = self.boundary
        h.database.claim_barrier = threading.Barrier(2)
        workers = [h.new_scope()["send_daily_render_report"] for _ in range(2)]
        # Both workers pass SELECT/INSERT before either can claim. Do not use
        # process-global stdout redirection in worker threads.
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(worker, "+" + PHONE) for worker in workers]
            results = [future.result(timeout=10) for future in futures]
        self.assertEqual(sorted(result["status"] for result in results), ["accepted", "sending"])
        self.assertTrue(next(result for result in results if result["status"] == "sending")["already_attempted"])
        self.assertNotIn(SECRET, json.dumps(results))
        h.sender.assert_called_once()
        self.assertEqual(h.render_status.call_count, 2)
        self.assertEqual(sum(event[0] == "claimed" for event in h.database.events), 1)
        self.assertEqual(len(h.database.rows), 1)
        self.assertEqual(h.database.rows[(h.day(), PHONE)]["state"], "accepted")
        self.assertEqual(self.call_report(restart=True)["status"], "accepted")

    def test_report_template_literals_match_the_submitted_contract(self):
        h = self.boundary
        self.assertEqual({key: h.scope[key] for key in TEMPLATE_CONSTANTS}, {
            "REPORT_TEMPLATE_ID": TEMPLATE_ID, "REPORT_TEMPLATE_NAME": TEMPLATE_NAME,
            "REPORT_TEMPLATE_LANGUAGE": "en", "REPORT_TEMPLATE_BODY": TEMPLATE_BODY,
            "REPORT_TEMPLATE_FOOTER": TEMPLATE_FOOTER,
        })
        self.assertTrue(h.scope["render_report_template_approved"](approved_template()))
        self.assertEqual(h.imports, [])
        h.connect.assert_not_called()
        h.template_getter.assert_not_called()

    def test_ast_extraction_rejects_nonliteral_template_assignments_without_execution(self):
        probe = Mock(side_effect=AssertionError("Computed assignments must never execute"))
        source = "REPORT_TEMPLATE_ID = probe()\ndef selected():\n    return REPORT_TEMPLATE_ID\n"
        with patch.object(Path, "read_text", return_value=source):
            with self.assertRaises(ValueError):
                extract_definitions(
                    "app/core/render_status.py", {"selected"}, {"probe": probe},
                    literal_names={"REPORT_TEMPLATE_ID"},
                )
        probe.assert_not_called()
        self.assertEqual(self.boundary.imports, [])

    def test_template_approval_requires_exact_id_name_status_category_and_language(self):
        approve = self.boundary.scope["render_report_template_approved"]
        invalid = {
            "id": [None, int(TEMPLATE_ID), "1443140931240356", " " + TEMPLATE_ID, "９" * 16],
            "name": [None, "hello_world", TEMPLATE_NAME.upper(), TEMPLATE_NAME + " "],
            "status": [None, "approved", "APPROVED ", "PENDING", "REJECTED", "PAUSED"],
            "category": [None, "MARKETING", "AUTHENTICATION", "utility", "UTILITY "],
            "language": [None, "en_US", "EN", "en ", "hi"],
        }
        for key, values in invalid.items():
            for value in values:
                with self.subTest(key=key, value=value):
                    template = approved_template()
                    template[key] = value
                    self.assertFalse(approve(template))
            template = approved_template()
            del template[key]
            with self.subTest(missing=key):
                self.assertFalse(approve(template))

    def test_template_approval_requires_exact_body_footer_and_no_extra_components(self):
        approve = self.boundary.scope["render_report_template_approved"]
        components = approved_template()["components"]
        invalid = [
            None, {}, "BODY", tuple(components), [], [components[0]], [components[1]],
            [components[0], components[0]], [components[1], components[1]],
            [None, components[1]], [components[0], "FOOTER"],
        ]
        for extra in [{"type": "HEADER", "text": "Report"}, {"type": "BUTTONS", "buttons": []},
                      {"type": "BODY", "text": TEMPLATE_BODY}]:
            invalid.append(components + [extra])
        for index in (0, 1):
            for key in ("type", "text"):
                for value in (None, "", components[index][key].lower(), components[index][key] + " "):
                    altered = deepcopy(components)
                    altered[index][key] = value
                    invalid.append(altered)
                altered = deepcopy(components)
                del altered[index][key]
                invalid.append(altered)
        altered = deepcopy(components)
        altered[0]["text"] = TEMPLATE_BODY.replace("{{4}}", "{{3}}")
        invalid.append(altered)
        altered = deepcopy(components)
        altered[0]["text"] = TEMPLATE_BODY.replace("\n", " ")
        invalid.append(altered)
        for value in invalid:
            with self.subTest(components=value):
                template = approved_template()
                template["components"] = value
                self.assertFalse(approve(template))
        template = approved_template()
        del template["components"]
        self.assertFalse(approve(template))
        template["components"] = list(reversed(components))
        self.assertTrue(approve(template))

    def test_malformed_template_metadata_fails_closed_without_claim_or_secrets(self):
        metadata_values = [None, [], [approved_template()], "APPROVED", 200, True, {},
                           {"data": [approved_template()]}, {"error": SECRET}]
        for metadata in metadata_values:
            with self.subTest(metadata=metadata):
                h = ReportBoundary()
                h.open_numbers.clear()
                h.template_metadata = metadata
                self.assertFalse(h.scope["render_report_template_approved"](metadata))
                self.assertEqual(self.call_report(h), {
                    "report_date": h.day(), "recipient": PHONE, "status": "pending",
                    "reason": "report_template_not_approved",
                })
                self.assertEqual(h.database.rows[(h.day(), PHONE)]["state"], "pending")
                h.template_getter.assert_called_once_with(TEMPLATE_ID)
                h.sender.assert_not_called()
                self.assertFalse(any(event[:2] == ("sql", "claim") for event in h.database.events))

    def test_pending_rejected_paused_or_unavailable_template_never_claims(self):
        for status in ["PENDING", "REJECTED", "PAUSED", "DISABLED", "IN_APPEAL", None, "unavailable"]:
            with self.subTest(status=status):
                h = ReportBoundary()
                h.open_numbers.clear()
                metadata = approved_template()
                metadata.update({"status": status, "access_token": SECRET, "raw_error": SECRET})

                def inspect_pending(template_id):
                    self.assertEqual(template_id, TEMPLATE_ID)
                    row = h.database.rows[(h.day(), PHONE)]
                    self.assertEqual(row["state"], "pending")
                    self.assertIn(("commit", "insert"), h.database.events)
                    self.assertFalse(any(event[:2] == ("sql", "claim") for event in h.database.events))
                    h.sender.assert_not_called()
                    return metadata

                h.template_getter.side_effect = inspect_pending
                for restart in [False, True]:
                    result = self.call_report(h, restart=restart)
                    self.assertEqual((result["status"], result["reason"]),
                                     ("pending", "report_template_not_approved"))
                self.assertEqual(h.database.rows[(h.day(), PHONE)]["state"], "pending")
                h.sender.assert_not_called()
                self.assertEqual(h.template_getter.call_count, 2)

    def test_formatter_normalizes_whitespace_before_template_label_parsing(self):
        h = self.boundary
        baseline = h.scope["build_render_daily_report"](h.data)
        keys = ["plan", "suspended", "latest_deploy", "bandwidth", "bandwidth_remaining",
                "projected", "bt_verdict", "bt_mode", "http_responses", "service_initiated",
                "avg_per_day", "instance_uptime", "instance_limit", "pipeline_minutes",
                "soft_warn_at", "heavy_pause_at", "suspend_at", "api_source"]
        for key in keys:
            h.data[key] = "\t " + h.data[key].replace(" ", " \n\t ") + "\r\n "
        h.env["RENDER_SERVICE_NAME"] = " \tboundary-studio\r\n "
        report = h.scope["build_render_daily_report"](h.data)
        self.assertEqual(report, baseline)
        self.assertNotIn("\t", report)
        self.assertNotIn("\r", report)
        self.assertEqual(h.scope["build_render_report_template_params"](report), EXPECTED_PARAMS)
        self.assertNotIn(SECRET, report)

    def test_template_params_use_four_saved_timestamp_and_whitelisted_groups(self):
        h = self.boundary
        report = h.scope["build_render_daily_report"](h.data)
        report += f"\nCPU: {SECRET}\nRAM: {SECRET}\nToken: {SECRET}\nUnrecognized: {SECRET}"
        h.clock.instant += timedelta(hours=2)
        h.data["latest_deploy"] = "regenerated-deployment"
        h.env["RENDER_SERVICE_NAME"] = "regenerated-service"
        params = h.scope["build_render_report_template_params"](report)
        self.assertEqual(params, EXPECTED_PARAMS)
        self.assertEqual(len(params), 4)
        for value in params:
            self.assertIsInstance(value, str)
            self.assertEqual(value, " ".join(value.split()))
        self.assertNotIn(SECRET, json.dumps(params))
        self.assertNotIn("CPU/RAM", json.dumps(params))
        self.assertNotIn("regenerated", json.dumps(params))
        self.assertTrue(set(params).isdisjoint(REVIEW_SAMPLES))
        h.render_status.assert_not_called()
        h.connect.assert_not_called()

    def test_template_params_missing_labels_are_explicit_not_fabricated(self):
        params = self.boundary.scope["build_render_report_template_params"](
            "*Saved report*\n 2026-10-31\t23:59  IST \nUnknown: " + SECRET)
        self.assertEqual(params[0], "2026-10-31 23:59 IST")
        self.assertEqual(len(params), 4)
        for actual, baseline in zip(params[1:], EXPECTED_PARAMS[1:]):
            labels = [field.partition(": ")[0] for field in baseline.split("; ")]
            self.assertEqual(actual, "; ".join(label + ": not available" for label in labels))
        self.assertNotIn(SECRET, json.dumps(params))

    def test_closed_approved_template_commits_claim_and_sends_four_real_params(self):
        h = self.boundary
        h.open_numbers.clear()
        h.template_metadata = approved_template()
        h.template_metadata["access_token"] = SECRET
        h.provider_result.update({"response": SECRET, "error": SECRET})
        result = self.call_report()
        row = h.database.rows[(h.day(), PHONE)]
        self.assertEqual(result, {"report_date": h.day(), "recipient": PHONE, "status": "accepted"})
        self.assertEqual(row["state"], "accepted")
        h.guardian.assert_called_once_with(PHONE)
        h.template_getter.assert_called_once_with(TEMPLATE_ID)
        h.sender.assert_called_once_with(
            phone=PHONE, message=row["report_text"], sensitive=True,
            template_name=TEMPLATE_NAME, template_params=EXPECTED_PARAMS, language_code="en",
        )
        events = h.database.events
        self.assertLess(events.index(("commit", "insert")), events.index(("metadata", TEMPLATE_ID)))
        self.assertLess(events.index(("metadata", TEMPLATE_ID)), events.index(("sql", "claim", (h.day(), PHONE))))
        self.assertLess(events.index(("commit", "claim")), events.index(("provider", PHONE)))
        self.assertLess(events.index(("provider", PHONE)), events.index(("commit", "final")))
        self.assertTrue(set(h.sender.call_args.kwargs["template_params"]).isdisjoint(REVIEW_SAMPLES))
        self.assertNotIn("hello_world", json.dumps(h.sender.call_args.kwargs))
        self.assertFalse(any("telegram" in name for name in h.imports))

    def test_saved_pending_report_reused_after_approval_and_restart(self):
        h = self.boundary
        h.open_numbers.clear()
        self.assertEqual(self.call_report()["status"], "pending")
        saved = h.database.rows[(h.day(), PHONE)]["report_text"]
        h.clock.instant += timedelta(minutes=30)
        for key in ["latest_deploy", "plan", "bandwidth", "bt_mode", "instance_uptime", "api_source"]:
            h.data[key] = "regenerated-value-must-not-send"
        h.env["RENDER_SERVICE_NAME"] = "regenerated-service-must-not-send"
        self.assertEqual(self.call_report(restart=True)["status"], "pending")
        self.assertEqual(h.database.rows[(h.day(), PHONE)]["report_text"], saved)
        h.sender.assert_not_called()
        h.template_metadata = approved_template()
        h.clock.instant += timedelta(hours=1)
        self.assertEqual(self.call_report(restart=True)["status"], "accepted")
        h.sender.assert_called_once_with(
            phone=PHONE, message=saved, sensitive=True, template_name=TEMPLATE_NAME,
            template_params=EXPECTED_PARAMS, language_code="en",
        )
        self.assertNotIn("regenerated", json.dumps(h.sender.call_args.kwargs))
        self.assertEqual(h.database.rows[(h.day(), PHONE)]["report_text"], saved)
        self.assertTrue(self.call_report(restart=True)["already_attempted"])
        self.assertEqual(h.template_getter.call_count, 3)
        h.sender.assert_called_once()

    def test_approved_template_date_recipient_dedup_survives_restarts(self):
        h = self.boundary
        h.open_numbers.clear()
        h.template_metadata = approved_template()
        first_day = h.day()
        self.assertEqual(self.call_report()["status"], "accepted")
        self.assertTrue(self.call_report(restart=True)["already_attempted"])
        self.assertEqual(self.call_report(recipient=OTHER_PHONE, restart=True)["status"], "accepted")
        h.clock.instant += timedelta(days=1)
        self.assertEqual(self.call_report(restart=True)["status"], "accepted")
        self.assertTrue(self.call_report(restart=True)["already_attempted"])
        self.assertEqual(h.sender.call_count, 3)
        self.assertEqual(h.template_getter.call_count, 3)
        self.assertEqual(set(h.database.rows), {
            (first_day, PHONE), (first_day, OTHER_PHONE), (h.day(), PHONE),
        })
        self.assertTrue(all(row["state"] == "accepted" for row in h.database.rows.values()))
        for call in h.sender.call_args_list:
            self.assertEqual(call.kwargs["template_name"], TEMPLATE_NAME)
            self.assertEqual(len(call.kwargs["template_params"]), 4)
            self.assertTrue(call.kwargs["sensitive"])

    def test_concurrent_approved_template_workers_claim_and_send_once(self):
        h = self.boundary
        h.open_numbers.clear()
        h.template_metadata = approved_template()
        h.database.claim_barrier = threading.Barrier(2)
        workers = [h.new_scope()["send_daily_render_report"] for _ in range(2)]
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(worker, PHONE) for worker in workers]
            results = [future.result(timeout=10) for future in futures]
        self.assertEqual(sorted(result["status"] for result in results), ["accepted", "sending"])
        self.assertTrue(next(result for result in results if result["status"] == "sending")["already_attempted"])
        self.assertNotIn(SECRET, json.dumps(results))
        self.assertEqual(h.template_getter.call_count, 2)
        h.sender.assert_called_once_with(
            phone=PHONE, message=h.database.rows[(h.day(), PHONE)]["report_text"], sensitive=True,
            template_name=TEMPLATE_NAME, template_params=EXPECTED_PARAMS, language_code="en",
        )
        self.assertEqual(sum(event[0] == "claimed" for event in h.database.events), 1)
        self.assertEqual(len(h.database.rows), 1)
        self.assertEqual(h.database.rows[(h.day(), PHONE)]["state"], "accepted")
        self.assertTrue(all(conn.closed for conn in h.database.connections))
        self.assertTrue(self.call_report(restart=True)["already_attempted"])
        h.sender.assert_called_once()

    def test_approved_template_provider_failures_are_terminal_without_fallback(self):
        responses = [{}, {"success": True, "status": "accepted"},
                     {"success": True, "status": "accepted", "message_id": ""},
                     {"success": False, "status": "accepted", "message_id": "id"},
                     {"success": True, "status": "delivered", "message_id": "id"},
                     {"success": True, "status": "fallback", "message_id": "hello_world"}]
        for response in responses:
            with self.subTest(response=response):
                h = ReportBoundary()
                h.open_numbers.clear()
                h.template_metadata = approved_template()
                h.provider_result = {**response, "error": SECRET, "response": SECRET}
                self.assertEqual(self.call_report(h)["status"], "failed")
                retry = self.call_report(h, restart=True)
                self.assertEqual(retry["status"], "failed")
                self.assertTrue(retry["already_attempted"])
                h.sender.assert_called_once()
                h.template_getter.assert_called_once_with(TEMPLATE_ID)
                self.assertEqual(h.sender.call_args.kwargs["template_params"], EXPECTED_PARAMS)
                self.assertFalse(any("telegram" in name for name in h.imports))

    def test_approved_template_lost_claim_or_ambiguous_failure_never_resends(self):
        for phase in ["lost_claim", "provider", "malformed_provider", "final", "commit_final"]:
            with self.subTest(phase=phase):
                h = ReportBoundary()
                h.open_numbers.clear()
                h.template_metadata = approved_template()
                if phase == "lost_claim":
                    h.database.lose_claim = True
                elif phase == "provider":
                    h.sender.side_effect = RuntimeError(SECRET)
                elif phase == "malformed_provider":
                    h.provider_result = None
                else:
                    h.database.failure = phase
                result = self.call_report(h)
                self.assertEqual(result["status"], "sending" if phase == "lost_claim" else "error")
                self.assertEqual(h.database.rows[(h.day(), PHONE)]["state"], "sending")
                for _ in range(2):
                    retry = self.call_report(h, restart=True)
                    self.assertEqual(retry["status"], "sending")
                    self.assertTrue(retry["already_attempted"])
                self.assertEqual(h.sender.call_count, 0 if phase == "lost_claim" else 1)
                h.template_getter.assert_called_once_with(TEMPLATE_ID)

    def test_approved_template_preclaim_database_failures_do_not_send(self):
        for phase in ["claim", "commit_claim"]:
            with self.subTest(phase=phase):
                h = ReportBoundary()
                h.open_numbers.clear()
                h.template_metadata = approved_template()
                h.database.failure = phase
                result = self.call_report(h)
                self.assertEqual((result["status"], result["reason"]), ("error", "report_dispatch_failed"))
                self.assertEqual(h.database.rows[(h.day(), PHONE)]["state"], "pending")
                h.sender.assert_not_called()
                h.template_getter.assert_called_once_with(TEMPLATE_ID)

    def test_saved_approved_report_real_sender_payload_has_four_body_fields_no_otp_button(self):
        h = self.boundary
        c = CommunicationBoundary()
        c.response.json.return_value = {
            "messages": [{"id": "synthetic-message-id"}], "contacts": [{"wa_id": PHONE}],
        }
        h.open_numbers.clear()
        h.template_metadata = approved_template()

        def real_send(**kwargs):
            h.provider_send(**kwargs)
            return c.center.send_whatsapp_cloud_api(**kwargs)

        h.sender.side_effect = real_send
        self.assertEqual(self.call_report()["status"], "accepted")
        c.session.post.assert_called_once_with(
            "https://graph.facebook.com/v25.0/synthetic-phone-id/messages",
            headers={"Authorization": "Bearer " + SECRET, "Content-Type": "application/json",
                     "User-Agent": "NanoProAI-Studio/2.0"},
            json={"messaging_product": "whatsapp", "to": PHONE, "type": "template", "template": {
                "name": TEMPLATE_NAME, "language": {"code": "en"}, "components": [{
                    "type": "body", "parameters": [{"type": "text", "text": value} for value in EXPECTED_PARAMS],
                }],
            }}, timeout=12,
        )
        payload = c.session.post.call_args.kwargs["json"]
        self.assertNotIn("button", json.dumps(payload))
        self.assertNotIn("hello_world", json.dumps(payload))
        self.assertNotIn(SECRET, json.dumps(payload))
        self.assertEqual(c.imports, [])
        c.vault.get_credential.assert_not_called()
        c.center.record_ledger_entry.assert_called_once()
        self.assertNotIn("response", c.center.record_ledger_entry.call_args.kwargs["metadata"])
        self.assertNotIn(SECRET, str(c.log.call_args_list) + str(c.center.record_ledger_entry.call_args_list))

    def test_real_report_sender_provider_failures_never_fallback_or_expose_errors(self):
        for phase in ["window_closed", "provider_error", "timeout", "malformed_json"]:
            with self.subTest(phase=phase):
                h = ReportBoundary()
                c = CommunicationBoundary()
                h.open_numbers.clear()
                h.template_metadata = approved_template()
                if phase == "timeout":
                    c.session.post.side_effect = TimeoutError(SECRET)
                elif phase == "malformed_json":
                    c.response.json.side_effect = ValueError(SECRET)
                else:
                    c.response.status_code = 400
                    c.response.json.return_value = {
                        "error": {"code": 131047 if phase == "window_closed" else 100,
                                  "message": "24 hours " + SECRET, "token": SECRET},
                    }

                def real_send(**kwargs):
                    h.provider_send(**kwargs)
                    return c.center.send_whatsapp_cloud_api(**kwargs)

                h.sender.side_effect = real_send
                self.assertEqual(self.call_report(h)["status"], "failed")
                self.assertTrue(self.call_report(h, restart=True)["already_attempted"])
                h.sender.assert_called_once()
                c.session.post.assert_called_once()
                payload = c.session.post.call_args.kwargs["json"]
                self.assertEqual(payload["template"]["name"], TEMPLATE_NAME)
                self.assertEqual(payload["template"]["components"], [{
                    "type": "body", "parameters": [{"type": "text", "text": value} for value in EXPECTED_PARAMS],
                }])
                self.assertNotIn("hello_world", json.dumps(payload))
                self.assertEqual(c.imports, [])
                self.assertNotIn(SECRET, str(c.log.call_args_list))
                c.center.record_ledger_entry.assert_not_called()
                c.requests.get.assert_not_called()
                c.requests.post.assert_not_called()

    def test_scheduler_native_json_recipient_and_status_exit_code_contract(self):
        h = self.boundary
        task = {"name": "RENDER_DAILY_WHATSAPP_REPORT", "script_content": json.dumps({"recipient": PHONE})}
        stdout, stderr, code = h.scheduler._execute_app_job(task)
        self.assertEqual((json.loads(stdout)["status"], stderr, code), ("accepted", "", 0))
        h.native_sender.assert_called_once_with(PHONE)
        h.sender.assert_called_once()
        h.native_sender.side_effect = None
        for status in ["accepted", "pending", "skipped", "sending", "failed", "error", "delivered", None]:
            with self.subTest(status=status):
                response = {"status": status} if status is not None else {}
                h.native_sender.return_value = response
                stdout, stderr, code = h.scheduler._execute_app_job(task)
                self.assertEqual(json.loads(stdout), response)
                self.assertEqual(stderr, "")
                self.assertEqual(code, 0 if status in {"accepted", "pending", "skipped", "sending"} else 1)
                self.assertEqual(h.native_sender.call_args.args, (PHONE,))
        h.native_sender.return_value = {"status": "skipped"}
        for content in ["", "{}", None]:
            with self.subTest(default_content=content):
                h.scheduler._execute_app_job({"name": "render_daily_whatsapp_report", "script_content": content})
                self.assertEqual(h.native_sender.call_args.args, ("+" + PHONE,))

    def test_render_boot_registers_missing_report_once_without_sending(self):
        h = self.boundary
        cases = [
            ({}, None),
            ({"RENDER": "true"}, None),
            ({"RENDER": "true"}, {"name": "RENDER_DAILY_WHATSAPP_REPORT", "is_enabled": False, "is_paused": True}),
            ({"RENDER": "true"}, {"name": "render_daily_whatsapp_report", "is_enabled": False}),
        ]
        for env, existing in cases:
            with self.subTest(env=env, existing=existing):
                tasks = [existing] if existing is not None else []
                database = SimpleNamespace(
                    list_automation_tasks=Mock(side_effect=lambda: list(tasks)),
                    update_automation_task=Mock(),
                )
                scope = extract_definitions(
                    "app/core/automation_scheduler.py", {"_ensure_pipeline_tasks_seeded"},
                    {**h.namespace, "os": SimpleNamespace(environ=env), "db": database, "log_event": Mock()},
                    class_name="AutomationScheduler",
                )
                scheduler = scope["AutomationScheduler"]()
                scheduler.create_task = Mock(side_effect=tasks.append)
                scheduler._ensure_pipeline_tasks_seeded()
                scheduler._ensure_pipeline_tasks_seeded()
                reports = [call.args[0] for call in scheduler.create_task.call_args_list
                           if call.args[0]["name"] == "RENDER_DAILY_WHATSAPP_REPORT"]
                if env and existing is None:
                    self.assertEqual(len(reports), 1)
                    report = reports[0]
                    self.assertEqual(report["task_type"], "scheduled_job")
                    self.assertEqual(json.loads(report["script_content"]), {"recipient": "+" + PHONE})
                    self.assertEqual((report["schedule_type"], report["recurrence_expr"], report["timezone"]),
                                     ("daily", "10:00", "Asia/Kolkata"))
                    self.assertEqual(report["retry_policy"]["max_retries"], 0)
                    self.assertEqual(report["notification_pref"], {"email": False, "telegram": False, "whatsapp": False})
                    self.assertTrue(report["is_enabled"])
                    self.assertFalse(report["is_paused"])
                else:
                    self.assertEqual(reports, [])
                database.update_automation_task.assert_not_called()
        h.connect.assert_not_called()
        h.sender.assert_not_called()
        self.assertEqual(h.imports, [])

    def test_daily_1000_schedule_is_ist_independent_of_input_timezone(self):
        h = self.boundary
        cases = [
            (datetime(2026, 11, 6, 4, 29, 59, tzinfo=timezone.utc), "2026-11-06 10:00:00"),
            (datetime(2026, 11, 6, 4, 30, tzinfo=timezone.utc), "2026-11-07 10:00:00"),
            (datetime(2026, 11, 6, 4, 30, 1, tzinfo=timezone.utc), "2026-11-07 10:00:00"),
            (datetime(2026, 1, 31, 23, tzinfo=timezone.utc), "2026-02-01 10:00:00"),
            (datetime(2026, 7, 1, 4, 29, tzinfo=timezone.utc), "2026-07-01 10:00:00"),
            (datetime(2026, 11, 6, 9, 59), "2026-11-06 10:00:00"),
            (datetime(2026, 11, 6, 10), "2026-11-07 10:00:00"),
        ]
        for instant, expected in cases:
            variants = [instant] if instant.tzinfo is None else [
                instant, instant.astimezone(IST), instant.astimezone(timezone(timedelta(hours=-4))),
            ]
            for value in variants:
                with self.subTest(from_dt=value):
                    self.assertEqual(h.scheduler.calculate_next_run("daily", "10:00", value), expected)
                    self.assertEqual(h.scheduler.calculate_next_run(
                        "daily", "10:00", value, timezone_name="Asia/Kolkata"), expected)
        h.clock.instant = cases[0][0]
        self.assertEqual(h.scheduler.calculate_next_run("daily", "10:00"), "2026-11-06 10:00:00")
        self.assertEqual(h.scheduler.calculate_next_run(
            "daily", "10:00", cases[0][0], timezone_name="Not/AZone"), "2026-11-06 10:00:00")


class WhatsAppTemplateMetadataBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.boundary = CommunicationBoundary()

    def call_lookup(self, boundary=None, template_id=TEMPLATE_ID):
        h = boundary or self.boundary
        stdout, stderr = io.StringIO(), io.StringIO()
        escaped = None
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                result = h.center.get_whatsapp_template(template_id)
            except Exception as exc:
                escaped = type(exc).__name__
        if escaped:
            self.fail("Metadata lookup raised " + escaped + " instead of returning {}")
        self.assertNotIn(SECRET, json.dumps(result) + stdout.getvalue() + stderr.getvalue()
                         + str(h.log.call_args_list))
        h.log.assert_not_called()
        h.session.post.assert_not_called()
        h.requests.get.assert_not_called()
        h.requests.post.assert_not_called()
        h.center.record_ledger_entry.assert_not_called()
        self.assertEqual(h.imports, [])
        return result

    def test_lookup_uses_fixed_graph_get_bearer_header_fields_timeout_and_whitelist(self):
        h = self.boundary
        data = approved_template()
        data.update({"access_token": SECRET, "secret_value": SECRET, "raw_response": SECRET})
        h.response.json.return_value = data
        self.assertEqual(self.call_lookup(), approved_template())
        h.requests.Session.assert_called_once_with()
        h.session.get.assert_called_once_with(
            "https://graph.facebook.com/v25.0/" + TEMPLATE_ID,
            headers={"Authorization": "Bearer " + SECRET},
            params={"fields": "id,name,status,category,language,components"}, timeout=8,
        )
        url = h.session.get.call_args.args[0]
        self.assertNotIn(SECRET, url)
        self.assertNotIn("access_token", url)
        self.assertNotIn("access_token", h.session.get.call_args.kwargs["params"])
        h.vault.get_credential.assert_not_called()
        h.session.close.assert_called_once_with()
        h.response.json.assert_called_once_with()

    def test_lookup_uses_only_existing_vault_secret_when_env_token_is_absent(self):
        for env_token in [None, ""]:
            with self.subTest(env_token=env_token):
                h = CommunicationBoundary()
                if env_token is None:
                    del h.env["WHATSAPP_CLOUD_ACCESS_TOKEN"]
                else:
                    h.env["WHATSAPP_CLOUD_ACCESS_TOKEN"] = env_token
                h.vault.get_credential.return_value = {
                    "secret_value": SECRET, "username": "not-the-template-id", "access_token": "wrong-field",
                }
                self.assertEqual(self.call_lookup(h), approved_template())
                h.vault.get_credential.assert_called_once_with("WHATSAPP_BUSINESS_CLOUD")
                self.assertEqual(h.session.get.call_args.args, ("https://graph.facebook.com/v25.0/" + TEMPLATE_ID,))
                self.assertEqual(h.session.get.call_args.kwargs["headers"], {"Authorization": "Bearer " + SECRET})
                h.session.close.assert_called_once_with()

    def test_missing_token_returns_empty_without_creating_session(self):
        for credential in [None, {}, {"secret_value": None}, {"secret_value": ""}, {"token": SECRET}]:
            with self.subTest(credential=credential):
                h = CommunicationBoundary()
                h.env.clear()
                h.vault.get_credential.return_value = credential
                self.assertEqual(self.call_lookup(h), {})
                h.vault.get_credential.assert_called_once_with("WHATSAPP_BUSINESS_CLOUD")
                h.requests.Session.assert_not_called()
                h.session.get.assert_not_called()
                h.session.close.assert_not_called()

    def test_invalid_numeric_string_ids_return_empty_before_env_vault_or_request(self):
        invalid = ["", " ", " " + TEMPLATE_ID, TEMPLATE_ID + " ", "+" + TEMPLATE_ID,
                   TEMPLATE_ID + "?access_token=" + SECRET, TEMPLATE_ID + "/messages",
                   "https://example.invalid/" + TEMPLATE_ID, "123x", "１２３", "١٢٣", "123\n"]
        for template_id in invalid:
            with self.subTest(template_id=template_id):
                h = CommunicationBoundary()
                h.env = Mock()
                h.env.get.side_effect = AssertionError("Invalid ID must not read credentials")
                h.center.get_whatsapp_template.__globals__["os"] = SimpleNamespace(environ=h.env)
                self.assertEqual(self.call_lookup(h, template_id), {})
                h.env.get.assert_not_called()
                h.vault.get_credential.assert_not_called()
                h.requests.Session.assert_not_called()
                h.session.close.assert_not_called()

    def test_non200_provider_responses_return_empty_without_decoding_or_logging(self):
        for status in [201, 204, 302, 400, 401, 403, 429, 500, 503]:
            with self.subTest(status=status):
                h = CommunicationBoundary()
                h.response.status_code = status
                h.response.json.return_value = {"error": {"message": SECRET, "access_token": SECRET}}
                self.assertEqual(self.call_lookup(h), {})
                h.session.get.assert_called_once()
                h.response.json.assert_not_called()
                h.session.close.assert_called_once_with()

    def test_malformed_json_and_provider_error_objects_return_empty_and_close(self):
        data_values = [None, [], [approved_template()], SECRET, 123, True,
                       {"error": None}, {"error": {"message": SECRET, "token": SECRET}},
                       {**approved_template(), "error": SECRET}]
        for data in data_values:
            with self.subTest(data=data):
                h = CommunicationBoundary()
                h.response.json.return_value = data
                self.assertEqual(self.call_lookup(h), {})
                h.response.json.assert_called_once_with()
                h.session.close.assert_called_once_with()

    def test_vault_session_network_and_decode_exceptions_return_empty_without_secrets(self):
        for phase in ["vault", "session", "get", "timeout", "json"]:
            with self.subTest(phase=phase):
                h = CommunicationBoundary()
                if phase == "vault":
                    h.env.clear()
                    h.vault.get_credential.side_effect = RuntimeError(SECRET)
                elif phase == "session":
                    h.requests.Session.side_effect = RuntimeError(SECRET)
                elif phase in {"get", "timeout"}:
                    h.session.get.side_effect = TimeoutError(SECRET) if phase == "timeout" else OSError(SECRET)
                else:
                    h.response.json.side_effect = ValueError(SECRET)
                self.assertEqual(self.call_lookup(h), {})
                if phase in {"vault", "session"}:
                    h.session.close.assert_not_called()
                else:
                    h.session.get.assert_called_once()
                    h.session.close.assert_called_once_with()

    def test_lookup_api_version_default_blank_and_trimmed_versions(self):
        for version, expected in [(None, "v25.0"), ("", "v25.0"), (" \t ", "v25.0"), (" v24.0 ", "v24.0")]:
            with self.subTest(version=version):
                h = CommunicationBoundary()
                if version is not None:
                    h.env["WHATSAPP_CLOUD_API_VERSION"] = version
                self.assertEqual(self.call_lookup(h), approved_template())
                self.assertEqual(h.session.get.call_args.args, (f"https://graph.facebook.com/{expected}/{TEMPLATE_ID}",))
                h.session.close.assert_called_once_with()

    def test_lookup_preserves_pending_rejected_paused_metadata_for_strict_gate(self):
        approve = ReportBoundary().scope["render_report_template_approved"]
        for status in ["PENDING", "REJECTED", "PAUSED"]:
            with self.subTest(status=status):
                h = CommunicationBoundary()
                metadata = approved_template()
                metadata["status"] = status
                h.response.json.return_value = metadata
                result = self.call_lookup(h)
                self.assertEqual(result, metadata)
                self.assertFalse(approve(result))
                h.session.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
