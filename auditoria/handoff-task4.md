# Handoff — Task 4 (Pipeline Gold: durabilidade, retomada e lotes presos)

## Resumo do desenho

- **Sem fila externa** (RQ/Celery/SQS): mitigação no monólito alinhada ao [deep-research-report.md](deep-research-report.md) e ao [task4.md](task4.md).
- **Orfão / lock preso**: `pipeline_status=pending` com `pipeline_progress` cujo `updated_at` excede `NPBB_PIPELINE_STALE_AFTER_SECONDS` (default **420 s**) é tratado como **execução morta**; `POST /leads/batches/{id}/executar-pipeline` com `SELECT … FOR UPDATE` **re-enfileira** via `queue_pipeline_batch` em vez de devolver 409.
- **Heartbeat**: durante `run_pipeline` (CPU no executor), tarefa asyncio re-persiste o último `PipelineProgressEvent` (ou um passo sintético `normalize_rows`) a cada `NPBB_PIPELINE_HEARTBEAT_DURING_RUN_SECONDS` (default **15 s**) para refrescar `updated_at` e reduzir falsos “stale” em jobs longos.
- **Estado `stalled`**: novo valor em `PipelineStatus` + migração Postgres `ALTER TYPE pipelinestatus ADD VALUE 'STALLED'`. Existe helper (`mark_gold_pipeline_batch_stalled_worker_lost`) para construir `failure_context` + `resume_context`, e `POST executar-pipeline` em `stage=silver` **aceita** `pipeline_progress is None` e volta a enfileirar. Importante: **nesta task não ficou ligada uma deteção automática que grave `stalled` após kill/restart**; o caminho automático hoje é `pending` + `gold_pipeline_progress_is_stale=true` e reclaim no próximo `POST`.
- **API/UI**: `LeadBatchRead` inclui `gold_pipeline_stale_after_seconds` e `gold_pipeline_progress_is_stale` (derivados no `GET`, sem escrita). `ExecutarPipelineResponse` inclui `reclaimed_stale_lock: bool` quando o despacho libertou lock obsoleto. Após a revisão desta sessão, a `PipelineStatusPage` trata `gold_pipeline_progress_is_stale` como **estado recuperável**: pára o polling, mantém o aviso visível e expõe ação de **retomar**; superfícies auxiliares do fluxo de importação agora rotulam `stalled` como interrompido/retomável.
- **Task 3**: sem alteração à idempotência Gold / `begin_nested` no insert; apenas reentradas seguras após libertação.

## Ficheiros tocados

| Caminho | Alteração |
|---------|-----------|
| [backend/app/models/lead_batch.py](backend/app/models/lead_batch.py) | `PipelineStatus.STALLED`. |
| [backend/alembic/versions/b2c3d4e5f7a8_add_pipeline_status_stalled.py](backend/alembic/versions/b2c3d4e5f7a8_add_pipeline_status_stalled.py) | Migração Postgres (ADD VALUE com DO/EXCEPTION). |
| [backend/app/services/lead_pipeline_service.py](backend/app/services/lead_pipeline_service.py) | `load_batch_without_bronze_for_update`, stale/heartbeat env, `is_gold_pipeline_progress_stale`, `mark_gold_pipeline_batch_stalled_worker_lost`, `_build_worker_lost_stall_report`, `_run_pipeline_with_heartbeat` em `executar_pipeline_gold`. |
| [backend/app/schemas/lead_batch.py](backend/app/schemas/lead_batch.py) | Campos opcionais no read + `reclaimed_stale_lock` na resposta de execução. |
| [backend/app/routers/leads.py](backend/app/routers/leads.py) | `get_batch` enriquecido; `disparar_pipeline` com `FOR UPDATE`, ramo stale e resposta estendida. |
| [backend/tests/test_lead_gold_pipeline.py](backend/tests/test_lead_gold_pipeline.py) | Regressões stale/fresh, `stalled`, metadata GET. |
| [frontend/src/services/leads_import.ts](frontend/src/services/leads_import.ts) | Tipos `LeadBatch` / `ExecutarPipelineResult`. |
| [frontend/src/pages/leads/PipelineStatusPage.tsx](frontend/src/pages/leads/PipelineStatusPage.tsx) | Chip `stalled`, avisos orfão vs lento, `Retomar Pipeline` quando o backend marca `gold_pipeline_progress_is_stale=true`, e paragem do polling nesse estado. |
| [frontend/src/pages/leads/importacao/BatchSummaryCard.tsx](frontend/src/pages/leads/importacao/BatchSummaryCard.tsx) | `stalled` já não aparece como “pendente”; mostra “interrompido (retomável)”. |
| [frontend/src/pages/leads/importacao/batch/BatchUploadRow.tsx](frontend/src/pages/leads/importacao/batch/BatchUploadRow.tsx) | Estado downstream `stalled` rotulado como interrompido/retomável. |
| [frontend/src/pages/leads/importacao/batch/BatchWorkspaceSummaryCard.tsx](frontend/src/pages/leads/importacao/batch/BatchWorkspaceSummaryCard.tsx) | Linhas `stalled` entram na contagem/atalho de pipeline pendente-retomável. |
| [frontend/src/pages/__tests__/PipelineStatusPage.test.tsx](frontend/src/pages/__tests__/PipelineStatusPage.test.tsx) | Regressão: progresso stale do servidor mantém CTA de retomar e deixa de pollar. |
| [auditoria/handoff-task4.md](auditoria/handoff-task4.md) | Este ficheiro. |

