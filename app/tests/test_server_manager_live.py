import json
import unittest
from unittest.mock import patch

from app.core.server_manager_hub import ServerManagerHub


class ServerManagerLiveTelemetryTests(unittest.TestCase):
    def test_health_probe_reads_latency_and_runtime_health(self):
        response = unittest.mock.MagicMock()
        response.__enter__.return_value = response
        response.status = 200
        response.read.return_value = json.dumps({
            "health_status": "WARNING",
            "memory": {"used_ram_mb": 240, "total_ram_mb": 1024},
            "cpu": {"load_1m": 0.75},
        }).encode("utf-8")

        with patch("app.core.server_manager_hub.urllib.request.urlopen", return_value=response):
            probe = ServerManagerHub._read_health_endpoint("https://nano.example")

        self.assertEqual(probe["status"], "DEGRADED")
        self.assertEqual(probe["http_status"], 200)
        self.assertGreaterEqual(probe["ping_ms"], 0)
        self.assertEqual(probe["health"]["memory"]["used_ram_mb"], 240)

    def test_health_metrics_do_not_convert_system_load_into_cpu_percent(self):
        metrics = ServerManagerHub._health_metrics({
            "cpu": {"load_1m": 2.4, "utilization_estimate_pct": 48},
            "memory": {"used_ram_mb": 250.5, "total_ram_mb": 1024},
        })

        self.assertEqual(metrics["load"], "1m avg 2.4")
        self.assertEqual(metrics["memory_usage"], "250 / 1024 MB")

    def test_nodes_without_deploy_urls_are_not_reported_as_online(self):
        hub = ServerManagerHub.__new__(ServerManagerHub)
        hub._server_telemetry_cache = None
        hub._server_telemetry_cached_at = 0.0
        health = {
            "health_status": "HEALTHY",
            "cpu": {"load_1m": 0.2},
            "memory": {"used_ram_mb": 180, "total_ram_mb": 1024},
        }

        def fake_probe(url):
            if "fly.dev" in url:
                return {"status": "HEALTHY", "ping_ms": 31.2, "http_status": 200, "health": health}
            return {"status": "OFFLINE", "ping_ms": 4000, "message": "probe timed out"}

        with patch.dict("os.environ", {"NANOPRO_NODE_ID": "node_cloud_render"}, clear=True):
            with patch("app.agents.assistant_agent.monitoring_agent.get_system_health", return_value=health):
                with patch.object(hub, "_read_health_endpoint", side_effect=fake_probe):
                    nodes = hub._get_app_server_telemetry(force_refresh=True)

        self.assertEqual(len(nodes), 10)
        by_id = {node["id"]: node for node in nodes}
        self.assertTrue(by_id["node_cloud_render"]["is_current_host"])
        self.assertEqual(by_id["node_cloud_render"]["status"], "HEALTHY")
        self.assertEqual(by_id["node_cloud_flyio"]["ping_ms"], 31.2)
        self.assertEqual(by_id["node_cloud_northflank"]["status"], "NOT_CONFIGURED")
        self.assertIsNone(by_id["node_cloud_northflank"]["ping_ms"])
        self.assertEqual(by_id["node_cloud_flyio"]["memory_usage"], "180 / 1024 MB")


if __name__ == "__main__":
    unittest.main()
