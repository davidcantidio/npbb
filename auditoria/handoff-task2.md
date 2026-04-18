# Handoff — Task 2 (Commit ETL: falha parcial)

## Resumo

- Quando `persist_lead_batch()` devolve `has_errors=True` (há `failed_rows`), o commit deixa de gravar `status="committed"` e passa a usar **`partial_failure`**, com **`persistence_failures`** (tuplas `row_number`, `reason`) no resultado interno e no JSON persistido.
- **`get_commit_result()`** só devolve cache idempotente se o JSON armazenado tiver **`status == "committed"`**. Em `partial_failure`, devolve `None`, pelo que **`commit_preview_session`** volta a executar a persistência num novo `POST /leads/import/etl/commit` com o mesmo `session_token`.
- **`mark_committed()`** continua a ser o ponto único de gravação de `entity.status`, `committed_at` e `commit_result_json` (agora inclui a lista `persistence_failures`).
- API: **`ImportEtlResult`** aceita `status` `partial_failure` e expõe **`persistence_failures`** (modelo `ImportEtlPersistenceFailure`) com descrição no `Field` para OpenAPI. Respostas HTTP mantêm **200**; o cliente distingue sucesso fechado por `status == "committed"`.
- **Replay**: reexecuta o lote completo aprovado no preview (mesmo `approved_rows`); linhas já persistidas seguem a lógica existente de merge/update na persistência.

## Decisões de semântica

| `PreviewStatus` / `ImportEtlResult.status` | Significado |
|--------------------------------------------|-------------|
| `committed`                                | Persistência sem erros reportados (`has_errors` falso); cache idempotente ativo. |
| `partial_failure`                          | Pelo menos uma linha em `failed_rows`; commit **não** considerado fechado; retentar o mesmo endpoint com o mesmo token. |

- **`skipped > 0` sem `has_errors`** não força `partial_failure` (alinhado ao plano: `skipped_rows` não populado na prática).

## Ficheiros tocados

| Caminho | Alteração |
|---------|-----------|
| `backend/app/modules/leads_publicidade/application/etl_import/contracts.py` | `PreviewStatus` + `EtlCommitResult.persistence_failures`. |
| `backend/app/modules/leads_publicidade/application/etl_import/commit_service.py` | Uso de `LeadBatchPersistenceResult` completo; `partial_failure` vs `committed`. |
| `backend/app/modules/leads_publicidade/application/etl_import/preview_session_repository.py` | Serialização de falhas; `get_commit_result` só para `committed`. |
| `backend/app/schemas/lead_import_etl.py` | `ImportEtlPersistenceFailure`; `ImportEtlResult` estendido. |
| `backend/app/routers/leads.py` | `_serialize_etl_commit_response` inclui `persistence_failures`. |
| `backend/tests/test_leads_import_etl_endpoint.py` | `test_commit_etl_partial_failure_allows_retry_then_idempotent_committed`. |
| `auditoria/handoff-task2.md` | Este ficheiro. |

**Sem** migração Alembic: `LeadImportEtlPreviewSession.status` já é `str` (32 caracteres).

## Revisão / diffs

Comandos úteis (ajustar ramo base se necessário):

```bash
git diff main -- backend/app/modules/leads_publicidade/application/etl_import/ backend/app/schemas/lead_import_etl.py backend/app/routers/leads.py backend/tests/test_leads_import_etl_endpoint.py
```

Testes executados localmente:

```bash
cd backend
$env:PYTHONPATH="<repo>;<repo>/backend"; $env:TESTING="true"; $env:SECRET_KEY="ci-secret-key"
python -m pytest tests/test_leads_import_etl_endpoint.py tests/test_leads_import_etl_usecases.py -q
```

Resultado: **22 passed** (inclui o novo teste de parcial + retry + idempotência).

## Referência

- Pedido original: `auditoria/task2.md`
- Contexto do achado: `auditoria/deep-research-report.md` (secção Commit ETL / falha parcial)
