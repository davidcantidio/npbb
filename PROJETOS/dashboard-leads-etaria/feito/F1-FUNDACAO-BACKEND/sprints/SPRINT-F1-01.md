---
doc_id: "SPRINT-F1-01.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
---

# SPRINT-F1-01

## Objetivo da Sprint

Fechar a base de dados do dashboard: modelo Lead, migration e schemas de resposta iniciais.

## Capacidade

- story_points_planejados: 10
- issues_planejadas: 4
- override: nenhum

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Documento |
|---|---|---|---|---|
| ISSUE-F1-01-001 | Adicionar campos `is_cliente_bb` e `is_cliente_estilo` ao modelo Lead | 3 | done | [ISSUE-F1-01-001-ADICIONAR-CAMPOS-IS-CLIENTE-BB-E-IS-CLIENTE-ESTILO-AO-MODELO-LEAD.md](../issues/ISSUE-F1-01-001-ADICIONAR-CAMPOS-IS-CLIENTE-BB-E-IS-CLIENTE-ESTILO-AO-MODELO-LEAD.md) |
| ISSUE-F1-01-002 | Criar migration Alembic para novos campos do Lead | 2 | done | [ISSUE-F1-01-002-CRIAR-MIGRATION-ALEMBIC-PARA-NOVOS-CAMPOS-DO-LEAD.md](../issues/ISSUE-F1-01-002-CRIAR-MIGRATION-ALEMBIC-PARA-NOVOS-CAMPOS-DO-LEAD.md) |
| ISSUE-F1-01-003 | Atualizar schemas de leitura do Lead | 2 | done | [ISSUE-F1-01-003-ATUALIZAR-SCHEMAS-DE-LEITURA-DO-LEAD.md](../issues/ISSUE-F1-01-003-ATUALIZAR-SCHEMAS-DE-LEITURA-DO-LEAD.md) |
| ISSUE-F1-02-001 | Criar schemas Pydantic da análise etária | 3 | todo | [ISSUE-F1-02-001-CRIAR-SCHEMAS-PYDANTIC-DA-ANALISE-ETARIA.md](../issues/ISSUE-F1-02-001-CRIAR-SCHEMAS-PYDANTIC-DA-ANALISE-ETARIA.md) |

## Riscos e Bloqueios

- dependencia cruzada entre backend e frontend deve ser validada antes da troca de fase
- qualquer issue acima de 5 SP deve ser reavaliada e decomposta antes de execucao

## Encerramento

- decisao: pendente
- observacoes: manter a sprint alinhada aos limites de `SPRINT-LIMITS.md`
