import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GLOBAL_AI_LAB_SOURCE = REPO_ROOT / "app" / "ui" / "global_ai_lab_view.py"
STATIC_DASHBOARD = REPO_ROOT / "deploy" / "complete_nanopro_dashboard.html"


class GlobalAILabAPIAuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = GLOBAL_AI_LAB_SOURCE.read_text(encoding="utf-8")
        cls.static_html = STATIC_DASHBOARD.read_text(encoding="utf-8")

    def test_protected_apis_use_session_aware_fetch(self):
        self.assertTrue("window.ailabAuthFetch = function" in self.html)
        self.assertTrue('localStorage.getItem("nanopro_session_token")' in self.html)
        self.assertTrue('ailabAuthFetch("/api/ai/explorer/catalog"' in self.html)
        self.assertTrue('ailabAuthFetch(ORCH_API + "/overview"' in self.html)

    def test_explorer_surfaces_aws_list_permission_error(self):
        self.assertTrue("s3:ListBucket" in self.html)
        self.assertTrue("db.error" in self.html)
        self.assertTrue("db.detail" in self.html)
        self.assertTrue("s3ListDenied" in self.html)

    def test_explorer_stops_retrying_when_session_is_unauthorized(self):
        self.assertTrue("res.status === 401" in self.html)
        self.assertTrue("login_gateway.html" in self.html)

    def test_orchestrator_launcher_describes_the_current_tabs(self):
        self.assertTrue("DAGs • SFTP • Alerts • Logs" in self.html)

    def test_orchestrator_auth_error_links_to_login(self):
        self.assertTrue('Session expired - <a href="/login_gateway.html"' in self.html)

    def test_static_dashboard_contains_the_updated_global_ai_lab_view(self):
        self.assertTrue("window.ailabAuthFetch = function" in self.static_html)
        self.assertTrue('ailabAuthFetch("/api/ai/explorer/catalog"' in self.static_html)
        self.assertTrue("DAGs • SFTP • Alerts • Logs" in self.static_html)
        self.assertEqual(1, self.static_html.count("<!-- VIEW: GLOBAL AI LAB (FEATURE 53) -->"))


if __name__ == "__main__":
    unittest.main()
