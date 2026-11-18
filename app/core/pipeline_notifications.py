"""Alert recipients and the dispatch audit log for the live pipeline.

Both are stored as JSON in ``s3://<bucket>/config/`` so they survive a Render
redeploy, with a local copy under ``data/state/pipeline/`` as the fallback when
S3 is unreachable. Nothing here is seeded with sample data: an empty log means
no alert has been sent yet.
"""
from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

IST = timezone(timedelta(hours=5, minutes=30))
CONFIG_KEY = "config/alerts.json"
LOG_KEY = "config/notification_log.json"
LOG_LIMIT = 50
CONFIG_TTL_S = 30.0
LOG_TTL_S = 15.0

_LOCK = threading.RLock()
_CONFIG_CACHE: Dict[str, Any] = {"at": 0.0, "value": None}
_LOG_CACHE: Dict[str, Any] = {"at": 0.0, "value": None}


def _local_dir() -> str:
    path = os.path.join("data", "state", "pipeline")
    os.makedirs(path, exist_ok=True)
    return path


def _local_path(key: str) -> str:
    return os.path.join(_local_dir(), key.rsplit("/", 1)[-1])


def _s3():
    from app.core.sftp_ingestion import _s3 as sftp_s3

    return sftp_s3()


def _bucket() -> str:
    from app.core.sftp_ingestion import _bucket as sftp_bucket

    return sftp_bucket()


def _read(key: str, default: Any) -> Any:
    try:
        body = _s3().get_object(Bucket=_bucket(), Key=key)["Body"].read()
        value = json.loads(body)
        if isinstance(value, type(default)):
            return value
    except Exception:
        pass
    try:
        with open(_local_path(key), "r", encoding="utf-8") as handle:
            value = json.load(handle)
        if isinstance(value, type(default)):
            return value
    except Exception:
        pass
    return default


def _write(key: str, value: Any) -> None:
    body = json.dumps(value, indent=2, default=str)
    try:
        with open(_local_path(key), "w", encoding="utf-8") as handle:
            handle.write(body)
    except Exception:
        pass
    try:
        _s3().put_object(Bucket=_bucket(), Key=key, Body=body.encode("utf-8"),
                         ContentType="application/json")
    except Exception:
        pass


def _defaults() -> Dict[str, Any]:
    recipients = [item.strip().lower() for item in
                  (os.environ.get("NANOPRO_ALERT_RECIPIENTS") or "").replace(";", ",").split(",")
                  if item.strip()]
    return {
        "sender": (os.environ.get("NANOPRO_ALERT_SENDER") or "").strip(),
        "recipients": recipients,
        "telegram_channel": (os.environ.get("NANOPRO_TELEGRAM_CHAT") or "").strip(),
        "telegram_enabled": True,
        "whatsapp_number": (os.environ.get("NANOPRO_WHATSAPP_NUMBER") or "").strip(),
        "whatsapp_enabled": True,
    }


def config(force: bool = False) -> Dict[str, Any]:
    now = time.time()
    if not force and _CONFIG_CACHE["value"] is not None and now - _CONFIG_CACHE["at"] < CONFIG_TTL_S:
        return dict(_CONFIG_CACHE["value"])
    value = _defaults()
    stored = _read(CONFIG_KEY, {})
    if isinstance(stored, dict):
        for key in value:
            if key in stored:
                value[key] = stored[key]
    value["recipients"] = [str(item).strip().lower() for item in (value.get("recipients") or []) if str(item).strip()]
    _CONFIG_CACHE.update({"at": now, "value": value})
    return dict(value)


def save_config(**kwargs: Any) -> Dict[str, Any]:
    with _LOCK:
        conf = config(force=True)
        for key in ("sender", "telegram_channel", "whatsapp_number"):
            if kwargs.get(key) is not None:
                conf[key] = str(kwargs[key]).strip()
        for key in ("telegram_enabled", "whatsapp_enabled"):
            if kwargs.get(key) is not None:
                conf[key] = bool(kwargs[key])
        if kwargs.get("recipients") is not None:
            values = kwargs["recipients"]
            if isinstance(values, str):
                values = values.replace(";", ",").split(",")
            conf["recipients"] = [str(value).strip().lower() for value in values if str(value).strip()]
        _write(CONFIG_KEY, conf)
        _CONFIG_CACHE.update({"at": time.time(), "value": conf})
        return dict(conf)


def add_recipient(email: str) -> Dict[str, Any]:
    email = str(email or "").strip().lower()
    if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        raise ValueError("Invalid email address.")
    conf = config(force=True)
    if email not in conf["recipients"]:
        conf["recipients"].append(email)
        _write(CONFIG_KEY, conf)
        _CONFIG_CACHE.update({"at": time.time(), "value": conf})
    return dict(conf)


def remove_recipient(email: str) -> Dict[str, Any]:
    email = str(email or "").strip().lower()
    conf = config(force=True)
    if email in conf["recipients"]:
        conf["recipients"].remove(email)
        _write(CONFIG_KEY, conf)
        _CONFIG_CACHE.update({"at": time.time(), "value": conf})
    return dict(conf)


def logs(limit: int = LOG_LIMIT) -> List[Dict[str, Any]]:
    now = time.time()
    if _LOG_CACHE["value"] is None or now - _LOG_CACHE["at"] >= LOG_TTL_S:
        stored = _read(LOG_KEY, [])
        _LOG_CACHE.update({"at": now, "value": stored if isinstance(stored, list) else []})
    return list(_LOG_CACHE["value"])[:limit]


def append(entry: Dict[str, Any]) -> None:
    with _LOCK:
        current = logs(LOG_LIMIT)
        current.insert(0, entry)
        current = current[:LOG_LIMIT]
        _write(LOG_KEY, current)
        _LOG_CACHE.update({"at": time.time(), "value": current})


def stamp() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")
