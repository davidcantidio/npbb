#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PYTHON_BIN="${REPO_ROOT}/backend/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "Erro: ${PYTHON_BIN} nao encontrado. Crie a venv em backend/.venv e instale as dependencias." >&2
  exit 1
fi

export PYTHONPATH="${REPO_ROOT}:${REPO_ROOT}/backend${PYTHONPATH:+:${PYTHONPATH}}"
cd "${REPO_ROOT}"

exec "${PYTHON_BIN}" -m uvicorn app.main:app --reload --app-dir backend --host "${UVICORN_HOST:-127.0.0.1}" --port "${UVICORN_PORT:-8000}"
