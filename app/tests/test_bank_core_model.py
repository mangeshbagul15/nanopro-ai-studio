import unittest

from app.core import bank_core_model as model
from app.core.sftp_ingestion import _table_of


class BankCoreModelTest(unittest.TestCase):
    def setUp(self):
        self.summary = model.summary()
        self.index = {spec["table"]: spec for spec in model.all_tables()}

    def test_table_counts(self):
        self.assertEqual(self.summary["base_tables"], 8)
        self.assertEqual(self.summary["new_tables"], 49)
        self.assertEqual(self.summary["total_source_tables"], 57)
        self.assertEqual(self.summary["lanes"], {"bigquery": 42, "sftp": 7})

    def test_volume_is_one_hundred_rows_per_table(self):
        self.assertEqual(model.ROWS_PER_TABLE, 100)
        self.assertEqual(self.summary["rows_per_table"], 100)

    def test_every_table_has_a_primary_key_column(self):
        for spec in model.all_tables():
            names = [name for name, _ in spec["columns"]]
            self.assertTrue(names, spec["table"])
            self.assertIn(spec["pk"][0], names, spec["table"])

    def test_foreign_keys_resolve(self):
        known = set(model.BASE_TABLES) | set(self.index)
        for spec in model.all_tables():
            for column, (parent, parent_column) in (spec.get("fks") or {}).items():
                self.assertIn(column, [name for name, _ in spec["columns"]], spec["table"])
                self.assertIn(parent, known, f"{spec['table']}.{column} -> {parent}")
                if parent in self.index:
                    self.assertIn(parent_column,
                                  [name for name, _ in self.index[parent]["columns"]],
                                  f"{spec['table']}.{column} -> {parent}.{parent_column}")

    def test_names_are_unique(self):
        names = [spec["table"] for spec in model.all_tables()]
        self.assertEqual(len(names), len(set(names)))

    def test_no_credit_card_domain(self):
        for spec in model.all_tables():
            self.assertNotIn("CREDIT_CARD", spec["table"])
            for column, _ in spec["columns"]:
                self.assertNotIn("CREDIT_CARD", column)

    def test_scd_tables(self):
        self.assertEqual(set(model.scd_tables()), {
            "CMG_EXT", "GAM_EXT", "UBO_EXT", "SOL_EXT", "BORROWER_ENTITY",
            "GL_MASTER", "NPO_REGISTRY", "WATCHLIST_ENTRY", "DEBIT_CARD_MASTER",
            "UPI_MERCHANT",
        })

    def test_sftp_tables_are_partner_feeds(self):
        names = {spec["table"] for spec in model.sftp_tables()}
        self.assertEqual(names, {
            "UPI_TRANSACTION", "UPI_MERCHANT", "UPI_DISPUTE", "UPI_SETTLEMENT",
            "NEFT_RTGS_BATCH", "ATM_SWITCH", "DEBIT_CARD_TRANSACTION",
        })
        for spec in model.sftp_tables():
            self.assertTrue(spec["partner"], spec["table"])


class CanonicalSftpNamingTest(unittest.TestCase):
    def test_canonical_feeds_skip_partner_prefix(self):
        for table in ("UPI_TRANSACTION", "UPI_MERCHANT", "UPI_DISPUTE",
                      "UPI_SETTLEMENT", "NEFT_RTGS_BATCH", "ATM_SWITCH",
                      "DEBIT_CARD_TRANSACTION"):
            self.assertEqual(_table_of("ncpi", f"{table.lower()}_20261119.csv"), table)
            self.assertEqual(_table_of("ncpi", f"{table.lower()}.csv"), table)

    def test_partner_named_files_keep_partner_prefix(self):
        self.assertEqual(_table_of("icici", "icici_upi_settlement_20261119.csv"),
                         "ICICI_UPI_SETTLEMENT_20261119")


if __name__ == "__main__":
    unittest.main()
