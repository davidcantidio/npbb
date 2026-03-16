---
doc_id: "SPRINT-F2-01.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
---

# SPRINT-F2-01

## Objetivo da Sprint

Fechar o runbook da migracao de dados e produzir os artefatos de backup do
Supabase e export do PostgreSQL local antes da recarga.

## Capacidade
- story_points_planejados: 5
- issues_planejadas: 2
- override: nenhum

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Documento |
|---|---|---|---|---|
| ISSUE-F2-01-001 | Formalizar runbook de backup, export, import e rollback | 2 | done | [ISSUE-F2-01-001-Formalizar-Runbook-de-Backup-Export-Import-e-Rollback.md](../issues/ISSUE-F2-01-001-Formalizar-Runbook-de-Backup-Export-Import-e-Rollback.md) |
| ISSUE-F2-01-002 | Automatizar backup do Supabase e export do PostgreSQL local | 3 | done | [ISSUE-F2-01-002-Automatizar-Backup-do-Supabase-e-Export-do-PostgreSQL-Local.md](../issues/ISSUE-F2-01-002-Automatizar-Backup-do-Supabase-e-Export-do-PostgreSQL-Local.md) |

## Riscos e Bloqueios

- a sprint depende de credenciais validas para o Supabase e para o PostgreSQL local
- qualquer ausencia de `pg_dump` bloqueia a preparacao dos artefatos para a recarga

## Encerramento
- decisao: pendente
- observacoes: a sprint termina apenas com backup e export prontos para alimentar a recarga controlada
