#!/usr/bin/env bash
set -euo pipefail

echo "[hygiene] checking tracked runtime/cache artifacts..."

violations="$(
  git ls-files | while read -r path; do
    [[ -e "${path}" ]] && echo "${path}"
  done | rg '(^|/)node_modules/|(^|/)__pycache__/|(^|/)\.wrangler/|\.pyc$|^backend/app\.db$|^localhost\.har$|^issues\.zip$|^reports/.*\.docx$' || true
)"

if [[ -n "$violations" ]]; then
  echo "[hygiene] FAIL: tracked artifacts found:"
  echo "$violations"
  exit 1
fi

echo "[hygiene] checking legacy normalize helper is absent..."
legacy_helper_file="backend/app/utils/lead_import_normalize.py"
if [[ -e "$legacy_helper_file" ]]; then
  echo "[hygiene] FAIL: legacy helper should not exist: $legacy_helper_file"
  exit 1
fi

echo "[hygiene] OK"
