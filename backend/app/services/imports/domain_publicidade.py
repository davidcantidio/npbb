"""Especificacao e normalizacao do dominio de importacao de publicidade."""

from __future__ import annotations

from datetime import datetime, date

from app.services.imports.contracts import ImportDomainSpec, ImportFieldSpec

PUBLICIDADE_DOMAIN_SPEC = ImportDomainSpec(
    domain="publicidade",
    fields=(
        ImportFieldSpec(
            name="codigo_projeto",
            required=True,
            aliases=("codigo projeto", "cod projeto", "cod_projeto", "project_code"),
            kind="text",
            uppercase=True,
        ),
        ImportFieldSpec(
            name="projeto",
            required=True,
            aliases=("nome projeto", "project", "nome do projeto"),
            kind="text",
        ),
        ImportFieldSpec(
            name="data_veiculacao",
            required=True,
            aliases=(
                "data vinculacao",
                "data_vinculacao",
                "dt vinculacao",
                "data veiculacao",
                "data_veiculacao",
                "dt veiculacao",
                "linked_at",
            ),
            kind="date",
        ),
        ImportFieldSpec(
            name="meio",
            required=True,
            aliases=("canal", "midia", "media"),
            kind="text",
            uppercase=True,
        ),
        ImportFieldSpec(
            name="veiculo",
            required=True,
            aliases=("veiculo midia", "veiculo de midia"),
            kind="text",
        ),
        ImportFieldSpec(
            name="uf",
            required=True,
            aliases=("estado", "sigla uf"),
            kind="uf",
            uppercase=True,
        ),
        ImportFieldSpec(
            name="uf_extenso",
            required=False,
            aliases=("estado extenso", "nome estado"),
            kind="text",
        ),
        ImportFieldSpec(
            name="municipio",
            required=False,
            aliases=("cidade"),
            kind="text",
        ),
        ImportFieldSpec(
            name="camada",
            required=True,
            aliases=("layer", "nivel", "segmento"),
            kind="text",
            uppercase=True,
        ),
    ),
    required_key_fields=("codigo_projeto", "data_veiculacao", "meio", "veiculo", "uf", "camada"),
    alias_fields=("codigo_projeto",),
)

_UPPERCASE_FIELDS = {"codigo_projeto", "meio", "uf", "camada"}
_LEGACY_FIELD_MAP = {"data_vinculacao": "data_veiculacao"}


def parse_import_date(value: str) -> date | None:
    raw = (value or "").strip()
    if not raw:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def normalize_publicidade_value(field_name: str, value: str) -> object | None:
    raw = (value or "").strip()
    if not raw:
        return None
    if field_name in {"data_veiculacao", "data_vinculacao"}:
        return parse_import_date(raw)
    if field_name in _UPPERCASE_FIELDS:
        return raw.upper()
    return raw


def canonical_publicidade_field_name(field_name: str | None) -> str | None:
    if field_name is None:
        return None
    return _LEGACY_FIELD_MAP.get(field_name, field_name)
