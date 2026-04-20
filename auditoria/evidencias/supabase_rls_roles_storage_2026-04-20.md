# Supabase: RLS, roles e storage

Data: 2026-04-20.
Fonte: consulta read-only via MCP Supabase no ambiente configurado.

## Migrations

Classificacao: aplicado no banco/ambiente; observado em execucao real.

- `alembic_version` observado: `7a3c8d1e2f4b`.
- A migration nova `8b6f4c2d9a1e_apply_central_leads_rls_policies.py` existe no repositorio, mas nao estava aplicada no banco observado.

Conclusao verificavel: RLS central para `evento`, `ativacao`, `lead` e `lead_evento` esta implementada em codigo, mas nao aplicada no ambiente Supabase observado.

## RLS por tabela central

Classificacao: aplicado no banco/ambiente; observado em execucao real.

Estado observado em `pg_class.relrowsecurity`:

| tabela | relrowsecurity observado |
| --- | --- |
| `ativacao` | `false` |
| `evento` | `false` |
| `lead` | `false` |
| `lead_evento` | `false` |
| `ativacao_lead` | `true` |
| `usuario` | `true` |

Policies observadas em tabelas de importacao:

- `lead_batches`
- `lead_column_aliases`
- `lead_import_etl_job`
- `lead_import_etl_preview_session`
- `lead_import_etl_staging`
- `leads_silver`

Policies centrais nao observadas no banco:

- `evento_select`, `evento_insert`, `evento_update`, `evento_delete`
- `ativacao_select`, `ativacao_insert`, `ativacao_update`, `ativacao_delete`
- `lead_select`, `lead_insert`, `lead_update`, `lead_delete`
- `lead_evento_select`, `lead_evento_insert`, `lead_evento_update`, `lead_evento_delete`

Conclusao verificavel: antes da aplicacao da migration `8b6f4c2d9a1e`, a protecao central permanece incompleta no ambiente observado.

## Roles dedicadas

Classificacao: aplicado no banco/ambiente; observado em execucao real.

Roles observadas:

| role | rolsuper | rolbypassrls | rolcreaterole | rolcreatedb |
| --- | --- | --- | --- | --- |
| `npbb_api` | `false` | `false` | `false` | `false` |
| `npbb_worker` | `false` | `false` | `false` | `false` |

Conclusao verificavel: as roles dedicadas existem no banco observado e nao possuem `BYPASSRLS`.

## Storage/backfill

Classificacao: aplicado no banco/ambiente; observado em execucao real.

Contagem observada de payloads ainda inline:

| tabela | pendentes |
| --- | ---: |
| `lead_batches` | 222 |
| `lead_import_etl_job` | 0 |

Conclusao verificavel: backfill historico de `lead_batches.arquivo_bronze` nao esta completo no ambiente observado.
