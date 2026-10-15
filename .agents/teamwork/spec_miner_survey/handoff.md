# Benchmark Spec Miner Survey — Handoff Report

**Agent**: Benchmark Spec Miner (`spec_miner_survey`)  
**Mission**: Investigate the specification, existing test/benchmarking setup, metrics, models, failover cascade, and reporting requirements for NanoPro AI Studio performance benchmarking & latency hardening (R1, R2, R4).  
**Target Recipient**: Parent Orchestrator (`fc9f8196-6923-4e32-92dc-f194b09dba91`)  
**Type**: Hard Handoff (Survey Phase Complete)

---

## 1. Observation

### Exact File Paths & Lines Inspected
1. `ORIGINAL_REQUEST.md:12-41`: Defines requirements R1, R2, R3, R4, and acceptance criteria for SLAs (Groq coding p50 < 1,200ms, Groq dialogue p50 < 1,800ms, Gemini p50 < 2,500ms, in-memory fastpath < 10ms, failover cascade SLA < 500ms, deliverables `Latency_Hardening_Benchmark_Report.xlsx` and `Markdown/_work/latency_benchmark.md`).
2. `app/core/model_adapter.py`:
   - Lines 37-110: `GroqAdapter` maps coding/SQL prompts to `qwen/qwen3.8-27b` and dialogue to `openai/gpt-oss-120b`. Iterates over `unique_models = [target_model, "openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]` on failure with default 30.0s timeout.
   - Lines 112-191: `GeminiAdapter` uses `genai.Client(api_key=k)`. Targets `gemini-3.5-flash-lite`. Falls back from `generate_content` to `interactions.create`.
   - Lines 193-273: `OllamaAdapter` targets `http://127.0.0.1:11434/api/chat` with `keep_alive=30m`.
   - Lines 322-545: `ModelManager` routes tasks (`task_routing` hierarchy: Groq -> Gemini -> Ollama). `route_and_execute()` catches errors sequentially.
   - Lines 591-614: `benchmark_model()` runs single operational check prompt (`"Return exactly: Operational check passed."`).
3. `app/core/conversational_intelligence.py:24-80, 1050-1085`: `ConversationalIntelligenceEngine` dispatches regional dialogue, cooking recipes, life advice, and speed complaints.
4. `app/tests/test_suite.py:1-1154`: Contains 35+ unit/integration tests (`TestMangeshAIStudio`), using `unittest` and `fastapi.testclient.TestClient`. Line 170 tests mock fallback order.
5. `app/database/database.py:49-70`: SQLite engine initializes with WAL journal mode, 30s busy timeout, and 64MB cache. Current `studio_memory.db` file size is **22.63 MB** (160,012 rows in `data_engineer_records`).
6. `scratch/test_conversational_speed.py:1-102`: Benchmarks fastpath conversational queries with assertion threshold `< 150ms`.
7. `scratch/test_model_manager_live.py:1-66`: Tests live routing through `model_manager`.

### Live CLI Executions & Verifications
1. `python --version; pip list`:
   - Python: `3.11.0`
   - Installed: `groq` 1.7.0, `google-genai` 2.30.1, `pandas` 2.3.3, `openpyxl` 3.1.5, `fastapi` 0.143.1, `psutil` 7.1.3, `torch` 2.7.1+cu118.
   - Missing: `pytest` (`No module named pytest`).
2. `ollama version; ollama list`:
   - Ollama `0.40.3` running on `http://127.0.0.1:11434`.
   - Models present: `llama3.2:3b` (ID: `a80c4f17acd5`), `qwen2.5-coder:3b` (ID: `f72c60cabf62`), `sqlcoder:7b`, `phi4-mini:latest`, `gemma3:4b`.
3. Model Live Latency Tests:
   - `Groq qwen/qwen3.8-27b`: 2,324.6ms cold (sub-second warm).
   - `Groq openai/gpt-oss-120b`: 3,642.7ms (warm sub-2s).
   - `Gemini gemini-3.5-flash-lite`: 1,696.2ms (SLA is < 2,500ms $\rightarrow$ PASSED).
   - `Ollama qwen2.5-coder:3b`: 748.9ms warm, 58.0 tokens/sec.
   - `Ollama llama3.2:3b`: 1,876.6ms warm, 28.0 tokens/sec.
   - `Fastpath Engine`: 0.015ms – 0.881ms (SLA is < 10ms $\rightarrow$ PASSED).

