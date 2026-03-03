"""Rotas de autenticacao (login/sessao)."""

import os
from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

from app.core.auth import SESSION_COOKIE_NAME, get_current_user
from app.db.database import get_session
from app.models.models import Usuario
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.usuario import UsuarioRead
from app.utils.jwt import create_access_token
from app.utils.security import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

STATUS_APROVADO = (
    "APROVADO"  # TODO: centralizar status_aprovacao quando houver enum/constante global.
)

SESSION_COOKIE_MAX_AGE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")) * 60


def _cookie_secure() -> bool:
    env = os.getenv("COOKIE_SECURE")
    if env is not None:
        return env.lower() in {"1", "true", "yes"}
    return os.getenv("ENV", "").lower() in {"prod", "production"}


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=_cookie_secure(),
        samesite="lax",
        max_age=SESSION_COOKIE_MAX_AGE_SECONDS,
        path="/",
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")


def is_bb_user(usuario: Usuario) -> bool:
    """
    Retorna True se for usuario BB:
    - email termina com '@bb.com.br' (case-insensitive)
    - matricula valida (nao None / nao vazia / nao so espacos)
    """
    email = (usuario.email or "").strip().lower()
    if not email.endswith("@bb.com.br"):
        return False
    matricula = usuario.matricula
    if matricula is None:
        return False
    return bool(str(matricula).strip())


def _authenticate(session: Session, email: str, password: str) -> Usuario | None:
    email_norm = (email or "").strip().lower()
    usuario = session.exec(select(Usuario).where(func.lower(Usuario.email) == email_norm)).first()
    if not usuario or not usuario.ativo:
        return None
    if not verify_password(password, usuario.password_hash):
        return None
    return usuario


@router.post("/login", response_model=LoginResponse)
def login(
    credentials: LoginRequest,
    response: Response,
    session: Session = Depends(get_session),
):
    """Autentica usuario e retorna token de acesso."""
    usuario = _authenticate(session, credentials.email, credentials.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": usuario.id})
    _set_session_cookie(response, token)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UsuarioRead.model_validate(usuario, from_attributes=True),
    )


@router.get("/me", response_model=UsuarioRead)
def me(current_user: Usuario = Depends(get_current_user)):
    """Retorna dados publicos do usuario autenticado."""
    return UsuarioRead.model_validate(current_user, from_attributes=True)


@router.post("/refresh", response_model=LoginResponse)
def refresh_session(
    response: Response,
    current_user: Usuario = Depends(get_current_user),
):
    """Renova sessão ativa e emite novo cookie/token."""
    token = create_access_token({"sub": current_user.id})
    _set_session_cookie(response, token)
    response.headers["X-Auth-Mode"] = "dual-stack"
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UsuarioRead.model_validate(current_user, from_attributes=True),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> Response:
    """Limpa sessão de cookie do cliente."""
    _clear_session_cookie(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
