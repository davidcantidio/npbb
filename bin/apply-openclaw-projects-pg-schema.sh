#!/usr/bin/env bash
# Aplica schema_postgres.sql ao Postgres local (read model OpenClaw).
# Requer: psql no PATH, extensão pgvector instalada no servidor.
#
# Uso (raiz do repo):
#   export OPENCLAW_PROJECTS_DATABASE_URL='postgresql://user:pass@localhost:5432/openclaw_projects'
#   ./bin/apply-openclaw-projects-pg-schema.sh
#
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
sql_file="${repo_root}/scripts/openclaw_projects_index/schema_postgres.sql"

if [[ -z "${OPENCLAW_PROJECTS_DATABASE_URL:-}" ]]; then
  echo "OPENCLAW_PROJECTS_DATABASE_URL não definido (URL Postgres completa)." >&2
  exit 1
fi

if [[ ! -f "$sql_file" ]]; then
  echo "Ficheiro em falta: $sql_file" >&2
  exit 1
fi

exec psql "${OPENCLAW_PROJECTS_DATABASE_URL}" -v ON_ERROR_STOP=1 -f "$sql_file"
