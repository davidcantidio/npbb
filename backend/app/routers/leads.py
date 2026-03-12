"""Rotas de conversoes de lead."""

from __future__ import annotations

import csv
import io
import logging
import os
import re
import tracemalloc
from pathlib import Path
from collections.abc import Iterator

import httpx

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile, status
from fastapi import Response as FastAPIResponse
from fastapi.responses import StreamingResponse
from openpyxl import load_workbook
from sqlalchemy import func
from sqlmodel import Session, select

from core.leads_etl.models import coerce_lead_field
from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.lead_batch import BatchStage, LeadBatch, PipelineStatus
from app.models.models import Ativacao, Evento, Lead, LeadAlias, LeadAliasTipo, LeadConversao, Usuario, now_utc
from app.modules.leads_publicidade.application.leads_import_usecases import (
    importar_leads_usecase,
    preview_import_sample_usecase,
    validar_mapeamento_usecase,
)
from app.modules.leads_publicidade.application.leads_import_etl_usecases import (
    commit_leads_with_etl,
    import_leads_with_etl,
)
from app.modules.leads_publicidade.application.etl_import.exceptions import (
    EtlImportContractError,
    EtlImportValidationError,
    EtlPreviewSessionConflictError,
    EtlPreviewSessionNotFoundError,
)
from app.modules.leads_publicidade.application.etl_import.persistence import (
    build_dedupe_key,
    find_existing_lead,
    merge_lead,
    persist_lead_batch,
)
from app.services.lead_mapping import mapear_batch, suggest_column_mapping
from app.services.lead_pipeline_service import executar_pipeline_gold
from app.schemas.lead_batch import (
    ColunasResponse,
    ColumnSuggestionRead,
    ExecutarPipelineResponse,
    LeadBatchPreviewResponse,
    LeadBatchRead,
    MapearBatchRequest,
    MapearBatchResponse,
)
from app.schemas.lead_conversao import LeadConversaoCreate, LeadConversaoRead
from app.schemas.lead_import import LeadImportMapping
from app.schemas.lead_import_etl import ImportEtlCommitRequest, ImportEtlPreviewResponse, ImportEtlResult
from app.schemas.lead_list import LeadListItemRead, LeadListQuery, LeadListResponse
from app.schemas.landing_public import LandingSubmitRequest, LandingSubmitResponse
from app.services.leads_export import generate_gold_export
from app.services.landing_page_submission import get_public_lead_success_message, submit_public_lead
from app.utils.cpf import validate_and_normalize_cpf
from app.utils.http_errors import raise_http_error
from app.utils.text_normalize import normalize_text
from app.utils.fuzzy_match import best_match

router = APIRouter(prefix="/leads", tags=["leads"])
logger = logging.getLogger(__name__)

ALLOWED_IMPORT_EXTENSIONS = {".csv", ".xlsx"}
BATCH_SIZE = 500
DEFAULT_IMPORT_MAX_BYTES = 50 * 1024 * 1024
DEFAULT_BATCH_SUMMARY_LIMIT = 200
DEFAULT_LOG_MEMORY = "0"

CEP_CACHE: dict[str, dict[str, str]] = {}
CEP_CACHE_MAX = 500


def _fetch_cep_data(cep: str) -> dict[str, str] | None:
    if not cep or len(cep) != 8:
        return None
    cached = CEP_CACHE.get(cep)
    if cached is not None:
        return cached or None
    try:
        resp = httpx.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=2.0)
        if resp.status_code != 200:
            CEP_CACHE[cep] = {}
            return None
        data = resp.json()
        if data.get("erro"):
            CEP_CACHE[cep] = {}
            return None
        result = {
            "endereco_rua": (data.get("logradouro") or "").strip(),
            "bairro": (data.get("bairro") or "").strip(),
            "cidade": (data.get("localidade") or "").strip(),
            "estado": (data.get("uf") or "").strip(),
        }
        CEP_CACHE[cep] = result
        if len(CEP_CACHE) > CEP_CACHE_MAX:
            CEP_CACHE.clear()
        return result
    except Exception:
        return None


def _find_existing_lead(session: Session, payload: dict[str, object]) -> Lead | None:
    return find_existing_lead(session, payload)


def _dedupe_key(payload: dict[str, object]) -> str | None:
    return build_dedupe_key(payload)


def _merge_lead(existing: Lead, payload: dict[str, object]) -> None:
    merge_lead(existing, payload)


def _process_batch(
    session: Session,
    batch: list[tuple[dict[str, object], int] | None],
) -> tuple[int, int, int, bool]:
    return persist_lead_batch(session, batch)


def _get_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


MAX_IMPORT_FILE_BYTES = _get_env_int("LEADS_IMPORT_MAX_BYTES", DEFAULT_IMPORT_MAX_BYTES)
BATCH_SUMMARY_LIMIT = _get_env_int("LEADS_IMPORT_BATCH_SUMMARY_LIMIT", DEFAULT_BATCH_SUMMARY_LIMIT)
LOG_MEMORY = os.getenv("LEADS_IMPORT_LOG_MEMORY", DEFAULT_LOG_MEMORY).strip().lower() in {"1", "true", "yes"}


def _log_memory_usage(stage: str, batch_index: int | None = None) -> None:
    if not LOG_MEMORY:
        return
    if not tracemalloc.is_tracing():
        tracemalloc.start()
    current, peak = tracemalloc.get_traced_memory()
    logger.info(
        "Lead import memory stage=%s batch=%s current_mb=%.2f peak_mb=%.2f",
        stage,
        batch_index,
        current / (1024 * 1024),
        peak / (1024 * 1024),
    )


