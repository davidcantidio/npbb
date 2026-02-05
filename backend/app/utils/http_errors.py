"""Helpers para erros HTTP estruturados.

Padrao (detail):
{
  "code": "SOME_CODE",
  "message": "Mensagem humana",
  "field": "campo_opcional"
}
"""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException


def raise_http_error(
    status_code: int,
    *,
    code: str,
    message: str,
    field: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    detail: dict[str, Any] = {"code": code, "message": message}
    if field:
        detail["field"] = field
    if extra:
        detail.update(extra)
    raise HTTPException(status_code=status_code, detail=detail)
