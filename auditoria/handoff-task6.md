# Handoff - Task 6 (Rastreabilidade: linha do ficheiro original ate ao Gold)

## Resumo

- `row_index` em `leads_silver` continua a significar a posicao da linha dentro das linhas de dados apos deteccao de cabecalho e remocao de linhas vazias. Ele continua a servir apenas para ordenacao estavel (`ORDER BY row_index, id`).
- `source_row_original` passou a ser o campo canonico de rastreio no JSON `dados_brutos`. `source_row` continua presente por compatibilidade com o `lead_pipeline` e com o CSV Silver.
- Quando o batch e mapeado apos esta task, `source_file`, `source_sheet`, `source_row` e `source_row_original` passam a refletir o ficheiro/folha/linha fisica 1-based do upload original, inclusive quando existem linhas em branco entre os dados.
- Na materializacao Silver -> CSV, o backend usa `source_row_original` em preferencia a `source_row`. Se ambos faltarem em lotes Silver antigos, o backend relera o Bronze e reconstruira a linha fisica com `physical_line_numbers`; se isso nao for possivel, cai no fallback aritmetico por `row_index + (start_index + 2)`.
- A UI passou a expor essa referencia como "linha fisica" / "Linhas no ficheiro original".

## O que ficou resolvido

- Reader de importacao agora devolve `ImportPreviewResult.physical_line_numbers`, alinhado a `rows`, tanto no preview completo como na leitura por janela.
- `mapear_batch()` persiste `source_file`, `source_sheet`, `source_row` e `source_row_original` no Silver a partir das linhas fisicas calculadas pelo reader.
- `materializar_silver_como_csv()` usa ordem deterministica: `ORDER BY LeadSilver.row_index, LeadSilver.id`.
- `materializar_silver_como_csv()` prefere `source_row_original` sobre `source_row`.
- Compatibilidade com lotes Silver antigos sem `source_row`/`source_row_original` foi endurecida:
  - CSV legado com linhas em branco passa a reconstruir a linha fisica correta a partir de `physical_line_numbers`, nao apenas por offset.
  - XLSX legado sem `source_sheet` e sem `source_row*` passa a reconstruir folha e linha fisica a partir do Bronze.
  - CSV com `source_sheet == ""` deixou de forcar releitura do Bronze quando `source_row` ou `source_row_original` ja estao presentes; para CSV, string vazia continua a ser valor valido de folha.

## Limitacoes e risco residual

- Lotes Silver criados antes desta task podem cair em tres cenarios diferentes:
  - sem `source_row_original`, mas com `source_row` correto: a materializacao continua funcional;
  - sem ambos os campos: a materializacao tenta reconstruir a linha fisica relendo o Bronze;
  - com `source_row` ja persistido com a semantica antiga: o backend preserva esse valor por compatibilidade, entao a normalizacao total ainda exige remapeamento do batch.
- Nao houve migracao de schema nem backfill em massa.
- O contrato HTTP do relatorio Gold nao mudou: o backend continua a expor `source_row`, agora com semantica corrigida para lotes novos e fallback melhorado para lotes antigos sem metadados.

## Ficheiros tocados

| Caminho | Alteracao |
| --- | --- |
| [backend/app/services/imports/contracts.py](backend/app/services/imports/contracts.py) | `ImportPreviewResult` ganhou `physical_line_numbers`. |
| [backend/app/services/imports/file_reader.py](backend/app/services/imports/file_reader.py) | Leitura de CSV/XLSX passou a calcular linhas fisicas ao filtrar linhas vazias. |
| [backend/app/services/lead_mapping.py](backend/app/services/lead_mapping.py) | Silver passa a persistir `source_row` e `source_row_original` com linha fisica. |
| [backend/app/services/lead_pipeline_service.py](backend/app/services/lead_pipeline_service.py) | Materializacao ordena de forma estavel, prefere `source_row_original` e reconstrui fallback legado via `physical_line_numbers`. |
| [backend/tests/test_import_file_reader.py](backend/tests/test_import_file_reader.py) | Cobertura para preview XLSX e CSV com linha em branco. |
| [backend/tests/test_lead_silver_mapping.py](backend/tests/test_lead_silver_mapping.py) | Cobertura para persistencia de `source_row_original` e linha fisica em CSV/XLSX. |
| [backend/tests/test_lead_batch_endpoints.py](backend/tests/test_lead_batch_endpoints.py) | Fake de preview atualizado com `physical_line_numbers`. |
| [backend/tests/test_lead_gold_pipeline.py](backend/tests/test_lead_gold_pipeline.py) | Regressao para preferencia de `source_row_original` e compatibilidade legado CSV/XLSX. |
| [frontend/src/pages/leads/PipelineStatusPage.tsx](frontend/src/pages/leads/PipelineStatusPage.tsx) | Labels ajustados para "linha fisica" / "Linhas no ficheiro original". |

## Testes executados

```bash
cd backend
$env:PYTHONPATH="<repo>;<repo>/backend"; $env:TESTING="true"; $env:SECRET_KEY="ci-secret-key"
python -m pytest tests/test_import_file_reader.py tests/test_lead_silver_mapping.py::TestPostMapear tests/test_lead_batch_endpoints.py::TestGetBatchPreview::test_preview_uses_windowed_reader tests/test_lead_gold_pipeline.py::test_materializar_prefers_source_row_original_over_source_row tests/test_lead_gold_pipeline.py::test_materializar_legacy_csv_recovers_physical_source_rows_from_bronze tests/test_lead_gold_pipeline.py::test_materializar_legacy_xlsx_recovers_sheet_and_physical_source_rows_from_bronze tests/test_lead_gold_pipeline.py::TestLeadEventoInGoldPipeline::test_missing_birth_date_dq_reports_physical_line_after_blank_csv_row -q

cd frontend
npm run test:ui -- src/pages/__tests__/PipelineStatusPage.test.tsx
```

## Proximo passo recomendado

- Se houver necessidade operacional sobre batches pre-Task-6, o caminho mais confiavel continua a ser remapear o lote (`POST .../mapear`) para gravar `source_row_original` diretamente no Silver.
- Se o objetivo for apenas manter compatibilidade de leitura para lotes antigos sem esses metadados, a materializacao atual ja cobre CSV e XLSX relendo o Bronze quando necessario.

## Referencia

- Pedido: [auditoria/task6.md](task6.md)
- Contexto: [auditoria/deep-research-report.md](deep-research-report.md)
- Task anterior: [auditoria/handoff-task5.md](handoff-task5.md)
