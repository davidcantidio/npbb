---
doc_id: "US-6-04-PROBLEMAS-OPERACIONAIS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
task_instruction_mode: "required"
feature_id: "FEATURE-6"
decision_refs: []
---

# US-6-04 - Registro e listagem de problemas operacionais

## User Story

**Como** operador de eventos,
**quero** criar e listar ocorrencias operacionais por evento,
**para** acompanhar incidentes e alimentar o painel de problemas da FEATURE-8 sem planilhas paralelas.

## Feature de Origem

- **Feature**: FEATURE-6 (Distribuicao, remanejamento, ajustes e problemas operacionais)
- **Comportamento coberto**: estado `problema_registrado`; campos minimos para dashboard; visibilidade por evento.

## Contexto Tecnico

- Persistencia de ocorrencias com ligacao ao evento (e entidades relacionadas conforme modelo existente).
- API e UI para criacao e listagem; contrato de leitura preparado para agregacao no dashboard (FEATURE-8).
- Observabilidade: correlation_id quando aplicavel, alinhado ao manifesto da feature.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel no manifesto
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** um evento operacional existente,
  **when** o operador registra um problema com os campos minimos acordados (tipo, descricao, referencia ao evento, instante),
  **then** o registro persiste como `problema_registrado` (ou equivalente) e fica listavel.
- **Given** varios problemas em eventos distintos,
  **when** a listagem e filtrada por evento,
  **then** apenas ocorrencias daquele evento sao retornadas, com paginacao ou limite documentado.
- **Given** consumo futuro pelo dashboard,
  **when** a FEATURE-8 consumir a fonte de dados,
  **then** os campos expostos sao suficientes para o painel de ocorrencias sem duplicar logica ad hoc.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

| Task | Documento |
|------|-----------|
| T1 | [TASK-1.md](TASK-1.md) — Migration e modelo SQLModel |
| T2 | [TASK-2.md](TASK-2.md) — Schemas e endpoints API (criar + listar por evento) |
| T3 | [TASK-3.md](TASK-3.md) — Testes de API (pytest) |
| T4 | [TASK-4.md](TASK-4.md) — UI operacional |
| T5 | [TASK-5.md](TASK-5.md) — Contrato FEATURE-8 e observabilidade |

## Arquivos Reais Envolvidos

- Migracoes para entidade de problema operacional
- Backend `ingressos.py` / servicos e routers dedicados se necessario
- UI operacional para criacao e listagem
- Testes de API

## Artefato Minimo

- CRUD ou fluxo equivalente (criar + listar por evento) com testes automatizados e campos alinhados ao PRD.

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
- Outras USs: [US-6-01](../US-6-01-DISTRIBUICAO-RESPEITANDO-SALDO-DISPONIVEL/README.md) — pre-requisito de **escopo** (evento e operacao alinhados). Estado atual do manifesto US-6-01: `todo`. Pela [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md), a **execucao** desta US so e elegivel com US-6-01 em `done` (ou revisao explicita de dependencia pelo PM).
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
