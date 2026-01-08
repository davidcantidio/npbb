# Ativacoes (Eventos) - Contrato de API

Base da API (dev): `http://localhost:8000`

Todos os endpoints deste documento exigem autenticacao via JWT:
`Authorization: Bearer <token>`

## Visao geral (MVP)
- A ativacao e cadastrada por evento (`evento_id`).
- No formulario, o campo "Mensagem" usa `descricao` (opcional).
- Switches (defaults `false`): `redireciona_pesquisa`, `checkin_unico`, `termo_uso`, `gera_cupom`.
- Normalizacao: strings sao `strip()`; campos opcionais viram `null` quando vazios.
- `valor` existe no modelo/DB, mas fica fora do payload do modulo de ativacoes (MVP). No create, o backend grava `0.00`.
- Ordenacao da lista (MVP): `id` asc.
- Limites (max length):
  - `nome`: 100 (obrigatorio)
  - `descricao`: 240 (opcional)
  - `mensagem_qrcode`: 240 (opcional)

## Formato de erros
- Erro simples: `{"detail":"..."}`
- Erro estruturado:
  ```json
  {
    "detail": {
      "code": "SOME_CODE",
      "message": "Mensagem humana",
      "field": "campo_opcional",
      "dependencies": { "cupons": 2 }
    }
  }
  ```

Erros de validacao do FastAPI/Pydantic retornam `422` com `detail` como lista de erros.

---

## GET `/evento/{id}/ativacoes`
Lista as ativacoes do evento (ordenadas por `id` asc).

### Resposta
- `200 OK`: `AtivacaoRead[]`

Schema (`AtivacaoRead`):
```json
{
  "id": 1,
  "evento_id": 15,
  "nome": "Ativacao - Check-in",
  "descricao": "Ativacao de exemplo (check-in unico).",
  "mensagem_qrcode": "Check-in valido apenas uma vez.",
  "gamificacao_id": null,
  "redireciona_pesquisa": false,
  "checkin_unico": true,
  "termo_uso": false,
  "gera_cupom": false,
  "created_at": "2026-01-01T12:34:56.789Z",
  "updated_at": "2026-01-01T12:34:56.789Z"
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
curl "http://localhost:8000/evento/15/ativacoes" \
  -H "Authorization: Bearer <token>"
```

---

## POST `/evento/{id}/ativacoes`
Cria uma ativacao no evento.

### Body (JSON) - `AtivacaoCreate`
Exemplo minimo:
```json
{ "nome": "Ativacao - Check-in" }
```

Exemplo completo:
```json
{
  "nome": "Ativacao - Cupom",
  "descricao": "Ativacao de exemplo (gera cupom).",
  "mensagem_qrcode": "Cupom gerado apos o check-in.",
  "gamificacao_id": null,
  "redireciona_pesquisa": false,
  "checkin_unico": false,
  "termo_uso": true,
  "gera_cupom": true
}
```

### Resposta
- `201 Created`: `AtivacaoRead`

### Erros comuns
- `400 Bad Request` (gamificacao fora do evento):
  ```json
  {
    "detail": {
      "code": "GAMIFICACAO_OUT_OF_SCOPE",
      "message": "Gamificacao invalida para este evento",
      "field": "gamificacao_id"
    }
  }
  ```
- `401 Unauthorized`: token ausente/invalido
- `404 Not Found`:
  ```json
  { "detail": { "code": "EVENTO_NOT_FOUND", "message": "Evento nao encontrado" } }
  ```
- `422 Unprocessable Entity`: erro de validacao (required/min/max/trim)

### Exemplo (curl)
```bash
curl -X POST "http://localhost:8000/evento/15/ativacoes" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Ativacao - Cupom",
    "descricao": "Ativacao de exemplo (gera cupom).",
    "mensagem_qrcode": "Cupom gerado apos o check-in.",
    "termo_uso": true,
    "gera_cupom": true
  }'
```

---

## PUT `/ativacao/{id}`
Atualiza uma ativacao existente (PUT parcial).

### Body (JSON) - `AtivacaoUpdate`
Aceita qualquer campo como opcional, mas exige pelo menos um campo no body.

Exemplo:
```json
{ "checkin_unico": true }
```

### Resposta
- `200 OK`: `AtivacaoRead`

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
- `400 Bad Request` (gamificacao fora do evento da ativacao):
  ```json
  {
    "detail": {
      "code": "GAMIFICACAO_OUT_OF_SCOPE",
      "message": "Gamificacao invalida para este evento",
      "field": "gamificacao_id"
    }
  }
  ```
- `401 Unauthorized`: token ausente/invalido
- `404 Not Found` (id inexistente ou fora do escopo):
  ```json
  { "detail": { "code": "ATIVACAO_NOT_FOUND", "message": "Ativacao nao encontrada" } }
  ```
- `422 Unprocessable Entity`: erro de validacao (min/max/trim)

### Exemplo (curl)
```bash
curl -X PUT "http://localhost:8000/ativacao/10" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"checkin_unico":true}'
```

---

## DELETE `/ativacao/{id}`
Remove uma ativacao.

### Resposta
- `204 No Content`

### Regras (MVP)
- Bloqueia exclusao se existirem dependencias (por exemplo: `ativacao_leads`, `cupons`, `respostas_questionario`, `investimentos`).

### Erros comuns
- `401 Unauthorized`: token ausente/invalido
- `404 Not Found` (id inexistente ou fora do escopo):
  ```json
  { "detail": { "code": "ATIVACAO_NOT_FOUND", "message": "Ativacao nao encontrada" } }
  ```
- `409 Conflict` (bloqueado por dependencias):
  ```json
  {
    "detail": {
      "code": "ATIVACAO_DELETE_BLOCKED",
      "message": "Nao e possivel excluir ativacao com vinculos",
      "dependencies": {
        "cupons": 2
      }
    }
  }
  ```

### Exemplo (curl)
```bash
curl -i -X DELETE "http://localhost:8000/ativacao/10" \
  -H "Authorization: Bearer <token>"
```

