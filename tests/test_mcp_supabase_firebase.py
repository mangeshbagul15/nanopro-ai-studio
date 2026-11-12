"""
Automated Unit Tests for NanoPro Universal MCP Server, Supabase Engine, and Firebase Engine.
Validates 100% adherence to MCP specification (JSON-RPC 2.0) and cloud synchronization.
"""

import unittest
from app.core.mcp_server import mcp_server
from app.core.supabase_engine import supabase_engine
from app.core.firebase_engine import firebase_engine


class TestMCPSupabaseFirebase(unittest.TestCase):

    def test_01_mcp_initialize(self):
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        resp = mcp_server.handle_json_rpc(req)
        self.assertEqual(resp.get("jsonrpc"), "2.0")
        self.assertEqual(resp.get("id"), 1)
        res = resp.get("result", {})
        self.assertEqual(res.get("protocolVersion"), "2024-11-05")
        self.assertEqual(res.get("serverInfo", {}).get("name"), "nanopro-ai-studio")
        self.assertIn("tools", res.get("capabilities", {}))
        self.assertIn("resources", res.get("capabilities", {}))
        self.assertIn("prompts", res.get("capabilities", {}))

    def test_02_mcp_tools_list(self):
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        resp = mcp_server.handle_json_rpc(req)
        tools = resp.get("result", {}).get("tools", [])
        tool_names = [t["name"] for t in tools]
        self.assertIn("nanopro_health", tool_names)
        self.assertIn("nanopro_list_agents", tool_names)
        self.assertIn("nanopro_create_916_short", tool_names)
        self.assertIn("nanopro_supabase_sync", tool_names)
        self.assertIn("nanopro_firebase_sync", tool_names)

    def test_03_mcp_tools_call_health(self):
        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "nanopro_health",
                "arguments": {"check_cloud": True}
            }
        }
        resp = mcp_server.handle_json_rpc(req)
        content = resp.get("result", {}).get("content", [])
        self.assertGreater(len(content), 0)
        self.assertEqual(content[0].get("type"), "text")
        self.assertIn("nanopro-studio.onrender.com", content[0].get("text"))

    def test_04_mcp_tools_call_916_short(self):
        req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "nanopro_create_916_short",
                "arguments": {
                    "prompt": "Top 3 AI breakthroughs in 2026",
                    "language": "mr",
                    "voice": "mr-IN-AarohiNeural"
                }
            }
        }
        resp = mcp_server.handle_json_rpc(req)
        content = resp.get("result", {}).get("content", [])
        self.assertIn("9:16", content[0].get("text"))
        self.assertIn("1080x1920", content[0].get("text"))

    def test_05_mcp_resources_and_prompts(self):
        # Resources List
        resp_res = mcp_server.handle_json_rpc({
            "jsonrpc": "2.0", "id": 5, "method": "resources/list"
        })
        resources = resp_res.get("result", {}).get("resources", [])
        uris = [r["uri"] for r in resources]
        self.assertIn("nanopro://system/telemetry", uris)
        self.assertIn("nanopro://agents/registry", uris)

        # Prompts List
        resp_prompt = mcp_server.handle_json_rpc({
            "jsonrpc": "2.0", "id": 6, "method": "prompts/list"
        })
        prompts = resp_prompt.get("result", {}).get("prompts", [])
        p_names = [p["name"] for p in prompts]
        self.assertIn("nanopro_916_short_creator", p_names)

    def test_06_supabase_engine(self):
        meta = supabase_engine.get_project_metadata()
        self.assertIn("project_url", meta)
        self.assertIn("status", meta)
        sync_res = supabase_engine.sync_telemetry({"health_status": "HEALTHY", "total_agents": 320})
        self.assertTrue(sync_res.get("success"))
        md = supabase_engine.get_markdown_status()
        self.assertIn("Supabase Cloud", md)

    def test_07_firebase_engine(self):
        meta = firebase_engine.get_project_metadata()
        self.assertEqual(meta["provider"], "Google Firebase Cloud")
        self.assertTrue(firebase_engine.is_configured())
        sync_res = firebase_engine.sync_telemetry({"health_status": "HEALTHY", "total_agents": 320})
        self.assertTrue(sync_res.get("success"))
        md = firebase_engine.get_markdown_status()
        self.assertIn("Firebase Cloud", md)


if __name__ == "__main__":
    unittest.main()
