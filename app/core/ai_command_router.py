"""Single AI entry point for the NanoPro OS shell.

One request shape, deterministic intent classification, live system facts, then
exactly one model call (Gemini primary, Groq fallback). Status-shaped questions
are answered from facts alone so they never spend AI quota.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional, Tuple

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.api_auth import require_session

router = APIRouter(prefix="/api/v2", tags=["AICommandRouter"])

INTENTS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("status", ("status", "health", "egress", "bandwidth", "memory", "ram", "alive", "uptime", "down")),
    ("pipelines", ("pipeline", "etl", "bod", "sod", "eod", "t1", "schedule", "cron", "job", "task")),
    ("agents", ("agent", "station", "fleet", "worker", "305")),
    ("data", ("database", "sql", "schema", "table", "bigquery", "duckdb", "neon", "snowflake", "lakehouse")),
    ("comms", ("email", "telegram", "whatsapp", "sms", "mail", "message", "deliver")),
    ("security", ("security", "auth", "login", "access", "secret", "permission")),
)

SYSTEM_PROMPT = (
    "You are the NanoPro OS control-tower assistant. Answer in the language the user wrote in. "
    "Use ONLY the FACTS block; never invent numbers or claim an action ran. "
    "Keep it under 110 words, plain text, no markdown headings. "
    "If the facts do not cover the question, say so in one line and name the module to open."
)


class AskRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


def _scrub(text: str) -> str:
    """Strip keyed URL parameters and bearer tokens before anything is logged."""
    import re

    out = re.sub(r"(key|api_key|token|access_token)=[^&\s\"']+", r"\1=***", text or "")
    return re.sub(r"Bearer\s+[A-Za-z0-9._\-]+", "Bearer ***", out)


def classify_intent(message: str) -> str:
    text = (message or "").lower()
    for name, words in INTENTS:
        if any(word in text for word in words):
            return name
    return "general"


def _collect_facts(intent: str) -> Dict[str, Any]:
    facts: Dict[str, Any] = {
        "platform": {
            "name": "NanoPro OS (NanoPro AI Studio)",
            "what": (
                "One login for autonomous data pipelines, a SQL and data-modeling copilot, "
                "a 320-agent fleet, multi-channel communication (email, Telegram, WhatsApp), "
                "video tooling, payments and live monitoring."
            ),
            "lanes": (
                "The web app and light tasks run on the cloud lane; heavy banking "
                "pipelines run on the owner's laptop lane."
            ),
            "modules": [
                "Pipelines", "Data Modeling", "Infra & Security", "Databases",
                "Agent Station", "Communication", "Video Studio", "Payments",
                "Monitoring", "Signals",
            ],
        }
    }
    try:
        from app.core.runtime_profile import cloud_safe_mode, is_cloud

        facts["lane"] = "cloud" if is_cloud() else "local"
        facts["cloud_safe_mode"] = cloud_safe_mode()
    except Exception:
        pass
    try:
        from app.core.concurrency_guard import concurrency_status

        facts["concurrency"] = concurrency_status()
    except Exception:
        pass
    try:
        from app.core.egress_guard import egress_audit

        audit = egress_audit()
        facts["egress"] = {
            "used_gb": audit.get("used_gb"),
            "limit_gb": audit.get("limit_gb"),
            "verdict": audit.get("verdict"),
            "projected_month_gb": audit.get("projected_month_gb"),
        }
    except Exception:
        pass
    if intent in ("pipelines", "status", "general"):
        try:
            from app.core.database import db

            tasks = db.list_automation_tasks()

            def task_on(t):
                flag = t.get("is_enabled", t.get("enabled"))
                paused = str(t.get("is_paused", "")).lower() in ("1", "true")
                return not paused and str(flag).lower() in ("1", "true")

            enabled = [t for t in tasks if task_on(t)]
            facts["tasks"] = {
                "total": len(tasks),
                "enabled": len(enabled),
                "enabled_names": [t.get("task_name") or t.get("name") for t in enabled][:12],
                "disabled_names": [
                    t.get("task_name") or t.get("name") for t in tasks if not task_on(t)
                ][:12],
            }
        except Exception:
            pass
    if intent in ("agents", "status", "general"):
        try:
            from app.agents.agent_registry import agent_registry

            agents = agent_registry.list_all_agents()
            running = [a for a in agents if a.get("state") in ("Running", "Assigned", "Retrying")]
            facts["agents"] = {
                "total": len(agents),
                "active": len(running),
                "groups": len(agent_registry.get_group_summaries()),
            }
        except Exception:
            pass
    if intent == "data":
        facts["engines"] = ["Neon Postgres (persistent)", "DuckDB (local analytics)", "BigQuery", "Snowflake"]
    if intent == "comms":
        facts["channels"] = ["Email relay", "Telegram bots", "WhatsApp Cloud API"]
    if intent == "security":
        facts["guards"] = [
            "36+ sensitive API prefixes require a session",
            "Admin-only prefixes: /api/admin, /api/vault, /api/backup",
            "Heavy compute is local-lane only on the cloud host",
        ]
    return facts


def _facts_answer(intent: str, facts: Dict[str, Any]) -> str:
    if intent == "status":
        egress = facts.get("egress") or {}
        tasks = facts.get("tasks") or {}
        agents = facts.get("agents") or {}
        conc = facts.get("concurrency") or {}
        return (
            f"Lane: {facts.get('lane', 'unknown')} (safe mode {facts.get('cloud_safe_mode')}). "
            f"Egress {egress.get('used_gb')}/{egress.get('limit_gb')} GB — {egress.get('verdict')}. "
            f"Tasks {tasks.get('enabled')}/{tasks.get('total')} enabled. "
            f"Agents {agents.get('active')}/{agents.get('total')} active. "
            f"AI slots {conc.get('ai_active', 0)}/{conc.get('ai_limit', 0)}."
        )
    return "Facts only: " + ", ".join(f"{k}={v}" for k, v in facts.items() if not isinstance(v, dict))


@router.get("/render")
async def api_v2_render(_user: Dict[str, Any] = Depends(require_session)):
    from app.core.render_status import render_status

    return JSONResponse(render_status())


@router.post("/chat")
async def api_v2_chat(req: AskRequest):
    started = time.time()
    message = (req.message or "").strip()
    if not message:
        return JSONResponse(status_code=422, content={"status": "error", "detail": "message is required"})
    if len(message) > 4000:
        message = message[:4000]

    intent = classify_intent(message)
    facts = _collect_facts(intent)

    if intent == "status":
        return JSONResponse({
            "status": "success",
            "intent": intent,
            "answer": _facts_answer(intent, facts),
            "model": "rules",
            "chain": ["facts-only"],
            "latency_ms": int((time.time() - started) * 1000),
            "facts": facts,
        })

    prompt = (
        f"FACTS:\n{_facts_pretty(facts)}\n\n"
        f"USER QUESTION:\n{message}\n\n"
        "Reply with the answer only."
    )
    answer, model = "", ""
    chain: list = []
    try:
        from app.core.model_adapter import model_manager
    except Exception as exc:
        model_manager = None
        chain.append("import: " + type(exc).__name__)
    if model_manager is not None:
        # One shot per provider in this exact order: Gemini first, Groq second.
        # allow_fallback=False preserves the order because the manager otherwise
        # sorts Groq ahead of Gemini. gemini-3.8-flash is listed by the API but
        # hangs on this key (30s+), so 3.5-flash is the working newest model.
        for candidate in ("gemini-3.5-flash", "openai/gpt-oss-120b"):
            try:
                content, used, _mode = model_manager.execute_with_fallback(
                    prompt,
                    system_prompt=SYSTEM_PROMPT,
                    models=[candidate],
                    # Gemini answers in ~7-9s from the free Render lane, so the
                    # budget leaves headroom while still handing over to Groq.
                    timeout=12.0,
                    allow_fallback=False,
                )
                text = (content or "").strip()
                if text:
                    answer, model = text, used
                    chain.append(candidate + ": ok")
                    break
                chain.append(candidate + ": empty")
            except Exception as exc:
                # Exception type only in the response: provider errors can embed
                # keyed request URLs. The scrubbed detail goes to the server log.
                chain.append(candidate + ": " + type(exc).__name__)
                try:
                    from app.core.logger import log_event

                    log_event(
                        f"AI router: {candidate} failed: {type(exc).__name__}: {_scrub(str(exc))[:160]}",
                        level="WARNING",
                        component="AICommandRouter",
                    )
                except Exception:
                    pass
    if not answer:
        answer = _facts_answer(intent, facts)
        model = "rules"

    return JSONResponse({
        "status": "success",
        "intent": intent,
        "answer": answer,
        "model": model or "unknown",
        "chain": chain,
        "latency_ms": int((time.time() - started) * 1000),
        "facts": facts,
    })


def _facts_pretty(facts: Dict[str, Any]) -> str:
    lines = []
    for key, value in facts.items():
        if isinstance(value, dict):
            inner = ", ".join(f"{k}={v}" for k, v in value.items())
            lines.append(f"- {key}: {inner}")
        elif isinstance(value, list):
            lines.append(f"- {key}: {', '.join(str(v) for v in value)}")
        else:
            lines.append(f"- {key}: {value}")
    return "\n".join(lines)
