---
doc_id: "AUDIT-LOG.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-10"
---

# AUDIT-LOG - FRAMEWORK2.0

## Referencias

- [Intake](./INTAKE-FRAMEWORK2.0.md)
- [PRD](./PRD-FRAMEWORK2.0.md)
- [Framework de Auditoria](../COMUM/GOV-AUDITORIA.md)

## Politica

- toda auditoria formal deve gerar relatorio versionado por fase em `auditorias/`
- toda rodada deve registrar commit base, veredito e categoria dos achados materiais
- auditoria `hold` abre follow-ups rastreaveis
- follow-up pode ter destino `issue-local`, `new-intake` ou `cancelled`
- auditoria `go` e pre-requisito para mover fase a `feito/`

## Gate Atual por Fase

| Fase | Estado do Gate | Ultima Auditoria | Relatorio Mais Recente | Observacoes |
|---|---|---|---|---|
| F1 - HARMONIZACAO-E-RENOMEACAO | approved | F1-R02 | [RELATORIO-AUDITORIA-F1-R02.md](./F1-HARMONIZACAO-E-RENOMEACAO/auditorias/RELATORIO-AUDITORIA-F1-R02.md) | gate aprovado apos reconciliacao documental dos follow-ups de F1-R01 |
| F2 - ANTI-MONOLITH-ENFORCEMENT | not_ready | n-a | n-a | fase liberada para desenvolvimento |
| F3 - PROMPTS-DE-SESSAO | not_ready | n-a | n-a | aguardando priorizacao apos F2 |

## Rodadas

| Audit ID | Fase | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1-R02 | F1 - HARMONIZACAO-E-RENOMEACAO | 2026-03-10 | GPT-5 Codex | 010b60a5fa2a4fd8c6b9bbffa9eb21d487206599 | fe9ce4d9ce58650a4813362519c06f4aebd1ad76 | go | done | [RELATORIO-AUDITORIA-F1-R02.md](./F1-HARMONIZACAO-E-RENOMEACAO/auditorias/RELATORIO-AUDITORIA-F1-R02.md) | architecture-drift(low) | none | none | F1-R01 |
| F1-R01 | F1 - HARMONIZACAO-E-RENOMEACAO | 2026-03-09 | GPT-5 Codex | fe9ce4d9ce58650a4813362519c06f4aebd1ad76 | none | hold | done | [RELATORIO-AUDITORIA-F1-R01.md](./F1-HARMONIZACAO-E-RENOMEACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md) | scope-drift(high); architecture-drift(high); architecture-drift(medium) | issue-local | ISSUE-F1-04-001, ISSUE-F1-04-002, ISSUE-F1-05-001, SPRINT-F1-01/02/03 sync | none |
