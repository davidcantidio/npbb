# Eventos - Contrato de API

Base da API (dev): `http://localhost:8000`

Todos os endpoints deste documento exigem autenticacao via JWT:
`Authorization: Bearer <token>`

## Formato de erros
- Erro simples: `{"detail":"..."}`
- Erro estruturado:
  ```json
  {"detail":{"code":"SOME_CODE","message":"Mensagem humana","field":"campo_opcional"}}
  ```

## GET `/evento`
Lista eventos com paginacao e filtros opcionais.

### Query params
- `skip` (int, default `0`)
- `limit` (int, default `25`, max `200`)
- `search` (string) - busca por `nome` (case-insensitive)
- `estado` (string) - UF (case-insensitive; match exato)
- `cidade` (string) - cidade (case-insensitive; match exato)
- `data` (date `YYYY-MM-DD`) - retorna eventos cujo periodo contem a data (modo legado)
- `data_inicio` (date `YYYY-MM-DD`) - filtra por intervalo (sobreposicao de periodo)
- `data_fim` (date `YYYY-MM-DD`) - filtra por intervalo (sobreposicao de periodo)
- `diretoria_id` (int) - filtra por diretoria

Notas sobre datas:
- Se `data_inicio` ou `data_fim` forem informados, o backend aplica filtro por intervalo e ignora `data`.
- Se `data_inicio` e `data_fim` forem informados e `data_fim < data_inicio`, retorna `400` com `detail.code=DATE_RANGE_INVALID`.

### Resposta
- `200 OK`: lista de `EventoListItem`
- Header `X-Total-Count`: total de itens (com filtros aplicados)

**Visibilidade**:
- usuario `tipo_usuario=agencia` ve apenas eventos da propria `agencia_id`.

### Exemplos (curl)
```bash
# lista (paginado)
curl "http://localhost:8000/evento?skip=0&limit=25" \
  -H "Authorization: Bearer <token>"

# busca por nome (contains, case-insensitive)
curl "http://localhost:8000/evento?search=feira" \
  -H "Authorization: Bearer <token>"

# filtros por UF e cidade (match exato, case-insensitive)
curl "http://localhost:8000/evento?estado=SP&cidade=S%C3%A3o%20Paulo" \
  -H "Authorization: Bearer <token>"

# intervalo de datas (sobreposicao do periodo do evento)
curl "http://localhost:8000/evento?data_inicio=2025-01-01&data_fim=2025-01-31" \
  -H "Authorization: Bearer <token>"

# combinando filtros (nome + UF + diretoria + paginacao)
curl "http://localhost:8000/evento?search=teste&estado=SE&diretoria_id=15&skip=0&limit=50" \
  -H "Authorization: Bearer <token>"
```

## Saude dos dados (score)

A regra de pontuacao e documentada em:

```
npbb/docs/eventos_saude_dados.md
```

O arquivo de configuracao editavel (pesos, urgencia e excecoes) fica em:

```
npbb/docs/eventos_saude_dados_config.json
```

## GET `/evento/{id}`
Retorna detalhe do evento.

### Resposta
- `200 OK`: `EventoRead` (inclui `tag_ids` e `territorio_ids`)
- `404 Not Found`: evento nao encontrado (ou fora do escopo para usuario agencia)

## GET `/evento/export/csv`
Exporta a listagem de eventos em CSV (para download).

### Query params
Mesmos filtros do `GET /evento`, mais:
- `skip` (int, default `0`)
- `limit` (int, default `5000`, max `10000`)

### Resposta
- `200 OK`: arquivo CSV (`Content-Type: text/csv; charset=utf-8`)
- Header `Content-Disposition: attachment; filename="eventos.csv"`

Observacoes:
- Delimitador: `;` (compatibilidade com Excel/pt-BR).
- Inclui BOM UTF-8 (para acentos abrirem corretamente no Excel).

### Colunas do CSV
O CSV retorna, no minimo, as seguintes colunas (podem ser estendidas no futuro):

`id`, `nome`, `descricao`, `agencia_id`, `agencia_nome`, `diretoria_id`, `diretoria_nome`,
`divisao_demandante_id`, `divisao_demandante_nome`, `tipo_id`, `tipo_nome`, `subtipo_id`, `subtipo_nome`,
`status_id`, `status_nome`, `estado`, `cidade`, `data_inicio_prevista`, `data_fim_prevista`,
`data_inicio_realizada`, `data_fim_realizada`, `investimento`, `territorios`, `tags`, `qr_code_url`,
`created_at`, `updated_at`.

### Exemplos (curl)
```bash
# exporta tudo que o usuario pode ver
curl -L "http://localhost:8000/evento/export/csv" \
  -H "Authorization: Bearer <token>" \
  -o eventos.csv

# exporta com filtros (mesmos de GET /evento)
curl -L "http://localhost:8000/evento/export/csv?estado=SE&data_inicio=2025-01-01&data_fim=2025-12-31" \
  -H "Authorization: Bearer <token>" \
  -o eventos-filtrados.csv
```

## POST `/evento`
Cria um novo evento.

### Body (JSON) - `EventoCreate`
Campos principais:
- `nome` (string, obrigatorio)
- `cidade` (string, obrigatorio)
- `estado` (string, obrigatorio; normalizado para uppercase)
- `data_inicio_prevista` (date `YYYY-MM-DD`, obrigatorio)

