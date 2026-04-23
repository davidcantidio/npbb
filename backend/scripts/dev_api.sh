#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd -- "${BACKEND_DIR}/.." && pwd)"
PYTHON_BIN="${BACKEND_DIR}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "Erro: ${PYTHON_BIN} nao encontrado. Crie a venv com Python 3.12 e instale as dependencias." >&2
  exit 1
fi

PY_VERSION="$("${PYTHON_BIN}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if [[ "${PY_VERSION}" != "3.12" ]]; then
  echo "Erro: venv em Python ${PY_VERSION}. Esperado Python 3.12." >&2
  exit 1
fi

export PYTHONPATH="${REPO_ROOT}:${BACKEND_DIR}:${REPO_ROOT}/PROJETOS${PYTHONPATH:+:${PYTHONPATH}}"
cd "${BACKEND_DIR}"

reload_excludes=(
  "backend/alembic/versions/*"
)

uvicorn_args=(
  -m uvicorn
  app.main:app
  --reload
  --host "${UVICORN_HOST:-127.0.0.1}"
  --port "${UVICORN_PORT:-8000}"
)

for pattern in "${reload_excludes[@]}"; do
  uvicorn_args+=(--reload-exclude "${pattern}")
done

exec "${PYTHON_BIN}" "${uvicorn_args[@]}"
