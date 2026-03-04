"""Schema drift checks for the shared lead ETL core."""

from __future__ import annotations

import sqlalchemy as sa

from ._contracts import Check, CheckContext, CheckResult, CheckStatus, Severity
from ._dataset_config import DatasetCheckConfig


class SchemaCheck(Check):
    """Validate required columns for one dataset target table."""

    def __init__(self, dataset_config: DatasetCheckConfig) -> None:
        self.dataset_config = dataset_config
        self.check_id = f"dq.schema.{dataset_config.dataset_id}"
        self.description = "Valida schema esperado da tabela por dataset para detectar drift."

    def run(self, context: CheckContext) -> CheckResult:
        session = context.require_resource("session")
        inspector = sa.inspect(session.get_bind())
        table_name = self.dataset_config.table
        if table_name not in set(inspector.get_table_names()):
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self.dataset_config.severity,
                message=(
                    "Tabela de dataset nao encontrada. Como corrigir: "
                    "validar migration e nome da tabela no datasets.yml."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": self.dataset_config.dataset_id,
                    "domain": self.dataset_config.domain,
                    "table": table_name,
                    "missing_table": True,
                },
            )

        present_columns = {
            str(item["name"]).strip()
            for item in inspector.get_columns(table_name)
            if item.get("name") is not None
        }
        missing_columns = sorted(
            column for column in self.dataset_config.required_columns if column not in present_columns
        )
        if missing_columns:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self.dataset_config.severity,
                message=(
                    "Schema incompleto para dataset. Como corrigir: "
                    "alinhar migration/modelo com required_columns."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "dataset_id": self.dataset_config.dataset_id,
                    "domain": self.dataset_config.domain,
                    "table": table_name,
                    "missing_columns": missing_columns,
                    "required_columns": list(self.dataset_config.required_columns),
                },
            )
        return CheckResult(
            check_id=self.check_id,
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="Schema esperado encontrado para dataset.",
            ingestion_id=context.ingestion_id,
            evidence={
                "dataset_id": self.dataset_config.dataset_id,
                "domain": self.dataset_config.domain,
                "table": table_name,
                "required_columns_count": len(self.dataset_config.required_columns),
            },
        )


def build_schema_checks(configs: tuple[DatasetCheckConfig, ...]) -> tuple[SchemaCheck, ...]:
    """Build one `SchemaCheck` per dataset config."""

    return tuple(SchemaCheck(config) for config in configs)

