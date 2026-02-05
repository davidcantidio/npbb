"""Rotas de autenticacao (login)."""

from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.auth import get_current_user
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
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UsuarioRead.model_validate(usuario, from_attributes=True),
    )


@router.get("/me", response_model=UsuarioRead)
def me(current_user: Usuario = Depends(get_current_user)):
    """Retorna dados publicos do usuario autenticado."""
    return UsuarioRead.model_validate(current_user, from_attributes=True)
