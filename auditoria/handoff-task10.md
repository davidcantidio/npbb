# Handoff — Task 10 (observabilidade: métricas, logs e lotes presos)

## Resumo executivo

- **Objetivo:** correlacionar operação de importação de leads (`batch_id`, `session_token`, `request_id`), expor métricas Prometheus, logs JSON pesquisáveis, agregação de rejeições ETL por motivo e documentação de deteção de lotes Gold presos, alinhado a [auditoria/task10.md](task10.md) e [auditoria/deep-research-report.md](deep-research-report.md).
- **Logs estruturados (JSON):** módulo [`backend/app/observability/import_events.py`](../backend/app/observability/import_events.py) — `log_import_event` com `component=lead_import`, `event`, `ts`, `request_id` (quando existir). Desligar JSON e voltar ao formato legível: `NPBB_IMPORT_JSON_LOGS=0`.
- **Correlação HTTP:** middleware [`RequestIDMiddleware`](../backend/app/observability/request_id_middleware.py) em [`backend/app/main.py`](../backend/app/main.py) — lê ou gera `X-Request-ID`, devolve no header da resposta, exposto em CORS (`expose_headers`).
- **Métricas Prometheus:** [`backend/app/observability/prometheus_leads_import.py`](../backend/app/observability/prometheus_leads_import.py) + endpoint `GET /internal/metrics` em [`backend/app/routers/internal_metrics.py`](../backend/app/routers/internal_metrics.py).
- **ETL preview:** contagem por motivo em `rejection_reason_counts` na resposta [`ImportEtlPreviewResponse`](../backend/app/schemas/lead_import_etl.py); agregação em [`rejection_reasons.py`](../backend/app/modules/leads_publicidade/application/etl_import/rejection_reasons.py); contadores Prometheus incrementados apenas ao **criar** snapshot novo em [`preview_session_repository.create_snapshot`](../backend/app/modules/leads_publicidade/application/etl_import/preview_session_repository.py) (evita duplicar em cache idempotente).
- **Upload:** `record_import_upload_rejection` em falhas `ImportFileError` — [`extract.read_upload_bytes`](../backend/app/modules/leads_publicidade/application/etl_import/extract.py), rotas em [`leads.py`](../backend/app/routers/leads.py) e [`publicidade.py`](../backend/app/routers/publicidade.py).
- **Gold:** `_log_pipeline_event` passa a emitir JSON via `log_import_event`; histogramas `npbb_lead_gold_pipeline_stage_duration_seconds` para `run_pipeline`, `insert_leads`, `execution_total`; contador `npbb_lead_gold_pipeline_reclaimed_stale_total` ao reclamar lock stale no dispatch em [`leads.py`](../backend/app/routers/leads.py).

## Séries e campos Prometheus

| Nome | Tipo | Labels | Quando incrementa / observa |
|------|------|--------|-----------------------------|
| `npbb_lead_import_upload_rejected_total` | Counter | `code` | Falha em `inspect_upload` / `ImportFileError` |
| `npbb_lead_etl_preview_row_rejections_total` | Counter | `reason` | Uma vez por linha rejeitada ao persistir preview novo (`adapter_error`, `cpf_missing`, …) |
| `npbb_lead_gold_pipeline_stage_duration_seconds` | Histogram | `step` | Conclusão `run_pipeline`, `insert_leads`, duração total `execution_total` |
| `npbb_lead_gold_pipeline_reclaimed_stale_total` | Counter | — | Dispatch Gold reclama progresso `pending` stale |

## Autenticação `/internal/metrics`

- **JWT/cookie NPBB** (`UsuarioTipo.NPBB`), ou
- **Query** `?token=` igual a `NPBB_METRICS_SCRAPE_TOKEN` (se definido), para scrape sem sessão interativa.

## Variáveis de ambiente

| Variável | Efeito |
|----------|--------|
| `NPBB_IMPORT_JSON_LOGS` | `1` (default): logs `lead_import` em JSON; `0`: formato texto legado. |
| `NPBB_METRICS_SCRAPE_TOKEN` | Token opcional para `GET /internal/metrics?token=...`. |
| `NPBB_PIPELINE_STALE_AFTER_SECONDS` | Já existente; idade máxima (s) de `pipeline_progress.updated_at` antes de considerar stale (default 420). |

## Consultas operacionais

### SQL (Postgres) — lotes Gold `pending` com progresso antigo

Ajuste o intervalo ao mesmo valor operacional que `NPBB_PIPELINE_STALE_AFTER_SECONDS` (ex.: 7 minutos):

