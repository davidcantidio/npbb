# pg_stat_statements: top 10 atual

Data: 2026-04-20.
Fonte: MCP Supabase read-only.

Classificacao: validado por EXPLAIN/metrica; observado em execucao real.

Este arquivo registra a metrica atual. Ele nao e uma comparacao antes/depois.

| rank | query resumida | calls | total_exec_ms | mean_exec_ms | shared_blks_hit | shared_blks_read | temp_blks_read | temp_blks_written |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `SELECT lead_batches... arquivo_bronze ... WHERE lead_batches.id=$1` | 5252 | 1222809.848 | 232.827 | 31582 | 951276 | 0 | 0 |
| 2 | `SELECT lead_batches... arquivo_sha256 ... WHERE lead_batches.id=$1` | 982 | 647254.436 | 659.119 | 5861 | 511461 | 0 | 0 |
| 3 | `INSERT INTO lead (...) VALUES (...) RETURNING lead.id` | 24473 | 180048.062 | 7.357 | 235965 | 13967 | 0 | 0 |
| 4 | `SELECT lead_batches... WHERE enviado_por=$1 AND arquivo_sha256=$2 ...` | 201 | 179397.251 | 892.524 | 16549 | 128294 | 0 | 0 |
| 5 | `SELECT evento.id, evento.nome... ORDER BY evento.data_inicio DESC` | 183 | 82261.793 | 449.518 | 4439 | 62970 | 0 | 0 |
| 6 | `SELECT lead_batches... WHERE lead_batches.id = $1` | 3988 | 74264.902 | 18.622 | 22945 | 58083 | 0 | 0 |
| 7 | `UPDATE lead_batches SET status_processamento=$1... WHERE lead_batches.id=$8` | 417 | 30742.750 | 73.724 | 6787 | 21714 | 0 | 0 |
| 8 | `SELECT leads_silver... WHERE leads_silver.batch_id = $1 ORDER BY leads_silver.row_index` | 23 | 23181.626 | 1007.897 | 22973 | 133 | 652 | 654 |
| 9 | `INSERT INTO lead_batches (...) RETURNING lead_batches.id` | 201 | 22365.687 | 111.272 | 1881 | 13177 | 0 | 0 |
| 10 | `UPDATE lead_batches SET total_linhas=$1, linhas_validas=$2... WHERE lead_batches.id=$9` | 38 | 19821.844 | 521.628 | 241 | 16661 | 0 | 0 |

Leitura objetiva:

- Queries com `lead_batches.arquivo_bronze` ainda dominam custo total observado.
- Isto e consistente com a pendencia de 222 payloads inline registrada em `supabase_rls_roles_storage_2026-04-20.md`.
- Nao ha ganho medido nesta evidencia; ha baseline atual para comparacao futura.
