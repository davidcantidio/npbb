---
doc_id: "ISSUE-F2-01-002-IMPLEMENTAR-DASHBOARDLAYOUT-COM-SIDEBAR-DE-NAVEGACAO.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F2-01-002 - Implementar DashboardLayout com sidebar de navegação

## User Story

Como engenheiro de frontend do dashboard, quero entregar Implementar DashboardLayout com sidebar de navegação para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Criar o componente `DashboardLayout` que envolve todas as páginas do módulo dashboard.
Inclui sidebar de navegação renderizada a partir do manifesto, com links para análises
habilitadas e itens desabilitados para análises futuras.

Sem observacoes adicionais alem das dependencias e restricoes do epico.

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [x] Componente `DashboardLayout` renderiza sidebar + área de conteúdo (Outlet)
- [x] Sidebar lista todas as entradas do manifesto com ícone e nome
- [x] Entradas com `enabled: true` são links navegáveis com destaque de rota ativa
- [x] Entradas com `enabled: false` aparecem esmaecidas com tooltip "Em breve"
- [x] Layout responsivo: sidebar colapsa em mobile (hambúrguer ou drawer)
- [x] Componente não conflita com a navegação global da aplicação

## Definition of Done da Issue

- [x] Componente `DashboardLayout` renderiza sidebar + área de conteúdo (Outlet)
- [x] Sidebar lista todas as entradas do manifesto com ícone e nome
- [x] Entradas com `enabled: true` são links navegáveis com destaque de rota ativa
- [x] Entradas com `enabled: false` aparecem esmaecidas com tooltip "Em breve"
- [x] Layout responsivo: sidebar colapsa em mobile (hambúrguer ou drawer)
- [x] Componente não conflita com a navegação global da aplicação

## Tarefas Decupadas

- [x] T1: Criar componente `frontend/src/components/dashboard/DashboardLayout.tsx`
- [x] T2: Implementar sidebar com iteração sobre manifesto
- [x] T3: Implementar destaque de rota ativa via `useLocation()`
- [x] T4: Implementar comportamento responsivo (mobile)
- [x] T5: Estilizar com Tailwind seguindo padrão visual do projeto

## Arquivos Reais Envolvidos

- `frontend/src/components/dashboard/DashboardLayout.tsx`
- `frontend/src/App.tsx`

## Artifact Minimo

- `frontend/src/components/dashboard/DashboardLayout.tsx`

## Dependencias

- [Issue Dependente](./ISSUE-F2-01-001-CRIAR-MANIFESTO-DE-DASHBOARDS-NO-FRONTEND.md)
- [Epic](../EPIC-F2-01-LAYOUT-E-MANIFESTO-DASHBOARDS.md)
- [Fase](../F2_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F2-01-LAYOUT-E-MANIFESTO-DASHBOARDS]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
