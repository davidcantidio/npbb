---
doc_id: "EPIC-F3-02-UI-EXPORTACAO-DASHBOARD"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# EPIC-F3-02 — Interface de Exportação no Dashboard
**projeto:** AJUSTE-FINO-LEADS | **fase:** F3 | **status:** ✅

---
## 1. Resumo do Épico

Implementar no `DashboardLeads.tsx` o botão "Exportar Leads Ouro", o modal de configuração de exportação (seleção de evento e formato) e a lógica de download via Blob URL. O serviço frontend `exportLeadsGold()` consome o endpoint `GET /leads/export/gold` e dispara o download automático do arquivo.

## 2. Contexto Arquitetural

- Dashboard de Leads: `frontend/src/pages/DashboardLeads.tsx`
- Serviços de leads: `frontend/src/services/leads_import.ts` (ou novo `leads_export.ts`)
- Autocomplete de eventos: componente já utilizado no filtro do Dashboard
- Download via Blob: `URL.createObjectURL(blob)` com link `<a>` temporário
- MUI Components: Button, Dialog, Autocomplete, RadioGroup, CircularProgress

## 3. Riscos e Armadilhas

- Arquivos grandes podem demorar para baixar — exibir loading indicator durante a geração
- O Autocomplete de eventos deve reutilizar o mesmo datasource do filtro existente no Dashboard
- HTTP 204 (sem leads) deve ser tratado como caso válido: exibir toast informativo, não erro
- O download via Blob pode falhar em navegadores com política de segurança restritiva — testar em Chrome e Firefox

## 4. Definition of Done do Épico

- [ ] Botão "Exportar Leads Ouro" visível no `DashboardLeads.tsx`
- [ ] Modal de exportação com seleção de evento (+ opção "Todos") e formato (xlsx/csv)
- [ ] Serviço `exportLeadsGold()` no frontend consumindo `GET /leads/export/gold`
- [ ] Download automático via Blob URL com nome de arquivo correto
- [ ] Loading state durante geração do arquivo
- [ ] Toast informativo quando nenhum lead Gold é encontrado (HTTP 204)
- [ ] CI verde sem regressão

---
## Issues

### AFL-F3-02-001 — Serviço Frontend de Exportação e Download via Blob
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** ✅
**depende de:** AFL-F3-01-002 (endpoint disponível)

**User Story:**
Como desenvolvedor frontend, quero um serviço que chame o endpoint de exportação Gold e dispare o download automático do arquivo, para que o componente de UI do Dashboard possa simplesmente chamar uma função sem lidar com detalhes de Blob e Content-Disposition.

**Plano TDD:**
- **Red:** Escrever teste em `frontend/src/services/__tests__/leads_export.test.ts` que mocka `fetch` retornando um Blob com status 200 e verifica que `exportLeadsGold(token, {formato: "xlsx"})` retorna o Blob. Testar que status 204 retorna `null`. Testar que `triggerBlobDownload(blob, filename)` cria e clica um `<a>` temporário.
- **Green:** Criar `frontend/src/services/leads_export.ts` com `exportLeadsGold(token, params)` que faz fetch com `responseType: blob`. Criar função `triggerBlobDownload(blob, filename)` que usa `URL.createObjectURL`.
- **Refactor:** Consolidar headers de autenticação com helper já existente em `leads_import.ts`.

**Critérios de Aceitação:**

- **Given** o endpoint `GET /leads/export/gold` retorna status 200 com corpo binário
  **When** `exportLeadsGold(token, {formato: "xlsx"})` é chamado
  **Then** a função retorna um `Blob` com os bytes do arquivo

- **Given** o endpoint retorna status 204 (sem corpo)
  **When** `exportLeadsGold(token, {})` é chamado
  **Then** a função retorna `null`

- **Given** um Blob válido e um filename
  **When** `triggerBlobDownload(blob, "leads_ouro_todos_2026-03-06.xlsx")` é chamado
  **Then** um elemento `<a>` temporário é criado com `href=objectURL` e `download=filename`, é clicado e removido do DOM

