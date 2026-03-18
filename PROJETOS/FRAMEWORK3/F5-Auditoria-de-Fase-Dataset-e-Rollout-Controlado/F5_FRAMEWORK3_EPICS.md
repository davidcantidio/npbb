---
doc_id: "F5_FRAMEWORK3_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
audit_gate: "not_ready"
---

# Epicos - FRAMEWORK3 / F5 - Auditoria de Fase Dataset e Rollout Controlado

## Objetivo da Fase

Fechar o ciclo do FRAMEWORK3 com auditoria formal de fase dataset treinavel historico exportavel e piloto controlado de rollout.

## Gate de Saida da Fase

O modulo consegue auditar a fase registrar hold ou go materializar follow-ups extrair dataset treinavel e validar um piloto end-to-end com criterios de rollout.

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
- [ ] existe `RELATORIO-AUDITORIA-F5-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F5-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F5-01 | Auditoria de Fase e Remediacao de Hold | Formalizar a auditoria de fase registrar gate persistido e orquestrar remediacao quando a auditoria entrar em hold. | F4 concluida | todo | [EPIC-F5-01-Auditoria-de-Fase-e-Remediacao-de-Hold.md](./EPIC-F5-01-Auditoria-de-Fase-e-Remediacao-de-Hold.md) |
| EPIC-F5-02 | Dataset de Treinamento e Observabilidade | Definir o recorte treinavel do historico do FRAMEWORK3 e expor consulta export auditavel e telemetria minima. | F4 concluida | todo | [EPIC-F5-02-Dataset-de-Treinamento-e-Observabilidade.md](./EPIC-F5-02-Dataset-de-Treinamento-e-Observabilidade.md) |
| EPIC-F5-03 | Rollout Coexistencia e Piloto Operacional | Fechar a politica de coexistencia com legados e validar um piloto end-to-end antes de ampliar o uso do modulo. | EPIC-F5-01 EPIC-F5-02 | todo | [EPIC-F5-03-Rollout-Coexistencia-e-Piloto-Operacional.md](./EPIC-F5-03-Rollout-Coexistencia-e-Piloto-Operacional.md) |

## Dependencias entre Epicos

- `EPIC-F5-01`: F4 concluida
- `EPIC-F5-02`: F4 concluida
- `EPIC-F5-03`: EPIC-F5-01 e EPIC-F5-02

## Escopo desta Fase

### Dentro
- auditoria de fase relatorio gate persistido e remediacao de hold
- dataset treinavel telemetria e export auditavel do historico
- coexistencia com projetos legados onboarding e piloto controlado

### Fora
- expansao irrestrita para todos os projetos do repositorio
- migracao em massa de backlog legado
- infraestrutura externa adicional nao prevista no PRD

## Definition of Done da Fase
- [ ] passos 24 a 27 do algoritmo refletidos no modulo
- [ ] AUDIT-LOG e relatorios passam a ser o gate real da conclusao de fase
- [ ] criterios de rollout ficam fechados apos validacao de piloto
