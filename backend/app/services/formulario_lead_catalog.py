"""Catalogo compartilhado dos campos do formulario publico de landing."""

from __future__ import annotations

from typing import Any

FORMULARIO_CAMPOS_CATALOGO = [
    "Nome",
    "Email",
    "CPF",
    "Telefone",
    "Sobrenome",
    "Estado",
    "Data de nascimento",
    "Endereco",
    "Interesses",
    "Genero",
    "Area de atuacao",
]

FORMULARIO_CAMPOS_ORDEM_BY_LOWER = {
    nome.lower(): index for index, nome in enumerate(FORMULARIO_CAMPOS_CATALOGO)
}

FORMULARIO_CAMPOS_DEFAULT: list[tuple[str, bool]] = [
    ("Nome", True),
    ("Email", True),
    ("CPF", False),
    ("Telefone", False),
    ("Estado", False),
]

FORMULARIO_CAMPO_DEFINITIONS: dict[str, dict[str, Any]] = {
    "nome": {
        "key": "nome",
        "label": "Nome",
        "input_type": "text",
        "autocomplete": "name",
        "placeholder": "Como voce gostaria de ser chamado?",
    },
    "email": {
        "key": "email",
        "label": "Email",
        "input_type": "email",
        "autocomplete": "email",
        "placeholder": "voce@exemplo.com",
    },
    "cpf": {
        "key": "cpf",
        "label": "CPF",
        "input_type": "text",
        "autocomplete": "off",
        "placeholder": "00000000000",
    },
    "telefone": {
        "key": "telefone",
        "label": "Telefone",
        "input_type": "tel",
        "autocomplete": "tel",
        "placeholder": "(00) 00000-0000",
    },
    "sobrenome": {
        "key": "sobrenome",
        "label": "Sobrenome",
        "input_type": "text",
        "autocomplete": "family-name",
        "placeholder": "Seu sobrenome",
    },
    "estado": {
        "key": "estado",
        "label": "Estado",
        "input_type": "text",
        "autocomplete": "address-level1",
        "placeholder": "UF do seu estado",
    },
    "data de nascimento": {
        "key": "data_nascimento",
        "label": "Data de nascimento",
        "input_type": "date",
        "autocomplete": "bday",
        "placeholder": None,
    },
    "endereco": {
        "key": "endereco",
        "label": "Endereco",
        "input_type": "text",
        "autocomplete": "street-address",
        "placeholder": "Seu endereco",
    },
    "interesses": {
        "key": "interesses",
        "label": "Interesses",
        "input_type": "text",
        "autocomplete": "off",
        "placeholder": "Conte o que mais te interessa",
    },
    "genero": {
        "key": "genero",
        "label": "Genero",
        "input_type": "text",
        "autocomplete": "sex",
        "placeholder": "Como voce se identifica",
    },
    "area de atuacao": {
        "key": "area_de_atuacao",
        "label": "Area de atuacao",
        "input_type": "text",
        "autocomplete": "organization-title",
        "placeholder": "Sua area de atuacao",
    },
}


def get_form_field_definition(nome_campo: str) -> dict[str, Any]:
    normalized = str(nome_campo or "").strip().lower()
    default_key = normalized.replace(" ", "_")
    base = FORMULARIO_CAMPO_DEFINITIONS.get(normalized)
    if base:
        return dict(base)
    return {
        "key": default_key,
        "label": str(nome_campo or "").strip() or "Campo",
        "input_type": "text",
        "autocomplete": "off",
        "placeholder": None,
    }
