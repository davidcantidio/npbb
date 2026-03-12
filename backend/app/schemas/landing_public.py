"""Schemas publicos das landing pages dinamicas."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class LandingExperimentVariantRead(BaseModel):
    id: str
    label: str
    text: str


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
    cta_experiment_enabled: bool = False
    cta_variants: list[LandingExperimentVariantRead] = Field(default_factory=list)


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


class LandingEventRead(BaseModel):
    id: int
    nome: str
    cta_personalizado: str | None = None
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


class LandingAtivacaoRead(BaseModel):
    id: int
    nome: str
    descricao: str | None = None
    mensagem_qrcode: str | None = None


class GamificacaoPublicSchema(BaseModel):
    id: int
    nome: str
    descricao: str
    premio: str
    titulo_feedback: str
    texto_feedback: str


class LandingPageRead(BaseModel):
    ativacao_id: int | None = None
    ativacao: LandingAtivacaoRead | None = None
    gamificacoes: list[GamificacaoPublicSchema] = Field(default_factory=list)
    evento: LandingEventRead
    template: LandingTemplateConfigRead
    formulario: LandingFormRead
    marca: LandingBrandRead
    acesso: LandingAccessRead


class LandingSubmitRequest(BaseModel):
    nome: str | None = Field(default=None, max_length=100)
    sobrenome: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    event_id: int | None = Field(default=None, ge=1)
    ativacao_id: int | None = Field(default=None, ge=1)
    cpf: str | None = Field(default=None, max_length=20)
    telefone: str | None = Field(default=None, max_length=30)
    data_nascimento: date | None = None
    estado: str | None = Field(default=None, max_length=40)
    endereco: str | None = Field(default=None, max_length=200)
    interesses: str | None = Field(default=None, max_length=200)
    genero: str | None = Field(default=None, max_length=40)
    area_de_atuacao: str | None = Field(default=None, max_length=160)
    cta_variant_id: str | None = Field(default=None, max_length=60)
    landing_session_id: str | None = Field(default=None, max_length=120)
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
    ativacao_lead_id: int | None = None
    mensagem_sucesso: str
    conversao_registrada: bool = False
    bloqueado_cpf_duplicado: bool = False


class LandingAnalyticsTrackRequest(BaseModel):
    event_id: int
    ativacao_id: int | None = None
    categoria: str
    tema: str
    event_name: str
    cta_variant_id: str | None = Field(default=None, max_length=60)
    landing_session_id: str | None = Field(default=None, max_length=120)

    model_config = ConfigDict(str_strip_whitespace=True)


class LandingAnalyticsTrackResponse(BaseModel):
    status: str = "ok"


class LandingAnalyticsVariantSummaryRead(BaseModel):
    cta_variant_id: str
    views: int
    submits: int
    successes: int


class LandingAnalyticsSummaryRead(BaseModel):
    event_id: int
    categoria: str
    tema: str
    page_views: int
    form_starts: int
    submit_attempts: int
    submit_successes: int
    conversion_rate: float
    variants: list[LandingAnalyticsVariantSummaryRead] = Field(default_factory=list)


class EventoLandingCustomizationAuditRead(BaseModel):
    id: int
    event_id: int
    field_name: str
    old_value: str | None = None
    new_value: str | None = None
    changed_by_user_id: int | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
