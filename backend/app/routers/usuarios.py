"""Rotas de usuários: criação com validação e hashing de senha."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from app.db.database import get_session
from app.schemas.usuario import UsuarioCreate, UsuarioRead
from app.models.models import Usuario
from app.utils.security import hash_password

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post(
    "/",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_usuario(
    usuario_in: UsuarioCreate,
    session: Session = Depends(get_session),
):
    """Cria um novo usuário e retorna o registro sem expor a senha.

    - Faz hash da senha.
    - Persiste na base via Session.
    - Converte violações de chave única (e-mail) em HTTP 409.
    """
    usuario = Usuario(
        email=usuario_in.email,
        password_hash=hash_password(usuario_in.password),
        tipo_usuario=usuario_in.tipo_usuario,
        funcionario_id=usuario_in.funcionario_id,
        agencia_id=usuario_in.agencia_id,
    )

    try:
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
    except IntegrityError as e:
        session.rollback()
        # detectar email duplicado
        if "duplicate key value" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email já cadastrado",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar usuário",
        )

    return usuario
