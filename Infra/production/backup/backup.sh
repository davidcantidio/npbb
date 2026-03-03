#!/bin/sh
set -eu

: "${PGHOST:?PGHOST is required}"
: "${PGDATABASE:?PGDATABASE is required}"
: "${PGUSER:?PGUSER is required}"
: "${PGPASSWORD:?PGPASSWORD is required}"

BACKUP_DIR="${BACKUP_DIR:-/backups}"
BACKUP_FILE_PREFIX="${BACKUP_FILE_PREFIX:-npbb}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
TMP_FILE="${BACKUP_DIR}/${BACKUP_FILE_PREFIX}_${TIMESTAMP}.dump.tmp"
FINAL_FILE="${BACKUP_DIR}/${BACKUP_FILE_PREFIX}_${TIMESTAMP}.dump"

mkdir -p "${BACKUP_DIR}" "${BACKUP_DIR}/incoming"
export PGPASSWORD

pg_dump \
  --format=custom \
  --no-owner \
  --no-privileges \
  --host "${PGHOST}" \
  --port "${PGPORT:-5432}" \
  --username "${PGUSER}" \
  --dbname "${PGDATABASE}" \
  --file "${TMP_FILE}"

mv "${TMP_FILE}" "${FINAL_FILE}"

find "${BACKUP_DIR}" \
  -maxdepth 1 \
  -type f \
  -name "${BACKUP_FILE_PREFIX}_*.dump" \
  -mtime +"${BACKUP_RETENTION_DAYS}" \
  -print \
  -delete

echo "[backup] created ${FINAL_FILE}"
