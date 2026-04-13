"""Esquemas Pydantic para entrada/saida de usuarios."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, model_validator


class UsuarioTipo(str, Enum):
    BB = "bb"
    NPBB = "npbb"
    AGENCIA = "agencia"


class UsuarioCreate(BaseModel):
    """Payload de criacao de usuario (cadastro)."""

    email: EmailStr
    password: str
    tipo_usuario: UsuarioTipo
    matricula: Optional[str] = None
    agencia_id: Optional[int] = None
    diretoria_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_por_tipo(self):
        if self.tipo_usuario == UsuarioTipo.AGENCIA:
            if self.agencia_id is None:
                raise ValueError("Usuario do tipo 'agencia' deve ter agencia_id preenchido")
            if self.matricula:
                raise ValueError("Usuario do tipo 'agencia' nao deve ter matricula")
            if self.diretoria_id is not None:
                raise ValueError("Usuario do tipo 'agencia' nao deve ter diretoria_id")
        elif self.tipo_usuario == UsuarioTipo.BB:
            if not self.matricula or not str(self.matricula).strip():
                raise ValueError("Usuario do tipo 'bb' deve informar matricula")
            if self.diretoria_id is None:
                raise ValueError("Usuario do tipo 'bb' deve informar diretoria")
            if self.agencia_id is not None:
                raise ValueError("Usuario do tipo 'bb' nao deve ter agencia_id")
        else:  # NPBB
            if self.agencia_id is not None:
                raise ValueError("Usuario do tipo 'npbb' nao deve ter agencia_id")
            if self.diretoria_id is not None:
                raise ValueError("Usuario do tipo 'npbb' nao deve ter diretoria_id")
        return self


class UsuarioRead(BaseModel):
    """Resposta publica de usuario (sem hash de senha)."""

    id: int
    email: EmailStr
    matricula: Optional[str] = None
    diretoria_id: Optional[int] = None
    status_aprovacao: Optional[str] = None
    tipo_usuario: UsuarioTipo
    funcionario_id: Optional[int]
    agencia_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class UsuarioDiretoriaUpdate(BaseModel):
    diretoria_id: int


class UsuarioPerfilUpdate(BaseModel):
    matricula: str
    diretoria_id: int
