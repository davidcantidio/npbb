---
doc_id: "ISSUE-F3-01-003-IMPLEMENTAR-GRAFICO-DE-BARRAS-EMPILHADAS-DISTRIBUICAO-ETARIA.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F3-01-003 - Implementar gráfico de barras empilhadas (distribuição etária)

## User Story

Como engenheiro de frontend do dashboard, quero entregar Implementar gráfico de barras empilhadas (distribuição etária) para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Criar o gráfico de barras empilhadas que visualiza a distribuição etária por evento.
Cada barra representa um evento; as seções empilhadas representam as faixas 18–25,
26–40, fora de 18–40 e sem informação. Suportar hover com tooltip detalhado.

Se o projeto já usa uma biblioteca de gráficos, priorizar consistência. Caso contrário,
recharts é a escolha recomendada para React (leve, declarativo, boa tipagem TS).

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [x] Gráfico de barras empilhadas com uma barra por evento
- [x] Seções coloridas: 18–25 (azul), 26–40 (verde), fora 18–40 (laranja), sem info (cinza)
- [x] Legenda visível com nome de cada faixa e cor correspondente
- [x] Hover/tooltip exibe volume e percentual de cada faixa para o evento
- [x] Eixo Y: volume de leads; Eixo X: nome do evento (truncado se longo)
- [x] Scroll horizontal quando há muitos eventos (>10)
- [x] Responsivo: altura se ajusta ao viewport

## Definition of Done da Issue

- [x] Gráfico de barras empilhadas com uma barra por evento
- [x] Seções coloridas: 18–25 (azul), 26–40 (verde), fora 18–40 (laranja), sem info (cinza)
- [x] Legenda visível com nome de cada faixa e cor correspondente
- [x] Hover/tooltip exibe volume e percentual de cada faixa para o evento
- [x] Eixo Y: volume de leads; Eixo X: nome do evento (truncado se longo)
- [x] Scroll horizontal quando há muitos eventos (>10)
- [x] Responsivo: altura se ajusta ao viewport

## Tarefas Decupadas

- [x] T1: Avaliar e instalar biblioteca de gráficos (recharts recomendado)
- [x] T2: Criar componente `AgeDistributionChart.tsx`
- [x] T3: Mapear dados da API para formato esperado pelo gráfico
- [x] T4: Implementar tooltip customizado com volume e percentual
- [x] T5: Implementar legenda e responsividade
- [x] T6: Tratar cenário com muitos eventos (scroll horizontal)

## Arquivos Reais Envolvidos

- `frontend/src/components/dashboard/AgeDistributionChart.tsx`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`

## Artifact Minimo

- `frontend/src/components/dashboard/AgeDistributionChart.tsx`

## Dependencias

- [Issue Dependente](./ISSUE-F3-01-001-CRIAR-TIPOS-TYPESCRIPT-E-HOOK-DE-CONSUMO-DA-API.md)
- [Epic](../EPIC-F3-01-DADOS-E-VISUALIZACOES.md)
- [Fase](../F3_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F3-01-DADOS-E-VISUALIZACOES]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
