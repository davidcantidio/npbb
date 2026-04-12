# app/models/models.py

from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, List

from sqlalchemy import CheckConstraint, Column, DateTime, Index, Numeric, Text, UniqueConstraint
from sqlmodel import Field, Relationship

from app.db.metadata import SQLModel


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


# =========================
# ENUMS DE DOMÍNIO (estáveis)
# =========================


class UsuarioTipo(str, Enum):
    BB = "bb"
    NPBB = "npbb"
    AGENCIA = "agencia"


class SolicitacaoIngressoStatus(str, Enum):
    SOLICITADO = "SOLICITADO"
    CANCELADO = "CANCELADO"


class SolicitacaoIngressoTipo(str, Enum):
    SELF = "SELF"
    TERCEIRO = "TERCEIRO"


class TipoIngresso(str, Enum):
    PISTA = "pista"
    PISTA_PREMIUM = "pista_premium"
    CAMAROTE = "camarote"


class ModoFornecimento(str, Enum):
    INTERNO_EMITIDO_COM_QR = "interno_emitido_com_qr"
    EXTERNO_RECEBIDO = "externo_recebido"


class StatusInventario(str, Enum):
    """Application-layer enum for inventory state classification; not persisted as a DB column."""

    PLANEJADO = "planejado"
    RECEBIDO_CONFIRMADO = "recebido_confirmado"
    BLOQUEADO_POR_RECEBIMENTO = "bloqueado_por_recebimento"
    DISPONIVEL = "disponivel"
    DISTRIBUIDO = "distribuido"


class StatusDestinatario(str, Enum):
    ENVIADO = "enviado"
    CONFIRMADO = "confirmado"
    UTILIZADO = "utilizado"
    CANCELADO = "cancelado"


class TipoOcorrencia(str, Enum):
    ENTREGA_ERRADA = "entrega_errada"
    QUANTIDADE_DIVERGENTE = "quantidade_divergente"
    DESTINATARIO_INVALIDO = "destinatario_invalido"
    OUTRO = "outro"


class TipoAjuste(str, Enum):
    AUMENTO = "aumento"
    REDUCAO = "reducao"
    REMANEJAMENTO = "remanejamento"


class TipoBloqueioInventario(str, Enum):
    FALTA_RECEBIMENTO = "falta_recebimento"
    EXCESSO_RECEBIDO = "excesso_recebido"


class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=100, unique=True)
    matricula: Optional[str] = Field(default=None, max_length=20, unique=True)
    password_hash: str = Field(max_length=255)

    tipo_usuario: UsuarioTipo
    status_aprovacao: Optional[str] = Field(default=None, max_length=20)

    funcionario_id: Optional[int] = Field(default=None, foreign_key="funcionario.id")
    agencia_id: Optional[int] = Field(default=None, foreign_key="agencia.id")

    ativo: bool = Field(default=True)

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    )

    funcionario: Optional["Funcionario"] = Relationship(back_populates="usuario")
    agencia: Optional["Agencia"] = Relationship(back_populates="usuarios")
    landing_customization_audits: List["EventoLandingCustomizationAudit"] = Relationship(
        back_populates="changed_by_user"
    )

    @property
    def diretoria_id(self) -> Optional[int]:
        if self.funcionario and self.funcionario.diretoria_id:
            return int(self.funcionario.diretoria_id)
        return None


class PasswordResetToken(SQLModel, table=True):
    __tablename__ = "password_reset_token"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    token_hash: str = Field(max_length=64, unique=True, index=True)

    created_at: datetime = Field(default_factory=now_utc)
    sent_at: datetime = Field(default_factory=now_utc)
    expires_at: datetime
    used_at: Optional[datetime] = None


class StatusEvento(SQLModel, table=True):
    __tablename__ = "status_evento"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=30, unique=True)
    created_at: datetime = Field(default_factory=now_utc)

    eventos: List["Evento"] = Relationship(back_populates="status")


class TipoInvestimento(str, Enum):
    PATROCINIO = "Patrocínio"
    PROMOCAO = "Promoção"


