---
doc_id: "F1_OPENCLAW-MIGRATION_EPICS.md"
version: "1.3"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
audit_gate: "approved"
---

# Epicos - OPENCLAW-MIGRATION / F1 - Remediacao hold MIGRATION-R01

## Objetivo da Fase

Fechar os follow-ups bloqueantes do veredito `hold` da auditoria MIGRATION-R01, entregando artefactos corretivos em `PROJETOS/COMUM/` rastreados como issues `ISSUE-F1-01-00x`.

## Gate de Saida da Fase

Nova auditoria da migracao (ou feature equivalente) com veredito `go` ou follow-ups remanescentes explicitamente nao bloqueantes.

## Estado do Gate de Auditoria

- gate_atual: `approved`
- ultima_auditoria: MIGRATION-R02
- veredito_atual: `go`
- relatorio_mais_recente: [RELATORIO-AUDITORIA-MIGRATION-R02.md](../auditorias/RELATORIO-AUDITORIA-MIGRATION-R02.md)
- log_do_projeto: [AUDIT-LOG.md](../AUDIT-LOG.md)

## Checklist de Transicao de Gate

> A semantica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `hold -> pending` (remediacao)

- [x] todas as issues F1-01-001 a F1-01-004 concluidas (`done`) ou renegociadas por escrito no AUDIT-LOG
- [x] `AUDIT-LOG.md` com coluna Ref apontando para pastas `ISSUE-*`

### `pending -> approved`

- [x] existe relatorio de auditoria com veredito `go` para o escopo da migracao
- [x] `AUDIT-LOG.md` actualizado com o veredito

## Epicos

| ID | Nome | Objetivo | Feature | Depende de | Status | Arquivo |
|---|---|---|---|---|---|---|
| EPIC-F1-01 | Remediacao hold R01 | Implementar B1-B4 do relatorio MIGRATION-R01 nos artefactos centrais. | Migracao (spec) | nenhuma | done | [EPIC-F1-01-REMEDIACAO-HOLD-MIGRATION-R01.md](./EPIC-F1-01-REMEDIACAO-HOLD-MIGRATION-R01.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma

## Escopo desta Fase

### Dentro

- `TEMPLATE-USER-STORY.md`, `boot-prompt.md`, superficie SESSION/GOV conforme B3 e B4
- Rastreio no AUDIT-LOG e issues F1

### Fora

- Implementacao de codigo de produto fora de `PROJETOS/COMUM/` e skills

## Definition of Done da Fase

- [x] Quatro issues de remediacao executadas e revisadas conforme governanca
- [x] Hold R01 tratado documentalmente; proxima auditoria agendada ou registada
- [x] Indice SQLite sincronizado apos ultima gravacao em PROJETOS
