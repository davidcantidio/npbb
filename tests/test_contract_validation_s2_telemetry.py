"""Unit tests for CONT Sprint 2 backend telemetry helpers."""

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


def test_build_s2_contract_telemetry_event_success() -> None:
    payload = telemetry.S2ContractTelemetryInput(
        event_name="contract_validation_s2_profile_ready",
        correlation_id="cont-s2-correlation-001",
        event_message="Perfil de validacao CONT S2 pronto",
        severity="info",
        contract_id="CONT_STG_OPTIN_V2",
        dataset_name="stg_optin_events",
        source_kind="CSV",
        schema_version="V2",
        strict_validation=True,
        lineage_required=True,
        schema_checks_executed=8,
        domain_checks_executed=4,
        stage="service",
        context={"owner_team": "etl"},
    )
    event = telemetry.build_s2_contract_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("conts2evt-")
    assert event.correlation_id == "cont-s2-correlation-001"
    assert event.source_kind == "csv"
    assert event.schema_version == "v2"
    assert event.schema_checks_executed == 8
    assert event.domain_checks_executed == 4


def test_build_s2_contract_telemetry_event_rejects_invalid_schema_checks() -> None:
    payload = telemetry.S2ContractTelemetryInput(
        event_name="contract_validation_s2_profile_ready",
        correlation_id="cont-s2-correlation-001",
        event_message="Perfil de validacao CONT S2 pronto",
        severity="info",
        schema_checks_executed=-1,
    )

    with pytest.raises(telemetry.S2ContractTelemetryContractError) as exc:
        telemetry.build_s2_contract_telemetry_event(payload)

    assert exc.value.code == "INVALID_CONT_S2_TELEMETRY_SCHEMA_CHECKS"


def test_build_s2_contract_error_detail_includes_stage_and_context() -> None:
    detail = telemetry.build_s2_contract_error_detail(
        code="CONT_S2_VALIDATION_FAILED",
        message="Validacao de contrato falhou",
        action="Revisar logs de validacao.",
        correlation_id="cont-s2-correlation-001",
        telemetry_event_id="conts2evt-abc123",
        stage="validation",
        context={"contract_id": "CONT_STG_OPTIN_V2"},
    )

    assert detail["code"] == "CONT_S2_VALIDATION_FAILED"
    assert detail["telemetry_event_id"] == "conts2evt-abc123"
    assert detail["stage"] == "validation"
    assert detail["context"]["contract_id"] == "CONT_STG_OPTIN_V2"
