"""
Telegram Multi-Bot Specialized Message Router
Strictly isolates system alerts, health telemetry, career updates, and financial reports
to their dedicated category Telegram bots with zero cross-talk or leakage into News Bot.
"""

import os
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional
from app.core.config import (
    TELEGRAM_CHAT_ID,
    TELEGRAM_NEWS_BOT_TOKEN,
    TELEGRAM_NEWS_BOT_USERNAME,
    TELEGRAM_HEALTH_BOT_TOKEN,
    TELEGRAM_HEALTH_BOT_USERNAME,
    TELEGRAM_CAREER_BOT_TOKEN,
    TELEGRAM_CAREER_BOT_USERNAME,
    TELEGRAM_REPORTS_BOT_TOKEN,
    TELEGRAM_REPORTS_BOT_USERNAME,
    TELEGRAM_APK_BOT_TOKEN,
    TELEGRAM_APK_BOT_USERNAME,
)
from app.core.logger import log_event

# Bot Category Map - Strict Isolation
BOT_ROUTING_MAP = {
    # 1. Health & Infrastructure Bot (@mangesh_health_monitor_bot)
    "health": {
        "token": TELEGRAM_HEALTH_BOT_TOKEN,
        "username": TELEGRAM_HEALTH_BOT_USERNAME,
        "label": "System Health & DB Monitoring"
    },
    "monitoring": {
        "token": TELEGRAM_HEALTH_BOT_TOKEN,
        "username": TELEGRAM_HEALTH_BOT_USERNAME,
        "label": "System Health & DB Monitoring"
    },
    "system": {
        "token": TELEGRAM_HEALTH_BOT_TOKEN,
        "username": TELEGRAM_HEALTH_BOT_USERNAME,
        "label": "System Health & DB Monitoring"
    },
    "database": {
        "token": TELEGRAM_HEALTH_BOT_TOKEN,
        "username": TELEGRAM_HEALTH_BOT_USERNAME,
        "label": "Database Pipeline & Engine Health"
    },
    "pipeline": {
        "token": TELEGRAM_HEALTH_BOT_TOKEN,
        "username": TELEGRAM_HEALTH_BOT_USERNAME,
        "label": "Data Pipeline Vitals"
    },
    "security": {
        "token": TELEGRAM_HEALTH_BOT_TOKEN,
        "username": TELEGRAM_HEALTH_BOT_USERNAME,
        "label": "Security & Auth Guard"
    },
    "auth": {
        "token": TELEGRAM_HEALTH_BOT_TOKEN,
        "username": TELEGRAM_HEALTH_BOT_USERNAME,
        "label": "Authentication & Access Guard"
    },

    # 2. Career & Interview Study Bot (@mangesh_career_study_bot)
    "career": {
        "token": TELEGRAM_CAREER_BOT_TOKEN,
        "username": TELEGRAM_CAREER_BOT_USERNAME,
        "label": "Career & MNC HR Outreach"
    },
    "study": {
        "token": TELEGRAM_CAREER_BOT_TOKEN,
        "username": TELEGRAM_CAREER_BOT_USERNAME,
        "label": "Interview Practice & Study Drills"
    },
    "jobs": {
        "token": TELEGRAM_CAREER_BOT_TOKEN,
        "username": TELEGRAM_CAREER_BOT_USERNAME,
        "label": "Career & Job Radar"
    },
    "job": {
        "token": TELEGRAM_CAREER_BOT_TOKEN,
        "username": TELEGRAM_CAREER_BOT_USERNAME,
        "label": "Career & Job Radar"
    },
    "interview": {
        "token": TELEGRAM_CAREER_BOT_TOKEN,
        "username": TELEGRAM_CAREER_BOT_USERNAME,
        "label": "Interview Practice & Study Drills"
    },
    "drill": {
        "token": TELEGRAM_CAREER_BOT_TOKEN,
        "username": TELEGRAM_CAREER_BOT_USERNAME,
        "label": "Senior Interview Scenario Drill"
    },
    "technical": {
        "token": TELEGRAM_CAREER_BOT_TOKEN,
        "username": TELEGRAM_CAREER_BOT_USERNAME,
        "label": "Technical Interview Drills"
    },
    "hr": {
        "token": TELEGRAM_CAREER_BOT_TOKEN,
        "username": TELEGRAM_CAREER_BOT_USERNAME,
        "label": "MNC HR Outreach & Applications"
    },
    "recruiter": {
        "token": TELEGRAM_CAREER_BOT_TOKEN,
        "username": TELEGRAM_CAREER_BOT_USERNAME,
        "label": "Recruiter Pipeline Updates"
    },

    # 3. Executive & Financial Reports Bot (@mangesh_reports_bot)
    "reports": {
        "token": TELEGRAM_REPORTS_BOT_TOKEN,
        "username": TELEGRAM_REPORTS_BOT_USERNAME,
        "label": "Executive & Financial Reports"
    },
    "report": {
        "token": TELEGRAM_REPORTS_BOT_TOKEN,
        "username": TELEGRAM_REPORTS_BOT_USERNAME,
        "label": "Executive & Financial Reports"
    },
    "financial": {
        "token": TELEGRAM_REPORTS_BOT_TOKEN,
        "username": TELEGRAM_REPORTS_BOT_USERNAME,
        "label": "Executive & Financial Reports"
    },
    "finance": {
        "token": TELEGRAM_REPORTS_BOT_TOKEN,
        "username": TELEGRAM_REPORTS_BOT_USERNAME,
        "label": "Financial Ledger & Analytics"
    },
    "ledger": {
        "token": TELEGRAM_REPORTS_BOT_TOKEN,
        "username": TELEGRAM_REPORTS_BOT_USERNAME,
        "label": "Financial Ledger & BankDB"
    },
    "executive": {
        "token": TELEGRAM_REPORTS_BOT_TOKEN,
        "username": TELEGRAM_REPORTS_BOT_USERNAME,
        "label": "Executive Briefings"
    },
    "reconciliation": {
        "token": TELEGRAM_REPORTS_BOT_TOKEN,
        "username": TELEGRAM_REPORTS_BOT_USERNAME,
        "label": "Data & Financial Reconciliation"
    },

    # 4. Tech News & Live Trends Bot (@mangesh_technews_bot)
    "news": {
        "token": TELEGRAM_NEWS_BOT_TOKEN,
        "username": TELEGRAM_NEWS_BOT_USERNAME,
        "label": "AI Tech News & Live Trends"
    },
    "tech_news": {
        "token": TELEGRAM_NEWS_BOT_TOKEN,
        "username": TELEGRAM_NEWS_BOT_USERNAME,
        "label": "AI Tech News & Live Trends"
    },
    "deals": {
        "token": TELEGRAM_NEWS_BOT_TOKEN,
        "username": TELEGRAM_NEWS_BOT_USERNAME,
        "label": "Amazon Price Drop & Hardware Deals"
    },
    "amazon": {
        "token": TELEGRAM_NEWS_BOT_TOKEN,
        "username": TELEGRAM_NEWS_BOT_USERNAME,
        "label": "Amazon Price Drop & Hardware Deals"
    },
    "general": {
        "token": TELEGRAM_NEWS_BOT_TOKEN,
        "username": TELEGRAM_NEWS_BOT_USERNAME,
        "label": "AI Tech News & Live Trends"
    },

    # 5. Open-Source Android APK Dispatcher Bot (@mangesh_apk_bot)
    "apk": {
        "token": TELEGRAM_APK_BOT_TOKEN,
        "username": TELEGRAM_APK_BOT_USERNAME,
        "label": "Open-Source Android APK Dispatcher"
    },
    "apks": {
        "token": TELEGRAM_APK_BOT_TOKEN,
        "username": TELEGRAM_APK_BOT_USERNAME,
        "label": "Open-Source Android APK Dispatcher"
    },
    "app": {
        "token": TELEGRAM_APK_BOT_TOKEN,
        "username": TELEGRAM_APK_BOT_USERNAME,
        "label": "Open-Source Android APK Dispatcher"
    }
}


