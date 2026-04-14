"""Rotas de agências (consulta para cadastro e filtros)."""

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import func
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, select

from app.db.database import _agent_debug_ndjson, get_session
from app.models.models import Agencia
from app.schemas.agencia import AgenciaRead

router = APIRouter(prefix="/agencias", tags=["agencias"])


@router.get("/", response_model=list[AgenciaRead])
def listar_agencias(
    response: Response,
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    """Lista agências com paginação e busca opcional.

    - Retorna apenas `id`, `nome` e `dominio`.
    - Header `X-Total-Count` contém o total (com filtro aplicado, se houver).
    """
    query = select(Agencia)
    count_query = select(func.count()).select_from(Agencia)

    if search:
        like = f"%{search.strip()}%"
        query = query.where((Agencia.nome.ilike(like)) | (Agencia.dominio.ilike(like)))
        count_query = count_query.where((Agencia.nome.ilike(like)) | (Agencia.dominio.ilike(like)))

    # #region agent log
    try:
        total = session.exec(count_query).one()
        items = session.exec(query.order_by(Agencia.nome).offset(skip).limit(limit)).all()
    except OperationalError as e:
        msg = str(e.orig) if getattr(e, "orig", None) else str(e)
        _agent_debug_ndjson(
            "agencias.py:listar_agencias",
            "OperationalError_list",
            {
                "msg_prefix": msg[:240],
                "has_timeout": "timed out" in msg.lower() or "10060" in msg,
                "has_server_closed": "server closed the connection" in msg.lower(),
            },
            "H3",
        )
        raise
    # #endregion
    response.headers["X-Total-Count"] = str(total)
    return items
