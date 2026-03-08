---
doc_id: "ISSUE-F2-01-001-CRIAR-MANIFESTO-DE-DASHBOARDS-NO-FRONTEND.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F2-01-001 - Criar manifesto de dashboards no frontend

## User Story

Como engenheiro de frontend do dashboard, quero entregar Criar manifesto de dashboards no frontend para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Definir o manifesto declarativo de dashboards como array tipado em TypeScript. Cada
entrada define: id, rota, domínio, nome da análise, ícone, descrição curta e flag
`enabled`. O manifesto é a fonte de verdade para navegação, cards e sidebar.

O ícone pode ser string referenciando componente de ícone (Lucide, Heroicons) ou
nome de ícone — seguir padrão do projeto.

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [x] Tipo `DashboardManifestEntry` definido com campos: `id`, `route`, `domain`, `name`, `icon`, `description`, `enabled`
- [x] Array `DASHBOARD_MANIFEST` com ao menos 3 entradas: Análise Etária (enabled), Fechamento de Evento (disabled), Conversão por Evento (disabled)
- [x] Manifesto exportado de módulo dedicado (`frontend/src/config/dashboardManifest.ts`)
- [x] Tipo e array cobertos por teste unitário de shape

## Definition of Done da Issue

- [x] Tipo `DashboardManifestEntry` definido com campos: `id`, `route`, `domain`, `name`, `icon`, `description`, `enabled`
- [x] Array `DASHBOARD_MANIFEST` com ao menos 3 entradas: Análise Etária (enabled), Fechamento de Evento (disabled), Conversão por Evento (disabled)
- [x] Manifesto exportado de módulo dedicado (`frontend/src/config/dashboardManifest.ts`)
- [x] Tipo e array cobertos por teste unitário de shape

## Tarefas Decupadas

- [x] T1: Criar tipo `DashboardManifestEntry` em `frontend/src/types/dashboard.ts`
- [x] T2: Criar manifesto em `frontend/src/config/dashboardManifest.ts`
- [x] T3: Popular manifesto com entradas conforme PRD (seção 1.1)
- [x] T4: Escrever teste de shape do manifesto

## Arquivos Reais Envolvidos

- `frontend/src/types/dashboard.ts`
- `frontend/src/config/dashboardManifest.ts`

## Artifact Minimo

- `frontend/src/config/dashboardManifest.ts`

## Dependencias

- [Epic](../EPIC-F2-01-LAYOUT-E-MANIFESTO-DASHBOARDS.md)
- [Fase](../F2_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F2-01-LAYOUT-E-MANIFESTO-DASHBOARDS]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
