# EXPLAIN do dashboard etario
# label: phase1
# gerado em 2026-04-23T20:14:17.334955+00:00

## no_filters

Descricao: Sem filtros
Parametros: {'data_inicio': None, 'data_fim': None, 'evento_id': None}
### _load_lead_event_facts

Flags: seq_scan, temp_blocks

```sql
SELECT DISTINCT evento.id, evento.nome, evento.cidade, evento.estado, lead.id AS id_1, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome AS nome_1, lead.sobrenome, lead_evento.source_kind, lead_evento.tipo_lead 
FROM lead_evento JOIN lead ON lead.id = lead_evento.lead_id JOIN evento ON evento.id = lead_evento.evento_id
```

```text
HashAggregate  (cost=10357.33..10650.78 rows=29345 width=81) (actual time=132.519..162.794 rows=52313 loops=1)
  Group Key: evento.id, evento.nome, evento.cidade, evento.estado, lead.id, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome, lead.sobrenome, lead_evento.source_kind, lead_evento.tipo_lead
  Batches: 5  Memory Usage: 5049kB  Disk Usage: 3680kB
  Buffers: shared hit=2908, temp read=471 written=890
  ->  Gather  (cost=6249.03..9476.98 rows=29345 width=81) (actual time=73.493..92.882 rows=52313 loops=1)
        Workers Planned: 1
        Workers Launched: 1
        Buffers: shared hit=2908, temp read=71 written=138
        ->  HashAggregate  (cost=5249.03..5542.48 rows=29345 width=81) (actual time=69.574..81.181 rows=26156 loops=2)
              Group Key: evento.id, evento.nome, evento.cidade, evento.estado, lead.id, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome, lead.sobrenome, lead_evento.source_kind, lead_evento.tipo_lead
              Batches: 5  Memory Usage: 4409kB  Disk Usage: 712kB
              Buffers: shared hit=2908, temp read=71 written=138
              Worker 0:  Batches: 1  Memory Usage: 4249kB
              ->  Hash Join  (cost=1770.55..4368.68 rows=29345 width=81) (actual time=19.532..50.295 rows=26156 loops=2)
                    Hash Cond: (lead_evento.evento_id = evento.id)
                    Buffers: shared hit=2908
                    ->  Hash Join  (cost=1765.46..4283.04 rows=29345 width=52) (actual time=19.434..43.372 rows=26156 loops=2)
                          Hash Cond: (lead.id = lead_evento.lead_id)
                          Buffers: shared hit=2902
                          ->  Parallel Seq Scan on lead  (cost=0.00..2058.28 rows=44228 width=40) (actual time=0.008..4.680 rows=37891 loops=2)
                                Buffers: shared hit=1616
                          ->  Hash  (cost=1141.87..1141.87 rows=49887 width=16) (actual time=19.248..19.250 rows=52313 loops=2)
                                Buckets: 65536  Batches: 1  Memory Usage: 2965kB
                                Buffers: shared hit=1286
                                ->  Seq Scan on lead_evento  (cost=0.00..1141.87 rows=49887 width=16) (actual time=0.024..8.303 rows=52313 loops=2)
                                      Buffers: shared hit=1286
                    ->  Hash  (cost=3.93..3.93 rows=93 width=33) (actual time=0.084..0.085 rows=93 loops=2)
                          Buckets: 1024  Batches: 1  Memory Usage: 15kB
                          Buffers: shared hit=6
                          ->  Seq Scan on evento  (cost=0.00..3.93 rows=93 width=33) (actual time=0.023..0.057 rows=93 loops=2)
                                Buffers: shared hit=6
Planning:
  Buffers: shared hit=245
Planning Time: 1.067 ms
Execution Time: 167.670 ms
```

### _load_lead_event_facts_via_batch

Flags: temp_blocks

