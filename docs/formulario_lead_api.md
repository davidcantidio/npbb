# Formulario de Lead (Eventos) - Contrato de API

Base da API (dev): `http://localhost:8000`

Todos os endpoints deste documento exigem autenticacao via JWT:
`Authorization: Bearer <token>`

## Visao geral (MVP)
- A configuracao do Formulario de Lead e por evento (`evento_id`).
- `template_id` referencia um `FormularioLandingTemplate` (tema da landing).
- "Campo ativo" = existe um registro em `FormularioLeadCampo` (ou seja, aparece no array `campos[]`).
  - Campo desativado = ausencia no array.
- `obrigatorio` (bool) e `ordem` (int, ascendente) sao propriedades do registro do campo.

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

## GET `/evento/all/formulario-templates`
Lista templates/temas disponiveis para o dropdown de "Tema".

### Query params
- `search` (string, opcional): filtra por nome (case-insensitive; contains)

### Resposta
- `200 OK`: `[{id,nome}]` (ordenado por `nome`)

### Exemplo (curl)
```bash
curl "http://localhost:8000/evento/all/formulario-templates" \
  -H "Authorization: Bearer <token>"
```

### Exemplo de resposta
```json
[
  { "id": 2, "nome": "BB Seguros" },
  { "id": 3, "nome": "Padrao" },
  { "id": 1, "nome": "Surf" }
]
```

---

## GET `/evento/all/formulario-campos` (opcional)
Retorna o catalogo de campos possiveis para o Formulario de Lead (MVP).

### Resposta
- `200 OK`: `string[]`

### Exemplo (curl)
```bash
curl "http://localhost:8000/evento/all/formulario-campos" \
  -H "Authorization: Bearer <token>"
```

### Exemplo de resposta
```json
[
  "CPF",
  "Nome",
  "Sobrenome",
  "Telefone",
  "Email",
  "Data de nascimento",
  "Endereco",
  "Interesses",
  "Genero",
  "Area de atuacao"
]
```

---

## GET `/evento/{id}/form-config`
Retorna a configuracao do Formulario de Lead do evento.

### Regras (MVP)
- Se nao existir `FormularioLeadConfig` persistida para o evento, o backend retorna um "config default" (sem persistir):
  - `template_id: null`
  - `campos`: defaults (ativos) definidos no backend:
    - CPF (obrigatorio)
    - Nome (obrigatorio)
    - Sobrenome (opcional)
    - Email (obrigatorio)
    - Data de nascimento (obrigatorio)
- `urls`: sempre preenchidas (landing/check-in sem QR/questionario/api)
- Visibilidade:
  - usuario `tipo_usuario=agencia` so acessa eventos da propria `agencia_id` (caso contrario retorna `404`).

### Resposta (schema)
```json
{
  "evento_id": 123,
  "template_id": 1,
  "campos": [
    { "nome_campo": "Nome", "obrigatorio": true, "ordem": 0 }
  ],
  "urls": {
    "url_landing": "http://localhost:5173/landing/eventos/123",
    "url_checkin_sem_qr": "http://localhost:8000/checkin-sem-qr/eventos/123",
    "url_questionario": "http://localhost:8000/questionario/eventos/123",
    "url_api": "http://localhost:8000/docs"
  }
}
```

### Erros comuns
- `401 Unauthorized`: token ausente/invalido
- `404 Not Found`: `{"detail":"Evento nao encontrado"}` (inclui caso "fora do escopo" para usuario agencia)

### Exemplo (curl)
```bash
curl "http://localhost:8000/evento/123/form-config" \
  -H "Authorization: Bearer <token>"
```

---

## PUT `/evento/{id}/form-config`
Cria/atualiza a configuracao do Formulario de Lead (upsert).

### Body (JSON)
Campos:
- `template_id` (int | null, opcional)
  - `int`: define/atualiza o template
  - `null`: remove o template
  - omitido: mantem o valor atual
