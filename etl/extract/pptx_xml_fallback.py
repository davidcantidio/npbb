"""PPTX fallback extractor using ZIP/XML parsing only.

This module is used when `python-pptx` is unavailable or restricted. It reads
`ppt/slides/slide*.xml` entries from the PPTX package and extracts text blocks
(`a:t`) in deterministic slide order.

Limitations:
- Focuses on textual content only (no OCR, chart values, or media payloads).
- Uses simple title heuristics based on title placeholders (`title/ctrTitle`).
- Does not parse speaker notes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterator
from xml.etree import ElementTree as ET
import zipfile

try:  # package execution (repo root at `npbb`)
    from core.registry.location_ref import format_location
except ModuleNotFoundError:  # pragma: no cover - fallback for `npbb.*` imports
    from npbb.core.registry.location_ref import format_location


_NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}
_SLIDE_XML_RE = re.compile(r"^ppt/slides/slide(\d+)\.xml$")
_SPACE_RE = re.compile(r"\s+")


class PptxXmlFallbackError(RuntimeError):
    """Raised when the XML fallback reader cannot load or parse PPTX content."""


@dataclass(frozen=True)
class SlideText:
    """Text blocks extracted from a single slide XML.

    Attributes:
        slide_number: One-based slide number parsed from file name.
        slide_filename: Relative slide XML path inside PPTX package.
        slide_title: Heuristic title extracted from placeholder or first text.
        texts: Ordered text blocks for mapping and metric parsing.
        lineage_location: Canonical lineage location string (`slide:<n>`).
    """

    slide_number: int
    slide_filename: str
    slide_title: str
    texts: list[str]
    lineage_location: str


def _normalize_text(value: str | None) -> str:
    """Normalize XML text node into compact single-line string."""
    if value is None:
        return ""
    text = value.strip()
    if not text:
        return ""
    return _SPACE_RE.sub(" ", text)


def _slide_location(slide_number: int) -> str:
    """Return canonical lineage location for one slide number."""
    try:
        return format_location("slide", {"number": slide_number})
    except Exception:  # pragma: no cover - defensive fallback
        return f"slide:{slide_number}"


def _extract_slide_texts(xml_bytes: bytes, *, slide_filename: str) -> tuple[str, list[str]]:
    """Extract title and ordered text blocks from one slide XML payload.

    Args:
        xml_bytes: Raw slide XML bytes.
        slide_filename: Slide filename for actionable parse errors.

    Returns:
        Tuple `(slide_title, texts)`.

    Raises:
        PptxXmlFallbackError: If XML payload cannot be parsed.
    """

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise PptxXmlFallbackError(
            f"Falha ao parsear XML do slide '{slide_filename}'."
        ) from exc

    title = ""
    text_blocks: list[str] = []

    for shape in root.findall(".//p:sp", namespaces=_NS):
        ph = shape.find(".//p:nvSpPr/p:nvPr/p:ph", namespaces=_NS)
        ph_type = ph.attrib.get("type", "") if ph is not None else ""
        is_title = ph_type in {"title", "ctrTitle"}

        runs = [_normalize_text(node.text) for node in shape.findall(".//a:t", namespaces=_NS)]
        runs = [item for item in runs if item]
        if not runs:
            continue

        joined = " ".join(runs)
        if is_title and not title:
            title = joined
        else:
            text_blocks.append(joined)

    # Fallback for decks that do not use title placeholders.
    if not title and text_blocks:
        title = text_blocks[0]
        text_blocks = text_blocks[1:]

    # Last resort: collect all `a:t` nodes if shape traversal produced nothing.
    if not title and not text_blocks:
        all_runs = [_normalize_text(node.text) for node in root.findall(".//a:t", namespaces=_NS)]
        all_runs = [item for item in all_runs if item]
        if all_runs:
            title = all_runs[0]
            text_blocks = all_runs[1:]

    return title, text_blocks


def iter_slide_text_blocks(pptx_path: str | Path) -> Iterator[SlideText]:
    """Iterate slide text blocks from a PPTX package using ZIP/XML fallback.

    Args:
        pptx_path: Filesystem path to source `.pptx`.

    Yields:
        :class:`SlideText` objects with `slide_number`, `slide_title`, and
        ordered `texts`, including minimal lineage location by slide number.

    Raises:
        PptxXmlFallbackError: If path is missing/invalid, package is not a valid
            ZIP/PPTX, or slide XML cannot be parsed.
    """

    resolved = Path(pptx_path).expanduser()
    if not resolved.exists():
        raise PptxXmlFallbackError(f"Arquivo PPTX nao encontrado: {resolved}")
    if not resolved.is_file():
        raise PptxXmlFallbackError(f"Caminho invalido para PPTX (nao e arquivo): {resolved}")

    try:
        with zipfile.ZipFile(resolved, "r") as archive:
            slide_entries: list[tuple[int, str]] = []
            for name in archive.namelist():
                match = _SLIDE_XML_RE.match(name)
                if not match:
                    continue
                slide_entries.append((int(match.group(1)), name))

            slide_entries.sort(key=lambda item: item[0])
            for slide_number, slide_filename in slide_entries:
                xml_bytes = archive.read(slide_filename)
                slide_title, texts = _extract_slide_texts(
                    xml_bytes,
                    slide_filename=slide_filename,
                )
                yield SlideText(
                    slide_number=slide_number,
                    slide_filename=slide_filename,
                    slide_title=slide_title,
                    texts=texts,
                    lineage_location=_slide_location(slide_number),
                )
    except zipfile.BadZipFile as exc:
        raise PptxXmlFallbackError(
            f"Falha ao abrir PPTX '{resolved}' no fallback XML: arquivo nao e ZIP valido."
        ) from exc
    except OSError as exc:
        raise PptxXmlFallbackError(
            f"Falha de leitura no arquivo PPTX '{resolved}' durante fallback XML."
        ) from exc
