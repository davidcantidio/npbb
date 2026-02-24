"""Heuristicas reutilizaveis para sugestao de mapeamento de colunas."""

from __future__ import annotations

import re

from app.services.imports.contracts import ColumnSuggestion, ImportDomainSpec, ImportFieldSpec
from app.utils.text_normalize import normalize_text

MAX_CONFIDENCE = 0.9

_CPF_RE = re.compile(r"^\d{11}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_DATE_RE = (
    re.compile(r"^\d{2}/\d{2}/\d{4}$"),
    re.compile(r"^\d{4}-\d{2}-\d{2}$"),
)
_UF_SET = {
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
}


def column_samples(rows: list[list[str]], col_index: int, *, max_samples: int = 8) -> list[str]:
    samples: list[str] = []
    for row in rows:
        if col_index >= len(row):
            continue
        value = row[col_index].strip()
        if not value:
            continue
        samples.append(value)
        if len(samples) >= max_samples:
            break
    return samples


def build_samples_by_column(headers: list[str], rows: list[list[str]], *, max_samples: int = 8) -> list[list[str]]:
    return [column_samples(rows, idx, max_samples=max_samples) for idx, _ in enumerate(headers)]


def suggest_columns(
    domain_spec: ImportDomainSpec,
    headers: list[str],
    rows: list[list[str]],
) -> tuple[list[ColumnSuggestion], list[list[str]]]:
    samples_by_column = build_samples_by_column(headers, rows)
    suggestions: list[ColumnSuggestion] = []
    for idx, header in enumerate(headers):
        samples = samples_by_column[idx]
        campo, confianca = _infer_field(domain_spec, header, samples)
        suggestions.append(ColumnSuggestion(coluna=header or "", campo=campo, confianca=confianca))
    return suggestions, samples_by_column


def _infer_field(domain_spec: ImportDomainSpec, header: str, samples: list[str]) -> tuple[str | None, float | None]:
    best_field: str | None = None
    best_score = 0.0
    for field in domain_spec.fields:
        header_score = _score_header_match(header, field)
        value_score = _score_values(samples, field.kind)
        value_score = _apply_sample_penalty(value_score, len(samples))
        combined = _combine_scores(header_score, value_score)
        if combined > best_score:
            best_score = combined
            best_field = field.name

    if not best_field or best_score < 0.5:
        return None, None
    return best_field, min(best_score, MAX_CONFIDENCE)


def _combine_scores(header_score: float, value_score: float) -> float:
    if header_score and value_score:
        return max(header_score, min(0.94, (header_score * 0.62) + (value_score * 0.5)))
    if header_score:
        return header_score
    return value_score * 0.88


def _score_header_match(header: str, field: ImportFieldSpec) -> float:
    normalized_header = normalize_text(header)
    if not normalized_header:
        return 0.0

    candidates = [field.name, *field.aliases]
    best = 0.0
    for candidate in candidates:
        normalized_candidate = normalize_text(candidate)
        if not normalized_candidate:
            continue
        if normalized_header == normalized_candidate:
            best = max(best, 0.9)
            continue
        if normalized_candidate in normalized_header or normalized_header in normalized_candidate:
            best = max(best, 0.72)
            continue
        if normalized_header.replace(" ", "_") == normalized_candidate.replace(" ", "_"):
            best = max(best, 0.84)
    return best


def _apply_sample_penalty(score: float, sample_size: int) -> float:
    if sample_size <= 0:
        return 0.0
    if sample_size < 3:
        return score * (sample_size / 3)
    return score


def _score_values(values: list[str], kind: str) -> float:
    if not values:
        return 0.0
    if kind == "email":
        hits = sum(1 for value in values if _EMAIL_RE.match(value.strip().lower()))
        return hits / len(values)
    if kind == "cpf":
        hits = 0
        for value in values:
            digits = "".join(ch for ch in value if ch.isdigit())
            if _CPF_RE.match(digits):
                hits += 1
        return hits / len(values)
    if kind == "date":
        hits = sum(1 for value in values if any(regex.match(value.strip()) for regex in _DATE_RE))
        return hits / len(values)
    if kind == "uf":
        hits = sum(1 for value in values if value.strip().upper() in _UF_SET)
        return hits / len(values)
    if kind == "number":
        hits = 0
        for value in values:
            text = value.strip().replace(".", "").replace(",", ".")
            try:
                float(text)
                hits += 1
            except ValueError:
                continue
        return hits / len(values)

    # kind=text (ou desconhecido): scorea preenchimento nao-vazio.
    non_empty = sum(1 for value in values if value.strip())
    return non_empty / len(values)
