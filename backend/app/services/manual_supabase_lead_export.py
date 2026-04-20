"""Build a manual-import CSV for `public.lead` from frozen lead batches.

This module reconstructs Silver CSVs for a fixed list of batches, runs the
pipeline once to produce a canonical consolidated CSV, converts it into the
`public.lead` schema, and filters out rows that would conflict with the
current database state.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
import csv
from datetime import date, datetime, time, timezone
import json
from pathlib import Path
from typing import Any, Iterable, Iterator, Literal

from sqlmodel import Session, select

from app.models.lead_batch import LeadBatch
from app.models.lead_public_models import Lead
from app.services.lead_pipeline_service import (
    _build_lead_payload,
    load_batch_without_bronze,
    materializar_silver_como_csv,
)
from lead_pipeline.pipeline import PipelineConfig, PipelineResult, run_pipeline

DEFAULT_EXPORT_DATE = "2026-04-20"
DEFAULT_LOTE_ID = "manual_supabase_import_2026-04-20"
ExportMode = Literal["delta", "full", "both"]
EXPORT_MODES: tuple[ExportMode, ...] = ("delta", "full", "both")
LEAD_IMPORT_COLUMNS = [
    "id_salesforce",
    "nome",
    "sobrenome",
    "email",
    "telefone",
    "cpf",
    "data_nascimento",
    "data_criacao",
    "evento_nome",
    "sessao",
    "data_compra",
    "opt_in",
    "opt_in_id",
    "opt_in_flag",
    "metodo_entrega",
    "endereco_rua",
    "endereco_numero",
    "bairro",
    "cep",
    "cidade",
    "estado",
    "genero",
    "codigo_promocional",
    "ingresso_tipo",
    "ingresso_qtd",
    "fonte_origem",
    "data_compra_data",
    "data_compra_hora",
    "batch_id",
    "rg",
    "complemento",
    "is_cliente_bb",
    "is_cliente_estilo",
]
SKIPPED_EXISTING_COLUMNS = [
    "skip_reason",
    "source_file",
    "source_sheet",
    "source_row",
    "batch_id",
    "arquivo_sha256",
    *LEAD_IMPORT_COLUMNS,
]
RECONCILIATION_COLUMNS = [
    "file_name",
    "arquivo_sha256",
    "batch_id",
    "stage",
    "pipeline_status",
    "silver_rows",
    "raw_rows",
    "pipeline_rejected_rows",
    "pipeline_accepted_rows",
    "already_existing_pre_export_rows",
    "delta_rows",
]
REJECTED_AUDIT_COLUMNS = [
    "source_file",
    "source_sheet",
    "source_row",
    "motivo_rejeicao",
    "evento_nome",
    "related_field_names",
    "related_field_values_json",
    "nome",
    "cpf",
    "email",
    "telefone",
    "data_nascimento",
    "data_evento",
    "local",
    "sessao",
    "row_data_json",
]


@dataclass(frozen=True)
class FrozenBatchSpec:
    """Immutable mapping between a user-provided file hash and a batch."""

    file_name: str
    arquivo_sha256: str
    batch_id: int


@dataclass(frozen=True)
class MaterializedBatch:
    """Batch metadata plus the reconstructed Silver CSV path."""

    spec: FrozenBatchSpec
    batch: LeadBatch
    silver_csv_path: Path
    silver_rows: int


@dataclass(frozen=True)
class AcceptedSourceRef:
    """Source row that survived the pipeline."""

    source_file: str
    source_sheet: str
    source_row: int
    batch_id: int
    arquivo_sha256: str


@dataclass(frozen=True)
class ImportCandidate:
    """Lead row prepared for CSV output and conflict filtering."""

    source_file: str
    source_sheet: str
    source_row: int
    batch_id: int
    arquivo_sha256: str
    id_salesforce: str | None
    dedupe_key: str | None
    payload: dict[str, Any]
    csv_row: dict[str, str]


@dataclass(frozen=True)
class ExportArtifacts:
    """Paths and summary produced by a manual export run."""

    output_dir: Path
    mode: ExportMode
    export_created_at: datetime
    import_csv_path: Path | None
    full_import_csv_path: Path | None
    skipped_existing_csv_path: Path
    reconciliation_csv_path: Path
    rejected_rows_csv_path: Path
    manifest_path: Path
    pipeline_output_dir: Path
    pipeline_result: PipelineResult
    summary: dict[str, Any]


class ManualSupabaseLeadExportError(RuntimeError):
    """Raised when the export cannot be completed safely."""


FROZEN_BATCH_SPECS: tuple[FrozenBatchSpec, ...] = (
    FrozenBatchSpec(
        file_name="1ª Etapa Circuito Brasileiro de Vôlei de Praia - CBVP Adulto.xlsx",
        arquivo_sha256="01f97edac26f2d5f932fc720f16760984ffca0b9f1a00393f292f8cd91e4966f",
        batch_id=188,
    ),
    FrozenBatchSpec(
        file_name="Circuito Banco do Brasil de Surf - CBBS WSL (2).xlsx",
        arquivo_sha256="cc295232c6b9d5fb46822b3943b0aaa798a86e77e7b2a69dc1dd89f8ec788b1b",
        batch_id=187,
    ),
    FrozenBatchSpec(
        file_name="Circuito Banco do Brasil de Surf - CBBS WSL.xlsx",
        arquivo_sha256="ebd69f17ed9343ab891fb252712248439e8be8b5081493a2eb3c5b535ec7c682",
        batch_id=250,
    ),
    FrozenBatchSpec(
        file_name="Copa Brasil.xlsx",
        arquivo_sha256="66ef60f67f35e27351289ff068b841fa151a4d60229883ee70a36121374e8cf6",
        batch_id=115,
    ),
    FrozenBatchSpec(
        file_name="Festival de Verão (2).xlsx",
        arquivo_sha256="7fe278d62a302b0169ef453007bf37d235ddc6002cd402a1c9ccb93fc14b1365",
        batch_id=117,
    ),
    FrozenBatchSpec(
        file_name="Festival de Verão.xlsx",
        arquivo_sha256="ff9ee62d8c72e9fec92a1db99c68b3f6e9ba8ecbf750635fbcadf408d4b5a43e",
        batch_id=118,
    ),
    FrozenBatchSpec(
        file_name="Leads 1ª Etapa BPT João Pessoa.xlsx",
        arquivo_sha256="785bac8c363b13fc3bc0548a895e64469d54e28894ef0b9187150d368d920848",
        batch_id=193,
    ),
    FrozenBatchSpec(
        file_name="Leads 2ª Etapa CBVP João Pessoa.xlsx",
        arquivo_sha256="c35c1e079130397c40b54f6aa35daf79a7b9b739f8faa965f13542939f6f7b46",
        batch_id=252,
    ),
    FrozenBatchSpec(
        file_name="Leads Base expodireto Cotrijal - Diária.xlsx",
        arquivo_sha256="9c25bce675dcd24783cb8fe979ffa3d383cd6e6abc060d536969f10206fe4c8a",
        batch_id=253,
    ),
    FrozenBatchSpec(
        file_name="Opt-in Gilberto Gil - PA.xlsx",
        arquivo_sha256="3d331a50aa336c71a01d426eec31b41b1cad08e66cdb748c52663ab5697f4479",
        batch_id=247,
    ),
    FrozenBatchSpec(
        file_name="Opt-in Gilberto Gil - SP.xlsx",
        arquivo_sha256="c42e72038c3a527d627b0ae21bcb39e66c5b5dea4039c6c4b4ed387a1aa77104",
        batch_id=244,
    ),
    FrozenBatchSpec(
        file_name="Opt-in Gilberto Gil - SSA.xlsx",
        arquivo_sha256="ee4bcbeb873ee05ee43572eb95ff588400a5b2b91ee9eaa6006fd8db8ceafbd5",
        batch_id=248,
    ),
    FrozenBatchSpec(
        file_name="Show Rural Coopavel.xlsx",
        arquivo_sha256="5a89d59605685eb31e2099d57b99024981118f6f0d74958b34e0e42583c2883f",
        batch_id=199,
    ),
    FrozenBatchSpec(
        file_name="Turnê Alceu Valença - RJ - 14-03.xlsx",
        arquivo_sha256="8c014db779bd869c18262ddac577e1d5add5c535606b34b1e34fed7e6f37e986",
        batch_id=245,
    ),
    FrozenBatchSpec(
        file_name="Turnê Alceu Valença - SP - 28-03.xlsx",
        arquivo_sha256="2ddbb81df5fa10a45b822091d07d5e354f47659f021b53b117755f9573f503d1",
        batch_id=246,
    ),
)


def normalize_ticketing_value(value: object) -> str:
    """Normalize string-like values the same way as the lead dedupe logic."""

    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    return value.strip()


def build_ticketing_key(*, email: object, cpf: object, evento_nome: object, sessao: object) -> str | None:
    """Return the app-equivalent unique key used by `public.lead`.

    The app only applies the ticketing-dedupe lookup when CPF is present.
    """

    cpf_value = normalize_ticketing_value(cpf)
    if not cpf_value:
        return None
    email_value = normalize_ticketing_value(email)
    evento_value = normalize_ticketing_value(evento_nome)
    sessao_value = normalize_ticketing_value(sessao)
    return f"{email_value}|{cpf_value}|{evento_value}|{sessao_value}"


def serialize_lead_value(value: Any) -> str:
    """Serialize typed payload values into a CSV-friendly representation."""

    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        rendered = value.replace(tzinfo=None) if value.tzinfo is not None else value
        if rendered.microsecond:
            return rendered.strftime("%Y-%m-%d %H:%M:%S.%f")
        return rendered.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date) and not isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, time):
        return value.isoformat()
    return str(value)


def iter_chunks(values: Iterable[str], size: int = 1000) -> Iterator[list[str]]:
    """Yield non-empty chunks while preserving the input order."""

    chunk: list[str] = []
    for value in values:
        if not value:
            continue
        chunk.append(value)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def count_csv_rows(path: Path) -> int:
    """Count data rows in a CSV file."""

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return sum(1 for _ in reader)


def materialize_frozen_batches(db: Session) -> list[MaterializedBatch]:
    """Resolve and materialize the fixed batches into Silver CSVs."""

    batches: list[MaterializedBatch] = []
    for spec in FROZEN_BATCH_SPECS:
        batch = load_batch_without_bronze(db, spec.batch_id)
        if batch is None:
            raise ManualSupabaseLeadExportError(f"Lote {spec.batch_id} não encontrado.")

        if (batch.nome_arquivo_original or "").strip() != spec.file_name:
            raise ManualSupabaseLeadExportError(
                f"Lote {spec.batch_id} não corresponde ao arquivo congelado esperado."
            )

        batch_sha = str(batch.__dict__.get("arquivo_sha256") or "").strip().lower()
        if batch_sha and batch_sha != spec.arquivo_sha256:
            raise ManualSupabaseLeadExportError(
                f"Lote {spec.batch_id} não corresponde ao SHA-256 congelado esperado."
            )

        csv_path = materializar_silver_como_csv(spec.batch_id, db)
        silver_rows = count_csv_rows(csv_path)
        batches.append(
            MaterializedBatch(
                spec=spec,
                batch=batch,
                silver_csv_path=csv_path,
                silver_rows=silver_rows,
            )
        )
    return batches


def load_invalid_row_keys(report_path: Path) -> tuple[set[tuple[str, str, int]], Counter[str]]:
    """Load pipeline-invalid row coordinates and counts per source file."""

    report = json.loads(report_path.read_text(encoding="utf-8"))
    invalid_keys: set[tuple[str, str, int]] = set()
    counts = Counter[str]()
    for item in report.get("invalid_records", []):
        source_file = str(item.get("source_file") or "").strip()
        source_sheet = str(item.get("source_sheet") or "").strip()
        source_row = int(item.get("source_row") or 0)
        invalid_keys.add((source_file, source_sheet, source_row))
        counts[source_file] += 1
    return invalid_keys, counts


def related_fields_for_reject_reason(reason: str) -> tuple[str, ...]:
    """Return row-data fields most relevant to a pipeline rejection reason."""

    normalized = reason.strip().upper()
    if normalized == "CPF_INVALIDO":
        return ("cpf",)
    if normalized == "TELEFONE_INVALIDO":
        return ("telefone",)
    if normalized == "DATA_EVENTO_INVALIDA":
        return ("data_evento", "local", "cidade", "estado")
    return (
        "cpf",
        "email",
        "telefone",
        "data_nascimento",
        "data_evento",
        "evento",
        "local",
        "sessao",
    )


def build_rejected_audit_rows(report_path: Path) -> list[dict[str, str]]:
    """Build a human-readable CSV payload for rejected pipeline rows."""

    report = json.loads(report_path.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for item in report.get("invalid_records", []):
        row_data = item.get("row_data") or {}
        motivo = str(item.get("motivo_rejeicao") or "").strip()
        related_fields = related_fields_for_reject_reason(motivo)
        related_values = {
            field: serialize_lead_value(row_data.get(field))
            for field in related_fields
            if field in row_data
        }
        rows.append(
            {
                "source_file": str(item.get("source_file") or "").strip(),
                "source_sheet": str(item.get("source_sheet") or "").strip(),
                "source_row": str(int(item.get("source_row") or 0)),
                "motivo_rejeicao": motivo,
                "evento_nome": serialize_lead_value(row_data.get("evento")),
                "related_field_names": ", ".join(related_fields),
                "related_field_values_json": json.dumps(
                    related_values,
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "nome": serialize_lead_value(row_data.get("nome")),
                "cpf": serialize_lead_value(row_data.get("cpf")),
                "email": serialize_lead_value(row_data.get("email")),
                "telefone": serialize_lead_value(row_data.get("telefone")),
                "data_nascimento": serialize_lead_value(row_data.get("data_nascimento")),
                "data_evento": serialize_lead_value(row_data.get("data_evento")),
                "local": serialize_lead_value(row_data.get("local")),
                "sessao": serialize_lead_value(row_data.get("sessao")),
                "row_data_json": json.dumps(row_data, ensure_ascii=False, sort_keys=True),
            }
        )
    return rows


def build_accepted_source_refs(
    *,
    raw_csv_path: Path,
    invalid_keys: set[tuple[str, str, int]],
    batches_by_source_file: dict[str, MaterializedBatch],
) -> tuple[list[AcceptedSourceRef], Counter[str]]:
    """Return source rows that survived the pipeline, preserving the original order."""

    accepted: list[AcceptedSourceRef] = []
    raw_counts = Counter[str]()

    with raw_csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            source_file = str(row.get("source_file") or "").strip()
            source_sheet = str(row.get("source_sheet") or "").strip()
            source_row = int(row.get("source_row") or 0)
            raw_counts[source_file] += 1
            if (source_file, source_sheet, source_row) in invalid_keys:
                continue

            materialized = batches_by_source_file.get(source_file)
            if materialized is None:
                raise ManualSupabaseLeadExportError(
                    f"Arquivo de origem '{source_file}' não pertence ao conjunto congelado."
                )

            accepted.append(
                AcceptedSourceRef(
                    source_file=source_file,
                    source_sheet=source_sheet,
                    source_row=source_row,
                    batch_id=materialized.spec.batch_id,
                    arquivo_sha256=materialized.spec.arquivo_sha256,
                )
            )

    return accepted, raw_counts


def build_import_candidates(
    *,
    consolidated_csv_path: Path,
    accepted_source_refs: list[AcceptedSourceRef],
    batches_by_batch_id: dict[int, MaterializedBatch],
    export_created_at: datetime,
) -> list[ImportCandidate]:
    """Transform the canonical consolidated CSV into `public.lead` rows."""

    candidates: list[ImportCandidate] = []
    with consolidated_csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        final_rows = list(reader)

    if len(final_rows) != len(accepted_source_refs):
        raise ManualSupabaseLeadExportError(
            "O CSV final do pipeline não alinhou com as linhas aceitas de origem."
        )

    for final_row, source_ref in zip(final_rows, accepted_source_refs, strict=True):
        materialized = batches_by_batch_id[source_ref.batch_id]
        payload = _build_lead_payload(final_row, materialized.batch)
        payload["data_criacao"] = export_created_at
        payload["batch_id"] = source_ref.batch_id
        dedupe_key = build_ticketing_key(
            email=payload.get("email"),
            cpf=payload.get("cpf"),
            evento_nome=payload.get("evento_nome"),
            sessao=payload.get("sessao"),
        )
        csv_row = {
            column: serialize_lead_value(payload.get(column))
            for column in LEAD_IMPORT_COLUMNS
        }
        candidates.append(
            ImportCandidate(
                source_file=source_ref.source_file,
                source_sheet=source_ref.source_sheet,
                source_row=source_ref.source_row,
                batch_id=source_ref.batch_id,
                arquivo_sha256=source_ref.arquivo_sha256,
                id_salesforce=normalize_ticketing_value(payload.get("id_salesforce")) or None,
                dedupe_key=dedupe_key,
                payload=payload,
                csv_row=csv_row,
            )
        )

    return candidates


def fetch_existing_conflicts(
    db: Session,
    *,
    candidates: Iterable[ImportCandidate],
) -> tuple[set[str], set[str]]:
    """Fetch current `public.lead` keys that would conflict with candidates."""

    materialized_candidates = list(candidates)
    incoming_ids = [
        candidate.id_salesforce or ""
        for candidate in materialized_candidates
        if candidate.id_salesforce
    ]
    incoming_cpfs = [
        normalize_ticketing_value(candidate.payload.get("cpf"))
        for candidate in materialized_candidates
        if normalize_ticketing_value(candidate.payload.get("cpf"))
    ]

    existing_id_salesforce: set[str] = set()
    for chunk in iter_chunks(incoming_ids):
        stmt = select(Lead.id_salesforce).where(Lead.id_salesforce.in_(chunk))
        for value in db.exec(stmt):
            normalized = normalize_ticketing_value(value)
            if normalized:
                existing_id_salesforce.add(normalized)

    existing_ticketing_keys: set[str] = set()
    for chunk in iter_chunks(incoming_cpfs):
        stmt = (
            select(Lead.email, Lead.cpf, Lead.evento_nome, Lead.sessao)
            .where(Lead.cpf.in_(chunk))
        )
        for email, cpf, evento_nome, sessao in db.exec(stmt):
            key = build_ticketing_key(
                email=email,
                cpf=cpf,
                evento_nome=evento_nome,
                sessao=sessao,
            )
            if key is not None:
                existing_ticketing_keys.add(key)

    return existing_id_salesforce, existing_ticketing_keys


def split_candidates_by_conflict(
    *,
    candidates: Iterable[ImportCandidate],
    existing_id_salesforce: set[str],
    existing_ticketing_keys: set[str],
) -> tuple[list[ImportCandidate], list[tuple[ImportCandidate, str]]]:
    """Split candidates into import-ready rows and conflict rows."""

    ready: list[ImportCandidate] = []
    skipped: list[tuple[ImportCandidate, str]] = []
    for candidate in candidates:
        if candidate.id_salesforce and candidate.id_salesforce in existing_id_salesforce:
            skipped.append((candidate, "id_salesforce_exists"))
            continue
        if candidate.dedupe_key and candidate.dedupe_key in existing_ticketing_keys:
            skipped.append((candidate, "ticketing_key_exists"))
            continue
        ready.append(candidate)
    return ready, skipped


def write_csv(path: Path, *, fieldnames: list[str], rows: Iterable[dict[str, str]]) -> int:
    """Write a CSV file and return the number of data rows written."""

    count = 0
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def build_reconciliation_rows(
    *,
    batches: list[MaterializedBatch],
    raw_counts: Counter[str],
    invalid_counts: Counter[str],
    skipped_existing: list[tuple[ImportCandidate, str]],
    ready_candidates: list[ImportCandidate],
) -> list[dict[str, str]]:
    """Build per-file reconciliation rows for human-readable audit."""

    ready_counts = Counter(candidate.source_file for candidate in ready_candidates)
    skipped_existing_counts = Counter(candidate.source_file for candidate, _ in skipped_existing)
    rows: list[dict[str, str]] = []
    for materialized in batches:
        file_name = materialized.spec.file_name
        raw_rows = raw_counts.get(file_name, 0)
        invalid_rows = invalid_counts.get(file_name, 0)
        accepted_rows = raw_rows - invalid_rows
        rows.append(
            {
                "file_name": file_name,
                "arquivo_sha256": materialized.spec.arquivo_sha256,
                "batch_id": str(materialized.spec.batch_id),
                "stage": str(materialized.batch.stage.value),
                "pipeline_status": str(materialized.batch.pipeline_status.value),
                "silver_rows": str(materialized.silver_rows),
                "raw_rows": str(raw_rows),
                "pipeline_rejected_rows": str(invalid_rows),
                "pipeline_accepted_rows": str(accepted_rows),
                "already_existing_pre_export_rows": str(skipped_existing_counts.get(file_name, 0)),
                "delta_rows": str(ready_counts.get(file_name, 0)),
            }
        )
    return rows


def build_manifest(
    *,
    export_date: str,
    mode: ExportMode,
    export_created_at: datetime,
    batches: list[MaterializedBatch],
    pipeline_result: PipelineResult,
    raw_counts: Counter[str],
    invalid_counts: Counter[str],
    skipped_existing: list[tuple[ImportCandidate, str]],
    ready_candidates: list[ImportCandidate],
    import_csv_path: Path | None,
    full_import_csv_path: Path | None,
    skipped_existing_csv_path: Path,
    reconciliation_csv_path: Path,
    rejected_rows_csv_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    """Build a JSON-serializable manifest for the export."""

    reconciliation_rows = build_reconciliation_rows(
        batches=batches,
        raw_counts=raw_counts,
        invalid_counts=invalid_counts,
        skipped_existing=skipped_existing,
        ready_candidates=ready_candidates,
    )
    skipped_reason_counts = Counter(reason for _, reason in skipped_existing)

    files: list[dict[str, Any]] = []
    for row in reconciliation_rows:
        accepted_rows = int(row["pipeline_accepted_rows"])
        existing_rows = int(row["already_existing_pre_export_rows"])
        delta_rows = int(row["delta_rows"])
        files.append(
            {
                "file_name": row["file_name"],
                "arquivo_sha256": row["arquivo_sha256"],
                "batch_id": int(row["batch_id"]),
                "stage": row["stage"],
                "pipeline_status": row["pipeline_status"],
                "silver_rows": int(row["silver_rows"]),
                "raw_rows": int(row["raw_rows"]),
                "pipeline_rejected_rows": int(row["pipeline_rejected_rows"]),
                "pipeline_accepted_rows": accepted_rows,
                "already_existing_pre_export_rows": existing_rows,
                "delta_rows": delta_rows,
                "skipped_existing_rows": existing_rows,
                "import_ready_rows": delta_rows,
                "full_rows": accepted_rows,
            }
        )

    return {
        "export_date": export_date,
        "mode": mode,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "export_created_at": export_created_at.isoformat(),
        "lote_id": pipeline_result.lote_id,
        "pipeline": {
            "status": pipeline_result.status,
            "decision": pipeline_result.decision,
            "exit_code": pipeline_result.exit_code,
            "output_dir": str(pipeline_result.output_dir),
            "report_path": str(pipeline_result.report_path),
            "summary_path": str(pipeline_result.summary_path),
            "consolidated_path": str(pipeline_result.consolidated_path),
        },
        "artifacts": {
            "import_csv_path": str(import_csv_path) if import_csv_path is not None else None,
            "full_import_csv_path": (
                str(full_import_csv_path) if full_import_csv_path is not None else None
            ),
            "skipped_existing_csv_path": str(skipped_existing_csv_path),
            "reconciliation_csv_path": str(reconciliation_csv_path),
            "rejected_rows_csv_path": str(rejected_rows_csv_path),
            "manifest_path": str(manifest_path),
        },
        "summary": {
            "frozen_batches": len(batches),
            "pipeline_consolidated_rows": sum(raw_counts.values()) - sum(invalid_counts.values()),
            "full_rows": sum(raw_counts.values()) - sum(invalid_counts.values()),
            "pipeline_rejected_rows": sum(invalid_counts.values()),
            "skipped_existing_rows": len(skipped_existing),
            "already_existing_pre_export_rows": len(skipped_existing),
            "import_ready_rows": len(ready_candidates),
            "delta_rows": len(ready_candidates),
            "skipped_existing_reason_counts": dict(skipped_reason_counts),
        },
        "files": files,
        "frozen_batch_specs": [asdict(batch.spec) for batch in batches],
    }


def run_manual_supabase_lead_export(
    *,
    db: Session,
    output_dir: Path,
    export_date: str = DEFAULT_EXPORT_DATE,
    lote_id: str = DEFAULT_LOTE_ID,
    mode: ExportMode = "delta",
) -> ExportArtifacts:
    """Generate the manual Supabase import CSV and the related audit artifacts."""

    output_dir.mkdir(parents=True, exist_ok=True)
    pipeline_root = output_dir / "_pipeline_output"
    pipeline_root.mkdir(parents=True, exist_ok=True)
    export_created_at = datetime.now(timezone.utc)

    batches = materialize_frozen_batches(db)
    if any(batch.batch.evento_id is None for batch in batches):
        raise ManualSupabaseLeadExportError(
            "Todos os batches congelados precisam ter `evento_id` para reconstruir o pipeline."
        )

    pipeline_result = run_pipeline(
        PipelineConfig(
            lote_id=lote_id,
            input_files=[batch.silver_csv_path for batch in batches],
            output_root=pipeline_root,
            anchored_on_evento_id=True,
        )
    )
    if pipeline_result.exit_code != 0:
        raise ManualSupabaseLeadExportError(
            f"Pipeline consolidado falhou com status {pipeline_result.status}."
        )

    invalid_keys, invalid_counts = load_invalid_row_keys(pipeline_result.report_path)
    batches_by_source_file = {batch.spec.file_name: batch for batch in batches}
    batches_by_batch_id = {batch.spec.batch_id: batch for batch in batches}
    raw_csv_path = pipeline_result.output_dir / "raw.csv"
    accepted_source_refs, raw_counts = build_accepted_source_refs(
        raw_csv_path=raw_csv_path,
        invalid_keys=invalid_keys,
        batches_by_source_file=batches_by_source_file,
    )
    candidates = build_import_candidates(
        consolidated_csv_path=pipeline_result.consolidated_path,
        accepted_source_refs=accepted_source_refs,
        batches_by_batch_id=batches_by_batch_id,
        export_created_at=export_created_at,
    )

    existing_id_salesforce, existing_ticketing_keys = fetch_existing_conflicts(
        db,
        candidates=candidates,
    )
    ready_candidates, skipped_existing = split_candidates_by_conflict(
        candidates=candidates,
        existing_id_salesforce=existing_id_salesforce,
        existing_ticketing_keys=existing_ticketing_keys,
    )

    import_csv_path = (
        output_dir / f"supabase_public_lead_import_{export_date}.csv"
        if mode in {"delta", "both"}
        else None
    )
    full_import_csv_path = (
        output_dir / f"supabase_public_lead_import_full_{export_date}.csv"
        if mode in {"full", "both"}
        else None
    )
    skipped_existing_csv_path = (
        output_dir / f"supabase_public_lead_skipped_existing_{export_date}.csv"
    )
    reconciliation_csv_path = (
        output_dir / f"supabase_public_lead_reconciliation_{export_date}.csv"
    )
    rejected_rows_csv_path = (
        output_dir / f"supabase_public_lead_pipeline_rejections_{export_date}.csv"
    )
    manifest_path = output_dir / f"supabase_public_lead_manifest_{export_date}.json"

    if import_csv_path is not None:
        write_csv(
            import_csv_path,
            fieldnames=LEAD_IMPORT_COLUMNS,
            rows=(candidate.csv_row for candidate in ready_candidates),
        )
    if full_import_csv_path is not None:
        write_csv(
            full_import_csv_path,
            fieldnames=LEAD_IMPORT_COLUMNS,
            rows=(candidate.csv_row for candidate in candidates),
        )
    write_csv(
        skipped_existing_csv_path,
        fieldnames=SKIPPED_EXISTING_COLUMNS,
        rows=(
            {
                "skip_reason": reason,
                "source_file": candidate.source_file,
                "source_sheet": candidate.source_sheet,
                "source_row": str(candidate.source_row),
                "batch_id": str(candidate.batch_id),
                "arquivo_sha256": candidate.arquivo_sha256,
                **candidate.csv_row,
            }
            for candidate, reason in skipped_existing
        ),
    )
    write_csv(
        reconciliation_csv_path,
        fieldnames=RECONCILIATION_COLUMNS,
        rows=build_reconciliation_rows(
            batches=batches,
            raw_counts=raw_counts,
            invalid_counts=invalid_counts,
            skipped_existing=skipped_existing,
            ready_candidates=ready_candidates,
        ),
    )
    write_csv(
        rejected_rows_csv_path,
        fieldnames=REJECTED_AUDIT_COLUMNS,
        rows=build_rejected_audit_rows(pipeline_result.report_path),
    )

    manifest = build_manifest(
        export_date=export_date,
        mode=mode,
        export_created_at=export_created_at,
        batches=batches,
        pipeline_result=pipeline_result,
        raw_counts=raw_counts,
        invalid_counts=invalid_counts,
        skipped_existing=skipped_existing,
        ready_candidates=ready_candidates,
        import_csv_path=import_csv_path,
        full_import_csv_path=full_import_csv_path,
        skipped_existing_csv_path=skipped_existing_csv_path,
        reconciliation_csv_path=reconciliation_csv_path,
        rejected_rows_csv_path=rejected_rows_csv_path,
        manifest_path=manifest_path,
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return ExportArtifacts(
        output_dir=output_dir,
        mode=mode,
        export_created_at=export_created_at,
        import_csv_path=import_csv_path,
        full_import_csv_path=full_import_csv_path,
        skipped_existing_csv_path=skipped_existing_csv_path,
        reconciliation_csv_path=reconciliation_csv_path,
        rejected_rows_csv_path=rejected_rows_csv_path,
        manifest_path=manifest_path,
        pipeline_output_dir=pipeline_root,
        pipeline_result=pipeline_result,
        summary=manifest["summary"],
    )
