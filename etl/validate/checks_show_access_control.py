"""Show-coverage check focused on missing night access-control datasets.

This check prevents silent omission of expected show days by asserting that
`access_control` exists for each expected `NOTURNO_SHOW` session.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from .coverage_contract import DEFAULT_COVERAGE_CONTRACT_PATH
from .framework import Check, CheckContext, CheckResult, CheckStatus, Severity
from .show_coverage_evaluator import (
    CoverageMissingInput,
    evaluate_coverage,
    find_show_access_control_missing_inputs,
)
from ..transform.agenda_loader import AgendaMaster, AgendaMasterError, load_agenda_master

try:  # pragma: no cover - import style depends on caller cwd
    from app.models.models import EventSessionType
except ModuleNotFoundError:  # pragma: no cover
    from pathlib import Path as _Path
    import sys as _sys

    BACKEND_ROOT = _Path(__file__).resolve().parents[2] / "backend"
    if str(BACKEND_ROOT) not in _sys.path:
        _sys.path.insert(0, str(BACKEND_ROOT))
    from app.models.models import EventSessionType


_DEFAULT_FOCUS_SHOW_DATES: tuple[date, ...] = (
    date(2025, 12, 12),
    date(2025, 12, 14),
)


@dataclass(frozen=True)
class ShowAccessControlFinding:
    """One finding emitted by `MissingShowAccessControlCheck`."""

    session_key: str
    session_date: date
    status: str
    reason_code: str
    reason: str
    expected_artifact: str
    recommended_action: str
    critical_reason: str
    source_hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize finding into JSON-friendly dictionary."""

        payload = {
            "session_key": self.session_key,
            "session_date": self.session_date.isoformat(),
            "status": self.status,
            "reason_code": self.reason_code,
            "reason": self.reason,
            "expected_artifact": self.expected_artifact,
            "recommended_action": self.recommended_action,
            "critical_reason": self.critical_reason,
        }
        if self.source_hint:
            payload["source_hint"] = self.source_hint
        return payload


def _normalize_focus_dates(focus_dates: Iterable[date] | None) -> tuple[date, ...]:
    """Normalize optional focus-date filter."""

    if focus_dates is None:
        return ()
    return tuple(sorted({item for item in focus_dates}))


def _expected_show_days_from_agenda(
    agenda: AgendaMaster,
    *,
    event_id: int | None,
    focus_dates: tuple[date, ...],
) -> tuple[tuple[date, str | None], ...]:
    """Return expected show sessions from agenda filtered by event/date."""

    selected: list[tuple[date, str | None]] = []
    focus_set = set(focus_dates)
    for session in agenda.sessions:
        if session.session_type.value != "noturno_show":
            continue
        if event_id is not None and int(session.event_id) != int(event_id):
            continue
        if focus_set and session.session_date not in focus_set:
            continue
        selected.append((session.session_date, session.session_key))
    return tuple(sorted(selected, key=lambda item: (item[0], item[1] or "")))


def _coverage_missing_item_to_finding(item: CoverageMissingInput) -> ShowAccessControlFinding:
    """Convert one coverage missing-input item into check finding contract."""

    source_hint = ", ".join(item.sources_considered) if item.sources_considered else None
    return ShowAccessControlFinding(
        session_key=item.session_key,
        session_date=item.session_date,
        status=item.status,
        reason_code=item.reason_code,
        reason=item.reason,
        expected_artifact=item.expected_artifact,
        recommended_action=item.request_action,
        critical_reason=(
            "Controle de acesso noturno e fonte oficial de entradas validadas do show; "
            "sem ele, o fechamento por dia pode omitir ou distorcer comparecimento."
        ),
        source_hint=source_hint,
    )


class MissingShowAccessControlCheck(Check):
    """Detect expected show days without usable access-control coverage."""

    check_id = "dq.show_coverage.missing_access_control"
    description = (
        "Sinaliza ausencia critica de controle de acesso em sessoes NOTURNO_SHOW esperadas."
    )

    def __init__(
        self,
        *,
        event_id: int | None = None,
        agenda_path: Path | str | None = None,
        contract_path: Path | str = DEFAULT_COVERAGE_CONTRACT_PATH,
        focus_show_dates: Iterable[date] | None = _DEFAULT_FOCUS_SHOW_DATES,
        severity: Severity = Severity.ERROR,
        sample_limit: int = 10,
        include_partial_as_gap: bool = True,
    ) -> None:
        """Initialize show access-control coverage check.

        Args:
            event_id: Optional event filter for coverage evaluation.
            agenda_path: Optional agenda-master path to enforce expected sessions.
            contract_path: Coverage contract path used by evaluator.
            focus_show_dates: Optional explicit day focus (defaults: 12/12 and 14/12).
            severity: Severity for failing findings.
            sample_limit: Maximum sample findings in evidence payload.
            include_partial_as_gap: Treat partial access coverage as critical finding.

        Raises:
            ValueError: If sample limit is invalid.
        """

        if sample_limit <= 0:
            raise ValueError("sample_limit deve ser maior que zero.")
        self._event_id = event_id
        self._agenda_path = Path(agenda_path) if agenda_path is not None else None
        self._contract_path = contract_path
        self._focus_show_dates = _normalize_focus_dates(focus_show_dates)
        self._severity = severity
        self._sample_limit = int(sample_limit)
        self._include_partial_as_gap = bool(include_partial_as_gap)

    def run(self, context: CheckContext) -> CheckResult:
        """Execute check for missing show-day access-control coverage.

        Args:
            context: Check context with SQL session resource.

        Returns:
            Pass/fail check result with actionable findings.
        """

        session = context.require_resource("session")
        scoped_event_id = self._event_id
        if scoped_event_id is None:
            metadata_event = context.metadata.get("event_id")
            if isinstance(metadata_event, int):
                scoped_event_id = metadata_event

        report = evaluate_coverage(
            session,
            event_id=scoped_event_id,
            contract_path=self._contract_path,
        )

        findings: list[ShowAccessControlFinding] = []
        findings.extend(
            _coverage_missing_item_to_finding(item)
            for item in find_show_access_control_missing_inputs(
                report,
                include_partial=self._include_partial_as_gap,
                focus_dates=self._focus_show_dates,
            )
        )

        agenda_expected: tuple[tuple[date, str | None], ...] = ()
        if self._agenda_path is not None:
            try:
                agenda = load_agenda_master(self._agenda_path)
            except (FileNotFoundError, AgendaMasterError) as exc:
                return CheckResult(
                    check_id=self.check_id,
                    status=CheckStatus.FAIL,
                    severity=self._severity,
                    message=(
                        "Falha ao carregar agenda master para check de shows. Como corrigir: "
                        "validar caminho e schema da agenda."
                    ),
                    ingestion_id=context.ingestion_id,
                    evidence={
                        "agenda_path": str(self._agenda_path),
                        "error": str(exc),
                    },
                )

            agenda_expected = _expected_show_days_from_agenda(
                agenda,
                event_id=scoped_event_id,
                focus_dates=self._focus_show_dates,
            )
            report_show_keys = {
                (row.session_date, row.session_key)
                for row in report.sessions
                if row.session_type == EventSessionType.NOTURNO_SHOW
            }
            existing_missing_keys = {(item.session_date, item.session_key) for item in findings}

            for expected_date, expected_key in agenda_expected:
                candidate = (expected_date, expected_key or "")
                matched = False
                if expected_key:
                    matched = candidate in report_show_keys
                else:
                    matched = any(day == expected_date for day, _ in report_show_keys)
                if matched:
                    continue

                session_key = expected_key or f"SHOW_{expected_date.isoformat()}"
                if (expected_date, session_key) in existing_missing_keys:
                    continue
                findings.append(
                    ShowAccessControlFinding(
                        session_key=session_key,
                        session_date=expected_date,
                        status="gap",
                        reason_code="missing_show_session_in_event_sessions",
                        reason=(
                            "Sessao de show esperada na agenda nao foi encontrada em event_sessions."
                        ),
                        expected_artifact=(
                            "PDF de controle de acesso da sessao de show "
                            "com ingressos_validos/presentes/ausentes."
                        ),
                        recommended_action=(
                            "Solicitar/atualizar agenda master oficial e PDF de controle de acesso "
                            "do show para o dia informado."
                        ),
                        critical_reason=(
                            "Sem sessao esperada no catalogo, o fechamento pode omitir o dia de show "
                            "inteiro (bug de cobertura por dia)."
                        ),
                    )
                )

        if not findings:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message=(
                    "Cobertura de controle de acesso para shows esperados esta completa "
                    "no recorte analisado."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "event_id": scoped_event_id,
                    "focus_show_dates": [item.isoformat() for item in self._focus_show_dates],
                    "agenda_expected_show_days": [
                        {
                            "session_date": item[0].isoformat(),
                            "session_key": item[1],
                        }
                        for item in agenda_expected
                    ],
                    "finding_count": 0,
                },
            )

        sample = [item.to_dict() for item in findings[: self._sample_limit]]
        lineage_payload: dict[str, Any] = {}
        for item in findings:
            if item.source_hint:
                lineage_payload["source_id"] = item.source_hint.split(",")[0].strip()
                break

        return CheckResult(
            check_id=self.check_id,
            status=CheckStatus.FAIL,
            severity=self._severity,
            message=(
                "GAP critico de controle de acesso em show esperado. Como corrigir: "
                "solicitar PDF/relatorio oficial de acesso noturno e rerodar extractor."
            ),
            ingestion_id=context.ingestion_id,
            evidence={
                "event_id": scoped_event_id,
                "focus_show_dates": [item.isoformat() for item in self._focus_show_dates],
                "agenda_path": str(self._agenda_path) if self._agenda_path is not None else None,
                "finding_count": len(findings),
                "findings_sample": sample,
            },
            lineage=lineage_payload,
        )

