---
doc_id: "US-8-04-SERIE-TEMPORAL-OCORRENCIAS-E-METRICAS-PRD"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
task_instruction_mode: "required"
feature_id: "FEATURE-8"
decision_refs: []
---

# US-8-04 - Serie temporal, ocorrencias e metricas PRD 2.5

## User Story

**Como** diretoria ou operacao,
**quero** acompanhamento por data, um painel minimo de ocorrencias/problemas e exposicao de metricas leading/lagging acordadas no PRD,
**para** operar um evento real com visibilidade temporal e indicadores de negocio sem depender de planilha paralela como fonte de verdade.

## Feature de Origem

- **Feature**: FEATURE-8 (Dashboard de ativos operacional)
- **Comportamento coberto**: acompanhamento por data; painel de ocorrencias/problemas no **escopo minimo v1** (drill-down detalhado pode seguir decisao UX — Intake sec. 14 — sem bloquear o minimo PRD); mapeamento de pelo menos parte das metricas **leading/lagging** do PRD 2.5 para widget(s) e/ou **export** quando dados existirem (criterio de aceite 5 da feature).

## Contexto Tecnico

- Depende dos widgets base da [US-8-03](../US-8-03-WIDGETS-DIMENSOES-OPERACIONAIS/README.md).
- Backend pode estender agregacoes temporais ou export sobre os contratos da [US-8-01](../US-8-01-AGREGACOES-E-ENDPOINTS-DASHBOARD-ATIVOS/README.md) — detalhe nas tasks.
- Lacunas PRD sec. 3: documentar em `limitacoes` do handoff qualquer recorte v1 fechado em implementacao (ex.: lista resumida de problemas vs. drill-down completo TBD).

## Plano TDD (opcional no manifesto da US)

- **Red**: testes de API em [TASK-1.md](TASK-1.md) e [TASK-3.md](TASK-3.md) (`tdd_aplicavel: true`).
- **Green**: implementacao minima dos endpoints nas mesmas tasks.
- **Refactor**: apos green, mantendo suites verdes; UI (T2, T4, T5) sem TDD obrigatorio no manifesto.

## Criterios de Aceitacao (Given / When / Then)

- **Given** um evento com historico ou pontos temporais disponiveis na API,
  **when** o utilizador aplica filtro ou eixo temporal acordado,
  **then** o dashboard apresenta **acompanhamento por data** coerente com os dados agregados (sem inconsistencia com as oito dimensoes da US-8-03).
- **Given** problemas operacionais registados no dominio,
  **when** o utilizador abre o painel de ocorrencias/problemas,
  **then** ve um **minimo v1** util (ex.: contagem, lista resumida ou ultimos incidentes — fechado nas tasks) **sem** exigir drill-down profundo fechado no Intake 14 como bloqueio desta US.
- **Given** dados suficientes para metricas leading ou lagging do PRD 2.5,
  **when** o utilizador utiliza o dashboard ou export,
  **then** **pelo menos uma** metrica leading **ou** lagging documentada no PRD 2.5 aparece mapeada em widget dedicado ou export (CSV/planilha/API de export conforme decisao nas tasks), com legenda ou documentacao do mapeamento.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

Ordem sugerida: **T1** → (**T2** e **T3** apos T1) → **T4** apos T3 → **T5** apos T2 e T4.

- [TASK-1.md](TASK-1.md) — API read-only: serie temporal / agregacao por data
- [TASK-2.md](TASK-2.md) — UI: filtro e eixo temporal (`depends_on`: T1)
- [TASK-3.md](TASK-3.md) — API read-only: resumo de problemas por evento (`depends_on`: T1)
- [TASK-4.md](TASK-4.md) — UI: painel minimo de ocorrencias/problemas (`depends_on`: T3)
- [TASK-5.md](TASK-5.md) — Metrica PRD 2.5 + widget/export + handoff `limitacoes` (`depends_on`: T2, T4)

## Arquivos Reais Envolvidos

- `frontend/src/` — componentes de serie temporal, painel de problemas, export UI
- `backend/app/` — endpoints ou parametros de agregacao temporal/export se necessario
- `backend/tests/` — testes alinhados aos novos contratos

## Artefato Minimo

- Vista com dimensao temporal utilizavel no dashboard de ativos
- Painel minimo de problemas conforme criterios acima
- Um canal (widget ou export) demonstrando mapeamento PRD 2.5 quando dados existirem

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
- [PRD do projeto](../../../../PRD-ATIVOS-INGRESSOS.md) — secs. 2.5, 2.6, 3, 4.1
- [Intake](../../../../INTAKE-ATIVOS-INGRESSOS.md) — sec. 14 (drill-down TBD)
- Outras USs: [US-8-03](../US-8-03-WIDGETS-DIMENSOES-OPERACIONAIS/README.md) — **pre-requisito** (deve estar `done` antes da execucao desta US; estado atual no manifesto da US-8-03 prevalece)
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
