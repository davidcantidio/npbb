"""Unit tests for CONT Sprint 4 observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from core.contracts.s4_observability import (  # noqa: E402
    S4ContractObservabilityError,
    S4ContractObservabilityInput,
    build_s4_contract_actionable_error,
    build_s4_contract_observability_event,
)


def test_build_s4_contract_observability_event_success() -> None:
    payload = S4ContractObservabilityInput(
        event_name="contract_validation_s4_main_flow_completed",
        correlation_id="cont-s4-correlation-001",
        event_message="Fluxo principal CONT S4 concluido",
        severity="info",
        contract_id="CONT_STG_OPTIN_V4",
        dataset_name="stg_optin_events",
        source_kind="CSV",
        schema_version="V4",
        strict_validation=True,
        lineage_required=True,
        compatibility_mode="STRICT_BACKWARD",
        compatibility_result="BACKWARD_COMPATIBLE",
        breaking_change_detected=False,
        regression_failures=0,
        max_regression_failures=0,
        regression_gate_required=True,
        regression_gate_passed=True,
        stage="compatibility_validation",
        context={"regression_suite_version": "s4"},
    )
    event = build_s4_contract_observability_event(payload)

    assert event.observability_event_id.startswith("conts4coreevt-")
    assert event.correlation_id == "cont-s4-correlation-001"
    assert event.source_kind == "csv"
    assert event.schema_version == "v4"
    assert event.compatibility_mode == "strict_backward"
    assert event.compatibility_result == "backward_compatible"
    assert event.regression_failures == 0


def test_build_s4_contract_observability_event_rejects_invalid_regression_failures() -> None:
    payload = S4ContractObservabilityInput(
        event_name="contract_validation_s4_main_flow_completed",
        correlation_id="cont-s4-correlation-001",
        event_message="Fluxo principal CONT S4 concluido",
        severity="info",
        regression_failures=-1,
    )

    with pytest.raises(S4ContractObservabilityError) as exc:
        build_s4_contract_observability_event(payload)

    assert exc.value.code == "INVALID_CONT_S4_OBSERVABILITY_REGRESSION_FAILURES"


def test_build_s4_contract_actionable_error_includes_context() -> None:
    detail = build_s4_contract_actionable_error(
        code="CONT_S4_REGRESSION_GATE_FAILED",
        message="Regression gate bloqueou liberacao",
        action="Revisar falhas de regressao e limite permitido.",
        correlation_id="cont-s4-correlation-001",
        observability_event_id="conts4coreevt-abc123",
        stage="compatibility_validation",
        context={"contract_id": "CONT_STG_OPTIN_V4"},
    )

    assert detail["code"] == "CONT_S4_REGRESSION_GATE_FAILED"
    assert detail["observability_event_id"] == "conts4coreevt-abc123"
    assert detail["stage"] == "compatibility_validation"
    assert detail["context"]["contract_id"] == "CONT_STG_OPTIN_V4"
