#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${REPO_ROOT}/backend/.venv"
PYTHON_BIN=""

if [[ -x "${VENV_DIR}/bin/python" ]]; then
  PYTHON_BIN="${VENV_DIR}/bin/python"
elif [[ -f "${VENV_DIR}/Scripts/python.exe" ]]; then
  PYTHON_BIN="${VENV_DIR}/Scripts/python.exe"
fi

if [[ -z "${PYTHON_BIN}" ]]; then
  echo "Erro: venv em ${VENV_DIR} nao encontrada (esperado bin/python ou Scripts/python.exe)." >&2
  echo "Crie a venv em backend/.venv e instale as dependencias." >&2
  exit 1
fi

export PYTHONPATH="${REPO_ROOT}:${REPO_ROOT}/backend${PYTHONPATH:+:${PYTHONPATH}}"
cd "${REPO_ROOT}"

exec "${PYTHON_BIN}" -m uvicorn app.main:app --reload --app-dir backend --host "${UVICORN_HOST:-127.0.0.1}" --port "${UVICORN_PORT:-8000}"
