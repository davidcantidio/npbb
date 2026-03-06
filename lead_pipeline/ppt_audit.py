from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path

from .ppt_matching import (
    FAMILY_ALIASES,
    FAMILY_NUMERIC_SCOPE,
    eligible_coverage_basis,
    event_direct_aliases,
)
from .ppt_numeric import (
    ObservedMetric,
    compare_metric,
    extract_breakdown_metrics,
    extract_lead_summary_metrics,
    extract_topline_leads,
)
from .ppt_openxml import extract_presentation
from .ppt_profiles import SlideProfile, classify_slides
from .ppt_truth import TruthCatalog, TruthMetrics, load_truth_catalog


IGNORED_METRIC_LABELS = {
    "publico_impactado": "publico impactado",
    "spending": "spending",
    "cartoes_emitidos": "cartoes emitidos",
    "contas_abertas": "contas abertas",
    "experiencia_da_marca": "experiencia da marca",
}


@dataclass(frozen=True)
class PptAuditConfig:
    lote_id: str
    ppt_path: Path
    truth_csv_path: Path
    output_root: Path = Path("./eventos")


@dataclass(frozen=True)
class AuditFinding:
    code: str
    severity: str
    slide_index: int | None
    event_name: str | None
    event_family: str | None
    field: str | None
    expected_value: str | int | float | None
    actual_value: str | int | float | None
    message: str


@dataclass(frozen=True)
class EventCoverage:
    event_name: str
    event_family: str
    coverage_status: str
    matched_slides: list[int]
    coverage_basis: list[str]


@dataclass(frozen=True)
class PptAuditResult:
    lote_id: str
    status: str
    decision: str
    output_dir: Path
    report_path: Path
    summary_path: Path
    exit_code: int
    critical_count: int
    error_count: int
    warning_count: int
    ignored_count: int
    audited_slides: int


def audit_presentation(config: PptAuditConfig) -> PptAuditResult:
    output_dir = config.output_root / config.lote_id
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "report.json"
    summary_path = output_dir / "validation-summary.md"

    findings: list[AuditFinding] = []
    slide_profiles_payload: list[dict[str, object]] = []
    event_coverage: list[EventCoverage] = []
    audited_slide_count = 0

    try:
        truth_catalog = load_truth_catalog(config.truth_csv_path)
        slides = extract_presentation(config.ppt_path)
        audited_slide_count = len(slides)
        source_events = [item.name for item in truth_catalog.source_events]
        slide_profiles = classify_slides(slides, source_events)
        profile_by_slide = {profile.slide_index: profile for profile in slide_profiles}

        for profile in slide_profiles:
            slide_profiles_payload.append(
                {
                    "slide_index": profile.slide_index,
                    "profile_name": profile.profile_name,
                    "matched_events": sorted(profile.match.event_names),
                    "matched_families": sorted(profile.match.event_families),
                }
            )

        findings.extend(_ignored_metric_findings(slides, profile_by_slide))
        event_coverage, coverage_findings = _build_event_coverage(truth_catalog, slide_profiles)
        findings.extend(coverage_findings)
        findings.extend(_numeric_findings(slides, profile_by_slide, truth_catalog))
    except ValueError as exc:
        message = str(exc)
        if message.startswith("UNMAPPED_SOURCE_EVENT"):
            findings.append(
                AuditFinding(
                    code="UNMAPPED_SOURCE_EVENT",
                    severity="critical",
                    slide_index=None,
                    event_name=message.split(": ", 1)[1] if ": " in message else None,
                    event_family=None,
                    field=None,
                    expected_value=None,
                    actual_value=None,
                    message=message,
                )
            )
        else:
            raise

    report = _build_report(
        config=config,
        findings=findings,
        slide_profiles_payload=slide_profiles_payload,
        event_coverage=event_coverage,
        audited_slide_count=audited_slide_count,
        truth_source_count=len(event_coverage) if event_coverage else 0,
    )
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(_build_summary(report), encoding="utf-8")

    gate = report["gate"]
    return PptAuditResult(
        lote_id=config.lote_id,
        status=gate["status"],
        decision=gate["decision"],
        output_dir=output_dir,
        report_path=report_path,
        summary_path=summary_path,
        exit_code=2 if gate["status"] == "FAIL" else 0,
        critical_count=gate["critical_count"],
        error_count=gate["error_count"],
        warning_count=gate["warning_count"],
        ignored_count=gate["ignored_count"],
        audited_slides=audited_slide_count,
    )


