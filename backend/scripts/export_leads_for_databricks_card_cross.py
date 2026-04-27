"""Export current leads as a Databricks-ready CSV for card/spending matching.

The output grain is one row per lead-event pair. It includes both the notebook
aliases (`evento`, `local`, `data_evento`) and explicit event columns
(`event_id`, `event_name`, `event_location`, `event_date`).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, RowMapping


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "artifacts" / "databricks_lead_card_cross"
DEFAULT_ENV_FILE = REPO_ROOT / "backend" / ".env"

EXPORT_COLUMNS = [
    "lead_id",
    "event_id",
    "event_name",
    "event_location",
    "event_date",
    "evento",
    "local",
    "data_evento",
    "cpf",
    "cpf_hash_sha256",
    "nome",
    "sobrenome",
    "email",
    "telefone",
    "data_nascimento",
    "sessao",
    "fonte_origem",
    "is_cliente_bb",
    "is_cliente_estilo",
    "data_criacao",
    "batch_id",
    "source_relation",
    "source_kind",
    "source_ref_id",
]

UNRESOLVED_COLUMNS = [
    "lead_id",
    "cpf",
    "cpf_hash_sha256",
    "nome",
    "sobrenome",
    "email",
    "telefone",
    "data_nascimento",
    "evento_nome",
    "sessao",
    "fonte_origem",
    "data_criacao",
    "batch_id",
    "reason",
]

READY_QUERY = text(
    """
    WITH candidates AS (
        SELECT
            1 AS source_rank,
            'lead_evento' AS source_relation,
            l.id AS lead_id,
            e.id AS event_id,
            e.nome AS event_name,
            concat_ws(' / ', nullif(trim(e.cidade), ''), nullif(trim(e.estado), '')) AS event_location,
            coalesce(e.data_inicio_realizada, e.data_inicio_prevista) AS event_date,
            l.cpf,
            l.nome,
            l.sobrenome,
            l.email,
            l.telefone,
            l.data_nascimento,
            l.sessao,
            l.fonte_origem,
            l.is_cliente_bb,
            l.is_cliente_estilo,
            l.data_criacao,
            l.batch_id,
            le.source_kind::text AS source_kind,
            le.source_ref_id AS source_ref_id
        FROM lead l
        JOIN lead_evento le ON le.lead_id = l.id
        JOIN evento e ON e.id = le.evento_id
        WHERE nullif(trim(coalesce(l.cpf, '')), '') IS NOT NULL

        UNION ALL

        SELECT
            2 AS source_rank,
            'lead_batch' AS source_relation,
            l.id AS lead_id,
            e.id AS event_id,
            e.nome AS event_name,
            concat_ws(' / ', nullif(trim(e.cidade), ''), nullif(trim(e.estado), '')) AS event_location,
            coalesce(e.data_inicio_realizada, e.data_inicio_prevista) AS event_date,
            l.cpf,
            l.nome,
            l.sobrenome,
            l.email,
            l.telefone,
            l.data_nascimento,
            l.sessao,
            l.fonte_origem,
            l.is_cliente_bb,
            l.is_cliente_estilo,
            l.data_criacao,
            l.batch_id,
            'lead_batch' AS source_kind,
            b.id AS source_ref_id
        FROM lead l
        JOIN lead_batches b ON b.id = l.batch_id
        JOIN evento e ON e.id = b.evento_id
        WHERE b.evento_id IS NOT NULL
          AND nullif(trim(coalesce(l.cpf, '')), '') IS NOT NULL
    ),
    ranked AS (
        SELECT
            *,
            row_number() OVER (
                PARTITION BY lead_id, event_id
                ORDER BY source_rank, source_ref_id NULLS LAST
            ) AS rn
        FROM candidates
    )
    SELECT
        lead_id,
        event_id,
        event_name,
        event_location,
        event_date,
        event_name AS evento,
        event_location AS local,
        event_date AS data_evento,
        cpf,
        nome,
        sobrenome,
        email,
        telefone,
        data_nascimento,
        sessao,
        fonte_origem,
        is_cliente_bb,
        is_cliente_estilo,
        data_criacao,
        batch_id,
        source_relation,
        source_kind,
        source_ref_id
    FROM ranked
    WHERE rn = 1
    ORDER BY event_date NULLS LAST, event_id, lead_id
    """
)

UNRESOLVED_QUERY = text(
    """
    WITH resolved AS (
        SELECT DISTINCT l.id AS lead_id
        FROM lead l
        JOIN lead_evento le ON le.lead_id = l.id
        WHERE nullif(trim(coalesce(l.cpf, '')), '') IS NOT NULL

        UNION

        SELECT DISTINCT l.id AS lead_id
        FROM lead l
        JOIN lead_batches b ON b.id = l.batch_id
        WHERE b.evento_id IS NOT NULL
          AND nullif(trim(coalesce(l.cpf, '')), '') IS NOT NULL
    )
    SELECT
        l.id AS lead_id,
        l.cpf,
        l.nome,
        l.sobrenome,
        l.email,
        l.telefone,
        l.data_nascimento,
        l.evento_nome,
        l.sessao,
        l.fonte_origem,
        l.data_criacao,
        l.batch_id,
        'missing_event_association' AS reason
    FROM lead l
    WHERE nullif(trim(coalesce(l.cpf, '')), '') IS NOT NULL
      AND NOT EXISTS (
        SELECT 1 FROM resolved r WHERE r.lead_id = l.id
      )
    ORDER BY l.id
    """
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export lead-event rows for Databricks card/spending matching."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where CSV and manifest files will be written.",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=DEFAULT_ENV_FILE,
        help="Path to backend .env file.",
    )
    return parser.parse_args()


def build_engine() -> Engine:
    url = (
        os.getenv("DIRECT_URL")
        or os.getenv("WORKER_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or ""
    ).strip()
    if not url:
        raise RuntimeError("DIRECT_URL, WORKER_DATABASE_URL or DATABASE_URL must be configured.")
    return create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 10})


def serialize(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def cpf_hash(value: Any) -> str:
    digits = "".join(ch for ch in serialize(value) if ch.isdigit())
    if not digits:
        return ""
    return hashlib.sha256(digits.encode("utf-8")).hexdigest()


def row_to_dict(row: RowMapping, columns: Iterable[str]) -> dict[str, str]:
    output: dict[str, str] = {}
    for column in columns:
        if column == "cpf_hash_sha256":
            output[column] = cpf_hash(row.get("cpf"))
        else:
            output[column] = serialize(row.get(column))
    return output


def write_query_csv(
    engine: Engine,
    query: Any,
    path: Path,
    columns: list[str],
) -> tuple[int, set[str], set[str]]:
    row_count = 0
    lead_ids: set[str] = set()
    event_ids: set[str] = set()

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()

        with engine.connect() as conn:
            result = conn.execution_options(stream_results=True).execute(query)
            for row in result.mappings():
                rendered = row_to_dict(row, columns)
                writer.writerow(rendered)
                row_count += 1
                if rendered.get("lead_id"):
                    lead_ids.add(rendered["lead_id"])
                if rendered.get("event_id"):
                    event_ids.add(rendered["event_id"])

    return row_count, lead_ids, event_ids


def main() -> int:
    args = parse_args()
    load_dotenv(args.env_file)

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    ready_csv = output_dir / f"npbb_leads_eventos_card_cross_{today}.csv"
    unresolved_csv = output_dir / f"npbb_leads_eventos_card_cross_unresolved_{today}.csv"
    manifest_path = output_dir / f"npbb_leads_eventos_card_cross_manifest_{today}.json"

    engine = build_engine()
    ready_rows, ready_leads, ready_events = write_query_csv(
        engine,
        READY_QUERY,
        ready_csv,
        EXPORT_COLUMNS,
    )
    unresolved_rows, unresolved_leads, _ = write_query_csv(
        engine,
        UNRESOLVED_QUERY,
        unresolved_csv,
        UNRESOLVED_COLUMNS,
    )

    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "ready_csv": str(ready_csv),
        "unresolved_csv": str(unresolved_csv),
        "ready_rows": ready_rows,
        "ready_distinct_leads": len(ready_leads),
        "ready_distinct_events": len(ready_events),
        "unresolved_rows": unresolved_rows,
        "unresolved_distinct_leads": len(unresolved_leads),
        "grain": "one row per lead_id + event_id",
        "notebook_required_columns": ["cpf", "evento", "local", "data_evento"],
        "recommended_notebook_columns": [
            "lead_id",
            "event_id",
            "event_name",
            "event_location",
            "event_date",
        ],
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"ready_csv={ready_csv}")
    print(f"unresolved_csv={unresolved_csv}")
    print(f"manifest={manifest_path}")
    print(f"ready_rows={ready_rows}")
    print(f"ready_distinct_leads={len(ready_leads)}")
    print(f"ready_distinct_events={len(ready_events)}")
    print(f"unresolved_rows={unresolved_rows}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
