"""Reconciliation checks for attendance access-control facts.

This module validates internal consistency of access-control fields used by
report metrics:
- validos vs presentes/ausentes
- comparecimento bounds and consistency with base values.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

import sqlalchemy as sa
from sqlmodel import select

from .framework import Check, CheckContext, CheckResult, CheckStatus, Severity


def _as_decimal(value: Any) -> Decimal | None:
    """Convert numeric-like value to `Decimal`.

    Args:
        value: Source value from database row.

    Returns:
        Parsed decimal or `None` when value is null/unparseable.
    """

    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _lineage_payload(row: dict[str, Any]) -> dict[str, Any]:
    """Build lineage payload with optional source and lineage reference.

    Args:
        row: Row mapping containing optional source/lineage keys.

    Returns:
        Lineage payload for check findings.
    """

    payload: dict[str, Any] = {}
    source_id = row.get("source_id")
    if source_id is not None:
        payload["source_id"] = source_id

    lineage_ref_id = row.get("lineage_ref_id")
    try:
        if lineage_ref_id is not None:
            parsed = int(lineage_ref_id)
            if parsed > 0:
                payload["lineage_ref_id"] = parsed
    except (TypeError, ValueError):
        pass
    return payload


@dataclass(frozen=True)
class AccessControlRuleFinding:
    """One reconciliation finding for a specific session row.

    Args:
        code: Stable finding code.
        session_id: Related session id when available.
        message: Actionable finding description.
        source_id: Optional source id associated to row.
        lineage_ref_id: Optional lineage reference id.
        payload: Extra numeric details for debugging.
    """

    code: str
    session_id: int | None
    message: str
    source_id: str | None
    lineage_ref_id: int | None
    payload: dict[str, Any]


class AccessControlReconciliationCheck(Check):
    """Validate access-control reconciliation and percent bounds by session."""

    check_id = "dq.access_control.reconciliation"
    description = (
        "Valida reconciliacao de validos/presentes/ausentes e bounds de comparecimento."
    )

    def __init__(
        self,
        *,
        table_name: str = "attendance_access_control",
        ingestion_id_column: str = "ingestion_id",
        severity: Severity = Severity.ERROR,
        sample_limit: int = 10,
        pct_tolerance_fraction: Decimal = Decimal("0.01"),
        pct_tolerance_percent: Decimal = Decimal("1.0"),
    ) -> None:
        """Initialize access-control reconciliation check.

        Args:
            table_name: Target table name for access-control facts.
            ingestion_id_column: Column used to scope rows by ingestion id.
            severity: Severity used when inconsistencies are found.
            sample_limit: Maximum inconsistent sessions included in evidence sample.
            pct_tolerance_fraction: Tolerance for comparecimento values in [0, 1].
            pct_tolerance_percent: Tolerance for comparecimento values in (1, 100].

        Raises:
            ValueError: If sample limit or tolerances are invalid.
        """

        if sample_limit <= 0:
            raise ValueError("sample_limit deve ser maior que zero.")
        if pct_tolerance_fraction < 0 or pct_tolerance_percent < 0:
            raise ValueError("Tolerancias de percentual nao podem ser negativas.")

        self._table_name = table_name
        self._ingestion_id_column = ingestion_id_column
        self._severity = severity
        self._sample_limit = int(sample_limit)
        self._pct_tolerance_fraction = pct_tolerance_fraction
        self._pct_tolerance_percent = pct_tolerance_percent

    def run(self, context: CheckContext) -> CheckResult:
        """Execute reconciliation rules for access-control rows.

        Args:
            context: Check context with DB session and optional ingestion scope.

        Returns:
            One pass/fail/skip result summarizing reconciliation findings.
        """

        session = context.require_resource("session")
        engine = session.get_bind()
        inspector = sa.inspect(engine)
        if self._table_name not in set(inspector.get_table_names()):
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self._severity,
                message=(
                    "Tabela de controle de acesso nao encontrada. Como corrigir: "
                    "validar migration/modelo canonical de attendance."
                ),
                ingestion_id=context.ingestion_id,
                evidence={"table": self._table_name, "missing_table": True},
            )

        table = sa.Table(self._table_name, sa.MetaData(), autoload_with=engine)
        required_columns = {
            "session_id",
            "source_id",
            "lineage_ref_id",
            "ingressos_validos",
            "presentes",
            "ausentes",
            "comparecimento_pct",
        }
        missing_columns = sorted(column for column in required_columns if column not in table.c)
        if missing_columns:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self._severity,
                message=(
                    "Schema incompleto para reconciliacao de controle de acesso. Como corrigir: "
                    "alinhar tabela attendance_access_control."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "table": self._table_name,
                    "missing_columns": missing_columns,
                },
            )

        stmt = select(
            table.c.session_id,
            table.c.source_id,
            table.c.lineage_ref_id,
            table.c.ingressos_validos,
            table.c.presentes,
            table.c.ausentes,
            table.c.comparecimento_pct,
        ).select_from(table)
        if context.ingestion_id is not None and self._ingestion_id_column in table.c:
            stmt = stmt.where(table.c[self._ingestion_id_column] == context.ingestion_id)
        rows = [dict(row._mapping) for row in session.exec(stmt).all()]  # noqa: SLF001
        if not rows:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.SKIP,
                severity=Severity.INFO,
                message="Check ignorado: nenhuma linha de controle de acesso no escopo.",
                ingestion_id=context.ingestion_id,
                evidence={"table": self._table_name, "scoped_rows": 0},
            )

        findings: list[AccessControlRuleFinding] = []
        partial_rows = 0
        evaluated_rows = 0

        for row in rows:
            validos = _as_decimal(row.get("ingressos_validos"))
            presentes = _as_decimal(row.get("presentes"))
            ausentes = _as_decimal(row.get("ausentes"))
            comparecimento = _as_decimal(row.get("comparecimento_pct"))

            row_evaluated = False

            if validos is not None and presentes is not None:
                row_evaluated = True
                if presentes > validos:
                    findings.append(
                        AccessControlRuleFinding(
                            code="PRESENTES_MAIOR_QUE_VALIDOS",
                            session_id=row.get("session_id"),
                            source_id=row.get("source_id"),
                            lineage_ref_id=row.get("lineage_ref_id"),
                            message="presentes maior que ingressos_validos.",
                            payload={
                                "ingressos_validos": str(validos),
                                "presentes": str(presentes),
                            },
                        )
                    )

            if validos is not None and presentes is not None and ausentes is not None:
                row_evaluated = True
                if presentes + ausentes != validos:
                    findings.append(
                        AccessControlRuleFinding(
                            code="SOMA_PRESENTES_AUSENTES_DIVERGE_VALIDOS",
                            session_id=row.get("session_id"),
                            source_id=row.get("source_id"),
                            lineage_ref_id=row.get("lineage_ref_id"),
                            message="presentes + ausentes diverge de ingressos_validos.",
                            payload={
                                "ingressos_validos": str(validos),
                                "presentes": str(presentes),
                                "ausentes": str(ausentes),
                            },
                        )
                    )

            if comparecimento is not None:
                row_evaluated = True
                if comparecimento < 0 or comparecimento > 100:
                    findings.append(
                        AccessControlRuleFinding(
                            code="COMPARECIMENTO_FORA_BOUNDS",
                            session_id=row.get("session_id"),
                            source_id=row.get("source_id"),
                            lineage_ref_id=row.get("lineage_ref_id"),
                            message="comparecimento_pct fora de bounds [0,100].",
                            payload={"comparecimento_pct": str(comparecimento)},
                        )
                    )
                elif validos is not None and presentes is not None:
                    if validos > 0:
                        expected_fraction = presentes / validos
                        if comparecimento <= 1:
                            if abs(comparecimento - expected_fraction) > self._pct_tolerance_fraction:
                                findings.append(
                                    AccessControlRuleFinding(
                                        code="COMPARECIMENTO_DIVERGE_BASE",
                                        session_id=row.get("session_id"),
                                        source_id=row.get("source_id"),
                                        lineage_ref_id=row.get("lineage_ref_id"),
                                        message=(
                                            "comparecimento_pct (fracao) diverge de presentes/validos."
                                        ),
                                        payload={
                                            "comparecimento_pct": str(comparecimento),
                                            "esperado": str(expected_fraction),
                                        },
                                    )
                                )
                        else:
                            expected_percent = expected_fraction * Decimal("100")
                            if abs(comparecimento - expected_percent) > self._pct_tolerance_percent:
                                findings.append(
                                    AccessControlRuleFinding(
                                        code="COMPARECIMENTO_DIVERGE_BASE",
                                        session_id=row.get("session_id"),
                                        source_id=row.get("source_id"),
                                        lineage_ref_id=row.get("lineage_ref_id"),
                                        message=(
                                            "comparecimento_pct (0-100) diverge de presentes/validos."
                                        ),
                                        payload={
                                            "comparecimento_pct": str(comparecimento),
                                            "esperado": str(expected_percent),
                                        },
                                    )
                                )
                    elif validos == 0 and presentes not in (None, Decimal("0")):
                        findings.append(
                            AccessControlRuleFinding(
                                code="VALIDOS_ZERO_PRESENTES_NAO_ZERO",
                                session_id=row.get("session_id"),
                                source_id=row.get("source_id"),
                                lineage_ref_id=row.get("lineage_ref_id"),
                                message="ingressos_validos = 0 com presentes nao zero.",
                                payload={
                                    "ingressos_validos": str(validos),
                                    "presentes": str(presentes),
                                    "comparecimento_pct": str(comparecimento),
                                },
                            )
                        )

            if row_evaluated:
                evaluated_rows += 1
            else:
                partial_rows += 1

        if findings:
            sampled = findings[: self._sample_limit]
            sample_payload = [
                {
                    "code": item.code,
                    "session_id": item.session_id,
                    "source_id": item.source_id,
                    "lineage_ref_id": item.lineage_ref_id,
                    "message": item.message,
                    "payload": item.payload,
                }
                for item in sampled
            ]
            first_lineage = _lineage_payload(sample_payload[0]) if sample_payload else {}
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=self._severity,
                message=(
                    "Inconsistencias de reconciliacao detectadas no controle de acesso. "
                    "Como corrigir: revisar carga da sessao e fonte de acesso."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "table": self._table_name,
                    "scoped_rows": len(rows),
                    "evaluated_rows": evaluated_rows,
                    "partial_rows": partial_rows,
                    "finding_count": len(findings),
                    "sample_limit": self._sample_limit,
                    "findings_sample": sample_payload,
                },
                lineage=first_lineage,
            )

        if evaluated_rows == 0:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.SKIP,
                severity=Severity.INFO,
                message=(
                    "Check ignorado: fonte parcial sem campos suficientes para reconciliar."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "table": self._table_name,
                    "scoped_rows": len(rows),
                    "evaluated_rows": 0,
                    "partial_rows": partial_rows,
                },
            )

        return CheckResult(
            check_id=self.check_id,
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="Reconciliacao de controle de acesso sem inconsistencias no escopo.",
            ingestion_id=context.ingestion_id,
            evidence={
                "table": self._table_name,
                "scoped_rows": len(rows),
                "evaluated_rows": evaluated_rows,
                "partial_rows": partial_rows,
                "finding_count": 0,
            },
        )
