import unittest
from app.agents.assistant_agent import personal_assistant_agent
from app.core.telegram_router import classify_telegram_message, send_telegram_routed_message

class TestTelegramMultiBotRouting(unittest.TestCase):
    def test_smart_classification(self):
        self.assertEqual(
            classify_telegram_message("Senior Data Engineer Interview Drill: Explain Snowflake Micro-partitions."),
            "career"
        )
        self.assertEqual(
            classify_telegram_message("4-Hour Job Radar: 18 new Data Engineer openings in Pune and Mumbai."),
            "career"
        )
        self.assertEqual(
            classify_telegram_message("Database health check: Snowflake, Oracle XE, and Postgres connections are nominal."),
            "health"
        )
        self.assertEqual(
            classify_telegram_message("Critical System Alert: Server CPU at 95%, Fail2ban active."),
            "health"
        )
        self.assertEqual(
            classify_telegram_message("Daily Executive Financial Report: 142,500 transactions verified in BankDB ledger."),
            "reports"
        )
        self.assertEqual(
            classify_telegram_message("Daily Tech & AI Trends: OpenAI reasoning benchmarks and Groq LPU speed updates."),
            "news"
        )

    def test_live_delivery_isolation(self):
        tests = [
            ("Career", "💼 [Career Bot Drill Test] Explain Medallion Architecture and Delta Lake.", "@mangesh_career_study_bot"),
            ("Health", "🏥 [Health Bot Vitals Test] All database connections verified NOMINAL.", "@mangesh_health_monitor_bot"),
            ("Reports", "📊 [Reports Bot Briefing Test] Financial reconciliation complete for BankDB.", "@mangesh_reports_bot"),
            ("News", "📰 [News Bot Trends Test] Latest open-weights AI model release summary.", "@mangesh_technews_bot")
        ]

        for domain, msg, expected_bot in tests:
            res = personal_assistant_agent.send_telegram_message(msg)
            print(f"Domain [{domain}]: Sent to {res.get('bot_used')} | Expected: {expected_bot} | Status: {res.get('status')}")
            self.assertEqual(res.get("bot_used"), expected_bot)
            self.assertEqual(res.get("status"), "success")

if __name__ == "__main__":
    unittest.main()
