"""Cross-source inconsistency checks for shared metric keys.

This module detects when the same metric key appears in multiple sources with
conflicting values and records findings as `INCONSISTENTE` evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
from typing import Any, Mapping, Sequence

import sqlalchemy as sa
from sqlmodel import select

from .framework import Check, CheckContext, CheckResult, CheckStatus, Severity


@dataclass(frozen=True)
class CrossSourceDatasetSpec:
    """Dataset contract for cross-source inconsistency comparison.

    Args:
        dataset_id: Stable dataset identifier used in evidence payload.
        table: Database table name containing metric rows.
        metric_key_column: Column with metric key/identifier.
        metric_value_column: Numeric column with metric value.
        source_id_column: Column with source identifier.
        lineage_ref_id_column: Optional lineage reference id column.
        unit_column: Optional unit column used in grouping (`percent`, `count`).
        ingestion_id_column: Optional ingestion scope column.
        status_column: Optional status discriminator column.
        allowed_statuses: Optional accepted statuses for comparison.
    """

    dataset_id: str
    table: str
    metric_key_column: str = "metric_key"
    metric_value_column: str = "metric_value"
    source_id_column: str = "source_id"
    lineage_ref_id_column: str = "lineage_ref_id"
    unit_column: str = "unit"
    ingestion_id_column: str = "ingestion_id"
    status_column: str | None = None
    allowed_statuses: tuple[str, ...] = ()


def _to_decimal(value: Any) -> Decimal | None:
    """Convert source value to Decimal when possible."""

    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _normalize_optional_text(value: Any) -> str | None:
    """Normalize optional text value to stripped string or None."""

    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_positive_int(value: Any) -> int | None:
    """Parse positive integer value when possible."""

    try:
        if value is None:
            return None
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _collect_lineage_payload(finding: Mapping[str, Any]) -> dict[str, Any]:
    """Collect first available lineage payload from one finding."""

    payload: dict[str, Any] = {}
    for source_row in finding.get("source_values", []):
        source_id = source_row.get("source_id")
        if "source_id" not in payload and source_id:
            payload["source_id"] = source_id
        lineage_ids = source_row.get("lineage_ref_ids") or []
        for lineage_id in lineage_ids:
            parsed = _parse_positive_int(lineage_id)
            if parsed is not None:
                payload["lineage_ref_id"] = parsed
                break
        if "source_id" in payload and "lineage_ref_id" in payload:
            break
    return payload


def _serialize_json(value: Any) -> str:
    """Serialize payload to deterministic JSON string."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def persist_cross_source_inconsistencies(
    session: Any,
    *,
    ingestion_id: int | None,
    check_id: str,
    severity: Severity,
    findings: Sequence[Mapping[str, Any]],
    replace_existing: bool = True,
) -> int:
    """Persist cross-source inconsistencies in backend table `dq_inconsistency`.

    Args:
        session: SQLModel session connected to backend database.
        ingestion_id: Ingestion identifier for row scope.
        check_id: Stable checker identifier.
        severity: Severity assigned to persisted rows.
        findings: Inconsistency findings payloads.
        replace_existing: Whether previous rows for same scope should be removed.

    Returns:
        Number of persisted rows.

    Raises:
        RuntimeError: If backend model dependencies are unavailable.
        Exception: Any database error from session operations.
    """

    if ingestion_id is None:
        return 0

    try:
        from app.models.dq_inconsistency import (
            DQInconsistency,
            DQInconsistencySeverity,
            DQInconsistencyStatus,
            now_utc,
        )
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on caller PYTHONPATH
        raise RuntimeError(
            "Dependencia de backend indisponivel para persistir inconsistencias. "
            "Como corrigir: garantir import de app.models.dq_inconsistency."
        ) from exc

    if replace_existing:
        existing_rows = session.exec(
            select(DQInconsistency).where(
                DQInconsistency.ingestion_id == int(ingestion_id),
                DQInconsistency.check_id == check_id,
            )
        ).all()
        for row in existing_rows:
            session.delete(row)
        session.flush()

    persisted_count = 0
    severity_value = DQInconsistencySeverity(severity.value)
    for finding in findings:
        source_values = list(finding.get("source_values", []))
        source_ids = sorted(
            {
                str(item.get("source_id")).strip()
                for item in source_values
                if item.get("source_id")
            }
        )
        lineage_ids = sorted(
            {
                int(item)
                for source_item in source_values
                for item in (source_item.get("lineage_ref_ids") or [])
                if _parse_positive_int(item) is not None
            }
        )
        row = DQInconsistency(
            ingestion_id=int(ingestion_id),
            check_id=check_id,
            dataset_id=str(finding.get("dataset_id") or "").strip(),
            metric_key=str(finding.get("metric_key") or "").strip(),
            unit=_normalize_optional_text(finding.get("unit")),
            status=DQInconsistencyStatus.INCONSISTENTE,
            severity=severity_value,
            values_json=_serialize_json(source_values),
            sources_json=_serialize_json(source_ids),
            lineage_refs_json=_serialize_json(lineage_ids) if lineage_ids else None,
            evidence_json=_serialize_json(finding),
            suggested_action=str(finding.get("suggested_action") or "").strip()
            or "Revisar divergencia entre fontes e aplicar regra de precedencia.",
            created_at=now_utc(),
        )
        session.add(row)
        persisted_count += 1

    session.commit()
    return persisted_count


