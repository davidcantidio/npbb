"""Backend-side intake for Bronze lead batches."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date as date_type
from datetime import datetime, timezone

from fastapi import UploadFile, status
from sqlalchemy.orm import load_only
from sqlmodel import Session, select

from app.models.lead_batch import BatchStage, LeadBatch, PipelineStatus
from app.models.models import Ativacao, Evento
from app.schemas.lead_batch import (
    LeadBatchImportHintRead,
    LeadBatchIntakeItemRead,
    LeadBatchIntakeRequest,
    LeadBatchIntakeResponse,
    LeadBatchPreviewResponse,
    LeadBatchRead,
)
from app.services.evento_activation_import import (
    ACTIVATION_IMPORT_REQUIRES_AGENCY_CODE,
    get_activation_import_block_reason,
)
from app.services.imports.file_reader import ImportFileError, inspect_upload, read_raw_file_preview
from app.services.imports.payload_storage import persist_batch_payload
from app.utils.http_errors import raise_http_error


@dataclass(frozen=True)
class PreparedLeadBatchIntakeItem:
    client_row_id: str
    batch: LeadBatch
    preview: LeadBatchPreviewResponse
    hint_applied: LeadBatchImportHintRead | None


def parse_lead_batch_intake_manifest(manifest_json: str | None) -> LeadBatchIntakeRequest:
    raw = (manifest_json or "").strip()
    if not raw:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="EMPTY_BATCH_INTAKE_MANIFEST",
            message="manifest_json e obrigatorio para intake de batches.",
            field="manifest_json",
        )
    try:
        payload = LeadBatchIntakeRequest.model_validate_json(raw)
    except Exception as exc:  # pragma: no cover - pydantic raises different concrete errors
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_BATCH_INTAKE_MANIFEST",
            message="manifest_json invalido para intake de batches.",
            field="manifest_json",
        )
        raise exc
    if not payload.items:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="EMPTY_BATCH_INTAKE_MANIFEST",
            message="manifest_json deve conter pelo menos um item.",
            field="manifest_json",
        )
    return payload


def _parse_data_envio(value: str) -> datetime:
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValueError("empty")
    if cleaned.endswith("Z"):
        cleaned = f"{cleaned[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(cleaned)
    except ValueError:
        parsed_date = date_type.fromisoformat(cleaned)
        parsed = datetime.combine(parsed_date, datetime.min.time())
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def _build_import_hint_read(batch: LeadBatch) -> LeadBatchImportHintRead:
    return LeadBatchImportHintRead(
        arquivo_sha256=str(batch.arquivo_sha256 or ""),
        source_batch_id=int(batch.id),
        plataforma_origem=batch.plataforma_origem,
        data_envio=batch.data_envio,
        origem_lote=batch.origem_lote,
        tipo_lead_proponente=batch.tipo_lead_proponente,
        evento_id=batch.evento_id,
        ativacao_id=batch.ativacao_id,
        confidence="exact_hash_match",
        source_created_at=batch.created_at,
    )


def _find_import_hint(session: Session, *, user_id: int, arquivo_sha256: str) -> LeadBatchImportHintRead | None:
    source_batch = session.exec(
        select(LeadBatch)
        .options(
            load_only(
                LeadBatch.id,
                LeadBatch.arquivo_sha256,
                LeadBatch.plataforma_origem,
                LeadBatch.data_envio,
                LeadBatch.origem_lote,
                LeadBatch.tipo_lead_proponente,
                LeadBatch.evento_id,
                LeadBatch.ativacao_id,
                LeadBatch.created_at,
            )
        )
        .where(LeadBatch.enviado_por == user_id)
        .where(LeadBatch.arquivo_sha256 == arquivo_sha256)
        .order_by(LeadBatch.created_at.desc(), LeadBatch.id.desc())
        .limit(1)
    ).first()
    if source_batch is None:
        return None
    return _build_import_hint_read(source_batch)


def _resolve_platform(item_platform: str, hint: LeadBatchImportHintRead | None) -> str:
    plataforma_origem = (item_platform or "").strip()
    if plataforma_origem:
        return plataforma_origem
    if hint is not None:
        plataforma_origem = hint.plataforma_origem.strip()
    if not plataforma_origem:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="PLATAFORMA_ORIGEM_REQUIRED",
            message="plataforma_origem e obrigatorio para intake Bronze.",
            field="plataforma_origem",
        )
    return plataforma_origem


def _resolve_data_envio(item_data_envio: str, hint: LeadBatchImportHintRead | None) -> datetime:
    candidate = (item_data_envio or "").strip()
    if not candidate and hint is not None:
        candidate = hint.data_envio.isoformat()
    try:
        return _parse_data_envio(candidate)
    except (TypeError, ValueError):
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_DATE",
            message="data_envio deve ser ISO-8601 (YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS)",
            field="data_envio",
        )
    raise AssertionError("unreachable")


def _build_preview(raw: bytes, *, filename: str) -> LeadBatchPreviewResponse:
    try:
        preview = read_raw_file_preview(raw, filename=filename, sample_rows=3)
    except Exception:
        raise_http_error(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="PREVIEW_PARSE_ERROR",
            message="Nao foi possivel ler o arquivo do lote para gerar o preview.",
            field="file",
        )
    return LeadBatchPreviewResponse(
        headers=preview.headers,
        rows=preview.rows,
        total_rows=len(preview.rows),
    )


def _coerce_payload_file_count(manifest: LeadBatchIntakeRequest, files: list[UploadFile]) -> None:
    if len(files) != len(manifest.items):
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="BATCH_INTAKE_FILE_COUNT_MISMATCH",
            message="Quantidade de arquivos diverge do manifest_json.",
            extra={
                "manifest_items": len(manifest.items),
                "files": len(files),
            },
        )


def _validate_file_name(expected: str | None, uploaded: str) -> None:
    expected_name = (expected or "").strip()
    if expected_name and expected_name != uploaded:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="BATCH_INTAKE_FILE_NAME_MISMATCH",
            message="file_name do manifest_json diverge do arquivo enviado.",
            field="file_name",
            extra={"expected": expected_name, "uploaded": uploaded},
        )


def _resolve_evento(session: Session, evento_id: int | None) -> Evento | None:
    if evento_id is None:
        return None
    evento = session.get(Evento, evento_id)
    if evento is None:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="EVENTO_NOT_FOUND",
            message="Evento informado nao existe",
            field="evento_id",
        )
    return evento


def _normalize_origem_lote(value: str) -> str:
    origem_clean = (value or "proponente").strip().lower()
    if origem_clean not in ("proponente", "ativacao"):
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_ORIGEM_LOTE",
            message="origem_lote deve ser proponente ou ativacao",
            field="origem_lote",
        )
    return origem_clean


def _resolve_batch_metadata(
    *,
    session: Session,
    evento_id: int | None,
    origem_lote: str,
    tipo_lead_proponente: str | None,
    ativacao_id: int | None,
) -> tuple[int | None, str, str | None, int | None]:
    resolved_evento = _resolve_evento(session, evento_id)
    resolved_evento_id = int(resolved_evento.id) if resolved_evento is not None else None
    origem_clean = _normalize_origem_lote(origem_lote)

    resolved_tipo_lead_prop: str | None = None
    resolved_ativacao_id: int | None = None

    if origem_clean == "ativacao":
        if resolved_evento is None:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="EVENTO_REQUIRED_FOR_ATIVACAO_BATCH",
                message="evento_id e obrigatorio para importacao por ativacao",
                field="evento_id",
            )
        block_reason = get_activation_import_block_reason(resolved_evento)
        if block_reason is not None:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code=ACTIVATION_IMPORT_REQUIRES_AGENCY_CODE,
                message=block_reason,
                field="evento_id",
            )
        if ativacao_id is None:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="ATIVACAO_REQUIRED",
                message="ativacao_id e obrigatorio quando origem_lote=ativacao",
                field="ativacao_id",
            )
        ativacao = session.get(Ativacao, ativacao_id)
        if ativacao is None:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="ATIVACAO_NOT_FOUND",
                message="Ativacao nao encontrada",
                field="ativacao_id",
            )
        if int(ativacao.evento_id) != int(resolved_evento.id):
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="ATIVACAO_EVENTO_MISMATCH",
                message="ativacao_id deve pertencer ao evento_id informado",
                field="ativacao_id",
            )
        resolved_ativacao_id = int(ativacao_id)
    else:
        if ativacao_id is not None:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="ATIVACAO_NOT_ALLOWED",
                message="ativacao_id so e permitido quando origem_lote=ativacao",
                field="ativacao_id",
            )
        if tipo_lead_proponente is not None and str(tipo_lead_proponente).strip():
            normalized_tipo = str(tipo_lead_proponente).strip().lower()
            if normalized_tipo not in ("bilheteria", "entrada_evento"):
                raise_http_error(
                    status.HTTP_400_BAD_REQUEST,
                    code="INVALID_TIPO_LEAD_PROPONENTE",
                    message="tipo_lead_proponente deve ser bilheteria ou entrada_evento",
                    field="tipo_lead_proponente",
                )
            resolved_tipo_lead_prop = normalized_tipo

    return resolved_evento_id, origem_clean, resolved_tipo_lead_prop, resolved_ativacao_id


def execute_lead_batch_intake(
    *,
    session: Session,
    user_id: int,
    manifest: LeadBatchIntakeRequest,
    files: list[UploadFile],
    max_import_file_bytes: int,
) -> LeadBatchIntakeResponse:
    _coerce_payload_file_count(manifest, files)

    prepared_items: list[PreparedLeadBatchIntakeItem] = []
    batches_to_persist: list[LeadBatch] = []

    for item, upload in zip(manifest.items, files, strict=True):
        try:
            filename, _ext, _size = inspect_upload(upload, max_bytes=max_import_file_bytes)
        except ImportFileError as err:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code=err.code,
                message=err.message,
                field=err.field,
                extra=err.extra,
            )
        _validate_file_name(item.file_name, filename)
        raw = upload.file.read()
        arquivo_sha256 = hashlib.sha256(raw).hexdigest()
        hint = _find_import_hint(session, user_id=user_id, arquivo_sha256=arquivo_sha256)
        plataforma_origem = _resolve_platform(item.plataforma_origem, hint)
        parsed_data_envio = _resolve_data_envio(item.data_envio, hint)
        resolved_evento_id, origem_clean, tipo_lead_prop, resolved_ativacao_id = _resolve_batch_metadata(
            session=session,
            evento_id=item.evento_id,
            origem_lote=item.origem_lote,
            tipo_lead_proponente=item.tipo_lead_proponente,
            ativacao_id=item.ativacao_id,
        )

        batch = LeadBatch(
            enviado_por=user_id,
            plataforma_origem=plataforma_origem,
            data_envio=parsed_data_envio,
            nome_arquivo_original=filename,
            arquivo_sha256=arquivo_sha256,
            stage=BatchStage.BRONZE,
            evento_id=resolved_evento_id,
            origem_lote=origem_clean,
            tipo_lead_proponente=tipo_lead_prop,
            ativacao_id=resolved_ativacao_id,
            pipeline_status=PipelineStatus.PENDING,
        )
        persist_batch_payload(batch, raw, content_type=getattr(upload, "content_type", None))
        batches_to_persist.append(batch)
        prepared_items.append(
            PreparedLeadBatchIntakeItem(
                client_row_id=item.client_row_id,
                batch=batch,
                preview=_build_preview(raw, filename=filename),
                hint_applied=hint,
            )
        )

    for batch in batches_to_persist:
        session.add(batch)
    session.flush()
    session.commit()

    return LeadBatchIntakeResponse(
        items=[
            LeadBatchIntakeItemRead(
                client_row_id=item.client_row_id,
                batch=LeadBatchRead.model_validate(item.batch, from_attributes=True),
                preview=item.preview,
                hint_applied=item.hint_applied,
            )
            for item in prepared_items
        ]
    )
