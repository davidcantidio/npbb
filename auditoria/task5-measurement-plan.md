# Task 5 — Plano de medição (performance import leads)

Este documento fixa **como medir** e **metas de regressão** para o fluxo de importação (Bronze/Silver/Gold, preview ETL, snapshots). Baseline numérico: preencher na coluna “Baseline” após correr `backend/scripts/benchmark_lead_import_task5.py` na raiz do repositório e, em Postgres, as queries abaixo.

## Métricas

| Métrica | Método | Baseline | Meta pós-otimização |
|--------|--------|----------|---------------------|
| Pico RSS (MB) | `psutil.Process().memory_info().rss` antes/depois do trecho crítico no script; ou `tracemalloc` em teste dedicado | _a preencher_ | Não piorar > **15%** vs baseline no mesmo fixture |
| Tempo contagem CSV (ms) | Script: uma passagem `csv.reader` sem materializar todas as linhas | _a preencher_ | Não piorar > **10%** (contagem deve ser linear e barata) |
| Tempo insert Gold simulado / real | `pytest` perfis ou pipeline completo com fixture N linhas | _a preencher_ | Melhorar ou não piorar > **10%** em tempo total insert |
| `pg_total_relation_size` | Ver secção SQL | _a preencher_ | Esta task não muda schema de tamanho até PRs de compressão/Bronze externo |

## SQL (Postgres)

Executar com o mesmo `evento_id` / sessão de teste antes e depois de import controlado:

```sql
SELECT pg_size_pretty(pg_total_relation_size('lead_batches')) AS lead_batches;
SELECT pg_size_pretty(pg_total_relation_size('lead_import_etl_preview_session')) AS etl_preview;
```

## Fixtures recomendadas

- **Pequeno (CI):** 500–2 000 linhas CSV sintético (script por defeito).
- **Médio:** 10 000–50 000 linhas, máquina dev.
- **Grande:** até 100 000 linhas se RAM e tempo o permitirem; não obrigatório em CI.

## Variáveis de ambiente relevantes (Task 5)

| Variável | Efeito |
|----------|--------|
| `NPBB_LEAD_GOLD_INSERT_LOOKUP_CHUNK_SIZE` | Janela de linhas para lookup Gold em memória (default 1500). |
| `LEAD_GOLD_INSERT_COMMIT_BATCH_SIZE` | Commits parciais durante insert Gold. |

## Limites operacionais (resumo)

Ver [task5-operator-limits.md](task5-operator-limits.md).
