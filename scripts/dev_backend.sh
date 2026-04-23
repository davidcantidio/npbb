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

WORKER_PID=""
RUNTIME_DIR="${REPO_ROOT}/backend/.runtime"
WORKER_STDOUT="${RUNTIME_DIR}/leads_worker.stdout.log"
WORKER_STDERR="${RUNTIME_DIR}/leads_worker.stderr.log"
START_LEADS_WORKER_VALUE="$(printf '%s' "${START_LEADS_WORKER:-1}" | tr '[:upper:]' '[:lower:]')"

cleanup() {
  local status=$?
  if [[ -n "${WORKER_PID}" ]] && kill -0 "${WORKER_PID}" >/dev/null 2>&1; then
    echo "Encerrando leads worker local (PID ${WORKER_PID})..."
    kill "${WORKER_PID}" >/dev/null 2>&1 || true
    wait "${WORKER_PID}" 2>/dev/null || true
  fi
  exit "${status}"
}

trap cleanup EXIT INT TERM

if [[ "${START_LEADS_WORKER_VALUE}" =~ ^(0|false|no)$ ]]; then
  echo "START_LEADS_WORKER=false: worker local de leads nao sera iniciado."
else
  EXISTING_WORKER_PID=""
  if command -v pgrep >/dev/null 2>&1; then
    EXISTING_WORKER_PID="$(pgrep -f 'backend/scripts/run_leads_worker.py' | head -n 1 || true)"
  fi
  if [[ -n "${EXISTING_WORKER_PID}" ]]; then
    echo "Leads worker ja em execucao (PID ${EXISTING_WORKER_PID})."
  else
    mkdir -p "${RUNTIME_DIR}"
    rm -f "${WORKER_STDOUT}" "${WORKER_STDERR}"
    "${PYTHON_BIN}" backend/scripts/run_leads_worker.py >"${WORKER_STDOUT}" 2>"${WORKER_STDERR}" &
    WORKER_PID=$!
    sleep 2
    if ! kill -0 "${WORKER_PID}" >/dev/null 2>&1; then
      echo "Erro: falha ao iniciar leads worker. Logs: ${WORKER_STDERR}" >&2
      if [[ -f "${WORKER_STDERR}" ]]; then
        tail -n 40 "${WORKER_STDERR}" >&2 || true
      fi
      exit 1
    fi
    echo "Leads worker iniciado em background (PID ${WORKER_PID}). Logs: ${WORKER_STDOUT}"
  fi
fi

# So vigia backend/app (codigo da API); evita reload ao editar Alembic.
uvicorn_args=(
  -m uvicorn
  app.main:app
  --reload
  --reload-dir backend/app
  --app-dir backend
  --host "${UVICORN_HOST:-127.0.0.1}"
  --port "${UVICORN_PORT:-8000}"
)

"${PYTHON_BIN}" "${uvicorn_args[@]}"
