"""Schemas do fluxo de importacao assistida de publicidade."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PublicidadeImportMapping(BaseModel):
    coluna: str
    campo: Optional[str] = None
    confianca: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class PublicidadeAliasHit(BaseModel):
    id: int
    domain: str
    field_name: str
    source_value: str
    source_normalized: str
    canonical_value: Optional[str] = None
    canonical_ref_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class PublicidadeImportPreview(BaseModel):
    filename: str
    headers: list[str]
    rows: list[list[str]]
    delimiter: Optional[str] = None
    start_index: int
    suggestions: list[PublicidadeImportMapping]
    samples_by_column: list[list[str]]
    alias_hits: list[PublicidadeAliasHit | None] = Field(default_factory=list)


class PublicidadeImportError(BaseModel):
    line: int
    field: str
    message: str
    value: Optional[str] = None


class PublicidadeImportValidateResponse(BaseModel):
    ok: bool


class PublicidadeImportReport(BaseModel):
    filename: str
    received_rows: int
    valid_rows: int
    staged_inserted: int
    staged_skipped: int
    upsert_inserted: int
    upsert_updated: int
    unresolved_event_id: int
    errors: list[PublicidadeImportError] = Field(default_factory=list)


class PublicidadeEventReference(BaseModel):
    id: int
    nome: str
    external_project_code: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PublicidadeAliasRead(BaseModel):
    id: int
    domain: str
    field_name: str
    source_value: str
    source_normalized: str
    canonical_value: Optional[str] = None
    canonical_ref_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublicidadeAliasUpsert(BaseModel):
    field_name: str
    valor_origem: str
    canonical_value: Optional[str] = None
    canonical_ref_id: Optional[int] = Field(default=None, ge=1)


class EventPublicityRead(BaseModel):
    id: int
    event_id: Optional[int] = None
    publicity_project_code: str
    publicity_project_name: str
    linked_at: date
    medium: str
    vehicle: str
    uf: str
    uf_name: Optional[str] = None
    municipality: Optional[str] = None
    layer: str
    source_file: Optional[str] = None
    source_row_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
