from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import JSON, Column, DateTime, UniqueConstraint
from sqlmodel import Field

from app.db.metadata import SQLModel


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class LeadSilver(SQLModel, table=True):
    __tablename__ = "leads_silver"
    __table_args__ = (
        UniqueConstraint("batch_id", "row_index", name="uq_leads_silver_batch_row"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    batch_id: str = Field(foreign_key="lead_batches.id", index=True, max_length=36)
    row_index: int = Field(index=True)
    dados_brutos: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    evento_id: int = Field(foreign_key="evento.id", index=True)
    created_at: datetime = Field(default_factory=_now_utc, sa_column=Column(DateTime(timezone=True), nullable=False))


__all__ = ["LeadSilver"]
