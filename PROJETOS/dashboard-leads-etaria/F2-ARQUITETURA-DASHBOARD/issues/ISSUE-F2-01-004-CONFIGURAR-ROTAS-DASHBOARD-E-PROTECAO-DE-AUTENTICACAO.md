---
doc_id: "ISSUE-F2-01-004-CONFIGURAR-ROTAS-DASHBOARD-E-PROTECAO-DE-AUTENTICACAO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F2-01-004 - Configurar rotas /dashboard/* e proteção de autenticação

## User Story

Como engenheiro de frontend do dashboard, quero entregar Configurar rotas /dashboard/* e proteção de autenticação para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Configurar o roteamento aninhado para o módulo dashboard (`/dashboard/*`), integrar
com o `DashboardLayout` e aplicar guard de autenticação JWT para proteger todas as
rotas do módulo.

Reusar o guard de autenticação existente no projeto (verificar implementação atual
em `frontend/src/`). Não criar novo mecanismo de auth.

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [ ] Rota `/dashboard` renderiza `DashboardHome` dentro de `DashboardLayout`
- [ ] Rota `/dashboard/leads/analise-etaria` renderiza componente placeholder (até F3)
- [ ] Rotas do dashboard protegidas por guard de autenticação existente
- [ ] Acesso sem autenticação redireciona para login
- [ ] Rota inexistente dentro de `/dashboard/*` exibe 404 ou redireciona para `/dashboard`
- [ ] Link para "Dashboard" adicionado ao menu/navegação principal da aplicação

## Definition of Done da Issue

- [ ] Rota `/dashboard` renderiza `DashboardHome` dentro de `DashboardLayout`
- [ ] Rota `/dashboard/leads/analise-etaria` renderiza componente placeholder (até F3)
- [ ] Rotas do dashboard protegidas por guard de autenticação existente
- [ ] Acesso sem autenticação redireciona para login
- [ ] Rota inexistente dentro de `/dashboard/*` exibe 404 ou redireciona para `/dashboard`
- [ ] Link para "Dashboard" adicionado ao menu/navegação principal da aplicação

## Tarefas Decupadas

- [ ] T1: Configurar rotas aninhadas em `frontend/src/App.tsx` ou arquivo de rotas
- [ ] T2: Aplicar guard de autenticação ao grupo `/dashboard/*`
- [ ] T3: Criar componente placeholder para `/dashboard/leads/analise-etaria`
- [ ] T4: Adicionar link "Dashboard" ao menu de navegação principal
- [ ] T5: Testar navegação: autenticado e não-autenticado

## Arquivos Reais Envolvidos

- `frontend/src/App.tsx`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`

## Artifact Minimo

- `frontend/src/App.tsx`

## Dependencias

- [Issue Dependente](./ISSUE-F2-01-002-IMPLEMENTAR-DASHBOARDLAYOUT-COM-SIDEBAR-DE-NAVEGACAO.md)
- [Issue Dependente](./ISSUE-F2-01-003-IMPLEMENTAR-DASHBOARDHOME-SELETOR-VISUAL-DE-ANALISES.md)
- [Epic](../EPIC-F2-01-LAYOUT-E-MANIFESTO-DASHBOARDS.md)
- [Fase](../F2_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F2-01-LAYOUT-E-MANIFESTO-DASHBOARDS]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
