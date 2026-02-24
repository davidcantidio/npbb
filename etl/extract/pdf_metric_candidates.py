"""Shared PDF metric candidate extraction using regex/anchors.

This module extracts metric candidates from text PDFs and enforces a gap-aware
contract:
- candidate status `ok` requires evidence + page + parsed value
- candidate status `gap` is emitted when anchors/values are missing
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re
from typing import Any, Iterable

try:  # package execution (repo root at `npbb`)
    from etl.extract.pdf_classify import PdfClassificationError, classify_pdf
except ModuleNotFoundError:  # pragma: no cover - fallback for `npbb.etl.*` imports
    from npbb.etl.extract.pdf_classify import PdfClassificationError, classify_pdf


_NUMBER_RE = re.compile(
    r"[-+]?\d{1,3}(?:[.\s]\d{3})*(?:,\d+|\.\d+)?|[-+]?\d+(?:,\d+|\.\d+)?"
)
_PERCENT_RE = re.compile(
    r"([-+]?\d{1,3}(?:[.\s]\d{3})*(?:,\d+|\.\d+)?|[-+]?\d+(?:,\d+|\.\d+)?)\s*%"
)
_NON_EXTRACTABLE_STRATEGIES = {"ocr_or_assisted", "manual_assisted", "empty_document"}
_PARSE_MODES = {"first_number", "first_percent"}


@dataclass(frozen=True)
class MetricRule:
    """One metric extraction rule based on text anchor and parse mode.

    Args:
        metric_key: Canonical metric key.
        metric_label: Human-friendly metric label.
        anchor_pattern: Regex used to find evidence text in PDF lines.
        unit: Unit label for parsed value (`count`, `percent`, etc.).
        parse_mode: Numeric parse mode (`first_number` or `first_percent`).
    """

    metric_key: str
    metric_label: str
    anchor_pattern: str
    unit: str
    parse_mode: str

    def compiled_anchor(self) -> re.Pattern[str]:
        """Compile anchor regex using case-insensitive matching.

        Returns:
            Compiled anchor regex pattern.

        Raises:
            ValueError: If `parse_mode` or `anchor_pattern` is invalid.
        """

        if self.parse_mode not in _PARSE_MODES:
            raise ValueError(
                f"parse_mode invalido para {self.metric_key}: {self.parse_mode!r}. "
                f"Como corrigir: usar um de {sorted(_PARSE_MODES)}."
            )
        pattern = (self.anchor_pattern or "").strip()
        if not pattern:
            raise ValueError(
                f"anchor_pattern vazio para {self.metric_key}. "
                "Como corrigir: informar regex de ancora."
            )
        return re.compile(pattern, flags=re.IGNORECASE)

    @property
    def extraction_rule(self) -> str:
        """Return serializable extraction rule string."""
        return f"anchor:{self.anchor_pattern} | parse:{self.parse_mode}"


@dataclass(frozen=True)
class MetricCandidate:
    """One extracted metric candidate with gap-aware fields.

    Args:
        metric_key: Canonical metric key.
        metric_label: Human-friendly metric label.
        status: Candidate status (`ok` or `gap`).
        metric_value: Parsed numeric metric value.
        metric_value_raw: Raw numeric token captured from source text.
        unit: Unit label.
        pdf_page: Source page number where evidence was found.
        evidence_text: Source evidence text snippet.
        extraction_rule: Rule used to produce candidate.
        gap_reason: Actionable reason when status is `gap`.
        raw_payload: Debug payload for auditing/parser troubleshooting.
    """

    metric_key: str
    metric_label: str
    status: str
    metric_value: Decimal | None
    metric_value_raw: str | None
    unit: str
    pdf_page: int | None
    evidence_text: str | None
    extraction_rule: str
    gap_reason: str | None
    raw_payload: dict[str, Any]


def _normalize_decimal_token(token: str) -> str:
    """Normalize localized numeric token into Decimal-compatible format.

    Args:
        token: Raw numeric token.

    Returns:
        Normalized token using dot decimal separator.

    Raises:
        InvalidOperation: If token is empty.
    """

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
    """Parse raw token into Decimal.

    Args:
        token: Raw numeric token.

    Returns:
        Parsed Decimal or `None` when parsing fails.
    """

    try:
        return Decimal(_normalize_decimal_token(token))
    except (InvalidOperation, ValueError):
        return None


def _parse_value(line: str, *, parse_mode: str) -> tuple[Decimal | None, str | None]:
    """Parse one value token from an evidence line.

    Args:
        line: Evidence text line.
        parse_mode: Parse mode (`first_number` or `first_percent`).

    Returns:
        Tuple with parsed Decimal and raw token, both optional.
    """

    if parse_mode == "first_percent":
        match = _PERCENT_RE.search(line)
        if not match:
            return None, None
        token = match.group(1)
        return _parse_decimal(token), token

    match = _NUMBER_RE.search(line)
    if not match:
        return None, None
    token = match.group(0)
    return _parse_decimal(token), token


def _extract_page_lines(pdf_path: Path) -> list[tuple[int, list[str]]]:
    """Extract non-empty text lines per PDF page using `pypdf`.

    Args:
        pdf_path: Path to a readable PDF file.

    Returns:
        List of tuples `(page_number, lines)`.

    Raises:
        PdfClassificationError: If `pypdf` is missing.
        OSError: If file cannot be opened/read.
    """

    try:
        from pypdf import PdfReader  # type: ignore import-not-found
    except ModuleNotFoundError as exc:  # pragma: no cover - env dependent
        raise PdfClassificationError(
            "Dependencia ausente: instale 'pypdf' para extracao de metricas PDF."
        ) from exc

    reader = PdfReader(str(pdf_path))
    output: list[tuple[int, list[str]]] = []
    for index, page in enumerate(reader.pages, start=1):
        raw_text = str(page.extract_text() or "")
        lines = [re.sub(r"\s+", " ", line).strip() for line in raw_text.splitlines()]
        lines = [line for line in lines if line]
        output.append((index, lines))
    return output


def _gap_candidate(
    rule: MetricRule,
    *,
    reason: str,
    profile_summary: dict[str, Any],
    evidence_text: str | None = None,
    page_number: int | None = None,
) -> MetricCandidate:
    """Build one gap candidate with standardized debug payload.

    Args:
        rule: Metric extraction rule.
        reason: Gap reason code.
        profile_summary: PDF profile summary payload.
        evidence_text: Optional evidence line, if any.
        page_number: Optional source page number, if any.

    Returns:
        Gap `MetricCandidate`.
    """

    return MetricCandidate(
        metric_key=rule.metric_key,
        metric_label=rule.metric_label,
        status="gap",
        metric_value=None,
        metric_value_raw=None,
        unit=rule.unit,
        pdf_page=page_number,
        evidence_text=evidence_text,
        extraction_rule=rule.extraction_rule,
        gap_reason=reason,
        raw_payload={
            "reason": reason,
            "profile": profile_summary,
            "page": page_number,
            "evidence_text": evidence_text,
        },
    )


def extract_metric_candidates_from_pdf(
    pdf_path: str | Path,
    rules: Iterable[MetricRule],
) -> tuple[list[MetricCandidate], dict[str, Any]]:
    """Extract metric candidates using anchor/regex rules from PDF text.

    Args:
        pdf_path: Source PDF path.
        rules: Iterable of extraction rules.

    Returns:
        Tuple with:
        - list of `MetricCandidate` (always one candidate per rule),
        - PDF profile summary from classifier.

    Raises:
        PdfClassificationError: If PDF cannot be classified/read.
        OSError: If file operations fail.
        ValueError: If rule configuration is invalid.
    """

    resolved = Path(pdf_path).expanduser()
    profile = classify_pdf(resolved)
    profile_summary = profile.summary()
    rule_list = list(rules)
    if not rule_list:
        return [], profile_summary

    if (
        profile.suggested_strategy in _NON_EXTRACTABLE_STRATEGIES
        and profile.pages_with_text == 0
    ):
        return (
            [
                _gap_candidate(
                    rule,
                    reason=f"non_extractable_pdf:{profile.suggested_strategy}",
                    profile_summary=profile_summary,
                )
                for rule in rule_list
            ],
            profile_summary,
        )

    page_lines = _extract_page_lines(resolved)
    candidates: list[MetricCandidate] = []

    for rule in rule_list:
        anchor = rule.compiled_anchor()
        matched_line: str | None = None
        matched_page: int | None = None
        parsed_line: str | None = None
        parsed_page: int | None = None
        parsed_value: Decimal | None = None
        parsed_raw: str | None = None
        for page_number, lines in page_lines:
            for line in lines:
                if not anchor.search(line):
                    continue
                if matched_line is None:
                    matched_line = line
                    matched_page = page_number
                value, value_raw = _parse_value(line, parse_mode=rule.parse_mode)
                if value is not None and value_raw is not None:
                    parsed_line = line
                    parsed_page = page_number
                    parsed_value = value
                    parsed_raw = value_raw
                    break
            if parsed_line is not None:
                break

        if matched_line is None:
            candidates.append(
                _gap_candidate(
                    rule,
                    reason="anchor_not_found",
                    profile_summary=profile_summary,
                )
            )
            continue

        if parsed_value is None or parsed_raw is None or parsed_line is None:
            candidates.append(
                _gap_candidate(
                    rule,
                    reason="value_not_found",
                    profile_summary=profile_summary,
                    evidence_text=matched_line,
                    page_number=matched_page,
                )
            )
            continue

        candidates.append(
            MetricCandidate(
                metric_key=rule.metric_key,
                metric_label=rule.metric_label,
                status="ok",
                metric_value=parsed_value,
                metric_value_raw=parsed_raw,
                unit=rule.unit,
                pdf_page=parsed_page,
                evidence_text=parsed_line,
                extraction_rule=rule.extraction_rule,
                gap_reason=None,
                raw_payload={
                    "profile": profile_summary,
                    "page": parsed_page,
                    "evidence_text": parsed_line,
                    "metric_value_raw": parsed_raw,
                },
            )
        )

    return candidates, profile_summary
