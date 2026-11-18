import sys
import unittest
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

from app.core import snowflake_lakehouse as lakehouse


COLUMNS = {
    "CMG": [("CUST_ID", "VARCHAR"), ("CUST_NAME", "VARCHAR"), ("CUSTOMER_SEGMENT", "VARCHAR"),
            ("CUST_TYPE", "VARCHAR"), ("KYC_STATUS", "VARCHAR"), ("KYC_RISK_CATEGORY", "VARCHAR"),
            ("ANNUAL_INCOME_TURNOVER", "NUMBER"), ("PEP_FLAG", "BOOLEAN")],
    "GAM": [("ACID", "VARCHAR"), ("CUST_ID", "VARCHAR"), ("SOL_ID", "VARCHAR"), ("CLR_BAL_AMT", "NUMBER")],
    "HTD": [("TRAN_ID", "VARCHAR"), ("TRAN_TYPE", "VARCHAR"), ("TRAN_AMT_INR", "NUMBER")],
    "SOL": [("SOL_ID", "VARCHAR"), ("BRANCH_NAME", "VARCHAR")],
    "SWIFT_MSG": [("SWIFT_ID", "VARCHAR"), ("MESSAGE_TYPE", "VARCHAR")],
    "TAM_LAM": [("CONTRACT_ID", "VARCHAR"), ("CUST_ID", "VARCHAR"), ("CURRENT_OUTSTANDING_BAL", "NUMBER")],
    "UBO": [("UBO_ID", "VARCHAR"), ("CUST_ID", "VARCHAR"), ("SHARE_PCT", "NUMBER"), ("SANCTIONS_HIT", "BOOLEAN")],
    "VCT": [("VCT_ID", "VARCHAR"), ("SOL_ID", "VARCHAR"), ("TOTAL_CASH_AMOUNT", "NUMBER")],
}
AUDIT = [("_RUN_ID", "VARCHAR"), ("_LOADED_AT", "TIMESTAMP_NTZ"), ("_SOURCE_KEY", "VARCHAR")]


class _FakeCursor:
    def __init__(self, columns, counts=None):
        self.columns = columns
        self.counts = counts or {}
        self.statements = []
        self._rows = []
        self._row = None

    def execute(self, sql):
        self.statements.append(" ".join(sql.split()))
        if "INFORMATION_SCHEMA.COLUMNS" in sql:
            names = [name for name in self.columns]
            self._rows = [(table, column, dtype)
                          for table in names
                          for column, dtype in self.columns[table] + AUDIT
                          if f"'{table}'" in sql]
        elif sql.startswith("SELECT COUNT(*)"):
            target = sql.split("FROM", 1)[1].strip()
            self._row = (self.counts.get(target, 0),)
        else:
            self._row = None

    def fetchall(self):
        rows, self._rows = self._rows, []
        return rows

    def fetchone(self):
        return self._row


class BuildL1Test(unittest.TestCase):
    def test_business_key_dedupe_for_every_cbs_table(self):
        cursor = _FakeCursor(COLUMNS)
        result = lakehouse._build_l1(cursor, "BANK_DB", list(COLUMNS))

        self.assertEqual(len(result["tables"]), 8)
        self.assertEqual(result["errors"], [])
        for table, key in lakehouse.L1_KEYS.items():
            detail = result["details"][table]
            self.assertEqual(detail["key"], list(key), table)
            self.assertEqual(detail["strategy"], "business_key", table)
            sql = next(s for s in cursor.statements if f"L1_HARMONIZED.{table} " in s)
            self.assertIn(f'PARTITION BY "{key[0]}"', sql, table)
            self.assertIn('ORDER BY _LOADED_AT DESC', sql, table)

    def test_audit_columns_stay_out_of_l1(self):
        cursor = _FakeCursor({"CMG": COLUMNS["CMG"]})
        lakehouse._build_l1(cursor, "BANK_DB", ["CMG"])
        create_sql = next(s for s in cursor.statements if "CREATE OR REPLACE TABLE" in s)
        self.assertNotIn('"_RUN_ID"', create_sql)
        self.assertNotIn('"_SOURCE_KEY"', create_sql)
        self.assertIn('"ANNUAL_INCOME_TURNOVER"', create_sql)

    def test_unknown_table_falls_back_to_full_row_dedupe(self):
        cursor = _FakeCursor({"ADHOC": [("ID", "VARCHAR"), ("NOTE", "VARCHAR")]})
        result = lakehouse._build_l1(cursor, "BANK_DB", ["ADHOC"])
        self.assertEqual(result["details"]["ADHOC"]["strategy"], "full_row")
        create_sql = next(s for s in cursor.statements if "CREATE OR REPLACE TABLE" in s)
        self.assertIn("SELECT DISTINCT", create_sql)


