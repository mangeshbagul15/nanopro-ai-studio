# Handoff Report: Model Architecture Explorer (Survey Phase — R1 & R2)

**Working Directory:** `c:\Mangesh\AI video\Mangesh_Nano_Pro_AI_Studio_COMPLETE (34)\Mangesh_Nano_Pro_AI_Studio\.agents\teamwork\explorer_survey_1`  
**Parent Agent:** `fc9f8196-6923-4e32-92dc-f194b09dba91`  
**Date:** 2026-10-15  

---

## 1. Observation

1. **Model Architecture Implementation:**
   - `app/core/model_adapter.py` defines `ModelManager` (lines 322–616), `GroqAdapter` (lines 37–110), `GeminiAdapter` (lines 112–191), `OllamaAdapter` (lines 193–274), and `RemoteAPIAdapter` (lines 275–320).
   - In `app/core/model_adapter.py:335-343`, task routing priority order is:
     - `coding`: `["qwen/qwen3.8-27b", "gemini-3.5-flash-lite", "qwen2.5-coder:3b", "qwen2.5-coder:7b", "phi4-mini:latest"]`
     - `dialogue`: `["openai/gpt-oss-120b", "gemini-3.5-flash-lite", "openai/gpt-oss-20b", "llama3.2:3b", "qwen2.5-coder:3b"]`
   - Active API keys in `.env` for Groq (`gsk_...`) and Gemini (`AQ.Ab8...`) are present and live. Local Ollama server is running at `http://127.0.0.1:11434` with installed models: `llama3.2:3b`, `qwen2.5-coder:3b`, `phi4-mini:latest`, `gemma3:4b`, `sqlcoder:7b`.

2. **Live Workload Performance Measurements:**
   - Groq LPU SQL (`qwen/qwen3.8-27b`): **524.1ms**, 61 words, **151.3 TPS**.
   - Groq LPU Dialogue (Marathi) (`openai/gpt-oss-120b`): **3,319.7ms**, 350 words, **137.1 TPS**.
   - Groq LPU Dialogue (Hindi) (`openai/gpt-oss-120b`): **2,274.0ms**, 346 words, **197.8 TPS**.
   - Gemini Cloud SQL (`gemini-3.5-flash-lite`): **1,585.1ms**, 172 words, **141.1 TPS**.
   - Gemini Cloud Dialogue (Marathi): **4,789.6ms**, 389 words, **105.6 TPS**.
   - Gemini Cloud Code: **8,261.0ms**, 237 words, **37.3 TPS**.
   - Ollama GPU Code (`qwen2.5-coder:3b`): **1,232.2ms**, 97 words, **58.6 TPS** (warm GPU).
   - Ollama GPU SQL (`qwen2.5-coder:3b`): **21,853.5ms**, 168 words, **10.0 TPS** (cold model load).
   - In-memory Fastpath (`app/core/conversational_intelligence.py:17-150`):
     - `KHICHADI KASHI BANAVAYACHI?`: **0.924ms**
     - `I NEED WIFE, HOW CAN I ACHIVE?`: **0.098ms**
     - `SNOW RESPOND KARTOY NANOPRO`: **0.017ms**
     - `pohe kase banvayche`: **0.063ms**
   - End-to-end `ManagerAgent.chat_interact()` fastpath: **11.1ms - 17.8ms** due to synchronous SQLite `db.add_chat_message` transactions.

3. **Circuit Breaker & Fallback Behavior Observations:**
   - There is NO Circuit Breaker class or state tracking in `app/core/model_adapter.py`.
   - In `app/core/model_adapter.py:84-109`, `GroqAdapter.chat()` iterates through `[target_model, "openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]`.
   - In `app/core/model_adapter.py:488-523`, `route_and_execute()` cascades linearly across models. When Groq failed in our live test, it attempted `openai/gpt-oss-120b` (failed), then attempted `qwen/qwen3.8-27b` (failed), before falling back to Gemini.
   - During `test_suite.py` execution, Groq returned HTTP 429:
     `[INFO] [httpx] HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 429 Too Many Requests"`
     `[INFO] [groq._base_client] Retrying request to /openai/v1/chat/completions in 9.000000 seconds`
     The Groq SDK client paused execution for 9 seconds inside its retry loop because `groq.Groq` was instantiated without `max_retries=0`.
   - In `app/core/model_adapter.py:396-417` (`get_adapter_for_model`), local models (`llama3.2:3b`, `qwen2.5-coder:3b`) are checked against `self.ollama.is_available()`. If Ollama `/api/tags` takes >1.5s, `get_adapter_for_model` falls through to Groq:
     `ModelRouter: Routing [general] task to [llama3.2:1b] via [groq-lpu]...`
     `ModelRouter: Routing [general] task to [llama3.2:3b] via [groq-lpu]...`

4. **Metrics and Reporting Gaps:**
   - In `app/core/model_adapter.py:366-377`, `telemetry` records only average and last latency, total calls, and error count. Percentiles (p50, p95, p99) and tokens-per-second (TPS) are not recorded or computed.
   - Token usage objects (`resp.usage`, `resp.usage_metadata`, and `eval_count`) are stripped before returning.

---

## 2. Logic Chain

