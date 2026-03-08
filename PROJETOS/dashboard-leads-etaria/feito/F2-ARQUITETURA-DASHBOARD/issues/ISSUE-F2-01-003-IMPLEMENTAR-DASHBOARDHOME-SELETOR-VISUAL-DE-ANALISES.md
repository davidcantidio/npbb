---
doc_id: "ISSUE-F2-01-003-IMPLEMENTAR-DASHBOARDHOME-SELETOR-VISUAL-DE-ANALISES.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F2-01-003 - Implementar DashboardHome (seletor visual de análises)

## User Story

Como engenheiro de frontend do dashboard, quero entregar Implementar DashboardHome (seletor visual de análises) para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Criar a página `DashboardHome` que renderiza na rota `/dashboard`. Exibe cards
clicáveis em grid de 3 colunas, um por entrada no manifesto. Cards habilitados
navegam para a análise; cards desabilitados exibem badge "Em breve" e são
não-clicáveis.

Sem observacoes adicionais alem das dependencias e restricoes do epico.

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [x] Página renderiza na rota `/dashboard`
- [x] Grid de 3 colunas com cards para cada entrada do manifesto
- [x] Cards habilitados: clicáveis, com ícone, nome, descrição e hover effect
- [x] Cards desabilitados: badge "Em breve", opacidade reduzida, cursor default
- [x] Grid responsivo: 1 coluna em mobile, 2 em tablet, 3 em desktop
- [x] Título da página: "Dashboard" ou "Painel de Análises"

## Definition of Done da Issue

- [x] Página renderiza na rota `/dashboard`
- [x] Grid de 3 colunas com cards para cada entrada do manifesto
- [x] Cards habilitados: clicáveis, com ícone, nome, descrição e hover effect
- [x] Cards desabilitados: badge "Em breve", opacidade reduzida, cursor default
- [x] Grid responsivo: 1 coluna em mobile, 2 em tablet, 3 em desktop
- [x] Título da página: "Dashboard" ou "Painel de Análises"

## Tarefas Decupadas

- [x] T1: Criar página `frontend/src/pages/dashboard/DashboardHome.tsx`
- [x] T2: Criar componente de card `DashboardCard.tsx`
- [x] T3: Implementar grid responsivo com Tailwind
- [x] T4: Implementar estados de card (enabled/disabled) com badge "Em breve"
- [x] T5: Conectar click dos cards à navegação via React Router

## Arquivos Reais Envolvidos

- `frontend/src/pages/dashboard/DashboardHome.tsx`
- `frontend/src/components/dashboard/DashboardCard.tsx`

## Artifact Minimo

- `frontend/src/pages/dashboard/DashboardHome.tsx`

## Dependencias

- [Issue Dependente](./ISSUE-F2-01-001-CRIAR-MANIFESTO-DE-DASHBOARDS-NO-FRONTEND.md)
- [Epic](../EPIC-F2-01-LAYOUT-E-MANIFESTO-DASHBOARDS.md)
- [Fase](../F2_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F2-01-LAYOUT-E-MANIFESTO-DASHBOARDS]]`
- `[[../../../PRD-DASHBOARD-LEADS-ETARIA]]`
