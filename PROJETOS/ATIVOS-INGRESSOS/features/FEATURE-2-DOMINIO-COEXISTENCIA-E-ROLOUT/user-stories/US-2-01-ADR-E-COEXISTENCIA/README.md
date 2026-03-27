---
doc_id: "US-2-01-ADR-E-COEXISTENCIA"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-27"
task_instruction_mode: "optional"
feature_id: "FEATURE-2"
decision_refs: []
---

# US-2-01 - ADR e convivencia legado versus novo dominio

## User Story

Como equipa tecnica,
quero documentacao viva (ou ADR) que descreva a convivencia entre o modelo
agregado atual (`CotaCortesia` / `SolicitacaoIngresso`) e o novo dominio ate o
rollout,
para que implementacoes e revisoes alinhem-se ao baseline e ao plano de
transicao sem ambiguidade.

## Feature de Origem

- **Feature**: FEATURE-2 (Dominio, coexistencia com legado e rollout)
- **Comportamento coberto**: criterio de aceite 1 — documentacao de convivencia
  com referencia explicita ao baseline em `PRD-ATIVOS-INGRESSOS.md` sec. 4.0.

## Contexto Tecnico

O PRD fixa baseline em 4.0 (rotas `/ativos`, `/ingressos`, modelos em
`models.py`) e rollout gradual por evento (sec. 4.1, 8). O manifesto da feature
referencia `backend/docs/auditoria_eventos/ATIVOS_STATE_NOW.md` e documentacao
de auditoria em `docs/auditoria_eventos/`. O ADR ou doc viva deve cruzar estes
pontos sem duplicar o PRD como lista de backlog.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel (artefato documental)
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** o baseline descrito no PRD sec. 4.0,
  **when** um desenvolvedor abre o ADR ou documento de convivencia,
  **then** o texto explica explicitamente o que permanece no modelo agregado e o
  que pertence ao novo dominio ate o corte de rollout.
- **Given** o documento publicado no repositorio,
  **when** a equipa valida rastreabilidade,
  **then** ha ligacao clara ao `PRD-ATIVOS-INGRESSOS.md` sec. 4.0 e, quando
  util, aos anexos citados no manifesto da FEATURE-2.
- **Given** decisoes de transicao (ex.: dual-read, feature gate por evento),
  **when** o ADR as registra,
  **then** os leitores identificam criterio de ativacao e impacto em rotas
  existentes sem contradizer o PRD sec. 8.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [TASK-1.md](./TASK-1.md) — local, nome e esqueleto do ADR
- [TASK-2.md](./TASK-2.md) — legado agregado versus novo dominio
- [TASK-3.md](./TASK-3.md) — transicao, gate por evento e impacto em rotas
- [TASK-4.md](./TASK-4.md) — rastreabilidade e checklist de aceite

## Arquivos Reais Envolvidos

- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md`
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md`
- `backend/docs/auditoria_eventos/ATIVOS_STATE_NOW.md` *(referencia)*
- `docs/auditoria_eventos/RESTORE_ATIVOS_SUMMARY.md` *(referencia)*
- ADR canónico (TASK-1): `docs/adr/ATIVOS-INGRESSOS-coexistencia-legado-e-novo-dominio.md`

## Artefato Minimo

- ADR ou documento markdown versionado descrevendo convivencia legado/novo
  dominio com referencia ao PRD sec. 4.0.

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
- [Intake](../../../../INTAKE-ATIVOS-INGRESSOS.md)
- Outras USs: nenhuma *(recomenda-se concluir antes ou em paralelo a
  implementacao pesada de US-2-02 para orientar codigo)*
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
