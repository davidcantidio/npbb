"""Dependência de autenticação para obter o usuário atual."""

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session
import jwt

from app.db.database import get_session
from app.models.models import Usuario
from app.utils.jwt import decode_token

SESSION_COOKIE_NAME = "npbb_access_token"
http_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    token: str | None = None,
    bearer: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    cookie_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    session: Session = Depends(get_session),
) -> Usuario:
    """Valida bearer/cookie token, busca o usuário ativo e o retorna."""
    auth_headers = {"WWW-Authenticate": "Bearer"}
    token_value = token or (bearer.credentials if bearer else cookie_token)
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

    usuario = session.get(Usuario, user_id)
    if not usuario or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo ou inexistente",
            headers=auth_headers,
        )
    return usuario
