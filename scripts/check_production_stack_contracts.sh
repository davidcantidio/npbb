#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_EXAMPLE_FILE="${ROOT_DIR}/Infra/production/.env.example"
COMPOSE_FILE="${ROOT_DIR}/Infra/production/docker-compose.yml"
INIT_SCRIPT="${ROOT_DIR}/Infra/production/scripts/init-vps.sh"
DEPLOY_SCRIPT="${ROOT_DIR}/scripts/deploy_vps.sh"
SMOKE_SCRIPT="${ROOT_DIR}/scripts/smoke_vps.sh"
DOC_FILE="${ROOT_DIR}/docs/DEPLOY_HOSTINGER_VPS.md"
NGINX_RENDER_SCRIPT="${ROOT_DIR}/Infra/production/nginx/render.sh"
IP_TEMPLATE_FILE="${ROOT_DIR}/Infra/production/nginx/conf.d/ip.conf.template"
BACKUP_DOCKERFILE="${ROOT_DIR}/Infra/production/backup/Dockerfile"

fail() {
  echo "[prod-stack] FAIL: $*" >&2
  exit 1
}

assert_file() {
  local path="$1"
  [[ -f "${path}" ]] || fail "arquivo obrigatorio ausente: ${path}"
}

assert_doc_contains() {
  local pattern="$1"
  grep -Fq "${pattern}" "${DOC_FILE}" || fail "documentacao nao contem: ${pattern}"
}

assert_env_declares() {
  local name="$1"
  grep -Eq "^${name}=" "${ENV_EXAMPLE_FILE}" || fail ".env.example nao declara ${name}"
}

extract_service_block() {
  local service="$1"
  awk -v header="  ${service}:" '
    $0 == header {in_service=1; next}
    in_service && /^  [A-Za-z0-9_-]+:/ {exit}
    in_service && /^[A-Za-z0-9_-]+:/ {exit}
    in_service {print}
  ' "${COMPOSE_FILE}"
}

assert_service_setting() {
  local service="$1"
  local snippet="$2"
  local block
  block="$(extract_service_block "${service}")"
  grep -Fq "${snippet}" <<<"${block}" || fail "servico ${service} nao contem '${snippet}'"
}

assert_service_exists() {
  local service="$1"
  grep -Eq "^  ${service}:" "${COMPOSE_FILE}" || fail "docker-compose nao define o servico ${service}"
}

detect_stack_contract() {
  local services
  services="$(
    awk '
      /^services:/ {in_services=1; next}
      in_services && /^[^[:space:]]/ {in_services=0}
      in_services && /^  [A-Za-z0-9_-]+:/ {
        sub(/^  /, "", $0)
        sub(/:.*/, "", $0)
        print $0
      }
    ' "${COMPOSE_FILE}" | sort | xargs
  )"
  case "${services}" in
    "backend backup db nginx")
      STACK_CONTRACT="current"
      STACK_SERVICES=(db backend nginx backup)
      ;;
    "api backup edge postgres web")
      STACK_CONTRACT="legacy"
      STACK_SERVICES=(postgres api web edge backup)
      ;;
    *)
      fail "contrato de servicos inesperado: ${services}"
      ;;
  esac
}

assert_file "${ENV_EXAMPLE_FILE}"
assert_file "${COMPOSE_FILE}"
assert_file "${INIT_SCRIPT}"
assert_file "${DEPLOY_SCRIPT}"
assert_file "${SMOKE_SCRIPT}"
assert_file "${DOC_FILE}"
assert_file "${NGINX_RENDER_SCRIPT}"
assert_file "${IP_TEMPLATE_FILE}"
assert_file "${BACKUP_DOCKERFILE}"

[[ -x "${INIT_SCRIPT}" ]] || fail "script nao executavel: ${INIT_SCRIPT}"
[[ -x "${DEPLOY_SCRIPT}" ]] || fail "script nao executavel: ${DEPLOY_SCRIPT}"
[[ -x "${SMOKE_SCRIPT}" ]] || fail "script nao executavel: ${SMOKE_SCRIPT}"

detect_stack_contract

if [[ "${STACK_CONTRACT}" == "current" ]]; then
  for var in \
    DEPLOY_MODE \
    ENABLE_TLS \
    PUBLIC_HOST \
    APP_DOMAIN \
    VITE_API_BASE_URL \
    FRONTEND_ORIGIN \
    PUBLIC_APP_BASE_URL \
    PUBLIC_LANDING_BASE_URL \
    PUBLIC_API_DOC_URL \
    PASSWORD_RESET_URL \
    API_ROOT_PATH \
    FRONTEND_DIST_DIR \
    EDGE_HTTP_PORT \
    EDGE_HTTPS_PORT \
    CERTS_DIR \
    TLS_CERT_PATH \
    TLS_KEY_PATH \
    POSTGRES_USER \
    POSTGRES_PASSWORD \
    POSTGRES_DB \
    DATABASE_URL \
    DIRECT_URL \
    SECRET_KEY \
    ACCESS_TOKEN_EXPIRE_MINUTES \
    COOKIE_SECURE \
    ENV \
    SQL_ECHO \
    EMAIL_BACKEND \
    SMTP_HOST \
    SMTP_PORT \
    SMTP_USER \
    SMTP_PASSWORD \
    SMTP_FROM \
    SMTP_TLS \
    SMTP_SSL \
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES \
    PASSWORD_RESET_TOKEN_SECRET \
    PASSWORD_RESET_DEBUG \
    SEED_PASSWORD \
    USER_REGISTRATION_MODE \
    USER_REGISTRATION_INVITE_TOKEN \
    USER_REGISTRATION_RATE_LIMIT_MAX \
    USER_REGISTRATION_RATE_LIMIT_WINDOW_SEC \
    FORGOT_PASSWORD_RATE_LIMIT_MAX \
    FORGOT_PASSWORD_RATE_LIMIT_WINDOW_SEC \
    BACKUP_HOST_DIR \
    BACKUP_EXTERNAL_HOST_DIR \
    BACKUP_FILE_PREFIX \
    BACKUP_DAILY_RETENTION \
    BACKUP_WEEKLY_RETENTION \
    BACKUP_WEEKLY_DAY \
    BACKUP_SCHEDULE \
    TZ \
    SMOKE_LOGIN_EMAIL \
    SMOKE_LOGIN_PASSWORD
  do
    assert_env_declares "${var}"
  done
else
  for var in \
    DEPLOY_MODE \
    ENABLE_TLS \
    PUBLIC_HOST \
    APP_DOMAIN \
    API_DOMAIN \
    VITE_API_BASE_URL \
    FRONTEND_ORIGIN \
    PUBLIC_APP_BASE_URL \
    PUBLIC_LANDING_BASE_URL \
    PUBLIC_API_DOC_URL \
    PASSWORD_RESET_URL \
    API_ROOT_PATH \
    EDGE_HTTP_PORT \
    EDGE_HTTPS_PORT \
    CERTS_DIR \
    TLS_CERT_PATH \
    TLS_KEY_PATH \
    POSTGRES_USER \
    POSTGRES_PASSWORD \
    POSTGRES_DB \
    DATABASE_URL \
    DIRECT_URL \
    SECRET_KEY \
    ACCESS_TOKEN_EXPIRE_MINUTES \
    COOKIE_SECURE \
    ENV \
    SQL_ECHO \
    EMAIL_BACKEND \
    SMTP_HOST \
    SMTP_PORT \
    SMTP_USER \
    SMTP_PASSWORD \
    SMTP_FROM \
    SMTP_TLS \
    SMTP_SSL \
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES \
    PASSWORD_RESET_TOKEN_SECRET \
    PASSWORD_RESET_DEBUG \
    SEED_PASSWORD \
    USER_REGISTRATION_MODE \
    USER_REGISTRATION_INVITE_TOKEN \
    USER_REGISTRATION_RATE_LIMIT_MAX \
    USER_REGISTRATION_RATE_LIMIT_WINDOW_SEC \
    FORGOT_PASSWORD_RATE_LIMIT_MAX \
    FORGOT_PASSWORD_RATE_LIMIT_WINDOW_SEC \
    BACKUP_HOST_DIR \
    BACKUP_FILE_PREFIX \
    BACKUP_RETENTION_DAYS \
    BACKUP_SCHEDULE \
    TZ \
    SMOKE_LOGIN_EMAIL \
    SMOKE_LOGIN_PASSWORD
  do
    assert_env_declares "${var}"
  done
fi

for service in "${STACK_SERVICES[@]}"; do
  assert_service_exists "${service}"
  assert_service_setting "${service}" "restart: unless-stopped"
done

if [[ "${STACK_CONTRACT}" == "current" ]]; then
  assert_service_setting "db" "healthcheck:"
  assert_service_setting "backend" "healthcheck:"
  assert_service_setting "nginx" "healthcheck:"
  assert_service_setting "backup" "BACKUP_EXTERNAL_DIR: /archive"
else
  assert_service_setting "postgres" "healthcheck:"
  assert_service_setting "api" "healthcheck:"
  assert_service_setting "edge" "healthcheck:"
fi

grep -Eq '^HEALTHCHECK\b' "${BACKUP_DOCKERFILE}" || fail "backup Dockerfile sem HEALTHCHECK"
grep -Fq 'DEPLOY_MODE:-ip' "${NGINX_RENDER_SCRIPT}" || fail "render.sh nao assume modo ip por padrao"
grep -Fq 'ip.conf.template' "${NGINX_RENDER_SCRIPT}" || fail "render.sh nao renderiza ip.conf.template"

grep -Fq -- '--check-only' "${DEPLOY_SCRIPT}" || fail "deploy_vps.sh nao suporta --check-only"
grep -Fq 'Preflight OK:' "${DEPLOY_SCRIPT}" || fail "deploy_vps.sh nao emite resultado de preflight"
grep -Fq 'assert_service_healthy' "${SMOKE_SCRIPT}" || fail "smoke_vps.sh nao valida saude dos containers"
grep -Fq 'docker inspect' "${SMOKE_SCRIPT}" || fail "smoke_vps.sh nao usa docker inspect para saude"

assert_doc_contains 'bash /root/npbb-bootstrap/Infra/production/scripts/init-vps.sh'
assert_doc_contains './scripts/deploy_vps.sh --check-only /opt/npbb/env/.env.production'
assert_doc_contains './scripts/smoke_vps.sh /opt/npbb/env/.env.production'
assert_doc_contains 'authorized_keys'
assert_doc_contains 'fail2ban'
assert_doc_contains 'Nao use root como fluxo normal de deploy ou operacao.'

echo "[prod-stack] OK"
