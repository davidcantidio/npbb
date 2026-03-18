---
doc_id: "SPRINT-F1-01.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# SPRINT-F1-01

## Objetivo da Sprint

Restaurar a baseline executavel e fechar o dual-write minimo nos caminhos prioritarios.

## Capacidade

- story_points_planejados: 7
- issues_planejadas: 5
- override: nenhum

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Documento |
|---|---|---|---|---|
| ISSUE-F1-01-001 | Corrigir surface de modelo e boot da app | 1 | todo | [README](../issues/ISSUE-F1-01-001-CORRIGIR-SURFACE-DE-MODELO-E-BOOT-DA-APP/README.md) |
| ISSUE-F1-01-002 | Versionar migration de lead_evento | 2 | todo | [README](../issues/ISSUE-F1-01-002-VERSIONAR-MIGRATION-LEAD-EVENTO/README.md) |
| ISSUE-F1-02-001 | Garantir dual-write no submit publico | 2 | todo | [README](../issues/ISSUE-F1-02-001-GARANTIR-DUAL-WRITE-NO-SUBMIT-PUBLICO/README.md) |
| ISSUE-F1-02-002 | Cobrir duplicata de conversao e invariantes do submit | 1 | todo | [README](../issues/ISSUE-F1-02-002-COBRIR-DUPLICATA-DE-CONVERSAO-E-INVARIANTES-DO-SUBMIT/README.md) |
| ISSUE-F1-03-001 | Garantir LeadEvento no pipeline Gold | 1 | todo | [README](../issues/ISSUE-F1-03-001-GARANTIR-LEAD-EVENTO-NO-PIPELINE-GOLD/README.md) |

## Riscos e Bloqueios

Baseline atual quebra a coleta dos testes e a migration de `lead_evento` nao aparece versionada no repositorio.

## Encerramento

- decisao: pendente
- observacoes:
