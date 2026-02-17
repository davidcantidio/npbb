"""Unit tests for CONT Sprint 1 backend telemetry helpers."""

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


def test_build_s1_contract_telemetry_event_success() -> None:
    payload = telemetry.S1ContractTelemetryInput(
        event_name="contract_validation_s1_contract_ready",
        correlation_id="cont-s1-correlation-001",
        event_message="Contrato canonico CONT S1 pronto",
        severity="info",
        contract_id="CONT_STG_OPTIN_V1",
        dataset_name="stg_optin_events",
        source_kind="CSV",
        schema_version="V1",
        strict_validation=True,
        lineage_required=True,
        stage="service",
        context={"owner_team": "etl"},
    )
    event = telemetry.build_s1_contract_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("conts1evt-")
    assert event.correlation_id == "cont-s1-correlation-001"
    assert event.source_kind == "csv"
    assert event.schema_version == "v1"
    assert event.strict_validation is True
    assert event.lineage_required is True


def test_build_s1_contract_telemetry_event_rejects_invalid_severity() -> None:
    payload = telemetry.S1ContractTelemetryInput(
        event_name="contract_validation_s1_contract_ready",
        correlation_id="cont-s1-correlation-001",
        event_message="Contrato canonico CONT S1 pronto",
        severity="debug",
    )

    with pytest.raises(telemetry.S1ContractTelemetryContractError) as exc:
        telemetry.build_s1_contract_telemetry_event(payload)

    assert exc.value.code == "INVALID_CONT_S1_TELEMETRY_SEVERITY"


def test_build_s1_contract_error_detail_includes_stage_and_context() -> None:
    detail = telemetry.build_s1_contract_error_detail(
        code="CONT_S1_VALIDATION_FAILED",
        message="Validacao de contrato falhou",
        action="Revisar logs de validacao.",
        correlation_id="cont-s1-correlation-001",
        telemetry_event_id="conts1evt-abc123",
        stage="validation",
        context={"contract_id": "CONT_STG_OPTIN_V1"},
    )

    assert detail["code"] == "CONT_S1_VALIDATION_FAILED"
    assert detail["telemetry_event_id"] == "conts1evt-abc123"
    assert detail["stage"] == "validation"
    assert detail["context"]["contract_id"] == "CONT_STG_OPTIN_V1"
