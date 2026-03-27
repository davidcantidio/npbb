---
doc_id: "US-8-02-NAVEGACAO-DASHBOARD-ATIVOS-RBAC"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
task_instruction_mode: "required"
feature_id: "FEATURE-8"
decision_refs: []
---

# US-8-02 - Navegacao Dashboard Ativos e shell com RBAC

## User Story

**Como** utilizador autorizado ao modulo Dashboard,
**quero** uma entrada **Dashboard > Ativos** (ou equivalente acordado) com rota dedicada e permissoes alinhadas ao resto do produto,
**para** aceder a visao operacional de ativos sem contornar RBAC e com layout coerente com o dashboard de leads.

## Feature de Origem

- **Feature**: FEATURE-8 (Dashboard de ativos operacional)
- **Comportamento coberto**: nova entrada de navegacao, rota sob o modulo Dashboard, RBAC consistente, shell/estados de carregamento e estrutura visual alinhados ao padrao ja homologado (PRD 2.6, 6; manifesto FEATURE-8 sec. 2).

## Contexto Tecnico

- Reutilizar padroes de `frontend/src/components/dashboard/` (ex.: `DashboardLayout`, manifest de entradas em `frontend/src/config/dashboardManifest.ts`).
- Nao redesenhar o modulo Dashboard fora do padrao de leads.
- O shell pode renderizar estados vazios ou placeholders ate integracao completa dos widgets na US-8-03; a navegacao e RBAC sao o foco desta US.

## Plano TDD (opcional no manifesto da US)

- **Red**: a definir nas tasks (testes de rota/RBAC ou de layout conforme stack).
- **Green**: a definir nas tasks.
- **Refactor**: a definir nas tasks.

## Criterios de Aceitacao (Given / When / Then)

- **Given** um utilizador com permissao para o dashboard de ativos,
  **when** acede ao menu do Dashboard,
  **then** existe entrada visivel para **Ativos** (ou nome equivalente fechado na implementacao) que navega para a rota correta.
- **Given** um utilizador sem permissao,
  **when** tenta aceder diretamente a rota do dashboard de ativos,
  **then** o sistema nega acesso de forma consistente com o RBAC do modulo Dashboard (sem vazamento de dados).
- **Given** a rota carregada,
  **when** o utilizador autorizado a observa,
  **then** o layout respeita o padrao estrutural/visual do dashboard de leads (sidebar, outlet, hierarquia de navegacao).

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [TASK-1.md](./TASK-1.md) — Domínio Ativos no manifesto e sidebar
- [TASK-2.md](./TASK-2.md) — Rotas aninhadas e página shell
- [TASK-3.md](./TASK-3.md) — RBAC: visibilidade e bloqueio de rota direta
- [TASK-4.md](./TASK-4.md) — Testes automatizados (navegação e RBAC)

## Arquivos Reais Envolvidos

- `frontend/src/config/dashboardManifest.ts` — registo da entrada do dashboard
- `frontend/src/components/dashboard/` — layout e navegacao
- Rotas da aplicacao que montam o outlet do Dashboard (ex.: router principal em `frontend/src/`)

## Artefato Minimo

- Navegacao funcional **Dashboard > Ativos** com RBAC aplicado
- Rota acessivel e integrada ao layout do dashboard de leads

## Handoff para Revisao Pos-User Story

status: nao_iniciado
base_commit: nao_informado
target_commit: nao_informado
evidencia: nao_informado
commits_execucao: []
validacoes_executadas: []
arquivos_de_codigo_relevantes: []
limitacoes: []

## Dependencias

- [Manifesto da feature](../../FEATURE-8.md)
- [PRD do projeto](../../../../PRD-ATIVOS-INGRESSOS.md) — secs. 2.4, 2.6, 4.1, 6
- [Intake](../../../../INTAKE-ATIVOS-INGRESSOS.md)
- Outras USs: nenhuma (integracao de dados agregados na US-8-03 apos [US-8-01](../US-8-01-AGREGACOES-E-ENDPOINTS-DASHBOARD-ATIVOS/README.md))
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
