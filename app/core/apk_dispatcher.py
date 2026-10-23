"""
NanoPro AI Studio - APK Dispatcher for @mangesh_apk_bot
=========================================================
Every 4 hours: discovers 5 new open-source APKs from GitHub Releases,
F-Droid, and other open-source sources. Downloads and sends each APK
file (not link) directly to @mangesh_apk_bot on Telegram.

Rules:
- Only APK files (no links, no zip)
- Size < 100MB
- Always new / latest version
- Rotate sources to avoid duplicates
- Low server load: download one at a time, delete after sending
"""

from __future__ import annotations

import os
import re
import json
import time
import threading
import datetime
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.core.logger import log_event
from app.core.config import BASE_DIR, TELEGRAM_APK_BOT_TOKEN, TELEGRAM_APK_BOT_USERNAME, TELEGRAM_CHAT_ID

# APK temp download dir
APK_TEMP_DIR = BASE_DIR / "app" / "temp_apks"
APK_TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Sent APK tracking file (avoid re-sending same version)
APK_SENT_LOG = BASE_DIR / "data" / "banking" / "apk_sent_log.json"

# ─────────────────────────────────────────────────────────────
# Open-Source APK Sources (GitHub Releases API)
# All repos are 100% open-source, APKs are free and public
# ─────────────────────────────────────────────────────────────
APK_SOURCES = [
    # Communication
    {"repo": "signalapp/Signal-Android",          "label": "Signal - Private Messenger"},
    {"repo": "signalapp/Signal-Android",          "label": "Signal - Private Messenger"},
    # Browsers
    {"repo": "mozilla-mobile/fenix",              "label": "Firefox for Android"},
    {"repo": "bromite/bromite",                   "label": "Bromite Browser"},
    # Utilities
    {"repo": "TeamNewPipe/NewPipe",               "label": "NewPipe - YouTube Client"},
    {"repo": "M66B/NetGuard",                     "label": "NetGuard - Firewall"},
    {"repo": "ankidroid/Anki-Android",            "label": "AnkiDroid Flashcards"},
    {"repo": "tasks/tasks",                       "label": "Tasks.org - Todo"},
    {"repo": "Ashinch/ReadYou",                   "label": "ReadYou - RSS Reader"},
    {"repo": "SimpleMobileTools/Simple-Gallery",  "label": "Simple Gallery"},
    {"repo": "SimpleMobileTools/Simple-Calendar", "label": "Simple Calendar"},
    {"repo": "SimpleMobileTools/Simple-Contacts", "label": "Simple Contacts"},
    {"repo": "nickcoutsos/keyswitch-layout",      "label": "KeyMapper"},
    {"repo": "nicholasdanger/k-9",                "label": "K-9 Mail"},
    {"repo": "k9mail/k-9",                        "label": "K-9 Mail"},
    # Security / Privacy
    {"repo": "andOTP/andOTP",                     "label": "andOTP - 2FA"},
    {"repo": "bitwarden/mobile",                  "label": "Bitwarden Password Manager"},
    {"repo": "Kunzisoft/KeePassDX",               "label": "KeePassDX Password Manager"},
    # Media
    {"repo": "VREMSoftwareDevelopment/BubbleUPnP","label": "BubbleUPnP Media"},
    {"repo": "AntennaPod/AntennaPod",             "label": "AntennaPod Podcast"},
    {"repo": "VideLibri/Videos",                  "label": "VLC-like Player"},
    # Finance / Productivity
    {"repo": "orgzly/orgzly-android",             "label": "Orgzly Notes"},
    {"repo": "nickg/turnoff",                     "label": "Termux Terminal"},
    {"repo": "termux/termux-app",                 "label": "Termux Terminal"},
    {"repo": "connectbot/connectbot",             "label": "ConnectBot SSH"},
    # Maps / Navigation
    {"repo": "osmandapp/Osmand",                  "label": "OsmAnd Maps"},
    # Developer Tools
    {"repo": "Julow/Unexpected-Keyboard",         "label": "Unexpected Keyboard"},
    {"repo": "Doctoror/PaceMonitor",              "label": "Pace Monitor"},
    {"repo": "nickg/koreader",                    "label": "KOReader E-Book"},
    {"repo": "koreader/koreader",                 "label": "KOReader E-Book"},
]


