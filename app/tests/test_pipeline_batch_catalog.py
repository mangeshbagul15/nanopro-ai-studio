import os
import re
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

os.environ.setdefault("NANOPRO_PIPELINE_ALERTS", "0")
os.environ.setdefault("NANOPRO_REPORT_DELIVERY", "0")

from app.core import bank_batch_cycles as cycles
from app.core import pipeline_catalog as catalog
from app.core import snowflake_lakehouse as lakehouse


IST = cycles.IST


def _at(hour, minute, day=19):
    return datetime(2026, 11, day, hour, minute, tzinfo=IST)


class BatchSchedulerTest(unittest.TestCase):
    def setUp(self):
        cycles._DONE.clear()
        cycles.STATE["last_result"] = None
        cycles.STATE["history"].clear()
        cycles._HISTORY.update({"at": 0.0, "date": "", "value": {}})
        self.recorded = []

    def _patches(self, statuses):
        return (
            patch.object(cycles, "_snowflake_statuses", return_value=dict(statuses)),
            patch.object(cycles, "_record", side_effect=self._capture),
            patch.object(cycles, "_audit"),
        )

    def _capture(self, cycle, bdate, status, **kwargs):
        self.recorded.append({"cycle": cycle, "business_date": bdate, "status": status, **kwargs})
        return {"status": "recorded"}

    def test_nothing_runs_before_the_first_cycle(self):
        statuses, record, audit = self._patches({})
        with statuses, record, audit, patch.object(cycles, "run") as run:
            self.assertIsNone(cycles.poll(_at(5, 30)))
            run.assert_not_called()

    def test_latest_due_cycle_runs_and_earlier_one_is_missed(self):
        statuses, record, audit = self._patches({})
        with statuses, record, audit, patch.object(cycles, "run", return_value={"status": "SUCCESS"}) as run:
            cycles.poll(_at(9, 5))
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0], "SOD")
        self.assertEqual([(r["cycle"], r["status"]) for r in self.recorded], [("BOD", "MISSED")])
        self.assertEqual(self.recorded[0]["business_date"], "2026-11-19")

    def test_completed_cycle_is_not_repeated(self):
        statuses, record, audit = self._patches({"BOD": "SUCCESS"})
        with statuses, record, audit, patch.object(cycles, "run", return_value={}) as run:
            cycles.poll(_at(8, 30))
        self.assertEqual(run.call_args.args[0], "SOD")
        self.assertEqual(self.recorded, [])

    def test_error_cycle_is_retried(self):
        statuses, record, audit = self._patches({"BOD": "ERROR"})
        with statuses, record, audit, patch.object(cycles, "run", return_value={}) as run:
            cycles.poll(_at(6, 45))
        self.assertEqual(run.call_args.args[0], "BOD")

    def test_poll_runs_only_the_last_cycle_after_a_long_sleep(self):
        statuses, record, audit = self._patches({})
        with statuses, record, audit, patch.object(cycles, "run", return_value={}) as run:
            cycles.poll(_at(19, 0))
        self.assertEqual(run.call_args.args[0], "EOD")
        self.assertEqual([r["status"] for r in self.recorded], ["MISSED", "MISSED", "MISSED"])

    def test_status_timetable_reflects_the_ledger(self):
        statuses, record, audit = self._patches({"BOD": "SUCCESS", "SOD": "MISSED"})
        with statuses:
            result = cycles.status(_at(12, 0))
        states = {item["cycle"]: item["state"] for item in result["cycles"]}
        self.assertEqual(states, {"BOD": "SUCCESS", "SOD": "MISSED", "T1": "DUE", "EOD": "PENDING"})
        self.assertEqual(result["business_date"], "2026-11-19")
        self.assertEqual(result["timezone"], "Asia/Kolkata")


