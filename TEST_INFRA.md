# NanoPro AI Studio — E2E Test Infrastructure & Test Suite Documentation

## 1. Test Architecture Overview

NanoPro AI Studio's End-to-End (E2E) Test Suite is an opaque-box, requirement-driven automated verification harness designed to rigorously test latency hardening, multi-model routing, high-concurrency database stability, zero-downtime failover, and executive audit report generation across all 4 core tiers.

```
+----------------------------------------------------------------------------------------------------+
|                                    NanoPro AI Studio Test Architecture                             |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|   +--------------------------------------------------------------------------------------------+   |
|   | Tier 1: Feature Coverage (F1 - F17, >= 5 Tests per Feature = 85 Tests)                     |   |
|   | - F1: Multi-Provider Benchmark Harness       - F10: Credentials Vault In-Memory Caching    |   |
|   | - F2: Workload Test Suite (Python/SQL/Indic) - F11: Background Decoupled Telemetry         |   |
|   | - F3: Groq LPU Latency Hardening             - F12: SQLite Indexation & Query Tuning       |   |
|   | - F4: Gemini Cloud Latency Verification      - F13: TaskManager Lock Isolation             |   |
|   | - F5: Local Ollama GPU Warmup & Latency      - F14: Database Vacuuming & Size Opt          |   |
|   | - F6: In-Memory Fastpath Latency (<10ms)     - F15: 20-Worker Concurrency Validation       |   |
|   | - F7: Provider Circuit Breaker (<1ms Trip)   - F16: Excel Benchmark Report Generator       |   |
|   | - F8: Zero-Downtime Failover Cascade (<500ms)- F17: Markdown Executive Report Generator    |   |
|   | - F9: Deterministic Local Model Resolution                                                 |   |
|   +--------------------------------------------------------------------------------------------+   |
|                                                                                                    |
|   +--------------------------------------------------------------------------------------------+   |
|   | Tier 2: Boundary & Corner Cases (6 Categories x 5 Tests = 30 Tests)                        |   |
|   | - Empty & Whitespace Prompts                 - HTTP 429 Rate Limit Simulation & Backoff    |   |
|   | - Extreme Context Lengths & Token Limits     - Concurrent DB Writes & Conflict Resolution  |   |
|   | - Socket Timeouts & Disconnections           - Deep Conversation History (1,000+ msgs)     |   |
|   +--------------------------------------------------------------------------------------------+   |
|                                                                                                    |
|   +--------------------------------------------------------------------------------------------+   |
|   | Tier 3: Cross-Feature Combinations (Pairwise Feature Interactions = 15 Tests)              |   |
|   | - Failover during active DB write            - Fastpath execution during circuit TRIP      |   |
|   | - Vault retrieval during model routing       - Ollama fallback during health monitoring    |   |
|   | - Telemetry daemon during 20 concurrent qrys - Report export during benchmark run          |   |
|   | - TaskManager stage transition during VACUUM - High-concurrency chat endpoint pipeline     |   |
|   +--------------------------------------------------------------------------------------------+   |
|                                                                                                    |
|   +--------------------------------------------------------------------------------------------+   |
|   | Tier 4: Real-World Application Scenarios (10 Tests)                                        |   |
|   | - Full Python Coding Pipeline (AST + Backup) - Multi-Turn Marathi Dialogue with History    |   |
|   | - Python ETL Pipeline Generation             - Multi-Turn Hindi Dialogue with History      |   |
|   | - SQL Generation with Banking Schema Lookup  - ManagerAgent Full Chat Dispatch Flow        |   |
|   | - Complex SQL Window Function Analytics      - Emergency Offline Local GPU Fallback        |   |
|   | - Full Latency Audit & Report Export Pipeline- Sustained Multi-Tier Database Stability     |   |
|   +--------------------------------------------------------------------------------------------+   |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Invocation Commands

The entire test suite is completely self-contained and runnable via standard Python `unittest`:

```bash
# Run the complete master E2E test suite
python -m unittest app/tests/test_e2e_suite.py

# Run with verbose test case reporting
python -m unittest -v app/tests/test_e2e_suite.py

# Run a specific test class (e.g. Tier 1 Circuit Breaker)
python -m unittest app.tests.test_e2e_suite.TestTier1F7CircuitBreaker

