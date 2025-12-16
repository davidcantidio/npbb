# Tela: Novo Usuário / Cadastro de Conta

Tela onde um usuário se registra no sistema, escolhendo seu tipo e preenchendo os campos obrigatórios conforme regras de negócio.

## 1. Nome da Tela

**Novo Usuário / Cadastro de Conta**

## 2. Referência Visual

* Estado esperado da tela: cadastro em branco
* Padrão: **Material Design 3**
* Desenho conceitual inspirado no padrão de login já existente no sistema

---

## 3. Estrutura da Tela

### 3.1 Navegação / Header

* Tela independente (página de acesso público, sem navegação lateral)
* Logo do sistema no topo centralizado
* Título da página: **Criar nova conta**

### 3.2 Formulário de Cadastro

| Ordem | Campo                 | Tipo/Componente    | Obrigatório           | Observações                                                          |
| ----- | --------------------- | ------------------ | --------------------- | -------------------------------------------------------------------- |
| 1     | Tipo de usuário       | Radio group        | Sim                   | Opções: Funcionário BB / Funcionário NPBB / Funcionário Agência      |
| 2     | Email                 | Text input (email) | Sim                   | Validação por tipo (ver regras abaixo)                               |
| 3     | Senha                 | Password           | Sim                   | Campo protegido com política mínima                                  |
| 4     | Confirmar senha       | Password           | Sim                   | Deve coincidir com o campo Senha                                     |
| 5     | Matrícula BB          | Text input         | Condicional (BB)      | Apenas para Funcionário BB – alfanumérica (1 letra + até 16 números) |
| 6     | Agência               | Dropdown           | Condicional (Agência) | Apenas para Funcionário Agência – carregado via API                  |
| 7     | Botão **Criar Conta** | Button             | Sim                   | Desabilitado até que todas as validações estejam OK                  |

---

## 4. Comportamento da Tela

### 4.1 Interação por Tipo de Usuário

| Tipo Selecionado    | Campos Habilitados                          | Validações Aplicadas                                                             |
| ------------------- | ------------------------------------------- | -------------------------------------------------------------------------------- |
| Funcionário BB      | Email, Senha, Confirmar Senha, Matrícula BB | Email deve terminar com `@bb.com.br`<br>Matrícula: regex `^[A-Za-z][0-9]{1,16}$` |
| Funcionário NPBB    | Email, Senha, Confirmar Senha               | Email deve terminar com `@npbb.com.br`                                           |
| Funcionário Agência | Email, Senha, Confirmar Senha, Agência      | Email deve ser do domínio da agência selecionada (`agencia.dominio`)<br>Agência deve ser selecionada                |

### 4.2 Validações Dinâmicas

O botão **Criar Conta** só é habilitado quando **TODAS** as condições abaixo forem verdadeiras:

* Email com formato válido
* Senha e Confirmação de senha coincidem
* Senha atende à política mínima (letras + números, mínimo 6 caracteres)
* Domínio do email respeita a regra do tipo selecionado
* Matrícula BB no formato correto (quando aplicável)
* Agência selecionada (quando aplicável)

Feedback visual de erro em tempo real para:

* Email inválido
* Email fora do domínio esperado
* Senhas não coincidem
* Senha fora da política mínima
* Matrícula em formato inválido
* Agência não selecionada

---

## 5. Regras de Negócio

| Regra                                  | Detalhe                                                                         |
| -------------------------------------- | ------------------------------------------------------------------------------- |
| Domínio de email – Funcionário BB      | Deve terminar com `@bb.com.br`                                                  |
| Domínio de email – Funcionário NPBB    | Deve terminar com `@npbb.com.br`                                                |
| Domínio de email – Funcionário Agência | Deve corresponder ao domínio da agência selecionada (`agencia.dominio`, ex.: `v3a.com.br`) |
| Matrícula BB                           | 1 letra + até 16 números (regex `^[A-Za-z][0-9]{1,16}$`)                        |
| Política de Senha                      | Mínimo 6 caracteres, ao menos 1 letra e 1 número (regex mínima abaixo)          |
| Seleção de agência                     | Obrigatória apenas para tipo “Funcionário Agência”<br>Lista via GET `/agencias/` (dropdown mostra apenas o nome; domínio usado para validação) |
| Submissão                              | Bloqueada até que todas as validações client-side estejam OK                    |

