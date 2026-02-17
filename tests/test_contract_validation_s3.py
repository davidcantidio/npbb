"""Unit tests for CONT Sprint 3 scaffold and service contracts."""

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
    S3ContractValidationServiceError,
    execute_s3_contract_validation_service,
)
from core.contracts.s3_scaffold import (  # noqa: E402
    S3CanonicalContractScaffoldRequest,
    S3ContractScaffoldError,
    build_s3_contract_scaffold,
)


def test_cont_s3_scaffold_success_returns_ready_contract() -> None:
    request = S3CanonicalContractScaffoldRequest(
        contract_id="cont fct revenue v3",
        dataset_name="fct_revenue",
        source_kind="api",
        schema_version="v3",
        strict_validation=True,
        lineage_required=True,
        owner_team="analytics",
        schema_required_fields=("record_id", "event_ts", "source_id", "payload_checksum"),
        lineage_field_requirements={
            "record_id": ("crm.orders.id",),
            "source_id": ("crm.sources.origin_system",),
        },
        metric_lineage_requirements={
            "gross_revenue": ("crm.orders.total_amount", "erp.invoices.gross_total"),
        },
        correlation_id="cont-s3-test-001",
    )

    output = build_s3_contract_scaffold(request)

    assert output.contrato_versao == "cont.s3.v1"
    assert output.correlation_id == "cont-s3-test-001"
    assert output.status == "ready"
    assert output.contract_id == "CONT_FCT_REVENUE_V3"
    assert output.lineage_profile["enforcement_scope"] == "field_and_metric_lineage"
    assert output.lineage_profile["field_lineage_rules_count"] == 2
    assert output.lineage_profile["metric_lineage_rules_count"] == 1
    assert output.pontos_integracao["cont_s3_prepare_endpoint"] == "/internal/contracts/s3/prepare"


def test_cont_s3_scaffold_rejects_lineage_field_not_in_schema() -> None:
    request = S3CanonicalContractScaffoldRequest(
        contract_id="CONT_STG_OPTIN_V3",
        dataset_name="stg_optin_events",
        source_kind="csv",
        schema_required_fields=("record_id", "event_ts"),
        lineage_field_requirements={"source_id": ("crm.sources.origin_system",)},
        metric_lineage_requirements={"total_optin": ("crm.optin.count",)},
    )

    with pytest.raises(S3ContractScaffoldError) as exc:
        build_s3_contract_scaffold(request)

    error = exc.value
    assert error.code == "LINEAGE_FIELD_NOT_IN_SCHEMA"
    assert "schema" in error.action.lower()


def test_cont_s3_service_success_returns_profile_and_observability() -> None:
    request = S3CanonicalContractScaffoldRequest(
        contract_id="CONT_FCT_TICKET_SALES_V3",
        dataset_name="fct_ticket_sales",
        source_kind="xlsx",
        schema_version="v3",
        strict_validation=True,
        lineage_required=True,
        owner_team="analytics",
        schema_required_fields=("record_id", "event_ts", "source_id", "payload_checksum"),
        lineage_field_requirements={
            "record_id": ("erp.sales.id",),
            "source_id": ("erp.sales.channel",),
        },
        metric_lineage_requirements={
            "ticket_count": ("erp.sales.qty",),
            "gross_revenue": ("erp.sales.total_amount",),
        },
        correlation_id="cont-s3-service-001",
    )

    output = execute_s3_contract_validation_service(request).to_dict()

    assert output["contrato_versao"] == "cont.s3.service.v1"
    assert output["correlation_id"] == "cont-s3-service-001"
    assert output["status"] == "ready"
    assert output["contract_id"] == "CONT_FCT_TICKET_SALES_V3"
    assert output["lineage_profile"]["enforcement_scope"] == "field_and_metric_lineage"
    assert output["observabilidade"]["flow_started_event_id"].startswith("conts3evt-")
    assert output["observabilidade"]["lineage_profile_ready_event_id"].startswith("conts3evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("conts3evt-")


def test_cont_s3_service_raises_actionable_error_for_invalid_source_kind() -> None:
    request = S3CanonicalContractScaffoldRequest(
        contract_id="CONT_STG_OPTIN_V3",
        dataset_name="stg_optin_events",
        source_kind="parquet",
        correlation_id="cont-s3-invalid-kind",
        lineage_field_requirements={"record_id": ("crm.orders.id",)},
        metric_lineage_requirements={"total_optin": ("crm.optin.count",)},
    )

    with pytest.raises(S3ContractValidationServiceError) as exc:
        execute_s3_contract_validation_service(request)

    error = exc.value
    assert error.code == "INVALID_SOURCE_KIND"
    assert "source_kind suportado" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("conts3evt-")
