#!/bin/sh
set -eu

: "${BACKUP_SCHEDULE:=0 2 * * *}"
: "${BACKUP_DIR:=/backups}"

mkdir -p "${BACKUP_DIR}" "${BACKUP_DIR}/incoming"
envsubst '${BACKUP_SCHEDULE}' < /etc/cron.template > /etc/crontabs/root

echo "[backup] cron schedule: ${BACKUP_SCHEDULE}"
crond -f -l 2
