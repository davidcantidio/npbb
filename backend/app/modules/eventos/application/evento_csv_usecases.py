"""Use cases for evento CSV import/export operations."""

from __future__ import annotations

import csv
import io
import logging
from datetime import date
from typing import Any, Callable

from fastapi import HTTPException, Response, UploadFile, status
from pydantic import ValidationError
from sqlalchemy import func
from sqlmodel import Session, select

from app.models.models import (
    Agencia,
    DivisaoDemandante,
    Diretoria,
    Evento,
    EventoTag,
    EventoTerritorio,
    StatusEvento,
    SubtipoEvento,
    Tag,
    Territorio,
    TipoEvento,
    Usuario,
)
from app.schemas.evento import EventoCreate, EventoUpdate


def exportar_eventos_csv_usecase(
    *,
    session: Session,
    current_user: Usuario,
    skip: int,
    limit: int,
    search: str | None,
    estado: str | None,
    cidade: str | None,
    data: date | None,
    data_inicio: date | None,
    data_fim: date | None,
    diretoria_id: int | None,
    apply_visibility: Callable[..., Any],
    raise_http: Callable[..., None],
    format_csv_date: Callable[[date | None], str],
    csv_filename: Callable[[], str],
) -> Response:
    query = select(Evento)
    query = apply_visibility(query, current_user)

    if search:
        like = f"%{search.strip()}%"
        query = query.where(Evento.nome.ilike(like))

    if estado:
        uf = estado.strip().lower()
        query = query.where(func.lower(Evento.estado) == uf)

    if cidade:
        city = cidade.strip().lower()
        query = query.where(func.lower(Evento.cidade) == city)

    if diretoria_id is not None:
        query = query.where(Evento.diretoria_id == diretoria_id)

    if data_inicio and data_fim and data_fim < data_inicio:
        raise_http(
            status.HTTP_400_BAD_REQUEST,
            code="DATE_RANGE_INVALID",
            message="data_fim deve ser maior/igual a data_inicio",
        )

    if data_inicio or data_fim:
        inicio = func.coalesce(Evento.data_inicio_prevista, Evento.data_inicio_realizada)
        fim = func.coalesce(Evento.data_fim_prevista, Evento.data_fim_realizada, inicio)
        query = query.where(inicio.is_not(None))
        if data_inicio:
            query = query.where(fim >= data_inicio)
        if data_fim:
            query = query.where(inicio <= data_fim)
    elif data:
        inicio = func.coalesce(Evento.data_inicio_prevista, Evento.data_inicio_realizada)
        fim = func.coalesce(Evento.data_fim_prevista, Evento.data_fim_realizada, inicio)
        query = query.where(inicio.is_not(None)).where(inicio <= data).where(fim >= data)

    eventos = session.exec(query.order_by(Evento.id.desc()).offset(skip).limit(limit)).all()

    evento_ids = [e.id for e in eventos if e.id is not None]
    agencia_ids: set[int] = {e.agencia_id for e in eventos if e.agencia_id}
    diretoria_ids: set[int] = {e.diretoria_id for e in eventos if e.diretoria_id}
    status_ids: set[int] = {e.status_id for e in eventos if e.status_id}
    tipo_ids: set[int] = {e.tipo_id for e in eventos if e.tipo_id}
    subtipo_ids: set[int] = {e.subtipo_id for e in eventos if e.subtipo_id}
    divisao_ids: set[int] = {e.divisao_demandante_id for e in eventos if e.divisao_demandante_id}

    def fetch_nome_map(model_cls, ids: set[int]) -> dict[int, str]:
        if not ids:
            return {}
        rows = session.exec(
            select(model_cls.id, model_cls.nome).where(model_cls.id.in_(sorted(ids)))
        ).all()
        return {
            int(row_id): str(nome)
            for row_id, nome in rows
            if row_id is not None and nome is not None
        }

    agencia_nome_by_id = fetch_nome_map(Agencia, agencia_ids)
    diretoria_nome_by_id = fetch_nome_map(Diretoria, diretoria_ids)
    status_nome_by_id = fetch_nome_map(StatusEvento, status_ids)
    tipo_nome_by_id = fetch_nome_map(TipoEvento, tipo_ids)
    subtipo_nome_by_id = fetch_nome_map(SubtipoEvento, subtipo_ids)
    divisao_nome_by_id = fetch_nome_map(DivisaoDemandante, divisao_ids)

    tags_by_evento: dict[int, list[str]] = {}
    territorios_by_evento: dict[int, list[str]] = {}

    if evento_ids:
        tag_rows = session.exec(
            select(EventoTag.evento_id, Tag.nome)
            .join(Tag, EventoTag.tag_id == Tag.id)
            .where(EventoTag.evento_id.in_(evento_ids))
            .order_by(EventoTag.evento_id, Tag.nome)
        ).all()
        for evento_id, nome in tag_rows:
            if evento_id is None or not nome:
                continue
            tags_by_evento.setdefault(int(evento_id), []).append(str(nome))

        territorio_rows = session.exec(
            select(EventoTerritorio.evento_id, Territorio.nome)
            .join(Territorio, EventoTerritorio.territorio_id == Territorio.id)
            .where(EventoTerritorio.evento_id.in_(evento_ids))
            .order_by(EventoTerritorio.evento_id, Territorio.nome)
        ).all()
        for evento_id, nome in territorio_rows:
            if evento_id is None or not nome:
                continue
            territorios_by_evento.setdefault(int(evento_id), []).append(str(nome))

    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter=";")

    writer.writerow(
        [
            "id",
            "nome",
            "descricao",
            "agencia_id",
            "agencia_nome",
            "diretoria_id",
            "diretoria_nome",
            "divisao_demandante_id",
            "divisao_demandante_nome",
            "tipo_id",
            "tipo_nome",
            "subtipo_id",
            "subtipo_nome",
            "status_id",
            "status_nome",
            "estado",
            "cidade",
            "data_inicio_prevista",
            "data_fim_prevista",
            "data_inicio_realizada",
            "data_fim_realizada",
            "investimento",
            "territorios",
            "tags",
            "qr_code_url",
            "created_at",
            "updated_at",
        ]
    )

    for e in eventos:
        eid = int(e.id) if e.id is not None else None
        tags = ", ".join(tags_by_evento.get(eid or -1, [])) if eid is not None else ""
        territorios = ", ".join(territorios_by_evento.get(eid or -1, [])) if eid is not None else ""
        writer.writerow(
            [
                eid or "",
                e.nome,
                e.descricao or "",
                e.agencia_id or "",
                agencia_nome_by_id.get(e.agencia_id, ""),
                e.diretoria_id or "",
                diretoria_nome_by_id.get(e.diretoria_id or -1, "") if e.diretoria_id else "",
                e.divisao_demandante_id or "",
                divisao_nome_by_id.get(e.divisao_demandante_id or -1, "")
                if e.divisao_demandante_id
                else "",
                e.tipo_id or "",
                tipo_nome_by_id.get(e.tipo_id or -1, ""),
                e.subtipo_id or "",
                subtipo_nome_by_id.get(e.subtipo_id or -1, "") if e.subtipo_id else "",
                e.status_id,
                status_nome_by_id.get(e.status_id, ""),
                e.estado,
                e.cidade,
                format_csv_date(e.data_inicio_prevista),
                format_csv_date(e.data_fim_prevista),
                format_csv_date(e.data_inicio_realizada),
                format_csv_date(e.data_fim_realizada),
                str(e.investimento) if e.investimento is not None else "",
                territorios,
                tags,
                e.qr_code_url or "",
                e.created_at.isoformat() if e.created_at else "",
                e.updated_at.isoformat() if e.updated_at else "",
            ]
        )

    content = "\ufeff" + buffer.getvalue()
    headers = {"Content-Disposition": f'attachment; filename="{csv_filename()}"'}
    return Response(content=content, media_type="text/csv; charset=utf-8", headers=headers)


