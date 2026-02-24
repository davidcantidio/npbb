"""Critical NULL checks driven by dataset YAML configuration.

This module implements `NotNullCheck`, which validates dataset critical key
columns and emits actionable findings with optional lineage hints.
"""

from __future__ import annotations

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
    """Apply ingestion scope filter when table has ingestion column.

    Args:
        statement: SQLAlchemy selectable statement.
        table: Reflected SQLAlchemy table object.
        ingestion_id_column: Configured ingestion id column name.
        ingestion_id: Optional ingestion id from check context.

    Returns:
        Statement with optional ingestion filter applied.
    """

    if ingestion_id is None:
        return statement
    if ingestion_id_column not in table.c:
        return statement
    return statement.where(table.c[ingestion_id_column] == ingestion_id)


def _extract_lineage_payload(
    row_mapping: dict[str, Any],
    *,
    source_id_column: str,
    lineage_ref_id_column: str,
) -> dict[str, Any]:
    """Extract lineage hints from one offending row mapping.

    Args:
        row_mapping: Dict-style row payload from one failing row.
        source_id_column: Configured source id column name.
        lineage_ref_id_column: Configured lineage ref column name.

    Returns:
        Lineage payload with optional `source_id` and `lineage_ref_id`.
    """

    lineage: dict[str, Any] = {}
    source_id = row_mapping.get(source_id_column)
    if source_id is not None:
        lineage["source_id"] = source_id

    lineage_ref_id = row_mapping.get(lineage_ref_id_column)
    try:
        if lineage_ref_id is not None:
            parsed = int(lineage_ref_id)
            if parsed > 0:
                lineage["lineage_ref_id"] = parsed
    except (TypeError, ValueError):
        pass
    return lineage


class NotNullCheck(Check):
    """Validate configured critical columns are not NULL for one dataset."""

    def __init__(self, dataset_config: DatasetCheckConfig) -> None:
        """Create one not-null check bound to dataset configuration.

        Args:
            dataset_config: Dataset check configuration loaded from YAML.
        """

        self.dataset_config = dataset_config
        self.check_id = f"dq.not_null.{dataset_config.dataset_id}"
        self.description = (
            "Valida nulos criticos em colunas-chave do dataset para detectar carga parcial."
        )

    def run(self, context: CheckContext) -> CheckResult:
        """Execute critical-null validation for one configured dataset table.

        Args:
            context: Check execution context with DB session resource.

        Returns:
            Pass/fail/skip check result with evidence and optional lineage hints.
        """

        if not self.dataset_config.critical_not_null_columns:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.SKIP,
                severity=Severity.INFO,
                message="Check ignorado: dataset sem critical_not_null_columns configuradas.",
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": self.dataset_config.dataset_id,
                    "table": self.dataset_config.table,
                },
            )

        session = context.require_resource("session")
        engine = session.get_bind()
        inspector = sa.inspect(engine)
        table_name = self.dataset_config.table

        if table_name not in set(inspector.get_table_names()):
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self.dataset_config.severity,
                message=(
                    "Tabela de dataset nao encontrada para check de nulos. Como corrigir: "
                    "validar migration e config no datasets.yml."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": self.dataset_config.dataset_id,
                    "domain": self.dataset_config.domain,
                    "table": table_name,
                    "missing_table": True,
                },
            )

        table = sa.Table(table_name, sa.MetaData(), autoload_with=engine)
        available_columns = set(table.c.keys())
        missing_columns = sorted(
            col for col in self.dataset_config.critical_not_null_columns if col not in available_columns
        )
        if missing_columns:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self.dataset_config.severity,
                message=(
                    "Config de nulos referencia coluna inexistente. Como corrigir: "
                    "ajustar datasets.yml ou schema da tabela."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": self.dataset_config.dataset_id,
                    "table": table_name,
                    "missing_columns": missing_columns,
                    "critical_not_null_columns": list(self.dataset_config.critical_not_null_columns),
                },
            )

        scoped_total_stmt = _apply_scope_filters(
            select(sa.func.count()).select_from(table),
            table=table,
            ingestion_id_column=self.dataset_config.ingestion_id_column,
            ingestion_id=context.ingestion_id,
        )
        scoped_total = int(session.exec(scoped_total_stmt).one() or 0)
        if scoped_total <= 0:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.SKIP,
                severity=Severity.INFO,
                message=(
                    "Check ignorado: sem linhas no escopo atual para avaliar nulos criticos."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": self.dataset_config.dataset_id,
                    "table": table_name,
                    "scoped_total_rows": scoped_total,
                },
            )

        null_predicate = sa.or_(
            *[table.c[column_name].is_(None) for column_name in self.dataset_config.critical_not_null_columns]
        )
        null_count_stmt = _apply_scope_filters(
            select(sa.func.count()).select_from(table).where(null_predicate),
            table=table,
            ingestion_id_column=self.dataset_config.ingestion_id_column,
            ingestion_id=context.ingestion_id,
        )
        null_count = int(session.exec(null_count_stmt).one() or 0)
        if null_count <= 0:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message="Sem nulos criticos no dataset para o escopo analisado.",
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": self.dataset_config.dataset_id,
                    "domain": self.dataset_config.domain,
                    "table": table_name,
                    "scoped_total_rows": scoped_total,
                    "null_critical_rows": 0,
                },
            )

        sample_columns: list[sa.Column] = []
        if self.dataset_config.source_id_column in table.c:
            sample_columns.append(table.c[self.dataset_config.source_id_column])
        if self.dataset_config.lineage_ref_id_column in table.c:
            sample_columns.append(table.c[self.dataset_config.lineage_ref_id_column])
        for column_name in self.dataset_config.critical_not_null_columns:
            sample_columns.append(table.c[column_name])

        sample_stmt = _apply_scope_filters(
            select(*sample_columns).select_from(table).where(null_predicate).limit(1),
            table=table,
            ingestion_id_column=self.dataset_config.ingestion_id_column,
            ingestion_id=context.ingestion_id,
        )
        sample_row = session.exec(sample_stmt).first()
        sample_mapping: dict[str, Any] = {}
        if sample_row is not None:
            sample_mapping = dict(sample_row._mapping)  # noqa: SLF001

        return CheckResult(
            check_id=self.check_id,
            status=CheckStatus.FAIL,
            severity=self.dataset_config.severity,
            message=(
                "Nulos criticos detectados no dataset. Como corrigir: revisar extractor/loader "
                "e validar campos-chave antes de promover para marts."
            ),
            ingestion_id=context.ingestion_id,
            evidence={
                "dataset_id": self.dataset_config.dataset_id,
                "domain": self.dataset_config.domain,
                "table": table_name,
                "scoped_total_rows": scoped_total,
                "null_critical_rows": null_count,
                "critical_not_null_columns": list(self.dataset_config.critical_not_null_columns),
                "sample_row": sample_mapping,
            },
            lineage=_extract_lineage_payload(
                sample_mapping,
                source_id_column=self.dataset_config.source_id_column,
                lineage_ref_id_column=self.dataset_config.lineage_ref_id_column,
            ),
        )


def build_not_null_checks(configs: Sequence[DatasetCheckConfig]) -> tuple[NotNullCheck, ...]:
    """Build one `NotNullCheck` per dataset config.

    Args:
        configs: Dataset check configs loaded from YAML.

    Returns:
        Tuple of critical-not-null checks preserving config order.
    """

    return tuple(NotNullCheck(config) for config in configs)
