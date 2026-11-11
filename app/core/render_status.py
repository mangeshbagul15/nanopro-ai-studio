"""Live Render free-tier usage for the control tower.

Bandwidth numbers come from the app's own meter (egress_guard), which is what
Render suspends a service over. Account-level fields (suspended flag, deploys,
custom domains) light up automatically when RENDER_API_KEY and
RENDER_SERVICE_ID are configured; without them the drawer says so instead of
inventing numbers. Render's billing page stays authoritative.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, Optional

FREE_BANDWIDTH_GB = 5.0
FREE_PIPELINE_MINUTES = 500
FREE_INSTANCE_HOURS = 750
FREE_CUSTOM_DOMAINS = 2
API_TIMEOUT = 4.0
API_CACHE_SECONDS = 60.0

_cache: Dict[str, Any] = {"at": 0.0, "data": None}


def _fmt_bytes(value: float) -> str:
    value = float(value or 0)
    if value < 1024:
        return f"{int(value)} B"
    for unit in ("KB", "MB", "GB"):
        value /= 1024
        if value < 1024 or unit == "GB":
            return f"{value:.2f} {unit}"
    return f"{value:.2f} GB"


def _uptime_hours() -> float:
    """Age of this process, not the shared host kernel's uptime."""
    try:
        with open("/proc/self/stat", "r", encoding="utf-8") as fh:
            after_comm = fh.read().rsplit(")", 1)[1].split()
        start_ticks = float(after_comm[19])
        with open("/proc/uptime", "r", encoding="utf-8") as fh:
            host_uptime = float(fh.read().split()[0])
        return max((host_uptime - start_ticks / float(os.sysconf("SC_CLK_TCK"))) / 3600.0, 0.0)
    except Exception:
        return 0.0


def _expected_month_hours() -> int:
    now = datetime.now(timezone.utc)
    next_month = datetime(now.year + (1 if now.month == 12 else 0), (now.month % 12) + 1, 1)
    return (next_month - datetime(now.year, now.month, 1)).days * 24


