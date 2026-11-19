import unittest

from app.core import bank_core_model as model
from app.core import bank_layers


class _FakeCursor:
    def __init__(self):
        self.statements = []
        self._rows = []

    def execute(self, sql):
        self.statements.append(" ".join(sql.split()))
        self._rows = []

    def fetchall(self):
        rows, self._rows = self._rows, []
        return rows

    def fetchone(self):
        return (0,)


class StarSpecsTest(unittest.TestCase):
    def setUp(self):
        self.specs = bank_layers._star_specs("BANK_DB")
        self.names = {spec["name"] for spec in self.specs}

    def test_names_unique(self):
        self.assertEqual(len(self.names), len(self.specs))

    def test_conformed_dimensions_and_facts(self):
        dims = {name for name in self.names if name.startswith("DIM_")}
        facts = {name for name in self.names if name.startswith("FACT_")}
        self.assertGreaterEqual(len(dims), 11)
        self.assertGreaterEqual(len(facts), 21)
        for required in ("DIM_CUSTOMER", "DIM_ACCOUNT", "DIM_BRANCH", "DIM_DATE",
                         "DIM_CREDIT_CARD", "FACT_TRANSACTION", "FACT_LOAN", "FACT_UPI",
                         "FACT_CARD", "FACT_ATM", "FACT_CREDIT_CARD", "FACT_CARD_STATEMENT",
                         "FACT_COUNTERFEIT", "FACT_WALK_IN_CASH"):
            self.assertIn(required, self.names)

    def test_requirements_resolve(self):
        cur_tables = {spec["table"] for spec in model.all_tables()}
        base_tables = set(model.BASE_TABLES)
        for spec in self.specs:
            for place, table in spec["requires"]:
                if place == "h":
                    self.assertIn(table, cur_tables | base_tables, spec["name"])
                elif place == "c":
                    self.assertIn(table, cur_tables, spec["name"])
                else:
                    self.assertIn(place, ("star",), spec["name"])

    def test_every_spec_has_readable_sql(self):
        for spec in self.specs:
            self.assertIn("FROM", spec["sql"].upper(), spec["name"])
            self.assertNotIn("None", spec["sql"], spec["name"])


class ReportSpecsTest(unittest.TestCase):
    def setUp(self):
        self.specs = bank_layers._report_specs("BANK_DB")
        self.star_names = {spec["name"] for spec in bank_layers._star_specs("BANK_DB")}

    def test_all_report_schemas_are_used(self):
        used = {spec["schema"] for spec in self.specs}
        self.assertEqual(used, set(bank_layers.REPORT_SCHEMAS))

    def test_report_requirements_resolve(self):
        cur_tables = {spec["table"] for spec in model.all_tables()}
        base_tables = set(model.BASE_TABLES)
        for spec in self.specs:
            for place, table in spec["requires"]:
                if place == "h":
                    self.assertIn(table, base_tables | cur_tables, spec["name"])
                elif place == "c":
                    self.assertIn(table, cur_tables, spec["name"])
                elif place == "star":
                    self.assertIn(table, self.star_names, spec["name"])

    def test_report_names_unique_per_schema(self):
        seen = set()
        for spec in self.specs:
            key = (spec["schema"], spec["name"])
            self.assertNotIn(key, seen)
            seen.add(key)

    def test_reports_match_the_bank_catalogue(self):
        fiu = [s for s in self.specs if s["schema"] == "RPT_FIU"]
        rbi = [s for s in self.specs if s["schema"] == "RPT_RBI"]
        alm = [s for s in self.specs if s["schema"] == "RPT_ALM"]
        upi = [s for s in self.specs if s["schema"] == "RPT_UPI"]
        self.assertGreaterEqual(len(fiu), 20)
        self.assertGreaterEqual(len(rbi), 12)
        self.assertGreaterEqual(len(alm), 10)
        self.assertGreaterEqual(len(upi), 8)


class LayerBuildTest(unittest.TestCase):
    def _patched(self, tables):
        from unittest import mock

        return mock.patch.object(
            bank_layers, "_infoschema",
            side_effect=lambda cur, db, schema: set(tables) if schema == bank_layers.HIST_SCHEMA else set())

    def test_current_state_uses_latest_scn_and_drops_deletes(self):
        cursor = _FakeCursor()
        with self._patched({"CMG_EXT"}):
            result = bank_layers.build_current(cursor, "BANK_DB")
        self.assertIn("CMG_EXT", result["current"])
        sql = next(s for s in cursor.statements if "L1_CUR.CMG_EXT" in s)
        self.assertIn('PARTITION BY "CUST_ID"', sql)
        self.assertIn("ORDER BY COMMIT_SCN DESC", sql)
        self.assertIn("OP <> 'D'", sql)

    def test_scd2_has_validity_columns(self):
        cursor = _FakeCursor()
        with self._patched({"CMG_EXT"}):
            result = bank_layers.build_scd2(cursor, "BANK_DB")
        self.assertEqual(result["tables"], ["CMG_EXT"])
        sql = next(s for s in cursor.statements if "L1_SCD2.CMG_EXT" in s)
        for token in ("VALID_FROM", "VALID_TO", "IS_CURRENT", "VERSION", "OP <> 'D'"):
            self.assertIn(token, sql)


class DisabledTest(unittest.TestCase):
    def test_disabled_switch(self):
        import os
        os.environ["NANOPRO_BANK_LAYERS"] = "0"
        try:
            self.assertEqual(bank_layers.build(), {"status": "skipped",
                                                   "reason": "NANOPRO_BANK_LAYERS is off"})
        finally:
            os.environ.pop("NANOPRO_BANK_LAYERS", None)


if __name__ == "__main__":
    unittest.main()
