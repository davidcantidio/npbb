# Mapeamento de artefatos `out/*` para Supabase

Este documento define como os arquivos em `tools/mcp-bb-scraping/out/<patrocinado>/` entram no schema SQL:

- `docs/supabase_scraping_schema.sql`

## 1) Tabela pai: patrocinado

- Origem principal:
  - `config/instagram_handles.csv`
  - nome da pasta de saida (`out/<slug>`)
- Destino: `bb_scraping.sponsors`

Mapeamento recomendado:
- `slug` <- nome da pasta (`alison_paz`)
- `name` <- `name` em `instagram_handles.csv`
- `instagram_handle` <- `handle` em `instagram_handles.csv` (sem `@`)
- `instagram_url` <- `url` em `instagram_handles.csv`
- `status` <- `status` em `instagram_handles.csv`
- `notes` <- `notes` em `instagram_handles.csv`
- `source_row_json` <- linha CSV completa em JSONB (auditoria)

## 2) Execucao (run)

- Origem:
  - `run_<handle>.csv`
  - `run_<handle>.log`
- Destino: `bb_scraping.scraping_runs`

Mapeamento:
- `started_at` <- primeira linha `INFO` de inicio
- `finished_at` <- ultima linha de encerramento/sucesso (quando existir)
- `out_dir` <- diretorio da run
- `run_csv_path`, `run_log_path` <- caminhos dos arquivos
- `since_date`, `until_date`, `max_items` <- parse da mensagem inicial
- `run_status` <- `success|partial|failed|unknown` por regra de log

## 3) Posts (fato principal)

- Origem prioritaria:
  - `<nome>_<handle>_posts.csv` (enriquecido IG)
- Origem complementar:
  - `posts_<handle>.csv` (unificado com X/TikTok)
- Destino: `bb_scraping.social_posts`

Chave natural de upsert:
- `(platform, post_url)`
- fallback auxiliar IG: `(platform, shortcode)` quando disponivel

Mapeamento de colunas:
- `platform` <- `platform` (ou `instagram` no enriquecido IG)
- `post_url` <- `post_url`/`url`
- `post_datetime` <- `datetime`
- `post_date` <- `date` (somente fallback)
- `text_content` <- `caption`/`text`
- `hashtags_raw` <- `hashtags`
- `mentions_raw` <- `mentions`
- `owner_username` <- `owner_username`
- `is_owner_profile` <- `is_owner_profile`
- `media_type` <- `media_type`
- `shortcode` <- `shortcode`
- `is_collab` <- `is_collab`
- `coauthors_raw` <- `coauthors`
- `paid_partnership` <- `paid_partnership`
- `paid_partner` <- `paid_partner`
- `location` <- `location`
- `likes/comments/views/plays_or_views/replies/reposts/shares` <- colunas homonimas
- `is_bb_mention` <- `is_bb_mention`
- `bb_connection_type` <- `bb_connection_type`
- `bb_markers_count` <- `bb_markers_count`
- `scraped_at` <- `scraped_at`
- `raw_row_json` <- linha original como JSONB

## 4) Tabelas filhas normalizadas

As colunas pipe-delimited devem virar tabelas N:N para consulta analitica:

- `bb_scraping.post_hashtags`
  - explode de `hashtags_raw` por `|`
- `bb_scraping.post_mentions`
  - explode de `mentions_raw` por `|`
- `bb_scraping.post_coauthors`
  - explode de `coauthors_raw` por `|`

Regras:
- trim de espacos
- remover vazios
- deduplicar por `post_id + valor`

## 5) Snapshot de perfil por plataforma

- Origem:
  - `instagram_profile_<handle>.csv/json`
  - `x_profile_<handle>.csv`
  - `tiktok_profile_<handle>.csv`
- Destino: `bb_scraping.social_profile_snapshots`

Observacoes:
- usar `platform` = `instagram|x|tiktok`
- campo `raw_json` deve receber o JSON completo quando existir

## 6) Indicadores

- Origem:
  - `indicadores_<handle>.csv` (1 linha e muitas colunas)
  - `indicadores.json` (estrutura hierarquica)
  - `indicadores_bb_por_mes_<handle>.csv`
- Destinos:
  - `bb_scraping.indicators_snapshot`
  - `bb_scraping.indicators_monthly`

Mapeamento:
- `indicators_csv_flat` <- objeto chave/valor da linha unica do CSV
- `indicators_json` <- JSON completo do arquivo
- `generated_at_utc` <- campo `generated_at_utc` do CSV quando existir
- mensal:
  - `month` <- `YYYY-MM` convertido para `date` (primeiro dia do mes)
  - `posts_bb`, `posts_total` <- colunas homonimas

## 7) O que e persistido vs runtime

Persistir:
- dados brutos de posts/perfis/runs
- flags calculadas no scraping (`is_bb_mention`, `bb_connection_type`, etc)
- snapshots de indicadores para rastreabilidade

Calcular em runtime (views SQL):
- shares e percentuais
- top N (hashtags, mentions, brands)
- medianas de performance
- recencia da ultima mencao BB

As views iniciais estao no final de `supabase_scraping_schema.sql`:
- `bb_scraping.v_bb_monthly_kpis`
- `bb_scraping.v_sponsor_runtime_summary`

## 8) Sequencia de carga recomendada (idempotente)

1. upsert `sponsors`
2. insert `scraping_runs`
3. upsert `social_posts`
4. refresh das tabelas filhas (`post_hashtags`, `post_mentions`, `post_coauthors`) por `post_id`
5. insert `indicators_snapshot`
6. upsert `indicators_monthly`
7. validacao de contagens por patrocinado/plataforma
