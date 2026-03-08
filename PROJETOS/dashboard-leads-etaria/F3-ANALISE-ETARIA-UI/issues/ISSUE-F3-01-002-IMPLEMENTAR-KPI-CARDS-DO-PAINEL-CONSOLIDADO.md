---
doc_id: "ISSUE-F3-01-002-IMPLEMENTAR-KPI-CARDS-DO-PAINEL-CONSOLIDADO.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F3-01-002 - Implementar KPI Cards do painel consolidado

## User Story

Como engenheiro de frontend do dashboard, quero entregar Implementar KPI Cards do painel consolidado para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Criar os KPI cards que aparecem no topo da página de análise etária, exibindo métricas
consolidadas: base total de leads, clientes BB (volume + percentual com indicador de
cobertura), faixa dominante e eventos no filtro.

Sem observacoes adicionais alem das dependencias e restricoes do epico.

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [x] Card "Base Total" exibe contagem total de leads no filtro
- [x] Card "Clientes BB" exibe volume e percentual; indicador de cobertura (barra ou badge)
- [x] Card "Faixa Dominante" exibe nome da faixa com maior volume (ex.: "26–40")
- [x] Card "Eventos" exibe quantidade de eventos no filtro
- [x] Cards com design consistente: ícone, valor principal, valor secundário, tendência (opcional)
- [x] Componente `KpiCard` genérico e reutilizável

## Definition of Done da Issue

- [x] Card "Base Total" exibe contagem total de leads no filtro
- [x] Card "Clientes BB" exibe volume e percentual; indicador de cobertura (barra ou badge)
- [x] Card "Faixa Dominante" exibe nome da faixa com maior volume (ex.: "26–40")
- [x] Card "Eventos" exibe quantidade de eventos no filtro
- [x] Cards com design consistente: ícone, valor principal, valor secundário, tendência (opcional)
- [x] Componente `KpiCard` genérico e reutilizável

## Tarefas Decupadas

- [x] T1: Criar componente genérico `KpiCard.tsx` em `frontend/src/components/dashboard/`
- [x] T2: Implementar card "Base Total"
- [x] T3: Implementar card "Clientes BB" com indicador de cobertura
- [x] T4: Implementar card "Faixa Dominante"
- [x] T5: Compor os 4 cards no topo da página com grid responsivo

## Arquivos Reais Envolvidos

- `frontend/src/components/dashboard/KpiCard.tsx`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`

## Artifact Minimo

- `frontend/src/components/dashboard/KpiCard.tsx`

## Dependencias

- [Issue Dependente](./ISSUE-F3-01-001-CRIAR-TIPOS-TYPESCRIPT-E-HOOK-DE-CONSUMO-DA-API.md)
- [Epic](../EPIC-F3-01-DADOS-E-VISUALIZACOES.md)
- [Fase](../F3_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F3-01-DADOS-E-VISUALIZACOES]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
