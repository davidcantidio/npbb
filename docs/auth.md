# Autenticacao - Endpoints

Base da API: `http://localhost:8000` (ajuste conforme ambiente).

Variaveis de ambiente relevantes
- `DATABASE_URL` / `DIRECT_URL`: conexao com Postgres (Supabase).
- `SECRET_KEY`: chave do JWT (HS256).
- `ACCESS_TOKEN_EXPIRE_MINUTES`: minutos para expiracao do token.
- `FRONTEND_ORIGIN`: liberacao de CORS para o front.

POST /auth/login
- Body JSON: `{"email": "user@example.com", "password": "senha123"}`
- 200 OK: `{"access_token":"<jwt>","token_type":"bearer","user":{...}}`
- 401 Unauthorized: credenciais invalidas.
- O JWT usa HS256 e payload contem pelo menos:
  - `sub`: id do usuario (string)
  - `exp`: timestamp de expiracao (UTC)

GET /auth/me
- Header: `Authorization: Bearer <jwt>`
- 200 OK: retorna JSON do usuario autenticado.
- 401 Unauthorized: token ausente/invalido/expirado.

Exemplos curl
```bash
# login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"sua-senha"}'

# me
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer <token>"
```
