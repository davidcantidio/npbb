#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${REPO_ROOT}/backend/.venv"
BACKEND_ENV="${REPO_ROOT}/backend/.env"
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

if [[ ! -f "${BACKEND_ENV}" ]]; then
  echo "Erro: backend/.env nao encontrado. Copie backend/.env.example para backend/.env e preencha DATABASE_URL/DIRECT_URL." >&2
  exit 1
fi

if ! grep -Eq '^[[:space:]]*DATABASE_URL[[:space:]]*=[[:space:]]*[^[:space:]#"]|^[[:space:]]*DATABASE_URL[[:space:]]*=[[:space:]]*"[^"]+"' "${BACKEND_ENV}"; then
  echo "Erro: DATABASE_URL em backend/.env esta ausente ou vazia." >&2
  exit 1
fi

PY_VERSION="$("${PYTHON_BIN}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if [[ "${PY_VERSION}" != "3.12" ]]; then
  echo "Erro: venv em Python ${PY_VERSION}. Esperado Python 3.12." >&2
  exit 1
fi

export PYTHONPATH="${REPO_ROOT}:${REPO_ROOT}/backend${PYTHONPATH:+:${PYTHONPATH}}"
cd "${REPO_ROOT}"

echo "Backend Python: ${PYTHON_BIN}"
exec "${PYTHON_BIN}" -m uvicorn app.main:app --reload --app-dir backend --host "${UVICORN_HOST:-127.0.0.1}" --port "${UVICORN_PORT:-8000}"
