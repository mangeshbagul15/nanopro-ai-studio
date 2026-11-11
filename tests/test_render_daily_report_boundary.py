"""Exercise extracted report/scheduler code without initializing any app module."""

import ast
import builtins
import io
import json
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Optional
from unittest.mock import Mock
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


ROOT = Path(__file__).resolve().parents[1]
PHONE = "918433755448"
OTHER_PHONE = "919876543210"
SECRET = "synthetic-secret-never-disclose"
IST = timezone(timedelta(hours=5, minutes=30))


def extract_definitions(relative_path, names, namespace, class_name=None):
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
    scope = {"Any": Any, "Dict": Dict, "Optional": Optional, **namespace}
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
        self.native_sender = Mock()
        self.imports = []
        self.stubs = {
            "app.core": SimpleNamespace(dm_persistence=SimpleNamespace(_connect=self.connect)),
            "app.core.communication_center": SimpleNamespace(
                communication_center=SimpleNamespace(send_whatsapp_cloud_api=self.sender)),
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
            "app/core/render_status.py", {"build_render_daily_report", "send_daily_render_report"},
            self.namespace,
        )

    def day(self):
        return self.clock.instant.astimezone(IST).date().isoformat()

    def provider_send(self, **kwargs):
        with self.database.lock:
            row = self.database.rows[(self.day(), kwargs["phone"])]
            assert row["state"] == "sending", "Provider called before durable claim commit"
            assert kwargs == {
                "phone": kwargs["phone"], "message": row["report_text"], "sensitive": True,
            }, "No template or generic fallback is allowed"
            self.database.events.append(("provider", kwargs["phone"]))
        return self.provider_result


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
        self.assertEqual(result["reason"], "whatsapp_reply_required")
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


if __name__ == "__main__":
    unittest.main()
