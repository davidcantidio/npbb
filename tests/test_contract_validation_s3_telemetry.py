"""Unit tests for CONT Sprint 3 backend telemetry helpers."""

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


def test_build_s3_contract_telemetry_event_success() -> None:
    payload = telemetry.S3ContractTelemetryInput(
        event_name="contract_validation_s3_lineage_profile_ready",
        correlation_id="cont-s3-correlation-001",
        event_message="Perfil de linhagem CONT S3 pronto",
        severity="info",
        contract_id="CONT_STG_OPTIN_V3",
        dataset_name="stg_optin_events",
        source_kind="CSV",
        schema_version="V3",
        strict_validation=True,
        lineage_required=True,
        field_lineage_checks_executed=9,
        metric_lineage_checks_executed=3,
        stage="service",
        context={"owner_team": "etl"},
    )
    event = telemetry.build_s3_contract_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("conts3evt-")
    assert event.correlation_id == "cont-s3-correlation-001"
    assert event.source_kind == "csv"
    assert event.schema_version == "v3"
    assert event.field_lineage_checks_executed == 9
    assert event.metric_lineage_checks_executed == 3


def test_build_s3_contract_telemetry_event_rejects_invalid_field_lineage_checks() -> None:
    payload = telemetry.S3ContractTelemetryInput(
        event_name="contract_validation_s3_lineage_profile_ready",
        correlation_id="cont-s3-correlation-001",
        event_message="Perfil de linhagem CONT S3 pronto",
        severity="info",
        field_lineage_checks_executed=-1,
    )

    with pytest.raises(telemetry.S3ContractTelemetryContractError) as exc:
        telemetry.build_s3_contract_telemetry_event(payload)

    assert exc.value.code == "INVALID_CONT_S3_TELEMETRY_FIELD_LINEAGE_CHECKS"


def test_build_s3_contract_error_detail_includes_stage_and_context() -> None:
    detail = telemetry.build_s3_contract_error_detail(
        code="CONT_S3_LINEAGE_ENFORCEMENT_FAILED",
        message="Enforcement de linhagem falhou",
        action="Revisar logs de enforcement.",
        correlation_id="cont-s3-correlation-001",
        telemetry_event_id="conts3evt-abc123",
        stage="lineage_enforcement",
        context={"contract_id": "CONT_STG_OPTIN_V3"},
    )

    assert detail["code"] == "CONT_S3_LINEAGE_ENFORCEMENT_FAILED"
    assert detail["telemetry_event_id"] == "conts3evt-abc123"
    assert detail["stage"] == "lineage_enforcement"
    assert detail["context"]["contract_id"] == "CONT_STG_OPTIN_V3"
