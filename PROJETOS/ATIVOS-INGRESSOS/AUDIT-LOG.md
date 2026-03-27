---
doc_id: "AUDIT-LOG.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
---

# AUDIT-LOG - ATIVOS-INGRESSOS

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
| [FEATURE-1-FOUNDATION](features/FEATURE-1-FOUNDATION/FEATURE-1.md) | not_ready | nao_aplicavel | [RELATORIO-AUDITORIA-F1-R01.md](features/FEATURE-1-FOUNDATION/auditorias/RELATORIO-AUDITORIA-F1-R01.md) | O ficheiro em `auditorias/` e um shell com `status: planned`; nao ha veredito canonico ate haver auditoria real concluida e registo coerente neste log. Scaffold inicial gerado. |

## Resolucoes de Follow-ups

| Data | Audit ID de Origem | Feature | Follow-up | Destino Final | Resumo | Ref | Observacoes |
|---|---|---|---|---|---|---|---|
| nenhum | - | - | - | - | - | - | - |

## Rodadas

| Audit ID | Feature | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nenhum | - | - | - | - | - | - | - | - | - | - | - | - |