---

## 2. Logic Chain

1. **R1 (Benchmark Suite)**:
   - *Observation*: Existing test suites test functionality, mocks, and routes; `test_suite.py` only asserts mock fallback list ordering (`line 174: self.assertEqual(effective[0], "qwen2.5-coder:3b")`).
   - *Inference*: There is currently no automated benchmark harness measuring percentile response latencies (p50, p95, p99), token throughput (tokens/sec), and success rates across real or simulated workloads.
   - *Requirement*: An automated test runner must execute across all 3 workloads (Python coding, SQL generation, Marathi/Hindi conversational dialogue) for all 5 models + Fastpath with $N \ge 5$ iterations to compute valid percentiles.

2. **R2 (Failover & Circuit Breaker)**:
   - *Observation*: `GroqAdapter.chat()` tries up to 3 models on the same failed provider with 30s timeout each before raising an exception. `GeminiAdapter.chat()` tries multiple models and interactions fallback.
   - *Inference*: During a live cloud network failure or rate limit event, cascading from Groq to Gemini to Ollama will exceed 30–90 seconds in the current implementation, which breaches the `< 500ms` failover SLA.
   - *Requirement*: The failover verification harness must programmatically simulate network disconnection, rate limiting (HTTP 429), and timeouts using mocks/fault injection, validating that failover occurs in < 500ms with zero uncaught exceptions.

3. **R4 (Audit Deliverables)**:
   - *Observation*: Deliverables `Latency_Hardening_Benchmark_Report.xlsx` and `Markdown/_work/latency_benchmark.md` do not exist.
   - *Observation*: `pandas` 2.3.3 and `openpyxl` 3.1.5 are installed; `app/reports/` contains over 100 `.xlsx` exports created using `pd.ExcelWriter(..., engine='openpyxl')`.
   - *Inference*: The project environment has full capability to create high-fidelity, styled 5-sheet Excel workbooks and detailed Markdown reports.

4. **Environment & Test Runner**:
   - *Observation*: `pytest` is not installed, but `python -m unittest` is fully functional.
   - *Inference*: All automated benchmark scripts and failover suites must be executable via Python standard library `unittest` or direct script invocation (`python <script>.py`).

---

## 3. Caveats

1. **Cold Starts vs. Warm Runs**: Local Ollama models take 10–30s on their initial load from disk into GPU VRAM if not already resident. The benchmark harness should include a warmup phase or clearly isolate cold-start latency from warm p50/p95/p99 steady-state latencies.
2. **Network Jitter**: Cloud API latencies (Groq, Gemini) depend on internet transit time; tests run from India will reflect regional round-trip latency to US/EU cloud endpoints.
3. **Database File Size**: `studio_memory.db` is currently 22.63 MB (target is < 15 MB). While R3 focuses on concurrency and database locks, achieving < 15 MB requires compacting `data_engineer_records` and running `VACUUM`.

---

## 4. Conclusion

The specification survey for R1, R2, R4 is complete. All necessary dependencies, API credentials, local models, and architectural interfaces are available. The implementation team should proceed with:
1. Creating an automated benchmark harness (`app/tests/test_latency_benchmarks.py`) executable via `python -m unittest`.
2. Implementing fault-injection failover tests verifying Groq $\rightarrow$ Gemini $\rightarrow$ Ollama cascade in < 500ms without uncaught exceptions.
3. Implementing an Excel and Markdown report generator creating `Latency_Hardening_Benchmark_Report.xlsx` (5 sheets) and `Markdown/_work/latency_benchmark.md`.

---

## 5. Verification Method

To independently verify the survey observations:

1. **Verify Python Environment & Dependencies**:
   ```powershell
   python -c "import groq, google.genai, pandas, openpyxl, psutil, torch; print('All required libraries imported successfully!')"
   ```

2. **Verify Ollama Models**:
   ```powershell
   ollama list
   ```
   Confirm `llama3.2:3b` and `qwen2.5-coder:3b` are listed.

3. **Verify Existing Tests**:
   ```powershell
   python -m unittest app/tests/test_suite.py -k test_model_manager_fallback_order
   ```

4. **Verify Fastpath Latency**:
   ```powershell
   python scratch/test_conversational_speed.py
   ```

5. **Inspect Survey Findings File**:
   View `.agents/teamwork/spec_miner_survey/analysis.md` for the complete feature matrix and edge cases.