class TipoPergunta(str, Enum):
    ABERTA_TEXTO_SIMPLES = "aberta_texto_simples"
    ABERTA_TEXTO_AREA = "aberta_texto_area"
    OBJETIVA_UNICA = "objetiva_unica"
    OBJETIVA_MULTIPLA = "objetiva_multipla"
    DATA = "data"
    AVALIACAO = "avaliacao"
    NUMERICA = "numerica"


class LeadConversaoTipo(str, Enum):
    COMPRA_INGRESSO = "COMPRA_INGRESSO"
    ACAO_EVENTO = "ACAO_EVENTO"


class LeadAliasTipo(str, Enum):
    EVENTO = "EVENTO"
    CIDADE = "CIDADE"
    ESTADO = "ESTADO"
    GENERO = "GENERO"


# =========================
# TABELAS BÁSICAS
# =========================


class Agencia(SQLModel, table=True):
    __tablename__ = "agencia"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=100)
    dominio: str = Field(max_length=100, unique=True)
    lote: int
    created_at: datetime = Field(default_factory=now_utc)
    logo_url: Optional[str] = Field(default=None, max_length=500)

    eventos: List["Evento"] = Relationship(back_populates="agencia")
    usuarios: List["Usuario"] = Relationship(back_populates="agencia")


class Diretoria(SQLModel, table=True):
    __tablename__ = "diretoria"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=100, unique=True)
    created_at: datetime = Field(default_factory=now_utc)

    funcionarios: List["Funcionario"] = Relationship(back_populates="diretoria")
    eventos: List["Evento"] = Relationship(back_populates="diretoria")
    cotas: List["CotaCortesia"] = Relationship(back_populates="diretoria")


class DivisaoDemandante(SQLModel, table=True):
    __tablename__ = "divisao_demandante"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=100, unique=True)
    created_at: datetime = Field(default_factory=now_utc)

    eventos: List["Evento"] = Relationship(back_populates="divisao_demandante")


class Funcionario(SQLModel, table=True):
    __tablename__ = "funcionario"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=100)
    chave_c: str = Field(max_length=20, unique=True)
    diretoria_id: int = Field(foreign_key="diretoria.id")
    email: str = Field(max_length=60, unique=True)
    telefone: Optional[str] = Field(default=None, max_length=25)
    created_at: datetime = Field(default_factory=now_utc)

    diretoria: Optional[Diretoria] = Relationship(back_populates="funcionarios")
    eventos_gestor: List["Evento"] = Relationship(back_populates="gestor")
    convites_feitos: List["Convite"] = Relationship(back_populates="funcionario_convidador")
    convidados_associados: List["Convidado"] = Relationship(back_populates="funcionario_associado")

    usuario: Optional["Usuario"] = Relationship(back_populates="funcionario")


# =========================
# EVENTO / TIPO / SUBTIPO
# =========================


class TipoEvento(SQLModel, table=True):
    __tablename__ = "tipo_evento"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=50, unique=True)

    subtipos: List["SubtipoEvento"] = Relationship(back_populates="tipo")
    eventos: List["Evento"] = Relationship(back_populates="tipo")


class SubtipoEvento(SQLModel, table=True):
    __tablename__ = "subtipo_evento"

    id: Optional[int] = Field(default=None, primary_key=True)
    tipo_id: int = Field(foreign_key="tipo_evento.id")
    nome: str = Field(max_length=80)

    tipo: Optional[TipoEvento] = Relationship(back_populates="subtipos")
    eventos: List["Evento"] = Relationship(back_populates="subtipo")