def classify_telegram_message(text: str) -> str:
    """
    Intelligently analyzes the text content to determine the strictly isolated bot category.
    Guarantees that Career/Interview, System/Health, and Financial/Report messages
    NEVER get routed to the News bot.
    """
    t_lower = (text or "").lower()

    # 1. Career / Job / Interview / Recruiter / Resume / Drills
    career_keywords = [
        "interview", "interview drill", "scenario drill", "job", "career", "hr outreach", 
        "recruiter", "resume", "salary", "hiring", "openings", "python drill", 
        "sql drill", "candidate:", "candidate", "mangesh bagul", "mnc hr", "job radar", 
        "shortlisted", "job hunter", "tech events radar", "cidco", "jio world",
        "data engineer opening", "snowflake opening", "aws opening", "interviewer evaluation tip",
        "interview question", "senior interview", "recruiter profile shortlisted", "applied to"
    ]
    if any(k in t_lower for k in career_keywords):
        return "career"

    # 2. Health / System Monitoring / Database Pipeline / Security
    health_keywords = [
        "system health", "pipeline health", "lakehouse health", "database health",
        "cpu", "memory", "ram", "disk", "offline", "connection failure", "heartbeat",
        "nominal", "latency:", "unreachable", "fail2ban", "login failed", "banned ip",
        "vault security", "diagnostics report", "oracle xe (local", "snowflake (bank_db",
        "postgres (my_postgres", "render cloud health", "security alert", "unauthorized",
        "failover alert", "email failover", "fraud alert", "संशयास्पद बँकिंग व्यवहार",
        "data engineering ingestion complete", "files processed:", "rows loaded to db"
    ]
    if any(k in t_lower for k in health_keywords):
        return "health"

    # 3. Reports / Financial / BankDB / Executive Ledger
    reports_keywords = [
        "executive report", "executive briefing", "financial report", "financial ledger",
        "balance sheet", "p&l", "bankdb", "transactions verified", "transactions reconciled",
        "daily executive", "daily briefing", "excel report", "dispatch ledger",
        "reconciliation report", "total records in dw"
    ]
    if any(k in t_lower for k in reports_keywords):
        return "reports"

    # 4. APK / Open-Source Android Apps
    if any(k in t_lower for k in [".apk", "apk dispatcher", "f-droid", "android app", "foss app", "open-source ॲप"]):
        return "apk"

    # 5. Amazon Price Watches / Deals
    if any(k in t_lower for k in ["amazon price drop", "price drop alert", "product link:", "target reached"]):
        return "deals"

    # 6. Default: Tech News & AI Trends
    return "news"


