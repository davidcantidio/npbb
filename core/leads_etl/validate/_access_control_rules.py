"""Access-control reconciliation rules for the shared lead ETL core."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

import sqlalchemy as sa

from ._contracts import Check, CheckContext, CheckResult, CheckStatus, Severity


def _as_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _lineage_payload(row: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if row.get("source_id") is not None:
        payload["source_id"] = row.get("source_id")
    try:
        if row.get("lineage_ref_id") is not None and int(row["lineage_ref_id"]) > 0:
            payload["lineage_ref_id"] = int(row["lineage_ref_id"])
    except (TypeError, ValueError):
        pass
    return payload


@dataclass(frozen=True)
class AccessControlRuleFinding:
    """One reconciliation finding for a specific session row."""

    code: str
    session_id: int | None
    message: str
    source_id: str | None
    lineage_ref_id: int | None
    payload: dict[str, Any]


class AccessControlReconciliationCheck(Check):
    """Validate access-control reconciliation and percent bounds by session."""

    check_id = "dq.access_control.reconciliation"
    description = "Valida reconciliacao de validos/presentes/ausentes e bounds de comparecimento."

    def __init__(self, *, table_name: str = "attendance_access_control", ingestion_id_column: str = "ingestion_id", severity: Severity = Severity.ERROR, sample_limit: int = 10, pct_tolerance_fraction: Decimal = Decimal("0.01"), pct_tolerance_percent: Decimal = Decimal("1.0")) -> None:
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
        session = context.require_resource("session")
        inspector = sa.inspect(session.get_bind())
        if self._table_name not in set(inspector.get_table_names()):
            return CheckResult(check_id=self.check_id, status=CheckStatus.FAIL, severity=self._severity, message=("Tabela de controle de acesso nao encontrada. Como corrigir: validar migration/modelo canonical de attendance."), ingestion_id=context.ingestion_id, evidence={"table": self._table_name, "missing_table": True})

        table = sa.Table(self._table_name, sa.MetaData(), autoload_with=session.get_bind())
        required_columns = {"session_id", "source_id", "lineage_ref_id", "ingressos_validos", "presentes", "ausentes", "comparecimento_pct"}
        missing_columns = sorted(column for column in required_columns if column not in table.c)
        if missing_columns:
            return CheckResult(check_id=self.check_id, status=CheckStatus.FAIL, severity=self._severity, message=("Schema incompleto para reconciliacao de controle de acesso. Como corrigir: alinhar tabela attendance_access_control."), ingestion_id=context.ingestion_id, evidence={"table": self._table_name, "missing_columns": missing_columns})

        stmt = sa.select(table.c.session_id, table.c.source_id, table.c.lineage_ref_id, table.c.ingressos_validos, table.c.presentes, table.c.ausentes, table.c.comparecimento_pct).select_from(table)
        if context.ingestion_id is not None and self._ingestion_id_column in table.c:
            stmt = stmt.where(table.c[self._ingestion_id_column] == context.ingestion_id)
        rows = [dict(row) for row in session.execute(stmt).mappings().all()]
        if not rows:
            return CheckResult(check_id=self.check_id, status=CheckStatus.SKIP, severity=Severity.INFO, message="Check ignorado: nenhuma linha de controle de acesso no escopo.", ingestion_id=context.ingestion_id, evidence={"table": self._table_name, "scoped_rows": 0})

        findings: list[AccessControlRuleFinding] = []
        partial_rows = 0
        evaluated_rows = 0
        for row in rows:
            findings.extend(self._find_row_issues(row))
            if any(_as_decimal(row.get(field)) is not None for field in ("ingressos_validos", "presentes", "ausentes", "comparecimento_pct")):
                evaluated_rows += 1
            else:
                partial_rows += 1

        if findings:
            sample_payload = [{"code": item.code, "session_id": item.session_id, "source_id": item.source_id, "lineage_ref_id": item.lineage_ref_id, "message": item.message, "payload": item.payload} for item in findings[: self._sample_limit]]
            return CheckResult(check_id=self.check_id, status=CheckStatus.FAIL, severity=self._severity, message=("Inconsistencias de reconciliacao detectadas no controle de acesso. Como corrigir: revisar carga da sessao e fonte de acesso."), ingestion_id=context.ingestion_id, evidence={"table": self._table_name, "scoped_rows": len(rows), "evaluated_rows": evaluated_rows, "partial_rows": partial_rows, "finding_count": len(findings), "sample_limit": self._sample_limit, "findings_sample": sample_payload}, lineage=_lineage_payload(sample_payload[0]))

        if evaluated_rows == 0:
            return CheckResult(check_id=self.check_id, status=CheckStatus.SKIP, severity=Severity.INFO, message="Check ignorado: fonte parcial sem campos suficientes para reconciliar.", ingestion_id=context.ingestion_id, evidence={"table": self._table_name, "scoped_rows": len(rows), "evaluated_rows": 0, "partial_rows": partial_rows})
        return CheckResult(check_id=self.check_id, status=CheckStatus.PASS, severity=Severity.INFO, message="Reconciliacao de controle de acesso sem inconsistencias no escopo.", ingestion_id=context.ingestion_id, evidence={"table": self._table_name, "scoped_rows": len(rows), "evaluated_rows": evaluated_rows, "partial_rows": partial_rows, "finding_count": 0})

    def _find_row_issues(self, row: dict[str, Any]) -> list[AccessControlRuleFinding]:
        validos = _as_decimal(row.get("ingressos_validos"))
        presentes = _as_decimal(row.get("presentes"))
        ausentes = _as_decimal(row.get("ausentes"))
        comparecimento = _as_decimal(row.get("comparecimento_pct"))
        findings: list[AccessControlRuleFinding] = []
        if validos is not None and presentes is not None and presentes > validos:
            findings.append(self._finding(row, "PRESENTES_MAIOR_QUE_VALIDOS", "presentes maior que ingressos_validos.", {"ingressos_validos": str(validos), "presentes": str(presentes)}))
        if validos is not None and presentes is not None and ausentes is not None and presentes + ausentes != validos:
            findings.append(self._finding(row, "SOMA_PRESENTES_AUSENTES_DIVERGE_VALIDOS", "presentes + ausentes diverge de ingressos_validos.", {"ingressos_validos": str(validos), "presentes": str(presentes), "ausentes": str(ausentes)}))
        if comparecimento is not None:
            findings.extend(self._find_comparecimento_issues(row, validos, presentes, comparecimento))
        return findings

    def _find_comparecimento_issues(self, row: dict[str, Any], validos: Decimal | None, presentes: Decimal | None, comparecimento: Decimal) -> list[AccessControlRuleFinding]:
        if comparecimento < 0 or comparecimento > 100:
            return [self._finding(row, "COMPARECIMENTO_FORA_BOUNDS", "comparecimento_pct fora de bounds [0,100].", {"comparecimento_pct": str(comparecimento)})]
        if validos is None or presentes is None:
            return []
        if validos == 0 and presentes not in (None, Decimal("0")):
            return [self._finding(row, "VALIDOS_ZERO_PRESENTES_NAO_ZERO", "ingressos_validos = 0 com presentes nao zero.", {"ingressos_validos": str(validos), "presentes": str(presentes), "comparecimento_pct": str(comparecimento)})]
        if validos <= 0:
            return []
        expected_fraction = presentes / validos
        if comparecimento <= 1 and abs(comparecimento - expected_fraction) > self._pct_tolerance_fraction:
            return [self._finding(row, "COMPARECIMENTO_DIVERGE_BASE", "comparecimento_pct (fracao) diverge de presentes/validos.", {"comparecimento_pct": str(comparecimento), "esperado": str(expected_fraction)})]
        expected_percent = expected_fraction * Decimal("100")
        if comparecimento > 1 and abs(comparecimento - expected_percent) > self._pct_tolerance_percent:
            return [self._finding(row, "COMPARECIMENTO_DIVERGE_BASE", "comparecimento_pct (0-100) diverge de presentes/validos.", {"comparecimento_pct": str(comparecimento), "esperado": str(expected_percent)})]
        return []

    def _finding(self, row: dict[str, Any], code: str, message: str, payload: dict[str, Any]) -> AccessControlRuleFinding:
        return AccessControlRuleFinding(code=code, session_id=row.get("session_id"), message=message, source_id=row.get("source_id"), lineage_ref_id=row.get("lineage_ref_id"), payload=payload)

