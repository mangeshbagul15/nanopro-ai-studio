"""
Telegram Multi-Bot Specialized Message Router
Routes system alerts, health telemetry, career updates, and financial reports
to their dedicated category Telegram bots.
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
)
from app.core.logger import log_event

# Bot Category Map
BOT_ROUTING_MAP = {
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
    "reports": {
        "token": TELEGRAM_REPORTS_BOT_TOKEN,
        "username": TELEGRAM_REPORTS_BOT_USERNAME,
        "label": "Executive & Financial Reports"
    },
    "financial": {
        "token": TELEGRAM_REPORTS_BOT_TOKEN,
        "username": TELEGRAM_REPORTS_BOT_USERNAME,
        "label": "Executive & Financial Reports"
    },
    "news": {
        "token": TELEGRAM_NEWS_BOT_TOKEN,
        "username": TELEGRAM_NEWS_BOT_USERNAME,
        "label": "AI Tech News & Live Trends"
    },
    "general": {
        "token": TELEGRAM_NEWS_BOT_TOKEN,
        "username": TELEGRAM_NEWS_BOT_USERNAME,
        "label": "AI Tech News & Live Trends"
    }
}


def send_telegram_routed_message(
    category: str,
    text: str,
    chat_id: Optional[str] = None,
    document_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Dispatches a Telegram message to its specialized bot channel.
    If the specialized bot encounters an error (e.g. user hasn't pressed /start yet),
    it automatically falls back to the primary News bot so no message is ever lost.
    """
    target_chat_id = chat_id or TELEGRAM_CHAT_ID
    clean_cat = (category or "general").lower().strip()
    route_info = BOT_ROUTING_MAP.get(clean_cat, BOT_ROUTING_MAP["general"])
    
    primary_token = route_info["token"]
    primary_bot = route_info["username"]
    fallback_token = TELEGRAM_NEWS_BOT_TOKEN
    fallback_bot = TELEGRAM_NEWS_BOT_USERNAME

    # 1. Attempt dispatch to the specialized bot
    res = _dispatch_telegram_http(primary_token, target_chat_id, text, document_path)
    if res.get("success"):
        res["bot_used"] = primary_bot
        res["category"] = clean_cat
        res["fallback_used"] = False
        log_event(f"Telegram routed alert [{clean_cat}] delivered via {primary_bot}", component="TelegramRouter")
        return res

    # 2. If primary fails (e.g. 400 Bad Request if chat not started), fall back to primary News bot
    log_event(
        f"Specialized Telegram bot {primary_bot} notice: {res.get('error')}. Falling back to primary bot {fallback_bot}...",
        level="WARNING",
        component="TelegramRouter"
    )
    fallback_text = f"[{route_info['label']}]\n{text}"
    fb_res = _dispatch_telegram_http(fallback_token, target_chat_id, fallback_text, document_path)
    if fb_res.get("success"):
        fb_res["bot_used"] = fallback_bot
        fb_res["category"] = clean_cat
        fb_res["fallback_used"] = True
        fb_res["primary_error"] = res.get("error")
        fb_res["hint"] = f"To receive messages directly in {primary_bot}, open {primary_bot} in Telegram and press START."
        return fb_res

    return {
        "success": False,
        "error": f"Both specialized bot ({primary_bot}) and fallback bot ({fallback_bot}) failed: {fb_res.get('error')}",
        "category": clean_cat
    }


def _dispatch_telegram_http(
    token: str,
    chat_id: str,
    text: str,
    document_path: Optional[str] = None
) -> Dict[str, Any]:
    """Underlying HTTP dispatcher over HTTPS port 443."""
    if not token or not chat_id:
        return {"success": False, "error": "Missing bot token or chat ID"}

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    headers = {"User-Agent": "NanoProStudio/2.0"}

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=8.0) as resp:
            resp_body = resp.read().decode("utf-8")
            return {"success": True, "response": json.loads(resp_body) if resp_body.startswith("{") else resp_body}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        return {"success": False, "error": f"HTTP {e.code}: {err_msg}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def test_all_specialized_bots(chat_id: Optional[str] = None) -> Dict[str, Any]:
    """Test ping to all 4 specialized bots."""
    cid = chat_id or TELEGRAM_CHAT_ID
    results = {}
    
    test_cases = [
        ("health", "🏥 [Health Monitor Bot] Snowflake, 3x Oracle XE, and Render Cloud health is NOMINAL. Latency: 2ms."),
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
