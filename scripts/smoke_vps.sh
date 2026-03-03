#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
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

set -a
source "${ENV_FILE}"
set +a

if ! command -v curl >/dev/null 2>&1; then
  echo "curl nao encontrado no PATH." >&2
  exit 1
fi

FRONTEND_URL="${PUBLIC_APP_BASE_URL%/}"
API_BASE_URL="${VITE_API_BASE_URL%/}"
DOCS_URL="${PUBLIC_API_DOC_URL}"

http_code() {
  curl -k -sS -o /dev/null -w "%{http_code}" "$1"
}

assert_code() {
  local url="$1"
  local expected="$2"
  local got
  got="$(http_code "${url}")"
  if [[ "${got}" != "${expected}" ]]; then
    echo "Falha: ${url} retornou ${got}, esperado ${expected}" >&2
    exit 1
  fi
  echo "OK ${url} -> ${got}"
}

assert_contains() {
  local url="$1"
  local pattern="$2"
  local body
  body="$(curl -k -fsS "${url}")"
  if ! grep -q "${pattern}" <<<"${body}"; then
    echo "Falha: ${url} nao contem o padrao esperado: ${pattern}" >&2
    exit 1
  fi
  echo "OK ${url} contem ${pattern}"
}

assert_code "${API_BASE_URL}/health" "200"
assert_code "${DOCS_URL}" "200"
assert_contains "${DOCS_URL}" "Swagger UI"
assert_code "${FRONTEND_URL}/" "200"
assert_contains "${FRONTEND_URL}/" "id=\"root\""
assert_code "${FRONTEND_URL}/eventos" "200"
assert_contains "${FRONTEND_URL}/eventos" "id=\"root\""

login_status="$(curl -k -sS -o /dev/null -w "%{http_code}" \
  -H 'Content-Type: application/json' \
  -d '{"email":"smoke@example.com","password":"wrong-pass"}' \
  "${API_BASE_URL}/auth/login")"

if [[ "${login_status}" != "401" && "${login_status}" != "422" ]]; then
  echo "Falha: endpoint /auth/login retornou ${login_status} para credenciais invalidas." >&2
  exit 1
fi
echo "OK ${API_BASE_URL}/auth/login responde (${login_status})"

if [[ -z "${SMOKE_LOGIN_EMAIL:-}" || -z "${SMOKE_LOGIN_PASSWORD:-}" ]]; then
  echo "SMOKE_LOGIN_EMAIL/SMOKE_LOGIN_PASSWORD nao configurados; checks autenticados foram pulados."
  exit 0
fi

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

printf 'nome,email\nSmoke,smoke@example.com\n' > "${TMP_DIR}/leads.csv"
printf 'placeholder xlsx' > "${TMP_DIR}/leads.xlsx"
printf 'evento,codigo\nSmoke,ABC123\n' > "${TMP_DIR}/publicidade.csv"

login_response="$(
  curl -k -fsS \
    -H 'Content-Type: application/json' \
    -d "{\"email\":\"${SMOKE_LOGIN_EMAIL}\",\"password\":\"${SMOKE_LOGIN_PASSWORD}\"}" \
    "${API_BASE_URL}/auth/login"
)"

token="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])' <<<"${login_response}")"

auth_header="Authorization: Bearer ${token}"

assert_code_with_auth() {
  local url="$1"
  local expected="$2"
  local got
  got="$(
    curl -k -sS -o /dev/null -w "%{http_code}" \
      -H "${auth_header}" \
      "$url"
  )"
  if [[ "${got}" != "${expected}" ]]; then
    echo "Falha: ${url} retornou ${got}, esperado ${expected}" >&2
    exit 1
  fi
  echo "OK ${url} -> ${got}"
}

assert_code_with_auth "${API_BASE_URL}/auth/me" "200"
assert_code_with_auth "${API_BASE_URL}/eventos" "200"
assert_code_with_auth "${API_BASE_URL}/dashboard/leads" "200"

upload_code="$(
  curl -k -sS -o /dev/null -w "%{http_code}" \
    -H "${auth_header}" \
    -F "file=@${TMP_DIR}/leads.csv;type=text/csv" \
    "${API_BASE_URL}/leads/import/upload"
)"
if [[ "${upload_code}" != "200" ]]; then
  echo "Falha: upload CSV de leads retornou ${upload_code}" >&2
  exit 1
fi
echo "OK upload CSV de leads"

upload_code="$(
  curl -k -sS -o /dev/null -w "%{http_code}" \
    -H "${auth_header}" \
    -F "file=@${TMP_DIR}/leads.xlsx;type=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
    "${API_BASE_URL}/leads/import/upload"
)"
if [[ "${upload_code}" != "200" ]]; then
  echo "Falha: upload XLSX de leads retornou ${upload_code}" >&2
  exit 1
fi
echo "OK upload XLSX de leads"

upload_code="$(
  curl -k -sS -o /dev/null -w "%{http_code}" \
    -H "${auth_header}" \
    -F "file=@${TMP_DIR}/publicidade.csv;type=text/csv" \
    "${API_BASE_URL}/publicidade/import/upload"
)"
if [[ "${upload_code}" != "200" ]]; then
  echo "Falha: upload CSV de publicidade retornou ${upload_code}" >&2
  exit 1
fi
echo "OK upload CSV de publicidade"
