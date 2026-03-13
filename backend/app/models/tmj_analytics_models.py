"""Modelos de ingestao, canonical ETL e data quality que nao precisam viver no core transacional."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, DateTime, Numeric, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship

from app.db.metadata import SQLModel
from app.models.models import now_utc


class SourceKind(str, Enum):
    DOCX = "DOCX"
    PDF = "PDF"
    XLSX = "XLSX"
    PPTX = "PPTX"
    CSV = "CSV"
    MANUAL = "MANUAL"
    OTHER = "OTHER"


class IngestionStatus(str, Enum):
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class Source(SQLModel, table=True):
    __tablename__ = "source"

    source_id: str = Field(primary_key=True, max_length=160)
    kind: SourceKind
    uri: str = Field(max_length=800)
    display_name: Optional[str] = Field(default=None, max_length=200)
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
            "app.models.tmj_analytics_models.IngestionRun",
            back_populates="source",
        )
    )


class IngestionRun(SQLModel, table=True):
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
            "app.models.tmj_analytics_models.Source",
            back_populates="ingestions",
        )
    )


class MetricLineage(SQLModel, table=True):
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

    source: Optional["Source"] = Relationship(
        sa_relationship=relationship("app.models.tmj_analytics_models.Source")
    )
    ingestion: Optional["IngestionRun"] = Relationship(
        sa_relationship=relationship("app.models.tmj_analytics_models.IngestionRun")
    )


class EventSessionType(str, Enum):
    DIURNO_GRATUITO = "DIURNO_GRATUITO"
    NOTURNO_SHOW = "NOTURNO_SHOW"
    OUTRO = "OUTRO"


class BbRelationshipSegment(str, Enum):
    CLIENTE_BB = "CLIENTE_BB"
    CARTAO_BB = "CARTAO_BB"
    FUNCIONARIO_BB = "FUNCIONARIO_BB"
    PUBLICO_GERAL = "PUBLICO_GERAL"
    OUTRO = "OUTRO"
    DESCONHECIDO = "DESCONHECIDO"


class EventSession(SQLModel, table=True):
    __tablename__ = "event_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: Optional[int] = Field(default=None, foreign_key="evento.id", index=True)
    session_key: str = Field(max_length=120, unique=True, index=True)
    session_name: str = Field(max_length=200)
    session_type: EventSessionType = Field(index=True)
    session_date: date = Field(index=True)
    session_start_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    session_end_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    source_of_truth_source_id: Optional[str] = Field(
        default=None, foreign_key="source.source_id", index=True
    )
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    )


class AttendanceAccessControl(SQLModel, table=True):
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


class DataQualityScope(str, Enum):
    STAGING = "STAGING"
    CANONICAL = "CANONICAL"
    MARTS = "MARTS"


class DataQualitySeverity(str, Enum):
    WARN = "WARN"
    ERROR = "ERROR"


class DataQualityStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"


class IngestionEvidence(SQLModel, table=True):
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
