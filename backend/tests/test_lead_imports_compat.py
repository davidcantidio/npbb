"""Compatibility coverage for the temporary leads_publicidade import path."""

from __future__ import annotations

import importlib


def test_legacy_deep_import_aliases_real_module() -> None:
    real = importlib.import_module(
        "app.modules.lead_imports.application.etl_import.persistence"
    )
    legacy = importlib.import_module(
        "app.modules.leads_publicidade.application.etl_import.persistence"
    )

    assert legacy is real
    assert legacy.persist_lead_batch is real.persist_lead_batch


def test_legacy_dotted_monkeypatch_reaches_real_module(monkeypatch) -> None:
    real = importlib.import_module(
        "app.modules.lead_imports.application.etl_import.staging_repository"
    )

    def fake_copy_rows_to_staging(*_args, **_kwargs):
        return None

    monkeypatch.setattr(
        "app.modules.leads_publicidade.application.etl_import."
        "staging_repository._copy_rows_to_staging",
        fake_copy_rows_to_staging,
    )
    legacy = importlib.import_module(
        "app.modules.leads_publicidade.application.etl_import.staging_repository"
    )

    assert legacy is real
    assert real._copy_rows_to_staging is fake_copy_rows_to_staging
