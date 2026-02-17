"""Unit tests for CONT Sprint 3 observability contracts."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from core.contracts.s3_observability import (  # noqa: E402
    S3ContractObservabilityError,
    S3ContractObservabilityInput,
    build_s3_contract_actionable_error,
    build_s3_contract_observability_event,
)


def test_build_s3_contract_observability_event_success() -> None:
    payload = S3ContractObservabilityInput(
        event_name="contract_validation_s3_main_flow_completed",
        correlation_id="cont-s3-correlation-001",
        event_message="Fluxo principal CONT S3 concluido",
        severity="info",
        contract_id="CONT_STG_OPTIN_V3",
        dataset_name="stg_optin_events",
        source_kind="CSV",
        schema_version="V3",
        strict_validation=True,
        lineage_required=True,
        field_lineage_checks_executed=9,
        metric_lineage_checks_executed=3,
        stage="main_flow",
        context={"field_lineage_rules_count": 9},
    )
    event = build_s3_contract_observability_event(payload)

    assert event.observability_event_id.startswith("conts3coreevt-")
    assert event.correlation_id == "cont-s3-correlation-001"
    assert event.source_kind == "csv"
    assert event.schema_version == "v3"
    assert event.field_lineage_checks_executed == 9
    assert event.metric_lineage_checks_executed == 3


def test_build_s3_contract_observability_event_rejects_invalid_metric_lineage_checks() -> None:
    payload = S3ContractObservabilityInput(
        event_name="contract_validation_s3_main_flow_completed",
        correlation_id="cont-s3-correlation-001",
        event_message="Fluxo principal CONT S3 concluido",
        severity="info",
        metric_lineage_checks_executed=-1,
    )

    with pytest.raises(S3ContractObservabilityError) as exc:
        build_s3_contract_observability_event(payload)

    assert exc.value.code == "INVALID_CONT_S3_OBSERVABILITY_METRIC_LINEAGE_CHECKS"


def test_build_s3_contract_actionable_error_includes_context() -> None:
    detail = build_s3_contract_actionable_error(
        code="CONT_S3_LINEAGE_ENFORCEMENT_FAILED",
        message="Enforcement de linhagem falhou",
        action="Revisar logs de enforcement.",
        correlation_id="cont-s3-correlation-001",
        observability_event_id="conts3coreevt-abc123",
        stage="lineage_enforcement",
        context={"contract_id": "CONT_STG_OPTIN_V3"},
    )

    assert detail["code"] == "CONT_S3_LINEAGE_ENFORCEMENT_FAILED"
    assert detail["observability_event_id"] == "conts3coreevt-abc123"
    assert detail["stage"] == "lineage_enforcement"
    assert detail["context"]["contract_id"] == "CONT_STG_OPTIN_V3"
