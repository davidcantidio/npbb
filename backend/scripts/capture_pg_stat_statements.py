"""Captura snapshots de pg_stat_statements para evidencias versionadas.

Uso:
  python scripts/capture_pg_stat_statements.py --label before
  python scripts/capture_pg_stat_statements.py --label after --profile dashboard_age_analysis
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sqlalchemy as sa
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE_DIR.parent
DEFAULT_OUT_DIR = REPO_ROOT / "auditoria" / "evidencias"

PROFILE_PATTERNS: dict[str, tuple[str, ...]] = {
    "dashboard_age_analysis": (
        "%from lead_evento join lead on lead.id = lead_evento.lead_id join evento on evento.id = lead_evento.evento_id%",
        "%from lead join lead_batches on lead.batch_id = lead_batches.id join evento on evento.id = lead_batches.evento_id%",
        "%select evento.id, evento.nome, evento.cidade, evento.estado from evento%",
        "%select lead.id, lead.evento_nome, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome, lead.sobrenome from lead%",
    ),
}


for env_path in (BASE_DIR / ".env", REPO_ROOT / ".env"):
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    load_dotenv()


@dataclass(frozen=True, slots=True)
class PgStatStatementRow:
    queryid: str
    calls: int
    total_exec_ms: float
    mean_exec_ms: float
    rows: int
    shared_blks_hit: int
    shared_blks_read: int
    temp_blks_read: int
    temp_blks_written: int
    query_sample: str


@dataclass(frozen=True, slots=True)
class PgStatDeltaRow:
    queryid: str
    calls_delta: int
    total_exec_ms_delta: float
    mean_exec_ms_after: float
    rows_delta: int
    shared_blks_hit_delta: int
    shared_blks_read_delta: int
    temp_blks_read_delta: int
    temp_blks_written_delta: int
    query_sample: str


def _url() -> str:
    url = (os.getenv("DIRECT_URL") or os.getenv("DATABASE_URL") or "").strip()
    if not url or url.startswith("sqlite"):
        raise SystemExit("Defina DIRECT_URL ou DATABASE_URL Postgres para consultar pg_stat_statements.")
    return url


def build_engine(url: str):
    connect_args: dict[str, Any] = {"connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "30"))}
    if (
        "sslmode=" not in url
        and "ssl=require" not in url
        and "127.0.0.1" not in url
        and "localhost" not in url
    ):
        connect_args["sslmode"] = "require"
    return sa.create_engine(url, connect_args=connect_args, pool_pre_ping=True)


def _profile_patterns(profile: str | None) -> tuple[str, ...]:
    if profile is None:
        return ()
    try:
        return PROFILE_PATTERNS[profile]
    except KeyError as exc:
        known = ", ".join(sorted(PROFILE_PATTERNS))
        raise SystemExit(f"Profile desconhecido: {profile}. Perfis validos: {known}") from exc


def _profile_sql_clause(profile: str | None) -> tuple[str, dict[str, str]]:
    patterns = _profile_patterns(profile)
    if not patterns:
        return "", {}

    clauses: list[str] = []
    params: dict[str, str] = {}
    for index, pattern in enumerate(patterns):
        key = f"profile_pattern_{index}"
        clauses.append(f"lower(query) like :{key}")
        params[key] = pattern.lower()
    return " and (" + " or ".join(clauses) + ")", params


def pg_stat_statements_installed(conn: sa.Connection) -> bool:
    return bool(
        conn.execute(
            sa.text("select exists (select 1 from pg_extension where extname = 'pg_stat_statements')")
        ).scalar()
    )


def fetch_pg_stat_statements_rows(
    conn: sa.Connection,
    *,
    profile: str | None = None,
    limit: int = 10,
) -> list[PgStatStatementRow]:
    clause, params = _profile_sql_clause(profile)
    query = sa.text(
        f"""
        select
          coalesce(queryid::text, md5(query)) as queryid,
          calls,
          round(total_exec_time::numeric, 3) as total_exec_ms,
          round(mean_exec_time::numeric, 3) as mean_exec_ms,
          rows,
          shared_blks_hit,
          shared_blks_read,
          temp_blks_read,
          temp_blks_written,
          left(regexp_replace(query, '\\s+', ' ', 'g'), 700) as query_sample
        from pg_stat_statements
        where dbid = (select oid from pg_database where datname = current_database())
        {clause}
        order by total_exec_time desc
        limit :limit
        """
    )
    rows = conn.execute(query, {**params, "limit": limit}).fetchall()
    return [
        PgStatStatementRow(
            queryid=str(row.queryid),
            calls=int(row.calls or 0),
            total_exec_ms=float(row.total_exec_ms or 0.0),
            mean_exec_ms=float(row.mean_exec_ms or 0.0),
            rows=int(row.rows or 0),
            shared_blks_hit=int(row.shared_blks_hit or 0),
            shared_blks_read=int(row.shared_blks_read or 0),
            temp_blks_read=int(row.temp_blks_read or 0),
            temp_blks_written=int(row.temp_blks_written or 0),
            query_sample=str(row.query_sample or ""),
        )
        for row in rows
    ]


def compute_pg_stat_delta(
    before: list[PgStatStatementRow],
    after: list[PgStatStatementRow],
) -> list[PgStatDeltaRow]:
    def counter_delta(current: int | float, previous: int | float) -> int | float:
        raw = current - previous
        return raw if raw >= 0 else current

    before_index = {row.queryid: row for row in before}
    deltas: list[PgStatDeltaRow] = []
    for row in after:
        old = before_index.get(row.queryid)
        if old is None:
            calls_delta = row.calls
            total_exec_ms_delta = row.total_exec_ms
            rows_delta = row.rows
            shared_blks_hit_delta = row.shared_blks_hit
            shared_blks_read_delta = row.shared_blks_read
            temp_blks_read_delta = row.temp_blks_read
            temp_blks_written_delta = row.temp_blks_written
        else:
            calls_delta = int(counter_delta(row.calls, old.calls))
            total_exec_ms_delta = round(float(counter_delta(row.total_exec_ms, old.total_exec_ms)), 3)
            rows_delta = int(counter_delta(row.rows, old.rows))
            shared_blks_hit_delta = int(counter_delta(row.shared_blks_hit, old.shared_blks_hit))
            shared_blks_read_delta = int(counter_delta(row.shared_blks_read, old.shared_blks_read))
            temp_blks_read_delta = int(counter_delta(row.temp_blks_read, old.temp_blks_read))
            temp_blks_written_delta = int(counter_delta(row.temp_blks_written, old.temp_blks_written))
        if calls_delta <= 0 and total_exec_ms_delta <= 0:
            continue
        deltas.append(
            PgStatDeltaRow(
                queryid=row.queryid,
                calls_delta=calls_delta,
                total_exec_ms_delta=total_exec_ms_delta,
                mean_exec_ms_after=row.mean_exec_ms,
                rows_delta=rows_delta,
                shared_blks_hit_delta=shared_blks_hit_delta,
                shared_blks_read_delta=shared_blks_read_delta,
                temp_blks_read_delta=temp_blks_read_delta,
                temp_blks_written_delta=temp_blks_written_delta,
                query_sample=row.query_sample,
            )
        )

    deltas.sort(
        key=lambda item: (
            -item.total_exec_ms_delta,
            -item.calls_delta,
            -item.shared_blks_read_delta,
            item.queryid,
        )
    )
    return deltas


def serialize_rows(rows: list[PgStatStatementRow]) -> list[dict[str, object]]:
    return [asdict(row) for row in rows]


def serialize_deltas(rows: list[PgStatDeltaRow]) -> list[dict[str, object]]:
    return [asdict(row) for row in rows]


def save_snapshot_json(path: Path, rows: list[PgStatStatementRow]) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rows": serialize_rows(rows),
    }
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def render_pg_stat_markdown(
    *,
    rows: list[PgStatStatementRow],
    label: str,
    profile: str | None = None,
) -> str:
    title = "# pg_stat_statements snapshot"
    if profile:
        title += f" ({profile})"
    lines = [
        title,
        f"# label: {label}",
        f"# gerado em {datetime.now(timezone.utc).isoformat()}",
        "",
        "queryid | calls | total_exec_ms | mean_exec_ms | rows | shared_blks_hit | shared_blks_read | temp_blks_read | temp_blks_written | query_sample",
    ]
    for row in rows:
        lines.append(
            " | ".join(
                [
                    row.queryid,
                    str(row.calls),
                    f"{row.total_exec_ms:.3f}",
                    f"{row.mean_exec_ms:.3f}",
                    str(row.rows),
                    str(row.shared_blks_hit),
                    str(row.shared_blks_read),
                    str(row.temp_blks_read),
                    str(row.temp_blks_written),
                    row.query_sample,
                ]
            )
        )
    return "\n".join(lines) + "\n"


def render_pg_stat_delta_markdown(
    *,
    rows: list[PgStatDeltaRow],
    label: str,
    profile: str | None = None,
) -> str:
    title = "# pg_stat_statements delta"
    if profile:
        title += f" ({profile})"
    lines = [
        title,
        f"# label: {label}",
        f"# gerado em {datetime.now(timezone.utc).isoformat()}",
        "",
        "queryid | calls_delta | total_exec_ms_delta | mean_exec_ms_after | rows_delta | shared_blks_hit_delta | shared_blks_read_delta | temp_blks_read_delta | temp_blks_written_delta | query_sample",
    ]
    for row in rows:
        lines.append(
            " | ".join(
                [
                    row.queryid,
                    str(row.calls_delta),
                    f"{row.total_exec_ms_delta:.3f}",
                    f"{row.mean_exec_ms_after:.3f}",
                    str(row.rows_delta),
                    str(row.shared_blks_hit_delta),
                    str(row.shared_blks_read_delta),
                    str(row.temp_blks_read_delta),
                    str(row.temp_blks_written_delta),
                    row.query_sample,
                ]
            )
        )
    return "\n".join(lines) + "\n"


def _default_output_name(*, label: str, profile: str | None = None) -> str:
    if profile:
        return f"pg_stat_statements_{profile}_{label}.md"
    return f"pg_stat_statements_top10_{label}.txt"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="current", help="Sufixo do arquivo: before, after ou current")
    parser.add_argument("--profile", default=None, help="Perfil opcional de filtro de queries.")
    parser.add_argument("--limit", type=int, default=10, help="Quantidade maxima de rows no snapshot.")
    parser.add_argument("--snapshot-json", default=None, help="Arquivo JSON opcional com o snapshot bruto.")
    parser.add_argument(
        "--out-dir",
        default=os.getenv("LEADS_AUDIT_EVIDENCE_DIR", str(DEFAULT_OUT_DIR)),
        help="Diretorio versionado para salvar evidencia.",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / _default_output_name(label=args.label, profile=args.profile)

    with build_engine(_url()).connect() as conn:
        if not pg_stat_statements_installed(conn):
            lines = [
                "# pg_stat_statements snapshot",
                f"# label: {args.label}",
                f"# gerado em {datetime.now(timezone.utc).isoformat()}",
                "",
                "ERRO: pg_stat_statements nao esta instalado no banco alvo.",
            ]
            out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
            print(f"Escrito: {out_file}")
            raise SystemExit(1)
        rows = fetch_pg_stat_statements_rows(conn, profile=args.profile, limit=args.limit)

    out_file.write_text(
        render_pg_stat_markdown(rows=rows, label=args.label, profile=args.profile),
        encoding="utf-8",
    )
    print(f"Escrito: {out_file}")

    if args.snapshot_json:
        snapshot_path = Path(args.snapshot_json)
        if not snapshot_path.is_absolute():
            snapshot_path = out_dir / snapshot_path
        save_snapshot_json(snapshot_path, rows)
        print(f"Escrito: {snapshot_path}")


if __name__ == "__main__":
    main()
