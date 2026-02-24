"""PDF access-control extractor and staging loader with page lineage.

This module extracts session-level access-control numbers from PDFs and stores
them in staging with one lineage reference per page (`location_type=page`).

Extraction strategy:
- primary: table-like rows from PDF pages (pdfplumber),
- fallback: line parsing from extracted text when table parsing is unstable,
- guarded by PDF profile classification to detect scan/image-only documents.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterator
import unicodedata

from sqlmodel import Session

try:  # package execution (repo root at `npbb`)
    from etl.extract.pdf_classify import PdfClassificationError, classify_pdf
    from etl.extract.pdf_assisted_specs import (
        PdfAssistedSpecsError,
        extract_with_spec,
        load_pdf_table_specs,
    )
except ModuleNotFoundError:  # pragma: no cover - fallback for `npbb.etl.*` imports
    from npbb.etl.extract.pdf_classify import PdfClassificationError, classify_pdf
    from npbb.etl.extract.pdf_assisted_specs import (
        PdfAssistedSpecsError,
        extract_with_spec,
        load_pdf_table_specs,
    )

try:  # pragma: no cover - import style depends on caller cwd
    from core.registry.location_ref import format_location
except ModuleNotFoundError:  # pragma: no cover
    from npbb.core.registry.location_ref import format_location

try:  # pragma: no cover
    from app.db.database import engine
    from app.models.etl_registry import IngestionStatus
    from app.models.stg_access_control import StgAccessControlSession
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
    from app.models.stg_access_control import StgAccessControlSession
    from app.services.etl_lineage_service import create_lineage_ref
    from app.services.etl_registry_service import (
        enforce_lineage_policy,
        finish_ingestion_run,
        register_source_from_path,
        start_ingestion_run,
    )
    from app.services.session_resolver import resolve_session_reference


_NUMBER_RE = re.compile(r"[-+]?\d{1,3}(?:[.\s]\d{3})*(?:,\d+|\.\d+)?|[-+]?\d+(?:,\d+|\.\d+)?")
_TEXT_ROW_RE = re.compile(
    r"(?P<session>[A-Za-zÀ-ÿ0-9\-\s]{2,}?\d{1,2}/\d{1,2})\s+"
    r"(?P<ing>\d+)\s+"
    r"(?P<inv>\d+)\s+"
    r"(?P<bloq>\d+)\s+"
    r"(?P<pres>\d+)\s+"
    r"(?P<aus>\d+)\s+"
    r"(?P<pct>\d+(?:[.,]\d+)?)%?",
    flags=re.IGNORECASE,
)
_NON_EXTRACTABLE_STRATEGIES = {"ocr_or_assisted", "manual_assisted", "empty_document"}
_DRIFT_SEVERITIES = {"partial", "failed"}

_HEADER_KEYWORDS = {
    "session_name": ("sessao", "session", "show"),
    "ingressos_validos": ("ingressos validos", "validos", "validos total", "ingressos"),
    "invalidos": ("invalidos", "inválidos"),
    "bloqueados": ("bloqueados",),
    "presentes": ("presentes", "compareceram"),
    "ausentes": ("ausentes", "faltas"),
    "comparecimento_pct": ("comparecimento", "presenca", "presença", "taxa"),
}


@dataclass(frozen=True)
class AccessControlFinding:
    """Extraction finding used to report layout drift or non-extractable PDFs."""

    code: str
    message: str
    page_number: int | None = None


def _normalize_text(value: Any) -> str:
    """Normalize text for matching/parsing."""
    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _normalize_header_key(value: str) -> str:
    """Normalize header text removing accents and punctuation noise."""
    text = _normalize_text(value).casefold()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^a-z0-9% ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _to_decimal(value: Any) -> Decimal | None:
    """Parse numeric-like values into Decimal."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    raw = _normalize_text(value).replace(" ", "")
    if not raw:
        return None
    has_dot = "." in raw
    has_comma = "," in raw
    if has_dot and has_comma:
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif has_comma:
        left, right = raw.rsplit(",", 1)
        if right.isdigit() and len(right) <= 2:
            raw = f"{left.replace(',', '')}.{right}"
        else:
            raw = raw.replace(",", "")
    try:
        return Decimal(raw)
    except InvalidOperation:
        return None


