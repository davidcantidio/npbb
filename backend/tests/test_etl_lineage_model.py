"""Tests for ETL lineage ORM model and location-type domain."""

from __future__ import annotations

from app.models.etl_lineage import LineageLocationType, LineageRef


def test_etl_lineage_model_import_and_table_name() -> None:
    """Lineage model imports correctly and targets expected table name."""
    assert LineageRef.__tablename__ == "lineage_refs"


def test_etl_lineage_location_type_domain() -> None:
    """Location type enum exposes controlled domain values."""
    assert {item.value for item in LineageLocationType} == {"page", "slide", "sheet", "range"}


def test_etl_lineage_foreign_keys_and_indexes_exist() -> None:
    """Lineage model defines FKs to sources/ingestions and key indexes."""
    table = LineageRef.__table__
    fk_targets = {
        f"{fk.column.table.name}.{fk.column.name}"
        for constraint in table.foreign_key_constraints
        for fk in constraint.elements
    }
    assert "sources.source_id" in fk_targets
    assert "ingestions.id" in fk_targets

    indexed_columns = {
        column.name
        for index in table.indexes
        for column in index.columns
    }
    assert {"source_id", "ingestion_id", "location_type"} <= indexed_columns

