"""Schemas para conversoes de lead."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.models import LeadConversaoTipo


class LeadConversaoCreate(BaseModel):
    tipo: LeadConversaoTipo
    acao_nome: Optional[str] = None
    fonte_origem: Optional[str] = None
    evento_id: Optional[int] = None
    data_conversao_evento: Optional[datetime] = None


class LeadConversaoRead(LeadConversaoCreate):
    id: int
    lead_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
