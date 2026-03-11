"""Schema dedicado ao payload de landing por evento/ativacao."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.landing_public import (
    GamificacaoPublicSchema,
    LandingAccessRead,
    LandingAtivacaoRead,
    LandingBrandRead,
    LandingEventRead,
    LandingFormRead,
    LandingTemplateConfigRead,
)


class LandingPayload(BaseModel):
    ativacao_id: int | None = None
    ativacao: LandingAtivacaoRead | None = None
    gamificacoes: list[GamificacaoPublicSchema] = Field(default_factory=list)
    evento: LandingEventRead
    template: LandingTemplateConfigRead
    formulario: LandingFormRead
    marca: LandingBrandRead
    acesso: LandingAccessRead
    lead_reconhecido: bool = False
    token: str | None = None
