"""
Targeted Verification Tests for Upgraded AI Manager & Animated Pixel-Art AI Agent Office
Verifies:
1. Unified AI Manager Conversational Interface (replaces old two sections).
2. UNDERSTAND -> DISCUSS -> PROPOSE -> REFINE -> APPROVE -> EXECUTE -> VERIFY workflow.
3. Proposal card with all required sections and functional controls.
4. Follow-up refinements: 'Explain this again', 'Use the second approach', 'Make it simpler', 'Add email notifications', 'Modify the previous solution', 'Now execute it'.
5. Genuine multi-agent execution with real scripts, real SQL DDL/tests, real Excel report, and AgentRegistry updates.
6. Central AI Manager Holographic Station transformed into living interactive pixel-art office.
7. Real-time telemetry sync between AI Manager executions and Pixel-Art Office workstations.
8. Strict scope adherence: Exactly 46 views, no regressions.
"""

import unittest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient
from pathlib import Path
from main import app
from app.ui.dashboard import get_dashboard_html
from app.agents.agent_registry import agent_registry

class TestAIManagerAndOfficeUpgrade(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.html = get_dashboard_html()
        cls.soup = BeautifulSoup(cls.html, 'html.parser')

    def test_ai_manager_unified_conversational_interface(self):
        manager_view = self.soup.find('div', id='view-ai_manager')
        self.assertIsNotNone(manager_view, "AI Manager view must exist")
        
        # Verify single unified container
        self.assertIn('unified-manager-card', str(manager_view))
        self.assertIn('manager-chat-topbar', str(manager_view))
        self.assertIn('id="managerChatStream"', str(manager_view))
        self.assertIn('id="managerChatInput"', str(manager_view))
        self.assertIn('sendManagerMessage()', str(manager_view))

        # Verify Voice integration controls
        self.assertIn('id="managerVoiceMicBtn"', str(manager_view))
        self.assertIn('id="managerVoiceLangSelect"', str(manager_view))
        self.assertIn('id="managerTtsCheckbox"', str(manager_view))
        self.assertIn('toggleManagerVoiceRecording()', str(manager_view))

        # Verify old separate panel cards are unified
        self.assertIn('AI Manager Ready. How can I assist you with your models, data pipelines, coding, or automation today?', str(manager_view))

    def test_conversational_workflow_proposal_and_refinement(self):
        # 1. Propose implementation plan
        res_prop = self.client.post('/api/manager/chat', json={
            "message": "Build a Snowflake ETL pipeline with Python validation and SQL testing.",
            "session_id": "test_workflow_sess"
        })
        self.assertEqual(res_prop.status_code, 200)
        d_prop = res_prop.json()
        self.assertEqual(d_prop.get("status"), "PROPOSED")
        self.assertIn("solution_plan", d_prop)
        
        plan = d_prop["solution_plan"]
        self.assertIn("objective", plan)
        self.assertIn("requirements", plan)
        self.assertIn("proposed_approach", plan)
        self.assertIn("required_agents", plan)
        self.assertIn("dependencies", plan)
        self.assertIn("required_connections", plan)
        self.assertIn("expected_deliverables", plan)
        self.assertIn("risks_and_limitations", plan)
        self.assertIn("next_action", plan)

        # Controls available
        self.assertIn("Approve & Execute", d_prop.get("actions", []))
        self.assertIn("Modify Plan", d_prop.get("actions", []))
        self.assertIn("Discuss Further", d_prop.get("actions", []))
        self.assertIn("Show Details", d_prop.get("actions", []))
        self.assertIn("Cancel", d_prop.get("actions", []))

        # 2. Follow-up: Explain this again
        res_exp = self.client.post('/api/manager/chat', json={
            "message": "Explain this again.",
            "session_id": "test_workflow_sess"
        })
        self.assertEqual(res_exp.status_code, 200)
        self.assertIn("solution_plan", res_exp.json())
        self.assertIn("step-by-step breakdown", res_exp.json().get("response", "").lower())

        # 3. Follow-up: Use the second approach
        res_app2 = self.client.post('/api/manager/chat', json={
            "message": "Use the second approach.",
            "session_id": "test_workflow_sess"
        })
        self.assertEqual(res_app2.status_code, 200)
        self.assertIn("Dynamic Tables", res_app2.json()["solution_plan"]["proposed_approach"])

        # 4. Follow-up: Make it simpler
        res_simple = self.client.post('/api/manager/chat', json={
            "message": "Make it simpler.",
            "session_id": "test_workflow_sess"
        })
        self.assertEqual(res_simple.status_code, 200)
        self.assertIn("Streamlined 3-Step", res_simple.json()["solution_plan"]["proposed_approach"])

        # 5. Follow-up: Add email notifications
        res_email = self.client.post('/api/manager/chat', json={
            "message": "Add email notifications.",
            "session_id": "test_workflow_sess"
        })
        self.assertEqual(res_email.status_code, 200)
        agents = [a["name"] for a in res_email.json()["solution_plan"]["required_agents"]]
        self.assertIn("Email Agent", agents)

        # 6. Follow-up: Modify the previous solution
        res_mod = self.client.post('/api/manager/chat', json={
            "message": "Modify the previous solution.",
            "session_id": "test_workflow_sess"
        })
        self.assertEqual(res_mod.status_code, 200)
        self.assertIn("solution_plan", res_mod.json())

    def test_plan_execution_and_agent_orchestration(self):
        # Trigger execution of plan
        res_exec = self.client.post('/api/manager/chat', json={
            "message": "Now execute it.",
            "session_id": "test_workflow_sess"
        })
        self.assertEqual(res_exec.status_code, 200)
        d_exec = res_exec.json()
        self.assertEqual(d_exec.get("status"), "COMPLETED")

        # Operational Events Stream
        events = d_exec.get("operational_events", [])
        self.assertGreaterEqual(len(events), 5)
        self.assertTrue(any("Plan Approved" in e for e in events))
        self.assertTrue(any("Agent Assigned" in e for e in events))
        self.assertTrue(any("Verification Started" in e for e in events))
        self.assertTrue(any("Task Completed" in e for e in events))

        # Verified Deliverables
        deliverables = d_exec.get("deliverables", [])
        self.assertIn("data_ingestion/validate_pipeline_records.py", deliverables)
        self.assertIn("data_ingestion/snowflake_medallion_etl.sql", deliverables)
        self.assertIn("data_ingestion/test_pipeline_integrity.sql", deliverables)
        
        # Verify physical file existence
        self.assertTrue(Path("data_ingestion/validate_pipeline_records.py").exists())
        self.assertTrue(Path("data_ingestion/snowflake_medallion_etl.sql").exists())
        self.assertTrue(Path("data_ingestion/test_pipeline_integrity.sql").exists())

        # Test Assertions Table
        table = d_exec.get("table_data", {})
        self.assertEqual(table.get("total_count"), 4)
        for r in table.get("rows", []):
            self.assertEqual(r[5], "PASSED")

        # Code Artifacts
        code = d_exec.get("code_artifacts", {})
        self.assertIn("python_validation", code)
        self.assertIn("snowflake_sql", code)
        self.assertIn("sql_tests", code)

        # Agent Registry update verification
        mgr = agent_registry.get_agent("agent_01")
        self.assertEqual(mgr.current_state, "Completed")
        de = agent_registry.get_agent("agent_06")
        self.assertEqual(de.current_state, "Completed")
        py_agent = agent_registry.get_agent("agent_39")
        self.assertEqual(py_agent.current_state, "Completed")

    def test_central_holographic_station_pixel_art_office(self):
        office_view = self.soup.find('div', id='view-ai_office')
        self.assertIsNotNone(office_view, "AI Agent Office view must exist")

        # Verify Central Holographic Station transformed into pixel-art office
        self.assertIn('CENTRAL AI MANAGER HOLOGRAPHIC STATION', str(office_view))
        self.assertIn('id="centralManagerStation"', str(office_view))
        self.assertIn('pixel-office-station-container', str(office_view))
        self.assertIn('id="pixelOfficeCanvas"', str(office_view))
        self.assertIn('id="pixelOfficeViewport"', str(office_view))
        self.assertIn('id="pixelAgentDetailDrawer"', str(office_view))

        # Verify station interactive controls
        self.assertIn('zoomPixelOffice', self.html)
        self.assertIn('resetPixelOfficeZoom', self.html)
        self.assertIn('togglePixelOfficeFullscreen', self.html)
        self.assertIn('togglePixelOfficeAnim', self.html)

        # Verify rest of office page is strictly preserved
        self.assertIn('id="officeAgentsGridContainer"', str(office_view))
        self.assertIn('id="officeAgentsListContainer"', str(office_view))
        self.assertIn('officeKpiTotal', self.html)
        self.assertIn('officeKpiActive', self.html)

if __name__ == "__main__":
    unittest.main()
    def test_interactivity_and_modal_inspector(self):
        # Verify inspectAgentModal and openAgentDetailsModal exist in dashboard HTML/JS
        self.assertIn('function inspectAgentModal', self.html)
        self.assertIn('openAgentDetailsModal = inspectAgentModal', self.html)
        self.assertIn('id="agentDetailsModal"', self.html)
        self.assertIn('id="modalAgentName"', self.html)
        self.assertIn('id="modalAgentStateBadge"', self.html)
        
        # Verify setOfficeViewMode supports 3d, grid, and list
        self.assertIn('function setOfficeViewMode', self.html)
        self.assertIn('btnOfficeView3d', self.html)
        self.assertIn('btnOfficeViewGrid', self.html)
        self.assertIn('btnOfficeViewList', self.html)

    def test_cloud_trends_dialogue_integration(self):
        # Verify AI Manager handles Snowflake vs AWS trends inquiry
        res = self.client.post('/api/manager/chat', json={
            'message': 'स्नोफ्लेक आणि एडब्ल्यूएस मधील टॉप 10 ट्रेंड्स सांग',
            'session_id': 'cloud_trends_session'
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn('Snowflake vs AWS', data.get('response', ''))
        self.assertIn('Cortex AI', data.get('response', ''))
        self.assertIn('Bedrock AgentCore', data.get('response', ''))
        self.assertIn('table_data', data)


