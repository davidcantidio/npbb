"""Percentage bounds validation for the shared lead ETL core."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

import sqlalchemy as sa

from ._contracts import CheckContext, CheckResult, CheckStatus, Severity
from ._percentage_config import BasePercentageCheck, PercentageCheckConfig, resolve_lineage_payload


class PercentBoundsCheck(BasePercentageCheck):
    """Validate percentage values are within configured bounds and lineage rules."""

    def __init__(self, config: PercentageCheckConfig) -> None:
        super().__init__(config)
        self.check_id = f"dq.percent.bounds.{config.dataset_id}"
        self.description = "Valida bounds de percentuais por dataset."

    def run(self, context: CheckContext) -> CheckResult:
        session = context.require_resource("session")
        inspector = sa.inspect(session.get_bind())
        table_name = self.config.table
        if table_name not in set(inspector.get_table_names()):
            return CheckResult(check_id=self.check_id, status=CheckStatus.FAIL, severity=self.config.severity, message=("Tabela de dataset nao encontrada para check de percentuais. Como corrigir: validar migration e config percentage_checks."), ingestion_id=context.ingestion_id, evidence={"dataset_id": self.config.dataset_id, "table": table_name, "missing_table": True})

        table = sa.Table(table_name, sa.MetaData(), autoload_with=session.get_bind())
        ok, missing_columns = self._ensure_columns(table, required=(self.config.value_column, self.config.unit_column, self.config.source_id_column, self.config.lineage_ref_id_column))
        if not ok:
            return CheckResult(check_id=self.check_id, status=CheckStatus.FAIL, severity=self.config.severity, message=("Schema incompleto para check de percentuais. Como corrigir: alinhar tabela alvo com config percentage_checks."), ingestion_id=context.ingestion_id, evidence={"dataset_id": self.config.dataset_id, "table": table_name, "missing_columns": missing_columns})

        rows = [dict(row) for row in session.execute(self._build_base_filtered_stmt(context, table, include_value_not_null=True)).mappings().all()]
        if not rows:
            return CheckResult(check_id=self.check_id, status=CheckStatus.SKIP, severity=Severity.INFO, message="Check ignorado: nenhum percentual encontrado no escopo.", ingestion_id=context.ingestion_id, evidence={"dataset_id": self.config.dataset_id, "table": table_name, "scoped_rows": 0})

        findings: list[dict[str, Any]] = []
        for row in rows:
            raw_value = row.get(self.config.value_column)
            try:
                value = Decimal(str(raw_value))
            except (InvalidOperation, ValueError, TypeError):
                findings.append({"code": "PERCENT_VALUE_INVALID", "value": raw_value, "row_hint": {"source_id": row.get(self.config.source_id_column), "lineage_ref_id": row.get(self.config.lineage_ref_id_column)}})
                continue
            if value < self.config.lower_bound or value > self.config.upper_bound:
                findings.append({"code": "PERCENT_OUT_OF_BOUNDS", "value": str(value), "bounds": [str(self.config.lower_bound), str(self.config.upper_bound)], "row_hint": {"source_id": row.get(self.config.source_id_column), "lineage_ref_id": row.get(self.config.lineage_ref_id_column)}})
            if self.config.require_lineage and not _has_lineage(row.get(self.config.lineage_ref_id_column)):
                findings.append({"code": "PERCENT_MISSING_LINEAGE", "value": str(value), "row_hint": {"source_id": row.get(self.config.source_id_column), "lineage_ref_id": row.get(self.config.lineage_ref_id_column)}})

        if findings:
            sample = findings[:10]
            return CheckResult(check_id=self.check_id, status=CheckStatus.FAIL, severity=self.config.severity, message=("Percentuais fora de bounds e/ou sem linhagem detectados. Como corrigir: revisar parse da metrica e registro de lineage_ref."), ingestion_id=context.ingestion_id, evidence={"dataset_id": self.config.dataset_id, "table": table_name, "scoped_rows": len(rows), "finding_count": len(findings), "findings_sample": sample}, lineage=resolve_lineage_payload(sample[0].get("row_hint", {}), source_id_column="source_id", lineage_ref_id_column="lineage_ref_id"))
        return CheckResult(check_id=self.check_id, status=CheckStatus.PASS, severity=Severity.INFO, message="Percentuais em bounds e com linhagem no escopo.", ingestion_id=context.ingestion_id, evidence={"dataset_id": self.config.dataset_id, "table": table_name, "scoped_rows": len(rows), "finding_count": 0})


def _has_lineage(value: Any) -> bool:
    try:
        return value is not None and int(value) > 0
    except (TypeError, ValueError):
        return False

