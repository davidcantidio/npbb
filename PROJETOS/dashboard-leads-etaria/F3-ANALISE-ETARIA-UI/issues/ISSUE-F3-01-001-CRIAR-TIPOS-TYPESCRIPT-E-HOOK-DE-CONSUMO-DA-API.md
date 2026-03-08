---
doc_id: "ISSUE-F3-01-001-CRIAR-TIPOS-TYPESCRIPT-E-HOOK-DE-CONSUMO-DA-API.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F3-01-001 - Criar tipos TypeScript e hook de consumo da API

## User Story

Como engenheiro de frontend do dashboard, quero entregar Criar tipos TypeScript e hook de consumo da API para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Definir os tipos TypeScript que espelham os schemas Pydantic do backend
(`AgeAnalysisResponse`, `EventoAgeAnalysis`, `AgeBreakdown`, `FaixaEtariaMetrics`) e
criar um hook customizado (`useAgeAnalysis`) que consome o endpoint e gerencia loading,
error e data.

Seguir o padrão de hooks do projeto (verificar se usa React Query, SWR ou fetch manual).

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [ ] Tipos definidos em `frontend/src/types/dashboard.ts` (ou mesmo módulo do manifesto)
- [ ] `useAgeAnalysis(filters)` aceita `evento_id`, `data_inicio`, `data_fim` opcionais
- [ ] Hook retorna `{ data, isLoading, error, refetch }`
- [ ] Token JWT incluído automaticamente nas requisições (reusar padrão do projeto)
- [ ] Tipo de resposta reflete exatamente o schema do backend (seção 5 do PRD)

## Definition of Done da Issue

- [ ] Tipos definidos em `frontend/src/types/dashboard.ts` (ou mesmo módulo do manifesto)
- [ ] `useAgeAnalysis(filters)` aceita `evento_id`, `data_inicio`, `data_fim` opcionais
- [ ] Hook retorna `{ data, isLoading, error, refetch }`
- [ ] Token JWT incluído automaticamente nas requisições (reusar padrão do projeto)
- [ ] Tipo de resposta reflete exatamente o schema do backend (seção 5 do PRD)

## Tarefas Decupadas

- [ ] T1: Definir tipos TypeScript para `FaixaEtariaMetrics`, `AgeBreakdown`, `EventoAgeAnalysis`, `ConsolidadoAgeAnalysis`, `AgeAnalysisResponse`
- [ ] T2: Criar hook `useAgeAnalysis` em `frontend/src/hooks/useAgeAnalysis.ts`
- [ ] T3: Integrar com mecanismo de autenticação existente
- [ ] T4: Tratar estados de loading, error e data vazia

## Arquivos Reais Envolvidos

- `frontend/src/types/dashboard.ts`
- `frontend/src/hooks/useAgeAnalysis.ts`

## Artifact Minimo

- `frontend/src/hooks/useAgeAnalysis.ts`

## Dependencias

- [Epic](../EPIC-F3-01-DADOS-E-VISUALIZACOES.md)
- [Fase](../F3_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F3-01-DADOS-E-VISUALIZACOES]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