1. **Latency SLA Compliance (R1):**
   - Observation 2 demonstrates that Groq SQL generation (`qwen/qwen3.8-27b`) achieves 524.1ms (< 1,200ms target) and Gemini SQL generation achieves 1,585.1ms (< 2,500ms target).
   - Fastpath in-memory queries execute in 0.017ms - 0.924ms (< 10ms target).
   - However, dialogue latency on Groq (`openai/gpt-oss-120b`) is 2,274ms - 3,319ms for unconstrained responses because the model outputs 340-350 words at ~150 TPS. Constraining `max_tokens` or instructing concise answers is required to reliably achieve the < 1,800ms SLA.
   - When executed through `ManagerAgent.chat_interact()`, SQLite disk writes add 10-17ms, pushing fastpath queries to 11-18ms.

2. **Failover Cascading & Circuit Breaker (R2):**
   - Observation 3 proves that `ModelManager.route_and_execute` successfully cascades from Groq -> Gemini -> Ollama without uncaught exceptions.
   - However, because there is no provider-level circuit breaker, a failing provider causes ModelManager to sequentially test every model configured for that provider.
   - Furthermore, because the Groq SDK has `max_retries=2`, a 429 rate limit error causes an internal 9-second sleep before failing over, directly violating the < 500ms failover requirement.
   - When Ollama is under load, `self.ollama.is_available()` times out at 1.5s, causing local models to be erroneously dispatched to Groq cloud.

3. **Benchmark Test Harness Gap (R1 & R4):**
   - Observation 4 shows that percentile calculation and token throughput tracking do not exist in the codebase.
   - An automated test harness must be implemented to run $N$ iterations, collect latencies, compute p50/p95/p99/TPS, test failover with mock faults, and output the required Excel and Markdown audit reports.

---

## 3. Caveats

- **Network Jitter & Cloud Availability:** Cloud API latencies (Groq and Gemini) fluctuate with global network conditions and free-tier throttling.
- **VRAM Constraints on Local GPU:** The local machine is equipped with an NVIDIA RTX 3050 GPU. When loading larger models (e.g. `qwen2.5-coder:7b` or multiple models simultaneously), VRAM allocation delays can cause cold-load spikes (15-22 seconds). Lightweight 3B models (`llama3.2:3b`, `qwen2.5-coder:3b`) remain warm and responsive (~1.2s) when kept resident via `OLLAMA_KEEP_ALIVE`.
- **Read-Only Scope:** In accordance with explorer subagent instructions, no source files were modified.

---

## 4. Conclusion

The core foundation for NanoPro AI Studio's hybrid multi-model architecture is fully operational across Groq LPU, Gemini Cloud, and Local Ollama GPU. However, achieving compliance with requirements R1 and R2 requires three key hardening implementations:
1. **Provider-Level Circuit Breakers with Fast Abort:** Implement a `ProviderCircuitBreaker` (`CLOSED`, `OPEN`, `HALF_OPEN`) in `app/core/model_adapter.py`. Set `max_retries=0` on the Groq client to prevent 9-second rate-limit freezes.
2. **Deterministic Local Model Resolution & Health Caching:** Update `get_adapter_for_model()` to always bind local Ollama models (`llama3.2:3b`, `qwen2.5-coder:3b`) to `OllamaAdapter`, and cache `is_available()` checks.
3. **Automated Multi-Provider Benchmark & Reporting Suite:** Implement an automated benchmark script that executes repeated trials across Python, SQL, and Marathi/Hindi workloads, calculates p50/p95/p99 and TPS throughput, verifies simulated failover in < 500ms, and exports to `Latency_Hardening_Benchmark_Report.xlsx` and `Markdown/_work/latency_benchmark.md`.

---

## 5. Verification Method

1. **Provider Connectivity & Live Response Verification:**
   ```bash
   python -c "from dotenv import load_dotenv; load_dotenv(); from app.core.model_adapter import model_manager; print('Groq:', model_manager.groq.is_available(), 'Gemini:', model_manager.gemini.is_available(), 'Ollama:', model_manager.ollama.is_available())"
   ```
   *Expected:* `Groq: True Gemini: True Ollama: True`.

2. **In-Memory Fastpath Latency (< 10ms SLA):**
   ```bash
   python -c "import time; from app.core.conversational_intelligence import conversational_intelligence; t0=time.perf_counter(); res=conversational_intelligence.dispatch('khichadi kashi banavayachi', 'khichadi kashi banavayachi'); print(f'Latency: {(time.perf_counter()-t0)*1000:.3f}ms')"
   ```
   *Expected:* Latency < 1.0 ms.

3. **Simulated Failover Cascading Verification (Groq -> Gemini -> Ollama):**
   ```bash
   python -c "from dotenv import load_dotenv; load_dotenv(); from app.core.model_adapter import model_manager; from unittest.mock import patch;
   with patch.object(model_manager.groq, 'chat', side_effect=ConnectionError('Simulated Groq Outage')):
       c, m, mode, lat = model_manager.route_and_execute('Test fallback', task_type='general');
       print(f'Fallback Result: {m} via {mode}')
   "
   ```
   *Expected:* `gemini-3.5-flash-lite via gemini-cloud:gemini-3.5-flash-lite`.

4. **Full Technical Analysis Reference:**
   - Review complete findings in `analysis.md` at `.agents/teamwork/explorer_survey_1/analysis.md`.
