"""Shared policy helpers for ETL preview DQ reports."""

from __future__ import annotations

from collections.abc import Iterable

from .contracts import EtlPreviewDQItem


def compute_has_warnings(issues: Iterable[EtlPreviewDQItem]) -> bool:
    # affected_rows is evidence detail, not the gate signal; checking it here
    # would let visible preview warnings bypass the explicit force_warnings flow.
    return any(item.severity == "warning" for item in issues)
