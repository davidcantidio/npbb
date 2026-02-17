"""Unit tests for CONT Sprint 2 scaffold and service contracts."""

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
    S2ContractValidationServiceError,
    execute_s2_contract_validation_service,
)
from core.contracts.s2_scaffold import (  # noqa: E402
    S2CanonicalContractScaffoldRequest,
    S2ContractScaffoldError,
    build_s2_contract_scaffold,
)


def test_cont_s2_scaffold_success_returns_ready_contract() -> None:
    request = S2CanonicalContractScaffoldRequest(
        contract_id="cont stg optin v2",
        dataset_name="stg_optin_events",
        source_kind="csv",
        schema_version="v2",
        strict_validation=True,
        lineage_required=True,
        owner_team="etl",
        schema_required_fields=("record_id", "event_ts", "source_id", "payload_checksum"),
        domain_constraints={
            "source_id": ("app", "crm"),
            "record_id": ("not_null",),
        },
        correlation_id="cont-s2-test-001",
    )

    output = build_s2_contract_scaffold(request)

    assert output.contrato_versao == "cont.s2.v1"
    assert output.correlation_id == "cont-s2-test-001"
    assert output.status == "ready"
    assert output.contract_id == "CONT_STG_OPTIN_V2"
    assert output.validation_profile["validation_scope"] == "schema_and_domain"
    assert "lineage_ref_id" in output.validation_profile["schema_required_fields"]
    assert output.validation_profile["domain_rules_count"] >= 2
    assert output.pontos_integracao["cont_s2_prepare_endpoint"] == "/internal/contracts/s2/prepare"


def test_cont_s2_scaffold_rejects_domain_field_not_in_schema() -> None:
    request = S2CanonicalContractScaffoldRequest(
        contract_id="CONT_STG_OPTIN_V2",
        dataset_name="stg_optin_events",
        source_kind="csv",
        schema_required_fields=("record_id", "event_ts"),
        domain_constraints={"source_id": ("app",)},
    )

    with pytest.raises(S2ContractScaffoldError) as exc:
        build_s2_contract_scaffold(request)

    error = exc.value
    assert error.code == "DOMAIN_FIELD_NOT_IN_SCHEMA"
    assert "schema" in error.action.lower()


def test_cont_s2_service_success_returns_profile_and_observability() -> None:
    request = S2CanonicalContractScaffoldRequest(
        contract_id="CONT_FCT_TICKET_SALES_V2",
        dataset_name="fct_ticket_sales",
        source_kind="xlsx",
        schema_version="v2",
        strict_validation=True,
        lineage_required=True,
        owner_team="analytics",
        schema_required_fields=("record_id", "event_ts", "source_id", "payload_checksum"),
        domain_constraints={
            "source_id": ("pdv", "online"),
            "record_id": ("not_null",),
        },
        correlation_id="cont-s2-service-001",
    )

    output = execute_s2_contract_validation_service(request).to_dict()

    assert output["contrato_versao"] == "cont.s2.service.v1"
    assert output["correlation_id"] == "cont-s2-service-001"
    assert output["status"] == "ready"
    assert output["contract_id"] == "CONT_FCT_TICKET_SALES_V2"
    assert output["validation_profile"]["validation_scope"] == "schema_and_domain"
    assert output["observabilidade"]["flow_started_event_id"].startswith("conts2evt-")
    assert output["observabilidade"]["validation_profile_ready_event_id"].startswith("conts2evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("conts2evt-")


def test_cont_s2_service_raises_actionable_error_for_invalid_source_kind() -> None:
    request = S2CanonicalContractScaffoldRequest(
        contract_id="CONT_STG_OPTIN_V2",
        dataset_name="stg_optin_events",
        source_kind="parquet",
        correlation_id="cont-s2-invalid-kind",
    )

    with pytest.raises(S2ContractValidationServiceError) as exc:
        execute_s2_contract_validation_service(request)

    error = exc.value
    assert error.code == "INVALID_SOURCE_KIND"
    assert "source_kind suportado" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("conts2evt-")
