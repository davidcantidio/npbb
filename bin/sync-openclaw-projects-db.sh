#!/usr/bin/env bash
# Reconstrói o índice derivado de PROJETOS/ (fonte de verdade = Markdown no Git).
# Default: SQLite. Para Postgres: OPENCLAW_PROJECTS_DATABASE_URL + pip install -r scripts/openclaw_projects_index/requirements.txt
# e ./bin/sync-openclaw-projects-db.sh -- --backend postgres
# Uso: a partir da raiz do repo: ./bin/sync-openclaw-projects-db.sh [-- args para sync.py]

set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
export OPENCLAW_REPO_ROOT="${OPENCLAW_REPO_ROOT:-$repo_root}"
exec python3 "$repo_root/scripts/openclaw_projects_index/sync.py" "$@"
