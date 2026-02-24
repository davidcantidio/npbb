"""Unit tests for core ingestion registry contracts and errors."""

from __future__ import annotations

from datetime import datetime, timezone

from core.registry import (
    IngestionId,
    IngestionNotFoundError,
    IngestionRecord,
    InvalidIngestionStatusError,
    InvalidStatusTransitionError,
    RegistryReader,
    RegistryRepository,
    SourceId,
    SourceNotFoundError,
    SourceRecord,
    TERMINAL_INGESTION_STATUSES,
)


class _InMemoryRegistry:
    """Minimal adapter implementing registry protocol surface for tests."""

    def get_source(self, source_id: SourceId):  # noqa: ANN001
        return None

    def get_ingestion(self, ingestion_id: IngestionId):  # noqa: ANN001
        return None

    def get_latest_ingestion_by_source(self, source_id: SourceId):  # noqa: ANN001
        return None

    def upsert_source(self, source: SourceRecord) -> SourceRecord:
        return source

    def start_ingestion(self, **kwargs):  # noqa: ANN003
        return IngestionRecord(
            ingestion_id=IngestionId(1),
            source_id=SourceId("src_a"),
            status="RUNNING",
            started_at=datetime.now(timezone.utc),
        )

    def finish_ingestion(self, **kwargs):  # noqa: ANN003
        return IngestionRecord(
            ingestion_id=IngestionId(1),
            source_id=SourceId("src_a"),
            status="SUCCEEDED",
            finished_at=datetime.now(timezone.utc),
        )


def test_registry_module_exports_import_and_protocol_contracts() -> None:
    """Registry package exports import correctly and protocols are runtime-checkable."""
    adapter = _InMemoryRegistry()
    assert isinstance(adapter, RegistryReader)
    assert isinstance(adapter, RegistryRepository)


def test_registry_base_types_and_records_work() -> None:
    """Base aliases and dataclasses can be instantiated safely."""
    source = SourceRecord(source_id=SourceId("src_pdf_001"), kind="PDF", uri="file:///tmp/a.pdf")
    ingestion = IngestionRecord(
        ingestion_id=IngestionId(42),
        source_id=source.source_id,
        status="RUNNING",
        pipeline="extract_pdf_access",
    )
    assert source.source_id == "src_pdf_001"
    assert ingestion.ingestion_id == 42
    assert set(TERMINAL_INGESTION_STATUSES) == {"SUCCEEDED", "FAILED", "SKIPPED"}


def test_registry_errors_are_actionable() -> None:
    """Registry exceptions include actionable remediation guidance."""
    assert "Como corrigir" in str(SourceNotFoundError(SourceId("src_missing")))
    assert "Como corrigir" in str(IngestionNotFoundError(IngestionId(99)))
    assert "status permitido" in str(InvalidIngestionStatusError("DONE")).casefold()
    assert "Transicao de status invalida" in str(InvalidStatusTransitionError("RUNNING", "RUNNING"))
