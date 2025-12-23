# Gamificacao (Eventos) - Contrato de API

Base da API (dev): `http://localhost:8000`

Todos os endpoints deste documento exigem autenticacao via JWT:
`Authorization: Bearer <token>`

## Visao geral (MVP)
- A gamificacao e cadastrada por evento (`evento_id`).
- A ativacao pode selecionar uma gamificacao via `ativacao.gamificacao_id` (opcional). No front, esta selecao acontece na etapa de "Ativacoes".
- Campos obrigatorios (MVP): `nome`, `descricao`, `premio`, `titulo_feedback`, `texto_feedback`.
- Normalizacao: strings sao `strip()`; se ficar vazio, e invalido.
- Limites (max length):
  - `nome`: 150
  - `descricao`: 240
  - `premio`: 200
  - `titulo_feedback`: 200
  - `texto_feedback`: 240

## Formato de erros
- Erro simples: `{"detail":"..."}`
- Erro estruturado:
  ```json
  {
    "detail": {
      "code": "SOME_CODE",
      "message": "Mensagem humana",
      "field": "campo_opcional"
    }
  }
  ```

Erros de validacao do FastAPI/Pydantic retornam `422` com `detail` como lista de erros.

---

## GET `/evento/{id}/gamificacoes`
Lista as gamificacoes do evento (ordenadas por `id` asc).

### Resposta
- `200 OK`: `GamificacaoRead[]`

Schema (`GamificacaoRead`):
```json
{
  "id": 1,
  "evento_id": 15,
  "nome": "BB SEGUROS :: CARDS",
  "descricao": "Descricao",
  "premio": "PARABENS",
  "titulo_feedback": "Titulo",
  "texto_feedback": "Texto"
}
```

### Regras de visibilidade
- Usuario `tipo_usuario=agencia` so acessa eventos da propria `agencia_id` (caso contrario retorna `404`).

### Erros comuns
- `401 Unauthorized`: token ausente/invalido
- `404 Not Found`:
  ```json
  { "detail": { "code": "EVENTO_NOT_FOUND", "message": "Evento nao encontrado" } }
  ```

### Exemplo (curl)
```bash
curl "http://localhost:8000/evento/15/gamificacoes" \
  -H "Authorization: Bearer <token>"
```

---

## POST `/evento/{id}/gamificacoes`
Cria uma gamificacao no evento.

### Body (JSON) - `GamificacaoCreate`
```json
{
  "nome": "BB SEGUROS :: CARDS",
  "descricao": "Descricao",
  "premio": "PARABENS",
  "titulo_feedback": "Titulo",
  "texto_feedback": "Texto"
}
```

### Resposta
- `201 Created`: `GamificacaoRead`

### Erros comuns
- `401 Unauthorized`: token ausente/invalido
- `404 Not Found`:
  ```json
  { "detail": { "code": "EVENTO_NOT_FOUND", "message": "Evento nao encontrado" } }
  ```
- `422 Unprocessable Entity`: erro de validacao (required/min/max/trim)

### Exemplo (curl)
```bash
curl -X POST "http://localhost:8000/evento/15/gamificacoes" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "BB SEGUROS :: CARDS",
    "descricao": "Descricao",
    "premio": "PARABENS",
    "titulo_feedback": "Titulo",
    "texto_feedback": "Texto"
  }'
```

---

## PUT `/gamificacao/{id}`
Atualiza uma gamificacao existente (PUT parcial).

### Body (JSON) - `GamificacaoUpdate`
Aceita qualquer campo como opcional, mas exige pelo menos um campo no body.

Exemplo:
```json
{ "premio": "NOVO PREMIO" }
```

### Resposta
- `200 OK`: `GamificacaoRead`

### Erros comuns
- `400 Bad Request` (nenhum campo enviado):
  ```json
  {
    "detail": {
      "code": "VALIDATION_ERROR_NO_FIELDS",
      "message": "Nenhum campo para atualizar"
    }
  }
  ```
- `401 Unauthorized`: token ausente/invalido
- `404 Not Found` (id inexistente ou fora do escopo):
  ```json
  { "detail": { "code": "GAMIFICACAO_NOT_FOUND", "message": "Gamificacao nao encontrada" } }
  ```
- `422 Unprocessable Entity`: erro de validacao (min/max/trim)

### Exemplo (curl)
```bash
curl -X PUT "http://localhost:8000/gamificacao/10" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"premio":"NOVO PREMIO"}'
```

---

## DELETE `/gamificacao/{id}`
Remove uma gamificacao.

### Resposta
- `204 No Content`

### Erros comuns
- `401 Unauthorized`: token ausente/invalido
- `404 Not Found` (id inexistente ou fora do escopo):
  ```json
  { "detail": { "code": "GAMIFICACAO_NOT_FOUND", "message": "Gamificacao nao encontrada" } }
  ```

### Exemplo (curl)
```bash
curl -i -X DELETE "http://localhost:8000/gamificacao/10" \
  -H "Authorization: Bearer <token>"
```

