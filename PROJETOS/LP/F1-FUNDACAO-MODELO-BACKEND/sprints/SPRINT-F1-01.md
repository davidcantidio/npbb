---
doc_id: "SPRINT-F1-01.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-11"
---

# SPRINT-F1-01

## Objetivo da Sprint

Fechar a fundação do backend: modelos, migrations, CRUD de ativações, geração de QR e endpoint de landing.

## Capacidade

- story_points_planejados: 13
- issues_planejadas: 5
- override: nenhum

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Documento |
|---|---|---|---|---|
| ISSUE-F1-01-001 | Modelo Ativacao e migration | 2 | done | [ISSUE-F1-01-001-MODELO-ATIVACAO-E-MIGRATION.md](../issues/ISSUE-F1-01-001-MODELO-ATIVACAO-E-MIGRATION.md) |
| ISSUE-F1-01-002 | Modelos conversao_ativacao e lead_reconhecimento_token | 3 | todo | [ISSUE-F1-01-002-MODELOS-CONVERSAO-E-TOKEN.md](../issues/ISSUE-F1-01-002-MODELOS-CONVERSAO-E-TOKEN.md) |
| ISSUE-F1-02-001 | Schemas e endpoints CRUD de ativações | 3 | todo | [ISSUE-F1-02-001-SCHEMAS-E-ENDPOINTS-CRUD-ATIVACOES.md](../issues/ISSUE-F1-02-001-SCHEMAS-E-ENDPOINTS-CRUD-ATIVACOES.md) |
| ISSUE-F1-03-001 | Serviço de geração de QR | 2 | done | [ISSUE-F1-03-001-SERVICO-GERACAO-QR.md](../issues/ISSUE-F1-03-001-SERVICO-GERACAO-QR.md) |
| ISSUE-F1-03-002 | Endpoint GET landing | 3 | todo | [ISSUE-F1-03-002-ENDPOINT-GET-LANDING.md](../issues/ISSUE-F1-03-002-ENDPOINT-GET-LANDING.md) |

## Riscos e Bloqueios

- Ordem de execução: ISSUE-F1-01-001 e ISSUE-F1-01-002 antes de F1-02 e F1-03
- ISSUE-F1-02-001 e F1-03 dependem de F1-01

## Encerramento

- decisao: pendente
- observacoes: respeitar limites de GOV-SPRINT-LIMITES.md (max 13 SP, max 5 issues — considerar split em 2 sprints se necessário)