Campos opcionais:
- `descricao` (string; recomendado <= 240)
- `investimento` (decimal/number)
- `agencia_id` (int) - se informado, deve existir em `agencia`
- `diretoria_id` (int)
- `gestor_id` (int)
- `tipo_id` (int) - se informado, deve existir em `tipo_evento`
- `subtipo_id` (int) - se informado, deve pertencer ao `tipo_id`
- `status_id` (int, opcional) - FK para `status_evento` (ver dicionarios). Se omitido, o backend infere:
  - se `data_inicio_prevista` > hoje -> `Previsto`
  - se `data_fim_prevista` < hoje -> `Realizado`
  - caso contrario -> `Confirmado`
  - se nao houver datas -> `A Confirmar`

Campos adicionais:
- `divisao_demandante_id` (int) - FK para o dominio `divisao_demandante` (ver dicionarios)
- `thumbnail` (string URL)
- `qr_code_url` (string URL)
- Datas (ISO `YYYY-MM-DD`):
  - `data_inicio_prevista` (obrigatoria)
  - `data_fim_prevista` (opcional)
- Publico:
  - `publico_projetado`, `publico_realizado`

Relacionamentos (N:N):
- `tag_ids` (list[int]) - ids existentes em `tag`
- `territorio_ids` (list[int]) - ids existentes em `territorio`

### Resposta
- `201 Created`: `EventoRead`

### Erros comuns
- `400` com `detail.code`:
  - `AGENCIA_NOT_FOUND`, `DIRETORIA_NOT_FOUND`, `DIVISAO_DEMANDANTE_NOT_FOUND`, `TIPO_EVENTO_NOT_FOUND`, `SUBTIPO_EVENTO_NOT_FOUND`
  - `TIPO_EVENTO_REQUIRED` (quando `subtipo_id` foi informado sem `tipo_id`)
  - `SUBTIPO_EVENTO_INVALID` (subtipo nao pertence ao tipo)
  - `STATUS_NOT_FOUND`, `STATUS_REQUIRED`
  - `TAG_NOT_FOUND`, `TERRITORIO_NOT_FOUND`
  - `TAG_ID_INVALID`, `TERRITORIO_ID_INVALID` (ids invalidos)
- `403` com `detail.code=FORBIDDEN` (ex.: usuario agencia tentando alterar `agencia_id`)

## PUT `/evento/{id}`
Atualiza um evento existente (PUT parcial).

### Body (JSON) - `EventoUpdate`
Aceita qualquer campo de `EventoCreate` como opcional, mais:
- `tag_ids` (list[int] | null): substitui o conjunto de tags do evento
- `territorio_ids` (list[int] | null): substitui o conjunto de territorios do evento

### Regras
- Se `subtipo_id` for informado, deve pertencer ao `tipo_id` (novo ou atual).
- Usuario `tipo_usuario=agencia` nao pode alterar `agencia_id`.

### Resposta
- `200 OK`: `EventoRead`
- `404 Not Found`: evento nao encontrado (ou fora do escopo para usuario agencia)

## DELETE `/evento/{id}`
Exclui um evento.

### Resposta
- `204 No Content`: removido
- `404 Not Found`: evento nao encontrado (ou fora do escopo para usuario agencia)
- `409 Conflict` (bloqueado por dependencias):
  ```json
  {
    "detail": {
      "code": "EVENTO_DELETE_BLOCKED",
      "message": "Nao e possivel excluir evento com vinculos",
      "dependencies": {
        "ativacoes": 1,
        "cotas": 2
      }
    }
  }
  ```

## Dicionarios (GET `/evento/all/*`)
Usados para preencher dropdowns/autocomplete no front.

- `/evento/all/cidades` -> `string[]` (cidades existentes em eventos visiveis ao usuario)
- `/evento/all/cidades?estado=UF` -> `string[]` (cidades filtradas por UF; case-insensitive)
- `/evento/all/estados` -> `string[]` (UFs existentes em eventos visiveis ao usuario)
- `/evento/all/divisoes-demandantes` -> `{id,nome}[]` (suporta `search`)
- `/evento/all/diretorias` -> `DiretoriaRead[]` (suporta `search`)
- `/evento/all/tipos-evento` -> `TipoEventoRead[]` (suporta `search`)
- `/evento/all/subtipos-evento` -> `SubtipoEventoRead[]` (suporta `tipo_id` e `search`)
- `/evento/all/status-evento` -> `StatusEventoRead[]` (suporta `search`)
- `/evento/all/territorios` -> `TerritorioRead[]` (suporta `search`)
- `/evento/all/tags` -> `TagRead[]` (suporta `search`)

### Exemplos (curl)
```bash
curl "http://localhost:8000/evento/all/diretorias" \
  -H "Authorization: Bearer <token>"

curl "http://localhost:8000/evento/all/subtipos-evento?tipo_id=1" \
  -H "Authorization: Bearer <token>"

curl "http://localhost:8000/evento/all/tags?search=cult" \
  -H "Authorization: Bearer <token>"
```

## POST `/evento/tags`
Cria (ou reutiliza) uma tag para uso no formulario de evento.

### Body
```json
{ "nome": "Nova Tag" }
```

### Resposta
- `201 Created`: `TagRead` (tag criada)
- `200 OK`: `TagRead` (tag ja existia)

### Exemplo (curl)
```bash
curl -X POST "http://localhost:8000/evento/tags" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"nome":"Nova Tag"}'
```
