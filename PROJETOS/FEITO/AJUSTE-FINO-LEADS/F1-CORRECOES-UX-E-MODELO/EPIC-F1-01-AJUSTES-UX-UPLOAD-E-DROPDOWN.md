---
doc_id: "EPIC-F1-01-AJUSTES-UX-UPLOAD-E-DROPDOWN"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# EPIC-F1-01 — Ajustes de UX no Upload e Dropdown de Eventos
**projeto:** AJUSTE-FINO-LEADS | **fase:** F1 | **status:** ✅

---
## 1. Resumo do Épico

Corrigir dois problemas de usabilidade identificados na sessão de revisão com a equipe de produto: (1) o campo `data_envio` do formulário de upload de batch não possui valor padrão, forçando preenchimento manual desnecessário; (2) o dropdown de seleção de evento no mapeamento de leads exibe apenas o nome, sem data, impossibilitando distinguir eventos homônimos.

## 2. Contexto Arquitetural

- Upload de batch: `POST /leads/batches` via `createLeadBatch()` em `frontend/src/services/leads_import.ts`
- Referência de eventos: `GET /leads/referencias/eventos` via `listReferenciaEventos()` em `frontend/src/services/leads_import.ts`
- Backend routers: `backend/app/routers/leads.py`
- Modelo de referência de eventos: serialização em `backend/app/schemas/` ou inline no router
- PYTHONPATH: `/workspace:/workspace/backend`

## 3. Riscos e Armadilhas

- Eventos sem `data_inicio_prevista` (NULL) não devem causar crash no dropdown — exibir apenas o nome
- A ordenação decrescente por data deve tratar NULLs (colocar ao final)
- O pré-preenchimento de `data_envio` não deve impedir edição manual

## 4. Definition of Done do Épico

- [ ] Campo `data_envio` pré-preenchido com data atual (`YYYY-MM-DD`) ao abrir formulário de upload
- [ ] Campo permanece editável pelo operador
- [ ] `POST /leads/batches` recebe `data_envio` correta mesmo sem edição manual
- [ ] Endpoint `GET /leads/referencias/eventos` retorna `data_inicio_prevista` em todos os itens
- [ ] Dropdown exibe `[Nome] — [DD/MM/YYYY]` em cada opção
- [ ] Eventos sem data exibem apenas o nome (sem erro)
- [ ] Ordenação por `data_inicio_prevista` decrescente como padrão
- [ ] CI verde sem regressão

---
## Issues

### AFL-F1-01-001 — Pré-preenchimento de `data_envio` no Formulário de Upload
**tipo:** fix | **sp:** 1 | **prioridade:** média | **status:** ✅
**depende de:** nenhuma

**User Story:**
Como operador de importação de leads, quero que o campo `data_envio` já venha preenchido com a data de hoje ao abrir o formulário de upload, para evitar preenchimento manual repetitivo.

**Plano TDD:**
- **Red:** Escrever teste em `frontend/src/pages/__tests__/ImportacaoPage.test.tsx` que verifica que o campo `data_envio` é renderizado com valor igual à data atual (`new Date().toISOString().slice(0, 10)`) ao montar o componente.
- **Green:** Inicializar o estado do campo `data_envio` com `new Date().toISOString().slice(0, 10)` na página de upload de batch.
- **Refactor:** Extrair lógica de data padrão para utilitário reutilizável se houver outros campos de data com comportamento semelhante.

**Critérios de Aceitação:**

- **Given** o formulário de upload de batch é aberto pela primeira vez
  **When** o componente é renderizado
  **Then** o campo `data_envio` exibe a data atual no formato `YYYY-MM-DD`

- **Given** o campo `data_envio` está pré-preenchido com a data atual
  **When** o operador altera manualmente a data para outro valor
  **Then** o valor alterado é enviado no `POST /leads/batches` ao submeter o formulário

**Tarefas:**
- [ ] T1: Localizar o componente do formulário de upload em `frontend/src/pages/` (provável `ImportacaoPage.tsx` ou similar)
- [ ] T2: Inicializar estado de `data_envio` com `new Date().toISOString().slice(0, 10)`
- [ ] T3: Verificar que o campo continua editável (controlled input)
- [ ] T4: Escrever teste unitário validando o pré-preenchimento

---

### AFL-F1-01-002 — Inclusão de `data_inicio_prevista` no Endpoint de Referência de Eventos
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** ✅
**depende de:** nenhuma

