"""Unit tests for controlled audience metric definitions and contracts."""

from __future__ import annotations

import pytest

from core.metrics import (
    AudienceMeasure,
    MetricDefinitionError,
    MetricLabelContract,
    MetricType,
    audience_measure_usage_note,
)


def test_metric_domains_are_controlled_and_stable() -> None:
    """Metric domains expose expected controlled values."""

    assert MetricType.ABSOLUTO.value == "absoluto"
    assert MetricType.PERCENTUAL.value == "percentual"
    assert MetricType.TAXA.value == "taxa"

    assert AudienceMeasure.ENTRADAS_VALIDADAS.value == "entradas_validadas"
    assert AudienceMeasure.PUBLICO_UNICO.value == "publico_unico"
    assert AudienceMeasure.INGRESSOS_VENDIDOS.value == "ingressos_vendidos"
    assert AudienceMeasure.OPTIN_ACEITOS.value == "optin_aceitos"


def test_derived_metric_requires_numerator_and_denominator() -> None:
    """Derived metric labels must define numerator and denominator contracts."""

    with pytest.raises(MetricDefinitionError, match="numerator"):
        MetricLabelContract(
            metric_key="taxa_comparecimento",
            metric_type=MetricType.PERCENTUAL,
            audience_measure=AudienceMeasure.ENTRADAS_VALIDADAS,
            denominator="ingressos_validos",
        ).validate()

    with pytest.raises(MetricDefinitionError, match="denominator"):
        MetricLabelContract(
            metric_key="taxa_comparecimento",
            metric_type=MetricType.TAXA,
            audience_measure=AudienceMeasure.ENTRADAS_VALIDADAS,
            numerator="presentes",
        ).validate()


def test_absoluto_metric_rejects_denominator_field() -> None:
    """Absolute metrics must not declare denominator in the contract."""

    with pytest.raises(MetricDefinitionError, match="nao deve definir denominator"):
        MetricLabelContract(
            metric_key="entradas_total",
            metric_type=MetricType.ABSOLUTO,
            audience_measure=AudienceMeasure.ENTRADAS_VALIDADAS,
            denominator="total_dia",
        ).validate()


def test_optin_cannot_be_primary_kpi() -> None:
    """`optin_aceitos` cannot be used as primary headline KPI."""

    with pytest.raises(MetricDefinitionError, match="nao pode ser KPI primario"):
        MetricLabelContract(
            metric_key="publico_principal",
            metric_type=MetricType.ABSOLUTO,
            audience_measure=AudienceMeasure.OPTIN_ACEITOS,
            is_primary_kpi=True,
        ).validate()


def test_valid_metric_contract_passes_and_usage_note_is_explicit() -> None:
    """Valid contract should pass and opt-in note must state non-substitution rule."""

    contract = MetricLabelContract(
        metric_key="taxa_comparecimento_show",
        metric_type=MetricType.PERCENTUAL,
        audience_measure=AudienceMeasure.ENTRADAS_VALIDADAS,
        numerator="presentes",
        denominator="ingressos_validos",
        is_primary_kpi=True,
    )
    contract.validate()

    note = audience_measure_usage_note(AudienceMeasure.OPTIN_ACEITOS)
    assert "Nao substitui" in note
    assert "ingressos_vendidos" in note
    assert "entradas_validadas" in note

