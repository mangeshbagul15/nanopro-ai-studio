"""Single place that decides what runs on the cloud host vs the local compute lane."""

import os


def _truthy(name: str, default: str = "") -> bool:
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes", "on")


def is_cloud() -> bool:
    return bool(os.environ.get("RENDER") or os.environ.get("IS_CLOUD"))


def cloud_safe_mode() -> bool:
    """Cloud hosts run the thin gateway profile unless explicitly opted out."""
    return is_cloud() and _truthy("NANOPRO_CLOUD_SAFE", "1")


def heavy_lane_enabled() -> bool:
    """Video, APK, archives and bulk engine work belong to the local lane."""
    if _truthy("NANOPRO_HEAVY_LANE", "0"):
        return True
    return not is_cloud()


HEAVY_PATH_PREFIXES = (
    "/api/sql_video",
    "/api/video",
    "/api/tech_video",
    "/api/apk",
    "/api/heygen",
)

HEAVY_PATH_EXACT = {
    "/api/backup/create",
    "/api/banking/duckdb/backup_s3",
}

HEAVY_PATH_ALLOWED = (
    "/api/sql_video/presets",
    "/api/sql_video/generate_prompt",
    "/api/video/2026_matrix_catalog",
    "/api/video/modern_models",
    "/api/video/matrix/full_catalog",
    "/api/apk/status",
    "/api/apk/config",
    "/api/heygen/status",
)

HEAVY_FEATURE_MESSAGE = (
    "This feature runs on the local compute lane (laptop), not the free cloud host. "
    "Open NanoPro on the laptop tunnel or set NANOPRO_HEAVY_LANE=1 on a paid host."
)


def is_blocked_heavy_path(path: str) -> bool:
    if heavy_lane_enabled():
        return False
    if path in HEAVY_PATH_EXACT:
        return True
    for allowed in HEAVY_PATH_ALLOWED:
        if path == allowed or path.startswith(allowed + "/"):
            return False
    return any(path == p or path.startswith(p + "/") for p in HEAVY_PATH_PREFIXES)