def send_telegram_routed_message(
    category: Optional[str] = None,
    text: str = "",
    chat_id: Optional[str] = None,
    document_path: Optional[str] = None,
    parse_mode: Optional[str] = "HTML"
) -> Dict[str, Any]:
    """
    Dispatches a Telegram message to its specialized bot channel.
    Zero cross-contamination:
    - Never falls back to News Bot for Career, Health, or Report messages.
    - If category is omitted or general, auto-classifies from message content.
    """
    target_chat_id = chat_id or TELEGRAM_CHAT_ID
    clean_cat = (category or "").lower().strip()

    # If category is omitted, general, or all -> run smart content classification
    if not clean_cat or clean_cat in ["general", "all", "default"]:
        clean_cat = classify_telegram_message(text)

    route_info = BOT_ROUTING_MAP.get(clean_cat)
    if not route_info:
        clean_cat = classify_telegram_message(text)
        route_info = BOT_ROUTING_MAP.get(clean_cat, BOT_ROUTING_MAP["news"])

    primary_token = route_info["token"]
    primary_bot = route_info["username"]

    # 1. Attempt dispatch to the strictly assigned specialized bot
    res = _dispatch_telegram_http(primary_token, target_chat_id, text, document_path=document_path, parse_mode=parse_mode)
    if res.get("success"):
        res["bot_used"] = primary_bot
        res["category"] = clean_cat
        res["fallback_used"] = False
        res["status"] = "success"
        log_event(f"Telegram routed alert [{clean_cat}] delivered via {primary_bot}", component="TelegramRouter")
        return res

    # 2. Strict Isolation: If dispatch to the specialized bot failed, DO NOT leak into News Bot!
    log_event(
        f"Specialized Telegram bot {primary_bot} failed for category [{clean_cat}]: {res.get('error')}. Cross-bot fallback disabled to prevent message pollution.",
        level="ERROR",
        component="TelegramRouter"
    )
    return {
        "success": False,
        "status": "error",
        "bot_used": primary_bot,
        "category": clean_cat,
        "error": f"Failed to deliver to {primary_bot}: {res.get('error')}",
        "hint": f"Ensure Chat ID {target_chat_id} has started {primary_bot} in Telegram by sending /start."
    }


