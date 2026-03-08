---
doc_id: "EPIC-F2-01-LAYOUT-E-MANIFESTO-DASHBOARDS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-08"
---

# EPIC-F2-01 - Layout e Manifesto de Dashboards

## Objetivo

Criar a infraestrutura frontend do módulo Dashboard: um manifesto declarativo de análises
disponíveis, o componente de layout com sidebar de navegação, a página seletora
(`DashboardHome`) com cards visuais e o roteamento protegido por autenticação. O design
segue o princípio de extensibilidade zero-change: novos dashboards são adicionados apenas
via manifesto + componente de página.

## Resultado de Negocio Mensuravel

O modulo dashboard passa a ter uma arquitetura extensivel, em que novas analises entram por configuracao e nao por refatoracao estrutural.

## Contexto Arquitetural

- Frontend React + Vite com Tailwind CSS
- Roteamento via React Router (padrão do projeto)
- Autenticação JWT existente — reusar guards/hooks já implementados
- Estrutura de páginas em `frontend/src/pages/`
- Componentes reutilizáveis em `frontend/src/components/`
- Novo módulo: `frontend/src/components/dashboard/` e `frontend/src/pages/dashboard/`

## Definition of Done do Epico

- [ ] Manifesto tipado com entradas para análises (ativa + "Em breve")
- [ ] `DashboardLayout` com sidebar funcional baseada no manifesto
- [ ] `DashboardHome` com grid de cards clicáveis/não-clicáveis
- [ ] Rotas `/dashboard` e `/dashboard/leads/analise-etaria` protegidas e funcionais
- [ ] Extensibilidade validada: nova entrada no manifesto = novo card sem alterar layout

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-01-001 | Criar manifesto de dashboards no frontend | Criar manifesto de dashboards no frontend | 2 | todo | [ISSUE-F2-01-001-CRIAR-MANIFESTO-DE-DASHBOARDS-NO-FRONTEND.md](./issues/ISSUE-F2-01-001-CRIAR-MANIFESTO-DE-DASHBOARDS-NO-FRONTEND.md) |
| ISSUE-F2-01-002 | Implementar DashboardLayout com sidebar de navegação | Implementar DashboardLayout com sidebar de navegação | 3 | todo | [ISSUE-F2-01-002-IMPLEMENTAR-DASHBOARDLAYOUT-COM-SIDEBAR-DE-NAVEGACAO.md](./issues/ISSUE-F2-01-002-IMPLEMENTAR-DASHBOARDLAYOUT-COM-SIDEBAR-DE-NAVEGACAO.md) |
| ISSUE-F2-01-003 | Implementar DashboardHome (seletor visual de análises) | Implementar DashboardHome (seletor visual de análises) | 3 | todo | [ISSUE-F2-01-003-IMPLEMENTAR-DASHBOARDHOME-SELETOR-VISUAL-DE-ANALISES.md](./issues/ISSUE-F2-01-003-IMPLEMENTAR-DASHBOARDHOME-SELETOR-VISUAL-DE-ANALISES.md) |
| ISSUE-F2-01-004 | Configurar rotas /dashboard/* e proteção de autenticação | Configurar rotas /dashboard/* e proteção de autenticação | 2 | todo | [ISSUE-F2-01-004-CONFIGURAR-ROTAS-DASHBOARD-E-PROTECAO-DE-AUTENTICACAO.md](./issues/ISSUE-F2-01-004-CONFIGURAR-ROTAS-DASHBOARD-E-PROTECAO-DE-AUTENTICACAO.md) |

## Artifact Minimo do Epico

- `frontend/src/config/dashboardManifest.ts`
- `frontend/src/components/dashboard/DashboardLayout.tsx`
- `frontend/src/pages/dashboard/DashboardHome.tsx`

## Dependencias

- [PRD](../PRD-DASHBOARD-LEADS-ETARIA.md)
- [Fase](./F2_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [Decision Protocol](../DECISION-PROTOCOL.md)

## Notas de Implementacao Globais

- A arquitetura deve ser genérica o suficiente para acomodar dashboards de qualquer
domínio (leads, eventos, publicidade) sem alteração no layout
- Evitar acoplamento entre o manifesto e componentes específicos de análise
- O manifesto é configuração estática — não vem da API nesta versão

## Navegacao Rapida

- `[[./issues/ISSUE-F2-01-001-CRIAR-MANIFESTO-DE-DASHBOARDS-NO-FRONTEND]]`
- `[[./issues/ISSUE-F2-01-002-IMPLEMENTAR-DASHBOARDLAYOUT-COM-SIDEBAR-DE-NAVEGACAO]]`
- `[[./issues/ISSUE-F2-01-003-IMPLEMENTAR-DASHBOARDHOME-SELETOR-VISUAL-DE-ANALISES]]`
- `[[./issues/ISSUE-F2-01-004-CONFIGURAR-ROTAS-DASHBOARD-E-PROTECAO-DE-AUTENTICACAO]]`
- `[[../PRD-DASHBOARD-LEADS-ETARIA]]`
