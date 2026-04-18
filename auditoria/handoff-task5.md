# Handoff - Task 5 (Performance, memoria e custo - import leads)

## Resumo executivo

- Esta task entregou melhorias localizadas de memoria e polling, sem alterar schema, API publica ou estrategia estrutural de storage.
- O foco real ficou em tres pontos:
  - reduzir memoria no insert Gold evitando `list(DictReader)` do consolidado inteiro;
  - evitar `read()` completo do CSV no fluxo de `publicidade_import`, mantendo compatibilidade com `utf-8-sig` e `latin-1`;
  - reduzir carga de polling no frontend quando o progresso continua `pending`, mas fica muito tempo no mesmo `step|pct`.
- Esta task **nao** resolveu:
  - Bronze como blob na tabela `lead_batches`;
  - snapshots ETL pesados em `lead_import_etl_preview_session`;
  - fila duravel para o Gold;
  - baseline oficial em ambiente alvo com `pg_total_relation_size`.

## Estado da entrega

### Resolvido

- **Gold insert por janelas de lookup**
  - [`backend/app/services/lead_pipeline_service.py`](../backend/app/services/lead_pipeline_service.py)
  - `_inserir_leads_gold()` deixou de materializar o CSV consolidado inteiro em memoria.
  - O total de linhas agora vem de `_count_consolidated_csv_data_rows()`.
  - O lookup passa a ser carregado em janelas configuraveis por `NPBB_LEAD_GOLD_INSERT_LOOKUP_CHUNK_SIZE` (default `1500`, minimo `50`, maximo `50000`).
  - `merge_lead_lookup_context()` junta candidatos sem duplicar `Lead.id` entre janelas.

- **Streaming CSV no backend sem perder fallback de encoding**
  - [`backend/app/services/imports/file_reader.py`](../backend/app/services/imports/file_reader.py)
  - `iter_data_rows()` para `.csv` continua em streaming com `TextIOWrapper` + `csv.reader`, mas agora detecta encoding antes de iterar:
    - valida UTF-8 incrementalmente;
    - faz fallback para `latin-1` sem materializar o upload inteiro;
    - preserva `detach()` no `finally`.
  - Importante: este caminho e usado hoje no fluxo de [`backend/app/services/publicidade_import.py`](../backend/app/services/publicidade_import.py), nao no fluxo legado principal de importacao de leads.

- **Backoff de polling no frontend**
  - [`frontend/src/pages/leads/PipelineStatusPage.tsx`](../frontend/src/pages/leads/PipelineStatusPage.tsx)
  - A Task 5 adiciona backoff de `1500 ms` para `4500 ms` apos `120 s` com o mesmo `step|pct` enquanto o lote segue `pending` e **nao** esta marcado como stale pelo backend.
  - O estado `gold_pipeline_progress_is_stale`, o CTA de retomada e a parada de polling para progresso orfao vieram da Task 4; a Task 5 so aproveita esses sinais.

### Parcial

- **Medicao**
  - [`auditoria/task5-measurement-plan.md`](task5-measurement-plan.md)
  - [`backend/scripts/benchmark_lead_import_task5.py`](../backend/scripts/benchmark_lead_import_task5.py)
  - Existe plano de medicao e script reprodutivel.
  - Existe smoke local do script.
  - **Nao existe baseline oficial preenchido** nem evidencia registada de `pg_total_relation_size` em ambiente alvo.

- **Limites operacionais**
  - [`auditoria/task5-operator-limits.md`](task5-operator-limits.md)
  - O documento esta util para operacao, mas continua provisoriamente conservador porque Bronze e snapshots ETL ainda estao no banco.

### Pendente / fora de escopo desta task

- Bronze em object storage ou outra estrategia que retire blob bruto do banco.
- Compactacao/reducao estrutural de snapshots ETL.
- Fila duravel / retry robusto para pipeline Gold.
- Medicao em ambiente proximo do real com massa grande e queries de tamanho em Postgres.

## Baseline vs depois

| Metrica | Estado atual |
|---------|--------------|
| Script `benchmark_lead_import_task5.py` | Smoke local executado; usar apenas como verificacao do script, nao como baseline oficial. |
| Pico RSS em insert Gold | Ainda nao medido em ambiente alvo. |
| `pg_total_relation_size('lead_batches')` | Ainda nao registado para esta task. |
| `pg_total_relation_size('lead_import_etl_preview_session')` | Ainda nao registado para esta task. |

## Ficheiros tocados nesta entrega

