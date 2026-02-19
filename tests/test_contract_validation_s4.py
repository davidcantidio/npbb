"""Unit tests for CONT Sprint 4 scaffold and service base contracts."""

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

from app.services.contract_validation_service import (  # noqa: E402
    S4ContractValidationServiceError,
    execute_s4_contract_validation_service,
)
from core.contracts.s4_scaffold import (  # noqa: E402
    S4CanonicalContractScaffoldRequest,
    S4ContractScaffoldError,
    build_s4_contract_scaffold,
)


def _build_valid_s4_request(*, correlation_id: str) -> S4CanonicalContractScaffoldRequest:
    return S4CanonicalContractScaffoldRequest(
        contract_id="CONT_STG_OPTIN_V4",
        dataset_name="stg_optin_events",
        source_kind="csv",
        schema_version="v4",
        strict_validation=True,
        lineage_required=True,
        owner_team="etl",
        schema_required_fields=("record_id", "event_ts", "source_id", "payload_checksum"),
        lineage_field_requirements={
            "record_id": ("crm.orders.id",),
            "source_id": ("crm.sources.origin_system",),
        },
        metric_lineage_requirements={
            "optin_total": ("crm.optin.total",),
        },
        compatibility_mode="strict_backward",
        previous_contract_versions=("v3",),
        regression_gate_required=True,
        regression_suite_version="s4",
        max_regression_failures=0,
        breaking_change_policy="block",
        deprecation_window_days=0,
        correlation_id=correlation_id,
    )


def test_cont_s4_scaffold_success_returns_ready_contract() -> None:
    request = _build_valid_s4_request(correlation_id="cont-s4-test-001")

    output = build_s4_contract_scaffold(request)

    assert output.contrato_versao == "cont.s4.v1"
    assert output.correlation_id == "cont-s4-test-001"
    assert output.status == "ready"
    assert output.contract_id == "CONT_STG_OPTIN_V4"
    assert output.versioning_profile["compatibility_scope"] == "contract_version_and_regression_gate"
    assert output.versioning_profile["compatibility_mode"] == "strict_backward"
    assert output.versioning_profile["previous_contract_versions"] == ["v3"]
    assert output.pontos_integracao["cont_s4_prepare_endpoint"] == "/internal/contracts/s4/prepare"


def test_cont_s4_scaffold_rejects_invalid_compatibility_mode() -> None:
    request = _build_valid_s4_request(correlation_id="cont-s4-invalid-mode")
    request = replace(request, compatibility_mode="legacy_only")

    with pytest.raises(S4ContractScaffoldError) as exc:
        build_s4_contract_scaffold(request)

    error = exc.value
    assert error.code == "INVALID_COMPATIBILITY_MODE"
    assert "compatibility_mode suportado" in error.action


def test_cont_s4_service_success_returns_profile_and_observability() -> None:
    request = _build_valid_s4_request(correlation_id="cont-s4-service-001")

    output = execute_s4_contract_validation_service(request).to_dict()

    assert output["contrato_versao"] == "cont.s4.service.v1"
    assert output["correlation_id"] == "cont-s4-service-001"
    assert output["status"] == "ready"
    assert output["contract_id"] == "CONT_STG_OPTIN_V4"
    assert output["versioning_profile"]["compatibility_mode"] == "strict_backward"
    assert output["execucao"]["status"] == "ready"
    assert output["observabilidade"]["flow_started_event_id"].startswith("conts4evt-")
    assert output["observabilidade"]["versioning_profile_ready_event_id"].startswith("conts4evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("conts4evt-")
    assert output["scaffold"]["contrato_versao"] == "cont.s4.v1"


def test_cont_s4_service_raises_actionable_error_for_conflicting_policy() -> None:
    request = _build_valid_s4_request(correlation_id="cont-s4-invalid-policy")
    request = replace(request, breaking_change_policy="allow_with_waiver")

    with pytest.raises(S4ContractValidationServiceError) as exc:
        execute_s4_contract_validation_service(request)

    error = exc.value
    assert error.code == "STRICT_VALIDATION_CONFLICTING_BREAKING_CHANGE_POLICY"
    assert "breaking_change_policy=block" in error.action or "block" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("conts4evt-")
