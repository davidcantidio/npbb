# Diagnostico tecnico do dashboard etario
# label: phase1
# gerado em 2026-04-23T20:14:17.255403+00:00

## Status das evidencias

- pg_stat_statements: disponivel
- EXPLAIN ANALYZE: disponivel

## Ranking de gargalos

- `_load_lead_event_facts`: impacto `alto` (39.23% do tempo medio agregado). Causa: Leitura ampla no Postgres para alimentar a etapa. Proximo passo: `novo índice`. Evidencia: pct_total=39.23%, flags=seq_scan,temp_blocks.
- `_load_lead_event_facts_via_batch`: impacto `alto` (28.02% do tempo medio agregado). Causa: Plano com uso de temporarios/spill durante a leitura. Proximo passo: `novo índice`. Evidencia: pct_total=28.02%, flags=temp_blocks.
- `_load_lead_event_facts_via_evento_nome`: impacto `alto` (24.15% do tempo medio agregado). Causa: Leitura ampla no Postgres para alimentar a etapa. Proximo passo: `reduzir full scan`. Evidencia: pct_total=24.15%, flags=seq_scan.
- `post_processing_full_passes`: impacto `medio` (1.78% do tempo medio agregado). Causa: Mesma base `link_facts` reprocessada em passes separados de qualidade, confianca e insights. Proximo passo: `remover recomputação Python`. Evidencia: pct_total=1.78%, functions=_build_qualidade_por_origem, _build_qualidade_consolidado, _build_confianca_consolidado, _build_insights.
- `_build_qualidade_por_origem`: impacto `medio` (0.91% do tempo medio agregado). Causa: Reprocessamento completo da mesma base em uma etapa derivada. Proximo passo: `remover recomputação Python`. Evidencia: pct_total=0.91%, flags=none.
- `_build_qualidade_consolidado`: impacto `medio` (0.63% do tempo medio agregado). Causa: Reprocessamento completo da mesma base em uma etapa derivada. Proximo passo: `remover recomputação Python`. Evidencia: pct_total=0.63%, flags=none.
- `_build_confianca_consolidado`: impacto `medio` (0.23% do tempo medio agregado). Causa: Reprocessamento completo da mesma base em uma etapa derivada. Proximo passo: `remover recomputação Python`. Evidencia: pct_total=0.23%, flags=none.
- `_build_insights`: impacto `medio` (0.00% do tempo medio agregado). Causa: Reprocessamento completo da mesma base em uma etapa derivada. Proximo passo: `remover recomputação Python`. Evidencia: pct_total=0.00%, flags=none.
- `build_age_analysis_unattributed`: impacto `baixo` (2.90% do tempo medio agregado). Causa: Custo observado sem sinal forte de I/O ou spill. Proximo passo: `não otimizar agora`. Evidencia: pct_total=2.90%, flags=none.
- `_accumulate_link_metrics`: impacto `baixo` (2.37% do tempo medio agregado). Causa: Agregacao principal mantida em Python sobre facts materializados. Proximo passo: `não otimizar agora`. Evidencia: pct_total=2.37%, flags=none.
- `_merge_and_dedupe_facts`: impacto `baixo` (1.55% do tempo medio agregado). Causa: Uniao de multiplas fontes seguida de deduplicacao em memoria. Proximo passo: `não otimizar agora`. Evidencia: pct_total=1.55%, flags=none.
- `_finalize_event_analysis`: impacto `baixo` (0.01% do tempo medio agregado). Causa: Agregacao principal mantida em Python sobre facts materializados. Proximo passo: `não otimizar agora`. Evidencia: pct_total=0.01%, flags=none.
- `_build_consolidated_analysis`: impacto `baixo` (0.00% do tempo medio agregado). Causa: Agregacao principal mantida em Python sobre facts materializados. Proximo passo: `não otimizar agora`. Evidencia: pct_total=0.00%, flags=none.

## Cenarios

### no_filters

