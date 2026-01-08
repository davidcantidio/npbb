"""Schemas do modulo de Questionario (por evento) - MVP."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.models.models import TipoPergunta


class QuestionarioOpcaoRead(BaseModel):
    id: int
    ordem: int
    texto: str

    model_config = ConfigDict(from_attributes=True)


class QuestionarioPerguntaRead(BaseModel):
    id: int
    ordem: int
    tipo: TipoPergunta
    texto: str
    obrigatoria: bool
    opcoes: list[QuestionarioOpcaoRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class QuestionarioPaginaRead(BaseModel):
    id: int
    ordem: int
    titulo: str
    descricao: str | None = None
    perguntas: list[QuestionarioPerguntaRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class QuestionarioEstruturaRead(BaseModel):
    evento_id: int
    paginas: list[QuestionarioPaginaRead] = Field(default_factory=list)
