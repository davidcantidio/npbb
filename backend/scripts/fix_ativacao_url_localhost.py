"""Fix persisted ativacao URLs that still point to localhost."""

from __future__ import annotations

import argparse
import os
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
from app.services.qr_code import build_qr_code_data_url  # noqa: E402
from app.utils.urls import build_ativacao_public_urls  # noqa: E402
from scripts.seed_common import get_engine_for_scripts, load_env  # noqa: E402

LOCALHOST_TOKENS = ("localhost", "127.0.0.1")


@dataclass(frozen=True)
class AtivacaoUrlUpdate:
    ativacao_id: int
    old_landing_url: str | None
    new_landing_url: str
    old_url_promotor: str | None
    new_url_promotor: str
    old_qr_code_url: str | None
    new_qr_code_url: str


@dataclass(frozen=True)
class FixSummary:
    public_app_base_url: str
    candidates: int
    updates: int
    dry_run: bool


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Corrige registros de ativacao com URLs locais persistidas."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Calcula e valida as alteracoes sem persistir commit.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def require_public_app_base_url() -> str:
    load_env()
    value = (os.getenv("PUBLIC_APP_BASE_URL") or "").strip().rstrip("/")
    if not value:
        raise RuntimeError("PUBLIC_APP_BASE_URL precisa estar configurada para executar o script.")
    return value


def build_localhost_predicate():
    clauses = []
    for token in LOCALHOST_TOKENS:
        clauses.append(Ativacao.landing_url.contains(token))
        clauses.append(Ativacao.url_promotor.contains(token))
    return or_(*clauses)


def find_ativacoes_with_local_urls(session: Session) -> list[Ativacao]:
    statement = (
        select(Ativacao)
        .where(build_localhost_predicate())
        .order_by(Ativacao.id)
    )
    return list(session.exec(statement).all())


def build_update_plan(ativacoes: Sequence[Ativacao]) -> list[AtivacaoUrlUpdate]:
    updates: list[AtivacaoUrlUpdate] = []
    for ativacao in ativacoes:
        if ativacao.id is None:
            raise RuntimeError("Ativacao sem ID nao pode ser migrada.")

        urls = build_ativacao_public_urls(ativacao.id)
        landing_url = urls["landing_url"]
        url_promotor = urls["url_promotor"]
        qr_code_url = build_qr_code_data_url(landing_url)

        if (
            ativacao.landing_url == landing_url
            and ativacao.url_promotor == url_promotor
            and ativacao.qr_code_url == qr_code_url
        ):
            continue

        updates.append(
            AtivacaoUrlUpdate(
                ativacao_id=ativacao.id,
                old_landing_url=ativacao.landing_url,
                new_landing_url=landing_url,
                old_url_promotor=ativacao.url_promotor,
                new_url_promotor=url_promotor,
                old_qr_code_url=ativacao.qr_code_url,
                new_qr_code_url=qr_code_url,
            )
        )
    return updates


def apply_updates(
    session: Session, updates: Sequence[AtivacaoUrlUpdate], *, dry_run: bool
) -> int:
    if not updates:
        return 0

    update_by_id = {update.ativacao_id: update for update in updates}
    statement = select(Ativacao).where(Ativacao.id.in_(list(update_by_id)))
    ativacoes = list(session.exec(statement).all())

    try:
        for ativacao in ativacoes:
            if ativacao.id is None:
                raise RuntimeError("Ativacao sem ID nao pode ser atualizada.")
            update = update_by_id[ativacao.id]
            ativacao.landing_url = update.new_landing_url
            ativacao.url_promotor = update.new_url_promotor
            ativacao.qr_code_url = update.new_qr_code_url
            session.add(ativacao)

        if dry_run:
            session.flush()
            session.rollback()
            return len(updates)

        session.commit()
        return len(updates)
    except Exception:
        session.rollback()
        raise


def execute_fix(session: Session, *, dry_run: bool) -> tuple[FixSummary, list[AtivacaoUrlUpdate]]:
    public_app_base_url = require_public_app_base_url()
    ativacoes = find_ativacoes_with_local_urls(session)
    updates = build_update_plan(ativacoes)
    applied = apply_updates(session, updates, dry_run=dry_run)
    return (
        FixSummary(
            public_app_base_url=public_app_base_url,
            candidates=len(ativacoes),
            updates=applied,
            dry_run=dry_run,
        ),
        updates,
    )


def print_updates(updates: Sequence[AtivacaoUrlUpdate], *, dry_run: bool) -> None:
    prefix = "[DRY-RUN]" if dry_run else "[APPLY]"
    if not updates:
        print(f"{prefix} Nenhum registro pendente.")
        return

    for update in updates:
        print(f"{prefix} ativacao_id={update.ativacao_id}")
        print(f"  landing_url: {update.old_landing_url or '<vazio>'} -> {update.new_landing_url}")
        print(f"  url_promotor: {update.old_url_promotor or '<vazio>'} -> {update.new_url_promotor}")
        qr_changed = update.old_qr_code_url != update.new_qr_code_url
        print(f"  qr_code_url recalculado: {'sim' if qr_changed else 'nao'}")


def print_summary(summary: FixSummary) -> None:
    mode = "DRY-RUN" if summary.dry_run else "EXECUCAO"
    print(f"{mode}: PUBLIC_APP_BASE_URL={summary.public_app_base_url}")
    print(f"Registros elegiveis: {summary.candidates}")
    print(f"Registros processados: {summary.updates}")
    if summary.dry_run:
        print("Nenhuma alteracao foi persistida.")
    else:
        print("Alteracoes persistidas com sucesso.")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    engine = get_engine_for_scripts()

    with Session(engine) as session:
        summary, updates = execute_fix(session, dry_run=args.dry_run)

    print_updates(updates, dry_run=args.dry_run)
    print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
