
"""Rotas de lotes Bronze, mapeamento Silver e pipeline Gold."""

from __future__ import annotations

import io
import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi import Response as FastAPIResponse
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import load_only
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.lead_batch import BatchStage, LeadBatch, PipelineStatus
from app.models.models import Usuario
from app.observability.prometheus_leads_import import inc_gold_reclaimed_stale, record_import_upload_rejection
from app.schemas.lead_batch import (
    BatchColumnGroupRead,
    BatchColumnOccurrenceRead,
    ColunasBatchRequest,
    ColunasBatchResponse,
    ColunasResponse,
    ColumnSuggestionRead,
    ExecutarPipelineResponse,
    LeadBatchImportHintRead,
    LeadBatchIntakeResponse,
    LeadBatchPreviewResponse,
    LeadBatchRead,
    MapearBatchRequest,
    MapearBatchResponse,
    MapearLotesBatchItemResponse,
    MapearLotesBatchRequest,
    MapearLotesBatchResponse,
)
from app.services.imports.file_reader import ImportFileError
from app.services.imports.payload_storage import PayloadNotFoundError, read_batch_payload
from app.services.lead_batch_intake_service import (
    execute_lead_batch_intake,
    parse_lead_batch_intake_manifest,
)
from app.services.lead_mapping import (
    BatchMappingBlockedError,
    mapear_batch,
    mapear_batches,
    suggest_batch_column_mapping,
    suggest_column_mapping,
)
from app.services.lead_pipeline_service import (
    is_gold_pipeline_progress_stale,
    load_batch_without_bronze,
    pipeline_stale_after_seconds,
)
from app.utils.http_errors import raise_http_error

from ._shared import (
    ARQUIVO_SHA256_PATTERN,
    MAX_IMPORT_FILE_BYTES,
    _load_owned_batch_or_404,
    _require_current_user_id,
    logger,
)

router = APIRouter()


@router.post("/batches/intake", response_model=LeadBatchIntakeResponse, status_code=status.HTTP_201_CREATED)
@router.post("/batches/intake/", response_model=LeadBatchIntakeResponse, status_code=status.HTTP_201_CREATED)
def intake_batches(
    manifest_json: str = Form(...),
    files: list[UploadFile] = File(...),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    if not current_user.id:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_USER",
            message="Usuario autenticado invalido para upload",
        )

    manifest = parse_lead_batch_intake_manifest(manifest_json)
    return execute_lead_batch_intake(
        session=session,
        user_id=int(current_user.id),
        manifest=manifest,
        files=files,
        max_import_file_bytes=MAX_IMPORT_FILE_BYTES,
    )


@router.post("/batches", response_model=LeadBatchRead, status_code=status.HTTP_201_CREATED)
@router.post("/batches/", response_model=LeadBatchRead, status_code=status.HTTP_201_CREATED)
def criar_batch(
    file: UploadFile = File(...),
    plataforma_origem: str = Form(...),
    data_envio: str = Form(...),
    evento_id: int | None = Form(default=None),
    origem_lote: str | None = Form(default=None),
    enrichment_only: bool = Form(default=False),
    tipo_lead_proponente: str | None = Form(default=None),
    ativacao_id: int | None = Form(default=None),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    if not current_user.id:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_USER",
            message="Usuario autenticado invalido para upload",
        )
    manifest = parse_lead_batch_intake_manifest(
        json.dumps(
            {
                "items": [
                    {
                        "client_row_id": "single-upload",
                        "plataforma_origem": plataforma_origem,
                        "data_envio": data_envio,
                        "evento_id": evento_id,
                        "origem_lote": origem_lote,
                        "enrichment_only": enrichment_only,
                        "tipo_lead_proponente": tipo_lead_proponente,
                        "ativacao_id": ativacao_id,
                        "file_name": file.filename,
                    }
                ]
            },
            ensure_ascii=False,
        )
    )
    try:
        intake = execute_lead_batch_intake(
            session=session,
            user_id=int(current_user.id),
            manifest=manifest,
            files=[file],
            max_import_file_bytes=MAX_IMPORT_FILE_BYTES,
        )
    except Exception as exc:
        if isinstance(exc, ImportFileError):
            record_import_upload_rejection(exc, filename_hint=file.filename)
        raise
    return intake.items[0].batch