# Run a specific tier (e.g. Tier 4 Real-World Scenarios)
python -m unittest app.tests.test_e2e_suite.TestTier4RealWorldScenarios
```

---

## 3. Tier Summary & Test Counts

| Tier | Name | Target Scope | Test Count | Pass Rate |
|---|---|---|---|---|
| **Tier 1** | Feature Coverage (F1 - F17) | Baseline requirements across all 17 features (>= 5 tests per feature) | **85** | 100% (85/85) |
| **Tier 2** | Boundary & Corner Cases | Empty prompts, token limits, network timeouts, 429 backoff, DB collisions, large history | **30** | 100% (30/30) |
| **Tier 3** | Cross-Feature Combinations | Pairwise interactions between router, database, vault, telemetry, and fastpath | **15** | 100% (15/15) |
| **Tier 4** | Real-World Application Scenarios | End-to-end Python coding, SQL generation, multi-turn Indic dialogues, offline emergency | **10** | 100% (10/10) |
| **Total** | **Full E2E Suite** | **Comprehensive opaque-box verification** | **140** | **100% (140/140)** |

---

## 4. Feature Matrix (F1 - F17)

| Feature # | Feature Name | Test Class | Test Methods Count | Core SLAs & Contracts Verified |
|---|---|---|---|---|
| **F1** | Multi-Provider Benchmark Harness | `TestTier1F1BenchmarkHarness` | 5 | p50/p95/p99 math, TPS formula, success rate, provider aggregation |
| **F2** | Workload Test Suite | `TestTier1F2WorkloadTestSuite` | 5 | Python AST, SQL schema prompt, Marathi dialogue, Hindi dialogue, JSON schema |
| **F3** | Groq LPU Latency Hardening | `TestTier1F3GroqLPULatency` | 5 | `< 1,200ms` code, `< 1,800ms` dialogue, `max_retries=0`, token boundaries |
| **F4** | Gemini Cloud Latency Verification | `TestTier1F4GeminiCloudLatency` | 5 | `< 2,500ms` cloud SLA, `generate_content` + `interactions.create` fallback |
| **F5** | Local Ollama GPU Warmup & Latency | `TestTier1F5OllamaGPUWarmup` | 5 | `keep_alive` option, 15s health caching, `llama3.2:3b`, `qwen2.5-coder:3b` |
| **F6** | In-Memory Fastpath Latency | `TestTier1F6FastpathLatency` | 5 | `< 10ms` response SLA, recipes (Khichadi/Pohe), marriage advice, speed complaint |
| **F7** | Provider Circuit Breaker | `TestTier1F7CircuitBreaker` | 5 | CLOSED/OPEN/HALF_OPEN, `< 1ms` trip time on HTTP 429/connection error |
| **F8** | Zero-Downtime Failover Cascade | `TestTier1F8FailoverCascade` | 5 | Groq -> Gemini -> Ollama `< 500ms` cascade without uncaught caller exceptions |
| **F9** | Deterministic Local Model Resolution | `TestTier1F9LocalModelResolution` | 5 | Direct local Ollama binding (`qwen2.5-coder:3b`, `llama3.2:3b`), zero cloud misrouting |
| **F10** | Credentials Vault In-Memory Caching | `TestTier1F10CredentialsVaultCaching` | 5 | `< 5ms` warm retrieval (< 0.1ms target), cache invalidation on write/delete |
| **F11** | Background Decoupled Telemetry | `TestTier1F11DecoupledTelemetry` | 5 | `< 5ms` response (< 0.1ms target), background thread refresh every 10s |
| **F12** | SQLite Indexation & Query Tuning | `TestTier1F12SQLiteIndexation` | 5 | B-Tree indexes on `conversations(session_id)`, `credentials(service_name)`, `tasks(created_at)` |
| **F13** | TaskManager Lock Isolation | `TestTier1F13TaskManagerLockIsolation` | 5 | `db.save_task()` disk I/O moved outside `self._lock` critical section |
| **F14** | Database Vacuuming & Size Optimization | `TestTier1F14DatabaseVacuuming` | 5 | WAL journal mode, `< 15 MB` file size, `wal_checkpoint(TRUNCATE)`, integrity check |
| **F15** | 20-Worker Concurrency Validation | `TestTier1F15Concurrency20Workers` | 5 | 20 concurrent threads: 0 `database is locked` errors, stable latency |
| **F16** | Excel Benchmark Report Generation | `TestTier1F16ExcelReportGeneration` | 5 | `Latency_Hardening_Benchmark_Report.xlsx` with 5 sheets and openpyxl styling |
| **F17** | Markdown Executive Report Generation | `TestTier1F17MarkdownReportGeneration` | 5 | `Markdown/_work/latency_benchmark.md` with SLA compliance table & audit logs |

---

## 5. Report Artifacts Generated

Running the test suite programmatically creates and validates the two primary reporting artifacts:
1. `Latency_Hardening_Benchmark_Report.xlsx`:
   - Sheet 1: `Executive Summary`
   - Sheet 2: `Provider Benchmarks`
   - Sheet 3: `Failover Matrix`
   - Sheet 4: `Database Latency`
   - Sheet 5: `Concurrency SLA`
2. `Markdown/_work/latency_benchmark.md`:
   - Executive Summary & Architecture Overview
   - SLA Compliance Matrix (p50, p95, status)
   - Failover and Circuit Breaker Verification Logs
