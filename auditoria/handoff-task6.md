# Handoff — Task 6 (Rastreabilidade: linha do ficheiro original até ao Gold)

## Resumo

- **`row_index` (tabela `leads_silver`):** índice da linha na lista de **linhas de dados** após deteção de cabeçalho e **remoção de linhas vazias** no segmento de dados — continua a servir ordenação estável (`ORDER BY row_index, id`).
- **`source_row` e `source_row_original` (JSON `dados_brutos`):** ambos passam a refletir a **linha física 1-based** no ficheiro (CSV) ou na folha (XLSX), incluindo linhas em branco entre dados. `source_row_original` é o campo explícito de rastreio; `source_row` mantém o mesmo valor para compatibilidade com o pacote `lead_pipeline` e CSV Silver.
- **`ImportPreviewResult.physical_line_numbers`:** lista alinhada a `rows`, preenchida em `_build_preview_result` e `_read_preview_window_from_rows` quando a extração é feita pelo `file_reader`.
- **Materialização Silver → CSV:** `ORDER BY LeadSilver.row_index, LeadSilver.id`; coluna CSV `source_row` usa `source_row_original` em preferência a `source_row`, depois fallback `row_index + (start_index+2)` e releitura do Bronze se metadados faltarem.
- **Frontend:** métricas de qualidade mostram “linha física” / “Linhas no ficheiro original” para alinhar a UI à semântica.

## Ficheiros tocados

| Caminho | Alteração |
|---------|-----------|
| [backend/app/services/imports/contracts.py](backend/app/services/imports/contracts.py) | Campo `physical_line_numbers` em `ImportPreviewResult`. |
| [backend/app/services/imports/file_reader.py](backend/app/services/imports/file_reader.py) | Cálculo de linha física ao filtrar linhas vazias (preview completo e janela). |
| [backend/app/services/lead_mapping.py](backend/app/services/lead_mapping.py) | `source_row` / `source_row_original` a partir de `physical_line_numbers` com fallback. |
| [backend/app/services/lead_pipeline_service.py](backend/app/services/lead_pipeline_service.py) | `ORDER BY` com `id`; leitura de `source_row_original`; condição de fallback de metadados. |
| [backend/tests/test_import_file_reader.py](backend/tests/test_import_file_reader.py) | `physical_line_numbers` no preview XLSX; CSV com linha em branco. |
| [backend/tests/test_lead_silver_mapping.py](backend/tests/test_lead_silver_mapping.py) | Expectativas `source_row_original`; teste CSV com linha em branco; `ImportPreviewResult` em monkeypatch. |
| [backend/tests/test_lead_batch_endpoints.py](backend/tests/test_lead_batch_endpoints.py) | `physical_line_numbers` no fake de preview. |
| [backend/tests/test_lead_gold_pipeline.py](backend/tests/test_lead_gold_pipeline.py) | `_upload_batch(..., file_content=)`; materializar prefere `source_row_original`; integração Gold + CSV com linha em branco. |
| [frontend/src/pages/leads/PipelineStatusPage.tsx](frontend/src/pages/leads/PipelineStatusPage.tsx) | Labels “linha física” / “Linhas no ficheiro original”. |

## Dados existentes e compatibilidade

- Lotes Silver **antes** desta alteração: podem não ter `source_row_original`. A materialização continua a usar `source_row` e o fallback por releitura do Bronze quando ambos faltam.
- Para **recalcular** rastreio a partir do ficheiro Bronze: voltar a executar o mapeamento (`POST .../mapear`) no mesmo lote.
- API HTTP dos relatórios Gold: sem mudança de contrato; o backend continua a expor `source_row` nos objetos do relatório com a semântica de linha física corrigida.

## Diffs / revisão (por componente)

```bash
git diff main -- backend/app/services/imports/contracts.py backend/app/services/imports/file_reader.py backend/app/services/lead_mapping.py backend/app/services/lead_pipeline_service.py
git diff main -- backend/tests/test_import_file_reader.py backend/tests/test_lead_silver_mapping.py backend/tests/test_lead_batch_endpoints.py backend/tests/test_lead_gold_pipeline.py
git diff main -- frontend/src/pages/leads/PipelineStatusPage.tsx auditoria/handoff-task6.md
```

## Testes executados

```bash
cd backend
$env:PYTHONPATH="<repo>;<repo>/backend"; $env:TESTING="true"; $env:SECRET_KEY="ci-secret-key"
python -m pytest tests/test_import_file_reader.py tests/test_lead_silver_mapping.py::TestPostMapear -q
python -m pytest tests/test_lead_gold_pipeline.py::test_materializar_prefers_source_row_original_over_source_row tests/test_lead_gold_pipeline.py::TestLeadEventoInGoldPipeline::test_missing_birth_date_dq_reports_physical_line_after_blank_csv_row -q
python -m pytest tests/test_lead_batch_endpoints.py::TestGetBatchPreview::test_preview_uses_windowed_reader -q
```

## Referência

- Pedido: [auditoria/task6.md](task6.md)
- Contexto: [auditoria/deep-research-report.md](deep-research-report.md)
- Task 5: [auditoria/handoff-task5.md](handoff-task5.md)
