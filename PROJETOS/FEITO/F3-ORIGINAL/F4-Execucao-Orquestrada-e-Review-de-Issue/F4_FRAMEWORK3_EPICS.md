---
doc_id: "F4_FRAMEWORK3_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
audit_gate: "not_ready"
---

# Epicos - FRAMEWORK3 / F4 - Execucao Orquestrada e Review de Issue

## Objetivo da Fase

Cobrir a selecao da proxima task a execucao sequencial por issue o review pos-issue e a sincronizacao de estado do FRAMEWORK3.

## Gate de Saida da Fase

O modulo seleciona a proxima unidade executavel monta work order valida preflight executa tasks em sequencia registra review e mantem a cascata de estados coerente.

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
- [ ] existe `RELATORIO-AUDITORIA-F4-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F4-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F4-01 | Selecao da Unidade Executavel e Work Order | Escolher a proxima task elegivel montar o execution scope e barrar preflights invalidos antes da execucao. | F3 concluida | todo | [EPIC-F4-01-Selecao-da-Unidade-Executavel-e-Work-Order.md](./EPIC-F4-01-Selecao-da-Unidade-Executavel-e-Work-Order.md) |
| EPIC-F4-02 | Execucao Sequencial de Tasks por Orquestrador | Rodar tasks em sequencia por issue registrar evidencias minimas e tratar retry e stop conditions. | EPIC-F4-01 | todo | [EPIC-F4-02-Execucao-Sequencial-de-Tasks-por-Orquestrador.md](./EPIC-F4-02-Execucao-Sequencial-de-Tasks-por-Orquestrador.md) |
| EPIC-F4-03 | Review Pos-Issue e Follow-ups | Registrar review pos-issue com veredito canonico e materializar follow-ups rastreaveis quando necessario. | EPIC-F4-02 | todo | [EPIC-F4-03-Review-Pos-Issue-e-Follow-ups.md](./EPIC-F4-03-Review-Pos-Issue-e-Follow-ups.md) |
| EPIC-F4-04 | Sincronizacao de Estado e Notificacao HITL | Sincronizar a cascata issue epic fase sprint apos execucao e review e expor proxima acao nos gates obrigatorios. | EPIC-F4-02 EPIC-F4-03 | todo | [EPIC-F4-04-Sincronizacao-de-Estado-e-Notificacao-HITL.md](./EPIC-F4-04-Sincronizacao-de-Estado-e-Notificacao-HITL.md) |

## Dependencias entre Epicos

- `EPIC-F4-01`: F3 concluida
- `EPIC-F4-02`: EPIC-F4-01
- `EPIC-F4-03`: EPIC-F4-02
- `EPIC-F4-04`: EPIC-F4-02 e EPIC-F4-03

## Escopo desta Fase

### Dentro
- selecao da proxima task elegivel e preparacao da sessao operacional
- loop sequencial de execucao de tasks por issue com evidencias e stop conditions
- review pos-issue follow-ups e sincronizacao de estado com notificacao HITL

### Fora
- auditoria formal de fase e remediacao de hold
- dataset treinavel e export consolidado
- rollout piloto e onboarding de legados

## Definition of Done da Fase
- [ ] passos 16 a 23 do algoritmo refletidos no modulo
- [ ] issue fecha apenas com review e rastreabilidade minima por task
- [ ] proxima acao e estados derivados permanecem coerentes apos follow-up
