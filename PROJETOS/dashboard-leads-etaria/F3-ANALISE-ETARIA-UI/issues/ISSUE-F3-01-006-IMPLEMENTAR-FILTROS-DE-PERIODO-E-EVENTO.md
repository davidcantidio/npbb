---
doc_id: "ISSUE-F3-01-006-IMPLEMENTAR-FILTROS-DE-PERIODO-E-EVENTO.md"
version: "1.0"
status: "todo"
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

- [ ] Seletor de período com date pickers para data início e data fim
- [ ] Dropdown/select de evento com busca (lista de eventos disponíveis)
- [ ] Opção "Todos os eventos" como default do seletor de evento
- [ ] Filtros refletidos na URL como query params (deep link suportado)
- [ ] Alteração de filtro dispara nova chamada à API via hook `useAgeAnalysis`
- [ ] Botão "Limpar filtros" restaura estado default

## Definition of Done da Issue

- [ ] Seletor de período com date pickers para data início e data fim
- [ ] Dropdown/select de evento com busca (lista de eventos disponíveis)
- [ ] Opção "Todos os eventos" como default do seletor de evento
- [ ] Filtros refletidos na URL como query params (deep link suportado)
- [ ] Alteração de filtro dispara nova chamada à API via hook `useAgeAnalysis`
- [ ] Botão "Limpar filtros" restaura estado default

## Tarefas Decupadas

- [ ] T1: Criar componente `AgeAnalysisFilters.tsx`
- [ ] T2: Implementar date pickers de período
- [ ] T3: Implementar dropdown de eventos (consumir lista de eventos da API existente)
- [ ] T4: Sincronizar filtros com query params da URL
- [ ] T5: Conectar filtros ao hook `useAgeAnalysis`

## Arquivos Reais Envolvidos

- `frontend/src/components/dashboard/AgeAnalysisFilters.tsx`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`

## Artifact Minimo

- `frontend/src/components/dashboard/AgeAnalysisFilters.tsx`

## Dependencias

- [Issue Dependente](./ISSUE-F3-01-001-CRIAR-TIPOS-TYPESCRIPT-E-HOOK-DE-CONSUMO-DA-API.md)
- [Epic](../EPIC-F3-01-DADOS-E-VISUALIZACOES.md)
- [Fase](../F3_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F3-01-DADOS-E-VISUALIZACOES]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
