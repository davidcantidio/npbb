"""Esquemas Pydantic para leitura de agências."""

from pydantic import BaseModel, ConfigDict


class AgenciaRead(BaseModel):
    id: int
    nome: str
    dominio: str

    model_config = ConfigDict(from_attributes=True)
