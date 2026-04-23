"""Row-level staging persistence for ETL lead imports."""

from __future__ import annotations

import csv
import json
import logging
import os
from datetime import datetime, timezone
from tempfile import SpooledTemporaryFile
from typing import Any, Literal

from sqlalchemy import delete, func, or_
from sqlmodel import Session, select

from app.models.models import LeadImportEtlStagingRow
from core.leads_etl.models import backend_payload_to_lead_row


StagingIngestionStrategy = Literal["insert", "copy"]
ImportErrorPhase = Literal["validation", "merge", "all"]

DEFAULT_COPY_MIN_ROWS = 10_000
DEFAULT_COPY_MIN_BYTES = 8 * 1024 * 1024
DEFAULT_INSERT_CHUNK_SIZE = 1_000

logger = logging.getLogger(__name__)


def _env_int(name: str, default: int, *, min_value: int = 1) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(value, min_value)


def copy_min_rows() -> int:
    return _env_int("LEAD_IMPORT_ETL_COPY_MIN_ROWS", DEFAULT_COPY_MIN_ROWS)


def copy_min_bytes() -> int:
    return _env_int("LEAD_IMPORT_ETL_COPY_MIN_BYTES", DEFAULT_COPY_MIN_BYTES)


def insert_chunk_size() -> int:
    return _env_int("LEAD_IMPORT_ETL_STAGING_INSERT_CHUNK_SIZE", DEFAULT_INSERT_CHUNK_SIZE)


def choose_staging_ingestion_strategy(
    session: Session,
    *,
    total_rows: int,
    source_file_size_bytes: int,
) -> StagingIngestionStrategy:
    bind = session.get_bind()
    if bind.dialect.name != "postgresql":
        return "insert"
    if total_rows >= copy_min_rows():
        return "copy"
    if source_file_size_bytes >= copy_min_bytes():
        return "copy"
    return "insert"


def staging_rows_exist(session: Session, session_token: str) -> bool:
    stmt = select(func.count(LeadImportEtlStagingRow.id)).where(
        LeadImportEtlStagingRow.session_token == session_token
    )
    return int(session.exec(stmt).one()) > 0


def persist_staging_rows(
    session: Session,
    *,
    rows: list[dict[str, Any]],
    source_file_size_bytes: int,
) -> StagingIngestionStrategy:
    if not rows:
        return "insert"

    strategy = choose_staging_ingestion_strategy(
        session,
        total_rows=len(rows),
        source_file_size_bytes=source_file_size_bytes,
    )
    if strategy == "copy":
        try:
            _copy_rows_to_staging(session, rows)
        except Exception as exc:
            logger.warning(
                "Lead import staging COPY fallback to insert detail=%s",
                str(exc).strip() or exc.__class__.__name__,
            )
            _insert_rows_to_staging(session, rows)
            return "insert"
    else:
        _insert_rows_to_staging(session, rows)
    return strategy


def _insert_rows_to_staging(session: Session, rows: list[dict[str, Any]]) -> None:
    session_token = str(rows[0]["session_token"])
    session.exec(
        delete(LeadImportEtlStagingRow).where(LeadImportEtlStagingRow.session_token == session_token)
    )
    chunk = insert_chunk_size()
    for start in range(0, len(rows), chunk):
        current = rows[start : start + chunk]
        if current:
            session.bulk_insert_mappings(LeadImportEtlStagingRow, current)
    session.commit()


