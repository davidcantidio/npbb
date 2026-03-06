"""Schemas do endpoint publico de conclusao de gamificacao."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class GamificacaoCompleteRequest(BaseModel):
    gamificacao_id: int = Field(ge=1)
    gamificacao_completed: bool


class GamificacaoCompleteResponse(BaseModel):
    ativacao_lead_id: int
    gamificacao_id: int
    gamificacao_completed: bool
    gamificacao_completed_at: datetime | None = None
