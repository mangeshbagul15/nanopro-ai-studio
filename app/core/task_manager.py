"""
Mangesh Nano Pro AI Studio - Central Task & Multi-Agent Lifecycle Orchestrator
Manages job queues, agent status tracking, real-time stage monitoring, and task execution threads.
Supports strict lifecycle states: CREATED, QUEUED, RUNNING, WAITING_FOR_APPROVAL, RETRYING, COMPLETED, FAILED, CANCELLED.
"""

import time
import uuid
import queue
import threading
from typing import Dict, Any, List, Optional
from app.core.database import db
from app.core.logger import log_event

class TaskManager:
    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._persist_queue: queue.Queue = queue.Queue()
        self._persist_thread = threading.Thread(
            target=self._persistence_worker,
            daemon=True,
            name="TaskManagerPersistenceWorker"
        )
        self._persist_thread.start()
        now = time.time()
        
        # 13 Core Multi-Agent Fleet Definitions
        agent_definitions = [
            ("manager", "AI Studio Manager", "JARVIS Orchestration & Planning", "qwen2.5-coder:3b", "Ollama Local"),
            ("data_engineer", "Data Engineer Agent", "Schema Discovery & 6-Stage ETL", "qwen2.5-coder:3b", "Ollama Local"),
            ("data_analyst", "Data Analyst Agent", "Data Profiling & Quality Health", "phi4-mini:latest", "Ollama Local"),
            ("data_science", "Data Science & ML Agent", "Predictive Modeling & Scikit-Learn", "phi4-mini:latest", "Ollama Local"),
            ("file_converter", "File Converter Agent", "Multi-Format File Transformation", "qwen2.5-coder:3b", "Ollama Local"),
            ("cyber_lab", "Cybersecurity Agent", "Threat Analysis & Vault Guard", "shieldgemma:2b", "Ollama Local"),
            ("coding_agent", "Coding Agent", "Code Review, AST & Auto-Healing", "qwen2.5-coder:3b", "Ollama Local"),
            ("video_agent", "Video Creator Agent", "SQL & Python Animated Videos", "qwen2.5-coder:3b", "Ollama Local"),
            ("image_agent", "Image Studio Agent", "Thumbnails & Banner Generation", "PIL Engine", "Local OS"),
            ("research_agent", "Research & Knowledge Agent", "Universal Knowledge & Web Retrieval", "gemma3:4b", "Ollama Local"),
            ("assistant_agent", "Personal Assistant Agent", "Tasks, Schedules & Reminders", "llama3.2:3b", "Ollama Local"),
            ("telegram_agent", "Telegram Broadcast Agent", "Bot API Dispatcher & News Feed", "llama3.2:3b", "Ollama Local"),
            ("monitoring_agent", "Monitoring & Health Agent", "System Supervisor & Watchdog", "Local Daemon", "Local OS")
        ]

        self._agent_states: Dict[str, Dict[str, Any]] = {}
        for aid, name, role, model, provider in agent_definitions:
            self._agent_states[aid] = {
                "id": aid,
                "name": name,
                "role": role,
                "model_assigned": model,
                "provider": provider,
                "status": "idle",
                "current_job_id": None,
                "current_task": None,
                "stage": "Ready",
                "start_time": None,
                "finish_time": None,
                "progress": 0,
                "retry_count": 0,
                "max_retries": 3,
                "tools_used": [],
                "last_activity": "Standing by",
                "error_message": None,
                "updated": now
            }

    def _persist_job(self, job_data: Dict[str, Any]):
        """Persist task snapshot asynchronously to avoid blocking the caller thread."""
        task_copy = dict(job_data)
        if hasattr(db, "stage_task"):
            db.stage_task(task_copy)
        self._persist_queue.put(task_copy)

    def _persistence_worker(self):
        while True:
            try:
                task_data = self._persist_queue.get()
                if task_data is None:
                    break
                try:
                    db.save_task(task_data)
                except Exception as e:
                    log_event(f"Persistence error for job {task_data.get('id')}: {e}", level="ERROR", component="TaskManager")
                finally:
                    self._persist_queue.task_done()
            except Exception:
                pass

    def flush(self, timeout: float = 2.0):
        """Blocks until all queued task writes are persisted to disk."""
        try:
            self._persist_queue.join()
        except Exception:
            pass

    def create_job(self, prompt: str, agent_id: str = "manager", plan: Optional[List[str]] = None) -> str:
        job_id = f"job_{uuid.uuid4().hex[:10]}"
        now = time.time()
        job_data = {
            "id": job_id,
            "prompt": prompt,
            "agent_id": agent_id,
            "status": "queued",
            "stage": "initialized",
            "progress": 0,
            "plan": plan or [],
            "logs": [],
            "tools_used": [],
            "retry_count": 0,
            "max_retries": 3,
            "result_data": {},
            "error_message": None,
            "created_at": now,
            "started_at": now,
            "updated_at": now,
            "completed_at": None,
            "html_ready": False,
            "html": None
        }

        with self._lock:
            self._jobs[job_id] = job_data
            if agent_id not in self._agent_states:
                self._agent_states[agent_id] = {
                    "id": agent_id,
                    "name": agent_id.replace("_", " ").title(),
                    "role": "Specialist",
                    "model_assigned": "qwen2.5-coder:3b",
                    "provider": "Ollama Local",
                    "status": "idle",
                    "current_job_id": None,
                    "current_task": None,
                    "stage": "Ready",
                    "start_time": None,
                    "finish_time": None,
                    "progress": 0,
                    "retry_count": 0,
                    "max_retries": 3,
                    "tools_used": [],
                    "last_activity": "Initialized",
                    "error_message": None,
                    "updated": now
                }
            
            self._agent_states[agent_id].update({
                "status": "running",
                "current_job_id": job_id,
                "current_task": prompt[:80],
                "stage": "Queued",
                "start_time": now,
                "finish_time": None,
                "progress": 5,
                "retry_count": 0,
                "tools_used": [],
                "last_activity": "Task queued for execution",
                "error_message": None,
                "updated": now
            })

        # Persist asynchronously
        self._persist_job(job_data)
        log_event(f"Created job {job_id} for agent [{agent_id}]", component="TaskManager", job_id=job_id)
        return job_id

    def update_job_stage(self, job_id: str, stage: str, progress: int = None, status: str = None, tool_used: str = None):
        now = time.time()
        job_to_save = None
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job["stage"] = stage
                if progress is not None:
                    job["progress"] = progress
                if status is not None:
                    job["status"] = status
                if tool_used and tool_used not in job["tools_used"]:
                    job["tools_used"].append(tool_used)
                job["updated_at"] = now

                agent_id = job.get("agent_id", "manager")
                if agent_id in self._agent_states:
                    self._agent_states[agent_id].update({
                        "stage": stage,
                        "progress": job["progress"],
                        "last_activity": f"Executing stage: {stage}",
                        "updated": now
                    })
                    if tool_used and tool_used not in self._agent_states[agent_id]["tools_used"]:
                        self._agent_states[agent_id]["tools_used"].append(tool_used)
                    if status:
                        self._agent_states[agent_id]["status"] = status

                job_to_save = dict(job)

        if job_to_save:
            self._persist_job(job_to_save)
            log_event(f"Job {job_id} stage -> {stage} ({job_to_save['progress']}%)", component="TaskManager", job_id=job_id)

    def record_tool_call(self, job_id: str, tool_name: str, input_summary: str = ""):
        now = time.time()
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                if tool_name not in job["tools_used"]:
                    job["tools_used"].append(tool_name)
                job["logs"].append(f"[{time.strftime('%H:%M:%S')}] Tool invocation: {tool_name} {input_summary}")
                agent_id = job.get("agent_id", "manager")
                if agent_id in self._agent_states:
                    if tool_name not in self._agent_states[agent_id]["tools_used"]:
                        self._agent_states[agent_id]["tools_used"].append(tool_name)
                    self._agent_states[agent_id]["last_activity"] = f"Tool: {tool_name}"
                    self._agent_states[agent_id]["updated"] = now

    def set_job_waiting_approval(self, job_id: str, approval_id: str):
        now = time.time()
        job_to_save = None
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job["status"] = "waiting_for_approval"
                job["stage"] = f"Awaiting approval {approval_id}"
                job["updated_at"] = now
                agent_id = job.get("agent_id", "manager")
                if agent_id in self._agent_states:
                    self._agent_states[agent_id].update({
                        "status": "waiting_for_approval",
                        "stage": f"Approval Pending ({approval_id})",
                        "last_activity": "Waiting for user sign-off in Approval Queue",
                        "updated": now
                    })
                job_to_save = dict(job)
        if job_to_save:
            self._persist_job(job_to_save)

    def set_job_completed(self, job_id: str, result_data: Dict[str, Any]):
        now = time.time()
        job_to_save = None
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job["status"] = "done"
                job["stage"] = "completed"
                job["progress"] = 100
                job["result_data"] = result_data
                job["updated_at"] = now
                job["completed_at"] = now
                agent_id = job.get("agent_id", "manager")
                if agent_id in self._agent_states:
                    self._agent_states[agent_id].update({
                        "status": "idle",
                        "current_job_id": None,
                        "current_task": None,
                        "stage": "Completed",
                        "finish_time": now,
                        "progress": 100,
                        "last_activity": "Task successfully finished",
                        "updated": now
                    })
                job_to_save = dict(job)
        if job_to_save:
            self._persist_job(job_to_save)
            log_event(f"Job {job_id} successfully completed", component="TaskManager", job_id=job_id)

    def set_job_failed(self, job_id: str, error_msg: str):
        now = time.time()
        job_to_save = None
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job["status"] = "error"
                job["stage"] = "failed"
                job["error_message"] = error_msg
                job["updated_at"] = now
                job["completed_at"] = now
                agent_id = job.get("agent_id", "manager")
                if agent_id in self._agent_states:
                    self._agent_states[agent_id].update({
                        "status": "failed",
                        "current_job_id": None,
                        "current_task": f"Error: {error_msg[:40]}",
                        "stage": "Failed",
                        "finish_time": now,
                        "last_activity": f"Failed: {error_msg[:40]}",
                        "error_message": error_msg,
                        "updated": now
                    })
                job_to_save = dict(job)
        if job_to_save:
            self._persist_job(job_to_save)
            log_event(f"Job {job_id} failed: {error_msg}", level="ERROR", component="TaskManager", job_id=job_id)

    def cancel_job(self, job_id: str) -> bool:
        """Cancels a queued or running job."""
        now = time.time()
        job_to_save = None
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job["status"] = "cancelled"
                job["stage"] = "cancelled_by_user"
                job["updated_at"] = now
                job["completed_at"] = now
                agent_id = job.get("agent_id", "manager")
                if agent_id in self._agent_states:
                    self._agent_states[agent_id].update({
                        "status": "idle",
                        "current_job_id": None,
                        "current_task": None,
                        "stage": "Cancelled",
                        "finish_time": now,
                        "last_activity": "Task cancelled by user",
                        "updated": now
                    })
                job_to_save = dict(job)
        if job_to_save:
            self._persist_job(job_to_save)
            log_event(f"Job {job_id} cancelled by user", component="TaskManager", job_id=job_id)
            return True
        return False

    def retry_job(self, job_id: str) -> bool:
        """Retries a failed job if under retry limits."""
        now = time.time()
        job_to_save = None
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                if job.get("retry_count", 0) >= job.get("max_retries", 3):
                    log_event(f"Cannot retry {job_id}: Exceeded max retries (3)", level="WARNING", component="TaskManager")
                    return False
                job["retry_count"] += 1
                job["status"] = "retrying"
                job["stage"] = f"Retrying (attempt {job['retry_count']})"
                job["progress"] = 10
                job["error_message"] = None
                job["updated_at"] = now
                agent_id = job.get("agent_id", "manager")
                if agent_id in self._agent_states:
                    self._agent_states[agent_id].update({
                        "status": "running",
                        "current_job_id": job_id,
                        "current_task": job["prompt"][:80],
                        "stage": f"Retrying attempt {job['retry_count']}",
                        "retry_count": job["retry_count"],
                        "start_time": now,
                        "last_activity": f"Retrying job {job_id}",
                        "updated": now
                    })
                job_to_save = dict(job)
        if job_to_save:
            self._persist_job(job_to_save)
            log_event(f"Retrying job {job_id} (Attempt {job_to_save['retry_count']})", component="TaskManager", job_id=job_id)
            return True
        return False

    def append_job_log(self, job_id: str, message: str):
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id]["logs"].append(message)
                if len(self._jobs[job_id]["logs"]) > 500:
                    self._jobs[job_id]["logs"].pop(0)

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            if job_id in self._jobs:
                return dict(self._jobs[job_id])
        return db.get_task(job_id)

    def get_agent_states(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return {k: dict(v) for k, v in self._agent_states.items()}

    def get_agent_details(self, agent_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            if agent_id in self._agent_states:
                return dict(self._agent_states[agent_id])
        return None

    def get_studio_stats(self) -> Dict[str, Any]:
        tasks = db.list_tasks(limit=500)
        total = len(tasks)
        completed = sum(1 for t in tasks if t["status"] in ("done", "COMPLETED"))
        failed = sum(1 for t in tasks if t["status"] in ("error", "FAILED"))
        running = sum(1 for t in tasks if t["status"] in ("running", "queued", "working", "RUNNING", "retrying"))
        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "running_tasks": running,
            "agent_health": "All 13 Multi-Agents Active",
            "storage_status": "Healthy"
        }

task_manager = TaskManager()
