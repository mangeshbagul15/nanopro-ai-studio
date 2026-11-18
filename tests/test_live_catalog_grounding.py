"""Database answers must be grounded in the live catalog, never model memory."""
import unittest
from unittest import mock

from app.core import live_catalog_context as lc


CATALOG = [
    {
        "id": "connection:GOOGLE_BIGQUERY_SANDBOX",
        "name": "Google BigQuery",
        "engine": "bigquery",
        "status": "live",
        "error": "",
        "schemas": [
            {"name": "nanopro_cbs_bronze", "tables": ["CMG", "GAM", "HTD", "SOL", "SWIFT_MSG", "TAM_LAM", "UBO", "VCT"]},
            {"name": "nanopro_studio", "tables": ["ai_chat_attachments", "ai_chat_messages"]},
        ],
    },
    {
        "id": "connection:NANO_PRO_SNOWFLAKE",
        "name": "Snowflake Warehouse",
        "engine": "snowflake",
        "status": "live",
        "error": "",
        "schemas": [],
    },
]


class TestCatalogIntent(unittest.TestCase):

    def test_catalog_questions_are_detected(self):
        prompts = [
            "Google BigQuery ya madhe konta schema ahe?",
            "nanopro madhe db kiti ahet",
            "Data Explorer madhun live datasets bagh",
            "Which schemas exist in Snowflake?",
            "how many tables in nanopro_cbs_bronze",
            "RAW_DATA madhe kay ahe?",
            "AUDIT_LOGS kiti records ahet",
        ]
        for prompt in prompts:
            self.assertTrue(lc.is_catalog_question(prompt), prompt)

    def test_ordinary_chat_is_not_grounded(self):
        prompts = [
            "write a python script",
            "explain the medallion architecture",
            "generate a logo for nanopro",
            "how are you?",
        ]
        for prompt in prompts:
            self.assertFalse(lc.is_catalog_question(prompt), prompt)


class TestCatalogPrompt(unittest.TestCase):

    def _prompt(self, question: str) -> str:
        with mock.patch.object(lc, "live_databases", return_value=CATALOG):
            return lc.system_prompt_for(question) or ""

    def test_prompt_lists_only_live_objects(self):
        prompt = self._prompt("Google BigQuery madhe konta schema ahe?")
        self.assertIn("nanopro_cbs_bronze", prompt)
        self.assertIn("nanopro_studio", prompt)
        self.assertIn("SWIFT_MSG", prompt)
        self.assertNotIn("BANK_DB", prompt)
        self.assertNotIn("RAW_DATA", prompt)

    def test_empty_connection_is_reported_as_empty(self):
        prompt = self._prompt("Snowflake madhe konta schema ahe?")
        self.assertIn("schemas: 0", prompt)

    def test_rules_forbid_invention(self):
        prompt = self._prompt("how many databases does NanoPro have?")
        self.assertIn("Never invent", prompt)
        self.assertIn("LIVE DATA CATALOG", prompt)

    def test_non_catalog_question_gets_no_prompt(self):
        with mock.patch.object(lc, "live_databases", return_value=CATALOG):
            self.assertIsNone(lc.system_prompt_for("write a python script"))


if __name__ == "__main__":
    unittest.main()
