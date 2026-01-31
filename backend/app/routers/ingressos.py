"""Rotas de solicitacao de ingressos."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from sqlalchemy import func

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import (
    CotaCortesia,
    Diretoria,
    Evento,
    Funcionario,
    SolicitacaoIngresso,
    SolicitacaoIngressoStatus,
    SolicitacaoIngressoTipo,
    Usuario,
)
from app.schemas.ingressos import (
    IngressoAtivoListItem,
    SolicitacaoIngressoCreate,
    SolicitacaoIngressoRead,
)
from app.utils.http_errors import raise_http_error

router = APIRouter(prefix="/ingressos", tags=["ingressos"])


def _normalize_email(value: str) -> str:
    return value.strip().lower()


def _is_valid_email(value: str) -> bool:
    return "@" in value and "." in value and " " not in value


def _get_user_diretoria_id(session: Session, user: Usuario) -> int | None:
    if user.funcionario_id:
        funcionario = session.get(Funcionario, user.funcionario_id)
        if funcionario and funcionario.diretoria_id:
            return int(funcionario.diretoria_id)
    return None


def _count_solicitacoes_ativas(session: Session, cota_id: int) -> int:
    return int(
        session.exec(
            select(func.count(SolicitacaoIngresso.id)).where(
                SolicitacaoIngresso.cota_id == cota_id,
                SolicitacaoIngresso.status == SolicitacaoIngressoStatus.SOLICITADO,
            )
        ).one()
    )


@router.get("/ativos", response_model=list[IngressoAtivoListItem])
def listar_ativos_para_ingressos(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    solicitante_email = _normalize_email(current_user.email or "")
    if not solicitante_email.endswith("@bb.com.br"):
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_EMAIL",
            message="Email deve ser @bb.com.br",
        )

    diretoria_id = _get_user_diretoria_id(session, current_user)
    if not diretoria_id:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="MISSING_DIRETORIA",
            message="Usuario sem diretoria definida",
        )

    rows = session.exec(
        select(CotaCortesia, Evento, Diretoria)
        .join(Evento, CotaCortesia.evento_id == Evento.id)
        .join(Diretoria, CotaCortesia.diretoria_id == Diretoria.id)
        .where(CotaCortesia.diretoria_id == diretoria_id)
        .order_by(
            func.coalesce(Evento.data_inicio_prevista, Evento.data_inicio_realizada),
            Evento.id,
            CotaCortesia.id,
        )
    ).all()

    if not rows:
        return []

    cota_ids = [int(cota.id) for cota, _, _ in rows if cota.id is not None]
    usados_por_cota: dict[int, int] = {}
    if cota_ids:
        usados_rows = session.exec(
            select(SolicitacaoIngresso.cota_id, func.count())
            .where(SolicitacaoIngresso.cota_id.in_(cota_ids))
            .where(SolicitacaoIngresso.status == SolicitacaoIngressoStatus.SOLICITADO)
            .group_by(SolicitacaoIngresso.cota_id)
        ).all()
        usados_por_cota = {
            int(cota_id): int(count)
            for cota_id, count in usados_rows
            if cota_id is not None and count is not None
        }

    items: list[IngressoAtivoListItem] = []
    for cota, evento, diretoria in rows:
        cota_id = int(cota.id) if cota.id is not None else 0
        total = int(cota.quantidade)
        usados = usados_por_cota.get(cota_id, 0)
        disponiveis = max(total - usados, 0)

        data_inicio = evento.data_inicio_prevista or evento.data_inicio_realizada
        data_fim = evento.data_fim_prevista or evento.data_fim_realizada or data_inicio

        items.append(
            IngressoAtivoListItem(
                cota_id=cota_id,
                evento_id=int(evento.id),
                evento_nome=str(evento.nome),
                diretoria_id=int(cota.diretoria_id),
                diretoria_nome=str(diretoria.nome),
                total=total,
                usados=usados,
                disponiveis=disponiveis,
                data_inicio=data_inicio,
                data_fim=data_fim,
            )
        )

    return items


@router.post("/solicitacoes", response_model=SolicitacaoIngressoRead, status_code=status.HTTP_201_CREATED)
def criar_solicitacao(
    payload: SolicitacaoIngressoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    solicitante_email = _normalize_email(current_user.email or "")
    if not solicitante_email.endswith("@bb.com.br"):
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_EMAIL",
            message="Email deve ser @bb.com.br",
        )

    diretoria_id = _get_user_diretoria_id(session, current_user)
    if not diretoria_id:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="MISSING_DIRETORIA",
            message="Usuario sem diretoria definida",
        )

    cota = session.get(CotaCortesia, payload.cota_id)
    if not cota:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="COTA_NOT_FOUND",
            message="Cota nao encontrada",
        )

    if int(cota.diretoria_id) != int(diretoria_id):
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="COTA_NOT_FOUND",
            message="Cota nao encontrada",
        )

    indicado_email = None
    if payload.tipo == SolicitacaoIngressoTipo.SELF:
        indicado_email = solicitante_email
    else:
        raw_indicado = payload.indicado_email or ""
        if not raw_indicado:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="INVALID_EMAIL",
                message="Email do indicado e obrigatorio",
            )
        indicado_email = _normalize_email(raw_indicado)
        if not _is_valid_email(indicado_email):
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="INVALID_EMAIL",
                message="Email do indicado invalido",
            )

    existente = session.exec(
        select(SolicitacaoIngresso.id).where(
            SolicitacaoIngresso.cota_id == payload.cota_id,
            SolicitacaoIngresso.indicado_email == indicado_email,
        )
    ).first()
    if existente:
        raise_http_error(
            status.HTTP_409_CONFLICT,
            code="DUPLICATE_REQUEST",
            message="Solicitacao duplicada para este indicado",
        )

    usados = _count_solicitacoes_ativas(session, int(cota.id))
    disponiveis = int(cota.quantidade) - usados
    if disponiveis <= 0:
        raise_http_error(
            status.HTTP_409_CONFLICT,
            code="COTA_EMPTY",
            message="Nao ha ingressos disponiveis",
        )

    evento = session.get(Evento, cota.evento_id)
    if not evento:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="EVENTO_NOT_FOUND",
            message="Evento nao encontrado",
        )

    solicitacao = SolicitacaoIngresso(
        cota_id=int(cota.id),
        evento_id=int(evento.id),
        diretoria_id=int(cota.diretoria_id),
        solicitante_usuario_id=int(current_user.id),
        solicitante_email=solicitante_email,
        tipo=payload.tipo,
        indicado_email=indicado_email,
        status=SolicitacaoIngressoStatus.SOLICITADO,
    )
    session.add(solicitacao)
    session.commit()
    session.refresh(solicitacao)

    return SolicitacaoIngressoRead.model_validate(solicitacao)