class Evento(SQLModel, table=True):
    __tablename__ = "evento"

    id: Optional[int] = Field(default=None, primary_key=True)
    thumbnail: Optional[str] = Field(default=None, max_length=500)
    template_override: Optional[str] = Field(default=None, max_length=50)
    cta_personalizado: Optional[str] = Field(default=None, max_length=200)
    descricao_curta: Optional[str] = Field(default=None, max_length=500)
    # Divisao demandante (lookup table).
    divisao_demandante_id: Optional[int] = Field(default=None, foreign_key="divisao_demandante.id")
    qr_code_url: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    # Codigo externo para reconciliacao de imports (ex.: publicidade).
    external_project_code: Optional[str] = Field(default=None, max_length=120, index=True)

    nome: str = Field(max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=240)
    investimento: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 2)))

    data_inicio_prevista: Optional[date] = None
    data_inicio_realizada: Optional[date] = None
    data_fim_prevista: Optional[date] = None
    data_fim_realizada: Optional[date] = None

    publico_projetado: Optional[int] = None
    publico_realizado: Optional[int] = None

    concorrencia: bool = Field(default=False)
    cidade: str = Field(max_length=40, index=True)
    estado: str = Field(max_length=40, index=True)

    agencia_id: Optional[int] = Field(default=None, foreign_key="agencia.id")
    diretoria_id: Optional[int] = Field(default=None, foreign_key="diretoria.id")
    gestor_id: Optional[int] = Field(default=None, foreign_key="funcionario.id")

    tipo_id: Optional[int] = Field(default=None, foreign_key="tipo_evento.id")
    subtipo_id: Optional[int] = Field(default=None, foreign_key="subtipo_evento.id")

    status_id: int = Field(foreign_key="status_evento.id")

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    )

    agencia: Optional[Agencia] = Relationship(back_populates="eventos")
    diretoria: Optional[Diretoria] = Relationship(back_populates="eventos")
    divisao_demandante: Optional[DivisaoDemandante] = Relationship(back_populates="eventos")
    gestor: Optional[Funcionario] = Relationship(back_populates="eventos_gestor")
    tipo: Optional[TipoEvento] = Relationship(back_populates="eventos")
    subtipo: Optional[SubtipoEvento] = Relationship(back_populates="eventos")
    status: Optional[StatusEvento] = Relationship(back_populates="eventos")

    territorios: List["EventoTerritorio"] = Relationship(back_populates="evento")
    tags: List["EventoTag"] = Relationship(back_populates="evento")
    ativacoes: List["Ativacao"] = Relationship(back_populates="evento")
    lead_reconhecimento_tokens: List["LeadReconhecimentoToken"] = Relationship(
        back_populates="evento"
    )
    gamificacoes: List["Gamificacao"] = Relationship(back_populates="evento")
    cotas: List["CotaCortesia"] = Relationship(back_populates="evento")
    paginas_questionario: List["QuestionarioPagina"] = Relationship(back_populates="evento")
    respostas_questionario: List["QuestionarioResposta"] = Relationship(back_populates="evento")
    landing_customization_audits: List["EventoLandingCustomizationAudit"] = Relationship(
        back_populates="evento"
    )
    landing_analytics_events: List["LandingAnalyticsEvent"] = Relationship(back_populates="evento")
    lead_eventos: List["LeadEvento"] = Relationship(back_populates="evento")


# =========================
# TERRITÓRIOS / TAGS
# =========================


class Territorio(SQLModel, table=True):
    __tablename__ = "territorio"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=80, unique=True)

    eventos: List["EventoTerritorio"] = Relationship(back_populates="territorio")


class EventoTerritorio(SQLModel, table=True):
    __tablename__ = "evento_territorio"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")
    territorio_id: int = Field(foreign_key="territorio.id")

    evento: Optional[Evento] = Relationship(back_populates="territorios")
    territorio: Optional[Territorio] = Relationship(back_populates="eventos")


class Tag(SQLModel, table=True):
    __tablename__ = "tag"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=80, unique=True)

    eventos: List["EventoTag"] = Relationship(back_populates="tag")


class EventoTag(SQLModel, table=True):
    __tablename__ = "evento_tag"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")
    tag_id: int = Field(foreign_key="tag.id")

    evento: Optional[Evento] = Relationship(back_populates="tags")
    tag: Optional[Tag] = Relationship(back_populates="eventos")


from app.models.lead_public_models import (
    EventPublicity,
    ImportAlias,
    Lead,
    LeadAlias,
    LeadConversao,
    LeadEvento,
    LeadEventoSourceKind,
    LeadImportEtlPreviewSession,
    PublicityImportStaging,
    TipoLead,
    TipoResponsavel,
)


# =========================
# ATIVAÇÃO / GAMIFICAÇÃO / TERMO / INVESTIMENTO / RELAÇÃO LEAD
# =========================


