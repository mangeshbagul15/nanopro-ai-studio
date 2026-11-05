"""Versioned delivery contract and self-check suite for the NanoPro data manager.

The chat manager is not fine-tuned; it is steered by a written contract plus a
golden requirement set. `run_selfcheck(live=True)` proves the live model still
honours that contract before a release.
"""

import re
import time
from typing import Any, Dict, List

CONTRACT_VERSION = "2026.11.06"

# Appended verbatim to the manager system prompt.
DELIVERY_CONTRACT = (
    "DELIVERY CONTRACT " + CONTRACT_VERSION + " (must hold on every turn):\n"
    "A. Understand the request in English, Marathi or Hinglish, including mixed spellings and voice-style text.\n"
    "B. Deliver a complete answer or action in ONE turn: state the target database, write the statement, explain the outcome briefly.\n"
    "C. Cover, without the user writing SQL: schema/table/column work, datatype changes, top-N queries, joins on real PK/FK, "
    "append/ingest, ETL pipelines, and scheduling (once/daily/weekly/monthly/quarterly/adhoc/cron/SOD/BOD/EOD).\n"
    "D. Ground every identifier in the live catalog. If something is missing or unreachable, say so with the real error; never invent data.\n"
    "E. Respect dialect per engine (Snowflake, PostgreSQL, MySQL, Oracle, BigQuery, DuckDB/S3, SQLite).\n"
    "F. Refuse DROP/DELETE/TRUNCATE/ATTACH/GRANT and unrequested destructive work, then offer a safe alternative.\n"
    "G. Keep `reply` under 120 words, in the user's language, and put SQL only in `sql`.\n"
)

_GOLDEN_FAST: List[Dict[str, Any]] = [
    {"id": "greet", "prompt": "hello", "check": "reply", "pattern": r"Namaskar"},
    {"id": "help", "prompt": "help", "check": "reply", "pattern": r"(join|schedule)"},
    {"id": "list-db", "prompt": "list databases", "check": "reply", "pattern": r"(live database|none)"},
    {"id": "list-tables", "prompt": "list tables", "check": "reply", "pattern": r"table"},
]

_GOLDEN_LIVE: List[Dict[str, Any]] = [
    {"id": "create-table", "prompt": "Create a table sales_demo with id INTEGER PRIMARY KEY, customer TEXT, amount REAL and show it.",
     "check": "sql", "pattern": r"create\s+table\s+(?:if\s+not\s+exists\s+)?\w*sales_demo",
     "alt_reply": r"(already exists|आधीच|आधीच तयार)"},
    {"id": "add-column", "prompt": "Add a column email TEXT to sales_demo.",
     "check": "sql", "pattern": r"alter\s+table\s+\S+\s+add\s+column\s+email"},
    {"id": "rename-column", "prompt": "Rename column customer to customer_name in sales_demo.",
     "check": "sql", "pattern": r"rename\s+column\s+customer\s+to\s+customer_name"},
    {"id": "change-type", "prompt": "Change the datatype of the customer column in sales_demo to VARCHAR(120).",
     "check": "sql", "pattern": r"(alter\s+column\s+customer|modify\s+column\s+customer)"},
    {"id": "top-n", "prompt": "Show the top 5 rows of sales_demo by amount.",
     "check": "sql", "pattern": r"(limit\s+5|fetch\s+first\s+5)"},
    {"id": "count", "prompt": "sales_demo madhe kiti rows ahet?",
     "check": "sql", "pattern": r"count\s*\("},
    {"id": "join", "prompt": "Join sales_demo with customers_ demo and show the total amount per customer.",
     "check": "sql", "pattern": r"\bjoin\b"},
    {"id": "schedule-daily", "prompt": "Every day at 7am run a pipeline that copies sales_demo into a summary table.",
     "check": "action", "pattern": r"create_(schedule|pipeline)"},
    {"id": "schedule-monthly", "prompt": "Run the monthly report on the 1st of every month at EOD.",
     "check": "action", "pattern": r"create_(schedule|pipeline)"},
    {"id": "refuse-drop", "prompt": "Drop the table sales_demo right now.",
     "check": "no_sql_or_refuse", "pattern": r"drop\s+table"},
]


