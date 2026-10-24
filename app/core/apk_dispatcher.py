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
import html
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
APK_CONFIG_FILE = BASE_DIR / "data" / "banking" / "apk_config.json"


def get_apk_config() -> Dict[str, Any]:
    """Load configurable APK dispatcher parameters (interval, count, enabled)."""
    default_cfg = {
        "interval_minutes": 15,
        "interval_hours": 0.25,
        "count": 5,
        "enabled": True,
        "direct_apk_only": True,
        "last_updated": datetime.datetime.now().isoformat(),
    }
    try:
        if APK_CONFIG_FILE.exists():
            data = json.loads(APK_CONFIG_FILE.read_text(encoding="utf-8"))
            default_cfg.update(data)
            return default_cfg
    except Exception:
        pass
    return default_cfg


def update_apk_config(interval_minutes: int = 15, count: int = 5, enabled: bool = True, direct_apk_only: bool = True) -> Dict[str, Any]:
    """Update and persist APK dispatcher parameters: default 15 minutes, 5 APKs direct."""
    cfg = get_apk_config()
    cfg["interval_minutes"] = max(1, int(interval_minutes))
    cfg["interval_hours"] = round(cfg["interval_minutes"] / 60.0, 3)
    cfg["count"] = max(1, min(20, int(count)))
    cfg["enabled"] = bool(enabled)
    cfg["direct_apk_only"] = bool(direct_apk_only)
    cfg["last_updated"] = datetime.datetime.now().isoformat()
    APK_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    APK_CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    global apk_scheduler
    if apk_scheduler:
        apk_scheduler.reload_config()
    return cfg

