import unittest

from app.core import bank_core_model as model
from app.core.sftp_ingestion import _table_of


class BankCoreModelTest(unittest.TestCase):
    def setUp(self):
        self.summary = model.summary()
        self.index = {spec["table"]: spec for spec in model.all_tables()}

    def test_table_counts(self):
        self.assertEqual(self.summary["base_tables"], 8)
        self.assertEqual(self.summary["new_tables"], 54)
        self.assertEqual(self.summary["total_source_tables"], 62)
        self.assertEqual(self.summary["lanes"], {"bigquery": 42, "sftp": 12})

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

    def test_credit_card_and_cash_domain_present(self):
        names = {spec["table"] for spec in model.all_tables()}
        for table in ("CREDIT_CARD_MASTER", "CREDIT_CARD_TRANSACTION",
                      "CREDIT_CARD_STATEMENT", "COUNTERFEIT_INCIDENT",
                      "WALK_IN_CASH_TXN"):
            self.assertIn(table, names)

    def test_scd_tables(self):
        self.assertEqual(set(model.scd_tables()), {
            "CMG_EXT", "GAM_EXT", "UBO_EXT", "SOL_EXT", "BORROWER_ENTITY",
            "GL_MASTER", "NPO_REGISTRY", "WATCHLIST_ENTRY", "DEBIT_CARD_MASTER",
            "CREDIT_CARD_MASTER", "UPI_MERCHANT",
        })

    def test_sftp_tables_are_partner_feeds(self):
        names = {spec["table"] for spec in model.sftp_tables()}
        self.assertEqual(names, {
            "UPI_TRANSACTION", "UPI_MERCHANT", "UPI_DISPUTE", "UPI_SETTLEMENT",
            "NEFT_RTGS_BATCH", "ATM_SWITCH", "DEBIT_CARD_TRANSACTION",
            "CREDIT_CARD_MASTER", "CREDIT_CARD_TRANSACTION", "CREDIT_CARD_STATEMENT",
            "COUNTERFEIT_INCIDENT", "WALK_IN_CASH_TXN",
        })
        for spec in model.sftp_tables():
            self.assertTrue(spec["partner"], spec["table"])


class CanonicalSftpNamingTest(unittest.TestCase):
    def test_canonical_feeds_skip_partner_prefix(self):
        for table in ("UPI_TRANSACTION", "UPI_MERCHANT", "UPI_DISPUTE",
                      "UPI_SETTLEMENT", "NEFT_RTGS_BATCH", "ATM_SWITCH",
                      "DEBIT_CARD_TRANSACTION", "CREDIT_CARD_MASTER",
                      "CREDIT_CARD_TRANSACTION", "CREDIT_CARD_STATEMENT",
                      "COUNTERFEIT_INCIDENT", "WALK_IN_CASH_TXN"):
            self.assertEqual(_table_of("ncpi", f"{table.lower()}_20261119.csv"), table)
            self.assertEqual(_table_of("ncpi", f"{table.lower()}.csv"), table)

    def test_partner_named_files_keep_partner_prefix(self):
        self.assertEqual(_table_of("icici", "icici_upi_settlement_20261119.csv"),
                         "ICICI_UPI_SETTLEMENT_20261119")


class SeedRowGenerationTest(unittest.TestCase):
    def setUp(self):
        from datetime import date

        from app.core import bank_core_seed as seed

        self.seed = seed
        self.today = date.today()
        self.keys = {
            (table, pk): [f"{table}{index:06d}" for index in range(1, 101)]
            for table, pk in model.BASE_TABLES.items()
        }

    def test_every_table_generates_all_declared_columns(self):
        for spec in model.all_tables():
            for index in (1, 5, 50, 100):
                row = self.seed._rows_for(spec, index, self.keys, self.today)
                missing = [name for name, _ in spec["columns"] if name not in row]
                self.assertEqual(missing, [], f"{spec['table']} @ {index}")

    def test_credit_card_and_cash_derivations(self):
        txn = model.get("CREDIT_CARD_TRANSACTION")
        row = self.seed._rows_for(txn, 7, self.keys, self.today)
        self.assertIn("INR_AMOUNT", row)
        self.assertIsInstance(row["FOREIGN_FLAG"], bool)

        stmt = model.get("CREDIT_CARD_STATEMENT")
        row = self.seed._rows_for(stmt, 9, self.keys, self.today)
        self.assertLessEqual(row["DAYS_PAST_DUE"], 180)
        self.assertAlmostEqual(row["MIN_DUE"], round(float(row["TOTAL_DUE"]) * 0.05, 2), places=2)

    def test_categorical_columns_use_bank_domains(self):
        deposit = self.seed._rows_for(model.get("DEPOSIT_MASTER"), 3, self.keys, self.today)
        self.assertIn(deposit["RATE_TYPE"], ("FIXED", "FLOATING"))
        self.assertIn(deposit["BENCHMARK"], ("REPO", "MCLR", "TBILL", "CMT", "SOFR"))
        card = self.seed._rows_for(model.get("CREDIT_CARD_MASTER"), 4, self.keys, self.today)
        self.assertEqual(card["CARD_TYPE"], "CREDIT")


if __name__ == "__main__":
    unittest.main()
