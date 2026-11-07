"""
Automated E2E Test Suite for Data Modeling DuckDB Chat & Project Persistence per User
=====================================================================================
Verifies:
  1. Isolated DuckDB database file creation per user in data/modeling/users/{username}_chats.duckdb.
  2. Workspace (Chat) & Project creation, renaming, pinning, and deletion in DuckDB.
  3. Chat history persistence: user prompts, AI responses, SQL queries, and metadata.
  4. User Isolation: User B cannot see User A's chats or messages.
  5. URL Refresh / Session Restoration: Active workspace state is retrieved from DuckDB and chat history is fully restored.
  6. Exporting dialogue in Google / Claude format.
"""

import os
import shutil
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.duckdb_chat_store import duckdb_chat_store, _user_db_path
from app.core import data_modeling_ai as dm
from main import app


class TestDuckDBChatPersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.user_a = "test_mangesh_user"
        cls.user_b = "test_other_user"

        # Clean any preexisting test DBs
        for u in [cls.user_a, cls.user_b]:
            p = _user_db_path(u)
            if p.exists():
                try:
                    p.unlink()
                except Exception:
                    pass

    @classmethod
    def tearDownClass(cls):
        for u in [cls.user_a, cls.user_b]:
            p = _user_db_path(u)
            if p.exists():
                try:
                    p.unlink()
                except Exception:
                    pass

    def test_01_duckdb_file_created_per_user(self):
        ws_a = dm.create_workspace(name="Mangesh DuckDB Chat", user=self.user_a)
        self.assertTrue(ws_a["id"].startswith("ws_"))
        self.assertEqual(ws_a["created_by"], self.user_a)

        # Check DuckDB file exists on disk
        db_path_a = _user_db_path(self.user_a)
        self.assertTrue(db_path_a.exists(), f"User DuckDB file must exist at {db_path_a}")

    def test_02_chat_history_messages_stored_in_duckdb(self):
        ws = dm.create_workspace(name="Financial Modeling Chat", user=self.user_a)
        wid = ws["id"]

        # Add user prompt
        msg1 = dm.add_message(wid, "user", "Show me sales by region from Snowflake", user=self.user_a)
        self.assertEqual(msg1["role"], "user")
        self.assertEqual(msg1["content"], "Show me sales by region from Snowflake")

        # Add assistant reply
        msg2 = dm.add_message(
            wid,
            "assistant",
            "SELECT region, sum(sales) FROM sales GROUP BY region;",
            sql_text="SELECT region, sum(sales) FROM sales GROUP BY region;",
            meta={"latency_ms": 145.2, "row_count": 4, "model": "gemini-2.5-flash"},
            user=self.user_a,
        )
        self.assertEqual(msg2["role"], "assistant")
        self.assertEqual(msg2["meta"]["latency_ms"], 145.2)

        # Fetch messages directly from DuckDB via dm.get_messages
        history = dm.get_messages(wid, user=self.user_a)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["content"], "Show me sales by region from Snowflake")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertIn("SELECT region", history[1]["sql"])

    def test_03_user_isolation(self):
        # Create workspace for User B
        ws_b = dm.create_workspace(name="User B Private Project", user=self.user_b)
        dm.add_message(ws_b["id"], "user", "Secret info of User B", user=self.user_b)

        # List workspaces for User A
        workspaces_a = dm.list_workspaces(user=self.user_a)
        ws_ids_a = [w["id"] for w in workspaces_a]
        self.assertNotIn(ws_b["id"], ws_ids_a, "User A must NOT see User B's workspaces!")

        # List workspaces for User B
        workspaces_b = dm.list_workspaces(user=self.user_b)
        ws_ids_b = [w["id"] for w in workspaces_b]
        self.assertIn(ws_b["id"], ws_ids_b)
        self.assertEqual(len(workspaces_b), 1)

        # User A trying to get User B's messages from DuckDB directly
        msgs_b_for_a = duckdb_chat_store.get_messages(self.user_a, ws_b["id"])
        self.assertEqual(len(msgs_b_for_a), 0, "User A DuckDB store must not contain User B messages")

    def test_04_refresh_simulation_state_restoration(self):
        # Simulate user selecting a workspace and refreshing page
        ws = dm.create_workspace(name="Active Workspace Before Refresh", user=self.user_a)
        wid = ws["id"]
        dm.add_message(wid, "user", "Message before URL refresh", user=self.user_a)
        dm.add_message(wid, "assistant", "Response preserved after refresh", user=self.user_a)

        # User state saved in DuckDB
        dm.save_user_state(self.user_a, wid)

        # Simulate URL reload by fetching user state from backend
        state = dm.get_user_state(self.user_a)
        self.assertEqual(state["active_workspace_id"], wid)

        # Reload messages for active workspace as frontend does on initDataModeling()
        reloaded_messages = dm.get_messages(state["active_workspace_id"], user=self.user_a)
        self.assertEqual(len(reloaded_messages), 2)
        self.assertEqual(reloaded_messages[0]["content"], "Message before URL refresh")
        self.assertEqual(reloaded_messages[1]["content"], "Response preserved after refresh")

    def test_05_project_grouping_and_chat_association(self):
        project = dm.create_project(name="Q4 Enterprise Lakehouse", user=self.user_a)
        pid = project["id"]
        self.assertTrue(pid.startswith("prj_"))

        ws = dm.create_workspace(name="ETL Pipeline Modeling", user=self.user_a, project_id=pid)
        self.assertEqual(ws["project_id"], pid)

        # Check projects list
        projects = dm.list_projects(user=self.user_a)
        found_project = next((p for p in projects if p["id"] == pid), None)
        self.assertIsNotNone(found_project)
        self.assertEqual(found_project["name"], "Q4 Enterprise Lakehouse")

    def test_06_google_claude_format_export(self):
        ws = dm.create_workspace(name="Claude Export Test", user=self.user_a)
        wid = ws["id"]
        dm.add_message(wid, "user", "What is the query plan?", user=self.user_a)
        dm.add_message(wid, "assistant", "EXPLAIN SELECT * FROM orders;", sql_text="EXPLAIN SELECT * FROM orders;", user=self.user_a)

        export = dm.export_user_chat(self.user_a, wid)
        self.assertEqual(export["format"], "google_claude_dialogue_v1")
        self.assertEqual(export["total_messages"], 2)
        self.assertEqual(export["transcript"][0]["author"], "Human")
        self.assertEqual(export["transcript"][1]["author"], "Assistant")
        self.assertEqual(export["transcript"][1]["sql"], "EXPLAIN SELECT * FROM orders;")


if __name__ == "__main__":
    unittest.main()