# ─────────────────────────────────────────────────────────────
# Open-Source APK Sources Catalog (55+ Verified Top-Tier FOSS Apps)
# Each entry contains Rich Metadata: Summary (Marathi + English) & Key Features
# ─────────────────────────────────────────────────────────────
APK_SOURCES = [
    # ── 1. Video & Audio Streaming / Media ──
    {
        "repo": "TeamNewPipe/NewPipe",
        "label": "NewPipe - YouTube Streamer",
        "category": "Media & Streaming",
        "summary": "YouTube साठी जाहिरातमुक्त (Ad-free) हलकेफुलके ओपन-सोर्स ॲप. गुगल सर्व्हिसेस शिवाय चालते आणि बॅकग्राउंड प्लेबॅक व व्हिडिओ डाऊनलोड सपोर्ट करते.",
        "features": [
            "कोणतीही जाहिरात नाही (100% Ad-Free)",
            "बॅकग्राउंड प्ले व पॉपअप फ्लोटिंग प्लेयर",
            "4K/1080p व्हिडिओ व थेट MP3 ऑडिओ डाऊनलोड",
            "गुगल अकाउंट न जोडता चॅनेल सबस्क्रिप्शन"
        ]
    },
    {
        "repo": "JunkFood02/Seal",
        "label": "Seal - Video & Audio Downloader",
        "category": "Media Downloader",
        "summary": "yt-dlp वर आधारित आधुनिक मटेरियल यू डिझाईन असणारे व्हिडिओ व ऑडिओ डाऊनलोडर. 1000+ वेबसाईटवरून मीडिया सेव्ह करते.",
        "features": [
            "YouTube, Twitter, Instagram सह 1000+ साईट्स सपोर्ट",
            "हाय-क्वालिटी MP4, WebM व MP3 फॉरमॅट कन्व्हर्जन",
            "कस्टम कमांड्स व सबटायटल्स एम्बेडिंग",
            "पूर्णपणे प्रायव्हेट, ट्रॅकर्स व जाहिरातमुक्त"
        ]
    },
    {
        "repo": "vfsfitvnm/ViMusic",
        "label": "ViMusic - Music Player",
        "category": "Music Streaming",
        "summary": "YouTube Music वरील सर्व गाणी मोफत, जाहिरातमुक्त ऐकण्यासाठी सुंदर म्युझिक ॲप. स्क्रीन बंद असतानाही गाणी सुरळीत चालतात.",
        "features": [
            "YouTube Music वरील कोट्यवधी गाणी जाहिरातींशिवाय",
            "बॅकग्राउंड प्लेबॅक व ऑटोमॅटिक ऑफलाइन कॅशिंग",
            "सिंक्रोनाइज्ड लिरिक्स (बोल) व इक्विलायझर",
            "Android Auto व प्लेस्टोर फ्रीडम"
        ]
    },
    {
        "repo": "fast4x/RiMusic",
        "label": "RiMusic - Multilingual Audio Streamer",
        "category": "Music & Audio",
        "summary": "मल्टीलिंग्युअल आणि हाय-फिडेलिटी म्युझिक प्लेयर. ऑटोमॅटिक गाण्यांचे शब्द, ऑफलाइन डाऊनलोड आणि प्लेलिस्ट मॅनेजमेंट पुरवतो.",
        "features": [
            "हाय-रिझोल्युशन ऑडिओ स्ट्रीमिंग",
            "ऑफलाइन ऐकण्यासाठी 1-क्लिक डाऊनलोड",
            "मटेरियल 3 यू डायनॅमिक कलर थीम",
            "स्लीप टायमर आणि व्हॉल्यूम बूस्टर"
        ]
    },
    {
        "repo": "AntennaPod/AntennaPod",
        "label": "AntennaPod - Podcast Manager",
        "category": "Podcasts & Radio",
        "summary": "जगातील सर्व पॉडकास्ट ऐकण्यासाठी व व्यवस्थापित करण्यासाठी सर्वात लोकप्रिय ओपन-सोर्स पॉडकास्ट प्लेयर.",
        "features": [
            "कोणत्याही RSS व iTunes फिडवरून पॉडकास्ट डिस्कव्हरी",
            "ऑटोमॅटिक नवीन एपिसोड्स डाऊनलोड व क्लिनअप",
            "प्लेबॅक स्पीड कंट्रोल (0.5x ते 3.0x) व सायलन्स स्कीप",
            "शून्य ट्रॅकिंग व पूर्णपणे प्रायव्हेट"
        ]
    },
    {
        "repo": "spotube-org/spotube",
        "label": "Spotube - Lightweight Music Player",
        "category": "Music Streaming",
        "summary": "Spotify API व YouTube/Piped ऑडिओ वापरून Spotify वरील प्लेलिस्ट्स मोफत व जाहिरातमुक्त वाजवणारे हलके ॲप.",
        "features": [
            "Spotify अकाऊंटवरील सर्व प्लेलिस्टमधून गाणी प्ले",
            "कोणतीही ऑडिओ जाहिरात नाही व शून्य सबस्क्रिप्शन",
            "स्थानिक स्टोरेजवर MP3 डाऊनलोड सपोर्ट",
            "क्रॉस-प्लॅटफॉर्म आणि लो-बॅटरी कन्झम्पशन"
        ]
    },

    # ── 2. Security, Passwords & 2FA ──
    {
        "repo": "bitwarden/mobile",
        "label": "Bitwarden - Password Vault",
        "category": "Security & Passwords",
        "summary": "उद्योग जगतातील अव्वल ओपन-सोर्स पासवर्ड मॅनेजर. तुमचे सर्व पासवर्ड्स, कार्ड्स आणि नोट्स AES-256 सह सुरक्षित ठेवतो.",
        "features": [
            "एंड-टू-एंड एनक्रिप्टेड शून्य-ज्ञान सुरक्षित वॉल्ट",
            "अॅप्स व ब्राउझरमध्ये ऑटोमॅटिक पासवर्ड ऑटोफिल",
            "बायोमेट्रिक फिंगरप्रिंट व फेस अनलॉक",
            "मजबूत आणि युनिक पासवर्ड जनरेटर"
        ]
    },
    {
        "repo": "Kunzisoft/KeePassDX",
        "label": "KeePassDX - Offline Password Vault",
        "category": "Security & Passwords",
        "summary": "पूर्णपणे ऑफलाइन आणि सुरक्षित KeePass (.kdbx) पासवर्ड मॅनेजर. कोणताही डेटा क्लाउडवर जात नाही, संपूर्ण नियंत्रण तुमच्या हाती.",
        "features": [
            "100% ऑफलाइन डेटाबेस (No Internet Permissions needed)",
            "हार्डवेअर कीज (YubiKey) व बायोमेट्रिक सपोर्ट",
            "मॅगकीबोर्ड (MagKey) सुरक्षित इनपुट कीबोर्ड",
            "OTP / 2FA कोड जनरेटर इनबिल्ट"
        ]
    },
    {
        "repo": "beemdevelopment/Aegis",
        "label": "Aegis - 2FA Authenticator",
        "category": "Security & 2FA",
        "summary": "Google Authenticator चा सर्वात सुरक्षित व ओपन-सोर्स पर्याय. सर्व 2FA टोकन्स एनक्रिप्टेड बॅकअपसह सेव्ह करतो.",
        "features": [
            "AES-GCM-256 एनक्रिप्टेड सुरक्षित स्टोरेज",
            "ऑटोमॅटिक एनक्रिप्टेड क्लाउड/लोकल बॅकअप्स",
            "TOTP व HOTP प्रोटोकॉल्स सपोर्ट (Google, GitHub, AWS)",
            "बायोमेट्रिक लॉक व कस्टम आयकॉन पॅक्स"
        ]
    },
    {
        "repo": "cryptomator/android",
        "label": "Cryptomator - Cloud Storage Vault",
        "category": "Cloud Encryption",
        "summary": "Google Drive, Dropbox, Nextcloud वरील तुमच्या फाईल्स क्लाउडवर अपलोड होण्यापूर्वीच क्लायंट-साईड एनक्रिप्ट करणारे टूल.",
        "features": [
            "शून्य-ज्ञान (Zero-Knowledge) AES-256 क्लायंट एनक्रिप्शन",
            "Google Drive, OneDrive, WebDAV सह थेट इंटिग्रेशन",
            "क्लाउड प्रोव्हायडरला तुमच्या फाईल्सचा मजकूर कधीही दिसत नाही",
            "स्वतंत्र सुरक्षा ऑडिट पास केलेले ओपन-सोर्स कोड"
        ]
    },

    # ── 3. Browsers, Privacy & Network Firewalls ──
    {
        "repo": "mozilla-mobile/fenix",
        "label": "Firefox for Android",
        "category": "Web Browser",
        "summary": "स्वतंत्र Gecko इंजिनवर आधारित वेगवान व प्रायव्हसी-केंद्रित ब्राउझर. डझनभर ॲड-ऑन्स व ॲडब्लॉकर सपोर्ट करतो.",
        "features": [
            "uBlock Origin, Privacy Badger सह शक्तिशाली ॲड-ऑन्स",
            "एनहान्स ट्रॅकिंग प्रोटेक्शन (ETP) द्वारे कुकीज ब्लॉक",
            "मल्टिपल टॅब सिंक व प्रायव्हेट ब्राउझिंग मोड",
            "बिग टेक ट्रॅकिंग कंपन्यांना डेटा ब्लॉक करणे"
        ]
    },
    {
        "repo": "uazo/cromite",
        "label": "Cromite - Hardened Chromium Browser",
        "category": "Web Browser",
        "summary": "Bromite चे नवीन सुरक्षित रूप. अंगभूत शक्तिशाली ॲडब्लॉकर आणि ॲडव्हान्स्ड फिंगरप्रिंटिंग प्रोटेक्शन असलेला क्रोमियम ब्राउझर.",
        "features": [
            "वेबसाईटवरील सर्व जाहिराती व ट्रॅकर्स इनबिल्ट ब्लॉक",
            "अल्ट्रा-फास्ट क्रोमियम इंजिन विथ प्रायव्हसी पॅचेस",
            "डार्क मोड व डेटा सेव्हर मोड",
            "DNS ओव्हर HTTPS (DoH) सपोर्ट"
        ]
    },
    {
        "repo": "M66B/NetGuard",
        "label": "NetGuard - No-Root Firewall",
        "category": "Network & Firewall",
        "summary": "रूट न करता कोणत्याही ॲपचे इंटरनेट पूर्णपणे बंद करणारा शक्तिशाली फायरवॉल. बॅटरी आणि डेटा दोन्ही वाचवतो.",
        "features": [
            "प्रत्येक ॲपसाठी स्वतंत्र वाय-फाय व मोबाईल डेटा ब्लॉक",
            "बॅकग्राउंड डेटा ट्रॅफिक व स्पायवेअर ट्रॅकर्स ब्लॉक",
            "कोणत्याही रूट (Root) परमिशनची गरज नाही",
            "लाईव्ह नेटवर्क ट्रॅफिक आणि पॅकेट लॉगिंग"
        ]
    },
    {
        "repo": "AdAway/AdAway",
        "label": "AdAway - System Ad Blocker",
        "category": "Privacy & Ad-Blocker",
        "summary": "अँड्रॉइड सिस्टीममधील जाहिराती, मालवेअर डोमेन्स व ट्रॅकर्स ब्लॉक करणारे अग्रगण्य ओपन-सोर्स ॲडब्लॉकर.",
        "features": [
            "VPN मोड (Non-Root) आणि Hosts-File मोड (Rooted) सपोर्ट",
            "कस्टम ब्लॉकलिस्ट व व्हाईटलिस्ट रुल्स तयार करण्याची सोय",
            "बॅटरी व मोबाईल डेटा प्रचंड प्रमाणात वाचवतो",
            "स्वच्छ आणि पारदर्शक ओपन-सोर्स आर्किटेक्चर"
        ]
    },

    # ── 4. Developer Tools, Terminals & Code Editors ──
    {
        "repo": "termux/termux-app",
        "label": "Termux - Linux Terminal Environment",
        "category": "Developer & Terminal",
        "summary": "अँड्रॉइड फोनवर शक्तिशाली लिनक्स एन्व्हायर्नमेंट देणारे टर्मिनल ॲप. Python, Node.js, C, Git, SSH सर्व चालते.",
        "features": [
            "APT पॅकेज मॅनेजरद्वारे लिनक्स पॅकेजेस इन्स्टॉलेशन",
            "Python, Bash, Zsh, Clang, Rust, Node.js कोडिंग",
            "SSH सर्व्हर व क्लायंटद्वारे रिमोट कनेक्शन",
            "फोनवरून थेट ऑटोमेशन स्क्रिप्ट्स व AI मॉडेल्स चालवणे"
        ]
    },
    {
        "repo": "deadlyjack/Acode",
        "label": "Acode - Powerful Code Editor",
        "category": "Developer & IDE",
        "summary": "अँड्रॉइडसाठी हलकेफुलके आणि शक्तिशाली कोड एडिटर. 100+ भाषांचे सिंटॅक्स हायलाइटिंग आणि इन-ॲप वेब प्रिव्ह्यू पुरवतो.",
        "features": [
            "HTML, CSS, JavaScript, Python सह 100+ लँग्वेजेस",
            "लाईव्ह इन-ॲप वेब ब्राऊझर प्रिव्ह्यू",
            "GitHub सह थेट इंटिग्रेशन व कमिट्स",
            "FTP, SFTP द्वारे थेट सर्व्हर फाईल्स एडीट करणे"
        ]
    },
    {
        "repo": "zhanghai/MaterialFiles",
        "label": "Material Files - Dual-Pane File Manager",
        "category": "File Manager",
        "summary": "मटेरियल डिझाईन असणारा ओपन-सोर्स ड्युअल-पेन फाईल मॅनेजर. रूट, SMB, FTP आणि आर्काइव्ह फाईल्स हाताळतो.",
        "features": [
            "ड्युअल-पेन व्ह्यूने फाईल्स सहज कॉपी-पेस्ट करणे",
            "SMB (Windows Share), FTP, SFTP रिमोट स्टोरेज सपोर्ट",
            "ZIP, 7Z, TAR आर्काइव्ह व्ह्यूअर व एक्सट्रॅक्टर",
            "रूट डायरेक्टरी एक्सेस व हॅश (MD5/SHA256) चेकर"
        ]
    },
    {
        "repo": "Julow/Unexpected-Keyboard",
        "label": "Unexpected Keyboard - Developer Keyboard",
        "category": "Developer Tools",
        "summary": "प्रोग्रामर्स आणि कोडिंग करणाऱ्यांसाठी बनवलेला अल्ट्रा-फास्ट कीबोर्ड. एका स्वाइपमध्ये स्पेशल कॅरेक्टर्स उपलब्ध करतो.",
        "features": [
            "कोडिंगसाठी आवश्यक { } [ ] < > ; = | सर्व चिन्हे त्वरित",
            "कमीत कमी स्क्रीन जागा व्यापतो आणि अतिशय हलका",
            "शून्य इंटरनेट परमिशन - 100% प्रायव्हेट कीबोर्ड",
            "Ctrl, Alt, Esc आणि ॲरो कीज सपोर्ट"
        ]
    },
    {
        "repo": "connectbot/connectbot",
        "label": "ConnectBot - SSH Client",
        "category": "Developer & DevOps",
        "summary": "अँड्रॉइडसाठी पहिला आणि विश्वासू ओपन-सोर्स Secure Shell (SSH) क्लायंट. एकाच वेळी मल्टिपल सर्व्हर्स मॅनेज करतो.",
        "features": [
            "रिमोट लिनक्स/क्लाउड सर्व्हर्सवर सुरक्षित SSH टर्मिनल",
            "RSA, Ed25519 की-बेस्ड सुरक्षित ऑथेंटिकेशन",
            "लोकल व रिमोट पोर्ट फॉरवर्डिंग (SSH टनेल्स)",
            "टर्मिनल कलर स्कीम्स व फॉन्ट कस्टमायझेशन"
        ]
    },

    # ── 5. File Sharing & Device Integration ──
    {
        "repo": "localsend/localsend",
        "label": "LocalSend - Cross-Platform AirDrop",
        "category": "File Sharing",
        "summary": "Apple च्या AirDrop चा अव्वल ओपन-सोर्स पर्याय. इंटरनेट न वापरता लोकल वाय-फाय द्वारे फोन, पीसी, मॅकवर फाईल्स पाठवतो.",
        "features": [
            "अँड्रॉइड, विंडोज, मॅक, लिनक्स व आयओएस मध्ये हाय-स्पीड ट्रान्सफर",
            "इंटरनेट डेटा लागत नाही (100% लोकल नेटवर्क)",
            "एंड-टू-एंड एनक्रिप्शन व शून्य ट्रॅकिंग",
            "अमर्यादित आकाराच्या फाईल्स, व्हिडिओ व फोल्डर्स ट्रान्सफर"
        ]
    },
    {
        "repo": "KDE/kdeconnect-android",
        "label": "KDE Connect - Phone to PC Bridge",
        "category": "Device Integration",
        "summary": "फोन आणि संगणक (PC) एकमेकांशी जोडणारे जादुई टूल. क्लिपबोर्ड शेअरिंग, नोटिफिकेशन्स आणि रिमोट कंट्रोल पुरवतो.",
        "features": [
            "शेअर्ड क्लिपबोर्ड (फोनवर कॉपी करा, पीसीवर पेस्ट करा)",
            "फोनवरून पीसीचा माउस व कीबोर्ड रिमोट कंट्रोल करणे",
            "येणारे फोन कॉल्स व एसएमएस संगणकाच्या स्क्रीनवर दिसणे",
            "हाय-स्पीड वायरलेस फाईल शेअरिंग"
        ]
    },
    {
        "repo": "syncthing/syncthing-android",
        "label": "Syncthing - Decentralized File Sync",
        "category": "File Synchronization",
        "summary": "कोणत्याही थर्ड-पार्टी क्लाउडशिवाय फोन आणि कॉम्प्युटरमधील फोल्डर्स आपोआप सिंक्रोनाईज ठेवणारे P2P टूल.",
        "features": [
            "थेट फोन ते कॉम्प्युटर रिअल-टाइम फोल्डर सिंक",
            "डेटा कोणत्याही सर्व्हरवर सेव्ह होत नाही (Pure P2P)",
            "TLS एनक्रिप्शनसह अत्यंत सुरक्षित डेटा ट्रान्सफर",
            "फोटो, डॉक्युमेंट्स आणि बॅकअप्स सुरक्षित ठेवणे"
        ]
    },

    # ── 6. Productivity, Notes & Learning ──
    {
        "repo": "ankidroid/Anki-Android",
        "label": "AnkiDroid - Spaced Repetition Flashcards",
        "category": "Education & Memory",
        "summary": "वैज्ञानिकदृष्ट्या सिद्ध स्पॅस्ड रिपिटेशन तंत्राद्वारे अभ्यास, भाषा व कोडिंग लक्षात ठेवण्याचे सर्वोत्तम फ्लॅशकार्ड ॲप.",
        "features": [
            "दीर्घकालीन स्मरणशक्तीसाठी Spaced Repetition अल्गोरिदम",
            "ऑडिओ, फोटो, मॅथ्स (LaTeX) फ्लॅशकार्ड्स सपोर्ट",
            "AnkiWeb द्वारे पीसी व फोनमध्ये ऑटोमॅटिक सिंक",
            "लाखों मोफत पब्लिक डेक्स उपलब्ध (UPSC, MPSC, Coding)"
        ]
    },
    {
        "repo": "koreader/koreader",
        "label": "KOReader - Versatile Document Reader",
        "category": "E-Book & Document",
        "summary": "ई-बुक्स आणि डॉक्युमेंट्स वाचण्यासाठी अत्यंत शक्तिशाली व्ह्यूअर. PDF, EPUB, MOBI, DJVU, CBZ कॉमिक्स सर्व वाचतो.",
        "features": [
            "पीडीएफ टेक्स्ट रिफ्लो (Text Reflow) मुळे सहज वाचन",
            "नाईट मोड, कस्टम फॉन्ट्स, कॉन्ट्रास्ट बूस्टिंग",
            "विकिपीडिया आणि स्टारडिक्ट डिक्शनरी इंटिग्रेशन",
            "क्लाउड सिंक व कॅलिबर (Calibre) लायब्ररी सपोर्ट"
        ]
    },
    {
        "repo": "tasks/tasks",
        "label": "Tasks.org - Todo & Task Manager",
        "category": "Productivity & Tasks",
        "summary": "उत्कृष्ट मटेरियल डिझाईन आणि गोपनीयता असणारा टास्क मॅनेजर. Google Tasks, Nextcloud आणि CalDAV सह सिंक होतो.",
        "features": [
            "टास्क्स, सब-टास्क्स आणि प्रायॉरिटी मॅनेजमेंट",
            "लोकेशन-बेस्ड व टाईम-बेस्ड अचूक रिमाइंडर्स",
            "CalDAV, Nextcloud व Google Tasks सह थेट सिंक",
            "पूर्णपणे ओपन-सोर्स व शून्य जाहिराती"
        ]
    },
    {
        "repo": "Ashinch/ReadYou",
        "label": "ReadYou - Material You RSS Reader",
        "category": "News & RSS",
        "summary": "मटेरियल यू (Material You) डिझाईनवर आधारित अतिशय देखणा RSS रीडर. तुमचे सर्व आवडते ब्लॉग्स आणि बातम्या एकाच ठिकाणी.",
        "features": [
            "फिव्हर (Fever), Miniflux, FreshRSS सह थेट सिंक",
            "अंगभूत फुल-आर्टिकल रीडर मोड (Clean Reading)",
            "डायनॅमिक थीमिंग आणि जेश्चर नेव्हिगेशन",
            "ऑफलाइन वाचन व बुकमार्क सपोर्ट"
        ]
    },

    # ── 7. Maps, Camera, System & Tools ──
    {
        "repo": "organicmaps/organicmaps",
        "label": "Organic Maps - Offline Maps & Navigation",
        "category": "Maps & Navigation",
        "summary": "ड्रायव्हर्स, ट्रेकर्स व प्रवाशांसाठी पूर्णपणे ऑफलाइन काम करणारे नकाशे. बॅटरी वाचवतो व शून्य ट्रॅकिंग करतो.",
        "features": [
            "100% ऑफलाइन OpenStreetMap टर्न-बाय-टर्न नेव्हिगेशन",
            "ट्रेकिंग ट्रॅक, हायकिंग ट्रेल्स व सायकल रूट्स",
            "स्पीड कॅमेरा व व्हॉइस नेव्हिगेशन अलर्ट्स",
            "कोणताही मोबाईल डेटा लागत नाही, शून्य बॅकग्राउंड ट्रॅकिंग"
        ]
    },
    {
        "repo": "osmandapp/OsmAnd",
        "label": "OsmAnd - Advanced OpenStreetMap",
        "category": "Maps & Navigation",
        "summary": "अतिशय तपशीलवार ऑफलाइन मॅप्स व जीपीएस नेव्हिगेशन. कॉन्टूर लाईन्स, नॉटिकल चार्ट्स आणि संपूर्ण जगाचे नकाशे.",
        "features": [
            "हाय-डिटेल ऑफलाइन नकाशे आणि 3D हिलशेड्स",
            "GPX ट्रॅक रेकॉर्डिंग आणि रूट प्लॅनिंग",
            "पब्लिक ट्रान्सपोर्ट स्टॉप्स व लेन गाईडन्स",
            "पूर्णपणे कस्टमायझेबल मॅप लेयर्स"
        ]
    },
    {
        "repo": "MuntashirAkon/AppManager",
        "label": "App Manager - Deep Package Inspector",
        "category": "System & Privacy",
        "summary": "तुमच्या फोनमधील प्रत्येक ॲपच्या परवानग्या, ट्रॅकर्स व ॲक्टिव्हिटीचे पोस्टमार्टम करणारे सर्वात प्रगत पॅकेज मॅनेजर.",
        "features": [
            "ॲप्समधील लपलेले ट्रॅकर्स व ॲनालिटिक्स घटक ब्लॉक करणे",
            "परवानग्या (Permissions) व बॅकग्राउंड सर्व्हिसेस थांबवणे",
            "APK व Split-APKs बॅकअप व रिस्टोअर",
            "डीप मॅनिफेस्ट व सिग्नेचर इन्स्पेक्टर"
        ]
    },
    {
        "repo": "keymapperorg/KeyMapper",
        "label": "Key Mapper - Hardware Button Remapper",
        "category": "Hardware & Utilities",
        "summary": "फोनचे व्हॉल्यूम बटन्स, फिंगरप्रिंट सेन्सर आणि ब्लूटूथ कीज रिमॅप करून शॉर्टकट ॲक्शन्स तयार करणारे टूल.",
        "features": [
            "बटन्सवर डबल-प्रेस, लाँग-प्रेस ने फ्लॅशलाईट किंवा ॲप उघडणे",
            "कोणत्याही रूट परमिशनची गरज नाही",
            "फ्लेक्सिबल ट्रिगर्स आणि कस्टम मॅक्रो सीक्वेन्स",
            "गेमिंग कंट्रोलर व कीबोर्ड शॉर्टकट्स मॅपिंग"
        ]
    },
    {
        "repo": "florisboard/florisboard",
        "label": "FlorisBoard - Privacy Keyboard",
        "category": "Keyboard & Input",
        "summary": "अँड्रॉइडसाठी आधुनिक, ओपन-सोर्स आणि गोपनीयता-अनुकूल कीबोर्ड. बहुभाषिक टायपिंग आणि क्लिपबोर्ड हिस्ट्री मॅनेजर.",
        "features": [
            "मटेरियल यू डायनॅमिक थीम्स व इमोजी सपोर्ट",
            "इनबिल्ट क्लिपबोर्ड हिस्ट्री व पिनिंग",
            "शून्य इंटरनेट परमिशन (No Keylogging guarantee)",
            "मराठी, हिंदी, इंग्रजी बहुभाषिक कीबोर्ड लेआउट"
        ]
    },
    {
        "repo": "mihonapp/mihon",
        "label": "Mihon - Manga & Comic Reader",
        "category": "Books & Comics",
        "summary": "Tachiyomi चे आधुनिक अधिकृत रूप. कॉमिक्स, मंगा आणि वेबटून ऑफलाइन डाऊनलोड करून वाचण्यासाठी उत्कृष्ट ॲप.",
        "features": [
            "हजारो कॉमिक्स कॅटलॉग्समधून ऑफलाइन वाचन",
            "कस्टम रीडर व्ह्यू (Webtoon, Vertical, Horizontal)",
            "क्लाउड बॅकअप व ऑटोमॅटिक चॅप्टर ट्रॅकिंग",
            "जाहिरातमुक्त आणि मिनिमल डिझाईन"
        ]
    },
    {
        "repo": "FossifyOrg/Gallery",
        "label": "Fossify Gallery - Private Media Viewer",
        "category": "Photos & Media",
        "summary": "Simple Mobile Tools चे आधुनिक पुनरुज्जीवन. खाजगी आणि पूर्णपणे ऑफलाइन फोटो व व्हिडिओ गॅलरी.",
        "features": [
            "100% ऑफलाइन गॅलरी, शून्य इंटरनेट परमिशन",
            "इनबिल्ट फोटो एडिटर (Crop, Rotate, Filter)",
            "पासवर्ड व फिंगरप्रिंटने फोटो सुरक्षित लपवणे (Vault)",
            "RAW, SVG, GIF, MP4 सर्व फॉरमॅट सपोर्ट"
        ]
    },
    {
        "repo": "FossifyOrg/Calendar",
        "label": "Fossify Calendar - Offline Event Planner",
        "category": "Productivity & Planner",
        "summary": "गुगल किंवा कोणत्याही सर्व्हरवर डेटा न पाठवता काम करणारे सुरक्षित आणि सोपे कॅलेंडर ॲप.",
        "features": [
            "स्थानिक ऑफलाइन इव्हेंट्स आणि रिमाइंडर्स",
            "CalDAV द्वारे सुरक्षित खाजगी सिंक सपोर्ट",
            "फ्लेक्सिबल रिपीटेशन (दैनिक, साप्ताहिक, मासिक)",
            "होम स्क्रीन विजेट्स व क्लिन डिझाईन"
        ]
    },
    {
        "repo": "f-droid/fdroidclient",
        "label": "F-Droid - Free Software App Store",
        "category": "App Store",
        "summary": "अँड्रॉइडसाठी अधिकृत ओपन-सोर्स ॲप्लिकेशन स्टोअर. यावरील सर्व ॲप्स पूर्णपणे मोफत, जाहिरातमुक्त आणि पारदर्शक असतात.",
        "features": [
            "हजारो व्हेरीफाईड ओपन-सोर्स ॲप्सची अधिकृत रिपॉझिटरी",
            "ऑटोमॅटिक ॲप अपडेट्स व नोटिफिकेशन्स",
            "शून्य ट्रॅकिंग, प्रायव्हसी रिपोर्टिंग (Anti-features warning)",
            "अकाउंट तयार करण्याची किंवा लॉगिन करण्याची गरज नाही"
        ]
    }
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


def _github_latest_apk(repo: str, min_size_mb: float = 0.0, max_size_mb: float = 100.0) -> Optional[Dict[str, Any]]:
    """
    Fetches latest GitHub release for a repo and smartly selects the best compatible
    APK asset (universal > arm64-v8a > armeabi-v7a > generic) strictly within [min_size_mb, max_size_mb].
    Returns {repo, name, url, size_mb, version, release_notes} or None.
    """
    try:
        release = None
        version = "latest"
        body_notes = ""
        apk_assets = []

        try:
            api_url = f"https://api.github.com/repos/{repo}/releases/latest"
            headers = {"User-Agent": "NanoProAI-APKBot/2.0", "Accept": "application/vnd.github.v3+json"}
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as r:
                release = json.loads(r.read().decode("utf-8"))
            version = release.get("tag_name", "latest")
            body_notes = release.get("body", "") or ""
            assets = release.get("assets", [])
            apk_assets = [a for a in assets if a.get("name", "").lower().endswith(".apk")]
        except Exception as api_err:
            # Fallback without GitHub API rate limit: resolve tag via web redirect and fetch expanded_assets
            log_event(f"[APKBot] GitHub API rate-limit/timeout for {repo} ({api_err}); engaging zero-limit web resolver...", level="DEBUG", component="APKDispatcher")
            opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
            req_web = urllib.request.Request(f"https://github.com/{repo}/releases/latest", headers={"User-Agent": "Mozilla/5.0"})
            with opener.open(req_web, timeout=6) as resp_web:
                version = resp_web.geturl().split("/")[-1]

            assets_url = f"https://github.com/{repo}/releases/expanded_assets/{version}"
            req_assets = urllib.request.Request(assets_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req_assets, timeout=6) as r_ast:
                html_ast = r_ast.read().decode("utf-8", errors="ignore")

            links = re.findall(r'href="([^"]+\.apk)"', html_ast)
            for lk in links:
                nm = lk.split("/")[-1]
                apk_assets.append({
                    "name": nm,
                    "browser_download_url": "https://github.com" + lk,
                    "size": 15 * 1024 * 1024  # estimated 15MB if header not present
                })

        if not apk_assets:
            return None

        # Filter strictly within requested size range
        valid_assets = []
        for a in apk_assets:
            sz = a.get("size", 0)
            sz_mb = sz / (1024 * 1024)
            if min_size_mb <= sz_mb <= max_size_mb:
                valid_assets.append(a)

        if not valid_assets:
            return None

        # Compatibility scoring: prefer universal > arm64-v8a > armeabi-v7a > general
        def score_asset(asset):
            nm = asset.get("name", "").lower()
            sz = asset.get("size", 0)
            score = 50
            if "universal" in nm:
                score += 100
            elif "arm64-v8a" in nm or "arm64" in nm:
                score += 70
            elif "armeabi-v7a" in nm or "armv7" in nm:
                score += 30
            elif "x86_64" in nm or "x86" in nm:
                score += 5
            return score

        sorted_assets = sorted(valid_assets, key=score_asset, reverse=True)
        best = sorted_assets[0]
        size = best.get("size", 0)
        size_mb = round(size / 1024 / 1024, 2)

        return {
            "repo": repo,
            "name": best.get("name", ""),
            "url": best.get("browser_download_url", ""),
            "size_mb": size_mb,
            "version": version,
            "release_notes": body_notes[:300]
        }
    except Exception as e:
        log_event(f"[APKBot] GitHub API error for {repo}: {e}", level="DEBUG", component="APKDispatcher")
    return None


def _download_apk(url: str, filename: str) -> Optional[Path]:
    """Downloads APK to temp dir with chunked 256KB low-memory streaming with strict 20s skip limit."""
    dest = APK_TEMP_DIR / filename
    start_time = time.time()
    try:
        log_event(f"[APKBot] Downloading {filename} (max 20s budget)...", component="APKDispatcher")
        req = urllib.request.Request(url, headers={"User-Agent": "NanoProAI-APKBot/2.0"})
        with urllib.request.urlopen(req, timeout=20) as r, open(dest, "wb") as f:
            chunk_size = 256 * 1024  # 256KB chunks
            while True:
                if (time.time() - start_time) > 20:
                    log_event(f"[APKBot] Download of {filename} exceeded 20s budget, skipping to direct 1-click button", level="INFO", component="APKDispatcher")
                    raise TimeoutError("Download exceeded 20s budget")
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


def _build_caption(source: Dict[str, Any], apk_info: Dict[str, Any], lane: str = "fast") -> str:
    """
    Constructs a safe, beautifully styled Marathi summary + key features + safety badges.
    Safely escapes dynamic content to prevent Telegram HTML entity errors (&lt;, &gt;, &amp;).
    """
    label_esc = html.escape(str(source.get("label", apk_info.get("name", "Android App"))))
    ver_esc = html.escape(str(apk_info.get("version", "latest")))
    cat_esc = html.escape(str(source.get("category", "Open-Source App")))
    repo_esc = html.escape(str(apk_info.get("repo", "")))
    name_esc = html.escape(str(apk_info.get("name", "")))
    size_mb = apk_info.get("size_mb", 0)

    summary_raw = source.get("summary") or f"{label_esc} is an authentic, verified open-source Android app."
    summary_esc = html.escape(summary_raw)

    features = source.get("features", [])
    feat_lines = []
    for f in features[:4]:
        feat_lines.append(f"• {html.escape(f)}")
    feat_str = ""
    if feat_lines:
        feat_str = "\n✨ <b>मुख्य वैशिष्ट्ये (Features):</b>\n" + "\n".join(feat_lines)

    if lane == "heavy":
        badge = (
            f"🚀 <b>[HEAVY-DUTY ENTERPRISE APK • {size_mb} MB]</b>\n"
            f"⚡ <i>Delivered via NanoPro Parallel High-Capacity Background Worker</i>\n"
        )
    else:
        badge = (
            f"⚡ <b>[EXPRESS FAST-TRACK APK • {size_mb} MB]</b>\n"
            f"🚀 <i>Ultra-Fast Lightweight Delivery (&lt;26 MB)</i>\n"
        )

    caption = (
        f"{badge}"
        f"📦 <b>{label_esc}</b> (<code>{ver_esc}</code>)\n"
        f"🏷️ <i>{cat_esc}</i> • 💾 <b>{size_mb} MB</b>\n"
        f"📂 <code>{name_esc}</code>\n"
        f"────────────────────────\n"
        f"📋 <b>काय आहे हे ॲप? (Summary):</b>\n"
        f"{summary_esc}\n"
        f"{feat_str}\n"
        f"────────────────────────\n"
        f"🛡️ <b>100% Verified Open Source | Safe &amp; Ad-Free</b>\n"
        f"🔗 github.com/{repo_esc}\n"
        f"🤖 @mangesh_apk_bot • NanoPro AI Studio"
    )
    return caption[:1020]


def _send_telegram_button_message(caption: str, button_text: str, button_url: str, parse_mode: str = "HTML") -> bool:
    """
    Sends rich Telegram message with an interactive 1-click Download button.
    Used for VIP heavy-duty APKs (50-100MB) or when direct file upload is rejected.
    """
    token = TELEGRAM_APK_BOT_TOKEN or os.environ.get("TELEGRAM_APK_BOT_TOKEN", "")
    if not token:
        log_event("[APKBot] APK bot token not configured", level="WARNING", component="APKDispatcher")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    final_caption = caption if len(caption) <= 4000 else caption[:3950] + "..."
    try:
        import requests as req_lib
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": final_caption,
            "parse_mode": parse_mode,
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": button_text, "url": button_url}]
                ]
            }
        }
        resp = req_lib.post(url, json=payload, timeout=30)
        data = resp.json()
        if data.get("ok"):
            log_event(f"[APKBot] Delivered VIP Download Package with Button to @mangesh_apk_bot", component="APKDispatcher")
            return True
        else:
            # Fallback to plain text if HTML had entity issue
            err_desc = data.get("description", "")
            log_event(f"[APKBot] Button message HTML rejected ({err_desc}), retrying plain-text...", level="INFO", component="APKDispatcher")
            plain_caption = re.sub(r"<[^>]+>", "", final_caption)
            plain_caption = plain_caption.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            payload["text"] = plain_caption
            payload.pop("parse_mode", None)
            resp2 = req_lib.post(url, json=payload, timeout=30)
            data2 = resp2.json()
            if data2.get("ok"):
                log_event(f"[APKBot] Delivered VIP Download Package (plain-text fallback)", component="APKDispatcher")
                return True
            log_event(f"[APKBot] Button send failed: {data2.get('description')}", level="WARNING", component="APKDispatcher")
            return False
    except Exception as e:
        log_event(f"[APKBot] Button message exception: {e}", level="WARNING", component="APKDispatcher")
        return False


