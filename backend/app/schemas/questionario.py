"""Schemas do modulo de Questionario (por evento) - MVP."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

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


class QuestionarioOpcaoWrite(BaseModel):
    id: int | None = Field(default=None, ge=1)
    ordem: int = Field(ge=1)
    texto: str = Field(min_length=1, max_length=200)

    @field_validator("texto", mode="before")
    @classmethod
    def normalize_texto(cls, value: str):
        return value.strip() if isinstance(value, str) else value


class QuestionarioPerguntaWrite(BaseModel):
    id: int | None = Field(default=None, ge=1)
    ordem: int = Field(ge=1)
    tipo: TipoPergunta
    texto: str = Field(min_length=1, max_length=500)
    obrigatoria: bool = False
    opcoes: list[QuestionarioOpcaoWrite] = Field(default_factory=list)

    @field_validator("texto", mode="before")
    @classmethod
    def normalize_texto(cls, value: str):
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_opcoes_objetivas(self):
        if (
            self.tipo in {TipoPergunta.OBJETIVA_UNICA, TipoPergunta.OBJETIVA_MULTIPLA}
            and not self.opcoes
        ):
            raise ValueError("opcoes obrigatorias para perguntas objetivas")
        return self


class QuestionarioPaginaWrite(BaseModel):
    id: int | None = Field(default=None, ge=1)
    ordem: int = Field(ge=1)
    titulo: str = Field(min_length=1, max_length=200)
    descricao: str | None = Field(default=None, max_length=200)
    perguntas: list[QuestionarioPerguntaWrite] = Field(default_factory=list)

    @field_validator("titulo", mode="before")
    @classmethod
    def normalize_titulo(cls, value: str):
        return value.strip() if isinstance(value, str) else value

    @field_validator("descricao", mode="before")
    @classmethod
    def normalize_descricao(cls, value: str | None):
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value


class QuestionarioEstruturaWrite(BaseModel):
    paginas: list[QuestionarioPaginaWrite] = Field(default_factory=list)
