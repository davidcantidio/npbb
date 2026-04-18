# Handoff — Task 3 (Dedupe e idempotência no Postgres)

## Resumo

- Substituído o unique em colunas `uq_lead_ticketing_dedupe(email, cpf, evento_nome, sessao)` por um **índice único parcial** `uq_lead_ticketing_dedupe_norm` sobre expressões  
  `(COALESCE(TRIM(email), ''), cpf, COALESCE(TRIM(evento_nome), ''), COALESCE(TRIM(sessao), ''))` com predicado **`WHERE NULLIF(TRIM(cpf), '') IS NOT NULL`**, alinhado à regra de **CPF obrigatório** no ETL (`validate_normalized_lead_payload`).
- **Semântica**: `NULL` e string vazia nos campos opcionais da chave tratam-se como string vazia para unicidade; linhas **sem CPF** (inclui `NULL`, `''` e whitespace-only) não entram no índice. Duplicatas só com email continuam possíveis no nível DB para legados sem CPF.
- **Aplicação**: `find_lead_by_ticketing_dedupe_key()` + `is_ticketing_dedupe_integrity_error()` em [`persistence.py`](backend/app/modules/leads_publicidade/application/etl_import/persistence.py); no insert em lote linha-a-linha, **savepoint interno** + em caso de `IntegrityError` de dedupe → merge no registo existente e contagem como **updated**.
- **Correção pós-review**: `is_ticketing_dedupe_integrity_error()` foi estreitado para aceitar apenas conflito do índice novo, do nome legado e da assinatura exata da unique antiga em SQLite. Conflitos não relacionados, como `lead.id_salesforce`, já não entram no fluxo de recovery de dedupe.
- **Gold**: [`lead_pipeline_service.py`](backend/app/services/lead_pipeline_service.py) — cada insert novo corre dentro de `begin_nested()`; em conflito de dedupe, refetch + merge (sem `rollback()` da transação inteira).
- **Testes**: marcador `postgres` + `NPBB_POSTGRES_TEST_URL`; dois threads com `persist_lead_batch` e payload com `sessao`/`email` nulos → um único `lead` + query de verificação de duplicados no teste. Review adicional cobriu CPF vazio fora do índice e falso positivo de `id_salesforce` no detector de `IntegrityError`.
- **Risco de negócio**: se `evento_nome` estiver vazio em dois contextos distintos para o mesmo CPF, a chave normalizada colapsa — nos fluxos ETL/Gold com evento explícito o risco é baixo.

## Ficheiros tocados

| Caminho | Alteração |
|---------|-----------|
| [`backend/alembic/versions/a1c9e8f7d6b5_lead_ticketing_dedupe_functional_unique.py`](backend/alembic/versions/a1c9e8f7d6b5_lead_ticketing_dedupe_functional_unique.py) | **Nova migração** (head anterior: `fb2c3d4e5f6a`): drop `uq_lead_ticketing_dedupe`, `CREATE UNIQUE INDEX` funcional + parcial (PG e SQLite). |
| [`backend/app/models/lead_public_models.py`](backend/app/models/lead_public_models.py) | `Lead.__table_args__` via `@declared_attr` com `Index` único em expressões + `sqlite_where` / `postgresql_where`. |
| [`backend/app/modules/leads_publicidade/application/etl_import/persistence.py`](backend/app/modules/leads_publicidade/application/etl_import/persistence.py) | Helpers de dedupe + recuperação `IntegrityError` no insert linha-a-linha. |
| [`backend/app/services/lead_pipeline_service.py`](backend/app/services/lead_pipeline_service.py) | `begin_nested` + conflito de dedupe no insert Gold. |
| [`backend/tests/test_lead_constraints.py`](backend/tests/test_lead_constraints.py) | Regressão: duplicatas com `cpf=''` não devem ser bloqueadas pelo índice parcial. |
| [`backend/tests/test_etl_import_persistence.py`](backend/tests/test_etl_import_persistence.py) | Regressões: `find_lead_by_ticketing_dedupe_key()` com CPF whitespace-only e `is_ticketing_dedupe_integrity_error()` não deve confundir `lead.id_salesforce`. |
| [`backend/tests/test_lead_ticketing_dedupe_postgres.py`](backend/tests/test_lead_ticketing_dedupe_postgres.py) | Teste de concorrência (novo). |
| [`backend/tests/test_lead_gold_insert_batching.py`](backend/tests/test_lead_gold_insert_batching.py) | `_FakeSession.exec` / `begin_nested`; expectativas de heartbeat alinhadas ao novo custo de `perf_counter` por linha. |
| [`backend/pyproject.toml`](backend/pyproject.toml) | Registo do marcador `postgres` em `[tool.pytest.ini_options]`. |
| [`auditoria/handoff-task3.md`](auditoria/handoff-task3.md) | Este ficheiro. |

