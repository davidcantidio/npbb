"""Rotas de usuarios: criacao com validacao e hashing de senha."""

import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.models import Agencia, Funcionario, Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioTipo
from app.utils.security import hash_password

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

PASSWORD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{6,}$")
MATRICULA_RE = re.compile(r"^[A-Za-z][0-9]{1,16}$")


def _raise_http(status_code: int, code: str, message: str, field: str | None = None) -> None:
    detail: dict[str, str] = {"code": code, "message": message}
    if field:
        detail["field"] = field
    raise HTTPException(status_code=status_code, detail=detail)


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

    Payload (cadastro):
    - email
    - password (sera hasheada no servidor)
    - tipo_usuario: bb | npbb | agencia
    - matricula (BB) / agencia_id (AGENCIA)

    Regras:
    - Dominios de email:
      - bb: @bb.com.br
      - npbb: @npbb.com.br
      - agencia: deve bater com Agencia.dominio
    - Senha: minimo 6 chars, com letra e numero.
    - Duplicados: retorna 409.
    """
    email = str(usuario_in.email).strip().lower()

    if not PASSWORD_RE.match(usuario_in.password or ""):
        _raise_http(
            status.HTTP_400_BAD_REQUEST,
            code="PASSWORD_POLICY",
            message="Minimo 6 caracteres, com pelo menos 1 letra e 1 numero",
            field="password",
        )

    funcionario_id: int | None = None
    agencia_id: int | None = None

    if usuario_in.tipo_usuario == UsuarioTipo.BB:
        if not email.endswith("@bb.com.br"):
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="EMAIL_DOMAIN_INVALID",
                message="Para BB, use email @bb.com.br",
                field="email",
            )
        matricula = (usuario_in.matricula or "").strip()
        if not MATRICULA_RE.match(matricula):
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="MATRICULA_INVALID",
                message="Matricula invalida (ex.: A123)",
                field="matricula",
            )
        funcionario = session.exec(select(Funcionario).where(Funcionario.chave_c == matricula)).first()
        if not funcionario:
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="MATRICULA_NOT_FOUND",
                message="Matricula nao encontrada",
                field="matricula",
            )
        funcionario_id = funcionario.id

    elif usuario_in.tipo_usuario == UsuarioTipo.NPBB:
        if not email.endswith("@npbb.com.br"):
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="EMAIL_DOMAIN_INVALID",
                message="Para NPBB, use email @npbb.com.br",
                field="email",
            )
        if usuario_in.matricula:
            matricula = usuario_in.matricula.strip()
            if not MATRICULA_RE.match(matricula):
                _raise_http(
                    status.HTTP_400_BAD_REQUEST,
                    code="MATRICULA_INVALID",
                    message="Matricula invalida (ex.: A123)",
                    field="matricula",
                )
            funcionario = session.exec(select(Funcionario).where(Funcionario.chave_c == matricula)).first()
            if not funcionario:
                _raise_http(
                    status.HTTP_400_BAD_REQUEST,
                    code="MATRICULA_NOT_FOUND",
                    message="Matricula nao encontrada",
                    field="matricula",
                )
            funcionario_id = funcionario.id
        else:
            funcionario = session.exec(select(Funcionario).where(Funcionario.email == email)).first()
            if funcionario:
                funcionario_id = funcionario.id

    else:  # AGENCIA
        agencia = session.get(Agencia, usuario_in.agencia_id)
        if not agencia:
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="AGENCIA_NOT_FOUND",
                message="Agencia nao encontrada",
                field="agencia_id",
            )

        email_domain = email.split("@")[-1]
        agencia_domain = str(agencia.dominio).lower().lstrip("@")
        if email_domain != agencia_domain and not email_domain.endswith(f".{agencia_domain}"):
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="EMAIL_DOMAIN_MISMATCH",
                message=f"Email deve ser do dominio @{agencia_domain}",
                field="email",
            )
        agencia_id = agencia.id

    usuario = Usuario(
        email=email,
        password_hash=hash_password(usuario_in.password),
        tipo_usuario=usuario_in.tipo_usuario.value,
        funcionario_id=funcionario_id,
        agencia_id=agencia_id,
    )

    try:
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
    except IntegrityError as e:
        session.rollback()
        if "duplicate key value" in str(e.orig):
            _raise_http(
                status.HTTP_409_CONFLICT,
                code="EMAIL_ALREADY_REGISTERED",
                message="Email ja cadastrado",
                field="email",
            )
        _raise_http(
            status.HTTP_400_BAD_REQUEST,
            code="USER_CREATE_FAILED",
            message="Erro ao criar usuario",
        )

    return usuario
