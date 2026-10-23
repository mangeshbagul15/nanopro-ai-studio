"""
Mangesh Nano Pro AI Studio - Central Configuration Module
Handles project directories, platform detection, environment variables, and model configs.
"""

import os
import sys
import platform
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base project directory
SYSTEM_OS = platform.system()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Subdirectories
APP_DIR = BASE_DIR / "app"
CONFIG_DIR = APP_DIR / "config"
DATABASE_DIR = APP_DIR / "database"
LOGS_DIR = APP_DIR / "logs"
REPORTS_DIR = APP_DIR / "reports"
BACKUPS_DIR = APP_DIR / "backups"
MEMORY_DIR = APP_DIR / "memory"

VIDEO_MAKER_DIR = APP_DIR / "video_maker"
VIDEO_SQL_DIR = VIDEO_MAKER_DIR / "sql"
VIDEO_PY_DIR = VIDEO_MAKER_DIR / "python"
VIDEO_AUDIO_DIR = VIDEO_MAKER_DIR / "audio"
VIDEO_OUTPUT_DIR = VIDEO_MAKER_DIR / "output"

IMAGE_MAKER_DIR = APP_DIR / "image_maker"
IMAGE_OUTPUT_DIR = IMAGE_MAKER_DIR / "output"

CODING_DIR = APP_DIR / "coding_agent"
CODING_BACKUPS_DIR = CODING_DIR / "backups"
CODING_PATCHES_DIR = CODING_DIR / "patches"

# Ensure runtime directories exist
for d in [
    CONFIG_DIR, DATABASE_DIR, LOGS_DIR, REPORTS_DIR, BACKUPS_DIR, MEMORY_DIR,
    VIDEO_SQL_DIR, VIDEO_PY_DIR, VIDEO_AUDIO_DIR, VIDEO_OUTPUT_DIR,
    IMAGE_OUTPUT_DIR, CODING_BACKUPS_DIR, CODING_PATCHES_DIR
]:
    d.mkdir(parents=True, exist_ok=True)

# Database path configuration
if "STUDIO_DB_PATH" in os.environ:
    SQLITE_DB_PATH = Path(os.environ["STUDIO_DB_PATH"])
else:
    try:
        test_db = DATABASE_DIR / ".probe.db"
        import sqlite3
        conn = sqlite3.connect(str(test_db))
        conn.execute("CREATE TABLE IF NOT EXISTS _p (id INT)")
        conn.close()
        test_db.unlink(missing_ok=True)
        SQLITE_DB_PATH = DATABASE_DIR / "studio_memory.db"
    except Exception:
        SQLITE_DB_PATH = Path("/tmp/studio_memory.db") if SYSTEM_OS != "Windows" else DATABASE_DIR / "studio_memory.db"

# Default Model & Ollama configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_KEEP_ALIVE = "30m"
DEFAULT_MODELS_TO_TRY = [
    "qwen2.5-coder:3b",
    "qwen2.5-coder:7b",
    "gemma3:4b",
    "phi4-mini:latest",
    "llama3.2:3b",
]
DEFAULT_METADATA_MODELS = [
    "qwen2.5-coder:3b",
    "phi4-mini:latest",
    "gemma3:4b",
    "llama3.2:3b",
    "qwen2.5-coder:7b",
]

# Telegram Multi-Bot Configurations (Specialized Channels)
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1200023268")

# Bot 1: News & AI Trends (Default Primary)
TELEGRAM_NEWS_BOT_TOKEN = os.environ.get("TELEGRAM_NEWS_BOT_TOKEN", "")
TELEGRAM_NEWS_BOT_USERNAME = "@mangesh_technews_bot"

# Bot 2: Health & System Monitoring
TELEGRAM_HEALTH_BOT_TOKEN = os.environ.get("TELEGRAM_HEALTH_BOT_TOKEN", "")
TELEGRAM_HEALTH_BOT_USERNAME = "@mangesh_health_monitor_bot"

# Bot 3: Career, Jobs & Interview Study
TELEGRAM_CAREER_BOT_TOKEN = os.environ.get("TELEGRAM_CAREER_BOT_TOKEN", "")
TELEGRAM_CAREER_BOT_USERNAME = "@mangesh_career_study_bot"

# Bot 4: Executive & Financial Reports
TELEGRAM_REPORTS_BOT_TOKEN = os.environ.get("TELEGRAM_REPORTS_BOT_TOKEN", "")
TELEGRAM_REPORTS_BOT_USERNAME = "@mangesh_reports_bot"

# Bot 5: APK Dispatcher
TELEGRAM_APK_BOT_TOKEN = os.environ.get("TELEGRAM_APK_BOT_TOKEN", "")
TELEGRAM_APK_BOT_USERNAME = "@mangesh_apk_bot"

# Global Default Token
TELEGRAM_BOT_TOKEN = TELEGRAM_NEWS_BOT_TOKEN
TELEGRAM_BOT_USERNAME = TELEGRAM_NEWS_BOT_USERNAME
REMINDERS_CHECK_INTERVAL = int(os.environ.get("REMINDERS_CHECK_INTERVAL", 60))

# Audio fallback policy
AUDIO_FALLBACK_LOOP = "loop"
AUDIO_FALLBACK_PAD = "silence"
AUDIO_FALLBACK_STRETCH = "stretch"

# Port and server host
# In container / Hugging Face Spaces environments, bind to 0.0.0.0 and listen on $PORT (default 7860 on HF)
is_cloud_or_container = bool(os.environ.get("SPACE_ID") or os.environ.get("PORT"))
default_host = "0.0.0.0" if is_cloud_or_container else "127.0.0.1"
default_port = int(os.environ.get("PORT", 7860 if os.environ.get("SPACE_ID") else 8000))

SERVER_HOST = os.environ.get("STUDIO_HOST", os.environ.get("HOST", default_host))
SERVER_PORT = int(os.environ.get("STUDIO_PORT", default_port))
