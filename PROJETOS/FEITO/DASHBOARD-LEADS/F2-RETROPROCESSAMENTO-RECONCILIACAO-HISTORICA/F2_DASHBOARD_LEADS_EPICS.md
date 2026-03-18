---
doc_id: "F2_DASHBOARD_LEADS_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
audit_gate: "not_ready"
---

# Epicos - DASHBOARD-LEADS / F2 - RETROPROCESSAMENTO E RECONCILIACAO HISTORICA

## Objetivo da Fase

Materializar historico resolvivel em `LeadEvento`, separar casos ambiguos e formalizar o fallback operacional via bronze/reprocessamento.

## Gate de Saida da Fase

O backfill reexecuta sem duplicar, os casos nao resolvidos ficam rastreaveis e o fallback operacional via bronze fica documentado e conectado aos artefatos atuais.

## Gate de Auditoria da Fase

- estado_do_gate: `not_ready`
- ultima_auditoria: `nao_aplicavel`
- veredito_atual: `nao_aplicavel`
- relatorio_mais_recente: `nao_aplicavel`
- log_do_projeto: [AUDIT-LOG](../../AUDIT-LOG.md)

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F2-01 | Backfill idempotente multi-origem | Expor execucao controlada do backfill de `LeadEvento` a partir das tres fontes previstas no PRD. | F1 concluida | todo | [EPIC-F2-01-BACKFILL-IDEMPOTENTE-MULTI-ORIGEM.md](./EPIC-F2-01-BACKFILL-IDEMPOTENTE-MULTI-ORIGEM.md) |
| EPIC-F2-02 | Reconciliacao de casos ambiguos e nao resolvidos | Separar os casos historicos nao resolvidos e permitir fechamento manual controlado. | EPIC-F2-01 | todo | [EPIC-F2-02-RECONCILIACAO-DE-CASOS-AMBIGUOS-E-NAO-RESOLVIDOS.md](./EPIC-F2-02-RECONCILIACAO-DE-CASOS-AMBIGUOS-E-NAO-RESOLVIDOS.md) |
| EPIC-F2-03 | Protocolo de fallback via bronze | Traduzir o fallback via bronze/reprocessamento em criterio operacional executavel sobre as superfices ja existentes. | EPIC-F2-02 | todo | [EPIC-F2-03-PROTOCOLO-DE-FALLBACK-VIA-BRONZE.md](./EPIC-F2-03-PROTOCOLO-DE-FALLBACK-VIA-BRONZE.md) |

## Dependencias entre Epicos

- `EPIC-F2-01`: F1 concluida
- `EPIC-F2-02`: EPIC-F2-01
- `EPIC-F2-03`: EPIC-F2-02

## Escopo desta Fase

### Dentro

- implementar runner de backfill idempotente multi-origem
- testar precedencia e upgrade de `source_kind`
- emitir relatorio de reconciliacao para `missing` e `ambiguous`
- formalizar fechamento `manual_reconciled`
- definir protocolo de fallback via bronze/reprocessamento

### Fora

- mudanca de payload frontend
- desativacao final das heuristicas remanescentes

## Definition of Done da Fase

- [ ] backfill multi-origem reexecuta sem duplicidade por `(lead_id, evento_id)`
- [ ] casos `missing` e `ambiguous` geram artefato rastreavel
- [ ] `manual_reconciled` fica definido como caminho explicito de fechamento
- [ ] criterio de fallback via bronze/reprocessamento fica documentado e conectado aos artefatos atuais

## Navegacao Rapida

- [Intake](../../INTAKE-DASHBOARD-LEADS.md)
- [PRD](../../PRD-DASHBOARD-LEADS.md)
- [Audit Log](../../AUDIT-LOG.md)
- [EPIC-F2-01](./EPIC-F2-01-BACKFILL-IDEMPOTENTE-MULTI-ORIGEM.md)
- [EPIC-F2-02](./EPIC-F2-02-RECONCILIACAO-DE-CASOS-AMBIGUOS-E-NAO-RESOLVIDOS.md)
- [EPIC-F2-03](./EPIC-F2-03-PROTOCOLO-DE-FALLBACK-VIA-BRONZE.md)
