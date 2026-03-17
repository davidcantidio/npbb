---
doc_id: "AUDIT-LOG.md"
version: "1.4"
status: "active"
owner: "PM"
last_updated: "2026-03-17"
---

# AUDIT-LOG - DASHBOARD-LEADS

## Politica

- toda auditoria formal deve gerar relatorio versionado por fase em `auditorias/`
- toda rodada deve registrar commit base, veredito e categoria dos achados materiais
- auditoria `hold` abre follow-ups rastreaveis
- follow-up pode ter destino `issue-local`, `new-intake` ou `cancelled`
- auditoria `go` e pre-requisito para mover fase a `feito/`
- cada resolucao de follow-up deve registrar o `Audit ID de Origem` da rodada
  `hold` que gerou o item

## Gate Atual por Fase

| Fase | Estado do Gate | Ultima Auditoria | Relatorio Mais Recente | Observacoes |
|---|---|---|---|---|
| preencher |  |  |  |  |

## Resolucoes de Follow-ups

| Data | Audit ID de Origem | Fase | Follow-up | Destino Final | Resumo | Ref | Observacoes |
|---|---|---|---|---|---|---|---|

> Em `Ref`, para `issue-local`, apontar para a pasta `ISSUE-*/` ou para
> `README.md` quando a issue for granularizada; usar `ISSUE-*.md` apenas para
> legado.

## Rodadas

| Audit ID | Fase | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nenhum | - | - | - | - | - | - | - | - | - | - | - | - |
