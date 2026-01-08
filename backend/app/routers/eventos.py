"""Rotas de eventos (CRUD, dicionarios e detalhes)."""

from __future__ import annotations

import csv
import io
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import case, func
from sqlalchemy import delete as sa_delete
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import (
    Agencia,
    Ativacao,
    CotaCortesia,
    DivisaoDemandante,
    Diretoria,
    Evento,
    EventoTag,
    EventoTerritorio,
    FormularioLandingTemplate,
    FormularioLeadCampo,
    FormularioLeadConfig,
    Funcionario,
    Gamificacao,
    QuestionarioPagina,
    QuestionarioResposta,
    StatusEvento,
    SubtipoEvento,
    Tag,
    Territorio,
    TipoEvento,
    Usuario,
    UsuarioTipo,
    now_utc,
)
from app.schemas.ativacao import AtivacaoCreate, AtivacaoRead
from app.schemas.dominios import (
    DivisaoDemandanteRead,
    DiretoriaRead,
    StatusEventoRead,
    SubtipoEventoRead,
    TagCreate,
    TagRead,
    TerritorioRead,
    TipoEventoRead,
)
from app.schemas.evento import EventoCreate, EventoListItem, EventoRead, EventoUpdate
from app.schemas.formulario_lead import (
    FormularioLandingTemplateRead,
    FormularioLeadCampoRead,
    FormularioLeadConfigRead,
    FormularioLeadConfigUpsert,
)
from app.schemas.gamificacao import GamificacaoCreate, GamificacaoRead
from app.schemas.questionario import (
    QuestionarioEstruturaRead,
    QuestionarioEstruturaWrite,
    QuestionarioPaginaRead,
)
from app.services.questionario import load_questionario_estrutura, replace_questionario_estrutura
from app.utils.http_errors import raise_http_error
from app.utils.urls import build_evento_public_urls

router = APIRouter(prefix="/evento", tags=["evento"])

FORMULARIO_CAMPOS_CATALOGO = [
    "CPF",
    "Nome",
    "Sobrenome",
    "Telefone",
    "Email",
    "Data de nascimento",
    "Endereco",
    "Interesses",
    "Genero",
    "Area de atuacao",
]

FORMULARIO_CAMPOS_ORDEM_BY_LOWER = {nome.lower(): index for index, nome in enumerate(FORMULARIO_CAMPOS_CATALOGO)}

# Defaults (MVP) quando ainda nao existe config persistida para o evento.
# Screenshot/UX: CPF, Nome, Sobrenome, Email e Data de nascimento ativos; Sobrenome opcional.
FORMULARIO_CAMPOS_DEFAULT: list[tuple[str, bool]] = [
    ("CPF", True),
    ("Nome", True),
    ("Sobrenome", False),
    ("Email", True),
    ("Data de nascimento", True),
]


def _raise_http(status_code: int, code: str, message: str, extra: dict | None = None) -> None:
    raise_http_error(status_code, code=code, message=message, extra=extra)


