---
doc_id: "US-8-03-WIDGETS-DIMENSOES-OPERACIONAIS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-8"
decision_refs: []
---

# US-8-03 - Widgets das oito dimensoes operacionais

## User Story

**Como** diretoria ou operacao,
**quero** graficos e tabelas no dashboard de ativos que mostrem claramente cada dimensao operacional,
**para** acompanhar saldos e movimentos sem ambiguidade entre remanejamento e ajustes (aumento/reducao).

## Feature de Origem

- **Feature**: FEATURE-8 (Dashboard de ativos operacional)
- **Comportamento coberto**: leituras **distintas** para planejado, recebido, bloqueado, distribuido, remanejado, aumentado, reduzido e problemas; mesmos padroes de componente do dashboard de leads; filtros por evento e dimensoes v1 (Area equivalente a Diretoria conforme PRD 2.6).

## Contexto Tecnico

- Consome os endpoints definidos na [US-8-01](../US-8-01-AGREGACOES-E-ENDPOINTS-DASHBOARD-ATIVOS/README.md).
- Superficie entregue na [US-8-02](../US-8-02-NAVEGACAO-DASHBOARD-ATIVOS-RBAC/README.md) (rota e layout).
- Frontend React/Vite; reutilizar patterns de cards, graficos e tabelas do dashboard de leads onde existirem.

## Plano TDD (opcional no manifesto da US)

- **Red**: a definir nas tasks (testes de componente ou contrato de integracao).
- **Green**: a definir nas tasks.
- **Refactor**: a definir nas tasks.

## Criterios de Aceitacao (Given / When / Then)

- **Given** um evento selecionado e dados agregados disponiveis,
  **when** o utilizador autorizado abre o dashboard de ativos,
  **then** existem visualizacoes separadas para **planejado, recebido, bloqueado, distribuido, remanejado, aumentado, reduzido** e **problemas**, cada uma com rotulo e dados coerentes com o contrato da API.
- **Given** a restricao do PRD 2.6,
  **when** os widgets sao revistos,
  **then** **remanejado** nao mistura semantica com aumento nem reducao (leituras distintas).
- **Given** o guardrail de design (PRD 6),
  **when** a pagina e comparada ao dashboard de leads,
  **then** nao ha redesign do modulo Dashboard fora do padrao homologado.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

> Desdobramento em `PROJETOS/COMUM/SESSION-DECOMPOR-US-EM-TASKS.md` / `PROMPT-US-PARA-TASKS.md`. Nesta etapa **nao** existem ficheiros `TASK-*.md`.

- (pendente de decomposicao em tasks)

## Arquivos Reais Envolvidos

- `frontend/src/` — paginas ou modulos do dashboard de ativos, servicos HTTP
- `frontend/src/components/dashboard/` — reutilizacao de componentes
- Contrato alinhado ao backend entregue na US-8-01

## Artefato Minimo

- Pagina do dashboard de ativos com oito dimensoes operacionais visiveis e alinhadas ao contrato de API

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
- Outras USs: [US-8-01](../US-8-01-AGREGACOES-E-ENDPOINTS-DASHBOARD-ATIVOS/README.md) **done**, [US-8-02](../US-8-02-NAVEGACAO-DASHBOARD-ATIVOS-RBAC/README.md) **done**
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