---

## 6. Validação em Código (Frontend)

```ts
// Email
const isValidEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
const hasCorrectDomain = (email: string, type: UserType, agenciaDominio?: string) => {
  if (type === 'BB') return email.endsWith('@bb.com.br');
  if (type === 'NPBB') return email.endsWith('@npbb.com.br');
  if (type === 'AGENCIA') {
    const emailDomain = email.split('@').pop()?.toLowerCase();
    const domain = (agenciaDominio || '').toLowerCase().replace(/^@/, '');
    return Boolean(emailDomain && domain && (emailDomain === domain || emailDomain.endsWith(`.${domain}`)));
  }
  return true;
};

// Matrícula BB
const isValidMatriculaBB = (matricula: string) => /^[A-Za-z][0-9]{1,16}$/.test(matricula);

// Política de Senha (mínimo 6 chars com letra e número)
const isValidPassword = (password: string) =>
  /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/.test(password);
```

---

## 7. Chamadas de API Relevantes

| Ação                       | Endpoint                          | Método | Notas                                        |
| -------------------------- | --------------------------------- | ------ | -------------------------------------------- |
| Buscar agências            | `/agencias/`                      | GET    | Suporta `skip`, `limit`, `search` e retorna `X-Total-Count`; resposta inclui `{ id, nome, dominio }` (dominio não aparece no dropdown) |
| Verificar email (opcional) | `/usuarios/check-email?email=...` | GET    | Não implementado (futuro)                    |
| Criar usuário              | `/usuarios/`                      | POST   | Body `UsuarioCreate` (`email`, `password`, `tipo_usuario`=`bb|npbb|agencia`, `matricula`/`agencia_id`); senha enviada em texto e hasheada no servidor |

### 7.1 Formato de erros (backend)
- Login (`/auth/login`) retorna erro simples: `{"detail":"Credenciais invalidas"}` (401).
- Cadastro (`/usuarios/`) retorna erros estruturados (400/409) em `detail`:
  ```json
  {"detail":{"code":"EMAIL_ALREADY_REGISTERED","message":"Email ja cadastrado","field":"email"}}
  ```

---

## 8. Diferenças – Sistema Original × Nova Versão

| Item                    | Sistema Original | Nova Versão                   |
| ----------------------- | ---------------- | ----------------------------- |
| Tela de cadastro        | Não presente     | Nova tela de registro         |
| Tipos de usuário        | Único            | BB / NPBB / Agência           |
| Validação por tipo      | Não existia      | Regras de domínio por tipo    |
| Integração com agências | Não existente    | Dropdown carregado do backend |

---

## 9. Pendências / Dúvidas

* Haverá verificação por e-mail (link de ativação) para confirmar usuário após cadastro?
* A matrícula de funcionário interno (BB/NPBB) deve ser validada contra base existente de funcionários?
* Funcionário de agência poderá ter vínculo com múltiplas agências no futuro?

---

## 10. Backlog da Tela (Requisitos)

### Backend

* [x] `GET /agencias/` -> retorna lista de agências (`id`, `nome`, `dominio`)
* [x] `POST /usuarios/` -> cria usuário com validações server-side:

  * Domínio de email conforme tipo (BB/NPBB) ou agência selecionada (`agencia.dominio`)
  * Formato da matrícula BB
  * Política de senha mínima (letras+ números; >=6)
* [x] Erros claros (400/409) com mensagens específicas

### Frontend

* [x] Componente de cadastro (rota `/novo-usuario`)
* [x] Campos dinâmicos conforme tipo de usuário selecionado
* [x] Validações em tempo real (client-side)
* [x] Feedback visual de erro imediato
* [x] Botão de submissão habilitado apenas com formulário válido
* [x] Integração com `GET /agencias/` e `POST /usuarios/`
