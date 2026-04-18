# Handoff — Task 9 (validação de upload: conteúdo além da extensão)

## Resumo executivo

- **Objetivo:** rejeitar cedo ficheiros com extensão aceite (`.csv` / `.xlsx`) mas conteúdo incoerente, alinhado ao achado P3 do [auditoria/deep-research-report.md](deep-research-report.md) (*superfície de upload*).
- **Onde centralizado:** [`backend/app/services/imports/file_reader.py`](backend/app/services/imports/file_reader.py) — `inspect_upload` passa a ler um *probe* dos primeiros bytes (até 8192, igual a `CSV_STREAM_SNIFF_BYTES`) após validar extensão, tamanho e ficheiro vazio.
- **Regras:**
  - **`.xlsx`:** exige cabeçalho local ZIP `PK` + `\x03\x04`, `\x05\x06` ou `\x07\x08`; ficheiros com menos de 4 bytes ou sem assinatura ZIP são `INVALID_FILE_CONTENT`.
  - **`.csv`:** rejeita `\x00` no *probe* (binário); rejeita se o *probe* começar como ZIP (ex.: `.xlsx` renomeado para `.csv`).
- **Limites:** inalterados — `max_bytes` em `inspect_upload` (default `DEFAULT_IMPORT_MAX_BYTES`, 50 MB) e os limites por rota (`MAX_IMPORT_FILE_BYTES` em leads, `PUBLICIDADE_IMPORT_MAX_BYTES` em publicidade).
- **HTTP:** novo código de erro `INVALID_FILE_CONTENT` com mensagem em português, sem stack trace (via `raise_http_error` / `HTTPException` com `detail` estruturado, como os demais `ImportFileError`).

## Ficheiros alterados

| Caminho | Alteração |
|---------|-----------|
| [backend/app/services/imports/file_reader.py](backend/app/services/imports/file_reader.py) | `_probe_starts_with_zip_local_header`, `_validate_import_content_probe`, extensão de `inspect_upload` com leitura do *probe* e `seek(0)` final. |
| [backend/app/routers/leads.py](backend/app/routers/leads.py) | `validar_upload_import` e `criar_batch` passam a usar `inspect_upload` + mapeamento de `ImportFileError` para 400; removida duplicação de checagens de tamanho/vazio em `validar_upload_import`. |
| [backend/tests/test_import_file_reader.py](backend/tests/test_import_file_reader.py) | Testes: XLSX falso, CSV com NUL, CSV com bytes ZIP, regressão CSV UTF-8 e ZIP mínimo com assinatura válida. |
| [backend/tests/test_lead_batch_endpoints.py](backend/tests/test_lead_batch_endpoints.py) | Cenário `INVALID_XLSX_CONTENT`: upload Bronze rejeitado no `POST` com `INVALID_FILE_CONTENT` (antes aceitava e falhava no preview). |

**Sem alteração** em [`extract.py`](backend/app/modules/leads_publicidade/application/etl_import/extract.py): `read_upload_bytes` já depende de `inspect_upload`.

## Diffs / revisão

```bash
git diff -- backend/app/services/imports/file_reader.py backend/app/routers/leads.py
git diff -- backend/tests/test_import_file_reader.py backend/tests/test_lead_batch_endpoints.py
```

Estatística aproximada da sessão: ~120 linhas tocadas nos quatro ficheiros acima (inserções + remoções).

## Compatibilidade com clientes (ficheiros limítrofes)

- **CSV UTF-8 (com ou sem BOM)** e **Latin-1** legíveis como texto, sem NUL e sem começar como ZIP: **continuam aceites**.
- **XLSX reais** (Office Open XML = ZIP com `PK\x03\x04`): **aceites** desde que a extensão seja `.xlsx`.
- **Rejeitados mais cedo do que antes:** conteúdo textual com nome `.xlsx` (sem ZIP); ZIP/Excel renomeado para `.csv`; CSV com bytes nulos no início.
- **`POST /leads/import/upload` e `POST /leads/batches`:** mensagens de `FILE_TOO_LARGE` / `EMPTY_FILE` / `INVALID_FILE_TYPE` passam a ser as de `inspect_upload` (textos ligeiramente diferentes dos antigos hardcoded em leads para tamanho/vazio — mesmo `code` e semântica).

## Verificação

- Com `PYTHONPATH` incluindo a raiz do repositório (módulo `lead_pipeline`):  
  `pytest tests/test_import_file_reader.py tests/test_lead_batch_endpoints.py` — verde.
- Teste spot ETL: `test_preview_etl_reports_invalid_email_and_cpf_validation_errors` — verde.

## Referências

- Pedido: [auditoria/task9.md](task9.md)
- Contexto de merge (task 8, fora de escopo aqui): [auditoria/handoff-task8.md](handoff-task8.md)
