---
doc_id: "SPRINT-F1-01.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
---

# SPRINT-F1-01

## Objetivo da Sprint

Fechar o sibling de baseline, evidencia e handoff da remediacao do hold da F1
em um unico ciclo, sem tocar o gate da F1 original, sem reabrir backlog
funcional do fluxo publico e sem absorver o refactor de
`backend/app/routers/leads.py`.

## Capacidade

- story_points_planejados: 12
- issues_planejadas: 5
- override: nenhum

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Documento |
|---|---|---|---|---|
| ISSUE-F1-01-001 | Classificar PRD vs repo no fluxo publico | 3 | todo | [ISSUE-F1-01-001-CLASSIFICAR-PRD-VS-REPO-NO-FLUXO-PUBLICO.md](../issues/ISSUE-F1-01-001-CLASSIFICAR-PRD-VS-REPO-NO-FLUXO-PUBLICO.md) |
| ISSUE-F1-01-002 | Validar baseline estrutural da F1 | 2 | todo | [ISSUE-F1-01-002-VALIDAR-BASELINE-ESTRUTURAL-DA-F1.md](../issues/ISSUE-F1-01-002-VALIDAR-BASELINE-ESTRUTURAL-DA-F1.md) |
| ISSUE-F1-02-001 | Consolidar evidencia de contrato e paridade | 3 | todo | [ISSUE-F1-02-001-CONSOLIDAR-EVIDENCIA-DE-CONTRATO-E-PARIDADE.md](../issues/ISSUE-F1-02-001-CONSOLIDAR-EVIDENCIA-DE-CONTRATO-E-PARIDADE.md) |
| ISSUE-F1-02-002 | Consolidar evidencia de metadata e threshold | 2 | todo | [ISSUE-F1-02-002-CONSOLIDAR-EVIDENCIA-DE-METADATA-E-THRESHOLD.md](../issues/ISSUE-F1-02-002-CONSOLIDAR-EVIDENCIA-DE-METADATA-E-THRESHOLD.md) |
| ISSUE-F1-03-001 | Preparar handoff para reauditoria | 2 | todo | [ISSUE-F1-03-001-PREPARAR-HANDOFF-PARA-REAUDITORIA.md](../issues/ISSUE-F1-03-001-PREPARAR-HANDOFF-PARA-REAUDITORIA.md) |

## Riscos e Bloqueios

- drift material fora do PRD derivado exigir novo intake em vez de ajuste dentro do sibling
- qualquer evidencia focal de backend, frontend ou metadata falhar e transformar a trilha em `BLOQUEADO`
- pressao para absorver o refactor de `backend/app/routers/leads.py` neste mesmo ciclo
- tentativa de usar o sibling para promover o gate da F1 original sem nova auditoria formal
- inflacao de escopo com LGPD de CPF em repouso

## Encerramento

- decisao: pendente
- observacoes: a sequencia operacional comeca por `ISSUE-F1-01-001`, fecha a baseline estrutural em `ISSUE-F1-01-002`, consolida a evidencia em `ISSUE-F1-02-001` e `ISSUE-F1-02-002`, e termina no handoff `ISSUE-F1-03-001`
