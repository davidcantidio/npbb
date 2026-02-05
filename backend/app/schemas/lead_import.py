"""Schemas para mapeamento de importacao de leads."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class LeadImportMapping(BaseModel):
    coluna: str
    campo: Optional[str] = None
    confianca: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
