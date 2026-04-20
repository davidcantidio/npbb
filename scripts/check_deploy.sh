#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if ! command -v rg >/dev/null 2>&1; then
  echo "[deploy] FAIL: ripgrep (rg) is required but was not found in PATH."
  exit 1
fi

echo "[deploy] checking tracked Wrangler artifacts..."
wrangler_files="$(
  git ls-files | while read -r path; do
    [[ -e "${path}" ]] && echo "${path}"
  done | rg '(^|/)\.wrangler/' || true
)"
if [[ -n "${wrangler_files}" ]]; then
  echo "[deploy] FAIL: tracked .wrangler artifacts found:"
  echo "${wrangler_files}"
  exit 1
fi

echo "[deploy] checking deploy documentation..."
if [[ ! -f "${ROOT_DIR}/docs/DEPLOY_RENDER_CLOUDFLARE.md" ]]; then
  echo "[deploy] FAIL: docs/DEPLOY_RENDER_CLOUDFLARE.md is required."
  exit 1
fi
if [[ ! -f "${ROOT_DIR}/docs/render.yaml" ]]; then
  echo "[deploy] FAIL: docs/render.yaml is required (referencia para Render)."
  exit 1
fi

echo "[deploy] checking leads import runtime gates in Render blueprints..."
for blueprint in render.yaml docs/render.yaml; do
  if ! rg -q 'python scripts/verify_leads_runtime_env.py --service api' "${ROOT_DIR}/${blueprint}"; then
    echo "[deploy] FAIL: ${blueprint} must run verify_leads_runtime_env.py before API startup."
    exit 1
  fi
  if ! rg -q 'python scripts/verify_leads_runtime_env.py --service worker' "${ROOT_DIR}/${blueprint}"; then
    echo "[deploy] FAIL: ${blueprint} must run verify_leads_runtime_env.py before worker startup."
    exit 1
  fi
  if ! rg -q 'name: npbb-leads-worker' "${ROOT_DIR}/${blueprint}"; then
    echo "[deploy] FAIL: ${blueprint} must declare the dedicated leads worker."
    exit 1
  fi
  if [[ "$(rg -c 'value: supabase' "${ROOT_DIR}/${blueprint}")" -lt 2 ]]; then
    echo "[deploy] FAIL: ${blueprint} must pin OBJECT_STORAGE_BACKEND=supabase for API and worker."
    exit 1
  fi
done

echo "[deploy] OK"
