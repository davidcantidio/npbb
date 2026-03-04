#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${ROOT_DIR}/frontend/dist"
FORBIDDEN="http://localhost:8000"

if [[ ! -d "${DIST_DIR}" ]]; then
  echo "[frontend-api-base] FAIL: build directory not found: ${DIST_DIR}" >&2
  exit 1
fi

if rg -n --fixed-strings "${FORBIDDEN}" "${DIST_DIR}" >/dev/null; then
  echo "[frontend-api-base] FAIL: forbidden API base found in bundle: ${FORBIDDEN}" >&2
  rg -n --fixed-strings "${FORBIDDEN}" "${DIST_DIR}" || true
  exit 1
fi

echo "[frontend-api-base] OK: bundle does not contain ${FORBIDDEN}"
