"""Tests for DQ cross-source inconsistency persistence model."""

from __future__ import annotations

from app.models.dq_inconsistency import (
    DQInconsistency,
    DQInconsistencySeverity,
    DQInconsistencyStatus,
)


def test_dq_inconsistency_model_table_name() -> None:
    """Model imports correctly and points to expected table."""

    assert DQInconsistency.__tablename__ == "dq_inconsistency"


def test_dq_inconsistency_domain_values() -> None:
    """Enum domains should remain explicit and controlled."""

    assert {item.value for item in DQInconsistencyStatus} == {"inconsistente"}
    assert {item.value for item in DQInconsistencySeverity} == {"info", "warning", "error"}


def test_dq_inconsistency_fk_and_indexes() -> None:
    """Model should keep ingestion FK and operational indexes."""

    table = DQInconsistency.__table__
    fk_targets = {
        f"{fk.column.table.name}.{fk.column.name}"
        for constraint in table.foreign_key_constraints
        for fk in constraint.elements
    }
    assert "ingestions.id" in fk_targets

    indexed_columns = {
        column.name
        for index in table.indexes
        for column in index.columns
    }
    assert {"ingestion_id", "check_id", "dataset_id", "metric_key", "status", "severity"} <= indexed_columns