- Descricao: Sem filtros
- Parametros: `{'data_inicio': None, 'data_fim': None, 'evento_id': None}`
- Total ms: min=16057.141, p50=20233.995, mean=21680.175, p95=31714.682, max=36941.491
- Volumes: `{'facts_primary': 52313, 'facts_batch': 39554, 'facts_event_name': 46813, 'facts_after_dedupe': 60728, 'dedupe_candidate_volume': 138680, 'dedupe_suppressed_volume': 77952, 'event_name_candidate_volume': 75782, 'event_name_ambiguous_volume': 27668, 'event_name_missing_volume': 1301, 'base_total': 60728, 'event_count': 15, 'lineage_mix': {'lead_batch': 39737, 'ativacao': 12576, 'evento_nome_backfill': 8415}, 'base_total_min': 60728, 'base_total_max': 60728}`
- Top stages: _load_lead_event_facts=7576.609ms (34.95%), _load_lead_event_facts_via_evento_nome=6512.17ms (30.04%), _load_lead_event_facts_via_batch=5644.662ms (26.04%), build_age_analysis_unattributed=653.531ms (3.01%), _accumulate_link_metrics=523.462ms (2.41%)
- Top query families: _load_lead_event_facts.sql=5013.767ms, _load_lead_event_facts_via_evento_nome.sql=4583.081ms, _load_lead_event_facts_via_batch.sql=3913.391ms, _load_visible_events_by_normalized_name.sql=68.389ms
- Explain flags: _load_lead_event_facts=[seq_scan,temp_blocks], _load_lead_event_facts_via_batch=[temp_blocks], _load_lead_event_facts_via_evento_nome=[seq_scan], _load_visible_events_by_normalized_name=[seq_scan]
- pg_stat delta top1: `{'queryid': '737253698671314193', 'calls_delta': 61, 'total_exec_ms_delta': 63128.731, 'mean_exec_ms_after': 1128.486, 'rows_delta': 3099522, 'shared_blks_hit_delta': 9813093, 'shared_blks_read_delta': 0, 'temp_blks_read_delta': 0, 'temp_blks_written_delta': 0, 'query_sample': 'SELECT DISTINCT evento.id, evento.nome, evento.cidade, evento.estado, lead.id AS id_1, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome AS nome_1, lead.sobrenome, lead_evento.source_kind, lead_evento.tipo_lead FROM lead_evento JOIN lead ON lead.id = lead_evento.lead_id JOIN evento ON evento.id = lead_evento.evento_id'}`

### reference_event

- Descricao: Evento de maior volume recente ou total
- Parametros: `{'data_inicio': None, 'data_fim': None, 'evento_id': 107}`
- Total ms: min=2693.303, p50=3550.41, mean=5305.448, p95=11142.02, max=13607.519
- Volumes: `{'facts_primary': 10461, 'facts_batch': 8273, 'facts_event_name': 0, 'facts_after_dedupe': 10461, 'dedupe_candidate_volume': 18734, 'dedupe_suppressed_volume': 8273, 'event_name_candidate_volume': 0, 'event_name_ambiguous_volume': 0, 'event_name_missing_volume': 0, 'base_total': 10461, 'event_count': 1, 'lineage_mix': {'lead_batch': 10461}, 'base_total_min': 10461, 'base_total_max': 10461}`
- Top stages: _load_lead_event_facts=2787.072ms (52.53%), _load_lead_event_facts_via_batch=2190.636ms (41.29%), build_age_analysis_unattributed=122.243ms (2.3%), _accumulate_link_metrics=100.087ms (1.89%), _build_qualidade_por_origem=42.691ms (0.8%)
- Top query families: _load_lead_event_facts_via_batch.sql=1992.951ms, _load_lead_event_facts.sql=1910.17ms
- Explain flags: _load_lead_event_facts=[seq_scan], _load_lead_event_facts_via_batch=[none]
- pg_stat delta top1: `{'queryid': '737253698671314193', 'calls_delta': 48, 'total_exec_ms_delta': 17977.236, 'mean_exec_ms_after': 1128.486, 'rows_delta': 2419453, 'shared_blks_hit_delta': 9775280, 'shared_blks_read_delta': 0, 'temp_blks_read_delta': 0, 'temp_blks_written_delta': 0, 'query_sample': 'SELECT DISTINCT evento.id, evento.nome, evento.cidade, evento.estado, lead.id AS id_1, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome AS nome_1, lead.sobrenome, lead_evento.source_kind, lead_evento.tipo_lead FROM lead_evento JOIN lead ON lead.id = lead_evento.lead_id JOIN evento ON evento.id = lead_evento.evento_id'}`

### rolling_30d

