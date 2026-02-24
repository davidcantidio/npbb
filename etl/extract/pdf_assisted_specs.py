"""YAML-driven assisted PDF table extraction (bbox + column mapping).

This module loads table extraction specs and applies them to PDF pages using
`pdfplumber.extract_words()`. It is designed for unstable PDF layouts where
automatic extraction fails and a versioned assist spec is required.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re
from typing import Any

import yaml


_LINE_TOLERANCE = 3.0
_POSTPROCESS_ALLOWED = {"int", "percent", "text"}


class PdfAssistedSpecsError(ValueError):
    """Raised when assisted PDF table spec is invalid or cannot be executed."""


@dataclass(frozen=True)
class PdfSpecColumn:
    """One assisted spec column mapped by x coordinate range."""

    name: str
    x_min: float
    x_max: float


@dataclass(frozen=True)
class PdfTableSpec:
    """One assisted extraction spec for a PDF table layout."""

    table_id: str
    dataset: str
    pages: list[int]
    bbox: tuple[float, float, float, float]
    columns: list[PdfSpecColumn]
    header_rows: int
    postprocess: dict[str, str]
    evidence_label: str | None


@dataclass(frozen=True)
class PdfTableSpecs:
    """Top-level assisted PDF table specs loaded from YAML."""

    schema_version: str
    tables: list[PdfTableSpec]


def _err(path: str, message: str) -> PdfAssistedSpecsError:
    """Build schema error message with JSONPath-like context."""
    return PdfAssistedSpecsError(f"{path}: {message}")


def _require_dict(value: Any, path: str) -> dict[str, Any]:
    """Require mapping/dict input."""
    if not isinstance(value, dict):
        raise _err(path, f"expected mapping/dict, got {type(value).__name__}")
    return value


def _require_list(value: Any, path: str) -> list[Any]:
    """Require list input."""
    if not isinstance(value, list):
        raise _err(path, f"expected list, got {type(value).__name__}")
    return value


def _require_non_empty_str(parent: dict[str, Any], key: str, path: str) -> str:
    """Extract required non-empty string field from mapping."""
    if key not in parent:
        raise _err(f"{path}.{key}", "missing required field")
    value = parent[key]
    if not isinstance(value, str):
        raise _err(f"{path}.{key}", f"expected string, got {type(value).__name__}")
    clean = value.strip()
    if not clean:
        raise _err(f"{path}.{key}", "must be a non-empty string")
    return clean


def _require_positive_int(value: Any, path: str) -> int:
    """Parse positive integer value."""
    if isinstance(value, bool):
        raise _err(path, "expected positive integer, got bool")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise _err(path, f"expected positive integer, got {type(value).__name__}") from exc
    if parsed <= 0:
        raise _err(path, "must be positive integer")
    return parsed


def _require_float(value: Any, path: str) -> float:
    """Parse float value for bbox and column boundaries."""
    if isinstance(value, bool):
        raise _err(path, "expected number, got bool")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise _err(path, f"expected number, got {type(value).__name__}") from exc


def _parse_bbox(value: Any, path: str) -> tuple[float, float, float, float]:
    """Parse bbox in format [x0, top, x1, bottom]."""
    row = _require_list(value, path)
    if len(row) != 4:
        raise _err(path, "bbox must have exactly 4 numbers: [x0, top, x1, bottom]")
    x0, top, x1, bottom = (
        _require_float(row[0], f"{path}[0]"),
        _require_float(row[1], f"{path}[1]"),
        _require_float(row[2], f"{path}[2]"),
        _require_float(row[3], f"{path}[3]"),
    )
    if x1 <= x0:
        raise _err(path, "bbox invalid: x1 must be greater than x0")
    if bottom <= top:
        raise _err(path, "bbox invalid: bottom must be greater than top")
    return (x0, top, x1, bottom)


def _parse_columns(value: Any, path: str) -> list[PdfSpecColumn]:
    """Parse assisted columns with x ranges."""
    rows = _require_list(value, path)
    if not rows:
        raise _err(path, "must contain at least one column")
    parsed: list[PdfSpecColumn] = []
    seen_names: set[str] = set()
    for index, raw in enumerate(rows):
        row_path = f"{path}[{index}]"
        data = _require_dict(raw, row_path)
        name = _require_non_empty_str(data, "name", row_path)
        if name in seen_names:
            raise _err(f"{row_path}.name", f"duplicated column name '{name}'")
        seen_names.add(name)
        x_min = _require_float(data.get("x_min"), f"{row_path}.x_min")
        x_max = _require_float(data.get("x_max"), f"{row_path}.x_max")
        if x_max <= x_min:
            raise _err(row_path, "x_max must be greater than x_min")
        parsed.append(PdfSpecColumn(name=name, x_min=x_min, x_max=x_max))
    return parsed


def _parse_postprocess(value: Any, path: str) -> dict[str, str]:
    """Parse postprocess mapping (`column_name -> operation`)."""
    if value is None:
        return {}
    data = _require_dict(value, path)
    out: dict[str, str] = {}
    for key, raw in data.items():
        if not isinstance(key, str) or not key.strip():
            raise _err(path, "postprocess keys must be non-empty strings")
        if not isinstance(raw, str) or not raw.strip():
            raise _err(f"{path}.{key}", "postprocess value must be non-empty string")
        operation = raw.strip().lower()
        if operation not in _POSTPROCESS_ALLOWED:
            raise _err(
                f"{path}.{key}",
                f"invalid postprocess '{operation}'. Allowed: {sorted(_POSTPROCESS_ALLOWED)}",
            )
        out[key.strip()] = operation
    return out


def _parse_table_specs(value: Any, path: str) -> list[PdfTableSpec]:
    """Parse table specs list from YAML payload."""
    rows = _require_list(value, path)
    if not rows:
        raise _err(path, "must contain at least one table spec")
    parsed: list[PdfTableSpec] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(rows):
        row_path = f"{path}[{index}]"
        data = _require_dict(raw, row_path)
        table_id = _require_non_empty_str(data, "table_id", row_path)
        if table_id in seen_ids:
            raise _err(f"{row_path}.table_id", f"duplicated table_id '{table_id}'")
        seen_ids.add(table_id)
        pages_raw = _require_list(data.get("pages"), f"{row_path}.pages")
        pages = [
            _require_positive_int(page, f"{row_path}.pages[{page_index}]")
            for page_index, page in enumerate(pages_raw)
        ]
        if not pages:
            raise _err(f"{row_path}.pages", "must contain at least one page number")
        header_rows = data.get("header_rows", 1)
        parsed.append(
            PdfTableSpec(
                table_id=table_id,
                dataset=_require_non_empty_str(data, "dataset", row_path),
                pages=pages,
                bbox=_parse_bbox(data.get("bbox"), f"{row_path}.bbox"),
                columns=_parse_columns(data.get("columns"), f"{row_path}.columns"),
                header_rows=_require_positive_int(header_rows, f"{row_path}.header_rows"),
                postprocess=_parse_postprocess(data.get("postprocess"), f"{row_path}.postprocess"),
                evidence_label=(str(data.get("evidence_label")).strip() if data.get("evidence_label") is not None else None),
            )
        )
    return parsed


def load_pdf_table_specs(path: str | Path) -> PdfTableSpecs:
    """Load YAML table specs for assisted PDF extraction.

    Args:
        path: YAML path for assisted table specs.

    Returns:
        Parsed and validated :class:`PdfTableSpecs`.

    Raises:
        FileNotFoundError: If YAML path does not exist.
        PdfAssistedSpecsError: If YAML syntax/schema is invalid.
    """

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise FileNotFoundError(f"PDF assisted specs YAML not found: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        if mark is not None:
            raise PdfAssistedSpecsError(
                f"{yaml_path}:{mark.line + 1}:{mark.column + 1}: invalid YAML syntax"
            ) from exc
        raise PdfAssistedSpecsError(f"{yaml_path}: invalid YAML syntax ({exc})") from exc

    root = _require_dict(payload, "$")
    schema_version = _require_non_empty_str(root, "schema_version", "$")
    tables = _parse_table_specs(root.get("tables"), "$.tables")
    return PdfTableSpecs(schema_version=schema_version, tables=tables)


def _normalize_text(value: Any) -> str:
    """Normalize text fragments from PDF words."""
    return re.sub(r"\s+", " ", str(value or "").strip())


def _group_words_by_line(words: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Group word tokens by approximate vertical position (`top`)."""
    if not words:
        return []
    ordered = sorted(words, key=lambda item: (float(item.get("top", 0.0)), float(item.get("x0", 0.0))))
    groups: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    current_top: float | None = None
    for word in ordered:
        top = float(word.get("top", 0.0))
        if current_top is None or abs(top - current_top) <= _LINE_TOLERANCE:
            current.append(word)
            current_top = top if current_top is None else min(current_top, top)
            continue
        groups.append(sorted(current, key=lambda item: float(item.get("x0", 0.0))))
        current = [word]
        current_top = top
    if current:
        groups.append(sorted(current, key=lambda item: float(item.get("x0", 0.0))))
    return groups


