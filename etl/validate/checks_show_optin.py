"""Show-coverage check focused on missing night opt-in datasets.

This check prevents silent omission of expected show days by asserting opt-in
coverage for `NOTURNO_SHOW` sessions. Severity depends on contract semantics:
- required show opt-in: critical finding (`error`);
- optional show opt-in: warning finding (`warning`).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from .coverage_contract import (
    DEFAULT_COVERAGE_CONTRACT_PATH,
    CoverageContractError,
    DatasetCoverageRule,
    load_coverage_contract,
)
from .coverage_matrix import CoverageRequirementsConfig, build_coverage_matrix
from .framework import Check, CheckContext, CheckResult, CheckStatus, Severity
from .show_coverage_evaluator import (
    CoverageMissingInput,
    evaluate_coverage,
    find_show_optin_missing_inputs,
)
from ..transform.agenda_loader import AgendaMaster, AgendaMasterError, load_agenda_master

try:  # pragma: no cover - import style depends on caller cwd
    from app.models.etl_registry import CoverageDataset, IngestionStatus
    from app.models.models import EventSessionType
    from app.services.etl_coverage_queries import (
        SessionDatasetSourceCandidate,
        build_session_dataset_source_candidates,
    )
except ModuleNotFoundError:  # pragma: no cover
    from pathlib import Path as _Path
    import sys as _sys

    BACKEND_ROOT = _Path(__file__).resolve().parents[2] / "backend"
    if str(BACKEND_ROOT) not in _sys.path:
        _sys.path.insert(0, str(BACKEND_ROOT))
    from app.models.etl_registry import CoverageDataset, IngestionStatus
    from app.models.models import EventSessionType
    from app.services.etl_coverage_queries import (
        SessionDatasetSourceCandidate,
        build_session_dataset_source_candidates,
    )


_DEFAULT_FOCUS_SHOW_DATES: tuple[date, ...] = (
    date(2025, 12, 12),
    date(2025, 12, 14),
)


@dataclass(frozen=True)
class ShowOptInFinding:
    """One finding emitted by `MissingShowOptInCheck`."""

    session_key: str
    session_date: date
    status: str
    severity: Severity
    required_by_contract: bool
    reason_code: str
    reason: str
    expected_artifact: str
    expected_filename_pattern: str
    recommended_action: str
    methodological_note: str
    source_hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize finding into JSON-friendly dictionary."""

        payload = {
            "session_key": self.session_key,
            "session_date": self.session_date.isoformat(),
            "status": self.status,
            "severity": self.severity.value,
            "required_by_contract": self.required_by_contract,
            "reason_code": self.reason_code,
            "reason": self.reason,
            "expected_artifact": self.expected_artifact,
            "expected_filename_pattern": self.expected_filename_pattern,
            "recommended_action": self.recommended_action,
            "methodological_note": self.methodological_note,
        }
        if self.source_hint:
            payload["source_hint"] = self.source_hint
        return payload


def _severity_rank(value: Severity) -> int:
    """Return comparable integer rank for severity values."""

    if value == Severity.ERROR:
        return 3
    if value == Severity.WARNING:
        return 2
    return 1


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


def _expected_optin_artifact(session_type: EventSessionType) -> str:
    """Return expected opt-in artifact description for one session type."""

    show_hint = " da sessao de show" if session_type == EventSessionType.NOTURNO_SHOW else ""
    return f"XLSX de opt-in/Eventim{show_hint} em granularidade transacional."


def _expected_filename_pattern(session_date: date) -> str:
    """Return deterministic expected filename pattern by session day."""

    return f"*OPTIN*{session_date.strftime('%Y%m%d')}*SHOW*.xlsx"


def _resolve_show_optin_rule(contract: Any) -> DatasetCoverageRule:
    """Resolve show-session opt-in rule from coverage contract."""

    show_contract = contract.session_types.get(EventSessionType.NOTURNO_SHOW)
    if show_contract is not None:
        for rule in show_contract.datasets:
            if rule.dataset == CoverageDataset.OPTIN:
                return rule
    return DatasetCoverageRule(
        dataset=CoverageDataset.OPTIN,
        required=False,
        severity=Severity.WARNING,
        status_on_missing="partial",
        description="Regra padrao de fallback para opt-in de show.",
    )


