"""Esquemas de leitura para dominios (dicionarios) usados no front."""

from pydantic import BaseModel, ConfigDict, Field


class DiretoriaRead(BaseModel):
    id: int
    nome: str

    model_config = ConfigDict(from_attributes=True)


class DivisaoDemandanteRead(BaseModel):
    id: int
    nome: str

    model_config = ConfigDict(from_attributes=True)


class TipoEventoRead(BaseModel):
    id: int
    nome: str

    model_config = ConfigDict(from_attributes=True)


class SubtipoEventoRead(BaseModel):
    id: int
    tipo_id: int
    nome: str

    model_config = ConfigDict(from_attributes=True)


class TerritorioRead(BaseModel):
    id: int
    nome: str

    model_config = ConfigDict(from_attributes=True)


class TagRead(BaseModel):
    id: int
    nome: str

    model_config = ConfigDict(from_attributes=True)


class StatusEventoRead(BaseModel):
    id: int
    nome: str

    model_config = ConfigDict(from_attributes=True)


class TagCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=80)
