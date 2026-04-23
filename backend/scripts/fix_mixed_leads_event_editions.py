"""Split mixed lead imports across two event editions safely.

Usage:
  cd backend
  python -m scripts.fix_mixed_leads_event_editions --evento-id 4 --input-file "C:\\path\\file.xlsx"
  python -m scripts.fix_mixed_leads_event_editions --evento-id 4 --input-file "C:\\path\\file.xlsx" --apply

The script defaults to dry-run mode and writes a JSON audit artifact for every run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from sqlalchemy import bindparam, text
from sqlmodel import Session, select

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.models.lead_batch import BatchStage, LeadBatch, LeadSilver, PipelineStatus  # noqa: E402
from app.models.lead_public_models import LeadEventoSourceKind, TipoLead, TipoResponsavel  # noqa: E402
from app.models.models import Evento, Lead, LeadEvento  # noqa: E402
from app.services.lead_event_service import _resolve_proponente_nome  # noqa: E402
from scripts.seed_common import get_engine_for_scripts, load_env  # noqa: E402

_GOLD_PIPELINE_STATUSES = {PipelineStatus.PASS, PipelineStatus.PASS_WITH_WARNINGS}
_DEFAULT_OLD_START = date(2025, 2, 5)
_DEFAULT_OLD_END = date(2025, 2, 9)
_ARTIFACT_DIR = Path("artifacts") / "data_fixes"
_JSON_INDENT = 2

LIST_EVENT_BATCHES_SQL = text(
    """
    SELECT
        id,
        evento_id,
        nome_arquivo_original,
        arquivo_sha256,
        stage,
        pipeline_status,
        origem_lote,
        tipo_lead_proponente,
        data_upload,
        created_at,
        updated_at
    FROM lead_batches
    WHERE evento_id = :evento_id
      AND lower(coalesce(arquivo_sha256, '')) = :arquivo_sha256
    ORDER BY id ASC
    """
)

MOVE_BATCH_EVENT_SQL = text(
    """
    UPDATE lead_batches
    SET evento_id = :new_evento_id
    WHERE id IN :batch_ids
    """
).bindparams(bindparam("batch_ids", expanding=True))

MOVE_SILVER_EVENT_SQL = text(
    """
    UPDATE leads_silver
    SET evento_id = :new_evento_id
    WHERE batch_id IN :batch_ids
    """
).bindparams(bindparam("batch_ids", expanding=True))

MOVE_LEAD_EVENT_SQL = text(
    """
    UPDATE lead_evento
    SET evento_id = :new_evento_id
    WHERE id IN :lead_evento_ids
    """
).bindparams(bindparam("lead_evento_ids", expanding=True))


@dataclass(frozen=True)
class BatchRow:
    id: int
    evento_id: int | None
    nome_arquivo_original: str | None
    arquivo_sha256: str | None
    stage: str | None
    pipeline_status: str | None
    origem_lote: str | None
    tipo_lead_proponente: str | None
    data_upload: Any
    created_at: Any
    updated_at: Any


@dataclass(frozen=True)
class LeadEventRow:
    id: int
    lead_id: int
    evento_id: int
    source_ref_id: int | None


@dataclass(frozen=True)
class RepairSummary:
    dry_run: bool
    old_event_id: int
    new_event_id: int | None
    arquivo_sha256: str
    batches_moved: int
    gold_batches: list[int]
    lead_events_moved: int
    restored_old_event_links: int
    ambiguous_leads: list[int]
    validation: dict[str, Any]
    artifact_path: str | None = None


@dataclass(frozen=True)
class RepairSnapshot:
    old_event: dict[str, Any]
    matched_batches: list[dict[str, Any]]
    contaminated_lead_eventos: list[dict[str, Any]]
    restore_batch_ids: list[int]
    ambiguous_lead_ids: list[int]
    old_event_dashboard_before: dict[str, Any] | None


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Separa leads de edicoes diferentes que foram misturados no mesmo evento."
    )
    parser.add_argument("--evento-id", type=int, required=True, help="ID do evento contaminado.")
    parser.add_argument(
        "--input-file",
        type=Path,
        required=True,
        help="Arquivo originalmente importado de forma incorreta no evento.",
    )
    parser.add_argument(
        "--old-start-date",
        type=_parse_date,
        default=_DEFAULT_OLD_START,
        help="Data inicial correta da edicao antiga (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--old-end-date",
        type=_parse_date,
        default=_DEFAULT_OLD_END,
        help="Data final correta da edicao antiga (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--new-start-date",
        type=_parse_date,
        default=None,
        help="Data inicial da nova edicao. Se omitida, usa a data atual do evento antigo.",
    )
    parser.add_argument(
        "--new-end-date",
        type=_parse_date,
        default=None,
        help="Data final da nova edicao. Se omitida, usa a data atual do evento antigo.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=_ARTIFACT_DIR,
        help="Diretorio para gravar o snapshot/auditoria JSON.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Persiste as alteracoes. Sem a flag, executa dry-run e faz rollback.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:  # pragma: no cover - argparse handles the message
        raise argparse.ArgumentTypeError(f"Data invalida: {value!r}. Use YYYY-MM-DD.") from exc


def _hash_file(path: Path) -> str:
    sha256 = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def _to_batch_row(row: Any) -> BatchRow:
    return BatchRow(
        id=int(row["id"]),
        evento_id=int(row["evento_id"]) if row["evento_id"] is not None else None,
        nome_arquivo_original=row["nome_arquivo_original"],
        arquivo_sha256=row["arquivo_sha256"],
        stage=str(row["stage"]) if row["stage"] is not None else None,
        pipeline_status=str(row["pipeline_status"]) if row["pipeline_status"] is not None else None,
        origem_lote=row["origem_lote"],
        tipo_lead_proponente=row["tipo_lead_proponente"],
        data_upload=row["data_upload"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _enum_matches(raw_value: str | None, expected: BatchStage | PipelineStatus) -> bool:
    if raw_value is None:
        return False
    normalized = raw_value.strip().lower()
    return normalized in {expected.value.lower(), expected.name.lower()}


def _event_payload(evento: Evento, *, start_date: date, end_date: date) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for column_name in Evento.__table__.columns.keys():
        if column_name in {"id", "created_at", "updated_at"}:
            continue
        payload[column_name] = getattr(evento, column_name)
    payload["data_inicio_prevista"] = start_date
    payload["data_fim_prevista"] = end_date
    return payload


def _resolve_new_dates(
    evento: Evento,
    *,
    new_start_date: date | None,
    new_end_date: date | None,
) -> tuple[date, date]:
    resolved_start = new_start_date or evento.data_inicio_prevista
    resolved_end = new_end_date or evento.data_fim_prevista
    if resolved_start is None or resolved_end is None:
        raise ValueError(
            "Nao foi possivel inferir as datas da nova edicao. Informe --new-start-date e --new-end-date."
        )
    return resolved_start, resolved_end


def _configure_statement_timeout_for_fix(session: Session) -> None:
    bind = session.get_bind()
    if bind is None or bind.dialect.name != "postgresql":
        return
    session.execute(text("SET LOCAL statement_timeout = 0"))


def _build_event_validation_snapshot(session: Session, *, evento_id: int) -> dict[str, Any]:
    lead_event_rows = session.execute(
        text(
            """
            SELECT
                COUNT(DISTINCT le.lead_id) AS total,
                COUNT(DISTINCT CASE WHEN l.data_nascimento IS NOT NULL THEN le.lead_id END) AS with_birthdate
            FROM lead_evento le
            JOIN lead l ON l.id = le.lead_id
            WHERE le.evento_id = :evento_id
            """
        ),
        {"evento_id": evento_id},
    ).mappings().first()
    batch_rows = session.execute(
        text(
            """
            SELECT
                COUNT(DISTINCT l.id) AS total,
                COUNT(DISTINCT CASE WHEN l.data_nascimento IS NOT NULL THEN l.id END) AS with_birthdate
            FROM lead l
            JOIN lead_batches lb ON lb.id = l.batch_id
            WHERE lb.evento_id = :evento_id
              AND lower(CAST(lb.stage AS TEXT)) IN ('gold')
              AND lower(CAST(lb.pipeline_status AS TEXT)) IN ('pass', 'pass_with_warnings')
            """
        ),
        {"evento_id": evento_id},
    ).mappings().first()
    combined_rows = session.execute(
        text(
            """
            WITH canonical_leads AS (
                SELECT l.id AS lead_id, l.data_nascimento
                FROM lead_evento le
                JOIN lead l ON l.id = le.lead_id
                WHERE le.evento_id = :evento_id
                UNION
                SELECT l.id AS lead_id, l.data_nascimento
                FROM lead l
                JOIN lead_batches lb ON lb.id = l.batch_id
                WHERE lb.evento_id = :evento_id
                  AND lower(CAST(lb.stage AS TEXT)) IN ('gold')
                  AND lower(CAST(lb.pipeline_status AS TEXT)) IN ('pass', 'pass_with_warnings')
            )
            SELECT
                COUNT(DISTINCT lead_id) AS total,
                COUNT(DISTINCT CASE WHEN data_nascimento IS NOT NULL THEN lead_id END) AS with_birthdate
            FROM canonical_leads
            """
        ),
        {"evento_id": evento_id},
    ).mappings().first()
    return {
        "evento_id": evento_id,
        "lead_evento": dict(lead_event_rows or {}),
        "gold_batch": dict(batch_rows or {}),
        "combined_unique": dict(combined_rows or {}),
    }


def _load_matched_batches(
    session: Session,
    *,
    evento_id: int,
    arquivo_sha256: str,
) -> list[BatchRow]:
    rows = session.execute(
        LIST_EVENT_BATCHES_SQL,
        {"evento_id": evento_id, "arquivo_sha256": arquivo_sha256.lower()},
    ).mappings().all()
    return [_to_batch_row(row) for row in rows]


def _load_contaminated_lead_eventos(
    session: Session,
    *,
    old_event_id: int,
    gold_batch_ids: list[int],
) -> list[LeadEventRow]:
    if not gold_batch_ids:
        return []
    rows = session.exec(
        select(LeadEvento)
        .where(LeadEvento.evento_id == old_event_id)
        .where(LeadEvento.source_kind == LeadEventoSourceKind.LEAD_BATCH)
        .where(LeadEvento.source_ref_id.in_(gold_batch_ids))
        .order_by(LeadEvento.id.asc())
    ).all()
    return [
        LeadEventRow(
            id=int(row.id),
            lead_id=int(row.lead_id),
            evento_id=int(row.evento_id),
            source_ref_id=int(row.source_ref_id) if row.source_ref_id is not None else None,
        )
        for row in rows
        if row.id is not None
    ]


def _resolve_restore_batches(
    session: Session,
    *,
    old_event_id: int,
    contaminated_lead_ids: list[int],
    contaminated_batch_ids: set[int],
) -> tuple[dict[int, list[int]], list[int]]:
    if not contaminated_lead_ids:
        return {}, []

    leads = session.exec(
        select(Lead.id, Lead.batch_id)
        .where(Lead.id.in_(contaminated_lead_ids))
        .order_by(Lead.id.asc())
    ).all()
    batch_ids = sorted(
        {
            int(batch_id)
            for _lead_id, batch_id in leads
            if batch_id is not None and int(batch_id) not in contaminated_batch_ids
        }
    )
    batch_map = {
        int(batch.id): batch
        for batch in session.exec(select(LeadBatch).where(LeadBatch.id.in_(batch_ids))).all()
        if batch.id is not None
    }

    restore_map: dict[int, list[int]] = {}
    ambiguous_leads: list[int] = []
    for lead_id, batch_id in leads:
        resolved_lead_id = int(lead_id)
        if batch_id is None:
            ambiguous_leads.append(resolved_lead_id)
            continue
        resolved_batch_id = int(batch_id)
        if resolved_batch_id in contaminated_batch_ids:
            continue
        batch = batch_map.get(resolved_batch_id)
        if batch is None or batch.evento_id != old_event_id:
            ambiguous_leads.append(resolved_lead_id)
            continue
        restore_map.setdefault(resolved_batch_id, []).append(resolved_lead_id)
    return restore_map, ambiguous_leads


def _tipo_lead_for_batch(batch: LeadBatch) -> TipoLead:
    if (batch.tipo_lead_proponente or "").strip().lower() == TipoLead.BILHETERIA.value:
        return TipoLead.BILHETERIA
    return TipoLead.ENTRADA_EVENTO


def _apply_old_event_link_restoration(
    session: Session,
    *,
    old_event_id: int,
    restore_map: dict[int, list[int]],
) -> int:
    if not restore_map:
        return 0
    old_event = session.get(Evento, old_event_id)
    if old_event is None:
        raise ValueError(f"Evento {old_event_id} nao encontrado durante a restauracao.")
    responsavel_nome = _resolve_proponente_nome(session, old_event)
    if responsavel_nome is None:
        responsavel_nome = old_event.nome
    restored: list[LeadEvento] = []
    for batch_id, lead_ids in restore_map.items():
        batch = session.get(LeadBatch, batch_id)
        if batch is None:
            raise ValueError(f"Batch {batch_id} nao encontrado durante a restauracao do evento antigo.")
        tipo_lead = _tipo_lead_for_batch(batch)
        for lead_id in sorted(set(lead_ids)):
            restored.append(
                LeadEvento(
                    lead_id=lead_id,
                    evento_id=old_event_id,
                    source_kind=LeadEventoSourceKind.LEAD_BATCH,
                    source_ref_id=batch_id,
                    tipo_lead=tipo_lead,
                    responsavel_tipo=TipoResponsavel.PROPONENTE,
                    responsavel_nome=responsavel_nome,
                    responsavel_agencia_id=None,
                )
            )
    if restored:
        session.add_all(restored)
        session.flush()
    return len(restored)


def _serialize_for_json(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _serialize_for_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize_for_json(item) for item in value]
    return value


def _write_artifact(
    artifact_dir: Path,
    payload: dict[str, Any],
) -> Path:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact_path = artifact_dir / f"fix-mixed-leads-event-editions-{timestamp}.json"
    artifact_path.write_text(
        json.dumps(_serialize_for_json(payload), ensure_ascii=False, indent=_JSON_INDENT),
        encoding="utf-8",
    )
    return artifact_path


def repair_event_editions(
    session: Session,
    *,
    old_event_id: int,
    input_file: Path,
    old_start_date: date,
    old_end_date: date,
    new_start_date: date | None,
    new_end_date: date | None,
    apply: bool,
    artifact_dir: Path,
) -> RepairSummary:
    arquivo_sha256 = _hash_file(input_file)
    old_event = session.get(Evento, old_event_id)
    if old_event is None:
        raise ValueError(f"Evento {old_event_id} nao encontrado.")

    resolved_new_start, resolved_new_end = _resolve_new_dates(
        old_event,
        new_start_date=new_start_date,
        new_end_date=new_end_date,
    )
    matched_batches = _load_matched_batches(
        session,
        evento_id=old_event_id,
        arquivo_sha256=arquivo_sha256,
    )
    if not matched_batches:
        raise ValueError(
            "Nenhum lead_batch do evento informado corresponde ao arquivo anexado pelo SHA-256 calculado."
        )

    contaminated_batch_ids = {batch.id for batch in matched_batches}
    gold_batch_ids = [
        batch.id
        for batch in matched_batches
        if _enum_matches(batch.stage, BatchStage.GOLD)
        and any(_enum_matches(batch.pipeline_status, status) for status in _GOLD_PIPELINE_STATUSES)
    ]
    if not gold_batch_ids:
        raise ValueError("Nenhum batch Gold promovido foi encontrado para o arquivo informado.")

    contaminated_lead_eventos = _load_contaminated_lead_eventos(
        session,
        old_event_id=old_event_id,
        gold_batch_ids=gold_batch_ids,
    )
    contaminated_lead_ids = [row.lead_id for row in contaminated_lead_eventos]
    restore_map, ambiguous_leads = _resolve_restore_batches(
        session,
        old_event_id=old_event_id,
        contaminated_lead_ids=contaminated_lead_ids,
        contaminated_batch_ids=contaminated_batch_ids,
    )

    snapshot = RepairSnapshot(
        old_event=_event_payload(
            old_event,
            start_date=old_event.data_inicio_prevista or old_start_date,
            end_date=old_event.data_fim_prevista or old_end_date,
        ),
        matched_batches=[asdict(batch) for batch in matched_batches],
        contaminated_lead_eventos=[asdict(row) for row in contaminated_lead_eventos],
        restore_batch_ids=sorted(restore_map.keys()),
        ambiguous_lead_ids=sorted(ambiguous_leads),
        old_event_dashboard_before=_build_event_validation_snapshot(session, evento_id=old_event_id),
    )

    if apply and ambiguous_leads:
        raise ValueError(
            "Foram encontrados leads ambiguos sem origem segura para restaurar no evento antigo: "
            + ", ".join(str(lead_id) for lead_id in sorted(ambiguous_leads)[:20])
        )

    new_event_payload = _event_payload(
        old_event,
        start_date=resolved_new_start,
        end_date=resolved_new_end,
    )
    _configure_statement_timeout_for_fix(session)
    new_event = Evento(**new_event_payload)
    session.add(new_event)
    session.flush()
    if new_event.id is None:
        raise RuntimeError("Falha ao criar o novo evento para a edicao segregada.")
    new_event_id = int(new_event.id)

    old_event.data_inicio_prevista = old_start_date
    old_event.data_fim_prevista = old_end_date
    session.add(old_event)

    batch_ids = sorted(contaminated_batch_ids)
    session.execute(
        MOVE_BATCH_EVENT_SQL,
        {"new_evento_id": new_event_id, "batch_ids": batch_ids},
    )
    session.execute(
        MOVE_SILVER_EVENT_SQL,
        {"new_evento_id": new_event_id, "batch_ids": batch_ids},
    )

    contaminated_lead_event_ids = [row.id for row in contaminated_lead_eventos]
    if contaminated_lead_event_ids:
        session.execute(
            MOVE_LEAD_EVENT_SQL,
            {"new_evento_id": new_event_id, "lead_evento_ids": contaminated_lead_event_ids},
        )

    restored_old_event_links = _apply_old_event_link_restoration(
        session,
        old_event_id=old_event_id,
        restore_map=restore_map,
    )

    validation = {
        "old_event_dashboard_after": _build_event_validation_snapshot(session, evento_id=old_event_id),
        "new_event_dashboard_after": _build_event_validation_snapshot(session, evento_id=new_event_id),
        "remaining_old_event_hash_batches": len(
            _load_matched_batches(
                session,
                evento_id=old_event_id,
                arquivo_sha256=arquivo_sha256,
            )
        ),
        "remaining_old_event_contaminated_links": len(
            _load_contaminated_lead_eventos(
                session,
                old_event_id=old_event_id,
                gold_batch_ids=gold_batch_ids,
            )
        ),
    }

    artifact_payload = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "mode": "apply" if apply else "dry-run",
        "input_file": str(input_file),
        "arquivo_sha256": arquivo_sha256,
        "old_event_id": old_event_id,
        "new_event_id": new_event_id,
        "old_event_dates": {
            "data_inicio_prevista": old_start_date.isoformat(),
            "data_fim_prevista": old_end_date.isoformat(),
        },
        "new_event_dates": {
            "data_inicio_prevista": resolved_new_start.isoformat(),
            "data_fim_prevista": resolved_new_end.isoformat(),
        },
        "snapshot": asdict(snapshot),
        "restored_old_event_links": restored_old_event_links,
        "validation": validation,
    }
    artifact_path = _write_artifact(artifact_dir, artifact_payload)

    if apply:
        session.commit()
    else:
        session.rollback()

    return RepairSummary(
        dry_run=not apply,
        old_event_id=old_event_id,
        new_event_id=new_event_id,
        arquivo_sha256=arquivo_sha256,
        batches_moved=len(batch_ids),
        gold_batches=gold_batch_ids,
        lead_events_moved=len(contaminated_lead_event_ids),
        restored_old_event_links=restored_old_event_links,
        ambiguous_leads=sorted(ambiguous_leads),
        validation=validation,
        artifact_path=str(artifact_path),
    )


def print_report(summary: RepairSummary) -> None:
    prefix = "[DRY-RUN]" if summary.dry_run else "[APPLY]"
    print(f"{prefix} Evento antigo: {summary.old_event_id}")
    print(f"{prefix} Novo evento: {summary.new_event_id}")
    print(f"{prefix} SHA-256 do arquivo: {summary.arquivo_sha256}")
    print(f"{prefix} Batches movidos: {summary.batches_moved} (gold={summary.gold_batches})")
    print(f"{prefix} LeadEvento movidos: {summary.lead_events_moved}")
    print(f"{prefix} Vínculos 2025 restaurados: {summary.restored_old_event_links}")
    print(f"{prefix} Leads ambiguos: {len(summary.ambiguous_leads)}")
    print(
        f"{prefix} Validacao: remaining_old_event_hash_batches="
        f"{summary.validation.get('remaining_old_event_hash_batches')} "
        f"remaining_old_event_contaminated_links="
        f"{summary.validation.get('remaining_old_event_contaminated_links')}"
    )
    if summary.artifact_path:
        print(f"{prefix} Artefato JSON: {summary.artifact_path}")
    if summary.dry_run:
        print(f"{prefix} Nenhuma alteracao foi persistida. Execute novamente com --apply para aplicar.")
    else:
        print(f"{prefix} Alteracoes persistidas com sucesso.")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.evento_id <= 0:
        print("evento_id deve ser maior que zero.", file=sys.stderr)
        return 1
    if not args.input_file.exists():
        print(f"Arquivo nao encontrado: {args.input_file}", file=sys.stderr)
        return 1
    load_env()
    engine = get_engine_for_scripts()
    try:
        with Session(engine) as session:
            summary = repair_event_editions(
                session,
                old_event_id=args.evento_id,
                input_file=args.input_file,
                old_start_date=args.old_start_date,
                old_end_date=args.old_end_date,
                new_start_date=args.new_start_date,
                new_end_date=args.new_end_date,
                apply=bool(args.apply),
                artifact_dir=args.artifact_dir,
            )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print_report(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
