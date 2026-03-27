---
doc_id: "US-8-01-AGREGACOES-E-ENDPOINTS-DASHBOARD-ATIVOS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
task_instruction_mode: "required"
feature_id: "FEATURE-8"
decision_refs: []
---

# US-8-01 - Agregacoes read-only e endpoints do dashboard de ativos

## User Story

**Como** equipa de produto e engenharia,
**quero** exposicao read-only de agregacoes operacionais de ativos por evento (e dimensoes alinhadas ao PRD),
**para** alimentar o modulo Dashboard com leituras consistentes, testaveis e performaticas sem duplicar fonte de verdade.

## Feature de Origem

- **Feature**: FEATURE-8 (Dashboard de ativos operacional)
- **Comportamento coberto**: modelagem read-only (views materializadas ou queries agregadas conforme necessario), endpoints de agregacao alinhados ao padrao do dashboard de leads, testes de API e preocupacoes de performance descritas no manifesto da feature (secs. 6 e 7).

## Contexto Tecnico

- Depende do dominio entregue por **FEATURE-2**, **FEATURE-4** e **FEATURE-6** (dados de planejado, recebido, bloqueado, distribuicao, remanejamento, ajustes e problemas).
- Backend FastAPI; sem alterar semantica de negocio — apenas leituras agregadas. Cache opcional conforme manifesto.
- Contrato de resposta deve permitir que o frontend replique o padrao de consumo do dashboard de leads (`frontend/src/config/dashboardManifest.ts`, componentes sob `frontend/src/components/dashboard/`).

## Plano TDD (opcional no manifesto da US)

- **Red**: a definir nas tasks (testes de API falhando para contratos de agregacao).
- **Green**: a definir nas tasks.
- **Refactor**: a definir nas tasks.

## Criterios de Aceitacao (Given / When / Then)

- **Given** evento e parametros de filtro suportados pelo contrato (ex.: evento, diretoria/area v1),
  **when** um cliente autorizado chama os endpoints de agregacao do dashboard de ativos,
  **then** a resposta expoe valores agregados distinguindo **planejado, recebido, bloqueado, distribuido, remanejado, aumentado, reduzido** e **problemas**, sem misturar remanejado com aumento/reducao (PRD 2.6).
- **Given** ausencia de dados para uma dimensao num evento,
  **when** o endpoint e invocado,
  **then** o comportamento e documentado e estavel (ex.: zeros ou colecoes vazias), sem erro 500 por falta de linhas agregadas.
- **Given** a suíte de testes de API do backend,
  **when** a US for concluida,
  **then** existem testes automatizados cobrindo contrato e casos limite acordados nas tasks.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

Desdobramento em `PROJETOS/COMUM/SESSION-DECOMPOR-US-EM-TASKS.md` / `PROMPT-US-PARA-TASKS.md`.

- [T1 — Contrato Pydantic e alinhamento ao padrao dashboard de leads](./TASK-1.md)
- [T2 — Estrategia read-only no banco (views ou queries documentadas)](./TASK-2.md)
- [T3 — Servico de agregacao read-only](./TASK-3.md)
- [T4 — Router FastAPI e registro no app](./TASK-4.md)
- [T5 — Testes de API: contrato, dimensoes e ausencia de dados](./TASK-5.md)

## Arquivos Reais Envolvidos

- `backend/app/` — routers, servicos ou schemas novos ou estendidos para agregacoes read-only
- `backend/alembic/` — quando views ou objetos de leitura exigirem migracao
- `backend/tests/` — testes de API das agregacoes
- Referencia de padrao UI/consumo: `frontend/src/components/dashboard/`, `frontend/src/config/dashboardManifest.ts`

## Artefato Minimo

- Endpoints documentados (OpenAPI ou doc interna) consumiveis pelo frontend do dashboard de ativos
- Evidencia de testes de API passando para o contrato acordado

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
- [PRD do projeto](../../../../PRD-ATIVOS-INGRESSOS.md) — secs. 2.4–2.6, 4.1
- [Intake](../../../../INTAKE-ATIVOS-INGRESSOS.md)
- Features dominio: [FEATURE-2](../../../FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md), [FEATURE-4](../../../FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/FEATURE-4.md), [FEATURE-6](../../../FEATURE-6-DISTRIBUICAO-REMANEJAMENTO-AJUSTES-PROBLEMAS/FEATURE-6.md)
- Outras USs: nenhuma
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
