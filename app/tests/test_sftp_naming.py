import unittest

from app.core.sftp_ingestion import _table_of


class SftpNamingTest(unittest.TestCase):
    def test_partner_prefix_is_not_repeated(self):
        self.assertEqual(_table_of("icici", "icici_upi_settlement_20261119.csv"),
                         "ICICI_UPI_SETTLEMENT_20261119")
        self.assertEqual(_table_of("icici", "icici.csv"), "ICICI")

    def test_partner_comes_first_for_plain_names(self):
        self.assertEqual(_table_of("hdfc", "partner_payments_20261119.xlsx"),
                         "HDFC_PARTNER_PAYMENTS_20261119")

    def test_numeric_stem_keeps_the_partner_prefix(self):
        self.assertEqual(_table_of("manual", "2026-11-19.csv"), "MANUAL_2026_11_19")

    def test_numeric_partner_gets_a_letter_prefix(self):
        self.assertEqual(_table_of("123", "report.csv"), "T_123_REPORT")

    def test_name_is_capped_at_the_snowflake_limit(self):
        self.assertEqual(len(_table_of("axis", "x" * 80 + ".csv")), 60)


if __name__ == "__main__":
    unittest.main()
