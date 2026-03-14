"""Regenera QR codes que estao com placeholder (quadrado amarelo) em vez de QR real.

Identifica ativacoes e eventos cujo qr_code_url contem o SVG placeholder
("QR Code alternativo") e recalcula usando build_qr_code_data_url com a
biblioteca qrcode instalada.

Pre-requisitos:
- Executar a partir de `backend/`.
- Pacote `qrcode` instalado (pip install -r requirements.txt).
- Configurar DIRECT_URL ou DATABASE_URL para acesso ao banco.

Uso:
- Dry-run: `python -m scripts.regenerar_qr_codes_placeholder --dry-run`
- Execucao real: `python -m scripts.regenerar_qr_codes_placeholder`
"""

from __future__ import annotations

import argparse
import base64
import sys
from pathlib import Path
from typing import Sequence

from sqlmodel import Session, select

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.models.models import Ativacao, Evento  # noqa: E402
from app.services.landing_pages import hydrate_ativacao_public_urls, hydrate_evento_public_urls  # noqa: E402
from scripts.seed_common import get_engine_for_scripts, load_env  # noqa: E402

PLACEHOLDER_MARKER = "QR Code alternativo"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Regenera QR codes com placeholder por QR codes reais."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Calcula e valida as alteracoes sem persistir commit.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def is_placeholder_qr(qr_code_url: str | None) -> bool:
    """Retorna True se qr_code_url contem o SVG placeholder."""
    if not qr_code_url or not qr_code_url.startswith("data:image/svg+xml;base64,"):
        return False
    try:
        encoded = qr_code_url.split(",", 1)[1]
        decoded = base64.b64decode(encoded).decode("utf-8")
        return PLACEHOLDER_MARKER in decoded
    except Exception:
        return False


def find_ativacoes_com_placeholder(session: Session) -> list[Ativacao]:
    """Lista ativacoes cujo qr_code_url e o placeholder."""
    ativacoes = list(session.exec(select(Ativacao).order_by(Ativacao.id)).all())
    return [a for a in ativacoes if is_placeholder_qr(a.qr_code_url)]


def find_eventos_precisam_qr(session: Session) -> list[Evento]:
    """Lista eventos com qr_code_url nulo ou placeholder."""
    eventos = list(session.exec(select(Evento).order_by(Evento.id)).all())
    return [
        e
        for e in eventos
        if e.qr_code_url is None or is_placeholder_qr(e.qr_code_url)
    ]


def regenerate_ativacoes(
    session: Session, ativacoes: list[Ativacao], *, dry_run: bool
) -> int:
    """Regenera qr_code_url das ativacoes. Retorna quantidade alterada."""
    changed_count = 0
    for ativacao in ativacoes:
        if hydrate_ativacao_public_urls(ativacao):
            session.add(ativacao)
            changed_count += 1
    if changed_count and not dry_run:
        session.commit()
        for ativacao in ativacoes:
            session.refresh(ativacao)
    elif changed_count and dry_run:
        session.rollback()
    return changed_count


def regenerate_eventos(
    session: Session, eventos: list[Evento], *, dry_run: bool
) -> int:
    """Regenera qr_code_url dos eventos. Retorna quantidade alterada."""
    changed_count = 0
    for evento in eventos:
        if hydrate_evento_public_urls(evento):
            session.add(evento)
            changed_count += 1
    if changed_count and not dry_run:
        session.commit()
        for evento in eventos:
            session.refresh(evento)
    elif changed_count and dry_run:
        session.rollback()
    return changed_count


def main(argv: Sequence[str] | None = None) -> int:
    load_env()
    args = parse_args(argv)
    engine = get_engine_for_scripts()

    with Session(engine) as session:
        ativacoes = find_ativacoes_com_placeholder(session)
        eventos = find_eventos_precisam_qr(session)

        prefix = "[DRY-RUN]" if args.dry_run else "[APPLY]"
        print(f"{prefix} Ativacoes com placeholder: {len(ativacoes)}")
        print(f"{prefix} Eventos sem QR ou com placeholder: {len(eventos)}")

        if not ativacoes and not eventos:
            print("Nenhum registro para regenerar.")
            return 0

        ativacoes_changed = regenerate_ativacoes(
            session, ativacoes, dry_run=args.dry_run
        )
        eventos_changed = regenerate_eventos(
            session, eventos, dry_run=args.dry_run
        )

        print(f"{prefix} Ativacoes regeneradas: {ativacoes_changed}")
        print(f"{prefix} Eventos regenerados: {eventos_changed}")

        if args.dry_run:
            print("Nenhuma alteracao foi persistida. Execute sem --dry-run para aplicar.")
        else:
            print("Alteracoes persistidas com sucesso.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
