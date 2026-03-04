"""Runner and rendering helpers for core lead ETL validation."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Iterable, Sequence

from ._contracts import Check, CheckContext, CheckReport, CheckResult, CheckStatus, Severity
from ._framework_persistence import persist_check_results


def _severity_rank(value: Severity) -> int:
    """Return comparable integer rank for severity values."""

    order = {Severity.INFO: 1, Severity.WARNING: 2, Severity.ERROR: 3}
    return order[value]


def _normalize_check_output(
    check_output: CheckResult | Sequence[CheckResult],
) -> list[CheckResult]:
    """Normalize one check output into a list of `CheckResult`."""

    if isinstance(check_output, CheckResult):
        return [check_output]
    return list(check_output)


def _build_summary(results: Sequence[CheckResult]) -> dict[str, int]:
    """Aggregate result counts by status and severity."""

    summary = {"total": len(results), "pass": 0, "fail": 0, "skip": 0, "info": 0, "warning": 0, "error": 0}
    for result in results:
        summary[result.status.value] += 1
        summary[result.severity.value] += 1
    return summary


def _compute_exit_code(results: Sequence[CheckResult], fail_on: Severity | None) -> int:
    """Compute gate-friendly exit code from results and severity threshold."""

    if fail_on is None:
        return 0
    threshold = _severity_rank(fail_on)
    for result in results:
        if result.status == CheckStatus.FAIL and _severity_rank(result.severity) >= threshold:
            return 1
    return 0


class CheckRunner:
    """Execute a list of checks and generate one consolidated report."""

    def __init__(
        self,
        checks: Iterable[Check],
        *,
        fail_on: Severity | None = Severity.ERROR,
        persist_results: bool = False,
        replace_existing_results: bool = True,
        default_source_id: str | None = None,
    ) -> None:
        self._checks = tuple(checks)
        self._fail_on = fail_on
        self._persist_results = persist_results
        self._replace_existing_results = replace_existing_results
        self._default_source_id = default_source_id

    def run(self, context: CheckContext) -> CheckReport:
        """Run configured checks and return one report."""

        collected: list[CheckResult] = []
        for check in self._checks:
            try:
                for result in _normalize_check_output(check.run(context)):
                    if result.ingestion_id is None:
                        result.ingestion_id = context.ingestion_id
                    collected.append(result)
            except Exception as exc:  # pragma: no cover
                collected.append(
                    CheckResult(
                        check_id=getattr(check, "check_id", check.__class__.__name__),
                        status=CheckStatus.FAIL,
                        severity=Severity.ERROR,
                        message=(
                            "Falha inesperada ao executar check. Como corrigir: "
                            "revisar stacktrace e tratamento de excecao do check."
                        ),
                        ingestion_id=context.ingestion_id,
                        evidence={"exception_type": type(exc).__name__, "exception_message": str(exc)},
                    )
                )

        if self._persist_results:
            try:
                persisted_count = persist_check_results(
                    context.require_resource("session"),
                    ingestion_id=context.ingestion_id,
                    results=collected,
                    replace_existing=self._replace_existing_results,
                    default_source_id=self._default_source_id,
                )
                context.metadata["dq_persisted_count"] = persisted_count
            except Exception as exc:
                collected.append(
                    CheckResult(
                        check_id="dq.persist_results",
                        status=CheckStatus.FAIL,
                        severity=Severity.ERROR,
                        message=(
                            "Falha ao persistir resultados de DQ. Como corrigir: "
                            "validar tabela dq_check_result e sessao de banco."
                        ),
                        ingestion_id=context.ingestion_id,
                        evidence={"exception_type": type(exc).__name__, "exception_message": str(exc)},
                    )
                )

        return CheckReport(
            ingestion_id=context.ingestion_id,
            generated_at=datetime.now(timezone.utc),
            fail_on=self._fail_on,
            exit_code=_compute_exit_code(collected, self._fail_on),
            summary=_build_summary(collected),
            results=tuple(collected),
        )


def render_report_json(report: CheckReport) -> str:
    """Render a report in JSON format."""

    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n"


def render_report_markdown(report: CheckReport) -> str:
    """Render a report in Markdown format."""

    lines = [
        "# Data Quality Report",
        "",
        f"- ingestion_id: {report.ingestion_id}",
        f"- generated_at: {report.generated_at.isoformat()}",
        f"- fail_on: {report.fail_on.value if report.fail_on else 'none'}",
        f"- exit_code: {report.exit_code}",
        f"- total: {report.summary.get('total', 0)}",
        f"- pass: {report.summary.get('pass', 0)}",
        f"- fail: {report.summary.get('fail', 0)}",
        f"- skip: {report.summary.get('skip', 0)}",
        "",
        "| check_id | status | severity | message | evidence | lineage |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for result in report.results:
        evidence_text = json.dumps(result.evidence, ensure_ascii=False, sort_keys=True)
        lineage_text = json.dumps(result.lineage, ensure_ascii=False, sort_keys=True)
        lines.append(
            "| "
            + " | ".join(
                [
                    result.check_id,
                    result.status.value,
                    result.severity.value,
                    result.message.replace("|", "\\|"),
                    evidence_text.replace("|", "\\|"),
                    lineage_text.replace("|", "\\|"),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def parse_fail_on(value: str) -> Severity | None:
    """Parse CLI fail-on option to severity threshold."""

    normalized = str(value or "").strip().lower()
    if normalized == "none":
        return None
    try:
        return Severity(normalized)
    except ValueError as exc:
        raise ValueError(
            "Valor invalido para fail_on. Como corrigir: usar info|warning|error|none."
        ) from exc