def _apply_postprocess(value: str, operation: str) -> Any:
    """Apply supported postprocess operation to one extracted cell."""
    text = _normalize_text(value)
    if not text:
        return None
    if operation == "text":
        return text
    if operation == "int":
        normalized = text.replace(" ", "").replace(".", "").replace(",", "")
        if normalized.isdigit():
            return int(normalized)
        return None
    if operation == "percent":
        normalized = text.replace("%", "").replace(" ", "")
        if "," in normalized and "." in normalized:
            if normalized.rfind(",") > normalized.rfind("."):
                normalized = normalized.replace(".", "").replace(",", ".")
            else:
                normalized = normalized.replace(",", "")
        elif "," in normalized:
            normalized = normalized.replace(",", ".")
        try:
            return Decimal(normalized)
        except InvalidOperation:
            return None
    return text


def _extract_rows_from_table_spec(page: Any, spec: PdfTableSpec, page_number: int) -> list[dict[str, Any]]:
    """Extract table rows from one page/spec combination."""
    cropped = page.within_bbox(spec.bbox)
    words = cropped.extract_words() or []
    lines = _group_words_by_line(words)
    if not lines:
        return []

    rows: list[dict[str, Any]] = []
    for line in lines:
        row: dict[str, Any] = {column.name: "" for column in spec.columns}
        for word in line:
            word_text = _normalize_text(word.get("text"))
            if not word_text:
                continue
            center = (float(word.get("x0", 0.0)) + float(word.get("x1", 0.0))) / 2.0
            matched_column = None
            for column in spec.columns:
                if column.x_min <= center <= column.x_max:
                    matched_column = column
                    break
            if matched_column is None:
                continue
            previous = row.get(matched_column.name, "")
            row[matched_column.name] = _normalize_text(f"{previous} {word_text}")

        if not any(_normalize_text(cell) for cell in row.values()):
            continue
        rows.append(row)

    data_rows = rows[spec.header_rows :] if len(rows) > spec.header_rows else []
    out: list[dict[str, Any]] = []
    bbox_text = ",".join(str(value) for value in spec.bbox)
    for row in data_rows:
        processed: dict[str, Any] = {}
        for column in spec.columns:
            raw_value = row.get(column.name, "")
            op = spec.postprocess.get(column.name, "text")
            processed[column.name] = _apply_postprocess(raw_value, op)

        evidence_label = spec.evidence_label or spec.table_id
        processed.update(
            {
                "pdf_page": page_number,
                "table_header": evidence_label,
                "evidence_text": (
                    f"spec={spec.table_id}; dataset={spec.dataset}; "
                    f"page={page_number}; bbox={bbox_text}; evidence={evidence_label}"
                ),
                "__lineage_bbox": bbox_text,
                "__spec_table_id": spec.table_id,
                "__raw_payload": {"row": row},
            }
        )
        out.append(processed)
    return out


