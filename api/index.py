"""
Vercel Python serverless entry point.

Vercel routes /api/* to this file. The backend FastAPI app has routes at
/graph/*, /gaps/*, etc., so we strip the /api prefix before handing off.
"""
import sys
import os

_backend = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if _backend not in sys.path:
    sys.path.insert(0, _backend)

from main import app as _fastapi_app  # noqa: E402
from starlette.types import ASGIApp, Scope, Receive, Send


class _StripApiPrefix:
    """Strip /api so FastAPI routes (/graph/build etc.) match correctly."""

    def __init__(self, inner: ASGIApp) -> None:
        self.inner = inner

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] in ("http", "websocket"):
            path: str = scope.get("path", "")
            if path.startswith("/api"):
                stripped = path[4:] or "/"
                scope = {**scope, "path": stripped, "raw_path": stripped.encode()}
        await self.inner(scope, receive, send)


app = _StripApiPrefix(_fastapi_app)
