# PRD — LP (QR por Ativação)
**Landing Pages — QR-code por Ativação, Fluxo CPF-first e Reconhecimento de Leads**

| | |
|---|---|
| **Versão** | 1.0 |
| **Data** | Março 2026 |
| **Status** | draft |
| **Origem do Intake** | [INTAKE-LP-QR-ATIVACOES.md](./INTAKE-LP-QR-ATIVACOES.md) |
| **Projeto** | LP |
| **Log de Auditoria** | [AUDIT-LOG.md](./AUDIT-LOG.md) |

---

## 1. Objetivo e Contexto

Este documento especifica os requisitos para a nova mecânica de **QR-code por ativação**, fluxo **CPF-first** e **reconhecimento de leads** entre ativações no mesmo evento. Cada ativação terá seu próprio QR-code; o visitante valida CPF na primeira vez e, em ativações subsequentes do mesmo evento, é reconhecido automaticamente, com cada escaneada registrando uma conversão.

> **Problema a resolver:** Não existe conceito de ativação com QR próprio; não há fluxo CPF-first nem reconhecimento de leads entre pontos de contato no mesmo evento; conversões não são atribuídas por ativação. A página atual de formulário de leads não contempla ativações nem QR-codes.

### 1.1 Tese

Cada ativação de um evento terá seu próprio QR-code; o visitante acessa via QR, valida CPF na primeira vez e, em ativações subsequentes no mesmo evento, é reconhecido automaticamente, com cada escaneada registrando uma conversão.

### 1.2 Valor Esperado

- **Rastreabilidade por ativação:** cada QR mapeia para uma ativação e permite medir conversões por ponto de contato.
- **Experiência fluida:** lead reconhecido não repete CPF em novas ativações do mesmo evento.
- **Flexibilidade:** ativações podem permitir conversão única ou múltipla, com opção de registrar outro CPF quando alguém usa o celular para converter terceiros.

---

## 2. Escopo

### 2.1 Dentro do Escopo

| Item | Descrição |
|---|---|
| Modelo de dados | Ativação (vínculo com evento, QR único, flag conversão única/múltipla) |
| Geração de QR | QR-code único por ativação |
| Fluxo CPF-first | Landing exibe apenas CPF no primeiro acesso; validação de dígito verificador |
| Reconhecimento de lead | Entre ativações do mesmo evento (cookie/session/token) |
| Registro de conversão | Por ativação |
| Opção "Registrar outro CPF" | Em ativação de conversão única quando o lead já converteu |
| Bloqueio de CPF duplicado | Em ativação de conversão única |

### 2.2 Fora do Escopo

| Item | Motivo |
|---|---|
| Validação de CPF contra base externa (Receita Federal) | Apenas validação algorítmica do dígito verificador |
| Integração com sistemas de impressão de QR | Fora de escopo inicial |
| Alteração do modelo de eventos | Apenas o necessário para ativações |
| Suporte a múltiplos eventos no mesmo fluxo de reconhecimento | Escopo inicial: mesmo evento |
| Redesenho completo do formulário de leads | Além do fluxo CPF-first |

---

## 3. Público e Operadores

| Papel | Descrição |
|---|---|
| **Usuário principal** | Visitante que escaneia o QR da ativação e preenche o formulário de lead |
| **Usuário secundário** | Operador que configura ativações (QR, tipo de conversão única/múltipla) e visualiza conversões por ativação |
| **Operador interno** | Equipe de marketing/eventos |

---

## 4. Fluxo Principal

1. **Operador** cria ativações para o evento; cada ativação gera um QR-code único.
2. **Visitante** escaneia QR da ativação → é direcionado à landing page.
3. **Primeiro acesso (não reconhecido):** vê apenas o campo CPF. Preenche CPF → validação do dígito verificador.
4. Se CPF válido → exibe o restante dos campos do formulário de lead configurado; preenche e submete → conversão registrada na ativação.
5. **Acesso subsequente (mesmo lead, outra ativação no mesmo evento):** sistema reconhece o lead → não exige CPF novamente; exibe diretamente o formulário completo ou confirmação de conversão conforme regra da ativação.
6. Cada escaneada com CPF válido registra uma conversão na ativação correspondente.
7. **Ativação com conversão única:** se o lead já converteu nessa ativação → oferece opção "Registrar outro CPF" (caso use o celular para converter outra pessoa).
8. **Barreira:** se a pessoa tentar cadastrar para outro mas informar o próprio CPF novamente em ativação de conversão única → sistema barra (CPF já convertido nessa ativação).

