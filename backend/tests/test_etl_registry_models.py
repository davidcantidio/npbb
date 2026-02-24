"""Tests for ETL registry ORM models and status domain."""

from __future__ import annotations

from app.models.etl_registry import IngestionRun, IngestionStatus, Source, SourceKind


def test_etl_registry_models_import_and_table_names() -> None:
    """Registry models import correctly and expose expected table names."""
    assert Source.__tablename__ == "sources"
    assert IngestionRun.__tablename__ == "ingestions"


def test_etl_registry_status_domain_and_constraints() -> None:
    """Ingestion status enum and check constraints follow controlled domain."""
    assert {status.value for status in IngestionStatus} == {"success", "failed", "partial"}
    checks = [constraint for constraint in IngestionRun.__table__.constraints if constraint.__class__.__name__ == "CheckConstraint"]
    assert any("status in ('SUCCESS','FAILED','PARTIAL')" in str(constraint.sqltext) for constraint in checks)


def test_etl_registry_source_unique_constraint_and_kind_domain() -> None:
    """Source model defines unique source_id constraint and source kind domain."""
    assert {kind.value for kind in SourceKind} >= {"pdf", "xlsx", "pptx", "docx"}
    uniques = [constraint for constraint in Source.__table__.constraints if constraint.__class__.__name__ == "UniqueConstraint"]
    assert any("source_id" in [column.name for column in constraint.columns] for constraint in uniques)
