"""Validate that no ativacao URLs still point to localhost.

Pre-requisitos:
- Executar a partir de `backend/`.
- Configurar `DIRECT_URL` ou `DATABASE_URL` para acesso ao banco alvo.

Uso:
- `python -m scripts.validate_no_localhost_urls`
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from sqlalchemy import or_
from sqlmodel import Session, select

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.models.models import Ativacao  # noqa: E402
from scripts.seed_common import get_engine_for_scripts  # noqa: E402

LOCALHOST_TOKENS = ("localhost", "127.0.0.1")


@dataclass(frozen=True)
class AtivacaoUrlViolation:
    ativacao_id: int
    landing_url: str | None
    url_promotor: str | None


@dataclass(frozen=True)
class ValidationSummary:
    total_violations: int
    sample: list[AtivacaoUrlViolation]


def build_localhost_predicate():
    clauses = []
    for token in LOCALHOST_TOKENS:
        clauses.append(Ativacao.landing_url.contains(token))
        clauses.append(Ativacao.url_promotor.contains(token))
    return or_(*clauses)


def find_ativacoes_with_local_urls(
    session: Session, *, limit: int | None = None
) -> list[Ativacao]:
    statement = select(Ativacao).where(build_localhost_predicate()).order_by(Ativacao.id)
    if limit is not None:
        statement = statement.limit(limit)
    return list(session.exec(statement).all())


def collect_validation_summary(
    session: Session, *, sample_limit: int = 10
) -> ValidationSummary:
    offenders = find_ativacoes_with_local_urls(session)
    sample = [
        AtivacaoUrlViolation(
            ativacao_id=ativacao.id,
            landing_url=ativacao.landing_url,
            url_promotor=ativacao.url_promotor,
        )
        for ativacao in offenders[:sample_limit]
        if ativacao.id is not None
    ]
    return ValidationSummary(total_violations=len(offenders), sample=sample)


def assert_no_localhost_urls(session: Session, *, sample_limit: int = 10) -> ValidationSummary:
    summary = collect_validation_summary(session, sample_limit=sample_limit)
    if summary.total_violations:
        raise AssertionError(build_failure_message(summary))
    return summary


def build_failure_message(summary: ValidationSummary) -> str:
    lines = [
        "Validacao falhou: existem registros em `ativacao` com localhost ou 127.0.0.1.",
        f"Total de registros incorretos: {summary.total_violations}.",
    ]
    if summary.sample:
        lines.append("Amostra de registros afetados:")
        for item in summary.sample:
            lines.append(
                f"- ativacao_id={item.ativacao_id} "
                f"landing_url={item.landing_url or '<vazio>'} "
                f"url_promotor={item.url_promotor or '<vazio>'}"
            )
    lines.append(
        "Corrija os registros via migracao antes de prosseguir com a validacao pos-migracao."
    )
    return "\n".join(lines)


def print_success_message() -> None:
    print("Validacao concluida: zero registros com localhost ou 127.0.0.1 em `ativacao`.")


def main(argv: Sequence[str] | None = None) -> int:
    if argv not in (None, []):
        raise SystemExit("Este comando nao aceita argumentos.")

    engine = get_engine_for_scripts()
    with Session(engine) as session:
        try:
            assert_no_localhost_urls(session)
        except AssertionError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    print_success_message()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