---

## 5. Decisões de Implementação (Respostas às Lacunas do Intake)

### 5.1 Mecanismo de Reconhecimento

**Decisão:** Cookie HTTP-only emitido pelo backend + token opcional na URL para fallback.

- **Cookie:** `lp_lead_token` com valor opaco (hash ou UUID) vinculado ao `lead_id` + `evento_id`; TTL de 7 dias; emitido via `Set-Cookie` pelo backend para o domínio da aplicação.
- **Fallback:** parâmetro `?token=` na URL quando o visitante compartilha o link (ex.: WhatsApp) — token de uso único ou de curta validade.
- **Persistência:** 7 dias — suficiente para eventos multi-dia; respeita LGPD (não armazena CPF no cookie).

### 5.2 Estrutura de URL do QR

**Decisão:** `/eventos/:evento_id/ativacoes/:ativacao_id` (ou `/e/:evento_id/a/:ativacao_id` para URLs mais curtas).

- O QR aponta para essa URL; o frontend carrega a landing com contexto de evento e ativação.
- Query params opcionais: `?token=` para reconhecimento via link compartilhado.

### 5.3 Opção "Registrar outro CPF"

**Decisão:** Exibida como link/botão secundário abaixo da mensagem de sucesso ("Você já se cadastrou nesta ativação") quando:
- ativação tem conversão única;
- lead já converteu nessa ativação;
- lead está reconhecido (cookie/token presente).

**Copy sugerido:** "Cadastrar outra pessoa" ou "Registrar outro CPF".

**Fluxo:** ao clicar, limpa o estado de "já converteu nesta ativação" para a sessão atual e exibe novamente o campo CPF; o novo CPF submetido registra nova conversão na mesma ativação (conversão múltipla implícita para esse caso de uso).

### 5.4 Ativação Múltipla — Lead Reconhecido

**Decisão:** Lead reconhecido em ativação múltipla vai **diretamente para o formulário completo** (sem repetir CPF). Preenche os demais campos e submete → nova conversão registrada na ativação.

### 5.5 Definição de "Primeiro Acesso" vs. "Reconhecido"

**Critério técnico:**
- **Reconhecido:** cookie `lp_lead_token` presente e válido (não expirado) OU token na URL válido; e o lead associado já converteu em pelo menos uma ativação do evento.
- **Primeiro acesso:** ausência de cookie/token válido OU lead nunca converteu em nenhuma ativação do evento.

---

## 6. Modelo de Dados

### 6.1 Tabela `ativacao`

| Campo | Tipo | Nullable | Descrição |
|---|---|---|---|
| `id` | INTEGER PK | não | Identificador único |
| `evento_id` | INTEGER FK | não | Evento ao qual a ativação pertence |
| `nome` | VARCHAR | não | Nome da ativação (ex.: "Stand Principal") |
| `descricao` | TEXT | sim | Descrição opcional |
| `conversao_unica` | BOOLEAN | não | `true` = uma conversão por CPF; `false` = múltiplas |
| `qr_code_url` | VARCHAR | sim | URL do QR (ou path para imagem gerada) |
| `created_at` | TIMESTAMP | não | Data de criação |
| `updated_at` | TIMESTAMP | não | Data de atualização |

### 6.2 Tabela `conversao_ativacao` (ou extensão de modelo existente)

| Campo | Tipo | Nullable | Descrição |
|---|---|---|---|
| `id` | INTEGER PK | não | Identificador único |
| `ativacao_id` | INTEGER FK | não | Ativação |
| `lead_id` | INTEGER FK | não | Lead que converteu |
| `cpf` | VARCHAR | não | CPF (para bloqueio em conversão única) |
| `created_at` | TIMESTAMP | não | Data da conversão |

