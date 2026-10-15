# Project: NanoPro AI Studio — Latency Hardening & Performance Benchmarking

## Architecture
- **Multi-Model Routing Layer (`app/core/model_adapter.py`)**:
  - `ModelManager`: Orchestrates requests across cloud and local providers with hierarchical routing.
  - `ProviderCircuitBreaker`: Manages state (`CLOSED`, `OPEN`, `HALF_OPEN`) per provider (Groq, Gemini, Ollama) with fast-abort on rate-limiting, network disconnections, and timeouts (< 500ms cascade).
  - `GroqAdapter`: Connects to Groq LPU with `max_retries=0` and low-latency parameters for `qwen/qwen3.8-27b` and `openai/gpt-oss-120b`.
  - `GeminiAdapter`: Connects to Google Gemini Cloud for `gemini-3.5-flash-lite`.
  - `OllamaAdapter`: Connects to Local Ollama GPU on RTX 3050 for `llama3.2:3b` and `qwen2.5-coder:3b` with cached availability and keep-alive.
  - `ConversationalIntelligenceEngine`: In-memory pattern matching fastpath responding in < 10ms.
- **Database & Telemetry Storage (`app/core/database.py`, `app/agents/assistant_agent.py`)**:
  - `CredentialsVault`: In-memory encrypted credential cache with TTL/LRU invalidation (< 5ms retrieval).
  - SQLite Database (`studio_memory.db`): Optimized WAL mode, indexed queries (`conversations`, `credentials`, `tasks`), connection reuse, and automated vacuuming (< 15MB file size).
  - `MonitoringAgent`: Background daemon updating system metrics every 10s to ensure `get_system_health()` returns in < 5ms without blocking.
- **Benchmarking & Audit Reporting (`app/tests/`, `reports/`)**:
  - Automated benchmark harness computing p50, p95, p99 latencies, token throughput (tokens/sec), and success rates across Python coding, SQL generation, and Marathi/Hindi dialogue.
  - Excel Audit Ledger (`Latency_Hardening_Benchmark_Report.xlsx`) with 5 styled sheets via openpyxl.
  - Executive Markdown Report (`Markdown/_work/latency_benchmark.md`).

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | Multi-Provider Benchmark Harness | Automated benchmark measuring p50, p95, p99, tokens/sec, and success rates across Groq, Gemini, Ollama, and Fastpath | M3 | R1 Survey |
| F2 | Workload Test Suite | Benchmarking prompts for Python coding, SQL generation, and Marathi/Hindi conversational dialogue | M3 | R1 Survey |
| F3 | Groq LPU Latency Hardening | Optimizing Groq parameters (`max_retries=0`, token boundaries) to meet < 1,200ms (coding) and < 1,800ms (dialogue) SLAs | M1 | R1 Survey |
| F4 | Gemini Cloud Latency Verification | Verifying `gemini-3.5-flash-lite` meets < 2,500ms SLA | M3 | R1 Survey |
| F5 | Local Ollama GPU Warmup & Latency | Ensuring `llama3.2:3b` and `qwen2.5-coder:3b` run with keep-alive on GPU and cached health checks | M1 | R1 Survey |
| F6 | In-Memory Fastpath Latency | Ensuring conversational fastpath executes in < 10ms end-to-end | M1 | R1 Survey |
| F7 | ModelManager Provider Circuit Breaker | Provider-level circuit breaker (CLOSED/OPEN/HALF_OPEN) with sub-500ms trip time | M1 | R2 Survey |
| F8 | Zero-Downtime Failover Cascade | Cascading Groq -> Gemini -> Ollama in < 500ms without uncaught exceptions during disconnections or 429 rate limits | M1 | R2 Survey |
| F9 | Deterministic Local Model Resolution | Resolving local models to Ollama without timeout-induced cloud misrouting | M1 | R2 Survey |
| F10 | Credentials Vault In-Memory Caching | Caching decrypted credentials with invalidation on write/delete to guarantee < 5ms retrieval | M2 | R3 Survey |
| F11 | Background Decoupled Telemetry | Decoupling `monitoring_agent.get_system_health()` to a background worker to ensure < 5ms response | M2 | R3 Survey |
| F12 | SQLite Indexation & Query Tuning | Adding B-Tree indexes on `conversations(session_id)`, `credentials(service_name)`, and `tasks(created_at)` | M2 | R3 Survey |
| F13 | TaskManager Lock Isolation | Removing synchronous DB disk flush from inside `self._lock` critical section | M2 | R3 Survey |
| F14 | Database Vacuuming & Size Optimization | Enforcing WAL checkpointing and database compaction to maintain file size < 15MB | M2 | R3 Survey |
| F15 | 20-Worker Concurrency Validation | Proving 20 concurrent workers execute without table locks or `database is locked` errors | M2 | R3 Survey |
| F16 | Excel Benchmark Report Generation | Consolidated 5-sheet workbook `Latency_Hardening_Benchmark_Report.xlsx` | M3 | R4 Survey |
| F17 | Markdown Executive Report Generation | Executive summary and metric breakdown at `Markdown/_work/latency_benchmark.md` | M3 | R4 Survey |
| F18 | Comprehensive E2E Test Suite | Opaque-box test suite covering Tiers 1-4 across all features and requirements | E2E Track | Project Pattern |
| F19 | Adversarial Coverage Hardening | White-box stress testing, boundary fault injection, and coverage audit (Tier 5) | M4 | Project Pattern |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | ModelManager Hardening & Circuit Breaker | F3, F5, F6, F7, F8, F9: Implement `ProviderCircuitBreaker`, Groq `max_retries=0`, Ollama model binding & cached health, fastpath end-to-end latency | none | IN_PROGRESS (39a19688-c993-48a2-a4a9-94f49a05cdfa) |
| M2 | Database & Telemetry Concurrency Hardening | F10, F11, F12, F13, F14, F15: Implement `CredentialsVault` memory cache (<5ms), decoupled `MonitoringAgent` telemetry (<5ms), SQLite indexes, vacuuming (<15MB), 20-worker concurrency | none | IN_PROGRESS (ef925c23-362d-4cbf-8f2e-4ace23e4cba9) |
| M3 | Benchmark Suite & Audit Report Generator | F1, F2, F4, F16, F17: Implement multi-provider benchmark harness (p50/p95/p99/TPS), Excel report generator (`Latency_Hardening_Benchmark_Report.xlsx`), Markdown report generator (`Markdown/_work/latency_benchmark.md`) | M1, M2 | PLANNED |
| M4 | Final Milestone: 100% E2E Test Pass & Hardening | Phase 1: Pass 100% E2E tests (Tiers 1-4); Phase 2: Tier 5 adversarial stress testing, coverage verification, audit signoff | M3, TEST_READY | PLANNED |
| E2E | E2E Testing Track | F18: Build requirement-driven opaque-box test suite (Tiers 1-4), generate `TEST_INFRA.md`, publish `TEST_READY.md` | none | IN_PROGRESS (a21b670d-cd3e-4698-a98e-89a4292ebeb6) |

