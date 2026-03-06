# app/models/models.py

from datetime import datetime, date, time, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, List

from sqlalchemy import Column, DateTime, Numeric, Text, UniqueConstraint
from sqlalchemy.orm import relationship
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
    hero_image_url: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    cta_personalizado: Optional[str] = Field(default=None, max_length=200)
    descricao_curta: Optional[str] = Field(default=None, max_length=500)
    # Divisao demandante (lookup table).
    divisao_demandante_id: Optional[int] = Field(default=None, foreign_key="divisao_demandante.id")
    qr_code_url: Optional[str] = Field(default=None, max_length=500)
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
    gamificacoes: List["Gamificacao"] = Relationship(back_populates="evento")
    cotas: List["CotaCortesia"] = Relationship(back_populates="evento")
    paginas_questionario: List["QuestionarioPagina"] = Relationship(back_populates="evento")
    respostas_questionario: List["QuestionarioResposta"] = Relationship(back_populates="evento")
    landing_customization_audits: List["EventoLandingCustomizationAudit"] = Relationship(
        back_populates="evento"
    )
    landing_analytics_events: List["LandingAnalyticsEvent"] = Relationship(back_populates="evento")


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


# =========================
# LEAD
# =========================


class Lead(SQLModel, table=True):
    __tablename__ = "lead"
    __table_args__ = (
        UniqueConstraint("email", "cpf", "evento_nome", "sessao", name="uq_lead_ticketing_dedupe"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    id_salesforce: Optional[str] = Field(default=None, max_length=200, unique=True)

    nome: Optional[str] = Field(default=None, max_length=100)
    sobrenome: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=100)
    telefone: Optional[str] = Field(default=None, max_length=100)

    # CPF pode repetir entre eventos/sessoes; dedupe e composto.
    cpf: Optional[str] = Field(default=None, max_length=11)
    data_nascimento: Optional[date] = None
    data_criacao: datetime = Field(default_factory=now_utc, index=True)

    evento_nome: Optional[str] = Field(default=None, max_length=150)
    sessao: Optional[str] = Field(default=None, max_length=80)
    data_compra: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    data_compra_data: Optional[date] = None
    data_compra_hora: Optional[time] = None
    opt_in: Optional[str] = Field(default=None, max_length=80)
    opt_in_id: Optional[str] = Field(default=None, max_length=80)
    opt_in_flag: Optional[bool] = None
    metodo_entrega: Optional[str] = Field(default=None, max_length=160)
    rg: Optional[str] = Field(default=None, max_length=30)
    # Address fields
    endereco_rua: Optional[str] = Field(default=None, max_length=200)
    endereco_numero: Optional[str] = Field(default=None, max_length=120)
    complemento: Optional[str] = Field(default=None, max_length=120)
    bairro: Optional[str] = Field(default=None, max_length=160)
    cep: Optional[str] = Field(default=None, max_length=20)
    cidade: Optional[str] = Field(default=None, max_length=120)
    estado: Optional[str] = Field(default=None, max_length=40)
    genero: Optional[str] = Field(default=None, max_length=40)
    codigo_promocional: Optional[str] = Field(default=None, max_length=80)
    ingresso_tipo: Optional[str] = Field(default=None, max_length=160)
    ingresso_qtd: Optional[int] = None
    fonte_origem: Optional[str] = Field(default=None, max_length=80)
    batch_id: Optional[int] = Field(default=None, foreign_key="lead_batches.id", index=True)

    ativacoes: List["AtivacaoLead"] = Relationship(back_populates="lead")
    cupons: List["Cupom"] = Relationship(back_populates="lead")
    respostas_questionario: List["QuestionarioResposta"] = Relationship(back_populates="lead")
    conversoes: List["LeadConversao"] = Relationship(back_populates="lead")


class LeadConversao(SQLModel, table=True):
    __tablename__ = "lead_conversao"

    id: Optional[int] = Field(default=None, primary_key=True)
    lead_id: int = Field(foreign_key="lead.id")
    tipo: LeadConversaoTipo
    acao_nome: Optional[str] = Field(default=None, max_length=120)
    fonte_origem: Optional[str] = Field(default=None, max_length=80)
    evento_id: Optional[int] = Field(default=None, foreign_key="evento.id")
    data_conversao_evento: Optional[datetime] = None
    created_at: datetime = Field(default_factory=now_utc)

    lead: Optional["Lead"] = Relationship(back_populates="conversoes")
    evento: Optional["Evento"] = Relationship()


class LeadAlias(SQLModel, table=True):
    __tablename__ = "lead_alias"

    id: Optional[int] = Field(default=None, primary_key=True)
    tipo: LeadAliasTipo
    valor_origem: str = Field(max_length=200)
    valor_normalizado: str = Field(max_length=200)
    canonical_value: Optional[str] = Field(default=None, max_length=200)
    evento_id: Optional[int] = Field(default=None, foreign_key="evento.id")
    created_at: datetime = Field(default_factory=now_utc)

    __table_args__ = (
        UniqueConstraint("tipo", "valor_normalizado", name="uq_lead_alias_tipo_valor_normalizado"),
    )

    evento: Optional["Evento"] = Relationship()


class PublicityImportStaging(SQLModel, table=True):
    __tablename__ = "publicity_import_staging"
    __table_args__ = (
        UniqueConstraint("source_file", "source_row_hash", name="uq_publicity_import_staging_file_hash"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    source_file: str = Field(max_length=260, index=True)
    source_row_hash: str = Field(max_length=64, index=True)
    imported_at: datetime = Field(default_factory=now_utc, index=True)

    codigo_projeto: str = Field(max_length=120)
    projeto: str = Field(max_length=200)
    data_vinculacao: date
    meio: str = Field(max_length=120)
    veiculo: str = Field(max_length=160)
    uf: str = Field(max_length=8)
    uf_extenso: Optional[str] = Field(default=None, max_length=80)
    municipio: Optional[str] = Field(default=None, max_length=160)
    camada: str = Field(max_length=120)

    normalized_payload: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))


class EventPublicity(SQLModel, table=True):
    __tablename__ = "event_publicity"
    __table_args__ = (
        UniqueConstraint(
            "publicity_project_code",
            "linked_at",
            "medium",
            "vehicle",
            "uf",
            "layer",
            name="uq_event_publicity_natural_key",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: Optional[int] = Field(default=None, foreign_key="evento.id", index=True)

    publicity_project_code: str = Field(max_length=120)
    publicity_project_name: str = Field(max_length=200)
    linked_at: date = Field(index=True)
    medium: str = Field(max_length=120)
    vehicle: str = Field(max_length=160)
    uf: str = Field(max_length=8)
    uf_name: Optional[str] = Field(default=None, max_length=80)
    municipality: Optional[str] = Field(default=None, max_length=160)
    layer: str = Field(max_length=120)

    source_file: Optional[str] = Field(default=None, max_length=260)
    source_row_hash: Optional[str] = Field(default=None, max_length=64)

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    )

    evento: Optional["Evento"] = Relationship()


class LeadImportEtlPreviewSession(SQLModel, table=True):
    __tablename__ = "lead_import_etl_preview_session"

    session_token: str = Field(primary_key=True, max_length=120)
    idempotency_key: str = Field(index=True, max_length=160, unique=True)
    evento_id: int = Field(foreign_key="evento.id", index=True)
    evento_nome: str = Field(max_length=150)
    filename: str = Field(max_length=255)
    strict: bool = Field(default=False)
    status: str = Field(default="previewed", max_length=32, index=True)
    total_rows: int = Field(default=0)
    valid_rows: int = Field(default=0)
    invalid_rows: int = Field(default=0)
    has_validation_errors: bool = Field(default=False)
    approved_rows_json: str = Field(sa_column=Column(Text, nullable=False))
    rejected_rows_json: str = Field(sa_column=Column(Text, nullable=False))
    dq_report_json: str = Field(sa_column=Column(Text, nullable=False))
    commit_result_json: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(default_factory=now_utc, index=True)
    committed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )


class ImportAlias(SQLModel, table=True):
    __tablename__ = "import_alias"
    __table_args__ = (
        UniqueConstraint("domain", "field_name", "source_normalized", name="uq_import_alias_domain_field_source"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    domain: str = Field(max_length=64)
    field_name: str = Field(max_length=80)
    source_value: str = Field(max_length=255)
    source_normalized: str = Field(max_length=255)
    canonical_value: Optional[str] = Field(default=None, max_length=255)
    canonical_ref_id: Optional[int] = Field(default=None, index=True)

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
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
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    ativacao_id: int = Field(foreign_key="ativacao.id")
    lead_id: int = Field(foreign_key="lead.id", index=True)
    gamificacao_id: Optional[int] = Field(default=None, foreign_key="gamificacao.id")
    gamificacao_completed: Optional[bool] = Field(default=False)
    gamificacao_completed_at: Optional[datetime] = Field(default=None)

    ativacao: Optional[Ativacao] = Relationship(back_populates="ativacao_leads")
    lead: Optional[Lead] = Relationship(back_populates="ativacoes")
    gamificacao: Optional[Gamificacao] = Relationship()


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


# =========================
# COTAS / CONVIDADOS / CONVITES
# =========================


class CotaCortesia(SQLModel, table=True):
    __tablename__ = "cota_cortesia"
    __table_args__ = (UniqueConstraint("evento_id", "diretoria_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")
    diretoria_id: int = Field(foreign_key="diretoria.id", index=True)

    quantidade: int

    evento: Optional[Evento] = Relationship(back_populates="cotas")
    diretoria: Optional[Diretoria] = Relationship(back_populates="cotas")
    convites: List["Convite"] = Relationship(back_populates="cota")
    solicitacoes: List["SolicitacaoIngresso"] = Relationship(back_populates="cota")


class SolicitacaoIngresso(SQLModel, table=True):
    __tablename__ = "solicitacao_ingresso"

    id: Optional[int] = Field(default=None, primary_key=True)
    cota_id: int = Field(foreign_key="cota_cortesia.id", index=True)
    evento_id: int = Field(foreign_key="evento.id")
    diretoria_id: int = Field(foreign_key="diretoria.id")

    solicitante_usuario_id: int = Field(foreign_key="usuario.id")
    solicitante_email: str = Field(max_length=120)
    tipo: SolicitacaoIngressoTipo
    indicado_email: Optional[str] = Field(default=None, max_length=120)
    status: SolicitacaoIngressoStatus

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)

    cota: Optional[CotaCortesia] = Relationship(back_populates="solicitacoes")
    evento: Optional[Evento] = Relationship()
    diretoria: Optional[Diretoria] = Relationship()
    solicitante_usuario: Optional[Usuario] = Relationship()


class Convidado(SQLModel, table=True):
    __tablename__ = "convidado"

    id: Optional[int] = Field(default=None, primary_key=True)
    funcionario_associado_id: Optional[int] = Field(default=None, foreign_key="funcionario.id")
    nome: str = Field(max_length=100)
    cpf: str = Field(max_length=11, unique=True)
    email: str = Field(max_length=100, unique=True)
    externo: bool

    funcionario_associado: Optional[Funcionario] = Relationship(
        back_populates="convidados_associados"
    )
    convites: List["Convite"] = Relationship(back_populates="convidado")


class Convite(SQLModel, table=True):
    __tablename__ = "convite"

    id: Optional[int] = Field(default=None, primary_key=True)
    cota_id: int = Field(foreign_key="cota_cortesia.id")
    convidado_id: int = Field(foreign_key="convidado.id")
    funcionario_convidador_id: int = Field(foreign_key="funcionario.id")

    status: str = Field(max_length=20)

    cota: Optional[CotaCortesia] = Relationship(back_populates="convites")
    convidado: Optional[Convidado] = Relationship(back_populates="convites")
    funcionario_convidador: Optional[Funcionario] = Relationship(back_populates="convites_feitos")


# =========================
# QUESTIONÁRIO (CONFIG + RESPOSTAS)
# =========================


class QuestionarioPagina(SQLModel, table=True):
    __tablename__ = "questionario_pagina"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")
    ordem: int
    titulo: str = Field(max_length=200)
    descricao: Optional[str] = None

    evento: Optional[Evento] = Relationship(back_populates="paginas_questionario")
    perguntas: List["QuestionarioPergunta"] = Relationship(back_populates="pagina")


class QuestionarioPergunta(SQLModel, table=True):
    __tablename__ = "questionario_pergunta"

    id: Optional[int] = Field(default=None, primary_key=True)
    pagina_id: int = Field(foreign_key="questionario_pagina.id")
    ordem: int
    texto: str = Field(max_length=500)
    tipo: TipoPergunta
    obrigatoria: bool = Field(default=False)

    pagina: Optional[QuestionarioPagina] = Relationship(back_populates="perguntas")
    opcoes: List["QuestionarioOpcao"] = Relationship(back_populates="pergunta")
    respostas: List["QuestionarioRespostaPergunta"] = Relationship(back_populates="pergunta")


class QuestionarioOpcao(SQLModel, table=True):
    __tablename__ = "questionario_opcao"

    id: Optional[int] = Field(default=None, primary_key=True)
    pergunta_id: int = Field(foreign_key="questionario_pergunta.id")
    ordem: int
    texto: str = Field(max_length=200)
    valor_numerico: Optional[int] = None

    pergunta: Optional[QuestionarioPergunta] = Relationship(back_populates="opcoes")
    respostas_opcao: List["QuestionarioRespostaOpcao"] = Relationship(back_populates="opcao")


class QuestionarioResposta(SQLModel, table=True):
    __tablename__ = "questionario_resposta"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")
    ativacao_id: Optional[int] = Field(default=None, foreign_key="ativacao.id")
    lead_id: Optional[int] = Field(default=None, foreign_key="lead.id")

    data_resposta: datetime = Field(default_factory=now_utc)

    evento: Optional[Evento] = Relationship(back_populates="respostas_questionario")
    ativacao: Optional[Ativacao] = Relationship(back_populates="respostas_questionario")
    lead: Optional[Lead] = Relationship(back_populates="respostas_questionario")

    respostas_pergunta: List["QuestionarioRespostaPergunta"] = Relationship(
        back_populates="resposta"
    )


class QuestionarioRespostaPergunta(SQLModel, table=True):
    __tablename__ = "questionario_resposta_pergunta"

    id: Optional[int] = Field(default=None, primary_key=True)
    resposta_id: int = Field(foreign_key="questionario_resposta.id")
    pergunta_id: int = Field(foreign_key="questionario_pergunta.id")

    valor_texto: Optional[str] = None
    valor_numerico: Optional[Decimal] = None
    valor_data: Optional[date] = None

    resposta: Optional[QuestionarioResposta] = Relationship(back_populates="respostas_pergunta")
    pergunta: Optional[QuestionarioPergunta] = Relationship(back_populates="respostas")
    opcoes_marcadas: List["QuestionarioRespostaOpcao"] = Relationship(
        back_populates="resposta_pergunta"
    )


class QuestionarioRespostaOpcao(SQLModel, table=True):
    __tablename__ = "questionario_resposta_opcao"

    id: Optional[int] = Field(default=None, primary_key=True)
    resposta_pergunta_id: int = Field(foreign_key="questionario_resposta_pergunta.id")
    opcao_id: int = Field(foreign_key="questionario_opcao.id")

    resposta_pergunta: Optional[QuestionarioRespostaPergunta] = Relationship(
        back_populates="opcoes_marcadas"
    )
    opcao: Optional[QuestionarioOpcao] = Relationship(back_populates="respostas_opcao")


# =========================
# FORMULÁRIO DE LEAD / LANDING
# =========================


class FormularioLandingTemplate(SQLModel, table=True):
    __tablename__ = "formulario_landing_template"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=100, unique=True)
    html_conteudo: str
    css_conteudo: Optional[str] = Field(default=None)
    criado_em: datetime = Field(default_factory=now_utc)

    configuracoes: List["FormularioLeadConfig"] = Relationship(back_populates="template")


class FormularioLeadConfig(SQLModel, table=True):
    __tablename__ = "formulario_lead_config"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")
    nome: str = Field(max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=240)
    template_id: Optional[int] = Field(default=None, foreign_key="formulario_landing_template.id")

    url_landing: Optional[str] = Field(default=None, max_length=500)
    url_checkin_sem_qr: Optional[str] = Field(default=None, max_length=500)
    url_questionario: Optional[str] = Field(default=None, max_length=500)
    url_api: Optional[str] = Field(default=None, max_length=500)

    criado_em: datetime = Field(default_factory=now_utc)
    atualizado_em: datetime = Field(default_factory=now_utc)

    evento: Optional[Evento] = Relationship()
    template: Optional[FormularioLandingTemplate] = Relationship(back_populates="configuracoes")
    campos: List["FormularioLeadCampo"] = Relationship(back_populates="config")


class FormularioLeadCampo(SQLModel, table=True):
    __tablename__ = "formulario_lead_campo"

    id: Optional[int] = Field(default=None, primary_key=True)
    config_id: int = Field(foreign_key="formulario_lead_config.id")
    nome_campo: str = Field(max_length=80)
    obrigatorio: bool = Field(default=True)
    ordem: int

    config: Optional[FormularioLeadConfig] = Relationship(back_populates="campos")


# =========================
# INGESTION REGISTRY / CATALOGO DE FONTES (TMJ / ETL)
# =========================


class SourceKind(str, Enum):
    """Tipos de fonte suportados pelo pipeline de fechamento/ETL."""

    DOCX = "DOCX"
    PDF = "PDF"
    XLSX = "XLSX"
    PPTX = "PPTX"
    CSV = "CSV"
    MANUAL = "MANUAL"
    OTHER = "OTHER"


class IngestionStatus(str, Enum):
    """Status padronizado de execucao de ingestao."""

    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class Source(SQLModel, table=True):
    """Registro canonico de uma fonte (arquivo/artefato) no catalogo de ingestao."""

    __tablename__ = "source"

    # `source_id` e a chave estavel usada no fechamento (ex.: SRC_PDF_ACESSO_NOTURNO_TREZE).
    source_id: str = Field(primary_key=True, max_length=160)
    kind: SourceKind
    uri: str = Field(max_length=800)

    display_name: Optional[str] = Field(default=None, max_length=200)

    # Snapshot de arquivo (melhor-esforco). Pode ficar nulo para fontes nao-arquivo.
    file_sha256: Optional[str] = Field(default=None, max_length=64)
    file_size_bytes: Optional[int] = Field(default=None)
    file_mtime_utc: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    )

    ingestions: List["IngestionRun"] = Relationship(
        sa_relationship=relationship(
            "app.models.models.IngestionRun",
            back_populates="source",
        )
    )


class IngestionRun(SQLModel, table=True):
    """Uma execucao de ingestao para uma fonte.

    A regra operacional e: qualquer carga deve registrar uma execucao com status e logs,
    mesmo quando falhar.
    """

    __tablename__ = "ingestion"

    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: str = Field(foreign_key="source.source_id", index=True)

    pipeline: Optional[str] = Field(default=None, max_length=80)
    status: IngestionStatus = Field(default=IngestionStatus.RUNNING)

    started_at: datetime = Field(default_factory=now_utc)
    finished_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    file_sha256: Optional[str] = Field(default=None, max_length=64)
    file_size_bytes: Optional[int] = Field(default=None)

    log_text: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: datetime = Field(default_factory=now_utc)

    source: Optional["Source"] = Relationship(
        sa_relationship=relationship(
            "app.models.models.Source",
            back_populates="ingestions",
        )
    )


class MetricLineage(SQLModel, table=True):
    """Lineage de metricas: liga uma metrica agregada a uma fonte + local + evidencia.

    Observacao: valores numericos devem viver nas tabelas canonicas/marts. Esta tabela
    serve para auditoria, rastreabilidade e para o gerador de relatorio exibir "Fonte:".
    """

    __tablename__ = "metric_lineage"

    id: Optional[int] = Field(default=None, primary_key=True)

    metric_key: str = Field(max_length=200, index=True)
    docx_section: Optional[str] = Field(default=None, max_length=240)

    source_id: str = Field(foreign_key="source.source_id", index=True)
    ingestion_id: Optional[int] = Field(default=None, foreign_key="ingestion.id", index=True)

    location_raw: str = Field(max_length=200)
    location_norm: Optional[str] = Field(default=None, max_length=200)
    evidence: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: datetime = Field(default_factory=now_utc)

    source: Optional[Source] = Relationship()
    ingestion: Optional[IngestionRun] = Relationship()


# =========================
# TMJ / ETL - CANONICAL (NORMALIZACAO E REGRAS DE METRICA)
# =========================


class EventSessionType(str, Enum):
    """Tipos canonicos de sessao para fechamento (granularidade dia/sessao)."""

    DIURNO_GRATUITO = "DIURNO_GRATUITO"
    NOTURNO_SHOW = "NOTURNO_SHOW"
    OUTRO = "OUTRO"


class BbRelationshipSegment(str, Enum):
    """Segmentos canonicos (proxy) para relacionamento BB, derivados de categorias de ingresso."""

    CLIENTE_BB = "CLIENTE_BB"
    CARTAO_BB = "CARTAO_BB"
    FUNCIONARIO_BB = "FUNCIONARIO_BB"
    PUBLICO_GERAL = "PUBLICO_GERAL"
    OUTRO = "OUTRO"
    DESCONHECIDO = "DESCONHECIDO"


class EventSession(SQLModel, table=True):
    """Dimensao de sessoes do evento (dia/sessao), para ligar fatos a um `session_id` consistente."""

    __tablename__ = "event_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: Optional[int] = Field(default=None, foreign_key="evento.id", index=True)

    # Chave estavel (ex.: TMJ2025_20251213_SHOW).
    session_key: str = Field(max_length=120, unique=True, index=True)

    session_name: str = Field(max_length=200)
    session_type: EventSessionType = Field(index=True)

    # `session_date` e obrigatorio para suportar agregacoes por dia.
    session_date: date = Field(index=True)

    session_start_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    session_end_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    # Fonte que define a existencia (ou a "verdade") da sessao.
    source_of_truth_source_id: Optional[str] = Field(
        default=None, foreign_key="source.source_id", index=True
    )

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    )


