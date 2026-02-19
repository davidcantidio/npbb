"""Rotas de usuarios: criacao com validacao e hashing de senha."""

import hashlib
import logging
import re
import time

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import Agencia, Diretoria, Funcionario, Usuario
from app.schemas.dominios import DiretoriaRead
from app.schemas.password_reset import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.schemas.usuario import UsuarioCreate, UsuarioDiretoriaUpdate, UsuarioRead, UsuarioTipo
from app.services.password_reset import PasswordResetError, request_password_reset, reset_password
from app.utils.log_sanitize import sanitize_exception, sanitize_text
from app.utils.security import hash_password

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

PASSWORD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{6,}$")
MATRICULA_RE = re.compile(r"^[A-Za-z][0-9]{1,16}$")
FORGOT_PASSWORD_MESSAGE = (
    "Se o email estiver cadastrado, você receberá instruções para redefinir a senha."
)
PASSWORD_RESET_DELAY_SEC = 0.3
telemetry_logger = logging.getLogger("app.telemetry")


def _generate_chave_c(session: Session, seed: str) -> str:
    base_key = "".join(ch for ch in seed if ch.isalnum()).upper() or "BBUSER"
    base_key = base_key[:16]
    chave_c = base_key
    suffix = 1
    while session.exec(select(Funcionario).where(Funcionario.chave_c == chave_c)).first():
        suffix_str = str(suffix)
        chave_c = f"{base_key[: max(1, 16 - len(suffix_str))]}{suffix_str}"
        suffix += 1
    return chave_c


def _raise_http(status_code: int, code: str, message: str, field: str | None = None) -> None:
    detail: dict[str, str] = {"code": code, "message": message}
    if field:
        detail["field"] = field
    raise HTTPException(status_code=status_code, detail=detail)


def _hash_email(email: str | None) -> str:
    if not email:
        return ""
    normalized = email.strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


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
    - matricula + diretoria (BB) / agencia_id (AGENCIA)

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
    matricula_value: str | None = None

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
        if usuario_in.diretoria_id is None:
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="DIRETORIA_REQUIRED",
                message="Diretoria e obrigatoria para usuarios BB",
                field="diretoria_id",
            )
        matricula_value = matricula.lower()
        diretoria = session.get(Diretoria, usuario_in.diretoria_id)
        if not diretoria:
            _raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="DIRETORIA_NOT_FOUND",
                message="Diretoria nao encontrada",
                field="diretoria_id",
            )
        funcionario = session.exec(
            select(Funcionario).where(func.lower(Funcionario.chave_c) == matricula_value)
        ).first()
        if funcionario:
            if funcionario.diretoria_id and int(funcionario.diretoria_id) != int(diretoria.id):
                _raise_http(
                    status.HTTP_400_BAD_REQUEST,
                    code="DIRETORIA_MISMATCH",
                    message="Diretoria nao corresponde a matricula",
                    field="diretoria_id",
                )
            funcionario_id = funcionario.id
        else:
            email_local = email.split("@")[0]
            funcionario = Funcionario(
                nome=email_local or email,
                chave_c=matricula_value,
                diretoria_id=int(diretoria.id),
                email=email,
            )
            session.add(funcionario)
            session.commit()
            session.refresh(funcionario)
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
            matricula_value = matricula.lower()
            funcionario = session.exec(
                select(Funcionario).where(func.lower(Funcionario.chave_c) == matricula_value)
            ).first()
            if funcionario:
                funcionario_id = funcionario.id
        else:
            funcionario = session.exec(
                select(Funcionario).where(Funcionario.email == email)
            ).first()
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
        matricula=matricula_value,
        password_hash=hash_password(usuario_in.password),
        tipo_usuario=usuario_in.tipo_usuario.value,
        funcionario_id=funcionario_id,
        agencia_id=agencia_id,
        status_aprovacao="PENDENTE" if usuario_in.tipo_usuario == UsuarioTipo.BB else None,
    )

    try:
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
    except IntegrityError as e:
        session.rollback()
        constraint_name = None
        try:
            constraint_name = getattr(getattr(e.orig, "diag", None), "constraint_name", None)
        except Exception:
            constraint_name = None

        error_message = str(getattr(e, "orig", e))
        is_unique = (
            "duplicate key value" in error_message or "UNIQUE constraint failed" in error_message
        )
        if is_unique:
            if (
                constraint_name in {"usuario_email_key"}
                or "usuario_email_key" in error_message
                or "usuario.email" in error_message
            ):
                _raise_http(
                    status.HTTP_409_CONFLICT,
                    code="EMAIL_ALREADY_REGISTERED",
                    message="Email ja cadastrado",
                    field="email",
                )
            if (
                constraint_name in {"uq_usuario_matricula", "usuario_matricula_key"}
                or "uq_usuario_matricula" in error_message
                or "usuario_matricula_key" in error_message
                or "usuario.matricula" in error_message
            ):
                _raise_http(
                    status.HTTP_409_CONFLICT,
                    code="MATRICULA_ALREADY_REGISTERED",
                    message="Matricula ja cadastrada",
                    field="matricula",
                )
        _raise_http(
            status.HTTP_400_BAD_REQUEST,
            code="USER_CREATE_FAILED",
            message="Erro ao criar usuario",
        )
    except ProgrammingError as e:
        session.rollback()
        error_message = str(getattr(e, "orig", e))
        if 'column "matricula"' in error_message and "does not exist" in error_message:
            _raise_http(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                code="DB_SCHEMA_OUT_OF_DATE",
                message="Banco de dados desatualizado (coluna usuario.matricula). Rode: alembic upgrade head",
            )
        _raise_http(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="DB_ERROR",
            message="Erro no banco de dados",
        )

    return usuario


