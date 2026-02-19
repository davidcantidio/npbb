"""Esquemas do dominio de ativos (cotas de ingressos)."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class AtivoAssignPayload(BaseModel):
    quantidade: int = Field(ge=0)


class AtivoListItem(BaseModel):
    id: int
    evento_id: int
    evento_nome: str
    diretoria_id: int
    diretoria_nome: str
    total: int
    usados: int
    disponiveis: int
    percentual_usado: float
    data_inicio: date | None = None
    data_fim: date | None = None

    model_config = ConfigDict(from_attributes=True)
