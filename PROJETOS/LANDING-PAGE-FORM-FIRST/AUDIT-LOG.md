---
doc_id: "AUDIT-LOG.md"
version: "1.2"
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
| F1 - LAYOUT-FORM-ONLY | not_ready | nenhuma | n-a | desenvolvimento ainda em andamento |
| F2 - BACKOFFICE-E-PREVIEW | not_ready | nenhuma | n-a | fase ainda nao iniciou |
| F3 - QA-CROSS-TEMPLATE | hold | R02 (`hold`) | [RELATORIO-AUDITORIA-F3-R02](./F3-QA-CROSS-TEMPLATE/auditorias/RELATORIO-AUDITORIA-F3-R02.md) | R02 formaliza o gate em base limpa; `F3-R01` permanece como antecedente nao canonico de escopo issue e sem SHA valido |

## Rodadas

| Audit ID | Fase | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F3-R02 | F3 - QA-CROSS-TEMPLATE | 2026-03-08 | GPT-5 Codex | 11f60f688118c49a477609169f5253a9ef15bd87 | n-a (`F3-R01` sem SHA valido) | hold | done | [RELATORIO-AUDITORIA-F3-R02](./F3-QA-CROSS-TEMPLATE/auditorias/RELATORIO-AUDITORIA-F3-R02.md) | A-01 (`test-gap/medium`), A-02 (`scope-drift/medium`), A-03 (`architecture-drift/medium`), A-04 (`scope-drift/low`) | issue-local | A-01, A-02 | F3-R01 |
