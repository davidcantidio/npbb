-- Supabase/Postgres schema for mcp-bb-scraping outputs.
-- Target source: tools/mcp-bb-scraping/out/<sponsor>/*.csv|*.json

create extension if not exists pgcrypto;

create schema if not exists bb_scraping;

create or replace function bb_scraping.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table if not exists bb_scraping.sponsors (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  name text,
  instagram_handle text unique,
  instagram_url text,
  status text,
  notes text,
  source_row_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists bb_scraping.scraping_runs (
  id uuid primary key default gen_random_uuid(),
  sponsor_id uuid not null references bb_scraping.sponsors(id) on delete cascade,
  run_handle text,
  out_dir text not null,
  run_csv_path text,
  run_log_path text,
  started_at timestamptz,
  finished_at timestamptz,
  since_date date,
  until_date date,
  max_items integer,
  scrape_instagram boolean,
  scrape_x boolean,
  scrape_tiktok boolean,
  run_status text not null default 'unknown' check (run_status in ('success', 'partial', 'failed', 'unknown')),
  source_files_hash text,
  created_at timestamptz not null default now()
);

create index if not exists idx_scraping_runs_sponsor_started_at
  on bb_scraping.scraping_runs (sponsor_id, started_at desc);

create table if not exists bb_scraping.social_profile_snapshots (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references bb_scraping.scraping_runs(id) on delete cascade,
  sponsor_id uuid not null references bb_scraping.sponsors(id) on delete cascade,
  platform text not null check (platform in ('instagram', 'x', 'tiktok')),
  profile_url text not null,
  fetched_at timestamptz,
  username text,
  display_name text,
  followers bigint,
  following bigint,
  posts_count bigint,
  likes_total bigint,
  bio text,
  external_url text,
  meta_description text,
  og_title text,
  og_description text,
  raw_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (platform, profile_url, fetched_at)
);

create index if not exists idx_profile_snapshots_sponsor_platform_fetched_at
  on bb_scraping.social_profile_snapshots (sponsor_id, platform, fetched_at desc);

create table if not exists bb_scraping.social_posts (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references bb_scraping.scraping_runs(id) on delete cascade,
  sponsor_id uuid not null references bb_scraping.sponsors(id) on delete cascade,
  platform text not null check (platform in ('instagram', 'x', 'tiktok')),
  post_url text not null,
  shortcode text,
  post_datetime timestamptz,
  post_date date,
  text_content text,
  hashtags_raw text,
  mentions_raw text,
  owner_username text,
  is_owner_profile boolean,
  media_type text,
  is_collab boolean,
  coauthors_raw text,
  paid_partnership boolean,
  paid_partner text,
  location text,
  likes bigint,
  comments bigint,
  views bigint,
  plays_or_views bigint,
  replies bigint,
  reposts bigint,
  shares bigint,
  is_bb_mention boolean,
  bb_connection_type text check (bb_connection_type in ('mention', 'hashtag', 'mention-hashtag') or bb_connection_type is null),
  bb_markers_count integer,
  scraped_at timestamptz,
  raw_row_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (platform, post_url)
);

create unique index if not exists uq_social_posts_platform_shortcode
  on bb_scraping.social_posts (platform, shortcode)
  where shortcode is not null and shortcode <> '';

create index if not exists idx_social_posts_sponsor_platform_datetime
  on bb_scraping.social_posts (sponsor_id, platform, post_datetime desc);

create index if not exists idx_social_posts_sponsor_is_bb
  on bb_scraping.social_posts (sponsor_id, is_bb_mention);

create table if not exists bb_scraping.post_hashtags (
  post_id uuid not null references bb_scraping.social_posts(id) on delete cascade,
  hashtag text not null,
  created_at timestamptz not null default now(),
  primary key (post_id, hashtag)
);

create table if not exists bb_scraping.post_mentions (
  post_id uuid not null references bb_scraping.social_posts(id) on delete cascade,
  mention_handle text not null,
  created_at timestamptz not null default now(),
  primary key (post_id, mention_handle)
);

create table if not exists bb_scraping.post_coauthors (
  post_id uuid not null references bb_scraping.social_posts(id) on delete cascade,
  coauthor_handle text not null,
  created_at timestamptz not null default now(),
  primary key (post_id, coauthor_handle)
);

create table if not exists bb_scraping.indicators_snapshot (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null unique references bb_scraping.scraping_runs(id) on delete cascade,
  sponsor_id uuid not null references bb_scraping.sponsors(id) on delete cascade,
  handler text,
  source_indicadores_csv_path text,
  source_indicadores_json_path text,
  generated_at_utc timestamptz,
  indicators_csv_flat jsonb not null default '{}'::jsonb,
  indicators_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists bb_scraping.indicators_monthly (
  id uuid primary key default gen_random_uuid(),
  snapshot_id uuid not null references bb_scraping.indicators_snapshot(id) on delete cascade,
  handler text,
  month date not null,
  posts_bb integer not null default 0,
  posts_total integer not null default 0,
  created_at timestamptz not null default now(),
  unique (snapshot_id, month)
);

create index if not exists idx_indicators_monthly_month
  on bb_scraping.indicators_monthly (month);

drop trigger if exists trg_sponsors_set_updated_at on bb_scraping.sponsors;
create trigger trg_sponsors_set_updated_at
before update on bb_scraping.sponsors
for each row execute function bb_scraping.set_updated_at();

drop trigger if exists trg_social_posts_set_updated_at on bb_scraping.social_posts;
create trigger trg_social_posts_set_updated_at
before update on bb_scraping.social_posts
for each row execute function bb_scraping.set_updated_at();

-- Runtime views (derived metrics, no duplicated persistence).
create or replace view bb_scraping.v_bb_monthly_kpis as
select
  s.id as sponsor_id,
  s.slug as sponsor_slug,
  date_trunc('month', p.post_datetime)::date as month,
  count(*)::int as posts_total,
  count(*) filter (where coalesce(p.is_bb_mention, false))::int as posts_bb,
  round(
    100.0 * count(*) filter (where coalesce(p.is_bb_mention, false))
    / nullif(count(*), 0),
    2
  ) as bb_share_pct
from bb_scraping.social_posts p
join bb_scraping.sponsors s on s.id = p.sponsor_id
where p.post_datetime is not null
group by s.id, s.slug, date_trunc('month', p.post_datetime)::date;

create or replace view bb_scraping.v_sponsor_runtime_summary as
select
  s.id as sponsor_id,
  s.slug as sponsor_slug,
  count(*)::int as posts_total,
  count(*) filter (where coalesce(p.is_bb_mention, false))::int as bb_posts_total,
  round(
    100.0 * count(*) filter (where coalesce(p.is_bb_mention, false))
    / nullif(count(*), 0),
    2
  ) as bb_share_pct,
  max(p.post_datetime) filter (where coalesce(p.is_bb_mention, false)) as bb_last_post_datetime,
  percentile_cont(0.5) within group (order by p.likes)
    filter (where p.likes is not null and coalesce(p.is_collab, false)) as sponsored_median_likes,
  percentile_cont(0.5) within group (order by p.comments)
    filter (where p.comments is not null and coalesce(p.is_collab, false)) as sponsored_median_comments
from bb_scraping.sponsors s
left join bb_scraping.social_posts p on p.sponsor_id = s.id
group by s.id, s.slug;