class Ativacao(SQLModel, table=True):
    __tablename__ = "ativacao"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=240)
    evento_id: int = Field(foreign_key="evento.id")
    gamificacao_id: Optional[int] = Field(default=None, foreign_key="gamificacao.id")
    landing_url: Optional[str] = Field(default=None, max_length=500)
    qr_code_url: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    url_promotor: Optional[str] = Field(default=None, max_length=500)

    valor: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 2)))

    mensagem_qrcode: Optional[str] = Field(default=None, max_length=240)

    redireciona_pesquisa: bool = Field(default=False)
    checkin_unico: bool = Field(default=False)
    termo_uso: bool = Field(default=False)
    gera_cupom: bool = Field(default=False)

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    )

    evento: Optional[Evento] = Relationship(back_populates="ativacoes")
    gamificacao: Optional["Gamificacao"] = Relationship(back_populates="ativacoes")
    termo_uso_obj: Optional["TermoUsoAtivacao"] = Relationship(back_populates="ativacao")
    investimentos: List["Investimento"] = Relationship(back_populates="ativacao")
    ativacao_leads: List["AtivacaoLead"] = Relationship(back_populates="ativacao")
    conversoes_ativacao: List["ConversaoAtivacao"] = Relationship(back_populates="ativacao")
    cupons: List["Cupom"] = Relationship(back_populates="ativacao")
    respostas_questionario: List["QuestionarioResposta"] = Relationship(back_populates="ativacao")
    landing_analytics_events: List["LandingAnalyticsEvent"] = Relationship(back_populates="ativacao")


class Gamificacao(SQLModel, table=True):
    __tablename__ = "gamificacao"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")

    nome: str = Field(max_length=150)
    descricao: str = Field(max_length=240)
    premio: str = Field(max_length=200)
    titulo_feedback: str = Field(max_length=200)
    texto_feedback: str = Field(max_length=240)

    evento: Optional[Evento] = Relationship(back_populates="gamificacoes")
    ativacoes: List[Ativacao] = Relationship(back_populates="gamificacao")


class TermoUsoAtivacao(SQLModel, table=True):
    __tablename__ = "termo_uso_ativacao"

    id: Optional[int] = Field(default=None, primary_key=True)
    ativacao_id: int = Field(foreign_key="ativacao.id", unique=True)

    titulo: Optional[str] = Field(default=None, max_length=200)
    texto: str
    obrigatorio: bool = Field(default=True)

    ativacao: Optional[Ativacao] = Relationship(back_populates="termo_uso_obj")


class Investimento(SQLModel, table=True):
    __tablename__ = "investimento"

    id: Optional[int] = Field(default=None, primary_key=True)
    ativacao_id: int = Field(foreign_key="ativacao.id")

    tipo: TipoInvestimento
    descricao: str = Field(max_length=200)
    valor: Decimal = Field(sa_column=Column(Numeric(12, 2)))

    ativacao: Optional[Ativacao] = Relationship(back_populates="investimentos")


