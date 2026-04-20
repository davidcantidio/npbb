# EXPLAIN atual de queries criticas

Data: 2026-04-20.
Fonte: MCP Supabase read-only.

Classificacao: validado por EXPLAIN/metrica; observado em execucao real.

Este arquivo registra planos atuais. Ele nao prova ganho antes/depois.

## Query 1: `lead_batches` por id

Resumo da query: leitura de lote por `id`, incluindo colunas de payload e ponteiro.

Plano observado:

```text
Index Scan using pk_lead_batches on lead_batches
  Index Cond: (id = $1)
  Buffers: shared hit=5
Planning Time: 0.590 ms
Execution Time: 1.094 ms
```

Leitura objetiva:

- O acesso por `id` usa `pk_lead_batches`.
- O plano pontual e barato para o id amostrado.
- A metrica agregada de `pg_stat_statements` ainda mostra alto custo acumulado em leituras que incluem `arquivo_bronze`.

## Query 2: `leads_silver` por batch com ordenacao por `row_index`

Resumo da query: leitura das primeiras 200 linhas de `leads_silver` de um lote grande, ordenada por `row_index`.

Plano observado:

```text
Limit
  -> Index Scan using uq_leads_silver_batch_row on leads_silver
       Index Cond: (batch_id = $1)
Planning Time: 0.828 ms
Execution Time: 845.812 ms
```

Detalhe relevante do plano:

- A etapa final de leitura por batch usa `uq_leads_silver_batch_row`.
- O custo total capturado inclui a subquery de amostragem que localizou o maior batch por `GROUP BY batch_id`.
- `pg_stat_statements` indicou temp blocks para a familia de query `leads_silver ... ORDER BY row_index`.

Leitura objetiva:

- Existe indice util para `batch_id, row_index`.
- A evidencia atual nao demonstra remocao de sort residual nem ganho medido.
- A proxima medicao deve separar a query real do dashboard/importacao da subquery usada para escolher amostra.