```sql
SELECT DISTINCT evento.id, evento.nome, evento.cidade, evento.estado, lead.id AS id_1, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome AS nome_1, lead.sobrenome, lead_batches.origem_lote, lead_batches.tipo_lead_proponente 
FROM lead JOIN lead_batches ON lead.batch_id = lead_batches.id JOIN evento ON evento.id = lead_batches.evento_id 
WHERE lead.batch_id IS NOT NULL AND lead_batches.evento_id IS NOT NULL AND lead_batches.stage = 'GOLD' AND lead_batches.pipeline_status IN ('PASS', 'PASS_WITH_WARNINGS')
```

```text
HashAggregate  (cost=470.97..477.13 rows=616 width=98) (actual time=59.519..81.913 rows=39554 loops=1)
  Group Key: evento.id, evento.nome, evento.cidade, evento.estado, lead.id, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome, lead.sobrenome, lead_batches.origem_lote, lead_batches.tipo_lead_proponente
  Batches: 5  Memory Usage: 4409kB  Disk Usage: 3416kB
  Buffers: shared hit=1315, temp read=273 written=623
  ->  Merge Join  (cost=0.65..452.49 rows=616 width=98) (actual time=0.036..28.415 rows=39554 loops=1)
        Merge Cond: (lead_batches.evento_id = evento.id)
        Buffers: shared hit=1315
        ->  Nested Loop  (cost=0.43..823.40 rows=616 width=69) (actual time=0.026..21.143 rows=39554 loops=1)
              Buffers: shared hit=1304
              ->  Index Only Scan using idx_lead_batches_dashboard_gold_evento_status on lead_batches  (cost=0.14..3.64 rows=2 width=33) (actual time=0.011..0.044 rows=20 loops=1)
                    Index Cond: ((evento_id IS NOT NULL) AND (pipeline_status = ANY ('{PASS,PASS_WITH_WARNINGS}'::pipelinestatus[])))
                    Heap Fetches: 10
                    Buffers: shared hit=10
              ->  Index Scan using ix_lead_lead_batch_id on lead  (cost=0.29..380.08 rows=2980 width=44) (actual time=0.008..0.478 rows=1978 loops=20)
                    Index Cond: ((batch_id = lead_batches.id) AND (batch_id IS NOT NULL))
                    Buffers: shared hit=1294
        ->  Index Scan using evento_pkey on evento  (cost=0.14..6.84 rows=93 width=33) (actual time=0.005..0.056 rows=93 loops=1)
              Buffers: shared hit=11
Planning:
  Buffers: shared hit=234
Planning Time: 1.017 ms
Execution Time: 84.712 ms
```

### _load_visible_events_by_normalized_name

Flags: seq_scan

```sql
SELECT evento.id, evento.nome, evento.cidade, evento.estado 
FROM evento
```

```text
Seq Scan on evento  (cost=0.00..3.93 rows=93 width=33) (actual time=0.015..0.036 rows=93 loops=1)
  Buffers: shared hit=3
Planning Time: 0.064 ms
Execution Time: 0.060 ms
```

### _load_lead_event_facts_via_evento_nome

Flags: seq_scan

```sql
SELECT lead.id, lead.evento_nome, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome, lead.sobrenome 
FROM lead 
WHERE lead.evento_nome IS NOT NULL AND trim(lead.evento_nome) != ''
```

```text
Seq Scan on lead  (cost=0.00..2743.82 rows=74812 width=61) (actual time=0.016..36.406 rows=75782 loops=1)
  Filter: ((evento_nome IS NOT NULL) AND (TRIM(BOTH FROM evento_nome) <> ''::text))
  Buffers: shared hit=1616
Planning:
  Buffers: shared hit=3
Planning Time: 0.106 ms
Execution Time: 40.240 ms
```

## reference_event

Descricao: Evento de maior volume recente ou total
Parametros: {'data_inicio': None, 'data_fim': None, 'evento_id': 107}
### _load_lead_event_facts

Flags: seq_scan

