---
doc_id: "US-4-06-SUPERFICIE-CONCILIACAO-BLOQUEIOS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS"
decision_refs: []
---

# US-4-06 - Superficie de conciliacao e indicadores de bloqueio

## User Story

**Como** operador,
**quero** telas que mostrem divergencia planejado versus recebido e indicadores claros de bloqueio por recebimento,
**para** executar a conciliacao sem depender de planilhas paralelas (manifesto FEATURE-4 sec. 2 e 6).

## Feature de Origem

- **Feature**: FEATURE-4 - Recebimento, conciliacao e bloqueios por ticketeira
- **Comportamento coberto**: UI / superficie de ativos e ingressos para conciliacao e visibilidade de bloqueios; reforco operacional dos criterios de aceite 1–3 e trilha visivel para a operacao.

## Contexto Tecnico

- Consome APIs e regras de [US-4-02](../US-4-02-REGISTRO-RECEBIDO-CONFIRMADO/README.md), [US-4-03](../US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL/README.md) e [US-4-04](../US-4-04-BLOQUEIO-POR-RECEBIMENTO/README.md).
- Frontend React/Vite existente do projeto NPBB; padroes de dashboard alinhados ao modulo Ativos quando aplicavel.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** dados de planejado e recebido para um contexto de evento/categoria,
  **when** o operador abre a vista de conciliacao,
  **then** ve divergencia e totais coerentes com o backend (US-4-03).
- **Given** itens em `bloqueado_por_recebimento`,
  **when** a lista ou detalhe e carregada,
  **then** o motivo do bloqueio e visivel e atualiza apos novo recebimento (US-4-04).
- **Given** permissao de operador,
  **when** regista recebimento pela UI (se previsto no desenho),
  **then** o fluxo respeita validacoes do US-4-02 e deixa trilha utilizavel (US-4-01/auditoria).

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [TASK-1.md](./TASK-1.md) — Rotas, submenu Ativos e shell operacional
- [TASK-2.md](./TASK-2.md) — Vista de conciliacao planejado vs recebido
- [TASK-3.md](./TASK-3.md) — Vista de bloqueios por recebimento
- [TASK-4.md](./TASK-4.md) — Registo de recebimento na UI (condicional ao desenho)
- [TASK-5.md](./TASK-5.md) — Validacao de aceite e evidencias

## Arquivos Reais Envolvidos

- `frontend/` rotas e componentes de ativos/ingressos
- [FEATURE-4.md](../../FEATURE-4.md)

## Artefato Minimo

- Fluxos de UI entregues e validados contra APIs de recebimento, saldo e bloqueio.

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

- [FEATURE-4](../../FEATURE-4.md)
- [PRD ATIVOS-INGRESSOS](../../../../PRD-ATIVOS-INGRESSOS.md)
- Outras USs (backend / contrato): [US-4-02](../US-4-02-REGISTRO-RECEBIDO-CONFIRMADO/README.md), [US-4-03](../US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL/README.md), [US-4-04](../US-4-04-BLOQUEIO-POR-RECEBIMENTO/README.md) — estado dos manifestos pode estar `todo`; a execucao funcional desta US fica **bloqueada** ate APIs e regras dessas US estarem disponiveis (ver `precondicoes` em cada `TASK-*.md`).
- [GOV-USER-STORY.md](../../../../COMUM/GOV-USER-STORY.md)

## Navegacao Rapida

- [US-4-04](../US-4-04-BLOQUEIO-POR-RECEBIMENTO/README.md)
- [FEATURE-4](../../FEATURE-4.md)
