import unittest
from fastapi.testclient import TestClient
from main import app
from app.agents.coding_agent import coding_agent
from app.agents.manager_agent import manager_agent
from pathlib import Path

class TestCodeArchitect(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_analyze_file_endpoint(self):
        response = self.client.post("/api/code/analyze-file", json={"file_path": "main.py"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("valid_syntax"))
        self.assertGreater(data.get("lines_of_code", 0), 100)
        self.assertIn("functions", data)

    def test_modify_code_by_prompt_execution(self):
        # Create a temporary scratch file to test prompt-to-code modification safely
        scratch_file = Path("app/agents/scratch_test_code.py")
        scratch_file.write_text("# Initial test file\ndef sample():\n    return 42\n", encoding="utf-8")
        try:
            res = coding_agent.modify_code_by_prompt(
                instruction="Add docstring header and comment",
                file_path=str(scratch_file)
            )
            self.assertTrue(res.get("success"), f"Modification failed: {res}")
            self.assertTrue(res.get("syntax_valid"))
            self.assertTrue(scratch_file.exists())
            self.assertIn("documentation_added", res.get("applied_action", ""))
        finally:
            if scratch_file.exists():
                scratch_file.unlink()

    def test_code_backups_list_and_restore(self):
        response = self.client.get("/api/code/backups")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("backups", data)

    def test_manager_agent_code_mod_intent(self):
        # Test that manager agent detects code modification requests
        result = manager_agent.chat_interact("Please modify code in main.py to add a new health check route")
        self.assertIn("response", result)
        resp_text = result["response"].lower()
        self.assertTrue("code" in resp_text or "architect" in resp_text or "diff" in resp_text or "main.py" in resp_text)

if __name__ == "__main__":
    unittest.main()
