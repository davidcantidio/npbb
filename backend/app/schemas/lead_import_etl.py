"""Schemas for ETL lead import preview and commit endpoints."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class DQCheckResult(BaseModel):
    check_name: str
    severity: Literal["error", "warning", "info"]
    affected_rows: int
    sample: list[dict[str, Any]] = Field(default_factory=list)
    check_id: str | None = None
    message: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ImportEtlPreviewResponse(BaseModel):
    session_token: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    dq_report: list[DQCheckResult]

    model_config = ConfigDict(from_attributes=True)


class ImportEtlCommitRequest(BaseModel):
    session_token: str
    evento_id: int
    force_warnings: bool = False


class ImportEtlResult(BaseModel):
    session_token: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    created: int
    updated: int
    skipped: int
    errors: int
    strict: bool
    status: Literal["previewed", "committed", "expired", "rejected"]
    dq_report: list[DQCheckResult]

    model_config = ConfigDict(from_attributes=True)
