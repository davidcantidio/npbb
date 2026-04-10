"""Schemas for ETL lead import preview and commit endpoints."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class DQCheckResult(BaseModel):
    check_name: str
    severity: Literal["error", "warning", "info"]
    affected_rows: int
    sample: list[dict[str, Any]] = Field(default_factory=list)
    check_id: str | None = None
    message: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ImportEtlPreviewResponse(BaseModel):
    status: Literal["previewed"] = "previewed"
    session_token: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    dq_report: list[DQCheckResult]

    model_config = ConfigDict(from_attributes=True)


class ImportEtlHeaderColumn(BaseModel):
    column_index: int
    column_letter: str
    source_value: str

    model_config = ConfigDict(from_attributes=True)


class ImportEtlHeaderRequiredResponse(BaseModel):
    status: Literal["header_required"]
    message: str
    max_row: int
    scanned_rows: int
    required_fields: list[str] = Field(default_factory=lambda: ["cpf"])

    model_config = ConfigDict(from_attributes=True)


class ImportEtlCpfColumnRequiredResponse(BaseModel):
    status: Literal["cpf_column_required"]
    message: str
    header_row: int
    columns: list[ImportEtlHeaderColumn]
    required_fields: list[str] = Field(default_factory=lambda: ["cpf"])

    model_config = ConfigDict(from_attributes=True)


ImportEtlPreviewResponseUnion = Annotated[
    ImportEtlPreviewResponse | ImportEtlHeaderRequiredResponse | ImportEtlCpfColumnRequiredResponse,
    Field(discriminator="status"),
]


class ImportEtlCommitRequest(BaseModel):
    session_token: str
    evento_id: int
    force_warnings: bool = False


class ImportEtlResult(BaseModel):
    session_token: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    created: int
    updated: int
    skipped: int
    errors: int
    strict: bool
    status: Literal["previewed", "committed", "expired", "rejected"]
    dq_report: list[DQCheckResult]

    model_config = ConfigDict(from_attributes=True)