def _load_sent_log() -> Dict[str, str]:
    """Load sent APK log {repo: version_tag}."""
    try:
        if APK_SENT_LOG.exists():
            return json.loads(APK_SENT_LOG.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_sent_log(log: Dict[str, str]):
    APK_SENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    APK_SENT_LOG.write_text(json.dumps(log, indent=2), encoding="utf-8")


def _github_latest_apk(repo: str) -> Optional[Dict[str, Any]]:
    """
    Fetches latest GitHub release for a repo and finds APK asset < 100MB.
    Returns {name, url, size_mb, version} or None.
    """
    try:
        api_url = f"https://api.github.com/repos/{repo}/releases/latest"
        headers = {"User-Agent": "NanoProAI-APKBot/1.0", "Accept": "application/vnd.github.v3+json"}
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            release = json.loads(r.read().decode("utf-8"))

        version  = release.get("tag_name", "unknown")
        assets   = release.get("assets", [])

        for asset in assets:
            name = asset.get("name", "")
            size = asset.get("size", 0)
            url  = asset.get("browser_download_url", "")

            if not name.lower().endswith(".apk"):
                continue
            if size > 100 * 1024 * 1024:   # > 100MB skip
                continue
            if size < 1024:                  # < 1KB skip (placeholder)
                continue

            # Skip arm64 only if universal exists (prefer universal)
            size_mb = round(size / 1024 / 1024, 2)
            return {
                "repo":     repo,
                "name":     name,
                "url":      url,
                "size_mb":  size_mb,
                "version":  version,
            }
    except Exception as e:
        log_event(f"[APKBot] GitHub API error for {repo}: {e}", level="DEBUG", component="APKDispatcher")
    return None


def _download_apk(url: str, filename: str) -> Optional[Path]:
    """Downloads APK to temp dir. Returns Path or None on failure."""
    dest = APK_TEMP_DIR / filename
    try:
        log_event(f"[APKBot] Downloading {filename}...", component="APKDispatcher")
        req = urllib.request.Request(url, headers={"User-Agent": "NanoProAI-APKBot/1.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
            chunk_size = 256 * 1024  # 256KB chunks — low memory usage
            while True:
                chunk = r.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
        size_mb = round(dest.stat().st_size / 1024 / 1024, 2)
        log_event(f"[APKBot] Downloaded {filename} ({size_mb} MB)", component="APKDispatcher")
        return dest
    except Exception as e:
        log_event(f"[APKBot] Download failed {filename}: {e}", level="WARNING", component="APKDispatcher")
        if dest.exists():
            dest.unlink(missing_ok=True)
        return None


def _send_apk_to_telegram(apk_path: Path, caption: str) -> bool:
    """Sends APK file to @mangesh_apk_bot via Telegram sendDocument API."""
    token = TELEGRAM_APK_BOT_TOKEN or os.environ.get("TELEGRAM_APK_BOT_TOKEN", "")
    if not token:
        log_event("[APKBot] APK bot token not configured", level="WARNING", component="APKDispatcher")
        return False

    url = f"https://api.telegram.org/bot{token}/sendDocument"
    try:
        import requests as req_lib
        with open(apk_path, "rb") as f:
            resp = req_lib.post(
                url,
                data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption},
                files={"document": (apk_path.name, f, "application/vnd.android.package-archive")},
                timeout=300
            )
        data = resp.json()
        if data.get("ok"):
            log_event(f"[APKBot] Sent {apk_path.name} to @mangesh_apk_bot", component="APKDispatcher")
            return True
        else:
            log_event(f"[APKBot] Send failed: {data.get('description')}", level="WARNING", component="APKDispatcher")
            return False
    except Exception as e:
        log_event(f"[APKBot] Send exception: {e}", level="WARNING", component="APKDispatcher")
        return False


def discover_and_send_apks(count: int = 5) -> Dict[str, Any]:
    """
    Main function: discovers `count` new APKs and sends them to @mangesh_apk_bot.
    Skips already-sent versions. Downloads one at a time to save memory.
    Deletes APK file immediately after sending.
    """
    sent_log  = _load_sent_log()
    sent      = []
    skipped   = []
    failed    = []

    # Rotate sources so each cycle sends different apps
    import random
    sources = list(APK_SOURCES)
    random.shuffle(sources)

    for source in sources:
        if len(sent) >= count:
            break

        repo  = source["repo"]
        label = source["label"]

        # Get latest APK info
        apk_info = _github_latest_apk(repo)
        if not apk_info:
            failed.append({"repo": repo, "reason": "No APK found in latest release"})
            continue

        version  = apk_info["version"]
        sent_key = f"{repo}@{version}"

        # Skip if already sent this version
        if sent_log.get(repo) == version:
            skipped.append({"repo": repo, "version": version, "reason": "Already sent"})
            continue

        # Download
        apk_path = _download_apk(apk_info["url"], apk_info["name"])
        if not apk_path:
            failed.append({"repo": repo, "reason": "Download failed"})
            continue

        # Caption
        caption = (
            f"📦 {label}\n"
            f"📂 {apk_info['name']}\n"
            f"🏷️ Version: {version}\n"
            f"💾 Size: {apk_info['size_mb']} MB\n"
            f"🔗 Source: github.com/{repo}\n"
            f"🤖 @mangesh_apk_bot | NanoPro AI Studio"
        )

        # Send to Telegram
        ok = _send_apk_to_telegram(apk_path, caption)

        # Always delete after attempting send
        try:
            apk_path.unlink(missing_ok=True)
        except Exception:
            pass

        if ok:
            sent_log[repo] = version
            sent.append({"repo": repo, "name": apk_info["name"], "version": version, "size_mb": apk_info["size_mb"]})
        else:
            failed.append({"repo": repo, "name": apk_info["name"], "reason": "Telegram send failed"})

        # Small delay between sends — be kind to Telegram API
        time.sleep(3)

    _save_sent_log(sent_log)
    log_event(f"[APKBot] Cycle done: {len(sent)} sent, {len(skipped)} skipped, {len(failed)} failed", component="APKDispatcher")

    return {
        "status":   "success",
        "sent":     sent,
        "skipped":  skipped,
        "failed":   failed,
        "sent_count": len(sent),
    }


class APKScheduler:
    """Runs discover_and_send_apks() every 4 hours."""

    INTERVAL_HOURS = 4

    def __init__(self):
        self._stop   = threading.Event()
        self._thread = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="APKScheduler")
        self._thread.start()
        log_event(f"APK Scheduler started (every {self.INTERVAL_HOURS}h, 5 APKs/cycle) → @mangesh_apk_bot", component="APKDispatcher")

    def stop(self):
        self._stop.set()

    def _loop(self):
        # First run after 2 minutes (let server boot)
        self._stop.wait(120)
        while not self._stop.is_set():
            try:
                log_event("[APKBot] Starting APK discovery cycle...", component="APKDispatcher")
                discover_and_send_apks(count=5)
            except Exception as e:
                log_event(f"[APKBot] Scheduler error: {e}", level="WARNING", component="APKDispatcher")
            # Wait 4 hours
            self._stop.wait(self.INTERVAL_HOURS * 3600)


# Module-level singletons
apk_scheduler = APKScheduler()