class CrossSourceInconsistencyCheck(Check):
    """Detect cross-source metric divergences and classify as INCONSISTENTE."""

    check_id = "dq.cross_source.inconsistency"
    description = (
        "Compara metricas com mesma chave entre fontes e marca divergencias como INCONSISTENTE."
    )

    def __init__(
        self,
        dataset_specs: Sequence[CrossSourceDatasetSpec],
        *,
        severity: Severity = Severity.WARNING,
        tolerance: Decimal = Decimal("0"),
        min_sources: int = 2,
        sample_limit: int = 10,
        persist_inconsistencies: bool = True,
        replace_existing: bool = True,
    ) -> None:
        """Initialize cross-source inconsistency check.

        Args:
            dataset_specs: Dataset specifications to compare across sources.
            severity: Severity used when inconsistencies are found.
            tolerance: Maximum allowed absolute difference between source values.
            min_sources: Minimum number of distinct sources per metric key.
            sample_limit: Maximum findings included in check evidence.
            persist_inconsistencies: Whether findings are persisted to table.
            replace_existing: Whether previous persisted rows are replaced.

        Raises:
            ValueError: If arguments are invalid.
        """

        if not dataset_specs:
            raise ValueError("dataset_specs nao pode ser vazio.")
        if tolerance < 0:
            raise ValueError("tolerance nao pode ser negativo.")
        if min_sources < 2:
            raise ValueError("min_sources deve ser >= 2.")
        if sample_limit <= 0:
            raise ValueError("sample_limit deve ser > 0.")

        self._dataset_specs = tuple(dataset_specs)
        self._severity = severity
        self._tolerance = tolerance
        self._min_sources = int(min_sources)
        self._sample_limit = int(sample_limit)
        self._persist_inconsistencies = bool(persist_inconsistencies)
        self._replace_existing = bool(replace_existing)

    def run(self, context: CheckContext) -> CheckResult:
        """Execute cross-source divergence detection.

        Args:
            context: Check context with SQL session resource.

        Returns:
            Pass/fail/skip result with evidence and optional persistence count.
        """

        session = context.require_resource("session")
        engine = session.get_bind()
        inspector = sa.inspect(engine)
        table_names = set(inspector.get_table_names())

        grouped: dict[tuple[str, str, str | None], list[dict[str, Any]]] = {}
        missing_tables: list[str] = []
        invalid_schema: list[dict[str, Any]] = []
        skipped_non_numeric = 0
        compared_rows = 0

        for spec in self._dataset_specs:
            if spec.table not in table_names:
                missing_tables.append(spec.table)
                continue

            table = sa.Table(spec.table, sa.MetaData(), autoload_with=engine)
            required_columns = [
                spec.metric_key_column,
                spec.metric_value_column,
                spec.source_id_column,
                spec.lineage_ref_id_column,
            ]
            if spec.unit_column:
                required_columns.append(spec.unit_column)
            if spec.status_column:
                required_columns.append(spec.status_column)

            missing_columns = sorted(column for column in required_columns if column not in table.c)
            if missing_columns:
                invalid_schema.append(
                    {
                        "dataset_id": spec.dataset_id,
                        "table": spec.table,
                        "missing_columns": missing_columns,
                    }
                )
                continue

            select_columns = [
                table.c[spec.metric_key_column].label("metric_key"),
                table.c[spec.metric_value_column].label("metric_value"),
                table.c[spec.source_id_column].label("source_id"),
                table.c[spec.lineage_ref_id_column].label("lineage_ref_id"),
            ]
            if spec.unit_column:
                select_columns.append(table.c[spec.unit_column].label("unit"))
            else:
                select_columns.append(sa.literal(None).label("unit"))

            stmt = select(*select_columns).select_from(table).where(
                table.c[spec.metric_key_column].is_not(None),
                table.c[spec.metric_value_column].is_not(None),
                table.c[spec.source_id_column].is_not(None),
            )
            if context.ingestion_id is not None and spec.ingestion_id_column in table.c:
                stmt = stmt.where(table.c[spec.ingestion_id_column] == context.ingestion_id)

            allowed_statuses = {status.lower() for status in spec.allowed_statuses}
            if spec.status_column and allowed_statuses:
                status_expr = sa.func.lower(sa.cast(table.c[spec.status_column], sa.String))
                stmt = stmt.where(status_expr.in_(list(allowed_statuses)))

            rows = session.execute(stmt).mappings().all()
            for row in rows:
                metric_key = str(row.get("metric_key") or "").strip()
                source_id = str(row.get("source_id") or "").strip()
                unit = _normalize_optional_text(row.get("unit"))
                metric_value = _to_decimal(row.get("metric_value"))
                if not metric_key or not source_id:
                    continue
                if metric_value is None:
                    skipped_non_numeric += 1
                    continue

                compared_rows += 1
                group_key = (spec.dataset_id, metric_key, unit)
                grouped.setdefault(group_key, []).append(
                    {
                        "source_id": source_id,
                        "metric_value": metric_value,
                        "lineage_ref_id": _parse_positive_int(row.get("lineage_ref_id")),
                    }
                )

        if invalid_schema:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self._severity,
                message=(
                    "Schema invalido para comparacao entre fontes. Como corrigir: "
                    "alinhar colunas dos datasets configurados."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "invalid_schema": invalid_schema,
                    "missing_tables": missing_tables,
                },
            )

        findings: list[dict[str, Any]] = []
        for (dataset_id, metric_key, unit), entries in grouped.items():
            per_source_values: dict[str, set[Decimal]] = {}
            per_source_lineage: dict[str, set[int]] = {}
            for item in entries:
                source_id = str(item["source_id"])
                per_source_values.setdefault(source_id, set()).add(item["metric_value"])
                lineage_id = _parse_positive_int(item.get("lineage_ref_id"))
                if lineage_id is not None:
                    per_source_lineage.setdefault(source_id, set()).add(lineage_id)

            if len(per_source_values) < self._min_sources:
                continue

            distinct_values = sorted({value for values in per_source_values.values() for value in values})
            if not distinct_values:
                continue
            min_value = distinct_values[0]
            max_value = distinct_values[-1]
            has_source_internal_conflict = any(len(values) > 1 for values in per_source_values.values())
            has_cross_source_conflict = (max_value - min_value) > self._tolerance
            if not has_source_internal_conflict and not has_cross_source_conflict:
                continue

            source_values: list[dict[str, Any]] = []
            for source_id in sorted(per_source_values):
                values = sorted(per_source_values[source_id])
                lineage_ids = sorted(per_source_lineage.get(source_id, set()))
                source_values.append(
                    {
                        "source_id": source_id,
                        "metric_values": [str(value) for value in values],
                        "lineage_ref_ids": lineage_ids,
                    }
                )

            findings.append(
                {
                    "status": "INCONSISTENTE",
                    "dataset_id": dataset_id,
                    "metric_key": metric_key,
                    "unit": unit,
                    "source_count": len(per_source_values),
                    "distinct_value_count": len(distinct_values),
                    "source_values": source_values,
                    "suggested_action": (
                        "Revisar fonte A vs B e definir regra de precedencia antes de publicar."
                    ),
                }
            )

        findings.sort(
            key=lambda item: (
                str(item.get("dataset_id") or ""),
                str(item.get("metric_key") or ""),
                str(item.get("unit") or ""),
            )
        )
        persisted_count = 0
        if findings and self._persist_inconsistencies:
            persisted_count = persist_cross_source_inconsistencies(
                session,
                ingestion_id=context.ingestion_id,
                check_id=self.check_id,
                severity=self._severity,
                findings=findings,
                replace_existing=self._replace_existing,
            )

        if findings:
            sample = findings[: self._sample_limit]
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self._severity,
                message=(
                    "Metricas INCONSISTENTE detectadas entre fontes. Como corrigir: "
                    "revisar evidencias e registrar decisao de reconciliacao."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "status": "INCONSISTENTE",
                    "finding_count": len(findings),
                    "metric_keys": [str(item.get("metric_key") or "") for item in findings],
                    "sample_limit": self._sample_limit,
                    "findings_sample": sample,
                    "missing_tables": missing_tables,
                    "compared_rows": compared_rows,
                    "skipped_non_numeric": skipped_non_numeric,
                    "persisted_count": persisted_count,
                },
                lineage=_collect_lineage_payload(sample[0]),
            )

        if compared_rows == 0:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.SKIP,
                severity=Severity.INFO,
                message="Check ignorado: nenhuma metrica comparavel no escopo.",
                ingestion_id=context.ingestion_id,
                evidence={
                    "missing_tables": missing_tables,
                    "compared_rows": 0,
                    "skipped_non_numeric": skipped_non_numeric,
                },
            )

        return CheckResult(
            check_id=self.check_id,
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="Sem inconsistencias entre fontes para as metricas comparadas.",
            ingestion_id=context.ingestion_id,
            evidence={
                "missing_tables": missing_tables,
                "compared_rows": compared_rows,
                "skipped_non_numeric": skipped_non_numeric,
                "finding_count": 0,
            },
        )
