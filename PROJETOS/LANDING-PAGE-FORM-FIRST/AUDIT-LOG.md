---
doc_id: "AUDIT-LOG.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
---

# AUDIT-LOG - LANDING-PAGE-FORM-FIRST

## Referencias

- [Intake](./INTAKE-LANDING-PAGE-FORM-FIRST.md)
- [PRD](./PRD-LANDING-PAGE-FORM-FIRST.md)
- [Framework de Auditoria](../COMUM/AUDITORIA-GOV.md)

## Politica

- toda auditoria formal deve gerar relatorio versionado por fase em `auditorias/`
- toda rodada deve registrar commit base, veredito e categoria dos achados materiais
- follow-up pode ter destino `issue-local`, `new-intake` ou `cancelled`
- auditoria `go` e pre-requisito para mover fase a `feito/`

## Gate Atual por Fase

| Fase | Estado do Gate | Ultima Auditoria | Relatorio Mais Recente | Observacoes |
|---|---|---|---|---|
| F1 - LAYOUT-FORM-ONLY | approved | R01 (`go`) | [RELATORIO-AUDITORIA-F1-R01](./F1-LAYOUT-FORM-ONLY/auditorias/RELATORIO-AUDITORIA-F1-R01.md) | follow-up local de cor de rodape resolvido e gate de auditoria liberado |
| F2 - BACKOFFICE-E-PREVIEW | not_ready | nenhuma | n-a | fase ainda nao iniciou |
| F3 - QA-CROSS-TEMPLATE | not_ready | nenhuma | n-a | fase ainda nao iniciou |

## Rodadas

| Audit ID | Fase | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1-R01 | F1 - LAYOUT-FORM-ONLY | 2026-03-08 | GPT-5 Codex | 11f60f688118c49a477609169f5253a9ef15bd87 | n-a | go | done | [RELATORIO-AUDITORIA-F1-R01](./F1-LAYOUT-FORM-ONLY/auditorias/RELATORIO-AUDITORIA-F1-R01.md) | S-01 (`monolithic-file/medium`), S-02 (`architecture-drift/medium`) | cancelled | n-a | none |
