---
doc_id: "US-2-02-HOOK-COMPARTILHADO-E-SHELL-CANONICO-DE-IMPORTACAO"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-22"
task_instruction_mode: "required"
feature_id: "FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS"
decision_refs: []
---

# US-2-02 - Hook compartilhado e shell canonico de importacao

## User Story

Como engenharia do NPBB, quero compartilhar o hook de referencia de eventos e
simplificar o lazy-load da importacao para reduzir duplicacao interna no
frontend sem tocar nas rotas suportadas pelos operadores.

## Feature de Origem

- **Feature**: `FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS`
- **Comportamento coberto**: hook compartilhado, shell canonico preservado e
  redirects legados intactos

## Contexto Tecnico

`useReferenciaEventos` atendia tanto a listagem de leads quanto a analise
etaria, mas vivia sob a pasta de dashboard. Ao mesmo tempo, a rota
`/leads/importar` passava por um wrapper que apenas reexportava
`ImportacaoPage`. Esta US elimina esses dois acoplamentos internos.

## Criterios de Aceitacao (Given / When / Then)

- **Given** a lista de leads e a analise etaria,
  **when** ambas precisam carregar eventos de referencia,
  **then** elas reutilizam o mesmo hook em `frontend/src/hooks`.
- **Given** a rota `/leads/importar`,
  **when** o usuario navega para o shell de importacao,
  **then** o lazy-load aponta diretamente para `pages/leads/ImportacaoPage`.
- **Given** os deep links legados de mapeamento e pipeline,
  **when** o usuario os acessa,
  **then** os query params e redirects continuam funcionando.

## Tasks

- [T1 - Centralizar o hook compartilhado de referencia de eventos](./TASK-1.md)
- [T2 - Simplificar o lazy-load da rota de importacao e validar a trilha impactada](./TASK-2.md)

## Arquivos Reais Envolvidos

- `frontend/src/hooks/useReferenciaEventos.ts`
- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/pages/leads/LeadsListPage.tsx`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`
- `frontend/src/pages/__tests__/LeadsListPage.test.tsx`
- `frontend/src/pages/__tests__/ImportacaoPage.test.tsx`
- `frontend/src/pages/__tests__/LegacyLeadStepRedirect.test.tsx`
- `frontend/src/pages/__tests__/MapeamentoPage.test.tsx`
- `frontend/src/pages/__tests__/BatchMapeamentoPage.test.tsx`
- `frontend/src/pages/__tests__/PipelineStatusPage.test.tsx`
- `frontend/src/pages/dashboard/__tests__/DashboardModule.test.tsx`
- `frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.filters.test.tsx`
- `frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.states.test.tsx`

## Dependencias

- [US-2-01](../US-2-01-MODULARIZACAO-DO-ROUTER-DE-LEADS-E-ALINHAMENTO-DOCUMENTAL/README.md)
- [PRD estrutural](../../../../PRD-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md)