- Descricao: Janela movel de 30 dias ancorada na maior lead.data_criacao
- Parametros: `{'data_inicio': datetime.date(2026, 3, 24), 'data_fim': datetime.date(2026, 4, 22), 'evento_id': None}`
- Total ms: min=15646.318, p50=18392.918, mean=20139.673, p95=28857.726, max=32628.047
- Volumes: `{'facts_primary': 52313, 'facts_batch': 39554, 'facts_event_name': 45104, 'facts_after_dedupe': 59019, 'dedupe_candidate_volume': 136971, 'dedupe_suppressed_volume': 77952, 'event_name_candidate_volume': 74072, 'event_name_ambiguous_volume': 27668, 'event_name_missing_volume': 1300, 'base_total': 59019, 'event_count': 14, 'lineage_mix': {'lead_batch': 39737, 'ativacao': 12576, 'evento_nome_backfill': 6706}, 'base_total_min': 59019, 'base_total_max': 59019}`
- Top stages: _load_lead_event_facts=7760.513ms (38.53%), _load_lead_event_facts_via_evento_nome=5384.054ms (26.73%), _load_lead_event_facts_via_batch=5201.013ms (25.82%), build_age_analysis_unattributed=593.541ms (2.95%), _accumulate_link_metrics=488.317ms (2.42%)
- Top query families: _load_lead_event_facts.sql=5286.135ms, _load_lead_event_facts_via_batch.sql=3711.081ms, _load_lead_event_facts_via_evento_nome.sql=3379.743ms, _load_visible_events_by_normalized_name.sql=143.046ms
- Explain flags: _load_lead_event_facts=[seq_scan,temp_blocks], _load_lead_event_facts_via_batch=[temp_blocks], _load_lead_event_facts_via_evento_nome=[seq_scan], _load_visible_events_by_normalized_name=[seq_scan]
- pg_stat delta top1: `{'queryid': '-7775742807276796399', 'calls_delta': 13, 'total_exec_ms_delta': 46309.497, 'mean_exec_ms_after': 3693.325, 'rows_delta': 680069, 'shared_blks_hit_delta': 37804, 'shared_blks_read_delta': 0, 'temp_blks_read_delta': 6596, 'temp_blks_written_delta': 12237, 'query_sample': 'SELECT DISTINCT evento.id, evento.nome, evento.cidade, evento.estado, lead.id AS id_1, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome AS nome_1, lead.sobrenome, lead_evento.source_kind, lead_evento.tipo_lead FROM lead_evento JOIN lead ON lead.id = lead_evento.lead_id JOIN evento ON evento.id = lead_evento.evento_id WHERE lead.data_criacao >= $1::timestamptz AND lead.data_criacao < $2::timestamptz'}`

### reference_event_30d

- Descricao: Evento de referencia com janela movel de 30 dias
- Parametros: `{'data_inicio': datetime.date(2026, 3, 24), 'data_fim': datetime.date(2026, 4, 22), 'evento_id': 107}`
- Total ms: min=1767.284, p50=2026.546, mean=2139.822, p95=2602.108, max=2723.841
- Volumes: `{'facts_primary': 10461, 'facts_batch': 8273, 'facts_event_name': 0, 'facts_after_dedupe': 10461, 'dedupe_candidate_volume': 18734, 'dedupe_suppressed_volume': 8273, 'event_name_candidate_volume': 0, 'event_name_ambiguous_volume': 0, 'event_name_missing_volume': 0, 'base_total': 10461, 'event_count': 1, 'lineage_mix': {'lead_batch': 10461}, 'base_total_min': 10461, 'base_total_max': 10461}`
- Top stages: _load_lead_event_facts=1200.842ms (56.12%), _load_lead_event_facts_via_batch=768.782ms (35.93%), build_age_analysis_unattributed=58.999ms (2.76%), _accumulate_link_metrics=53.77ms (2.51%), _merge_and_dedupe_facts=27.519ms (1.29%)
- Top query families: _load_lead_event_facts.sql=792.255ms, _load_lead_event_facts_via_batch.sql=633.887ms
- Explain flags: _load_lead_event_facts=[seq_scan], _load_lead_event_facts_via_batch=[none]
- pg_stat delta top1: `{'queryid': '737253698671314193', 'calls_delta': 48, 'total_exec_ms_delta': 17977.236, 'mean_exec_ms_after': 1128.486, 'rows_delta': 2419453, 'shared_blks_hit_delta': 9775280, 'shared_blks_read_delta': 0, 'temp_blks_read_delta': 0, 'temp_blks_written_delta': 0, 'query_sample': 'SELECT DISTINCT evento.id, evento.nome, evento.cidade, evento.estado, lead.id AS id_1, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome AS nome_1, lead.sobrenome, lead_evento.source_kind, lead_evento.tipo_lead FROM lead_evento JOIN lead ON lead.id = lead_evento.lead_id JOIN evento ON evento.id = lead_evento.evento_id'}`

