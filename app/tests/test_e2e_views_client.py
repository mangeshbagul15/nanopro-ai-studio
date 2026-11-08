import unittest
from fastapi.testclient import TestClient
from main import app
from bs4 import BeautifulSoup

class TestAll46ViewsClientEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        res = cls.client.get("/")
        assert res.status_code == 200, f"Dashboard failed with status {res.status_code}"
        cls.html = res.text
        cls.soup = BeautifulSoup(cls.html, 'html.parser')

    def test_all_46_views_rendered_inside_viewport(self):
        views = self.soup.find_all('div', class_='workspace-view')
        self.assertEqual(len(views), 46)
        
        viewport = self.soup.find('main', id='main-content-viewport')
        self.assertIsNotNone(viewport)
        vp_views = viewport.find_all('div', class_='workspace-view')
        self.assertEqual(len(vp_views), 46)

    def test_core_api_endpoints_connectivity(self):
        # 1. Models
        res = self.client.get("/api/models/list")
        self.assertEqual(res.status_code, 200)

        # 2. Vault (requires Super Admin session)
        res = self.client.get("/api/vault/list")
        self.assertIn(res.status_code, (401, 403))

        # 3. Connections
        res = self.client.get("/api/connections/list")
        self.assertEqual(res.status_code, 200)

        # 4. Operations State
        res = self.client.get("/api/operations/state")
        self.assertEqual(res.status_code, 200)
        d = res.json()
        self.assertEqual(d.get("total_agents"), 205)

        # 5. Cloud Trends
        res = self.client.get("/api/cloud-trends/summary")
        self.assertEqual(res.status_code, 200)
        d = res.json()
        self.assertEqual(len(d.get("snowflake_trends", [])), 10)
        self.assertEqual(len(d.get("aws_trends", [])), 10)

        # 6. Approvals
        res = self.client.get("/api/approvals/list")
        self.assertEqual(res.status_code, 200)

        # 7. Reminders / Assistant
        res = self.client.get("/api/reminders")
        self.assertEqual(res.status_code, 200)

        # 8. Storage Dashboard
        res = self.client.get("/api/storage/usage")
        self.assertEqual(res.status_code, 200)

        # 9. Discovery Dashboard
        res = self.client.get("/api/discovery/system/issues")
        self.assertEqual(res.status_code, 200)

        # 10. Amazon Tracker
        res = self.client.get("/api/amazon/products")
        self.assertEqual(res.status_code, 200)

        # 11. Career Hub
        res = self.client.post("/api/career/jobs/search", json={"role": "Data Engineer", "location": "Mumbai"})
        self.assertEqual(res.status_code, 200)

        # 12. Logs
        res = self.client.get("/api/logs/live")
        self.assertEqual(res.status_code, 200)

        # 13. System Health / Monitoring
        res = self.client.get("/api/monitoring/health")
        self.assertEqual(res.status_code, 200)

        # 14. Task History
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)

        # 15. Free APIs
        res = self.client.get("/api/discovery/apis")
        self.assertEqual(res.status_code, 200)

        # 16. Research Library
        res = self.client.get("/api/discovery/library")
        self.assertEqual(res.status_code, 200)

        # 17. News Center
        res = self.client.get("/api/news/articles")
        self.assertEqual(res.status_code, 200)

        # 18. Entertainment Center
        res = self.client.get("/api/entertainment/items?category=All")
        self.assertEqual(res.status_code, 200)

        # 19. Book Reader
        res = self.client.get("/api/books/list")
        self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
