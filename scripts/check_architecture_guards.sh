#!/usr/bin/env bash
set -euo pipefail

if ! command -v rg >/dev/null 2>&1; then
  echo "[guard] FAIL: ripgrep (rg) is required but was not found in PATH."
  exit 1
fi

echo "[guard] checking forbidden sys.path.insert usage in backend/app..."
if rg -n "sys\.path\.insert\(" backend/app >/dev/null; then
  echo "[guard] FAIL: sys.path.insert found in backend/app"
  rg -n "sys\.path\.insert\(" backend/app
  exit 1
fi

echo "[guard] checking forbidden imports in core/leads_etl..."
core_forbidden_pattern='^\s*(from|import)\s+(fastapi|sqlmodel|app|backend|etl)(\.|\b)'
if rg -n "$core_forbidden_pattern" core/leads_etl >/dev/null; then
  echo "[guard] FAIL: forbidden import found in core/leads_etl"
  rg -n "$core_forbidden_pattern" core/leads_etl
  exit 1
fi

echo "[guard] checking core/leads_etl python modules stay below 200 lines..."
too_long=""
while IFS= read -r file; do
  lines=$(wc -l < "$file")
  lines=${lines//[[:space:]]/}
  if (( lines > 200 )); then
    too_long+="$file:$lines"$'\n'
  fi
done < <(find core/leads_etl -type f -name "*.py" ! -name "__init__.py" | sort)

if [[ -n "$too_long" ]]; then
  echo "[guard] FAIL: core/leads_etl module exceeds 200 lines"
  printf "%s" "$too_long"
  exit 1
fi

echo "[guard] checking migrated legacy wrappers stay thin and delegate to core..."
migrated_wrappers=(
  "etl/transform/column_normalize.py"
  "etl/transform/segment_mapper.py"
  "etl/validate/framework.py"
  "etl/validate/checks_schema.py"
  "etl/validate/checks_not_null.py"
  "etl/validate/checks_duplicates.py"
  "etl/validate/checks_access_control.py"
  "etl/validate/checks_percentages.py"
  "etl/validate/checks_cross_source.py"
  "etl/validate/render_dq_report.py"
)

wrapper_fail=0
for wrapper in "${migrated_wrappers[@]}"; do
  if ! rg -n '^from core\.leads_etl\.' "$wrapper" >/dev/null; then
    echo "[guard] FAIL: migrated wrapper does not delegate to core: $wrapper"
    wrapper_fail=1
  fi

  lines=$(wc -l < "$wrapper")
  lines=${lines//[[:space:]]/}
  if (( lines > 40 )); then
    echo "[guard] FAIL: migrated wrapper grew beyond thin facade budget (40 lines): $wrapper:$lines"
    wrapper_fail=1
  fi
done

if [[ "$wrapper_fail" -ne 0 ]]; then
  exit 1
fi

echo "[guard] checking internal routers are role-guarded..."
internal_routers=$(rg --files backend/app/routers | while read -r file; do
  if rg -n 'prefix\s*=\s*"/internal' "$file" >/dev/null; then
    echo "$file"
  fi
done)

router_fail=0
while read -r router; do
  [[ -z "$router" ]] && continue
  if ! rg -n "require_npbb_user|require_internal_user" "$router" >/dev/null; then
    echo "[guard] FAIL: missing internal authz dependency in $router"
    router_fail=1
  fi
done <<<"$internal_routers"

if [[ "$router_fail" -ne 0 ]]; then
  exit 1
fi

echo "[guard] checking legacy normalize helper was fully removed..."
legacy_helper_file="backend/app/utils/lead_import_normalize.py"
if [[ -e "$legacy_helper_file" ]]; then
  echo "[guard] FAIL: legacy normalize helper must be removed: $legacy_helper_file"
  exit 1
fi

echo "[guard] checking codebase no longer imports legacy normalize helper..."
legacy_imports="$(rg -n 'from app\.utils\.lead_import_normalize import|import app\.utils\.lead_import_normalize' backend tests -g '*.py' || true)"
if [[ -n "$legacy_imports" ]]; then
  echo "[guard] FAIL: legacy normalize helper import reintroduced"
  echo "$legacy_imports"
  exit 1
fi

echo "[guard] checking lead ETL contract coherence..."
PYTHONPATH=. python3 scripts/check_lead_etl_contracts.py

echo "[guard] OK"
