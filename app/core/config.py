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


def _sanitize_no_proxy() -> None:
    """httpx rejects bracketed IPv6 entries in NO_PROXY ("Invalid port: ':1]'").

    Windows sets NO_PROXY to "...127.0.0.0/8,[::1],::1" on this machine, which
    breaks every SDK call (Groq, Gemini, Anthropic) before the request is sent.
    Drop the bracketed form and keep the bare "::1" token.
    """
    raw = os.environ.get("NO_PROXY") or os.environ.get("no_proxy") or ""
    if "[" not in raw:
        return
    kept = [part.strip() for part in raw.split(",") if part.strip() and not part.strip().startswith("[")]
    if "::1" not in kept:
        kept.append("::1")
    for var in ("NO_PROXY", "no_proxy"):
        if var in os.environ:
            os.environ[var] = ",".join(kept)


_sanitize_no_proxy()

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

# Legacy single-bot token still deployed on Render; used as last-resort fallback
_LEGACY_TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# Bot 1: Tech News & AI Trends (@mangesh_technews_bot)
TELEGRAM_NEWS_BOT_TOKEN = os.environ.get("TELEGRAM_NEWS_BOT_TOKEN") or _LEGACY_TELEGRAM_BOT_TOKEN
TELEGRAM_NEWS_BOT_USERNAME = "@mangesh_technews_bot"

# Bot 2: System Health & Infrastructure Sentinel (@mangesh_health_monitor_bot)
TELEGRAM_HEALTH_BOT_TOKEN = os.environ.get("TELEGRAM_HEALTH_BOT_TOKEN", "")
TELEGRAM_HEALTH_BOT_USERNAME = "@mangesh_health_monitor_bot"

# Bot 3: Career Radar & Senior Interview Practice (@mangesh_career_study_bot)
TELEGRAM_CAREER_BOT_TOKEN = os.environ.get("TELEGRAM_CAREER_BOT_TOKEN", "")
TELEGRAM_CAREER_BOT_USERNAME = "@mangesh_career_study_bot"

# Bot 4: Executive Briefings & Financial Ledger (@mangesh_reports_bot)
TELEGRAM_REPORTS_BOT_TOKEN = os.environ.get("TELEGRAM_REPORTS_BOT_TOKEN", "")
TELEGRAM_REPORTS_BOT_USERNAME = "@mangesh_reports_bot"

# Bot 5: Android Open-Source APK Dispatcher (@mangesh_apk_bot)
TELEGRAM_APK_BOT_TOKEN = os.environ.get("TELEGRAM_APK_BOT_TOKEN", "")
TELEGRAM_APK_BOT_USERNAME = "@mangesh_apk_bot"

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
default_host = "0.0.0.0"
default_port = int(os.environ.get("PORT", 7860 if os.environ.get("SPACE_ID") else 8000))

SERVER_HOST = os.environ.get("STUDIO_HOST", os.environ.get("HOST", default_host))
SERVER_PORT = int(os.environ.get("STUDIO_PORT", default_port))

# OpenRouter Unified Multi-Model Gateway (432+ Models)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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").strip()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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").strip()
DEEPINFRA_API_KEY = os.environ.get("DEEPINFRA_API_KEY", "sk-di-GZlkK2nWUqmV5nxhsdCbGLWxce5EkSAJ").strip()
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-2d5bc8b3419244e6bc17f23b36dd6d66").strip()
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "mstrl_OZwEdSDxbLIE8xd9Sg0i3wDLH2l2wOnQ_1OV8Q4").strip()
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY", "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").strip()
FAL_AI_API_KEY = os.environ.get("FAL_AI_API_KEY", "fal_sk_d1a4032b2a4d4c94ad7cbef5395d439f:ad79f427f9e0d633316032a561ab9999").strip()
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "r8_VSW8CuVp9dP35gBcLCIFIJcNxfzVpuY3jNpQI").strip()
AIMLAPI_KEY = os.environ.get("AIMLAPI_KEY", "d6b5f7f58a5d797e02fd021c231026ea").strip()
AIMLAPI_BACKUP_KEY = os.environ.get("AIMLAPI_BACKUP_KEY", "666612ebe3ae25e4db14bd8da4b654fd").strip()
