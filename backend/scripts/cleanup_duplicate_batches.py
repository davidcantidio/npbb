"""Clean duplicate lead batches for a single event.

Usage:
  cd backend
  python -m scripts.cleanup_duplicate_batches --evento-id 85
  python -m scripts.cleanup_duplicate_batches --evento-id 85 --apply

By default the script runs in dry-run mode and rolls back all changes.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from sqlalchemy import bindparam, text
from sqlmodel import Session

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.seed_common import get_engine_for_scripts, load_env  # noqa: E402


LIST_EVENT_SQL = text(
    """
    SELECT id, nome
    FROM evento
    WHERE id = :evento_id
    """
)

LIST_BATCHES_SQL = text(
    """
    SELECT id, evento_id, created_at, nome_arquivo_original, stage, pipeline_status
    FROM lead_batches
    WHERE evento_id = :evento_id
    ORDER BY created_at ASC, id ASC
    """
)

UNLINK_LEADS_SQL = text(
    """
    UPDATE lead
    SET batch_id = NULL
    WHERE batch_id IN :batch_ids
    """
).bindparams(bindparam("batch_ids", expanding=True))

DELETE_SILVER_SQL = text(
    """
    DELETE FROM leads_silver
    WHERE batch_id IN :batch_ids
    """
).bindparams(bindparam("batch_ids", expanding=True))

DELETE_BATCHES_SQL = text(
    """
    DELETE FROM lead_batches
    WHERE id IN :batch_ids
    """
).bindparams(bindparam("batch_ids", expanding=True))


@dataclass(frozen=True)
class BatchInfo:
    id: int
    evento_id: int | None
    created_at: Any
    nome_arquivo_original: str | None
    stage: str | None
    pipeline_status: str | None


@dataclass(frozen=True)
class CleanupResult:
    evento_id: int
    evento_nome: str | None
    apply: bool
    batches_found: list[BatchInfo]
    kept_batch: BatchInfo | None
    removed_batches: list[BatchInfo]
    leads_unlinked: int
    silver_deleted: int
    batches_deleted: int

    @property
    def status_label(self) -> str:
        return "APPLY" if self.apply else "DRY-RUN"

    @property
    def changed(self) -> bool:
        return bool(self.removed_batches)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Limpa batches duplicados de um evento mantendo o batch mais antigo."
    )
    parser.add_argument(
        "--evento-id",
        type=int,
        required=True,
        help="ID do evento que tera os batches avaliados.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Persiste as alteracoes. Sem essa flag o script roda em dry-run.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def _to_batch_info(row: Any) -> BatchInfo:
    return BatchInfo(
        id=int(row["id"]),
        evento_id=int(row["evento_id"]) if row["evento_id"] is not None else None,
        created_at=row["created_at"],
        nome_arquivo_original=row["nome_arquivo_original"],
        stage=str(row["stage"]) if row["stage"] is not None else None,
        pipeline_status=str(row["pipeline_status"]) if row["pipeline_status"] is not None else None,
    )


def _format_datetime(value: Any) -> str:
    if value is None:
        return "-"
    isoformat = getattr(value, "isoformat", None)
    if callable(isoformat):
        return isoformat()
    return str(value)


def _print_batch(prefix: str, label: str, batch: BatchInfo) -> None:
    print(
        f"{prefix} {label}: "
        f"id={batch.id} created_at={_format_datetime(batch.created_at)} "
        f"arquivo={batch.nome_arquivo_original!r} stage={batch.stage} "
        f"pipeline_status={batch.pipeline_status}"
    )


def cleanup_duplicate_batches_for_event(
    session: Session,
    *,
    evento_id: int,
    apply: bool,
) -> CleanupResult:
    event_row = session.execute(LIST_EVENT_SQL, {"evento_id": evento_id}).mappings().first()
    if event_row is None:
        raise ValueError(f"Evento {evento_id} nao encontrado.")

    batch_rows = session.execute(LIST_BATCHES_SQL, {"evento_id": evento_id}).mappings().all()
    batches = [_to_batch_info(row) for row in batch_rows]
    if len(batches) <= 1:
        kept = batches[0] if batches else None
        return CleanupResult(
            evento_id=evento_id,
            evento_nome=event_row["nome"],
            apply=apply,
            batches_found=batches,
            kept_batch=kept,
            removed_batches=[],
            leads_unlinked=0,
            silver_deleted=0,
            batches_deleted=0,
        )

    kept_batch = batches[0]
    removed_batches = batches[1:]
    batch_ids = [batch.id for batch in removed_batches]

    try:
        leads_result = session.execute(UNLINK_LEADS_SQL, {"batch_ids": batch_ids})
        silver_result = session.execute(DELETE_SILVER_SQL, {"batch_ids": batch_ids})
        batches_result = session.execute(DELETE_BATCHES_SQL, {"batch_ids": batch_ids})

        leads_unlinked = int(leads_result.rowcount or 0)
        silver_deleted = int(silver_result.rowcount or 0)
        batches_deleted = int(batches_result.rowcount or 0)

        if apply:
            session.commit()
        else:
            session.rollback()
    except Exception:
        session.rollback()
        raise

    return CleanupResult(
        evento_id=evento_id,
        evento_nome=event_row["nome"],
        apply=apply,
        batches_found=batches,
        kept_batch=kept_batch,
        removed_batches=removed_batches,
        leads_unlinked=leads_unlinked,
        silver_deleted=silver_deleted,
        batches_deleted=batches_deleted,
    )


def print_report(result: CleanupResult) -> None:
    prefix = f"[{result.status_label}]"
    evento_nome = result.evento_nome or "(sem nome)"

    print(f"{prefix} Evento: id={result.evento_id} nome={evento_nome!r}")
    print(f"{prefix} Batches encontrados: {len(result.batches_found)}")

    for batch in result.batches_found:
        _print_batch(prefix, "Batch", batch)

    if not result.changed:
        print(f"{prefix} Nenhuma limpeza necessaria.")
        return

    if result.kept_batch is not None:
        _print_batch(prefix, "Mantido", result.kept_batch)

    for batch in result.removed_batches:
        _print_batch(prefix, "Removido", batch)

    print(f"{prefix} Leads desvinculados: {result.leads_unlinked}")
    print(f"{prefix} Leads silver removidos: {result.silver_deleted}")
    print(f"{prefix} Lead batches removidos: {result.batches_deleted}")

    if result.apply:
        print(f"{prefix} Alteracoes persistidas com sucesso.")
    else:
        print(f"{prefix} Nenhuma alteracao foi persistida. Execute com --apply para aplicar.")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.evento_id <= 0:
        print("evento_id deve ser maior que zero.", file=sys.stderr)
        return 1

    load_env()
    engine = get_engine_for_scripts()

    try:
        with Session(engine) as session:
            result = cleanup_duplicate_batches_for_event(
                session,
                evento_id=args.evento_id,
                apply=bool(args.apply),
            )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print_report(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