**Tarefas:**
- [ ] T1: Criar `frontend/src/services/leads_export.ts`
- [ ] T2: Implementar `exportLeadsGold(token, params)` com fetch e tratamento de 200/204
- [ ] T3: Implementar `triggerBlobDownload(blob, filename)` com `URL.createObjectURL`
- [ ] T4: Extrair filename do header `Content-Disposition` da resposta (fallback para nome padrão)
- [ ] T5: Escrever testes unitários com mock de fetch

---

### AFL-F3-02-002 — Botão e Modal de Exportação no DashboardLeads
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** ✅
**depende de:** AFL-F3-02-001

**User Story:**
Como operador do Dashboard de Leads, quero um botão "Exportar Leads Ouro" que abre um modal onde posso selecionar o evento e o formato de exportação, para que eu consiga extrair os dados tratados dos leads Gold de forma simples e direta.

**Plano TDD:**
- **Red:** Escrever teste em `frontend/src/pages/__tests__/DashboardLeads.export.test.tsx` que renderiza `DashboardLeads`, verifica que o botão "Exportar Leads Ouro" está presente, clica nele e verifica que o modal abre com Autocomplete de eventos (com opção "Todos") e seleção de formato (xlsx/csv).
- **Green:** Adicionar botão "Exportar Leads Ouro" ao `DashboardLeads.tsx`. Criar componente `ExportGoldModal` com Autocomplete de eventos (reutilizando datasource existente + opção fixa "Todos os eventos") e RadioGroup para formato. No submit, chamar `exportLeadsGold()` e `triggerBlobDownload()`.
- **Refactor:** Extrair `ExportGoldModal` para `frontend/src/components/ExportGoldModal.tsx` se o componente crescer além de 100 linhas.

**Critérios de Aceitação:**

- **Given** o operador acessa `/dashboard/leads`
  **When** a página é renderizada
  **Then** o botão "Exportar Leads Ouro" está visível na seção superior do Dashboard

- **Given** o operador clica em "Exportar Leads Ouro"
  **When** o modal abre
  **Then** o Autocomplete de eventos exibe "Todos os eventos" como opção fixa no topo e os eventos carregados do endpoint de referência

- **Given** o operador seleciona "Todos os eventos" e formato ".xlsx" e clica "Exportar"
  **When** o endpoint retorna 200 com o arquivo
  **Then** o download inicia automaticamente, o modal fecha e um toast de sucesso é exibido

- **Given** o operador seleciona um evento específico e clica "Exportar"
  **When** o endpoint retorna 204 (nenhum lead Gold encontrado)
  **Then** o modal permanece aberto e um toast informativo exibe "Nenhum lead em fase Ouro encontrado para os filtros selecionados."

**Tarefas:**
- [ ] T1: Adicionar botão "Exportar Leads Ouro" ao `DashboardLeads.tsx` (MUI Button com ícone de download)
- [ ] T2: Criar componente `ExportGoldModal` com Dialog, Autocomplete de eventos e RadioGroup de formato
- [ ] T3: Carregar eventos via `listReferenciaEventos()` + adicionar opção fixa "Todos os eventos" (id=null)
- [ ] T4: Implementar submit: loading state → chamar `exportLeadsGold()` → `triggerBlobDownload()` → fechar modal
- [ ] T5: Tratar HTTP 204: exibir toast informativo via Snackbar/toast do MUI
- [ ] T6: Escrever teste de renderização e interação do componente

## 5. Artifact Mínimo do Épico

`artifacts/ajuste-fino-leads/phase-f3/epic-f3-02-ui-evidence.md` — screenshot do botão no Dashboard, modal aberto com opções, e evidência de download bem-sucedido.

## 6. Dependências

- [PRD Refino Leads v2](../PRD_Refino_Leads_v2.md) — Seções 4.1–4.4, 4.6, 4.10
- [SCRUM-GOV](../../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../../COMUM/DECISION-PROTOCOL.md)
- EPIC-F3-01 (endpoint de exportação disponível)
- EPIC-F1-01 (dropdown de eventos com data — opcional, melhora UX do modal)
