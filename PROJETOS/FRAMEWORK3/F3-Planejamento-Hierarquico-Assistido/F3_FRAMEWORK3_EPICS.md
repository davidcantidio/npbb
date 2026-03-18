---
doc_id: "F3_FRAMEWORK3_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
audit_gate: "not_ready"
---

# Epicos - FRAMEWORK3 / F3 - Planejamento Hierarquico Assistido

## Objetivo da Fase

Cobrir o fluxo de planejamento do FRAMEWORK3 desde intake e PRD ate issues tasks e artefatos Markdown canonicos com gates HITL.

## Gate de Saida da Fase

Um projeto novo consegue passar de intake ate tasks required aprovadas com historico completo aprovacoes rastreaveis e artefatos sincronizados.

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`

## Checklist de Transicao de Gate

> A semantica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [ ] todos os epicos estao `done`
- [ ] todas as issues filhas estao `done`
- [ ] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F3-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F3-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F3-01 | Intake e PRD Assistidos com Aprovacao | Cobrir intake e PRD com gates explicitos de aprovacao e rastreabilidade de origem. | F2 concluida | todo | [EPIC-F3-01-Intake-e-PRD-Assistidos-com-Aprovacao.md](./EPIC-F3-01-Intake-e-PRD-Assistidos-com-Aprovacao.md) |
| EPIC-F3-02 | Planejamento de Fases, Epicos e Sprints | Gerar e aprovar fases epicos e sprints respeitando os limites canonicos do framework. | EPIC-F3-01 | todo | [EPIC-F3-02-Planejamento-de-Fases-Epicos-e-Sprints.md](./EPIC-F3-02-Planejamento-de-Fases-Epicos-e-Sprints.md) |
| EPIC-F3-03 | Planejamento de Issues, Tasks e Instrucoes TDD | Gerar issues canonicas em pasta tasks required e instrucoes TDD com bloqueio de elegibilidade. | EPIC-F3-02 | todo | [EPIC-F3-03-Planejamento-de-Issues-Tasks-e-Instrucoes-TDD.md](./EPIC-F3-03-Planejamento-de-Issues-Tasks-e-Instrucoes-TDD.md) |
| EPIC-F3-04 | Historico de Aprovacoes e Artefatos Canonicos | Persistir prompts outputs aprovacoes evidencias e estado de sincronizacao dos artefatos gerados durante o planejamento. | EPIC-F3-01 EPIC-F3-02 EPIC-F3-03 | todo | [EPIC-F3-04-Historico-de-Aprovacoes-e-Artefatos-Canonicos.md](./EPIC-F3-04-Historico-de-Aprovacoes-e-Artefatos-Canonicos.md) |

## Dependencias entre Epicos

- `EPIC-F3-01`: F2 concluida
- `EPIC-F3-02`: EPIC-F3-01
- `EPIC-F3-03`: EPIC-F3-02
- `EPIC-F3-04`: EPIC-F3-01 e EPIC-F3-02 e EPIC-F3-03

## Escopo desta Fase

### Dentro
- intake e PRD assistidos com aprovacao explicita
- geracao e aprovacao de fases epicos sprints issues e tasks
- materializacao de historico aprovacoes e artefatos Markdown canonicos

### Fora
- execucao sequencial das tasks por orquestrador
- review pos-issue e follow-ups operacionais
- auditoria de fase e rollout do modulo

## Definition of Done da Fase
- [ ] passos 1 a 15 do algoritmo refletidos no modulo
- [ ] issues novas geradas em pasta com `task_instruction_mode: required`
- [ ] historico e estado de sincronizacao visiveis e persistidos