class AttendanceAccessControl(SQLModel, table=True):
    """Fato de controle de acesso por sessao (entradas validadas e derivados)."""

    __tablename__ = "attendance_access_control"
    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "session_id",
            name="uq_attendance_access_control_source_session",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="event_sessions.id", index=True)

    source_id: str = Field(foreign_key="source.source_id", index=True, max_length=160)
    ingestion_id: Optional[int] = Field(default=None, foreign_key="ingestion.id", index=True)

    ingressos_validos: Optional[int] = None
    invalidos: Optional[int] = None
    bloqueados: Optional[int] = None
    presentes: Optional[int] = None
    ausentes: Optional[int] = None
    comparecimento_pct: Optional[Decimal] = Field(
        default=None, sa_column=Column(Numeric(7, 4), nullable=True)
    )

    pdf_page: Optional[int] = None
    evidence: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: datetime = Field(default_factory=now_utc)


class OptinTransaction(SQLModel, table=True):
    """Fato de opt-in (Eventim) em granularidade transacional, com minimizacao de PII."""

    __tablename__ = "optin_transactions"
    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "sheet_name",
            "row_number",
            name="uq_optin_transactions_source_sheet_row",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="event_sessions.id", index=True)

    source_id: str = Field(foreign_key="source.source_id", index=True, max_length=160)
    ingestion_id: Optional[int] = Field(default=None, foreign_key="ingestion.id", index=True)

    sheet_name: Optional[str] = Field(default=None, max_length=120)
    row_number: Optional[int] = None

    purchase_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    purchase_date: Optional[date] = Field(default=None, index=True)

    opt_in_text: Optional[str] = Field(default=None, max_length=200)
    opt_in_id: Optional[str] = Field(default=None, max_length=80)
    opt_in_status: Optional[str] = Field(default=None, max_length=80)

    sales_channel: Optional[str] = Field(default=None, max_length=160)
    delivery_method: Optional[str] = Field(default=None, max_length=160)

    ticket_category_raw: Optional[str] = Field(default=None, max_length=200)
    ticket_category_norm: Optional[str] = Field(default=None, max_length=200, index=True)
    ticket_qty: Optional[int] = None

    cpf_hash: Optional[str] = Field(default=None, max_length=64, index=True)
    email_hash: Optional[str] = Field(default=None, max_length=64, index=True)
    person_key_hash: Optional[str] = Field(default=None, max_length=64, index=True)

    created_at: datetime = Field(default_factory=now_utc)


