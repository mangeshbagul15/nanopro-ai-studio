# Stage 0: Inventory and Plan

## 1. Project Size & Statistics
- **Total files (excluding .git/venv/etc.)**: 371
- **File breakdown by extension**:
  - `.xlsx`: 111 (Data/reports)
  - `.csv`: 104 (Data/reports)
  - `.py`: 58 (Python source code, ~40,000 lines)
  - `.png`: 50 (Rendered assets/diagrams)
  - `.gz`: 21 (Database backups)
  - `.md`: 9 (Markdown reports/documentation)
  - `.db`: 5 (SQLite database files)
  - `.txt`: 3 (requirements.txt, etc.)
  - `.sql`: 2 (SQL schemas/migration scripts)
  - `.log`: 2 (Log files)
  - `.pdf`: 2 (Generated resume/report artifacts)
  - `.bat` / `.ps1`: 2 (Launch scripts)
  - `.env` / `.env.example`: 2 (Config templates)
- **Total lines of code/text**: ~46,994 lines across 76 text/code files.

## 2. File Classification by Tier

### Tier 1 (Read Fully - Core Logic, Entry Points, Data Access, Architecture) - 51 files
- **Configuration & Root Entry Points**: `requirements.txt`, `.env.example`, `.env`, `README.md`, `main.py`, `run_studio.bat`, `run_studio.ps1`
- **Core Engine (`app/core/`)**:
  - `app/core/config.py`
  - `app/core/database.py`
  - `app/core/connection_manager.py`
  - `app/core/model_adapter.py`
  - `app/core/automation_scheduler.py`
  - `app/core/autonomous_operations_manager.py`
  - `app/core/backup_manager.py`
  - `app/core/scheduler_recovery.py`
  - `app/core/smtp_client.py`
  - `app/core/task_manager.py`
  - `app/core/logger.py`
  - `app/core/audio_processor.py`
  - `app/core/storage_inspector.py`
- **AI Agents (`app/agents/`)**:
  - `app/agents/agent_registry.py`
  - `app/agents/manager_agent.py`
  - `app/agents/assistant_agent.py`
  - `app/agents/discovery_engine.py`
  - `app/agents/discovery_scheduler.py`
  - `app/agents/extended_intents.py`
  - `app/agents/career_agent.py`
  - `app/agents/coding_agent.py`
  - `app/agents/cloud_trends_agent.py`
  - `app/agents/book_agent.py`
  - `app/agents/news_agent.py`
  - `app/agents/learning_agent.py`
  - `app/agents/price_tracker_agent.py`
  - `app/agents/research_agent.py`
  - `app/agents/image_agent.py`
  - `app/agents/entertainment_agent.py`
  - `app/agents/telegram_router.py`
  - `app/agents/voice_assistant.py`
- **UI & Web Dashboard (`app/ui/`)**:
  - `app/ui/dashboard.py` (FastAPI / HTML rendering engine)
  - `app/ui/dashboard_views.py`
  - `app/ui/dashboard_css.py`
  - `app/ui/dashboard_js.py`
- **Video Maker Engines (`app/video_maker/`)**:
  - `app/video_maker/unified_video_maker.py`
  - `app/video_maker/python/python_core.py`
  - `app/video_maker/sql/sql_core.py`
- **Data Ingestion & Route Auditing**:
  - `data_ingestion/validate_pipeline_records.py`
  - `audit_routes.py`

### Tier 2 (Read Key Parts / Structure - Tests, Guides, Scripts) - 21 files
- `app/tests/test_suite.py`
- `app/tests/test_all_46_views.py`
- `app/tests/test_e2e_views_client.py`
- `app/tests/test_career_hub.py`
- `app/tests/test_cloud_trends.py`
- `app/tests/test_code_architect.py`
- `app/tests/test_command_center_features.py`
- `app/tests/test_ui_restructure.py`
- `app/tests/test_ai_manager_and_office_upgrade.py`
- `CAREER_AND_JOB_SEARCH_DATA_ENGINEERING_GUIDE.md`
- `DATABASE_CONNECTION_MANAGER_AND_VAULT_REPORT.md`
- `NANO_PRO_ADVANCED_COMMAND_CENTER_REDESIGN_REPORT.md`
- `NANO_PRO_AI_OPERATING_CENTER_GUIDE.md`
- `NANO_PRO_UI_UX_RESTRUCTURE_ARCHITECTURAL_REPORT.md`
- `PIPELINE_ETL_AND_AGENT_GUIDE.md`
- `SMTP_SECURITY_AND_FIX_REPORT.md`
- `SNOWFLAKE_VS_AWS_OCTOBER_2026_TRENDS_REPORT.md`

