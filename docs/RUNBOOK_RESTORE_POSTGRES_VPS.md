# Restore Postgres na VPS

Runbook para restaurar um dump `pg_dump -Fc` no Postgres local da stack VPS.

## Pre-requisitos

- stack ja inicializada na VPS;
- arquivo `.dump` disponivel em `/opt/npbb/backups/postgres/incoming` ou `/opt/npbb/backups/archive/daily`;
- acesso ao host com usuario capaz de executar `docker compose`.

## 1) Verificar se o banco esta de pe

```bash
cd /opt/npbb/app
docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml ps
```

Se necessario, suba apenas o banco:

```bash
docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml up -d db
```

## 2) Garantir extensoes base

Em banco novo, o bootstrap ja cria:
- `pgcrypto`
- `unaccent`
- `pg_trgm`
- funcao `immutable_unaccent(text)`

Se o restore reclamar de extensao ou funcao, rode:

```bash
docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml exec -T db \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml exec -T db \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE EXTENSION IF NOT EXISTS unaccent;"
docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml exec -T db \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

## 3) Restaurar o dump

```bash
cd /opt/npbb/app
set -a
source /opt/npbb/env/.env.production
set +a

docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml exec -T db \
  pg_restore --clean --if-exists --no-owner --no-privileges \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  < /opt/npbb/backups/postgres/incoming/npbb_final.dump
```

## 4) Reaplicar migrations no schema restaurado

```bash
cd /opt/npbb/app
docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml up -d backend
docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml exec -T backend alembic upgrade head
```

## 5) Validar a aplicacao

```bash
cd /opt/npbb/app
./scripts/check_vps_health.sh /opt/npbb/env/.env.production
./scripts/smoke_vps.sh /opt/npbb/env/.env.production
```

## 6) Restore drill nao-destrutivo

Use o script de drill para validar restauracao em ambiente descartavel:

```bash
cd /opt/npbb/app
./scripts/restore_backup_drill.sh /opt/npbb/env/.env.production
```

O script:
- escolhe o dump mais recente em `/opt/npbb/backups/archive/daily` ou `/opt/npbb/backups/postgres/daily`;
- sobe um projeto Docker temporario com apenas `db`;
- executa `pg_restore` no ambiente descartavel;
- valida que o schema publico foi restaurado;
- roda o smoke da stack ativa;
- grava evidencia em `artifacts/phase-f4/evidence/backup-drill.json`.

## 7) Rollback rapido antes da reabertura

Se o restore falhar antes da liberacao para usuarios:
- mantenha a infraestrutura antiga ativa;
- nao troque DNS;
- descarte o ambiente temporario do drill ou o volume restaurado apenas se tiver certeza de que o ambiente antigo continua sendo a fonte de verdade.

Nao use rollback destrutivo apos reabrir escrita sem um novo dump do banco mais recente.
