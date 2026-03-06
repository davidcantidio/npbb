"""Schemas publicos das landing pages dinamicas."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class LandingTemplateConfigRead(BaseModel):
    categoria: str
    tema: str
    mood: str
    cta_text: str
    color_primary: str
    color_secondary: str
    color_background: str
    color_text: str
    hero_layout: str
    cta_variant: str
    graphics_style: str
    tone_of_voice: str


class LandingFieldRead(BaseModel):
    key: str
    label: str
    input_type: str
    required: bool
    autocomplete: str | None = None
    placeholder: str | None = None


class LandingFormRead(BaseModel):
    event_id: int
    ativacao_id: int | None = None
    submit_url: str
    campos: list[LandingFieldRead]
    campos_obrigatorios: list[str]
    campos_opcionais: list[str]
    mensagem_sucesso: str
    lgpd_texto: str
    privacy_policy_url: str


class LandingBrandRead(BaseModel):
    tagline: str
    versao_logo: str
    url_hero_image: str
    hero_alt: str


class LandingEventRead(BaseModel):
    id: int
    nome: str
    descricao: str | None = None
    descricao_curta: str | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    cidade: str
    estado: str


class LandingAccessRead(BaseModel):
    landing_url: str | None = None
    qr_code_url: str | None = None
    url_promotor: str | None = None


class LandingPageRead(BaseModel):
    ativacao_id: int | None = None
    evento: LandingEventRead
    template: LandingTemplateConfigRead
    formulario: LandingFormRead
    marca: LandingBrandRead
    acesso: LandingAccessRead


class LandingSubmitRequest(BaseModel):
    nome: str | None = Field(default=None, max_length=100)
    sobrenome: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    cpf: str | None = Field(default=None, max_length=20)
    telefone: str | None = Field(default=None, max_length=30)
    data_nascimento: date | None = None
    estado: str | None = Field(default=None, max_length=40)
    endereco: str | None = Field(default=None, max_length=200)
    interesses: str | None = Field(default=None, max_length=200)
    genero: str | None = Field(default=None, max_length=40)
    area_de_atuacao: str | None = Field(default=None, max_length=160)
    consentimento_lgpd: bool

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def validate_required_identity(self):
        if not (self.nome or "").strip():
            raise ValueError("nome obrigatorio")
        if self.email is None:
            raise ValueError("email obrigatorio")
        if not self.consentimento_lgpd:
            raise ValueError("consentimento_lgpd obrigatorio")
        if self.cpf is not None:
            digits = "".join(ch for ch in self.cpf if ch.isdigit())
            self.cpf = digits or None
        if self.telefone is not None:
            digits = "".join(ch for ch in self.telefone if ch.isdigit())
            self.telefone = digits or None
        return self


class LandingSubmitResponse(BaseModel):
    lead_id: int
    event_id: int
    ativacao_id: int | None = None
    mensagem_sucesso: str
