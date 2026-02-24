"""Unit tests for coverage contract loader and matrix compatibility."""

from __future__ import annotations

from pathlib import Path
import sys
from textwrap import dedent

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.etl_registry import CoverageDataset  # noqa: E402
from app.models.models import EventSessionType  # noqa: E402
from etl.validate.coverage_contract import (  # noqa: E402
    CoverageContractError,
    coverage_requirements_from_contract,
    load_coverage_contract,
    required_datasets_for_session_type,
)
from etl.validate.coverage_matrix import load_coverage_requirements_config  # noqa: E402


def test_load_default_coverage_contract_has_show_critical_access_control() -> None:
    """Default contract should define critical access-control requirement for show."""

    contract = load_coverage_contract()
    show = contract.session_types[EventSessionType.NOTURNO_SHOW]
    by_dataset = {rule.dataset: rule for rule in show.datasets}

    access = by_dataset[CoverageDataset.ACCESS_CONTROL]
    assert access.required is True
    assert access.severity.value == "error"
    assert access.status_on_missing == "gap"
    assert {"ok", "gap", "partial"}.issubset(set(contract.status_domain))


def test_load_default_coverage_contract_marks_show_optin_as_required_critical() -> None:
    """Show opt-in rule should be configured as required and critical by default."""

    contract = load_coverage_contract()
    show = contract.session_types[EventSessionType.NOTURNO_SHOW]
    by_dataset = {rule.dataset: rule for rule in show.datasets}

    optin = by_dataset[CoverageDataset.OPTIN]
    assert optin.required is True
    assert optin.severity.value == "error"
    assert optin.status_on_missing == "partial"


def test_coverage_contract_rejects_show_without_access_control(tmp_path: Path) -> None:
    """Contract loader should fail when show session misses critical access dataset."""

    path = tmp_path / "coverage_contract_invalid.yml"
    path.write_text(
        dedent(
            """
            version: 1
            status_domain: [ok, gap, partial]
            default_required_datasets: [access_control]
            session_types:
              NOTURNO_SHOW:
                datasets:
                  - dataset: ticket_sales
                    required: true
                    severity: error
                    status_on_missing: gap
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(CoverageContractError, match="access_control"):
        load_coverage_contract(path)


def test_coverage_requirements_view_is_consumable_by_evaluator() -> None:
    """Derived requirements should expose required datasets per session type."""

    contract = load_coverage_contract()
    requirements = coverage_requirements_from_contract(contract)

    assert requirements.default_required_datasets == (CoverageDataset.ACCESS_CONTROL,)
    assert requirements.required_datasets_by_session_type[EventSessionType.NOTURNO_SHOW] == (
        CoverageDataset.ACCESS_CONTROL,
        CoverageDataset.TICKET_SALES,
        CoverageDataset.OPTIN,
    )


def test_coverage_matrix_loader_accepts_new_contract_format(tmp_path: Path) -> None:
    """Coverage-matrix loader should parse dedicated coverage contract files."""

    path = tmp_path / "coverage_contract.yml"
    path.write_text(
        dedent(
            """
            version: 1
            status_domain: [ok, gap, partial]
            default_required_datasets: [access_control]
            session_types:
              NOTURNO_SHOW:
                datasets:
                  - dataset: access_control
                    required: true
                    severity: error
                    status_on_missing: gap
                  - dataset: ticket_sales
                    required: true
                    severity: error
                    status_on_missing: gap
              DIURNO_GRATUITO:
                datasets:
                  - dataset: access_control
                    required: true
                    severity: error
                    status_on_missing: gap
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    requirements = load_coverage_requirements_config(path)
    show = required_datasets_for_session_type(
        load_coverage_contract(path),
        EventSessionType.NOTURNO_SHOW,
    )

    assert requirements.default_required_datasets == (CoverageDataset.ACCESS_CONTROL,)
    assert requirements.required_datasets_by_session_type[EventSessionType.NOTURNO_SHOW] == (
        CoverageDataset.ACCESS_CONTROL,
        CoverageDataset.TICKET_SALES,
    )
    assert show == (CoverageDataset.ACCESS_CONTROL, CoverageDataset.TICKET_SALES)
