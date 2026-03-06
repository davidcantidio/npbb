"""Use cases for evento write operations."""

from __future__ import annotations

import logging
from datetime import date
from types import SimpleNamespace
from urllib.parse import urlparse

from fastapi import Response, status
from sqlalchemy import func
from sqlalchemy import delete as sa_delete
from sqlmodel import Session, select

from app.models.models import (
    Agencia,
    Ativacao,
    CotaCortesia,
    DivisaoDemandante,
    Diretoria,
    Evento,
    EventoLandingCustomizationAudit,
    EventoTag,
    EventoTerritorio,
    Funcionario,
    QuestionarioPagina,
    QuestionarioResposta,
    StatusEvento,
    SubtipoEvento,
    Tag,
    Territorio,
    TipoEvento,
    Usuario,
    UsuarioTipo,
)
from app.schemas.evento import EventoCreate, EventoRead, EventoUpdate
from app.services.data_health import compute_event_data_health
from app.services.landing_pages import normalize_template_override_input
from app.utils.http_errors import raise_http_error


telemetry_logger = logging.getLogger("app.telemetry")

STATUS_PREVISTO = "Previsto"
STATUS_A_CONFIRMAR = "A Confirmar"
STATUS_CONFIRMADO = "Confirmado"
STATUS_REALIZADO = "Realizado"


def _raise_http(status_code: int, code: str, message: str, extra: dict | None = None) -> None:
    raise_http_error(status_code, code=code, message=message, extra=extra)


def _validate_fk(session: Session, model_cls, obj_id: int | None, code: str, message: str) -> None:
    if obj_id is None:
        return
    if not session.get(model_cls, obj_id):
        _raise_http(status.HTTP_400_BAD_REQUEST, code=code, message=message)


def _normalize_str(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _normalize_estado(value: str | None) -> str | None:
    text = _normalize_str(value)
    return text.upper() if text else None


def _validate_landing_customization_fields(data: dict) -> None:
    if "template_override" in data:
        raw = data.get("template_override")
        normalized = normalize_template_override_input(raw)
        if raw is not None and str(raw).strip() and normalized is None:
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="LANDING_TEMPLATE_OVERRIDE_INVALID",
                message="template_override fora do catalogo homologado",
            )
        data["template_override"] = normalized

    if "hero_image_url" in data:
        hero_image_url = data.get("hero_image_url")
        if hero_image_url:
            parsed = urlparse(hero_image_url)
            allowed = parsed.scheme in {"http", "https"} or hero_image_url.startswith("data:image/")
            if not allowed:
                _raise_http(
                    status.HTTP_400_BAD_REQUEST,
                    code="LANDING_HERO_URL_INVALID",
                    message="hero_image_url deve usar http, https ou data:image/",
                )


def _infer_status_nome(data_inicio_prevista: date | None, data_fim_prevista: date | None) -> str:
    today = date.today()
    if data_inicio_prevista and data_inicio_prevista > today:
        return STATUS_PREVISTO
    if data_fim_prevista and data_fim_prevista < today:
        return STATUS_REALIZADO
    if data_inicio_prevista and data_inicio_prevista <= today:
        return STATUS_CONFIRMADO
    return STATUS_A_CONFIRMAR


def _get_status_id_by_nome(session: Session, nome: str) -> int:
    row = session.exec(
        select(StatusEvento).where(func.lower(StatusEvento.nome) == nome.lower())
    ).first()
    if not row or row.id is None:
        _raise_http(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="STATUS_NOT_CONFIGURED",
            message=f"Status '{nome}' nao configurado no banco",
        )
    return row.id


def _normalize_unique_ids(values: list[int] | None, *, code: str, message: str) -> list[int]:
    if not values:
        return []
    unique: list[int] = []
    seen: set[int] = set()
    for raw in values:
        try:
            value = int(raw)
        except (TypeError, ValueError):
            _raise_http(status.HTTP_400_BAD_REQUEST, code=code, message=message)
        if value < 1:
            _raise_http(status.HTTP_400_BAD_REQUEST, code=code, message=message)
        if value in seen:
            continue
        seen.add(value)
        unique.append(value)
    return unique


