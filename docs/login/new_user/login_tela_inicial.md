# Tela: Criar nova conta (Cadastro)

Rota no frontend: `/novo-usuario`

Esta tela permite que um usuario se registre no sistema, escolhendo seu tipo e preenchendo os campos obrigatorios conforme regras de negocio.

Status no novo sistema:
- Frontend: implementado (formulario em etapas).
- Backend: endpoints implementados (`GET /agencias/` e `POST /usuarios/`).

---

## 1. Fluxo (etapas)
O cadastro e dividido em etapas (wizard/stepper):

1. **Tipo de usuario**
   - Opcoes: Funcionario BB, Funcionario NPBB, Funcionario Agencia
2. **Agencia** (apenas se tipo = Agencia)
   - Dropdown de agencias (lista via API)
   - O dropdown mostra apenas `nome` (nao exibe `dominio`)
3. **Dados da conta**
   - Email
   - Senha
   - Confirmar senha
   - Matricula BB (apenas se tipo = BB)

Ao final, o botao **Criar conta** envia os dados para o backend.

---

## 2. Regras de validacao
### 2.1 Dominio do email por tipo
- **BB**: email deve terminar com `@bb.com.br`
- **NPBB**: email deve terminar com `@npbb.com.br`
- **Agencia**: o dominio do email deve corresponder ao dominio da agencia selecionada (`agencia.dominio`, ex.: `v3a.com.br`)

Observacao: para Agencia, a validacao aceita `email@v3a.com.br` e subdominios como `email@x.v3a.com.br` (quando aplicavel).

### 2.2 Matricula BB
- Obrigatoria apenas para tipo **BB**
- Formato: 1 letra + 1 a 16 numeros
- Regex: `^[A-Za-z][0-9]{1,16}$` (ex.: `c1351833`)

### 2.3 Politica minima de senha
- Minimo 6 caracteres
- Pelo menos 1 letra e 1 numero

---

## 3. Endpoints de API envolvidos
### 3.1 Listar agencias
`GET /agencias/`

Query params:
- `skip` (default 0)
- `limit` (default 25)
- `search` (opcional)

Headers:
- `X-Total-Count`: total de agencias com filtros aplicados

Resposta (exemplo):
```json
[
  { "id": 1, "nome": "V3A", "dominio": "v3a.com.br" }
]
```

### 3.2 Criar usuario (cadastro)
`POST /usuarios/`

Body JSON (`UsuarioCreate`):
- `email` (string)
- `password` (string) - enviada em texto e hasheada no servidor
- `tipo_usuario` (`bb|npbb|agencia`)
- `matricula` (string, apenas BB)
- `agencia_id` (int, apenas Agencia)

Respostas:
- `201 Created`: retorna `UsuarioRead`
- `400 Bad Request`: erro de validacao (erro estruturado em `detail`)
- `409 Conflict`: email ja cadastrado (ex.: `EMAIL_ALREADY_REGISTERED`)

Formato de erro estruturado:
```json
{
  "detail": {
    "code": "EMAIL_ALREADY_REGISTERED",
    "message": "Email ja cadastrado",
    "field": "email"
  }
}
```

### 3.3 Login
`POST /auth/login` (ver `docs/auth.md`)

---

## 4. Notas de seguranca
- A senha nunca deve ser armazenada em texto puro: o backend deve persistir apenas o hash.
- Nao versionar credenciais em `.env`. Use `.env.example` com placeholders.

---

## 5. Backlog / futuras melhorias
- [ ] Confirmacao de email (ativacao de conta)
- [ ] Endpoint opcional `GET /usuarios/check-email?email=...` (para pre-validar cadastro)
- [ ] Politica de senha mais forte (regras e UX)
