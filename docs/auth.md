# Autenticacao (JWT) - Endpoints

Base da API: `http://localhost:8000` (ajuste conforme ambiente).

## Variaveis de ambiente relevantes
- `DATABASE_URL`: conexao usada pelo app (Postgres/Supabase).
- `DIRECT_URL`: conexao direta para migrations/seed (recomendado no Supabase).
- `SECRET_KEY`: chave do JWT (HS256).
- `ACCESS_TOKEN_EXPIRE_MINUTES`: minutos para expiracao do token.
- `FRONTEND_ORIGIN`: liberacao de CORS para o front.

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
Para cadastro de usuarios e listagem de agencias (fluxo de "Criar Conta"), veja `docs/login/new_user/login_tela_inicial.md`.

## Recuperacao de senha (usuarios)

### POST `/usuarios/forgot-password`
- Body JSON: `{"email":"user@example.com"}`
- 200 OK: `{"message":"Email de recuperacao enviado"}`
- 404 Not Found: `{"detail":{"code":"USER_NOT_FOUND","message":"Email nao encontrado","field":"email"}}`
- Observacoes:
  - Com `EMAIL_BACKEND=console` (padrao em dev), o "email" e impresso no terminal do `uvicorn`.
  - Em desenvolvimento, com `PASSWORD_RESET_DEBUG=true`, o backend retorna tambem `token`, `expires_at` e `reset_url`.

### POST `/usuarios/reset-password`
- Body JSON: `{"token":"<token>","password":"Nova123"}`
- 200 OK: `{"message":"Senha atualizada com sucesso"}`
- 400 Bad Request (erros estruturados em `detail`):
  - `PASSWORD_POLICY`: senha fora da politica minima
  - `TOKEN_INVALID|TOKEN_EXPIRED|TOKEN_USED`: token invalido/expirado/ja usado

### Variaveis de ambiente
- `EMAIL_BACKEND` (`console|smtp`) e `SMTP_*` (quando `smtp`).
- `PASSWORD_RESET_URL`, `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES`, `PASSWORD_RESET_DEBUG`.