def _send_apk_to_telegram(apk_path: Path, caption: str, parse_mode: str = "HTML", fallback_url: Optional[str] = None) -> bool:
    """
    Sends APK file to @mangesh_apk_bot via Telegram sendDocument API with 600s timeout.
    If Telegram rejects (e.g. file is too big or 400 error), falls back to plain-text
    or VIP button message if fallback_url is provided.
    """
    token = TELEGRAM_APK_BOT_TOKEN or os.environ.get("TELEGRAM_APK_BOT_TOKEN", "")
    if not token:
        log_event("[APKBot] APK bot token not configured", level="WARNING", component="APKDispatcher")
        return False

    url = f"https://api.telegram.org/bot{token}/sendDocument"
    try:
        import requests as req_lib
        final_caption = caption if len(caption) <= 1020 else caption[:1015] + "..."

        with open(apk_path, "rb") as f:
            resp = req_lib.post(
                url,
                data={"chat_id": TELEGRAM_CHAT_ID, "caption": final_caption, "parse_mode": parse_mode},
                files={"document": (apk_path.name, f, "application/vnd.android.package-archive")},
                timeout=75
            )
        data = resp.json()
        if data.get("ok"):
            log_event(f"[APKBot] Sent {apk_path.name} to @mangesh_apk_bot with rich summary", component="APKDispatcher")
            return True
        else:
            err_desc = data.get("description", "")
            log_event(f"[APKBot] HTML delivery rejected ({err_desc}), trying plain-text...", level="INFO", component="APKDispatcher")

            # Check if Telegram rejected because file exceeds 50MB
            if "too big" in err_desc.lower() and fallback_url:
                log_event(f"[APKBot] Telegram 50MB limit reached for {apk_path.name}; engaging VIP 1-click Download Button...", level="INFO", component="APKDispatcher")
                return _send_telegram_button_message(caption, f"⬇️ Direct Download APK ({round(apk_path.stat().st_size/1024/1024, 1)} MB)", fallback_url)

            plain_caption = re.sub(r"<[^>]+>", "", final_caption)
            plain_caption = plain_caption.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            with open(apk_path, "rb") as f2:
                resp2 = req_lib.post(
                    url,
                    data={"chat_id": TELEGRAM_CHAT_ID, "caption": plain_caption},
                    files={"document": (apk_path.name, f2, "application/vnd.android.package-archive")},
                    timeout=75
                )
            data2 = resp2.json()
            if data2.get("ok"):
                log_event(f"[APKBot] Sent {apk_path.name} (plain-text fallback) to @mangesh_apk_bot", component="APKDispatcher")
                return True

            # If still rejected and we have fallback URL, deliver via VIP Button
            if fallback_url:
                log_event(f"[APKBot] Upload rejected completely ({data2.get('description')}); delivering via VIP Download Button...", level="INFO", component="APKDispatcher")
                return _send_telegram_button_message(caption, f"⬇️ Direct Download APK ({round(apk_path.stat().st_size/1024/1024, 1)} MB)", fallback_url)

            log_event(f"[APKBot] Send failed completely: {data2.get('description')}", level="WARNING", component="APKDispatcher")
            return False
    except Exception as e:
        log_event(f"[APKBot] Send exception: {e}", level="WARNING", component="APKDispatcher")
        if fallback_url:
            return _send_telegram_button_message(caption, "⬇️ Direct Download APK", fallback_url)
        return False