def criar_evento_usecase(payload: EventoCreate, session: Session, current_user: Usuario) -> EventoRead:
    agencia_id = payload.agencia_id
    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        agencia_id = current_user.agencia_id

    _validate_fk(session, Agencia, agencia_id, "AGENCIA_NOT_FOUND", "Agencia nao encontrada")
    if payload.tipo_id is not None:
        _validate_fk(
            session,
            TipoEvento,
            payload.tipo_id,
            "TIPO_EVENTO_NOT_FOUND",
            "Tipo de evento nao encontrado",
        )
    if payload.subtipo_id is not None:
        if payload.tipo_id is None:
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="TIPO_EVENTO_REQUIRED",
                message="tipo_id obrigatorio quando subtipo_id informado",
            )
        subtipo = session.get(SubtipoEvento, payload.subtipo_id)
        if not subtipo:
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="SUBTIPO_EVENTO_NOT_FOUND",
                message="Subtipo de evento nao encontrado",
            )
        if subtipo.tipo_id != payload.tipo_id:
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="SUBTIPO_EVENTO_INVALID",
                message="Subtipo nao pertence ao tipo informado",
            )
    _validate_fk(
        session, Diretoria, payload.diretoria_id, "DIRETORIA_NOT_FOUND", "Diretoria nao encontrada"
    )
    _validate_fk(
        session,
        DivisaoDemandante,
        payload.divisao_demandante_id,
        "DIVISAO_DEMANDANTE_NOT_FOUND",
        "Divisao demandante nao encontrada",
    )
    _validate_fk(session, Funcionario, payload.gestor_id, "GESTOR_NOT_FOUND", "Gestor nao encontrado")

    tag_ids = _normalize_unique_ids(payload.tag_ids, code="TAG_ID_INVALID", message="tag_ids invalidos")
    territorio_ids = _normalize_unique_ids(
        payload.territorio_ids, code="TERRITORIO_ID_INVALID", message="territorio_ids invalidos"
    )
    for tag_id in tag_ids:
        _validate_fk(session, Tag, tag_id, "TAG_NOT_FOUND", "Tag nao encontrada")
    for territorio_id in territorio_ids:
        _validate_fk(session, Territorio, territorio_id, "TERRITORIO_NOT_FOUND", "Territorio nao encontrado")

    status_id = payload.status_id
    if status_id is not None:
        _validate_fk(session, StatusEvento, status_id, "STATUS_NOT_FOUND", "Status nao encontrado")
    else:
        status_nome = _infer_status_nome(payload.data_inicio_prevista, payload.data_fim_prevista)
        status_id = _get_status_id_by_nome(session, status_nome)

    landing_data = {
        "template_override": _normalize_str(payload.template_override),
        "hero_image_url": _normalize_str(payload.hero_image_url),
        "cta_personalizado": _normalize_str(payload.cta_personalizado),
        "descricao_curta": _normalize_str(payload.descricao_curta),
    }
    _validate_landing_customization_fields(landing_data)

    evento = Evento(
        thumbnail=_normalize_str(payload.thumbnail),
        template_override=landing_data["template_override"],
        hero_image_url=landing_data["hero_image_url"],
        cta_personalizado=landing_data["cta_personalizado"],
        descricao_curta=landing_data["descricao_curta"],
        divisao_demandante_id=payload.divisao_demandante_id,
        qr_code_url=_normalize_str(payload.qr_code_url),
        external_project_code=_normalize_str(payload.external_project_code),
        nome=_normalize_str(payload.nome) or "",
        descricao=_normalize_str(payload.descricao),
        investimento=payload.investimento,
        data_inicio_prevista=payload.data_inicio_prevista,
        data_inicio_realizada=payload.data_inicio_realizada,
        data_fim_prevista=payload.data_fim_prevista,
        data_fim_realizada=payload.data_fim_realizada,
        publico_projetado=payload.publico_projetado,
        publico_realizado=payload.publico_realizado,
        concorrencia=payload.concorrencia,
        cidade=_normalize_str(payload.cidade) or "",
        estado=_normalize_estado(payload.estado) or "",
        agencia_id=agencia_id,
        diretoria_id=payload.diretoria_id,
        gestor_id=payload.gestor_id,
        tipo_id=payload.tipo_id,
        subtipo_id=payload.subtipo_id,
        status_id=status_id,
    )
    session.add(evento)
    session.flush()

    if evento.id is None:
        _raise_http(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="EVENTO_CREATE_FAILED",
            message="Falha ao criar evento",
        )

    for territorio_id in territorio_ids:
        session.add(EventoTerritorio(evento_id=evento.id, territorio_id=territorio_id))
    for tag_id in tag_ids:
        session.add(EventoTag(evento_id=evento.id, tag_id=tag_id))

    session.commit()
    session.refresh(evento)
    read = EventoRead.model_validate(evento, from_attributes=True)
    return read.model_copy(update={"tag_ids": tag_ids, "territorio_ids": territorio_ids})