**User Story:**
Como operador de mapeamento de leads, quero que o endpoint de referência de eventos retorne a data de início de cada evento, para que o dropdown do frontend consiga exibir essa informação e distinguir eventos de mesmo nome.

**Plano TDD:**
- **Red:** Escrever teste em `backend/tests/test_leads_referencias.py` que chama `GET /leads/referencias/eventos` e verifica que cada item da resposta contém o campo `data_inicio_prevista` (string ISO ou null).
- **Green:** Alterar a query e o schema de resposta do endpoint para incluir `data_inicio_prevista` a partir da tabela de eventos. Adicionar ordenação por `data_inicio_prevista DESC NULLS LAST`.
- **Refactor:** Consolidar o schema de referência de evento em `backend/app/schemas/` se atualmente estiver definido inline no router.

**Critérios de Aceitação:**

- **Given** existem eventos com e sem `data_inicio_prevista` no banco
  **When** o frontend chama `GET /leads/referencias/eventos`
  **Then** a resposta contém `{id, nome, data_inicio_prevista}` para cada evento, com `data_inicio_prevista` null quando ausente

- **Given** existem 5 eventos com datas distintas
  **When** o endpoint é chamado sem parâmetros
  **Then** os eventos são retornados ordenados por `data_inicio_prevista` decrescente, com NULLs ao final

**Tarefas:**
- [ ] T1: Localizar o endpoint `GET /leads/referencias/eventos` em `backend/app/routers/leads.py`
- [ ] T2: Alterar query para incluir `data_inicio_prevista` do modelo de evento
- [ ] T3: Atualizar schema de resposta (criar ou estender em `backend/app/schemas/`)
- [ ] T4: Adicionar `ORDER BY data_inicio_prevista DESC NULLS LAST`
- [ ] T5: Escrever pytest validando presença do campo e ordenação

---

### AFL-F1-01-003 — Exibição de Data e Ordenação no Dropdown de Eventos
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** ✅
**depende de:** AFL-F1-01-002

**User Story:**
Como operador de mapeamento de leads, quero que o dropdown de seleção de evento exiba o nome do evento acompanhado da data de início, para que eu consiga distinguir eventos homônimos e escolher o correto.

**Plano TDD:**
- **Red:** Escrever teste em `frontend/src/pages/__tests__/MapeamentoPage.test.tsx` que mocka `listReferenciaEventos()` retornando eventos com `data_inicio_prevista` e verifica que o label de cada opção no dropdown segue o formato `Nome — DD/MM/YYYY`.
- **Green:** Atualizar o tipo de retorno de `listReferenciaEventos()` em `leads_import.ts` para incluir `data_inicio_prevista`. Alterar o componente de dropdown para formatar o label como `${nome} — ${formatDate(data_inicio_prevista)}`.
- **Refactor:** Extrair função `formatEventoLabel(nome, data)` para utils reutilizável.

**Critérios de Aceitação:**

- **Given** o dropdown de eventos é renderizado com dados do endpoint atualizado
  **When** um evento possui `data_inicio_prevista = "2025-05-15"`
  **Then** o label exibido é `[Nome do Evento] — 15/05/2025`

- **Given** um evento possui `data_inicio_prevista = null`
  **When** o dropdown é renderizado
  **Then** o label exibido é apenas o nome do evento, sem traço nem texto "null"

**Tarefas:**
- [ ] T1: Atualizar tipo `ReferenciaEvento` em `frontend/src/services/leads_import.ts` adicionando `data_inicio_prevista: string | null`
- [ ] T2: Criar função `formatEventoLabel(nome: string, data: string | null): string` em utils
- [ ] T3: Atualizar componente de dropdown no fluxo de mapeamento para usar o novo label
- [ ] T4: Escrever teste unitário com mock de dados (evento com data, evento sem data)

## 5. Artifact Mínimo do Épico

`artifacts/ajuste-fino-leads/phase-f1/epic-f1-01-ux-evidence.md` — screenshot ou log demonstrando data preenchida e dropdown com datas visíveis.

## 6. Dependências

- [PRD Refino Leads v2](../PRD_Refino_Leads_v2.md) — Seções 3.1 e 3.2
- [GOV-SCRUM](../../../../COMUM/GOV-SCRUM.md)
- [GOV-DECISOES](../../../../COMUM/GOV-DECISOES.md)