def _to_int(value: Any) -> int | None:
    """Parse integer-like values when possible."""
    parsed = _to_decimal(value)
    if parsed is None:
        return None
    try:
        return int(parsed)
    except Exception:
        return None


def _to_percent(value: Any) -> Decimal | None:
    """Parse percentage-like values, accepting optional '%' suffix."""
    if value is None:
        return None
    text = _normalize_text(value).replace("%", "")
    return _to_decimal(text)


def _detect_header_map(header_row: list[str]) -> dict[str, int]:
    """Map canonical field names to header indices using keyword matching."""
    mapping: dict[str, int] = {}
    normalized = [_normalize_header_key(cell) for cell in header_row]
    for index, cell in enumerate(normalized):
        if not cell:
            continue
        for target, keywords in _HEADER_KEYWORDS.items():
            if target in mapping:
                continue
            if any(keyword in cell for keyword in keywords):
                mapping[target] = index
    return mapping


def _choose_session_column(mapping: dict[str, int], header_row: list[str]) -> int | None:
    """Choose session column index with fallback to first textual column."""
    if "session_name" in mapping:
        return mapping["session_name"]
    for idx, cell in enumerate(header_row):
        if _normalize_text(cell):
            return idx
    return None


def _extract_rows_from_table(
    table: list[list[Any]],
    *,
    page_number: int,
) -> list[dict[str, Any]]:
    """Extract canonical access-control rows from one raw table payload."""
    cleaned_rows: list[list[str]] = []
    for row in table:
        current = [_normalize_text(cell) for cell in (row or [])]
        if any(current):
            cleaned_rows.append(current)
    if len(cleaned_rows) < 2:
        return []

    header = cleaned_rows[0]
    header_map = _detect_header_map(header)
    session_col = _choose_session_column(header_map, header)
    if session_col is None:
        return []

    evidence_header = " | ".join(cell for cell in header if cell)
    out: list[dict[str, Any]] = []
    for row in cleaned_rows[1:]:
        if session_col >= len(row):
            continue
        session_name = _normalize_text(row[session_col])
        if not session_name:
            continue
        get = lambda key: row[header_map[key]] if key in header_map and header_map[key] < len(row) else None  # noqa: E731
        out.append(
            {
                "pdf_page": page_number,
                "session_name": session_name,
                "ingressos_validos": _to_int(get("ingressos_validos")),
                "invalidos": _to_int(get("invalidos")),
                "bloqueados": _to_int(get("bloqueados")),
                "presentes": _to_int(get("presentes")),
                "ausentes": _to_int(get("ausentes")),
                "comparecimento_pct": _to_percent(get("comparecimento_pct")),
                "table_header": evidence_header or None,
                "evidence_text": evidence_header or f"pagina {page_number}",
                "__raw_payload": {"header": header, "row": row},
            }
        )
    return out


def _extract_rows_from_text(page_text: str, *, page_number: int) -> list[dict[str, Any]]:
    """Extract canonical rows from text lines when table parser is insufficient."""
    out: list[dict[str, Any]] = []
    for line in (page_text or "").splitlines():
        normalized = _normalize_text(line)
        if not normalized:
            continue
        match = _TEXT_ROW_RE.search(normalized)
        if not match:
            continue
        out.append(
            {
                "pdf_page": page_number,
                "session_name": _normalize_text(match.group("session")),
                "ingressos_validos": _to_int(match.group("ing")),
                "invalidos": _to_int(match.group("inv")),
                "bloqueados": _to_int(match.group("bloq")),
                "presentes": _to_int(match.group("pres")),
                "ausentes": _to_int(match.group("aus")),
                "comparecimento_pct": _to_percent(match.group("pct")),
                "table_header": "text_fallback",
                "evidence_text": normalized,
                "__raw_payload": {"line": normalized},
            }
        )
    return out


