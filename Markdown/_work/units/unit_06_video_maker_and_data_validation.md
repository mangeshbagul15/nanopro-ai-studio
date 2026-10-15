# Unit 06: Video Maker Engines & Data Ingestion Validation

## Purpose and Responsibility
Orchestrates educational programming animation generation and dataset ingestion quality validation:
- `unified_video_maker.py`: Central video coordinator binding SQL and Python animation pipelines, headless browser rendering via Playwright, audio looping/trimming via FFmpeg, and YouTube metadata generation.
- `sql_core.py`: Clause-by-clause animated SQL visualizer (FROM -> JOIN -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY), simulated data table animation, syntax parsing, and thumbnail generator.
- `python_core.py`: Step-by-step animated Python code typing engine, AST statement visitor, sandboxed 5-second execution output capture, and data structure chips visualizer.
- `validate_pipeline_records.py`: Pre-load data engineering dataset validator enforcing null limits, non-negative balance checks, and primary key uniqueness.

## Files Read
- `app/video_maker/unified_video_maker.py`: Unified video creation coordinator [Tier 1]
- `app/video_maker/sql/sql_core.py`: SQL animation generator, clause formatter, Playwright capture [Tier 1]
- `app/video_maker/python/python_core.py`: Python animation generator, AST splitter, subprocess runner [Tier 1]
- `data_ingestion/validate_pipeline_records.py`: Dataset schema, null and uniqueness validator [Tier 1]

## Key Classes / Functions
- `UnifiedVideoMaker.generate_video_pipeline()` (`unified_video_maker.py:39`): [Verified] Coordinates 5 stages: input parsing, AI plan generation, HTML build, Playwright screen recording, FFmpeg audio muxing.
- `sql_core.generate_animation_data()` (`sql_core.py`): [Verified] Breaks SQL query into sequential animated clauses and generates mock relational tables for visualization.
- `py_core.generate_animation_data()` (`python_core.py`): [Verified] Extracts Python literals, creates visualization chips/tables, and sandboxes code execution in a 5s subprocess.
- `validate_pipeline_dataset(df)` (`validate_pipeline_records.py:8`): [Verified] Inspects pandas DataFrame for null violations in critical columns, duplicate keys, and negative balances.

## Dependencies IN & OUT
- **Dependencies IN**: `main.py` (`/api/video/generate`, `/api/metadata/generate`, `/api/thumbnail/generate`), UI dashboard.
- **Dependencies OUT**:
  - Internal: `app.core.config`, `app.core.logger`, `app.core.task_manager`, `app.core.audio_processor`.
  - External: `playwright.async_api`, `ollama`, `fastapi`, `pandas`, `subprocess`, `asyncio`.

## Data Touched
- Filesystem: `app/video_maker/sql/anim_*.html`, `app/video_maker/python/anim_*.html`, `app/video_maker/output/*.mp4`.
- Memory dataframes and JSON representations.

## Config and Env Variables Used
- `OLLAMA_HOST`, `VIDEO_SQL_DIR`, `VIDEO_PY_DIR`, `VIDEO_OUTPUT_DIR`, `IMAGE_OUTPUT_DIR`

## Error Handling, Retries, Logging, Idempotency
- Playwright import wrapped with fallback simulation using FFmpeg `lavfi` color canvas if browser dependencies are missing.
- Python code execution runs in isolated subprocess with strict 5-second timeout to prevent infinite loops.
- `PIPELINE_LOCK` enforces single-threaded video rendering to avoid GPU/CPU saturation.

## Observed Issues
- **U-UNIT06-01** | Category: Code Quality / Redundancy | Severity: Medium | Location: `app/video_maker/sql/sql_core.py:57`, `app/video_maker/python/python_core.py:60`
  - Evidence: Both `sql_core.py` and `python_core.py` independently instantiate unmounted `app = FastAPI()` instances and define duplicate local loggers and model fallback lists.
  - Fix: Remove standalone FastAPI instances and import shared model router and logger from `app.core`.
- **U-UNIT06-02** | Category: Scalability / Resource Contention | Severity: Medium | Location: `app/video_maker/unified_video_maker.py:108`
  - Evidence: Video rendering spawns `asyncio.run()` synchronously inside worker threads, which can cause event loop conflicts on Windows.
  - Fix: Run browser automation on a dedicated async worker process or Celery/background worker queue.

## Open Questions
- None.