```sql
SELECT DISTINCT evento.id, evento.nome, evento.cidade, evento.estado, lead.id AS id_1, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome AS nome_1, lead.sobrenome, lead_evento.source_kind, lead_evento.tipo_lead 
FROM lead_evento JOIN lead ON lead.id = lead_evento.lead_id JOIN evento ON evento.id = lead_evento.evento_id 
WHERE evento.id = 107
```

```text
HashAggregate  (cost=3728.42..3810.00 rows=8158 width=81) (actual time=35.776..39.393 rows=10461 loops=1)
  Group Key: evento.nome, evento.cidade, evento.estado, lead.id, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome, lead.sobrenome, lead_evento.source_kind, lead_evento.tipo_lead
  Batches: 1  Memory Usage: 1817kB
  Buffers: shared hit=3978
  ->  Nested Loop  (cost=850.14..3504.08 rows=8158 width=81) (actual time=5.673..28.962 rows=10461 loops=1)
        Buffers: shared hit=3978
        ->  Index Scan using ix_evento_nome on evento  (cost=0.14..7.24 rows=1 width=33) (actual time=0.041..0.053 rows=1 loops=1)
              Filter: (id = 107)
              Rows Removed by Filter: 92
              Buffers: shared hit=33
        ->  Hash Join  (cost=850.00..3415.26 rows=8158 width=52) (actual time=5.629..27.461 rows=10461 loops=1)
              Hash Cond: (lead.id = lead_evento.lead_id)
              Buffers: shared hit=3945
              ->  Seq Scan on lead  (cost=0.00..2367.88 rows=75188 width=40) (actual time=0.010..7.387 rows=75782 loops=1)
                    Buffers: shared hit=1616
              ->  Hash  (cost=748.03..748.03 rows=8158 width=16) (actual time=5.610..5.612 rows=10461 loops=1)
                    Buckets: 16384 (originally 8192)  Batches: 1 (originally 1)  Memory Usage: 619kB
                    Buffers: shared hit=2329
                    ->  Index Scan using idx_lead_evento_evento_id_lead_id on lead_evento  (cost=0.29..748.03 rows=8158 width=16) (actual time=0.024..3.519 rows=10461 loops=1)
                          Index Cond: (evento_id = 107)
                          Buffers: shared hit=2329
Planning:
  Buffers: shared hit=11
Planning Time: 0.464 ms
Execution Time: 40.041 ms
```

### _load_lead_event_facts_via_batch

Flags: nenhuma

```sql
SELECT DISTINCT evento.id, evento.nome, evento.cidade, evento.estado, lead.id AS id_1, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome AS nome_1, lead.sobrenome, lead_batches.origem_lote, lead_batches.tipo_lead_proponente 
FROM lead JOIN lead_batches ON lead.batch_id = lead_batches.id JOIN evento ON evento.id = lead_batches.evento_id 
WHERE evento.id = 107 AND lead.batch_id IS NOT NULL AND lead_batches.evento_id IS NOT NULL AND lead_batches.stage = 'GOLD' AND lead_batches.pipeline_status IN ('PASS', 'PASS_WITH_WARNINGS')
```