class TicketCategorySegmentMap(SQLModel, table=True):
    """Mapeamento auditavel: categoria de ingresso -> segmento BB canonical."""

    __tablename__ = "ticket_category_segment_map"
    __table_args__ = (
        UniqueConstraint(
            "ticket_category_norm",
            name="uq_ticket_category_segment_map_ticket_category_norm",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    ticket_category_raw: str = Field(max_length=200)
    ticket_category_norm: str = Field(max_length=200, index=True)

    segment: BbRelationshipSegment = Field(index=True)

    inferred: bool = Field(default=True)
    inference_rule: Optional[str] = Field(default=None, max_length=200)

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    )


class TicketSales(SQLModel, table=True):
    """Fato de vendas (quando houver fonte completa de vendidos por sessao)."""

    __tablename__ = "ticket_sales"
    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "session_id",
            name="uq_ticket_sales_source_session",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="event_sessions.id", index=True)

    source_id: str = Field(foreign_key="source.source_id", index=True, max_length=160)
    ingestion_id: Optional[int] = Field(default=None, foreign_key="ingestion.id", index=True)

    sold_total: Optional[int] = None
    refunded_total: Optional[int] = None
    net_sold_total: Optional[int] = None

    location_raw: Optional[str] = Field(default=None, max_length=200)
    evidence: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: datetime = Field(default_factory=now_utc)