def _extract_with_findings(
    pdf_path: str | Path,
    *,
    assisted_spec_path: str | Path | None = None,
    assisted_table_id: str = "access_control_default",
) -> tuple[list[dict[str, Any]], list[AccessControlFinding], dict[str, Any]]:
    """Extract rows plus findings/profile summary for loader decisions."""
    profile = classify_pdf(pdf_path)
    profile_summary = profile.summary()
    findings: list[AccessControlFinding] = []
    extracted: list[dict[str, Any]] = []
    can_try_automatic = profile.suggested_strategy not in _NON_EXTRACTABLE_STRATEGIES
    can_try_assisted = assisted_spec_path is not None

    if not can_try_automatic and not can_try_assisted:
        guidance = (
            "PDF nao extraivel automaticamente com confianca. "
            "Como corrigir: usar OCR/assistido e revisar template manual de controle de acesso."
        )
        return (
            [],
            [
                AccessControlFinding(
                    code="NON_EXTRACTABLE_PDF",
                    message=f"{guidance} strategy={profile.suggested_strategy}",
                )
            ],
            profile_summary,
        )

    try:
        import pdfplumber  # type: ignore import-not-found
    except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
        raise PdfClassificationError(
            "Dependencia ausente: instale 'pdfplumber' para extracao de controle de acesso."
        ) from exc

    seen_keys: set[tuple[int, str]] = set()
    if can_try_automatic:
        with pdfplumber.open(str(Path(pdf_path).expanduser())) as document:
            for page_index, page in enumerate(document.pages, start=1):
                page_rows: list[dict[str, Any]] = []
                for raw_table in page.extract_tables() or []:
                    page_rows.extend(_extract_rows_from_table(raw_table, page_number=page_index))

                if not page_rows:
                    page_text = page.extract_text() or ""
                    page_rows.extend(_extract_rows_from_text(page_text, page_number=page_index))

                for row in page_rows:
                    dedupe_key = (int(row["pdf_page"]), str(row["session_name"]).casefold())
                    if dedupe_key in seen_keys:
                        continue
                    seen_keys.add(dedupe_key)
                    extracted.append(row)

    if not extracted and can_try_assisted:
        try:
            specs = load_pdf_table_specs(assisted_spec_path)
            assisted_rows = extract_with_spec(
                pdf_path,
                specs,
                table_id=assisted_table_id,
            )
            for row in assisted_rows:
                session_name = str(row.get("session_name") or "").strip()
                if not session_name:
                    continue
                dedupe_key = (int(row.get("pdf_page") or 0), session_name.casefold())
                if dedupe_key in seen_keys:
                    continue
                seen_keys.add(dedupe_key)
                extracted.append(
                    {
                        "pdf_page": int(row.get("pdf_page") or 0),
                        "session_name": session_name,
                        "ingressos_validos": _to_int(row.get("ingressos_validos")),
                        "invalidos": _to_int(row.get("invalidos")),
                        "bloqueados": _to_int(row.get("bloqueados")),
                        "presentes": _to_int(row.get("presentes")),
                        "ausentes": _to_int(row.get("ausentes")),
                        "comparecimento_pct": _to_percent(row.get("comparecimento_pct")),
                        "table_header": row.get("table_header"),
                        "evidence_text": row.get("evidence_text"),
                        "__lineage_bbox": row.get("__lineage_bbox"),
                        "__spec_table_id": row.get("__spec_table_id"),
                        "__raw_payload": row.get("__raw_payload", {}),
                    }
                )
        except (PdfAssistedSpecsError, FileNotFoundError) as exc:
            findings.append(
                AccessControlFinding(
                    code="ASSISTED_SPEC_FAILED",
                    message=f"Falha no fallback assistido: {exc}",
                )
            )

    if not extracted:
        findings.append(
            AccessControlFinding(
                code="NO_ROWS_EXTRACTED",
                message=(
                    "Nenhuma linha de controle de acesso foi extraida automaticamente. "
                    "Como corrigir: revisar layout do PDF e executar fluxo assistido."
                ),
            )
        )
    return extracted, findings, profile_summary


def extract_access_control_pdf(pdf_path: str | Path) -> Iterator[dict[str, Any]]:
    """Extract access-control rows from PDF pages/tables.

    Args:
        pdf_path: Source PDF path.

    Yields:
        Canonical row dictionaries with session metrics and page evidence.

    Raises:
        PdfClassificationError: If PDF classification/parsing fails.
        OSError: If file cannot be read.
    """
    rows, _, _ = _extract_with_findings(pdf_path)
    for row in rows:
        yield row