def _apply_visibility(query, current_user: Usuario):
    if current_user.tipo_usuario == UsuarioTipo.AGENCIA:
        if not current_user.agencia_id:
            _raise_http(
                status.HTTP_403_FORBIDDEN,
                code="FORBIDDEN",
                message="Usuario agencia sem agencia_id",
                extra={"field": "agencia_id"},
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
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    diretoria_id: int | None = Query(None, ge=1),
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

    if diretoria_id is not None:
        query = query.where(Evento.diretoria_id == diretoria_id)
        count_query = count_query.where(Evento.diretoria_id == diretoria_id)

    if data_inicio and data_fim and data_fim < data_inicio:
        _raise_http(
            status.HTTP_400_BAD_REQUEST,
            code="DATE_RANGE_INVALID",
            message="data_fim deve ser maior/igual a data_inicio",
        )

    if data_inicio or data_fim:
        inicio = func.coalesce(Evento.data_inicio_prevista, Evento.data_inicio_realizada)
        fim = func.coalesce(Evento.data_fim_prevista, Evento.data_fim_realizada, inicio)
        query = query.where(inicio.is_not(None))
        count_query = count_query.where(inicio.is_not(None))

        if data_inicio:
            query = query.where(fim >= data_inicio)
            count_query = count_query.where(fim >= data_inicio)
        if data_fim:
            query = query.where(inicio <= data_fim)
            count_query = count_query.where(inicio <= data_fim)
    elif data:
        inicio = func.coalesce(Evento.data_inicio_prevista, Evento.data_inicio_realizada)
        fim = func.coalesce(Evento.data_fim_prevista, Evento.data_fim_realizada, inicio)
        query = query.where(inicio.is_not(None)).where(inicio <= data).where(fim >= data)
        count_query = count_query.where(inicio.is_not(None)).where(inicio <= data).where(fim >= data)

    total = session.exec(count_query).one()
    items = session.exec(query.order_by(Evento.id.desc()).offset(skip).limit(limit)).all()
    response.headers["X-Total-Count"] = str(total)
    return items


def _format_csv_date(value: date | None) -> str:
    if not value:
        return ""
    return value.strftime("%Y-%m-%d")


def _csv_filename() -> str:
    return "eventos.csv"


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
    """Exporta a listagem de eventos em CSV (com filtros opcionais).

    - respeita as mesmas regras de visibilidade de `/evento`
    - inclui BOM UTF-8 (Excel-friendly)
    """
    query = select(Evento)
    query = _apply_visibility(query, current_user)

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
        _raise_http(
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
        territorios = (
            ", ".join(territorios_by_evento.get(eid or -1, [])) if eid is not None else ""
        )
        writer.writerow(
            [
                eid or "",
                e.nome,
                e.descricao,
                e.agencia_id,
                agencia_nome_by_id.get(e.agencia_id, ""),
                e.diretoria_id or "",
                diretoria_nome_by_id.get(e.diretoria_id or -1, "") if e.diretoria_id else "",
                e.divisao_demandante_id or "",
                divisao_nome_by_id.get(e.divisao_demandante_id or -1, "")
                if e.divisao_demandante_id
                else "",
                e.tipo_id,
                tipo_nome_by_id.get(e.tipo_id, ""),
                e.subtipo_id or "",
                subtipo_nome_by_id.get(e.subtipo_id or -1, "") if e.subtipo_id else "",
                e.status_id,
                status_nome_by_id.get(e.status_id, ""),
                e.estado,
                e.cidade,
                _format_csv_date(e.data_inicio_prevista),
                _format_csv_date(e.data_fim_prevista),
                _format_csv_date(e.data_inicio_realizada),
                _format_csv_date(e.data_fim_realizada),
                str(e.investimento) if e.investimento is not None else "",
                territorios,
                tags,
                e.qr_code_url or "",
                e.created_at.isoformat() if e.created_at else "",
                e.updated_at.isoformat() if e.updated_at else "",
            ]
        )

    content = "\ufeff" + buffer.getvalue()
    headers = {"Content-Disposition": f'attachment; filename="{_csv_filename()}"'}
    return Response(content=content, media_type="text/csv; charset=utf-8", headers=headers)


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


STATUS_PREVISTO = "Previsto"
STATUS_A_CONFIRMAR = "A Confirmar"
STATUS_CONFIRMADO = "Confirmado"
STATUS_REALIZADO = "Realizado"
STATUS_CANCELADO = "Cancelado"


def _infer_status_nome(data_inicio_prevista: date | None, data_fim_prevista: date | None) -> str:
    """Infere o nome do status quando o cliente nao envia `status_id`.

    Regra exigida:
    - se `data_inicio_prevista` > hoje -> Previsto

    Complemento:
    - se `data_fim_prevista` < hoje -> Realizado
    - caso contrario -> Confirmado
    - se nao houver datas -> A Confirmar
    """
    today = date.today()
    if data_inicio_prevista and data_inicio_prevista > today:
        return STATUS_PREVISTO
    if data_fim_prevista and data_fim_prevista < today:
        return STATUS_REALIZADO
    if data_inicio_prevista and data_inicio_prevista <= today:
        return STATUS_CONFIRMADO
    return STATUS_A_CONFIRMAR


def _get_status_id_by_nome(session: Session, nome: str) -> int:
    row = session.exec(select(StatusEvento).where(func.lower(StatusEvento.nome) == nome.lower())).first()
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
    _validate_fk(
        session,
        DivisaoDemandante,
        payload.divisao_demandante_id,
        "DIVISAO_DEMANDANTE_NOT_FOUND",
        "Divisao demandante nao encontrada",
    )
    _validate_fk(session, Funcionario, payload.gestor_id, "GESTOR_NOT_FOUND", "Gestor nao encontrado")

    tag_ids = _normalize_unique_ids(
        payload.tag_ids, code="TAG_ID_INVALID", message="tag_ids invalidos"
    )
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

    evento = Evento(
        thumbnail=_normalize_str(payload.thumbnail),
        divisao_demandante_id=payload.divisao_demandante_id,
        qr_code_url=_normalize_str(payload.qr_code_url),
        nome=_normalize_str(payload.nome) or "",
        descricao=_normalize_str(payload.descricao) or "",
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
        _raise_http(status.HTTP_500_INTERNAL_SERVER_ERROR, code="EVENTO_CREATE_FAILED", message="Falha ao criar evento")

    for territorio_id in territorio_ids:
        session.add(EventoTerritorio(evento_id=evento.id, territorio_id=territorio_id))
    for tag_id in tag_ids:
        session.add(EventoTag(evento_id=evento.id, tag_id=tag_id))

    session.commit()
    session.refresh(evento)
    read = EventoRead.model_validate(evento, from_attributes=True)
    return read.model_copy(update={"tag_ids": tag_ids, "territorio_ids": territorio_ids})


@router.post("/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def criar_tag(
    payload: TagCreate,
    response: Response,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    nome = _normalize_str(payload.nome)
    if not nome:
        _raise_http(status.HTTP_400_BAD_REQUEST, code="TAG_NAME_REQUIRED", message="nome obrigatorio")

    existing = session.exec(select(Tag).where(func.lower(Tag.nome) == nome.lower())).first()
    if existing:
        response.status_code = status.HTTP_200_OK
        return existing

    tag = Tag(nome=nome)
    session.add(tag)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        existing = session.exec(select(Tag).where(func.lower(Tag.nome) == nome.lower())).first()
        if existing:
            response.status_code = status.HTTP_200_OK
            return existing
        raise

    session.refresh(tag)
    return tag


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
    if "qr_code_url" in data:
        data["qr_code_url"] = _normalize_str(data["qr_code_url"])

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

    read = EventoRead.model_validate(evento, from_attributes=True)
    return read.model_copy(update={"tag_ids": list(tag_ids_final), "territorio_ids": list(territorio_ids_final)})


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
    estado: str | None = Query(None, min_length=1, max_length=10),
):
    query = select(Evento.cidade).where(Evento.cidade.is_not(None)).distinct()
    query = _apply_visibility(query, current_user)
    if estado:
        uf = estado.strip().lower()
        query = query.where(func.lower(Evento.estado) == uf)
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


@router.get("/all/status-evento", response_model=list[StatusEventoRead])
def listar_status_evento(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    query = select(StatusEvento)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(StatusEvento.nome.ilike(like))
    desired = [
        STATUS_PREVISTO,
        STATUS_A_CONFIRMAR,
        STATUS_CONFIRMADO,
        STATUS_REALIZADO,
        STATUS_CANCELADO,
    ]
    order_case = case(
        *[(func.lower(StatusEvento.nome) == nome.lower(), idx) for idx, nome in enumerate(desired, start=1)],
        else_=99,
    )
    return session.exec(query.order_by(order_case, StatusEvento.nome)).all()


@router.get("/all/divisoes-demandantes", response_model=list[DivisaoDemandanteRead])
def listar_divisoes_demandantes(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    query = select(DivisaoDemandante)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(DivisaoDemandante.nome.ilike(like))
    return session.exec(query.order_by(DivisaoDemandante.nome)).all()


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


@router.get("/all/formulario-templates", response_model=list[FormularioLandingTemplateRead])
def listar_formulario_templates(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    """Lista temas/templates disponíveis para a landing de leads.

    Retorna apenas `id` e `nome`, ordenado por `nome`.
    """
    query = select(FormularioLandingTemplate)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(FormularioLandingTemplate.nome.ilike(like))
    return session.exec(query.order_by(FormularioLandingTemplate.nome)).all()


@router.get("/all/formulario-campos", response_model=list[str])
def listar_formulario_campos(
    current_user: Usuario = Depends(get_current_user),
):
    """Lista o catálogo de campos possíveis para o Formulário de Lead (MVP)."""
    return FORMULARIO_CAMPOS_CATALOGO


@router.get("/{evento_id}/form-config", response_model=FormularioLeadConfigRead)
@router.get("/{evento_id}/form-config/", response_model=FormularioLeadConfigRead)
def obter_formulario_lead_config(
    evento_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    """Retorna a configuração do Formulário de Lead para um evento.

    MVP: se não existir config persistida, retorna um "config default" (sem persistir).
    """
    evento = session.get(Evento, evento_id)
    if not evento:
        _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        if evento.agencia_id != current_user.agencia_id:
            _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    computed_urls = build_evento_public_urls(evento_id, backend_base_url=str(request.base_url))

    config = session.exec(select(FormularioLeadConfig).where(FormularioLeadConfig.evento_id == evento_id)).first()
    if not config:
        default_campos = [
            FormularioLeadCampoRead(
                nome_campo=nome,
                obrigatorio=obrigatorio,
                ordem=FORMULARIO_CAMPOS_ORDEM_BY_LOWER.get(nome.lower(), 0),
            )
            for nome, obrigatorio in FORMULARIO_CAMPOS_DEFAULT
        ]
        return FormularioLeadConfigRead(
            evento_id=evento_id, template_id=None, campos=default_campos, **computed_urls
        )

    campos = session.exec(
        select(FormularioLeadCampo)
        .where(FormularioLeadCampo.config_id == config.id)
        .order_by(FormularioLeadCampo.ordem, FormularioLeadCampo.id)
    ).all()

    read = FormularioLeadConfigRead.model_validate(config, from_attributes=True)
    url_updates = {key: value for key, value in computed_urls.items() if getattr(read, key) is None}
    return read.model_copy(
        update={
            "campos": [FormularioLeadCampoRead.model_validate(c, from_attributes=True) for c in campos],
            **url_updates,
        }
    )


@router.put("/{evento_id}/form-config", response_model=FormularioLeadConfigRead)
@router.put("/{evento_id}/form-config/", response_model=FormularioLeadConfigRead)
def upsert_formulario_lead_config(
    evento_id: int,
    payload: FormularioLeadConfigUpsert,
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    """Cria/atualiza config do Formulário de Lead (MVP: template + campos)."""
    evento = session.get(Evento, evento_id)
    if not evento:
        _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        if evento.agencia_id != current_user.agencia_id:
            _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    update_template = "template_id" in payload.model_fields_set
    if update_template and payload.template_id is not None:
        _validate_fk(
            session,
            FormularioLandingTemplate,
            payload.template_id,
            "FORM_TEMPLATE_NOT_FOUND",
            "Template nao encontrado",
        )

    config = session.exec(select(FormularioLeadConfig).where(FormularioLeadConfig.evento_id == evento_id)).first()
    if not config:
        config = FormularioLeadConfig(
            evento_id=evento_id,
            nome="Formulario de Lead",
        )
    if update_template:
        config.template_id = payload.template_id
    config.atualizado_em = now_utc()
    session.add(config)

    replace_campos = "campos" in payload.model_fields_set

    # MVP: estrategia "replace all" para lista de campos (em transacao).
    try:
        session.flush()  # garante config.id para FK sem commitar

        if replace_campos:
            session.exec(sa_delete(FormularioLeadCampo).where(FormularioLeadCampo.config_id == config.id))
            for campo in payload.campos:
                session.add(
                    FormularioLeadCampo(
                        config_id=config.id,
                        nome_campo=campo.nome_campo.strip(),
                        obrigatorio=campo.obrigatorio,
                        ordem=campo.ordem,
                    )
                )

        session.commit()
    except Exception:
        session.rollback()
        raise

    session.refresh(config)

    campos = session.exec(
        select(FormularioLeadCampo)
        .where(FormularioLeadCampo.config_id == config.id)
        .order_by(FormularioLeadCampo.ordem, FormularioLeadCampo.id)
    ).all()

    computed_urls = build_evento_public_urls(evento_id, backend_base_url=str(request.base_url))
    read = FormularioLeadConfigRead.model_validate(config, from_attributes=True)
    url_updates = {key: value for key, value in computed_urls.items() if getattr(read, key) is None}
    return read.model_copy(
        update={
            "campos": [FormularioLeadCampoRead.model_validate(c, from_attributes=True) for c in campos],
            **url_updates,
        }
    )


@router.get("/{evento_id}/questionario", response_model=QuestionarioEstruturaRead)
@router.get("/{evento_id}/questionario/", response_model=QuestionarioEstruturaRead)
def obter_questionario(
    evento_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    evento = session.get(Evento, evento_id)
    if not evento:
        _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        if evento.agencia_id != current_user.agencia_id:
            _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    paginas = load_questionario_estrutura(session, evento_id=evento_id)
    paginas_read = [QuestionarioPaginaRead.model_validate(p, from_attributes=True) for p in paginas]
    return QuestionarioEstruturaRead(evento_id=evento_id, paginas=paginas_read)


@router.put("/{evento_id}/questionario", response_model=QuestionarioEstruturaRead)
@router.put("/{evento_id}/questionario/", response_model=QuestionarioEstruturaRead)
def salvar_questionario(
    evento_id: int,
    payload: QuestionarioEstruturaWrite,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    evento = session.get(Evento, evento_id)
    if not evento:
        _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        if evento.agencia_id != current_user.agencia_id:
            _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    respostas = session.exec(
        select(func.count())
        .select_from(QuestionarioResposta)
        .where(QuestionarioResposta.evento_id == evento_id)
    ).one()
    if int(respostas) > 0:
        _raise_http(
            status.HTTP_409_CONFLICT,
            code="QUESTIONARIO_UPDATE_BLOCKED",
            message="Nao e possivel atualizar questionario com respostas",
            extra={"extra": {"dependencies": {"respostas_questionario": int(respostas)}}},
        )

    paginas = replace_questionario_estrutura(session, evento_id=evento_id, payload=payload)
    paginas_read = [QuestionarioPaginaRead.model_validate(p, from_attributes=True) for p in paginas]
    return QuestionarioEstruturaRead(evento_id=evento_id, paginas=paginas_read)


@router.get("/{evento_id}/gamificacoes", response_model=list[GamificacaoRead])
@router.get("/{evento_id}/gamificacoes/", response_model=list[GamificacaoRead])
def listar_gamificacoes(
    evento_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    evento = session.get(Evento, evento_id)
    if not evento:
        _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        if evento.agencia_id != current_user.agencia_id:
            _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    gamificacoes = session.exec(
        select(Gamificacao).where(Gamificacao.evento_id == evento_id).order_by(Gamificacao.id)
    ).all()
    return [GamificacaoRead.model_validate(g, from_attributes=True) for g in gamificacoes]


@router.post(
    "/{evento_id}/gamificacoes",
    response_model=GamificacaoRead,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/{evento_id}/gamificacoes/",
    response_model=GamificacaoRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_gamificacao(
    evento_id: int,
    payload: GamificacaoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    evento = session.get(Evento, evento_id)
    if not evento:
        _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        if evento.agencia_id != current_user.agencia_id:
            _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    gamificacao = Gamificacao(
        evento_id=evento_id,
        nome=payload.nome,
        descricao=payload.descricao,
        premio=payload.premio,
        titulo_feedback=payload.titulo_feedback,
        texto_feedback=payload.texto_feedback,
    )
    session.add(gamificacao)
    session.commit()

    session.refresh(gamificacao)
    return GamificacaoRead.model_validate(gamificacao, from_attributes=True)


@router.get("/{evento_id}/ativacoes", response_model=list[AtivacaoRead])
@router.get("/{evento_id}/ativacoes/", response_model=list[AtivacaoRead])
def listar_ativacoes(
    evento_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    evento = session.get(Evento, evento_id)
    if not evento:
        _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        if evento.agencia_id != current_user.agencia_id:
            _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    ativacoes = session.exec(select(Ativacao).where(Ativacao.evento_id == evento_id).order_by(Ativacao.id)).all()
    return [AtivacaoRead.model_validate(a, from_attributes=True) for a in ativacoes]


@router.post(
    "/{evento_id}/ativacoes",
    response_model=AtivacaoRead,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/{evento_id}/ativacoes/",
    response_model=AtivacaoRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_ativacao(
    evento_id: int,
    payload: AtivacaoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    evento = session.get(Evento, evento_id)
    if not evento:
        _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        if evento.agencia_id != current_user.agencia_id:
            _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    if payload.gamificacao_id is not None:
        gamificacao = session.get(Gamificacao, payload.gamificacao_id)
        if not gamificacao or gamificacao.evento_id != evento_id:
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="GAMIFICACAO_OUT_OF_SCOPE",
                message="Gamificacao invalida para este evento",
                extra={"field": "gamificacao_id"},
            )

    ativacao = Ativacao(
        evento_id=evento_id,
        nome=payload.nome,
        descricao=payload.descricao,
        mensagem_qrcode=payload.mensagem_qrcode,
        gamificacao_id=payload.gamificacao_id,
        redireciona_pesquisa=payload.redireciona_pesquisa,
        checkin_unico=payload.checkin_unico,
        termo_uso=payload.termo_uso,
        gera_cupom=payload.gera_cupom,
        valor=Decimal("0.00"),
    )
    session.add(ativacao)
    session.commit()

    session.refresh(ativacao)
    return AtivacaoRead.model_validate(ativacao, from_attributes=True)


@router.get("/{evento_id}", response_model=EventoRead)
@router.get("/{evento_id}/", response_model=EventoRead)
def obter_evento(
    evento_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    evento = session.get(Evento, evento_id)
    if not evento:
        _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        if evento.agencia_id != current_user.agencia_id:
            _raise_http(status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado")

    tag_ids = session.exec(
        select(EventoTag.tag_id).where(EventoTag.evento_id == evento_id).order_by(EventoTag.tag_id)
    ).all()
    territorio_ids = session.exec(
        select(EventoTerritorio.territorio_id)
        .where(EventoTerritorio.evento_id == evento_id)
        .order_by(EventoTerritorio.territorio_id)
    ).all()

    read = EventoRead.model_validate(evento, from_attributes=True)
    return read.model_copy(update={"tag_ids": list(tag_ids), "territorio_ids": list(territorio_ids)})
