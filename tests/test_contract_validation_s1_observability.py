"""Unit tests for CONT Sprint 1 observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from core.contracts.s1_observability import (  # noqa: E402
    S1ContractObservabilityError,
    S1ContractObservabilityInput,
    build_s1_contract_actionable_error,
    build_s1_contract_observability_event,
)


def test_build_s1_contract_observability_event_success() -> None:
    payload = S1ContractObservabilityInput(
        event_name="contract_validation_s1_main_flow_completed",
        correlation_id="cont-s1-correlation-001",
        event_message="Fluxo principal CONT S1 concluido",
        severity="info",
        contract_id="CONT_STG_OPTIN_V1",
        dataset_name="stg_optin_events",
        source_kind="CSV",
        schema_version="V1",
        strict_validation=True,
        lineage_required=True,
        stage="main_flow",
        context={"required_fields_count": 5},
    )
    event = build_s1_contract_observability_event(payload)

    assert event.observability_event_id.startswith("conts1coreevt-")
    assert event.correlation_id == "cont-s1-correlation-001"
    assert event.source_kind == "csv"
    assert event.schema_version == "v1"
    assert event.strict_validation is True
    assert event.lineage_required is True


def test_build_s1_contract_observability_event_rejects_invalid_severity() -> None:
    payload = S1ContractObservabilityInput(
        event_name="contract_validation_s1_main_flow_completed",
        correlation_id="cont-s1-correlation-001",
        event_message="Fluxo principal CONT S1 concluido",
        severity="debug",
    )

    with pytest.raises(S1ContractObservabilityError) as exc:
        build_s1_contract_observability_event(payload)

    assert exc.value.code == "INVALID_CONT_S1_OBSERVABILITY_SEVERITY"


def test_build_s1_contract_actionable_error_includes_context() -> None:
    detail = build_s1_contract_actionable_error(
        code="CONT_S1_VALIDATION_FAILED",
        message="Validacao de contrato falhou",
        action="Revisar logs de validacao.",
        correlation_id="cont-s1-correlation-001",
        observability_event_id="conts1coreevt-abc123",
        stage="validation",
        context={"contract_id": "CONT_STG_OPTIN_V1"},
    )

    assert detail["code"] == "CONT_S1_VALIDATION_FAILED"
    assert detail["observability_event_id"] == "conts1coreevt-abc123"
    assert detail["stage"] == "validation"
    assert detail["context"]["contract_id"] == "CONT_STG_OPTIN_V1"