| Caminho | Alteracao |
|---------|-----------|
| [`auditoria/task5-measurement-plan.md`](task5-measurement-plan.md) | Plano de medicao e metas. |
| [`auditoria/task5-operator-limits.md`](task5-operator-limits.md) | Limites recomendados para operadores. |
| [`auditoria/handoff-task5.md`](handoff-task5.md) | Este handoff, revisto para refletir o estado real da task. |
| [`backend/scripts/benchmark_lead_import_task5.py`](../backend/scripts/benchmark_lead_import_task5.py) | Benchmark leve CSV / RSS opcional. |
| [`backend/app/modules/leads_publicidade/application/etl_import/persistence.py`](../backend/app/modules/leads_publicidade/application/etl_import/persistence.py) | `merge_lead_lookup_context`. |
| [`backend/app/services/lead_pipeline_service.py`](../backend/app/services/lead_pipeline_service.py) | `_count_consolidated_csv_data_rows`, `_lead_gold_insert_lookup_chunk_size`, insert Gold por janelas, log `lookup_chunk_size`. |
| [`backend/app/services/imports/file_reader.py`](../backend/app/services/imports/file_reader.py) | `iter_data_rows()` em streaming com deteccao incremental de encoding. |
| [`backend/tests/test_import_file_reader.py`](../backend/tests/test_import_file_reader.py) | Regressao de streaming CSV e fallback `latin-1`. |
| [`backend/tests/test_etl_import_persistence.py`](../backend/tests/test_etl_import_persistence.py) | Teste `merge_lead_lookup_context`. |
| [`backend/tests/test_lead_gold_insert_batching.py`](../backend/tests/test_lead_gold_insert_batching.py) | Testes de `_count_consolidated_csv_data_rows` e lookup chunking. |
| [`backend/tests/test_lead_gold_pipeline.py`](../backend/tests/test_lead_gold_pipeline.py) | Cobertura do estado stale herdado da Task 4, reutilizado pelo frontend. |
| [`frontend/src/pages/leads/PipelineStatusPage.tsx`](../frontend/src/pages/leads/PipelineStatusPage.tsx) | Backoff de polling quando `step|pct` ficam estagnados. |
| [`frontend/src/pages/__tests__/PipelineStatusPage.test.tsx`](../frontend/src/pages/__tests__/PipelineStatusPage.test.tsx) | Teste dedicado do backoff de polling e teste separado de stale/orphan. |
| [`frontend/src/services/leads_import.ts`](../frontend/src/services/leads_import.ts) | Comentario e tipos ja alinhados com o comportamento do polling/stale. |

## Variaveis de ambiente

| Variavel | Default | Efeito |
|----------|---------|--------|
| `NPBB_LEAD_GOLD_INSERT_LOOKUP_CHUNK_SIZE` | `1500` | Linhas por janela de `_load_lead_lookup_context()` no insert Gold. |
| `LEAD_GOLD_INSERT_COMMIT_BATCH_SIZE` | `100` | Tamanho do commit parcial no insert Gold. |

## Diffs / revisao

```bash
git diff main -- auditoria/task5-measurement-plan.md auditoria/task5-operator-limits.md auditoria/handoff-task5.md
git diff main -- backend/scripts/benchmark_lead_import_task5.py backend/app/services/lead_pipeline_service.py backend/app/modules/leads_publicidade/application/etl_import/persistence.py backend/app/services/imports/file_reader.py backend/tests/
git diff main -- frontend/src/pages/leads/PipelineStatusPage.tsx frontend/src/pages/__tests__/PipelineStatusPage.test.tsx frontend/src/services/leads_import.ts
```

## Testes executados

```bash
cd backend
$env:PYTHONPATH="<repo>;<repo>/backend"; $env:TESTING="true"; $env:SECRET_KEY="ci-secret-key"
python -m pytest tests/test_import_file_reader.py tests/test_lead_gold_insert_batching.py tests/test_etl_import_persistence.py::test_merge_lead_lookup_context_deduplicates_lead_ids tests/test_lead_gold_pipeline.py -q

cd ../frontend
npx vitest run src/pages/__tests__/PipelineStatusPage.test.tsx

cd ..
python backend/scripts/benchmark_lead_import_task5.py --rows 5000
```

## Validacao manual dirigida

- Reproduzido CSV `latin-1` com acento para confirmar paridade entre preview e `iter_data_rows()`.
- Confirmado que o handoff revisto nao afirma baseline oficial nem metricas de DB que nao foram capturadas.

## Deploy

1. Sem migracao Alembic nesta entrega.
2. Ajustar `NPBB_LEAD_GOLD_INSERT_LOOKUP_CHUNK_SIZE` so se for necessario trocar memoria por mais queries de lookup no Postgres.
3. Nao ha mudanca de contrato HTTP nem de schema para coordenar com frontend/backend.

## Riscos residuais

- O ganho de memoria desta task e real, mas localizado:
  - Bronze continua como blob no banco;
  - preview ETL continua pesado;
  - pipeline Gold continua sem fila duravel.
- A deteccao incremental de UTF-8 evita regressao de `latin-1`, mas faz uma passada de validacao no stream antes da iteracao efetiva; o objetivo aqui e reduzir memoria, nao minimizar IO.
- O backoff do frontend reduz carga quando o progresso fica estagnado, mas nao substitui a logica de stale/reclaim da Task 4.

## Referencia

- Pedido: [`auditoria/task5.md`](task5.md)
- Contexto: [`auditoria/deep-research-report.md`](deep-research-report.md)
- Stale/reclaim do pipeline Gold: [`auditoria/handoff-task4.md`](handoff-task4.md)