def _lineage_note() -> str:
    """Return fixed methodology note for opt-in interpretation."""

    return (
        "Opt-in e recorte de adesao e nao substitui metrica de ingressos vendidos total."
    )


def _resolve_missing_reason_from_candidates(
    candidates: list[SessionDatasetSourceCandidate],
) -> tuple[str, str, str]:
    """Resolve status/reason fields from source candidates."""

    if not candidates:
        return (
            "gap",
            "missing_in_catalog",
            "Nenhuma fonte de opt-in correspondente foi encontrada no catalogo para a sessao.",
        )

    has_failed = any(candidate.latest_status == IngestionStatus.FAILED for candidate in candidates)
    has_partial = any(candidate.latest_status == IngestionStatus.PARTIAL for candidate in candidates)
    has_success = any(candidate.latest_status == IngestionStatus.SUCCESS for candidate in candidates)

    if has_failed:
        return (
            "partial",
            "ingestion_failed",
            "Fonte de opt-in encontrada, mas a ultima ingestao terminou como failed.",
        )
    if has_partial:
        return (
            "partial",
            "ingestion_partial",
            "Fonte de opt-in encontrada, mas a ultima ingestao terminou como partial.",
        )
    if has_success:
        return (
            "partial",
            "session_resolution_gap",
            "Fonte de opt-in com success sem cobertura efetiva para a sessao.",
        )
    return (
        "partial",
        "catalog_without_run",
        "Fonte de opt-in catalogada sem status de ingestao concluido.",
    )


def _build_recommended_action(
    *,
    status: str,
    expected_artifact: str,
    candidates: list[SessionDatasetSourceCandidate],
) -> str:
    """Build one short actionable request/recovery message."""

    if status == "gap":
        return f"Solicitar: {expected_artifact}"
    source_ids = sorted({candidate.source_id for candidate in candidates})
    if source_ids:
        joined = ", ".join(source_ids)
        return (
            "Reprocessar/validar extractor de opt-in para as fontes catalogadas "
            f"({joined}) e confirmar cobertura da sessao."
        )
    return f"Reprocessar ingestao e validar cobertura do artefato esperado: {expected_artifact}"


def _coverage_missing_item_to_finding(
    item: CoverageMissingInput,
    *,
    finding_severity: Severity,
    required_by_contract: bool,
) -> ShowOptInFinding:
    """Convert one evaluator missing-item into check finding contract."""

    source_hint = ", ".join(item.sources_considered) if item.sources_considered else None
    return ShowOptInFinding(
        session_key=item.session_key,
        session_date=item.session_date,
        status=item.status,
        severity=finding_severity,
        required_by_contract=required_by_contract,
        reason_code=item.reason_code,
        reason=item.reason,
        expected_artifact=item.expected_artifact,
        expected_filename_pattern=_expected_filename_pattern(item.session_date),
        recommended_action=item.request_action,
        methodological_note=_lineage_note(),
        source_hint=source_hint,
    )


