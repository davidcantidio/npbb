---
doc_id: "EPIC-F2-01-DUMP-E-RESTORE-SUPABASE"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F2-01 - Dump e Restore Supabase

## Objetivo

Definir e executar o fluxo canonico de dump do Supabase e restore no Postgres local da VPS, com preflight, rollback e reaplicacao de migrations documentados.

## Resultado de Negocio Mensuravel

A migracao do banco deixa de depender de procedimento manual ad hoc e passa a ter uma janela operacional repetivel, auditavel e reversivel.

## Definition of Done

- O preflight bloqueia execucao sem `SUPABASE_DATABASE_URL`, `LOCAL_DATABASE_URL`, aprovacao humana explicita e rollback definido.
- O dump `pg_dump -Fc` gera arquivo identificavel por data e manifest de execucao.
- O restore no Postgres local ocorre sem erro de ownership ou privilege e com extensoes base garantidas.
- `alembic upgrade head` roda contra o banco restaurado sem erro.
- `artifacts/phase-f2/epic-f2-01-dump-e-restore-supabase.md` consolida checklist, dump, restore, alembic e rollback state.

## Issues

### ISSUE-F2-01-01 - Formalizar preflight, work order e decision da migracao
Status: todo

**User story**
Como pessoa responsavel pela janela de migracao, quero um preflight com work order, decision e rollback definido para bloquear execucao incompleta antes de tocar no banco.

**Plano TDD**
1. `Red`: usar `Infra/production/.env.example`, `docs/RUNBOOK_RESTORE_POSTGRES_VPS.md`, `PROJETOS/WORK-ORDER-SPEC.md` e `PROJETOS/DECISION-PROTOCOL.md` para tornar explicita a falha quando faltarem `SUPABASE_DATABASE_URL`, `LOCAL_DATABASE_URL`, `idempotency_key`, aprovacao humana ou `rollback_plan`.
2. `Green`: complementar `docs/RUNBOOK_RESTORE_POSTGRES_VPS.md` com checklist de preflight e definir `artifacts/phase-f2/work-order-and-decision.md` com os blocos YAML canonicos de `work_order` e `decision`.
3. `Refactor`: unificar nomenclatura de variaveis, risco e rollback entre o PRD, o runbook e o artifact para remover instrucoes conflitantes.

**Criterios de aceitacao**
- Given ausencia de qualquer variavel obrigatoria ou de aprovacao humana, When o preflight e revisado ou executado, Then a fase permanece bloqueada antes de `pg_dump` ou `pg_restore`.
- Given preflight completo, When a janela e aprovada, Then o artifact registra `risk_tier=R3`, `explicit_human_approval=true` e rollback de volta ao Supabase como fonte de verdade.

### ISSUE-F2-01-02 - Executar dump do Supabase e restore no Postgres local
Status: todo

**User story**
Como pessoa responsavel pela migracao do banco, quero gerar um dump completo do Supabase e restaura-lo no Postgres local para preparar a stack da VPS sem downtime.

**Plano TDD**
1. `Red`: usar `Infra/production/docker-compose.yml`, `Infra/production/postgres/init/00-extensions.sql` e `docs/RUNBOOK_RESTORE_POSTGRES_VPS.md` para fazer o fluxo falhar quando o `db` nao estiver saudavel, quando extensoes base faltarem ou quando o manifest do dump nao for produzido.
2. `Green`: codificar no runbook e no artifact do epico a sequencia literal do PRD com `pg_dump $SUPABASE_DATABASE_URL -Fc`, `docker-compose up -d db` e `pg_restore -d $LOCAL_DATABASE_URL`, registrando nome do arquivo, horario, tamanho e hash do dump.
3. `Refactor`: separar pre-restore, restore e captura de manifest para que o procedimento seja idempotente em homologacao e na janela final.

**Criterios de aceitacao**
- Given `SUPABASE_DATABASE_URL` valido e Postgres local pronto, When dump e restore rodam, Then um `.dump` e gerado e o destino local recebe schema e dados sem falha de ownership ou privileges.
- Given extensao ausente ou `db` nao saudavel, When o restore inicia, Then a execucao e interrompida antes da escrita definitiva e a causa fica registrada no artifact.

### ISSUE-F2-01-03 - Reaplicar Alembic e validar prontidao do banco restaurado
Status: todo

**User story**
Como pessoa mantenedora do backend, quero reaplicar as migrations apos o restore para garantir que o banco local esteja no mesmo estado logico esperado pela aplicacao.

**Plano TDD**
1. `Red`: usar `backend/alembic/env.py`, `backend/alembic.ini` e `backend/app/db/database.py` para reproduzir falhas quando o banco restaurado nao alcanca `head` ou quando runtime e migrations divergem de URL.
2. `Green`: incluir o passo `alembic upgrade head` no fechamento do runbook e registrar no artifact do epico a revision final, o log da execucao e o estado das extensoes base.
3. `Refactor`: alinhar a linguagem do runbook com a expectativa do backend para conexao e post-restore, sem depender de inferencia operacional.

**Criterios de aceitacao**
- Given banco restaurado com conexao valida, When `alembic upgrade head` roda, Then a revision atual coincide com `head` e o comando termina sem erro.
- Given falha de migration ou divergencia de URL, When a validacao pos-restore roda, Then a fase continua bloqueada e o rollback aponta para o Supabase como fonte de verdade.

## Artifact Minimo do Epico

- `artifacts/phase-f2/epic-f2-01-dump-e-restore-supabase.md` com checklist de preflight, YAMLs de `work_order` e `decision`, manifest do dump, log do restore, resultado de `alembic upgrade head` e estado de rollback.

## Dependencias

- [PRD](../prd_vps_migration.md)
- [SCRUM-GOV](../SCRUM-GOV.md)
- [DECISION-PROTOCOL](../DECISION-PROTOCOL.md)
