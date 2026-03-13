#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if ! command -v rg >/dev/null 2>&1; then
  echo "[legacy] FAIL: ripgrep (rg) is required but was not found in PATH."
  exit 1
fi

echo "[legacy] checking tracked Wrangler artifacts..."
wrangler_files="$(
  git ls-files | while read -r path; do
    [[ -e "${path}" ]] && echo "${path}"
  done | rg '(^|/)\.wrangler/' || true
)"
if [[ -n "${wrangler_files}" ]]; then
  echo "[legacy] FAIL: tracked .wrangler artifacts found:"
  echo "${wrangler_files}"
  exit 1
fi

echo "[legacy] checking deploy documentation..."
if [[ ! -f "${ROOT_DIR}/docs/DEPLOY_RENDER_CLOUDFLARE.md" ]]; then
  echo "[legacy] FAIL: docs/DEPLOY_RENDER_CLOUDFLARE.md is required."
  exit 1
fi
if [[ ! -f "${ROOT_DIR}/docs/legacy/render.yaml" ]]; then
  echo "[legacy] FAIL: docs/legacy/render.yaml is required (referencia para Render)."
  exit 1
fi

echo "[legacy] OK"