def _probe_optional_show_optin_findings(
    session: Any,
    *,
    event_id: int | None,
    focus_dates: tuple[date, ...],
    finding_severity: Severity,
) -> list[ShowOptInFinding]:
    """Probe optional show opt-in coverage even when not required by contract."""

    config = CoverageRequirementsConfig(
        default_required_datasets=(CoverageDataset.OPTIN,),
        required_datasets_by_session_type={
            EventSessionType.NOTURNO_SHOW: (CoverageDataset.OPTIN,),
        },
    )
    matrix_rows = build_coverage_matrix(
        session,
        event_id=event_id,
        config=config,
    )
    candidates = build_session_dataset_source_candidates(
        session,
        event_id=event_id,
        expected_datasets=(CoverageDataset.OPTIN,),
    )
    candidates_by_session: dict[int, list[SessionDatasetSourceCandidate]] = defaultdict(list)
    for candidate in candidates:
        if candidate.dataset != CoverageDataset.OPTIN:
            continue
        candidates_by_session[int(candidate.session_id)].append(candidate)

    focus_set = set(focus_dates)
    findings: list[ShowOptInFinding] = []
    for row in matrix_rows:
        if row.session_type != EventSessionType.NOTURNO_SHOW:
            continue
        if row.dataset != CoverageDataset.OPTIN:
            continue
        if focus_set and row.session_date not in focus_set:
            continue
        if row.matrix_status == "ok":
            continue

        row_candidates = candidates_by_session.get(int(row.session_id), [])
        status, reason_code, reason = _resolve_missing_reason_from_candidates(row_candidates)
        expected_artifact = _expected_optin_artifact(row.session_type)
        source_hint = None
        if row_candidates:
            source_hint = ", ".join(sorted({item.source_id for item in row_candidates}))
        findings.append(
            ShowOptInFinding(
                session_key=row.session_key,
                session_date=row.session_date,
                status=status,
                severity=finding_severity,
                required_by_contract=False,
                reason_code=reason_code,
                reason=reason,
                expected_artifact=expected_artifact,
                expected_filename_pattern=_expected_filename_pattern(row.session_date),
                recommended_action=_build_recommended_action(
                    status=status,
                    expected_artifact=expected_artifact,
                    candidates=row_candidates,
                ),
                methodological_note=_lineage_note(),
                source_hint=source_hint,
            )
        )
    return sorted(
        findings,
        key=lambda item: (
            item.session_date,
            item.session_key,
            item.status,
            item.reason_code,
        ),
    )


