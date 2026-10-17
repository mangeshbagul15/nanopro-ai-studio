"""
Mangesh Nano Pro AI Studio - Centralized Multi-Model Intelligent Router
Supports:
1. Groq Ultra-Fast LPU Cloud Inference (openai/gpt-oss-120b, qwen/qwen3.8-27b, openai/gpt-oss-20b) [Sub-second ~500ms - 1.5s]
2. Google Gemini Intelligence Cloud API (gemini-3.5-flash-lite, gemini-3.8-flash, gemini-3.1-flash-lite) [High-Context & Multimodal]
3. Local Ollama GPU Engine (qwen2.5-coder:3b, llama3.2:3b, phi4-mini, gemma3) on NVIDIA RTX 3050 [100% Offline Resilience]
4. Remote API Adapter (OpenAI / Anthropic Compatible)
5. Zero-downtime automatic fallback chains, real-time latency measurement, and health telemetry
"""

import os
import time
import json
import threading
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Tuple, Union
from app.core.config import OLLAMA_HOST, OLLAMA_KEEP_ALIVE, DEFAULT_MODELS_TO_TRY, DEFAULT_METADATA_MODELS
from app.core.logger import log_event

try:
    from google.genai import types as _genai_types
except ImportError:
    _genai_types = None


class CircuitBreakerState:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class ProviderCircuitBreaker:
    """
    High-performance, thread-safe circuit breaker for LLM providers.
    Tracks failure counts and states per provider: 'groq', 'gemini', 'ollama', 'remote'.
    Immediately trips to OPEN (< 1ms) on:
      - ConnectionError / URLError / RemoteDisconnected
      - TimeoutError / socket.timeout
      - HTTP 429 (RateLimitError) / 401 Unauthorized
      - 3 consecutive failures of any kind
    Transitions to HALF_OPEN after recovery_timeout (default 30.0s) to probe recovery.
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0, half_open_success_threshold: Optional[int] = None):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_success_threshold = half_open_success_threshold if half_open_success_threshold is not None else (1 if recovery_timeout < 1.0 else 2)
        self._lock = threading.RLock()
        self._states: Dict[str, str] = {}
        self._failures: Dict[str, int] = {}
        self._last_failure_time: Dict[str, float] = {}
        self._last_errors: Dict[str, str] = {}
        self._half_open_probes: Dict[str, bool] = {}
        self._half_open_successes: Dict[str, int] = {}

    def _normalize(self, provider: str) -> str:
        p = provider.lower()
        if "groq" in p:
            return "groq"
        if "gemini" in p:
            return "gemini"
        if "deepseek" in p:
            return "deepseek"
        if "openrouter" in p:
            return "openrouter"
        if "ollama" in p:
            return "ollama"
        if "remote" in p:
            return "remote"
        return p

    def get_state(self, provider: str) -> str:
        key = self._normalize(provider)
        with self._lock:
            state = self._states.get(key, CircuitBreakerState.CLOSED)
            if state == CircuitBreakerState.OPEN:
                last_time = self._last_failure_time.get(key, 0.0)
                if (time.time() - last_time) >= self.recovery_timeout:
                    self._states[key] = CircuitBreakerState.HALF_OPEN
                    self._half_open_probes[key] = False
                    self._half_open_successes[key] = 0
                    return CircuitBreakerState.HALF_OPEN
            return state

    def can_execute(self, provider: str) -> bool:
        """
        Returns False if provider circuit is OPEN (< 0.01ms check),
        enabling instant bypass to the next provider in the cascade.
        In HALF_OPEN, allows only 1 canary probe request at a time,
        fast-aborting concurrent requests to the next provider.
        """
        key = self._normalize(provider)
        with self._lock:
            state = self.get_state(key)
            if state == CircuitBreakerState.CLOSED:
                return True
            if state == CircuitBreakerState.HALF_OPEN:
                if not self._half_open_probes.get(key, False):
                    self._half_open_probes[key] = True
                    return True
                return False
            return False

    def record_success(self, provider: str) -> None:
        """
        Resets failure counts and restores CLOSED state on successful completion.
        In HALF_OPEN state, requires consecutive successes (2 in production)
        before restoring CLOSED to prevent flapping.
        If state is OPEN, record_success is ignored (cannot close an OPEN breaker directly).
        """
        key = self._normalize(provider)
        with self._lock:
            state = self._states.get(key, CircuitBreakerState.CLOSED)
            if state == CircuitBreakerState.OPEN:
                return
            self._half_open_probes[key] = False
            if state == CircuitBreakerState.HALF_OPEN:
                count = self._half_open_successes.get(key, 0) + 1
                self._half_open_successes[key] = count
                if count >= self.half_open_success_threshold:
                    self._states[key] = CircuitBreakerState.CLOSED
                    self._failures[key] = 0
                    self._half_open_successes[key] = 0
                    self._last_errors.pop(key, None)
            else:
                self._states[key] = CircuitBreakerState.CLOSED
                self._failures[key] = 0
                self._half_open_successes[key] = 0
                self._last_errors.pop(key, None)

    def record_failure(self, provider: str, error: Optional[Exception] = None) -> None:
        """
        Records provider failure. Immediately trips to OPEN on fatal errors:
        HTTP 429 RateLimitError, ConnectionError, TimeoutError, 401 Unauthorized,
        network disconnects/resets, or when failure count reaches failure_threshold.
        """
        key = self._normalize(provider)
        now = time.time()
        err_msg = str(error) if error else "Generic failure"
        err_lower = err_msg.lower()

        is_fast_trip = False
        if error is not None:
            if isinstance(error, (ConnectionError, TimeoutError, urllib.error.URLError)):
                is_fast_trip = True
            elif "429" in err_msg or "rate limit" in err_lower or "rate_limit" in err_lower:
                is_fast_trip = True
            elif any(k in err_lower for k in [
                "connection", "disconnect", "remote", "closed", "reset", "network",
                "timeout", "quota", "unauthorized"
            ]) or any(c in err_msg for c in ["401", "502", "503", "504", "529"]):
                is_fast_trip = True

        with self._lock:
            self._half_open_probes[key] = False
            self._half_open_successes[key] = 0
            count = self._failures.get(key, 0) + 1
            self._failures[key] = count
            self._last_failure_time[key] = now
            self._last_errors[key] = err_msg

            if is_fast_trip or count >= self.failure_threshold:
                self._states[key] = CircuitBreakerState.OPEN
            else:
                if key not in self._states:
                    self._states[key] = CircuitBreakerState.CLOSED

    def trip(self, provider: str, error: Optional[Exception] = None) -> None:
        """Immediately forces a provider circuit to OPEN for testing or fault injection."""
        key = self._normalize(provider)
        with self._lock:
            self._half_open_probes[key] = False
            self._half_open_successes[key] = 0
            self._states[key] = CircuitBreakerState.OPEN
            self._failures[key] = max(self._failures.get(key, 0), self.failure_threshold)
            self._last_failure_time[key] = time.time()
            if error:
                self._last_errors[key] = str(error)

    def reset(self, provider: Optional[str] = None) -> None:
        """Resets circuit breaker for specified provider or all providers."""
        with self._lock:
            if provider:
                key = self._normalize(provider)
                self._states[key] = CircuitBreakerState.CLOSED
                self._failures[key] = 0
                self._half_open_probes[key] = False
                self._half_open_successes[key] = 0
                self._last_errors.pop(key, None)
            else:
                self._states.clear()
                self._failures.clear()
                self._last_failure_time.clear()
                self._last_errors.clear()
                self._half_open_probes.clear()
                self._half_open_successes.clear()

    def get_summary(self) -> Dict[str, Any]:
        with self._lock:
            return {
                p: {
                    "state": self.get_state(p),
                    "failures": self._failures.get(p, 0),
                    "last_error": self._last_errors.get(p, None),
                    "last_failure_time": self._last_failure_time.get(p, 0.0)
                }
                for p in ["groq", "gemini", "ollama", "remote"]
            }


class TelemetryDict(dict):
    """
    Subclass of dict representing response telemetry.
    Supports dictionary access: telemetry['latency_ms'], telemetry['token_count'], telemetry['tps'].
    Returns mode/provider string upon str() for 100% backward compatibility.
    """
    def __str__(self) -> str:
        return self.get("mode", self.get("provider", super().__str__()))


class ModelProviderAdapter:
    """Abstract interface for LLM providers."""
    def is_available(self) -> bool:
        raise NotImplementedError

    def chat(
        self,
        model: str,
        prompt: str,
        schema: Optional[Dict] = None,
        system_prompt: Optional[str] = None,
        timeout: float = 60.0,
        **kwargs
    ) -> Tuple[str, Any]:
        raise NotImplementedError


class GroqAdapter(ModelProviderAdapter):
    """
    Adapter for ultra-fast LPU inference via Groq Cloud API.
    Provides sub-second token generation (~500ms - 1.5s):
    - openai/gpt-oss-120b: 120B Flagship Reasoning, Multilingual (Marathi/Hindi/English), Math & Logic
    - qwen/qwen3.8-27b: 27B State-of-the-Art Code, SQL, and Pipeline Generation
    - openai/gpt-oss-20b: Sub-second conversational responses and quick greetings
    """
    def __init__(self, api_key: Optional[str] = None, circuit_breaker: Optional[ProviderCircuitBreaker] = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self.circuit_breaker = circuit_breaker
        self._client = None

    def is_available(self) -> bool:
        k = self.api_key or os.environ.get("GROQ_API_KEY", "")
        return bool(k and k.startswith("gsk_"))

    def _get_client(self):
        k = self.api_key or os.environ.get("GROQ_API_KEY", "")
        if self._client is None and k:
            import groq
            # max_retries=0 eliminates the internal 9s-34s backoff sleep on 429 rate limits
            self._client = groq.Groq(api_key=k, max_retries=0)
        return self._client

    def chat(
        self,
        model: str,
        prompt: str,
        schema: Optional[Dict] = None,
        system_prompt: Optional[str] = None,
        timeout: float = 30.0,
        **kwargs
    ) -> Tuple[str, Any]:
        if not self.is_available():
            raise ValueError("Groq API Key is not configured. Set GROQ_API_KEY environment variable.")
        
        if self.circuit_breaker and not self.circuit_breaker.can_execute("groq"):
            raise ConnectionError("Groq circuit breaker is OPEN. Fast-aborting request.")

        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        target_model = model
        # Map local model identifiers to optimal Groq equivalents
        if "code" in target_model.lower() or "qwen" in target_model.lower() or "sql" in target_model.lower():
            target_model = "qwen/qwen3.8-27b"
        elif target_model not in ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]:
            target_model = "openai/gpt-oss-120b"

        models_to_try = [target_model, "openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]
        unique_models = []
        for m in models_to_try:
            if m not in unique_models:
                unique_models.append(m)

        # Dialogue requests max token boundary to strictly preserve < 1,800ms SLA
        is_dialogue = "gpt-oss" in target_model.lower() or "dialogue" in str(kwargs.get("task_type", "")).lower()
        default_max_tokens = 768 if is_dialogue else 2048
        max_tokens_val = kwargs.get("max_tokens") or default_max_tokens

        last_err = None
        for m in unique_models:
            t_start = time.time()
            try:
                call_kwargs: Dict[str, Any] = {
                    "model": m,
                    "messages": messages,
                    "temperature": 0.35,
                    "timeout": timeout,
                    "max_tokens": max_tokens_val
                }
                if schema:
                    call_kwargs["response_format"] = {"type": "json_object"}
                resp = client.chat.completions.create(**call_kwargs)
                content = resp.choices[0].message.content.strip()
                if content:
                    dur_sec = max(0.0001, time.time() - t_start)
                    t_dur_ms = max(0.1, round(dur_sec * 1000, 1))
                    token_count = 0
                    if hasattr(resp, "usage") and resp.usage:
                        raw_tc = getattr(resp.usage, "completion_tokens", 0)
                        if isinstance(raw_tc, (int, float)):
                            token_count = int(raw_tc)
                    if token_count <= 0 and content:
                        token_count = max(1, len(content.split()))
                    tps = round(token_count / dur_sec, 2)

                    if self.circuit_breaker:
                        self.circuit_breaker.record_success("groq")

                    telemetry = TelemetryDict({
                        "latency_ms": t_dur_ms,
                        "token_count": token_count,
                        "tps": tps,
                        "model": m,
                        "provider": "groq-lpu",
                        "mode": f"groq-lpu:{m}"
                    })
                    return content, telemetry
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                is_provider_fatal = (
                    isinstance(e, (ConnectionError, TimeoutError, urllib.error.URLError))
                    or "429" in str(e)
                    or "rate limit" in err_str
                    or "rate_limit" in err_str
                    or any(k in err_str for k in ["connection", "disconnect", "remote", "closed", "reset", "network", "timeout", "quota", "unauthorized"])
                    or any(c in str(e) for c in ["401", "502", "503", "504", "529"])
                )
                if self.circuit_breaker:
                    self.circuit_breaker.record_failure("groq", e)
                # On provider-level fatal failures (429 rate limit or network down), do NOT loop through
                # remaining models on Groq; raise immediately so ModelManager cascades without delay.
                if is_provider_fatal:
                    raise e
                continue

        raise RuntimeError(f"Groq LPU execution failed across {unique_models}: {last_err}")


class GeminiAdapter(ModelProviderAdapter):
    """
    Adapter for Google Gemini Cloud Intelligence API.
    Models:
    - gemini-3.5-flash-lite: Ultra-fast multimodal & high-context intelligence (~1.6s)
    - gemini-3.8-flash: Advanced reasoning & deep architectural synthesis
    - gemini-3.1-flash-lite: Resilient fast fallback
    """
    def __init__(self, api_key: Optional[str] = None, circuit_breaker: Optional[ProviderCircuitBreaker] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.circuit_breaker = circuit_breaker
        self._client = None

    def is_available(self) -> bool:
        k = self.api_key or os.environ.get("GEMINI_API_KEY", "")
        return bool(k and len(k) > 20)

    def _get_client(self):
        k = self.api_key or os.environ.get("GEMINI_API_KEY", "")
        if self._client is None and k:
            from google import genai
            self._client = genai.Client(api_key=k)
        return self._client

    def chat(
        self,
        model: str,
        prompt: str,
        schema: Optional[Dict] = None,
        system_prompt: Optional[str] = None,
        timeout: float = 30.0,
        **kwargs
    ) -> Tuple[str, Any]:
        if not self.is_available():
            raise ValueError("Gemini API Key is not configured. Set GEMINI_API_KEY environment variable.")
        
        if self.circuit_breaker and not self.circuit_breaker.can_execute("gemini"):
            raise ConnectionError("Gemini circuit breaker is OPEN. Fast-aborting request.")

        client = self._get_client()
        types = _genai_types

        target_model = "gemini-3.5-flash-lite" if ("gemini" not in model.lower()) else model
        models_to_try = [target_model, "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.8-flash"]
        unique_models = []
        for m in models_to_try:
            if m not in unique_models:
                unique_models.append(m)

        last_err = None
        for m in unique_models:
            t_start = time.time()
            # 1. Preferred Fastpath: models.generate_content
            try:
                cfg_kwargs: Dict[str, Any] = {"temperature": 0.35}
                if system_prompt:
                    cfg_kwargs["system_instruction"] = system_prompt
                if schema:
                    cfg_kwargs["response_mime_type"] = "application/json"
                cfg = types.GenerateContentConfig(**cfg_kwargs)
                resp = client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=cfg
                )
                if resp.text:
                    dur_sec = max(0.0001, time.time() - t_start)
                    t_dur_ms = max(0.1, round(dur_sec * 1000, 1))
                    token_count = 0
                    if hasattr(resp, "usage_metadata") and resp.usage_metadata:
                        raw_tc = getattr(resp.usage_metadata, "candidates_token_count", 0)
                        if isinstance(raw_tc, (int, float)):
                            token_count = int(raw_tc)
                    if token_count <= 0 and resp.text:
                        token_count = max(1, len(resp.text.split()))
                    tps = round(token_count / dur_sec, 2)

                    if self.circuit_breaker:
                        self.circuit_breaker.record_success("gemini")

                    telemetry = TelemetryDict({
                        "latency_ms": t_dur_ms,
                        "token_count": token_count,
                        "tps": tps,
                        "model": m,
                        "provider": "gemini-cloud",
                        "mode": f"gemini-cloud:{m}"
                    })
                    return resp.text.strip(), telemetry
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                is_provider_fatal = (
                    isinstance(e, (ConnectionError, TimeoutError, urllib.error.URLError))
                    or "429" in str(e)
                    or "resource_exhausted" in err_str
                    or "rate limit" in err_str
                    or any(k in err_str for k in ["connection", "disconnect", "remote", "closed", "reset", "network", "timeout", "quota"])
                    or any(c in str(e) for c in ["401", "502", "503", "504", "529"])
                )
                if self.circuit_breaker:
                    self.circuit_breaker.record_failure("gemini", e)
                if is_provider_fatal:
                    raise e

            # 2. Resilient Fallback: interactions.create
            try:
                int_kwargs: Dict[str, Any] = {
                    "model": m,
                    "input": prompt
                }
                if system_prompt:
                    int_kwargs["system_instruction"] = system_prompt
                interaction = client.interactions.create(**int_kwargs)
                if interaction.output_text:
                    dur_sec = max(0.0001, time.time() - t_start)
                    t_dur_ms = max(0.1, round(dur_sec * 1000, 1))
                    token_count = max(1, len(interaction.output_text.split()))
                    tps = round(token_count / dur_sec, 2)

                    if self.circuit_breaker:
                        self.circuit_breaker.record_success("gemini")

                    telemetry = TelemetryDict({
                        "latency_ms": t_dur_ms,
                        "token_count": token_count,
                        "tps": tps,
                        "model": m,
                        "provider": "gemini-cloud",
                        "mode": f"gemini-interactions:{m}"
                    })
                    return interaction.output_text.strip(), telemetry
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                is_provider_fatal = (
                    isinstance(e, (ConnectionError, TimeoutError, urllib.error.URLError))
                    or "429" in str(e)
                    or "resource_exhausted" in err_str
                    or "rate limit" in err_str
                    or any(k in err_str for k in ["connection", "disconnect", "remote", "closed", "reset", "network", "timeout", "quota"])
                    or any(c in str(e) for c in ["401", "502", "503", "504", "529"])
                )
                if self.circuit_breaker:
                    self.circuit_breaker.record_failure("gemini", e)
                if is_provider_fatal:
                    raise e
                continue

        raise RuntimeError(f"Gemini execution failed across models {unique_models}: {last_err}")


class OllamaAdapter(ModelProviderAdapter):
    """Local offline adapter for Ollama on NVIDIA RTX 3050 GPU."""
    def __init__(self, host: str = OLLAMA_HOST, circuit_breaker: Optional[ProviderCircuitBreaker] = None):
        self.host = host.rstrip("/")
        self.circuit_breaker = circuit_breaker
        self._availability_cache: Optional[Tuple[float, bool]] = None
        self._availability_lock = threading.Lock()
        self._availability_ttl: float = 15.0
        self._cached_models: Optional[Tuple[float, List[str]]] = None

    def is_available(self, force_refresh: bool = False) -> bool:
        """
        Cached availability probe with 15-second TTL.
        Prevents blocking the event loop with 1.5s HTTP calls on every route request.
        """
        now = time.time()
        with self._availability_lock:
            if not force_refresh and self._availability_cache is not None:
                cache_time, cached_val = self._availability_cache
                if (now - cache_time) < self._availability_ttl:
                    return cached_val

        try:
            req = urllib.request.Request(f"{self.host}/api/tags", headers={"User-Agent": "MangeshStudio/1.0"})
            with urllib.request.urlopen(req, timeout=0.2) as resp:
                up = (resp.status == 200)
        except Exception:
            up = False

        with self._availability_lock:
            self._availability_cache = (time.time(), up)
        return up

    def list_installed_models(self) -> List[str]:
        now = time.time()
        if self._cached_models and (now - self._cached_models[0] < 60.0):
            return self._cached_models[1]
        if not self.is_available():
            return self._cached_models[1] if self._cached_models else []
        try:
            req = urllib.request.Request(f"{self.host}/api/tags")
            with urllib.request.urlopen(req, timeout=0.2) as resp:
                data = json.loads(resp.read().decode())
                res = [m["name"] for m in data.get("models", [])]
                self._cached_models = (now, res)
                return res
        except Exception:
            return self._cached_models[1] if self._cached_models else []

    def chat(
        self,
        model: str,
        prompt: str,
        schema: Optional[Dict] = None,
        system_prompt: Optional[str] = None,
        timeout: float = 60.0,
        **kwargs
    ) -> Tuple[str, Any]:
        if self.circuit_breaker and not self.circuit_breaker.can_execute("ollama"):
            raise ConnectionError("Ollama circuit breaker is OPEN. Fast-aborting local execution.")

        t_start = time.time()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        is_tiny_greeting = len(prompt.strip()) < 35 and any(w in prompt.lower().split() for w in ["hi", "hello", "hey", "namaskar", "kasa", "kaise", "test"])
        num_tokens = 300 if is_tiny_greeting else 2048
        chat_temp = 0.60 if is_tiny_greeting else 0.35

        scaled_timeout = max(15.0, min(timeout, 90.0))
        if "7b" in model.lower() or "8b" in model.lower() or "4b" in model.lower():
            scaled_timeout = max(scaled_timeout, 45.0)

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": chat_temp,
                "num_ctx": 4096,
                "num_predict": num_tokens,
                "top_p": 0.9,
                "repeat_penalty": 1.05
            },
            "keep_alive": OLLAMA_KEEP_ALIVE
        }
        if schema:
            payload["format"] = schema

        try:
            req = urllib.request.Request(
                f"{self.host}/api/chat",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=scaled_timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                content = result.get("message", {}).get("content", "").strip()
                dur_sec = max(0.0001, time.time() - t_start)
                t_dur_ms = max(0.1, round(dur_sec * 1000, 1))

                token_count = result.get("eval_count", 0) or 0
                if token_count <= 0 and content:
                    token_count = max(1, len(content.split()))

                eval_dur_ns = result.get("eval_duration", 0) or 0
                if eval_dur_ns > 0:
                    tps = round(token_count / (eval_dur_ns / 1e9), 2)
                else:
                    tps = round(token_count / dur_sec, 2)

                with self._availability_lock:
                    self._availability_cache = (time.time(), True)
                if self.circuit_breaker:
                    self.circuit_breaker.record_success("ollama")

                telemetry = TelemetryDict({
                    "latency_ms": t_dur_ms,
                    "token_count": token_count,
                    "tps": tps,
                    "model": model,
                    "provider": "ollama",
                    "mode": "ollama-http"
                })
                return content, telemetry
        except urllib.error.URLError as e:
            with self._availability_lock:
                self._availability_cache = (time.time(), False)
            if self.circuit_breaker:
                self.circuit_breaker.record_failure("ollama", e)
            raise ConnectionError(f"Ollama connection error at {self.host}: {str(e)}")
        except Exception as e:
            if self.circuit_breaker:
                self.circuit_breaker.record_failure("ollama", e)
            raise RuntimeError(f"Ollama execution error: {str(e)}")

class DeepSeekAdapter(ModelProviderAdapter):
    """
    Adapter for DeepSeek Super-Intelligence & Reasoning API.
    Provides OpenAI-compatible inference with:
    - deepseek-chat: DeepSeek-V3 ultra-fast flagship reasoning, code & multilingual (Marathi/Hindi/English)
    - deepseek-reasoner: DeepSeek-R1 state-of-the-art chain-of-thought reasoning, mathematics, logic & debugging
    """
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, circuit_breaker: Optional[ProviderCircuitBreaker] = None):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY", "")
        self.base_url = (base_url or os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")).rstrip("/")
        self.circuit_breaker = circuit_breaker

    def is_available(self) -> bool:
        k = self.api_key or os.environ.get("DEEPSEEK_API_KEY", "")
        return bool(k and k.startswith("sk-"))

    def chat(
        self,
        model: str,
        prompt: str,
        schema: Optional[Dict] = None,
        system_prompt: Optional[str] = None,
        timeout: float = 60.0,
        **kwargs
    ) -> Tuple[str, Any]:
        k = self.api_key or os.environ.get("DEEPSEEK_API_KEY", "")
        if not k:
            raise ValueError("DeepSeek API Key is not configured. Set DEEPSEEK_API_KEY environment variable.")

        if self.circuit_breaker and not self.circuit_breaker.can_execute("deepseek"):
            raise ConnectionError("DeepSeek API circuit breaker is OPEN. Fast-aborting request.")

        t_start = time.time()
        m_clean = model if model in ["deepseek-chat", "deepseek-reasoner"] else "deepseek-chat"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": m_clean,
            "messages": messages,
            "stream": False
        }
        if m_clean != "deepseek-reasoner":
            payload["temperature"] = 0.3
        if schema:
            payload["response_format"] = {"type": "json_object"}

        try:
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {k}"
                }
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                choice = data["choices"][0]
                content = choice.get("message", {}).get("content", "") or ""
                content = content.strip()
                reasoning = choice.get("message", {}).get("reasoning_content", "") or ""
                if reasoning and not content:
                    content = reasoning.strip()

                dur_sec = max(0.0001, time.time() - t_start)
                t_dur_ms = max(0.1, round(dur_sec * 1000, 1))
                token_count = data.get("usage", {}).get("completion_tokens", 0) or 0
                if token_count <= 0 and content:
                    token_count = max(1, len(content.split()))
                tps = round(token_count / dur_sec, 2)

                if self.circuit_breaker:
                    self.circuit_breaker.record_success("deepseek")

                telemetry = TelemetryDict({
                    "latency_ms": t_dur_ms,
                    "token_count": token_count,
                    "tps": tps,
                    "model": m_clean,
                    "provider": "deepseek",
                    "mode": "deepseek-cloud"
                })
                return content, telemetry
        except Exception as e:
            if self.circuit_breaker:
                self.circuit_breaker.record_failure("deepseek", e)
            raise e


class RemoteAPIAdapter(ModelProviderAdapter):
    """Adapter for standard OpenAI / Anthropic compatible remote endpoints."""
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, circuit_breaker: Optional[ProviderCircuitBreaker] = None):
        self.api_key = api_key or os.environ.get("AI_STUDIO_API_KEY", "")
        self.base_url = (base_url or os.environ.get("AI_STUDIO_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.circuit_breaker = circuit_breaker

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(
        self,
        model: str,
        prompt: str,
        schema: Optional[Dict] = None,
        system_prompt: Optional[str] = None,
        timeout: float = 60.0,
        **kwargs
    ) -> Tuple[str, Any]:
        if not self.is_available():
            raise ValueError("Remote API Key is not configured. Set AI_STUDIO_API_KEY environment variable.")
        
        if self.circuit_breaker and not self.circuit_breaker.can_execute("remote"):
            raise ConnectionError("Remote API circuit breaker is OPEN. Fast-aborting request.")

        t_start = time.time()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model or "gpt-4o-mini",
            "messages": messages,
            "temperature": 0.25
        }
        if schema:
            payload["response_format"] = {"type": "json_object"}

        try:
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"].strip()
                dur_sec = max(0.0001, time.time() - t_start)
                t_dur_ms = max(0.1, round(dur_sec * 1000, 1))
                token_count = data.get("usage", {}).get("completion_tokens", 0) or 0
                if token_count <= 0 and content:
                    token_count = max(1, len(content.split()))
                tps = round(token_count / dur_sec, 2)

                if self.circuit_breaker:
                    self.circuit_breaker.record_success("remote")

                telemetry = TelemetryDict({
                    "latency_ms": t_dur_ms,
                    "token_count": token_count,
                    "tps": tps,
                    "model": model or "remote-api",
                    "provider": "remote",
                    "mode": "remote-api"
                })
                return content, telemetry
        except Exception as e:
            if self.circuit_breaker:
                self.circuit_breaker.record_failure("remote", e)
            raise e


class OpenRouterAdapter(ModelProviderAdapter):
    """
    Adapter for OpenRouter Multi-Model Cloud API (Aggregates 400+ frontier & open-source AI models).
    Provides access to Llama 3.3, Qwen 2.5, Nemotron, Mistral, and Claude/GPT fallback models.
    """
    def __init__(self, api_key: Optional[str] = None, circuit_breaker: Optional[ProviderCircuitBreaker] = None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.base_url = "https://openrouter.ai/api/v1"
        self.circuit_breaker = circuit_breaker

    def is_available(self) -> bool:
        k = self.api_key or os.environ.get("OPENROUTER_API_KEY", "")
        return bool(k and k.startswith("sk-or-"))

    def chat(
        self,
        model: str,
        prompt: str,
        schema: Optional[Dict] = None,
        system_prompt: Optional[str] = None,
        timeout: float = 60.0,
        **kwargs
    ) -> Tuple[str, Any]:
        k = self.api_key or os.environ.get("OPENROUTER_API_KEY", "")
        if not k:
            raise ValueError("OpenRouter API Key is not configured. Set OPENROUTER_API_KEY environment variable.")

        if self.circuit_breaker and not self.circuit_breaker.can_execute("openrouter"):
            raise ConnectionError("OpenRouter API circuit breaker is OPEN. Fast-aborting request.")

        t_start = time.time()
        m_clean = model if model and ("/" in model or ":free" in model) else "liquid/lfm-2.5-2.6b:free"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": m_clean,
            "messages": messages
        }
        if schema:
            payload["response_format"] = {"type": "json_object"}

        try:
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {k}",
                    "HTTP-Referer": "https://nanopro-ai-studio.onrender.com",
                    "X-Title": "NanoPro AI Studio"
                }
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"] or ""
                content = content.strip()

                dur_sec = max(0.0001, time.time() - t_start)
                t_dur_ms = max(0.1, round(dur_sec * 1000, 1))
                token_count = data.get("usage", {}).get("completion_tokens", 0) or 0
                if token_count <= 0 and content:
                    token_count = max(1, len(content.split()))
                tps = round(token_count / dur_sec, 2)

                if self.circuit_breaker:
                    self.circuit_breaker.record_success("openrouter")

                telemetry = TelemetryDict({
                    "latency_ms": t_dur_ms,
                    "token_count": token_count,
                    "tps": tps,
                    "model": m_clean,
                    "provider": "openrouter",
                    "mode": "openrouter-cloud"
                })
                return content, telemetry
        except Exception as e:
            if self.circuit_breaker:
                self.circuit_breaker.record_failure("openrouter", e)
            raise e


class ModelManager:
    """
    Centralized Multi-Model Intelligent Router for Mangesh Nano Pro AI Studio.
    Provides sub-second LPU execution (Groq), deep cloud intelligence (Gemini),
    and 100% offline local GPU execution (Ollama) with zero-downtime failover (< 500ms).
    """
    def __init__(self):
        self.circuit_breaker = ProviderCircuitBreaker()
        self.groq = GroqAdapter(circuit_breaker=self.circuit_breaker)
        self.gemini = GeminiAdapter(circuit_breaker=self.circuit_breaker)
        self.deepseek = DeepSeekAdapter(circuit_breaker=self.circuit_breaker)
        self.openrouter = OpenRouterAdapter(circuit_breaker=self.circuit_breaker)
        self.ollama = OllamaAdapter(circuit_breaker=self.circuit_breaker)
        self.remote = RemoteAPIAdapter(circuit_breaker=self.circuit_breaker)

        # Task-specific capability routing hierarchy
        self.task_routing: Dict[str, List[str]] = {
            "coding": ["deepseek-chat", "deepseek-reasoner", "qwen/qwen3.8-27b", "gemini-3.5-flash-lite", "qwen2.5-coder:3b", "qwen2.5-coder:7b", "phi4-mini:latest"],
            "dialogue": ["deepseek-chat", "openai/gpt-oss-120b", "gemini-3.5-flash-lite", "openai/gpt-oss-20b", "llama3.2:3b", "qwen2.5-coder:3b"],
            "data_analyst": ["deepseek-reasoner", "gemini-3.5-flash-lite", "openai/gpt-oss-120b", "qwen/qwen3.8-27b", "phi4-mini:latest"],
            "research": ["deepseek-reasoner", "gemini-3.5-flash-lite", "openai/gpt-oss-120b", "gemma3:4b", "llama3.2:3b"],
            "price_tracking": ["openai/gpt-oss-120b", "gemini-3.5-flash-lite", "phi4-mini:latest"],
            "learning": ["deepseek-chat", "gemini-3.5-flash-lite", "openai/gpt-oss-120b", "qwen/qwen3.8-27b"],
            "general": ["deepseek-chat", "openai/gpt-oss-120b", "gemini-3.5-flash-lite", "qwen/qwen3.8-27b", "llama3.2:3b", "qwen2.5-coder:3b"]
        }

        # Model metadata registry
        self.model_metadata: Dict[str, Dict[str, Any]] = {
            "deepseek-chat": {"role": "DeepSeek-V3 Flagship Coding & Intelligence", "vram_mb": 0, "strength": "Ultra-Fast Reasoning & Multi-language Code (~1.1s)"},
            "deepseek-reasoner": {"role": "DeepSeek-R1 Chain-of-Thought Reasoning Engine", "vram_mb": 0, "strength": "State-of-the-Art Deep Logic & Math (~2.2s)"},
            "openrouter/free": {"role": "OpenRouter 400+ Multi-Model Cloud Aggregator", "vram_mb": 0, "strength": "Instant Access to 400+ Frontier Models (~1.5s)"},
            "openai/gpt-oss-120b": {"role": "Flagship 120B Reasoning & Multilingual (Groq LPU)", "vram_mb": 0, "strength": "State-of-the-Art Reasoning (Sub-2s)"},
            "qwen/qwen3.8-27b": {"role": "LPU Ultra-Fast Code & SQL Engine (Groq LPU)", "vram_mb": 0, "strength": "Sub-Second Code Generation (~500ms)"},
            "openai/gpt-oss-20b": {"role": "Lightning Conversational Dialogue (Groq LPU)", "vram_mb": 0, "strength": "Sub-Second Natural Chat (~700ms)"},
            "gemini-3.5-flash-lite": {"role": "Google Gemini Cloud Intelligence", "vram_mb": 0, "strength": "Multimodal, Deep Context & Marathi Nuance (~1.6s)"},
            "gemini-3.8-flash": {"role": "Google Gemini Cloud Reasoning", "vram_mb": 0, "strength": "Deep Logical Reasoning & Architecture"},
            "qwen2.5-coder:3b": {"role": "Primary Local Coder & ETL", "vram_mb": 1900, "strength": "Fast Offline Code & SQL"},
            "qwen2.5-coder:7b": {"role": "Advanced Local Coder", "vram_mb": 4700, "strength": "Complex Offline Architecture"},
            "llama3.2:3b": {"role": "Local Dialogue & Assistant", "vram_mb": 2000, "strength": "Offline Conversational Logic"},
            "phi4-mini:latest": {"role": "Local Math & Structured JSON", "vram_mb": 2500, "strength": "Data Profiling & Extraction"},
            "gemma3:4b": {"role": "Local Knowledge & Research", "vram_mb": 3400, "strength": "Synthesis & Information Retrieval"}
        }

        self.selected_model: Optional[str] = None
        self._telemetry_lock = threading.Lock()

        # Telemetry metrics per model
        self.telemetry: Dict[str, Dict[str, Any]] = {}
        for m in self.model_metadata.keys():
            self._init_model_telemetry(m)

    def _init_model_telemetry(self, model: str):
        with self._telemetry_lock:
            if model not in self.telemetry:
                self.telemetry[model] = {
                    "total_calls": 0,
                    "success_count": 0,
                    "error_count": 0,
                    "avg_latency_ms": 0.0,
                    "last_latency_ms": 0.0,
                    "last_token_count": 0,
                    "last_tps": 0.0,
                    "last_status": "Ready",
                    "last_used_at": None,
                    "last_error": None
                }

    def set_primary_model(self, model_name: str) -> Dict[str, Any]:
        """Manually switches the primary AI model used across NanoPro Studio."""
        self.selected_model = model_name
        self._init_model_telemetry(model_name)
        log_event(f"Active model manually switched to: {model_name}", component="ModelRouter")
        return {"status": "success", "active_model": model_name}

    def get_primary_model(self) -> str:
        if self.selected_model:
            return self.selected_model
        if self.groq.is_available() and self.circuit_breaker.can_execute("groq"):
            return "openai/gpt-oss-120b"
        if self.gemini.is_available() and self.circuit_breaker.can_execute("gemini"):
            return "gemini-3.5-flash-lite"
        eff = self.get_effective_model_list()
        return eff[0] if eff else "qwen2.5-coder:3b"

    def get_adapter_for_model(self, model: str) -> Tuple[ModelProviderAdapter, str]:
        """
        Deterministically selects the exact provider adapter based on model identifier.
        Local models (llama3.2:3b, qwen2.5-coder:3b, phi4-mini, gemma3, sqlcoder)
        deterministically map to OllamaAdapter without cloud misrouting.
        """
        m_lower = model.lower()

        # 1. Deterministic Groq Cloud LPU models
        if "gpt-oss" in m_lower or "qwen3.8" in m_lower or "groq" in m_lower:
            return self.groq, "groq-lpu"

        # 2. Deterministic Google Gemini Cloud models
        if "gemini" in m_lower:
            return self.gemini, "gemini-cloud"

        # 3. Deterministic DeepSeek Cloud models (deepseek-chat, deepseek-reasoner)
        if ("deepseek-chat" in m_lower or "deepseek-reasoner" in m_lower or m_lower.startswith("deepseek/")):
            if self.deepseek.is_available() and self.circuit_breaker.can_execute("deepseek"):
                return self.deepseek, "deepseek-cloud"

        # 4. OpenRouter Cloud models (or explicit models with :free tag, or openrouter prefix)
        if "openrouter" in m_lower or (self.openrouter.is_available() and ":free" in m_lower):
            if self.openrouter.is_available() and self.circuit_breaker.can_execute("openrouter"):
                return self.openrouter, "openrouter-cloud"

        # 5. Deterministic Local Ollama models
        is_local = (
            ":" in model
            or any(m_lower.startswith(p) for p in ["llama", "qwen2", "phi", "gemma", "sqlcoder", "deepseek", "mistral", "codellama"])
            or any(k in m_lower for k in ["llama3.2", "qwen2.5", "phi4-mini", "gemma3", "sqlcoder"])
        )
        if is_local:
            return self.ollama, "ollama"

        # 6. Fallback based on availability & circuit breaker for unknown/custom model names
        if self.deepseek.is_available() and self.circuit_breaker.can_execute("deepseek"):
            return self.deepseek, "deepseek-cloud"
        if self.openrouter.is_available() and self.circuit_breaker.can_execute("openrouter"):
            return self.openrouter, "openrouter-cloud"
        if self.groq.is_available() and self.circuit_breaker.can_execute("groq"):
            return self.groq, "groq-lpu"
        if self.gemini.is_available() and self.circuit_breaker.can_execute("gemini"):
            return self.gemini, "gemini-cloud"
        if self.ollama.is_available() and self.circuit_breaker.can_execute("ollama"):
            return self.ollama, "ollama"
        if self.remote.is_available() and self.circuit_breaker.can_execute("remote"):
            return self.remote, "remote"

        return self.ollama, "ollama-offline"

    def get_preferred_adapter(self) -> Tuple[ModelProviderAdapter, str]:
        if self.deepseek.is_available() and self.circuit_breaker.can_execute("deepseek"):
            return self.deepseek, "deepseek-cloud"
        if self.openrouter.is_available() and self.circuit_breaker.can_execute("openrouter"):
            return self.openrouter, "openrouter-cloud"
        if self.groq.is_available() and self.circuit_breaker.can_execute("groq"):
            return self.groq, "groq-lpu"
        if self.gemini.is_available() and self.circuit_breaker.can_execute("gemini"):
            return self.gemini, "gemini-cloud"
        if self.ollama.is_available() and self.circuit_breaker.can_execute("ollama"):
            return self.ollama, "ollama"
        if self.remote.is_available() and self.circuit_breaker.can_execute("remote"):
            return self.remote, "remote"
        return self.ollama, "ollama-offline"

    def get_effective_model_list(self, requested_models: Optional[List[str]] = None, task_type: str = "general") -> List[str]:
        """
        Determines the priority order of models based on cloud API credentials,
        installed Ollama models, and task category.
        Prioritizes 3B / low-latency models for local RTX 3050 VRAM constraints.
        """
        base_list = requested_models or self.task_routing.get(task_type, self.task_routing["general"])
        effective = []

        # 1. Include DeepSeek models if available and circuit not OPEN
        if self.deepseek.is_available() and self.circuit_breaker.can_execute("deepseek"):
            for m in base_list:
                if "deepseek" in m and m not in effective:
                    effective.append(m)

        # 2. Include Groq models if available and circuit not OPEN
        if self.groq.is_available() and self.circuit_breaker.can_execute("groq"):
            for m in base_list:
                if ("gpt-oss" in m or "qwen3.8" in m) and m not in effective:
                    effective.append(m)

        # 3. Include Gemini models if available and circuit not OPEN
        if self.gemini.is_available() and self.circuit_breaker.can_execute("gemini"):
            for m in base_list:
                if "gemini" in m and m not in effective:
                    effective.append(m)

        # 4. Include OpenRouter models if available and circuit not OPEN
        if self.openrouter.is_available() and self.circuit_breaker.can_execute("openrouter"):
            for m in base_list:
                if ("openrouter" in m or ":free" in m) and m not in effective:
                    effective.append(m)

        # 3. Include installed Ollama models from cache without blocking failover cascade
        installed = self.ollama._cached_models[1] if (self.ollama._cached_models and (time.time() - self.ollama._cached_models[0] < 60.0)) else []
        if installed:
            matched_installed = []
            for req in base_list:
                req_clean = req.split(":")[0]
                for inst in installed:
                    if (req == inst or req_clean in inst) and inst not in matched_installed:
                        matched_installed.append(inst)

            # Sort matched installed with 3b / smaller models first for local RTX 3050 VRAM optimization
            def _local_vram_priority(name: str) -> int:
                n = name.lower()
                if "1b" in n: return 1
                if "3b" in n or "mini" in n: return 2
                if "4b" in n: return 3
                if "7b" in n or "8b" in n: return 4
                return 5

            matched_installed.sort(key=_local_vram_priority)

            for inst in matched_installed:
                if inst not in effective:
                    effective.append(inst)

            for inst in installed:
                if inst not in effective and not any(k in inst for k in ["embed"]):
                    effective.append(inst)

        # 4. Always ensure offline fallback candidates from base_list are present
        local_candidates = []
        for req in base_list:
            req_lower = req.lower()
            is_local = (
                ":" in req
                or any(req_lower.startswith(p) for p in ["llama", "qwen2", "phi", "gemma", "sqlcoder"])
                or any(k in req_lower for k in ["llama3.2", "qwen2.5", "phi4-mini", "gemma3", "sqlcoder"])
            ) and not ("qwen3.8" in req_lower or "gpt-oss" in req_lower or "gemini" in req_lower)
            if is_local and req not in effective and req not in local_candidates:
                local_candidates.append(req)

        def _vram_priority(name: str) -> int:
            n = name.lower()
            if "1b" in n: return 1
            if "3b" in n or "mini" in n: return 2
            if "4b" in n: return 3
            if "7b" in n or "8b" in n: return 4
            return 5

        local_candidates.sort(key=_vram_priority)
        for cand in local_candidates:
            effective.append(cand)

        # Fallback to base list if empty
        if not effective:
            effective = list(base_list)

        if self.selected_model and not requested_models:
            res_copy = [m for m in effective if m != self.selected_model]
            res_copy.insert(0, self.selected_model)
            return res_copy
        return effective

    def route_and_execute(
        self,
        prompt: str,
        task_type: str = "general",
        schema: Optional[Dict] = None,
        system_prompt: Optional[str] = None,
        timeout: float = 60.0,
        models: Optional[List[str]] = None,
        **kwargs
    ) -> Tuple[str, str, Any, float]:
        """
        Intelligently routes task to best-matched model, measures latency,
        and provides zero-downtime automatic fallback across Groq, Gemini, and Ollama.
        Cascades Groq -> Gemini -> Ollama in < 500ms without uncaught exceptions.
        Returns: (content, model_used, provider_mode_or_telemetry, latency_ms)
        """
        if not models and "model" in kwargs:
            models = [kwargs["model"]]

        model_list = self.get_effective_model_list(requested_models=models, task_type=task_type)
        last_error = ""
        failed_providers_this_call = set()

        for model in model_list:
            adapter, provider_type = self.get_adapter_for_model(model)
            norm_prov = self.circuit_breaker._normalize(provider_type)

            # 1. Fast circuit breaker check (< 0.01ms): bypass OPEN providers instantly
            if not self.circuit_breaker.can_execute(norm_prov):
                log_event(
                    f"ModelRouter: Circuit breaker OPEN for [{norm_prov}]. Bypassing [{model}] (< 0.01ms)",
                    level="INFO", component="ModelRouter"
                )
                continue

            # 2. Skip if this provider already failed during the current cascading call
            if norm_prov in failed_providers_this_call:
                continue

            # 3. Check adapter availability (Ollama uses 15s cached probe)
            if not adapter.is_available():
                continue

            self._init_model_telemetry(model)
            t_start = time.time()
            try:
                log_event(f"ModelRouter: Routing [{task_type}] task to [{model}] via [{provider_type}]...", component="ModelRouter")
                chat_kwargs = dict(kwargs)
                chat_kwargs.pop("model", None)
                content, mode = adapter.chat(
                    model,
                    prompt,
                    schema=schema,
                    system_prompt=system_prompt,
                    timeout=timeout,
                    task_type=task_type,
                    **chat_kwargs
                )
                t_dur_ms = max(0.1, round((time.time() - t_start) * 1000, 1))

                if content:
                    self.circuit_breaker.record_success(norm_prov)
                    with self._telemetry_lock:
                        if model not in self.telemetry:
                            self.telemetry[model] = {
                                "total_calls": 0, "success_count": 0, "error_count": 0,
                                "avg_latency_ms": 0.0, "last_latency_ms": 0.0,
                                "last_token_count": 0, "last_tps": 0.0,
                                "last_status": "Ready", "last_used_at": None, "last_error": None
                            }
                        stat = self.telemetry[model]
                        stat["total_calls"] += 1
                        stat["success_count"] += 1
                        stat["last_latency_ms"] = t_dur_ms
                        stat["avg_latency_ms"] = round((stat["avg_latency_ms"] * (stat["success_count"] - 1) + t_dur_ms) / stat["success_count"], 1)
                        stat["last_status"] = "Success"
                        stat["last_used_at"] = time.time()

                        if isinstance(mode, dict):
                            stat["last_token_count"] = mode.get("token_count", 0)
                            stat["last_tps"] = mode.get("tps", 0.0)

                    log_event(f"ModelRouter: Success with [{model}] in {t_dur_ms}ms ({mode})", component="ModelRouter")
                    return content, model, mode, t_dur_ms

            except Exception as e:
                t_dur_ms = max(0.1, round((time.time() - t_start) * 1000, 1))
                last_error = str(e)
                failed_providers_this_call.add(norm_prov)
                self.circuit_breaker.record_failure(norm_prov, e)

                with self._telemetry_lock:
                    if model not in self.telemetry:
                        self.telemetry[model] = {
                            "total_calls": 0, "success_count": 0, "error_count": 0,
                            "avg_latency_ms": 0.0, "last_latency_ms": 0.0,
                            "last_token_count": 0, "last_tps": 0.0,
                            "last_status": "Ready", "last_used_at": None, "last_error": None
                        }
                    stat = self.telemetry[model]
                    stat["total_calls"] += 1
                    stat["error_count"] += 1
                    stat["last_latency_ms"] = t_dur_ms
                    stat["last_status"] = "Failed"
                    stat["last_error"] = last_error
                log_event(
                    f"ModelRouter: Model [{model}] failed ({last_error}). Cascading to next provider candidate...",
                    level="WARNING", component="ModelRouter"
                )

        raise RuntimeError(f"All routed model candidates exhausted for [{task_type}]. Last error: {last_error}")

    def execute_with_fallback(
        self,
        prompt: str,
        schema: Optional[Dict] = None,
        system_prompt: Optional[str] = None,
        models: List[str] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Tuple[str, str, Any]:
        """Backward-compatible wrapper for execute_with_fallback."""
        is_code = any(k in prompt.lower() for k in ["python", "sql", "code", "syntax", "function", "pipeline", "etl"])
        task = "coding" if is_code else "dialogue"
        eff_timeout = timeout if timeout is not None else 15.0
        content, model, mode, _ = self.route_and_execute(
            prompt,
            task_type=task,
            schema=schema,
            system_prompt=system_prompt,
            timeout=eff_timeout,
            models=models,
            **kwargs
        )
        return content, model, mode

    def get_router_telemetry(self) -> Dict[str, Any]:
        """Returns real-time performance, availability, circuit breaker, and routing statistics."""
        installed = self.ollama.list_installed_models()
        is_ollama_up = self.ollama.is_available()
        is_groq_up = self.groq.is_available()
        is_gemini_up = self.gemini.is_available()

        models_status = []
        with self._telemetry_lock:
            telemetry_snapshot = {m: dict(stats) for m, stats in self.telemetry.items()}

        for m, meta in self.model_metadata.items():
            t = telemetry_snapshot.get(m, {})
            if "gpt-oss" in m or "qwen3.8" in m:
                status = "Online (Groq LPU Cloud)" if is_groq_up else "API Key Required"
                installed_flag = is_groq_up
            elif "gemini" in m:
                status = "Online (Gemini Cloud API)" if is_gemini_up else "API Key Required"
                installed_flag = is_gemini_up
            else:
                is_inst = m in installed or any(m.split(":")[0] in inst for inst in installed)
                status = "Online (Local GPU)" if (is_ollama_up and is_inst) else ("Installed (Service Offline)" if is_inst else "Not Installed")
                installed_flag = is_inst

            models_status.append({
                "model_name": m,
                "role": meta["role"],
                "strength": meta["strength"],
                "vram_mb": meta["vram_mb"],
                "installed": installed_flag,
                "status": status,
                "total_calls": t.get("total_calls", 0),
                "success_count": t.get("success_count", 0),
                "error_count": t.get("error_count", 0),
                "avg_latency_ms": t.get("avg_latency_ms", 0.0),
                "last_latency_ms": t.get("last_latency_ms", 0.0),
                "last_token_count": t.get("last_token_count", 0),
                "last_tps": t.get("last_tps", 0.0)
            })

        return {
            "groq_lpu_connected": is_groq_up,
            "gemini_cloud_connected": is_gemini_up,
            "ollama_connected": is_ollama_up,
            "ollama_host": self.ollama.host,
            "installed_models_count": len(installed),
            "circuit_breaker": self.circuit_breaker.get_summary(),
            "task_routing_map": self.task_routing,
            "models": models_status
        }

    def benchmark_model(self, model_name: str) -> Dict[str, Any]:
        """Benchmarks an individual model for real-time responsiveness."""
        t_start = time.time()
        adapter, mode = self.get_adapter_for_model(model_name)
        try:
            prompt = "Return exactly: Operational check passed."
            content, pmode = adapter.chat(model_name, prompt, timeout=15.0)
            dur_ms = round((time.time() - t_start) * 1000, 1)
            token_count = pmode.get("token_count", len(content.split())) if isinstance(pmode, dict) else len(content.split())
            tps = pmode.get("tps", 0.0) if isinstance(pmode, dict) else round(token_count / (dur_ms / 1000.0), 2)
            return {
                "status": "success",
                "model": model_name,
                "latency_ms": dur_ms,
                "token_count": token_count,
                "tps": tps,
                "response": content[:80],
                "mode": str(pmode)
            }
        except Exception as e:
            dur_ms = round((time.time() - t_start) * 1000, 1)
            return {
                "status": "failed",
                "model": model_name,
                "latency_ms": dur_ms,
                "error": str(e)
            }


model_manager = ModelManager()
provider_circuit_breaker = model_manager.circuit_breaker
