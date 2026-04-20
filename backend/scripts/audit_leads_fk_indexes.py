"""Audita FKs sem indice util no schema public e salva evidencia versionada.

Uso:
  python scripts/audit_leads_fk_indexes.py
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

import sqlalchemy as sa
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE_DIR.parent
DEFAULT_OUT_DIR = REPO_ROOT / "auditoria" / "evidencias"

LEADS_CONTEXT_TABLES = {
    "lead",
    "lead_evento",
    "lead_batches",
    "leads_silver",
    "lead_import_etl_job",
    "lead_import_etl_staging",
    "lead_import_etl_preview_session",
    "ativacao",
    "ativacao_lead",
    "evento",
}

CRITICAL_FK_COLUMNS = {
    ("lead", "batch_id"),
    ("lead_evento", "lead_id"),
    ("lead_evento", "evento_id"),
    ("lead_evento", "responsavel_agencia_id"),
    ("lead_batches", "evento_id"),
    ("lead_batches", "ativacao_id"),
    ("leads_silver", "batch_id"),
    ("leads_silver", "evento_id"),
    ("lead_import_etl_job", "batch_id"),
    ("lead_import_etl_staging", "job_id"),
    ("lead_import_etl_staging", "batch_id"),
    ("ativacao", "evento_id"),
    ("ativacao_lead", "ativacao_id"),
    ("ativacao_lead", "lead_id"),
}

for env_path in (BASE_DIR / ".env", REPO_ROOT / ".env"):
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    load_dotenv()


def _url() -> str:
    url = (os.getenv("DIRECT_URL") or os.getenv("DATABASE_URL") or "").strip()
    if not url or url.startswith("sqlite"):
        raise SystemExit("Defina DIRECT_URL ou DATABASE_URL Postgres para auditar FKs.")
    return url


def _engine(url: str):
    connect_args: dict = {"connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "30"))}
    if "sslmode=" not in url and "ssl=require" not in url and "127.0.0.1" not in url and "localhost" not in url:
        connect_args["sslmode"] = "require"
    return sa.create_engine(url, connect_args=connect_args, pool_pre_ping=True)


def _classification(table_name: str, fk_columns: str) -> str:
    columns = tuple(part.strip() for part in fk_columns.split(","))
    if table_name not in LEADS_CONTEXT_TABLES:
        return "irrelevante no contexto atual"
    if len(columns) == 1 and (table_name, columns[0]) in CRITICAL_FK_COLUMNS:
        return "critica"
    return "importante"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-dir",
        default=os.getenv("LEADS_AUDIT_EVIDENCE_DIR", str(DEFAULT_OUT_DIR)),
        help="Diretorio versionado para salvar evidencia.",
    )
    args = parser.parse_args()

    query = """
    with fk_cols as (
      select
        con.oid as constraint_oid,
        con.conname,
        con.conrelid,
        n.nspname as schema_name,
        tbl.relname as table_name,
        ref.relname as referenced_table,
        array_agg(att.attname order by ord.ordinality) as fk_columns,
        array_agg(att.attnum order by ord.ordinality) as fk_attnums
      from pg_constraint con
      join pg_class tbl on tbl.oid = con.conrelid
      join pg_namespace n on n.oid = tbl.relnamespace
      join pg_class ref on ref.oid = con.confrelid
      join unnest(con.conkey) with ordinality as ord(attnum, ordinality) on true
      join pg_attribute att on att.attrelid = con.conrelid and att.attnum = ord.attnum
      where con.contype = 'f'
        and n.nspname = 'public'
      group by con.oid, con.conname, con.conrelid, n.nspname, tbl.relname, ref.relname
    ),
    index_cols as (
      select
        i.indrelid,
        idx.relname as index_name,
        array_agg(ord.attnum order by ord.ordinality) as ind_attnums
      from pg_index i
      join pg_class idx on idx.oid = i.indexrelid
      join unnest(i.indkey) with ordinality as ord(attnum, ordinality) on ord.attnum > 0
      where i.indisvalid
        and i.indisready
      group by i.indrelid, idx.relname
    ),
    matching_indexes as (
      select
        fk.constraint_oid,
        idx.index_name
      from fk_cols fk
      join index_cols idx on idx.indrelid = fk.conrelid
      where idx.ind_attnums[:array_length(fk.fk_attnums, 1)] = fk.fk_attnums
    )
    select
      fk.table_name,
      fk.conname,
      array_to_string(fk.fk_columns, ',') as fk_columns,
      fk.referenced_table,
      coalesce(string_agg(mi.index_name, ', ' order by mi.index_name), '') as useful_indexes
    from fk_cols fk
    left join matching_indexes mi on mi.constraint_oid = fk.constraint_oid
    group by fk.table_name, fk.conname, fk.fk_columns, fk.referenced_table
    order by fk.table_name, fk.conname
    """

    lines = [
        "# auditoria de FKs sem indice util",
        f"# gerado em {datetime.now(timezone.utc).isoformat()}",
        "",
        "table | constraint | fk_columns | referenced_table | useful_indexes | classificacao | decisao",
    ]
    with _engine(_url()).connect() as conn:
        rows = conn.execute(sa.text(query)).fetchall()
        for table_name, conname, fk_columns, referenced_table, useful_indexes in rows:
            classification = _classification(str(table_name), str(fk_columns))
            decision = "sem acao: indice util encontrado" if useful_indexes else "requer revisao"
            lines.append(
                " | ".join(
                    [
                        str(table_name),
                        str(conname),
                        str(fk_columns),
                        str(referenced_table),
                        str(useful_indexes or "<ausente>"),
                        classification,
                        decision,
                    ]
                )
            )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "fk_index_audit.txt"
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Escrito: {out_file}")


if __name__ == "__main__":
    main()