@router.get("/batches/import-hint", response_model=LeadBatchImportHintRead)
@router.get("/batches/import-hint/", response_model=LeadBatchImportHintRead)
def obter_hint_importacao_batch(
    arquivo_sha256: str | None = Query(default=None),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    if not current_user.id:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_USER",
            message="Usuario autenticado invalido para consulta de hint",
        )

    normalized_hash = (arquivo_sha256 or "").strip().lower()
    if not ARQUIVO_SHA256_PATTERN.fullmatch(normalized_hash):
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_ARQUIVO_SHA256",
            message="arquivo_sha256 deve ser hexadecimal com 64 caracteres",
            field="arquivo_sha256",
        )

    stmt = (
        select(LeadBatch)
        .options(
            load_only(
                LeadBatch.id,
                LeadBatch.arquivo_sha256,
                LeadBatch.plataforma_origem,
                LeadBatch.data_envio,
                LeadBatch.origem_lote,
                LeadBatch.enrichment_only,
                LeadBatch.tipo_lead_proponente,
                LeadBatch.evento_id,
                LeadBatch.ativacao_id,
                LeadBatch.created_at,
            )
        )
        .where(LeadBatch.enviado_por == int(current_user.id))
        .where(LeadBatch.arquivo_sha256 == normalized_hash)
        .order_by(LeadBatch.created_at.desc(), LeadBatch.id.desc())
        .limit(1)
    )
    source_batch = session.exec(stmt).first()
    if source_batch is None:
        return FastAPIResponse(status_code=status.HTTP_204_NO_CONTENT)

    logger.info(
        "lead_batch.import_hint.matched user_id=%r source_batch_id=%r arquivo_sha256=%r",
        current_user.id,
        source_batch.id,
        normalized_hash,
    )
    return LeadBatchImportHintRead(
        arquivo_sha256=normalized_hash,
        source_batch_id=int(source_batch.id),
        plataforma_origem=source_batch.plataforma_origem,
        data_envio=source_batch.data_envio,
        origem_lote=source_batch.origem_lote,
        enrichment_only=bool(source_batch.enrichment_only),
        tipo_lead_proponente=source_batch.tipo_lead_proponente,
        evento_id=source_batch.evento_id,
        ativacao_id=source_batch.ativacao_id,
        confidence="exact_hash_match",
        source_created_at=source_batch.created_at,
    )


@router.get("/batches/{batch_id}/arquivo")
@router.get("/batches/{batch_id}/arquivo/")
def download_arquivo_batch(
    batch_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    user_id = _require_current_user_id(current_user)
    batch = _load_owned_batch_or_404(session=session, batch_id=batch_id, user_id=user_id)
    try:
        payload = read_batch_payload(batch)
    except PayloadNotFoundError:
        payload = None
    if not payload:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="FILE_NOT_FOUND",
            message="Arquivo nao encontrado no lote",
        )
    filename = batch.nome_arquivo_original or "arquivo"
    ext = Path(filename).suffix.lower()
    media_type = "text/csv" if ext == ".csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return StreamingResponse(
        io.BytesIO(payload),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/batches/{batch_id}/preview", response_model=LeadBatchPreviewResponse)
@router.get("/batches/{batch_id}/preview/", response_model=LeadBatchPreviewResponse)
def preview_batch(
    batch_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    user_id = _require_current_user_id(current_user)
    batch = _load_owned_batch_or_404(session=session, batch_id=batch_id, user_id=user_id)
    try:
        payload = read_batch_payload(batch)
    except PayloadNotFoundError:
        payload = None
    if not payload:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="FILE_NOT_FOUND",
            message="Arquivo nao encontrado no lote",
        )
    filename = batch.nome_arquivo_original or ""
    try:
        from app.routers import leads as leads_router

        preview = leads_router.read_raw_file_preview(payload, filename=filename, sample_rows=3)
        result = {
            "headers": preview.headers,
            "rows": preview.rows,
            "total_rows": len(preview.rows),
        }
    except Exception:
        raise_http_error(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="PREVIEW_PARSE_ERROR",
            message="Nao foi possivel ler o arquivo do lote para gerar o preview.",
        )
    return LeadBatchPreviewResponse(**result)


