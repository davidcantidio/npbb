---
doc_id: "US-2-02-MODELO-E-MIGRACOES-INICIAIS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-2"
decision_refs: []
---

# US-2-02 - Modelo canonico inicial e migracoes seguras

## User Story

Como engenheiro de backend,
quero introduzir o esqueleto de entidades e migracoes alinhado ao PRD sec. 4.1
(e Intake sec. 10) sem violar unicidade e comportamento atual de
`CotaCortesia`,
para que FEATURE-3 e seguintes tenham base persistida e rollback compativel com
o PRD sec. 8.

## Feature de Origem

- **Feature**: FEATURE-2 (Dominio, coexistencia com legado e rollout)
- **Comportamento coberto**: criterio de aceite 3; estrategia de implementacao
  item 1 (modelagem e migration); comportamento esperado sobre modelo canonico
  inicial e migracao versionada.

## Contexto Tecnico

Alembic/SQLModel no monolito NPBB; tabelas e constraints novas nao devem
apagar dados reconciliados em cenario de rollback salvo decisao documentada.
Preservar contratos existentes para eventos nao migrados. Impacto em
`backend/app/models/models.py` e migracoes sob `backend/alembic/`.

## Plano TDD (opcional no manifesto da US)

- **Red**: testes ou migracao em dry-run que exponham violacao de integridade ou
  perda de dados em rollback *(detalhar em TASKs)*
- **Green**: migracao `upgrade`/`downgrade` validada; modelos carregando sem
  regressao nos fluxos legados cobertos
- **Refactor**: ajustes de indices/nomenclatura mantendo compatibilidade

## Criterios de Aceitacao (Given / When / Then)

- **Given** o estado atual de `CotaCortesia` e tabelas relacionadas,
  **when** a migracao `upgrade` e aplicada,
  **then** o esqueleto do novo dominio existe sem remover linhas necessarias ao
  legado e sem quebrar unicidade documentada no PRD 4.0.
- **Given** um cenario de rollback alinhado ao PRD sec. 8,
  **when** `downgrade` (ou procedimento equivalente) e executado,
  **then** dados reconciliados nao sao eliminados de forma irreversivel salvo
  decisao explicitamente documentada.
- **Given** o codigo de modelo,
  **when** os testes de regressao baseline forem executados,
  **then** nenhuma falha e introduzida nos contratos de listagem e atribuicao
  descritos no PRD 4.0 para o fluxo agregado *(evidencia complementada em
  US-2-05)*.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

*(Desdobramento em `TASK-*.md` na etapa `SESSION-DECOMPOR-US-EM-TASKS.md` /
`PROMPT-US-PARA-TASKS.md`. Nenhuma task criada nesta sessao.)*

## Arquivos Reais Envolvidos

- `backend/app/models/models.py`
- `backend/alembic/versions/` *(novas revisoes)*
- `backend/alembic/env.py`
- `PROJETOS/ATIVOS-INGRESSOS/INTAKE-ATIVOS-INGRESSOS.md` *(sec. 10)*

## Artefato Minimo

- Revisao Alembic aplicavel + modelos SQLModel para esqueleto do dominio alvo,
  com nota de rollback no PR ou ADR quando houver excecao ao criterio de
  preservacao de dados.

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

- [Manifesto FEATURE-2](../../FEATURE-2.md)
- [PRD ATIVOS-INGRESSOS](../../../../PRD-ATIVOS-INGRESSOS.md)
- Outras USs: [US-2-01 - ADR e convivencia](../US-2-01-ADR-E-COEXISTENCIA/README.md)
  *(recomendado para alinhar decisoes de transicao; nao bloqueante se ADR
  estiver em rascunho acordado)*
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