class FestivalLead(SQLModel, table=True):
    """Fato de leads capturados em planilhas (sem PII; chaves hash por padrao)."""

    __tablename__ = "festival_leads"
    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "sheet_name",
            "row_number",
            name="uq_festival_leads_source_sheet_row",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: Optional[int] = Field(default=None, foreign_key="evento.id", index=True)
    session_id: Optional[int] = Field(default=None, foreign_key="event_sessions.id", index=True)

    source_id: str = Field(foreign_key="source.source_id", index=True, max_length=160)
    ingestion_id: Optional[int] = Field(default=None, foreign_key="ingestion.id", index=True)

    sheet_name: Optional[str] = Field(default=None, max_length=120)
    row_number: Optional[int] = None

    lead_created_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    lead_created_date: Optional[date] = Field(default=None, index=True)

    cpf_hash: Optional[str] = Field(default=None, max_length=64, index=True)
    email_hash: Optional[str] = Field(default=None, max_length=64, index=True)
    person_key_hash: Optional[str] = Field(default=None, max_length=64, index=True)

    sexo: Optional[str] = Field(default=None, max_length=40)
    estado: Optional[str] = Field(default=None, max_length=40)
    cidade: Optional[str] = Field(default=None, max_length=120)

    acoes: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    interesses: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    area_atuacao: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: datetime = Field(default_factory=now_utc)


