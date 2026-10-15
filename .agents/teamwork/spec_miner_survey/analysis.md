# NanoPro AI Studio - Performance Benchmarking & Latency Hardening Specification Mining Report

**Timestamp**: 2026-10-14T18:28:00Z  
**Working Directory**: `c:\Mangesh\AI video\Mangesh_Nano_Pro_AI_Studio_COMPLETE (34)\Mangesh_Nano_Pro_AI_Studio\.agents\teamwork\spec_miner_survey`  
**Target Scope**: R1 (Multi-Provider Latency & Throughput Benchmark Suite), R2 (Automated Zero-Downtime Failover & Circuit Breaker Verification), R4 (Automated Performance & Latency Audit Deliverables).

---

## 1. Executive Summary

This specification mining survey investigated the existing codebase, runtime environment, test harnesses, LLM model routing, failover cascades, in-memory conversational fastpaths, and reporting utilities for NanoPro AI Studio.

Key findings:
1. **Multi-Model Integration Operational**: Groq LPU Cloud (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`), Google Gemini Cloud (`gemini-3.5-flash-lite`), and Local Ollama GPU (`llama3.2:3b`, `qwen2.5-coder:3b`) are fully present, authenticated via `.env`, and verified operational on NVIDIA RTX 3050 GPU.
2. **Sub-Millisecond Conversational Fastpath**: `ConversationalIntelligenceEngine` in `app/core/conversational_intelligence.py` serves conversational dialogue (recipes, Marathi advice, greetings, latency complaints) directly from in-memory RAM in **0.015ms – 0.88ms**, easily exceeding the `< 10ms` SLA.
3. **Existing Test Framework**: 9 test suites exist in `app/tests/` (most notably `test_suite.py` with 35+ test cases, 1,154 lines). However, `pytest` is **not installed** in the Python 3.11 environment; tests are executed via standard library `unittest` or direct script invocation.
4. **Critical Gaps in R1, R2, R4**:
   - **R1 Gap**: No automated benchmark harness currently measures percentile response times (p50, p95, p99), token throughput (tok/sec), or concurrent success rates across the 3 integrated providers and 5 models.
   - **R2 Gap**: `ModelManager.route_and_execute` lacks a stateful Circuit Breaker (`CLOSED`, `OPEN`, `HALF-OPEN`). If Groq or Gemini fails, their respective adapters iterate through multiple fallback models with default 30-second timeouts, causing up to 90 seconds of latency during outages—severely breaching the `< 500ms` failover cascade SLA.
   - **R4 Gap**: Neither `Latency_Hardening_Benchmark_Report.xlsx` nor `Markdown/_work/latency_benchmark.md` exist. However, `openpyxl` 3.1.5 and `pandas` 2.3.3 are installed and ready to generate multi-tab executive reports.

---

## Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Model Routing | `ModelManager.route_and_execute` | Intelligently routes tasks to primary/fallback models based on task type (`coding`, `dialogue`, `general`), measuring latency | `prompt: str`, `task_type: str`, `schema: Optional[Dict]`, `system_prompt: Optional[str]`, `timeout: float` | `(content: str, model: str, mode: str, latency_ms: float)` | Catches exception per candidate, logs warning, falls back to next model. If all fail, raises `RuntimeError` | `app/core/model_adapter.py:472` |
| 2 | Model Adapter | `GroqAdapter.chat` | Ultra-fast LPU inference via Groq Cloud API for `qwen/qwen3.8-27b`, `openai/gpt-oss-120b`, `openai/gpt-oss-20b` | `model: str`, `prompt: str`, `schema: Optional[Dict]`, `system_prompt: Optional[str]`, `timeout: float` | `Tuple[str, str]` (content, `groq-lpu:<model>`) | If key missing raises `ValueError`; iterates over unique fallback models before raising `RuntimeError` | `app/core/model_adapter.py:37` |
| 3 | Model Adapter | `GeminiAdapter.chat` | High-context & multimodal intelligence via Google Gemini Cloud API (`gemini-3.5-flash-lite`, `gemini-3.8-flash`) | `model: str`, `prompt: str`, `schema: Optional[Dict]`, `system_prompt: Optional[str]`, `timeout: float` | `Tuple[str, str]` (content, `gemini-cloud:<model>`) | Tries `models.generate_content`, then `interactions.create`; if all fail raises `RuntimeError` | `app/core/model_adapter.py:112` |
| 4 | Model Adapter | `OllamaAdapter.chat` | Local GPU offline inference via HTTP REST (`/api/chat`) on NVIDIA RTX 3050 | `model: str`, `prompt: str`, `schema: Optional[Dict]`, `system_prompt: Optional[str]`, `timeout: float` | `Tuple[str, str]` (content, `ollama-http`) | Raises `ConnectionError` on `URLError`, or `RuntimeError` on execution error | `app/core/model_adapter.py:193` |
| 5 | Telemetry | `ModelManager.get_router_telemetry` | Real-time health, connection state, model call counts, error counts, and average latencies | None | `Dict[str, Any]` with `groq_lpu_connected`, `gemini_cloud_connected`, `ollama_connected`, `models` list | Non-throwing; returns current memory dictionary | `app/core/model_adapter.py:546` |
| 6 | Telemetry | `ModelManager.benchmark_model` | Single-shot latency probe executing test prompt against specified model | `model_name: str` | `Dict[str, Any]` (`status`, `model`, `latency_ms`, `response` or `error`) | Catches exceptions, returns `status: "failed"` with `latency_ms` | `app/core/model_adapter.py:591` |
| 7 | Fastpath | `ConversationalIntelligenceEngine.dispatch` | Instant sub-millisecond in-memory RAM conversational responses for cooking, recipes, life advice, speed complaints, banter | `p_lower: str`, `user_message: str`, `session_id: str` | `Dict[str, Any]` (`handled`, `reply`, `agent_id`) or `None` | Non-throwing regex matching and string template return | `app/core/conversational_intelligence.py:1050` |
| 8 | REST API | `/api/manager/chat` | Main natural-language entrypoint processing chat, conversational fastpath, risk governance, and training recording | `ChatRequest(message, session_id, action, plan_id)` | `JSONResponse` with reply, reasoning, plan_id, agent_id | Catches model errors, falls back to conversational intelligence or generic guidance | `main.py:513` |
| 9 | REST API | `/api/models/list` | Returns provider status, installed Ollama models, and effective model fallback list | None | `JSONResponse` with provider, installed_models, effective_models | Returns default list if Ollama unreachable | `main.py:732` |
| 10 | REST API | `/api/models/test` | Inference verification endpoint for a given model | `{"model": str}` | `JSONResponse` with status, model, mode, response, duration_sec | Returns status `error` with exception string and duration | `main.py:747` |
| 11 | REST API | `/api/coding/execute` | Code generation, debugging, explanation, and unit test generation | `CodingRequest(prompt, code, action, language, model)` | `JSONResponse` with result, model_used, analysis | Returns error with `fallback_hint` | `main.py:802` |
| 12 | Database Concurrency | `DatabaseManager.get_connection` | SQLite WAL connection with 30s busy timeout, 64MB cache, and exponential backoff retry | `db_path: Optional[Path]` | `sqlite3.Connection` | Retries up to 5 times on `database is locked` / `busy` with exponential backoff | `app/core/database.py:49` |
| 13 | Reporting | Excel Writer Utility | Multi-sheet Excel workbook export using `pandas` and `openpyxl` engine | DataFrames, sheet names, output path | `.xlsx` file on disk | Raises IO/permissions errors if file locked | `app/agents/lakehouse_drills.py:511` |
| 14 | Test Suite | `TestMangeshAIStudio` | 35+ comprehensive unit and integration tests across all studio modules | `unittest` test loader | Test execution results (Pass/Fail) | Halts on assertion error or uncaught exception | `app/tests/test_suite.py:48` |

---

## Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Groq LPU Initial Request | First prompt to `qwen/qwen3.8-27b` after cold start | 2,324.6ms latency due to initial SSL handshake & TCP connection negotiation; subsequent warm calls achieve sub-second execution. |
| 2 | Groq Cloud Failure & Fallback | Groq API key invalid or network disconnected | `GroqAdapter.chat` sequentially loops through up to 3 candidate models (`target_model`, `openai/gpt-oss-120b`, `qwen/qwen3.8-27b`). If network times out at 30s per model, cumulative failure latency can reach 90s before falling back to Gemini. |
| 3 | Gemini Cloud API Latency | `gemini-3.5-flash-lite` prompt | 1,696.2ms latency observed, comfortably within the `< 2,500ms` SLA. Fallback from `generate_content` to `interactions.create` adds ~1,500ms if initial API method rejects payload. |
| 4 | Ollama Model Cold Start | First call to `qwen2.5-coder:3b` when unloaded from GPU VRAM | 30,015.8ms latency as weights are loaded into NVIDIA RTX 3050 VRAM. Subsequent warm requests respond in 748.9ms at 58.0 tokens/sec. |
| 5 | Ollama Model Cold Start | First call to `llama3.2:3b` when unloaded from GPU VRAM | 10,667.6ms latency during VRAM page-in. Subsequent warm requests respond in 1,876.6ms at 28.0 tokens/sec. |
| 6 | In-Memory Conversational Fastpath | Multilingual queries: Marathi recipes ("KHICHADI KASHI BANAVAYACHI?"), marriage guidance, latency complaints | Responds in **0.015ms to 0.881ms** completely bypassing LLM network hops and local GPU loading, complying with the `< 10ms` SLA. |
| 7 | SQLite Database Size | Querying `studio_memory.db` size | Current file size is **22.63 MB** (containing 160,012 `data_engineer_records` and 20,000 `FACT_BANK_TRANSACTIONS`). To satisfy the SLA of `< 15 MB`, a table archival/compaction and SQLite `VACUUM` is required. |
| 8 | Python Test Runner | Running `pytest` | Command fails with `No module named pytest`. Only Python standard library `unittest` (`python -m unittest`) is available in the Python 3.11 environment. |
| 9 | Rapid Consecutive Imports | Importing `app.core.model_adapter` without isolating environment | `app/__init__.py` executes `from .core import *`, which initializes `autonomous_operations_manager`, triggering `DiscoveryScheduler` background threads that attempt live Telegram notifications. |

---

## 2. Detailed Technical Audit (R1, R2, R4)

### R1. Multi-Provider Latency & Throughput Benchmark Suite

#### Required Specifications
- **Metrics**:
  - Latency: p50 (median), p95, p99, min, max, mean, standard deviation (in milliseconds).
  - Throughput: tokens-per-second (`completion_tokens / (latency_ms / 1000)`).
  - Success Rate: `successful_calls / total_calls * 100%`.
  - Concurrency: Measure performance and contention under concurrent load.
  - Process Memory: Process RSS RAM before/after via `psutil.Process().memory_info().rss`.
- **Integrated Models (5 Models across 3 Providers)**:
  1. Groq LPU Cloud:
     - `openai/gpt-oss-120b`: Flagship 120B reasoning, multilingual Marathi/Hindi/English. SLA: p50 < 1,800ms.
     - `qwen/qwen3.8-27b`: 27B state-of-the-art code & SQL engine. SLA: p50 < 1,200ms.
  2. Google Gemini Cloud:
     - `gemini-3.5-flash-lite`: Multimodal, deep context & Marathi nuance. SLA: p50 < 2,500ms.
  3. Local Ollama GPU (NVIDIA RTX 3050):
     - `llama3.2:3b`: Offline dialogue & conversational logic.
     - `qwen2.5-coder:3b`: Fast offline Python code & SQL generation.
  4. Fastpath Engine:
     - In-memory conversational fastpath. SLA: p50 < 10ms.
- **Simulated Workloads**:
  1. *Python Coding Workload*: Real-world Python tasks (e.g., Pandas data transformation, recursive graph search, CSV chunking parser).
  2. *SQL Generation Workload*: Real-world enterprise SQL (e.g., Window functions `ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY txn_date DESC)`, `QUALIFY` deduplication, SCD Type 2 merge logic).
  3. *Marathi/Hindi Conversational Workload*: Authentic regional dialogue ("KHICHADI KASHI BANAVAYACHI?", "I NEED WIFE, HOW CAN I ACHIVE?", "SNOW RESPOND KARTOY", Marathi guidance).

---

### R2. Automated Zero-Downtime Failover & Circuit Breaker Verification

#### Cascade Hierarchy
The required failover cascade sequence is:
$$\text{Groq LPU Cloud} \longrightarrow \text{Google Gemini Cloud} \longrightarrow \text{Local Ollama GPU}$$

#### Failover SLAs & Assertions
1. **Cascade Latency**: Total transition time from failure detection on the primary provider to a successful secondary provider response must be **< 500ms** (or within the fast-fail circuit breaker SLA).
2. **Exception Containment**: Zero uncaught exceptions propagated to the caller. All failures must be intercepted and handled transparently.
3. **Simulated Failure Scenarios**:
   - Scenario A: Groq API failure (simulated 429 Rate Limit / HTTP 503 / Network Timeout) $\rightarrow$ Seamless fallback to Gemini Cloud.
   - Scenario B: Cloud Outage (Groq and Gemini both offline/unreachable) $\rightarrow$ Seamless fallback to Local Ollama GPU (`llama3.2:3b` / `qwen2.5-coder:3b`).
   - Scenario C: Circuit Breaker State Transition $\rightarrow$ Verify circuit trips from `CLOSED` to `OPEN` after repeated threshold errors, bypassing dead providers without waiting for network timeouts.

#### Current Implementation Analysis in `model_adapter.py`
In the existing codebase:
- `ModelManager.route_and_execute()` catches exceptions in a `try...except Exception as e:` block and iterates to the next candidate in `model_list`.
- **Vulnerability**: If Groq experiences a network timeout, `GroqAdapter.chat()` attempts `target_model`, `openai/gpt-oss-120b`, `qwen/qwen3.8-27b`, and `openai/gpt-oss-20b` sequentially. With a default timeout of 30s per model, the caller waits up to 90 seconds before Groq raises an error and Gemini is attempted!
- **Architectural Solution**: A stateful `CircuitBreaker` pattern with configurable `per_call_timeout` (e.g., 2.0s or fast-fail upon connection errors) must be incorporated to achieve the `< 500ms` failover SLA.

---

### R4. Automated Performance & Latency Audit Deliverables

#### Deliverable 1: `Latency_Hardening_Benchmark_Report.xlsx`
The benchmark suite must generate a structured multi-tab Excel workbook using `openpyxl` / `pandas`:
- **Sheet 1: `Executive_Summary`**
  - Benchmark run metadata: Execution timestamp, host OS (Windows 11), CPU/GPU (NVIDIA RTX 3050), Python version (3.11.0).
  - SLA Compliance Summary Table: Metric, Provider, Model, Target SLA, Measured p50, Compliance Status (`PASSED` / `FAILED`).
- **Sheet 2: `Provider_Latency_Matrix`**
  - Performance statistics table across all 5 models + Fastpath across all 3 workloads:
    - Provider, Model Name, Workload, Sample Runs ($N$), Min Latency (ms), Mean Latency (ms), Median / p50 (ms), p95 (ms), p99 (ms), Max Latency (ms), Throughput (Tokens/sec), Success Rate (%).
- **Sheet 3: `Failover_Cascade_Audit`**
  - Assertions ledger for failover scenarios:
    - Test ID, Failure Injection Type (Rate Limit 429, Network Timeout, Complete Cloud Offline), Primary Provider Attempted, Failover Target, Failover Transition Latency (ms), Target SLA (< 500ms), Unhandled Exceptions Count (0), Verdict (`PASSED`).
- **Sheet 4: `Workload_Detailed_Runs`**
  - Granular raw log of every individual inference invocation:
    - Run ID, Timestamp, Provider, Model, Task Type, Prompt Preview, Output Tokens, Latency (ms), Process RAM Delta (MB), HTTP Status, Error (if any).
- **Sheet 5: `Fastpath_Telemetry`**
  - Verification of the in-memory fastpath engine:
    - Query, Category, Handler Method, Latency (ms), SLA (< 10ms), Verified (`PASSED`).

#### Deliverable 2: `Markdown/_work/latency_benchmark.md`
A comprehensive Markdown executive report covering:
1. Executive Overview & Methodology
2. Hardware & Runtime Topology
3. Benchmark Results & Percentile Analysis (p50, p95, p99)
4. Throughput (Tokens/sec) Comparison Matrix
5. Zero-Downtime Failover & Circuit Breaker Verification Ledger
6. SLA Compliance Scorecard
7. Database Concurrency & Storage Optimization Audit
8. Recommendations & Latency Hardening Roadmap

---

## 3. Environment & Dependency Audit

| Component | Status | Details |
|-----------|--------|---------|
| **Operating System** | Windows 10 / 11 64-bit | Local environment with PowerShell / cmd |
| **Python** | 3.11.0 | Standard CPython 3.11.0 |
| **Package: `groq`** | Installed (v1.7.0) | Live API Key configured and operational |
| **Package: `google-genai`** | Installed (v2.30.1) | Live API Key configured and operational |
| **Package: `pandas`** | Installed (v2.3.3) | Dataframe processing & multi-sheet Excel output |
| **Package: `openpyxl`** | Installed (v3.1.5) | Excel styling, formatting, and tab generation |
| **Package: `fastapi` / `uvicorn`** | Installed (v0.143.1 / v0.54.0) | Web API framework |
| **Package: `psutil`** | Installed (v7.1.3) | Process CPU and memory footprint profiling |
| **Package: `torch`** | Installed (v2.7.1+cu118) | GPU acceleration runtime |
| **Test Runner: `pytest`** | **NOT INSTALLED** | `python -m pytest` returns module not found |
| **Test Runner: `unittest`** | **AVAILABLE** | Standard library `python -m unittest` supported |
| **Ollama Service** | **RUNNING** (v0.40.3) | Host: `http://127.0.0.1:11434` |
| **Local Model: `llama3.2:3b`** | **INSTALLED** | ID: `a80c4f17acd5` (2.0 GB), ~28 tok/sec warm |
| **Local Model: `qwen2.5-coder:3b`**| **INSTALLED** | ID: `f72c60cabf62` (1.9 GB), ~58 tok/sec warm |
| **Database File** | Present | `app/database/studio_memory.db` (22.63 MB, WAL enabled) |

---

## 4. Recommended Test Harness & Runner Architecture

To execute the benchmark and generate the required deliverables without introducing external dependencies or failing test runners:

1. **Standalone Benchmark Harness (`app/tests/benchmark_harness.py`)**:
   - Implemented as an executable Python module runnable via:
     `python -m unittest app/tests/test_latency_benchmarks.py` OR `python app/tests/benchmark_harness.py`.
   - Uses `time.perf_counter()` for sub-microsecond timing precision.
   - Computes empirical percentiles ($p50, p95, p99$) using standard math / `numpy` / `pandas`.
   - Runs $N \ge 5$ iterations per model across all 3 workloads to establish statistically rigorous percentiles.

2. **Automated Mock/Real Provider Injector**:
   - Supports both Live Provider execution (benchmarking real Groq, Gemini, and Ollama latencies) and Simulated Fault Injection (intercepting network/HTTP calls using `unittest.mock.patch` to verify <500ms failover cascades).

3. **Report Generation Service (`app/reports/benchmark_report_generator.py`)**:
   - Consumes the benchmark dataset and outputs:
     * `Latency_Hardening_Benchmark_Report.xlsx` in project root with professional formatting.
     * `Markdown/_work/latency_benchmark.md` with structured executive tables.
