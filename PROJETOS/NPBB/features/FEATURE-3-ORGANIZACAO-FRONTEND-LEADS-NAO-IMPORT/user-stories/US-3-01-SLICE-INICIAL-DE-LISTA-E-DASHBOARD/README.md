---
doc_id: "US-3-01-SLICE-INICIAL-DE-LISTA-E-DASHBOARD"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-23"
task_instruction_mode: "required"
feature_id: "FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT"
decision_refs:
  - "plano_organizacao_import.md"
---

# US-3-01 - Slice inicial de lista e dashboard

## User Story

Como engenharia do NPBB, quero mover a implementacao nao-import de leads para
`frontend/src/features/leads`, com wrappers de compatibilidade nos caminhos
legados, para reduzir acoplamento interno sem alterar a superficie publica.

## Feature de Origem

- **Feature**: `FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT`
- **Comportamento coberto**: slice inicial de lista, analise etaria e hook
  compartilhado

## Contexto Tecnico

Outras areas do frontend ja usam `features/*`, mas a vertical de leads ainda
estava distribuida entre `pages/leads`, `pages/dashboard` e `hooks`. Esta US
cria o primeiro slice interno dessa vertical, sem tocar no shell de importacao
e sem religar `DashboardLeads.tsx`.

Em 2026-04-23, os testes focados de lista e dashboard foram consolidados para
importar a implementacao real via `frontend/src/features/leads`, preservando os
wrappers legados como camada de compatibilidade.

## Criterios de Aceitacao (Given / When / Then)

- **Given** a lista e o dashboard de leads,
  **when** o time navegar pelo codigo,
  **then** a implementacao principal mora em `frontend/src/features/leads`.
- **Given** imports legados de `pages/*` e `hooks/useReferenciaEventos.ts`,
  **when** o frontend e os testes carregarem esses caminhos,
  **then** a compatibilidade permanece via wrappers finos.
- **Given** `DashboardLeads.tsx`,
  **when** esta rodada estrutural terminar,
  **then** o arquivo continua sem rota e documentado como legado fora do slice.

## Tasks

- [T1 - Criar o slice `features/leads` e mover a implementacao nao-import](./TASK-1.md)
- [T2 - Registrar `DashboardLeads.tsx` como artefato legado nao roteado](./TASK-2.md)
- [T3 - Validar typecheck e suites focadas do recorte](./TASK-3.md)

## Arquivos Reais Envolvidos

- `frontend/src/features/leads/`
- `frontend/src/pages/leads/LeadsListPage.tsx`
- `frontend/src/pages/leads/leadsListExport.ts`
- `frontend/src/pages/leads/leadsListQuarterPresets.ts`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`
- `frontend/src/pages/dashboard/useAgeAnalysisFilters.ts`
- `frontend/src/hooks/useReferenciaEventos.ts`
- `frontend/src/pages/DashboardLeads.tsx`
- `plano_organizacao_import.md`

## Dependencias

- [PRD frontend nao-import](../../../../PRD-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md)
- [Feature 2](../../../FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS/FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS.md)
