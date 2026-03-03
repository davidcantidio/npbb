#!/usr/bin/env bash
set -euo pipefail

echo "[guard] checking forbidden sys.path.insert usage in backend/app..."
if rg -n "sys\.path\.insert\(" backend/app >/dev/null; then
  echo "[guard] FAIL: sys.path.insert found in backend/app"
  rg -n "sys\.path\.insert\(" backend/app
  exit 1
fi

echo "[guard] checking internal routers are role-guarded..."
internal_routers=$(rg --files backend/app/routers | while read -r file; do
  if rg -n 'prefix\s*=\s*"/internal' "$file" >/dev/null; then
    echo "$file"
  fi
done)

fail=0
while read -r router; do
  [[ -z "$router" ]] && continue
  if ! rg -n "require_npbb_user|require_internal_user" "$router" >/dev/null; then
    echo "[guard] FAIL: missing internal authz dependency in $router"
    fail=1
  fi
done <<<"$internal_routers"

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi

echo "[guard] OK"
