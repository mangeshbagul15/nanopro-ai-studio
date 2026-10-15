"""
Unit Tests for Cloud Trends & Lakehouse Architecture Engine (Snowflake vs AWS October 2026)
"""

import unittest
from app.agents.cloud_trends_agent import cloud_trends_agent, SNOWFLAKE_TRENDS_2026, AWS_TRENDS_2026, COMPARISON_MATRIX
from app.agents.manager_agent import manager_agent
from app.agents.voice_assistant import voice_assistant

class TestCloudTrends(unittest.TestCase):
    def test_snowflake_trends_count_and_keys(self):
        self.assertEqual(len(SNOWFLAKE_TRENDS_2026), 10)
        for item in SNOWFLAKE_TRENDS_2026:
            self.assertIn("id", item)
            self.assertIn("rank", item)
            self.assertIn("name", item)
            self.assertIn("name_mr", item)
            self.assertIn("status", item)
            self.assertIn("category", item)
            self.assertIn("de_use_case", item)
            self.assertIn("de_use_case_mr", item)
            self.assertIn("code_snippet", item)
            self.assertTrue(len(item["code_snippet"]) > 20)

    def test_aws_trends_count_and_keys(self):
        self.assertEqual(len(AWS_TRENDS_2026), 10)
        for item in AWS_TRENDS_2026:
            self.assertIn("id", item)
            self.assertIn("rank", item)
            self.assertIn("name", item)
            self.assertIn("name_mr", item)
            self.assertIn("status", item)
            self.assertIn("category", item)
            self.assertIn("de_use_case", item)
            self.assertIn("de_use_case_mr", item)
            self.assertIn("code_snippet", item)
            self.assertTrue(len(item["code_snippet"]) > 20)

    def test_comparison_matrix(self):
        self.assertEqual(len(COMPARISON_MATRIX), 6)
        comp = cloud_trends_agent.get_comparison()
        self.assertIn("matrix", comp)
        self.assertIn("benchmark_scores", comp)
        self.assertIn("strategic_summary_en", comp)
        self.assertIn("strategic_summary_mr", comp)
        self.assertEqual(len(comp["benchmark_scores"]["pillars"]), 6)

    def test_code_generation(self):
        # Snowflake Cortex Agent DDL
        res_sf = cloud_trends_agent.generate_code_artifact("snowflake", "sf_01")
        self.assertEqual(res_sf["trend_id"], "sf_01")
        self.assertIn("CORTEX AGENT", res_sf["code"])

        # Snowflake Dynamic Table DDL
        res_dt = cloud_trends_agent.generate_code_artifact("snowflake", "sf_04")
        self.assertEqual(res_dt["trend_id"], "sf_04")
        self.assertIn("DYNAMIC TABLE", res_dt["code"])

        # AWS S3 Tables Iceberg V3
        res_aws = cloud_trends_agent.generate_code_artifact("aws", "aws_02")
        self.assertEqual(res_aws["trend_id"], "aws_02")
        self.assertIn("s3tables", res_aws["code"])

        # AWS Bedrock AgentCore
        res_bedrock = cloud_trends_agent.generate_code_artifact("aws", "aws_01")
        self.assertEqual(res_bedrock["trend_id"], "aws_01")
        self.assertIn("bedrock-agent", res_bedrock["code"])

    def test_career_roadmap(self):
        roadmap_en = cloud_trends_agent.get_career_roadmap("en")
        self.assertIn("core_skills", roadmap_en)
        self.assertIn("action_plan", roadmap_en)
        self.assertTrue(len(roadmap_en["core_skills"]) >= 5)

        roadmap_mr = cloud_trends_agent.get_career_roadmap("mr")
        self.assertIn("करिअर रोडमॅप", roadmap_mr.get("headline", ""))
        self.assertTrue(len(roadmap_mr["core_skills"]) >= 5)

    def test_manager_agent_cloud_trends_dialogue(self):
        prompt = "Top 10 upcoming / latest trends: Snowflake vs AWS for data engineers"
        resp = manager_agent.chat_interact(prompt, session_id="test_cloud_trends")
        self.assertEqual(resp["status"], "COMPLETED")
        self.assertEqual(resp["agent_id"], "cloud_trends_agent")
        self.assertIn("table_data", resp)
        self.assertIn("chart_data", resp)
        self.assertIn("kpi_cards", resp)
        self.assertIn("execution_card", resp)
        self.assertEqual(len(resp["table_data"]["rows"]), 10)
        self.assertIn("Cortex AI Agents", resp["response"])
        self.assertIn("Amazon Bedrock AgentCore", resp["response"])

    def test_voice_assistant_cloud_trends_marathi(self):
        prompt = "नॅनोप्रो, स्नोफ्लेक आणि एडब्ल्यूएस मधील टॉप 10 ट्रेंड्स सांग"
        resp = voice_assistant.process_voice_command(prompt, language="mr-IN")
        self.assertEqual(resp["action_taken"], "cloud_trends_voice")
        self.assertIn("स्नोफ्लेक", resp["response_text"])
        self.assertIn("एडब्ल्यूएस", resp["response_text"])
        self.assertIn("data", resp)

if __name__ == "__main__":
    unittest.main()