## Interface Contracts
### ModelManager ↔ ProviderCircuitBreaker
- `circuit_breaker.record_success(provider: str) -> None`
- `circuit_breaker.record_failure(provider: str, error: Exception) -> None`
- `circuit_breaker.can_execute(provider: str) -> bool`
- Provider state transition: 3 consecutive failures or immediate HTTP 429 / ConnectionError -> `OPEN` (trip time < 1ms). Timeout to `HALF_OPEN`: 30s.

### ModelManager ↔ Provider Adapters
- `chat(prompt: str, system_prompt: str = None, **kwargs) -> Tuple[str, Dict[str, Any]]`
- Telemetry dictionary returned must include:
  - `latency_ms: float`
  - `token_count: int` (completion tokens)
  - `tps: float` (tokens per second)
  - `model: str`
  - `provider: str`

### CredentialsVault Interface
- `get_credential(service_name_or_id: str) -> Optional[Dict[str, Any]]`
  - Must return in < 5ms (target < 0.1ms for cached hit).
  - Cache invalidated automatically on `add_credential()` or `delete_credential()`.

### MonitoringAgent Interface
- `get_system_health() -> Dict[str, Any]`
  - Must return in < 5ms (target < 0.1ms).
  - Background daemon thread refreshes metrics every 10s.

## Code Layout
- `app/core/model_adapter.py`: `ModelManager`, `ProviderCircuitBreaker`, `GroqAdapter`, `GeminiAdapter`, `OllamaAdapter`.
- `app/core/database.py`: `Database`, `CredentialsVault`, connection management, pragmas, indexes.
- `app/agents/assistant_agent.py`: `MonitoringAgent`, system health telemetry.
- `app/core/task_manager.py`: `TaskManager`, lock isolation.
- `app/tests/test_latency_benchmarks.py`: Benchmark suite and latency test cases.
- `app/tests/test_failover_circuit_breaker.py`: Circuit breaker and failover tests.
- `app/tests/test_database_concurrency.py`: 20-worker concurrency and DB latency tests.
- `app/reports/latency_report_generator.py`: Generates `Latency_Hardening_Benchmark_Report.xlsx` and `Markdown/_work/latency_benchmark.md`.
- `Latency_Hardening_Benchmark_Report.xlsx`: Root deliverable Excel workbook.
- `Markdown/_work/latency_benchmark.md`: Root deliverable Markdown executive summary.