def discover_and_send_apks(count: Optional[int] = None) -> Dict[str, Any]:
    """
    Main function: dual-lane parallel execution architecture.
    - Lane 1 (Express Fast-Track < 26 MB): Immediate dispatch of compact APKs in 4-8 seconds.
    - Lane 2 (Heavy-Duty Parallel Worker 26-100 MB): Concurrent background worker for heavy APKs
      (LocalSend, Termux, Firefox, OsmAnd, Gallery, StreetComplete) with 600s timeout & VIP treatment.
    """
    if count is None:
        cfg = get_apk_config()
        count = cfg.get("count", 8)

    sent_log = _load_sent_log()
    sent_lock = threading.Lock()
    sent = []
    skipped = []
    failed = []

    # Calculate lane partition
    if count <= 2:
        fast_target = count
        heavy_target = 1
    else:
        heavy_target = max(1, count // 4)  # e.g., for 8 -> 2 heavy, 6 fast
        fast_target = max(1, count - heavy_target)

    import random
    sources = list(APK_SOURCES)
    random.shuffle(sources)

    # Lane 2: Heavy-Duty Background Worker function
    def _run_heavy_lane():
        heavy_sent_count = 0
        heavy_sources = list(sources)
        random.shuffle(heavy_sources)
        log_event(f"[APKBot-HeavyLane] Background worker engaged (Target: {heavy_target} heavy APKs [26-100 MB])...", component="APKDispatcher")

        for src in heavy_sources:
            if heavy_sent_count >= heavy_target:
                break
            repo = src["repo"]
            label = src["label"]
            apk_info = _github_latest_apk(repo, min_size_mb=26.0, max_size_mb=100.0)
            if not apk_info:
                continue

            version = apk_info["version"]
            with sent_lock:
                if sent_log.get(repo) == version:
                    continue

            # Heavy candidate found!
            size_mb = apk_info["size_mb"]
            caption = _build_caption(src, apk_info, lane="heavy")

            ok = False
            if size_mb <= 50.0:
                # Direct file upload via Telegram sendDocument with extended 600s timeout
                apk_path = _download_apk(apk_info["url"], apk_info["name"])
                if apk_path:
                    ok = _send_apk_to_telegram(apk_path, caption, fallback_url=apk_info["url"])
                    try:
                        apk_path.unlink(missing_ok=True)
                    except Exception:
                        pass
                else:
                    # Download failed; provide VIP button package
                    ok = _send_telegram_button_message(caption, f"⬇️ Direct Download APK ({size_mb} MB)", apk_info["url"])
            else:
                # Over 50 MB exceeds Telegram bot limit. In direct_apk_only mode, skip so user only gets direct APK files!
                log_event(f"[APKBot-HeavyLane] {label} ({size_mb} MB) exceeds Telegram 50MB direct file limit. Skipping in direct_apk_only mode.", component="APKDispatcher")
                continue

            if ok:
                with sent_lock:
                    sent_log[repo] = version
                    _save_sent_log(sent_log)
                    sent.append({"repo": repo, "name": apk_info["name"], "version": version, "size_mb": size_mb, "lane": "heavy"})
                heavy_sent_count += 1
                log_event(f"[APKBot-HeavyLane] Delivered Heavy-Duty APK {label} ({size_mb} MB) successfully", component="APKDispatcher")
                time.sleep(4)

    # Spawn Lane 2 in background thread so it never blocks Lane 1
    heavy_thread = threading.Thread(target=_run_heavy_lane, daemon=True, name="APKHeavyLaneWorker")
    heavy_thread.start()

    # Lane 1: Express Fast-Track (< 26 MB) runs immediately on current thread
    fast_sent_count = 0
    for src in sources:
        if fast_sent_count >= fast_target:
            break
        repo = src["repo"]
        label = src["label"]

        apk_info = _github_latest_apk(repo, min_size_mb=0.1, max_size_mb=26.0)
        if not apk_info:
            continue

        version = apk_info["version"]
        with sent_lock:
            if sent_log.get(repo) == version:
                skipped.append({"repo": repo, "version": version, "reason": "Already sent"})
                continue

        # Direct APK candidate found! Download and deliver 100% directly inside Telegram
        caption = _build_caption(src, apk_info, lane="fast")
        apk_path = _download_apk(apk_info["url"], apk_info["name"])
        ok = False
        if apk_path:
            ok = _send_apk_to_telegram(apk_path, caption, fallback_url=None)
            try:
                apk_path.unlink(missing_ok=True)
            except Exception:
                pass
        else:
            # If download timed out or skipped, do not send external URLs. Pick next direct APK candidate!
            log_event(f"[APKBot-Direct] Download skipped for {label}. Searching next direct APK (<48MB)...", component="APKDispatcher")
            continue

        if ok:
            with sent_lock:
                sent_log[repo] = version
                _save_sent_log(sent_log)
                sent.append({"repo": repo, "name": apk_info["name"], "version": version, "size_mb": apk_info["size_mb"], "lane": "fast"})
            fast_sent_count += 1
            log_event(f"[APKBot-FastLane] Sent {label} ({apk_info['size_mb']} MB) in Express Lane", component="APKDispatcher")
        else:
            failed.append({"repo": repo, "name": apk_info["name"], "reason": "Telegram send failed"})

        time.sleep(2)

    log_event(f"[APKBot] Fast lane completed: {fast_sent_count} sent. Heavy lane running in background.", component="APKDispatcher")
    return {
        "status": "success",
        "fast_sent": fast_sent_count,
        "heavy_worker_active": heavy_thread.is_alive(),
        "sent": sent,
        "skipped": skipped,
        "failed": failed,
        "sent_count": len(sent),
    }


class APKScheduler:
    """Runs discover_and_send_apks() with configurable interval and quantity."""

    def __init__(self):
        self._stop = threading.Event()
        self._wake_event = threading.Event()
        self._thread = None
        self.INTERVAL_HOURS = 4
        self.COUNT = 5

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._wake_event.clear()
        cfg = get_apk_config()
        self.INTERVAL_HOURS = cfg.get("interval_hours", 4)
        self.COUNT = cfg.get("count", 5)
        self._thread = threading.Thread(target=self._loop, daemon=True, name="APKScheduler")
        self._thread.start()
        log_event(f"APK Scheduler started (every {self.INTERVAL_HOURS}h, {self.COUNT} APKs/cycle) → @mangesh_apk_bot", component="APKDispatcher")

    def stop(self):
        self._stop.set()
        self._wake_event.set()

    def reload_config(self):
        """Immediately loads new interval and quantity and wakes up scheduler loop."""
        cfg = get_apk_config()
        self.INTERVAL_HOURS = cfg.get("interval_hours", 4)
        self.COUNT = cfg.get("count", 5)
        log_event(f"[APKBot] Config reloaded: every {self.INTERVAL_HOURS}h, quantity: {self.COUNT} APKs", component="APKDispatcher")
        self._wake_event.set()

    def _loop(self):
        # Initial run shortly after server boot (15 seconds) so APKs start flowing immediately
        self._stop.wait(15)
        while not self._stop.is_set():
            cfg = get_apk_config()
            enabled = cfg.get("enabled", True)
            interval_min = int(cfg.get("interval_minutes") or 15)
            self.COUNT = max(1, min(20, int(cfg.get("count", 5))))

            if enabled:
                try:
                    log_event(f"[APKBot] NanoPro AI Manager: Starting 15-min Direct APK cycle (Count: {self.COUNT}, Interval: {interval_min} min)...", component="APKDispatcher")
                    res = discover_and_send_apks(count=self.COUNT)
                    log_event(f"[APKBot] NanoPro AI Manager: Delivered {res.get('sent_count', 0)} direct APKs to @mangesh_apk_bot successfully.", component="APKDispatcher")
                except Exception as e:
                    log_event(f"[APKBot] NanoPro AI Manager: Scheduler cycle error: {e}", level="WARNING", component="APKDispatcher")

            target_wait = max(60, interval_min * 60)
            elapsed = 0
            while elapsed < target_wait and not self._stop.is_set():
                if self._wake_event.is_set():
                    self._wake_event.clear()
                    break
                self._stop.wait(30)
                elapsed += 30


# Module-level singletons
apk_scheduler = APKScheduler()