### Tier 3 (Sample Only - Datasets, Reports, CSV/XLSX) - 219 files
- CSV files in `data_ingestion/`, `app/reports/`
- Excel files in `app/reports/`

### Tier 4 (Skip - Binaries, Databases, Backups, Images) - 80 files
- SQLite `.db` files (`app/database/*.db`)
- Backup archives (`app/backups/*.gz`)
- Images (`app/image_maker/*.png`)
- Logs (`app/logs/*.log`)
- PDFs (`app/resumes/*.pdf`, `app/reports/*.pdf`)

## 3. Work Units Partitioning

We organize the 51 Tier 1 + 21 Tier 2 files into 8 logical Work Units:

1. **UNIT 01: Config, Launch Scripts & Root Entry Points**
   - Files: `requirements.txt`, `.env.example`, `README.md`, `main.py`, `run_studio.bat`, `run_studio.ps1`, `audit_routes.py`
2. **UNIT 02: Core Infrastructure & Storage (Data, Config, Connection, Storage)**
   - Files: `app/core/config.py`, `app/core/database.py`, `app/core/connection_manager.py`, `app/core/storage_inspector.py`, `app/core/logger.py`
3. **UNIT 03: Core Operations, Scheduling, AI Adapter & Services**
   - Files: `app/core/model_adapter.py`, `app/core/automation_scheduler.py`, `app/core/autonomous_operations_manager.py`, `app/core/backup_manager.py`, `app/core/scheduler_recovery.py`, `app/core/smtp_client.py`, `app/core/task_manager.py`, `app/core/audio_processor.py`
4. **UNIT 04: AI Agents Framework & Meta-Management**
   - Files: `app/agents/agent_registry.py`, `app/agents/manager_agent.py`, `app/agents/assistant_agent.py`, `app/agents/extended_intents.py`, `app/agents/telegram_router.py`, `app/agents/voice_assistant.py`
5. **UNIT 05: Specialized AI Agents & Discovery Engine**
   - Files: `app/agents/discovery_engine.py`, `app/agents/discovery_scheduler.py`, `app/agents/career_agent.py`, `app/agents/coding_agent.py`, `app/agents/cloud_trends_agent.py`, `app/agents/book_agent.py`, `app/agents/news_agent.py`, `app/agents/learning_agent.py`, `app/agents/price_tracker_agent.py`, `app/agents/research_agent.py`, `app/agents/image_agent.py`, `app/agents/entertainment_agent.py`
6. **UNIT 06: Video Maker Engines & Data Ingestion Validation**
   - Files: `app/video_maker/unified_video_maker.py`, `app/video_maker/python/python_core.py`, `app/video_maker/sql/sql_core.py`, `data_ingestion/validate_pipeline_records.py`
7. **UNIT 07: UI Dashboard & Frontend Presentation System**
   - Files: `app/ui/dashboard.py`, `app/ui/dashboard_views.py`, `app/ui/dashboard_css.py`, `app/ui/dashboard_js.py`
8. **UNIT 08: Test Suite, Architectural Reports & Guides**
   - Files: `app/tests/test_suite.py`, `app/tests/test_all_46_views.py`, `app/tests/test_e2e_views_client.py`, `app/tests/test_ui_restructure.py`, `app/tests/*.py`, and markdown technical reports.

## 4. Planned Documentation Structure
- `Markdown/00_INDEX.md`
- `Markdown/01_overview_and_purpose.md`
- `Markdown/02_directory_structure.md`
- `Markdown/03_architecture.md`
- `Markdown/04_workflow_end_to_end.md`
- `Markdown/05_modules/`
  - `01_core_system.md`
  - `02_agent_framework.md`
  - `03_specialized_agents.md`
  - `04_video_generation_engine.md`
  - `05_ui_command_center.md`
- `Markdown/06_data_models_and_schemas.md`
- `Markdown/07_configuration_and_environments.md`
- `Markdown/08_dependencies_and_integrations.md`
- `Markdown/09_setup_run_deploy.md`
- `Markdown/10_testing_and_quality.md`
- `Markdown/11_error_handling_logging_monitoring.md`
- `Markdown/12_glossary.md`
- `<root>/Project.md`
- `<root>/Improvements.md`
