# Unit 05: Specialized AI Agents & Discovery Engine

## Purpose and Responsibility
Implements vertical domain agents and continuous research spiders:
- `discovery_engine.py`: Live search for GitHub AI repositories and free developer APIs with offline local backups.
- `discovery_scheduler.py`: 10-category autonomous background inspector (App status, System health, Features, Models, Database, Telegram, Improvements, Ideas, Issues, Security) with hourly Telegram notification dispatch.
- `career_agent.py`: Data Engineering BFSI job hunter, resume matcher, 4-year experience interview preparation, and recruiter email generator.
- `coding_agent.py`: AST parsing, code modification by prompt, backup creation (`.bak`), patch tracking.
- `cloud_trends_agent.py`: October 2026 Snowflake vs AWS architectural benchmarks, DDL generators (Cortex Agents, S3 Tables, Dynamic Tables).
- `book_agent.py`: Multi-format document ingestion (PDF, DOCX, TXT), chapter parsing, semantic chunking, and AI learning assistant.
- `price_tracker_agent.py`: Amazon ASIN validation, price scraping, price-drop detection, and multi-channel alerting.
- `learning_agent.py`: SQL and Snowflake interview practice sessions with score tracking.
- `planning_agent.py`: Morning operational agenda and evening productivity recap generator.
- `news_agent.py`: Dual-language news monitor for ABP Majha (Marathi) and Aaj Tak (Hindi).
- `entertainment_agent.py`: Lifestyle and multimedia discovery engine.
- `research_agent.py`: Grounded historical landmarks and live multilingual research engine.
- `image_agent.py`: Pillow and FFmpeg thumbnail generator.

## Files Read
- `app/agents/discovery_engine.py`: GitHub & Free API live scraper and search [Tier 1]
- `app/agents/discovery_scheduler.py`: 10-category system health inspector & scheduler [Tier 1]
- `app/agents/career_agent.py`: Career tracker and interview simulator [Tier 1]
- `app/agents/coding_agent.py`: Code architect, AST syntax analyzer, file modifier [Tier 1]
- `app/agents/cloud_trends_agent.py`: Snowflake vs AWS technical trends engine [Tier 1]
- `app/agents/book_agent.py`: Reader and study assistant [Tier 1]
- `app/agents/price_tracker_agent.py`: Amazon product monitor [Tier 1]
- `app/agents/learning_agent.py`: Technical scenario practice generator [Tier 1]
- `app/agents/planning_agent.py`: Morning and evening executive planners [Tier 1]
- `app/agents/news_agent.py`: ABP Majha & Aaj Tak news engine [Tier 1]
- `app/agents/entertainment_agent.py`: Cinema and streaming curator [Tier 1]
- `app/agents/research_agent.py`: Universal research and historical fact grounder [Tier 1]
- `app/agents/image_agent.py`: Image creation and thumbnail generator [Tier 1]

## Key Classes / Functions
- `DiscoveryEngine.search_github()` (`discovery_engine.py:25`): [Verified] Scrapes GitHub API or queries local database fallback, tags multi-language capability (Marathi, Hindi, English).
- `SystemDiscoveryScheduler.run_discovery_cycle()` (`discovery_scheduler.py:108`): [Verified] Conducts 10-point audit across app, OS, DB, Telegram, and LLMs.
- `CodingAgent.safe_modify_file()` (`coding_agent.py:67`): [Verified] Creates pre-edit file backup, analyzes AST syntax, and commits changes safely.
- `BookReaderAgent.ingest_book()` (`book_agent.py:97`): [Verified] Parses chapters and extracts chunks from PDF, DOCX, and TXT files.
- `AmazonPriceTrackerAgent.check_price()` (`price_tracker_agent.py:86`): [Verified] Extracts ASIN, calculates percentage price drops, and triggers Telegram and Email alerts.
- `CareerAgent.search_jobs()` (`career_agent.py:63`): [Verified] Matches profile against authentic corporate job listings in Mumbai/Navi Mumbai/Thane.

## Dependencies IN & OUT
- **Dependencies IN**: `main.py`, `app.agents.manager_agent`, UI dashboard views.
- **Dependencies OUT**:
  - Internal: `app.core.database`, `app.core.logger`, `app.core.model_adapter`, `app.core.config`, `app.core.storage_inspector`, `app.core.smtp_client`.
  - External: `urllib.request`, `ast`, `shutil`, `re`, `PIL` (Pillow).

## Data Touched
- SQLite tables: `free_apis`, `github_projects`, `research_library`, `discovery_schedules`, `scheduled_discovery_cycles`, `notification_history`, `amazon_products`, `amazon_prices`, `uploaded_books`, `book_chunks`, `learning_sessions`, `news_articles`, `entertainment_items`.
- Filesystem: `app/coding_agent/backups/*.bak`, `app/image_maker/output/*.png`, `data_ingestion/books/`.

## Config and Env Variables Used
- `OLLAMA_HOST`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `GMAIL_APP_PASSWORD`

## Error Handling, Retries, Logging, Idempotency
- GitHub search falls back gracefully to local SQLite store when GitHub rate limits or network issues occur.
- Coding agent verifies `ast.parse` syntax validity before replacing file contents on disk.
- News agent caches RSS feeds for 5 minutes (`300s`) to avoid rate limiting publisher endpoints.

## Observed Issues
- **U-UNIT05-01** | Category: Code Injection / Safety | Severity: High | Location: `app/agents/coding_agent.py:109-150`
  - Evidence: `modify_code_by_prompt()` applies automated text modifications to live source files (including `main.py`) based on prompt matching without sandbox isolation.
  - Fix: Restrict self-modification targets to a dedicated sandbox or require mandatory approval through the `approvals` table.
- **U-UNIT05-02** | Category: Reliability | Severity: Medium | Location: `app/agents/price_tracker_agent.py:52`
  - Evidence: `_fetch_product_price()` relies on HTML regex scraping of Amazon product pages, which is vulnerable to bot verification blocks (CAPTCHA/HTTP 503).
  - Fix: Incorporate header rotation, user-agent randomization, and headless browser fallback via Playwright.

## Open Questions
- None.
