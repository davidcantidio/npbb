---
doc_id: "US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS"
decision_refs: []
---

# US-4-03 - Prevalencia do recebido e teto distribuivel

## User Story

**Como** operacao,
**quero** que o sistema aplique a prevalencia do recebido confirmado para origem ticketeira e limite o saldo distribuivel ao recebido,
**para** que nunca se distribua acima do efetivamente conciliado quando houver divergencia face ao planejado (PRD 2.4).

## Feature de Origem

- **Feature**: FEATURE-4 - Recebimento, conciliacao e bloqueios por ticketeira
- **Comportamento coberto**: calculo/exposicao de divergencia planejado vs recebido; teto de `disponivel` para fornecimento externo; criterio de aceite da feature item 2.

## Contexto Tecnico

- Regras centralizadas em servicos de dominio de saldo (manifesto FEATURE-4 sec. 7).
- Cenarios de teste: planejado maior que recebido; recebido maior que planejado; ausencia de recebimento.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** origem ticketeira com planejado e recebido diferentes,
  **when** o sistema calcula o saldo distribuivel,
  **then** o teto efetivo segue o **recebido confirmado** (prevalencia do recebido).
- **Given** um contexto com recebimento registado,
  **when** um operador ou API consulta a divergencia,
  **then** planejado, recebido e delta sao apresentados de forma auditavel.
- **Given** ausencia total de recebido confirmado para um lote externo,
  **when** se pede distribuicao,
  **then** o saldo distribuivel para essa origem nao excede zero (ou politica explicita documentada se houver excecao controlada).

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [TASK-1.md](./TASK-1.md) — Servico de dominio: prevalencia do recebido e teto distribuivel
- [TASK-2.md](./TASK-2.md) — Integrar teto distribuivel nos fluxos de listagem e solicitacao
- [TASK-3.md](./TASK-3.md) — API de leitura da divergencia planejado vs recebido
- [TASK-4.md](./TASK-4.md) — Testes de integracao dos tres criterios Given/When/Then

## Arquivos Reais Envolvidos

- Servicos de dominio e consultas de saldo em `backend/`
- [FEATURE-4.md](../../FEATURE-4.md)

## Artefato Minimo

- Regras implementadas e testadas para prevalencia do recebido e teto distribuivel.

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
- Outras USs: [US-4-02](../US-4-02-REGISTRO-RECEBIDO-CONFIRMADO/README.md) `todo` *(predecessora; deve estar `done` antes da execucao de codigo desta US)*
- [GOV-USER-STORY.md](../../../../COMUM/GOV-USER-STORY.md)

## Navegacao Rapida

- [US-4-02](../US-4-02-REGISTRO-RECEBIDO-CONFIRMADO/README.md)
- [FEATURE-4](../../FEATURE-4.md)
