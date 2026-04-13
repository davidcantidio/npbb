---
doc_id: "AUDIT-LOG.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-04-12"
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
| [FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD](features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD.md) | approved | FEATURE-1-R01 | [RELATORIO-AUDITORIA-F1-R01.md](features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/auditorias/RELATORIO-AUDITORIA-F1-R01.md) | R01 aprovada em `2026-04-12`; `DRIFT_INDICE` registrado por preflight `exit 12`; nenhum follow-up bloqueante; projeto apto para encerramento. |

## Resolucoes de Follow-ups

| Data | Audit ID de Origem | Feature | Follow-up | Destino Final | Resumo | Ref | Observacoes |
|---|---|---|---|---|---|---|---|
| nenhum | - | - | - | - | - | - | - |

## Rodadas

| Audit ID | Feature | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FEATURE-1-R01 | FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD | 2026-04-12 | gpt-5-codex | d1414d0c288eeb0be8364658cc41962d51d9b283 | - | go | done | [RELATORIO-AUDITORIA-F1-R01.md](features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/auditorias/RELATORIO-AUDITORIA-F1-R01.md) | `M-01` e `M-02` em warn nao bloqueante; limitacao ETL sem `batch_id` mantida documentada | - | - | - |
