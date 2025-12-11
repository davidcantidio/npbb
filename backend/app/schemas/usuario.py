from typing import Optional
from enum import Enum

from pydantic import BaseModel, EmailStr, root_validator


class UsuarioTipo(str, Enum):
    BB = "bb"
    NPBB = "npbb"
    AGENCIA = "agencia"


class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str
    tipo_usuario: UsuarioTipo

    funcionario_id: Optional[int] = None
    agencia_id: Optional[int] = None

    @root_validator
    def check_vinculo_por_tipo(cls, values):
        tipo = values.get("tipo_usuario")
        func  = values.get("funcionario_id")
        ag    = values.get("agencia_id")

        if tipo == UsuarioTipo.AGENCIA:
            if ag is None:
                raise ValueError("Usuário do tipo 'agencia' deve ter agencia_id preenchido")
            if func is not None:
                raise ValueError("Usuário do tipo 'agencia' não deve ter funcionario_id")
        else:
            # bb ou npbb
            if func is None:
                raise ValueError("Usuário do tipo 'bb' ou 'npbb' deve ter funcionario_id preenchido")
            if ag is not None:
                raise ValueError("Usuário do tipo 'bb' ou 'npbb' não deve ter agencia_id")

        return values


class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    tipo_usuario: Optional[UsuarioTipo] = None

    funcionario_id: Optional[int] = None
    agencia_id: Optional[int] = None

    @root_validator
    def check_vinculo_por_tipo(cls, values):
        tipo = values.get("tipo_usuario")
        func  = values.get("funcionario_id")
        ag    = values.get("agencia_id")

        if tipo == UsuarioTipo.AGENCIA:
            if ag is None:
                raise ValueError("Usuário do tipo 'agencia' deve ter agencia_id preenchido")
        else:
            if func is None:
                raise ValueError("Usuário do tipo 'bb' ou 'npbb' deve ter funcionario_id preenchido")

        return values
