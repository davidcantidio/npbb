---
doc_id: "US-6-03-AJUSTES-PREVISAO-VS-REMANEJAMENTO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-6"
decision_refs: []
---

# US-6-03 - Ajustes de previsao separados de remanejamento

## User Story

**Como** operador ou gestor de ativos,
**quero** que aumentos e reducoes de previsao ou estoque aparecam como leituras distintas de remanejamento,
**para** relatorios e APIs refletirem corretamente PRD 2.6 e o risco de mistura semantica.

## Feature de Origem

- **Feature**: FEATURE-6 (Distribuicao, remanejamento, ajustes e problemas operacionais)
- **Comportamento coberto**: leituras **aumentado** e **reduzido** separadas de **remanejado** em API ou views acordadas.

## Contexto Tecnico

- PRD distingue `aumentado`, `reduzido` e `remanejado`; o manifesto da feature aponta PRD 2.6 e risco em sec. 5.
- Implementacao pode envolver views materializadas, endpoints dedicados ou agregacoes documentadas; o contrato precisa ser explicito para consumo pelo dashboard (FEATURE-8) e integracoes.
- Convivencia com legado e tratada em US-6-05; esta US foca no contrato canonico.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel no manifesto
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** um conjunto de eventos que inclui remanejamento, aumento de previsao e reducao,
  **when** um consumidor chama a API ou view acordada para cada leitura,
  **then** `aumentado`, `reduzido` e `remanejado` nao contam os mesmos movimentos de forma duplicada ou ambigua.
- **Given** documentacao do contrato (OpenAPI, ADR curto ou secao em spec interna),
  **when** um desenvolvedor integra o cliente,
  **then** fica explicito qual endpoint ou campo corresponde a cada semantica.
- **Given** cenarios de teste com sobreposicao temporal de operacoes,
  **when** os testes automatizados executam,
  **then** as agregacoes respeitam as regras de separacao acordadas com produto.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [TASK-1 — Contrato de consumo (API/view vs semantica PRD)](./TASK-1.md)
- [TASK-2 — Servico de agregacao no dominio F6](./TASK-2.md)
- [TASK-3 — Exposicao HTTP e schemas (OpenAPI FastAPI)](./TASK-3.md)
- [TASK-4 — Testes automatizados e sobreposicao temporal](./TASK-4.md)

## Arquivos Reais Envolvidos

- Servicos de leitura / agregacao no backend
- Possiveis migracoes para campos ou tabelas de ajuste
- Testes de contrato de API ou de views
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` — sec. 2.3 e 2.6

## Artefato Minimo

- Superficie acordada (API ou views) com testes que provam separacao entre `aumentado`, `reduzido` e `remanejado`.

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
- Outras USs: [US-6-01](../US-6-01-DISTRIBUICAO-RESPEITANDO-SALDO-DISPONIVEL/README.md) `done`; alinhamento recomendado com [US-6-02](../US-6-02-REMANEJAMENTO-AUDITAVEL/README.md) para modelo de eventos coerente
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
