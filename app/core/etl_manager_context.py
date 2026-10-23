"""
NanoPro Manager ETL Context & Training Module
==============================================
Gives the AI Manager complete knowledge about:
- All 9 ETL projects (Credit Card, AML, ALM, ADF CIMS, CBS, UPI, UCIC, Bureau Mart, Data Lake)
- BOD/SOD/EOD batch cycles and T-1 report logic
- How to generate reports from natural language prompts
- Where data lives (Neon L0/L1, Snowflake L2 DIM/FACT)
- Current pipeline status, watermarks, load modes
"""

from __future__ import annotations
import datetime
from typing import Dict, Any, Optional

from app.core.logger import log_event


def get_etl_system_context() -> str:
    """
    Returns a comprehensive system context string for the NanoPro Manager.
    Inject this into the AI Manager's system prompt so it knows everything
    about the ETL pipeline and can generate reports from natural language.
    """
    try:
        from app.core.etl_automation_pipeline import (
            PROJECTS, STAR_SCHEMA, etl_pipeline,
            _today, _yesterday, _now_ist, _get_batch_cycle, _t1_report_dates
        )
        t1 = _t1_report_dates()
        cycle = t1["batch_cycle"]

        proj_lines = []
        for key, p in PROJECTS.items():
            star     = STAR_SCHEMA.get(key, {})
            wm       = etl_pipeline.get_watermark(key) or "Not run yet"
            mode     = etl_pipeline.detect_load_mode(key)
            dim_tbls = ", ".join(list(star.get("dims", {}).keys())[:4])
            fact_tbls= ", ".join(list(star.get("facts", {}).keys())[:3])
            proj_lines.append(
                f"  - {p['code']} ({p['domain']}): "
                f"Neon L0={p['neon_l0']}, L1={p['neon_l1']}, "
                f"Snowflake={p['sf_table']} | "
                f"Mode={mode} | WM={wm} | "
                f"DIMs=[{dim_tbls}] | FACTs=[{fact_tbls}]"
            )

        ctx = f"""
=== NANOPRO ETL PIPELINE — MANAGER KNOWLEDGE BASE ===

TODAY: {_today()} | BATCH CYCLE: {cycle}
T-1 Report Date: {t1['report_date']} (Data cut at {t1['t1_cutoff']})
Execution Time: {t1['execution_date']}

--- BATCH CYCLE SCHEDULE ---
BOD (Begin of Day)  06:00 IST: Previous day data loaded, T-1 reports ready
SOD (Start of Day)  08:00 IST: Open positions, beginning balances, alerts
INTRADAY           10:00 IST: Daily T-1 report dispatch (email + Telegram)
EOD (End of Day)   18:00 IST: Cut-off, final balances, close positions

--- ETL ARCHITECTURE ---
Source Data  -->  Neon PostgreSQL (L0 Raw + L1 Clean)
                  -->  Snowflake BANK_DB.L2_CURATED (DIM + FACT Star Schema)
                       -->  Email (nanoproaistudio@gmail.com) + Telegram (@mangesh_reports_bot)

Load Modes:
- FULL_LOAD: First run or monthly (30+ days). Truncate + reload all tables.
- INCREMENTAL: Daily delta load (watermark-based). Only new records since last run.

--- ALL 9 ETL PROJECTS ---
{chr(10).join(proj_lines)}

--- HOW TO GENERATE REPORTS FROM PROMPTS ---
User can ask: "Generate T-1 AML report" or "Run UPI settlement report for yesterday"
Manager should:
1. Identify project from prompt (aml, upi, credit_card, etc.)
2. Call etl_pipeline.run_project_pipeline(project_key, load_mode="INCREMENTAL")
3. Report will auto-send to email + Telegram
4. Or query Neon/Snowflake for specific data

--- PROMPT EXAMPLES THE MANAGER UNDERSTANDS ---
- "Run all pipelines" -> etl_pipeline.run_all_projects()
- "AML T-1 report" -> etl_pipeline.run_project_pipeline("aml")
- "UPI settlement yesterday" -> etl_pipeline.run_project_pipeline("upi")
- "Show CBS EOD balance" -> Query FACT_CBS_GL_BALANCE in Snowflake L2_CURATED
- "UCIC dedup status" -> Query FACT_UCIC_DEDUP in Snowflake L2_CURATED
- "Bureau NPA alert" -> Query FACT_NPA_EARLY_WARNING
- "Data lake ingestion status" -> Query FACT_INGESTION_LOG
- "Full load credit card" -> etl_pipeline.run_project_pipeline("credit_card", load_mode="FULL_LOAD")
- "Reset watermark AML" -> etl_pipeline.reset_watermark("aml")
- "Pipeline status" -> etl_pipeline status for all 9 projects

=== END NANOPRO ETL CONTEXT ===
"""
        return ctx.strip()
    except Exception as e:
        return f"ETL context unavailable: {e}"


