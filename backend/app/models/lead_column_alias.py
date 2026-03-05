from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from app.db.metadata import SQLModel


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class LeadColumnAlias(SQLModel, table=True):
    __tablename__ = "lead_column_aliases"
    __table_args__ = (
        UniqueConstraint(
            "nome_coluna_original",
            "plataforma_origem",
            name="uq_lead_column_aliases_coluna_plataforma",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    nome_coluna_original: str = Field(max_length=255)
    campo_canonico: str = Field(max_length=120)
    plataforma_origem: str = Field(max_length=80, index=True)
    criado_por: int = Field(foreign_key="usuario.id", index=True)
    created_at: datetime = Field(default_factory=_now_utc)


__all__ = ["LeadColumnAlias"]
