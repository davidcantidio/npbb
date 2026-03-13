---
doc_id: "ISSUE-F3-01-005-IMPLEMENTAR-PAINEL-CONSOLIDADO-COM-TOP-3-MEDIA-E-MEDIANA.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F3-01-005 - Implementar painel consolidado com Top 3, média e mediana

## User Story

Como engenheiro de frontend do dashboard, quero entregar Implementar painel consolidado com Top 3, média e mediana para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Criar o painel de resumo consolidado que aparece no topo da página (abaixo dos KPI
cards), destacando os Top 3 eventos por volume, média por evento, mediana por evento
e concentração Top 3.

Sem observacoes adicionais alem das dependencias e restricoes do epico.

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [x] Top 3 eventos listados com nome, volume e percentual da base total
- [x] Média por evento exibida com 1 casa decimal
- [x] Mediana por evento exibida como inteiro
- [x] Concentração Top 3 exibida como percentual
- [x] Tooltip na mediana explica: "Valor central ao ordenar eventos por volume"
- [x] Tooltip na média explica: "Soma total dividida pela quantidade de eventos"
- [x] Layout em linha ou cards horizontais, integrado ao design da página

## Definition of Done da Issue

- [x] Top 3 eventos listados com nome, volume e percentual da base total
- [x] Média por evento exibida com 1 casa decimal
- [x] Mediana por evento exibida como inteiro
- [x] Concentração Top 3 exibida como percentual
- [x] Tooltip na mediana explica: "Valor central ao ordenar eventos por volume"
- [x] Tooltip na média explica: "Soma total dividida pela quantidade de eventos"
- [x] Layout em linha ou cards horizontais, integrado ao design da página

## Tarefas Decupadas

- [x] T1: Criar componente `ConsolidatedPanel.tsx`
- [x] T2: Implementar seção Top 3 com ranking visual (1º, 2º, 3º)
- [x] T3: Implementar métricas estatísticas (média, mediana, concentração)
- [x] T4: Adicionar tooltips interpretativos
- [x] T5: Integrar no layout da página abaixo dos KPI cards

## Arquivos Reais Envolvidos

- `frontend/src/components/dashboard/ConsolidatedPanel.tsx`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`

## Artifact Minimo

- `frontend/src/components/dashboard/ConsolidatedPanel.tsx`

## Dependencias

- [Issue Dependente](./ISSUE-F3-01-001-CRIAR-TIPOS-TYPESCRIPT-E-HOOK-DE-CONSUMO-DA-API.md)
- [Epic](../EPIC-F3-01-DADOS-E-VISUALIZACOES.md)
- [Fase](../F3_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F3-01-DADOS-E-VISUALIZACOES]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