class BatchRunTest(unittest.TestCase):
    def setUp(self):
        cycles._DONE.clear()
        cycles.STATE["last_result"] = None
        cycles.STATE["history"].clear()
        cycles._HISTORY.update({"at": 0.0, "date": "", "value": {}})

    def test_run_wraps_the_pipeline_and_records_the_outcome(self):
        from app.core import bq_export_scheduler as scheduler

        export = {"status": "success", "run_id": "R123", "tables": [{}] * 8, "rows": 500,
                  "bytes": 66470, "summary": "8 tables exported"}
        with patch.object(scheduler, "run_once", return_value=export), \
                patch.object(scheduler, "STATE", {"snowflake": {"status": "synced", "l1": {"duplicates_removed": 0}},
                                                  "duckdb": {"status": "reconciled"}}), \
                patch.object(cycles, "_record", return_value={"status": "recorded"}) as record, \
                patch.object(cycles, "_audit"):
            result = cycles.run("bod", trigger="test", now=_at(6, 30))

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["run_id"], "R123")
        self.assertEqual(result["details"]["snowflake_status"], "synced")
        self.assertEqual(result["details"]["duckdb_status"], "reconciled")
        self.assertEqual(result["details"]["exported_tables"], 8)
        record.assert_called_once()
        self.assertEqual(record.call_args.args[:3], ("BOD", "2026-11-19", "SUCCESS"))
        self.assertIn(("2026-11-19", "BOD"), cycles._DONE)

    def test_run_maps_partial_and_error_statuses(self):
        from app.core import bq_export_scheduler as scheduler

        for pipeline_status, expected in (("partial", "PARTIAL"), ("error", "ERROR")):
            with patch.object(scheduler, "run_once", return_value={"status": pipeline_status, "tables": []}), \
                    patch.object(scheduler, "STATE", {}), \
                    patch.object(cycles, "_record", return_value={}), \
                    patch.object(cycles, "_audit"):
                result = cycles.run("eod", trigger="test", now=_at(18, 5))
            self.assertEqual(result["status"], expected, pipeline_status)

    def test_pipeline_exception_is_recorded_as_error(self):
        from app.core import bq_export_scheduler as scheduler

        with patch.object(scheduler, "run_once", side_effect=RuntimeError("boom")), \
                patch.object(cycles, "_record", return_value={}) as record, \
                patch.object(cycles, "_audit"):
            result = cycles.run("sod", trigger="test", now=_at(8, 0))
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["details"]["error"], "boom")
        self.assertEqual(record.call_args.args[2], "ERROR")

    def test_unknown_cycle_is_rejected(self):
        with self.assertRaises(ValueError):
            cycles.run("XYZ")


class _CaptureCursor:
    def __init__(self, rows=None):
        self.statements = []
        self._rows = rows or []

    def execute(self, sql):
        self.statements.append(" ".join(str(sql).split()))

    def fetchall(self):
        return list(self._rows)


class _FakeConnection:
    def __init__(self, rows=None):
        self.cursor_obj = _CaptureCursor(rows)
        self.committed = False

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.committed = True

    def close(self):
        pass


class BatchLedgerTest(unittest.TestCase):
    def test_record_batch_upserts_without_reserved_rows_column(self):
        connection = _FakeConnection()
        started = datetime(2026, 11, 19, 0, 30, tzinfo=timezone.utc)
        with patch.object(lakehouse, "_connect", return_value=connection), \
                patch("app.core.snowflake_client.load_config", return_value={"database": "BANK_DB"}):
            result = lakehouse.record_batch("bod", "2026-11-19", "SUCCESS", trigger="test", run_id="R1",
                                            tables=8, rows=500, details={"summary": "ok"},
                                            started_at=started, finished_at=started)

        self.assertEqual(result["batch_id"], "2026-11-19-BOD")
        self.assertTrue(connection.committed)
        merge = next(s for s in connection.cursor_obj.statements if s.startswith("MERGE"))
        self.assertIn("TO_DATE('2026-11-19')", merge)
        self.assertIn("EXPORTED_ROWS", merge)
        self.assertIsNone(re.search(r"\bROWS\b", merge))
        self.assertIn("TRIGGERED_BY", merge)
        self.assertIsNone(re.search(r"\bTRIGGER\b", merge))
        self.assertIn("WHEN NOT MATCHED THEN INSERT", merge)
        self.assertIn("BANK_DB.L2_CURATED.BATCH_CONTROL", merge)

    def test_batch_history_maps_rows(self):
        rows = [("2026-11-19-EOD", "EOD", "2026-11-19", "SUCCESS", "scheduler", "R9",
                 8, 500, "{}", "2026-11-19 12:30:00", "2026-11-19 12:31:00")]
        connection = _FakeConnection(rows)
        with patch.object(lakehouse, "_connect", return_value=connection), \
                patch("app.core.snowflake_client.load_config", return_value={"database": "BANK_DB"}):
            history = lakehouse.batch_history("2026-11-19")

        self.assertEqual(history[0]["batch_id"], "2026-11-19-EOD")
        self.assertEqual(history[0]["status"], "SUCCESS")
        self.assertEqual(history[0]["rows"], 500)
        query = connection.cursor_obj.statements[0]
        self.assertIn("BANK_DB.L2_CURATED.BATCH_CONTROL", query)
        self.assertIn("BUSINESS_DATE = TO_DATE('2026-11-19')", query)