@router.post("/batches/colunas", response_model=ColunasBatchResponse)
@router.post("/batches/colunas/", response_model=ColunasBatchResponse)
def sugerir_mapeamento_colunas_batch(
    payload: ColunasBatchRequest,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    user_id = _require_current_user_id(current_user)

    try:
        preview = suggest_batch_column_mapping(payload.batch_ids, db=session, owner_user_id=user_id)
    except BatchMappingBlockedError as exc:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="BATCH_MAPPING_BLOCKED",
            message="O mapeamento unificado deste batch foi bloqueado.",
            extra={"blockers": exc.blockers},
        )
    except ValueError as exc:
        message = str(exc)
        raise_http_error(
            status.HTTP_404_NOT_FOUND if "nao encontrado" in message else status.HTTP_400_BAD_REQUEST,
            code="BATCH_NOT_FOUND" if "nao encontrado" in message else "INVALID_BATCH_MAPPING_REQUEST",
            message=message,
        )

    return ColunasBatchResponse(
        batch_ids=preview.batch_ids,
        primary_batch_id=preview.primary_batch_id,
        aggregation_rule=preview.aggregation_rule,
        colunas=[
            BatchColumnGroupRead(
                chave_agregada=group.chave_agregada,
                nome_exibicao=group.nome_exibicao,
                variantes=group.variantes,
                aparece_em_arquivos=group.aparece_em_arquivos,
                ocorrencias=[
                    BatchColumnOccurrenceRead(
                        batch_id=occurrence.batch_id,
                        file_name=occurrence.file_name,
                        coluna_original=occurrence.coluna_original,
                        amostras=occurrence.amostras,
                        campo_sugerido=occurrence.campo_sugerido,
                        confianca=occurrence.confianca,
                        evento_id=occurrence.evento_id,
                        plataforma_origem=occurrence.plataforma_origem,
                    )
                    for occurrence in group.ocorrencias
                ],
                campo_sugerido=group.campo_sugerido,
                confianca=group.confianca,
                warnings=group.warnings,
            )
            for group in preview.colunas
        ],
        warnings=preview.warnings,
        blockers=preview.blockers,
        blocked_batch_ids=preview.blocked_batch_ids,
    )


@router.post("/batches/mapear", response_model=MapearLotesBatchResponse, status_code=status.HTTP_200_OK)
@router.post("/batches/mapear/", response_model=MapearLotesBatchResponse, status_code=status.HTTP_200_OK)
def confirmar_mapeamento_batch(
    payload: MapearLotesBatchRequest,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    if not payload.mapeamento:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="EMPTY_MAPPING",
            message="mapeamento nao pode ser vazio",
            field="mapeamento",
        )

    user_id = _require_current_user_id(current_user, message="Usuario autenticado invalido")

    try:
        result = mapear_batches(
            batch_ids=payload.batch_ids,
            mapeamento=payload.mapeamento,
            user_id=user_id,
            db=session,
        )
    except BatchMappingBlockedError as exc:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="BATCH_MAPPING_BLOCKED",
            message="O mapeamento unificado deste batch foi bloqueado.",
            extra={"blockers": exc.blockers},
        )
    except ValueError as exc:
        message = str(exc)
        if message == "mapeamento nao pode ser vazio":
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="EMPTY_MAPPING",
                message=message,
                field="mapeamento",
            )
        raise_http_error(
            status.HTTP_404_NOT_FOUND if "nao encontrado" in message else status.HTTP_400_BAD_REQUEST,
            code="BATCH_NOT_FOUND" if "nao encontrado" in message else "INVALID_BATCH_MAPPING_REQUEST",
            message=message,
        )

    return MapearLotesBatchResponse(
        batch_ids=[item.batch_id for item in result.results],
        primary_batch_id=result.primary_batch_id,
        total_silver_count=result.total_silver_count,
        results=[
            MapearLotesBatchItemResponse(
                batch_id=item.batch_id,
                silver_count=item.silver_count,
                stage=item.stage,
            )
            for item in result.results
        ],
        stage="silver",
    )


@router.get("/batches/{batch_id}/colunas", response_model=ColunasResponse)
@router.get("/batches/{batch_id}/colunas/", response_model=ColunasResponse)
def sugerir_mapeamento_colunas(
    batch_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    user_id = _require_current_user_id(current_user)
    _load_owned_batch_or_404(session=session, batch_id=batch_id, user_id=user_id)

    try:
        suggestions = suggest_column_mapping(batch_id=batch_id, db=session, owner_user_id=user_id)
    except ValueError as exc:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="BATCH_NOT_FOUND",
            message=str(exc),
        )

    return ColunasResponse(
        batch_id=batch_id,
        colunas=[
            ColumnSuggestionRead(
                coluna_original=s.coluna_original,
                campo_sugerido=s.campo_sugerido,
                confianca=s.confianca,
            )
            for s in suggestions
        ],
    )