def extract_with_spec(
    pdf_path: str | Path,
    specs: PdfTableSpecs,
    *,
    table_id: str,
) -> list[dict[str, Any]]:
    """Extract rows from PDF using one assisted table spec.

    Args:
        pdf_path: Source PDF path.
        specs: Loaded assisted specs.
        table_id: Target table_id from spec file.

    Returns:
        Extracted rows with canonical metadata fields (`pdf_page`, evidence, bbox).

    Raises:
        PdfAssistedSpecsError: If target table spec is missing or extraction fails.
        FileNotFoundError: If PDF path does not exist.
    """

    target = next((table for table in specs.tables if table.table_id == table_id), None)
    if target is None:
        raise PdfAssistedSpecsError(
            f"table_id '{table_id}' nao encontrado em pdf_table_specs.yml."
        )

    try:
        import pdfplumber  # type: ignore import-not-found
    except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
        raise PdfAssistedSpecsError(
            "Dependencia ausente: instale 'pdfplumber' para usar extract_with_spec."
        ) from exc

    resolved = Path(pdf_path).expanduser()
    if not resolved.exists():
        raise FileNotFoundError(f"PDF not found: {resolved}")
    if not resolved.is_file():
        raise PdfAssistedSpecsError(f"Caminho invalido para PDF (nao e arquivo): {resolved}")

    rows: list[dict[str, Any]] = []
    try:
        with pdfplumber.open(str(resolved)) as document:
            for page_number in target.pages:
                if page_number <= 0 or page_number > len(document.pages):
                    raise PdfAssistedSpecsError(
                        f"page {page_number} fora do intervalo do PDF (1..{len(document.pages)})."
                    )
                page = document.pages[page_number - 1]
                rows.extend(_extract_rows_from_table_spec(page, target, page_number))
    except PdfAssistedSpecsError:
        raise
    except Exception as exc:
        raise PdfAssistedSpecsError(
            f"Falha ao extrair com spec '{table_id}' do PDF '{resolved}'."
        ) from exc
    return rows
