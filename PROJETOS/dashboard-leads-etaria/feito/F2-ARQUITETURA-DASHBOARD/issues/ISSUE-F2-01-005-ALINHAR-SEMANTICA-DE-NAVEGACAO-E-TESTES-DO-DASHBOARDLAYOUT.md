---
doc_id: "ISSUE-F2-01-005-ALINHAR-SEMANTICA-DE-NAVEGACAO-E-TESTES-DO-DASHBOARDLAYOUT.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-08"
task_instruction_mode: "required"
---

# ISSUE-F2-01-005 - Alinhar semantica de navegacao e testes do DashboardLayout

## User Story

Como engenheiro de frontend do dashboard, quero alinhar a semantica de navegacao do
`DashboardLayout/DashboardSidebar` com os testes da arquitetura para remover o `hold`
da auditoria F2-R02 sem ampliar escopo funcional da fase.

## Contexto Tecnico

A auditoria F2-R02 identificou falha bloqueante de semantica/acessibilidade na sidebar
do dashboard. O pacote `DashboardLayout.test.tsx` falha ao buscar o landmark de
navegacao esperado (`role="navigation"` com nome acessivel).

O ajuste deve ser contido ao escopo da fase F2, preservando comportamento de portal,
fallback inline e drawer mobile.

## Plano TDD

- Red: reproduzir as 2 falhas do `DashboardLayout.test.tsx`.
- Green: ajustar markup/contrato para os testes passarem sem regressao de layout.
- Refactor: consolidar semantica e nomes acessiveis sem criar rotas/feature novas.

## Criterios de Aceitacao

- [ ] Sidebar do dashboard expõe landmark de navegacao com nome acessivel estavel.
- [ ] Cenario com `app-sidebar-slot` e cenario fallback inline passam no `DashboardLayout.test.tsx`.
- [ ] Comportamento mobile continua usando slot de sidebar do `AppLayout` sem duplicacao.
- [ ] Nao ha regressao em `DashboardHome.test.tsx` e `DashboardModule.test.tsx`.

## Definition of Done da Issue

- [ ] Criterios de aceitacao validados por testes locais
- [ ] Ajuste documentado no arquivo da issue e vinculado ao `RELATORIO-AUDITORIA-F2-R02`
- [ ] Nenhum desvio adicional de escopo introduzido na fase F2

## Tarefas Decupadas

- [ ] T1: Revisar o markup atual de `DashboardSidebar`/`DashboardLayout` para definir o landmark de navegacao.
- [ ] T2: Ajustar componente para expor semantica acessivel consistente nos modos portal e fallback.
- [ ] T3: Atualizar/estabilizar assercoes de teste se houver drift nominal justificado.
- [ ] T4: Reexecutar pacote de testes F2 (`DashboardLayout`, `DashboardHome`, `DashboardModule`).

## Instructions por Task

### T1 - Revisar contrato de navegacao

1. Validar no DOM qual elemento deve carregar `role="navigation"` e `aria-label`.
2. Preservar `aside` como container apenas quando semanticamente adequado.

### T2 - Ajustar componente

1. Aplicar o landmark de navegacao no ponto unico de renderizacao da sidebar.
2. Garantir que o nome acessivel permaneça identico entre portal e fallback.

### T3 - Alinhar testes

1. Se o componente mudar nomes visiveis, manter o matcher dos testes baseado em nome acessivel estavel.
2. Nao afrouxar testes a ponto de perder cobertura do achado da auditoria.

### T4 - Validar regressao

1. Rodar `DashboardLayout.test.tsx`, `DashboardHome.test.tsx` e `DashboardModule.test.tsx`.
2. Registrar resultado observado na issue para fechamento.

## Arquivos Reais Envolvidos

- `frontend/src/components/dashboard/DashboardLayout.tsx`
- `frontend/src/components/dashboard/DashboardSidebar.tsx`
- `frontend/src/components/dashboard/__tests__/DashboardLayout.test.tsx`

## Artifact Minimo

- `frontend/src/components/dashboard/DashboardSidebar.tsx`

## Dependencias

- [Epic](../EPIC-F2-01-LAYOUT-E-MANIFESTO-DASHBOARDS.md)
- [Fase](../F2_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [Auditoria](../auditorias/RELATORIO-AUDITORIA-F2-R02.md)

## Navegacao Rapida

- `[[../EPIC-F2-01-LAYOUT-E-MANIFESTO-DASHBOARDS]]`
- `[[../auditorias/RELATORIO-AUDITORIA-F2-R02]]`
