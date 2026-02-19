"""Unit tests for CONF Sprint 4 scaffold and service base contracts."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))
BACKEND_ROOT = NPBB_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.confidence_policy_service import (  # noqa: E402
    S4ConfidencePolicyServiceError,
    execute_s4_confidence_policy_service,
)
from core.confidence.s4_scaffold import (  # noqa: E402
    S4ConfidenceScaffoldError,
    S4ConfidenceScaffoldRequest,
    build_s4_confidence_scaffold,
)


def _build_valid_s4_request(*, correlation_id: str) -> S4ConfidenceScaffoldRequest:
    return S4ConfidenceScaffoldRequest(
        policy_id="CONF_REPORT_POLICY_V4",
        dataset_name="event_report_lines",
        entity_kind="evento",
        schema_version="v4",
        owner_team="etl",
        field_weights={
            "nome_evento": 0.30,
            "data_evento": 0.30,
            "local_evento": 0.20,
            "diretoria": 0.20,
        },
        default_weight=0.10,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.60,
        gap_threshold=0.40,
        missing_field_penalty=0.10,
        decision_mode="feedback_adjusted_thresholds",
        gap_escalation_required=True,
        max_manual_review_queue=500,
        critical_fields=("nome_evento", "data_evento", "local_evento"),
        min_critical_fields_present=2,
        critical_field_penalty=0.25,
        critical_violation_route="manual_review",
        critical_override_required=True,
        feedback_window_days=30,
        min_feedback_samples=200,
        auto_threshold_tuning_enabled=True,
        max_threshold_delta=0.10,
        quality_drop_tolerance=0.05,
        calibration_freeze_on_anomaly=True,
        correlation_id=correlation_id,
    )


def test_conf_s4_scaffold_success_returns_ready_contract() -> None:
    request = _build_valid_s4_request(correlation_id="conf-s4-test-001")

    output = build_s4_confidence_scaffold(request)

    assert output.contrato_versao == "conf.s4.v1"
    assert output.correlation_id == "conf-s4-test-001"
    assert output.status == "ready"
    assert output.policy_id == "CONF_REPORT_POLICY_V4"
    assert output.decision_policy["decision_mode"] == "feedback_adjusted_thresholds"
    assert output.decision_policy["threshold_calibration_policy"]["feedback_window_days"] == 30
    assert output.decision_policy["threshold_calibration_policy"]["min_feedback_samples"] == 200
    assert output.pontos_integracao["conf_s4_prepare_endpoint"] == "/internal/confidence/s4/prepare"


def test_conf_s4_scaffold_rejects_invalid_decision_mode() -> None:
    request = _build_valid_s4_request(correlation_id="conf-s4-invalid-mode")
    request = replace(request, decision_mode="legacy_mode")

    with pytest.raises(S4ConfidenceScaffoldError) as exc:
        build_s4_confidence_scaffold(request)

    error = exc.value
    assert error.code == "INVALID_DECISION_MODE"
    assert "decision_mode suportado" in error.action


def test_conf_s4_service_success_returns_policy_and_observability() -> None:
    request = _build_valid_s4_request(correlation_id="conf-s4-service-001")

    output = execute_s4_confidence_policy_service(request).to_dict()

    assert output["contrato_versao"] == "conf.s4.service.v1"
    assert output["correlation_id"] == "conf-s4-service-001"
    assert output["status"] == "ready"
    assert output["policy_id"] == "CONF_REPORT_POLICY_V4"
    assert output["decision_policy"]["decision_mode"] == "feedback_adjusted_thresholds"
    assert output["execucao"]["status"] == "ready"
    assert output["observabilidade"]["flow_started_event_id"].startswith("confs4evt-")
    assert output["observabilidade"]["policy_profile_ready_event_id"].startswith("confs4evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("confs4evt-")
    assert output["scaffold"]["contrato_versao"] == "conf.s4.v1"


def test_conf_s4_service_raises_actionable_error_for_manual_tuning_conflict() -> None:
    request = _build_valid_s4_request(correlation_id="conf-s4-invalid-manual-tuning")
    request = replace(request, auto_threshold_tuning_enabled=False)

    with pytest.raises(S4ConfidencePolicyServiceError) as exc:
        execute_s4_confidence_policy_service(request)

    error = exc.value
    assert error.code == "MANUAL_TUNING_REQUIRES_ZERO_MAX_THRESHOLD_DELTA"
    assert "max_threshold_delta=0.0" in error.action or "max_threshold_delta" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("confs4evt-")
