# Unit 03: Core Operations, Scheduling, AI Adapter & Services

## Purpose and Responsibility
Orchestrates operational subsystems: model selection and fallback management (`model_adapter.py`), asynchronous job scheduling and recurrence calculations (`automation_scheduler.py`), continuous supervisor lifecycle for 45 agents (`autonomous_operations_manager.py`), compressed database backup/restore (`backup_manager.py`), crash recovery and reminder coalescing (`scheduler_recovery.py`), verified SMTP/Gmail communication (`smtp_client.py`), fine-grained in-flight task tracking (`task_manager.py`), and FFmpeg audio-video muxing (`audio_processor.py`).

## Files Read
- `app/core/model_adapter.py`: Ollama + Remote LLM adapters, circuit breaker, capability routing [Tier 1]
- `app/core/automation_scheduler.py`: Windows Task Scheduler replacement supporting Python, SQL, Batch [Tier 1]
- `app/core/autonomous_operations_manager.py`: Continuous operation supervisor (Start/Pause/Resume/Emergency Stop) [Tier 1]
- `app/core/backup_manager.py`: Tarball `.tar.gz` archiving of DB, memory, configs with ledger recording [Tier 1]
- `app/core/scheduler_recovery.py`: Startup recovery cycle, orphaned task detection, reminder coalescing [Tier 1]
- `app/core/smtp_client.py`: Gmail SMTP client with TLS/SSL, attachment handling, delivery logging [Tier 1]
- `app/core/task_manager.py`: In-memory thread-safe task registry with 13 core agent fleets and SQLite sync [Tier 1]
- `app/core/audio_processor.py`: FFmpeg duration inspector, stream looping, volume filter, muxing [Tier 1]

## Key Classes / Functions
- `ModelManager.chat()` (`model_adapter.py:180`): [Verified] Tries primary model with scaled timeouts, handles graceful fallbacks across Ollama and remote APIs.
- `AutomationScheduler.calculate_next_run()` (`automation_scheduler.py:92`): [Verified] Calculates upcoming timestamps for minutes, hourly, daily, weekly, monthly, and cron recurrence.
- `AutonomousOperationsManager.emergency_stop()` (`autonomous_operations_manager.py:117`): [Verified] Immediately sets operations state to `EMERGENCY_STOPPED`, terminates continuous loop, and isolates active agents.
- `BackupManager.create_system_backup()` (`backup_manager.py:21`): [Verified] Creates compressed `.tar.gz` archive of database and configs, storing checksum and byte size in `backups_ledger`.
- `StartupRecoveryEngine.execute_startup_recovery()` (`scheduler_recovery.py:24`): [Verified] Discovers interrupted tasks (>300s old), reschedules them, and deduplicates pending notifications.
- `SMTPClient.send_email()` (`smtp_client.py:245`): [Verified] Validates email address format via regex, binds to secure TLS socket, sends MIME body with attachments, logs communication to `communication_logs`.
- `TaskManager.create_job()` (`task_manager.py:60`): [Verified] Generates UUID job ID, initializes agent state, and saves task to SQLite.
- `AudioProcessor.mux_video_audio()` (`audio_processor.py:108`): [Verified] Muxes background music and animation video using `-shortest` to ensure video duration is never exceeded.

## Dependencies IN & OUT
- **Dependencies IN**: `main.py`, `app.agents.manager_agent`, `app.agents.assistant_agent`, UI dashboard routes.
- **Dependencies OUT**:
  - Internal: `app.core.config`, `app.core.logger`, `app.core.database`, `app.core.connection_manager`.
  - External: `urllib.request`, `smtplib`, `ssl`, `subprocess` (`ffmpeg`, `ffprobe`), `tarfile`, `threading`.

## Data Touched
- SQLite tables: `tasks`, `reminders`, `backups_ledger`, `scheduled_automation_tasks`, `recovery_history`, `communication_logs`.
- Filesystem: `app/backups/*.tar.gz`, `app/video_maker/output/*.mp4`, `app/video_maker/audio/*.mp3`.

## Config and Env Variables Used
- `OLLAMA_HOST`, `OLLAMA_KEEP_ALIVE`, `AI_STUDIO_API_KEY`, `AI_STUDIO_BASE_URL`
- `GMAIL_APP_PASSWORD`, `SMTP_PASSWORD`
- `AUDIO_FALLBACK_LOOP`, `AUDIO_FALLBACK_PAD`
- `FFMPEG_PATH`, `FFPROBE_PATH`

## Error Handling, Retries, Logging, Idempotency
- Model adapter scales timeout dynamically (45s for 3b/4b models, 90s for 7b/8b models) and catches `urllib.error.URLError`.
- Backup restore enforces explicit `confirmation=True` parameter before replacing database file.
- Recovery engine marks stale tasks (>5 mins old in running state) as recovered to prevent zombie tasks.

## Observed Issues
- **U-UNIT03-01** | Category: Security | Severity: Critical | Location: `app/core/smtp_client.py:73`
  - Evidence: Hardcoded Gmail App Password literal `agunjgvexwcjudbx` returned as default fallback at line 73.
  - Fix: Remove password fallback string literal from `get_secret_password()`, raise descriptive configuration error or return `None` if unconfigured.
- **U-UNIT03-02** | Category: Logic Error / Incomplete Implementation | Severity: Medium | Location: `app/core/scheduler_recovery.py:130-135`
  - Evidence: In `start_scheduler_loop()`, the periodic reminder loop iterates through pending reminders and contains only a `pass` statement without dispatching notifications.
  - Fix: Implement reminder trigger comparison logic against `r["due_time"]` and trigger dispatch via `telegram_router` / `smtp_client`.
- **U-UNIT03-03** | Category: External Tool Dependency | Severity: Low | Location: `app/core/audio_processor.py:18-19`
  - Evidence: Relies on `shutil.which("ffmpeg")` without fallback to explicit `FFMPEG_PATH` environment variable defined in `.env.example`.
  - Fix: Prioritize `os.environ.get("FFMPEG_PATH")` before falling back to system PATH.

## Open Questions
- None.