- `campos` (array, opcional)
  - quando enviado: substitui a lista inteira ("replace all")
  - enviar `[]` limpa todos os campos
  - omitido: mantem a lista atual

Item de `campos[]`:
- `nome_campo` (string, obrigatorio)
- `obrigatorio` (bool, default `true`)
- `ordem` (int >= 0, obrigatorio)

Validacoes:
- `campos[].nome_campo` e normalizado via `strip()`
- nomes duplicados (case-insensitive) no payload retornam `422`

### Resposta
- `200 OK`: mesmo formato do `GET /evento/{id}/form-config` (inclui `urls`)

### Erros comuns
- `400 Bad Request` (template inexistente):
  ```json
  { "detail": { "code": "FORM_TEMPLATE_NOT_FOUND", "message": "Template nao encontrado" } }
  ```
- `401 Unauthorized`: token ausente/invalido
- `404 Not Found`: `{"detail":"Evento nao encontrado"}`
- `422 Unprocessable Entity`: erro de validacao do payload (ex.: nomes duplicados, ordem negativa)

### Exemplo (curl) - salvar tema + campos
```bash
curl -X PUT "http://localhost:8000/evento/123/form-config" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": 1,
    "campos": [
      { "nome_campo": "Nome", "obrigatorio": true, "ordem": 0 },
      { "nome_campo": "Email", "obrigatorio": true, "ordem": 1 }
    ]
  }'
```

---

## Geracao de URLs (env vars)
O objeto `urls` e preenchido pelo backend via `app/utils/urls.py`.

Prioridades (MVP):
- `PUBLIC_APP_BASE_URL`: base publica do frontend para landing/promotor (ex.: `https://app.seudominio.com`)
  - fallback: primeiro origin de `FRONTEND_ORIGIN`
  - fallback final (dev): `http://localhost:5173`
- `PUBLIC_LANDING_BASE_URL`: base publica do backend para check-in sem QR/questionario (ex.: `https://api.seudominio.com`)
  - fallback: `${request.base_url}`
  - fallback final (dev): `http://localhost:8000`
- `PUBLIC_API_DOC_URL`: override opcional para `urls.url_api`
  - se nao definido: usa `${request.base_url}/docs` (Swagger do backend)

Padroes:
- `url_landing`: `{PUBLIC_APP_BASE_URL}/landing/eventos/{evento_id}`
- `url_checkin_sem_qr`: `{PUBLIC_LANDING_BASE_URL}/checkin-sem-qr/eventos/{evento_id}`
- `url_questionario`: `{PUBLIC_LANDING_BASE_URL}/questionario/eventos/{evento_id}`
- `url_api`: `http://localhost:8000/docs` (dev; pode variar conforme ambiente)

Exemplo de landing publica (dev):
- `http://localhost:5173/landing/eventos/123`

---

## Check-in sem QR (publico)
Nao requer autenticacao. Retorna HTML nos endpoints GET/POST.

### URLs publicas (dev)
- `http://localhost:8000/checkin-sem-qr/eventos/123`
- `http://localhost:8000/checkin-sem-qr/eventos/123?ativacao_id=10`

### GET `/checkin-sem-qr/eventos/{evento_id}`
Retorna HTML da etapa 1 (CPF) ou etapa 2 quando `etapa=2` for usado como query param.

### POST `/checkin-sem-qr/eventos/{evento_id}`
Recebe o submit do formulario e retorna HTML com confirmacao/erro.

Campos esperados (form-data):
- `cpf` (obrigatorio)
- `ativacao_id` (obrigatorio)
- `etapa` (opcional, usar `2` para etapa de cadastro completo)

### POST `/checkin-sem-qr/eventos/{evento_id}/cpf`
Consulta se o CPF ja existe no evento e retorna JSON.

Exemplo (curl):
```bash
curl -X POST "http://localhost:8000/checkin-sem-qr/eventos/123/cpf" \
  -H "Content-Type: application/json" \
  -d '{"cpf":"529.982.247-25","ativacao_id":10}'
```

Resposta:
```json
{ "lead_existe": true }
```
