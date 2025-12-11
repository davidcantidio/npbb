"""Rotas de autenticação (login)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.models import Usuario
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.usuario import UsuarioRead
from app.utils.jwt import create_access_token
from app.utils.security import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _authenticate(session: Session, email: str, password: str) -> Usuario | None:
    usuario = session.exec(select(Usuario).where(Usuario.email == email)).first()
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
    """Autentica usuário e retorna token de acesso."""
    usuario = _authenticate(session, credentials.email, credentials.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": usuario.id})
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UsuarioRead.model_validate(usuario, from_attributes=True),
    )
