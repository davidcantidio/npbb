"""Unit tests for CONT Sprint 2 observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from core.contracts.s2_observability import (  # noqa: E402
    S2ContractObservabilityError,
    S2ContractObservabilityInput,
    build_s2_contract_actionable_error,
    build_s2_contract_observability_event,
)


def test_build_s2_contract_observability_event_success() -> None:
    payload = S2ContractObservabilityInput(
        event_name="contract_validation_s2_main_flow_completed",
        correlation_id="cont-s2-correlation-001",
        event_message="Fluxo principal CONT S2 concluido",
        severity="info",
        contract_id="CONT_STG_OPTIN_V2",
        dataset_name="stg_optin_events",
        source_kind="CSV",
        schema_version="V2",
        strict_validation=True,
        lineage_required=True,
        schema_checks_executed=8,
        domain_checks_executed=4,
        stage="main_flow",
        context={"domain_rules_count": 4},
    )
    event = build_s2_contract_observability_event(payload)

    assert event.observability_event_id.startswith("conts2coreevt-")
    assert event.correlation_id == "cont-s2-correlation-001"
    assert event.source_kind == "csv"
    assert event.schema_version == "v2"
    assert event.schema_checks_executed == 8
    assert event.domain_checks_executed == 4


def test_build_s2_contract_observability_event_rejects_invalid_domain_checks() -> None:
    payload = S2ContractObservabilityInput(
        event_name="contract_validation_s2_main_flow_completed",
        correlation_id="cont-s2-correlation-001",
        event_message="Fluxo principal CONT S2 concluido",
        severity="info",
        domain_checks_executed=-1,
    )

    with pytest.raises(S2ContractObservabilityError) as exc:
        build_s2_contract_observability_event(payload)

    assert exc.value.code == "INVALID_CONT_S2_OBSERVABILITY_DOMAIN_CHECKS"


def test_build_s2_contract_actionable_error_includes_context() -> None:
    detail = build_s2_contract_actionable_error(
        code="CONT_S2_VALIDATION_FAILED",
        message="Validacao de contrato falhou",
        action="Revisar logs de validacao.",
        correlation_id="cont-s2-correlation-001",
        observability_event_id="conts2coreevt-abc123",
        stage="validation",
        context={"contract_id": "CONT_STG_OPTIN_V2"},
    )

    assert detail["code"] == "CONT_S2_VALIDATION_FAILED"
    assert detail["observability_event_id"] == "conts2coreevt-abc123"
    assert detail["stage"] == "validation"
    assert detail["context"]["contract_id"] == "CONT_STG_OPTIN_V2"
