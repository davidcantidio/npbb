"""Actionable exceptions for ingestion registry interactions."""

from __future__ import annotations

from typing import Optional

from .types import IngestionId, IngestionStatus, SourceId


class RegistryError(RuntimeError):
    """Base class for registry errors with actionable guidance."""

    def __init__(self, message: str, *, action: Optional[str] = None) -> None:
        self.message = message
        self.action = action
        full = message if not action else f"{message} Como corrigir: {action}"
        super().__init__(full)


class SourceNotFoundError(RegistryError):
    """Raised when source lookup fails in registry."""

    def __init__(self, source_id: SourceId) -> None:
        super().__init__(
            f"Fonte nao encontrada no registry: {source_id}",
            action="Registrar a fonte com upsert_source antes de iniciar ingestao.",
        )


class IngestionNotFoundError(RegistryError):
    """Raised when ingestion lookup fails in registry."""

    def __init__(self, ingestion_id: IngestionId) -> None:
        super().__init__(
            f"Ingestion nao encontrada no registry: {ingestion_id}",
            action="Validar o ingestion_id retornado por start_ingestion.",
        )


class DuplicateSourceError(RegistryError):
    """Raised when source insertion conflicts with existing source_id."""

    def __init__(self, source_id: SourceId) -> None:
        super().__init__(
            f"Conflito de source_id no registry: {source_id}",
            action="Usar upsert_source ou revisar normalizacao do source_id.",
        )


class InvalidIngestionStatusError(RegistryError):
    """Raised when caller provides an unsupported ingestion status."""

    def __init__(self, status: str) -> None:
        super().__init__(
            f"Status de ingestao invalido: {status}",
            action="Usar um status permitido: RUNNING, SUCCEEDED, FAILED ou SKIPPED.",
        )


class InvalidStatusTransitionError(RegistryError):
    """Raised when an invalid status transition is attempted."""

    def __init__(self, from_status: IngestionStatus, to_status: IngestionStatus) -> None:
        super().__init__(
            f"Transicao de status invalida: {from_status} -> {to_status}",
            action="Finalizar somente ingestoes em RUNNING com status terminal.",
        )


class SourceFileError(RegistryError):
    """Base class for source-file fingerprint and metadata errors."""


class SourceFileNotFoundError(SourceFileError):
    """Raised when source file path does not exist."""

    def __init__(self, path: str) -> None:
        super().__init__(
            f"Arquivo de fonte nao encontrado: {path}",
            action="Verificar caminho do arquivo e disponibilidade no disco local.",
        )


class SourceFilePermissionError(SourceFileError):
    """Raised when process cannot read file content or metadata."""

    def __init__(self, path: str, operation: str) -> None:
        super().__init__(
            f"Sem permissao para {operation} o arquivo de fonte: {path}",
            action="Ajustar permissoes de leitura do arquivo/pasta e tentar novamente.",
        )