## Variáveis de ambiente

| Variável | Default | Efeito |
|----------|---------|--------|
| `NPBB_PIPELINE_STALE_AFTER_SECONDS` | `420` | Idade máxima de `pipeline_progress.updated_at` antes de considerar orfão (mínimo 60, máximo 86400). |
| `NPBB_PIPELINE_HEARTBEAT_DURING_RUN_SECONDS` | `15` | Intervalo entre refrescos de progresso durante `run_pipeline` (mínimo 5, máximo 300). |

## Diffs / revisão (por área)

```bash
git diff main -- backend/app/models/lead_batch.py \
  backend/alembic/versions/b2c3d4e5f7a8_add_pipeline_status_stalled.py \
  backend/app/services/lead_pipeline_service.py \
  backend/app/schemas/lead_batch.py \
  backend/app/routers/leads.py \
  backend/tests/test_lead_gold_pipeline.py \
  frontend/src/services/leads_import.ts \
  frontend/src/pages/leads/PipelineStatusPage.tsx \
  frontend/src/pages/leads/importacao/BatchSummaryCard.tsx \
  frontend/src/pages/leads/importacao/batch/BatchUploadRow.tsx \
  frontend/src/pages/leads/importacao/batch/BatchWorkspaceSummaryCard.tsx \
  frontend/src/pages/__tests__/PipelineStatusPage.test.tsx \
  auditoria/handoff-task4.md
```

## Deploy

1. **Alembic** `upgrade head` (adiciona valor ao enum Postgres) **antes** de colocar API nova em serviço.
2. **API** — sem worker separado; `BackgroundTasks` inalterado.
3. **Lotes `pending` com progresso antigo em produção**: após deploy, o primeiro `POST executar-pipeline` válido **re-enfileira** em vez de 409; operadores já não precisam de SQL manual para esse caso.

## Riscos

- **`FOR UPDATE` em Postgres**: bloqueia concorrência no mesmo `batch_id` durante o despacho (desejável).
- **SQLite / testes**: `FOR UPDATE` é no-op; concorrência real só em Postgres.
- **Heartbeat**: carga extra de `COMMIT` no intervalo configurado; aumentar demasiado o intervalo reduz proteção contra orfão; reduzir demasiado aumenta escrita em BD.
- **Kill real do processo**: a cobertura automática valida stale/reclaim e heartbeat, mas a prova de “matar o worker no meio” continua manual; não há teste end-to-end que reinicie a API e observe o reclaim em Postgres real.

## Verificação manual mínima (critério task4)

1. Silver pronto → `POST …/executar-pipeline` → durante `normalize_rows`, **terminar o processo** do servidor (kill).
2. Confirmar `GET …/batches/{id}`: `gold_pipeline_progress_is_stale` passa a `true` após ~7 min (default 420 s) **ou** ajustar `NPBB_PIPELINE_STALE_AFTER_SECONDS=61` em ambiente de teste e esperar 61 s.
3. `POST …/executar-pipeline` de novo → **202**, `reclaimed_stale_lock: true`, progresso volta a `queued`.

## Testes automáticos

```bash
cd backend
$env:PYTHONPATH="<repo>;<repo>/backend"; $env:TESTING="true"; $env:SECRET_KEY="ci-secret-key"
python -m pytest tests/test_lead_gold_pipeline.py::TestGetBatch tests/test_lead_gold_pipeline.py::TestExecutarPipeline -q

cd ../frontend
npx vitest run src/pages/__tests__/PipelineStatusPage.test.tsx
```

## Referência

- Pedido: [auditoria/task4.md](task4.md)
- Contexto: [auditoria/deep-research-report.md](deep-research-report.md)
- Dedupe Gold anterior: [auditoria/handoff-task3.md](handoff-task3.md)
