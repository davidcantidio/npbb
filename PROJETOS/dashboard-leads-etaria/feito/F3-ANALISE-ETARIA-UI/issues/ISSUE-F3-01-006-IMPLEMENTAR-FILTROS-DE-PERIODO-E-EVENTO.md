---
doc_id: "ISSUE-F3-01-006-IMPLEMENTAR-FILTROS-DE-PERIODO-E-EVENTO.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F3-01-006 - Implementar filtros de período e evento

## User Story

Como engenheiro de frontend do dashboard, quero entregar Implementar filtros de período e evento para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Criar o painel de filtros da análise etária com seletores de período (data início/fim)
e evento específico. Os filtros atualizam os query params da URL e disparam nova
chamada à API.

Reusar componentes de date picker e select existentes no projeto. Consultar
`frontend/src/components/` para componentes de formulário disponíveis.

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [x] Seletor de período com date pickers para data início e data fim
- [x] Dropdown/select de evento com busca (lista de eventos disponíveis)
- [x] Opção "Todos os eventos" como default do seletor de evento
- [x] Filtros refletidos na URL como query params (deep link suportado)
- [x] Alteração de filtro dispara nova chamada à API via hook `useAgeAnalysis`
- [x] Botão "Limpar filtros" restaura estado default

## Definition of Done da Issue

- [x] Seletor de período com date pickers para data início e data fim
- [x] Dropdown/select de evento com busca (lista de eventos disponíveis)
- [x] Opção "Todos os eventos" como default do seletor de evento
- [x] Filtros refletidos na URL como query params (deep link suportado)
- [x] Alteração de filtro dispara nova chamada à API via hook `useAgeAnalysis`
- [x] Botão "Limpar filtros" restaura estado default

## Tarefas Decupadas

- [x] T1: Criar componente `AgeAnalysisFilters.tsx`
- [x] T2: Implementar date pickers de período
- [x] T3: Implementar dropdown de eventos (consumir lista de eventos da API existente)
- [x] T4: Sincronizar filtros com query params da URL
- [x] T5: Conectar filtros ao hook `useAgeAnalysis`

## Arquivos Reais Envolvidos

- `frontend/src/components/dashboard/AgeAnalysisFilters.tsx`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`

## Artifact Minimo

- `frontend/src/components/dashboard/AgeAnalysisFilters.tsx`

## Evidencia de Validacao

- comando: `cd /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/frontend && npm run test -- --run src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.filters.test.tsx`
- resultado: `1 arquivo, 4 testes passando`

## Dependencias

- [Issue Dependente](./ISSUE-F3-01-001-CRIAR-TIPOS-TYPESCRIPT-E-HOOK-DE-CONSUMO-DA-API.md)
- [Epic](../EPIC-F3-01-DADOS-E-VISUALIZACOES.md)
- [Fase](../F3_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F3-01-DADOS-E-VISUALIZACOES]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
