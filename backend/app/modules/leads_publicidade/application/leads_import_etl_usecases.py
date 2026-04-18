"""Public use cases for ETL lead import preview and commit."""

from __future__ import annotations

from sqlmodel import Session

from app.services.imports.file_reader import DEFAULT_IMPORT_MAX_BYTES

from .etl_import.commit_service import commit_preview_session
from .etl_import.contracts import EtlCommitResult, EtlCpfColumnRequired, EtlHeaderRequired, EtlPreviewSnapshot
from .etl_import.preview_service import create_preview_snapshot


async def import_leads_with_etl(
    file,
    evento_id: int,
    db: Session,
    strict: bool = False,
    header_row: int | None = None,
    field_aliases_json: str | None = None,
    sheet_name: str | None = None,
    max_scan_rows: int | None = None,
) -> EtlPreviewSnapshot | EtlHeaderRequired | EtlCpfColumnRequired:
    return create_preview_snapshot(
        file=file,
        evento_id=evento_id,
        strict=strict,
        db=db,
        max_bytes=DEFAULT_IMPORT_MAX_BYTES,
        header_row=header_row,
        field_aliases_json=field_aliases_json,
        sheet_name=sheet_name,
        max_scan_rows=max_scan_rows,
    )


async def commit_leads_with_etl(
    session_token: str,
    evento_id: int,
    db: Session,
    force_warnings: bool = False,
) -> EtlCommitResult:
    return commit_preview_session(
        session_token=session_token,
        evento_id=evento_id,
        force_warnings=force_warnings,
        db=db,
    )