class BuildL2Test(unittest.TestCase):
    def _counts(self):
        counts = {f"BANK_DB.L0_STAGING.{t}": 5 for t in COLUMNS}
        counts.update({f"BANK_DB.L1_HARMONIZED.{t}": 4 for t in COLUMNS})
        for mart in lakehouse._marts("BANK_DB"):
            counts[f"BANK_DB.L2_CURATED.{mart['name']}"] = 2
        return counts

    def test_all_business_marts_build_when_every_table_is_present(self):
        details = {t: {"key": list(k), "strategy": "business_key"} for t, k in lakehouse.L1_KEYS.items()}
        cursor = _FakeCursor(COLUMNS, self._counts())
        result = lakehouse._build_l2(cursor, "BANK_DB", list(COLUMNS), details)

        expected = {mart["name"] for mart in lakehouse._marts("BANK_DB")}
        self.assertEqual(set(result["marts"]), expected)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["skipped"], [])
        self.assertEqual(result["rows"]["CUSTOMER_360_MART"], 2)

    def test_marts_skip_when_source_tables_are_missing(self):
        cursor = _FakeCursor({"CMG": COLUMNS["CMG"]}, self._counts())
        result = lakehouse._build_l2(cursor, "BANK_DB", ["CMG"], {"CMG": {"key": ["CUST_ID"], "strategy": "business_key"}})
        self.assertEqual(result["marts"], ["CUSTOMER_SEGMENT_MART"])
        skipped = " | ".join(result["skipped"])
        self.assertIn("CUSTOMER_360_MART", skipped)
        self.assertIn("BRANCH_NETWORK_MART", skipped)

    def test_quality_mart_keeps_keys_and_dedupe_counts(self):
        details = {"CMG": {"key": ["CUST_ID"], "strategy": "business_key"}}
        counts = {"BANK_DB.L0_STAGING.CMG": 50, "BANK_DB.L1_HARMONIZED.CMG": 48}
        cursor = _FakeCursor({"CMG": COLUMNS["CMG"]}, counts)
        result = lakehouse._build_l2(cursor, "BANK_DB", ["CMG"], details)

        self.assertEqual(result["quality"][0][:4], ("CMG", 50, 48, 2))
        ddl = next(s for s in cursor.statements if "DATA_QUALITY_MART (" in s)
        self.assertIn("KEY_COLUMNS", ddl)
        self.assertIn("DEDUPE_STRATEGY", ddl)
        insert_sql = next(s for s in cursor.statements if "INSERT INTO BANK_DB.L2_CURATED.DATA_QUALITY_MART" in s)
        self.assertIn("'CUST_ID'", insert_sql)
        self.assertIn("'business_key'", insert_sql)

    def test_catalog_records_only_built_marts(self):
        cursor = _FakeCursor({"CMG": COLUMNS["CMG"]}, self._counts())
        lakehouse._build_l2(cursor, "BANK_DB", ["CMG"], {"CMG": {"key": ["CUST_ID"], "strategy": "business_key"}})
        insert_sql = next(s for s in cursor.statements if "INSERT INTO BANK_DB.L2_CURATED.MART_CATALOG" in s)
        self.assertIn("'CUSTOMER_SEGMENT_MART'", insert_sql)
        self.assertIn("'DATA_QUALITY_MART'", insert_sql)
        self.assertNotIn("'CUSTOMER_360_MART'", insert_sql)


if __name__ == "__main__":
    unittest.main()