def _build_event_coverage(
    truth_catalog: TruthCatalog,
    slide_profiles: list[SlideProfile],
) -> tuple[list[EventCoverage], list[AuditFinding]]:
    findings: list[AuditFinding] = []
    coverage_records: list[EventCoverage] = []

    for source_event in truth_catalog.source_events:
        best_status = "missing"
        matched_slides: set[int] = set()
        coverage_basis: set[str] = set()
        for profile in slide_profiles:
            basis = eligible_coverage_basis(profile.profile_name)
            if basis is None:
                continue

            direct_match = source_event.name in profile.match.event_names
            family_match = source_event.family in profile.match.event_families
            if not direct_match and not family_match:
                continue

            matched_slides.add(profile.slide_index)
            coverage_basis.add(basis)
            candidate = _coverage_candidate_status(source_event.family, direct_match, family_match, profile.profile_name)
            if _coverage_rank(candidate) > _coverage_rank(best_status):
                best_status = candidate

        coverage = EventCoverage(
            event_name=source_event.name,
            event_family=source_event.family,
            coverage_status=best_status,
            matched_slides=sorted(matched_slides),
            coverage_basis=sorted(coverage_basis),
        )
        coverage_records.append(coverage)

        if best_status == "missing":
            findings.append(
                AuditFinding(
                    code="EVENT_MISSING_FROM_PRESENTATION",
                    severity="critical",
                    slide_index=None,
                    event_name=source_event.name,
                    event_family=source_event.family,
                    field=None,
                    expected_value="contemplated",
                    actual_value="missing",
                    message=f"Evento de origem ausente no PPT: {source_event.name}",
                )
            )
        elif best_status == "summary_only":
            findings.append(
                AuditFinding(
                    code="EVENT_ONLY_SUMMARY_COVERAGE",
                    severity="warning",
                    slide_index=coverage.matched_slides[0] if coverage.matched_slides else None,
                    event_name=source_event.name,
                    event_family=source_event.family,
                    field=None,
                    expected_value="numeric_coverage",
                    actual_value="summary_only",
                    message=f"Evento contemplado apenas por resumo/familia: {source_event.name}",
                )
            )

    return coverage_records, findings


def _coverage_candidate_status(
    family: str,
    direct_match: bool,
    family_match: bool,
    profile_name: str,
) -> str:
    if profile_name in {"lead_summary_profile", "coverage_section_profile"}:
        return "summary_only"

    scope = FAMILY_NUMERIC_SCOPE[family]
    if scope == "coverage_only":
        return "summary_only"
    if scope == "family" and family_match:
        return "family_numeric"
    if scope == "lead_only" and family_match:
        return "family_numeric"
    if scope in {"direct_event", "lead_only"} and direct_match:
        return "direct_numeric"
    if family_match:
        return "family_numeric"
    return "summary_only"


def _coverage_rank(status: str) -> int:
    return {
        "missing": 0,
        "summary_only": 1,
        "family_numeric": 2,
        "direct_numeric": 3,
    }[status]


