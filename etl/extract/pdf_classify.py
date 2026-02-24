"""PDF content classifier for extraction strategy decisions.

This module profiles PDF pages to detect text and image signals before running
table extraction. It supports:
- standalone classification (`classify_pdf`)
- registry-aware execution with ingestion summary (`classify_pdf_with_registry`)

Classification output is intentionally lightweight and auditable.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

try:  # package execution (repo root at `npbb`)
    from etl.extract.pdf_profile import PdfPageProfile, PdfProfile
except ModuleNotFoundError:  # pragma: no cover - fallback for `npbb.etl.*` imports
    from npbb.etl.extract.pdf_profile import PdfPageProfile, PdfProfile


_TOKEN_RE = re.compile(r"\S+")


class PdfClassificationError(RuntimeError):
    """Raised when PDF profile classification cannot be completed safely."""


def _resolve_pdf_path(path: str | Path) -> Path:
    """Resolve and validate PDF path."""
    resolved = Path(path).expanduser()
    if not resolved.exists():
        raise PdfClassificationError(f"Arquivo PDF nao encontrado: {resolved}")
    if not resolved.is_file():
        raise PdfClassificationError(f"Caminho invalido para PDF (nao e arquivo): {resolved}")
    return resolved


def _require_pdf_dependencies() -> tuple[Any, Any]:
    """Import pypdf and pdfplumber dependencies lazily with actionable errors."""
    try:
        from pypdf import PdfReader  # type: ignore import-not-found
    except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
        raise PdfClassificationError(
            "Dependencia ausente: instale 'pypdf' para classificar PDFs."
        ) from exc
    try:
        import pdfplumber  # type: ignore import-not-found
    except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
        raise PdfClassificationError(
            "Dependencia ausente: instale 'pdfplumber' para classificar PDFs."
        ) from exc
    return PdfReader, pdfplumber


def _safe_extract_text(pdfplumber_page: Any) -> str:
    """Extract text from one page and downgrade parser errors to empty text."""
    try:
        return str(pdfplumber_page.extract_text() or "")
    except Exception:
        return ""


def _safe_extract_image_count(pdfplumber_page: Any | None, pypdf_page: Any) -> int:
    """Extract image count from pdfplumber and fallback to pypdf when needed."""
    count = 0
    if pdfplumber_page is not None:
        try:
            count = len(pdfplumber_page.images or [])
        except Exception:
            count = 0
    if count > 0:
        return count
    try:
        return len(list(pypdf_page.images))
    except Exception:
        return 0


def _page_class(*, has_text: bool, has_images: bool) -> str:
    """Return page class from text/image booleans."""
    if has_text and has_images:
        return "mixed"
    if has_text:
        return "text"
    if has_images:
        return "image"
    return "empty"


def _suggest_strategy(
    *,
    page_count: int,
    pages_with_text: int,
    pages_with_images: int,
) -> str:
    """Suggest extraction strategy from aggregate profile signals."""
    if page_count <= 0:
        return "empty_document"
    if pages_with_text > 0 and pages_with_images == 0:
        return "text_table"
    if pages_with_text == 0 and pages_with_images > 0:
        return "ocr_or_assisted"
    if pages_with_text > 0 and pages_with_images > 0:
        return "hybrid"
    return "manual_assisted"


def classify_pdf(path: str | Path) -> PdfProfile:
    """Classify PDF content profile by page text/image signals.

    Args:
        path: Source PDF path.

    Returns:
        Document-level :class:`PdfProfile` including per-page details and
        suggested extraction strategy.

    Raises:
        PdfClassificationError: If dependencies are missing, file is invalid,
            or PDF cannot be parsed.
    """

    resolved = _resolve_pdf_path(path)
    PdfReader, pdfplumber = _require_pdf_dependencies()

    try:
        reader = PdfReader(str(resolved))
        page_count = len(reader.pages)
    except Exception as exc:
        raise PdfClassificationError(
            f"Falha ao abrir PDF '{resolved}'. Verifique se o arquivo e um PDF valido."
        ) from exc

    pages: list[PdfPageProfile] = []
    text_like_pages = 0
    image_like_pages = 0
    mixed_pages = 0
    empty_pages = 0
    pages_with_text = 0
    pages_with_images = 0

    try:
        with pdfplumber.open(str(resolved)) as plumber_doc:
            for page_index in range(page_count):
                page_number = page_index + 1
                pypdf_page = reader.pages[page_index]
                plumber_page = plumber_doc.pages[page_index] if page_index < len(plumber_doc.pages) else None

                text = _safe_extract_text(plumber_page) if plumber_page is not None else ""
                text_chars = len(text.strip())
                word_count = len(_TOKEN_RE.findall(text))
                image_count = _safe_extract_image_count(plumber_page, pypdf_page)

                has_text = text_chars > 0
                has_images = image_count > 0
                page_class = _page_class(has_text=has_text, has_images=has_images)
                if page_class == "text":
                    text_like_pages += 1
                elif page_class == "image":
                    image_like_pages += 1
                elif page_class == "mixed":
                    mixed_pages += 1
                else:
                    empty_pages += 1
                if has_text:
                    pages_with_text += 1
                if has_images:
                    pages_with_images += 1

                pages.append(
                    PdfPageProfile(
                        page_number=page_number,
                        text_chars=text_chars,
                        word_count=word_count,
                        image_count=image_count,
                        has_text=has_text,
                        has_images=has_images,
                        page_class=page_class,  # type: ignore[arg-type]
                    )
                )
    except PdfClassificationError:
        raise
    except Exception as exc:
        raise PdfClassificationError(
            f"Falha ao classificar PDF '{resolved}'. Verifique integridade do arquivo."
        ) from exc

    strategy = _suggest_strategy(
        page_count=page_count,
        pages_with_text=pages_with_text,
        pages_with_images=pages_with_images,
    )
    return PdfProfile(
        page_count=page_count,
        pages_with_text=pages_with_text,
        pages_with_images=pages_with_images,
        text_like_pages=text_like_pages,
        image_like_pages=image_like_pages,
        mixed_pages=mixed_pages,
        empty_pages=empty_pages,
        has_text=pages_with_text > 0,
        has_images=pages_with_images > 0,
        suggested_strategy=strategy,  # type: ignore[arg-type]
        pages=pages,
    )


def classify_pdf_with_registry(
    *,
    source_id: str,
    pdf_path: str | Path,
) -> dict[str, Any]:
    """Classify PDF and persist profile summary in ingestion run notes.

    Args:
        source_id: Stable source identifier.
        pdf_path: Source PDF path.

    Returns:
        Summary dict with source/run identifiers and profile summary.

    Raises:
        PdfClassificationError: If PDF classification fails.
        ValueError: If registry operations fail.
        OSError: If file operations fail.
    """

    try:  # pragma: no cover - import style depends on caller cwd
        from app.db.database import engine
        from app.models.etl_registry import IngestionStatus
        from app.services.etl_registry_service import (
            finish_ingestion_run,
            register_source_from_path,
            start_ingestion_run,
        )
    except ModuleNotFoundError:  # pragma: no cover
        backend_root = Path(__file__).resolve().parents[2] / "backend"
        if str(backend_root) not in sys.path:
            sys.path.insert(0, str(backend_root))
        from app.db.database import engine
        from app.models.etl_registry import IngestionStatus
        from app.services.etl_registry_service import (
            finish_ingestion_run,
            register_source_from_path,
            start_ingestion_run,
        )

    from sqlmodel import Session

    with Session(engine) as session:
        source = register_source_from_path(session, source_id, Path(pdf_path))
        run = start_ingestion_run(session, source.source_id, "classify_pdf")
        try:
            profile = classify_pdf(pdf_path)
            profile_summary = profile.summary()
            notes = "pdf_profile=" + json.dumps(profile_summary, ensure_ascii=False, sort_keys=True)
            finish_ingestion_run(
                session,
                ingestion_id=int(run.id),
                status=IngestionStatus.SUCCESS,
                notes=notes,
            )
            return {
                "source_id": source.source_id,
                "ingestion_id": int(run.id),
                "profile": profile_summary,
            }
        except Exception as exc:
            persisted_run = session.get(type(run), run.id)
            if persisted_run is not None and persisted_run.finished_at is None:
                finish_ingestion_run(
                    session,
                    ingestion_id=int(run.id),
                    status=IngestionStatus.FAILED,
                    notes=f"Falha ao classificar PDF: {exc}",
                )
            raise


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for PDF classification and optional registry logging."""
    parser = argparse.ArgumentParser(prog="pdf-classify")
    parser.add_argument("--pdf", required=True, help="Path to source PDF file.")
    parser.add_argument(
        "--source-id",
        default="",
        help="Optional source ID. When set, classification is logged in ingestion registry.",
    )
    args = parser.parse_args(argv)

    if args.source_id.strip():
        result = classify_pdf_with_registry(source_id=args.source_id, pdf_path=args.pdf)
        print(json.dumps(result, ensure_ascii=False))
        return 0

    profile = classify_pdf(args.pdf)
    payload = {
        "profile": profile.summary(),
        "pages": [page.to_dict() for page in profile.pages],
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
