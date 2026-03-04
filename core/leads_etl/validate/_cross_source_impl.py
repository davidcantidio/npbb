"""Cross-source inconsistency checks for the shared lead ETL core."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

import sqlalchemy as sa

from ._contracts import Check, CheckContext, CheckResult, CheckStatus, Severity
from ._cross_source_persistence import persist_cross_source_inconsistencies


@dataclass(frozen=True)
class CrossSourceDatasetSpec:
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
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_positive_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _collect_lineage_payload(finding: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for source_row in finding.get("source_values", []):
        if "source_id" not in payload and source_row.get("source_id"):
            payload["source_id"] = source_row.get("source_id")
        for lineage_id in source_row.get("lineage_ref_ids") or []:
            parsed = _parse_positive_int(lineage_id)
            if parsed is not None:
                payload["lineage_ref_id"] = parsed
                break
        if "source_id" in payload and "lineage_ref_id" in payload:
            break
    return payload


class CrossSourceInconsistencyCheck(Check):
    """Detect cross-source metric divergences and classify as INCONSISTENTE."""

    check_id = "dq.cross_source.inconsistency"
    description = "Compara metricas com mesma chave entre fontes e marca divergencias como INCONSISTENTE."

    def __init__(self, dataset_specs: tuple[CrossSourceDatasetSpec, ...], *, severity: Severity = Severity.WARNING, tolerance: Decimal = Decimal("0"), min_sources: int = 2, sample_limit: int = 10, persist_inconsistencies: bool = True, replace_existing: bool = True) -> None:
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
        session = context.require_resource("session")
        table_names = set(sa.inspect(session.get_bind()).get_table_names())
        grouped: dict[tuple[str, str, str | None], list[dict[str, Any]]] = {}
        missing_tables: list[str] = []
        invalid_schema: list[dict[str, Any]] = []
        skipped_non_numeric = 0
        compared_rows = 0

        for spec in self._dataset_specs:
            if spec.table not in table_names:
                missing_tables.append(spec.table)
                continue
            table = sa.Table(spec.table, sa.MetaData(), autoload_with=session.get_bind())
            required_columns = [spec.metric_key_column, spec.metric_value_column, spec.source_id_column, spec.lineage_ref_id_column]
            if spec.unit_column:
                required_columns.append(spec.unit_column)
            if spec.status_column:
                required_columns.append(spec.status_column)
            missing_columns = sorted(column for column in required_columns if column not in table.c)
            if missing_columns:
                invalid_schema.append({"dataset_id": spec.dataset_id, "table": spec.table, "missing_columns": missing_columns})
                continue
            compared_rows, skipped_non_numeric = self._collect_rows(session, context.ingestion_id, spec, table, grouped, compared_rows, skipped_non_numeric)

        if invalid_schema:
            return CheckResult(check_id=self.check_id, status=CheckStatus.FAIL, severity=self._severity, message=("Schema invalido para comparacao entre fontes. Como corrigir: alinhar colunas dos datasets configurados."), ingestion_id=context.ingestion_id, evidence={"invalid_schema": invalid_schema, "missing_tables": missing_tables})

        findings = self._build_findings(grouped)
        persisted_count = 0
        if findings and self._persist_inconsistencies:
            persisted_count = persist_cross_source_inconsistencies(session, ingestion_id=context.ingestion_id, check_id=self.check_id, severity=self._severity, findings=findings, replace_existing=self._replace_existing)
        if findings:
            sample = findings[: self._sample_limit]
            return CheckResult(check_id=self.check_id, status=CheckStatus.FAIL, severity=self._severity, message=("Metricas INCONSISTENTE detectadas entre fontes. Como corrigir: revisar evidencias e registrar decisao de reconciliacao."), ingestion_id=context.ingestion_id, evidence={"status": "INCONSISTENTE", "finding_count": len(findings), "metric_keys": [str(item.get("metric_key") or "") for item in findings], "sample_limit": self._sample_limit, "findings_sample": sample, "missing_tables": missing_tables, "compared_rows": compared_rows, "skipped_non_numeric": skipped_non_numeric, "persisted_count": persisted_count}, lineage=_collect_lineage_payload(sample[0]))
        if compared_rows == 0:
            return CheckResult(check_id=self.check_id, status=CheckStatus.SKIP, severity=Severity.INFO, message="Check ignorado: nenhuma metrica comparavel no escopo.", ingestion_id=context.ingestion_id, evidence={"missing_tables": missing_tables, "compared_rows": 0, "skipped_non_numeric": skipped_non_numeric})
        return CheckResult(check_id=self.check_id, status=CheckStatus.PASS, severity=Severity.INFO, message="Sem inconsistencias entre fontes para as metricas comparadas.", ingestion_id=context.ingestion_id, evidence={"missing_tables": missing_tables, "compared_rows": compared_rows, "skipped_non_numeric": skipped_non_numeric, "finding_count": 0})

    def _collect_rows(self, session: Any, ingestion_id: int | None, spec: CrossSourceDatasetSpec, table: sa.Table, grouped: dict[tuple[str, str, str | None], list[dict[str, Any]]], compared_rows: int, skipped_non_numeric: int) -> tuple[int, int]:
        stmt = sa.select(table.c[spec.metric_key_column].label("metric_key"), table.c[spec.metric_value_column].label("metric_value"), table.c[spec.source_id_column].label("source_id"), table.c[spec.lineage_ref_id_column].label("lineage_ref_id"), (table.c[spec.unit_column].label("unit") if spec.unit_column else sa.literal(None).label("unit"))).select_from(table).where(table.c[spec.metric_key_column].is_not(None), table.c[spec.metric_value_column].is_not(None), table.c[spec.source_id_column].is_not(None))
        if ingestion_id is not None and spec.ingestion_id_column in table.c:
            stmt = stmt.where(table.c[spec.ingestion_id_column] == ingestion_id)
        allowed_statuses = {status.lower() for status in spec.allowed_statuses}
        if spec.status_column and allowed_statuses:
            stmt = stmt.where(sa.func.lower(sa.cast(table.c[spec.status_column], sa.String)).in_(list(allowed_statuses)))
        for row in session.execute(stmt).mappings().all():
            metric_key = str(row.get("metric_key") or "").strip()
            source_id = str(row.get("source_id") or "").strip()
            metric_value = _to_decimal(row.get("metric_value"))
            if not metric_key or not source_id:
                continue
            if metric_value is None:
                skipped_non_numeric += 1
                continue
            compared_rows += 1
            grouped.setdefault((spec.dataset_id, metric_key, _normalize_optional_text(row.get("unit"))), []).append({"source_id": source_id, "metric_value": metric_value, "lineage_ref_id": _parse_positive_int(row.get("lineage_ref_id"))})
        return compared_rows, skipped_non_numeric

    def _build_findings(self, grouped: dict[tuple[str, str, str | None], list[dict[str, Any]]]) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        for (dataset_id, metric_key, unit), entries in grouped.items():
            per_source_values: dict[str, set[Decimal]] = {}
            per_source_lineage: dict[str, set[int]] = {}
            for item in entries:
                per_source_values.setdefault(str(item["source_id"]), set()).add(item["metric_value"])
                lineage_id = _parse_positive_int(item.get("lineage_ref_id"))
                if lineage_id is not None:
                    per_source_lineage.setdefault(str(item["source_id"]), set()).add(lineage_id)
            if len(per_source_values) < self._min_sources:
                continue
            distinct_values = sorted({value for values in per_source_values.values() for value in values})
            if distinct_values and (any(len(values) > 1 for values in per_source_values.values()) or (distinct_values[-1] - distinct_values[0]) > self._tolerance):
                findings.append({"status": "INCONSISTENTE", "dataset_id": dataset_id, "metric_key": metric_key, "unit": unit, "source_count": len(per_source_values), "distinct_value_count": len(distinct_values), "source_values": [{"source_id": source_id, "metric_values": [str(value) for value in sorted(per_source_values[source_id])], "lineage_ref_ids": sorted(per_source_lineage.get(source_id, set()))} for source_id in sorted(per_source_values)], "suggested_action": "Revisar fonte A vs B e definir regra de precedencia antes de publicar."})
        findings.sort(key=lambda item: (str(item.get("dataset_id") or ""), str(item.get("metric_key") or ""), str(item.get("unit") or "")))
        return findings

