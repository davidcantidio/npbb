---
doc_id: "AUDIT-LOG.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-09"
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
| F1 - HARMONIZACAO-E-RENOMEACAO | hold | F1-R01 | [RELATORIO-AUDITORIA-F1-R01.md](./F1-HARMONIZACAO-E-RENOMEACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md) | hold por lacuna material de rastreabilidade entre entrega e status documental |
| F2 - ANTI-MONOLITH-ENFORCEMENT | not_ready | n-a | n-a | depende de F1-01 concluido |
| F3 - PROMPTS-DE-SESSAO | not_ready | n-a | n-a | depende de F1 concluida |

## Rodadas

| Audit ID | Fase | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1-R01 | F1 - HARMONIZACAO-E-RENOMEACAO | 2026-03-09 | GPT-5 Codex | fe9ce4d9ce58650a4813362519c06f4aebd1ad76 | none | hold | done | [RELATORIO-AUDITORIA-F1-R01.md](./F1-HARMONIZACAO-E-RENOMEACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md) | scope-drift(high); architecture-drift(high); architecture-drift(medium) | issue-local | ISSUE-F1-04-001, ISSUE-F1-04-002, ISSUE-F1-05-001, SPRINT-F1-01/02/03 sync | none |
