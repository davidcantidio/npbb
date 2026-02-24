"""DOCX sections extractor.

Extracts the heading hierarchy (Heading 1/2/3...) and associates body paragraphs
to the last seen heading.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence

from docx import Document

from .spec_models import DocxSection


class DocxSpecError(RuntimeError):
    """Raised when the DOCX spec cannot be extracted (invalid file, parse error, etc)."""


_HEADING_STYLE_RE = re.compile(
    r"^(Heading|Title|Titulo|T\u00edtulo)\s+(?P<level>\d+)\s*$",
    flags=re.IGNORECASE,
)


def _heading_level(style_name: str) -> Optional[int]:
    """Return heading level for a paragraph style name (or None if not a heading)."""
    if not style_name:
        return None
    m = _HEADING_STYLE_RE.match(style_name.strip())
    if not m:
        return None
    try:
        return int(m.group("level"))
    except ValueError:
        return None


@dataclass
class DocxSectionExtractor:
    """Extract sections (headings + body lines) from a DOCX template."""

    def extract_sections(self, docx_path: str | Path) -> List[DocxSection]:
        """Extract ordered sections from a DOCX.

        Args:
            docx_path: Path to a .docx file.

        Returns:
            A list of DocxSection in document order.

        Raises:
            FileNotFoundError: If docx_path does not exist.
            DocxSpecError: If the DOCX cannot be parsed.
        """
        path = Path(docx_path)
        if not path.exists():
            raise FileNotFoundError(f"DOCX not found: {path}")

        try:
            doc = Document(path)
        except Exception as e:  # python-docx raises generic exceptions here
            raise DocxSpecError(f"Failed to open DOCX: {path}") from e

        sections: List[DocxSection] = []
        current: Optional[DocxSection] = None
        current_body: List[str] = []

        for i, par in enumerate(doc.paragraphs):
            text = (par.text or "").strip()
            if not text:
                continue

            style_name = par.style.name if par.style else ""
            level = _heading_level(style_name)

            if level is not None:
                # flush previous section
                if current is not None:
                    sections.append(
                        DocxSection(
                            level=current.level,
                            title=current.title,
                            body_lines=list(current_body),
                            start_paragraph_index=current.start_paragraph_index,
                        )
                    )
                # start new section
                current = DocxSection(
                    level=level,
                    title=text,
                    body_lines=[],
                    start_paragraph_index=i,
                )
                current_body = []
                continue

            if current is not None:
                current_body.append(text)

        if current is not None:
            sections.append(
                DocxSection(
                    level=current.level,
                    title=current.title,
                    body_lines=list(current_body),
                    start_paragraph_index=current.start_paragraph_index,
                )
            )

        return sections


def find_nearest_section_title(
    paragraph_index: int,
    sections: Sequence[DocxSection],
) -> Optional[str]:
    """Return the nearest section title above a paragraph index.

    Args:
        paragraph_index: Paragraph position in document order.
        sections: Extracted sections in document order.

    Returns:
        Title of the last section whose start index is <= paragraph_index.
        Returns None when no section exists above the paragraph.
    """
    last: Optional[str] = None
    for section in sections:
        if section.start_paragraph_index <= paragraph_index:
            last = section.title
            continue
        break
    return last
