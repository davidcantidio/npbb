# Modelo Canonico Minimo (para sustentar o DOCX)

Objetivo: propor um modelo canonico no banco que suporte a geracao automatica do relatorio, com rastreabilidade de fonte e granularidade coerente (evento, dia, sessao).

Observacao importante:

- O NPBB ja possui entidades como `evento`, `lead`, `ativacao` e relacionamentos de leads por ativacao.
- O modelo abaixo complementa o que existe, adicionando camadas de "ingestao", "fonte", "sessoes do evento" e fatos de metricas (controle de acesso, midias, imprensa, survey).

## Entidades e granularidades

- Evento:
  - Uma linha por evento (cidade, periodo, metadados).
- Sessao:
  - Uma linha por sessao do evento (ex.: diurno gratuito, noturno show), com timestamps e tipo.
- Fatos por sessao:
  - Controle de acesso (entradas validadas e derivados) por sessao.
  - Vendas (total) por sessao, quando existir.
  - Opt-in (Eventim) por transacao (ou por agregacao, se exigido por LGPD).
- Fatos por periodo/plataforma:
  - Metricas de redes e social listening.
- Fatos de survey:
  - Respostas agregadas por pergunta/opcao (ou microdados, se disponivel).
- Catalogo e rastreio:
  - `sources` e `ingestions` para controlar linhagem e auditoria.

## Tabelas (canonico)

### sources

Registro de fontes (arquivos e sistemas).

- `source_id` (chave natural, ex.: `SRC_*`)
- `source_type` (pdf, xlsx, pptx, docx, sistema)
- `source_name` (nome humano)
- `file_name` (quando arquivo)
- `file_path` (quando arquivo)
- `file_hash` (sha)
- `created_at`

### ingestions

Registro de execucoes de ingestao por fonte.

- `ingestion_id`
- `source_id`
- `ingestion_started_at`, `ingestion_finished_at`
- `status` (success, failed, partial)
- `extractor_name` (qual extractor rodou)
- `notes` (erros, observacoes)

### events (ou mapeado para evento do NPBB)

Dimensao do evento.

- `event_id`
- `event_name`
- `city`, `state`
- `venue`
- `event_start_date`, `event_end_date`
- `report_scope_notes`

Integra com NPBB:

- Se o banco ja usa `evento`, manter `events` como view para `evento` ou estender `evento` com campos faltantes.

### event_sessions

Dimensao de sessao do evento.

- `session_id`
- `event_id`
- `session_name` (rotulo consistente)
- `session_type` (diurno_gratuito, noturno_show, outro)
- `session_start_at`, `session_end_at`
- `session_date`
- `source_of_truth_source_id` (qual fonte define a existencia da sessao)

### attendance_access_control

Fato de controle de acesso por sessao (entradas validadas).

- `attendance_id`
- `session_id`
- `ingestion_id`
- `ingressos_validos`
- `invalidos`
- `bloqueados`
- `presentes`
- `ausentes`
- `comparecimento_pct` (opcional: derivado, pode ir para mart)
- `lineage_ref` (pagina/trecho quando extraido de PDF)

### ticket_sales

Fato de vendas totais por sessao (quando existir fonte de vendas completa).

- `ticket_sales_id`
- `session_id`
- `ingestion_id`
- `sold_total`
- `refunded_total`
- `net_sold_total`
- `lineage_ref`

### optin_transactions

Fato de opt-in (Eventim), idealmente em granularidade de transacao (com cuidado LGPD).

- `optin_tx_id`
- `session_id`
- `ingestion_id`
- `purchase_at`
- `opt_in_flag`
- `sales_channel`
- `delivery_method`
- `ticket_category` (categoria/segmento)
- `ticket_qty`
- `person_key_hash` (hash de CPF/email, quando aplicavel)
- `lineage_ref` (aba/range)

### bb_relationship_metrics

Agregados de relacionamento BB por sessao (proxy via categoria/segmento).

- `bb_rel_id`
- `session_id`
- `ingestion_id`
- `segment` (cliente_bb, cartao_bb, funcionario_bb, publico_geral, outro)
- `tickets_qty` (ou transacoes_qty, conforme regra)
- `share_pct` (derivado, pode ir para mart)
- `lineage_ref`

### audience_survey_dimac

Fato de survey DIMAC (agregado por pergunta/opcao).

- `survey_id`
- `event_id`
- `ingestion_id`
- `question_group`
- `question_text`
- `answer_option`
- `value_pct`
- `value_count` (quando houver)
- `sample_notes` (metodologia, recorte)
- `lineage_ref` (pagina/figura)

### social_metrics

Metricas de redes sociais (Instagram etc) agregadas por periodo.

- `social_metric_id`
- `event_id`
- `ingestion_id`
- `platform`
- `metric_name`
- `metric_value`
- `period_start_date`, `period_end_date`
- `lineage_ref` (slide/box)

### social_listening

Highlights de social listening.

- `listening_id`
- `event_id`
- `ingestion_id`
- `provider` (ex.: brandwatch)
- `metric_name`
- `metric_value`
- `period_start_date`, `period_end_date`
- `methodology_notes`
- `lineage_ref`

### press_clipping

Metricas de midia/imprensa e (opcional) itens detalhados.

- `press_id`
- `event_id`
- `ingestion_id`
- `metric_name`
- `metric_value`
- `channel` (quando aplicavel)
- `lineage_ref`

Opcional (detalhado):

- `press_items` com uma linha por insercao/release (se a base existir).

### activations / leads (existente no NPBB)

- `ativacao` como dimensao de ativacao.
- `lead` como fato de lead (com dedupe).
- `ativacao_lead` como relacao lead x ativacao.

Complemento sugerido:

- Adicionar `event_session_id` (opcional) em `lead`/`ativacao_lead` se houver granularidade de sessao/dia na captura.

## Marts / Views (para render do relatorio)

Objetivo: reduzir logica no gerador de Word, concentrando calculos em views.

- `mart_report_big_numbers`
- `mart_report_attendance_by_session`
- `mart_report_show_day_summary`
- `mart_report_presale_curves`
- `mart_report_bb_share`
- `mart_report_audience_profile`
- `mart_report_satisfaction`
- `mart_report_social_summary`
- `mart_report_press_summary`
- `mart_report_leads_summary`

