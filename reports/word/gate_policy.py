"""Report publication gate policy for Word generation.

This module evaluates DQ report payloads and decides whether report output
should be blocked, allowed, or marked as partial.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml


DEFAULT_REPORT_GATE_POLICY_PATH = (
    Path(__file__).resolve().parent / "config" / "report_gate.yml"
)


@dataclass(frozen=True)
class GateBlockPolicy:
    """Blocking gate thresholds and critical matching rules.

    Args:
        enabled: Enable/disable block checks.
        min_error_findings: Minimum `summary.error` count to trigger block.
        critical_statuses: Statuses considered critical for token matching.
        critical_tokens: Tokens that, when found in finding text, trigger block.
    """

    enabled: bool = True
    min_error_findings: int = 1
    critical_statuses: tuple[str, ...] = ("GAP", "INCONSISTENTE")
    critical_tokens: tuple[str, ...] = (
        "12/12",
        "14/12",
        "2025-12-12",
        "2025-12-14",
        "show_12",
        "show_14",
    )


@dataclass(frozen=True)
class GatePartialPolicy:
    """Partial mode rules when output is still allowed.

    Args:
        enabled: Enable/disable partial checks.
        statuses: Statuses that trigger partial mode.
        min_findings: Minimum matching findings required to mark partial.
        banner_text: Status text to be written in generated DOCX.
    """

    enabled: bool = True
    statuses: tuple[str, ...] = ("GAP", "INCONSISTENTE")
    min_findings: int = 1
    banner_text: str = (
        "PARCIAL: relatorio gerado com gaps/inconsistencias; revisar secao GAP/INCONSISTENTE."
    )


@dataclass(frozen=True)
class GateOutputPolicy:
    """Output behavior for blocked decisions.

    Args:
        allow_partial_on_block: If `True`, blocked decisions downgrade to partial.
    """

    allow_partial_on_block: bool = False


@dataclass(frozen=True)
class GateShowCoveragePolicy:
    """Show-day coverage policy integrated with report gate.

    Args:
        enabled: Enable/disable show-coverage gate checks.
        session_type: Canonical session type under show coverage control.
        critical_dataset: Dataset that must be explicitly covered (or GAP declared).
        critical_statuses: Coverage statuses considered critical.
        required_placeholders: Placeholders that must exist in template when
            show-coverage critical finding occurs.
    """

    enabled: bool = True
    session_type: str = "NOTURNO_SHOW"
    critical_dataset: str = "access_control"
    critical_statuses: tuple[str, ...] = ("GAP",)
    required_placeholders: tuple[str, ...] = (
        "SHOW__COVERAGE__TABLE",
        "GAPS__SUMMARY__TEXT",
    )


@dataclass(frozen=True)
class ReportGatePolicy:
    """Root policy contract loaded from YAML config."""

    version: int
    block: GateBlockPolicy
    partial: GatePartialPolicy
    output: GateOutputPolicy
    show_coverage: GateShowCoveragePolicy


@dataclass(frozen=True)
class GateDecision:
    """Gate decision contract.

    Args:
        status: Decision status (`allow`, `partial`, `block`).
        should_generate_output: Whether DOCX generation should proceed.
        reason: Short decision reason for logs/CLI.
        blockers: Blocking findings summary.
        partial_findings: Partial findings summary.
        status_note: Optional status note to insert in DOCX.
    """

    status: Literal["allow", "partial", "block"]
    should_generate_output: bool
    reason: str
    blockers: tuple[str, ...] = ()
    partial_findings: tuple[str, ...] = ()
    status_note: str | None = None


class ReportGatePolicyError(ValueError):
    """Raised when gate policy config or evaluation input is invalid."""


def _as_mapping(value: Any, *, field: str) -> Mapping[str, Any]:
    """Ensure a YAML node is a mapping."""

    if isinstance(value, Mapping):
        return value
    raise ReportGatePolicyError(f"{field} invalido: esperado objeto YAML.")


def _to_bool(value: Any, *, field: str, default: bool) -> bool:
    """Parse bool value with fallback default."""

    if value is None:
        return default
    if isinstance(value, bool):
        return value
    raise ReportGatePolicyError(f"{field} invalido: esperado true/false.")


def _to_int(value: Any, *, field: str, default: int) -> int:
    """Parse positive integer with fallback default."""

    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ReportGatePolicyError(f"{field} invalido: esperado inteiro.") from exc
    if parsed < 0:
        raise ReportGatePolicyError(f"{field} invalido: esperado inteiro >= 0.")
    return parsed


def _to_upper_tuple(value: Any, *, field: str, default: tuple[str, ...]) -> tuple[str, ...]:
    """Parse list[str] and normalize to uppercase tuple."""

    if value is None:
        return default
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ReportGatePolicyError(f"{field} invalido: esperado lista de textos.")
    normalized = tuple(str(item).strip().upper() for item in value if str(item).strip())
    if not normalized:
        raise ReportGatePolicyError(f"{field} invalido: lista nao pode ser vazia.")
    return normalized


def _to_token_tuple(value: Any, *, field: str, default: tuple[str, ...]) -> tuple[str, ...]:
    """Parse token list and normalize to lowercase tuple."""

    if value is None:
        return tuple(token.casefold() for token in default)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ReportGatePolicyError(f"{field} invalido: esperado lista de textos.")
    tokens = tuple(str(item).strip().casefold() for item in value if str(item).strip())
    if not tokens:
        raise ReportGatePolicyError(f"{field} invalido: lista nao pode ser vazia.")
    return tokens


def _to_non_empty_text(value: Any, *, field: str, default: str) -> str:
    """Parse non-empty text with fallback default."""

    if value is None:
        return default
    text = str(value).strip()
    if not text:
        raise ReportGatePolicyError(f"{field} invalido: texto nao pode ser vazio.")
    return text


def _to_placeholder_tuple(
    value: Any,
    *,
    field: str,
    default: tuple[str, ...],
) -> tuple[str, ...]:
    """Parse placeholder list and normalize to uppercase tuple."""

    if value is None:
        return tuple(item.strip().upper() for item in default)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ReportGatePolicyError(f"{field} invalido: esperado lista de placeholders.")
    items = tuple(str(item).strip().upper() for item in value if str(item).strip())
    if not items:
        raise ReportGatePolicyError(f"{field} invalido: lista nao pode ser vazia.")
    return items


def _as_text_set(value: Any) -> set[str]:
    """Normalize arbitrary sequence into lower-case text set."""

    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return set()
    return {str(item).strip().casefold() for item in value if str(item).strip()}


def _extract_gate_entries(dq_report: Mapping[str, Any]) -> list[dict[str, str]]:
    """Extract normalized GAP/INCONSISTENTE entries from DQ report payload."""

    entries: list[dict[str, str]] = []
    sections = dq_report.get("sections")
    if isinstance(sections, Mapping):
        for item in sections.get("inconsistencies", []) or []:
            if not isinstance(item, Mapping):
                continue
            entries.append(
                {
                    "status": "INCONSISTENTE",
                    "dataset_id": str(item.get("dataset_id", item.get("dataset", "unknown"))),
                    "message": str(item.get("message", "")),
                    "evidence_text": str(item.get("evidence_text", item.get("evidence", ""))),
                }
            )
        gaps = sections.get("gaps_by_dataset")
        if isinstance(gaps, Mapping):
            for dataset_id, values in gaps.items():
                if not isinstance(values, Sequence) or isinstance(values, (str, bytes, bytearray)):
                    continue
                for item in values:
                    if not isinstance(item, Mapping):
                        continue
                    entries.append(
                        {
                            "status": "GAP",
                            "dataset_id": str(item.get("dataset_id", dataset_id)),
                            "message": str(item.get("message", "")),
                            "evidence_text": str(item.get("evidence_text", item.get("evidence", ""))),
                        }
                    )
    return entries


def _extract_coverage_sessions(
    *,
    dq_report: Mapping[str, Any] | None,
    coverage_report: Mapping[str, Any] | None,
) -> list[Mapping[str, Any]]:
    """Extract coverage session rows from coverage or DQ payload."""

    if isinstance(coverage_report, Mapping):
        sessions = coverage_report.get("sessions")
        if isinstance(sessions, Sequence) and not isinstance(sessions, (str, bytes, bytearray)):
            return [item for item in sessions if isinstance(item, Mapping)]

    if isinstance(dq_report, Mapping):
        sections = dq_report.get("sections")
        if isinstance(sections, Mapping):
            coverage = sections.get("coverage")
            if isinstance(coverage, Mapping):
                sessions = coverage.get("sessions")
                if isinstance(sessions, Sequence) and not isinstance(
                    sessions,
                    (str, bytes, bytearray),
                ):
                    return [item for item in sessions if isinstance(item, Mapping)]
    return []


def _coverage_dataset_status(session_item: Mapping[str, Any], *, dataset: str) -> str:
    """Resolve dataset status (`ok`/`partial`/`gap`) for one coverage session."""

    dataset_key = dataset.strip().casefold()
    missing = _as_text_set(session_item.get("missing_datasets"))
    if dataset_key in missing:
        return "GAP"
    partial = _as_text_set(session_item.get("partial_datasets"))
    if dataset_key in partial:
        return "PARTIAL"
    observed = _as_text_set(session_item.get("observed_datasets"))
    if dataset_key in observed:
        return "OK"
    return "GAP"


def _collect_show_coverage_critical_entries(
    *,
    policy: GateShowCoveragePolicy,
    dq_report: Mapping[str, Any] | None,
    coverage_report: Mapping[str, Any] | None,
) -> list[dict[str, str]]:
    """Collect critical show-coverage entries from available coverage payload."""

    sessions = _extract_coverage_sessions(dq_report=dq_report, coverage_report=coverage_report)
    if not sessions:
        return []

    required_session_type = policy.session_type.strip().casefold()
    critical_statuses = {status.casefold() for status in policy.critical_statuses}
    critical_entries: list[dict[str, str]] = []
    for session_item in sessions:
        session_type = str(session_item.get("session_type", "")).strip().casefold()
        if session_type != required_session_type:
            continue

        dataset_status = _coverage_dataset_status(
            session_item,
            dataset=policy.critical_dataset,
        )
        if dataset_status.casefold() not in critical_statuses:
            continue

        session_key = str(session_item.get("session_key", "unknown")).strip() or "unknown"
        session_date = str(session_item.get("session_date", "")).strip()
        dataset_id = f"{session_key}_{policy.critical_dataset}".strip("_")
        message = (
            "Cobertura critica de show sem "
            f"{policy.critical_dataset} em {session_key} ({session_date or 'data n/d'})."
        )
        evidence_text = (
            f"status={dataset_status.lower()} | session_type={session_type or 'n/d'}"
        )
        critical_entries.append(
            {
                "status": "GAP",
                "dataset_id": dataset_id,
                "message": message,
                "evidence_text": evidence_text,
            }
        )

    return critical_entries


def merge_show_coverage_gaps(
    dq_report: Mapping[str, Any] | None,
    *,
    coverage_report: Mapping[str, Any] | None,
    policy: ReportGatePolicy,
) -> dict[str, Any]:
    """Merge show-coverage critical findings into DQ `gaps_by_dataset`.

    Args:
        dq_report: Optional original DQ payload.
        coverage_report: Optional explicit coverage payload.
        policy: Loaded report gate policy.

    Returns:
        New DQ payload with critical show-coverage entries added to
        `sections.gaps_by_dataset`.
    """

    base_report: dict[str, Any]
    if isinstance(dq_report, Mapping):
        base_report = dict(dq_report)
    else:
        base_report = {}

    if not policy.show_coverage.enabled:
        return base_report

    critical_entries = _collect_show_coverage_critical_entries(
        policy=policy.show_coverage,
        dq_report=dq_report,
        coverage_report=coverage_report,
    )
    if not critical_entries:
        return base_report

    sections = base_report.get("sections")
    if not isinstance(sections, Mapping):
        sections = {}
    sections_dict = dict(sections)

    gaps_by_dataset = sections_dict.get("gaps_by_dataset")
    if not isinstance(gaps_by_dataset, Mapping):
        gaps_by_dataset = {}
    gaps_dict = {
        str(key): list(value) if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) else []
        for key, value in gaps_by_dataset.items()
    }

    existing_tokens = {
        (
            str(item.get("dataset_id", "")).casefold(),
            str(item.get("message", "")).casefold(),
        )
        for values in gaps_dict.values()
        for item in values
        if isinstance(item, Mapping)
    }
    for entry in critical_entries:
        dataset_id = str(entry.get("dataset_id", "show_coverage")).strip() or "show_coverage"
        token = (
            dataset_id.casefold(),
            str(entry.get("message", "")).casefold(),
        )
        if token in existing_tokens:
            continue
        existing_tokens.add(token)
        gaps_dict.setdefault(dataset_id, []).append(
            {
                "dataset_id": dataset_id,
                "message": str(entry.get("message", "")),
                "evidence_text": str(entry.get("evidence_text", "")),
            }
        )

    sections_dict["gaps_by_dataset"] = gaps_dict
    if coverage_report is not None and "coverage" not in sections_dict:
        sections_dict["coverage"] = dict(coverage_report)
    base_report["sections"] = sections_dict
    return base_report


def load_report_gate_policy(
    path: Path | str = DEFAULT_REPORT_GATE_POLICY_PATH,
) -> ReportGatePolicy:
    """Load report gate policy from YAML config.

    Args:
        path: Policy YAML path.

    Returns:
        Parsed policy dataclass.

    Raises:
        FileNotFoundError: If policy file does not exist.
        ReportGatePolicyError: If config content is invalid.
    """

    policy_path = Path(path)
    if not policy_path.exists():
        raise FileNotFoundError(f"Arquivo de policy nao encontrado: {policy_path}")

    raw = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    root = _as_mapping(raw, field="$")
    version = _to_int(root.get("version"), field="$.version", default=1)
    if version <= 0:
        raise ReportGatePolicyError("$.version invalido: esperado inteiro positivo.")

    block_raw = _as_mapping(root.get("block", {}), field="$.block")
    partial_raw = _as_mapping(root.get("partial", {}), field="$.partial")
    output_raw = _as_mapping(root.get("output", {}), field="$.output")
    show_cov_raw = _as_mapping(root.get("show_coverage", {}), field="$.show_coverage")

    block = GateBlockPolicy(
        enabled=_to_bool(block_raw.get("enabled"), field="$.block.enabled", default=True),
        min_error_findings=_to_int(
            block_raw.get("min_error_findings"),
            field="$.block.min_error_findings",
            default=1,
        ),
        critical_statuses=_to_upper_tuple(
            block_raw.get("critical_statuses"),
            field="$.block.critical_statuses",
            default=("GAP", "INCONSISTENTE"),
        ),
        critical_tokens=_to_token_tuple(
            block_raw.get("critical_tokens"),
            field="$.block.critical_tokens",
            default=GateBlockPolicy().critical_tokens,
        ),
    )

    banner_text = partial_raw.get("banner_text")
    if banner_text is None:
        banner = GatePartialPolicy().banner_text
    else:
        banner = str(banner_text).strip()
        if not banner:
            raise ReportGatePolicyError("$.partial.banner_text invalido: texto vazio.")

    partial = GatePartialPolicy(
        enabled=_to_bool(partial_raw.get("enabled"), field="$.partial.enabled", default=True),
        statuses=_to_upper_tuple(
            partial_raw.get("statuses"),
            field="$.partial.statuses",
            default=("GAP", "INCONSISTENTE"),
        ),
        min_findings=_to_int(
            partial_raw.get("min_findings"),
            field="$.partial.min_findings",
            default=1,
        ),
        banner_text=banner,
    )

    output = GateOutputPolicy(
        allow_partial_on_block=_to_bool(
            output_raw.get("allow_partial_on_block"),
            field="$.output.allow_partial_on_block",
            default=False,
        )
    )
    show_coverage = GateShowCoveragePolicy(
        enabled=_to_bool(
            show_cov_raw.get("enabled"),
            field="$.show_coverage.enabled",
            default=True,
        ),
        session_type=_to_non_empty_text(
            show_cov_raw.get("session_type"),
            field="$.show_coverage.session_type",
            default=GateShowCoveragePolicy().session_type,
        ).upper(),
        critical_dataset=_to_non_empty_text(
            show_cov_raw.get("critical_dataset"),
            field="$.show_coverage.critical_dataset",
            default=GateShowCoveragePolicy().critical_dataset,
        ).casefold(),
        critical_statuses=_to_upper_tuple(
            show_cov_raw.get("critical_statuses"),
            field="$.show_coverage.critical_statuses",
            default=GateShowCoveragePolicy().critical_statuses,
        ),
        required_placeholders=_to_placeholder_tuple(
            show_cov_raw.get("required_placeholders"),
            field="$.show_coverage.required_placeholders",
            default=GateShowCoveragePolicy().required_placeholders,
        ),
    )

    return ReportGatePolicy(
        version=version,
        block=block,
        partial=partial,
        output=output,
        show_coverage=show_coverage,
    )


def evaluate_report_gate(
    dq_report: Mapping[str, Any] | None,
    policy: ReportGatePolicy,
    *,
    coverage_report: Mapping[str, Any] | None = None,
    template_placeholders: Sequence[str] | None = None,
) -> GateDecision:
    """Evaluate publication gate decision from DQ report and policy.

    Args:
        dq_report: DQ report payload (JSON-like dict).
        policy: Loaded gate policy.
        coverage_report: Optional explicit show coverage payload.
        template_placeholders: Optional placeholder ids found in template.

    Returns:
        Gate decision (`allow`, `partial`, or `block`).
    """

    if dq_report is None and coverage_report is None:
        return GateDecision(
            status="allow",
            should_generate_output=True,
            reason="DQ/coverage report nao informado; gate nao aplicavel.",
        )
    if dq_report is not None and not isinstance(dq_report, Mapping):
        raise ReportGatePolicyError("dq_report invalido: esperado objeto/dict.")
    if coverage_report is not None and not isinstance(coverage_report, Mapping):
        raise ReportGatePolicyError("coverage_report invalido: esperado objeto/dict.")

    summary = dq_report.get("summary") if isinstance(dq_report, Mapping) else None
    if isinstance(summary, Mapping):
        error_count = _to_int(summary.get("error"), field="dq_report.summary.error", default=0)
    else:
        error_count = 0

    entries = _extract_gate_entries(dq_report) if isinstance(dq_report, Mapping) else []
    blockers: list[str] = []
    hard_blockers: list[str] = []

    if policy.block.enabled and policy.block.min_error_findings > 0:
        if error_count >= policy.block.min_error_findings:
            blockers.append(
                f"summary.error={error_count} >= {policy.block.min_error_findings}"
            )

    if policy.block.enabled and entries:
        for entry in entries:
            status = str(entry.get("status", "")).upper()
            if status not in policy.block.critical_statuses:
                continue
            searchable = " | ".join(
                (
                    str(entry.get("dataset_id", "")).casefold(),
                    str(entry.get("message", "")).casefold(),
                    str(entry.get("evidence_text", "")).casefold(),
                )
            )
            matched = [token for token in policy.block.critical_tokens if token in searchable]
            if not matched:
                continue
            token_preview = ", ".join(matched[:2])
            blockers.append(
                f"{status} em dataset={entry.get('dataset_id', 'unknown')} (token={token_preview})"
            )

    show_critical_entries: list[dict[str, str]] = []
    if policy.show_coverage.enabled:
        show_critical_entries = _collect_show_coverage_critical_entries(
            policy=policy.show_coverage,
            dq_report=dq_report if isinstance(dq_report, Mapping) else None,
            coverage_report=coverage_report,
        )
        for entry in show_critical_entries:
            blockers.append(
                "SHOW_COVERAGE_CRITICO | "
                f"dataset={entry.get('dataset_id', 'unknown')} | "
                f"{entry.get('message', '')}"
            )

        if show_critical_entries and template_placeholders is not None:
            available = {
                str(item).strip().upper()
                for item in template_placeholders
                if str(item).strip()
            }
            required = set(policy.show_coverage.required_placeholders)
            missing = sorted(required - available)
            if missing:
                hard_blockers.append(
                    "PLACEHOLDER_OBRIGATORIO_AUSENTE | "
                    + ", ".join(missing)
                )

    partial_findings: list[str] = []
    if policy.partial.enabled and entries:
        for entry in entries:
            status = str(entry.get("status", "")).upper()
            if status not in policy.partial.statuses:
                continue
            partial_findings.append(
                f"{status} em dataset={entry.get('dataset_id', 'unknown')}"
            )

    if policy.show_coverage.enabled:
        for entry in show_critical_entries:
            partial_findings.append(
                "SHOW_COVERAGE_CRITICO em dataset="
                f"{entry.get('dataset_id', 'unknown')}"
            )

    if hard_blockers:
        return GateDecision(
            status="block",
            should_generate_output=False,
            reason="Gate critico acionado com requisitos obrigatorios de secao ausentes.",
            blockers=tuple((*hard_blockers, *blockers)),
            partial_findings=tuple(partial_findings),
        )

    if blockers:
        if policy.output.allow_partial_on_block:
            return GateDecision(
                status="partial",
                should_generate_output=True,
                reason="Gate critico acionado; geracao parcial habilitada por policy.",
                blockers=tuple(blockers),
                partial_findings=tuple(partial_findings),
                status_note=policy.partial.banner_text,
            )
        return GateDecision(
            status="block",
            should_generate_output=False,
            reason="Gate critico acionado; geracao bloqueada por policy.",
            blockers=tuple(blockers),
            partial_findings=tuple(partial_findings),
        )

    if (
        policy.partial.enabled
        and policy.partial.min_findings > 0
        and len(partial_findings) >= policy.partial.min_findings
    ):
        return GateDecision(
            status="partial",
            should_generate_output=True,
            reason="Gate em modo parcial por findings de GAP/INCONSISTENTE.",
            partial_findings=tuple(partial_findings),
            status_note=policy.partial.banner_text,
        )

    return GateDecision(
        status="allow",
        should_generate_output=True,
        reason="Gate aprovado sem bloqueios.",
    )