class AtivacaoLead(SQLModel, table=True):
    __tablename__ = "ativacao_lead"
    __table_args__ = (
        UniqueConstraint("ativacao_id", "lead_id", name="uq_ativacao_lead_ativacao_id_lead_id"),
        CheckConstraint(
            "nome_ativacao IS NULL OR length(trim(nome_ativacao)) > 0",
            name="nome_ativacao_not_blank",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    ativacao_id: int = Field(foreign_key="ativacao.id")
    lead_id: int = Field(foreign_key="lead.id", index=True)
    gamificacao_id: Optional[int] = Field(default=None, foreign_key="gamificacao.id")
    gamificacao_completed: Optional[bool] = Field(default=False)
    gamificacao_completed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    nome_ativacao: Optional[str] = Field(default=None, max_length=150)

    ativacao: Optional[Ativacao] = Relationship(back_populates="ativacao_leads")
    lead: Optional[Lead] = Relationship(back_populates="ativacoes")
    gamificacao: Optional[Gamificacao] = Relationship()


class ConversaoAtivacao(SQLModel, table=True):
    __tablename__ = "conversao_ativacao"
    __table_args__ = (Index("ix_conversao_ativacao_ativacao_id_cpf", "ativacao_id", "cpf"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    ativacao_id: int = Field(foreign_key="ativacao.id")
    lead_id: int = Field(foreign_key="lead.id")
    cpf: str = Field(max_length=11)
    created_at: datetime = Field(default_factory=now_utc)

    ativacao: Optional[Ativacao] = Relationship(back_populates="conversoes_ativacao")
    lead: Optional[Lead] = Relationship(back_populates="conversoes_ativacao")


class LeadReconhecimentoToken(SQLModel, table=True):
    __tablename__ = "lead_reconhecimento_token"

    token_hash: str = Field(primary_key=True, index=True, max_length=64)
    lead_id: int = Field(foreign_key="lead.id")
    evento_id: int = Field(foreign_key="evento.id")
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))

    lead: Optional[Lead] = Relationship(back_populates="reconhecimento_tokens")
    evento: Optional[Evento] = Relationship(back_populates="lead_reconhecimento_tokens")


class EventoLandingCustomizationAudit(SQLModel, table=True):
    __tablename__ = "evento_landing_customization_audit"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="evento.id", index=True)
    field_name: str = Field(max_length=80)
    old_value: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    new_value: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    changed_by_user_id: Optional[int] = Field(default=None, foreign_key="usuario.id", index=True)
    created_at: datetime = Field(default_factory=now_utc)

    evento: Optional[Evento] = Relationship(back_populates="landing_customization_audits")
    changed_by_user: Optional[Usuario] = Relationship(back_populates="landing_customization_audits")


class LandingAnalyticsEvent(SQLModel, table=True):
    __tablename__ = "landing_analytics_event"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="evento.id", index=True)
    ativacao_id: Optional[int] = Field(default=None, foreign_key="ativacao.id", index=True)
    categoria: str = Field(max_length=80, index=True)
    tema: str = Field(max_length=80)
    event_name: str = Field(max_length=60, index=True)
    cta_variant_id: Optional[str] = Field(default=None, max_length=60, index=True)
    landing_session_id: Optional[str] = Field(default=None, max_length=120, index=True)
    created_at: datetime = Field(default_factory=now_utc, index=True)

    evento: Optional[Evento] = Relationship(back_populates="landing_analytics_events")
    ativacao: Optional[Ativacao] = Relationship(back_populates="landing_analytics_events")


class Cupom(SQLModel, table=True):
    __tablename__ = "cupom"

    id: Optional[int] = Field(default=None, primary_key=True)
    ativacao_id: int = Field(foreign_key="ativacao.id")
    codigo: str = Field(max_length=50, unique=True)
    descricao: Optional[str] = Field(default=None, max_length=200)

    data_criacao: datetime = Field(default_factory=now_utc)
    data_validade: Optional[date] = None
    usado: bool = Field(default=False)
    usado_em: Optional[datetime] = None

    lead_id: Optional[int] = Field(default=None, foreign_key="lead.id")

    ativacao: Optional[Ativacao] = Relationship(back_populates="cupons")
    lead: Optional[Lead] = Relationship(back_populates="cupons")


from app.models.event_support_models import (
    Convidado,
    Convite,
    CotaCortesia,
    FormularioLandingTemplate,
    FormularioLeadCampo,
    FormularioLeadConfig,
    QuestionarioOpcao,
    QuestionarioPagina,
    QuestionarioPergunta,
    QuestionarioResposta,
    QuestionarioRespostaOpcao,
    QuestionarioRespostaPergunta,
    SolicitacaoIngresso,
)
from app.models.tmj_analytics_models import (
    AttendanceAccessControl,
    BbRelationshipSegment,
    DataQualityResult,
    DataQualityScope,
    DataQualitySeverity,
    DataQualityStatus,
    EventSession,
    EventSessionType,
    FestivalLead,
    IngestionEvidence,
    IngestionRun,
    IngestionStatus,
    MetricLineage,
    OptinTransaction,
    Source,
    SourceKind,
    TicketCategorySegmentMap,
    TicketSales,
)
from app.models.sponsorship_models import (
    ContractClause,
    ContractExtractionDraft,
    ContractStatus,
    CounterpartRequirement,
    Delivery,
    DeliveryEvidence,
    DraftReviewStatus,
    EvidenceType,
    GroupMember,
    OccurrenceResponsible,
    OccurrenceStatus,
    OwnerType,
    PeriodType,
    RequirementOccurrence,
    RequirementStatus,
    ResponsibilityType,
    SocialProfile,
    SponsoredInstitution,
    SponsoredPerson,
    SponsorshipContract,
    SponsorshipGroup,
)