def _numeric_findings(
    slides,
    profile_by_slide: dict[int, SlideProfile],
    truth_catalog: TruthCatalog,
) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    family_sizes: dict[str, int] = {}
    for source_event in truth_catalog.source_events:
        family_sizes[source_event.family] = family_sizes.get(source_event.family, 0) + 1

    for slide in slides:
        profile = profile_by_slide[slide.slide_index]
        if profile.profile_name == "lead_summary_profile":
            observed = extract_lead_summary_metrics(slide)
            expected = {
                "total_leads": truth_catalog.total_metrics.total_leads,
                "clientes_bb": truth_catalog.total_metrics.clientes_bb,
            }
            findings.extend(
                _compare_observed_metrics(
                    slide_index=slide.slide_index,
                    event_name=None,
                    family=None,
                    observed_metrics=observed,
                    expected_metrics=expected,
                )
            )
        elif profile.profile_name == "event_breakdown_profile":
            observed = extract_breakdown_metrics(slide)
            subject_event, subject_family, truth_metrics = _resolve_breakdown_subject(profile, truth_catalog)
            if truth_metrics is None:
                continue
            findings.extend(
                _compare_observed_metrics(
                    slide_index=slide.slide_index,
                    event_name=subject_event,
                    family=subject_family,
                    observed_metrics=observed,
                    expected_metrics=_truth_metrics_dict(truth_metrics),
                )
            )
        elif profile.profile_name == "event_topline_profile":
            subject_aliases: dict[str, list[str]] = {}
            subject_expected: dict[str, tuple[str | None, str | None, TruthMetrics]] = {}

            for event_name in sorted(profile.match.event_names):
                family = next(item.family for item in truth_catalog.source_events if item.name == event_name)
                numeric_scope = FAMILY_NUMERIC_SCOPE[family]
                if numeric_scope == "direct_event" or (numeric_scope == "lead_only" and family_sizes[family] == 1):
                    subject_aliases[f"event::{event_name}"] = event_direct_aliases(event_name)
                    subject_expected[f"event::{event_name}"] = (
                        event_name,
                        family,
                        truth_catalog.event_metrics[event_name],
                    )

            for family in sorted(profile.match.event_families):
                numeric_scope = FAMILY_NUMERIC_SCOPE[family]
                family_subject_id = f"family::{family}"
                if numeric_scope in {"family", "lead_only"} and family_subject_id not in subject_aliases:
                    subject_aliases[family_subject_id] = [family_alias for family_alias in FAMILY_ALIASES[family]]
                    subject_expected[family_subject_id] = (
                        None,
                        family,
                        truth_catalog.family_metrics[family],
                    )

            observed_by_subject = extract_topline_leads(slide, subject_aliases)
            for subject_id, observed in observed_by_subject.items():
                event_name, family, metrics = subject_expected[subject_id]
                findings.extend(
                    _compare_observed_metrics(
                        slide_index=slide.slide_index,
                        event_name=event_name,
                        family=family,
                        observed_metrics={"total_leads": observed},
                        expected_metrics={"total_leads": metrics.total_leads},
                    )
                )

    return findings


def _resolve_breakdown_subject(
    profile: SlideProfile,
    truth_catalog: TruthCatalog,
) -> tuple[str | None, str | None, TruthMetrics | None]:
    if len(profile.match.event_names) == 1:
        event_name = next(iter(profile.match.event_names))
        family = next(item.family for item in truth_catalog.source_events if item.name == event_name)
        numeric_scope = FAMILY_NUMERIC_SCOPE[family]
        if numeric_scope == "direct_event":
            return event_name, family, truth_catalog.event_metrics[event_name]
        if numeric_scope == "family":
            return None, family, truth_catalog.family_metrics[family]

    if len(profile.match.event_families) == 1:
        family = next(iter(profile.match.event_families))
        if FAMILY_NUMERIC_SCOPE[family] in {"family", "lead_only"}:
            return None, family, truth_catalog.family_metrics[family]

    for family in sorted(profile.match.event_families):
        if FAMILY_NUMERIC_SCOPE[family] == "family":
            return None, family, truth_catalog.family_metrics[family]
    return None, None, None


def _compare_observed_metrics(
    *,
    slide_index: int,
    event_name: str | None,
    family: str | None,
    observed_metrics: dict[str, ObservedMetric],
    expected_metrics: dict[str, int],
) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    for field, expected in expected_metrics.items():
        observed = observed_metrics.get(field)
        if observed is None:
            continue
        if compare_metric(observed, expected):
            continue
        findings.append(
            AuditFinding(
                code="METRIC_MISMATCH",
                severity="error",
                slide_index=slide_index,
                event_name=event_name,
                event_family=family,
                field=field,
                expected_value=expected,
                actual_value=observed.display_text,
                message=(
                    f"Valor divergente para {field} no slide {slide_index}: "
                    f"esperado {expected}, encontrado {observed.display_text}"
                ),
            )
        )
    return findings


def _truth_metrics_dict(metrics: TruthMetrics) -> dict[str, int]:
    return {
        "total_leads": metrics.total_leads,
        "clientes_bb": metrics.clientes_bb,
        "nao_clientes": metrics.nao_clientes,
        "faixa_18_25": metrics.faixa_18_25,
        "faixa_26_40": metrics.faixa_26_40,
        "fora_18_40": metrics.fora_18_40,
    }


def _ignored_metric_findings(slides, profile_by_slide: dict[int, SlideProfile]) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    for slide in slides:
        profile = profile_by_slide[slide.slide_index]
        if profile.profile_name == "unsupported_profile":
            continue
        for field_code, alias in IGNORED_METRIC_LABELS.items():
            if alias not in slide.normalized_text:
                continue
            findings.append(
                AuditFinding(
                    code="UNSUPPORTED_METRIC_IGNORED",
                    severity="ignored",
                    slide_index=slide.slide_index,
                    event_name=None,
                    event_family=None,
                    field=field_code,
                    expected_value=None,
                    actual_value=None,
                    message=f"Metrica ignorada por falta de fonte de verdade: {field_code}",
                )
            )
    return findings


