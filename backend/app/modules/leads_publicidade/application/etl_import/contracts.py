"""Internal contracts for ETL preview and commit flows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


PreviewStatus = Literal["previewed", "committed", "expired", "rejected", "partial_failure"]


@dataclass(frozen=True)
class EtlPreviewDQItem:
    check_name: str
    severity: str
    affected_rows: int
    sample: list[dict[str, Any]] = field(default_factory=list)
    check_id: str | None = None
    message: str | None = None


@dataclass(frozen=True)
class EtlPreviewRow:
    row_number: int
    payload: dict[str, Any]
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EtlHeaderColumn:
    column_index: int
    column_letter: str
    source_value: str


@dataclass(frozen=True)
class EtlFieldAliasSelection:
    column_index: int | None = None
    source_value: str | None = None


@dataclass(frozen=True)
class EtlHeaderRequired:
    status: Literal["header_required"]
    message: str
    max_row: int
    scanned_rows: int
    required_fields: tuple[str, ...] = ("cpf",)


@dataclass(frozen=True)
class EtlCpfColumnRequired:
    status: Literal["cpf_column_required"]
    message: str
    header_row: int
    columns: tuple[EtlHeaderColumn, ...]
    required_fields: tuple[str, ...] = ("cpf",)


@dataclass(frozen=True)
class EtlPreviewSnapshot:
    session_token: str
    filename: str
    evento_id: int
    evento_nome: str
    strict: bool
    total_rows: int
    valid_rows: int
    invalid_rows: int
    approved_rows: tuple[EtlPreviewRow, ...]
    rejected_rows: tuple[EtlPreviewRow, ...]
    dq_report: tuple[EtlPreviewDQItem, ...]
    status: PreviewStatus
    idempotency_key: str
    has_validation_errors: bool
    has_warnings: bool


@dataclass(frozen=True)
class EtlCommitResult:
    session_token: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    created: int
    updated: int
    skipped: int
    errors: int
    strict: bool
    status: PreviewStatus
    dq_report: tuple[EtlPreviewDQItem, ...]
    persistence_failures: tuple[tuple[int, str], ...] = field(default_factory=tuple)