def _api_get(path: str) -> Optional[Any]:
    key = (os.environ.get("RENDER_API_KEY") or "").strip()
    service = (os.environ.get("RENDER_SERVICE_ID") or "").strip()
    if not key or not service:
        return None
    request = urllib.request.Request(
        f"https://api.render.com/v1/services/{service}{path}",
        headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=API_TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8", "replace"))
    except Exception:
        return None


def _parse_ts(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _build_minutes(deploys: Any) -> Optional[int]:
    if not isinstance(deploys, list):
        return None
    month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total = 0.0
    counted = 0
    for entry in deploys:
        deploy = (entry or {}).get("deploy") if isinstance(entry, dict) else None
        if not isinstance(deploy, dict):
            continue
        started = _parse_ts(deploy.get("createdAt"))
        finished = _parse_ts(deploy.get("finishedAt"))
        if not started or not finished or started < month_start:
            continue
        total += max((finished - started).total_seconds(), 0.0)
        counted += 1
    return int(round(total / 60.0)) if counted else 0


def _latest_deploy(deploys: Any) -> str:
    if not isinstance(deploys, list):
        return "n/a (Render API not connected)"
    for entry in deploys:
        deploy = (entry or {}).get("deploy") if isinstance(entry, dict) else None
        if not isinstance(deploy, dict):
            continue
        state = str(deploy.get("status") or "unknown")
        finished = _parse_ts(deploy.get("finishedAt")) or _parse_ts(deploy.get("createdAt"))
        if finished:
            return f"{state} · {finished.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC"
        return state
    return "no deploys found"


def _account_fields() -> Dict[str, Any]:
    configured = bool((os.environ.get("RENDER_API_KEY") or "").strip() and (os.environ.get("RENDER_SERVICE_ID") or "").strip())
    if not configured:
        return {
            "suspended": "unknown — connect Render API",
            "pipeline_minutes": "not measured without a Render API key",
            "custom_domains": f"0 of {FREE_CUSTOM_DOMAINS} (default onrender.com host)",
            "latest_deploy": "not measured without a Render API key",
            "api_source": "app meter only",
        }

    service = _api_get("")
    deploys = _api_get("/deploys?limit=50")
    domains = _api_get("/custom-domains?limit=100")

    suspended = "unknown"
    if isinstance(service, dict):
        if isinstance(service.get("service"), dict):
            service = service["service"]
        suspended = "yes" if service.get("suspended") else "no"

    minutes = _build_minutes(deploys)
    if minutes is None:
        build_text = "unreachable right now"
    else:
        build_text = f"{minutes} min used of {FREE_PIPELINE_MINUTES} (approx. deploy build time)"

    domain_text = "unreachable right now"
    if isinstance(domains, list):
        domain_text = f"{len(domains)} of {FREE_CUSTOM_DOMAINS}"

    return {
        "suspended": suspended,
        "pipeline_minutes": build_text,
        "custom_domains": domain_text,
        "latest_deploy": _latest_deploy(deploys),
        "api_source": "app meter + Render API",
    }


def _compose() -> Dict[str, Any]:
    from app.core.egress_guard import egress_audit

    audit = egress_audit()
    used_bytes = int(audit.get("used_bytes") or 0)
    limit_bytes = FREE_BANDWIDTH_GB * 1024 ** 3
    percent = round(used_bytes / limit_bytes * 100, 2)
    by_category = audit.get("by_category") or {}
    http_bytes = int(by_category.get("http") or 0)
    service_bytes = sum(int(v or 0) for k, v in by_category.items() if k != "http")

    now = datetime.now(timezone.utc)
    uptime = _uptime_hours()
    expected = _expected_month_hours()
    verdict = audit.get("verdict") or "ok"

    account = _account_fields()
    payload: Dict[str, Any] = {
        "status": "success",
        "plan": "Free · no card on file",
        "month": now.strftime("%Y-%m"),
        "day": f"day {now.day} · {audit.get('days_left')} days left",
        "bandwidth": f"{audit.get('used_gb')} GB of {FREE_BANDWIDTH_GB:g} GB ({percent}%)",
        "projected": f"{audit.get('projected_month_gb')} GB by month end",
        "bt_verdict": verdict,
        "bt_mode": audit.get("mode") or "normal",
        "http_responses": _fmt_bytes(http_bytes),
        "service_initiated": _fmt_bytes(service_bytes),
        "service_sources": ", ".join(sorted(k for k in by_category if k != "http")) or "none yet",
        "websocket_responses": "not metered by the app (Render counts them in bandwidth)",
        "private_link": "not used — shared free host, no private network egress",
        "soft_warn_at": f"{audit.get('soft_limit_gb')} GB — heavy features throttle",
        "heavy_pause_at": f"{audit.get('hard_limit_gb')} GB — heavy endpoints paused",
        "suspend_at": f"{FREE_BANDWIDTH_GB:g} GB — free service suspended for the month (no card)",
        "instance_uptime": f"{uptime:.1f} h since this boot · {expected} h max in this month",
        "instance_limit": f"{FREE_INSTANCE_HOURS} h/month · one always-on service uses at most {expected} h",
        "avg_per_day": f"{audit.get('avg_per_day_gb')} GB/day",
        "checked_at": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "note": "App meter; Render billing is authoritative and may differ by a few minutes.",
    }
    payload.update(account)
    return payload


def render_status(force: bool = False) -> Dict[str, Any]:
    now = time.monotonic()
    with_cache = _cache.get("data")
    if not force and with_cache is not None and (now - float(_cache.get("at") or 0)) < API_CACHE_SECONDS:
        return with_cache
    data = _compose()
    _cache["data"] = data
    _cache["at"] = now
    return data