def _get_lead_or_404(*, session: Session, lead_id: int) -> Lead:
    lead = session.get(Lead, lead_id)
    if not lead:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="LEAD_NOT_FOUND",
            message="Lead nao encontrado",
        )
    return lead


def _get_public_submit_context(
    session: Session,
    *,
    payload: LandingSubmitRequest,
) -> tuple[Evento, Ativacao | None, str | None]:
    ativacao: Ativacao | None = None

    if payload.ativacao_id is not None:
        ativacao = session.get(Ativacao, payload.ativacao_id)
        if ativacao is None:
            raise_http_error(
                status.HTTP_404_NOT_FOUND,
                code="ATIVACAO_NOT_FOUND",
                message="Ativacao nao encontrada",
                field="ativacao_id",
            )

        if payload.event_id is not None and payload.event_id != ativacao.evento_id:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="EVENTO_ATIVACAO_MISMATCH",
                message="event_id diverge da ativacao informada",
                field="event_id",
            )
        if not payload.cpf:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="CPF_REQUIRED",
                message="cpf obrigatorio quando ativacao_id for informado",
                field="cpf",
            )
        try:
            cpf_for_conversion = validate_and_normalize_cpf(payload.cpf)
        except ValueError:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="CPF_INVALID",
                message="CPF invalido",
                field="cpf",
            )

        evento = session.get(Evento, ativacao.evento_id)
        if evento is None:
            raise_http_error(
                status.HTTP_404_NOT_FOUND,
                code="EVENTO_NOT_FOUND",
                message="Evento nao encontrado",
                field="event_id",
            )
        return evento, ativacao, cpf_for_conversion

    if payload.event_id is None:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="EVENT_ID_REQUIRED",
            message="event_id obrigatorio quando ativacao_id nao for informado",
            field="event_id",
        )

    evento = session.get(Evento, payload.event_id)
    if evento is None:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="EVENTO_NOT_FOUND",
            message="Evento nao encontrado",
            field="event_id",
        )
    return evento, None, None


@router.post("", response_model=LandingSubmitResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=LandingSubmitResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def criar_lead_publico(
    payload: LandingSubmitRequest,
    session: Session = Depends(get_session),
):
    evento, ativacao, cpf_for_conversion = _get_public_submit_context(
        session,
        payload=payload,
    )
    return submit_public_lead(
        session,
        evento=evento,
        ativacao=ativacao,
        payload=payload,
        success_message=get_public_lead_success_message(session, evento=evento),
        cpf_for_conversion=cpf_for_conversion,
    )


@router.get("", response_model=LeadListResponse)
@router.get("/", response_model=LeadListResponse)
def listar_leads(
    params: LeadListQuery = Depends(),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    total = int(session.exec(select(func.count(Lead.id))).one() or 0)
    offset = (params.page - 1) * params.page_size

    latest_conversao_subquery = (
        select(
            LeadConversao.lead_id.label("lead_id"),
            func.max(LeadConversao.id).label("latest_conversao_id"),
        )
        .group_by(LeadConversao.lead_id)
        .subquery()
    )

    rows = session.exec(
        select(
            Lead.id,
            Lead.nome,
            Lead.sobrenome,
            Lead.email,
            Lead.cpf,
            Lead.telefone,
            Lead.evento_nome,
            Lead.cidade,
            Lead.estado,
            Lead.data_compra,
            Lead.data_criacao,
            LeadConversao.tipo,
            LeadConversao.data_conversao_evento,
            LeadConversao.created_at,
            LeadConversao.evento_id,
            Evento.nome.label("evento_convertido_nome"),
            Lead.rg,
            Lead.genero,
            Lead.is_cliente_bb,
            Lead.is_cliente_estilo,
            Lead.endereco_rua,
            Lead.endereco_numero,
            Lead.complemento,
            Lead.bairro,
            Lead.cep,
        )
        .select_from(Lead)
        .outerjoin(latest_conversao_subquery, latest_conversao_subquery.c.lead_id == Lead.id)
        .outerjoin(LeadConversao, LeadConversao.id == latest_conversao_subquery.c.latest_conversao_id)
        .outerjoin(Evento, Evento.id == LeadConversao.evento_id)
        .order_by(Lead.data_criacao.desc(), Lead.id.desc())
        .offset(offset)
        .limit(params.page_size)
    ).all()

    items: list[LeadListItemRead] = []
    for (
        lead_id,
        nome,
        sobrenome,
        email,
        cpf,
        telefone,
        evento_nome,
        cidade,
        estado,
        data_compra,
        data_criacao,
        tipo_conversao,
        data_conversao_evento,
        data_conversao_criada,
        evento_convertido_id,
        evento_convertido_nome,
        rg,
        genero,
        is_cliente_bb,
        is_cliente_estilo,
        endereco_rua,
        endereco_numero,
        complemento,
        bairro,
        cep,
    ) in rows:
        tipo_conversao_value = None
        if tipo_conversao is not None:
            tipo_conversao_value = (
                tipo_conversao.value if hasattr(tipo_conversao, "value") else str(tipo_conversao)
            )
        nome_completo = " ".join(
            part.strip()
            for part in [nome or "", sobrenome or ""]
            if part and part.strip()
        ) or None
        items.append(
            LeadListItemRead(
                id=int(lead_id),
                nome=nome_completo,
                sobrenome=sobrenome,
                email=email,
                cpf=cpf,
                telefone=telefone,
                evento_nome=evento_nome,
                cidade=cidade,
                estado=estado,
                data_compra=data_compra,
                data_criacao=data_criacao,
                evento_convertido_id=int(evento_convertido_id) if evento_convertido_id is not None else None,
                evento_convertido_nome=evento_convertido_nome,
                tipo_conversao=tipo_conversao_value,
                data_conversao=data_conversao_evento or data_conversao_criada,
                rg=rg,
                genero=genero,
                is_cliente_bb=is_cliente_bb,
                is_cliente_estilo=is_cliente_estilo,
                logradouro=endereco_rua,
                numero=endereco_numero,
                complemento=complemento,
                bairro=bairro,
                cep=cep,
            )
        )

    return LeadListResponse(
        page=params.page,
        page_size=params.page_size,
        total=total,
        items=items,
    )


@router.post("/{lead_id}/conversoes", response_model=LeadConversaoRead, status_code=status.HTTP_201_CREATED)
@router.post("/{lead_id}/conversoes/", response_model=LeadConversaoRead, status_code=status.HTTP_201_CREATED)
def criar_conversao(
    lead_id: int,
    payload: LeadConversaoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    lead = _get_lead_or_404(session=session, lead_id=lead_id)

    conversao = LeadConversao(
        lead_id=lead.id,
        tipo=payload.tipo,
        acao_nome=payload.acao_nome,
        fonte_origem=payload.fonte_origem,
        evento_id=payload.evento_id,
        data_conversao_evento=payload.data_conversao_evento,
        created_at=now_utc(),
    )
    session.add(conversao)
    session.commit()
    session.refresh(conversao)
    return LeadConversaoRead.model_validate(conversao, from_attributes=True)


@router.get("/{lead_id}/conversoes", response_model=list[LeadConversaoRead])
@router.get("/{lead_id}/conversoes/", response_model=list[LeadConversaoRead])
def listar_conversoes(
    lead_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    _get_lead_or_404(session=session, lead_id=lead_id)
    conversoes = session.exec(
        select(LeadConversao).where(LeadConversao.lead_id == lead_id).order_by(LeadConversao.created_at.desc())
    ).all()
    return [LeadConversaoRead.model_validate(item, from_attributes=True) for item in conversoes]


@router.post("/import/upload")
@router.post("/import/upload/")
def validar_upload_import(
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_IMPORT_EXTENSIONS:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_FILE_TYPE",
            message="Formato de arquivo invalido (use .csv ou .xlsx)",
            field="file",
        )
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_IMPORT_FILE_BYTES:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="FILE_TOO_LARGE",
            message="Arquivo excede o tamanho maximo permitido",
            field="file",
            extra={"max_bytes": MAX_IMPORT_FILE_BYTES},
        )
    if size == 0:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="EMPTY_FILE",
            message="Arquivo vazio",
            field="file",
        )

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_IMPORT_FILE_BYTES:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="FILE_TOO_LARGE",
            message="Arquivo excede o tamanho maximo permitido",
            field="file",
            extra={"max_bytes": MAX_IMPORT_FILE_BYTES},
        )
    if size == 0:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="EMPTY_FILE",
            message="Arquivo vazio",
            field="file",
        )

    return {"filename": filename, "size_bytes": size}


