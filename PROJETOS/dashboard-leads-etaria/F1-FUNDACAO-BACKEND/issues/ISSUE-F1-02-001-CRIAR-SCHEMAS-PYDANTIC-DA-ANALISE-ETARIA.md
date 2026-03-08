---
doc_id: "ISSUE-F1-02-001-CRIAR-SCHEMAS-PYDANTIC-DA-ANALISE-ETARIA.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F1-02-001 - Criar schemas Pydantic da análise etária

## User Story

Como engenheiro de backend do dashboard, quero entregar Criar schemas Pydantic da análise etária para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Implementar os schemas de resposta da análise etária conforme seção 5 do PRD:
`FaixaEtariaMetrics`, `AgeBreakdown`, `EventoAgeAnalysis`, `ConsolidadoAgeAnalysis` e
`AgeAnalysisResponse`. Os schemas devem ser rigorosamente tipados e documentados.

Usar `BaseModel` do Pydantic (não SQLModel) — estes schemas não representam tabelas.

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [x] `FaixaEtariaMetrics` com `volume: int` e `pct: float`
- [x] `AgeBreakdown` com `faixa_18_25`, `faixa_26_40`, `fora_18_40`, `sem_info_volume`, `sem_info_pct_da_base`
- [x] `EventoAgeAnalysis` com todos os campos de nível evento (seção 5.1 do PRD)
- [x] `ConsolidadoAgeAnalysis` com `base_total`, faixas, `top_eventos`, `media_por_evento`, `mediana_por_evento`, `concentracao_top3_pct`
- [x] `AgeAnalysisResponse` com `version`, `generated_at`, `filters`, `por_evento`, `consolidado`
- [x] Schemas passam em testes de serialização com dados de exemplo

## Definition of Done da Issue

- [x] `FaixaEtariaMetrics` com `volume: int` e `pct: float`
- [x] `AgeBreakdown` com `faixa_18_25`, `faixa_26_40`, `fora_18_40`, `sem_info_volume`, `sem_info_pct_da_base`
- [x] `EventoAgeAnalysis` com todos os campos de nível evento (seção 5.1 do PRD)
- [x] `ConsolidadoAgeAnalysis` com `base_total`, faixas, `top_eventos`, `media_por_evento`, `mediana_por_evento`, `concentracao_top3_pct`
- [x] `AgeAnalysisResponse` com `version`, `generated_at`, `filters`, `por_evento`, `consolidado`
- [x] Schemas passam em testes de serialização com dados de exemplo

## Tarefas Decupadas

- [x] T1: Criar módulo `backend/app/schemas/dashboard.py`
- [x] T2: Implementar `FaixaEtariaMetrics` e `AgeBreakdown`
- [x] T3: Implementar `EventoAgeAnalysis` e `ConsolidadoAgeAnalysis`
- [x] T4: Implementar `AgeAnalysisResponse` com envelope (version, generated_at, filters)
- [x] T5: Escrever testes de serialização com fixtures de dados

## Arquivos Reais Envolvidos

- `backend/app/schemas/dashboard.py`
- `backend/tests/`

## Artifact Minimo

- `backend/app/schemas/dashboard.py`

## Dependencias

- [Epic](../EPIC-F1-02-ENDPOINT-ANALISE-ETARIA.md)
- [Fase](../F1_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F1-02-ENDPOINT-ANALISE-ETARIA]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
