# Tela: Login

Rota no frontend: `/login`

Tela publica para autenticar o usuario e iniciar uma sessao.

Status no novo sistema:
- Frontend: implementado.
- Backend: endpoints implementados (`POST /auth/login`, `GET /auth/me`).

---

## 1. Estrutura da tela
- Campo **Email**
- Campo **Senha**
- Botao **Entrar**
- Link **Criar conta** -> `/novo-usuario`
- Link **Esqueceu a senha?** -> abre dialog/modal para solicitar recuperacao

---

## 2. Comportamento
### 2.1 Login
1. Usuario preenche email/senha e clica **Entrar**
2. Front chama `POST /auth/login`
3. Em sucesso:
   - token e salvo no frontend
   - front chama `GET /auth/me` (ou usa o `user` retornado no login)
   - usuario e redirecionado para a rota protegida (ex.: `/eventos`)
4. Em erro (401): mostrar mensagem de credenciais invalidas

### 2.2 Esqueceu a senha
1. Usuario clica **Esqueceu a senha?**
2. Abre dialog para informar email
3. Front chama `POST /usuarios/forgot-password`
4. Em sucesso: mostrar confirmacao ("Email de recuperacao enviado")
5. Em erro (404): mostrar "Email nao encontrado"

Em desenvolvimento:
- Se `EMAIL_BACKEND=console`, o backend imprime o email no terminal do `uvicorn`.
- Se `PASSWORD_RESET_DEBUG=true`, o backend retorna `reset_url` e o dialog pode exibir o link diretamente.

---

## 3. Endpoints de API envolvidos
- `POST /auth/login` (ver `docs/auth.md`)
- `GET /auth/me` (ver `docs/auth.md`)
- `POST /usuarios/forgot-password` (ver `docs/auth.md`)

