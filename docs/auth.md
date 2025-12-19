# Autenticacao (JWT) - Endpoints

Base da API: `http://localhost:8000` (ajuste conforme ambiente).

## Variaveis de ambiente relevantes
- `DATABASE_URL`: conexao usada pelo app (Postgres/Supabase).
- `DIRECT_URL`: conexao direta para migrations/seed (recomendado no Supabase).
- `SECRET_KEY`: chave do JWT (HS256).
- `ACCESS_TOKEN_EXPIRE_MINUTES`: minutos para expiracao do token.
- `FRONTEND_ORIGIN`: liberacao de CORS para o front.

Recuperacao de senha:
- `EMAIL_BACKEND`: `console` (padrao em dev) ou `smtp`.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_TLS`, `SMTP_SSL` (quando `EMAIL_BACKEND=smtp`).
- `PASSWORD_RESET_URL`: URL base do frontend para reset (ex.: `http://localhost:5173/reset-password`). Se nao informado, o backend usa `FRONTEND_ORIGIN` + `/reset-password`.
- `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES`: expiracao do token (default `60`, minimo `5`).
- `PASSWORD_RESET_TOKEN_SECRET`: segredo opcional para hashear tokens (fallback: `SECRET_KEY`).
- `PASSWORD_RESET_DEBUG`: quando `true`, o backend retorna `token`, `expires_at` e `reset_url` na resposta do forgot-password.

## POST `/auth/login`
- Body JSON: `{"email": "user@example.com", "password": "Senha123!"}`
- 200 OK:
  - `access_token`: JWT
  - `token_type`: `"bearer"`
  - `user`: `UsuarioRead` (sem hash de senha). Campos principais:
    - `id`, `email`, `tipo_usuario` (`bb|npbb|agencia`), `matricula` (opcional), `funcionario_id`, `agencia_id`
- Exemplo de resposta 200:
  ```json
  {
    "access_token": "<jwt>",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "tipo_usuario": "npbb",
      "matricula": null,
      "funcionario_id": null,
      "agencia_id": null
    }
  }
  ```
- 401 Unauthorized: `{"detail":"Credenciais invalidas"}`
- Observacoes:
  - O login compara o email de forma case-insensitive.
  - O JWT usa HS256 e payload contem pelo menos:
    - `sub`: id do usuario
    - `exp`: timestamp de expiracao (UTC)

## GET `/auth/me`
- Header: `Authorization: Bearer <jwt>`
- 200 OK: retorna JSON do usuario autenticado (`UsuarioRead`).
- 401 Unauthorized: token ausente/invalido/expirado.

## Exemplos curl
```bash
# login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"sua-senha"}'

# me
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer <token>"
```

## Cadastro (usuarios/agencias)
Estes endpoints suportam o fluxo de "Criar conta" no frontend.

### GET `/agencias/`
Lista agencias (publico; nao requer JWT). Usado para popular o dropdown no cadastro.

Query params:
- `skip` (int, default `0`)
- `limit` (int, default `50`, max `200`)
- `search` (string, opcional) - busca por `nome` ou `dominio`

Headers:
- `X-Total-Count`: total de agencias com filtros aplicados

Resposta (exemplo):
```json
[
  { "id": 1, "nome": "V3A", "dominio": "v3a.com.br" }
]
```

### POST `/usuarios/`
Cria uma conta de usuario (publico; nao requer JWT). A senha e enviada em texto e **hasheada no servidor**.

Body JSON (`UsuarioCreate`):
- `email` (string)
- `password` (string)
- `tipo_usuario` (`bb|npbb|agencia`)
- `matricula` (string, apenas `bb`)
- `agencia_id` (int, apenas `agencia`)

Respostas:
- `201 Created`: retorna `UsuarioRead`
- `400 Bad Request`: erro de validacao (erro estruturado em `detail`)
- `409 Conflict`: violacao de unicidade (ex.: email ja cadastrado)

Formato de erro estruturado:
```json
{
  "detail": {
    "code": "SOME_CODE",
    "message": "Mensagem humana",
    "field": "campo_opcional"
  }
}
```

Regras de dominio (servidor):
- `bb`: email termina com `@bb.com.br` + matricula no formato `^[A-Za-z][0-9]{1,16}$`
- `npbb`: email termina com `@npbb.com.br`
- `agencia`: dominio do email deve corresponder ao `agencia.dominio` selecionado

Para detalhes do fluxo e validacoes do formulario, veja `docs/login/new_user/login_tela_inicial.md`.

## Recuperacao de senha (usuarios)

### POST `/usuarios/forgot-password`
- Body JSON: `{"email":"user@example.com"}`
- 200 OK: `{"message":"Email de recuperacao enviado"}`
- 404 Not Found: `{"detail":{"code":"USER_NOT_FOUND","message":"Email nao encontrado","field":"email"}}`
- Observacoes:
  - Com `EMAIL_BACKEND=console` (padrao em dev), o "email" e impresso no terminal do `uvicorn`.
  - Em desenvolvimento, com `PASSWORD_RESET_DEBUG=true`, o backend retorna tambem `token`, `expires_at` e `reset_url`.
  - O link enviado aponta para o frontend em `/reset-password?token=...` (rota publica).

### POST `/usuarios/reset-password`
- Body JSON: `{"token":"<token>","password":"Nova123"}`
- 200 OK: `{"message":"Senha atualizada com sucesso"}`
- 400 Bad Request (erros estruturados em `detail`):
  - `PASSWORD_POLICY`: senha fora da politica minima
  - `TOKEN_INVALID|TOKEN_EXPIRED|TOKEN_USED`: token invalido/expirado/ja usado

### Variaveis de ambiente
- `EMAIL_BACKEND` (`console|smtp`) e `SMTP_*` (quando `smtp`).
- `PASSWORD_RESET_URL`, `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES`, `PASSWORD_RESET_DEBUG`.
