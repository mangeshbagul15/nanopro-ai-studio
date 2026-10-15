# Observed Issues Register

| ID | Unit | Category | Severity | Location | Description | Fix |
|---|---|---|---|---|---|---|
| U-UNIT01-01 | UNIT 01 | Security | High | .env.example:27-28 | Live Telegram token in template file | Replace with placeholder |
| U-UNIT01-02 | UNIT 01 | Logic/Quality | Medium | main.py:2115-2139 | Duplicate dynamic route handlers appended to main.py | Deduplicate route injection logic |
| U-UNIT01-03 | UNIT 01 | Architecture | Medium | main.py:43-170 | Self-modifying SMTP client fallback string writes code to disk at runtime | Ship module statically |
| U-UNIT01-04 | UNIT 01 | Documentation | Low | README.md:6,48 | Obsolete path C:\Mangesh\AI video\AI_manager and script start_studio.bat | Update README paths |
| U-UNIT02-01 | UNIT 02 | Security | Critical | app/core/connection_manager.py:108-152 | Hardcoded passwords (Snowflake, Oracle, Gmail SMTP, AWS Secret Key, AWS Bearer Token) in Python source | Purge literals and require .env/Vault exclusively |
| U-UNIT02-02 | UNIT 02 | Reliability | Medium | app/core/database.py:26 | SQLite connections lack explicit WAL pragma and busy_timeout in concurrent environment | Add PRAGMA journal_mode=WAL and busy_timeout=5000 |
| U-UNIT02-03 | UNIT 02 | Code Quality | Low | app/core/database.py:1893 | Missing socket import checked via globals() fallback | Explicitly import socket in database.py |
| U-UNIT03-01 | UNIT 03 | Security | Critical | app/core/smtp_client.py:73 | Hardcoded Gmail App Password literal fallback | Purge password literal, return None if missing |
| U-UNIT03-02 | UNIT 03 | Logic | Medium | app/core/scheduler_recovery.py:130-135 | Empty reminder trigger loop (contains only pass statement) | Implement dispatch logic for due reminders |
| U-UNIT03-03 | UNIT 03 | Config/Portability | Low | app/core/audio_processor.py:18-19 | Ignores FFMPEG_PATH env var, queries PATH directly | Read FFMPEG_PATH from os.environ first |
| U-UNIT04-01 | UNIT 04 | Security | Medium | app/agents/telegram_router.py:14 | Hardcoded authorized Telegram user ID string 1200023268 | Use config and vault exclusively |
| U-UNIT04-02 | UNIT 04 | Architecture | Medium | app/agents/extended_intents.py:8-70 | Deferred inline imports to bypass circular dependency cycles | Refactor agents to central dependency registry |
| U-UNIT05-01 | UNIT 05 | Safety/Security | High | app/agents/coding_agent.py:109-150 | Unsandboxed source code self-modification via natural language prompt | Enforce mandatory approval workflow and isolate edits to sandbox |
| U-UNIT05-02 | UNIT 05 | Reliability | Medium | app/agents/price_tracker_agent.py:52 | Brittle Amazon HTML regex scraping subject to anti-bot CAPTCHA | Implement Playwright fallback or structured API retrieval |
| U-UNIT06-01 | UNIT 06 | Code Quality | Medium | app/video_maker/sql/sql_core.py:57 | Redundant independent FastAPI apps and duplicate logging implementations | Deduplicate and consume app.core singletons |
| U-UNIT06-02 | UNIT 06 | Concurrency | Medium | app/video_maker/unified_video_maker.py:108 | Synchronous asyncio.run() called in multi-threaded contexts | Decouple video generation into separate worker queue |
