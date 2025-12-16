"""Esquemas Pydantic para leitura de eventos."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class EventoListItem(BaseModel):
    id: int
    qr_code_url: Optional[str] = None
    nome: str

    data_inicio_prevista: Optional[date] = None
    data_fim_prevista: Optional[date] = None
    data_inicio_realizada: Optional[date] = None
    data_fim_realizada: Optional[date] = None

    cidade: str
    estado: str

    diretoria_id: Optional[int] = None
    agencia_id: int
    status: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventoRead(BaseModel):
    id: int
    thumbnail: Optional[str] = None
    divisao_demandante: Optional[str] = None
    qr_code_url: Optional[str] = None

    nome: str
    descricao: str

    data_inicio_prevista: Optional[date] = None
    data_inicio_realizada: Optional[date] = None
    data_fim_prevista: Optional[date] = None
    data_fim_realizada: Optional[date] = None

    publico_projetado: Optional[int] = None
    publico_realizado: Optional[int] = None

    concorrencia: bool
    cidade: str
    estado: str

    agencia_id: int
    diretoria_id: Optional[int] = None
    gestor_id: Optional[int] = None
    tipo_id: int
    subtipo_id: Optional[int] = None

    status: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

