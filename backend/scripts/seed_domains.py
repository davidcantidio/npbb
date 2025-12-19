"""
Seed somente de tabelas de dominio (lookup tables) para desenvolvimento.

Uso:
  cd backend
  python scripts/seed_domains.py

Observacao:
  - Prefere `DIRECT_URL` quando disponivel (Supabase, porta 5432).
"""

from __future__ import annotations

import sys
from pathlib import Path

from sqlmodel import Session

# Garante que o pacote app/scripts seja encontrado quando o script eh executado fora do diretoria `backend/`.
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.seed_common import (
    get_engine_for_scripts,
    ensure_agencias,
    ensure_diretorias,
    ensure_divisoes_demandantes,
    ensure_status_evento,
    ensure_tipos_subtipos_evento,
    ensure_territorios,
    ensure_tags,
)


def main() -> None:
    engine = get_engine_for_scripts()
    with Session(engine) as session:
        ensure_agencias(session)
        ensure_diretorias(session)
        ensure_divisoes_demandantes(session)
        ensure_status_evento(session)
        ensure_tipos_subtipos_evento(session)
        ensure_territorios(session)
        ensure_tags(session)

    print("Seed de dominios concluido com sucesso.")


if __name__ == "__main__":
    main()
