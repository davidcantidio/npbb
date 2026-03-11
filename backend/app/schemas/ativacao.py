"""Schemas do modulo de Ativacoes (por evento) - MVP.

Contrato (MVP) (ver docs):
- "Mensagem" do formulario usa o campo `descricao` (opcional; max 240).
- `valor` existe no modelo/DB, mas fica fora do payload do modulo de ativacoes (MVP).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class AtivacaoLeadRead(BaseModel):
    id: int
    ativacao_id: int
    lead_id: int
    gamificacao_id: int | None = None
    gamificacao_completed: bool | None = False
    gamificacao_completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


def _normalize_required(text: str, *, field_name: str) -> str:
    value = (text or "").strip()
    if not value:
        raise ValueError(f"{field_name} obrigatorio")
    return value


def _normalize_optional(text: str | None) -> str | None:
    if text is None:
        return None
    value = text.strip()
    return value or None


def _validate_boolean_aliases(
    data: object,
    *,
    primary_field: str,
    alias_field: str,
) -> object:
    if not isinstance(data, dict):
        return data

    if primary_field in data and alias_field in data and data[primary_field] != data[alias_field]:
        raise ValueError(f"{primary_field} e {alias_field} nao podem divergir")

    return data


class AtivacaoRead(BaseModel):
    id: int
    evento_id: int
    nome: str
    descricao: str | None = None
    conversao_unica: bool = Field(
        validation_alias=AliasChoices("conversao_unica", "checkin_unico")
    )
    checkin_unico: bool = Field(validation_alias=AliasChoices("checkin_unico", "conversao_unica"))
    mensagem_qrcode: str | None = None
    gamificacao_id: int | None = None
    landing_url: str | None = None
    qr_code_url: str | None = None
    url_promotor: str | None = None

    redireciona_pesquisa: bool
    termo_uso: bool
    gera_cupom: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AtivacaoCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    descricao: str | None = Field(default=None, max_length=240)
    conversao_unica: bool = Field(
        default=True,
        validation_alias=AliasChoices("conversao_unica", "checkin_unico"),
    )
    checkin_unico: bool = Field(
        default=True,
        validation_alias=AliasChoices("checkin_unico", "conversao_unica"),
    )
    mensagem_qrcode: str | None = Field(default=None, max_length=240)
    gamificacao_id: int | None = Field(default=None, ge=1)

    redireciona_pesquisa: bool = False
    termo_uso: bool = False
    gera_cupom: bool = False

    @model_validator(mode="before")
    @classmethod
    def validate_boolean_aliases(cls, data: object):
        return _validate_boolean_aliases(
            data,
            primary_field="conversao_unica",
            alias_field="checkin_unico",
        )

    @model_validator(mode="after")
    def normalize_strings(self):
        return self.model_copy(
            update={
                "nome": _normalize_required(self.nome, field_name="nome"),
                "descricao": _normalize_optional(self.descricao),
                "mensagem_qrcode": _normalize_optional(self.mensagem_qrcode),
            }
        )


class AtivacaoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    descricao: str | None = Field(default=None, max_length=240)
    conversao_unica: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("conversao_unica", "checkin_unico"),
    )
    checkin_unico: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("checkin_unico", "conversao_unica"),
    )
    mensagem_qrcode: str | None = Field(default=None, max_length=240)
    gamificacao_id: int | None = Field(default=None, ge=1)

    redireciona_pesquisa: bool | None = None
    termo_uso: bool | None = None
    gera_cupom: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_boolean_aliases(cls, data: object):
        return _validate_boolean_aliases(
            data,
            primary_field="conversao_unica",
            alias_field="checkin_unico",
        )

    @model_validator(mode="after")
    def normalize_strings(self):
        update: dict[str, str | None] = {}

        if "nome" in self.model_fields_set and self.nome is not None:
            update["nome"] = _normalize_required(self.nome, field_name="nome")
        if "descricao" in self.model_fields_set:
            update["descricao"] = _normalize_optional(self.descricao)
        if "mensagem_qrcode" in self.model_fields_set:
            update["mensagem_qrcode"] = _normalize_optional(self.mensagem_qrcode)

        return self.model_copy(update=update)
