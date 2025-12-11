"""Esquemas Pydantic para autenticação."""

from pydantic import BaseModel, EmailStr

from app.schemas.usuario import UsuarioRead


class LoginRequest(BaseModel):
    """Payload de login com credenciais."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Resposta de login com token e dados públicos do usuário."""

    access_token: str
    token_type: str
    user: UsuarioRead
