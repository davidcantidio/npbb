---
doc_id: "AUDIT-LOG.md"
version: "1.4"
status: "active"
owner: "PM"
last_updated: "2026-03-17"
---

# AUDIT-LOG - FRAMEWORK3

## Politica

- toda auditoria formal deve gerar relatorio versionado por fase em `auditorias/`
- toda rodada deve registrar commit base, veredito e categoria dos achados materiais
- auditoria `hold` abre follow-ups rastreaveis
- follow-up pode ter destino `issue-local`, `new-intake` ou `cancelled`
- auditoria `go` e pre-requisito para mover fase a `feito/`
- cada resolucao de follow-up deve registrar o `Audit ID de Origem` da rodada `hold` que gerou o item

## Gate Atual por Fase

| Fase | Estado do Gate | Ultima Auditoria | Relatorio Mais Recente | Observacoes |
|---|---|---|---|---|
| F1-Fundacao-do-Modulo-e-Contrato-Canonico | not_ready | nao_aplicavel | nao_aplicavel | fase planejada; nenhuma rodada executada |
| F2-CRUD-Base-e-Superficie-Admin | not_ready | nao_aplicavel | nao_aplicavel | fase planejada; nenhuma rodada executada |
| F3-Planejamento-Hierarquico-Assistido | not_ready | nao_aplicavel | nao_aplicavel | fase planejada; nenhuma rodada executada |
| F4-Execucao-Orquestrada-e-Review-de-Issue | not_ready | nao_aplicavel | nao_aplicavel | fase planejada; nenhuma rodada executada |
| F5-Auditoria-de-Fase-Dataset-e-Rollout-Controlado | not_ready | nao_aplicavel | nao_aplicavel | fase planejada; nenhuma rodada executada |

## Resolucoes de Follow-ups

| Data | Audit ID de Origem | Fase | Follow-up | Destino Final | Resumo | Ref | Observacoes |
|---|---|---|---|---|---|---|---|
| nenhum | - | - | - | - | - | - | - |

> Em `Ref`, para `issue-local`, apontar para a pasta `ISSUE-*/` ou para `README.md` quando a issue for granularizada; usar `ISSUE-*.md` apenas para legado.

## Rodadas

| Audit ID | Fase | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nenhum | - | - | - | - | - | - | - | - | - | - | - | - |
