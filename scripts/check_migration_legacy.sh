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

echo "[legacy] checking render.yaml is archived..."
if [[ -e "${ROOT_DIR}/render.yaml" ]]; then
  echo "[legacy] FAIL: render.yaml must not exist at repository root."
  exit 1
fi
if [[ ! -f "${ROOT_DIR}/docs/legacy/render.yaml" ]]; then
  echo "[legacy] FAIL: archived docs/legacy/render.yaml is required."
  exit 1
fi
if [[ ! -f "${ROOT_DIR}/docs/legacy/DEPLOY_RENDER_CLOUDFLARE.md" ]]; then
  echo "[legacy] FAIL: archived docs/legacy/DEPLOY_RENDER_CLOUDFLARE.md is required."
  exit 1
fi

echo "[legacy] checking legacy deploy references outside docs/legacy..."
reference_hits="$(
  rg -n \
    --glob '!docs/legacy/**' \
    --glob '!docs/_archive/**' \
    --glob '!PROJETOS/**' \
    --glob '!deep-research-report.md' \
    --glob '!scripts/check_migration_legacy.sh' \
    'SUPABASE_|pages\.dev|onrender\.com' \
    README.MD docs .github scripts Infra backend frontend || true
)"
if [[ -n "${reference_hits}" ]]; then
  echo "[legacy] FAIL: forbidden legacy references found outside docs/legacy:"
  echo "${reference_hits}"
  exit 1
fi

echo "[legacy] OK"
