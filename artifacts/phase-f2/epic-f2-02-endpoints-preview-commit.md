# EPIC-F2-02 - Endpoints Preview Commit

Data de validacao: 2026-03-03

## Endpoints publicados no router `leads`

- `POST /leads/import/etl/preview`
- `POST /leads/import/etl/commit`

Arquivo principal:
- `backend/app/routers/leads.py`

## Contratos HTTP aplicados

Schemas canonicos do endpoint ETL:
- `backend/app/schemas/lead_import_etl.py`
  - `ImportEtlPreviewResponse`
  - `ImportEtlCommitRequest`
  - `ImportEtlResult`
  - `DQCheckResult`

### Preview (`/leads/import/etl/preview`)

Entrada:
- `multipart/form-data` com `file`, `evento_id`, `strict`

Saida:
- `session_token`
- `total_rows`
- `valid_rows`
- `invalid_rows`
- `dq_report`

### Commit (`/leads/import/etl/commit`)

Entrada:
- JSON com `session_token`, `evento_id`, `force_warnings`

Semantica aplicada:
- commit bloqueado quando existem erros de validacao no preview
- commit bloqueado quando existem warnings e `force_warnings=false`
- commit permitido quando existem warnings e `force_warnings=true` (sem erros)
- commit idempotente ao reutilizar `session_token` ja consumido

## Erros padronizados no formato do backend

Mapeamento de erros ETL para `detail.code`:
- `ETL_INVALID_INPUT` (`400`) para payload/arquivo invalido
- `ETL_COMMIT_BLOCKED` (`409`) para gate de validacao/warnings
- `ETL_SESSION_CONFLICT` (`409`) para conflito de sessao de preview
- `ETL_SESSION_NOT_FOUND` (`404`) para `session_token` inexistente/expirado

## Evidencias de resposta HTTP

Cobertura dedicada:
- `backend/tests/test_leads_import_etl_endpoint.py`

Cenarios cobertos:
- preview ETL retorna `session_token`, contagens e `dq_report`
- preview ETL com extensao invalida retorna `ETL_INVALID_INPUT`
- commit ETL bloqueia warnings sem confirmacao explicita (`force_warnings=false`)
- commit ETL permite persistencia com override explicito (`force_warnings=true`)
- commit ETL reutiliza resultado previamente comitado (idempotencia)
- commit ETL com token inexistente retorna `ETL_SESSION_NOT_FOUND`
- commit ETL bloqueia erros de validacao mesmo com `force_warnings=true`

## Compatibilidade com fluxo legado

Testes de regressao legados executados sem mudanca de contrato:
- `backend/tests/test_lead_import_preview_xlsx.py`
- `backend/tests/test_leads_import_csv_smoke.py`

Resultado:
- sem regressao em `/leads/import/preview`
- sem regressao em `/leads/import/validate`
- sem regressao em `/leads/import`

## Comandos e resultados

Comando executado:

```bash
PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend \
pytest backend/tests/test_leads_import_etl_endpoint.py \
       backend/tests/test_lead_import_preview_xlsx.py \
       backend/tests/test_leads_import_csv_smoke.py -q
```

Resultado:
- `10 passed in 5.71s`
