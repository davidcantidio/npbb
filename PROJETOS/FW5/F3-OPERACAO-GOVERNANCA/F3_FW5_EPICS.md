---
doc_id: "F3_FW5_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
audit_gate: "not_ready"
---

# Epicos - FW5 / F3 - Operacao e governanca

## Objetivo da Fase

Permitir execucao assistida, governanca de qualidade e consulta completa do historico operacional.

## Features Entregues

- Feature 4: Execucao assistida da proxima unidade elegivel
- Feature 5: Governanca final percebida pelo PM

## Gate de Saida da Fase

O sistema executa a proxima unidade elegivel com autonomia controlada, suporta review/auditoria e expoe trilha auditavel de ponta a ponta.

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`
- veredito_atual: `nao_aplicavel`
- relatorio_mais_recente: `PROJETOS/FW5/F3-OPERACAO-GOVERNANCA/auditorias/RELATORIO-AUDITORIA-F3-R01.md`
- log_do_projeto: [PROJETOS/FW5/AUDIT-LOG.md](PROJETOS/FW5/AUDIT-LOG.md)

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

| ID | Nome | Objetivo | Feature | Depende de | Status | Arquivo |
|---|---|---|---|---|---|---|
| EPIC-F3-01 | Execucao assistida com autonomia controlada | Selecionar a proxima unidade elegivel, montar contexto de execucao e aplicar politica de autonomia/HITL. | Feature 4 | F2 aprovada | todo | [EPIC-F3-01-EXECUCAO-ASSISTIDA-COM-AUTONOMIA-CONTROLADA.md](./EPIC-F3-01-EXECUCAO-ASSISTIDA-COM-AUTONOMIA-CONTROLADA.md) |
| EPIC-F3-02 | Governanca final e historico auditavel | Review pos-issue, gate de auditoria, follow-ups e timeline consultavel. | Feature 5 | EPIC-F3-01 | todo | [EPIC-F3-02-GOVERNANCA-FINAL-E-HISTORICO-AUDITAVEL.md](./EPIC-F3-02-GOVERNANCA-FINAL-E-HISTORICO-AUDITAVEL.md) |

## Dependencias entre Epicos

- `EPIC-F3-01`: F2 aprovada
- `EPIC-F3-02`: EPIC-F3-01

## Escopo desta Fase

### Dentro
- selecao da proxima unidade elegivel e montagem do work order
- politica de autonomia, override humano e evidencias operacionais
- review pos-issue, gate de auditoria, follow-ups e timeline auditavel

### Fora
- migracao em massa de projetos legados
- fine-tuning real de LLM
- mobile ou multi-tenancy avancado

## Definition of Done da Fase
- [ ] elegibilidade e execucao respeitam dependencias, gates e work order
- [ ] review e auditoria conseguem produzir veredito e follow-up rastreavel
- [ ] timeline operacional e evidencias sao consultaveis pelo PM
