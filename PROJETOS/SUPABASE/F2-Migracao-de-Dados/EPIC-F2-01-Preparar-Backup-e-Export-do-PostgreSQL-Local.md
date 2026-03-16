---
doc_id: "EPIC-F2-01-Preparar-Backup-e-Export-do-PostgreSQL-Local.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
---

# EPIC-F2-01 - Preparar backup e export do PostgreSQL local

## Objetivo

Transformar as diretrizes do PRD em um runbook executavel e produzir os
artefatos de backup do Supabase e export do PostgreSQL local antes de qualquer
acao destrutiva na base alvo.

## Resultado de Negocio Mensuravel

- existe um runbook operacional unico para backup, export, import e rollback
- o backup do Supabase e o export do PostgreSQL local sao gerados de forma reproduzivel
- a recarga de dados da F2 parte de insumos validos e de baixo risco operacional

## Contexto Arquitetural

- o PRD ja define `schema primeiro`, `pg_dump` ou formato equivalente, backup previo do Supabase e import com `psql` ou `pg_restore`
- `backend/.env.example`, `docs/SETUP.md` e `docs/TROUBLESHOOTING.md` registram o contrato atual de conexoes e gotchas operacionais
- `backend/scripts/seed_common.py` reforca a preferencia por `DIRECT_URL` para operacoes sensiveis de banco

## Definition of Done do Epico
- [ ] runbook de migracao fechado com precondicoes, ordem e rollback
- [ ] backup do Supabase gerado antes da recarga
- [ ] export do PostgreSQL local gerado para alimentar o import

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-01-001 | Formalizar runbook de backup, export, import e rollback | Fechar a sequencia operacional da migracao sem improviso | 2 | todo | [ISSUE-F2-01-001-Formalizar-Runbook-de-Backup-Export-Import-e-Rollback.md](./issues/ISSUE-F2-01-001-Formalizar-Runbook-de-Backup-Export-Import-e-Rollback.md) |
| ISSUE-F2-01-002 | Automatizar backup do Supabase e export do PostgreSQL local | Gerar artefatos de seguranca e export com comandos reproduziveis | 3 | todo | [ISSUE-F2-01-002-Automatizar-Backup-do-Supabase-e-Export-do-PostgreSQL-Local.md](./issues/ISSUE-F2-01-002-Automatizar-Backup-do-Supabase-e-Export-do-PostgreSQL-Local.md) |

## Artifact Minimo do Epico

- runbook com precondicoes, comandos e rollback
- backup do Supabase disponivel antes da recarga
- export do PostgreSQL local pronto para a importacao

## Dependencias
- [Intake](../INTAKE-SUPABASE.md)
- [PRD](../PRD-SUPABASE.md)
- [Fase](./F2_SUPABASE_EPICS.md)
- [F1](../F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md)
