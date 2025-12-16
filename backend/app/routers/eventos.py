"""Rotas de eventos (CRUD, dicionarios e detalhes)."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func
from sqlalchemy import delete as sa_delete
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import (
    Agencia,
    Ativacao,
    CotaCortesia,
    Diretoria,
    Evento,
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
from app.schemas.dominios import (
    DiretoriaRead,
    SubtipoEventoRead,
    TagRead,
    TerritorioRead,
    TipoEventoRead,
)
from app.schemas.evento import EventoCreate, EventoListItem, EventoRead, EventoUpdate

router = APIRouter(prefix="/evento", tags=["evento"])


def _raise_http(status_code: int, code: str, message: str, extra: dict | None = None) -> None:
    detail: dict = {"code": code, "message": message}
    if extra:
        detail.update(extra)
    raise HTTPException(status_code=status_code, detail=detail)


def _apply_visibility(query, current_user: Usuario):
    if current_user.tipo_usuario == UsuarioTipo.AGENCIA:
        if not current_user.agencia_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario agencia sem agencia_id",
            )
        return query.where(Evento.agencia_id == current_user.agencia_id)
    return query


@router.get("", response_model=list[EventoListItem])
@router.get("/", response_model=list[EventoListItem])
def listar_eventos(
    response: Response,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    search: str | None = Query(None, min_length=1, max_length=100),
    estado: str | None = Query(None, min_length=1, max_length=10),
    cidade: str | None = Query(None, min_length=1, max_length=100),
    data: date | None = Query(None),
):
    """Lista eventos com paginação e filtros opcionais.

    Filtros:
    - search: busca por nome (case-insensitive)
    - estado: UF (case-insensitive)
    - cidade: cidade (case-insensitive)
    - data: retorna eventos cujo periodo (previsto/realizado) contem a data

    Header `X-Total-Count` contem o total (com filtros aplicados).
    """
    query = select(Evento)
    count_query = select(func.count()).select_from(Evento)

    query = _apply_visibility(query, current_user)
    count_query = _apply_visibility(count_query, current_user)

    if search:
        like = f"%{search.strip()}%"
        query = query.where(Evento.nome.ilike(like))
        count_query = count_query.where(Evento.nome.ilike(like))

    if estado:
        uf = estado.strip().lower()
        query = query.where(func.lower(Evento.estado) == uf)
        count_query = count_query.where(func.lower(Evento.estado) == uf)

    if cidade:
        city = cidade.strip().lower()
        query = query.where(func.lower(Evento.cidade) == city)
        count_query = count_query.where(func.lower(Evento.cidade) == city)

    if data:
        inicio = func.coalesce(Evento.data_inicio_prevista, Evento.data_inicio_realizada)
        fim = func.coalesce(Evento.data_fim_prevista, Evento.data_fim_realizada, inicio)
        query = query.where(inicio.is_not(None)).where(inicio <= data).where(fim >= data)
        count_query = (
            count_query.where(inicio.is_not(None)).where(inicio <= data).where(fim >= data)
        )

    total = session.exec(count_query).one()
    items = session.exec(query.order_by(Evento.id.desc()).offset(skip).limit(limit)).all()
    response.headers["X-Total-Count"] = str(total)
    return items


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


def _parse_status(value: str | None) -> StatusEvento | None:
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    try:
        return StatusEvento(raw)
    except ValueError:
        allowed = ", ".join([s.value for s in StatusEvento])
        _raise_http(
            status.HTTP_400_BAD_REQUEST,
            code="STATUS_INVALID",
            message=f"Status invalido. Use um de: {allowed}",
        )


@router.post("", response_model=EventoRead, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=EventoRead, status_code=status.HTTP_201_CREATED)
def criar_evento(
    payload: EventoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    """Cria um novo evento."""
    agencia_id = payload.agencia_id
    if current_user.tipo_usuario == UsuarioTipo.AGENCIA:
        if not current_user.agencia_id:
            _raise_http(status.HTTP_403_FORBIDDEN, code="FORBIDDEN", message="Usuario sem agencia_id")
        agencia_id = current_user.agencia_id
    if not agencia_id:
        _raise_http(status.HTTP_400_BAD_REQUEST, code="AGENCIA_REQUIRED", message="agencia_id obrigatorio")

    _validate_fk(session, Agencia, agencia_id, "AGENCIA_NOT_FOUND", "Agencia nao encontrada")
    _validate_fk(session, TipoEvento, payload.tipo_id, "TIPO_EVENTO_NOT_FOUND", "Tipo de evento nao encontrado")
    if payload.subtipo_id is not None:
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
    _validate_fk(session, Diretoria, payload.diretoria_id, "DIRETORIA_NOT_FOUND", "Diretoria nao encontrada")
    _validate_fk(session, Funcionario, payload.gestor_id, "GESTOR_NOT_FOUND", "Gestor nao encontrado")

    status_enum = _parse_status(payload.status) or StatusEvento.PREVISTO

    evento = Evento(
        thumbnail=_normalize_str(payload.thumbnail),
        divisao_demandante=_normalize_str(payload.divisao_demandante),
        qr_code_url=_normalize_str(payload.qr_code_url),
        nome=_normalize_str(payload.nome) or "",
        descricao=_normalize_str(payload.descricao) or "",
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
        status=status_enum,
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return EventoRead.model_validate(evento, from_attributes=True)


@router.put("/{evento_id}", response_model=EventoRead)
@router.put("/{evento_id}/", response_model=EventoRead)
def atualizar_evento(
    evento_id: int,
    payload: EventoUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    """Atualiza um evento existente (PUT)."""
    evento = session.get(Evento, evento_id)
    if not evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento nao encontrado")

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        if evento.agencia_id != current_user.agencia_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento nao encontrado")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        _raise_http(status.HTTP_400_BAD_REQUEST, code="NO_FIELDS", message="Nenhum campo para atualizar")

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
    if "tipo_id" in data and data["tipo_id"] is not None:
        _validate_fk(session, TipoEvento, data["tipo_id"], "TIPO_EVENTO_NOT_FOUND", "Tipo de evento nao encontrado")

    if "subtipo_id" in data and data["subtipo_id"] is not None:
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
        _validate_fk(session, Diretoria, data.get("diretoria_id"), "DIRETORIA_NOT_FOUND", "Diretoria nao encontrada")
    if "gestor_id" in data:
        _validate_fk(session, Funcionario, data.get("gestor_id"), "GESTOR_NOT_FOUND", "Gestor nao encontrado")

    if "status" in data:
        status_enum = _parse_status(data.get("status"))
        data["status"] = status_enum

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
    if "divisao_demandante" in data:
        data["divisao_demandante"] = _normalize_str(data["divisao_demandante"])
    if "qr_code_url" in data:
        data["qr_code_url"] = _normalize_str(data["qr_code_url"])

    for key, value in data.items():
        setattr(evento, key, value)

    session.add(evento)
    session.commit()
    session.refresh(evento)
    return EventoRead.model_validate(evento, from_attributes=True)


@router.delete("/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/{evento_id}/", status_code=status.HTTP_204_NO_CONTENT)
def excluir_evento(
    evento_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    """Exclui evento, bloqueando quando houver dependencias."""
    evento = session.get(Evento, evento_id)
    if not evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento nao encontrado")

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        if evento.agencia_id != current_user.agencia_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento nao encontrado")

    ativacoes = session.exec(
        select(func.count()).select_from(Ativacao).where(Ativacao.evento_id == evento_id)
    ).one()
    cotas = session.exec(
        select(func.count()).select_from(CotaCortesia).where(CotaCortesia.evento_id == evento_id)
    ).one()
    paginas = session.exec(
        select(func.count())
        .select_from(QuestionarioPagina)
        .where(QuestionarioPagina.evento_id == evento_id)
    ).one()
    respostas = session.exec(
        select(func.count())
        .select_from(QuestionarioResposta)
        .where(QuestionarioResposta.evento_id == evento_id)
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

    # Limpa relacionamentos simples (join tables) antes de excluir o evento.
    session.exec(sa_delete(EventoTag).where(EventoTag.evento_id == evento_id))
    session.exec(sa_delete(EventoTerritorio).where(EventoTerritorio.evento_id == evento_id))
    session.delete(evento)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/all/cidades", response_model=list[str])
def listar_cidades(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    query = select(Evento.cidade).where(Evento.cidade.is_not(None)).distinct()
    query = _apply_visibility(query, current_user)
    rows = session.exec(query.order_by(func.lower(Evento.cidade))).all()
    values = [c for c in rows if c and str(c).strip()]
    return values


@router.get("/all/estados", response_model=list[str])
def listar_estados(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    query = select(Evento.estado).where(Evento.estado.is_not(None)).distinct()
    query = _apply_visibility(query, current_user)
    rows = session.exec(query.order_by(func.lower(Evento.estado))).all()
    values = [uf for uf in rows if uf and str(uf).strip()]
    return values


@router.get("/all/diretorias", response_model=list[DiretoriaRead])
def listar_diretorias(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    query = select(Diretoria)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(Diretoria.nome.ilike(like))
    return session.exec(query.order_by(Diretoria.nome)).all()


@router.get("/all/tipos-evento", response_model=list[TipoEventoRead])
def listar_tipos_evento(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    query = select(TipoEvento)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(TipoEvento.nome.ilike(like))
    return session.exec(query.order_by(TipoEvento.nome)).all()


@router.get("/all/subtipos-evento", response_model=list[SubtipoEventoRead])
def listar_subtipos_evento(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    tipo_id: int | None = Query(None, ge=1),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    query = select(SubtipoEvento)
    if tipo_id is not None:
        query = query.where(SubtipoEvento.tipo_id == tipo_id)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(SubtipoEvento.nome.ilike(like))
    return session.exec(query.order_by(SubtipoEvento.nome)).all()


@router.get("/all/territorios", response_model=list[TerritorioRead])
def listar_territorios(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    query = select(Territorio)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(Territorio.nome.ilike(like))
    return session.exec(query.order_by(Territorio.nome)).all()


@router.get("/all/tags", response_model=list[TagRead])
def listar_tags(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    query = select(Tag)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(Tag.nome.ilike(like))
    return session.exec(query.order_by(Tag.nome)).all()


@router.get("/{evento_id}", response_model=EventoRead)
@router.get("/{evento_id}/", response_model=EventoRead)
def obter_evento(
    evento_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    evento = session.get(Evento, evento_id)
    if not evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento nao encontrado")

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        if evento.agencia_id != current_user.agencia_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento nao encontrado")

    return EventoRead.model_validate(evento, from_attributes=True)