class MissingShowOptInCheck(Check):
    """Detect expected show days without usable opt-in coverage."""

    check_id = "dq.show_coverage.missing_optin"
    description = (
        "Sinaliza ausencia de opt-in em sessoes NOTURNO_SHOW esperadas com severidade por contrato."
    )

    def __init__(
        self,
        *,
        event_id: int | None = None,
        agenda_path: Path | str | None = None,
        contract_path: Path | str = DEFAULT_COVERAGE_CONTRACT_PATH,
        focus_show_dates: Iterable[date] | None = _DEFAULT_FOCUS_SHOW_DATES,
        required_missing_severity: Severity = Severity.ERROR,
        optional_missing_severity: Severity = Severity.WARNING,
        sample_limit: int = 10,
        include_partial_as_gap: bool = True,
    ) -> None:
        """Initialize show opt-in coverage check.

        Args:
            event_id: Optional event filter for coverage evaluation.
            agenda_path: Optional agenda-master path to enforce expected sessions.
            contract_path: Coverage contract path used by evaluator.
            focus_show_dates: Optional explicit day focus (defaults: 12/12 and 14/12).
            required_missing_severity: Severity when show opt-in is required.
            optional_missing_severity: Severity when show opt-in is optional.
            sample_limit: Maximum sample findings in evidence payload.
            include_partial_as_gap: Treat partial opt-in coverage as finding.

        Raises:
            ValueError: If sample limit is invalid.
        """

        if sample_limit <= 0:
            raise ValueError("sample_limit deve ser maior que zero.")
        self._event_id = event_id
        self._agenda_path = Path(agenda_path) if agenda_path is not None else None
        self._contract_path = contract_path
        self._focus_show_dates = _normalize_focus_dates(focus_show_dates)
        self._required_missing_severity = required_missing_severity
        self._optional_missing_severity = optional_missing_severity
        self._sample_limit = int(sample_limit)
        self._include_partial_as_gap = bool(include_partial_as_gap)

    def run(self, context: CheckContext) -> CheckResult:
        """Execute check for missing show-day opt-in coverage."""

        session = context.require_resource("session")
        scoped_event_id = self._event_id
        if scoped_event_id is None:
            metadata_event = context.metadata.get("event_id")
            if isinstance(metadata_event, int):
                scoped_event_id = metadata_event

        try:
            contract = load_coverage_contract(self._contract_path)
        except (FileNotFoundError, CoverageContractError) as exc:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=Severity.ERROR,
                message=(
                    "Falha ao carregar contrato de cobertura para check de opt-in. Como corrigir: "
                    "validar caminho e schema de coverage_contract.yml."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "contract_path": str(self._contract_path),
                    "error": str(exc),
                },
            )

        show_optin_rule = _resolve_show_optin_rule(contract)
        required_by_contract = bool(show_optin_rule.required)
        finding_severity = (
            self._required_missing_severity
            if required_by_contract
            else self._optional_missing_severity
        )

        report = evaluate_coverage(
            session,
            event_id=scoped_event_id,
            contract_path=self._contract_path,
        )

        findings: list[ShowOptInFinding] = []
        if required_by_contract:
            findings.extend(
                _coverage_missing_item_to_finding(
                    item,
                    finding_severity=finding_severity,
                    required_by_contract=True,
                )
                for item in find_show_optin_missing_inputs(
                    report,
                    include_partial=self._include_partial_as_gap,
                    focus_dates=self._focus_show_dates,
                )
            )
        else:
            findings.extend(
                _probe_optional_show_optin_findings(
                    session,
                    event_id=scoped_event_id,
                    focus_dates=self._focus_show_dates,
                    finding_severity=finding_severity,
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
                    severity=finding_severity,
                    message=(
                        "Falha ao carregar agenda master para check de opt-in de shows. Como corrigir: "
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
                    ShowOptInFinding(
                        session_key=session_key,
                        session_date=expected_date,
                        status="gap",
                        severity=finding_severity,
                        required_by_contract=required_by_contract,
                        reason_code="missing_show_session_in_event_sessions",
                        reason=(
                            "Sessao de show esperada na agenda nao foi encontrada em event_sessions."
                        ),
                        expected_artifact=_expected_optin_artifact(EventSessionType.NOTURNO_SHOW),
                        expected_filename_pattern=_expected_filename_pattern(expected_date),
                        recommended_action=(
                            "Solicitar agenda master oficial e XLSX de opt-in/Eventim para o show "
                            "do dia informado."
                        ),
                        methodological_note=_lineage_note(),
                    )
                )

        if not findings:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message=(
                    "Cobertura de opt-in para shows esperados esta completa no recorte analisado."
                ),
                ingestion_id=context.ingestion_id,
                evidence={
                    "event_id": scoped_event_id,
                    "contract_path": str(self._contract_path),
                    "rule_required": required_by_contract,
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

        highest = max((item.severity for item in findings), key=_severity_rank)
        sample = [item.to_dict() for item in findings[: self._sample_limit]]
        lineage_payload: dict[str, Any] = {}
        for item in findings:
            if item.source_hint:
                lineage_payload["source_id"] = item.source_hint.split(",")[0].strip()
                break

        if required_by_contract:
            message = (
                "Ausencia de opt-in em show com regra obrigatoria. Como corrigir: solicitar XLSX "
                "de opt-in/Eventim por dia e rerodar extractor."
            )
        else:
            message = (
                "Ausencia de opt-in em show com regra opcional (warning). Como corrigir: solicitar "
                "XLSX de opt-in quando aplicavel e manter nota metodologica no fechamento."
            )

        return CheckResult(
            check_id=self.check_id,
            status=CheckStatus.FAIL,
            severity=highest,
            message=message,
            ingestion_id=context.ingestion_id,
            evidence={
                "event_id": scoped_event_id,
                "contract_path": str(self._contract_path),
                "rule_required": required_by_contract,
                "focus_show_dates": [item.isoformat() for item in self._focus_show_dates],
                "agenda_path": str(self._agenda_path) if self._agenda_path is not None else None,
                "finding_count": len(findings),
                "findings_sample": sample,
            },
            lineage=lineage_payload,
        )
