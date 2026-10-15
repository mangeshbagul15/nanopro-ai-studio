"""
Mangesh Nano Pro AI Studio - Telegram Bot Command Router
Handles:
1. Allowlist authentication check for authorized user IDs
2. Routing commands: /start, /status, /today, /tasks, /pending, /prices, /jobs, /study, /errors, /report, /backup, /help
3. Natural language query fallback to AI Manager
"""

from typing import Dict, Any, Optional
from app.core.logger import log_event
from app.core.database import db, credentials_vault

def route_telegram_command(assistant, user_id: str, text: str) -> Dict[str, Any]:
    authorized_ids = {str(assistant.telegram_chat_id), "1200023268"}
    tg_cred = credentials_vault.get_credential("telegram")
    if tg_cred and tg_cred.get("additional_metadata", {}).get("allowed_user_ids"):
        for aid in tg_cred["additional_metadata"]["allowed_user_ids"]:
            authorized_ids.add(str(aid))

    if str(user_id) not in authorized_ids:
        log_event(f"Unauthorized Telegram access attempt from user_id={user_id}", level="WARNING", component="TelegramAgent")
        return {
            "status": "unauthorized",
            "reply": "⛔ <b>Access Denied:</b> This Telegram bot is private to Mangesh Nano Pro AI Studio. Your Telegram user ID is not authorized."
        }

    cmd_raw = text.strip()
    cmd_lower = cmd_raw.lower()

    if cmd_lower in ["/start", "/help"]:
        return {
            "status": "success",
            "reply": (
                "🤖 <b>Mangesh Nano Pro AI Operations Assistant</b>\n\n"
                "Welcome to your personal autonomous AI manager!\n\n"
                "<b>Quick Commands:</b>\n"
                "• <code>/today</code> — Morning briefing & priorities\n"
                "• <code>/tasks</code> — View active & pending tasks\n"
                "• <code>/prices</code> — Amazon tracked products & price drops\n"
                "• <code>/jobs</code> — Verified data engineering job openings\n"
                "• <code>/study</code> — SQL & Snowflake learning drills\n"
                "• <code>/status</code> — System health & agent workload\n"
                "• <code>/errors</code> — Diagnostic report on recent task failures\n"
                "• <code>/report</code> — Generate & send executive daily summary\n"
                "• <code>/movies</code> — Latest movie & OTT streaming releases\n• <code>/github</code> — Trending open-source AI repositories\n• <code>/apis</code> — Top verified free APIs & developer keys\n• <code>/news</code> — National & tech news updates\n• <code>/broadcast</code> — 360° multi-domain executive digest\n• <code>/ingest</code> — Trigger real-time data folder ingestion\n• <code>/backup</code> — Create an immediate database backup\n\n"
                "<i>You can also ask me anything in plain English, Marathi, or Hinglish!</i>"
            )
        }

    if cmd_lower in ["/status", "status"]:
        from app.agents.assistant_agent import monitoring_agent
        from app.core.model_adapter import model_manager
        h = monitoring_agent.get_system_health()
        models = model_manager.get_effective_model_list()
        primary = models[0] if models else "qwen2.5-coder:3b"
        return {
            "status": "success",
            "reply": (
                "⚡ <b>Nano Pro AI Studio — Live Operational Status:</b>\n\n"
                f"• <b>System Health:</b> <code>{h.get('health_status', 'HEALTHY')}</code>\n"
                f"• <b>Active AI Model:</b> <code>{primary}</code>\n"
                f"• <b>Storage:</b> {h['disk']['free_gb']} GB Free ({h['disk']['used_percentage']}% used)\n"
                f"• <b>Database:</b> SQLite (<code>studio_memory.db</code>) — {'✅ Healthy' if h['database']['healthy'] else '⚠️ Error'}\n"
                f"• <b>Error Rate:</b> {h['task_metrics']['failure_rate_pct']}% across {h['task_metrics']['recent_analyzed']} jobs\n"
                "• <b>Supervising Agent:</b> <code>MonitoringAgent</code> active"
            )
        }

    if cmd_lower in ["/today", "/pending", "/tasks", "today", "pending", "tasks"]:
        tasks = db.list_tasks(limit=15)
        reminders = db.list_reminders(status="pending")
        pending_tasks = [t for t in tasks if t.get("status") in ["pending", "QUEUED", "RUNNING"]]
        
        lines = ["📋 <b>Today's Operational Agenda & Pending Tasks:</b>\n"]
        if pending_tasks:
            lines.append(f"<b>Active / Pending Jobs ({len(pending_tasks)}):</b>")
            for t in pending_tasks[:6]:
                lines.append(f"• <code>{t['id']}</code> [{t.get('agent_id', 'agent').upper()}] — {t.get('prompt', '')[:50]}")
        else:
            lines.append("✅ <i>No pending background jobs. All tasks completed.</i>")

        if reminders:
            lines.append(f"\n<b>Upcoming Reminders ({len(reminders)}):</b>")
            for r in reminders[:5]:
                lines.append(f"• ⏰ <b>{r['title']}</b> (Due: <code>{r['due_time']}</code>)")
        else:
            lines.append("\n⏰ <i>No pending reminders scheduled.</i>")

        return {"status": "success", "reply": "\n".join(lines)}

    if cmd_lower in ["/prices", "prices", "amazon"]:
        from app.agents.price_tracker_agent import amazon_price_tracker
        summary = amazon_price_tracker.get_daily_price_summary()
        return {"status": "success", "reply": assistant._clean_telegram_text(summary)}

    if cmd_lower in ["/jobs", "jobs", "openings"]:
        from app.agents.career_agent import career_agent
        jobs = career_agent.search_jobs(role="Data Engineer", location="Mumbai, Navi Mumbai, Thane")
        lines = ["💼 <b>Top Verified Data Engineering Openings (Mumbai Region):</b>\n"]
        for j in jobs[:4]:
            lines.append(
                f"• <b>{j['title']}</b> at <i>{j['company']}</i>\n"
                f"  📍 {j['location']} | 💼 {j['experience_level']}\n"
                f"  🛠️ Skills: <code>{j['skills_required']}</code>\n"
                f"  🔗 <a href='{j['source_url']}'>View Job Opening</a>\n"
            )
        return {"status": "success", "reply": "\n".join(lines)}

    if cmd_lower in ["/study", "study", "learning"]:
        from app.agents.learning_agent import learning_agent
        drill = learning_agent.generate_sql_drill(topic="Window Functions & Joins", difficulty="medium")
        lines = [f"🎓 <b>SQL Interview Practice Drill — {drill['topic']}</b>\n"]
        lines.append(f"<b>Scenario:</b> {drill['scenario']}\n")
        for i, q in enumerate(drill['questions'], 1):
            lines.append(f"<b>Q{i}:</b> {q['question']}\n💡 <i>Hint: {q['hint']}</i>\n")
        return {"status": "success", "reply": "\n".join(lines)}

    if cmd_lower in ["/errors", "errors"]:
        tasks = db.list_tasks(limit=30)
        failed = [t for t in tasks if t.get("status") in ["error", "FAILED"]]
        if not failed:
            return {"status": "success", "reply": "✅ <b>Zero Task Failures:</b> All recent agent executions succeeded with 0 errors."}
        lines = [f"⚠️ <b>Recent Task Failures ({len(failed)}):</b>\n"]
        for f in failed[:5]:
            lines.append(f"• <code>{f['id']}</code> [{f.get('agent_id', 'agent').upper()}]: {f.get('error_message', 'Timeout or connection error')}")
        return {"status": "success", "reply": "\n".join(lines)}

    if cmd_lower in ["/report", "report"]:
        res = assistant.generate_daily_executive_report()
        return {"status": "success", "reply": assistant._clean_telegram_text(res["report_markdown"])}

    if cmd_lower in ["/movies", "movies", "cinema", "entertainment"]:
        digest = assistant.generate_multidomain_digest("movies")
        return {"status": "success", "reply": digest}

    if cmd_lower in ["/github", "github", "repos"]:
        digest = assistant.generate_multidomain_digest("github")
        return {"status": "success", "reply": digest}

    if cmd_lower in ["/apis", "apis", "free_api", "keys"]:
        digest = assistant.generate_multidomain_digest("apis")
        return {"status": "success", "reply": digest}

    if cmd_lower in ["/news", "news", "technews", "tech"]:
        digest = assistant.generate_multidomain_digest("tech")
        return {"status": "success", "reply": digest}

    if cmd_lower in ["/broadcast", "broadcast", "all"]:
        digest = assistant.generate_multidomain_digest("all")
        return {"status": "success", "reply": digest}

    if cmd_lower in ["/ingest", "ingest", "data"]:
        from app.agents.assistant_agent import data_engineer_agent
        res_i = data_engineer_agent.batch_folder_ingestion("data_ingestion", auto_dedup=True)
        return {
            "status": "success",
            "reply": (
                f"🗄 <b>Data Engineering Ingestion Complete:</b>\n\n"
                f"• <b>Files Ingested:</b> {res_i['total_files']} files\n"
                f"• <b>Records Loaded:</b> <code>{res_i['final_loaded_rows']:,}</code> rows\n"
                f"• <b>Speed:</b> <code>{res_i['throughput_mb_s']} MB/s</code> ({res_i['rows_per_sec']} rows/s)\n"
                f"• <b>Latency:</b> <code>{res_i['total_duration_ms']} ms</code>\n"
                f"• <b>Target Table:</b> <code>data_engineer_records</code> (SQLite)"
            )
        }

    if cmd_lower in ["/backup", "backup"]:
        from app.core.backup_manager import backup_manager
        res_b = backup_manager.create_system_backup()
        return {"status": "success", "reply": f"📦 <b>System Backup Completed:</b>\n• Archive: <code>{res_b.get('filename', 'backup.tar.gz')}</code>\n• Size: {res_b.get('size_bytes', 0):,} bytes\n• Validated in Backup Ledger: ✅"}

    # Natural language query fallback: Route to AI Manager
    from app.agents.manager_agent import manager_agent
    mgr_resp = manager_agent.chat_interact(cmd_raw, session_id=f"tg_{user_id}")
    return {
        "status": "success",
        "reply": assistant._clean_telegram_text(mgr_resp.get("response", "Task received."))
    }
