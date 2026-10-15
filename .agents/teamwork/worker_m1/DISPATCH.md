## 2026-10-14T18:36:07Z
You are Worker M1 (ModelManager Hardening & Circuit Breaker).

Your mission is to implement Milestone M1 (Features F3, F5, F6, F7, F8, F9) in `app/core/model_adapter.py`.

Exclusive File Ownership:
- You exclusively own: c:\Mangesh\AI video\Mangesh_Nano_Pro_AI_Studio_COMPLETE (34)\Mangesh_Nano_Pro_AI_Studio\app\core\model_adapter.py
- DO NOT touch database or test files owned by other agents.

Implementation Scope & Requirements:
1. ProviderCircuitBreaker Implementation:
   - Add ProviderCircuitBreaker class managing states: CLOSED, OPEN, HALF_OPEN.
   - Track failure counts per provider (groq, gemini, ollama).
   - Immediately trip to OPEN on ConnectionError, Timeout, or HTTP 429 (RateLimitError).
   - can_execute(provider) returns False if provider circuit is OPEN, allowing instant (< 1ms) bypass to next provider in cascade.
   - Half-open cooldown timer (e.g. 30s) to probe recovery.
2. Groq LPU Hardening:
   - Set max_retries=0 when instantiating groq.Groq client to eliminate the 9-second internal backoff sleep on 429 rate limits.
   - In GroqAdapter.chat(), do NOT iterate through 4 models sequentially if the provider network or quota has failed; trip the circuit breaker and raise immediately so ModelManager cascades.
   - Ensure dialogue requests use appropriate max token boundaries to stay within the < 1,800ms SLA.
3. Local Ollama Model Resolution & Health Caching:
   - In get_adapter_for_model(), deterministically map local models (llama3.2:3b, qwen2.5-coder:3b, phi4-mini, gemma3, sqlcoder) to OllamaAdapter.
   - Cache self.ollama.is_available() results with a 15-second TTL so it does not issue a 1.5-second blocking /api/tags HTTP call on every route request.
4. Token Usage & Latency Telemetry:
   - Preserve completion tokens (usage.completion_tokens, usage_metadata.candidates_token_count, or eval_count) in returned response dictionary.
   - Compute tokens_per_second (TPS) and return in telemetry: {"latency_ms": ..., "token_count": ..., "tps": ..., "model": ..., "provider": ...}.
5. Fastpath Latency:
   - Verify conversational fastpath queries respond in < 10ms.
6. Zero-Downtime Failover Verification:
   - Ensure cascading from Groq -> Gemini -> Ollama completes in under 500ms without throwing uncaught exceptions.

Verification Requirement:
- Run unit/integration tests verifying the changes:
  python -m unittest app/tests/test_suite.py
  and a standalone verification script verifying the circuit breaker trips and fails over in < 500ms.
- Document commands and results in your handoff report.

Mandatory Paths:
- Original Request: c:\Mangesh\AI video\Mangesh_Nano_Pro_AI_Studio_COMPLETE (34)\Mangesh_Nano_Pro_AI_Studio\.agents\teamwork\ORIGINAL_REQUEST.md (MANDATORY: read this first!)
- Scope Document: c:\Mangesh\AI video\Mangesh_Nano_Pro_AI_Studio_COMPLETE (34)\Mangesh_Nano_Pro_AI_Studio\PROJECT.md
- Survey Analysis: c:\Mangesh\AI video\Mangesh_Nano_Pro_AI_Studio_COMPLETE (34)\Mangesh_Nano_Pro_AI_Studio\.agents\teamwork\explorer_survey_1\analysis.md
- Your Working Directory: c:\Mangesh\AI video\Mangesh_Nano_Pro_AI_Studio_COMPLETE (34)\Mangesh_Nano_Pro_AI_Studio\.agents\teamwork\worker_m1
- Parent ID: fc9f8196-6923-4e32-92dc-f194b09dba91
