"""Clock-skew correction for outbound signed requests.

The workstation clock can drift by hours. AWS SigV4 rejects requests whose
signature timestamp is off by more than 15 minutes, and OAuth JWT assertions
appear already expired. This module measures the offset against an HTTPS
server's Date header and gives the SDKs a corrected UTC clock without touching
the operating system time.
"""

import datetime as _dt
import email.utils
import logging
import threading
import time
import urllib.request
from typing import Optional

logger = logging.getLogger("NanoPro.ClockSync")

_SYNC_HOSTS = ("https://www.google.com", "https://aws.amazon.com")
_REFRESH_SECONDS = 600

_lock = threading.Lock()
_offset_seconds = 0.0
_last_sync = 0.0
_last_error: Optional[str] = None


def _measure_offset(timeout: float = 5.0) -> Optional[float]:
    for host in _SYNC_HOSTS:
        try:
            req = urllib.request.Request(host, method="HEAD", headers={"User-Agent": "NanoPro-ClockSync"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                server_date = resp.headers.get("Date")
            if not server_date:
                continue
            server_dt = email.utils.parsedate_to_datetime(server_date)
            if server_dt.tzinfo is None:
                server_dt = server_dt.replace(tzinfo=_dt.timezone.utc)
            return (server_dt - _dt.datetime.now(_dt.timezone.utc)).total_seconds()
        except Exception:
            continue
    return None


def get_offset(refresh_seconds: int = _REFRESH_SECONDS) -> float:
    global _offset_seconds, _last_sync, _last_error
    with _lock:
        if time.time() - _last_sync > refresh_seconds:
            measured = _measure_offset()
            if measured is None:
                _last_error = "HTTPS Date header unavailable; using system clock"
            else:
                _offset_seconds = measured
                _last_error = None
                if abs(measured) >= 60:
                    logger.warning("System clock is %.0f seconds off from internet time; compensating for signed requests.", measured)
            _last_sync = time.time()
        return _offset_seconds


def now_utc() -> _dt.datetime:
    """UTC now (naive) corrected for local clock drift."""
    return _dt.datetime.now(_dt.timezone.utc).replace(tzinfo=None) + _dt.timedelta(seconds=get_offset())


def status() -> dict:
    offset = get_offset()
    return {
        "offset_seconds": round(offset, 1),
        "system_utc": _dt.datetime.now(_dt.timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds"),
        "corrected_utc": now_utc().isoformat(timespec="seconds"),
        "error": _last_error,
    }


def apply_botocore_patch() -> bool:
    """Route botocore's SigV4 timestamp through the corrected clock."""
    try:
        import botocore.auth as boto_auth
    except Exception:
        return False
    if getattr(boto_auth, "_nanopro_clock_patched", False):
        return True
    boto_auth.get_current_datetime = now_utc
    boto_auth._nanopro_clock_patched = True
    logger.info("botocore signing clock patched with measured skew correction.")
    return True
