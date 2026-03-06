---
doc_id: "EPIC-F2-01-MODAL-CRIACAO-RAPIDA-EVENTO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# EPIC-F2-01 — Modal de Criação Rápida de Evento no Mapeamento
**projeto:** AJUSTE-FINO-LEADS | **fase:** F2 | **status:** ✅

---
## 1. Resumo do Épico

Implementar um modal de criação rápida de evento acessível diretamente do dropdown de seleção de evento durante o fluxo de mapeamento de leads. Quando o operador pesquisa um evento que não existe, uma opção especial "Criar evento rapidamente" aparece. Ao clicar, um modal com formulário mínimo é exibido. Após salvar via `POST /evento/`, o evento é automaticamente selecionado e a lista de referências recarregada.

## 2. Contexto Arquitetural

- Dropdown de eventos no fluxo de mapeamento: `frontend/src/pages/leads/MapeamentoPage.tsx` (ou componente equivalente)
- Endpoint de criação: `POST /evento/` — já funcional (confirmado por smoke tests em `leads-evento.api.smoke.spec.ts`)
- Catálogo de diretorias: `GET /evento/all/diretorias`
- Referência de eventos: `GET /leads/referencias/eventos` via `listReferenciaEventos()`
- MUI Components: Autocomplete, Dialog, TextField, Select

## 3. Riscos e Armadilhas

- O campo `diretoria_id` é obrigatório na API `POST /evento/` — o modal deve carregar o catálogo de diretorias
- Se o `POST /evento/` falhar, o estado do mapeamento em andamento não pode ser perdido (campos já preenchidos devem permanecer)
- A opção "Criar evento rapidamente" deve aparecer apenas quando a busca não encontra resultados, sem poluir o dropdown em condições normais

## 4. Definition of Done do Épico

- [ ] Opção "Criar evento rapidamente" visível no Autocomplete/Select de eventos quando filtro não retorna resultados
- [ ] Modal `QuickCreateEventoModal` exibe os 5 campos essenciais: `nome`, `data_inicio_prevista`, `cidade`, `estado`, `diretoria_id`
- [ ] `diretoria_id` carregado dinamicamente de `GET /evento/all/diretorias`
- [ ] `POST /evento/` chamado com sucesso e evento selecionado automaticamente no dropdown
- [ ] `listReferenciaEventos()` recarregado após criação para atualizar lista
- [ ] Erro de criação exibe toast/mensagem sem perder estado do mapeamento
- [ ] Evento criado visível na listagem completa em `/eventos`
- [ ] CI verde sem regressão

---
## Issues

### AFL-F2-01-001 — Componente QuickCreateEventoModal
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** ✅
**depende de:** nenhuma

**User Story:**
Como operador de mapeamento de leads, quero um modal com formulário mínimo para criar um evento rapidamente, para que eu não precise sair do fluxo de mapeamento quando o evento ainda não existe no sistema.

**Plano TDD:**
- **Red:** Escrever teste em `frontend/src/components/__tests__/QuickCreateEventoModal.test.tsx` que renderiza o modal com props `open=true` e verifica a presença dos 5 campos obrigatórios (`nome`, `data_inicio_prevista`, `cidade`, `estado`, `diretoria_id`) e dos botões "Cancelar" e "Salvar".
- **Green:** Criar componente `frontend/src/components/QuickCreateEventoModal.tsx` com MUI Dialog, 5 campos e lógica de submit via `POST /evento/`. Carregar diretorias de `GET /evento/all/diretorias` ao abrir.
- **Refactor:** Extrair validação de formulário para hook `useQuickCreateEvento` se a complexidade justificar.

**Critérios de Aceitação:**

- **Given** o modal `QuickCreateEventoModal` é aberto com `open=true`
  **When** o componente é renderizado
  **Then** os 5 campos obrigatórios (`nome`, `data_inicio_prevista`, `cidade`, `estado`, `diretoria_id`) estão visíveis e editáveis

- **Given** o operador preenche todos os campos obrigatórios e clica "Salvar"
  **When** `POST /evento/` retorna sucesso com o evento criado
  **Then** o callback `onCreated(evento)` é chamado com os dados do evento e o modal fecha