def atualizar_evento_usecase(
    evento_id: int, payload: EventoUpdate, session: Session, current_user: Usuario
) -> EventoRead:
    evento = session.get(Evento, evento_id)
    if not evento:
        _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        if evento.agencia_id != current_user.agencia_id:
            _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        _raise_http(
            status.HTTP_400_BAD_REQUEST,
            code="VALIDATION_ERROR_NO_FIELDS",
            message="Nenhum campo para atualizar",
        )

    tag_ids_update = data.pop("tag_ids", None)
    territorio_ids_update = data.pop("territorio_ids", None)

    before_tag_ids = session.exec(
        select(EventoTag.tag_id).where(EventoTag.evento_id == evento_id).order_by(EventoTag.tag_id)
    ).all()
    before_territorio_ids = session.exec(
        select(EventoTerritorio.territorio_id)
        .where(EventoTerritorio.evento_id == evento_id)
        .order_by(EventoTerritorio.territorio_id)
    ).all()

    before_status_name = None
    if evento.status_id:
        status_before = session.get(StatusEvento, evento.status_id)
        if status_before:
            before_status_name = status_before.nome

    before_proxy = SimpleNamespace(
        **evento.model_dump(),
        tag_ids=list(before_tag_ids),
        territorio_ids=list(before_territorio_ids),
    )
    before_missing = compute_event_data_health(before_proxy, status_name=before_status_name)["missing_fields"]

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA:
        if "agencia_id" in data and data["agencia_id"] != evento.agencia_id:
            _raise_http(
                status.HTTP_403_FORBIDDEN,
                code="FORBIDDEN",
                message="Usuario agencia nao pode alterar agencia_id",
            )

    if "agencia_id" in data and data["agencia_id"] is not None:
        _validate_fk(session, Agencia, data["agencia_id"], "AGENCIA_NOT_FOUND", "Agencia nao encontrada")

    tipo_id = data.get("tipo_id", evento.tipo_id)
    if "tipo_id" in data:
        if data["tipo_id"] is not None:
            _validate_fk(
                session,
                TipoEvento,
                data["tipo_id"],
                "TIPO_EVENTO_NOT_FOUND",
                "Tipo de evento nao encontrado",
            )
            tipo_id = data["tipo_id"]
        else:
            tipo_id = None

    if "subtipo_id" in data and data["subtipo_id"] is not None:
        if tipo_id is None:
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="TIPO_EVENTO_REQUIRED",
                message="tipo_id obrigatorio quando subtipo_id informado",
            )
        subtipo = session.get(SubtipoEvento, data["subtipo_id"])
        if not subtipo:
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="SUBTIPO_EVENTO_NOT_FOUND",
                message="Subtipo de evento nao encontrado",
            )
        if subtipo.tipo_id != tipo_id:
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="SUBTIPO_EVENTO_INVALID",
                message="Subtipo nao pertence ao tipo informado",
            )

    if "diretoria_id" in data:
        _validate_fk(
            session,
            Diretoria,
            data.get("diretoria_id"),
            "DIRETORIA_NOT_FOUND",
            "Diretoria nao encontrada",
        )
    if "gestor_id" in data:
        _validate_fk(session, Funcionario, data.get("gestor_id"), "GESTOR_NOT_FOUND", "Gestor nao encontrado")
    if "divisao_demandante_id" in data:
        _validate_fk(
            session,
            DivisaoDemandante,
            data.get("divisao_demandante_id"),
            "DIVISAO_DEMANDANTE_NOT_FOUND",
            "Divisao demandante nao encontrada",
        )

    if "status_id" in data:
        if data.get("status_id") is None:
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="STATUS_REQUIRED",
                message="status_id obrigatorio",
            )
        _validate_fk(
            session,
            StatusEvento,
            data.get("status_id"),
            "STATUS_NOT_FOUND",
            "Status nao encontrado",
        )

    if "nome" in data:
        data["nome"] = _normalize_str(data["nome"])
    if "descricao" in data:
        data["descricao"] = _normalize_str(data["descricao"])
    if "cidade" in data:
        data["cidade"] = _normalize_str(data["cidade"])
    if "estado" in data:
        data["estado"] = _normalize_estado(data["estado"])
    if "thumbnail" in data:
        data["thumbnail"] = _normalize_str(data["thumbnail"])
    if "template_override" in data:
        data["template_override"] = _normalize_str(data["template_override"])
    if "hero_image_url" in data:
        data["hero_image_url"] = _normalize_str(data["hero_image_url"])
    if "cta_personalizado" in data:
        data["cta_personalizado"] = _normalize_str(data["cta_personalizado"])
    if "descricao_curta" in data:
        data["descricao_curta"] = _normalize_str(data["descricao_curta"])
    if "qr_code_url" in data:
        data["qr_code_url"] = _normalize_str(data["qr_code_url"])
    if "external_project_code" in data:
        data["external_project_code"] = _normalize_str(data["external_project_code"])

    _validate_landing_customization_fields(data)

    governed_fields = ["template_override", "hero_image_url", "cta_personalizado", "descricao_curta"]
    customization_audits: list[EventoLandingCustomizationAudit] = []
    for field_name in governed_fields:
        if field_name not in data:
            continue
        old_value = getattr(evento, field_name)
        new_value = data.get(field_name)
        if old_value == new_value:
            continue
        customization_audits.append(
            EventoLandingCustomizationAudit(
                event_id=evento_id,
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                changed_by_user_id=getattr(current_user, "id", None),
            )
        )

    for key, value in data.items():
        setattr(evento, key, value)

    session.add(evento)

    if tag_ids_update is not None:
        tag_ids = _normalize_unique_ids(tag_ids_update, code="TAG_ID_INVALID", message="tag_ids invalidos")
        for tag_id in tag_ids:
            _validate_fk(session, Tag, tag_id, "TAG_NOT_FOUND", "Tag nao encontrada")
        session.exec(sa_delete(EventoTag).where(EventoTag.evento_id == evento_id))
        for tag_id in tag_ids:
            session.add(EventoTag(evento_id=evento_id, tag_id=tag_id))

    if territorio_ids_update is not None:
        territorio_ids = _normalize_unique_ids(
            territorio_ids_update, code="TERRITORIO_ID_INVALID", message="territorio_ids invalidos"
        )
        for territorio_id in territorio_ids:
            _validate_fk(session, Territorio, territorio_id, "TERRITORIO_NOT_FOUND", "Territorio nao encontrado")
        session.exec(sa_delete(EventoTerritorio).where(EventoTerritorio.evento_id == evento_id))
        for territorio_id in territorio_ids:
            session.add(EventoTerritorio(evento_id=evento_id, territorio_id=territorio_id))

    for audit in customization_audits:
        session.add(audit)

    session.commit()
    session.refresh(evento)

    tag_ids_final = session.exec(
        select(EventoTag.tag_id).where(EventoTag.evento_id == evento_id).order_by(EventoTag.tag_id)
    ).all()
    territorio_ids_final = session.exec(
        select(EventoTerritorio.territorio_id)
        .where(EventoTerritorio.evento_id == evento_id)
        .order_by(EventoTerritorio.territorio_id)
    ).all()

    status_after_name = before_status_name
    if "status_id" in data:
        status_after = session.get(StatusEvento, data.get("status_id"))
        if status_after:
            status_after_name = status_after.nome

    after_proxy = SimpleNamespace(
        **evento.model_dump(),
        tag_ids=list(tag_ids_final),
        territorio_ids=list(territorio_ids_final),
    )
    after_missing = compute_event_data_health(after_proxy, status_name=status_after_name)["missing_fields"]

    completed_fields = [field for field in before_missing if field not in after_missing]
    for field in completed_fields:
        telemetry_logger.info(
            "completed_missing_field",
            extra={
                "event_id": evento_id,
                "evento_id": evento_id,
                "field_id": field,
                "user_id": getattr(current_user, "id", None),
            },
        )

    read = EventoRead.model_validate(evento, from_attributes=True)
    return read.model_copy(update={"tag_ids": list(tag_ids_final), "territorio_ids": list(territorio_ids_final)})


