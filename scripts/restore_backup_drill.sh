#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${ROOT_DIR}/Infra/production/docker-compose.yml"
DEFAULT_ENV_FILE="${ROOT_DIR}/Infra/production/.env.production"
HOST_ENV_FILE="/opt/npbb/env/.env.production"
EVIDENCE_DIR="${PHASE_F4_EVIDENCE_DIR:-${ROOT_DIR}/artifacts/phase-f4/evidence}"

if [[ -f "${HOST_ENV_FILE}" ]]; then
  DEFAULT_ENV_FILE="${HOST_ENV_FILE}"
fi

ENV_FILE="${1:-${DEFAULT_ENV_FILE}}"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Arquivo de ambiente nao encontrado: ${ENV_FILE}" >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker nao encontrado no PATH." >&2
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

mkdir -p "${EVIDENCE_DIR}"

PREFIX="${BACKUP_FILE_PREFIX:-npbb}"
EXTERNAL_DAILY_DIR="${BACKUP_EXTERNAL_HOST_DIR:-/opt/npbb/backups/archive}/daily"
LOCAL_DAILY_DIR="${BACKUP_HOST_DIR:-/opt/npbb/backups/postgres}/daily"
LATEST_DUMP="$(find "${EXTERNAL_DAILY_DIR}" "${LOCAL_DAILY_DIR}" -maxdepth 1 -type f -name "${PREFIX}_*.dump" 2>/dev/null | sort | tail -n 1)"

if [[ -z "${LATEST_DUMP}" ]]; then
  echo "Nenhum dump encontrado para restore drill." >&2
  exit 1
fi

PROJECT="npbb-restore-drill-$(date +%s)"
START_TS="$(date +%s)"

cleanup() {
  docker compose -p "${PROJECT}" --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker compose -p "${PROJECT}" --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" up -d db

for attempt in $(seq 1 30); do
  if docker compose -p "${PROJECT}" --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" exec -T db \
    pg_isready -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" >/dev/null 2>&1; then
    break
  fi
  if [[ "${attempt}" -eq 30 ]]; then
    echo "Banco temporario nao ficou pronto para restore drill." >&2
    exit 1
  fi
  sleep 2
done

docker compose -p "${PROJECT}" --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" exec -T db \
  pg_restore --clean --if-exists --no-owner --no-privileges \
  -U "${POSTGRES_USER}" \
  -d "${POSTGRES_DB}" \
  < "${LATEST_DUMP}"

table_count="$(
  docker compose -p "${PROJECT}" --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" exec -T db \
    psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -Atc \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
)"

if [[ "${table_count}" == "0" ]]; then
  echo "Restore drill nao restaurou tabelas no ambiente temporario." >&2
  exit 1
fi

"${ROOT_DIR}/scripts/smoke_vps.sh" "${ENV_FILE}"

DURATION_SEC="$(( $(date +%s) - START_TS ))"
if [[ "${DURATION_SEC}" -gt 1800 ]]; then
  echo "Restore drill excedeu 30 minutos (${DURATION_SEC}s)." >&2
  exit 1
fi

python3 - "${EVIDENCE_DIR}/backup-drill.json" "${LATEST_DUMP}" "${table_count}" "${DURATION_SEC}" <<'PY'
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

payload = {
    "status": "PASS",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "latest_dump": sys.argv[2],
    "restored_public_tables": int(sys.argv[3]),
    "duration_seconds": int(sys.argv[4]),
}

Path(sys.argv[1]).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY

echo "Restore drill concluido em ${DURATION_SEC}s usando ${LATEST_DUMP}"
