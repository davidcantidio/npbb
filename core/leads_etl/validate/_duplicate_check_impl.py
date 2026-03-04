"""Duplicate checks for the shared lead ETL core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import sqlalchemy as sa

from ._contracts import Check, CheckContext, CheckResult, CheckStatus, Severity
from ._dataset_config import DatasetCheckConfig


def _apply_scope_filters(statement: Any, *, table: sa.Table, ingestion_id_column: str, ingestion_id: int | None) -> Any:
    if ingestion_id is None or ingestion_id_column not in table.c:
        return statement
    return statement.where(table.c[ingestion_id_column] == ingestion_id)


def _sample_lineage_from_first_duplicate(session: Any, *, table: sa.Table, dataset_config: DatasetCheckConfig, key_columns: tuple[str, ...], first_group: dict[str, Any] | None, ingestion_id: int | None) -> dict[str, Any]:
    if not first_group:
        return {}
    if dataset_config.source_id_column not in table.c and dataset_config.lineage_ref_id_column not in table.c:
        return {}
    predicates = [table.c[column_name] == first_group.get(column_name) for column_name in key_columns if column_name in table.c]
    if not predicates:
        return {}
    select_cols: list[sa.Column] = []
    if dataset_config.source_id_column in table.c:
        select_cols.append(table.c[dataset_config.source_id_column])
    if dataset_config.lineage_ref_id_column in table.c:
        select_cols.append(table.c[dataset_config.lineage_ref_id_column])
    row = session.execute(_apply_scope_filters(sa.select(*select_cols).select_from(table).where(sa.and_(*predicates)).limit(1), table=table, ingestion_id_column=dataset_config.ingestion_id_column, ingestion_id=ingestion_id)).mappings().first()
    if row is None:
        return {}
    payload = dict(row)
    lineage: dict[str, Any] = {}
    if payload.get(dataset_config.source_id_column) is not None:
        lineage["source_id"] = payload.get(dataset_config.source_id_column)
    try:
        lineage_value = payload.get(dataset_config.lineage_ref_id_column)
        if lineage_value is not None and int(lineage_value) > 0:
            lineage["lineage_ref_id"] = int(lineage_value)
    except (TypeError, ValueError):
        pass
    return lineage


@dataclass(frozen=True)
class DuplicateCheckSpec:
    """One duplicate-check specification for a dataset key set."""

    dataset_config: DatasetCheckConfig
    key_columns: tuple[str, ...]


class DuplicateCheck(Check):
    """Detect duplicate rows for one dataset using configured key columns."""

    def __init__(self, spec: DuplicateCheckSpec, *, sample_limit: int = 5) -> None:
        if sample_limit <= 0:
            raise ValueError("sample_limit deve ser > 0.")
        self.spec = spec
        self.sample_limit = int(sample_limit)
        key_label = "_".join(spec.key_columns)
        self.check_id = f"dq.duplicates.{spec.dataset_config.dataset_id}.{key_label}"
        self.description = "Detecta duplicidade por chave configurada para evitar inflar contagens."

    def run(self, context: CheckContext) -> CheckResult:
        session = context.require_resource("session")
        inspector = sa.inspect(session.get_bind())
        dataset = self.spec.dataset_config
        table_name = dataset.table
        key_columns = self.spec.key_columns
        if table_name not in set(inspector.get_table_names()):
            return CheckResult(check_id=self.check_id, status=CheckStatus.FAIL, severity=dataset.severity, message=("Tabela de dataset nao encontrada para check de duplicidade. Como corrigir: validar migration e config no datasets.yml."), ingestion_id=context.ingestion_id, evidence={"dataset_id": dataset.dataset_id, "domain": dataset.domain, "table": table_name, "key_columns": list(key_columns), "missing_table": True})

        table = sa.Table(table_name, sa.MetaData(), autoload_with=session.get_bind())
        missing_columns = sorted(column for column in key_columns if column not in table.c)
        if missing_columns:
            return CheckResult(check_id=self.check_id, status=CheckStatus.FAIL, severity=dataset.severity, message=("Config de duplicidade referencia coluna inexistente. Como corrigir: ajustar duplicate_key_sets no datasets.yml."), ingestion_id=context.ingestion_id, evidence={"dataset_id": dataset.dataset_id, "table": table_name, "key_columns": list(key_columns), "missing_columns": missing_columns})

        group_columns = [table.c[column_name] for column_name in key_columns]
        duplicate_count_expr = sa.func.count().label("duplicate_count")
        grouped_stmt = _apply_scope_filters(sa.select(*group_columns, duplicate_count_expr).select_from(table).where(sa.and_(*[table.c[column_name].is_not(None) for column_name in key_columns])).group_by(*group_columns).having(sa.func.count() > 1), table=table, ingestion_id_column=dataset.ingestion_id_column, ingestion_id=context.ingestion_id)
        grouped_subquery = grouped_stmt.subquery()
        duplicate_group_count = int(session.execute(sa.select(sa.func.count()).select_from(grouped_subquery)).scalar_one() or 0)
        if duplicate_group_count <= 0:
            return CheckResult(check_id=self.check_id, status=CheckStatus.PASS, severity=Severity.INFO, message="Sem duplicidade para a chave configurada.", ingestion_id=context.ingestion_id, evidence={"dataset_id": dataset.dataset_id, "domain": dataset.domain, "table": table_name, "key_columns": list(key_columns), "duplicate_group_count": 0, "duplicate_total_rows": 0, "duplicate_excess_rows": 0, "sample_duplicates": []})

        duplicate_total_rows = int(session.execute(sa.select(sa.func.sum(grouped_subquery.c.duplicate_count)).select_from(grouped_subquery)).scalar_one() or 0)
        sample_rows = session.execute(_apply_scope_filters(sa.select(*group_columns, duplicate_count_expr).select_from(table).where(sa.and_(*[table.c[column_name].is_not(None) for column_name in key_columns])).group_by(*group_columns).having(sa.func.count() > 1).order_by(sa.desc(sa.func.count())).limit(self.sample_limit), table=table, ingestion_id_column=dataset.ingestion_id_column, ingestion_id=context.ingestion_id)).mappings().all()
        sample_duplicates = [dict(row) for row in sample_rows]
        lineage = _sample_lineage_from_first_duplicate(session, table=table, dataset_config=dataset, key_columns=key_columns, first_group=sample_duplicates[0] if sample_duplicates else None, ingestion_id=context.ingestion_id)
        return CheckResult(check_id=self.check_id, status=CheckStatus.FAIL, severity=dataset.severity, message=("Duplicidade detectada para chave configurada. Como corrigir: revisar reimportacoes e regras de dedupe no extractor/loader."), ingestion_id=context.ingestion_id, evidence={"dataset_id": dataset.dataset_id, "domain": dataset.domain, "table": table_name, "key_columns": list(key_columns), "duplicate_group_count": duplicate_group_count, "duplicate_total_rows": duplicate_total_rows, "duplicate_excess_rows": max(0, duplicate_total_rows - duplicate_group_count), "sample_limit": self.sample_limit, "sample_duplicates": sample_duplicates}, lineage=lineage)


def build_duplicate_checks(configs: tuple[DatasetCheckConfig, ...], *, sample_limit: int = 5) -> tuple[DuplicateCheck, ...]:
    """Build duplicate checks from dataset configs."""

    checks: list[DuplicateCheck] = []
    for config in configs:
        for key_set in config.duplicate_key_sets:
            checks.append(DuplicateCheck(DuplicateCheckSpec(dataset_config=config, key_columns=key_set), sample_limit=sample_limit))
    return tuple(checks)