```text
HashAggregate  (cost=671.62..674.70 rows=308 width=98) (actual time=9.510..12.213 rows=8273 loops=1)
  Group Key: evento.nome, evento.cidade, evento.estado, lead.id, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome, lead.sobrenome, lead_batches.origem_lote, lead_batches.tipo_lead_proponente
  Batches: 1  Memory Usage: 1561kB
  Buffers: shared hit=483
  ->  Nested Loop  (cost=0.57..663.15 rows=308 width=98) (actual time=0.063..4.134 rows=8273 loops=1)
        Buffers: shared hit=483
        ->  Nested Loop  (cost=0.28..9.61 rows=1 width=62) (actual time=0.049..0.060 rows=1 loops=1)
              Buffers: shared hit=36
              ->  Index Scan using ix_evento_nome on evento  (cost=0.14..7.24 rows=1 width=33) (actual time=0.038..0.047 rows=1 loops=1)
                    Filter: (id = 107)
                    Rows Removed by Filter: 92
                    Buffers: shared hit=33
              ->  Index Only Scan using idx_lead_batches_dashboard_gold_evento_status on lead_batches  (cost=0.14..2.36 rows=1 width=33) (actual time=0.009..0.011 rows=1 loops=1)
                    Index Cond: ((evento_id IS NOT NULL) AND (evento_id = 107) AND (pipeline_status = ANY ('{PASS,PASS_WITH_WARNINGS}'::pipelinestatus[])))
                    Heap Fetches: 1
                    Buffers: shared hit=3
        ->  Index Scan using ix_lead_lead_batch_id on lead  (cost=0.29..623.74 rows=2980 width=44) (actual time=0.013..1.817 rows=8273 loops=1)
              Index Cond: ((batch_id = lead_batches.id) AND (batch_id IS NOT NULL))
              Buffers: shared hit=447
Planning:
  Buffers: shared hit=3
Planning Time: 0.407 ms
Execution Time: 12.697 ms
```

## rolling_30d

Descricao: Janela movel de 30 dias ancorada na maior lead.data_criacao
Parametros: {'data_inicio': datetime.date(2026, 3, 24), 'data_fim': datetime.date(2026, 4, 22), 'evento_id': None}
### _load_lead_event_facts

Flags: seq_scan, temp_blocks

```sql
SELECT DISTINCT evento.id, evento.nome, evento.cidade, evento.estado, lead.id AS id_1, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome AS nome_1, lead.sobrenome, lead_evento.source_kind, lead_evento.tipo_lead 
FROM lead_evento JOIN lead ON lead.id = lead_evento.lead_id JOIN evento ON evento.id = lead_evento.evento_id 
WHERE lead.data_criacao >= '2026-03-24 00:00:00+00:00' AND lead.data_criacao < '2026-04-23 00:00:00+00:00'
```

```text
HashAggregate  (cost=10441.51..10727.69 rows=28618 width=81) (actual time=157.475..187.889 rows=52313 loops=1)
  Group Key: evento.id, evento.nome, evento.cidade, evento.estado, lead.id, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome, lead.sobrenome, lead_evento.source_kind, lead_evento.tipo_lead
  Batches: 5  Memory Usage: 5049kB  Disk Usage: 3680kB
  Buffers: shared hit=2908, temp read=498 written=894
  ->  Gather  (cost=6434.99..9582.97 rows=28618 width=81) (actual time=102.663..117.424 rows=52313 loops=1)
        Workers Planned: 1
        Workers Launched: 1
        Buffers: shared hit=2908, temp read=99 written=198
        ->  HashAggregate  (cost=5434.99..5721.17 rows=28618 width=81) (actual time=84.721..97.188 rows=26156 loops=2)
              Group Key: evento.id, evento.nome, evento.cidade, evento.estado, lead.id, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome, lead.sobrenome, lead_evento.source_kind, lead_evento.tipo_lead
              Batches: 1  Memory Usage: 3993kB
              Buffers: shared hit=2908, temp read=99 written=198
              Worker 0:  Batches: 5  Memory Usage: 4409kB  Disk Usage: 1032kB
              ->  Hash Join  (cost=1770.55..4576.45 rows=28618 width=81) (actual time=32.271..64.943 rows=26156 loops=2)
                    Hash Cond: (lead_evento.evento_id = evento.id)
                    Buffers: shared hit=2908
                    ->  Hash Join  (cost=1765.46..4492.81 rows=28618 width=52) (actual time=30.056..55.976 rows=26156 loops=2)
                          Hash Cond: (lead.id = lead_evento.lead_id)
                          Buffers: shared hit=2902
                          ->  Parallel Seq Scan on lead  (cost=0.00..2279.42 rows=43132 width=40) (actual time=0.009..9.390 rows=37036 loops=2)
                                Filter: ((data_criacao >= '2026-03-24 00:00:00'::timestamp without time zone) AND (data_criacao < '2026-04-23 00:00:00'::timestamp without time zone))
                                Rows Removed by Filter: 855
                                Buffers: shared hit=1616
                          ->  Hash  (cost=1141.87..1141.87 rows=49887 width=16) (actual time=24.035..24.036 rows=52313 loops=2)
                                Buckets: 65536  Batches: 1  Memory Usage: 2965kB
                                Buffers: shared hit=1286
                                ->  Seq Scan on lead_evento  (cost=0.00..1141.87 rows=49887 width=16) (actual time=0.025..8.606 rows=52313 loops=2)
                                      Buffers: shared hit=1286
                    ->  Hash  (cost=3.93..3.93 rows=93 width=33) (actual time=1.310..1.311 rows=93 loops=2)
                          Buckets: 1024  Batches: 1  Memory Usage: 15kB
                          Buffers: shared hit=6
                          ->  Seq Scan on evento  (cost=0.00..3.93 rows=93 width=33) (actual time=0.945..0.971 rows=93 loops=2)
                                Buffers: shared hit=6
Planning:
  Buffers: shared hit=25
Planning Time: 34.189 ms
Execution Time: 238.591 ms
```

