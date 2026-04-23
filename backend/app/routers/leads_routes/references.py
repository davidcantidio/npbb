
"""Rotas auxiliares de referencia, aliases e validacao de upload."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import Evento, Lead, LeadAlias, LeadAliasTipo, LeadEvento, Usuario, now_utc
from app.observability.prometheus_leads_import import record_import_upload_rejection
from app.schemas.lead_batch import LeadReferenceEventoRead
from app.services.evento_activation_import import get_activation_import_block_reason_from_agencia_id
from app.services.imports.file_reader import ImportFileError, inspect_upload
from app.utils.fuzzy_match import best_match
from app.utils.http_errors import raise_http_error
from app.utils.text_normalize import normalize_text

from ._shared import MAX_IMPORT_FILE_BYTES

router = APIRouter()


@router.post("/import/upload")
@router.post("/import/upload/")
def validar_upload_import(
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    try:
        filename, _ext, size = inspect_upload(file, max_bytes=MAX_IMPORT_FILE_BYTES)
    except ImportFileError as err:
        record_import_upload_rejection(err, filename_hint=file.filename)
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code=err.code,
            message=err.message,
            field=err.field,
            extra=err.extra,
        )
    return {"filename": filename, "size_bytes": size}


@router.get("/referencias/eventos", response_model=list[LeadReferenceEventoRead])
@router.get("/referencias/eventos/", response_model=list[LeadReferenceEventoRead])
def listar_referencia_eventos(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    count_stmt = (
        select(LeadEvento.evento_id, func.count(func.distinct(LeadEvento.lead_id)))
        .group_by(LeadEvento.evento_id)
    )
    lead_counts: dict[int, int] = {}
    for evento_id, cnt in session.exec(count_stmt).all():
        if evento_id is not None:
            lead_counts[int(evento_id)] = int(cnt or 0)

    stmt = (
        select(Evento.id, Evento.nome, Evento.data_inicio_prevista, Evento.agencia_id)
        .order_by(Evento.data_inicio_prevista.desc().nulls_last(), Evento.nome)
    )
    eventos = session.exec(stmt).all()
    return [
        {
            "id": int(eid),
            "nome": nome,
            "data_inicio_prevista": str(data_inicio) if data_inicio else None,
            "agencia_id": int(agencia_id) if agencia_id is not None else None,
            "supports_activation_import": bool(agencia_id is not None),
            "activation_import_block_reason": get_activation_import_block_reason_from_agencia_id(agencia_id),
            "leads_count": lead_counts.get(int(eid), 0),
        }
        for eid, nome, data_inicio, agencia_id in eventos
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