def parse_etl_intent(prompt: str) -> Optional[Dict[str, Any]]:
    """
    Parses a natural language prompt and returns ETL action intent.
    The NanoPro Manager calls this to understand what the user wants.

    Returns:
        {
          "action": "run_pipeline" | "run_all" | "reset_watermark" | "status" | "report",
          "project_key": "aml" | "upi" | ... | None,
          "load_mode": "FULL_LOAD" | "INCREMENTAL" | None,
          "report_type": "t1" | "eod" | "bod" | "weekly" | "monthly" | None,
        }
    """
    try:
        from app.core.etl_automation_pipeline import PROJECTS
    except Exception:
        return None

    p_lower = prompt.lower()

    # Detect project
    project_key = None
    for key, p in PROJECTS.items():
        if (key in p_lower
                or p["code"].lower() in p_lower
                or any(w in p_lower for w in key.split("_"))):
            project_key = key
            break

    # Keyword overrides
    kw_map = {
        "upi": "upi", "settlement": "upi", "npci": "upi",
        "aml": "aml", "suspicious": "aml", "str": "aml", "ctr": "aml", "fiu": "aml",
        "alm": "alm", "liquidity": "alm", "lcr": "alm", "nsfr": "alm",
        "cims": "adf_cims", "rbi": "adf_cims", "xbrl": "adf_cims", "slr": "adf_cims",
        "cbs": "cbs", "finacle": "cbs", "migration": "cbs", "gl": "cbs",
        "credit card": "credit_card", "fraud": "credit_card", "card": "credit_card",
        "ucic": "ucic", "customer 360": "ucic", "dedup": "ucic", "kyc": "ucic",
        "bureau": "bureau_mart", "cibil": "bureau_mart", "experian": "bureau_mart", "npa": "bureau_mart",
        "data lake": "data_lake", "ingestion": "data_lake", "schema drift": "data_lake",
    }
    for kw, proj in kw_map.items():
        if kw in p_lower:
            project_key = proj
            break

    # Detect action
    action = "status"
    if any(w in p_lower for w in ["run", "execute", "trigger", "start", "generate", "dispatch", "send"]):
        action = "run_pipeline" if project_key else "run_all"
    elif any(w in p_lower for w in ["all", "sagl", "every", "all project"]):
        action = "run_all"
    elif any(w in p_lower for w in ["reset", "full load", "full reload"]):
        action = "reset_watermark"
    elif any(w in p_lower for w in ["status", "check", "health", "watermark"]):
        action = "status"
    elif any(w in p_lower for w in ["report", "show", "fetch", "get", "display"]):
        action = "report"

    # Detect load mode
    load_mode = None
    if "full load" in p_lower or "full reload" in p_lower or "truncate" in p_lower:
        load_mode = "FULL_LOAD"
    elif any(w in p_lower for w in ["incremental", "delta", "new records"]):
        load_mode = "INCREMENTAL"

    # Detect report type
    report_type = None
    if "t-1" in p_lower or "t1" in p_lower or "yesterday" in p_lower:
        report_type = "t1"
    elif "eod" in p_lower or "end of day" in p_lower:
        report_type = "eod"
    elif "bod" in p_lower or "begin of day" in p_lower:
        report_type = "bod"
    elif "sod" in p_lower or "start of day" in p_lower:
        report_type = "sod"
    elif "weekly" in p_lower:
        report_type = "weekly"
    elif "monthly" in p_lower:
        report_type = "monthly"

    return {
        "action":       action,
        "project_key":  project_key,
        "load_mode":    load_mode,
        "report_type":  report_type or "t1",
        "original_prompt": prompt,
    }


def execute_etl_from_prompt(prompt: str,
                             send_email: bool = True,
                             send_telegram: bool = True) -> Dict[str, Any]:
    """
    Main entry point: NanoPro Manager calls this with a natural language prompt.
    Parses intent and executes the appropriate ETL action.

    Examples:
        execute_etl_from_prompt("Run AML T-1 report")
        execute_etl_from_prompt("Generate all pipelines for today")
        execute_etl_from_prompt("UPI settlement report yesterday")
        execute_etl_from_prompt("Full load credit card")
    """
    from app.core.etl_automation_pipeline import etl_pipeline, PROJECTS

    intent = parse_etl_intent(prompt)
    if not intent:
        return {"status": "error", "error": "Could not parse ETL intent from prompt"}

    log_event(f"ETL Manager: prompt='{prompt}' intent={intent}", component="ETLManager")

    action      = intent["action"]
    project_key = intent["project_key"]
    load_mode   = intent["load_mode"]

    # Execute
    if action == "run_all":
        result = etl_pipeline.run_all_projects(
            rows_per_project=200,
            send_email=send_email,
            send_telegram=send_telegram
        )
        result["intent"]  = intent
        result["message"] = f"All {len(PROJECTS)} ETL pipelines executed. Reports sent via Email + Telegram."
        return result

    elif action in ("run_pipeline", "report") and project_key:
        result = etl_pipeline.run_project_pipeline(
            project_key=project_key,
            rows=200,
            send_email=send_email,
            send_telegram=send_telegram,
            load_mode=load_mode
        )
        result["intent"]  = intent
        result["message"] = f"{PROJECTS[project_key]['code']} pipeline executed. T-1 report sent."
        return result

    elif action == "reset_watermark":
        etl_pipeline.reset_watermark(project_key)
        return {
            "status":  "success",
            "intent":  intent,
            "message": f"Watermark reset for {project_key or 'ALL'}. Next run will be FULL_LOAD."
        }

    elif action == "status":
        status = {}
        for key in PROJECTS:
            status[key] = {
                "load_mode":    etl_pipeline.detect_load_mode(key),
                "watermark":    etl_pipeline.get_watermark(key),
                "project_name": PROJECTS[key]["name"],
            }
        from app.core.etl_automation_pipeline import _t1_report_dates
        return {
            "status":   "success",
            "intent":   intent,
            "t1_dates": _t1_report_dates(),
            "projects": status,
            "message":  "ETL pipeline status for all projects."
        }

    return {
        "status":  "error",
        "intent":  intent,
        "error":   f"Could not execute action '{action}' for project '{project_key}'"
    }


# Module-level context string for quick injection into AI Manager
ETL_SYSTEM_CONTEXT = None

def get_cached_etl_context() -> str:
    """Returns cached ETL context (refreshed every call for live watermark data)."""
    return get_etl_system_context()
