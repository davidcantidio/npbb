"""Controlled metric definitions for TMJ audience ruler.

This module defines:
- controlled metric domains (`MetricType`, `AudienceMeasure`),
- a validation contract for mart/report metric labels,
- and explicit usage guidance for each audience measure.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MetricType(str, Enum):
    """Metric type domain used to label marts/report outputs.

    Use:
    - `absoluto` for direct counts (no denominator).
    - `percentual` for derived `%` metrics.
    - `taxa` for derived rates/ratios.

    Do not use:
    - `absoluto` for metrics that depend on numerator/denominator.
    """

    ABSOLUTO = "absoluto"
    PERCENTUAL = "percentual"
    TAXA = "taxa"


class AudienceMeasure(str, Enum):
    """Audience measure domain for TMJ closing metrics.

    Definitions:
    - `entradas_validadas`: official access-control validated entries.
    - `publico_unico`: deduplicated people count.
    - `ingressos_vendidos`: sold ticket count.
    - `optin_aceitos`: Eventim opt-in accepted subset.

    Important:
    - `optin_aceitos` is a subset/proxy slice and must not replace
      `ingressos_vendidos` or `entradas_validadas`.
    """

    ENTRADAS_VALIDADAS = "entradas_validadas"
    PUBLICO_UNICO = "publico_unico"
    INGRESSOS_VENDIDOS = "ingressos_vendidos"
    OPTIN_ACEITOS = "optin_aceitos"


DERIVED_METRIC_TYPES: tuple[MetricType, ...] = (
    MetricType.PERCENTUAL,
    MetricType.TAXA,
)

AUDIENCE_MEASURE_USAGE: dict[AudienceMeasure, str] = {
    AudienceMeasure.ENTRADAS_VALIDADAS: (
        "Medida oficial de comparecimento por controle de acesso/catraca."
    ),
    AudienceMeasure.PUBLICO_UNICO: (
        "Medida deduplicada de pessoas; depende de chave de dedupe consistente."
    ),
    AudienceMeasure.INGRESSOS_VENDIDOS: (
        "Medida oficial comercial de venda de ingressos."
    ),
    AudienceMeasure.OPTIN_ACEITOS: (
        "Recorte de usuarios com opt-in aceito (Eventim). Nao substitui "
        "ingressos_vendidos nem entradas_validadas."
    ),
}


class MetricDefinitionError(ValueError):
    """Raised when metric label contract validation fails."""


@dataclass(frozen=True)
class MetricLabelContract:
    """Contract for labeling one metric in marts/reports.

    Args:
        metric_key: Stable metric identifier in mart/report layer.
        metric_type: Controlled metric type (`absoluto`, `percentual`, `taxa`).
        audience_measure: Controlled audience measure used by the metric.
        numerator: Required when metric is derived (`percentual`/`taxa`).
        denominator: Required when metric is derived (`percentual`/`taxa`).
        is_primary_kpi: True when metric is used as official headline KPI.
        notes: Optional methodological note.
    """

    metric_key: str
    metric_type: MetricType
    audience_measure: AudienceMeasure
    numerator: str | None = None
    denominator: str | None = None
    is_primary_kpi: bool = False
    notes: str | None = None

    def validate(self) -> None:
        """Validate metric label contract constraints.

        Returns:
            None.

        Raises:
            MetricDefinitionError: If contract violates required rules.
        """

        if not str(self.metric_key or "").strip():
            raise MetricDefinitionError("metric_key obrigatorio para rotulagem de metrica.")

        if self.metric_type in DERIVED_METRIC_TYPES:
            if not str(self.numerator or "").strip():
                raise MetricDefinitionError(
                    "Metrica derivada exige numerator informado no contrato."
                )
            if not str(self.denominator or "").strip():
                raise MetricDefinitionError(
                    "Metrica derivada exige denominator informado no contrato."
                )
        else:
            if self.denominator is not None and str(self.denominator).strip():
                raise MetricDefinitionError(
                    "Metrica absoluta nao deve definir denominator."
                )

        if self.is_primary_kpi and self.audience_measure == AudienceMeasure.OPTIN_ACEITOS:
            raise MetricDefinitionError(
                "optin_aceitos e recorte e nao pode ser KPI primario. "
                "Use ingressos_vendidos ou entradas_validadas."
            )


def audience_measure_usage_note(audience_measure: AudienceMeasure) -> str:
    """Return usage guidance for one audience measure.

    Args:
        audience_measure: Controlled audience measure.

    Returns:
        Human-readable usage guidance note.

    Raises:
        KeyError: If the measure has no configured guidance note.
    """

    return AUDIENCE_MEASURE_USAGE[audience_measure]

