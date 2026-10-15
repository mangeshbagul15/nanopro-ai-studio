# Unit 01: Config, Launch Scripts & Root Entry Points

## Purpose and Responsibility
Responsible for application initialization, dependency specification, environment configuration, process orchestration, route exposure, and browser autolaunching. Serves as the primary operational entry point (`main.py`, `run_studio.bat`, `run_studio.ps1`).

## Files Read
- `requirements.txt`: Python package requirements manifest [Tier 1]
- `.env.example`: Configuration and credentials environment template [Tier 1]
- `README.md`: High-level system overview, manual, and architectural notes [Tier 1]
- `run_studio.bat`: Windows batch startup script with port-clearing and venv autodetection [Tier 1]
- `main.py`: Central FastAPI server, life-cycle manager, route registry (169 routes), browser launcher [Tier 1]
- `audit_routes.py`: Standalone route and frontend fetch consistency auditor [Tier 2]

## Key Classes / Functions
- `startup_event()` (`main.py:421`): [Verified] Initializes default connection managers, starts background automation scheduler (`automation_scheduler.start()`), and boots background news agent scheduler (`news_agent.start()`).
- `serve_dashboard()` (`main.py:434`): [Verified] Root route `GET /` returning the compiled HTML/JS/CSS single-page application dashboard via `get_dashboard_html()`.
- `auto_launch_chrome(url)` (`main.py:2045`): [Verified] Background worker that inspects OS registry/executables for Chrome and opens the application URL on port 8000.
- `run_server()` (`main.py:2103`): [Verified] Launches browser thread and invokes `uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)`.
- `main.py` dynamic SMTP self-healing stub (`main.py:40-170`): [Verified] Inline fallback that writes and dynamically imports `app/core/smtp_client.py` if missing during module import.

## Dependencies IN & OUT
- **Dependencies IN**: Executed by Windows shell scripts (`run_studio.bat`, `run_studio.ps1`), user terminal, or tests.
- **Dependencies OUT**:
  - Internal: Imports almost all modules: `app.core.config`, `app.core.logger`, `app.core.task_manager`, `app.core.database`, `app.core.backup_manager`, `app.core.model_adapter`, `app.core.audio_processor`, `app.core.connection_manager`, `app.core.automation_scheduler`, `app.agents.*`, `app.video_maker.unified_video_maker`, `app.ui.dashboard`.
  - External: `fastapi`, `uvicorn`, `pydantic`, `dotenv`, `smtplib`, `subprocess`, `requests`.

## Data Touched
- Environment variables via `python-dotenv` (`.env`).
- SQLite DB (`data/nano_pro_studio.db` / `app/database/nano_pro_studio.db`).
- Subprocess execution (`google-chrome`, `taskkill`, `netstat`).

## Config and Env Variables Used
- `STUDIO_HOST` / `SERVER_HOST`
- `STUDIO_PORT` / `SERVER_PORT`
- `GMAIL_APP_PASSWORD`
- `SMTP_PASSWORD`
- `SNOWFLAKE_PASSWORD`
- `ORACLE_PASSWORD`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`
- `OLLAMA_HOST`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `FFMPEG_PATH`
- `FFPROBE_PATH`

## Error Handling, Retries, Logging, Idempotency
- Global startup wraps connection and scheduler boot in try-except with warning logs.
- Port 8000 pre-clearing in `run_studio.bat` ensures idempotency when restarting without hanging processes.
- Dynamic SMTP loader self-repairs missing file on disk.

## Observed Issues
- **U-UNIT01-01** | Category: Security | Severity: High | Location: `.env.example:27-28`
  - Evidence: Live Telegram bot token `8693843358:AAHPJVgj4vEv-RtZgKYghyM7j7dQvkDN_Gs` and chat ID `1200023268` committed in cleartext inside `.env.example`.
  - Fix: Remove production token from `.env.example`, replace with placeholder `<YOUR_TELEGRAM_BOT_TOKEN>`.
- **U-UNIT01-02** | Category: Code Quality / Duplication | Severity: Medium | Location: `main.py:2115-2139`
  - Evidence: Duplicate synthesized routes `@app.get("/api/custom/please_modify_code_in_main_py")` appended twice by CodeArchitect at lines 2115 and 2129.
  - Fix: Deduplicate route registry or ensure dynamic code modifications in `main.py` prune prior synthesized handlers.
- **U-UNIT01-03** | Category: Architecture | Severity: Medium | Location: `main.py:43-170`
  - Evidence: `main.py` contains a 130-line hardcoded string literal defining an entire fallback SMTP module that writes to disk at runtime if `app.core.smtp_client` is not found.
  - Fix: Standardize repository file integrity via packaging or tests instead of runtime self-modifying source code.
- **U-UNIT01-04** | Category: Documentation | Severity: Low | Location: `README.md:6,48`
  - Evidence: README references legacy directory `C:\Mangesh\AI video\AI_manager` and launcher script `start_studio.bat`, whereas actual directory is `Mangesh_Nano_Pro_AI_Studio` and launcher is `run_studio.bat`.
  - Fix: Update README paths and filenames to reflect actual project tree.

## Open Questions
- None.
