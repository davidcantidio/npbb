---
doc_id: "US-6-02-REMANEJAMENTO-AUDITAVEL"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-6"
decision_refs: []
---

# US-6-02 - Remanejamento auditavel

## User Story

**Como** operador de ativos de ingressos,
**quero** registrar remanejamento entre areas, categorias ou destinatarios com historico consultavel,
**para** comprovar apenas realocacao efetiva (sem confundir com ajuste de previsao) e atender auditoria.

## Feature de Origem

- **Feature**: FEATURE-6 (Distribuicao, remanejamento, ajustes e problemas operacionais)
- **Comportamento coberto**: estado `remanejado`; trilha auditavel; motivo de remanejamento quando exigido pelo PRD ou pelo intake.

## Contexto Tecnico

- Semantica PRD: `remanejado` e somente realocacao efetiva (PRD 2.3 / 2.6).
- Modelagem: eventos de dominio ou tabelas de historico de remanejamento; transacoes consistentes no backend.
- UX: reduzir risco de confusao com aumento/reducao de previsao (risco explicitado no manifesto da feature).

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel no manifesto
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** ativos ja alocados de forma que remanejamento seja permitido pelas regras do dominio,
  **when** o operador executa um remanejamento valido,
  **then** o historico registra origem, destino, quantidade, instante e ator; o estado `remanejado` (ou leitura equivalente) fica consultavel.
- **Given** politica de motivo obrigatorio (quando PRD ou intake exigirem),
  **when** o operador tenta remanejar sem motivo,
  **then** a operacao e bloqueada ate preenchimento valido.
- **Given** consulta de auditoria por evento ou lote,
  **when** um revisor lista remanejamentos,
  **then** a cadeia de eventos e navegavel sem misturar com registros puramente de aumento ou reducao de previsao.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

Desdobrar em ate **5** tasks por US (`GOV-USER-STORY.md`) na etapa `SESSION-DECOMPOR-US-EM-TASKS.md`.

- [TASK-1.md](./TASK-1.md) — Modelo persistido e migracao para historico de remanejamento
- [TASK-2.md](./TASK-2.md) — Servico de dominio e API de registo de remanejamento
- [TASK-3.md](./TASK-3.md) — API de listagem e consulta de auditoria de remanejamentos
- [TASK-4.md](./TASK-4.md) — UI operacional: remanejamento e auditoria
- [TASK-5.md](./TASK-5.md) — Validacao integrada e checklist dos criterios Given/When/Then

## Arquivos Reais Envolvidos

- Modelo de dados e migracoes de remanejamento
- `backend/app/routers/ingressos.py` e servicos relacionados
- UI operacional (portal / admin)
- `test_ingressos_endpoints` ou equivalentes

## Artefato Minimo

- API ou persistencia com listagem/consulta de historico de remanejamento e testes cobrindo registro e leitura.

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
- Outras USs: [US-6-01](../US-6-01-DISTRIBUICAO-RESPEITANDO-SALDO-DISPONIVEL/README.md) deve estar `done` antes da execucao (base de distribuicao e alocacao coerente)
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
