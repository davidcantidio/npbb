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

set -a
source "${ENV_FILE}"
set +a

if ! command -v curl >/dev/null 2>&1; then
  echo "curl nao encontrado no PATH." >&2
  exit 1
fi
if ! command -v docker >/dev/null 2>&1; then
  echo "docker nao encontrado no PATH." >&2
  exit 1
fi

mkdir -p "${EVIDENCE_DIR}"

FRONTEND_URL="${PUBLIC_APP_BASE_URL%/}"
API_BASE_URL="${VITE_API_BASE_URL%/}"
DOCS_URL="${PUBLIC_API_DOC_URL}"
PROBE_FILE="$(mktemp)"
RUN_STATUS="PASS"
LOGIN_STATUS="skipped"
AUTH_SKIPPED="true"

cleanup() {
  rm -f "${PROBE_FILE}"
}
trap cleanup EXIT

write_evidence() {
  python3 - "${PROBE_FILE}" "${EVIDENCE_DIR}/smoke.json" "${RUN_STATUS}" "${LOGIN_STATUS}" "${AUTH_SKIPPED}" <<'PY'
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

probe_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])
status = sys.argv[3]
login_status = sys.argv[4]
auth_skipped = sys.argv[5] == "true"

probes = []
if probe_path.exists():
    with probe_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(
            handle,
            fieldnames=("kind", "url", "status_code", "latency_s", "detail"),
            delimiter="\t",
        )
        probes = list(reader)

payload = {
    "status": status,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "login_status": login_status,
    "authenticated_checks_skipped": auth_skipped,
    "probes": probes,
}
output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY
}

fail() {
  RUN_STATUS="FAIL"
  write_evidence
  echo "$1" >&2
  exit 1
}

docker_compose() {
  docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" "$@"
}

detect_service_contract() {
  local services
  services="$(docker_compose config --services | sort | xargs)"
  case "${services}" in
    "backend backup db nginx")
      SMOKE_SERVICES=(db backend nginx backup)
      ;;
    "api backup edge postgres web")
      SMOKE_SERVICES=(postgres api web edge backup)
      ;;
    *)
      fail "Contrato de servicos nao suportado para smoke: ${services}"
      ;;
  esac
}

record_probe() {
  printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" >> "${PROBE_FILE}"
}

assert_service_healthy() {
  local service="$1"
  local container_id
  local state
  local health

  container_id="$(docker_compose ps -q "${service}")"
  if [[ -z "${container_id}" ]]; then
    record_probe "container" "${service}" "missing" "0" "container-not-found"
    fail "Falha: servico ${service} nao possui container ativo."
  fi

  state="$(docker inspect --format '{{.State.Status}}' "${container_id}")"
  health="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "${container_id}")"
  record_probe "container" "${service}" "${state}" "0" "health=${health}"

  if [[ "${state}" != "running" ]]; then
    fail "Falha: servico ${service} esta em estado ${state}, esperado running."
  fi
  if [[ "${health}" != "healthy" ]]; then
    fail "Falha: servico ${service} esta com health ${health}, esperado healthy."
  fi
}

http_code_time() {
  curl -k -sS -o /dev/null -w "%{http_code} %{time_total}" "$1"
}

assert_code() {
  local url="$1"
  local expected="$2"
  local got latency
  read -r got latency <<<"$(http_code_time "${url}")"
  record_probe "code" "${url}" "${got}" "${latency}" "expected=${expected}"
  if [[ "${got}" != "${expected}" ]]; then
    fail "Falha: ${url} retornou ${got}, esperado ${expected}"
  fi
  echo "OK ${url} -> ${got} (${latency}s)"
}

assert_contains() {
  local url="$1"
  local pattern="$2"
  local body
  body="$(curl -k -fsS "${url}")"
  record_probe "contains" "${url}" "200" "0" "pattern=${pattern}"
  if ! grep -q "${pattern}" <<<"${body}"; then
    fail "Falha: ${url} nao contem o padrao esperado: ${pattern}"
  fi
  echo "OK ${url} contem ${pattern}"
}

