"""Structured JSON logs for lead import flows (ETL, upload, Gold pipeline)."""

from __future__ import annotations

import json
import logging
import os
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

_request_id_ctx: ContextVar[str | None] = ContextVar("npbb_request_id", default=None)


def get_request_id() -> str | None:
    return _request_id_ctx.get()


def set_request_id(value: str | None) -> Any:
    return _request_id_ctx.set(value)


def reset_request_id(token: Any) -> None:
    _request_id_ctx.reset(token)


def new_request_id() -> str:
    return str(uuid.uuid4())


def session_token_prefix(token: str | None, *, max_len: int = 10) -> str | None:
    if not token:
        return None
    t = str(token).strip()
    if not t:
        return None
    return t[:max_len]


def _json_default(value: Any) -> str:
    return str(value)


def log_import_event(logger: logging.Logger, event: str, level: int = logging.INFO, **fields: Any) -> None:
    """Emit one JSON log line for Loki / log aggregators (component=lead_import)."""
    if os.getenv("NPBB_IMPORT_JSON_LOGS", "1").strip().lower() in {"0", "false", "no"}:
        parts = " ".join(f"{k}={v!r}" for k, v in fields.items() if v is not None)
        msg = f"lead_import.{event}" + (f" {parts}" if parts else "")
        logger.log(level, msg)
        return

    rid = get_request_id()
    payload: dict[str, Any] = {
        "component": "lead_import",
        "event": event,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    if rid:
        payload["request_id"] = rid
    for key, value in fields.items():
        if value is not None:
            payload[key] = value
    line = json.dumps(payload, ensure_ascii=False, default=_json_default, separators=(",", ":"))
    logger.log(level, line)
