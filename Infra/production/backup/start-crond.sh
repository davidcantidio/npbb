#!/bin/sh
set -eu

: "${BACKUP_SCHEDULE:=0 2 * * *}"
: "${BACKUP_DIR:=/backups}"
: "${BACKUP_EXTERNAL_DIR:=/archive}"

mkdir -p "${BACKUP_DIR}" "${BACKUP_DIR}/incoming" "${BACKUP_EXTERNAL_DIR}"
envsubst '${BACKUP_SCHEDULE}' < /etc/cron.template > /etc/crontabs/root

echo "[backup] cron schedule: ${BACKUP_SCHEDULE}"
crond -f -l 2
