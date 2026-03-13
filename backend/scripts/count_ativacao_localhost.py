"""Count ativacao rows with local URLs persisted in the database.

Usage:
  cd backend
  python -m scripts.count_ativacao_localhost
"""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import func, or_
from sqlmodel import Session, select

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.models.models import Ativacao  # noqa: E402
from scripts.seed_common import get_engine_for_scripts  # noqa: E402

LOCALHOST_TOKENS = ("localhost", "127.0.0.1")


def _build_localhost_predicate():
    clauses = []
    for token in LOCALHOST_TOKENS:
        clauses.append(Ativacao.landing_url.contains(token))
        clauses.append(Ativacao.url_promotor.contains(token))
    return or_(*clauses)


def count_ativacoes_with_local_urls(session: Session) -> int:
    statement = select(func.count(func.distinct(Ativacao.id))).where(
        _build_localhost_predicate()
    )
    result = session.exec(statement).one()
    return int(result or 0)


def main() -> None:
    engine = get_engine_for_scripts()
    with Session(engine) as session:
        total = count_ativacoes_with_local_urls(session)

    print(f"Ativacoes com URL local persistida: {total}")
    print("Filtro: landing_url ou url_promotor contendo localhost ou 127.0.0.1.")


if __name__ == "__main__":
    main()
