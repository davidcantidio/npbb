-- Roles dedicadas para API (pooler :6543) e worker (:5432), sem BYPASSRLS.
-- Executar como superuser (ex.: role postgres no Supabase SQL Editor ou psql).
--
-- Apos criar, defina senhas fortes e atualize:
--   DATABASE_URL=postgresql+psycopg2://npbb_api:***@aws-0-...pooler.supabase.com:6543/postgres
--   WORKER_DATABASE_URL=postgresql+psycopg2://npbb_worker:***@db....supabase.co:5432/postgres
--
-- Ajuste GRANT conforme o menor privilegio aceitavel para o seu schema; este script
-- cobre o padrao monolitico em public usado pela aplicacao NPBB.

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'npbb_api') THEN
    CREATE ROLE npbb_api WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT NOREPLICATION;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'npbb_worker') THEN
    CREATE ROLE npbb_worker WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT NOREPLICATION;
  END IF;
END
$$;

ALTER ROLE npbb_api WITH NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT NOREPLICATION NOBYPASSRLS;
ALTER ROLE npbb_worker WITH NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT NOREPLICATION NOBYPASSRLS;

-- IMPORTANTE: defina senhas fora deste arquivo versionado, por exemplo:
-- ALTER ROLE npbb_api PASSWORD '...';
-- ALTER ROLE npbb_worker PASSWORD '...';

DO $grantdb$
DECLARE
  db text := current_database();
BEGIN
  EXECUTE format('GRANT CONNECT ON DATABASE %I TO npbb_api', db);
  EXECUTE format('GRANT CONNECT ON DATABASE %I TO npbb_worker', db);
END
$grantdb$;

GRANT USAGE ON SCHEMA public TO npbb_api;
GRANT USAGE ON SCHEMA public TO npbb_worker;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO npbb_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO npbb_worker;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO npbb_api;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO npbb_worker;

-- Objetos futuros criados pelo owner do schema (ex.: role postgres no Supabase):
-- ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO npbb_api;
-- ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO npbb_worker;
-- ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO npbb_api;
-- ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO npbb_worker;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO npbb_api;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO npbb_worker;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO npbb_api;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO npbb_worker;