**Índice composto:** `(ativacao_id, cpf)` para lookup rápido de "CPF já converteu nesta ativação?".

### 6.3 Token de Reconhecimento

- Armazenado em tabela `lead_reconhecimento_token` ou similar: `lead_id`, `evento_id`, `token_hash`, `expires_at`.
- Cookie armazena apenas o token opaco; o backend valida e associa ao lead.

---

## 7. Arquitetura Afetada

### 7.1 Backend

- Novo modelo `Ativacao`; endpoints para CRUD de ativações (operador).
- Endpoint `GET /eventos/:id/ativacoes/:ativacao_id/landing` — payload da landing com contexto de ativação.
- Endpoint `POST /leads/` — extensão para receber `ativacao_id`, validar CPF (dígito), registrar conversão, retornar token de reconhecimento e emitir `Set-Cookie` para `lp_lead_token`.
- Endpoint `GET /leads/reconhecer?token=` — valida token e retorna se lead está reconhecido para o evento.
- Geração de QR: serviço que gera imagem ou URL do QR (lib como `qrcode` em Python ou endpoint que retorna SVG/PNG).

### 7.2 Frontend

- Nova rota `/eventos/:evento_id/ativacoes/:ativacao_id` (ou equivalente).
- Landing com fluxo CPF-first: estado inicial mostra apenas CPF; após validação, exibe formulário completo.
- Lógica de reconhecimento: ao carregar, encaminha `?token=` quando presente e depende do cookie `lp_lead_token` já emitido pelo backend; se reconhecido, pula etapa CPF.
- Opção "Registrar outro CPF" na ativação de conversão única.
- Tratamento de bloqueio: mensagem clara quando CPF duplicado em ativação única.

### 7.3 Banco / Migrações

- Tabela `ativacao`; tabela `conversao_ativacao` (ou `ativacao_lead` se já existir conceito similar).
- Tabela `lead_reconhecimento_token` para tokens de sessão.
- Índices para lookup por `(ativacao_id, cpf)` e por `token_hash`.

### 7.4 Autorização / Autenticação

- Landing pública para preenchimento (sem login).
- Token de reconhecimento no cookie/URL — validado pelo backend em cada requisição relevante.
- CRUD de ativações: requer autenticação de operador.

---

## 8. Contrato de API (Resumo)

### 8.1 GET `/eventos/:evento_id/ativacoes/:ativacao_id/landing`

Retorna payload da landing com: evento, ativação, formulário configurado, template. Inclui flag `lead_reconhecido` quando cookie/token válido presente.

### 8.2 POST `/leads/`

**Request (extensão):**
- `ativacao_id` (obrigatório quando acesso via ativação)
- `cpf` (obrigatório no primeiro acesso)
- Demais campos do formulário

**Response (extensão):**
- `token_reconhecimento` — valor opaco retornado junto com `Set-Cookie: lp_lead_token=...`; a persistência do cookie é responsabilidade do backend
- `lead_reconhecido` — boolean
- `conversao_registrada` — boolean
- `bloqueado_cpf_duplicado` — boolean (quando aplicável)

### 8.3 Validação de CPF

- Apenas dígito verificador (algoritmo padrão). Sem consulta a base externa.

---

## 9. Resultado de Negócio e Métricas

### 9.1 Objetivo Principal

Atribuição de conversões por ativação e experiência fluida para leads recorrentes.

### 9.2 Métricas Leading

- Número de ativações por evento
- Conversões por ativação
- Taxa de reconhecimento de leads

### 9.3 Métricas Lagging

- Aumento de conversões atribuíveis
- Redução de abandono por repetição de CPF

### 9.4 Critério Mínimo de Sucesso

1. Cada ativação tem QR único
2. Fluxo CPF-first com validação
3. Lead reconhecido não repete CPF
4. Conversões registradas por ativação
5. Ativação única/múltipla funcionando
6. Bloqueio de CPF duplicado em ativação única

---

## 10. Restrições e Guardrails

