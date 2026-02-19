"""Unit tests for CONF Sprint 1 scaffold, core, and service contracts."""

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
    S1ConfidencePolicyServiceError,
    execute_s1_confidence_policy_service,
)
from core.confidence.s1_core import (  # noqa: E402
    S1ConfidenceCoreError,
    S1ConfidenceCoreInput,
    execute_s1_confidence_policy_main_flow,
)
from core.confidence.s1_scaffold import (  # noqa: E402
    S1ConfidenceScaffoldError,
    S1ConfidenceScaffoldRequest,
    build_s1_confidence_scaffold,
)


def _build_valid_request(*, correlation_id: str) -> S1ConfidenceScaffoldRequest:
    return S1ConfidenceScaffoldRequest(
        policy_id="conf lead quality v1",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v1",
        owner_team="etl",
        field_weights={
            "nome": 0.2,
            "email": 0.3,
            "telefone": 0.2,
            "documento": 0.3,
        },
        default_weight=0.1,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.6,
        missing_field_penalty=0.1,
        decision_mode="weighted_threshold",
        correlation_id=correlation_id,
    )


def test_conf_s1_scaffold_success_returns_ready_contract() -> None:
    request = _build_valid_request(correlation_id="conf-s1-test-001")

    output = build_s1_confidence_scaffold(request)

    assert output.contrato_versao == "conf.s1.v1"
    assert output.correlation_id == "conf-s1-test-001"
    assert output.status == "ready"
    assert output.policy_id == "CONF_LEAD_QUALITY_V1"
    assert output.confidence_policy["scoring_scope"] == "field_level"
    assert output.confidence_policy["field_weights_count"] == 4
    assert output.confidence_policy["thresholds"]["auto_approve"] == 0.85
    assert output.pontos_integracao["conf_s1_prepare_endpoint"] == "/internal/confidence/s1/prepare"


def test_conf_s1_scaffold_rejects_inverted_thresholds() -> None:
    request = _build_valid_request(correlation_id="conf-s1-invalid-thresholds")
    request = replace(request, manual_review_threshold=0.9, auto_approve_threshold=0.8)

    with pytest.raises(S1ConfidenceScaffoldError) as exc:
        build_s1_confidence_scaffold(request)

    error = exc.value
    assert error.code == "INVALID_CONFIDENCE_THRESHOLDS"
    assert "manual_review_threshold" in error.action


def test_conf_s1_service_success_returns_policy_and_observability() -> None:
    request = _build_valid_request(correlation_id="conf-s1-service-001")

    output = execute_s1_confidence_policy_service(request).to_dict()

    assert output["contrato_versao"] == "conf.s1.service.v1"
    assert output["correlation_id"] == "conf-s1-service-001"
    assert output["status"] == "completed"
    assert output["policy_id"] == "CONF_LEAD_QUALITY_V1"
    assert output["confidence_policy"]["decision_mode"] == "weighted_threshold"
    assert output["execucao"]["status"] == "succeeded"
    assert output["observabilidade"]["flow_started_event_id"].startswith("confs1evt-")
    assert output["observabilidade"]["policy_profile_ready_event_id"].startswith("confs1evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("confs1evt-")
    assert output["observabilidade"]["main_flow_started_event_id"].startswith("confs1coreevt-")
    assert output["observabilidade"]["main_flow_completed_event_id"].startswith("confs1coreevt-")
    assert output["scaffold"]["contrato_versao"] == "conf.s1.v1"


def test_conf_s1_service_raises_actionable_error_for_invalid_entity_kind() -> None:
    request = _build_valid_request(correlation_id="conf-s1-invalid-entity")
    request = replace(request, entity_kind="campanha")

    with pytest.raises(S1ConfidencePolicyServiceError) as exc:
        execute_s1_confidence_policy_service(request)

    error = exc.value
    assert error.code == "INVALID_ENTITY_KIND"
    assert "entity_kind suportado" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("confs1evt-")


def test_conf_s1_core_success_runs_main_flow() -> None:
    flow_input = S1ConfidenceCoreInput(
        policy_id="CONF_LEAD_QUALITY_V1",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v1",
        owner_team="etl",
        field_weights={
            "nome": 0.2,
            "email": 0.3,
            "telefone": 0.2,
            "documento": 0.3,
        },
        default_weight=0.1,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.6,
        missing_field_penalty=0.1,
        decision_mode="weighted_threshold",
        correlation_id="conf-s1-core-001",
    )

    output = execute_s1_confidence_policy_main_flow(flow_input).to_dict()

    assert output["contrato_versao"] == "conf.s1.core.v1"
    assert output["correlation_id"] == "conf-s1-core-001"
    assert output["status"] == "completed"
    assert output["policy_id"] == "CONF_LEAD_QUALITY_V1"
    assert output["execucao"]["status"] == "succeeded"
    assert output["execucao"]["decision"] in {"auto_approve", "manual_review", "reject"}
    assert output["observabilidade"]["flow_started_event_id"].startswith("confs1coreevt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("confs1coreevt-")


def test_conf_s1_core_raises_actionable_error_for_failed_scoring() -> None:
    flow_input = S1ConfidenceCoreInput(
        policy_id="CONF_LEAD_QUALITY_V1",
        dataset_name="leads_capture",
        entity_kind="lead",
        schema_version="v1",
        owner_team="etl",
        field_weights={
            "nome": 0.2,
            "email": 0.3,
            "telefone": 0.2,
            "documento": 0.3,
        },
        default_weight=0.1,
        auto_approve_threshold=0.85,
        manual_review_threshold=0.6,
        missing_field_penalty=0.1,
        decision_mode="weighted_threshold",
        correlation_id="conf-s1-core-failed",
    )

    def fail_scorer(_context: dict[str, object]) -> dict[str, object]:
        return {
            "status": "failed",
            "confidence_score": 0.42,
            "decision_reason": "missing_required_fields",
        }

    with pytest.raises(S1ConfidenceCoreError) as exc:
        execute_s1_confidence_policy_main_flow(flow_input, execute_scoring=fail_scorer)

    error = exc.value
    assert error.code == "CONF_S1_SCORING_FAILED"
    assert error.stage == "scoring"
    assert (error.event_id or "").startswith("confs1coreevt-")