def _copy_rows_to_staging(session: Session, rows: list[dict[str, Any]]) -> None:
    bind = session.get_bind()
    raw_connection = bind.raw_connection()
    session_token = str(rows[0]["session_token"])
    columns = (
        "session_token",
        "job_id",
        "requested_by",
        "evento_id",
        "source_file",
        "source_sheet",
        "source_row_number",
        "row_hash",
        "dedupe_key",
        "raw_payload_json",
        "normalized_payload_json",
        "validation_status",
        "validation_errors_json",
        "merge_status",
        "merge_error",
        "merged_lead_id",
        "merged_at",
        "created_at",
        "updated_at",
    )
    copy_sql = (
        "COPY lead_import_etl_staging ("
        + ", ".join(columns)
        + ") FROM STDIN WITH (FORMAT csv, NULL '')"
    )

    def _json(value: Any) -> str | None:
        if value is None:
            return None
        return json.dumps(value, ensure_ascii=False, default=str)

    try:
        with raw_connection.cursor() as cursor:
            if not hasattr(cursor, "copy_expert"):
                raise RuntimeError("DBAPI cursor does not support copy_expert")
            cursor.execute(
                "DELETE FROM lead_import_etl_staging WHERE session_token = %s",
                (session_token,),
            )
            with SpooledTemporaryFile(max_size=2_000_000, mode="w+", newline="", encoding="utf-8") as buffer:
                writer = csv.writer(buffer)
                for row in rows:
                    writer.writerow(
                        [
                            row.get("session_token"),
                            row.get("job_id"),
                            row.get("requested_by"),
                            row.get("evento_id"),
                            row.get("source_file"),
                            row.get("source_sheet"),
                            row.get("source_row_number"),
                            row.get("row_hash"),
                            row.get("dedupe_key"),
                            _json(row.get("raw_payload_json")),
                            _json(row.get("normalized_payload_json")),
                            row.get("validation_status"),
                            _json(row.get("validation_errors_json")),
                            row.get("merge_status"),
                            row.get("merge_error"),
                            row.get("merged_lead_id"),
                            row.get("merged_at").isoformat() if row.get("merged_at") else None,
                            row.get("created_at").isoformat(),
                            row.get("updated_at").isoformat(),
                        ]
                    )
                buffer.seek(0)
                cursor.copy_expert(copy_sql, buffer)
        raw_connection.commit()
    except Exception:
        raw_connection.rollback()
        raise
    finally:
        raw_connection.close()


def mark_superseded_duplicates(
    session: Session,
    session_token: str,
    *,
    auto_commit: bool = True,
) -> int:
    rows = session.exec(
        select(LeadImportEtlStagingRow)
        .where(LeadImportEtlStagingRow.session_token == session_token)
        .where(LeadImportEtlStagingRow.validation_status == "approved")
        .order_by(LeadImportEtlStagingRow.source_row_number.asc(), LeadImportEtlStagingRow.id.asc())
    ).all()
    latest_by_key: dict[str, LeadImportEtlStagingRow] = {}
    superseded_ids: set[int] = set()
    for row in rows:
        row_id = getattr(row, "id", None)
        key = str(row.dedupe_key or "").strip()
        if row_id is None or not key:
            continue
        previous = latest_by_key.get(key)
        if previous is not None and previous.id is not None:
            superseded_ids.add(int(previous.id))
        latest_by_key[key] = row

    if not superseded_ids:
        return 0

    merged_at = datetime.now(timezone.utc)
    changed = 0
    for row in rows:
        row_id = getattr(row, "id", None)
        if row_id is None or int(row_id) not in superseded_ids:
            continue
        if row.merge_status == "skipped":
            continue
        row.merge_status = "skipped"
        row.merge_error = "duplicate_in_batch_superseded"
        row.merged_at = merged_at
        session.add(row)
        changed += 1
    if auto_commit:
        session.commit()
    return changed


def load_rows_for_merge(session: Session, session_token: str) -> list[tuple[dict[str, Any], int]]:
    rows = session.exec(
        select(LeadImportEtlStagingRow)
        .where(LeadImportEtlStagingRow.session_token == session_token)
        .where(LeadImportEtlStagingRow.validation_status == "approved")
        .where(LeadImportEtlStagingRow.merge_status.in_(("pending", "failed")))
        .order_by(LeadImportEtlStagingRow.source_row_number.asc(), LeadImportEtlStagingRow.id.asc())
    ).all()
    batch: list[tuple[dict[str, Any], int]] = []
    for row in rows:
        if not row.normalized_payload_json:
            continue
        payload = backend_payload_to_lead_row(dict(row.normalized_payload_json)).model_dump(mode="python")
        if isinstance(payload.get("data_compra"), datetime):
            payload["data_compra_data"] = payload["data_compra"].date()
            payload["data_compra_hora"] = payload["data_compra"].time()
        batch.append((payload, int(row.source_row_number)))
    return batch