### _load_lead_event_facts_via_batch

Flags: temp_blocks

```sql
SELECT DISTINCT evento.id, evento.nome, evento.cidade, evento.estado, lead.id AS id_1, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome AS nome_1, lead.sobrenome, lead_batches.origem_lote, lead_batches.tipo_lead_proponente 
FROM lead JOIN lead_batches ON lead.batch_id = lead_batches.id JOIN evento ON evento.id = lead_batches.evento_id 
WHERE lead.data_criacao >= '2026-03-24 00:00:00+00:00' AND lead.data_criacao < '2026-04-23 00:00:00+00:00' AND lead.batch_id IS NOT NULL AND lead_batches.evento_id IS NOT NULL AND lead_batches.stage = 'GOLD' AND lead_batches.pipeline_status IN ('PASS', 'PASS_WITH_WARNINGS')
```

```text
HashAggregate  (cost=484.70..490.70 rows=600 width=98) (actual time=62.954..86.050 rows=39554 loops=1)
  Group Key: evento.id, evento.nome, evento.cidade, evento.estado, lead.id, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome, lead.sobrenome, lead_batches.origem_lote, lead_batches.tipo_lead_proponente
  Batches: 5  Memory Usage: 4409kB  Disk Usage: 3416kB
  Buffers: shared hit=1315, temp read=273 written=623
  ->  Merge Join  (cost=0.65..466.70 rows=600 width=98) (actual time=0.050..30.222 rows=39554 loops=1)
        Merge Cond: (lead_batches.evento_id = evento.id)
        Buffers: shared hit=1315
        ->  Nested Loop  (cost=0.43..851.72 rows=600 width=69) (actual time=0.039..22.931 rows=39554 loops=1)
              Buffers: shared hit=1304
              ->  Index Only Scan using idx_lead_batches_dashboard_gold_evento_status on lead_batches  (cost=0.14..3.64 rows=2 width=33) (actual time=0.018..0.049 rows=20 loops=1)
                    Index Cond: ((evento_id IS NOT NULL) AND (pipeline_status = ANY ('{PASS,PASS_WITH_WARNINGS}'::pipelinestatus[])))
                    Heap Fetches: 10
                    Buffers: shared hit=10
              ->  Index Scan using ix_lead_lead_batch_id on lead  (cost=0.29..394.98 rows=2906 width=44) (actual time=0.010..0.694 rows=1978 loops=20)
                    Index Cond: ((batch_id = lead_batches.id) AND (batch_id IS NOT NULL))
                    Filter: ((data_criacao >= '2026-03-24 00:00:00'::timestamp without time zone) AND (data_criacao < '2026-04-23 00:00:00'::timestamp without time zone))
                    Buffers: shared hit=1294
        ->  Index Scan using evento_pkey on evento  (cost=0.14..6.84 rows=93 width=33) (actual time=0.006..0.058 rows=93 loops=1)
              Buffers: shared hit=11
Planning:
  Buffers: shared hit=22
Planning Time: 3.237 ms
Execution Time: 89.577 ms
```

