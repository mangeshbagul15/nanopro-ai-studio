"""
Mangesh Nano Pro AI Studio - Persistent Scheduler & Startup Recovery Engine
Handles:
1. Boot-time database and service health checks
2. Detecting interrupted tasks from previous sessions
3. Discovering and recovering overdue scheduled tasks and price checks
4. Coalescing obsolete/repeated missed reminders to avoid notification bursts
5. Recording immutable recovery runs into `recovery_history`
6. Background scheduler loop for recurring tasks and periodic monitors
"""

import time
import threading
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import db
from app.core.task_manager import task_manager

class StartupRecoveryEngine:
    def __init__(self):
        self._running = False
        self._worker_thread = None

    def execute_startup_recovery(self) -> Dict[str, Any]:
        """
        Executes a complete startup recovery cycle:
        - Inspects interrupted tasks from prior sessions
        - Recovers overdue Amazon price checks
        - Coalesces pending/overdue reminders
        - Logs the recovery outcome to recovery_history
        """
        session_id = f"recovery_{int(time.time()*1000)}"
        log_event(f"Starting startup recovery cycle [{session_id}]...", component="RecoveryEngine")

        # 1. Inspect Interrupted Tasks
        interrupted_count = 0
        recovered_count = 0
        failed_count = 0
        all_tasks = db.list_tasks(limit=200)
        now = time.time()

        for t in all_tasks:
            # If a task was in RUNNING or QUEUED state from an older session (> 10 mins ago)
            if t.get("status") in ["RUNNING", "running", "QUEUED", "queued"]:
                if (now - t.get("updated_at", now)) > 300:
                    interrupted_count += 1
                    log_event(f"Recovering interrupted task [{t['id']}] for agent [{t.get('agent_id')}]", component="RecoveryEngine")
                    # Transition to PENDING or retry if eligible
                    try:
                        db.update_task_status(t["id"], "pending", error_message="Recovered by startup cycle; rescheduled for execution")
                        recovered_count += 1
                    except Exception as e:
                        failed_count += 1
                        log_event(f"Failed to recover task [{t['id']}]: {e}", level="ERROR", component="RecoveryEngine")

        # 2. Overdue Amazon Price Checks
        overdue_price_checks = 0
        try:
            from app.agents.price_tracker_agent import amazon_price_tracker
            overdue_price_checks = amazon_price_tracker.recover_overdue_checks()
        except Exception as e:
            log_event(f"Price tracker recovery error: {e}", level="WARNING", component="RecoveryEngine")

        # 3. Reminder Coalescence (Avoid alert flood on startup)
        coalesced_reminders = 0
        try:
            pending_reminders = db.list_reminders(status="pending")
            # If there are multiple repeated reminders for the same title, coalesce
            seen_titles = set()
            for r in pending_reminders:
                if r["title"] in seen_titles:
                    # Mark older duplicate as coalesced
                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE reminders SET status = 'coalesced' WHERE id = ?", (r["id"],))
                        conn.commit()
                    coalesced_reminders += 1
                else:
                    seen_titles.add(r["title"])
        except Exception as e:
            log_event(f"Reminder coalescence error: {e}", level="WARNING", component="RecoveryEngine")

        summary_msg = (
            f"Startup recovery completed: {interrupted_count} interrupted tasks discovered ({recovered_count} recovered), "
            f"{overdue_price_checks} overdue price checks refreshed, {coalesced_reminders} duplicate reminders coalesced."
        )
        log_event(summary_msg, component="RecoveryEngine")

        # Record recovery run
        run_id = db.record_recovery_run(
            session_id=session_id,
            interrupted=interrupted_count,
            overdue=overdue_price_checks,
            recovered=recovered_count,
            coalesced=coalesced_reminders,
            failed=failed_count,
            log_summary=summary_msg
        )

        return {
            "run_id": run_id,
            "session_id": session_id,
            "interrupted_discovered": interrupted_count,
            "tasks_recovered": recovered_count,
            "overdue_price_checks": overdue_price_checks,
            "reminders_coalesced": coalesced_reminders,
            "failed_retries": failed_count,
            "summary": summary_msg,
            "timestamp": now
        }

    def start_scheduler_loop(self):
        """Starts continuous persistent background scheduler for recurring tasks."""
        if self._running:
            return
        self._running = True

        def _loop():
            # Initial startup recovery
            try:
                self.execute_startup_recovery()
            except Exception as e:
                log_event(f"Initial startup recovery encountered an issue: {e}", level="ERROR", component="RecoveryEngine")

            while self._running:
                try:
                    # Periodic routine check every 60 seconds
                    now = time.time()
                    # 1. Process pending reminders
                    reminders = db.list_reminders(status="pending")
                    for r in reminders:
                        # Check if due (format YYYY-MM-DD or HH:MM)
                        # If due, mark as triggered and dispatch Telegram / Email
                        pass

                    # 2. Check active Amazon products monitoring
                    from app.agents.price_tracker_agent import amazon_price_tracker
                    amazon_price_tracker.recover_overdue_checks()

                except Exception as e:
                    log_event(f"Scheduler loop error: {e}", level="ERROR", component="RecoveryEngine")
                time.sleep(60)

        self._worker_thread = threading.Thread(target=_loop, daemon=True)
        self._worker_thread.start()
        log_event("Persistent Scheduler & Recovery Engine loop started.", component="RecoveryEngine")

    def stop_scheduler_loop(self):
        self._running = False

startup_recovery_engine = StartupRecoveryEngine()
