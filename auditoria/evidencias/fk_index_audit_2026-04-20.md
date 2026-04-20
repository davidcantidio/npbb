# Auditoria de FKs e indices uteis

Data: 2026-04-20.
Fonte: consulta de catalogo via MCP Supabase read-only.

Classificacao: aplicado no banco/ambiente; observado em execucao real.

## FKs criticas do fluxo de leads/importacao

| FK | classificacao | indice util observado |
| --- | --- | --- |
| `lead.batch_id` | critica | `ix_lead_lead_batch_id` |
| `lead_batches.ativacao_id` | critica | `ix_lead_batches_ativacao_id` |
| `lead_batches.enviado_por` | critica | `idx_lead_batches_enviado_por_arquivo_sha256_created_at`, `ix_lead_batches_lead_batches_enviado_por` |
| `lead_batches.evento_id` | critica | `ix_lead_batches_lead_batches_evento_id` |
| `lead_evento.evento_id` | critica | `idx_lead_evento_evento_id_lead_id` |
| `lead_evento.lead_id` | critica | `ix_lead_evento_lead_evento_lead_id`, `uq_lead_evento_lead_id_evento_id` |
| `lead_evento.responsavel_agencia_id` | critica | `ix_lead_evento_lead_evento_responsavel_agencia_id` |
| `lead_import_etl_job.evento_id` | critica | `ix_lead_import_etl_job_evento_id` |
| `lead_import_etl_staging.job_id` | critica | `ix_lead_import_etl_staging_job_id` |
| `leads_silver.batch_id` | critica | `uq_leads_silver_batch_row` |
| `leads_silver.evento_id` | critica | `ix_leads_silver_leads_silver_evento_id` |

## FKs sem indice util observadas, fora do nucleo imediato

| FK | classificacao | decisao |
| --- | --- | --- |
| `ativacao_lead.gamificacao_id` | importante, mas fora do caminho principal de importacao observado | nao criar indice sem query/plano que use este filtro |
| `evento.subtipo_id` | importante para catalogos/filtros, nao critica ao import atual | nao criar indice nesta rodada sem plano comparativo |
| `evento.tipo_id` | importante para catalogos/filtros, nao critica ao import atual | nao criar indice nesta rodada sem plano comparativo |
| `evento.divisao_demandante_id` | importante para gestao de eventos, nao critica ao import atual | nao criar indice nesta rodada sem plano comparativo |

Conclusao verificavel:

- As FKs criticas do fluxo de importacao/leads observadas possuem indice util.
- Nenhum indice novo foi declarado como correcao nesta rodada porque a evidencia disponivel nao justificou ganho mensurado.
