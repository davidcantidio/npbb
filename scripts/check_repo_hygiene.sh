#!/usr/bin/env bash
set -euo pipefail

echo "[hygiene] checking tracked runtime/cache artifacts..."

violations="$(git ls-files | rg '(^|/)node_modules/|(^|/)__pycache__/|\.pyc$|^backend/app\.db$|^localhost\.har$|^issues\.zip$|^reports/.*\.docx$' || true)"

if [[ -n "$violations" ]]; then
  echo "[hygiene] FAIL: tracked artifacts found:"
  echo "$violations"
  exit 1
fi

echo "[hygiene] OK"
