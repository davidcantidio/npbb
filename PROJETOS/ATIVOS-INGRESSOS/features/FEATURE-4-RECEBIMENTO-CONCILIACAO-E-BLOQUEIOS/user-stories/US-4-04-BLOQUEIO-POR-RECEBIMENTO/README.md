---
doc_id: "US-4-04-BLOQUEIO-POR-RECEBIMENTO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS"
decision_refs: []
---

# US-4-04 - Estado bloqueado por recebimento

## User Story

**Como** operacao,
**quero** que aumentos dependentes de ticketeira fiquem em `bloqueado_por_recebimento` ate existir recebimento correspondente,
**para** cumprir o guardrail do PRD 2.6 e o criterio de aceite da feature item 3.

## Feature de Origem

- **Feature**: FEATURE-4 - Recebimento, conciliacao e bloqueios por ticketeira
- **Comportamento coberto**: aplicacao do estado `bloqueado_por_recebimento` e transicao para desbloqueio quando o recebimento for confirmado.

## Contexto Tecnico

- Depende da distincao entre aumento dependente de origem externa e outros ajustes (alinhamento com US-4-05 para leituras separadas).
- Observabilidade: eventos de negocio correlacionaveis com FEATURE-2 quando aplicavel.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** um pedido de aumento dependente de ticketeira sem recebimento que o cubra,
  **when** o fluxo de ajuste e avaliado,
  **then** o item permanece bloqueado com motivo `bloqueado_por_recebimento` (ou equivalente persistido).
- **Given** o recebimento correspondente registado (US-4-02),
  **when** a conciliacao reconhecer cobertura,
  **then** o bloqueio e levantado de forma auditavel e o aumento pode prosseguir conforme regras de saldo (US-4-03).
- **Given** um aumento que nao depende de ticketeira,
  **when** avaliado pelo mesmo pipeline,
  **then** nao e indevidamente bloqueado por esta regra.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [TASK-1 — Contrato persistido para bloqueio por recebimento](./TASK-1.md)
- [TASK-2 — Avaliacao de pipeline: bloquear aumento dependente sem recebimento](./TASK-2.md)
- [TASK-3 — Desbloqueio auditavel quando a conciliacao reconhece cobertura](./TASK-3.md)
- [TASK-4 — Testes de dominio e evidencia no README da US](./TASK-4.md)

## Arquivos Reais Envolvidos

- Dominio de ajustes/bloqueios e APIs afetas em `backend/`
- [FEATURE-4.md](../../FEATURE-4.md)

## Artefato Minimo

- Comportamento de bloqueio e desbloqueio coberto por testes de dominio e documentado.

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
- Outras USs: [US-4-02](../US-4-02-REGISTRO-RECEBIDO-CONFIRMADO/README.md) `done`; [US-4-03](../US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL/README.md) `done` recomendado
- [GOV-USER-STORY.md](../../../../COMUM/GOV-USER-STORY.md)

## Navegacao Rapida

- [US-4-03](../US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL/README.md)
- [FEATURE-4](../../FEATURE-4.md)
