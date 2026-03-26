#!/usr/bin/env bash
# Espelha o índice SQLite v4 para Postgres (requer schema aplicado e psycopg).
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
export OPENCLAW_REPO_ROOT="${OPENCLAW_REPO_ROOT:-$repo_root}"
exec python3 "$repo_root/scripts/openclaw_projects_index/mirror_sqlite_to_postgres.py" "$@"