class _FakeBody:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return self.payload


class _FakePaginator:
    def __init__(self, contents):
        self.contents = contents

    def paginate(self, **_kwargs):
        yield {"Contents": self.contents}


class _FakeS3:
    def __init__(self, contents, objects):
        self.contents = contents
        self.objects = objects

    def get_paginator(self, _name):
        return _FakePaginator(self.contents)

    def get_object(self, Bucket, Key):
        return {"Body": _FakeBody(self.objects[Key])}


class _FakeGlue:
    def get_tables(self, DatabaseName):
        return {"TableList": []}


class AwsLayerTest(unittest.TestCase):
    def test_manifest_supplies_rows_and_columns(self):
        import json as _json

        manifest = _json.dumps({"files": [{
            "table": "CMG", "key": "bronze/bigquery/nanopro_cbs_bronze/cmg/cmg.parquet",
            "rows": 50, "bytes": 900,
            "columns": [{"name": "CUST_ID", "type": "VARCHAR"}, {"name": "CUST_NAME", "type": "VARCHAR"}],
        }]}).encode("utf-8")
        contents = [
            {"Key": "bronze/bigquery/nanopro_cbs_bronze/cmg/cmg.parquet", "Size": 900},
            {"Key": "bronze/bigquery/nanopro_cbs_bronze/_MANIFEST.json", "Size": len(manifest)},
            {"Key": "bronze/bigquery/nanopro_cbs_bronze/_SUCCESS", "Size": 20},
        ]
        s3 = _FakeS3(contents, {"bronze/bigquery/nanopro_cbs_bronze/_MANIFEST.json": manifest})
        with patch("app.core.chat_s3_export._aws_config",
                   return_value={"bucket": "b", "access_key": "k", "secret_key": "s", "region": "r"}), \
                patch("app.core.chat_s3_export._s3_client", return_value=s3), \
                patch("app.core.bigquery_aws_pipeline._aws_client", return_value=_FakeGlue()):
            layer = catalog._aws_layer()

        self.assertEqual(layer["kind"], "s3")
        self.assertEqual(layer["status"], "live")
        tables = layer["schemas"][0]["tables"]
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]["name"], "cmg")
        self.assertEqual(tables[0]["rows"], 50)
        self.assertEqual([col["name"] for col in tables[0]["columns"]], ["CUST_ID", "CUST_NAME"])


class PipelineCatalogTest(unittest.TestCase):
    def setUp(self):
        catalog._CACHE.update({"at": 0.0, "value": None})

    def test_snapshot_returns_three_layers_and_caches_them(self):
        layer_values = [
            {"id": "pipe_bigquery", "kind": "bigquery", "status": "live", "schemas": [{"name": "nanopro_cbs_bronze", "tables": []}]},
            {"id": "pipe_aws", "kind": "s3", "status": "live", "schemas": [{"name": "nanopro_cbs_bronze", "tables": []}]},
            {"id": "pipe_snowflake", "kind": "snowflake", "status": "live", "schemas": [{"name": "L0_STAGING", "tables": []}]},
        ]
        with patch.object(catalog, "_bigquery_layer", return_value=layer_values[0]) as bq, \
                patch.object(catalog, "_aws_layer", return_value=layer_values[1]), \
                patch.object(catalog, "_snowflake_layer", return_value=layer_values[2]):
            first = catalog.snapshot()
            second = catalog.snapshot()
            third = catalog.snapshot(force=True)

        self.assertFalse(first["cached"])
        self.assertTrue(second["cached"])
        self.assertFalse(third["cached"])
        self.assertEqual(bq.call_count, 2)
        self.assertEqual([layer["kind"] for layer in first["layers"]], ["bigquery", "s3", "snowflake"])
        self.assertIn("generated_at", first)


if __name__ == "__main__":
    unittest.main()
