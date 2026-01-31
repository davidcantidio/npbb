"""Esquemas de solicitacao de ingressos."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.models import SolicitacaoIngressoStatus, SolicitacaoIngressoTipo


class SolicitacaoIngressoCreate(BaseModel):
    cota_id: int
    tipo: SolicitacaoIngressoTipo
    indicado_email: str | None = None


class SolicitacaoIngressoRead(BaseModel):
    id: int
    cota_id: int
    solicitante_email: str
    indicado_email: str | None
    status: SolicitacaoIngressoStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IngressoAtivoListItem(BaseModel):
    cota_id: int
    evento_id: int
    evento_nome: str
    diretoria_id: int
    diretoria_nome: str
    total: int
    usados: int
    disponiveis: int
    data_inicio: date | None = None
    data_fim: date | None = None

    model_config = ConfigDict(from_attributes=True)