def importar_eventos_csv_usecase(
    *,
    file: UploadFile,
    session: Session,
    current_user: Usuario,
    raise_csv_empty: Callable[[], None],
    raise_http: Callable[..., None],
    detect_csv_delimiter: Callable[[str], str],
    normalize_csv_header: Callable[[str], str],
    build_evento_payload_from_row: Callable[[list[str], dict[str, int]], dict[str, Any]],
    find_evento_match: Callable[..., Evento | None],
    criar_evento: Callable[..., Any],
    atualizar_evento: Callable[..., Any],
    telemetry_logger: logging.Logger,
    sanitize_exception: Callable[[Exception], str],
) -> dict[str, Any]:
    content = file.file.read()
    if not content:
        raise_csv_empty()

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    if not text.strip():
        raise_csv_empty()

    delimiter = detect_csv_delimiter(text)
    rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))
    if not rows:
        raise_csv_empty()

    headers = [normalize_csv_header(h) for h in rows[0]]
    header_index = {h: idx for idx, h in enumerate(headers) if h}
    required_headers = {"nome", "cidade", "estado", "data_inicio_prevista"}
    missing = [h for h in sorted(required_headers) if h not in header_index]
    if missing:
        raise_http(
            status.HTTP_400_BAD_REQUEST,
            code="CSV_MISSING_HEADERS",
            message=f"CSV sem colunas obrigatorias: {', '.join(missing)}",
            extra={"missing_headers": missing},
        )

    success_count = 0
    failed_count = 0
    errors: list[dict[str, Any]] = []
    file_name = getattr(file, "filename", None)

    def log_row_error(
        exc: Exception,
        *,
        row_number: int,
        field: str | None = None,
        error_code: str | None = None,
    ) -> None:
        telemetry_logger.warning(
            "evento_import_row_error",
            extra={
                "row_number": row_number,
                "line_number": row_number,
                "file_name": file_name,
                "field": field,
                "error_type": type(exc).__name__,
                "error_code": error_code,
                "detail": sanitize_exception(exc),
                "user_id": getattr(current_user, "id", None),
            },
        )

    for row_index, row in enumerate(rows[1:], start=2):
        if not any(cell.strip() for cell in row):
            continue

        try:
            payload_data = build_evento_payload_from_row(row, header_index)
            create_payload = EventoCreate.model_validate(payload_data)
            update_payload = EventoUpdate.model_validate(payload_data)

            start_date = create_payload.data_inicio_prevista
            end_date = create_payload.data_fim_prevista or create_payload.data_inicio_prevista

            existing = find_evento_match(
                session,
                current_user,
                create_payload.nome,
                create_payload.cidade,
                create_payload.estado,
                start_date,
                end_date,
            )

            if existing and existing.id is not None:
                atualizar_evento(
                    evento_id=existing.id,
                    payload=update_payload,
                    session=session,
                    current_user=current_user,
                )
            else:
                criar_evento(payload=create_payload, session=session, current_user=current_user)
            success_count += 1
        except Exception as exc:
            if hasattr(exc, "field") and hasattr(exc, "message"):
                failed_count += 1
                field = str(getattr(exc, "field"))
                message = str(getattr(exc, "message"))
                value = getattr(exc, "value", None)
                error: dict[str, Any] = {
                    "line": row_index,
                    "field": field,
                    "message": message,
                }
                if value is not None:
                    error["value"] = value
                errors.append(error)
                log_row_error(
                    exc,
                    row_number=row_index,
                    field=field,
                    error_code="CSV_ROW_ISSUE",
                )
                continue
            if isinstance(exc, ValidationError):
                failed_count += 1
                err = exc.errors()[0] if exc.errors() else {}
                loc = err.get("loc") or []
                field = str(loc[-1]) if loc else "geral"
                message = err.get("msg") or "validacao invalida"
                errors.append(
                    {
                        "line": row_index,
                        "field": field,
                        "message": message,
                    }
                )
                log_row_error(
                    exc,
                    row_number=row_index,
                    field=field,
                    error_code="VALIDATION_ERROR",
                )
                continue
            if not isinstance(exc, HTTPException):
                failed_count += 1
                errors.append(
                    {
                        "line": row_index,
                        "field": "geral",
                        "message": "Erro ao importar linha",
                    }
                )
                log_row_error(
                    exc,
                    row_number=row_index,
                    field="geral",
                    error_code="UNEXPECTED_ERROR",
                )
                continue

            # HTTPException path (kept explicit for payload compatibility)
            http_exc = exc
            failed_count += 1
            field = "geral"
            message = "Erro ao importar linha"
            detail = http_exc.detail
            error_code: str | None = None
            if isinstance(detail, dict):
                field = detail.get("field") or field
                message = detail.get("message") or detail.get("detail") or message
                error_code = detail.get("code") or detail.get("error_code")
            elif isinstance(detail, str):
                message = detail
            errors.append(
                {
                    "line": row_index,
                    "field": field,
                    "message": message,
                }
            )
            log_row_error(
                http_exc,
                row_number=row_index,
                field=field,
                error_code=error_code or "HTTP_EXCEPTION",
            )

    return {
        "total": success_count + failed_count,
        "success": success_count,
        "failed": failed_count,
        "errors": errors,
    }
