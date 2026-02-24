"""Staging models for XLSX leads and parsed actions.

These tables persist extracted leads before canonical normalization and keep:
- ingestion lineage (`ingestion_id`, `lineage_ref_id`),
- row-level traceability (`sheet_name`, `row_number`, `source_range`),
- parsed lead actions in a normalized child table.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, DateTime, Text, UniqueConstraint
from sqlmodel import Field

from app.db.metadata import SQLModel


def now_utc() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class StgLead(SQLModel, table=True):
    """Staging row extracted from TMJ leads XLSX."""

    __tablename__ = "stg_leads"
    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "sheet_name",
            "row_number",
            name="uq_stg_leads_source_sheet_row",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: str = Field(max_length=160, foreign_key="sources.source_id", index=True)
    ingestion_id: int = Field(foreign_key="ingestions.id", index=True)
    lineage_ref_id: int = Field(foreign_key="lineage_refs.id", index=True)

    sheet_name: str = Field(max_length=120, index=True)
    header_row: int
    row_number: int
    source_range: str = Field(max_length=64)

    evento: Optional[str] = Field(default=None, max_length=200)
    data_criacao: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    sexo: Optional[str] = Field(default=None, max_length=40)
    estado: Optional[str] = Field(default=None, max_length=40)
    cidade: Optional[str] = Field(default=None, max_length=120)
    interesses: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    area_atuacao: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    cpf_hash: Optional[str] = Field(default=None, max_length=64, index=True)
    email_hash: Optional[str] = Field(default=None, max_length=64, index=True)
    person_key_hash: Optional[str] = Field(default=None, max_length=64, index=True)
    cpf_promotor_hash: Optional[str] = Field(default=None, max_length=64, index=True)
    nome_promotor: Optional[str] = Field(default=None, max_length=200)

    acoes_raw: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    raw_payload_json: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=now_utc)


class StgLeadAction(SQLModel, table=True):
    """Normalized action values parsed from one staging lead row."""

    __tablename__ = "stg_lead_actions"
    __table_args__ = (
        UniqueConstraint(
            "lead_id",
            "action_norm",
            name="uq_stg_lead_actions_lead_action_norm",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    lead_id: int = Field(foreign_key="stg_leads.id", index=True)
    source_id: str = Field(max_length=160, foreign_key="sources.source_id", index=True)
    ingestion_id: int = Field(foreign_key="ingestions.id", index=True)
    lineage_ref_id: int = Field(foreign_key="lineage_refs.id", index=True)

    action_order: int
    action_raw: str = Field(max_length=200)
    action_norm: str = Field(max_length=200, index=True)
    created_at: datetime = Field(default_factory=now_utc)

