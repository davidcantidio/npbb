---
doc_id: "AUDIT-LOG.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
---

# AUDIT-LOG - NPBB

## Politica

- toda auditoria formal deve gerar relatorio versionado por feature em `features/FEATURE-*/auditorias/`
- toda rodada deve registrar commit base, veredito e categoria dos achados materiais
- auditoria `hold` abre follow-ups rastreaveis
- follow-up pode ter destino `same-feature`, `new-intake` ou `cancelled`
- auditoria `go` e pre-requisito para encerrar a feature
- cada resolucao de follow-up deve registrar o `Audit ID de Origem` da rodada `hold` que gerou o item

## Gate Atual por Feature

| Feature | Estado do Gate | Ultima Auditoria | Relatorio Mais Recente | Observacoes |
|---|---|---|---|---|
| [FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD](features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD.md) | not_ready | nao_aplicavel | [RELATORIO-AUDITORIA-F1-R01.md](features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/auditorias/RELATORIO-AUDITORIA-F1-R01.md) | Rodada inicial planejada para a feature piloto real do `npbb`. O projeto ja esta no layout atual e o gate continua fechado ate a primeira execucao/revisao da US. |

## Resolucoes de Follow-ups

| Data | Audit ID de Origem | Feature | Follow-up | Destino Final | Resumo | Ref | Observacoes |
|---|---|---|---|---|---|---|---|
| nenhum | - | - | - | - | - | - | - |

## Rodadas

| Audit ID | Feature | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nenhum | - | - | - | - | - | - | - | - | - | - | - | - |
