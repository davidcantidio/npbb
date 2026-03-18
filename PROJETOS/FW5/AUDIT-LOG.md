---
doc_id: "AUDIT-LOG.md"
version: "1.4"
status: "active"
owner: "PM"
last_updated: "2026-03-18"
---

# AUDIT-LOG - FW5

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
| F1-FUNDACAO | not_ready | nao_aplicavel | [RELATORIO-AUDITORIA-F1-R01.md](./F1-FUNDACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md) | backlog canonico materializado para intake e PRD |
| F2-PLANEJAMENTO-EXECUTAVEL | not_ready | nao_aplicavel | [RELATORIO-AUDITORIA-F2-R01.md](./F2-PLANEJAMENTO-EXECUTAVEL/auditorias/RELATORIO-AUDITORIA-F2-R01.md) | fase planejada e aguardando execucao apos F1 |
| F3-OPERACAO-GOVERNANCA | not_ready | nao_aplicavel | [RELATORIO-AUDITORIA-F3-R01.md](./F3-OPERACAO-GOVERNANCA/auditorias/RELATORIO-AUDITORIA-F3-R01.md) | fase planejada e aguardando execucao apos F2 |

## Resolucoes de Follow-ups

| Data | Audit ID de Origem | Fase | Follow-up | Destino Final | Resumo | Ref | Observacoes |
|---|---|---|---|---|---|---|---|
| nenhum | - | - | - | - | - | - | - |

## Rodadas

| Audit ID | Fase | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nenhum | - | - | - | - | - | - | - | - | - | - | - | - |