| Tipo | Restrição |
|---|---|
| **Técnica** | Validação de CPF apenas por dígito verificador; mecanismo de reconhecimento deve respeitar privacidade e LGPD |
| **Legal/Compliance** | CPF é dado sensível (LGPD); armazenamento e tratamento conforme política de dados |
| **Produto** | Não validar CPF contra Receita Federal; não suportar múltiplos eventos no mesmo fluxo de reconhecimento (v1) |

---

## 11. Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| **Reconhecimento falha** (cross-device, privacidade) | Cookie com TTL de 7 dias; fallback com token na URL; documentar limitação |
| **CPF válido mas inexistente** | Aceitar como trade-off; validação Receita Federal fora de escopo |
| **Burlar bloqueio** (limpar cookies) | Aceitar como limitação conhecida; possível mitigação futura com fingerprinting (fora de escopo) |
| **CPF sensível (LGPD)** | Criptografia em repouso; mínimo de retenção; política de dados documentada |
| **Fricção no primeiro acesso** | UX clara; mensagem explicando que CPF é só na primeira vez |

---

## 12. Fatiamento por Fases

### Fase 1 — Fundação (Modelo e Backend)

- Modelo `Ativacao` e migração
- Tabela `conversao_ativacao` (ou equivalente)
- CRUD de ativações (operador)
- Geração de QR por ativação
- Endpoint de landing com contexto de ativação

### Fase 2 — Fluxo CPF-first e Conversão

- Fluxo CPF-first na landing (primeiro acesso)
- Validação de dígito verificador
- Registro de conversão por ativação
- Bloqueio de CPF duplicado em ativação de conversão única

### Fase 3 — Reconhecimento e Experiência Fluida

- Mecanismo de reconhecimento (cookie + token)
- Lead reconhecido pula CPF
- Ativação múltipla: formulário direto
- Ativação única: opção "Registrar outro CPF"

### Fase 4 — Operador e Métricas

- Interface de configuração de ativações (QR, tipo de conversão)
- Visualização de conversões por ativação
- Métricas e observabilidade

---

## 13. Critérios de Aceite — v1.0

### 13.1 Modelo e Ativações

- [ ] Tabela `ativacao` criada com migration
- [ ] Tabela `conversao_ativacao` (ou equivalente) criada
- [ ] Cada ativação gera QR-code único
- [ ] Operador pode criar/editar ativações com flag conversão única/múltipla

### 13.2 Fluxo CPF-first

- [ ] Primeiro acesso exibe apenas campo CPF
- [ ] Validação de dígito verificador antes de exibir formulário completo
- [ ] CPF inválido exibe mensagem de erro clara

### 13.3 Reconhecimento

- [ ] Lead reconhecido (cookie/token) não repete CPF em nova ativação do mesmo evento
- [ ] Token de reconhecimento retornado no submit e cookie `lp_lead_token` emitido via `Set-Cookie`

### 13.4 Conversão por Ativação

- [ ] Cada submit com CPF válido registra conversão na ativação correspondente
- [ ] Ativação única: bloqueio ao tentar cadastrar mesmo CPF novamente
- [ ] Ativação única: opção "Registrar outro CPF" quando lead já converteu

### 13.5 URL e QR

- [ ] URL do QR segue estrutura `/eventos/:id/ativacoes/:ativacao_id` (ou equivalente)
- [ ] Landing carrega com contexto correto de evento e ativação

---

## 14. Fora do Escopo — v1.0

- Validação de CPF contra base da Receita Federal
- Suporte a múltiplos eventos no mesmo fluxo de reconhecimento
- Redesenho completo do formulário de leads além do fluxo CPF-first
- Integração com sistemas de impressão de QR
- Fingerprinting para mitigar burla de bloqueio por limpeza de cookies

---

## 15. Referências

- **Intake de origem:** [INTAKE-LP-QR-ATIVACOES.md](./INTAKE-LP-QR-ATIVACOES.md)
- **Governança:** [PROJETOS/COMUM/GOV-INTAKE.md](../COMUM/GOV-INTAKE.md)
- **Formulário de leads atual:** `http://127.0.0.1:5173/eventos/111/formulario-lead`

---

*LP · PRD QR por Ativação v1.0 · Março 2026*
