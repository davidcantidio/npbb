"""Unit tests for ETL preview rejection reason aggregation."""

from __future__ import annotations

from app.modules.lead_imports.application.etl_import.contracts import EtlPreviewRow
from app.modules.lead_imports.application.etl_import.rejection_reasons import (
    aggregate_rejection_reason_counts,
)
from app.modules.lead_imports.application.etl_import.validators import (
    INVALID_CPF_REASON,
    MALFORMED_EMAIL_REASON,
    MISSING_CPF_REASON,
)


def test_aggregate_empty_rejections() -> None:
    assert aggregate_rejection_reason_counts(()) == {}


def test_aggregate_cpf_missing_and_email() -> None:
    rows = (
        EtlPreviewRow(row_number=1, payload={}, errors=[MISSING_CPF_REASON]),
        EtlPreviewRow(row_number=2, payload={}, errors=[MALFORMED_EMAIL_REASON]),
    )
    out = aggregate_rejection_reason_counts(rows)
    assert out["cpf_missing"] == 1
    assert out["email_malformed"] == 1


def test_aggregate_invalid_cpf() -> None:
    rows = (EtlPreviewRow(row_number=1, payload={}, errors=[INVALID_CPF_REASON]),)
    assert aggregate_rejection_reason_counts(rows) == {"cpf_invalid": 1}


def test_aggregate_pydantic_style_message() -> None:
    rows = (EtlPreviewRow(row_number=1, payload={}, errors=["Field required"]),)
    assert aggregate_rejection_reason_counts(rows) == {"pydantic_validation": 1}
