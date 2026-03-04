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
    "cidade": "local",
    "location": "local",
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
