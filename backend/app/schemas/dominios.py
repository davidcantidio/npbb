"""Esquemas de leitura para dominios (dicionarios) usados no front."""

from pydantic import BaseModel, ConfigDict


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
