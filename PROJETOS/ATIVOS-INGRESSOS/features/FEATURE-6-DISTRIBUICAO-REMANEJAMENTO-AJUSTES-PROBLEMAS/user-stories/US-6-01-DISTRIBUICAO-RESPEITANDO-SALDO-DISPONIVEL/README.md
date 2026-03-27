---
doc_id: "US-6-01-DISTRIBUICAO-RESPEITANDO-SALDO-DISPONIVEL"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
task_instruction_mode: "required"
feature_id: "FEATURE-6"
decision_refs: []
---

# US-6-01 - Distribuicao respeitando saldo disponivel

## User Story

**Como** operador de ativos de ingressos,
**quero** registrar distribuicao efetiva ao destinatario com validacao de saldo,
**para** nunca distribuir acima do `disponivel` derivado do recebido confirmado em origem externa (FEATURE-4).

## Feature de Origem

- **Feature**: FEATURE-6 (Distribuicao, remanejamento, ajustes e problemas operacionais)
- **Comportamento coberto**: distribuicao com bloqueio quando saldo disponivel insuficiente; estado `distribuido` rastreavel (incl. reenvios quando no escopo da feature).

## Contexto Tecnico

- Dependencias de feature: FEATURE-2, FEATURE-3, FEATURE-4, FEATURE-5 (saldo `disponivel` e emissao interna).
- Camadas: migracoes para eventos/tabelas de distribuicao se necessario; backend `ingressos.py` e servicos; UI `IngressosPortal` e admin; testes em `test_ingressos_endpoints`.
- Integracao opcional com email de saida para notificacoes nao altera a regra de bloqueio por saldo.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel no manifesto; detalhar em tasks quando `tdd_aplicavel: true`.
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** origem externa com saldo `disponivel` inferior a quantidade solicitada na distribuicao,
  **when** o operador confirma a distribuicao,
  **then** a operacao e rejeitada com mensagem clara e nenhuma alteracao inconsistente de estoque.
- **Given** saldo `disponivel` suficiente,
  **when** a distribuicao e concluida,
  **then** o estado reflete `distribuido` (ou equivalente acordado) com trilha auditavel associada ao destinatario e ao evento/categoria.
- **Given** ingresso interno emitido conforme FEATURE-5,
  **when** a distribuicao e registrada,
  **then** as regras de emissao e de saldo interno nao sao violadas nas transacoes persistidas.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [TASK-1 — Modelo e migracoes: persistencia de distribuicao e trilha minima](./TASK-1.md)
- [TASK-2 — Dominio e API: validar disponivel, transacao e resposta HTTP](./TASK-2.md)
- [TASK-3 — UI portal e admin: confirmar distribuicao e erros de saldo](./TASK-3.md)
- [TASK-4 — Testes de integracao e evidencia dos criterios Given/When/Then](./TASK-4.md)

## Arquivos Reais Envolvidos

- `backend/app/routers/ingressos.py` (ou modulo equivalente)
- Servicos de dominio de ingressos / ativos
- `frontend/` — portal e fluxos admin de distribuicao
- Testes `test_ingressos_endpoints` (ou suite alinhada)
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` — estados e restricoes de origem externa

## Artefato Minimo

- Fluxo de distribuicao persistido com validacao de `disponivel` para origem externa e evidencia em testes automatizados.

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

- [FEATURE-6](../../FEATURE-6.md)
- [PRD do projeto](../../../../PRD-ATIVOS-INGRESSOS.md)
- Outras USs: nenhuma (prerequisitos sao FEATURE-2 a FEATURE-5)
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