### _load_visible_events_by_normalized_name

Flags: seq_scan

```sql
SELECT evento.id, evento.nome, evento.cidade, evento.estado 
FROM evento
```

```text
Seq Scan on evento  (cost=0.00..3.93 rows=93 width=33) (actual time=0.015..0.040 rows=93 loops=1)
  Buffers: shared hit=3
Planning Time: 0.064 ms
Execution Time: 0.064 ms
```

### _load_lead_event_facts_via_evento_nome

Flags: seq_scan

```sql
SELECT lead.id, lead.evento_nome, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome, lead.sobrenome 
FROM lead 
WHERE lead.data_criacao >= '2026-03-24 00:00:00+00:00' AND lead.data_criacao < '2026-04-23 00:00:00+00:00' AND lead.evento_nome IS NOT NULL AND trim(lead.evento_nome) != ''
```

```text
Seq Scan on lead  (cost=0.00..3119.76 rows=72959 width=61) (actual time=0.016..37.661 rows=74072 loops=1)
  Filter: ((evento_nome IS NOT NULL) AND (data_criacao >= '2026-03-24 00:00:00'::timestamp without time zone) AND (data_criacao < '2026-04-23 00:00:00'::timestamp without time zone) AND (TRIM(BOTH FROM evento_nome) <> ''::text))
  Rows Removed by Filter: 1710
  Buffers: shared hit=1616
Planning:
  Buffers: shared hit=4
Planning Time: 0.145 ms
Execution Time: 41.463 ms
```

## reference_event_30d

Descricao: Evento de referencia com janela movel de 30 dias
Parametros: {'data_inicio': datetime.date(2026, 3, 24), 'data_fim': datetime.date(2026, 4, 22), 'evento_id': 107}
### _load_lead_event_facts

Flags: seq_scan

```sql
SELECT DISTINCT evento.id, evento.nome, evento.cidade, evento.estado, lead.id AS id_1, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome AS nome_1, lead.sobrenome, lead_evento.source_kind, lead_evento.tipo_lead 
FROM lead_evento JOIN lead ON lead.id = lead_evento.lead_id JOIN evento ON evento.id = lead_evento.evento_id 
WHERE evento.id = 107 AND lead.data_criacao >= '2026-03-24 00:00:00+00:00' AND lead.data_criacao < '2026-04-23 00:00:00+00:00'
```

```text
HashAggregate  (cost=4091.90..4171.46 rows=7956 width=81) (actual time=41.339..45.008 rows=10461 loops=1)
  Group Key: evento.nome, evento.cidade, evento.estado, lead.id, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome, lead.sobrenome, lead_evento.source_kind, lead_evento.tipo_lead
  Batches: 1  Memory Usage: 1817kB
  Buffers: shared hit=3978
  ->  Nested Loop  (cost=850.14..3873.11 rows=7956 width=81) (actual time=5.871..34.599 rows=10461 loops=1)
        Buffers: shared hit=3978
        ->  Index Scan using ix_evento_nome on evento  (cost=0.14..7.24 rows=1 width=33) (actual time=0.050..0.062 rows=1 loops=1)
              Filter: (id = 107)
              Rows Removed by Filter: 92
              Buffers: shared hit=33
        ->  Hash Join  (cost=850.00..3786.31 rows=7956 width=52) (actual time=5.818..33.076 rows=10461 loops=1)
              Hash Cond: (lead.id = lead_evento.lead_id)
              Buffers: shared hit=3945
              ->  Seq Scan on lead  (cost=0.00..2743.82 rows=73325 width=40) (actual time=0.011..15.151 rows=74072 loops=1)
                    Filter: ((data_criacao >= '2026-03-24 00:00:00'::timestamp without time zone) AND (data_criacao < '2026-04-23 00:00:00'::timestamp without time zone))
                    Rows Removed by Filter: 1710
                    Buffers: shared hit=1616
              ->  Hash  (cost=748.03..748.03 rows=8158 width=16) (actual time=5.798..5.799 rows=10461 loops=1)
                    Buckets: 16384 (originally 8192)  Batches: 1 (originally 1)  Memory Usage: 619kB
                    Buffers: shared hit=2329
                    ->  Index Scan using idx_lead_evento_evento_id_lead_id on lead_evento  (cost=0.29..748.03 rows=8158 width=16) (actual time=0.032..3.659 rows=10461 loops=1)
                          Index Cond: (evento_id = 107)
                          Buffers: shared hit=2329
Planning:
  Buffers: shared hit=15
Planning Time: 0.525 ms
Execution Time: 45.631 ms
```

