"""Esquemas Pydantic para entrada/saída de usuários."""

from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, model_validator


class UsuarioTipo(str, Enum):
    """Tipos de usuário suportados."""

    BB = "bb"
    NPBB = "npbb"
    AGENCIA = "agencia"


class UsuarioCreate(BaseModel):
    """Payload de criação de usuário com validação de vínculo."""

    email: EmailStr
    password: str
    tipo_usuario: UsuarioTipo
    funcionario_id: Optional[int] = None
    agencia_id: Optional[int] = None

    @model_validator(mode="after")
    def check_vinculo_por_tipo(self):
        """Garante que cada tipo informe apenas o vínculo permitido."""
        if self.tipo_usuario == UsuarioTipo.AGENCIA:
            if self.agencia_id is None:
                raise ValueError("Usuário do tipo 'agencia' deve ter agencia_id preenchido")
            if self.funcionario_id is not None:
                raise ValueError("Usuário do tipo 'agencia' não deve ter funcionario_id")
        else:
            if self.funcionario_id is None:
                raise ValueError("Usuário tipo 'bb' ou 'npbb' deve ter funcionario_id")
            if self.agencia_id is not None:
                raise ValueError("Usuário tipo 'bb' ou 'npbb' não deve ter agencia_id")
        return self


class UsuarioRead(BaseModel):
    """Resposta pública de usuário (sem hash de senha)."""

    id: int
    email: EmailStr
    tipo_usuario: UsuarioTipo
    funcionario_id: Optional[int]
    agencia_id: Optional[int]

    class Config:
        orm_mode = True
