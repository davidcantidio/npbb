"""Canonical field catalog for shared lead-row contracts."""

from __future__ import annotations

from typing import Final


LEAD_ROW_FIELDS: Final[tuple[str, ...]] = (
    "id_salesforce",
    "nome",
    "sobrenome",
    "email",
    "telefone",
    "cpf",
    "rg",
    "data_nascimento",
    "evento_nome",
    "sessao",
    "data_compra",
    "opt_in",
    "opt_in_id",
    "opt_in_flag",
    "metodo_entrega",
    "endereco_rua",
    "endereco_numero",
    "complemento",
    "bairro",
    "cep",
    "cidade",
    "estado",
    "genero",
    "codigo_promocional",
    "ingresso_tipo",
    "ingresso_qtd",
    "fonte_origem",
    "is_cliente_bb",
    "is_cliente_estilo",
)


LEAD_ROW_EXCLUDED_FIELDS: Final[dict[str, str]] = {
    "id": "Primary key de persistencia; nao pertence ao contrato de entrada.",
    "data_criacao": "Timestamp de persistencia/auditoria, definido fora do contrato.",
    "data_compra_data": "Campo derivado de persistencia a partir de data_compra.",
    "data_compra_hora": "Campo derivado de persistencia a partir de data_compra.",
    "batch_id": "FK para lead_batches; metadado de persistencia, definido fora do contrato.",
}


LEGACY_COERCION_FIELDS: Final[tuple[str, ...]] = (
    "email",
    "cpf",
    "telefone",
    "cep",
    "data_nascimento",
    "data_compra",
    "ingresso_qtd",
    "opt_in_flag",
    "estado",
)


ETL_ALIAS_TO_LEAD_ROW_FIELD: Final[dict[str, str]] = {
    "evento": "evento_nome",
    "sexo": "genero",
    "dt_hr_compra": "data_compra",
    "qtd_ingresso": "ingresso_qtd",
    "dt_nascimento": "data_nascimento",
    "ingresso": "ingresso_tipo",
}


ETL_FORBIDDEN_FIELDS: Final[tuple[str, ...]] = (
    "source_id",
    "ingestion_id",
    "lineage_ref_id",
    "sheet_name",
    "row_number",
    "source_range",
    "sessao_start_at",
    "cpf_hash",
    "email_hash",
    "person_key_hash",
    "cpf_promotor",
    "cpf_promotor_hash",
    "nome_promotor",
    "acoes",
    "acoes_raw",
    "acoes_list",
    "interesses",
    "area_atuacao",
    "event_id",
    "session_id",
    "lead_created_at",
    "lead_created_date",
    "delivery_method",
    "ticket_qty",
    "__sheet_name",
    "__header_row",
    "__header_range",
    "__used_range",
    "__source_range",
    "__row_number",
    "__raw_payload",
)
