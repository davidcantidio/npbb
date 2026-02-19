"""Unit tests for CONT Sprint 4 backend telemetry helpers."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))
BACKEND_ROOT = NPBB_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

telemetry = importlib.import_module(
    "app.services.contrato-can-nico-valida-o-estrita-linhagem-obrigat-ria_telemetry"
)


def test_build_s4_contract_telemetry_event_success() -> None:
    payload = telemetry.S4ContractTelemetryInput(
        event_name="contract_validation_s4_versioning_profile_ready",
        correlation_id="cont-s4-correlation-001",
        event_message="Perfil de versionamento CONT S4 pronto",
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
        stage="service",
        context={"owner_team": "etl"},
    )
    event = telemetry.build_s4_contract_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("conts4evt-")
    assert event.correlation_id == "cont-s4-correlation-001"
    assert event.source_kind == "csv"
    assert event.schema_version == "v4"
    assert event.compatibility_mode == "strict_backward"
    assert event.compatibility_result == "backward_compatible"
    assert event.regression_failures == 0


def test_build_s4_contract_telemetry_event_rejects_invalid_regression_failures() -> None:
    payload = telemetry.S4ContractTelemetryInput(
        event_name="contract_validation_s4_versioning_profile_ready",
        correlation_id="cont-s4-correlation-001",
        event_message="Perfil de versionamento CONT S4 pronto",
        severity="info",
        regression_failures=-1,
    )

    with pytest.raises(telemetry.S4ContractTelemetryContractError) as exc:
        telemetry.build_s4_contract_telemetry_event(payload)

    assert exc.value.code == "INVALID_CONT_S4_TELEMETRY_REGRESSION_FAILURES"


def test_build_s4_contract_error_detail_includes_stage_and_context() -> None:
    detail = telemetry.build_s4_contract_error_detail(
        code="CONT_S4_BREAKING_CHANGE_BLOCKED",
        message="Breaking change detectada com bloqueio",
        action="Revisar politica de compatibilidade e ajustes de schema.",
        correlation_id="cont-s4-correlation-001",
        telemetry_event_id="conts4evt-abc123",
        stage="compatibility_validation",
        context={"contract_id": "CONT_STG_OPTIN_V4"},
    )

    assert detail["code"] == "CONT_S4_BREAKING_CHANGE_BLOCKED"
    assert detail["telemetry_event_id"] == "conts4evt-abc123"
    assert detail["stage"] == "compatibility_validation"
    assert detail["context"]["contract_id"] == "CONT_STG_OPTIN_V4"
