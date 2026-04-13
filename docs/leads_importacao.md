# Importacao de Leads (CSV/XLSX)

## Objetivo
Importar leads via CSV/XLSX com mapeamento assistido, aliases e tratamento de datetime.

## Endpoints
- `GET /leads`  
  Lista leads paginados (`page`, `page_size`) com campos principais e a conversao mais recente
  (`evento_convertido_id`, `evento_convertido_nome`, `tipo_conversao`, `data_conversao`).
- `POST /leads/import/upload`  
  Valida arquivo (extensao/tamanho).
- `POST /leads/import/preview`  
  Retorna headers, amostra, `start_index`, `suggestions`, `samples_by_column`, `alias_hits`.
- `POST /leads/import/validate`  
  Valida mapeamento (exige email ou CPF).
- `POST /leads/import`  
  Executa import com mapeamento confirmado.
- `GET /leads/referencias/*`  
  Opcoes canonicas (eventos, cidades, estados, generos).
- `GET/POST /leads/aliases`  
  Lookup e persistencia de alias.

## Regras principais
- Campos essenciais: **email ou CPF**.
- Colunas sem correspondencia podem ser **ignoradas**.
- Campos mapeaveis adicionais (opcionais):
  - Endereco: `endereco_rua`, `endereco_numero`, `bairro`, `cidade`, `estado`, `cep`
  - Perfil: `genero`
  - Compra: `codigo_promocional`, `ingresso_tipo`, `ingresso_qtd`
- Heuristicas e pesos seguem o catalogo do PRD (ver `docs/leads_conversoes.md`).
- Auto-selecao:
  - So ocorre quando a amostra tem **>= 3** valores validos.
  - Confianca automatica e **capada em 0.9**.
- Dedupe (chave unica):
  - Regra: **email + cpf + evento_nome + sessao** (quando aplicavel).
  - Quando email ou cpf estiverem vazios, usa o campo disponivel.
  - Duplicidade no mesmo lote: **mantem a ultima ocorrencia**.
- Upsert (politica):
  - Atualiza apenas **campos nao-nulos** do import.
  - Campos existentes nao sao sobrescritos por valores vazios.
- Batch size:
  - Valor padrao: **500** registros por lote.
- Limite de upload:
  - Tamanho maximo do arquivo controlado por `LEADS_IMPORT_MAX_BYTES` (padrao **50MB**).
  - Para uploads grandes em dev, recomenda-se iniciar o uvicorn com `--timeout-keep-alive 120`.
- Resumo final:
  - O retorno inclui `summary` com `filename`, `total`, `created`, `updated`, `skipped`, `errors`.
  - `errors` corresponde ao total de linhas ignoradas por erro durante o import.
- Enriquecimento opcional por CEP:
  - Quando habilitado (`enriquecer_cep=true`), o sistema tenta preencher
    rua/bairro/cidade/estado a partir do CEP.
  - Falhas na consulta nao bloqueiam o import.
- Aliases:
  - Valores confirmados viram alias para imports futuros.
  - Campos suportados: evento, cidade, estado, genero.
- Datetime:
  - Mantem `data_compra` (datetime).
  - Separa em `data_compra_data` e `data_compra_hora` quando aplicavel.

## Fluxo esperado (legado)
1) Usuario envia arquivo.
2) Sistema detecta linha de dados e sugere mapeamento.
3) Usuario confirma mapeamento e referencias.
4) Import executa, retornando resumo (criadas/atualizadas/ignoradas).
5) UI recarrega a listagem de leads e exibe a tabela atualizada.

## Fluxo ETL (preview/commit)

Alternativa ao fluxo legado, com validacao de qualidade (DQ report) e commit
em duas etapas. O operador seleciona o evento de referencia, envia o arquivo
e revisa o preview antes de confirmar a importacao.

### Endpoints ETL

- `POST /leads/import/etl/preview`
- `POST /leads/import/etl/commit`

### Preview (`POST /leads/import/etl/preview`)

Entrada (`multipart/form-data`):

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `file` | arquivo | sim | CSV ou XLSX |
| `evento_id` | int | sim | ID do evento de referencia |
| `strict` | bool | nao (default `false`) | Quando `true`, o commit bloqueia se houver linhas invalidas |
| `header_row` | int | nao | Linha do cabecalho (1-indexed); enviado quando o sistema nao detecta automaticamente |
| `field_aliases_json` | string (JSON) | nao | Mapa de alias de cabecalho, e.g. `{"cpf": {"column_index": 2, "source_value": "Documento"}}` |

Saida (union discriminada por `status`):

- `status: "previewed"` — preview criado com sucesso:
  - `session_token`, `total_rows`, `valid_rows`, `invalid_rows`, `dq_report[]`.
- `status: "header_required"` — sistema nao detectou cabecalho com CPF:
  - `message`, `max_row`, `scanned_rows`, `required_fields`.
- `status: "cpf_column_required"` — cabecalho encontrado mas sem coluna CPF:
  - `message`, `header_row`, `columns[]` (com `column_index`, `column_letter`, `source_value`), `required_fields`.

### Commit (`POST /leads/import/etl/commit`)

Entrada (JSON):

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `session_token` | string | sim | Token retornado pelo preview |
| `evento_id` | int | sim | Deve corresponder ao preview |
| `force_warnings` | bool | nao (default `false`) | Quando `true`, ignora warnings do DQ report |

Saida (`ImportEtlResult`):
- `session_token`, `total_rows`, `valid_rows`, `invalid_rows`, `created`, `updated`, `skipped`, `errors`, `strict`, `status`, `dq_report[]`.

### Regras do commit

- **`strict=true`**: commit bloqueado quando o preview tem erros de validacao (`has_validation_errors`).
- **`strict=false`**: commit prossegue com as linhas aprovadas, mesmo que existam linhas rejeitadas no preview.
- **Warnings**: commit bloqueado por warnings (e.g. duplicatas no lote) a menos que `force_warnings=true`.
- **Idempotencia**: reutilizar um `session_token` ja comitado retorna o mesmo resultado sem reprocessar.

### Codigos de erro ETL

| Codigo | HTTP | Descricao |
|--------|------|-----------|
| `ETL_INVALID_INPUT` | 400 | Payload ou arquivo invalido |
| `ETL_COMMIT_BLOCKED` | 409 | Gate de validacao ou warnings bloqueou o commit |
| `ETL_SESSION_CONFLICT` | 409 | Conflito de sessao de preview (evento errado ou token ja consumido) |
| `ETL_SESSION_NOT_FOUND` | 404 | `session_token` inexistente ou expirado |

### Fluxo ETL esperado
1) Operador seleciona evento e envia arquivo CSV/XLSX.
2) Sistema retorna preview com contagens e DQ report. Se cabecalho nao detectado, pede `header_row`; se CPF ausente no cabecalho, pede `cpf_column_index`.
3) Operador revisa preview e confirma commit (com `force_warnings` se necessario).
4) Sistema persiste leads aprovados (dedupe por email+cpf+evento_nome+sessao, upsert nao-destrutivo).
5) Resultado final inclui contagens de `created`, `updated`, `skipped` e `errors`.

## Resposta de listagem (`GET /leads`)
- Estrutura:
  - `page`, `page_size`, `total`, `items[]`.
- Cada item inclui, entre outros:
  - Identificacao e contato: `id`, `nome`, `email`, `cpf`, `telefone`.
  - Origem: `evento_nome`, `cidade`, `estado`.
  - Conversao mais recente: `evento_convertido_id`, `evento_convertido_nome`,
    `tipo_conversao`, `data_conversao`.
  - Datas: `data_compra`, `data_criacao`.
