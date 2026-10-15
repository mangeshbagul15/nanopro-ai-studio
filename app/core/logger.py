"""
Mangesh Nano Pro AI Studio - Central Logging & Event Emitter
Thread-safe logging with SQLite persistence and WebSocket/live event integration.
"""

import sys
import time
import logging
import threading
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.core.config import LOGS_DIR

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

# File logger
log_file = LOGS_DIR / f"studio_{time.strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[
        logging.FileHandler(str(log_file), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("StudioLogger")

_live_logs: List[str] = []
_logs_lock = threading.Lock()
_thread_context = threading.local()

def set_current_job_id(job_id: str):
    """Binds the current execution thread to a specific job ID for scoped logging."""
    _thread_context.job_id = job_id

def get_current_job_id() -> Optional[str]:
    return getattr(_thread_context, "job_id", None)

def log_event(message: str, level: str = "INFO", component: str = "General", job_id: Optional[str] = None):
    """Central log entry point that routes to stdout, file, memory buffer, and active job."""
    timestamp = time.strftime("%H:%M:%S")
    formatted = f"[{timestamp}] [{component}] {message}"
    
    if level == "ERROR":
        logger.error(f"[{component}] {message}")
    elif level == "WARNING":
        logger.warning(f"[{component}] {message}")
    else:
        logger.info(f"[{component}] {message}")

    with _logs_lock:
        _live_logs.append(formatted)
        if len(_live_logs) > 2000:
            _live_logs.pop(0)

    # Scoped job tracking hook
    active_job = job_id or get_current_job_id()
    if active_job:
        from app.core.task_manager import task_manager
        task_manager.append_job_log(active_job, formatted)

def get_recent_logs(limit: int = 200) -> List[str]:
    with _logs_lock:
        return list(_live_logs[-limit:])
