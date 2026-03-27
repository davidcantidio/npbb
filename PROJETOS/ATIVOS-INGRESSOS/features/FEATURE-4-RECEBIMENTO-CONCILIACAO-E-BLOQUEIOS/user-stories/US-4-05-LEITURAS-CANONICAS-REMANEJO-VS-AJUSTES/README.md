---
doc_id: "US-4-05-LEITURAS-CANONICAS-REMANEJO-VS-AJUSTES"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS"
decision_refs: []
---

# US-4-05 - Leituras canonicas remanejado versus ajustes

## User Story

**Como** produto ou arquiteto,
**quero** leituras separadas que nao misturem **remanejado** com aumento ou reducao,
**para** fechar o modelo canonico citado no PRD sec. 3 / 2.6 e o criterio de aceite da feature item 4.

## Feature de Origem

- **Feature**: FEATURE-4 - Recebimento, conciliacao e bloqueios por ticketeira
- **Comportamento coberto**: implementacao ou contratos de consulta que expoem remanejado isolado de aumento, reducao e saldo nao distribuido; ADR ou documento vinculado (manifesto FEATURE-4 sec. 10).

## Contexto Tecnico

- Pode incluir ADR sob `docs/` ou pasta acordada pelo projeto mais ajustes em agregacoes/API.
- Alinhamento com dashboard operacional (FEATURE-8) como consumidor futuro das mesmas leituras.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** eventos de remanejamento e de aumento/reducao no mesmo evento/categoria,
  **when** um cliente interno consulta as leituras canonicas,
  **then** remanejado aparece em medida propria e nao e agregado indevidamente a aumento ou reducao.
- **Given** a necessidade de auditoria,
  **when** o ADR ou doc de modelo canonico e publicado,
  **then** define mapeamento entre entidades persistidas e cada leitura exposta.
- **Given** as consultas existentes de saldo,
  **when** comparadas ao ADR,
  **then** nao ha contradicao silenciosa com US-4-03 e US-4-04.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [TASK-1.md](./TASK-1.md) — ADR do modelo canonico de leituras (entidades → dimensoes expostas)
- [TASK-2.md](./TASK-2.md) — Leituras canonicas no dominio (servico/consultas)
- [TASK-3.md](./TASK-3.md) — Contrato estavel de API (schemas + rota)
- [TASK-4.md](./TASK-4.md) — Testes automatizados e checklist vs US-4-03 / US-4-04

## Arquivos Reais Envolvidos

- ADR ou documento de modelo; consultas/API em `backend/`
- [FEATURE-4.md](../../FEATURE-4.md)

## Artefato Minimo

- ADR (ou equivalente) mais implementacao ou contratos de leitura aderentes.

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
- Outras USs: [US-4-03](../US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL/README.md) `done` recomendado
- [GOV-USER-STORY.md](../../../../COMUM/GOV-USER-STORY.md)

## Navegacao Rapida

- [US-4-03](../US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL/README.md)
- [FEATURE-4](../../FEATURE-4.md)
