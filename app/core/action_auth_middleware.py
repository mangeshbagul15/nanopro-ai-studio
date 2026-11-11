"""Session policy for the sensitive API surface.

Handlers are easy to forget, so the gate lives in one ASGI middleware: any
request to a sensitive prefix needs a valid NanoPro session, and the
credential-management prefixes additionally need the admin role. The WhatsApp
webhook stays public because Meta calls it without a browser session.
"""
import json
from typing import Iterable, Optional, Tuple

from app.core.api_auth import session_user_from_headers

EXEMPT_PATHS = frozenset({"/api/whatsapp/webhook", "/api/telegram/webhook"})

DANGER_PREFIXES = (
    "/api/admin/",
    "/api/vault/",
    "/api/backup/",
    "/api/connections/",
    "/api/communication/",
    "/api/telegram/",
    "/api/whatsapp/",
    "/api/sms/",
    "/api/notifications/",
    "/api/integrations/",
    "/api/storage/",
    "/api/agents/",
    "/api/banking/",
    "/api/dms/",
    "/api/operations/",
    "/api/qa/",
    "/api/career/",
    "/api/amazon/",
    "/api/research/",
    "/api/image/",
    "/api/video/",
    "/api/sql_video/",
    "/api/tech_video/",
    "/api/document/",
    "/api/assistant/",
    "/api/automation/",
    "/api/scheduler/",
    "/api/identity/",
    "/api/data_modeling/",
    "/api/data_analyst/",
    "/api/data_science/",
    "/api/sql_studio/",
    "/api/coding/",
    "/api/data_engineer/",
    "/api/de_modern/",
    "/api/manager/",
    "/api/antigravity/",
    "/api/logs/",
    "/api/v2/",
)

ADMIN_PREFIXES = ("/api/admin/", "/api/vault/", "/api/backup/")


def _header(scope, name: bytes) -> str:
    for key, value in scope.get("headers") or ():
        if key == name:
            return value.decode("latin-1")
    return ""


async def _send_response(send, status: int, detail: str) -> None:
    body = json.dumps({"detail": detail}).encode()
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"application/json"),
                (b"cache-control", b"no-store"),
                (b"access-control-allow-origin", b"*"),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


class ActionAuthMiddleware:
    def __init__(
        self,
        app,
        danger_prefixes: Iterable[str] = DANGER_PREFIXES,
        admin_prefixes: Iterable[str] = ADMIN_PREFIXES,
        exempt_paths: Iterable[str] = EXEMPT_PATHS,
    ):
        self.app = app
        self.danger_prefixes: Tuple[str, ...] = tuple(danger_prefixes)
        self.admin_prefixes: Tuple[str, ...] = tuple(admin_prefixes)
        self.exempt_paths = frozenset(exempt_paths)

    def _needs_session(self, path: str) -> bool:
        if path in self.exempt_paths:
            return False
        return path.startswith(self.danger_prefixes)

    def _needs_admin(self, path: str) -> bool:
        return path.startswith(self.admin_prefixes)

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            return await self.app(scope, receive, send)
        path = scope.get("path") or ""
        if scope.get("method") == "OPTIONS" or not self._needs_session(path):
            return await self.app(scope, receive, send)

        user: Optional[dict] = session_user_from_headers(
            cookie_header=_header(scope, b"cookie"),
            x_session_token=_header(scope, b"x-session-token"),
            authorization=_header(scope, b"authorization"),
        )
        if not user:
            await _send_response(
                send,
                401,
                "Authentication required. Please log in to NanoPro AI Studio.",
            )
            return
        if self._needs_admin(path) and user.get("role") != "admin" and user.get("username") != "nanopro":
            await _send_response(send, 403, "Super Admin access required for this action.")
            return
        return await self.app(scope, receive, send)
