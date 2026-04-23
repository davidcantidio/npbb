---
doc_id: "TASK-1.md"
user_story_id: "US-6-01-IMPLEMENTAR-RENAME-MODULO-LEAD-IMPORTS"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-04-23"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/app/modules/lead_imports/**"
  - "backend/app/modules/leads_publicidade/**"
  - "backend/app/routers/leads_routes/classic_import.py"
  - "backend/app/routers/leads_routes/etl_import.py"
  - "backend/app/services/lead_pipeline_service.py"
  - "backend/scripts/run_leads_worker.py"
  - "backend/tests/test_*"
  - "plano_organizacao_import.md"
  - "PROJETOS/NPBB/INTAKE-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md"
  - "PROJETOS/NPBB/PRD-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md"
  - "PROJETOS/NPBB/features/FEATURE-6-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS/**"
tdd_aplicavel: true
---

# T1 - Implementar pacote lead_imports e compatibilidade legada

## objetivo

Executar o rename planejado de `app.modules.leads_publicidade` para
`app.modules.lead_imports`, mantendo o caminho antigo como alias temporario e
sem mudar comportamento funcional.

## passos_atomicos

1. confirmar consumidores com `rg`
2. criar `backend/app/modules/lead_imports` a partir da implementacao existente
3. ajustar imports absolutos internos do pacote novo para
   `app.modules.lead_imports`
4. transformar modulos folha do pacote antigo em shims para o pacote novo
5. migrar imports ativos em routers, servico, worker e testes focados
6. adicionar teste de compatibilidade para import legado profundo e monkeypatch
   por string
7. atualizar governanca e `plano_organizacao_import.md`
8. executar validacoes focadas

## comandos_permitidos

- `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade|app\\.modules\\.lead_imports|lead_imports" backend docs PROJETOS plano_organizacao_import.md`
- `Get-ChildItem -Recurse -Depth 3 backend/app/modules/leads_publicidade`
- `Get-ChildItem -Recurse -Depth 3 backend/app/modules/lead_imports`
- `cd backend && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q backend/tests/test_lead_imports_compat.py backend/tests/test_leads_import_etl_usecases.py backend/tests/test_etl_import_persistence.py backend/tests/test_lead_merge_policy.py backend/tests/test_etl_rejection_reasons.py backend/tests/test_etl_import_validators.py backend/tests/test_etl_csv_delimiter.py backend/tests/test_leads_import_etl_warning_policy.py backend/tests/test_leads_import_etl_staging_repository.py backend/tests/test_leads_import_etl_endpoint.py backend/tests/test_lead_silver_mapping.py backend/tests/test_lead_ticketing_dedupe_postgres.py`

## stop_conditions

- parar se a rodada exigir alteracao funcional em ETL, persistencia,
  validadores ou merge policy
- parar se houver necessidade de alterar contratos HTTP, schemas, rotas,
  frontend, dashboard, `lead_pipeline/` ou `core/leads_etl/`
- parar se a remocao do alias antigo for necessaria nesta mesma rodada

## resultado

- 2026-04-23: `backend/app/modules/lead_imports` criado como pacote real.
- 2026-04-23: imports ativos de producao, worker e testes focados migrados
  para `app.modules.lead_imports`.
- 2026-04-23: `backend/app/modules/leads_publicidade` mantido como camada de
  compatibilidade temporaria.
- 2026-04-23: teste `backend/tests/test_lead_imports_compat.py` adicionado para
  validar import profundo legado e monkeypatch por string.
- 2026-04-23: suite focada backend executada com `136 passed, 1 skipped`.
- 2026-04-23: nenhum contrato HTTP, schema, rota publica, frontend, dashboard,
  `lead_pipeline/` ou `core/leads_etl/` foi alterado por esta task.
