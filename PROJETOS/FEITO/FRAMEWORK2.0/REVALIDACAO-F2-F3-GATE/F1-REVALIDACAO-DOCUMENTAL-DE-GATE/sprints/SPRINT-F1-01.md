---
doc_id: "SPRINT-F1-01.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-10"
---

# SPRINT-F1-01

## Objetivo da Sprint

Concluir a revalidacao documental de gate de F2/F3, da baseline comparativa ao
encerramento rastreavel, sem simular auditoria formal e sem ampliar escopo para
alem de checklist/gate.

## Capacidade

- story_points_planejados: 9
- issues_planejadas: 4
- override: nenhum

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Documento |
|---|---|---|---|---|
| ISSUE-F1-01-001 | Comparar manifestos F2 e F3 com o template canonico de gate | 3 | todo | [ISSUE-F1-01-001-COMPARAR-MANIFESTOS-F2-E-F3-COM-O-TEMPLATE-CANONICO-DE-GATE.md](../issues/ISSUE-F1-01-001-COMPARAR-MANIFESTOS-F2-E-F3-COM-O-TEMPLATE-CANONICO-DE-GATE.md) |
| ISSUE-F1-02-001 | Ajustar manifesto F2 ao split canonico de gate | 2 | done | [ISSUE-F1-02-001-AJUSTAR-MANIFESTO-F2-AO-SPLIT-CANONICO-DE-GATE.md](../issues/ISSUE-F1-02-001-AJUSTAR-MANIFESTO-F2-AO-SPLIT-CANONICO-DE-GATE.md) |
| ISSUE-F1-02-002 | Ajustar manifesto F3 ao split canonico de gate | 2 | done | [ISSUE-F1-02-002-AJUSTAR-MANIFESTO-F3-AO-SPLIT-CANONICO-DE-GATE.md](../issues/ISSUE-F1-02-002-AJUSTAR-MANIFESTO-F3-AO-SPLIT-CANONICO-DE-GATE.md) |
| ISSUE-F1-03-001 | Consolidar evidencia da revalidacao sem simular auditoria | 2 | todo | [ISSUE-F1-03-001-CONSOLIDAR-EVIDENCIA-DA-REVALIDACAO-SEM-SIMULAR-AUDITORIA.md](../issues/ISSUE-F1-03-001-CONSOLIDAR-EVIDENCIA-DA-REVALIDACAO-SEM-SIMULAR-AUDITORIA.md) |

## Riscos e Bloqueios

- drift fora de checklist/gate exigir escopo maior do que o sibling aprovado
- tentativa de reinterpretar `status`, `audit_gate`, `gate_atual` ou `ultima_auditoria` de F2/F3
- fechamento da trilha depender de `RELATORIO-AUDITORIA-*` ou update em `AUDIT-LOG.md`

## Encerramento

- decisao: pendente
- observacoes: a sequencia operacional comeca por `ISSUE-F1-01-001`, segue com `ISSUE-F1-02-001` e `ISSUE-F1-02-002`, e fecha em `ISSUE-F1-03-001`
