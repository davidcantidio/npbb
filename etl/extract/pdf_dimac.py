"""DIMAC PDF metric extractor with gap-aware staging load.

This module extracts DIMAC metric candidates from text/quadro PDF content using
regex anchors. Each metric becomes either:
- `ok`: value parsed with page/evidence lineage
- `gap`: explicit missing anchor/value evidence record
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Iterator, Sequence

from sqlmodel import Session

try:  # package execution (repo root at `npbb`)
    from etl.extract.pdf_metric_candidates import (
        MetricCandidate,
        MetricRule,
        extract_metric_candidates_from_pdf,
    )
except ModuleNotFoundError:  # pragma: no cover - fallback for `npbb.etl.*` imports
    from npbb.etl.extract.pdf_metric_candidates import (
        MetricCandidate,
        MetricRule,
        extract_metric_candidates_from_pdf,
    )

try:  # pragma: no cover - import style depends on caller cwd
    from core.registry.location_ref import format_location
except ModuleNotFoundError:  # pragma: no cover
    from npbb.core.registry.location_ref import format_location

try:  # pragma: no cover
    from app.db.database import engine
    from app.models.etl_registry import IngestionStatus
    from app.models.stg_dimac_mtc import MetricExtractionStatus, StgDimacMetric
    from app.services.etl_lineage_service import create_lineage_ref
    from app.services.etl_registry_service import (
        enforce_lineage_policy,
        finish_ingestion_run,
        register_source_from_path,
        start_ingestion_run,
    )
except ModuleNotFoundError:  # pragma: no cover
    BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))
    from app.db.database import engine
    from app.models.etl_registry import IngestionStatus
    from app.models.stg_dimac_mtc import MetricExtractionStatus, StgDimacMetric
    from app.services.etl_lineage_service import create_lineage_ref
    from app.services.etl_registry_service import (
        enforce_lineage_policy,
        finish_ingestion_run,
        register_source_from_path,
        start_ingestion_run,
    )


_GAP_SEVERITIES = {"partial", "failed"}
_DIMAC_RULES: tuple[MetricRule, ...] = (
    MetricRule(
        metric_key="dimac.profile.age_distribution",
        metric_label="Distribuicao por faixa etaria",
        anchor_pattern=r"(faixa\s+et[aá]ria|distribui[cç][aã]o\s+et[aá]ria|idade)",
        unit="percent",
        parse_mode="first_percent",
    ),
    MetricRule(
        metric_key="dimac.profile.gender_distribution",
        metric_label="Distribuicao por genero",
        anchor_pattern=r"(g[eê]nero|sexo|distribui[cç][aã]o\s+por\s+sexo)",
        unit="percent",
        parse_mode="first_percent",
    ),
    MetricRule(
        metric_key="dimac.satisfaction.overall",
        metric_label="Satisfacao geral",
        anchor_pattern=r"(satisfa[cç][aã]o|satisfaction|avalia[cç][aã]o\s+geral)",
        unit="percent",
        parse_mode="first_percent",
    ),
)


def _coerce_gap_severity(value: str) -> str:
    """Validate severity domain for gap findings.

    Args:
        value: Raw severity value.

    Returns:
        Normalized severity (`partial` or `failed`).

    Raises:
        ValueError: If severity is unsupported.
    """

    normalized = (value or "").strip().lower()
    if normalized not in _GAP_SEVERITIES:
        raise ValueError(
            "gap severity invalida. Como corrigir: usar gap_severity em {partial, failed}."
        )
    return normalized


def _summarize_gaps(candidates: Sequence[MetricCandidate]) -> str:
    """Build compact actionable summary of gap candidates.

    Args:
        candidates: Candidate list including `ok` and `gap` rows.

    Returns:
        Compact summary text for ingestion notes.
    """

    parts = [
        (
            f"{item.metric_key}"
            f"{f'@page:{item.pdf_page}' if item.pdf_page else ''}"
            f" -> {item.gap_reason or 'gap'}"
        )
        for item in candidates
        if item.status == "gap"
    ]
    return " | ".join(parts)


def extract_dimac_pdf_metrics(pdf_path: str | Path) -> Iterator[MetricCandidate]:
    """Extract DIMAC metric candidates from one PDF.

    Args:
        pdf_path: Source PDF path.

    Yields:
        `MetricCandidate` rows for DIMAC metrics.

    Raises:
        ValueError: If rule configuration is invalid.
        OSError: If file cannot be read.
    """

    candidates, _ = extract_metric_candidates_from_pdf(pdf_path, _DIMAC_RULES)
    for candidate in candidates:
        yield candidate


def load_dimac_pdf_to_staging(
    *,
    source_id: str,
    pdf_path: str | Path,
    lineage_policy: str = "required",
    severity_on_missing: str = "partial",
    gap_severity: str = "partial",
) -> dict[str, Any]:
    """Load DIMAC metric candidates into `stg_dimac_metrics`.

    Args:
        source_id: Stable source identifier.
        pdf_path: Source PDF path.
        lineage_policy: Lineage enforcement policy for `ok` rows.
        severity_on_missing: Status when required lineage is missing.
        gap_severity: Status when one or more candidates are `gap`.

    Returns:
        Summary dictionary with counts, ingestion status and profile payload.

    Raises:
        ValueError: If gap severity is invalid or extraction fails with
            `gap_severity=failed`.
        OSError: If file cannot be read.
    """

    normalized_gap_severity = _coerce_gap_severity(gap_severity)
    with Session(engine) as session:
        source = register_source_from_path(session, source_id, Path(pdf_path))
        run = start_ingestion_run(session, source.source_id, "extract_pdf_dimac_metrics")
        loaded_rows: list[StgDimacMetric] = []
        rows_requiring_lineage: list[StgDimacMetric] = []
        try:
            candidates, profile = extract_metric_candidates_from_pdf(pdf_path, _DIMAC_RULES)
            for candidate in candidates:
                lineage_ref_id: int | None = None
                location_value: str | None = None
                if candidate.status == "ok":
                    if candidate.pdf_page is None or not candidate.evidence_text:
                        candidate = MetricCandidate(
                            metric_key=candidate.metric_key,
                            metric_label=candidate.metric_label,
                            status="gap",
                            metric_value=None,
                            metric_value_raw=None,
                            unit=candidate.unit,
                            pdf_page=candidate.pdf_page,
                            evidence_text=candidate.evidence_text,
                            extraction_rule=candidate.extraction_rule,
                            gap_reason="missing_lineage_fields",
                            raw_payload={
                                **candidate.raw_payload,
                                "reason": "missing_lineage_fields",
                            },
                        )
                    else:
                        location_value = format_location("page", {"number": candidate.pdf_page})
                        lineage_ref = create_lineage_ref(
                            session,
                            source_id=source.source_id,
                            ingestion_id=run.id,
                            location_type="page",
                            location_value=location_value,
                            evidence_text=candidate.evidence_text,
                            is_aggregated_metric=True,
                        )
                        lineage_ref_id = int(lineage_ref.id)

                status = (
                    MetricExtractionStatus.OK
                    if candidate.status == "ok"
                    else MetricExtractionStatus.GAP
                )
                row_model = StgDimacMetric(
                    source_id=source.source_id,
                    ingestion_id=int(run.id),
                    lineage_ref_id=lineage_ref_id,
                    metric_key=candidate.metric_key,
                    metric_label=candidate.metric_label,
                    metric_value=candidate.metric_value,
                    metric_value_raw=candidate.metric_value_raw,
                    unit=candidate.unit,
                    status=status,
                    gap_reason=candidate.gap_reason,
                    pdf_page=candidate.pdf_page,
                    location_value=location_value,
                    evidence_text=candidate.evidence_text,
                    extraction_rule=candidate.extraction_rule,
                    raw_payload_json=json.dumps(candidate.raw_payload, ensure_ascii=False, default=str),
                )
                loaded_rows.append(row_model)
                if row_model.status == MetricExtractionStatus.OK:
                    rows_requiring_lineage.append(row_model)

            if loaded_rows:
                session.add_all(loaded_rows)
                session.commit()

            enforce_lineage_policy(
                session,
                ingestion_id=int(run.id),
                dataset_name="stg_dimac_metrics",
                records=rows_requiring_lineage,
                policy=lineage_policy,
                severity_on_missing=severity_on_missing,
            )

            gap_count = sum(1 for row in loaded_rows if row.status == MetricExtractionStatus.GAP)
            ok_count = len(loaded_rows) - gap_count
            if gap_count > 0:
                gap_summary = _summarize_gaps(candidates)
                status = (
                    IngestionStatus.FAILED
                    if normalized_gap_severity == "failed"
                    else IngestionStatus.PARTIAL
                )
                finish_ingestion_run(
                    session,
                    ingestion_id=int(run.id),
                    status=status,
                    notes=(
                        f"pdf_profile={json.dumps(profile, ensure_ascii=False, sort_keys=True)}; "
                        f"gaps={gap_summary}"
                    ),
                )
                if normalized_gap_severity == "failed":
                    raise ValueError(
                        "Extracao DIMAC falhou por lacunas de evidencia/valor. "
                        f"Detalhes: {gap_summary}"
                    )
                return {
                    "source_id": source.source_id,
                    "ingestion_id": int(run.id),
                    "metrics_loaded": len(loaded_rows),
                    "ok_count": ok_count,
                    "gap_count": gap_count,
                    "status": IngestionStatus.PARTIAL.value,
                    "profile": profile,
                }

            finish_ingestion_run(
                session,
                ingestion_id=int(run.id),
                status=IngestionStatus.SUCCESS,
                notes=(
                    f"pdf_profile={json.dumps(profile, ensure_ascii=False, sort_keys=True)}; "
                    f"{len(loaded_rows)} metricas carregadas em stg_dimac_metrics."
                ),
            )
            return {
                "source_id": source.source_id,
                "ingestion_id": int(run.id),
                "metrics_loaded": len(loaded_rows),
                "ok_count": ok_count,
                "gap_count": 0,
                "status": IngestionStatus.SUCCESS.value,
                "profile": profile,
            }
        except Exception as exc:
            persisted_run = session.get(type(run), run.id)
            if persisted_run is not None and persisted_run.finished_at is None:
                finish_ingestion_run(
                    session,
                    ingestion_id=int(run.id),
                    status=IngestionStatus.FAILED,
                    notes=f"Falha no load stg_dimac_metrics: {exc}",
                )
            raise


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for DIMAC PDF extraction and staging load."""

    parser = argparse.ArgumentParser(prog="pdf-dimac")
    parser.add_argument("--source-id", required=True, help="Stable source identifier.")
    parser.add_argument("--pdf", required=True, help="Path to source PDF file.")
    parser.add_argument(
        "--lineage-policy",
        default="required",
        choices=("required", "optional"),
        help="Lineage enforcement policy for extracted ok metrics.",
    )
    parser.add_argument(
        "--severity-on-missing",
        default="partial",
        choices=("partial", "failed"),
        help="Final ingestion status when required lineage is missing.",
    )
    parser.add_argument(
        "--gap-severity",
        default="partial",
        choices=("partial", "failed"),
        help="Final ingestion status when one or more metrics are GAP.",
    )
    args = parser.parse_args(argv)

    result = load_dimac_pdf_to_staging(
        source_id=args.source_id,
        pdf_path=args.pdf,
        lineage_policy=args.lineage_policy,
        severity_on_missing=args.severity_on_missing,
        gap_severity=args.gap_severity,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