def _dispatch_telegram_http(
    token: str,
    chat_id: str,
    text: str,
    document_path: Optional[str] = None,
    parse_mode: Optional[str] = "HTML"
) -> Dict[str, Any]:
    """Underlying HTTP dispatcher over HTTPS port 443 with HTML and Plaintext support."""
    if not token or not chat_id:
        return {"success": False, "error": "Missing bot token or chat ID"}

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": False
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode

    data = urllib.parse.urlencode(payload).encode("utf-8")
    headers = {"User-Agent": "NanoProStudio/2.0"}

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            resp_body = resp.read().decode("utf-8")
            parsed = json.loads(resp_body) if resp_body.startswith("{") else {"raw": resp_body}
            return {"success": True, "response": parsed}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        # If HTML entity error, retry without parse_mode (plaintext fallback)
        if "can't parse entities" in err_msg.lower() or "bad request" in err_msg.lower():
            try:
                import re
                plain_text = re.sub(r'<[^>]*>', '', text).strip()
                payload_plain = {
                    "chat_id": chat_id,
                    "text": plain_text,
                    "disable_web_page_preview": False
                }
                data_plain = urllib.parse.urlencode(payload_plain).encode("utf-8")
                req_plain = urllib.request.Request(url, data=data_plain, headers=headers, method="POST")
                with urllib.request.urlopen(req_plain, timeout=10.0) as resp2:
                    resp_body2 = resp2.read().decode("utf-8")
                    parsed2 = json.loads(resp_body2) if resp_body2.startswith("{") else {"raw": resp_body2}
                    return {"success": True, "response": parsed2, "fallback_mode": "plaintext"}
            except Exception as e_plain:
                return {"success": False, "error": f"Plaintext fallback error: {str(e_plain)}"}
        return {"success": False, "error": f"HTTP {e.code}: {err_msg}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def test_all_specialized_bots(chat_id: Optional[str] = None) -> Dict[str, Any]:
    """Test ping to all 4 specialized bots with strict channel verification."""
    cid = chat_id or TELEGRAM_CHAT_ID
    results = {}
    
    test_cases = [
        ("health", "🏥 [Health Monitor Bot] Snowflake, 3x Oracle XE, DuckDB Lakehouse, and Cloudflare Gateway health is NOMINAL. Latency: 2ms."),
        ("career", "💼 [Career & Study Bot] 4-Hour Job Radar active. 18 new Data Engineer openings discovered across Pune & Mumbai."),
        ("reports", "📊 [Executive Reports Bot] Snowflake BankDB Daily Financial Ledger generated. 142,500 transactions verified."),
        ("news", "📰 [Tech News Bot] Daily AI Discovery Digest: Meta Llama, Groq LPU, and Snowflake Polaris trends.")
    ]

    for cat, msg in test_cases:
        res = send_telegram_routed_message(category=cat, text=msg, chat_id=cid)
        results[cat] = res

    return {
        "status": "success",
        "chat_id": cid,
        "test_results": results
    }
