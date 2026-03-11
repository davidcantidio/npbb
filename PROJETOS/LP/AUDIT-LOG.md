---
doc_id: "AUDIT-LOG.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-11"
---

# AUDIT-LOG - LP

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
| F1 | not_ready | nao_aplicavel | nao_aplicavel | Aguardando primeira auditoria formal |
| F2 | not_ready | nao_aplicavel | nao_aplicavel | Aguardando primeira auditoria formal |
| F3 | not_ready | nao_aplicavel | nao_aplicavel | Aguardando primeira auditoria formal |
| F4 | not_ready | nao_aplicavel | nao_aplicavel | Aguardando primeira auditoria formal |

## Resolucoes de Follow-ups

| Data | Audit ID de Origem | Fase | Follow-up | Destino Final | Resumo | Ref | Observacoes |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

## Rodadas

| Audit ID | Fase | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nenhum | - | - | - | - | - | - | - | - | - | - | - | - |
