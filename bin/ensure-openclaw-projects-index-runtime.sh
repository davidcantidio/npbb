#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="${OPENCLAW_REPO_ROOT:-$(cd "${script_dir}/.." && pwd)}"
requirements_file="${repo_root}/scripts/openclaw_projects_index/requirements.txt"
wheelhouse_dir="${repo_root}/.openclaw/projects-index-wheelhouse"

if [[ ! -f "$requirements_file" ]]; then
  echo "[ERROR] Missing requirements file: $requirements_file" >&2
  exit 1
fi

python_bin="$(command -v python3 || true)"
if [[ -z "$python_bin" ]]; then
  echo "[ERROR] python3 not found on PATH" >&2
  exit 1
fi

pinned_yaml_version="$(
  awk -F'==' '/^PyYAML==/ { print $2; exit }' "$requirements_file"
)"
if [[ -z "$pinned_yaml_version" ]]; then
  echo "[ERROR] Could not resolve pinned PyYAML version from $requirements_file" >&2
  exit 1
fi

current_yaml_version() {
  "$python_bin" - <<'PY'
try:
    import yaml
except Exception:
    raise SystemExit(1)

print(getattr(yaml, "__version__", "unknown"))
PY
}

if ! "$python_bin" -m pip --version >/dev/null 2>&1; then
  "$python_bin" -m ensurepip --upgrade >/dev/null
fi

pip_install_args=(--disable-pip-version-check)
if [[ -d "$wheelhouse_dir" ]] && find "$wheelhouse_dir" -maxdepth 1 -type f -name '*.whl' | grep -q .; then
  echo "[INFO] Using local wheelhouse at $wheelhouse_dir"
  pip_install_args+=(--no-index --find-links "$wheelhouse_dir")
fi

yaml_version=""
if yaml_version="$(current_yaml_version 2>/dev/null)"; then
  if [[ "$yaml_version" != "$pinned_yaml_version" ]]; then
    echo "[INFO] Adjusting PyYAML version from ${yaml_version} to ${pinned_yaml_version}"
    "$python_bin" -m pip install "${pip_install_args[@]}" --requirement "$requirements_file"
    yaml_version="$(current_yaml_version)"
  fi
else
  echo "[INFO] Installing index runtime requirements with $python_bin"
  "$python_bin" -m pip install "${pip_install_args[@]}" --requirement "$requirements_file"
  yaml_version="$(current_yaml_version)"
fi

if [[ "$yaml_version" != "$pinned_yaml_version" ]]; then
  echo "[ERROR] Expected PyYAML ${pinned_yaml_version}, found ${yaml_version}" >&2
  exit 1
fi

python_version="$("$python_bin" - <<'PY'
import platform
print(platform.python_version())
PY
)"

echo "PYTHON_BIN=$python_bin"
echo "PYTHON_VERSION=$python_version"
echo "PYYAML_VERSION=$yaml_version"
