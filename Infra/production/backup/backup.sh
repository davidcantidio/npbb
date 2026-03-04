#!/bin/sh
set -eu

: "${PGHOST:?PGHOST is required}"
: "${PGDATABASE:?PGDATABASE is required}"
: "${PGUSER:?PGUSER is required}"
: "${PGPASSWORD:?PGPASSWORD is required}"

BACKUP_DIR="${BACKUP_DIR:-/backups}"
BACKUP_EXTERNAL_DIR="${BACKUP_EXTERNAL_DIR:-/archive}"
BACKUP_FILE_PREFIX="${BACKUP_FILE_PREFIX:-npbb}"
BACKUP_DAILY_RETENTION="${BACKUP_DAILY_RETENTION:-7}"
BACKUP_WEEKLY_RETENTION="${BACKUP_WEEKLY_RETENTION:-4}"
BACKUP_WEEKLY_DAY="${BACKUP_WEEKLY_DAY:-7}"
BACKUP_FORCE_WEEKLY="${BACKUP_FORCE_WEEKLY:-false}"
TIMESTAMP="${BACKUP_TIMESTAMP:-$(date +%Y%m%d_%H%M%S)}"

DAILY_DIR="${BACKUP_DIR}/daily"
WEEKLY_DIR="${BACKUP_DIR}/weekly"
EXTERNAL_DAILY_DIR="${BACKUP_EXTERNAL_DIR}/daily"
EXTERNAL_WEEKLY_DIR="${BACKUP_EXTERNAL_DIR}/weekly"
TMP_FILE="${DAILY_DIR}/${BACKUP_FILE_PREFIX}_${TIMESTAMP}.dump.tmp"
FINAL_FILE="${DAILY_DIR}/${BACKUP_FILE_PREFIX}_${TIMESTAMP}.dump"
CHECKSUM_FILE="${FINAL_FILE}.sha256"

log() {
  echo "[backup] $(date +%Y-%m-%dT%H:%M:%S%z) $*"
}

on_exit() {
  status="$?"
  if [ "${status}" -ne 0 ]; then
    log "failed status=${status} file=${FINAL_FILE:-unknown}"
  fi
}
trap on_exit EXIT

trim_history() {
  dir_path="$1"
  keep_count="$2"

  [ -d "${dir_path}" ] || return 0

  count=0
  find "${dir_path}" -maxdepth 1 -type f -name "${BACKUP_FILE_PREFIX}_*.dump" | sort -r | while read -r dump_file; do
    count=$((count + 1))
    if [ "${count}" -le "${keep_count}" ]; then
      continue
    fi
    rm -f "${dump_file}" "${dump_file}.sha256"
  done
}

mkdir -p "${DAILY_DIR}" "${WEEKLY_DIR}" "${BACKUP_DIR}/incoming"
mkdir -p "${EXTERNAL_DAILY_DIR}" "${EXTERNAL_WEEKLY_DIR}"
export PGPASSWORD

log "starting dump file=${FINAL_FILE}"
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
sha256sum "${FINAL_FILE}" > "${CHECKSUM_FILE}"

cp "${FINAL_FILE}" "${EXTERNAL_DAILY_DIR}/"
cp "${CHECKSUM_FILE}" "${EXTERNAL_DAILY_DIR}/"

weekly_enabled="false"
if [ "${BACKUP_FORCE_WEEKLY}" = "true" ] || [ "$(date +%u)" = "${BACKUP_WEEKLY_DAY}" ]; then
  weekly_enabled="true"
  cp "${FINAL_FILE}" "${WEEKLY_DIR}/"
  cp "${CHECKSUM_FILE}" "${WEEKLY_DIR}/"
  cp "${FINAL_FILE}" "${EXTERNAL_WEEKLY_DIR}/"
  cp "${CHECKSUM_FILE}" "${EXTERNAL_WEEKLY_DIR}/"
fi

trim_history "${DAILY_DIR}" "${BACKUP_DAILY_RETENTION}"
trim_history "${WEEKLY_DIR}" "${BACKUP_WEEKLY_RETENTION}"
trim_history "${EXTERNAL_DAILY_DIR}" "${BACKUP_DAILY_RETENTION}"
trim_history "${EXTERNAL_WEEKLY_DIR}" "${BACKUP_WEEKLY_RETENTION}"

log "completed file=${FINAL_FILE} checksum=${CHECKSUM_FILE} weekly=${weekly_enabled}"
