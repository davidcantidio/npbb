from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.database import get_session
from app.schemas.usuario import UsuarioCreate
from app.models.models import Usuario

router = APIRouter(prefix="/usuarios")

@router.post("/")
def criar_usuario(usuario_in: UsuarioCreate, session: Session = Depends(get_session)):
    # Pydantic já validou vínculo
    usuario = Usuario(
        email=usuario_in.email,
        password_hash=hash_password(usuario_in.password),
        tipo_usuario=usuario_in.tipo_usuario,
        funcionario_id=usuario_in.funcionario_id,
        agencia_id=usuario_in.agencia_id,
    )

    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario
