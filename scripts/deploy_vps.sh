#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${ROOT_DIR}/Infra/production/docker-compose.yml"
ENV_EXAMPLE_FILE="${ROOT_DIR}/Infra/production/.env.example"
DEFAULT_ENV_FILE="${ROOT_DIR}/Infra/production/.env.production"
HOST_ENV_FILE="/opt/npbb/env/.env.production"
CHECK_ONLY=false

if [[ -f "${HOST_ENV_FILE}" ]]; then
  DEFAULT_ENV_FILE="${HOST_ENV_FILE}"
fi

usage() {
  cat <<'EOF'
Uso:
  ./scripts/deploy_vps.sh [--check-only] [env_file]
EOF
}

ENV_FILE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --check-only)
      CHECK_ONLY=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [[ -n "${ENV_FILE}" ]]; then
        echo "Apenas um arquivo de ambiente pode ser informado." >&2
        exit 1
      fi
      ENV_FILE="$1"
      ;;
  esac
  shift
done

ENV_FILE="${ENV_FILE:-${DEFAULT_ENV_FILE}}"

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

fail() {
  echo "$*" >&2
  exit 1
}

require_var() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    fail "Variavel obrigatoria ausente no env: ${name}"
  fi
}

ensure_env_example_declares() {
  local name="$1"
  if ! grep -Eq "^${name}=" "${ENV_EXAMPLE_FILE}"; then
    fail "Infra/production/.env.example nao declara ${name}"
  fi
}

docker_compose() {
  docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" "$@"
}

STACK_CONTRACT=""
BUILD_SERVICES=()
UP_SERVICES=()

detect_stack_contract() {
  local services
  services="$(docker_compose config --services | sort | xargs)"
  case "${services}" in
    "backend backup db nginx")
      STACK_CONTRACT="current"
      BUILD_SERVICES=(backend nginx backup)
      UP_SERVICES=(db backend nginx backup)
      ;;
    "api backup edge postgres web")
      STACK_CONTRACT="legacy"
      BUILD_SERVICES=(api web edge backup)
      UP_SERVICES=(postgres api web edge backup)
      ;;
    *)
      fail "Contrato de servicos invalido: ${services}. Esperado current(db/backend/nginx/backup) ou legacy(postgres/api/web/edge/backup)."
      ;;
  esac
}