def excluir_evento_usecase(evento_id: int, session: Session, current_user: Usuario) -> Response:
    evento = session.get(Evento, evento_id)
    if not evento:
        _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        if evento.agencia_id != current_user.agencia_id:
            _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    ativacoes = session.exec(
        select(func.count()).select_from(Ativacao).where(Ativacao.evento_id == evento_id)
    ).one()
    cotas = session.exec(
        select(func.count()).select_from(CotaCortesia).where(CotaCortesia.evento_id == evento_id)
    ).one()
    paginas = session.exec(
        select(func.count()).select_from(QuestionarioPagina).where(QuestionarioPagina.evento_id == evento_id)
    ).one()
    respostas = session.exec(
        select(func.count()).select_from(QuestionarioResposta).where(QuestionarioResposta.evento_id == evento_id)
    ).one()

    blocked = {
        "ativacoes": int(ativacoes),
        "cotas": int(cotas),
        "paginas_questionario": int(paginas),
        "respostas_questionario": int(respostas),
    }
    if any(v > 0 for v in blocked.values()):
        _raise_http(
            status.HTTP_409_CONFLICT,
            code="EVENTO_DELETE_BLOCKED",
            message="Nao e possivel excluir evento com vinculos",
            extra={"dependencies": {k: v for k, v in blocked.items() if v > 0}},
        )

    session.exec(sa_delete(EventoTag).where(EventoTag.evento_id == evento_id))
    session.exec(sa_delete(EventoTerritorio).where(EventoTerritorio.evento_id == evento_id))
    session.delete(evento)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
