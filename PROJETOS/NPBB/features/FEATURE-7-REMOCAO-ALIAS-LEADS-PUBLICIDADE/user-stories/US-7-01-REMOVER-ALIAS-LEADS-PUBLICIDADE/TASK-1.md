---
doc_id: "TASK-1.md"
user_story_id: "US-7-01-REMOVER-ALIAS-LEADS-PUBLICIDADE"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-04-23"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/app/modules/leads_publicidade/**"
  - "backend/tests/test_lead_imports_compat.py"
  - "plano_organizacao_import.md"
  - "PROJETOS/NPBB/INTAKE-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md"
  - "PROJETOS/NPBB/PRD-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md"
  - "PROJETOS/NPBB/features/FEATURE-7-REMOCAO-ALIAS-LEADS-PUBLICIDADE/**"
tdd_aplicavel: true
---

# T1 - Remover alias legado leads_publicidade

## objetivo

Remover a compatibilidade temporaria `app.modules.leads_publicidade`, mantendo
`app.modules.lead_imports` como unico caminho real e sem mudar comportamento
funcional.

## passos_atomicos

1. confirmar ausencia de consumidores ativos com `rg`
2. remover `backend/app/modules/leads_publicidade/**`
3. remover `backend/tests/test_lead_imports_compat.py`
4. atualizar governanca e `plano_organizacao_import.md`
5. executar buscas finais
6. executar validacoes focadas

## comandos_permitidos

- `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend/app backend/scripts backend/tests -g "!backend/app/modules/leads_publicidade/**" -g "!backend/tests/test_lead_imports_compat.py"`
- `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend docs PROJETOS plano_organizacao_import.md`
- `rg -n "app\\.modules\\.lead_imports|lead_imports" backend/app backend/scripts backend/tests`
- `Test-Path backend/app/modules/leads_publicidade`
- `cd backend && PYTHONPATH=C:\Users\NPBB\npbb;C:\Users\NPBB\npbb\backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q backend/tests/test_leads_import_etl_usecases.py backend/tests/test_etl_import_persistence.py backend/tests/test_lead_merge_policy.py backend/tests/test_etl_rejection_reasons.py backend/tests/test_etl_import_validators.py backend/tests/test_etl_csv_delimiter.py backend/tests/test_leads_import_etl_warning_policy.py backend/tests/test_leads_import_etl_staging_repository.py backend/tests/test_leads_import_etl_endpoint.py backend/tests/test_lead_silver_mapping.py backend/tests/test_lead_ticketing_dedupe_postgres.py`

## stop_conditions

- parar se aparecer consumidor ativo de `app.modules.leads_publicidade` fora
  dos shims e do teste dedicado
- parar se a rodada exigir alteracao funcional em ETL, persistencia,
  validadores ou merge policy
- parar se houver necessidade de alterar contratos HTTP, schemas, rotas,
  frontend, dashboard, `lead_pipeline/` ou `core/leads_etl/`

## resultado

- 2026-04-23: busca inicial sem consumidores ativos fora dos shims e do teste
  dedicado.
- 2026-04-23: `backend/app/modules/leads_publicidade` removido.
- 2026-04-23: teste `backend/tests/test_lead_imports_compat.py` removido.
- 2026-04-23: `app.modules.lead_imports` preservado como caminho real.
- 2026-04-23: nenhum contrato HTTP, schema, rota publica, frontend,
  dashboard, `lead_pipeline/` ou `core/leads_etl/` foi alterado por esta task.
