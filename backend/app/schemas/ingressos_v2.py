"""Schemas for ingressos v2 configuration and planned quantities."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.models import ModoFornecimento, TipoIngresso


def _validate_tipos_ingresso(
    value: list[TipoIngresso] | None, *, required: bool
) -> list[TipoIngresso] | None:
    if value is None:
        if required:
            raise ValueError("tipos_ingresso obrigatorio")
        return None
    if not value:
        raise ValueError("tipos_ingresso deve conter ao menos um item")

    unique: list[TipoIngresso] = []
    seen: set[TipoIngresso] = set()
    for item in value:
        if item in seen:
            raise ValueError("tipos_ingresso nao pode conter valores duplicados")
        seen.add(item)
        unique.append(item)
    return sorted(unique, key=lambda item: item.value)


class ConfiguracaoIngressoEventoCreate(BaseModel):
    modo_fornecimento: ModoFornecimento
    tipos_ingresso: list[TipoIngresso]

    model_config = ConfigDict(extra="forbid")

    @field_validator("tipos_ingresso")
    @classmethod
    def validate_tipos_ingresso(cls, value: list[TipoIngresso]) -> list[TipoIngresso]:
        validated = _validate_tipos_ingresso(value, required=True)
        assert validated is not None
        return validated


class ConfiguracaoIngressoEventoUpdate(BaseModel):
    modo_fornecimento: ModoFornecimento | None = None
    tipos_ingresso: list[TipoIngresso] | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("tipos_ingresso")
    @classmethod
    def validate_tipos_ingresso(
        cls, value: list[TipoIngresso] | None
    ) -> list[TipoIngresso] | None:
        return _validate_tipos_ingresso(value, required=False)


class ConfiguracaoIngressoEventoRead(BaseModel):
    id: int
    evento_id: int
    modo_fornecimento: ModoFornecimento
    tipos_ingresso: list[TipoIngresso]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PrevisaoIngressoCreate(BaseModel):
    diretoria_id: int = Field(ge=1)
    tipo_ingresso: TipoIngresso
    quantidade: int = Field(ge=0)

    model_config = ConfigDict(extra="forbid")


class PrevisaoIngressoRead(BaseModel):
    id: int
    evento_id: int
    diretoria_id: int
    tipo_ingresso: TipoIngresso
    quantidade: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
