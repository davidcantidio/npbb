"""Schemas for ETL lead import preview and commit endpoints."""

from __future__ import annotations

from datetime import datetime
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
    rejection_reason_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Contagem de linhas rejeitadas por bucket de motivo (preview ETL).",
    )
    sheet_name: str | None = None
    available_sheets: list[str] = Field(default_factory=list)

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
    available_sheets: list[str] = Field(default_factory=list)
    active_sheet: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ImportEtlCpfColumnRequiredResponse(BaseModel):
    status: Literal["cpf_column_required"]
    message: str
    header_row: int
    columns: list[ImportEtlHeaderColumn]
    required_fields: list[str] = Field(default_factory=lambda: ["cpf"])
    available_sheets: list[str] = Field(default_factory=list)
    active_sheet: str | None = None

    model_config = ConfigDict(from_attributes=True)


ImportEtlPreviewResponseUnion = Annotated[
    ImportEtlPreviewResponse | ImportEtlHeaderRequiredResponse | ImportEtlCpfColumnRequiredResponse,
    Field(discriminator="status"),
]


class ImportEtlCommitRequest(BaseModel):
    session_token: str
    evento_id: int
    force_warnings: bool = False


class LeadImportEtlFieldAliasSelection(BaseModel):
    column_index: int | None = None
    source_value: str | None = None


class ImportEtlJobProgressRead(BaseModel):
    phase: Literal["preview", "commit"]
    label: str
    pct: int | None = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


ImportEtlJobStatus = Literal[
    "queued",
    "running",
    "header_required",
    "cpf_column_required",
    "previewed",
    "commit_queued",
    "committing",
    "committed",
    "partial_failure",
    "failed",
]


class ImportEtlJobQueuedResponse(BaseModel):
    job_id: str
    status: Literal["queued", "commit_queued"]


class ImportEtlJobReprocessRequest(BaseModel):
    header_row: int | None = None
    field_aliases: dict[str, LeadImportEtlFieldAliasSelection] = Field(default_factory=dict)
    sheet_name: str | None = None
    max_scan_rows: int | None = None


class ImportEtlJobCommitRequest(BaseModel):
    force_warnings: bool = False


class ImportEtlPersistenceFailure(BaseModel):
    row_number: int
    reason: str

    model_config = ConfigDict(from_attributes=True)


class ImportEtlJobSummaryRead(BaseModel):
    session_token: str
    total_rows: int
    staged_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    created_rows: int
    updated_rows: int
    skipped_rows: int
    error_rows: int
    ingestion_strategy: str | None = None
    merge_strategy: str | None = None
    source_file_size_bytes: int | None = None
    committed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ImportEtlJobErrorRead(BaseModel):
    row_number: int
    phase: Literal["validation", "merge"]
    status: str
    message: str

    model_config = ConfigDict(from_attributes=True)


class ImportEtlJobErrorsResponse(BaseModel):
    job_id: str
    session_token: str | None = None
    total: int
    items: list[ImportEtlJobErrorRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


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
    status: Literal["previewed", "committed", "expired", "rejected", "partial_failure"]
    duplicate_rows: int = 0
    staged_rows: int = 0
    ingestion_strategy: str | None = None
    merge_strategy: str | None = None
    dq_report: list[DQCheckResult]
    persistence_failures: list[ImportEtlPersistenceFailure] = Field(
        default_factory=list,
        description=(
            "Linhas que falharam na persistencia do commit. "
            "Enquanto status for partial_failure, o commit nao esta fechado; "
            "repetir POST /leads/import/etl/commit com o mesmo session_token para retentar."
        ),
    )

    model_config = ConfigDict(from_attributes=True)


class ImportEtlJobRead(BaseModel):
    job_id: str
    evento_id: int
    filename: str
    status: ImportEtlJobStatus
    strict: bool = False
    preview_session_token: str | None = None
    progress: ImportEtlJobProgressRead | None = None
    preview_result: ImportEtlPreviewResponseUnion | None = None
    commit_result: ImportEtlResult | None = None
    summary: ImportEtlJobSummaryRead | None = None
    error_code: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
