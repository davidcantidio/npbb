"""Helpers simples para fuzzy match sem dependencias externas."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Iterable, Tuple


def best_match(value: str, candidates: Iterable[str], threshold: float = 0.85) -> Tuple[str | None, float]:
    if not value:
        return None, 0.0
    best = None
    best_score = 0.0
    value_norm = value.strip().lower()
    for item in candidates:
        if not item:
            continue
        candidate = str(item).strip().lower()
        if not candidate:
            continue
        score = SequenceMatcher(None, value_norm, candidate).ratio()
        if score > best_score:
            best_score = score
            best = item
    if best is None or best_score < threshold:
        return None, best_score
    return best, best_score