def _build_report(
    *,
    config: PptAuditConfig,
    findings: list[AuditFinding],
    slide_profiles_payload: list[dict[str, object]],
    event_coverage: list[EventCoverage],
    audited_slide_count: int,
    truth_source_count: int,
) -> dict[str, object]:
    critical_count = sum(1 for finding in findings if finding.severity == "critical")
    error_count = sum(1 for finding in findings if finding.severity == "error")
    warning_count = sum(1 for finding in findings if finding.severity == "warning")
    ignored_count = sum(1 for finding in findings if finding.severity == "ignored")

    if critical_count or error_count:
        status = "FAIL"
        decision = "hold"
    elif warning_count:
        status = "PASS_WITH_WARNINGS"
        decision = "promote"
    else:
        status = "PASS"
        decision = "promote"

    return {
        "lote_id": config.lote_id,
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "ppt_path": str(config.ppt_path),
        "truth_csv_path": str(config.truth_csv_path),
        "source_event_count": truth_source_count,
        "audited_slide_count": audited_slide_count,
        "slide_profiles": slide_profiles_payload,
        "event_coverage": [asdict(item) for item in event_coverage],
        "findings": [asdict(item) for item in findings],
        "gate": {
            "status": status,
            "decision": decision,
            "critical_count": critical_count,
            "error_count": error_count,
            "warning_count": warning_count,
            "ignored_count": ignored_count,
        },
    }


def _build_summary(report: dict[str, object]) -> str:
    gate = report["gate"]
    findings = report["findings"]
    coverage = report["event_coverage"]

    direct = [item for item in coverage if item["coverage_status"] == "direct_numeric"]
    family = [item for item in coverage if item["coverage_status"] == "family_numeric"]
    summary_only = [item for item in coverage if item["coverage_status"] == "summary_only"]
    missing = [item for item in coverage if item["coverage_status"] == "missing"]

    lines = [
        "# Validation Summary",
        "",
        "## Status",
        f"- Lote: {report['lote_id']}",
        f"- Status: {gate['status']}",
        f"- Decision: {gate['decision']}",
        f"- Slides auditados: {report['audited_slide_count']}",
        f"- Eventos de origem: {report['source_event_count']}",
        "",
        "## Problemas Graves",
    ]
    lines.extend(_format_findings(findings, severity="critical"))
    lines.extend(["", "## Divergências Numéricas"])
    lines.extend(_format_findings(findings, severity="error"))
    lines.extend(["", "## Eventos com Cobertura Numérica Direta"])
    lines.extend(_format_coverage(direct))
    lines.extend(["", "## Eventos com Cobertura Numérica por Família"])
    lines.extend(_format_coverage(family))
    lines.extend(["", "## Eventos Cobertos Apenas por Resumo"])
    lines.extend(_format_coverage(summary_only))
    lines.extend(["", "## Eventos Ausentes no PPT"])
    if missing:
        lines.append("- qualquer item abaixo e falha grave de cobertura")
    lines.extend(_format_coverage(missing))
    lines.extend(["", "## Itens Ignorados por Limitação de Fonte"])
    lines.extend(_format_findings(findings, severity="ignored"))
    return "\n".join(lines).rstrip() + "\n"


def _format_findings(findings: list[dict[str, object]], *, severity: str) -> list[str]:
    selected = [item for item in findings if item["severity"] == severity]
    if not selected:
        return ["- nenhum"]
    lines: list[str] = []
    for item in selected:
        lines.append(
            f"- {item['code']}: {item['message']}"
            + (f" [slide {item['slide_index']}]" if item["slide_index"] is not None else "")
        )
    return lines


def _format_coverage(records: list[dict[str, object]]) -> list[str]:
    if not records:
        return ["- nenhum"]
    lines: list[str] = []
    for item in records:
        slides = ", ".join(str(slide) for slide in item["matched_slides"]) or "-"
        basis = ", ".join(item["coverage_basis"]) or "-"
        lines.append(
            f"- {item['event_name']} ({item['event_family']}): slides [{slides}] via {basis}"
        )
    return lines
