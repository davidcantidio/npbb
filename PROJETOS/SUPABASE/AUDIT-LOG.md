---
doc_id: "AUDIT-LOG.md"
version: "1.3"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# AUDIT-LOG - SUPABASE

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
| F1-Schema-no-Supabase | hold | F1-R03 | [RELATORIO-AUDITORIA-F1-R03.md](./F1-Schema-no-Supabase/auditorias/RELATORIO-AUDITORIA-F1-R03.md) | rodada provisional por worktree sujo |
| F2-Migracao-de-Dados | approved | F2-R01 | [RELATORIO-AUDITORIA-F2-R01.md](./F2-Migracao-de-Dados/auditorias/RELATORIO-AUDITORIA-F2-R01.md) | observacoes estruturais `warn` nao bloqueantes em scripts operacionais |

## Resolucoes de Follow-ups

| Data | Audit ID de Origem | Fase | Follow-up | Destino Final | Resumo | Ref | Observacoes |
|---|---|---|---|---|---|---|---|
| 2026-03-16 | F1-R01 | F1-Schema-no-Supabase | B1 | issue-local | Commit e revalidar auditoria com arvore limpa | [ISSUE-F1-01-008-Commit-e-Revalidar-Auditoria-F1](./F1-Schema-no-Supabase/issues/ISSUE-F1-01-008-Commit-e-Revalidar-Auditoria-F1/) | resolvido F1-R02 |

## Rodadas

| Audit ID | Fase | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1-R01 | F1-Schema-no-Supabase | 2026-03-16 | cursor-composer | 2828545052e3018f581e0d83130bccdeba960fea | - | hold | provisional | [RELATORIO-AUDITORIA-F1-R01.md](./F1-Schema-no-Supabase/auditorias/RELATORIO-AUDITORIA-F1-R01.md) | worktree sujo | issue-local | B1 pendente | - |
| F1-R02 | F1-Schema-no-Supabase | 2026-03-16 | cursor-composer | 6d52905539cd1c993fb9434eb5b2af50327819cb | 2828545052e3018f581e0d83130bccdeba960fea | go | done | [RELATORIO-AUDITORIA-F1-R02.md](./F1-Schema-no-Supabase/auditorias/RELATORIO-AUDITORIA-F1-R02.md) | — | — | — | F1-R01 |
| F1-R03 | F1-Schema-no-Supabase | 2026-03-16 | gpt-5-codex | 2428c1b4ee20c0c55717ca4c6675cf57944ddbfd | 6d52905539cd1c993fb9434eb5b2af50327819cb | hold | provisional | [RELATORIO-AUDITORIA-F1-R03.md](./F1-Schema-no-Supabase/auditorias/RELATORIO-AUDITORIA-F1-R03.md) | worktree sujo | issue-local | B1 pendente | F1-R02 |
| F2-R01 | F2-Migracao-de-Dados | 2026-03-16 | gpt-5-codex | e3ab94fc6f4352ea34fbf7a35a96364c1be02957 | - | go | done | [RELATORIO-AUDITORIA-F2-R01.md](./F2-Migracao-de-Dados/auditorias/RELATORIO-AUDITORIA-F2-R01.md) | — | — | — | - |