@router.post("/diretoria", response_model=UsuarioRead)
def atualizar_diretoria(
    payload: UsuarioDiretoriaUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    if current_user.tipo_usuario != UsuarioTipo.BB:
        _raise_http(
            status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
            message="Acesso restrito",
        )

    diretoria = session.get(Diretoria, payload.diretoria_id)
    if not diretoria:
        _raise_http(
            status.HTTP_400_BAD_REQUEST,
            code="DIRETORIA_NOT_FOUND",
            message="Diretoria nao encontrada",
            field="diretoria_id",
        )

    funcionario_id: int | None = None
    if current_user.funcionario_id:
        funcionario = session.get(Funcionario, current_user.funcionario_id)
        if funcionario:
            funcionario.diretoria_id = int(diretoria.id)
            session.add(funcionario)
            session.commit()
            funcionario_id = funcionario.id

    if not funcionario_id:
        email = str(current_user.email or "").strip().lower()
        email_local = email.split("@")[0]
        chave_c = _generate_chave_c(session, email_local)
        funcionario = Funcionario(
            nome=email_local or email,
            chave_c=chave_c,
            diretoria_id=int(diretoria.id),
            email=email,
        )
        session.add(funcionario)
        session.commit()
        session.refresh(funcionario)
        current_user.funcionario_id = funcionario.id
        session.add(current_user)
        session.commit()

    session.refresh(current_user)
    return UsuarioRead.model_validate(current_user, from_attributes=True)


@router.get("/diretorias", response_model=list[DiretoriaRead])
def listar_diretorias_publicas(session: Session = Depends(get_session)):
    """Lista diretorias para cadastro BB (rota publica)."""
    return session.exec(select(Diretoria).order_by(Diretoria.nome)).all()


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    session: Session = Depends(get_session),
):
    """Solicita recuperacao de senha via email.

    Resposta sempre generica para evitar enumeracao.
    """
    result = None
    error_detail: str | None = None
    email_value = str(payload.email or "")
    email_hash = _hash_email(email_value)
    try:
        result = request_password_reset(session, email_value)
    except Exception as exc:
        error_detail = sanitize_exception(exc)

    ip_address = None
    user_agent = None
    request_id = None
    if request is not None:
        request_id = request.headers.get("x-request-id")
        user_agent = request.headers.get("user-agent")
        if request.client:
            ip_address = request.client.host

    telemetry_logger.info(
        "password_reset_requested",
        extra={
            "request_id": request_id,
            "ip": ip_address,
            "user_agent": sanitize_text(user_agent or ""),
            "email_hash": email_hash,
            "result": "FOUND" if getattr(result, "user_found", False) else "NOT_FOUND",
            "error_detail": error_detail,
        },
    )

    time.sleep(PASSWORD_RESET_DELAY_SEC)
    return ForgotPasswordResponse(message=FORGOT_PASSWORD_MESSAGE)


@router.post("/reset-password", response_model=ResetPasswordResponse)
def reset_password_endpoint(
    payload: ResetPasswordRequest,
    session: Session = Depends(get_session),
):
    """Redefine a senha usando um token valido."""
    if not PASSWORD_RE.match(payload.password or ""):
        _raise_http(
            status.HTTP_400_BAD_REQUEST,
            code="PASSWORD_POLICY",
            message="Minimo 6 caracteres, com pelo menos 1 letra e 1 numero",
            field="password",
        )

    try:
        reset_password(session, payload.token, hash_password(payload.password))
    except PasswordResetError as e:
        _raise_http(
            status.HTTP_400_BAD_REQUEST,
            code=e.code,
            message=e.message,
        )

    return ResetPasswordResponse(message="Senha atualizada com sucesso")
