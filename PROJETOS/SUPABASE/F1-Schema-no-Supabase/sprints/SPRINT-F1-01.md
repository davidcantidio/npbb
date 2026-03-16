---
doc_id: "SPRINT-F1-01.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# SPRINT-F1-01

## Objetivo da Sprint

Fechar a compatibilizacao de migrations com o contrato do Supabase e comprovar
que o schema atual sobe ate o head no ambiente alvo.

## Capacidade
- story_points_planejados: 8
- issues_planejadas: 2
- override: nenhum

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Documento |
|---|---|---|---|---|
| ISSUE-F1-01-001 | Adequar execucao de migrations ao Supabase | 3 | done | [ISSUE-F1-01-001-Adequar-Execucao-de-Migrations-ao-Supabase.md](../issues/ISSUE-F1-01-001-Adequar-Execucao-de-Migrations-ao-Supabase.md) |
| ISSUE-F1-01-002 | Validar schema do Supabase com Alembic upgrade head | 5 | todo | [ISSUE-F1-01-002-Validar-Schema-do-Supabase-com-Alembic-Upgrade-Head.md](../issues/ISSUE-F1-01-002-Validar-Schema-do-Supabase-com-Alembic-Upgrade-Head.md) |

## Riscos e Bloqueios

- a sprint depende de credenciais validas de `DIRECT_URL` e `DATABASE_URL`
- qualquer divergencia no historico Alembic bloqueia a entrada em F2

## Encerramento
- decisao: pendente
- observacoes: a sprint libera a fase de migracao de dados somente se o schema do Supabase atingir o head atual
