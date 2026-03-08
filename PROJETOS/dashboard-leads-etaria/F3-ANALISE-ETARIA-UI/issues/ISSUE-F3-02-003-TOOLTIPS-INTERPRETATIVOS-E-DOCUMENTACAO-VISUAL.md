---
doc_id: "ISSUE-F3-02-003-TOOLTIPS-INTERPRETATIVOS-E-DOCUMENTACAO-VISUAL.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F3-02-003 - Tooltips interpretativos e documentação visual

## User Story

Como engenheiro de frontend do dashboard, quero entregar Tooltips interpretativos e documentação visual para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Adicionar tooltips interpretativos em métricas que requerem contextualização para o
usuário final: faixa dominante, média vs. mediana, concentração Top 3 e cobertura BB.
Os textos seguem as notas interpretativas do PRD.

Reusar componente de tooltip existente no projeto se houver. Caso contrário, usar
`@radix-ui/react-tooltip` ou Tailwind-based tooltip.

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [x] Tooltip na média: "Soma dos volumes dividida pela quantidade de eventos"
- [x] Tooltip na mediana: "Volume central quando os eventos são ordenados por tamanho. Quando poucos eventos são muito grandes, a mediana é mais representativa do tamanho típico."
- [x] Tooltip na concentração Top 3: "Percentual da base total representada pelos 3 maiores eventos"
- [x] Tooltip na faixa dominante: "Faixa etária com maior volume de leads neste evento"
- [x] Tooltip na cobertura BB: "Percentual de leads com informação de vínculo BB disponível"
- [x] Ícone de info (ℹ️) ao lado da métrica indica presença de tooltip
- [x] Tooltips acessíveis (focusable via teclado, role="tooltip")

## Definition of Done da Issue

- [x] Tooltip na média: "Soma dos volumes dividida pela quantidade de eventos"
- [x] Tooltip na mediana: "Volume central quando os eventos são ordenados por tamanho. Quando poucos eventos são muito grandes, a mediana é mais representativa do tamanho típico."
- [x] Tooltip na concentração Top 3: "Percentual da base total representada pelos 3 maiores eventos"
- [x] Tooltip na faixa dominante: "Faixa etária com maior volume de leads neste evento"
- [x] Tooltip na cobertura BB: "Percentual de leads com informação de vínculo BB disponível"
- [x] Ícone de info (ℹ️) ao lado da métrica indica presença de tooltip
- [x] Tooltips acessíveis (focusable via teclado, role="tooltip")

## Tarefas Decupadas

- [x] T1: Criar componente `InfoTooltip.tsx` com ícone e texto
- [x] T2: Adicionar tooltips aos KPI cards relevantes
- [x] T3: Adicionar tooltips ao painel consolidado (média, mediana, concentração)
- [x] T4: Garantir acessibilidade (ARIA attributes, keyboard navigation)

## Arquivos Reais Envolvidos

- `frontend/src/components/dashboard/InfoTooltip.tsx`
- `frontend/src/components/dashboard/ConsolidatedPanel.tsx`

## Artifact Minimo

- `frontend/src/components/dashboard/InfoTooltip.tsx`

## Dependencias

- [Issue Dependente](./ISSUE-F3-01-005-IMPLEMENTAR-PAINEL-CONSOLIDADO-COM-TOP-3-MEDIA-E-MEDIANA.md)
- [Epic](../EPIC-F3-02-COBERTURA-ESTADOS-QUALIDADE.md)
- [Fase](../F3_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F3-02-COBERTURA-ESTADOS-QUALIDADE]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
