"""Typed profile models for PDF content classification.

The profile summarizes whether a PDF page/document is primarily text-based,
image/scanned, mixed, or empty. This helps extractors decide strategy before
attempting table parsing or OCR/manual fallback.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


PdfPageClass = Literal["text", "image", "mixed", "empty"]
PdfExtractionStrategy = Literal[
    "text_table",
    "ocr_or_assisted",
    "hybrid",
    "manual_assisted",
    "empty_document",
]


@dataclass(frozen=True)
class PdfPageProfile:
    """Classification summary for one PDF page.

    Attributes:
        page_number: One-based page index.
        text_chars: Number of extracted text characters.
        word_count: Number of extracted tokens separated by whitespace.
        image_count: Number of image-like objects detected on page.
        has_text: Whether page has text content.
        has_images: Whether page has image objects.
        page_class: Coarse class for extraction strategy.
    """

    page_number: int
    text_chars: int
    word_count: int
    image_count: int
    has_text: bool
    has_images: bool
    page_class: PdfPageClass

    def to_dict(self) -> dict[str, int | bool | str]:
        """Serialize page profile as plain dictionary."""
        return {
            "page_number": self.page_number,
            "text_chars": self.text_chars,
            "word_count": self.word_count,
            "image_count": self.image_count,
            "has_text": self.has_text,
            "has_images": self.has_images,
            "page_class": self.page_class,
        }


@dataclass(frozen=True)
class PdfProfile:
    """Document-level PDF profile used to choose extraction strategy.

    Attributes:
        page_count: Total number of pages.
        pages_with_text: Count of pages where extracted text is non-empty.
        pages_with_images: Count of pages with image objects.
        text_like_pages: Count of pages classified as text-only.
        image_like_pages: Count of pages classified as image-only.
        mixed_pages: Count of pages classified as mixed text+image.
        empty_pages: Count of pages without text/image evidence.
        has_text: Whether any page contains text.
        has_images: Whether any page contains images.
        suggested_strategy: Suggested extraction strategy from profile signals.
        pages: Per-page profile list.
    """

    page_count: int
    pages_with_text: int
    pages_with_images: int
    text_like_pages: int
    image_like_pages: int
    mixed_pages: int
    empty_pages: int
    has_text: bool
    has_images: bool
    suggested_strategy: PdfExtractionStrategy
    pages: list[PdfPageProfile]

    def summary(self) -> dict[str, int | bool | str]:
        """Return compact summary dictionary for logs/audit notes."""
        return {
            "page_count": self.page_count,
            "pages_with_text": self.pages_with_text,
            "pages_with_images": self.pages_with_images,
            "text_like_pages": self.text_like_pages,
            "image_like_pages": self.image_like_pages,
            "mixed_pages": self.mixed_pages,
            "empty_pages": self.empty_pages,
            "has_text": self.has_text,
            "has_images": self.has_images,
            "suggested_strategy": self.suggested_strategy,
        }
