"""PPTX social metrics extractor and staging loader with slide lineage.

This module implements mapping-driven extraction from PPTX slides and persists
results in `stg_social_metrics` with ingestion and lineage references.

Main flow:
- read slides using `iter_slides(...)` (with automatic XML fallback),
- match mapping rules by `slide_number` and/or `title_regex`,
- find metric label text in slide blocks,
- parse metric numeric values by extraction rule,
- persist staging rows with `location_type=slide` and evidence text.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterator, Sequence

from sqlmodel import Session

try:  # package execution (repo root at `npbb`)
    from etl.extract.pptx_mapping import PptxMappingRule, load_pptx_mapping
    from etl.extract.pptx_reader import PptxSlide, iter_slides
except ModuleNotFoundError:  # pragma: no cover - fallback for `npbb.etl.*` imports
    from npbb.etl.extract.pptx_mapping import PptxMappingRule, load_pptx_mapping
    from npbb.etl.extract.pptx_reader import PptxSlide, iter_slides

try:  # pragma: no cover - import style depends on caller cwd
    from core.registry.location_ref import format_location
except ModuleNotFoundError:  # pragma: no cover
    from npbb.core.registry.location_ref import format_location

try:  # pragma: no cover
    from app.db.database import engine
    from app.models.etl_registry import IngestionStatus
    from app.models.stg_social_metrics import StgSocialMetric
    from app.services.etl_lineage_service import create_lineage_ref
    from app.services.etl_registry_service import (
        enforce_lineage_policy,
        finish_ingestion_run,
        register_source_from_path,
        start_ingestion_run,
    )
    from app.services.session_resolver import resolve_session_reference
except ModuleNotFoundError:  # pragma: no cover
    BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))
    from app.db.database import engine
    from app.models.etl_registry import IngestionStatus
    from app.models.stg_social_metrics import StgSocialMetric
    from app.services.etl_lineage_service import create_lineage_ref
    from app.services.etl_registry_service import (
        enforce_lineage_policy,
        finish_ingestion_run,
        register_source_from_path,
        start_ingestion_run,
    )
    from app.services.session_resolver import resolve_session_reference


_INTEGER_RE = re.compile(r"[-+]?\d{1,3}(?:[.\s]\d{3})*|[-+]?\d+")
_NUMBER_RE = re.compile(r"[-+]?\d{1,3}(?:[.\s]\d{3})*(?:,\d+|\.\d+)?|[-+]?\d+(?:,\d+|\.\d+)?")
_PERCENT_RE = re.compile(r"([-+]?\d{1,3}(?:[.\s]\d{3})*(?:,\d+|\.\d+)?|[-+]?\d+(?:,\d+|\.\d+)?)\s*%")
_RULE_PARTS_RE = re.compile(r"\s*\|\s*")
_DRIFT_SEVERITIES = {"partial", "failed"}
_PARSE_MODES = {"first_integer", "first_number", "first_percent"}


@dataclass(frozen=True)
class ExtractionDirective:
    """Parsed extraction directive from one mapping rule.

    Attributes:
        label: Expected label/token that must be found in slide text.
        parse_mode: Numeric parsing mode (`first_integer`, `first_number`,
            `first_percent`).
    """

    label: str
    parse_mode: str


@dataclass(frozen=True)
class DriftFinding:
    """Layout drift finding for one rule/slide extraction miss."""

    metric_name: str
    platform: str
    reason: str
    message: str
    slide_number: int | None = None


def _infer_slide_title(slide: PptxSlide) -> str:
    """Infer slide title from first non-empty text block."""
    for text in slide.text_items:
        cleaned = str(text or "").strip()
        if cleaned:
            return cleaned
    return ""


def _parse_extraction_rule(extraction_rule: str, *, path: str) -> ExtractionDirective:
    """Parse extraction_rule text into typed directive.

    Expected format:
        `label:<text> | parse:<mode>`

    Args:
        extraction_rule: Raw rule string.
        path: Rule context string used in actionable errors.

    Returns:
        Parsed :class:`ExtractionDirective`.

    Raises:
        ValueError: If rule format is invalid or parse mode is unsupported.
    """

    text = (extraction_rule or "").strip()
    if not text:
        raise ValueError(f"{path}: extraction_rule vazio.")

    fields: dict[str, str] = {}
    for chunk in _RULE_PARTS_RE.split(text):
        if not chunk.strip():
            continue
        if ":" not in chunk:
            raise ValueError(
                f"{path}: extraction_rule invalida '{text}'. "
                "Como corrigir: usar formato 'label:<texto> | parse:<modo>'."
            )
        key, value = chunk.split(":", 1)
        key_norm = key.strip().lower()
        value_norm = value.strip()
        if not key_norm:
            raise ValueError(f"{path}: chave vazia em extraction_rule.")
        fields[key_norm] = value_norm

    label = fields.get("label", "").strip()
    parse_mode = fields.get("parse", "first_number").strip().lower()
    if not label:
        raise ValueError(
            f"{path}: extraction_rule sem label esperado. "
            "Como corrigir: incluir 'label:<texto visivel no slide>'."
        )
    if parse_mode not in _PARSE_MODES:
        raise ValueError(
            f"{path}: parse mode invalido '{parse_mode}'. "
            f"Como corrigir: usar parse em {sorted(_PARSE_MODES)}."
        )
    return ExtractionDirective(label=label, parse_mode=parse_mode)


def _find_label_text(text_items: Sequence[str], label: str) -> str | None:
    """Return first slide text item containing expected label substring."""
    needle = label.casefold()
    for text in text_items:
        candidate = str(text or "").strip()
        if not candidate:
            continue
        if needle in candidate.casefold():
            return candidate
    return None


def _normalize_decimal_token(token: str) -> str:
    """Normalize localized numeric token into Decimal-compatible format."""
    text = re.sub(r"\s+", "", token or "")
    if not text:
        raise InvalidOperation("empty token")

    has_dot = "." in text
    has_comma = "," in text
    if has_dot and has_comma:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif has_comma:
        left, right = text.rsplit(",", 1)
        if right.isdigit() and len(right) <= 2:
            text = f"{left.replace(',', '')}.{right}"
        else:
            text = text.replace(",", "")
    return text


def _parse_decimal(token: str) -> Decimal | None:
    """Parse numeric token into Decimal when possible."""
    try:
        normalized = _normalize_decimal_token(token)
        return Decimal(normalized)
    except (InvalidOperation, ValueError):
        return None


def _parse_metric_value(text: str, parse_mode: str) -> tuple[Decimal | None, str | None]:
    """Parse numeric metric value from text according to parse mode."""
    candidate = str(text or "")
    if parse_mode == "first_percent":
        match = _PERCENT_RE.search(candidate)
        if not match:
            return None, None
        token = match.group(1)
        return _parse_decimal(token), token

    if parse_mode == "first_integer":
        match = _INTEGER_RE.search(candidate)
        if not match:
            return None, None
        token = match.group(0)
        digits = re.sub(r"(?<=\d)[\.\s](?=\d{3}\b)", "", token)
        digits = digits.replace(" ", "")
        return _parse_decimal(digits), token

    match = _NUMBER_RE.search(candidate)
    if not match:
        return None, None
    token = match.group(0)
    return _parse_decimal(token), token


def _extract_social_metrics_with_findings(
    pptx_path: str | Path,
    mapping_rules: Sequence[PptxMappingRule],
) -> tuple[list[dict[str, Any]], list[DriftFinding]]:
    """Extract social metrics and collect drift findings in one pass.

    Args:
        pptx_path: Source presentation path.
        mapping_rules: Validated mapping rules.

    Returns:
        Tuple of:
        - extracted metric rows
        - drift findings for unmatched slides/labels/values
    """

    slides = list(iter_slides(pptx_path))
    extracted_rows: list[dict[str, Any]] = []
    findings: list[DriftFinding] = []

    for rule_index, rule in enumerate(mapping_rules):
        directive = _parse_extraction_rule(
            rule.extraction_rule,
            path=f"mapping_rules[{rule_index}]",
        )
        matching_slides: list[PptxSlide] = []
        for slide in slides:
            slide_title = _infer_slide_title(slide)
            if rule.matches(slide_number=slide.slide_number, slide_title=slide_title):
                matching_slides.append(slide)

        if not matching_slides:
            findings.append(
                DriftFinding(
                    metric_name=rule.metric_name,
                    platform=rule.platform,
                    reason="slide_not_matched",
                    message=(
                        "Regra nao encontrou slide correspondente por slide_number/title_regex."
                    ),
                )
            )
            continue

        for slide in matching_slides:
            slide_title = _infer_slide_title(slide)
            evidence_text = _find_label_text(slide.text_items, directive.label)
            if evidence_text is None:
                findings.append(
                    DriftFinding(
                        metric_name=rule.metric_name,
                        platform=rule.platform,
                        reason="label_not_found",
                        message=(
                            f"Label esperado '{directive.label}' nao encontrado no slide."
                        ),
                        slide_number=slide.slide_number,
                    )
                )
                continue

            metric_value, value_raw = _parse_metric_value(evidence_text, directive.parse_mode)
            if metric_value is None:
                findings.append(
                    DriftFinding(
                        metric_name=rule.metric_name,
                        platform=rule.platform,
                        reason="value_not_found",
                        message=(
                            f"Nenhum valor numerico encontrado para parse '{directive.parse_mode}' "
                            f"no texto '{evidence_text}'."
                        ),
                        slide_number=slide.slide_number,
                    )
                )
                continue

            extracted_rows.append(
                {
                    "slide_number": slide.slide_number,
                    "slide_title": slide_title,
                    "lineage_location": slide.lineage_location,
                    "platform": rule.platform,
                    "metric_name": rule.metric_name,
                    "metric_value": metric_value,
                    "metric_value_raw": value_raw,
                    "unit": rule.unit,
                    "evidence_label": directive.label,
                    "evidence_text": evidence_text,
                    "extraction_rule": rule.extraction_rule,
                    "raw_payload": {
                        "slide_text_items": list(slide.text_items),
                        "lineage_location": slide.lineage_location,
                    },
                }
            )

    return extracted_rows, findings


def extract_social_metrics(
    pptx_path: str | Path,
    mapping_rules: Sequence[PptxMappingRule],
) -> Iterator[dict[str, Any]]:
    """Extract social metrics from PPTX using mapping rules.

    Args:
        pptx_path: Source presentation path.
        mapping_rules: Validated mapping rules.

    Yields:
        Extracted row dictionaries containing:
        `slide_number`, `platform`, `metric_name`, `metric_value`, `unit`,
        and evidence/lineage fields.

    Raises:
        ValueError: If mapping rules contain invalid extraction directives.
        OSError: If PPTX cannot be read.
    """

    rows, _ = _extract_social_metrics_with_findings(pptx_path, mapping_rules)
    for row in rows:
        yield row


def _coerce_drift_severity(value: str) -> str:
    """Normalize drift severity and validate supported domain."""
    normalized = (value or "").strip().lower()
    if normalized not in _DRIFT_SEVERITIES:
        raise ValueError(
            "drift severity invalida. Como corrigir: usar drift_severity em {partial, failed}."
        )
    return normalized


def _summarize_findings(findings: Sequence[DriftFinding]) -> str:
    """Build compact actionable summary text for drift findings."""
    parts = [
        (
            f"{item.metric_name}/{item.platform}"
            f"{f'@slide:{item.slide_number}' if item.slide_number else ''}"
            f" -> {item.reason}: {item.message}"
        )
        for item in findings
    ]
    return " | ".join(parts)


def load_social_metrics_to_staging(
    *,
    source_id: str,
    pptx_path: str | Path,
    event_id: int | None = None,
    mapping_rules: Sequence[PptxMappingRule],
    lineage_policy: str = "required",
    severity_on_missing: str = "partial",
    drift_severity: str = "partial",
) -> dict[str, Any]:
    """Load extracted PPTX social metrics into staging with slide lineage.

    Args:
        source_id: Stable source identifier.
        pptx_path: Source `.pptx` path.
        event_id: Optional event identifier used during session resolution.
        mapping_rules: Mapping rules used for extraction.
        lineage_policy: Lineage enforcement policy (`required` or `optional`).
        severity_on_missing: Status when required lineage is missing.
        drift_severity: Status when layout drift is detected (`partial` or
            `failed`).

    Returns:
        Summary with source/run identifiers, counts and final status.

    Raises:
        ValueError: If drift severity is invalid, extraction fails, or drift is
            configured as fatal (`failed`).
        OSError: If file cannot be read.
    """

    normalized_drift = _coerce_drift_severity(drift_severity)
    with Session(engine) as session:
        source = register_source_from_path(session, source_id, Path(pptx_path))
        run = start_ingestion_run(session, source.source_id, "extract_pptx_social_metrics")
        loaded_rows: list[StgSocialMetric] = []
        session_resolution_findings: list[str] = []

        try:
            extracted_rows, drift_findings = _extract_social_metrics_with_findings(
                pptx_path,
                mapping_rules,
            )
            for extracted in extracted_rows:
                location_value = format_location("slide", {"number": int(extracted["slide_number"])})
                evidence_text = (
                    f"slide_title={extracted['slide_title'] or '(sem_titulo)'}; "
                    f"label={extracted['evidence_label']}; "
                    f"text={extracted['evidence_text']}"
                )
                lineage_ref = create_lineage_ref(
                    session,
                    source_id=source.source_id,
                    ingestion_id=run.id,
                    location_type="slide",
                    location_value=location_value,
                    evidence_text=evidence_text,
                    is_aggregated_metric=True,
                )
                resolution = resolve_session_reference(
                    session,
                    event_id=event_id,
                    raw_session_fields={
                        "source_id": source.source_id,
                        "session_name": extracted.get("slide_title"),
                        "slide_title": extracted.get("slide_title"),
                    },
                )
                row_model = StgSocialMetric(
                    source_id=source.source_id,
                    ingestion_id=int(run.id),
                    lineage_ref_id=int(lineage_ref.id),
                    event_id=resolution.event_id,
                    session_id=resolution.session_id,
                    slide_number=int(extracted["slide_number"]),
                    slide_title=extracted.get("slide_title"),
                    location_value=location_value,
                    platform=str(extracted["platform"]),
                    metric_name=str(extracted["metric_name"]),
                    metric_value=extracted["metric_value"],
                    metric_value_raw=extracted.get("metric_value_raw"),
                    unit=str(extracted["unit"]),
                    evidence_label=str(extracted["evidence_label"]),
                    evidence_text=str(extracted["evidence_text"]),
                    extraction_rule=str(extracted["extraction_rule"]),
                    session_resolution_finding=(
                        resolution.finding.message if resolution.finding else None
                    ),
                    raw_payload_json=json.dumps(extracted.get("raw_payload", {}), ensure_ascii=False),
                )
                loaded_rows.append(row_model)
                if resolution.finding:
                    session_resolution_findings.append(
                        (
                            f"metric={row_model.metric_name}; "
                            f"slide={row_model.slide_number}; "
                            f"code={resolution.finding.code}; "
                            f"message={resolution.finding.message}"
                        )
                    )

            if loaded_rows:
                session.add_all(loaded_rows)
                session.commit()

            enforce_lineage_policy(
                session,
                ingestion_id=int(run.id),
                dataset_name="stg_social_metrics",
                records=loaded_rows,
                policy=lineage_policy,
                severity_on_missing=severity_on_missing,
            )

            session_finding_summary = (
                " | ".join(session_resolution_findings[:10])
                if session_resolution_findings
                else ""
            )
            if drift_findings:
                drift_message = _summarize_findings(drift_findings)
                status = (
                    IngestionStatus.FAILED
                    if normalized_drift == "failed"
                    else IngestionStatus.PARTIAL
                )
                finish_ingestion_run(
                    session,
                    ingestion_id=int(run.id),
                    status=status,
                    notes=(
                        f"Drift de layout detectado em {len(drift_findings)} regra(s): "
                        f"{drift_message}; "
                        f"session_resolution_findings={len(session_resolution_findings)}; "
                        f"session_details={session_finding_summary}"
                    ),
                )
                if normalized_drift == "failed":
                    raise ValueError(
                        f"Drift de layout detectado para stg_social_metrics: {drift_message}"
                    )
                return {
                    "source_id": source.source_id,
                    "ingestion_id": int(run.id),
                    "metrics_loaded": len(loaded_rows),
                    "drift_count": len(drift_findings),
                    "findings_count": len(drift_findings) + len(session_resolution_findings),
                    "status": IngestionStatus.PARTIAL.value,
                }

            if session_resolution_findings:
                finish_ingestion_run(
                    session,
                    ingestion_id=int(run.id),
                    status=IngestionStatus.PARTIAL,
                    notes=(
                        f"session_resolution_findings={len(session_resolution_findings)}; "
                        f"session_details={session_finding_summary}"
                    ),
                )
                return {
                    "source_id": source.source_id,
                    "ingestion_id": int(run.id),
                    "metrics_loaded": len(loaded_rows),
                    "drift_count": 0,
                    "findings_count": len(session_resolution_findings),
                    "status": IngestionStatus.PARTIAL.value,
                }

            finish_ingestion_run(
                session,
                ingestion_id=int(run.id),
                status=IngestionStatus.SUCCESS,
                notes=f"{len(loaded_rows)} metricas carregadas em stg_social_metrics.",
            )
            return {
                "source_id": source.source_id,
                "ingestion_id": int(run.id),
                "metrics_loaded": len(loaded_rows),
                "drift_count": 0,
                "findings_count": 0,
                "status": IngestionStatus.SUCCESS.value,
            }
        except Exception as exc:
            persisted_run = session.get(type(run), run.id)
            if persisted_run is not None and persisted_run.finished_at is None:
                finish_ingestion_run(
                    session,
                    ingestion_id=int(run.id),
                    status=IngestionStatus.FAILED,
                    notes=f"Falha no load stg_social_metrics: {exc}",
                )
            raise


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for PPTX social metrics extraction and staging load."""

    parser = argparse.ArgumentParser(prog="pptx-social-metrics")
    parser.add_argument("--source-id", required=True, help="Stable source identifier.")
    parser.add_argument("--pptx", required=True, help="Path to source PPTX file.")
    parser.add_argument(
        "--event-id",
        type=int,
        default=None,
        help="Optional event identifier used for session resolution.",
    )
    parser.add_argument(
        "--mapping-yml",
        required=True,
        help="Path to mapping YAML with PPTX metric rules.",
    )
    parser.add_argument(
        "--lineage-policy",
        default="required",
        choices=("required", "optional"),
        help="Lineage enforcement policy for staging load.",
    )
    parser.add_argument(
        "--severity-on-missing",
        default="partial",
        choices=("partial", "failed"),
        help="Final ingestion status when required lineage is missing.",
    )
    parser.add_argument(
        "--drift-severity",
        default="partial",
        choices=("partial", "failed"),
        help="Status when mapping rule drifts (missing label/slide/value).",
    )
    args = parser.parse_args(argv)

    mapping = load_pptx_mapping(args.mapping_yml)
    result = load_social_metrics_to_staging(
        source_id=args.source_id,
        pptx_path=args.pptx,
        event_id=args.event_id,
        mapping_rules=mapping.rules,
        lineage_policy=args.lineage_policy,
        severity_on_missing=args.severity_on_missing,
        drift_severity=args.drift_severity,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
