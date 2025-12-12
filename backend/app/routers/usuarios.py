"""Rotas de usuarios: criacao com validacao e hashing de senha."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.db.database import get_session
from app.models.models import Agencia, Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioTipo
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
    """Cria um novo usuario e retorna o registro sem expor a senha.

    - Faz hash da senha.
    - Persiste na base via Session.
    - Converte violacoes de chave unica (email) em HTTP 409.
    - Para usuario do tipo "agencia", valida se o dominio do email bate com a agencia.
    """
    if usuario_in.tipo_usuario == UsuarioTipo.AGENCIA:
        agencia = session.get(Agencia, usuario_in.agencia_id)
        if not agencia:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agencia nao encontrada",
            )

        email_domain = str(usuario_in.email).split("@")[-1].lower()
        agencia_domain = str(agencia.dominio).lower().lstrip("@")
        if email_domain != agencia_domain and not email_domain.endswith(f".{agencia_domain}"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email deve ser do dominio @{agencia_domain}",
            )

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
        if "duplicate key value" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email ja cadastrado",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar usuario",
        )

    return usuario