def _coerce_drift_severity(value: str) -> str:
    """Normalize severity used when extraction is partial/non-extractable."""
    normalized = (value or "").strip().lower()
    if normalized not in _DRIFT_SEVERITIES:
        raise ValueError(
            "drift severity invalida. Como corrigir: usar non_extractable_severity em {partial, failed}."
        )
    return normalized


def load_access_control_pdf_to_staging(
    *,
    source_id: str,
    pdf_path: str | Path,
    event_id: int | None = None,
    lineage_policy: str = "required",
    severity_on_missing: str = "partial",
    non_extractable_severity: str = "partial",
    assisted_spec_path: str | Path | None = None,
    assisted_table_id: str = "access_control_default",
) -> dict[str, Any]:
    """Load extracted access-control rows into staging with page lineage.

    Args:
        source_id: Stable source identifier.
        pdf_path: Source PDF path.
        event_id: Optional event identifier used during session resolution.
        lineage_policy: Lineage enforcement policy (`required` or `optional`).
        severity_on_missing: Status when required lineage is missing.
        non_extractable_severity: Status for layout/non-extractable findings
            (`partial` or `failed`).
        assisted_spec_path: Optional YAML spec path for assisted extraction.
        assisted_table_id: Target table id from assisted spec file.

    Returns:
        Summary dictionary with counts, run status, and profile.

    Raises:
        ValueError: If extraction fails or severity configuration is invalid.
        OSError: If file cannot be read.
    """

    normalized_severity = _coerce_drift_severity(non_extractable_severity)
    with Session(engine) as session:
        source = register_source_from_path(session, source_id, Path(pdf_path))
        run = start_ingestion_run(session, source.source_id, "extract_pdf_access_control")
        loaded_rows: list[StgAccessControlSession] = []
        session_resolution_findings: list[str] = []
        try:
            extracted_rows, findings, profile = _extract_with_findings(
                pdf_path,
                assisted_spec_path=assisted_spec_path,
                assisted_table_id=assisted_table_id,
            )
            for extracted in extracted_rows:
                page_number = int(extracted["pdf_page"])
                location_value = format_location("page", {"number": page_number})
                lineage_ref = create_lineage_ref(
                    session,
                    source_id=source.source_id,
                    ingestion_id=run.id,
                    location_type="page",
                    location_value=location_value,
                    evidence_text=str(extracted.get("evidence_text") or f"pagina {page_number}"),
                    is_aggregated_metric=True,
                )
                resolution = resolve_session_reference(
                    session,
                    event_id=event_id,
                    raw_session_fields={
                        "source_id": source.source_id,
                        "session_name": extracted.get("session_name"),
                        "sessao": extracted.get("session_name"),
                    },
                )
                row_model = StgAccessControlSession(
                    source_id=source.source_id,
                    ingestion_id=int(run.id),
                    lineage_ref_id=int(lineage_ref.id),
                    event_id=resolution.event_id,
                    session_id=resolution.session_id,
                    pdf_page=page_number,
                    session_name=str(extracted["session_name"]),
                    ingressos_validos=extracted.get("ingressos_validos"),
                    invalidos=extracted.get("invalidos"),
                    bloqueados=extracted.get("bloqueados"),
                    presentes=extracted.get("presentes"),
                    ausentes=extracted.get("ausentes"),
                    comparecimento_pct=extracted.get("comparecimento_pct"),
                    table_header=extracted.get("table_header"),
                    evidence_text=extracted.get("evidence_text"),
                    session_resolution_finding=(
                        resolution.finding.message if resolution.finding else None
                    ),
                    raw_payload_json=json.dumps(extracted.get("__raw_payload", {}), ensure_ascii=False),
                )
                loaded_rows.append(row_model)
                if resolution.finding:
                    session_resolution_findings.append(
                        (
                            f"session={row_model.session_name}; "
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
                dataset_name="stg_access_control_sessions",
                records=loaded_rows,
                policy=lineage_policy,
                severity_on_missing=severity_on_missing,
            )

            session_finding_summary = (
                " | ".join(session_resolution_findings[:10])
                if session_resolution_findings
                else ""
            )
            if findings:
                finding_summary = " | ".join(
                    (
                        f"{item.code}"
                        f"{f'@page:{item.page_number}' if item.page_number else ''}: {item.message}"
                    )
                    for item in findings
                )
                status = (
                    IngestionStatus.FAILED
                    if normalized_severity == "failed"
                    else IngestionStatus.PARTIAL
                )
                notes = (
                    f"pdf_profile={json.dumps(profile, ensure_ascii=False, sort_keys=True)}; "
                    f"findings={finding_summary}; "
                    f"session_resolution_findings={len(session_resolution_findings)}; "
                    f"session_details={session_finding_summary}"
                )
                finish_ingestion_run(
                    session,
                    ingestion_id=int(run.id),
                    status=status,
                    notes=notes,
                )
                if normalized_severity == "failed":
                    raise ValueError(
                        "Extracao de controle de acesso falhou por nao-extracao automatica. "
                        f"Detalhes: {finding_summary}"
                    )
                return {
                    "source_id": source.source_id,
                    "ingestion_id": int(run.id),
                    "rows_loaded": len(loaded_rows),
                    "findings_count": len(findings) + len(session_resolution_findings),
                    "status": IngestionStatus.PARTIAL.value,
                    "profile": profile,
                }

            if session_resolution_findings:
                finish_ingestion_run(
                    session,
                    ingestion_id=int(run.id),
                    status=IngestionStatus.PARTIAL,
                    notes=(
                        f"pdf_profile={json.dumps(profile, ensure_ascii=False, sort_keys=True)}; "
                        f"session_resolution_findings={len(session_resolution_findings)}; "
                        f"session_details={session_finding_summary}"
                    ),
                )
                return {
                    "source_id": source.source_id,
                    "ingestion_id": int(run.id),
                    "rows_loaded": len(loaded_rows),
                    "findings_count": len(session_resolution_findings),
                    "status": IngestionStatus.PARTIAL.value,
                    "profile": profile,
                }

            finish_ingestion_run(
                session,
                ingestion_id=int(run.id),
                status=IngestionStatus.SUCCESS,
                notes=(
                    f"pdf_profile={json.dumps(profile, ensure_ascii=False, sort_keys=True)}; "
                    f"assisted_table_id={assisted_table_id if any(row.get('__spec_table_id') for row in extracted_rows) else ''}; "
                    f"{len(loaded_rows)} registros carregados em stg_access_control_sessions."
                ),
            )
            return {
                "source_id": source.source_id,
                "ingestion_id": int(run.id),
                "rows_loaded": len(loaded_rows),
                "findings_count": 0,
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
                    notes=f"Falha no load stg_access_control_sessions: {exc}",
                )
            raise


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for access-control PDF extraction and staging load."""
    parser = argparse.ArgumentParser(prog="pdf-access-control")
    parser.add_argument("--source-id", required=True, help="Stable source identifier.")
    parser.add_argument("--pdf", required=True, help="Path to source PDF file.")
    parser.add_argument(
        "--event-id",
        type=int,
        default=None,
        help="Optional event identifier used for session resolution.",
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
        "--non-extractable-severity",
        default="partial",
        choices=("partial", "failed"),
        help="Status when PDF is not extractable automatically.",
    )
    parser.add_argument(
        "--assisted-spec",
        default="",
        help="Optional YAML path for assisted extraction fallback.",
    )
    parser.add_argument(
        "--assisted-table-id",
        default="access_control_default",
        help="Table id inside assisted YAML spec.",
    )
    args = parser.parse_args(argv)

    result = load_access_control_pdf_to_staging(
        source_id=args.source_id,
        pdf_path=args.pdf,
        event_id=args.event_id,
        lineage_policy=args.lineage_policy,
        severity_on_missing=args.severity_on_missing,
        non_extractable_severity=args.non_extractable_severity,
        assisted_spec_path=args.assisted_spec or None,
        assisted_table_id=args.assisted_table_id,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
