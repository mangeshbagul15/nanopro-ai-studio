import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

from app.core import duckdb_report_engine as engine


def _make_parquet(workdir, table, rows):
    import duckdb

    path = str(Path(workdir) / f"{table}.parquet")
    conn = duckdb.connect()
    try:
        conn.execute("CREATE TABLE t (id INTEGER, label VARCHAR)")
        for i in range(rows):
            conn.execute("INSERT INTO t VALUES (?, ?)", [i, f"{table}-{i}"])
        conn.execute(f"COPY t TO '{path.replace(chr(92), '/')}' (FORMAT PARQUET)")
    finally:
        conn.close()
    return path


class DuckDBReportEngineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.workdir = Path(self.tmp.name)
        self.files = [
            {"table": "CMG", "key": "bronze/bigquery/nanopro_cbs_bronze/CMG/CMG.parquet"},
            {"table": "SOL", "key": "bronze/bigquery/nanopro_cbs_bronze/SOL/SOL.parquet"},
        ]
        self.local = {
            "CMG": _make_parquet(self.workdir, "CMG", 3),
            "SOL": _make_parquet(self.workdir, "SOL", 2),
        }
        self._patches = [
            patch("app.core.chat_s3_export._aws_config", return_value={"access_key": "k", "secret_key": "s",
                                                                      "region": "ap-southeast-2", "bucket": "b"}),
            patch.object(engine, "REPORT_DIR", str(self.workdir / "reports")),
        ]
        for item in self._patches:
            item.start()

    def tearDown(self):
        for item in reversed(self._patches):
            item.stop()
        self.tmp.cleanup()
        engine.STATE.clear()

    def _download(self, config, files, workdir):
        return [{"table": name, "path": path} for name, path in self.local.items()]

    def test_reconciles_with_snowflake(self):
        counts = {"CMG": {"l0": 3, "l1": 3}, "SOL": {"l0": 2, "l1": 2}}
        with patch.object(engine, "_download", side_effect=self._download), \
             patch.object(engine, "_snowflake_counts", return_value=counts):
            result = engine.build(self.files, "20261118T000000Z")
        self.assertEqual(result["status"], "reconciled")
        self.assertEqual(result["tables"], 2)
        self.assertEqual(result["rows"], 5)
        self.assertEqual(result["mismatches"], [])
        self.assertTrue(Path(result["report"]).exists())

    def test_reports_mismatch_without_failing(self):
        counts = {"CMG": {"l0": 9, "l1": 9}}
        with patch.object(engine, "_download", side_effect=self._download), \
             patch.object(engine, "_snowflake_counts", return_value=counts):
            result = engine.build(self.files, "run-2")
        self.assertEqual(result["status"], "built")
        self.assertIn("CMG", result["mismatches"])

    def test_builds_from_duckdb_when_snowflake_unreachable(self):
        with patch.object(engine, "_download", side_effect=self._download), \
             patch.object(engine, "_snowflake_counts", side_effect=RuntimeError("no password")):
            result = engine.build(self.files, "run-3")
        self.assertEqual(result["status"], "built")
        self.assertFalse(result["snowflake_checked"])
        self.assertEqual(result["rows"], 5)


if __name__ == "__main__":
    unittest.main()
