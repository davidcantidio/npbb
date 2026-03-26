---
doc_id: "AUDIT-LOG.md"
version: "2.1"
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
| nenhuma | aguardando decomposicao `PRD -> Features` | nao_aplicavel | nao_aplicavel | Nenhuma feature foi criada ainda; este log passa a registrar gates reais apenas apos a decomposicao do PRD aprovado. |

## Resolucoes de Follow-ups

| Data | Audit ID de Origem | Feature | Follow-up | Destino Final | Resumo | Ref | Observacoes |
|---|---|---|---|---|---|---|---|
| nenhum | - | - | - | - | - | - | - |

## Rodadas

| Audit ID | Feature | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nenhum | - | - | - | - | - | - | - | - | - | - | - | - |
