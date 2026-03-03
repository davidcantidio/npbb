#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${ROOT_DIR}/Infra/production/docker-compose.yml"
DEFAULT_ENV_FILE="${ROOT_DIR}/Infra/production/.env.production"
HOST_ENV_FILE="/opt/npbb/env/.env.production"

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

require_var() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "Variavel obrigatoria ausente no env: ${name}" >&2
    exit 1
  fi
}

require_var POSTGRES_USER
require_var POSTGRES_PASSWORD
require_var POSTGRES_DB
require_var DATABASE_URL
require_var DIRECT_URL
require_var SECRET_KEY
require_var FRONTEND_ORIGIN
require_var PUBLIC_APP_BASE_URL
require_var PUBLIC_LANDING_BASE_URL
require_var PUBLIC_API_DOC_URL
require_var PASSWORD_RESET_URL
require_var PASSWORD_RESET_TOKEN_SECRET
require_var VITE_API_BASE_URL

if [[ "${EMAIL_BACKEND:-console}" == "smtp" ]]; then
  require_var SMTP_HOST
  require_var SMTP_PORT
  require_var SMTP_USER
  require_var SMTP_PASSWORD
  require_var SMTP_FROM
fi

if [[ "${DEPLOY_MODE:-ip}" == "domain" ]]; then
  require_var APP_DOMAIN
  require_var API_DOMAIN
fi

mkdir -p "${BACKUP_HOST_DIR:-/opt/npbb/backups/postgres}"
mkdir -p "${BACKUP_HOST_DIR:-/opt/npbb/backups/postgres}/incoming"
mkdir -p "${CERTS_DIR:-/opt/npbb/certs}"

if [[ "${ENABLE_TLS:-false}" == "true" ]]; then
  cert_host_path="${CERTS_DIR:-/opt/npbb/certs}/$(basename "${TLS_CERT_PATH:-/etc/nginx/certs/origin.crt}")"
  key_host_path="${CERTS_DIR:-/opt/npbb/certs}/$(basename "${TLS_KEY_PATH:-/etc/nginx/certs/origin.key}")"
  if [[ ! -f "${cert_host_path}" || ! -f "${key_host_path}" ]]; then
    echo "TLS habilitado, mas os certificados nao foram encontrados em ${CERTS_DIR:-/opt/npbb/certs}." >&2
    exit 1
  fi
fi

docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" config >/dev/null

docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" build api web edge
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" up -d postgres api web edge backup

echo
echo "Containers ativos:"
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" ps

echo
echo "Health URLs:"
if [[ "${DEPLOY_MODE:-ip}" == "ip" ]]; then
  echo "Frontend: ${PUBLIC_APP_BASE_URL%/}/"
  echo "API health: ${VITE_API_BASE_URL%/}/health"
  echo "API docs: ${PUBLIC_API_DOC_URL}"
else
  scheme="http"
  if [[ "${ENABLE_TLS:-false}" == "true" ]]; then
    scheme="https"
  fi
  echo "Frontend: ${scheme}://${APP_DOMAIN}/"
  echo "API health: ${scheme}://${API_DOMAIN}/health"
  echo "API docs: ${PUBLIC_API_DOC_URL}"
fi
