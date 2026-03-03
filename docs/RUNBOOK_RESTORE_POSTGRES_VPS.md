# Restore Postgres na VPS

Runbook para restaurar um dump `pg_dump -Fc` no Postgres local da stack VPS.

## Pre-requisitos

- stack ja inicializada na VPS;
- arquivo `.dump` disponivel;
- acesso ao host com usuario capaz de executar `docker compose`.

## 1) Copiar o dump para a VPS

Destino recomendado:

```bash
/opt/npbb/backups/postgres/incoming/npbb_final.dump
```

## 2) Verificar se o banco esta de pe

```bash
cd /opt/npbb/app
docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml ps
```

Se necessario, suba apenas o Postgres:

```bash
docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml up -d postgres
```

## 3) Garantir extensoes base

Em banco novo, o bootstrap ja cria:
- `pgcrypto`
- `unaccent`
- `pg_trgm`
- funcao `immutable_unaccent(text)`

Se o restore vier de um banco legado e reclamar de extensao ou funcao, rode:

```bash
docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml exec -T postgres \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml exec -T postgres \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE EXTENSION IF NOT EXISTS unaccent;"
docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml exec -T postgres \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

## 4) Restaurar o dump

```bash
cd /opt/npbb/app
set -a
source /opt/npbb/env/.env.production
set +a

docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml exec -T postgres \
  pg_restore --clean --if-exists --no-owner --no-privileges \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  < /opt/npbb/backups/postgres/incoming/npbb_final.dump
```

## 5) Reaplicar migrations no schema restaurado

```bash
cd /opt/npbb/app
docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml up -d api
docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml exec -T api alembic upgrade head
```

## 6) Validar a aplicacao

```bash
cd /opt/npbb/app
./scripts/smoke_vps.sh /opt/npbb/env/.env.production
```

## 7) Rollback rapido antes da reabertura

Se o restore falhar antes da liberacao para usuarios:
- mantenha a infraestrutura antiga ativa;
- nao troque DNS;
- descarte o volume da VPS apenas se tiver certeza de que o ambiente antigo continua sendo a fonte de verdade.

Nao use rollback destrutivo apos reabrir escrita sem um novo dump do banco mais recente.