validate_env_contract() {
  local vars=()
  if [[ "${STACK_CONTRACT}" == "current" ]]; then
    vars=(
      DEPLOY_MODE ENABLE_TLS PUBLIC_HOST APP_DOMAIN VITE_API_BASE_URL FRONTEND_ORIGIN
      PUBLIC_APP_BASE_URL PUBLIC_LANDING_BASE_URL PUBLIC_API_DOC_URL PASSWORD_RESET_URL API_ROOT_PATH
      FRONTEND_DIST_DIR EDGE_HTTP_PORT EDGE_HTTPS_PORT CERTS_DIR TLS_CERT_PATH TLS_KEY_PATH
      POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB DATABASE_URL DIRECT_URL SECRET_KEY
      ACCESS_TOKEN_EXPIRE_MINUTES COOKIE_SECURE ENV SQL_ECHO EMAIL_BACKEND SMTP_HOST SMTP_PORT
      SMTP_USER SMTP_PASSWORD SMTP_FROM SMTP_TLS SMTP_SSL PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
      PASSWORD_RESET_TOKEN_SECRET PASSWORD_RESET_DEBUG SEED_PASSWORD USER_REGISTRATION_MODE
      USER_REGISTRATION_INVITE_TOKEN USER_REGISTRATION_RATE_LIMIT_MAX USER_REGISTRATION_RATE_LIMIT_WINDOW_SEC
      FORGOT_PASSWORD_RATE_LIMIT_MAX FORGOT_PASSWORD_RATE_LIMIT_WINDOW_SEC BACKUP_HOST_DIR
      BACKUP_EXTERNAL_HOST_DIR BACKUP_FILE_PREFIX BACKUP_DAILY_RETENTION BACKUP_WEEKLY_RETENTION
      BACKUP_WEEKLY_DAY BACKUP_SCHEDULE TZ SMOKE_LOGIN_EMAIL SMOKE_LOGIN_PASSWORD
    )
  else
    vars=(
      DEPLOY_MODE ENABLE_TLS PUBLIC_HOST APP_DOMAIN API_DOMAIN VITE_API_BASE_URL FRONTEND_ORIGIN
      PUBLIC_APP_BASE_URL PUBLIC_LANDING_BASE_URL PUBLIC_API_DOC_URL PASSWORD_RESET_URL API_ROOT_PATH
      EDGE_HTTP_PORT EDGE_HTTPS_PORT CERTS_DIR TLS_CERT_PATH TLS_KEY_PATH
      POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB DATABASE_URL DIRECT_URL SECRET_KEY
      ACCESS_TOKEN_EXPIRE_MINUTES COOKIE_SECURE ENV SQL_ECHO EMAIL_BACKEND SMTP_HOST SMTP_PORT
      SMTP_USER SMTP_PASSWORD SMTP_FROM SMTP_TLS SMTP_SSL PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
      PASSWORD_RESET_TOKEN_SECRET PASSWORD_RESET_DEBUG SEED_PASSWORD USER_REGISTRATION_MODE
      USER_REGISTRATION_INVITE_TOKEN USER_REGISTRATION_RATE_LIMIT_MAX USER_REGISTRATION_RATE_LIMIT_WINDOW_SEC
      FORGOT_PASSWORD_RATE_LIMIT_MAX FORGOT_PASSWORD_RATE_LIMIT_WINDOW_SEC BACKUP_HOST_DIR
      BACKUP_FILE_PREFIX BACKUP_RETENTION_DAYS BACKUP_SCHEDULE TZ SMOKE_LOGIN_EMAIL SMOKE_LOGIN_PASSWORD
    )
  fi

  for name in "${vars[@]}"; do
    ensure_env_example_declares "${name}"
  done
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

docker_compose config >/dev/null
detect_stack_contract
validate_env_contract

if [[ "${DEPLOY_MODE:-ip}" == "domain" ]]; then
  require_var APP_DOMAIN
  if [[ "${STACK_CONTRACT}" == "legacy" ]]; then
    require_var API_DOMAIN
  fi
fi

backup_dir="${BACKUP_HOST_DIR:-/opt/npbb/backups/postgres}"
external_backup_dir="${BACKUP_EXTERNAL_HOST_DIR:-/opt/npbb/backups/archive}"
frontend_dist_dir="${FRONTEND_DIST_DIR:-/opt/npbb/app/frontend/dist}"
certs_dir="${CERTS_DIR:-/opt/npbb/certs}"

if [[ "${CHECK_ONLY}" == "true" ]]; then
  [[ -d "${backup_dir}" ]] || fail "Diretorio ausente para preflight: ${backup_dir}"
  if [[ "${STACK_CONTRACT}" == "current" ]]; then
    [[ -d "${external_backup_dir}" ]] || fail "Diretorio ausente para preflight: ${external_backup_dir}"
    [[ -d "${frontend_dist_dir}" ]] || fail "Diretorio ausente para preflight: ${frontend_dist_dir}"
    [[ -f "${frontend_dist_dir%/}/index.html" ]] || fail "Frontend dist ausente em ${frontend_dist_dir}."
  fi
  [[ -d "${certs_dir}" ]] || fail "Diretorio ausente para preflight: ${certs_dir}"
else
  mkdir -p "${backup_dir}"
  mkdir -p "${external_backup_dir}"
  mkdir -p "${frontend_dist_dir}"
  mkdir -p "${certs_dir}"
fi

if [[ "${STACK_CONTRACT}" == "current" && ! -f "${frontend_dist_dir%/}/index.html" ]]; then
  fail "Frontend dist ausente em ${frontend_dist_dir}. Execute o build e sincronize o dist antes do deploy."
fi

if [[ "${ENABLE_TLS:-false}" == "true" ]]; then
  if [[ ! -f "${TLS_CERT_PATH:-}" || ! -f "${TLS_KEY_PATH:-}" ]]; then
    fail "TLS habilitado, mas os certificados nao foram encontrados em ${TLS_CERT_PATH:-} e ${TLS_KEY_PATH:-}."
  fi
fi

if [[ "${CHECK_ONLY}" == "true" ]]; then
  echo "Preflight OK: env, diretorios, contrato da stack e docker compose config validados."
  exit 0
fi

docker_compose build "${BUILD_SERVICES[@]}"
docker_compose up -d "${UP_SERVICES[@]}"

echo
echo "Containers ativos:"
docker_compose ps

echo
echo "Health URLs:"
echo "Frontend: ${PUBLIC_APP_BASE_URL%/}/"
echo "API health: ${VITE_API_BASE_URL%/}/health"
echo "API docs: ${PUBLIC_API_DOC_URL}"