def mark_merge_success(
    session: Session,
    session_token: str,
    *,
    applied_rows: list[tuple[int, str, int | None]],
    auto_commit: bool = True,
) -> None:
    if not applied_rows:
        return
    row_numbers = sorted({int(row_number) for row_number, _action, _lead_id in applied_rows})
    rows_by_number = {
        int(row.source_row_number): row
        for row in session.exec(
            select(LeadImportEtlStagingRow)
            .where(LeadImportEtlStagingRow.session_token == session_token)
            .where(LeadImportEtlStagingRow.source_row_number.in_(row_numbers))
        ).all()
    }
    merged_at = datetime.now(timezone.utc)
    for row_number, action, lead_id in applied_rows:
        row = rows_by_number.get(int(row_number))
        if row is None:
            continue
        row.merge_status = str(action)
        row.merged_lead_id = int(lead_id) if lead_id is not None else None
        row.merge_error = None
        row.merged_at = merged_at
        session.add(row)
    if auto_commit:
        session.commit()


def mark_merge_failures(
    session: Session,
    session_token: str,
    *,
    failed_rows: list[tuple[int, str]],
    auto_commit: bool = True,
) -> None:
    if not failed_rows:
        return
    row_numbers = sorted({int(row_number) for row_number, _reason in failed_rows})
    rows_by_number = {
        int(row.source_row_number): row
        for row in session.exec(
            select(LeadImportEtlStagingRow)
            .where(LeadImportEtlStagingRow.session_token == session_token)
            .where(LeadImportEtlStagingRow.source_row_number.in_(row_numbers))
        ).all()
    }
    merged_at = datetime.now(timezone.utc)
    for row_number, reason in failed_rows:
        row = rows_by_number.get(int(row_number))
        if row is None:
            continue
        row.merge_status = "failed"
        row.merge_error = str(reason)
        row.merged_at = merged_at
        session.add(row)
    if auto_commit:
        session.commit()


def list_merge_failures(session: Session, session_token: str) -> tuple[tuple[int, str], ...]:
    rows = session.exec(
        select(LeadImportEtlStagingRow)
        .where(LeadImportEtlStagingRow.session_token == session_token)
        .where(LeadImportEtlStagingRow.merge_status == "failed")
        .order_by(LeadImportEtlStagingRow.source_row_number.asc(), LeadImportEtlStagingRow.id.asc())
    ).all()
    return tuple((int(row.source_row_number), str(row.merge_error or "")) for row in rows)


def count_rows_by_merge_status(session: Session, session_token: str, merge_status: str) -> int:
    stmt = (
        select(func.count(LeadImportEtlStagingRow.id))
        .where(LeadImportEtlStagingRow.session_token == session_token)
        .where(LeadImportEtlStagingRow.merge_status == merge_status)
    )
    return int(session.exec(stmt).one())


def list_import_errors(
    session: Session,
    session_token: str,
    *,
    phase: ImportErrorPhase = "all",
    limit: int = 200,
    offset: int = 0,
) -> tuple[int, list[dict[str, Any]]]:
    limit = max(1, min(int(limit), 500))
    offset = max(0, int(offset))

    stmt = select(LeadImportEtlStagingRow).where(LeadImportEtlStagingRow.session_token == session_token)
    count_stmt = select(func.count(LeadImportEtlStagingRow.id)).where(
        LeadImportEtlStagingRow.session_token == session_token
    )
    if phase == "validation":
        predicate = LeadImportEtlStagingRow.validation_status == "rejected"
    elif phase == "merge":
        predicate = LeadImportEtlStagingRow.merge_status == "failed"
    else:
        predicate = or_(
            LeadImportEtlStagingRow.validation_status == "rejected",
            LeadImportEtlStagingRow.merge_status == "failed",
        )
    stmt = stmt.where(predicate)
    count_stmt = count_stmt.where(predicate)
    rows = session.exec(
        stmt.order_by(LeadImportEtlStagingRow.source_row_number.asc(), LeadImportEtlStagingRow.id.asc())
        .offset(offset)
        .limit(limit)
    ).all()

    items: list[dict[str, Any]] = []
    for row in rows:
        if phase in {"all", "validation"} and row.validation_status == "rejected":
            messages = list(row.validation_errors_json or [])
            items.append(
                {
                    "row_number": int(row.source_row_number),
                    "phase": "validation",
                    "status": row.validation_status,
                    "message": "; ".join(str(message) for message in messages if str(message).strip()),
                }
            )
        if phase in {"all", "merge"} and row.merge_status == "failed":
            items.append(
                {
                    "row_number": int(row.source_row_number),
                    "phase": "merge",
                    "status": row.merge_status,
                    "message": str(row.merge_error or ""),
                }
            )
    total = int(session.exec(count_stmt).one())
    return total, items
