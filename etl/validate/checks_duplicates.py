"""Duplicate-key checks driven by dataset YAML configuration.

This module provides `DuplicateCheck` to detect duplicate rows in dataset
tables using configured key sets (for example: `cpf_hash + evento + sessao`).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import sqlalchemy as sa
from sqlmodel import select

from .checks_schema import DatasetCheckConfig
from .framework import Check, CheckContext, CheckResult, CheckStatus, Severity


def _apply_scope_filters(
    statement: Any,  # sqlalchemy Select
    *,
    table: sa.Table,
    ingestion_id_column: str,
    ingestion_id: int | None,
) -> Any:
    """Apply ingestion scope filter when context and column are available.

    Args:
        statement: SQLAlchemy selectable statement.
        table: Reflected SQLAlchemy table object.
        ingestion_id_column: Configured ingestion column for the dataset.
        ingestion_id: Ingestion id from check context.

    Returns:
        Statement with optional ingestion filter.
    """

    if ingestion_id is None:
        return statement
    if ingestion_id_column not in table.c:
        return statement
    return statement.where(table.c[ingestion_id_column] == ingestion_id)


def _sample_lineage_from_first_duplicate(
    session: Any,
    *,
    table: sa.Table,
    dataset_config: DatasetCheckConfig,
    key_columns: tuple[str, ...],
    first_group: dict[str, Any] | None,
    ingestion_id: int | None,
) -> dict[str, Any]:
    """Resolve lineage hints for the first duplicate group.

    Args:
        session: SQLModel session.
        table: Reflected SQLAlchemy table.
        dataset_config: Dataset configuration.
        key_columns: Duplicate key columns.
        first_group: First duplicate group sample mapping.
        ingestion_id: Current ingestion scope id.

    Returns:
        Lineage payload with optional `source_id` and `lineage_ref_id`.
    """

    if not first_group:
        return {}
    source_column = dataset_config.source_id_column
    lineage_column = dataset_config.lineage_ref_id_column
    if source_column not in table.c and lineage_column not in table.c:
        return {}

    predicates = []
    for column_name in key_columns:
        if column_name not in table.c:
            continue
        predicates.append(table.c[column_name] == first_group.get(column_name))
    if not predicates:
        return {}

    select_cols: list[sa.Column] = []
    if source_column in table.c:
        select_cols.append(table.c[source_column])
    if lineage_column in table.c:
        select_cols.append(table.c[lineage_column])

    statement = select(*select_cols).select_from(table).where(sa.and_(*predicates)).limit(1)
    statement = _apply_scope_filters(
        statement,
        table=table,
        ingestion_id_column=dataset_config.ingestion_id_column,
        ingestion_id=ingestion_id,
    )
    row = session.exec(statement).first()
    if row is None:
        return {}

    payload = dict(row._mapping)  # noqa: SLF001
    lineage: dict[str, Any] = {}
    source_value = payload.get(source_column)
    if source_value is not None:
        lineage["source_id"] = source_value

    lineage_value = payload.get(lineage_column)
    try:
        if lineage_value is not None:
            parsed = int(lineage_value)
            if parsed > 0:
                lineage["lineage_ref_id"] = parsed
    except (TypeError, ValueError):
        pass
    return lineage


@dataclass(frozen=True)
class DuplicateCheckSpec:
    """One duplicate-check specification for a dataset key set.

    Args:
        dataset_config: Dataset-level configuration.
        key_columns: Columns used as duplicate key.
    """

    dataset_config: DatasetCheckConfig
    key_columns: tuple[str, ...]


class DuplicateCheck(Check):
    """Detect duplicate rows for one dataset using configured key columns."""

    def __init__(self, spec: DuplicateCheckSpec, *, sample_limit: int = 5) -> None:
        """Initialize duplicate-check instance.

        Args:
            spec: Duplicate-check spec with dataset and key columns.
            sample_limit: Maximum duplicate groups included in evidence sample.
        """

        if sample_limit <= 0:
            raise ValueError("sample_limit deve ser > 0.")
        self.spec = spec
        self.sample_limit = int(sample_limit)
        key_label = "_".join(spec.key_columns)
        self.check_id = f"dq.duplicates.{spec.dataset_config.dataset_id}.{key_label}"
        self.description = (
            "Detecta duplicidade por chave configurada para evitar inflar contagens."
        )

    def run(self, context: CheckContext) -> CheckResult:
        """Execute duplicate detection for one dataset key set.

        Args:
            context: Check execution context with DB session resource.

        Returns:
            Pass/fail check result with duplicate counts and sampled keys.
        """

        session = context.require_resource("session")
        engine = session.get_bind()
        inspector = sa.inspect(engine)
        dataset = self.spec.dataset_config
        table_name = dataset.table
        key_columns = self.spec.key_columns

        if table_name not in set(inspector.get_table_names()):
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=dataset.severity,
                message=(
                    "Tabela de dataset nao encontrada para check de duplicidade. "
                    "Como corrigir: validar migration e config no datasets.yml."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": dataset.dataset_id,
                    "domain": dataset.domain,
                    "table": table_name,
                    "key_columns": list(key_columns),
                    "missing_table": True,
                },
            )

        table = sa.Table(table_name, sa.MetaData(), autoload_with=engine)
        missing_columns = sorted(column for column in key_columns if column not in table.c)
        if missing_columns:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=dataset.severity,
                message=(
                    "Config de duplicidade referencia coluna inexistente. Como corrigir: "
                    "ajustar duplicate_key_sets no datasets.yml."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": dataset.dataset_id,
                    "table": table_name,
                    "key_columns": list(key_columns),
                    "missing_columns": missing_columns,
                },
            )

        group_columns = [table.c[column_name] for column_name in key_columns]
        non_null_predicates = [table.c[column_name].is_not(None) for column_name in key_columns]
        duplicate_count_label = "duplicate_count"
        duplicate_count_expr = sa.func.count().label(duplicate_count_label)

        grouped_stmt = (
            select(*group_columns, duplicate_count_expr)
            .select_from(table)
            .where(sa.and_(*non_null_predicates))
            .group_by(*group_columns)
            .having(sa.func.count() > 1)
        )
        grouped_stmt = _apply_scope_filters(
            grouped_stmt,
            table=table,
            ingestion_id_column=dataset.ingestion_id_column,
            ingestion_id=context.ingestion_id,
        )

        grouped_subquery = grouped_stmt.subquery()
        duplicate_group_count_stmt = select(sa.func.count()).select_from(grouped_subquery)
        duplicate_group_count = int(session.exec(duplicate_group_count_stmt).one() or 0)
        if duplicate_group_count <= 0:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message="Sem duplicidade para a chave configurada.",
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": dataset.dataset_id,
                    "domain": dataset.domain,
                    "table": table_name,
                    "key_columns": list(key_columns),
                    "duplicate_group_count": 0,
                    "duplicate_total_rows": 0,
                    "duplicate_excess_rows": 0,
                    "sample_duplicates": [],
                },
            )

        duplicate_total_rows_stmt = select(sa.func.sum(grouped_subquery.c[duplicate_count_label])).select_from(
            grouped_subquery
        )
        duplicate_total_rows = int(session.exec(duplicate_total_rows_stmt).one() or 0)
        duplicate_excess_rows = max(0, duplicate_total_rows - duplicate_group_count)

        sample_stmt = (
            select(*group_columns, duplicate_count_expr)
            .select_from(table)
            .where(sa.and_(*non_null_predicates))
            .group_by(*group_columns)
            .having(sa.func.count() > 1)
            .order_by(sa.desc(sa.func.count()))
            .limit(self.sample_limit)
        )
        sample_stmt = _apply_scope_filters(
            sample_stmt,
            table=table,
            ingestion_id_column=dataset.ingestion_id_column,
            ingestion_id=context.ingestion_id,
        )
        sample_rows = session.exec(sample_stmt).all()

        sample_duplicates: list[dict[str, Any]] = []
        for row in sample_rows:
            row_mapping = dict(row._mapping)  # noqa: SLF001
            sample_duplicates.append(row_mapping)

        first_group = sample_duplicates[0] if sample_duplicates else None
        lineage = _sample_lineage_from_first_duplicate(
            session,
            table=table,
            dataset_config=dataset,
            key_columns=key_columns,
            first_group=first_group,
            ingestion_id=context.ingestion_id,
        )

        return CheckResult(
            check_id=self.check_id,
            status=CheckStatus.FAIL,
            severity=dataset.severity,
            message=(
                "Duplicidade detectada para chave configurada. Como corrigir: revisar "
                "reimportacoes e regras de dedupe no extractor/loader."
            ),
            ingestion_id=context.ingestion_id,
            evidence={
                "dataset_id": dataset.dataset_id,
                "domain": dataset.domain,
                "table": table_name,
                "key_columns": list(key_columns),
                "duplicate_group_count": duplicate_group_count,
                "duplicate_total_rows": duplicate_total_rows,
                "duplicate_excess_rows": duplicate_excess_rows,
                "sample_limit": self.sample_limit,
                "sample_duplicates": sample_duplicates,
            },
            lineage=lineage,
        )


def build_duplicate_checks(
    configs: Sequence[DatasetCheckConfig],
    *,
    sample_limit: int = 5,
) -> tuple[DuplicateCheck, ...]:
    """Build duplicate checks from dataset configs.

    Args:
        configs: Dataset configs loaded from YAML.
        sample_limit: Maximum evidence samples per check result.

    Returns:
        Tuple of duplicate checks for configured duplicate key sets.
    """

    checks: list[DuplicateCheck] = []
    for config in configs:
        for key_set in config.duplicate_key_sets:
            checks.append(
                DuplicateCheck(
                    DuplicateCheckSpec(dataset_config=config, key_columns=key_set),
                    sample_limit=sample_limit,
                )
            )
    return tuple(checks)
