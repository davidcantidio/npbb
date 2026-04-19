"""Propagate X-Request-ID for correlating HTTP logs with import pipeline events."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.observability.import_events import new_request_id, reset_request_id, set_request_id


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        incoming = (request.headers.get("X-Request-ID") or "").strip()
        rid = incoming or new_request_id()
        token = set_request_id(rid)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = rid
            return response
        finally:
            reset_request_id(token)
