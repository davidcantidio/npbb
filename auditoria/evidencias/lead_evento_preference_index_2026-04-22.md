# lead_evento preference lookup index

Data: 2026-04-22.
Fonte: Supabase MCP + codigo do backend.

Classificacao: implementado e validado em banco real.

## Objetivo

Remover o `Incremental Sort` da subquery que resolve o evento preferido por lead em
`backend/app/routers/leads_routes/lead_records.py`, usando a mesma prioridade definida
pela aplicacao:

- `evento_nome_backfill` -> 1
- `lead_batch` -> 2
- `event_id_direct` -> 3
- `ativacao` -> 4
- `manual_reconciled` -> 5

Observacao importante:

- O plano inicial da auditoria tinha nomes antigos de enum (`event_name_backfill`,
  `event_direct`). O schema real usa `evento_nome_backfill` e `event_id_direct`.
- O indice tambem nao pode usar `source_kind::text` porque isso quebra a exigencia de
  imutabilidade da expressao do indice em Postgres.

## SQL aplicado

```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_lead_evento_lead_preference_lookup
ON public.lead_evento (
  lead_id,
  (
    CASE source_kind
      WHEN 'evento_nome_backfill'::public.leadeventosourcekind THEN 1
      WHEN 'lead_batch'::public.leadeventosourcekind THEN 2
      WHEN 'event_id_direct'::public.leadeventosourcekind THEN 3
      WHEN 'ativacao'::public.leadeventosourcekind THEN 4
      WHEN 'manual_reconciled'::public.leadeventosourcekind THEN 5
      ELSE 0
    END
  ) DESC,
  updated_at DESC,
  created_at DESC,
  id DESC
)
INCLUDE (evento_id);

ANALYZE public.lead_evento;
```

## EXPLAIN antes

Query validada:

```sql
WITH ranked AS (
  SELECT
    lead_id,
    evento_id,
    row_number() OVER (
      PARTITION BY lead_id
      ORDER BY
        (
          CASE source_kind
            WHEN 'evento_nome_backfill'::public.leadeventosourcekind THEN 1
            WHEN 'lead_batch'::public.leadeventosourcekind THEN 2
            WHEN 'event_id_direct'::public.leadeventosourcekind THEN 3
            WHEN 'ativacao'::public.leadeventosourcekind THEN 4
            WHEN 'manual_reconciled'::public.leadeventosourcekind THEN 5
            ELSE 0
          END
        ) DESC,
        updated_at DESC,
        created_at DESC,
        id DESC
    ) AS row_num
  FROM public.lead_evento
)
SELECT lead_id, evento_id
FROM ranked
WHERE row_num = 1;
```

Resumo do plano:

```text
Subquery Scan on ranked
  -> WindowAgg
       Run Condition: (row_number() OVER (?) <= 1)
       -> Incremental Sort
            Sort Key: lead_evento.lead_id, CASE ..., updated_at DESC, created_at DESC, id DESC
            Presorted Key: lead_evento.lead_id
            -> Index Scan using ix_lead_evento_lead_evento_lead_id on lead_evento
Planning Time: 22.039 ms
Execution Time: 498.372 ms
Buffers: shared hit=8150
```

## EXPLAIN depois

Resumo do plano:

```text
Subquery Scan on ranked
  -> WindowAgg
       Run Condition: (row_number() OVER (?) <= 1)
       -> Index Scan using idx_lead_evento_lead_preference_lookup on lead_evento
Planning Time: 1.508 ms
Execution Time: 49.703 ms
Buffers: shared hit=7100
```

## Resultado observado

- `Incremental Sort` removido do plano.
- `Execution Time` caiu de `498.372 ms` para `49.703 ms`.
- Ganho aproximado de `10x` na subquery quente.
- `pg_stat_user_indexes` confirmou uso imediato do novo indice:

```text
indexrelname: idx_lead_evento_lead_preference_lookup
idx_scan: 1
idx_tup_read: 43152
idx_tup_fetch: 43152
```

## Limitacoes

- Esta validacao cobre diretamente a subquery critica que compoe `listar_leads_impl`.
- A query completa da listagem continua com complexidade estrutural por causa do calculo
  de data/evento efetivos via `CASE` entre `lead_conversao`, `lead_evento` e
  `lead_batches`.
- Se a meta for reduzir ainda mais a latencia da listagem completa, o proximo passo nao
  e mais um indice simples: sera refatorar a query ou materializar o evento canonico e a
  data efetiva do lead.
