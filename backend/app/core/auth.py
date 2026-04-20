"""Dependência de autenticação para obter o usuário atual."""

import logging

import jwt
from fastapi import Cookie, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import OperationalError
from sqlmodel import Session

from app.db.database import get_session, set_db_request_context
from app.models.models import Usuario
from app.utils.jwt import decode_token

SESSION_COOKIE_NAME = "npbb_access_token"
http_bearer = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


def _database_unavailable_exception(exc: OperationalError) -> HTTPException:
    msg = str(exc.orig) if getattr(exc, "orig", None) else str(exc)
    raw = msg.lower()
    code = "DB_TIMEOUT" if "timeout" in raw or "timed out" in raw or "10060" in raw else "DB_UNAVAILABLE"
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": code,
            "message": "Banco de dados indisponivel durante a autenticacao.",
        },
    )


def _resolve_token_value(
    token: str | None,
    bearer: HTTPAuthorizationCredentials | None,
    cookie_token: str | None,
) -> str | None:
    direct_token = token if isinstance(token, str) else None
    session_cookie_token = cookie_token if isinstance(cookie_token, str) else None
    return direct_token or (bearer.credentials if bearer else session_cookie_token)


def get_current_user(
    token: str | None = Query(default=None, include_in_schema=False),
    bearer: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    cookie_token: str | None = Cookie(
        default=None,
        alias=SESSION_COOKIE_NAME,
        include_in_schema=False,
    ),
    session: Session = Depends(get_session),
) -> Usuario:
    """Valida bearer/cookie token, busca o usuário ativo e o retorna."""
    auth_headers = {"WWW-Authenticate": "Bearer"}
    token_value = _resolve_token_value(token, bearer, cookie_token)
    if not token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais ausentes",
            headers=auth_headers,
        )

    try:
        payload = decode_token(token_value)
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
                headers=auth_headers,
            )
        user_id = int(sub)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers=auth_headers,
        )
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers=auth_headers,
        )

    try:
        set_db_request_context(session, user_id=user_id)
        usuario = session.get(Usuario, user_id)
    except OperationalError as e:
        msg = str(e.orig) if getattr(e, "orig", None) else str(e)
        logger.warning(
            "auth.get_current_user: falha ao carregar usuario user_id=%s msg_prefix=%r",
            user_id,
            msg[:240],
        )
        raise _database_unavailable_exception(e) from e
    if not usuario or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo ou inexistente",
            headers=auth_headers,
        )
    set_db_request_context(
        session,
        user_id=user_id,
        user_type=str(getattr(getattr(usuario, "tipo_usuario", None), "value", getattr(usuario, "tipo_usuario", ""))),
        agencia_id=getattr(usuario, "agencia_id", None),
    )
    return usuario


def get_current_user_optional(
    token: str | None = Query(default=None, include_in_schema=False),
    bearer: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    cookie_token: str | None = Cookie(
        default=None,
        alias=SESSION_COOKIE_NAME,
        include_in_schema=False,
    ),
    session: Session = Depends(get_session),
) -> Usuario | None:
    """Tenta resolver o usuário atual via bearer/cookie sem retornar erro 401."""
    token_value = _resolve_token_value(token, bearer, cookie_token)
    if not token_value:
        return None

    try:
        payload = decode_token(token_value)
        sub = payload.get("sub")
        if sub is None:
            return None
        user_id = int(sub)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
        return None

    try:
        set_db_request_context(session, user_id=user_id)
        usuario = session.get(Usuario, user_id)
    except OperationalError as e:
        raise _database_unavailable_exception(e) from e
    if not usuario or not usuario.ativo:
        return None
    set_db_request_context(
        session,
        user_id=user_id,
        user_type=str(getattr(getattr(usuario, "tipo_usuario", None), "value", getattr(usuario, "tipo_usuario", ""))),
        agencia_id=getattr(usuario, "agencia_id", None),
    )
    return usuario
