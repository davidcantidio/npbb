---
doc_id: "ISSUE-F3-02-002-IMPLEMENTAR-ESTADOS-DA-INTERFACE-LOADING-EMPTY-ERROR.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F3-02-002 - Implementar estados da interface (loading, empty, error)

## User Story

Como engenheiro de frontend do dashboard, quero entregar Implementar estados da interface (loading, empty, error) para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Tratar todos os estados da interface conforme seção 7.3 do PRD: loading com skeleton
loaders que espelham o layout real, estado vazio com mensagem orientativa e estado de
erro com toast e botão de retry.

Sem observacoes adicionais alem das dependencias e restricoes do epico.

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [ ] Estado loading: skeleton loaders nos KPI cards (4 retângulos), no gráfico (área retangular) e na tabela (linhas fantasma)
- [ ] Estado empty: mensagem centralizada "Nenhum lead encontrado para os filtros aplicados" com ícone ilustrativo
- [ ] Estado error: toast de erro com mensagem descritiva + botão "Tentar novamente"
- [ ] Retry chama `refetch` do hook sem recarregar a página
- [ ] Sem flash de conteúdo: transição suave de skeleton para dados
- [ ] Estado "dados parciais": tooltips com "(dados parciais)" nos valores afetados

## Definition of Done da Issue

- [ ] Estado loading: skeleton loaders nos KPI cards (4 retângulos), no gráfico (área retangular) e na tabela (linhas fantasma)
- [ ] Estado empty: mensagem centralizada "Nenhum lead encontrado para os filtros aplicados" com ícone ilustrativo
- [ ] Estado error: toast de erro com mensagem descritiva + botão "Tentar novamente"
- [ ] Retry chama `refetch` do hook sem recarregar a página
- [ ] Sem flash de conteúdo: transição suave de skeleton para dados
- [ ] Estado "dados parciais": tooltips com "(dados parciais)" nos valores afetados

## Tarefas Decupadas

- [ ] T1: Criar componentes skeleton: `KpiCardSkeleton`, `ChartSkeleton`, `TableSkeleton`
- [ ] T2: Implementar lógica condicional na página (loading → skeleton, error → toast, empty → mensagem)
- [ ] T3: Implementar toast de erro com botão retry (reusar toast existente do projeto)
- [ ] T4: Implementar estado vazio com mensagem e ícone
- [ ] T5: Testar transições de estado (loading → data, loading → error, loading → empty)

## Arquivos Reais Envolvidos

- `frontend/src/components/dashboard/KpiCardSkeleton.tsx`
- `frontend/src/components/dashboard/ChartSkeleton.tsx`
- `frontend/src/components/dashboard/TableSkeleton.tsx`

## Artifact Minimo

- `frontend/src/components/dashboard/KpiCardSkeleton.tsx`

## Dependencias

- [Epic](../EPIC-F3-02-COBERTURA-ESTADOS-QUALIDADE.md)
- [Fase](../F3_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F3-02-COBERTURA-ESTADOS-QUALIDADE]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
