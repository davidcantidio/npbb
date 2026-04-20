"""Gera EXPLAIN ANALYZE para consultas criticas de leads (artefato pos-deploy).

Escreve em artifacts_migracao/explain_leads_critical_output.txt (cria o diretorio).
Requer DIRECT_URL ou DATABASE_URL apontando para Postgres (nao sqlite).

Uso:
  python scripts/run_critical_explains.py
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import sqlalchemy as sa
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE_DIR.parent
OUT_DIR = REPO_ROOT / "artifacts_migracao"
OUT_FILE = OUT_DIR / "explain_leads_critical_output.txt"

for env_path in (BASE_DIR / ".env", REPO_ROOT / ".env"):
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    load_dotenv()


def _url() -> str:
    u = (os.getenv("DIRECT_URL") or os.getenv("DATABASE_URL") or "").strip()
    if not u or u.startswith("sqlite"):
        raise SystemExit("Defina DIRECT_URL ou DATABASE_URL (Postgres) para rodar EXPLAIN.")
    return u


def main() -> None:
    url = _url()
    connect_args: dict = {"connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "30"))}
    if (
        "sslmode=" not in url
        and "ssl=require" not in url
        and "127.0.0.1" not in url
        and "localhost" not in url
    ):
        connect_args["sslmode"] = "require"
    engine = sa.create_engine(url, connect_args=connect_args)

    lines: list[str] = []
    lines.append(f"# gerado em {datetime.now(timezone.utc).isoformat()}")
    lines.append("")

    with engine.connect() as conn:
        batch_id = conn.execute(sa.text("SELECT id FROM lead_batches ORDER BY id DESC LIMIT 1")).scalar()
        evento_id = conn.execute(sa.text("SELECT id FROM evento ORDER BY id DESC LIMIT 1")).scalar()
        if not batch_id:
            lines.append("# Sem lead_batches — pulando explains que dependem de batch_id.")
        if not evento_id:
            lines.append("# Sem evento — pulando explains que dependem de evento_id.")

        def run(title: str, sql: str, params: dict | None = None) -> None:
            lines.append(f"## {title}")
            lines.append("")
            explain = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) {sql}"
            try:
                res = conn.execute(sa.text(explain), params or {})
                for row in res:
                    lines.append(row[0])
            except Exception as exc:  # noqa: BLE001
                lines.append(f"ERRO: {exc}")
            lines.append("")

        if batch_id:
            run(
                "lead_batches metadados (sem TOAST de arquivo_bronze)",
                """
                SELECT id, enviado_por, evento_id, nome_arquivo_original, arquivo_sha256, stage,
                       bronze_storage_bucket, bronze_storage_key, bronze_size_bytes
                FROM lead_batches WHERE id = :bid
                """,
                {"bid": batch_id},
            )
            run(
                "leads_silver ordenado por row_index (batch)",
                """
                SELECT id, batch_id, row_index FROM leads_silver
                WHERE batch_id = :bid ORDER BY row_index LIMIT 200
                """,
                {"bid": batch_id},
            )

        if evento_id:
            start = datetime.now(timezone.utc) - timedelta(days=30)
            end = datetime.now(timezone.utc) + timedelta(days=1)
            run(
                "dashboard-style: contagem por evento com filtro de data em lead.data_criacao (faixa)",
                """
                SELECT count(*) AS n
                FROM lead_evento le
                INNER JOIN evento e ON e.id = le.evento_id
                INNER JOIN lead l ON l.id = le.lead_id
                WHERE le.evento_id = :eid
                  AND l.data_criacao >= :start_at
                  AND l.data_criacao < :end_at
                """,
                {"eid": evento_id, "start_at": start, "end_at": end},
            )

        run(
            "indice parcial data_compra (amostra: ultimos leads com data_compra)",
            """
            SELECT id, data_compra FROM lead
            WHERE data_compra IS NOT NULL
            ORDER BY data_compra DESC NULLS LAST
            LIMIT 50
            """,
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Escrito: {OUT_FILE}")


if __name__ == "__main__":
    main()
