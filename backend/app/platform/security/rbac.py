"""Shared authz dependencies for internal APIs."""

from __future__ import annotations

from collections.abc import Iterable
from uuid import uuid4

from fastapi import Depends, HTTPException, status

from app.core.auth import get_current_user
from app.models.models import Usuario, UsuarioTipo


def require_internal_user(*, required_roles: Iterable[UsuarioTipo] | None = None):
    """Return dependency that enforces internal auth and optional role gate."""
    allowed = set(required_roles or [])

    def dependency(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if allowed and current_user.tipo_usuario not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "Acesso restrito para este recurso interno.",
                    "correlation_id": f"authz-{uuid4().hex[:12]}",
                    "action": "Solicite permissao ao administrador NPBB.",
                },
            )
        return current_user

    return dependency


require_npbb_user = require_internal_user(required_roles=[UsuarioTipo.NPBB])

