---
doc_id: "AUDIT-LOG.md"
version: "1.6"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
---

# AUDIT-LOG - OPENCLAW-MIGRATION

## Politica

- toda auditoria formal deve gerar relatorio versionado em `auditorias/`
- toda rodada deve registrar commit base, veredito e categoria dos achados materiais
- auditoria `hold` abre follow-ups rastreaveis
- follow-up pode ter destino `issue-local`, `new-intake` ou `cancelled`
- auditoria `go` e pre-requisito para considerar a migracao concluida
- cada resolucao de follow-up deve registrar o `Audit ID de Origem` da rodada `hold` que gerou o item

## Gate Atual por Fase

| Fase | Estado do Gate | Ultima Auditoria | Relatorio Mais Recente | Observacoes |
|---|---|---|---|---|
| OPENCLAW-MIGRATION | approved | MIGRATION-R02 | [RELATORIO-AUDITORIA-MIGRATION-R02.md](auditorias/RELATORIO-AUDITORIA-MIGRATION-R02.md) | Apos remediacao B1-B4, R02 com veredito `go`; achado residual low A-R02-01 (preambulo `boot-prompt.md`) nao bloqueante. |

## Resolucoes de Follow-ups

| Data | Audit ID de Origem | Fase | Follow-up | Destino Final | Resumo | Ref | Observacoes |
|---|---|---|---|---|---|---|---|
| 2026-03-25 | MIGRATION-R01 | F1-REMEDIACAO-HOLD-R01 | B1 | issue-local | Criar `TEMPLATE-USER-STORY.md` com os campos canônicos da US 2.2 | [ISSUE-F1-01-001-TEMPLATE-USER-STORY-CANONICO](F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-001-TEMPLATE-USER-STORY-CANONICO/) | Issue-local rastreavel; classificacao em [REMEDIACAO-HOLD-R01-CLASSIFICACAO.md](auditorias/REMEDIACAO-HOLD-R01-CLASSIFICACAO.md); entregar artefato em `PROJETOS/COMUM/TEMPLATE-USER-STORY.md` |
| 2026-03-25 | MIGRATION-R01 | F1-REMEDIACAO-HOLD-R01 | B2 | issue-local | Reescrever `boot-prompt.md` para descoberta `Feature -> User Story -> Task` e auditoria de feature | [ISSUE-F1-01-002-BOOT-PROMPT-FEATURE-US-TASK](F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-002-BOOT-PROMPT-FEATURE-US-TASK/) | Idem; entregar alteracoes em `PROJETOS/COMUM/boot-prompt.md` |
| 2026-03-25 | MIGRATION-R01 | F1-REMEDIACAO-HOLD-R01 | B3 | issue-local | Consolidar a superficie `SESSION-*`/governanca: criar `SESSION-REVISAR-US.md`, alinhar `SESSION-MAPA.md`, `SESSION-AUDITAR-FEATURE.md`, `GOV-SCRUM.md` e depreciar os prompts legados | [ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM](F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM/) | Idem; coordenacao multi-artefacto via tasks T1-T6 |
| 2026-03-25 | MIGRATION-R01 | F1-REMEDIACAO-HOLD-R01 | B4 | issue-local | Remover `issue-first` e referencias a fase fora de contexto `deprecated` em `GOV-FRAMEWORK-MASTER.md` e demais docs centrais | [ISSUE-F1-01-004-GOV-FRAMEWORK-MASTER-LIMPEZA](F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-004-GOV-FRAMEWORK-MASTER-LIMPEZA/) | Idem; compatibilidade apenas em blocos `deprecated` |

## Rodadas

| Audit ID | Fase | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MIGRATION-R01 | OPENCLAW-MIGRATION | 2026-03-25 | GPT-5 Codex | 6e678617f41e | none | hold | done | [RELATORIO-AUDITORIA-MIGRATION-R01.md](auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md) | A-01 critical; A-02-A-06 high | issue-local | [B1](F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-001-TEMPLATE-USER-STORY-CANONICO/), [B2](F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-002-BOOT-PROMPT-FEATURE-US-TASK/), [B3](F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM/), [B4](F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-004-GOV-FRAMEWORK-MASTER-LIMPEZA/) | none |
| MIGRATION-R02 | OPENCLAW-MIGRATION | 2026-03-25 | Claude (Cursor Agent) | d9ce18694076355e985e407df7189b1a10c7100f | MIGRATION-R01 | go | done | [RELATORIO-AUDITORIA-MIGRATION-R02.md](auditorias/RELATORIO-AUDITORIA-MIGRATION-R02.md) | A-R02-01 low (doc) | none | none | none |
