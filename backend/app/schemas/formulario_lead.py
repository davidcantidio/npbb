"""Schemas do módulo Formulário de Lead / Landing (por evento).

Contrato (MVP):
- Campo "ativo" = existe um registro em `FormularioLeadCampo` para a config do evento.
- `obrigatorio` e `ordem` são propriedades do registro (por campo).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator


class FormularioLandingTemplateRead(BaseModel):
    id: int
    nome: str

    model_config = ConfigDict(from_attributes=True)


class FormularioLeadCampoBase(BaseModel):
    nome_campo: str = Field(min_length=1, max_length=80)
    obrigatorio: bool = True
    ordem: int = Field(ge=0)


class FormularioLeadCampoRead(FormularioLeadCampoBase):
    model_config = ConfigDict(from_attributes=True)


class FormularioLeadCampoWrite(FormularioLeadCampoBase):
    pass


class FormularioLeadUrls(BaseModel):
    url_landing: str | None = None
    url_checkin_sem_qr: str | None = None
    url_questionario: str | None = None
    url_api: str | None = None


class FormularioLeadConfigRead(BaseModel):
    evento_id: int
    template_id: int | None = None

    # Armazenamos no banco como colunas separadas; expomos como objeto `urls` no contrato.
    url_landing: str | None = Field(default=None, exclude=True)
    url_checkin_sem_qr: str | None = Field(default=None, exclude=True)
    url_questionario: str | None = Field(default=None, exclude=True)
    url_api: str | None = Field(default=None, exclude=True)

    campos: list[FormularioLeadCampoRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def urls(self) -> FormularioLeadUrls:
        return FormularioLeadUrls(
            url_landing=self.url_landing,
            url_checkin_sem_qr=self.url_checkin_sem_qr,
            url_questionario=self.url_questionario,
            url_api=self.url_api,
        )


class FormularioLeadConfigUpsert(BaseModel):
    template_id: int | None = None
    campos: list[FormularioLeadCampoWrite] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_campos(self):
        seen: set[str] = set()
        duplicates: set[str] = set()
        for campo in self.campos:
            key = campo.nome_campo.strip().lower()
            if not key:
                continue
            if key in seen:
                duplicates.add(campo.nome_campo)
            seen.add(key)
        if duplicates:
            raise ValueError(f"Campos duplicados no payload: {', '.join(sorted(duplicates))}")
        return self


class FormularioLeadPreviewRequest(BaseModel):
    template_id: int | None = None
    template_override: str | None = Field(default=None, max_length=50)
    cta_personalizado: str | None = Field(default=None, max_length=200)
    descricao_curta: str | None = Field(default=None, max_length=500)
    campos: list[FormularioLeadCampoWrite] | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def validate_unique_campos(self):
        if self.campos is None:
            return self

        seen: set[str] = set()
        duplicates: set[str] = set()
        for campo in self.campos:
            key = campo.nome_campo.strip().lower()
            if not key:
                continue
            if key in seen:
                duplicates.add(campo.nome_campo)
            seen.add(key)
        if duplicates:
            raise ValueError(f"Campos duplicados no payload: {', '.join(sorted(duplicates))}")
        return self
