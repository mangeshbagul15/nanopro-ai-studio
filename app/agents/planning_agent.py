"""
Mangesh Nano Pro AI Studio - Personal Daily Planning Agent
Handles:
1. Morning Operational Briefings (agenda, pending jobs, reminders, priorities)
2. Afternoon check-ins and deadline alerts
3. Evening progress summaries (completed vs remaining tasks, learning status)
4. Weekly comprehensive learning and productivity summaries
5. Proactive scheduling recommendations
"""

import time
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import db

class DailyPlanningAgent:
    def __init__(self):
        pass

    def generate_morning_briefing(self) -> Dict[str, Any]:
        """Prepares comprehensive morning plan and priority agenda."""
        now = time.time()
        date_str = time.strftime("%A, %d %B %Y")
        
        # 1. Fetch pending tasks
        tasks = db.list_tasks(limit=50)
        pending = [t for t in tasks if t.get("status") in ["pending", "QUEUED", "RUNNING"]]
        
        # 2. Fetch pending reminders
        reminders = db.list_reminders(status="pending")
        
        # 3. Fetch active tracked products
        products = db.list_amazon_products(status="active")
        
        # 4. Fetch recent job opportunities
        jobs = db.list_job_postings()
        
        # 5. Suggested Top 3 Priorities
        priorities = []
        if any("sql" in (t.get("prompt") or "").lower() for t in pending):
            priorities.append("Practice advanced SQL scenario drills (window functions & CTEs).")
        else:
            priorities.append("Complete scheduled SQL / Python technical practice.")
            
        if products:
            priorities.append(f"Monitor price fluctuations for {len(products)} tracked Amazon hardware/book items.")
        else:
            priorities.append("Review latest Data Engineering job openings in Mumbai/Navi Mumbai/Thane.")
            
        priorities.append("Review system health and verify automated database backup integrity.")

        # Build markdown briefing
        lines = [
            f"# 🌅 Good Morning, Mangesh! — Nano Pro Studio Briefing\n"
            f"**Date:** {date_str} | **System Status:** ⚡ Operational\n\n"
            f"### 🎯 Top 3 Recommended Priorities for Today:\n"
        ]
        for i, prio in enumerate(priorities[:3], 1):
            lines.append(f"{i}. {prio}")
            
        lines.append(f"\n### 📋 Active Tasks & Operations ({len(pending)}):")
        if pending:
            for t in pending[:5]:
                lines.append(f"• `{t['id']}` [{t.get('agent_id', 'agent').upper()}]: {t.get('prompt', '')[:60]}")
        else:
            lines.append("• *No pending execution backlog. Ready for new assignments.*")
            
        lines.append(f"\n### ⏰ Scheduled Reminders ({len(reminders)}):")
        if reminders:
            for r in reminders[:5]:
                lines.append(f"• **{r['title']}** (Scheduled: `{r['due_time']}`)")
        else:
            lines.append("• *No reminders scheduled for today.*")

        if jobs:
            lines.append(f"\n### 💼 Career Watch ({len(jobs)} openings discovered):")
            for j in jobs[:3]:
                lines.append(f"• **{j['title']}** at *{j['company']}* ({j['location']})")

        briefing_text = "\n".join(lines)
        log_event("Morning operational briefing prepared successfully.", component="PlanningAgent")
        
        return {
            "date": date_str,
            "briefing_markdown": briefing_text,
            "priorities": priorities,
            "pending_count": len(pending),
            "reminders_count": len(reminders),
            "timestamp": now
        }

    def generate_evening_summary(self) -> Dict[str, Any]:
        """Prepares end-of-day operational recap."""
        now = time.time()
        date_str = time.strftime("%A, %d %B %Y")
        
        tasks = db.list_tasks(limit=100)
        completed = [t for t in tasks if t.get("status") == "done" and (now - t.get("updated_at", now)) < 86400]
        failed = [t for t in tasks if t.get("status") in ["error", "FAILED"] and (now - t.get("updated_at", now)) < 86400]
        pending = [t for t in tasks if t.get("status") in ["pending", "QUEUED", "RUNNING"]]

        learnings = db.list_learning_sessions()
        recent_learnings = [l for l in learnings if (now - l.get("created_at", now)) < 86400]

        lines = [
            f"# 🌙 Evening Progress Report — Nano Pro Studio\n"
            f"**Date:** {date_str}\n\n"
            f"### 📊 Execution Statistics (Last 24 Hours):\n"
            f"• ✅ **Completed Tasks:** {len(completed)}\n"
            f"• ⏳ **Remaining Backlog:** {len(pending)}\n"
            f"• ⚠️ **Execution Errors:** {len(failed)}\n"
            f"• 🎓 **Learning Sessions Completed:** {len(recent_learnings)}\n"
        ]

        if recent_learnings:
            lines.append("\n### 🧠 Learning & Drills Reviewed:")
            for s in recent_learnings[:3]:
                lines.append(f"• **{s['subject'].upper()}** ({s['topic']}): Score {s['score']}/100")

        if failed:
            lines.append("\n### ⚠️ Attention Required (Failures):")
            for f in failed[:3]:
                lines.append(f"• `{f['id']}`: {f.get('error_message', 'Timeout or connection issue')}")

        lines.append("\n*Automated nightly database backup will run at 02:00 AM IST.*")
        summary_text = "\n".join(lines)
        log_event("Evening progress report generated.", component="PlanningAgent")

        return {
            "date": date_str,
            "summary_markdown": summary_text,
            "completed_count": len(completed),
            "pending_count": len(pending),
            "failed_count": len(failed),
            "timestamp": now
        }

daily_planning_agent = DailyPlanningAgent()
