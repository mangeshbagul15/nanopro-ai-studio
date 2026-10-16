import unittest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAllFeatures(unittest.TestCase):
    def test_01_telegram_test_all_bots(self):
        res = client.post('/api/telegram/test_all_bots')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "success")
        self.assertIn("news", data.get("test_results", {}))
        self.assertIn("career", data.get("test_results", {}))
        self.assertIn("health", data.get("test_results", {}))
        self.assertIn("reports", data.get("test_results", {}))
        print("Test 1 Passed: All 4 Telegram Bots tested successfully.")

    def test_02_cyber_modules_catalog(self):
        res = client.get('/api/cyber/modules')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "success")
        self.assertGreaterEqual(data.get("total_modules", 0), 105)
        print(f"Test 2 Passed: {data.get('total_modules')} Cybersecurity modules loaded.")

    def test_03_cyber_run_audit(self):
        res = client.post('/api/cyber/run_audit', json={"module_id": "owasp_sqli_union"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "success")
        self.assertTrue(data.get("is_hardened"))
        self.assertIn("100% SECURE", data.get("audit_terminal_output", ""))
        print("Test 3 Passed: Defensive Security Audit simulated successfully.")

    def test_04_whatsapp_simulate_incoming(self):
        res = client.post('/api/whatsapp/simulate_incoming', json={
            "query": "आज किती डेटा लोड झाला?",
            "sender_phone": "+918433755448",
            "sender_name": "Mangesh Bagul"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "success")
        self.assertTrue("1,50,012" in data.get("reply", "") or "150,012" in data.get("reply", ""))
        print("Test 4 Passed: WhatsApp Two-Way AI simulation answered data load query.")

    def test_05_whatsapp_webhook_handshake(self):
        res = client.get('/api/whatsapp/webhook?hub.mode=subscribe&hub.challenge=test_chal_12345&hub.verify_token=nanopro_whatsapp_secret_2026')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, "test_chal_12345")
        print("Test 5 Passed: Meta WhatsApp Webhook Verification Handshake passed.")

    def test_06_discovery_run_all_schedules(self):
        res = client.post('/api/discovery/schedules/run_all')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "success")
        print(f"Test 6 Passed: Discovery schedules ran. Count: {data.get('total_schedules')}")

if __name__ == "__main__":
    unittest.main()