@router.post("/batches/{batch_id}/mapear", response_model=MapearBatchResponse, status_code=status.HTTP_200_OK)
@router.post("/batches/{batch_id}/mapear/", response_model=MapearBatchResponse, status_code=status.HTTP_200_OK)
def confirmar_mapeamento(
    batch_id: int,
    payload: MapearBatchRequest,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    user_id = _require_current_user_id(current_user, message="Usuario autenticado invalido")
    _load_owned_batch_or_404(session=session, batch_id=batch_id, user_id=user_id)

    if not payload.mapeamento:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="EMPTY_MAPPING",
            message="mapeamento nao pode ser vazio",
            field="mapeamento",
        )

    try:
        result = mapear_batch(
            batch_id=batch_id,
            evento_id=payload.evento_id,
            mapeamento=payload.mapeamento,
            user_id=user_id,
            db=session,
        )
    except BatchMappingBlockedError as exc:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="BATCH_MAPPING_BLOCKED",
            message="O mapeamento deste lote foi bloqueado.",
            extra={"blockers": exc.blockers},
        )
    except ValueError as exc:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="BATCH_NOT_FOUND",
            message=str(exc),
        )

    return MapearBatchResponse(
        batch_id=result.batch_id,
        silver_count=result.silver_count,
        stage=result.stage,
    )


@router.get("/batches/{batch_id}", response_model=LeadBatchRead)
@router.get("/batches/{batch_id}/", response_model=LeadBatchRead)
def get_batch(
    batch_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    user_id = _require_current_user_id(current_user)
    batch = load_batch_without_bronze(session, batch_id, owner_user_id=user_id)
    if not batch:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="BATCH_NOT_FOUND",
            message="Lote nao encontrado",
        )
    base = LeadBatchRead.model_validate(batch, from_attributes=True)
    return base.model_copy(
        update={
            "gold_pipeline_stale_after_seconds": pipeline_stale_after_seconds(),
            "gold_pipeline_progress_is_stale": is_gold_pipeline_progress_stale(batch),
        }
    )


@router.post(
    "/batches/{batch_id}/executar-pipeline",
    response_model=ExecutarPipelineResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
@router.post(
    "/batches/{batch_id}/executar-pipeline/",
    response_model=ExecutarPipelineResponse,
    status_code=status.HTTP_202_ACCEPTED,
    include_in_schema=False,
)
async def disparar_pipeline(
    batch_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    user_id = _require_current_user_id(current_user, message="Usuario autenticado invalido")
    from app.routers import leads as leads_router

    batch = leads_router.load_batch_without_bronze_for_update(session, batch_id, owner_user_id=user_id)
    if not batch:
        logger.warning(
            "lead_gold_pipeline.dispatch.rejected batch_id=%r user_id=%r reason=%r",
            batch_id,
            user_id,
            "BATCH_NOT_FOUND",
        )
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="BATCH_NOT_FOUND",
            message="Lote nao encontrado",
        )

    if batch.stage != BatchStage.SILVER:
        logger.warning(
            "lead_gold_pipeline.dispatch.rejected batch_id=%r user_id=%r reason=%r stage=%r pipeline_status=%r evento_id=%r",
            batch_id,
            user_id,
            "INVALID_STAGE",
            batch.stage,
            batch.pipeline_status,
            batch.evento_id,
        )
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_STAGE",
            message="Pipeline Gold so pode ser disparado em lotes com stage=silver",
            extra={"stage_atual": batch.stage},
        )

    reclaimed_stale_lock = False
    if batch.pipeline_progress is not None:
        if batch.pipeline_status == PipelineStatus.PENDING and is_gold_pipeline_progress_stale(batch):
            reclaimed_stale_lock = True
            logger.warning(
                "lead_gold_pipeline.dispatch.reclaimed_stale_lock batch_id=%r user_id=%r stage=%r pipeline_status=%r evento_id=%r",
                batch_id,
                user_id,
                batch.stage,
                batch.pipeline_status,
                batch.evento_id,
            )
            inc_gold_reclaimed_stale()
        else:
            logger.warning(
                "lead_gold_pipeline.dispatch.rejected batch_id=%r user_id=%r reason=%r stage=%r pipeline_status=%r evento_id=%r",
                batch_id,
                user_id,
                "PIPELINE_ALREADY_RUNNING",
                batch.stage,
                batch.pipeline_status,
                batch.evento_id,
            )
            raise_http_error(
                status.HTTP_409_CONFLICT,
                code="PIPELINE_ALREADY_RUNNING",
                message="Pipeline Gold ja esta em execucao para este lote",
            )

    leads_router.queue_pipeline_batch(batch)
    queued_stage = batch.stage
    queued_pipeline_status = batch.pipeline_status
    queued_evento_id = batch.evento_id
    session.add(batch)
    session.commit()

    logger.info(
        "lead_gold_pipeline.dispatch.accepted batch_id=%r user_id=%r stage=%r pipeline_status=%r evento_id=%r reclaimed_stale=%r",
        batch_id,
        user_id,
        queued_stage,
        queued_pipeline_status,
        queued_evento_id,
        reclaimed_stale_lock,
    )
    return ExecutarPipelineResponse(
        batch_id=batch_id,
        status="queued",
        reclaimed_stale_lock=reclaimed_stale_lock,
    )
