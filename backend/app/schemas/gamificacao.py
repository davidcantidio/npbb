"""Schemas do modulo de Gamificacao (por evento) - MVP."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


def _normalize_required(text: str, *, field_name: str) -> str:
    value = (text or "").strip()
    if not value:
        raise ValueError(f"{field_name} obrigatorio")
    return value


class GamificacaoRead(BaseModel):
    id: int
    evento_id: int
    nome: str
    descricao: str
    premio: str
    titulo_feedback: str
    texto_feedback: str

    model_config = ConfigDict(from_attributes=True)


class GamificacaoCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    descricao: str = Field(min_length=1, max_length=240)
    premio: str = Field(min_length=1, max_length=200)
    titulo_feedback: str = Field(min_length=1, max_length=200)
    texto_feedback: str = Field(min_length=1, max_length=240)

    @model_validator(mode="after")
    def normalize_strings(self):
        return self.model_copy(
            update={
                "nome": _normalize_required(self.nome, field_name="nome"),
                "descricao": _normalize_required(self.descricao, field_name="descricao"),
                "premio": _normalize_required(self.premio, field_name="premio"),
                "titulo_feedback": _normalize_required(self.titulo_feedback, field_name="titulo_feedback"),
                "texto_feedback": _normalize_required(self.texto_feedback, field_name="texto_feedback"),
            }
        )


class GamificacaoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=150)
    descricao: str | None = Field(default=None, min_length=1, max_length=240)
    premio: str | None = Field(default=None, min_length=1, max_length=200)
    titulo_feedback: str | None = Field(default=None, min_length=1, max_length=200)
    texto_feedback: str | None = Field(default=None, min_length=1, max_length=240)

    @model_validator(mode="after")
    def normalize_strings(self):
        update: dict[str, str] = {}
        if self.nome is not None:
            update["nome"] = _normalize_required(self.nome, field_name="nome")
        if self.descricao is not None:
            update["descricao"] = _normalize_required(self.descricao, field_name="descricao")
        if self.premio is not None:
            update["premio"] = _normalize_required(self.premio, field_name="premio")
        if self.titulo_feedback is not None:
            update["titulo_feedback"] = _normalize_required(self.titulo_feedback, field_name="titulo_feedback")
        if self.texto_feedback is not None:
            update["texto_feedback"] = _normalize_required(self.texto_feedback, field_name="texto_feedback")
        return self.model_copy(update=update)
