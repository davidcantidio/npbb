"""Rotas de import/export CSV de eventos."""

from __future__ import annotations

import logging
from datetime import date

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlmodel import Session

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import Usuario
from app.modules.eventos.application.evento_csv_parsers import (
    build_evento_payload_from_row,
    detect_csv_delimiter,
    find_evento_match,
    normalize_csv_header,
)
from app.modules.eventos.application.evento_csv_usecases import (
    exportar_eventos_csv_usecase,
    importar_eventos_csv_usecase,
)
from app.modules.eventos.application.evento_write_usecases import (
    atualizar_evento_usecase,
    criar_evento_usecase,
)
from app.utils.log_sanitize import sanitize_exception

from . import _shared

router = APIRouter()
telemetry_logger = logging.getLogger("app.telemetry")


def _format_csv_date(value: date | None) -> str:
    if not value:
        return ""
    return value.strftime("%Y-%m-%d")


def _csv_filename() -> str:
    return "eventos.csv"


def _raise_csv_empty() -> None:
    _shared._raise_http(
        status.HTTP_400_BAD_REQUEST,
        code="CSV_EMPTY",
        message="Arquivo CSV vazio",
    )


def _find_evento_match_wrapper(session, current_user, nome, cidade, estado, start, end):
    return find_evento_match(
        session=session,
        apply_visibility=_shared._apply_visibility,
        nome=nome,
        cidade=cidade,
        estado=estado,
        start=start,
        end=end,
        current_user=current_user,
    )


@router.get("/export/csv")
def exportar_eventos_csv(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(5000, ge=1, le=10000),
    search: str | None = Query(None, min_length=1, max_length=100),
    estado: str | None = Query(None, min_length=1, max_length=10),
    cidade: str | None = Query(None, min_length=1, max_length=100),
    data: date | None = Query(None),
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    diretoria_id: int | None = Query(None, ge=1),
):
    return exportar_eventos_csv_usecase(
        session=session,
        current_user=current_user,
        skip=skip,
        limit=limit,
        search=search,
        estado=estado,
        cidade=cidade,
        data=data,
        data_inicio=data_inicio,
        data_fim=data_fim,
        diretoria_id=diretoria_id,
        apply_visibility=_shared._apply_visibility,
        raise_http=_shared._raise_http,
        format_csv_date=_format_csv_date,
        csv_filename=_csv_filename,
    )


@router.post("/import/csv")
def importar_eventos_csv(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    return importar_eventos_csv_usecase(
        file=file,
        session=session,
        current_user=current_user,
        raise_csv_empty=_raise_csv_empty,
        raise_http=_shared._raise_http,
        detect_csv_delimiter=detect_csv_delimiter,
        normalize_csv_header=normalize_csv_header,
        build_evento_payload_from_row=build_evento_payload_from_row,
        find_evento_match=_find_evento_match_wrapper,
        criar_evento=criar_evento_usecase,
        atualizar_evento=atualizar_evento_usecase,
        telemetry_logger=telemetry_logger,
        sanitize_exception=sanitize_exception,
    )