## Diffs / revisão

```bash
git diff main -- backend/alembic/versions/a1c9e8f7d6b5_lead_ticketing_dedupe_functional_unique.py \
  backend/app/models/lead_public_models.py \
  backend/app/modules/leads_publicidade/application/etl_import/persistence.py \
  backend/app/services/lead_pipeline_service.py \
  backend/tests/test_lead_constraints.py \
  backend/tests/test_etl_import_persistence.py \
  backend/tests/test_lead_ticketing_dedupe_postgres.py \
  backend/tests/test_lead_gold_insert_batching.py \
  backend/pyproject.toml
```

### Backward compatibility

- **Deploy**: antes de `alembic upgrade`, executar agregação por chave normalizada e **fundir ou apagar** duplicados que violem o novo índice; caso contrário a migração falha ao criar o unique index.
- **Locks**: `CREATE UNIQUE INDEX` sem `CONCURRENTLY` bloqueia escritas na tabela `lead` durante a criação. Em tabelas grandes, preferir janela de manutenção ou SQL manual `CREATE UNIQUE INDEX CONCURRENTLY` + migração em duas fases (fora do scope deste ficheiro Alembic padrão).
- **Linhas sem CPF**: deixam de ser cobertas por este unique parcial; o predicado correto é `NULLIF(TRIM(cpf), '') IS NOT NULL`, não apenas `cpf IS NOT NULL`.
- **Recovery de conflito**: o helper de dedupe já não deve ser reutilizado para outras uniques da tabela `lead`; se aparecer novo unique relevante, atualizar explicitamente `is_ticketing_dedupe_integrity_error()`.

### Query de verificação pós-deploy

```sql
SELECT cpf,
       COALESCE(TRIM(email), '') AS email_n,
       COALESCE(TRIM(evento_nome), '') AS evento_n,
       COALESCE(TRIM(sessao), '') AS sessao_n,
       COUNT(*) AS n
FROM lead
WHERE NULLIF(TRIM(cpf), '') IS NOT NULL
GROUP BY 1, 2, 3, 4
HAVING COUNT(*) > 1;
```

Deve devolver **0 linhas**.

### Testes locais

```bash
cd backend
$env:PYTHONPATH="<repo>;<repo>/backend"; $env:TESTING="true"; $env:SECRET_KEY="ci-secret-key"
python -m pytest tests/test_lead_constraints.py tests/test_etl_import_persistence.py tests/test_leads_import_etl_endpoint.py -q
```

Com Postgres de teste (base descartável):

```bash
$env:NPBB_POSTGRES_TEST_URL="postgresql+psycopg2://..."
python -m pytest tests/test_lead_ticketing_dedupe_postgres.py -q
```

### Estado da validacao nesta review

- `tests/test_lead_constraints.py`: **passou**.
- `tests/test_etl_import_persistence.py`: **passou**.
- `tests/test_leads_import_etl_endpoint.py`: **passou**.
- `tests/test_lead_ticketing_dedupe_postgres.py`: **nao executado nesta maquina** porque `NPBB_POSTGRES_TEST_URL` nao estava definido.
- `tests/test_lead_gold_insert_batching.py`: continua com limitacao de ambiente ligada a `tmp_path` / `basetemp`; nao houve evidencia nova de regressao funcional do fluxo Gold nesta review.

## Referência

- Pedido: [`auditoria/task3.md`](task3.md)
- Contexto: [`auditoria/deep-research-report.md`](deep-research-report.md) (dedupe / corrida)
- Continuidade Task 2: [`auditoria/handoff-task2.md`](handoff-task2.md) (retentativas de commit aumentam pressão sobre dedupe atómica)
