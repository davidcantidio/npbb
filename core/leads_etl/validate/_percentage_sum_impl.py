"""Grouped percentage-sum validation for the shared lead ETL core."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import sqlalchemy as sa

from ._contracts import CheckContext, CheckResult, CheckStatus, Severity
from ._percentage_config import BasePercentageCheck, PercentSumRuleConfig, PercentageCheckConfig, resolve_lineage_payload


class PercentSumCheck(BasePercentageCheck):
    """Validate grouped percentage sums against configured target values."""

    def __init__(self, config: PercentageCheckConfig, rule: PercentSumRuleConfig) -> None:
        super().__init__(config)
        self.rule = rule
        self.check_id = f"dq.percent.sum.{config.dataset_id}.{rule.rule_id}"
        self.description = "Valida soma de percentuais por grupo configurado."

    def run(self, context: CheckContext) -> CheckResult:
        session = context.require_resource("session")
        inspector = sa.inspect(session.get_bind())
        table_name = self.config.table
        if table_name not in set(inspector.get_table_names()):
            return CheckResult(check_id=self.check_id, status=CheckStatus.FAIL, severity=self.config.severity, message=("Tabela de dataset nao encontrada para check de soma percentual. Como corrigir: validar migration e config percentage_checks."), ingestion_id=context.ingestion_id, evidence={"dataset_id": self.config.dataset_id, "table": table_name, "missing_table": True})

        table = sa.Table(table_name, sa.MetaData(), autoload_with=session.get_bind())
        required_columns = (self.config.value_column, self.config.unit_column, self.config.source_id_column, self.config.lineage_ref_id_column, *self.rule.group_by)
        ok, missing_columns = self._ensure_columns(table, required=required_columns)
        if not ok:
            return CheckResult(check_id=self.check_id, status=CheckStatus.FAIL, severity=self.config.severity, message=("Schema incompleto para check de soma de percentuais. Como corrigir: alinhar group_by/value columns no dataset alvo."), ingestion_id=context.ingestion_id, evidence={"dataset_id": self.config.dataset_id, "table": table_name, "rule_id": self.rule.rule_id, "missing_columns": missing_columns})

        conditions = _build_conditions(self.config, context.ingestion_id, table)
        grouped_stmt = sa.select(*[table.c[column_name] for column_name in self.rule.group_by], sa.func.count().label("item_count"), sa.func.sum(table.c[self.config.value_column]).label("sum_value"), sa.func.min(table.c[self.config.source_id_column]).label("sample_source_id"), sa.func.min(table.c[self.config.lineage_ref_id_column]).label("sample_lineage_ref_id")).select_from(table).where(sa.and_(*conditions)).group_by(*[table.c[column_name] for column_name in self.rule.group_by])
        grouped_rows = [dict(row) for row in session.execute(grouped_stmt).mappings().all()]
        if not grouped_rows:
            return CheckResult(check_id=self.check_id, status=CheckStatus.SKIP, severity=Severity.INFO, message="Check ignorado: nenhum grupo percentual encontrado no escopo.", ingestion_id=context.ingestion_id, evidence={"dataset_id": self.config.dataset_id, "table": table_name, "rule_id": self.rule.rule_id, "group_count": 0})

        findings: list[dict[str, Any]] = []
        evaluated_groups = 0
        for group in grouped_rows:
            item_count = int(group.get("item_count") or 0)
            if item_count < self.rule.min_items:
                continue
            evaluated_groups += 1
            group_sum = Decimal(str(group.get("sum_value")))
            if abs(group_sum - self.rule.target_sum) > self.rule.tolerance:
                findings.append({"code": "PERCENT_SUM_MISMATCH", "rule_id": self.rule.rule_id, "group_key": {column: group.get(column) for column in self.rule.group_by}, "group_item_count": item_count, "group_sum": str(group_sum), "target_sum": str(self.rule.target_sum), "tolerance": str(self.rule.tolerance), "row_hint": {"source_id": group.get("sample_source_id"), "lineage_ref_id": group.get("sample_lineage_ref_id")}})

        if findings:
            sample = findings[:10]
            return CheckResult(check_id=self.check_id, status=CheckStatus.FAIL, severity=self.config.severity, message=("Soma de percentuais inconsistente por grupo configurado. Como corrigir: revisar metricas da pergunta/grupo e evidencias de origem."), ingestion_id=context.ingestion_id, evidence={"dataset_id": self.config.dataset_id, "table": table_name, "rule_id": self.rule.rule_id, "group_count": len(grouped_rows), "evaluated_groups": evaluated_groups, "finding_count": len(findings), "findings_sample": sample}, lineage=resolve_lineage_payload(sample[0].get("row_hint", {}), source_id_column="source_id", lineage_ref_id_column="lineage_ref_id"))
        if evaluated_groups == 0:
            return CheckResult(check_id=self.check_id, status=CheckStatus.SKIP, severity=Severity.INFO, message="Check ignorado: grupos com menos itens que o minimo para validar soma percentual.", ingestion_id=context.ingestion_id, evidence={"dataset_id": self.config.dataset_id, "table": table_name, "rule_id": self.rule.rule_id, "group_count": len(grouped_rows), "evaluated_groups": 0, "min_items": self.rule.min_items})
        return CheckResult(check_id=self.check_id, status=CheckStatus.PASS, severity=Severity.INFO, message="Soma de percentuais consistente para grupos avaliados.", ingestion_id=context.ingestion_id, evidence={"dataset_id": self.config.dataset_id, "table": table_name, "rule_id": self.rule.rule_id, "group_count": len(grouped_rows), "evaluated_groups": evaluated_groups, "finding_count": 0})


def _build_conditions(config: PercentageCheckConfig, ingestion_id: int | None, table: sa.Table) -> list[Any]:
    conditions: list[Any] = [sa.func.lower(sa.cast(table.c[config.unit_column], sa.String)).in_(list(config.percent_units)), table.c[config.value_column].is_not(None)]
    if config.ingestion_id_column in table.c and ingestion_id is not None:
        conditions.append(table.c[config.ingestion_id_column] == ingestion_id)
    if config.status_column and config.status_column in table.c and config.allowed_statuses:
        conditions.append(sa.func.lower(sa.cast(table.c[config.status_column], sa.String)).in_(list(config.allowed_statuses)))
    return conditions