detect_service_contract
for service in "${SMOKE_SERVICES[@]}"; do
  assert_service_healthy "${service}"
done

assert_code "${API_BASE_URL}/health" "200"
assert_code "${DOCS_URL}" "200"
assert_contains "${DOCS_URL}" "Swagger UI"
assert_code "${FRONTEND_URL}/" "200"
assert_contains "${FRONTEND_URL}/" "id=\"root\""
assert_code "${FRONTEND_URL}/eventos" "200"
assert_contains "${FRONTEND_URL}/eventos" "id=\"root\""

LOGIN_STATUS="$(curl -k -sS -o /dev/null -w "%{http_code}" \
  -H 'Content-Type: application/json' \
  -d '{"email":"smoke@example.com","password":"wrong-pass"}' \
  "${API_BASE_URL}/auth/login")"
record_probe "auth" "${API_BASE_URL}/auth/login" "${LOGIN_STATUS}" "0" "invalid-credentials"

if [[ "${LOGIN_STATUS}" != "401" && "${LOGIN_STATUS}" != "422" ]]; then
  fail "Falha: endpoint /auth/login retornou ${LOGIN_STATUS} para credenciais invalidas."
fi
echo "OK ${API_BASE_URL}/auth/login responde (${LOGIN_STATUS})"

if [[ -z "${SMOKE_LOGIN_EMAIL:-}" || -z "${SMOKE_LOGIN_PASSWORD:-}" ]]; then
  AUTH_SKIPPED="true"
  RUN_STATUS="PASS"
  write_evidence
  echo "SMOKE_LOGIN_EMAIL/SMOKE_LOGIN_PASSWORD nao configurados; checks autenticados foram pulados."
  exit 0
fi

AUTH_SKIPPED="false"
TMP_DIR="$(mktemp -d)"
tmp_cleanup() {
  rm -rf "${TMP_DIR}"
}
trap 'tmp_cleanup; cleanup' EXIT

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
  local got latency
  read -r got latency <<<"$(
    curl -k -sS -o /dev/null -w "%{http_code} %{time_total}" \
      -H "${auth_header}" \
      "$url"
  )"
  record_probe "auth-code" "${url}" "${got}" "${latency}" "expected=${expected}"
  if [[ "${got}" != "${expected}" ]]; then
    fail "Falha: ${url} retornou ${got}, esperado ${expected}"
  fi
  echo "OK ${url} -> ${got} (${latency}s)"
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
record_probe "upload" "${API_BASE_URL}/leads/import/upload" "${upload_code}" "0" "csv"
if [[ "${upload_code}" != "200" ]]; then
  fail "Falha: upload CSV de leads retornou ${upload_code}"
fi
echo "OK upload CSV de leads"

upload_code="$(
  curl -k -sS -o /dev/null -w "%{http_code}" \
    -H "${auth_header}" \
    -F "file=@${TMP_DIR}/leads.xlsx;type=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
    "${API_BASE_URL}/leads/import/upload"
)"
record_probe "upload" "${API_BASE_URL}/leads/import/upload" "${upload_code}" "0" "xlsx"
if [[ "${upload_code}" != "200" ]]; then
  fail "Falha: upload XLSX de leads retornou ${upload_code}"
fi
echo "OK upload XLSX de leads"

upload_code="$(
  curl -k -sS -o /dev/null -w "%{http_code}" \
    -H "${auth_header}" \
    -F "file=@${TMP_DIR}/publicidade.csv;type=text/csv" \
    "${API_BASE_URL}/publicidade/import/upload"
)"
record_probe "upload" "${API_BASE_URL}/publicidade/import/upload" "${upload_code}" "0" "publicidade-csv"
if [[ "${upload_code}" != "200" ]]; then
  fail "Falha: upload CSV de publicidade retornou ${upload_code}"
fi
echo "OK upload CSV de publicidade"

RUN_STATUS="PASS"
write_evidence
