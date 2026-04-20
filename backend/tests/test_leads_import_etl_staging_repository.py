from __future__ import annotations

from types import SimpleNamespace

from app.modules.leads_publicidade.application.etl_import.staging_repository import (
    choose_staging_ingestion_strategy,
    persist_staging_rows,
)


class _FakeSession:
    def __init__(self, dialect_name: str):
        self._bind = SimpleNamespace(dialect=SimpleNamespace(name=dialect_name))

    def get_bind(self):
        return self._bind


def test_choose_staging_ingestion_strategy_uses_copy_for_large_postgres_load(monkeypatch) -> None:
    monkeypatch.setenv("LEAD_IMPORT_ETL_COPY_MIN_ROWS", "10")
    session = _FakeSession("postgresql")

    strategy = choose_staging_ingestion_strategy(
        session,
        total_rows=10,
        source_file_size_bytes=1024,
    )

    assert strategy == "copy"


def test_choose_staging_ingestion_strategy_keeps_insert_for_non_postgres(monkeypatch) -> None:
    monkeypatch.setenv("LEAD_IMPORT_ETL_COPY_MIN_ROWS", "10")
    session = _FakeSession("sqlite")

    strategy = choose_staging_ingestion_strategy(
        session,
        total_rows=1000,
        source_file_size_bytes=32 * 1024 * 1024,
    )

    assert strategy == "insert"


def test_persist_staging_rows_falls_back_to_insert_when_copy_fails(monkeypatch) -> None:
    monkeypatch.setenv("LEAD_IMPORT_ETL_COPY_MIN_ROWS", "1")
    session = _FakeSession("postgresql")
    calls: list[str] = []

    def broken_copy(_session, _rows):
        calls.append("copy")
        raise RuntimeError("copy unsupported by current connection")

    def insert_stub(_session, _rows):
        calls.append("insert")

    monkeypatch.setattr(
        "app.modules.leads_publicidade.application.etl_import.staging_repository._copy_rows_to_staging",
        broken_copy,
    )
    monkeypatch.setattr(
        "app.modules.leads_publicidade.application.etl_import.staging_repository._insert_rows_to_staging",
        insert_stub,
    )

    strategy = persist_staging_rows(
        session,
        rows=[
            {
                "session_token": "session-1",
                "source_row_number": 1,
            }
        ],
        source_file_size_bytes=1024,
    )

    assert strategy == "insert"
    assert calls == ["copy", "insert"]
