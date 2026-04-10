"""Lead, publicidade e staging ligados ao fluxo transacional legado."""

from datetime import date, datetime, time
from enum import Enum
from typing import List, Optional

from sqlalchemy import CheckConstraint, Column, DateTime, Enum as SQLEnum, Text, UniqueConstraint
from sqlmodel import Field, Relationship

from app.db.metadata import SQLModel
from app.models.models import LeadAliasTipo, LeadConversaoTipo, now_utc


def _enum_values(enum_cls: type[Enum]) -> list[str]:
    return [member.value for member in enum_cls]


class LeadEventoSourceKind(str, Enum):
    ACTIVATION = "ativacao"
    EVENT_DIRECT = "event_id_direct"
    LEAD_BATCH = "lead_batch"
    EVENT_NAME_BACKFILL = "evento_nome_backfill"
    MANUAL_RECONCILED = "manual_reconciled"


class TipoLead(str, Enum):
    BILHETERIA = "bilheteria"
    ENTRADA_EVENTO = "entrada_evento"
    ATIVACAO = "ativacao"


class TipoResponsavel(str, Enum):
    PROPONENTE = "proponente"
    AGENCIA = "agencia"


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
    is_cliente_bb: Optional[bool] = Field(
        default=None,
        index=True,
        description="True = cliente BB confirmado; False = nao cliente BB; NULL = cruzamento pendente.",
    )
    is_cliente_estilo: Optional[bool] = Field(
        default=None,
        index=True,
        description="True = cliente Estilo confirmado; False = nao cliente BB; NULL = cruzamento pendente.",
    )
    batch_id: Optional[int] = Field(default=None, foreign_key="lead_batches.id", index=True)

    ativacoes: List["AtivacaoLead"] = Relationship(back_populates="lead")
    lead_eventos: List["LeadEvento"] = Relationship(back_populates="lead")
    cupons: List["Cupom"] = Relationship(back_populates="lead")
    respostas_questionario: List["QuestionarioResposta"] = Relationship(back_populates="lead")
    conversoes: List["LeadConversao"] = Relationship(back_populates="lead")
    conversoes_ativacao: List["ConversaoAtivacao"] = Relationship(back_populates="lead")
    reconhecimento_tokens: List["LeadReconhecimentoToken"] = Relationship(back_populates="lead")


class LeadEvento(SQLModel, table=True):
    __tablename__ = "lead_evento"
    __table_args__ = (
        UniqueConstraint("lead_id", "evento_id", name="uq_lead_evento_lead_id_evento_id"),
        CheckConstraint(
            "tipo_lead IS NULL OR tipo_lead != 'ativacao' OR "
            "(responsavel_tipo IS NOT NULL AND responsavel_tipo = 'agencia')",
            name="tipo_lead_ativacao_agencia",
        ),
        CheckConstraint(
            "responsavel_tipo IS NULL OR "
            "(responsavel_nome IS NOT NULL AND length(trim(responsavel_nome)) > 0)",
            name="responsavel_nome_required",
        ),
        CheckConstraint(
            "responsavel_tipo IS NULL OR "
            "(responsavel_tipo = 'agencia' AND responsavel_agencia_id IS NOT NULL) OR "
            "(responsavel_tipo = 'proponente' AND responsavel_agencia_id IS NULL)",
            name="responsavel_agencia_consistency",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    lead_id: int = Field(foreign_key="lead.id", index=True)
    evento_id: int = Field(foreign_key="evento.id", index=True)
    source_kind: LeadEventoSourceKind = Field(index=True)
    source_ref_id: Optional[int] = Field(default=None, index=True)
    tipo_lead: Optional[TipoLead] = Field(
        default=None,
        sa_column=Column(
            SQLEnum(TipoLead, name="tipolead", values_callable=_enum_values),
            nullable=True,
            index=True,
        ),
    )
    responsavel_tipo: Optional[TipoResponsavel] = Field(
        default=None,
        sa_column=Column(
            SQLEnum(TipoResponsavel, name="tiporesponsavel", values_callable=_enum_values),
            nullable=True,
            index=True,
        ),
    )
    responsavel_nome: Optional[str] = Field(default=None, max_length=150)
    responsavel_agencia_id: Optional[int] = Field(
        default=None,
        foreign_key="agencia.id",
        index=True,
    )
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    )

    lead: Optional["Lead"] = Relationship(back_populates="lead_eventos")
    evento: Optional["Evento"] = Relationship(back_populates="lead_eventos")
    responsavel_agencia: Optional["Agencia"] = Relationship()


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
    __table_args__ = (
        UniqueConstraint("tipo", "valor_normalizado", name="uq_lead_alias_tipo_valor_normalizado"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    tipo: LeadAliasTipo
    valor_origem: str = Field(max_length=200)
    valor_normalizado: str = Field(max_length=200)
    canonical_value: Optional[str] = Field(default=None, max_length=200)
    evento_id: Optional[int] = Field(default=None, foreign_key="evento.id")
    created_at: datetime = Field(default_factory=now_utc)

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