```sql
SELECT id,
       pipeline_status,
       stage,
       pipeline_progress->>'step' AS last_step,
       pipeline_progress->>'updated_at' AS progress_updated_at
FROM lead_batches
WHERE pipeline_status = 'pending'
  AND pipeline_progress IS NOT NULL
  AND (pipeline_progress->>'updated_at')::timestamptz
        < (NOW() AT TIME ZONE 'utc') - INTERVAL '7 minutes'
ORDER BY (pipeline_progress->>'updated_at')::timestamptz ASC
LIMIT 100;
```

### Loki (exemplo)

Filtrar eventos JSON com `batch_id`:

```logql
{job="npbb-api"} |= `"component":"lead_import"` |= `"batch_id":123`
```

Filtrar preview ETL por prefixo de sessão (10 primeiros caracteres do token):

```logql
{job="npbb-api"} |= `"event":"etl.preview.completed"` |= `"session_token_prefix":"abc12"`
```

### Alerta Prometheus (exemplo)

Contagem de lotes presos costuma vir de **SQL agendado** ou exporter externo; exemplo de alerta sobre **reclamações de lock** (sinal de lotes órfãos frequentes):

```yaml
groups:
  - name: npbb_leads
    rules:
      - alert: NpbbGoldPipelineStaleReclaimsHigh
        expr: rate(npbb_lead_gold_pipeline_reclaimed_stale_total[15m]) > 0.1
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Reclamações frequentes de pipeline Gold stale"
```

Ajuste o limiar ao volume real.

## Runbook curto — lote Gold “preso”

1. Confirmar `GET /leads/batches/{id}` e `gold_pipeline_progress_is_stale`.
2. Pesquisar logs JSON com `batch_id` e eventos `gold.*`.
3. Se stale e operação segura, re-dispatch do pipeline (o router já reclama lock stale antes de enfileirar).
4. Se falha repetida, inspecionar `pipeline_report` e SQL acima; escalar com `batch_id` e intervalo sem `updated_at`.

## Ficheiros alterados / novos

| Caminho | Alteração |
|---------|-----------|
| `backend/app/observability/__init__.py` | Novo pacote |
| `backend/app/observability/import_events.py` | `log_import_event`, `ContextVar` request id, prefixo de token |
| `backend/app/observability/request_id_middleware.py` | `X-Request-ID` |
| `backend/app/observability/prometheus_leads_import.py` | Métricas + `record_import_upload_rejection` |
| `backend/app/routers/internal_metrics.py` | `GET /internal/metrics` |
| `backend/app/main.py` | Middleware + router |
| `backend/app/services/lead_pipeline_service.py` | Logs JSON + histogramas |
| `backend/app/modules/.../preview_service.py` | Logs ETL preview |
| `backend/app/modules/.../commit_service.py` | Logs ETL commit |
| `backend/app/modules/.../extract.py` | Métrica/log em `ImportFileError` |
| `backend/app/modules/.../preview_session_repository.py` | Métricas por linha rejeitada (snapshot novo) |
| `backend/app/modules/.../rejection_reasons.py` | Agregação por motivo |
| `backend/app/routers/leads.py` | Upload + `rejection_reason_counts` + reclaim metric |
| `backend/app/routers/publicidade.py` | Upload rejections |
| `backend/app/schemas/lead_import_etl.py` | Campo `rejection_reason_counts` |
| `backend/requirements.txt` | `prometheus-client==0.21.1` |
| `backend/tests/test_etl_rejection_reasons.py` | Novos testes unitários |
| `backend/tests/test_internal_metrics.py` | Auth do endpoint |
| `backend/tests/test_leads_import_etl_endpoint.py` | Asserção agregados |

## Dependência nova

- `prometheus-client==0.21.1` ([`backend/requirements.txt`](../backend/requirements.txt))

## Diffs / revisão

```bash
git diff -- backend/app/observability backend/app/main.py backend/app/routers/internal_metrics.py \
  backend/app/routers/leads.py backend/app/routers/publicidade.py \
  backend/app/services/lead_pipeline_service.py backend/requirements.txt \
  backend/app/modules/leads_publicidade/application/etl_import/
git diff -- backend/tests/test_etl_rejection_reasons.py backend/tests/test_internal_metrics.py \
  backend/tests/test_leads_import_etl_endpoint.py
```

## Verificação

```powershell
cd backend
$env:PYTHONPATH='c:\Users\NPBB\npbb'   # ajustar à raiz do clone
python -m pytest tests/test_etl_rejection_reasons.py tests/test_internal_metrics.py `
  tests/test_leads_import_etl_endpoint.py tests/test_lead_gold_pipeline.py `
  tests/test_lead_batch_endpoints.py tests/test_import_file_reader.py
```

## Referências

- Pedido: [auditoria/task10.md](task10.md)
- Contexto upload (task 9): [auditoria/handoff-task9.md](handoff-task9.md)
- Relatório: [auditoria/deep-research-report.md](deep-research-report.md)