### _load_lead_event_facts_via_batch

Flags: nenhuma

```sql
SELECT DISTINCT evento.id, evento.nome, evento.cidade, evento.estado, lead.id AS id_1, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome AS nome_1, lead.sobrenome, lead_batches.origem_lote, lead_batches.tipo_lead_proponente 
FROM lead JOIN lead_batches ON lead.batch_id = lead_batches.id JOIN evento ON evento.id = lead_batches.evento_id 
WHERE evento.id = 107 AND lead.data_criacao >= '2026-03-24 00:00:00+00:00' AND lead.data_criacao < '2026-04-23 00:00:00+00:00' AND lead.batch_id IS NOT NULL AND lead_batches.evento_id IS NOT NULL AND lead_batches.stage = 'GOLD' AND lead_batches.pipeline_status IN ('PASS', 'PASS_WITH_WARNINGS')
```

```text
HashAggregate  (cost=685.56..688.56 rows=300 width=98) (actual time=9.874..12.592 rows=8273 loops=1)
  Group Key: evento.nome, evento.cidade, evento.estado, lead.id, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome, lead.sobrenome, lead_batches.origem_lote, lead_batches.tipo_lead_proponente
  Batches: 1  Memory Usage: 1561kB
  Buffers: shared hit=483
  ->  Nested Loop  (cost=0.57..677.31 rows=300 width=98) (actual time=0.060..4.537 rows=8273 loops=1)
        Buffers: shared hit=483
        ->  Nested Loop  (cost=0.28..9.61 rows=1 width=62) (actual time=0.048..0.060 rows=1 loops=1)
              Buffers: shared hit=36
              ->  Index Scan using ix_evento_nome on evento  (cost=0.14..7.24 rows=1 width=33) (actual time=0.037..0.047 rows=1 loops=1)
                    Filter: (id = 107)
                    Rows Removed by Filter: 92
                    Buffers: shared hit=33
              ->  Index Only Scan using idx_lead_batches_dashboard_gold_evento_status on lead_batches  (cost=0.14..2.36 rows=1 width=33) (actual time=0.009..0.011 rows=1 loops=1)
                    Index Cond: ((evento_id IS NOT NULL) AND (evento_id = 107) AND (pipeline_status = ANY ('{PASS,PASS_WITH_WARNINGS}'::pipelinestatus[])))
                    Heap Fetches: 1
                    Buffers: shared hit=3
        ->  Index Scan using ix_lead_lead_batch_id on lead  (cost=0.29..638.64 rows=2906 width=44) (actual time=0.010..2.627 rows=8273 loops=1)
              Index Cond: ((batch_id = lead_batches.id) AND (batch_id IS NOT NULL))
              Filter: ((data_criacao >= '2026-03-24 00:00:00'::timestamp without time zone) AND (data_criacao < '2026-04-23 00:00:00'::timestamp without time zone))
              Buffers: shared hit=447
Planning:
  Buffers: shared hit=7
Planning Time: 0.486 ms
Execution Time: 13.078 ms
```

