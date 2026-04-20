# Deploy, runtime, worker e storage

Data: 2026-04-20.

## Gates implementados

Classificacao: implementado em codigo.

Arquivos alterados:

- `Makefile`: alvo `leads-deploy-gate`.
- `scripts/check_deploy.sh`: exige gates de runtime, worker dedicado e backend de storage Supabase nos blueprints.
- `render.yaml` e `docs/render.yaml`: API e worker executam `verify_leads_runtime_env.py` antes do start.
- `backend/scripts/verify_leads_runtime_env.py`: valida ambiente efetivo de API/worker.
- `backend/scripts/verify_leads_hardening_db.py`: valida migration, RLS, policies, roles e storage columns contra Postgres.

## API/runtime

Classificacao: implementado em codigo.

Validacoes adicionadas:

- API em Supabase com `DB_REQUIRE_SUPABASE_POOLER=true` deve usar porta `6543`.
- API nao pode usar role `postgres`.
- storage local e bloqueado em producao.
- Supabase storage exige bucket e credenciais explicitas em producao.

Classificacao: aplicado no banco/ambiente; observado em execucao real.

- Roles `npbb_api` e `npbb_worker` existem no Supabase observado.
- Ambas estao sem `BYPASSRLS`.

## Worker

Classificacao: implementado em codigo.

Mudancas:

- `backend/scripts/run_leads_worker.py` grava eventos estruturados.
- health file configuravel por `LEADS_WORKER_HEALTH_FILE`.
- retry/failure sleep configuravel por `LEADS_WORKER_FAILURE_SLEEP_SECONDS`.
- worker no blueprint usa `python scripts/run_leads_worker.py`.
- worker exige `WORKER_DATABASE_URL` ou `DIRECT_URL`.
- worker falha se estiver usando pooler Supabase `:6543` em vez de conexao direta.

Classificacao: observado em execucao real.

- Nao houve log real de worker capturado nesta rodada.
- Nao houve prova de processamento real de preview, commit e Gold fora da API nesta rodada.

## Storage

Classificacao: implementado em codigo.

Mudancas:

- `payload_storage.py` bloqueia fallback local em producao.
- `lead_batch_intake_service.py` persiste novos payloads via ponteiro de storage.
- `upload_spool.py` evita leitura integral de upload em memoria.
- testes direcionados validam ponteiro persistido e ausencia de novo blob inline.

Classificacao: aplicado no banco/ambiente; observado em execucao real.

- Supabase observado ainda tem 222 registros `lead_batches` com `arquivo_bronze` pendente.

Conclusao objetiva:

- O caminho novo foi endurecido em codigo.
- O backfill historico nao esta comprovado como executado.
- O deploy operacional do worker e storage nao foi observado por log/runtime nesta rodada.