# =========================
# TMJ / ETL - DATA QUALITY + OBSERVABILIDADE
# =========================


class DataQualityScope(str, Enum):
    """Camada/escopo do check."""

    STAGING = "STAGING"
    CANONICAL = "CANONICAL"
    MARTS = "MARTS"


class DataQualitySeverity(str, Enum):
    """Severidade do check. ERROR bloqueia geracao/publicacao; WARN alerta."""

    WARN = "WARN"
    ERROR = "ERROR"


class DataQualityStatus(str, Enum):
    """Resultado do check."""

    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"


class IngestionEvidence(SQLModel, table=True):
    """Resumo persistido do envelope de evidencias do extractor (layout/drift)."""

    __tablename__ = "ingestion_evidence"
    __table_args__ = (
        UniqueConstraint("ingestion_id", "extractor", name="uq_ingestion_evidence_ingestion_extractor"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    ingestion_id: int = Field(foreign_key="ingestion.id", index=True)
    source_id: str = Field(foreign_key="source.source_id", index=True, max_length=160)

    extractor: str = Field(max_length=120)
    evidence_status: str = Field(max_length=40)

    layout_signature: Optional[str] = Field(default=None, max_length=64, index=True)
    stats_json: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    evidence_path: Optional[str] = Field(default=None, max_length=800)

    created_at: datetime = Field(default_factory=now_utc)


class DataQualityResult(SQLModel, table=True):
    """Resultado de um check de qualidade associado a uma execucao de ingestao."""

    __tablename__ = "data_quality_result"

    id: Optional[int] = Field(default=None, primary_key=True)

    ingestion_id: int = Field(foreign_key="ingestion.id", index=True)
    source_id: Optional[str] = Field(default=None, foreign_key="source.source_id", index=True, max_length=160)
    session_id: Optional[int] = Field(default=None, foreign_key="event_sessions.id", index=True)

    scope: DataQualityScope = Field(index=True)
    severity: DataQualitySeverity = Field(index=True)
    status: DataQualityStatus = Field(index=True)

    check_key: str = Field(max_length=220, index=True)
    message: str = Field(max_length=500)
    details: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: datetime = Field(default_factory=now_utc)