- **Given** o operador clica "Salvar" sem preencher `nome`
  **When** a validação do formulário é executada
  **Then** uma mensagem de erro é exibida no campo `nome` e o submit é bloqueado

**Tarefas:**
- [ ] T1: Criar `frontend/src/components/QuickCreateEventoModal.tsx` com MUI Dialog
- [ ] T2: Implementar formulário com 5 campos (TextField para `nome`, `cidade`; DatePicker ou TextField type=date para `data_inicio_prevista`; Select de UFs para `estado`; Select dinâmico para `diretoria_id`)
- [ ] T3: Implementar chamada `GET /evento/all/diretorias` ao abrir (useEffect)
- [ ] T4: Implementar submit via `POST /evento/` com loading state e tratamento de erro
- [ ] T5: Escrever teste unitário do componente

**Notas técnicas:**
O `estado` deve ser um Select com as 27 UFs brasileiras. O `concorrencia` tem default `false` no backend, não precisa aparecer no modal. O campo `data_inicio_prevista` deve enviar no formato `YYYY-MM-DD`.

---

### AFL-F2-01-002 — Integração do Modal com Dropdown de Mapeamento
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** ✅
**depende de:** AFL-F2-01-001

**User Story:**
Como operador de mapeamento de leads, quero que a opção "Criar evento rapidamente" apareça automaticamente no dropdown de eventos quando minha busca não encontra resultados, para que eu possa criar o evento sem sair do fluxo de mapeamento.

**Plano TDD:**
- **Red:** Escrever teste em `frontend/src/pages/__tests__/MapeamentoPage.test.tsx` que mocka `listReferenciaEventos()` retornando lista vazia, digita texto no Autocomplete e verifica que a opção "Criar evento rapidamente" aparece. Clicar nela deve abrir o modal.
- **Green:** Adicionar lógica de "opção especial" no Autocomplete de evento na página de mapeamento. Quando `filterOptions` retorna lista vazia, adicionar item sintético `{ id: -1, nome: "+ Criar evento rapidamente" }`. Ao selecionar, abrir `QuickCreateEventoModal`. No callback `onCreated`, definir o evento no estado e recarregar `listReferenciaEventos()`.
- **Refactor:** Consolidar a lógica de opção especial em hook reutilizável `useEventoAutocompleteWithCreate` se o padrão for necessário em outros pontos.

**Critérios de Aceitação:**

- **Given** o operador digita "Workshop XYZ" no Autocomplete de eventos
  **When** nenhum evento corresponde à busca
  **Then** uma opção "+ Criar evento rapidamente" aparece no dropdown

- **Given** o operador clica em "+ Criar evento rapidamente" e preenche o modal
  **When** o evento é criado com sucesso via `POST /evento/`
  **Then** o evento recém-criado é automaticamente selecionado no dropdown e a lista de referências é atualizada

- **Given** o operador já preencheu parcialmente o mapeamento de colunas
  **When** ocorre um erro na criação do evento (ex: nome duplicado)
  **Then** o mapeamento parcial é preservado, o modal exibe a mensagem de erro e o operador pode corrigir ou cancelar

**Tarefas:**
- [ ] T1: Localizar o Autocomplete de evento na página de mapeamento
- [ ] T2: Adicionar lógica de `filterOptions` com item especial "Criar evento rapidamente" quando lista filtrada está vazia
- [ ] T3: Gerenciar estado `isQuickCreateOpen` para abrir/fechar o modal
- [ ] T4: No callback `onCreated`, definir o evento selecionado e chamar `listReferenciaEventos()` novamente
- [ ] T5: Escrever teste de integração com mock de API

## 5. Artifact Mínimo do Épico

`artifacts/ajuste-fino-leads/phase-f2/epic-f2-01-quick-create-evidence.md` — screenshot do dropdown com opção "Criar evento rapidamente" e do modal funcional.

## 6. Dependências

- [PRD Refino Leads v2](../PRD_Refino_Leads_v2.md) — Seção 3.4
- [SCRUM-GOV](../../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../../COMUM/DECISION-PROTOCOL.md)
- F1 concluída (dropdown de eventos com data — EPIC-F1-01)
