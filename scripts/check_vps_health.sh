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

mkdir -p "${EVIDENCE_DIR}"

PS_JSON="$(mktemp)"
cleanup() {
  rm -f "${PS_JSON}"
}
trap cleanup EXIT

docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" ps --format json > "${PS_JSON}"

python3 - "${PS_JSON}" "${EVIDENCE_DIR}/health.json" <<'PY'
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

required = {"backend", "db", "nginx", "backup"}
payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
services = {}
for item in payload:
    service_name = item.get("Service") or item.get("Name")
    if service_name:
        services[service_name] = {
            "name": item.get("Name"),
            "state": item.get("State"),
            "health": item.get("Health"),
        }

missing = sorted(required - services.keys())
unhealthy = sorted(
    service
    for service in required & services.keys()
    if services[service].get("state") != "running" or services[service].get("health") not in {None, "", "healthy"}
)

if missing or unhealthy:
    if missing:
        print(f"[health] FAIL: missing services: {', '.join(missing)}", file=sys.stderr)
    if unhealthy:
        print(f"[health] FAIL: unhealthy services: {', '.join(unhealthy)}", file=sys.stderr)
    raise SystemExit(1)

result = {
    "status": "PASS",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "services": {name: services[name] for name in sorted(required)},
}
Path(sys.argv[2]).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
PY

echo "[health] OK"
