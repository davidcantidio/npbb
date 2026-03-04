---
doc_id: "PHASE-F2-EPICS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# F2 Migracao Banco - Epicos

## Objetivo da Fase

Migrar o banco do Supabase para Postgres local na VPS Hostinger com dump e restore auditavel, migrations reaplicadas e validacao objetiva de integridade antes do cutover.

## Gate de Saida da Fase

Contagem de registros de `lead`, `evento` e `usuario` identica entre origem e destino, `alembic upgrade head` sem erros no banco local restaurado e `artifacts/phase-f2/validation-summary.md` gerado com decisao `promote | hold`.

## Epicos da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---|---|---|---|---|
| `EPIC-F2-01` | Dump e Restore Supabase | Definir e provar o fluxo canonico de dump do Supabase e restore no Postgres local com preflight, rollback e alembic. | `todo` | [EPIC-F2-01-DUMP-E-RESTORE-SUPABASE.md](./EPIC-F2-01-DUMP-E-RESTORE-SUPABASE.md) |
| `EPIC-F2-02` | Validacao Integridade Dados | Validar equivalencia minima de dados e prontidao do banco restaurado para prosseguir para o deploy. | `todo` | [EPIC-F2-02-VALIDACAO-INTEGRIDADE-DADOS.md](./EPIC-F2-02-VALIDACAO-INTEGRIDADE-DADOS.md) |

## Escopo desta Entrega

Inclui dump do Supabase, restore em Postgres local, extensoes base, reaplicacao de migrations, comparacao de contagens, validacao de integridade e artifact consolidado de `promote | hold`. Exclui deploy do backend, deploy do frontend, emissao de TLS, cutover DNS, pipeline GitHub Actions, pausas definitivas de Render e Supabase e remocao de `.wrangler/`.
