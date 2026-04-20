"""Generate a manual `public.lead` import CSV for batch 255.

This bypasses the Gold pipeline for a specific source whose CPF mapping was lost
in Silver. The raw source file is read from the batch payload, transformed into
the `public.lead` schema, deduplicated, and exported as CSV artifacts for
manual upload.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime, timezone
import io
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

from dotenv import load_dotenv
from sqlmodel import Session, select

ROOT_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = ROOT_DIR.parent
if str(REPO_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("DB_REQUIRE_SUPABASE_POOLER", "false")


BATCH_ID = 255
EXPORT_DATE = "2026-04-20"
DEFAULT_OUTPUT_DIR = REPO_DIR / "artifacts" / "manual_supabase_import_batch_255"
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
INPUT_FIELDNAMES = {
    "first_name": "First name",
    "last_name": "Last name",
    "email": "Email",
    "phone": "Phone number",
    "document": "ID or Passport number",
    "document_adjusted": "Ajustado",
    "birth_date": "Date of Birth (America/Sao_Paulo)",
    "document_type": "id_type",
}
SKIPPED_COLUMNS = ["reason", "source_row", *LEAD_IMPORT_COLUMNS]
NON_DIGIT_RE = re.compile(r"\D+")
SCIENTIFIC_PHONE_RE = re.compile(r"^\s*\d+[.,]\d+e\+\d+\s*$", re.IGNORECASE)
LOCALIZED_BIRTH_RE = re.compile(r"^\s*(\d{1,2})\s+([A-Za-zÀ-ÿ]{3})\s+(\d{4})")
MONTH_MAP = {
    "jan": 1,
    "fev": 2,
    "feb": 2,
    "mar": 3,
    "abr": 4,
    "apr": 4,
    "mai": 5,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "aug": 8,
    "set": 9,
    "sep": 9,
    "out": 10,
    "oct": 10,
    "nov": 11,
    "dez": 12,
    "dec": 12,
}


@dataclass(frozen=True)
class RowBuildResult:
    """Prepared row plus metadata used for dedupe and skipping."""

    source_row: int
    csv_row: dict[str, str]
    dedupe_key: str | None


def load_environment() -> None:
    """Load `backend/.env` when available."""

    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        return
    load_dotenv()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(
        description="Gera um CSV manual compatível com public.lead para o batch 255."
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Diretório onde os artefatos serão gravados.",
    )
    return parser.parse_args(argv)


def detect_encoding(payload: bytes) -> str:
    """Detect the text encoding with a small whitelist."""

    for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            payload.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    return "latin-1"


def digits_only(value: object) -> str:
    """Return only decimal digits from a value."""

    return NON_DIGIT_RE.sub("", str(value or ""))


def normalize_document_value(raw_document: object, adjusted_document: object) -> str:
    """Use the original document as source, with adjusted fallback for lost zeros."""

    raw_digits = digits_only(raw_document)
    adjusted_digits = digits_only(adjusted_document)
    if raw_digits and adjusted_digits and len(adjusted_digits) > len(raw_digits):
        if adjusted_digits.endswith(raw_digits):
            return adjusted_digits
    return raw_digits or adjusted_digits


def normalize_phone_value(raw_phone: object) -> str:
    """Preserve usable phones and blank out scientific-notation artifacts."""

    text = str(raw_phone or "").strip()
    if not text:
        return ""
    if SCIENTIFIC_PHONE_RE.match(text):
        return ""
    digits = digits_only(text)
    return digits


def parse_birth_date(raw_value: object) -> str:
    """Convert localized birth-date strings into `YYYY-MM-DD`."""

    text = str(raw_value or "").strip()
    if not text:
        return ""
    match = LOCALIZED_BIRTH_RE.match(text)
    if not match:
        return ""
    day = int(match.group(1))
    month_token = match.group(2).strip().lower()[:3]
    year = int(match.group(3))
    month = MONTH_MAP.get(month_token)
    if month is None:
        return ""
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return ""


def build_source_rows(payload: bytes, *, encoding: str) -> list[dict[str, str]]:
    """Read the raw CSV payload as a list of dictionaries."""

    text_stream = io.StringIO(payload.decode(encoding))
    reader = csv.DictReader(text_stream, delimiter=";")
    return [{str(key): str(value or "") for key, value in row.items()} for row in reader]


def fetch_batch_context(session: Session) -> tuple[Any, Any, bytes]:
    """Load batch, event, and raw payload."""

    from app.models.models import Evento
    from app.services.imports.payload_storage import read_batch_payload
    from app.services.lead_pipeline_service import load_batch_without_bronze

    batch = load_batch_without_bronze(session, BATCH_ID)
    if batch is None:
        raise RuntimeError(f"Lote {BATCH_ID} não encontrado.")
    if batch.evento_id is None:
        raise RuntimeError(f"Lote {BATCH_ID} sem evento_id.")
    evento = session.get(Evento, int(batch.evento_id))
    if evento is None:
        raise RuntimeError(f"Evento {batch.evento_id} não encontrado.")
    payload = read_batch_payload(batch)
    if not payload:
        raise RuntimeError(f"Payload do lote {BATCH_ID} indisponível.")
    return batch, evento, payload


def build_csv_row(
    *,
    source_row_number: int,
    raw_row: dict[str, str],
    evento_nome: str,
    sessao: str,
    cidade: str,
    estado: str,
    fonte_origem: str,
    data_criacao: str,
    batch_id: int,
    counters: dict[str, int],
) -> RowBuildResult:
    """Transform one raw source row into a `public.lead` row."""

    from app.services.manual_supabase_lead_export import build_ticketing_key

    document_value = normalize_document_value(
        raw_row.get(INPUT_FIELDNAMES["document"]),
        raw_row.get(INPUT_FIELDNAMES["document_adjusted"]),
    )
    if not document_value:
        counters["document_blank"] += 1
    if len(document_value) > 11:
        counters["document_over_11"] += 1
        document_for_cpf = ""
    else:
        document_for_cpf = document_value

    phone_value = normalize_phone_value(raw_row.get(INPUT_FIELDNAMES["phone"]))
    if not phone_value and str(raw_row.get(INPUT_FIELDNAMES["phone"]) or "").strip():
        counters["phone_blank_scientific"] += 1

    birth_date = parse_birth_date(raw_row.get(INPUT_FIELDNAMES["birth_date"]))
    if not birth_date and str(raw_row.get(INPUT_FIELDNAMES["birth_date"]) or "").strip():
        counters["birth_date_blank"] += 1

    first_name = str(raw_row.get(INPUT_FIELDNAMES["first_name"]) or "").strip()
    last_name = str(raw_row.get(INPUT_FIELDNAMES["last_name"]) or "").strip()
    if not first_name:
        first_name = last_name

    document_type = str(raw_row.get(INPUT_FIELDNAMES["document_type"]) or "").strip().upper()
    rg_value = document_value if document_type == "RG" and len(document_value) <= 30 else ""

    csv_row = {
        "id_salesforce": "",
        "nome": first_name,
        "sobrenome": last_name,
        "email": str(raw_row.get(INPUT_FIELDNAMES["email"]) or "").strip(),
        "telefone": phone_value,
        "cpf": document_for_cpf,
        "data_nascimento": birth_date,
        "data_criacao": data_criacao,
        "evento_nome": evento_nome,
        "sessao": sessao,
        "data_compra": "",
        "opt_in": "",
        "opt_in_id": "",
        "opt_in_flag": "",
        "metodo_entrega": "",
        "endereco_rua": "",
        "endereco_numero": "",
        "bairro": "",
        "cep": "",
        "cidade": cidade,
        "estado": estado,
        "genero": "",
        "codigo_promocional": "",
        "ingresso_tipo": "",
        "ingresso_qtd": "",
        "fonte_origem": fonte_origem,
        "data_compra_data": "",
        "data_compra_hora": "",
        "batch_id": str(batch_id),
        "rg": rg_value,
        "complemento": "",
        "is_cliente_bb": "",
        "is_cliente_estilo": "",
    }
    dedupe_key = build_ticketing_key(
        email=csv_row["email"],
        cpf=csv_row["cpf"],
        evento_nome=csv_row["evento_nome"],
        sessao=csv_row["sessao"],
    )
    return RowBuildResult(
        source_row=source_row_number,
        csv_row=csv_row,
        dedupe_key=dedupe_key,
    )


def fetch_existing_keys(session: Session, *, rows: list[RowBuildResult]) -> set[str]:
    """Fetch existing ticketing keys that would conflict with the import."""

    from app.models.lead_public_models import Lead
    from app.services.manual_supabase_lead_export import (
        build_ticketing_key,
        iter_chunks,
        normalize_ticketing_value,
    )

    cpfs = sorted(
        {
            normalize_ticketing_value(row.csv_row.get("cpf"))
            for row in rows
            if normalize_ticketing_value(row.csv_row.get("cpf"))
        }
    )
    existing_keys: set[str] = set()
    for chunk in iter_chunks(cpfs):
        stmt = (
            select(Lead.email, Lead.cpf, Lead.evento_nome, Lead.sessao)
            .where(Lead.cpf.in_(chunk))
            .where(Lead.evento_nome == "South Summit")
        )
        for email, cpf, evento_nome, sessao in session.exec(stmt):
            key = build_ticketing_key(
                email=email,
                cpf=cpf,
                evento_nome=evento_nome,
                sessao=sessao,
            )
            if key is not None:
                existing_keys.add(key)
    return existing_keys


def main(argv: list[str] | None = None) -> int:
    """Generate the manual import artifacts for batch 255."""

    from app.db.database import build_worker_engine, set_internal_service_db_context
    from app.services.manual_supabase_lead_export import write_csv

    args = parse_args(argv)
    load_environment()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    engine = build_worker_engine()
    with Session(engine) as session:
        set_internal_service_db_context(session)
        batch, evento, payload = fetch_batch_context(session)

        encoding = detect_encoding(payload)
        raw_rows = build_source_rows(payload, encoding=encoding)
        sessao = f"{str(evento.cidade or '').strip()}-{str(evento.estado or '').strip()}".strip("-")
        data_criacao = datetime.now(timezone.utc).replace(tzinfo=None).isoformat(sep=" ")
        counters = {
            "document_blank": 0,
            "document_over_11": 0,
            "phone_blank_scientific": 0,
            "birth_date_blank": 0,
        }

        prepared_rows: list[RowBuildResult] = []
        internal_duplicates: list[dict[str, str]] = []
        seen_keys: set[str] = set()
        for source_row_number, raw_row in enumerate(raw_rows, start=2):
            built = build_csv_row(
                source_row_number=source_row_number,
                raw_row=raw_row,
                evento_nome=str(evento.nome or ""),
                sessao=sessao,
                cidade=str(evento.cidade or ""),
                estado=str(evento.estado or ""),
                fonte_origem=str(batch.plataforma_origem or ""),
                data_criacao=data_criacao,
                batch_id=int(batch.id),
                counters=counters,
            )
            if built.dedupe_key and built.dedupe_key in seen_keys:
                internal_duplicates.append(
                    {
                        "reason": "duplicate_ticketing_key_in_file",
                        "source_row": str(built.source_row),
                        **built.csv_row,
                    }
                )
                continue
            if built.dedupe_key:
                seen_keys.add(built.dedupe_key)
            prepared_rows.append(built)

        existing_keys = fetch_existing_keys(session, rows=prepared_rows)
        final_rows: list[dict[str, str]] = []
        skipped_existing: list[dict[str, str]] = []
        for built in prepared_rows:
            if built.dedupe_key and built.dedupe_key in existing_keys:
                skipped_existing.append(
                    {
                        "reason": "ticketing_key_exists",
                        "source_row": str(built.source_row),
                        **built.csv_row,
                    }
                )
                continue
            final_rows.append(built.csv_row)

    import_csv_path = output_dir / f"supabase_public_lead_import_batch_{BATCH_ID}.csv"
    skipped_duplicates_path = output_dir / f"supabase_public_lead_skipped_batch_{BATCH_ID}.csv"
    manifest_path = output_dir / f"supabase_public_lead_manifest_batch_{BATCH_ID}.json"

    write_csv(
        import_csv_path,
        fieldnames=LEAD_IMPORT_COLUMNS,
        rows=final_rows,
    )
    write_csv(
        skipped_duplicates_path,
        fieldnames=SKIPPED_COLUMNS,
        rows=[*internal_duplicates, *skipped_existing],
    )

    manifest = {
        "batch_id": BATCH_ID,
        "source_file": str(batch.nome_arquivo_original),
        "arquivo_sha256": str(batch.__dict__.get("arquivo_sha256") or ""),
        "encoding": encoding,
        "evento_id": int(evento.id),
        "evento_nome": str(evento.nome or ""),
        "sessao": sessao,
        "summary": {
            "raw_rows": len(raw_rows),
            "internal_duplicates_skipped": len(internal_duplicates),
            "existing_conflicts_skipped": len(skipped_existing),
            "final_rows": len(final_rows),
            **counters,
        },
        "artifacts": {
            "import_csv_path": str(import_csv_path),
            "skipped_csv_path": str(skipped_duplicates_path),
            "manifest_path": str(manifest_path),
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"import_csv={import_csv_path}")
    print(f"skipped_csv={skipped_duplicates_path}")
    print(f"manifest={manifest_path}")
    print(f"final_rows={len(final_rows)}")
    print(f"internal_duplicates_skipped={len(internal_duplicates)}")
    print(f"existing_conflicts_skipped={len(skipped_existing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
