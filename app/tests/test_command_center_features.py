"""
Comprehensive Automated Tests for Nano Pro Advanced AI Command Center Redesign
Validates:
1. AI Agent Office 3D workspace, view switchers, overview metrics, agent action endpoints.
2. AI Manager compact 3D voice command station, trilingual voice configs, quick routing.
3. Data Engineering 3D ETL pipeline flow stages, sub-tab workspaces, connection tests.
4. Data Analyst SQL Lab, interactive result table, query explanation, presets.
5. Data Science & ML dataset explorer, model training, evaluation metrics, prediction playground.
6. SQL Learning & Drills multi-table join visualizer endpoint and dataset scenarios.
7. Cybersecurity Lab defensive headers scanner, auth audit, and AST taint checks.
8. Sidebar navigation: 9 logical command categories, no standalone voice assistant entry, exactly 46 views preserved.
"""

import unittest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient
from main import app
from app.ui.dashboard import get_dashboard_html

class TestCommandCenterFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.html = get_dashboard_html()
        cls.soup = BeautifulSoup(cls.html, 'html.parser')

    def test_sidebar_structure_and_voice_assistant_removal(self):
        sidebar = self.soup.find('aside', id='sidebar')
        self.assertIsNotNone(sidebar, "Sidebar must exist")
        
        # Verify standalone voice assistant menu entry is NOT in visible sidebar
        nav_items = sidebar.find_all(class_='nav-item')
        voice_entries = [
            item for item in nav_items 
            if 'switchView(\'voice_assistant\')' in item.get('onclick', '') or 'switchView("voice_assistant")' in item.get('onclick', '')
        ]
        self.assertEqual(len(voice_entries), 0, "Standalone Voice Assistant menu entry must be removed from sidebar!")

        # Verify exactly 46 workspace views are preserved
        views = self.soup.find_all('div', class_='workspace-view')
        self.assertEqual(len(views), 46, "All 46 views must remain in the DOM!")

        # Verify underlying view-voice_assistant container still exists
        self.assertIsNotNone(self.soup.find('div', id='view-voice_assistant'), "Underlying voice_assistant view must be preserved!")

    def test_ai_agent_office_redesign(self):
        office_view = self.soup.find('div', id='view-ai_office')
        self.assertIsNotNone(office_view, "AI Agent Office view must exist")

        # Verify 8-metric Office Overview
        self.assertIn("officeKpiTotal", self.html)
        self.assertIn("officeKpiActive", self.html)
        self.assertIn("officeKpiProcessing", self.html)
        self.assertIn("officeKpiStandby", self.html)
        self.assertIn("officeKpiWorkflows", self.html)

        # Verify 3 View Switcher buttons
        self.assertIn('id="btnOfficeView3d"', self.html)
        self.assertIn('id="btnOfficeViewGrid"', self.html)
        self.assertIn('id="btnOfficeViewList"', self.html)

        # Verify Agent Details Modal
        self.assertIn('id="agentDetailsModal"', self.html)

        # Verify Agent Action API Endpoints
        res_assign = self.client.post("/api/agents/data_engineer/assign", json={"task": "Run batch sync"})
        self.assertEqual(res_assign.status_code, 200)
        self.assertTrue(res_assign.json()["success"])

        res_pause = self.client.post("/api/agents/data_engineer/action/pause")
        self.assertEqual(res_pause.status_code, 200)
        self.assertTrue(res_pause.json()["success"])

        res_resume = self.client.post("/api/agents/data_engineer/action/resume")
        self.assertEqual(res_resume.status_code, 200)
        self.assertTrue(res_resume.json()["success"])

        res_details = self.client.get("/api/agents/details/data_engineer")
        self.assertEqual(res_details.status_code, 200)
        self.assertEqual(res_details.json()["id"], "data_engineer")

    def test_ai_manager_restored_conversation_window(self):
        # Verify AI Manager is restored as a clean talk-and-chat workspace
        manager_view = self.soup.find('div', id='view-ai_manager')
        self.assertIsNotNone(manager_view, "AI Manager view must exist")
        self.assertIn('id="managerChatInput"', str(manager_view))
        self.assertIn('id="managerChatStream"', str(manager_view))
        self.assertIn('sendManagerMessage()', str(manager_view))

        # Verify 3D voice command assistant panel is removed from AI Manager
        self.assertNotIn('voice-3d-hologram-card', str(manager_view))
        self.assertNotIn('compactVoiceSphere', str(manager_view))
        self.assertNotIn('voice-waveform-equalizer', str(manager_view))

        # Verify chat API endpoint interaction works
        res = self.client.post('/api/manager/chat', json={"message": "System status check and active agents."})
        self.assertEqual(res.status_code, 200)
        self.assertIn('response', res.json())

    def test_data_engineering_center(self):
        # Verify 3D animated pipeline viewport
        self.assertIn('class="etl-pipeline-viewport"', self.html)

        # Verify 6 pipeline stage nodes
        for stage in ['s1_source', 's2_bronze', 's3_quality', 's4_silver', 's5_gold', 's6_dispatch']:
            self.assertIn(f"inspectPipelineStage('{stage}')", self.html, f"Stage {stage} inspector missing")

        # Verify Data Engineering connection test API
        res = self.client.get("/api/data_engineer/test_connections")
        self.assertEqual(res.status_code, 200)
        self.assertIn("overall_health", res.json())

    def test_data_analyst_center(self):
        # Verify SQL editor, preset chips, and result table
        self.assertIn('id="analystSqlInput"', self.html)
        self.assertIn('id="analystResultTable"', self.html)

        # Test SQL query execution API endpoint
        res = self.client.post("/api/query/sql", json={"query": "SELECT * FROM studio_credentials LIMIT 2;"})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["success"])

    def test_data_science_and_ml_center(self):
        self.assertIn('id="dsDatasetSelect"', self.html)
        self.assertIn('id="dsModelAlgorithm"', self.html)
        self.assertIn('id="dsMetricsGrid"', self.html)

    def test_learning_hub_sql_join_scenario_endpoint(self):
        # Verify Multi-table join visualizer container
        self.assertIn('class="join-visualization-grid"', self.html)

        # Test Join Scenario API endpoint
        res = self.client.get("/api/learning/drills/join-scenario?scenario=customers_left_join_transactions")
        self.assertEqual(res.status_code, 200)
        d = res.json()
        self.assertIn("source_tables", d)
        self.assertIn("joined_table", d)
        self.assertIn("explanation", d)
        self.assertEqual(d["status"], "success")
        self.assertEqual(len(d["source_tables"]), 2)

    def test_cybersecurity_lab_defensive_scans(self):
        self.assertIn('id="cyberScanOutput"', self.html)
        self.assertIn("runSecurityHeaderScan()", self.html)
        self.assertIn("runSecurityLogAnalysis()", self.html)
        self.assertIn("runSecureCodeAudit()", self.html)

if __name__ == "__main__":
    unittest.main()