@router.get("/referencias/eventos")
@router.get("/referencias/eventos/")
def listar_referencia_eventos(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    stmt = (
        select(Evento.id, Evento.nome, Evento.data_inicio_prevista)
        .order_by(Evento.data_inicio_prevista.desc().nulls_last(), Evento.nome)
    )
    eventos = session.exec(stmt).all()
    return [
        {
            "id": int(eid),
            "nome": nome,
            "data_inicio_prevista": str(data_inicio) if data_inicio else None,
        }
        for eid, nome, data_inicio in eventos
        if eid is not None and nome
    ]


@router.get("/referencias/cidades")
@router.get("/referencias/cidades/")
def listar_referencia_cidades(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    rows = session.exec(select(Evento.cidade).where(Evento.cidade.is_not(None)).distinct()).all()
    return sorted({str(c).strip() for c in rows if c})


@router.get("/referencias/estados")
@router.get("/referencias/estados/")
def listar_referencia_estados(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    rows = session.exec(select(Evento.estado).where(Evento.estado.is_not(None)).distinct()).all()
    return sorted({str(c).strip() for c in rows if c})


@router.get("/referencias/generos")
@router.get("/referencias/generos/")
def listar_referencia_generos(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    rows = session.exec(select(Lead.genero).where(Lead.genero.is_not(None)).distinct()).all()
    return sorted({str(c).strip() for c in rows if c})


REFERENCE_THRESHOLDS = {
    LeadAliasTipo.EVENTO: 0.82,
    LeadAliasTipo.CIDADE: 0.85,
    LeadAliasTipo.ESTADO: 0.9,
    LeadAliasTipo.GENERO: 0.85,
}


@router.get("/referencias/suggest")
@router.get("/referencias/suggest/")
def sugerir_referencia(
    tipo: LeadAliasTipo,
    valor: str,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    threshold = REFERENCE_THRESHOLDS.get(tipo, 0.85)
    if tipo == LeadAliasTipo.EVENTO:
        candidates = [row[0] for row in session.exec(select(Evento.nome)).all() if row and row[0]]
    elif tipo == LeadAliasTipo.CIDADE:
        candidates = [row[0] for row in session.exec(select(Evento.cidade)).all() if row and row[0]]
    elif tipo == LeadAliasTipo.ESTADO:
        candidates = [row[0] for row in session.exec(select(Evento.estado)).all() if row and row[0]]
    else:
        candidates = [row[0] for row in session.exec(select(Lead.genero)).all() if row and row[0]]

    suggestion, score = best_match(valor, candidates, threshold=threshold)
    return {"suggested": suggestion, "score": score, "threshold": threshold}


def _normalize_alias_value(value: str) -> str:
    return normalize_text(value)


def _map_etl_import_error(exc: Exception) -> None:
    if isinstance(exc, EtlPreviewSessionNotFoundError):
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="ETL_SESSION_NOT_FOUND",
            message="session_token invalido ou expirado",
            field="session_token",
        )
    if isinstance(exc, EtlPreviewSessionConflictError):
        raise_http_error(
            status.HTTP_409_CONFLICT,
            code="ETL_SESSION_CONFLICT",
            message=str(exc),
            field="session_token",
        )
    if isinstance(exc, EtlImportValidationError):
        raise_http_error(
            status.HTTP_409_CONFLICT,
            code="ETL_COMMIT_BLOCKED",
            message=str(exc),
        )
    if isinstance(exc, EtlImportContractError):
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="ETL_INVALID_INPUT",
            message=str(exc),
        )
    raise exc


def _serialize_etl_preview_response(result) -> ImportEtlPreviewResponse:
    return ImportEtlPreviewResponse.model_validate(
        {
            "session_token": result.session_token,
            "total_rows": result.total_rows,
            "valid_rows": result.valid_rows,
            "invalid_rows": result.invalid_rows,
            "dq_report": [item.__dict__ for item in result.dq_report],
        }
    )


def _serialize_etl_commit_response(result) -> ImportEtlResult:
    return ImportEtlResult.model_validate(
        {
            "session_token": result.session_token,
            "total_rows": result.total_rows,
            "valid_rows": result.valid_rows,
            "invalid_rows": result.invalid_rows,
            "created": result.created,
            "updated": result.updated,
            "skipped": result.skipped,
            "errors": result.errors,
            "strict": result.strict,
            "status": result.status,
            "dq_report": [item.__dict__ for item in result.dq_report],
        }
    )


@router.get("/aliases")
@router.get("/aliases/")
def buscar_alias(
    tipo: LeadAliasTipo,
    valor_origem: str,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    normalized = _normalize_alias_value(valor_origem)
    alias = session.exec(
        select(LeadAlias).where(
            LeadAlias.tipo == tipo,
            LeadAlias.valor_normalizado == normalized,
        )
    ).first()
    if not alias:
        return None
    return {
        "id": alias.id,
        "tipo": alias.tipo,
        "valor_origem": alias.valor_origem,
        "valor_normalizado": alias.valor_normalizado,
        "canonical_value": alias.canonical_value,
        "evento_id": alias.evento_id,
    }


@router.post("/aliases", status_code=status.HTTP_201_CREATED)
@router.post("/aliases/", status_code=status.HTTP_201_CREATED)
def criar_alias(
    payload: dict,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    try:
        tipo = LeadAliasTipo(payload.get("tipo"))
    except Exception:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_ALIAS_TYPE",
            message="Tipo de alias invalido",
            field="tipo",
        )
    valor_origem = (payload.get("valor_origem") or "").strip()
    if not valor_origem:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_ALIAS_VALUE",
            message="valor_origem obrigatorio",
            field="valor_origem",
        )
    canonical_value = (payload.get("canonical_value") or "").strip() or None
    evento_id = payload.get("evento_id")
    normalized = _normalize_alias_value(valor_origem)

    existing = session.exec(
        select(LeadAlias).where(
            LeadAlias.tipo == tipo,
            LeadAlias.valor_normalizado == normalized,
        )
    ).first()
    if existing:
        updated = False
        if canonical_value and existing.canonical_value != canonical_value:
            existing.canonical_value = canonical_value
            updated = True
        if evento_id and existing.evento_id != evento_id:
            existing.evento_id = evento_id
            updated = True
        if updated:
            session.add(existing)
            session.commit()
            session.refresh(existing)
        return {
            "id": existing.id,
            "tipo": existing.tipo,
            "valor_origem": existing.valor_origem,
            "valor_normalizado": existing.valor_normalizado,
            "canonical_value": existing.canonical_value,
            "evento_id": existing.evento_id,
        }

    alias = LeadAlias(
        tipo=tipo,
        valor_origem=valor_origem,
        valor_normalizado=normalized,
        canonical_value=canonical_value,
        evento_id=evento_id,
        created_at=now_utc(),
    )
    session.add(alias)
    session.commit()
    session.refresh(alias)
    return {
        "id": alias.id,
        "tipo": alias.tipo,
        "valor_origem": alias.valor_origem,
        "valor_normalizado": alias.valor_normalizado,
        "canonical_value": alias.canonical_value,
        "evento_id": alias.evento_id,
    }


def _detect_csv_delimiter(sample_text: str) -> str:
    first_line = sample_text.splitlines()[0] if sample_text else ""
    comma_count = first_line.count(",")
    semi_count = first_line.count(";")
    return ";" if semi_count > comma_count else ","


def _score_row_tabular(row: list[str]) -> int:
    non_empty = [cell for cell in row if cell.strip()]
    if not row:
        return 0
    fill_ratio = len(non_empty) / max(len(row), 1)
    if len(non_empty) >= 2 and fill_ratio >= 0.5:
        return int(fill_ratio * 100)
    return 0


def _detect_data_start_index(rows: list[list[str]]) -> int:
    best_idx = 0
    best_score = -1
    for idx, row in enumerate(rows[:50]):
        score = _score_row_tabular(row)
        if score > best_score:
            best_score = score
            best_idx = idx
    return best_idx


def _read_csv_sample(file: UploadFile, max_rows: int) -> dict:
    file.file.seek(0)
    sample_bytes = file.file.read(4096)
    try:
        sample_text = sample_bytes.decode("utf-8-sig", errors="ignore")
    except Exception:
        sample_text = ""
    delimiter = _detect_csv_delimiter(sample_text)

    file.file.seek(0)
    text_stream = io.TextIOWrapper(file.file, encoding="utf-8-sig", errors="ignore", newline="")
    reader = csv.reader(text_stream, delimiter=delimiter)
    rows: list[list[str]] = []
    try:
        for row in reader:
            if row is None:
                continue
            rows.append([cell.strip() for cell in row])
            if len(rows) >= max_rows + 1:
                break
    finally:
        text_stream.detach()

    start_index = _detect_data_start_index(rows)
    headers = rows[start_index] if rows else []
    data_rows = rows[start_index + 1 :] if len(rows) > start_index + 1 else []
    return {
        "headers": headers,
        "rows": data_rows,
        "delimiter": delimiter,
        "start_index": start_index,
    }


def _read_xlsx_sample(file: UploadFile, max_rows: int) -> dict:
    file.file.seek(0)
    wb = load_workbook(file.file, read_only=True, data_only=True)
    ws = wb.worksheets[0]
    rows: list[list[str]] = []
    for row in ws.iter_rows(max_row=max_rows + 1, values_only=True):
        rows.append([("" if v is None else str(v)).strip() for v in row])
        if len(rows) >= max_rows + 1:
            break
    start_index = _detect_data_start_index(rows)
    headers = rows[start_index] if rows else []
    data_rows = rows[start_index + 1 :] if len(rows) > start_index + 1 else []
    return {
        "headers": headers,
        "rows": data_rows,
        "delimiter": None,
        "start_index": start_index,
    }


def _read_xlsx_rows(file: UploadFile) -> list[list[str]]:
    file.file.seek(0)
    wb = load_workbook(file.file, read_only=True, data_only=True)
    ws = wb.worksheets[0]
    rows: list[list[str]] = []
    for row in ws.iter_rows(values_only=True):
        rows.append([("" if v is None else str(v)).strip() for v in row])
    return rows


def _iter_csv_data_rows(file: UploadFile, delimiter: str, start_index: int) -> Iterator[list[str]]:
    file.file.seek(0)
    text_stream = io.TextIOWrapper(file.file, encoding="utf-8-sig", errors="ignore", newline="")
    reader = csv.reader(text_stream, delimiter=delimiter)
    try:
        for idx, row in enumerate(reader):
            if idx <= start_index:
                continue
            yield [cell.strip() for cell in row]
    finally:
        text_stream.detach()


def _iter_xlsx_data_rows(file: UploadFile, start_index: int) -> Iterator[list[str]]:
    file.file.seek(0)
    wb = load_workbook(file.file, read_only=True, data_only=True)
    ws = wb.worksheets[0]
    for idx, row in enumerate(ws.iter_rows(values_only=True)):
        if idx <= start_index:
            continue
        yield [("" if v is None else str(v)).strip() for v in row]


def _ensure_mapping_has_essential(mappings: list[LeadImportMapping]) -> None:
    essential = {"email", "cpf"}
    mapped_fields = {m.campo for m in mappings if m.campo}
    if not (mapped_fields & essential):
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="MAPPING_MISSING_ESSENTIAL",
            message="Informe email ou CPF",
        )


def _column_samples(rows: list[list[str]], col_index: int, max_samples: int = 5) -> list[str]:
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


def _score_email(values: list[str]) -> float:
    if not values:
        return 0.0
    pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    hits = sum(1 for v in values if pattern.match(v.lower()))
    return hits / len(values)


def _score_cpf(values: list[str]) -> float:
    if not values:
        return 0.0
    pattern = re.compile(r"^\d{11}$")
    hits = 0
    for v in values:
        digits = "".join(ch for ch in v if ch.isdigit())
        if pattern.match(digits):
            hits += 1
    return hits / len(values)


def _score_phone_br(values: list[str]) -> float:
    if not values:
        return 0.0
    # DDDs validos (Brasil)
    valid_ddds = {
        "11", "12", "13", "14", "15", "16", "17", "18", "19",
        "21", "22", "24", "27", "28",
        "31", "32", "33", "34", "35", "37", "38",
        "41", "42", "43", "44", "45", "46",
        "47", "48", "49",
        "51", "53", "54", "55",
        "61", "62", "63", "64", "65", "66", "67", "68", "69",
        "71", "73", "74", "75", "77",
        "79",
        "81", "82", "83", "84", "85", "86", "87", "88", "89",
        "91", "92", "93", "94", "95", "96", "97", "98", "99",
    }
    hits = 0
    for v in values:
        digits = "".join(ch for ch in v if ch.isdigit())
        if digits.startswith("55"):
            digits = digits[2:]
        if len(digits) != 11:
            continue
        ddd = digits[:2]
        numero = digits[2:]
        if ddd not in valid_ddds:
            continue
        if not numero.startswith("9"):
            continue
        hits += 1
    return hits / len(values)


def _score_cep(values: list[str]) -> float:
    if not values:
        return 0.0
    hits = 0
    for v in values:
        digits = "".join(ch for ch in v if ch.isdigit())
        if len(digits) == 8:
            hits += 1
    return hits / len(values)


def _score_uf(values: list[str]) -> float:
    if not values:
        return 0.0
    ufs = {
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
        "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
        "RS", "RO", "RR", "SC", "SP", "SE", "TO",
    }
    hits = sum(1 for v in values if v.strip().upper() in ufs)
    return hits / len(values)


def _score_date(values: list[str]) -> float:
    if not values:
        return 0.0
    patterns = [
        re.compile(r"^\d{2}/\d{2}/\d{4}$"),
        re.compile(r"^\d{4}-\d{2}-\d{2}$"),
    ]
    hits = sum(1 for v in values if any(p.match(v.strip()) for p in patterns))
    return hits / len(values)


def _score_number(values: list[str]) -> float:
    if not values:
        return 0.0
    hits = 0
    for v in values:
        text = v.strip().replace(".", "").replace(",", ".")
        try:
            float(text)
            hits += 1
        except ValueError:
            continue
    return hits / len(values)


def _score_datetime(values: list[str]) -> float:
    if not values:
        return 0.0
    patterns = [
        re.compile(r"^\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}(:\d{2})?$"),
        re.compile(r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(:\d{2})?$"),
    ]
    hits = sum(1 for v in values if any(p.match(v.strip()) for p in patterns))
    return hits / len(values)


def _score_address(values: list[str]) -> float:
    if not values:
        return 0.0
    keywords = ("rua", "avenida", "av", "travessa", "alameda", "rodovia", "praca", "praça")
    hits = 0
    for v in values:
        text = v.strip().lower()
        if any(k in text for k in keywords):
            hits += 1
    return hits / len(values)


def _score_genero(values: list[str]) -> float:
    if not values:
        return 0.0
    vocab = {
        "masculino",
        "feminino",
        "homem",
        "mulher",
        "m",
        "f",
    }
    hits = 0
    for v in values:
        text = v.strip().lower()
        if text in vocab:
            hits += 1
    return hits / len(values)


def _apply_sample_penalty(score: float, sample_size: int) -> float:
    if sample_size <= 0:
        return 0.0
    if sample_size < 3:
        return score * (sample_size / 3)
    return score


def _infer_column_mapping(header: str, samples: list[str]) -> LeadImportMapping:
    header_lc = header.lower().strip()
    sample_size = len(samples)
    thresholds = {
        "email": 0.8,
        "cpf": 0.8,
        "telefone": 0.85,
        "cep": 0.85,
        "uf": 0.85,
        "datetime": 0.85,
        "data": 0.75,
        "numero": 0.85,
        "endereco": 0.7,
        "genero": 0.7,
    }
    scores = {
        "email": _apply_sample_penalty(_score_email(samples), sample_size),
        "cpf": _apply_sample_penalty(_score_cpf(samples), sample_size),
        "telefone": _apply_sample_penalty(_score_phone_br(samples), sample_size),
        "cep": _apply_sample_penalty(_score_cep(samples), sample_size),
        "uf": _apply_sample_penalty(_score_uf(samples), sample_size),
        "data": _apply_sample_penalty(_score_date(samples), sample_size),
        "datetime": _apply_sample_penalty(_score_datetime(samples), sample_size),
        "numero": _apply_sample_penalty(_score_number(samples), sample_size),
        "endereco": _apply_sample_penalty(_score_address(samples), sample_size),
        "genero": _apply_sample_penalty(_score_genero(samples), sample_size),
    }

    campo = None
    confianca = None
    allow_auto = sample_size >= 3

    if allow_auto and scores["email"] >= thresholds["email"]:
        campo = "email"
        confianca = scores["email"]
    elif allow_auto and scores["cpf"] >= thresholds["cpf"]:
        campo = "cpf"
        confianca = scores["cpf"]
    elif allow_auto and scores["telefone"] >= thresholds["telefone"]:
        campo = "telefone"
        confianca = scores["telefone"]
    elif allow_auto and scores["cep"] >= thresholds["cep"]:
        campo = "cep"
        confianca = scores["cep"]
    elif allow_auto and scores["uf"] >= thresholds["uf"]:
        campo = "estado"
        confianca = scores["uf"]
    elif allow_auto and scores["datetime"] >= thresholds["datetime"]:
        campo = "data_compra"
        confianca = scores["datetime"]
    elif "email" in header_lc:
        campo = "email"
        confianca = max(scores["email"], 0.6)
    elif "cpf" in header_lc:
        campo = "cpf"
        confianca = max(scores["cpf"], 0.6)
    elif "telefone" in header_lc or "fone" in header_lc or "cel" in header_lc:
        campo = "telefone"
        confianca = max(scores["telefone"], 0.6)
    elif "cep" in header_lc:
        campo = "cep"
        confianca = max(scores["cep"], 0.6)
    elif "uf" in header_lc or "estado" in header_lc:
        campo = "estado"
        confianca = max(scores["uf"], 0.6)
    elif "compra" in header_lc and "hora" in header_lc:
        campo = "data_compra"
        confianca = max(scores["datetime"], 0.6)
    elif "endereco" in header_lc or "rua" in header_lc or header_lc.startswith("av"):
        campo = "endereco_rua"
        confianca = max(scores["endereco"], 0.55)
    elif "genero" in header_lc or "gênero" in header_lc:
        campo = "genero"
        confianca = max(scores["genero"], 0.55)
    elif "data" in header_lc or "nasc" in header_lc:
        campo = "data_nascimento"
        confianca = max(scores["data"], 0.5)
    elif allow_auto and scores["data"] >= thresholds["data"]:
        campo = "data_nascimento"
        confianca = scores["data"]
    elif allow_auto and scores["numero"] >= thresholds["numero"]:
        campo = "ingresso_qtd"
        confianca = scores["numero"]
    elif allow_auto and scores["endereco"] >= thresholds["endereco"]:
        campo = "endereco_rua"
        confianca = scores["endereco"]
    elif allow_auto and scores["genero"] >= thresholds["genero"]:
        campo = "genero"
        confianca = scores["genero"]

    if confianca is not None:
        confianca = min(confianca, 0.9)
    return LeadImportMapping(coluna=header or "", campo=campo, confianca=confianca)


 


@router.post("/import/sample")
@router.post("/import/sample/")
def preview_import_sample(
    file: UploadFile = File(...),
    sample_rows: int = 10,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    return preview_import_sample_usecase(
        file=file,
        sample_rows=sample_rows,
        session=session,
        current_user=current_user,
        allowed_import_extensions=ALLOWED_IMPORT_EXTENSIONS,
        max_import_file_bytes=MAX_IMPORT_FILE_BYTES,
        read_xlsx_sample=_read_xlsx_sample,
        read_csv_sample=_read_csv_sample,
        column_samples=_column_samples,
        infer_column_mapping=_infer_column_mapping,
        normalize_alias_value=_normalize_alias_value,
        raise_http_error=raise_http_error,
    )


@router.post("/import/validate")
@router.post("/import/validate/")
def validar_mapeamento(
    mappings: list[LeadImportMapping],
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    return validar_mapeamento_usecase(
        mappings=mappings,
        ensure_mapping_has_essential=_ensure_mapping_has_essential,
    )


@router.post("/import")
@router.post("/import/")
def importar_leads(
    file: UploadFile = File(...),
    mappings_json: str = Form(...),
    fonte_origem: str | None = Form(None),
    enriquecer_cep: bool = Form(False),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    return importar_leads_usecase(
        file=file,
        mappings_json=mappings_json,
        fonte_origem=fonte_origem,
        enriquecer_cep=enriquecer_cep,
        session=session,
        current_user=current_user,
        allowed_import_extensions=ALLOWED_IMPORT_EXTENSIONS,
        read_xlsx_sample=_read_xlsx_sample,
        read_csv_sample=_read_csv_sample,
        iter_xlsx_data_rows=_iter_xlsx_data_rows,
        iter_csv_data_rows=_iter_csv_data_rows,
        ensure_mapping_has_essential=_ensure_mapping_has_essential,
        dedupe_key=_dedupe_key,
        process_batch=_process_batch,
        fetch_cep_data=_fetch_cep_data,
        coerce_field=coerce_lead_field,
        log_memory_usage=_log_memory_usage,
        batch_size=BATCH_SIZE,
        batch_summary_limit=BATCH_SUMMARY_LIMIT,
        raise_http_error=raise_http_error,
    )


@router.post("/import/preview")
@router.post("/import/preview/")
def preview_import(
    file: UploadFile = File(...),
    sample_rows: int = 10,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    return preview_import_sample(
        file=file,
        sample_rows=sample_rows,
        session=session,
        current_user=current_user,
    )


@router.post("/import/etl/preview", response_model=ImportEtlPreviewResponse)
@router.post("/import/etl/preview/", response_model=ImportEtlPreviewResponse)
async def preview_import_etl(
    file: UploadFile = File(...),
    evento_id: int = Form(...),
    strict: bool = Form(False),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    try:
        result = await import_leads_with_etl(
            file=file,
            evento_id=evento_id,
            db=session,
            strict=strict,
        )
    except Exception as exc:
        _map_etl_import_error(exc)
    return _serialize_etl_preview_response(result)


@router.post("/import/etl/commit", response_model=ImportEtlResult)
@router.post("/import/etl/commit/", response_model=ImportEtlResult)
async def commit_import_etl(
    payload: ImportEtlCommitRequest,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    try:
        result = await commit_leads_with_etl(
            session_token=payload.session_token,
            evento_id=payload.evento_id,
            db=session,
            force_warnings=payload.force_warnings,
        )
    except Exception as exc:
        _map_etl_import_error(exc)
    return _serialize_etl_commit_response(result)


# ---------------------------------------------------------------------------
# Lead Batch (Bronze) endpoints
# ---------------------------------------------------------------------------


def _read_csv_preview(raw: bytes, max_rows: int = 3) -> dict:
    try:
        text = raw.decode("utf-8-sig", errors="ignore")
    except Exception:
        text = raw.decode("latin-1", errors="ignore")
    delimiter = _detect_csv_delimiter(text)
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows: list[list[str]] = []
    for row in reader:
        rows.append([cell.strip() for cell in row])
        if len(rows) >= max_rows + 1:
            break
    start_index = _detect_data_start_index(rows)
    headers = rows[start_index] if rows else []
    data_rows = rows[start_index + 1 :] if len(rows) > start_index + 1 else []
    return {"headers": headers, "rows": data_rows[:max_rows], "total_rows": len(data_rows)}


def _read_xlsx_preview(raw: bytes, max_rows: int = 3) -> dict:
    wb = load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
    ws = wb.worksheets[0]
    rows: list[list[str]] = []
    total_data = 0
    for row in ws.iter_rows(values_only=True):
        rows.append([("" if v is None else str(v)).strip() for v in row])
    start_index = _detect_data_start_index(rows)
    headers = rows[start_index] if rows else []
    data_rows = rows[start_index + 1 :] if len(rows) > start_index + 1 else []
    total_data = len(data_rows)
    return {"headers": headers, "rows": data_rows[:max_rows], "total_rows": total_data}


@router.get("/export/gold")
@router.get("/export/gold/")
def exportar_leads_gold(
    evento_id: int | None = None,
    formato: str = "xlsx",
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    """Exports Gold-stage leads as .xlsx or .csv.

    Returns HTTP 204 when no leads are found for the selected filters.
    """
    _ = current_user
    resultado = generate_gold_export(db=session, evento_id=evento_id, formato=formato)

    if resultado is None:
        return FastAPIResponse(status_code=204)

    file_bytes, filename = resultado

    if formato == "csv":
        media_type = "text/csv; charset=utf-8"
    else:
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/batches", response_model=LeadBatchRead, status_code=status.HTTP_201_CREATED)
@router.post("/batches/", response_model=LeadBatchRead, status_code=status.HTTP_201_CREATED)
def criar_batch(
    file: UploadFile = File(...),
    plataforma_origem: str = Form(...),
    data_envio: str = Form(...),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    if not current_user.id:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_USER",
            message="Usuario autenticado invalido para upload",
        )

    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_IMPORT_EXTENSIONS:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_FILE_TYPE",
            message="Formato de arquivo invalido (use .csv ou .xlsx)",
            field="file",
        )

    raw = file.file.read()
    if len(raw) == 0:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="EMPTY_FILE",
            message="Arquivo vazio",
            field="file",
        )
    if len(raw) > MAX_IMPORT_FILE_BYTES:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="FILE_TOO_LARGE",
            message="Arquivo excede o tamanho maximo permitido",
            field="file",
            extra={"max_bytes": MAX_IMPORT_FILE_BYTES},
        )

    from datetime import datetime as _dt
    try:
        parsed_data_envio = _dt.fromisoformat(data_envio)
    except (ValueError, TypeError):
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_DATE",
            message="data_envio deve ser ISO-8601",
            field="data_envio",
        )

    batch = LeadBatch(
        enviado_por=int(current_user.id),
        plataforma_origem=plataforma_origem.strip(),
        data_envio=parsed_data_envio,
        nome_arquivo_original=filename,
        arquivo_bronze=raw,
        stage=BatchStage.BRONZE,
        pipeline_status=PipelineStatus.PENDING,
    )
    session.add(batch)
    session.commit()
    session.refresh(batch)
    return LeadBatchRead.model_validate(batch, from_attributes=True)


@router.get("/batches/{batch_id}/arquivo")
@router.get("/batches/{batch_id}/arquivo/")
def download_arquivo_batch(
    batch_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    batch = session.get(LeadBatch, batch_id)
    if not batch:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="BATCH_NOT_FOUND",
            message="Lote nao encontrado",
        )
    if not batch.arquivo_bronze:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="FILE_NOT_FOUND",
            message="Arquivo nao encontrado no lote",
        )
    filename = batch.nome_arquivo_original or "arquivo"
    ext = Path(filename).suffix.lower()
    media_type = "text/csv" if ext == ".csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return StreamingResponse(
        io.BytesIO(batch.arquivo_bronze),
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
    _ = current_user
    batch = session.get(LeadBatch, batch_id)
    if not batch:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="BATCH_NOT_FOUND",
            message="Lote nao encontrado",
        )
    if not batch.arquivo_bronze:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="FILE_NOT_FOUND",
            message="Arquivo nao encontrado no lote",
        )
    filename = batch.nome_arquivo_original or ""
    ext = Path(filename).suffix.lower()
    try:
        if ext == ".csv":
            result = _read_csv_preview(batch.arquivo_bronze)
        else:
            result = _read_xlsx_preview(batch.arquivo_bronze)
    except Exception:
        raise_http_error(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="PREVIEW_PARSE_ERROR",
            message="Nao foi possivel ler o arquivo do lote para gerar o preview.",
        )
    return LeadBatchPreviewResponse(**result)


# ---------------------------------------------------------------------------
# F2 — Silver mapping endpoints
# ---------------------------------------------------------------------------


@router.get("/batches/{batch_id}/colunas", response_model=ColunasResponse)
@router.get("/batches/{batch_id}/colunas/", response_model=ColunasResponse)
def sugerir_mapeamento_colunas(
    batch_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    batch = session.get(LeadBatch, batch_id)
    if not batch:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="BATCH_NOT_FOUND",
            message="Lote nao encontrado",
        )

    try:
        suggestions = suggest_column_mapping(batch_id=batch_id, db=session)
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
    batch = session.get(LeadBatch, batch_id)
    if not batch:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="BATCH_NOT_FOUND",
            message="Lote nao encontrado",
        )

    if not payload.mapeamento:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="EMPTY_MAPPING",
            message="mapeamento nao pode ser vazio",
            field="mapeamento",
        )

    if not current_user.id:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_USER",
            message="Usuario autenticado invalido",
        )

    try:
        result = mapear_batch(
            batch_id=batch_id,
            evento_id=payload.evento_id,
            mapeamento=payload.mapeamento,
            user_id=int(current_user.id),
            db=session,
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


# ---------------------------------------------------------------------------
# F3 — Gold pipeline endpoints
# ---------------------------------------------------------------------------


@router.get("/batches/{batch_id}", response_model=LeadBatchRead)
@router.get("/batches/{batch_id}/", response_model=LeadBatchRead)
def get_batch(
    batch_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    batch = session.get(LeadBatch, batch_id)
    if not batch:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="BATCH_NOT_FOUND",
            message="Lote nao encontrado",
        )
    return LeadBatchRead.model_validate(batch, from_attributes=True)


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
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    batch = session.get(LeadBatch, batch_id)
    if not batch:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="BATCH_NOT_FOUND",
            message="Lote nao encontrado",
        )

    if batch.stage != BatchStage.SILVER:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_STAGE",
            message="Pipeline Gold so pode ser disparado em lotes com stage=silver",
            extra={"stage_atual": batch.stage},
        )

    background_tasks.add_task(executar_pipeline_gold, batch_id)
    return ExecutarPipelineResponse(batch_id=batch_id, status="queued")