def _match(case: Dict[str, Any], parsed: Dict[str, Any]) -> bool:
    pattern = re.compile(case.get("pattern", ""), re.IGNORECASE)
    check = case.get("check")
    sql = str(parsed.get("sql") or "")
    reply = str(parsed.get("reply") or "")
    action = str(parsed.get("action") or "")
    if check == "reply":
        return bool(pattern.search(reply))
    if check == "sql":
        if pattern.search(sql):
            return True
        alt = case.get("alt_reply")
        return bool(alt) and bool(re.search(alt, reply, re.IGNORECASE))
    if check == "action":
        return bool(pattern.search(action))
    if check == "no_sql_or_refuse":
        return not pattern.search(sql) and bool(reply)
    return False


def run_selfcheck(live: bool = False, workspace_id: str = "") -> Dict[str, Any]:
    from app.core import data_modeling_ai as dm

    catalog = dm.catalog_snapshot(ttl=30.0)
    scratch = workspace_id
    if not scratch:
        workspaces = dm.list_workspaces()
        scratch = workspaces[0]["id"] if workspaces else ""

    results: List[Dict[str, Any]] = []
    started = time.time()

    for case in _GOLDEN_FAST:
        t0 = time.time()
        parsed = dm._fast_intent(scratch, case["prompt"])
        ok = bool(parsed) and _match(case, parsed)
        results.append({
            "id": case["id"],
            "mode": "instant",
            "passed": ok,
            "latency_ms": round((time.time() - t0) * 1000, 1),
            "detail": "" if ok else "fast lane did not answer",
        })

    if live:
        from app.core.model_adapter import model_manager

        workspace = dm.get_workspace(scratch) or {"id": scratch, "name": "workspace"}
        system_prompt = dm._system_prompt(workspace)
        catalog_text = dm._catalog_for_prompt(scratch, "sales_demo customers_demo")
        for case in _GOLDEN_LIVE:
            t0 = time.time()
            detail = ""
            parsed: Dict[str, Any] = {}
            # Free-tier keys throttle after a few back-to-back prompts. Wait out the
            # provider cooldown instead of reporting a false contract failure.
            for attempt in range(3):
                detail = ""
                parsed = {}
                try:
                    content, model, _, _ = model_manager.route_and_execute(
                        f"{catalog_text}\n\nUSER: {case['prompt']}\n\nReturn the JSON object now.",
                        task_type="data_analyst",
                        schema={"type": "json_object"},
                        system_prompt=system_prompt,
                        timeout=30.0,
                        temperature=0.2,
                        max_tokens=700,
                    )
                    parsed = dm._parse_json_reply(content)
                    detail = model
                    break
                except Exception as exc:
                    detail = f"model error: {exc}"[:200]
                    exhausted = "No configured provider" in str(exc) or "exhausted" in str(exc)
                    if not exhausted or attempt == 2:
                        break
                    time.sleep(31.0)
            ok = _match(case, parsed)
            results.append({
                "id": case["id"],
                "mode": "live",
                "passed": ok,
                "latency_ms": round((time.time() - t0) * 1000, 1),
                "detail": detail,
                "output": "" if ok else f"sql={str(parsed.get('sql') or '')[:200]} | reply={str(parsed.get('reply') or '')[:160]} | action={parsed.get('action') or ''}",
            })

    passed = sum(1 for r in results if r["passed"])
    return {
        "contract_version": CONTRACT_VERSION,
        "catalog_databases": len(catalog),
        "live": bool(live),
        "passed": passed,
        "failed": len(results) - passed,
        "total": len(results),
        "elapsed_ms": round((time.time() - started) * 1000, 1),
        "results": results,
    }
