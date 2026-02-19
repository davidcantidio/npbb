"""Unit tests for CONT Sprint 1 scaffold and service contracts."""

from __future__ import annotations

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
    S1ContractValidationServiceError,
    build_s1_contract_validation_error_detail,
    execute_s1_contract_validation_service,
)
from core.contracts.s1_core import (  # noqa: E402
    S1CanonicalContractCoreError,
    S1CanonicalContractCoreInput,
    execute_s1_contract_validation_main_flow,
)
from core.contracts.s1_scaffold import (  # noqa: E402
    S1CanonicalContractScaffoldRequest,
    S1ContractScaffoldError,
    build_s1_contract_scaffold,
)


def test_cont_s1_scaffold_success_returns_ready_contract() -> None:
    request = S1CanonicalContractScaffoldRequest(
        contract_id="cont stg optin v1",
        dataset_name="stg_optin_events",
        source_kind="csv",
        schema_version="v1",
        strict_validation=True,
        lineage_required=True,
        owner_team="etl",
        correlation_id="cont-s1-test-001",
    )

    output = build_s1_contract_scaffold(request)

    assert output.contrato_versao == "cont.s1.v1"
    assert output.correlation_id == "cont-s1-test-001"
    assert output.status == "ready"
    assert output.contract_id == "CONT_STG_OPTIN_V1"
    assert output.canonical_contract["lineage_required"] is True
    assert "lineage_ref_id" in output.canonical_contract["required_fields"]
    assert output.pontos_integracao["cont_s1_validate_endpoint"] == "/internal/contracts/s1/validate"


def test_cont_s1_scaffold_rejects_invalid_schema_version() -> None:
    request = S1CanonicalContractScaffoldRequest(
        contract_id="CONT_STG_OPTIN_V1",
        dataset_name="stg_optin_events",
        source_kind="csv",
        schema_version="1.0",
    )

    with pytest.raises(S1ContractScaffoldError) as exc:
        build_s1_contract_scaffold(request)

    error = exc.value
    assert error.code == "INVALID_SCHEMA_VERSION"
    assert "formato vN" in error.action


def test_cont_s1_service_success_returns_contract_and_observability() -> None:
    request = S1CanonicalContractScaffoldRequest(
        contract_id="CONT_FCT_TICKET_SALES_V1",
        dataset_name="fct_ticket_sales",
        source_kind="xlsx",
        schema_version="v1",
        strict_validation=True,
        lineage_required=True,
        owner_team="analytics",
        correlation_id="cont-s1-service-001",
    )

    output = execute_s1_contract_validation_service(request).to_dict()

    assert output["contrato_versao"] == "cont.s1.service.v1"
    assert output["correlation_id"] == "cont-s1-service-001"
    assert output["status"] == "completed"
    assert output["contract_id"] == "CONT_FCT_TICKET_SALES_V1"
    assert output["canonical_contract"]["validation_mode"] == "strict"
    assert output["execucao"]["status"] == "succeeded"
    assert output["observabilidade"]["flow_started_event_id"].startswith("conts1evt-")
    assert output["observabilidade"]["contract_ready_event_id"].startswith("conts1evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("conts1evt-")
    assert output["observabilidade"]["main_flow_started_event_id"].startswith("conts1coreevt-")
    assert output["observabilidade"]["main_flow_completed_event_id"].startswith("conts1coreevt-")


def test_cont_s1_service_raises_actionable_error_for_invalid_source_kind() -> None:
    request = S1CanonicalContractScaffoldRequest(
        contract_id="CONT_STG_OPTIN_V1",
        dataset_name="stg_optin_events",
        source_kind="parquet",
        correlation_id="cont-s1-invalid-kind",
    )

    with pytest.raises(S1ContractValidationServiceError) as exc:
        execute_s1_contract_validation_service(request)

    error = exc.value
    assert error.code == "INVALID_SOURCE_KIND"
    assert "source_kind suportado" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("conts1evt-")


def test_cont_s1_core_success_runs_main_flow() -> None:
    flow_input = S1CanonicalContractCoreInput(
        contract_id="CONT_STG_OPTIN_V1",
        dataset_name="stg_optin_events",
        source_kind="csv",
        schema_version="v1",
        strict_validation=True,
        lineage_required=True,
        owner_team="etl",
        correlation_id="cont-s1-core-001",
    )

    output = execute_s1_contract_validation_main_flow(flow_input).to_dict()

    assert output["contrato_versao"] == "cont.s1.core.v1"
    assert output["correlation_id"] == "cont-s1-core-001"
    assert output["status"] == "completed"
    assert output["contract_id"] == "CONT_STG_OPTIN_V1"
    assert output["execucao"]["status"] == "succeeded"
    assert output["observabilidade"]["flow_started_event_id"].startswith("conts1coreevt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("conts1coreevt-")


def test_cont_s1_core_raises_actionable_error_for_failed_validation() -> None:
    flow_input = S1CanonicalContractCoreInput(
        contract_id="CONT_STG_OPTIN_V1",
        dataset_name="stg_optin_events",
        source_kind="csv",
        schema_version="v1",
        strict_validation=True,
        lineage_required=True,
        owner_team="etl",
        correlation_id="cont-s1-core-failed",
    )

    def fail_validator(context: dict[str, object]) -> dict[str, object]:
        return {"status": "failed", "decision_reason": "schema_violation", "ctx": context}

    with pytest.raises(S1CanonicalContractCoreError) as exc:
        execute_s1_contract_validation_main_flow(flow_input, execute_validation=fail_validator)

    error = exc.value
    assert error.code == "CONT_S1_VALIDATION_FAILED"
    assert error.stage == "validation"
    assert (error.event_id or "").startswith("conts1coreevt-")


def test_cont_s1_error_detail_contract() -> None:
    detail = build_s1_contract_validation_error_detail(
        code="INVALID_SOURCE_KIND",
        message="source_kind invalido: parquet",
        action="Use source_kind suportado.",
        correlation_id="cont-s1-error-001",
        event_id="conts1evt-abc123",
        stage="scaffold",
        context={"source_kind": "parquet"},
    )

    assert detail["code"] == "INVALID_SOURCE_KIND"
    assert detail["correlation_id"] == "cont-s1-error-001"
    assert detail["event_id"] == "conts1evt-abc123"
    assert detail["stage"] == "scaffold"
    assert detail["context"]["source_kind"] == "parquet"
