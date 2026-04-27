REQUIRED_COLUMNS = [
    "nome",
    "cpf",
    "data_nascimento",
    "email",
    "telefone",
    "evento",
    "tipo_evento",
    "local",
    "data_evento",
]

OPTIONAL_COLUMNS = [
    "id_salesforce",
    "sobrenome",
    "sessao",
    "data_compra",
    "data_compra_data",
    "data_compra_hora",
    "opt_in",
    "opt_in_id",
    "opt_in_flag",
    "metodo_entrega",
    "rg",
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
]

ALL_COLUMNS = [*REQUIRED_COLUMNS, *OPTIONAL_COLUMNS]

FINAL_FILENAME = "leads_multieventos_2025.csv"
MAPPING_VERSION = "multieventos_v1"
EVENTO_PADRAO = "Circuito Banco do Brasil de Corridas"
TIPO_EVENTO_PADRAO = "ESPORTE"

WARNING_CPF_INVALIDO = "CPF_INVALIDO_DESCARTADO"
WARNING_DUPLICIDADE_CPF_EVENTO = "DUPLICIDADE_CPF_EVENTO"
WARNING_ARQUIVO_ENCRIPTADO = "ARQUIVO_ENCRIPTADO_SEM_SENHA"
WARNING_ARQUIVO_ZIP_DUPLICADO = "ARQUIVO_IGNORADO_ZIP_DUPLICADO"
WARNING_CIDADE_FORA_MAPEAMENTO = "CIDADE_FORA_MAPEAMENTO"
WARNING_ARQUIVO_FONTE_AGREGADA = "ARQUIVO_EXCLUIDO_FONTE_AGREGADA"
WARNING_BATUKE_DATA_SEM_PRACA_CONFIRMADA = "BATUKE_DATA_SEM_PRACA_CONFIRMADA"
WARNING_LOCALIDADE_INVALIDA = "LOCALIDADE_INVALIDA"
WARNING_DATA_NASCIMENTO_INVALIDA = "DATA_NASCIMENTO_INVALIDA"
WARNING_DATA_NASCIMENTO_AUSENTE = "DATA_NASCIMENTO_AUSENTE"

HEADER_SYNONYMS = {
    "name": "nome",
    "full_name": "nome",
    "nome_completo": "nome",
    "documento": "cpf",
    "cpf_cnpj": "cpf",
    "birth_date": "data_nascimento",
    "dt_nascimento": "data_nascimento",
    "telefone_1": "telefone",
    "phone": "telefone",
    "last_name": "sobrenome",
    "lastname": "sobrenome",
    "surname": "sobrenome",
    "family_name": "sobrenome",
    "session": "sessao",
    "purchase_date": "data_compra",
    "purchase_datetime": "data_compra",
    "delivery_method": "metodo_entrega",
    "street": "endereco_rua",
    "address": "endereco_rua",
    "logradouro": "endereco_rua",
    "number": "endereco_numero",
    "numero": "endereco_numero",
    "postal_code": "cep",
    "zip_code": "cep",
    "zipcode": "cep",
    "sex": "genero",
    "sexo": "genero",
    "gender": "genero",
    "promo_code": "codigo_promocional",
    "coupon_code": "codigo_promocional",
    "ticket_type": "ingresso_tipo",
    "ticket_quantity": "ingresso_qtd",
    "ticket_qty": "ingresso_qtd",
    "salesforce_id": "id_salesforce",
    "source": "fonte_origem",
    "cliente": "is_cliente_bb",
    "cliente_bb": "is_cliente_bb",
    "eh_cliente": "is_cliente_bb",
    "e_cliente": "is_cliente_bb",
    "cliente_estilo": "is_cliente_estilo",
    "eh_cliente_estilo": "is_cliente_estilo",
    "e_cliente_estilo": "is_cliente_estilo",
    "location": "local",
    "evento_nome": "evento",
    "event_name": "evento",
    "event_type": "tipo_evento",
    "event_date": "data_evento",
    "dt_evento": "data_evento",
}

CITY_TO_LOCAL_UF = {
    "campo grande": "Campo Grande-MS",
    "rio de janeiro": "Rio de Janeiro-RJ",
    "salvador": "Salvador-BA",
    "sao luis": "São Luís-MA",
    "sao paulo": "São Paulo-SP",
    "brasilia": "Brasília-DF",
    "fortaleza": "Fortaleza-CE",
    "joao pessoa": "João Pessoa-PB",
    "macapa": "Macapá-AP",
    "porto alegre": "Porto Alegre-RS",
    "natal": "Natal-RN",
}

CITY_TO_EVENT_DATE = {
    "salvador": "2025-07-06",
    "rio de janeiro": "2025-07-20",
    "brasilia": "2025-11-30",
    "natal": "2025-09-21",
    "porto alegre": "2025-10-12",
    "joao pessoa": "2025-09-14",
    "macapa": "2025-11-02",
    "campo grande": "2025-05-18",
    "sao luis": "2025-08-03",
    "sao paulo": "2025-06-08",
    "fortaleza": "2025-12-14",
}
