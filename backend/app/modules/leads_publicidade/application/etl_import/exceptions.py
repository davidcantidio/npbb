"""Semantic errors for backend ETL import flows."""

from __future__ import annotations


class EtlImportError(Exception):
    """Base ETL import error."""


class EtlPreviewSessionNotFoundError(EtlImportError):
    """Raised when preview session token does not exist."""


class EtlPreviewSessionConflictError(EtlImportError):
    """Raised when preview session cannot be reused."""


class EtlImportValidationError(EtlImportError):
    """Raised when validation gate blocks persistence."""


class EtlImportContractError(EtlImportError):
    """Raised when preview payload cannot be materialized as canonical row."""


class EtlImportJobNotFoundError(EtlImportError):
    """Raised when ETL job id does not exist."""


class EtlImportJobConflictError(EtlImportError):
    """Raised when ETL job transition is invalid for the current state."""

