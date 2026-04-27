"""Cruza leads 'sem conexao com evento' (dashboard etario) com CPF de leads ja vinculados.

Usa a mesma consolidacao que `build_age_analysis`: lead_evento, batches GOLD e
backfill por nome do evento (quando habilitado via env).

Exemplo:

    cd backend
    $env:PYTHONPATH="..;$PWD"; python -m scripts.report_orphan_lead_cpf_dedupe

    python -m scripts.report_orphan_lead_cpf_dedupe --csv ../artifacts/orphan_cpf_bridge.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from sqlmodel import Session, create_engine, select

BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE_DIR.parent
DEFAULT_ENV = BASE_DIR / ".env"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.models.models import Lead, Usuario, UsuarioTipo  # noqa: E402
from app.schemas.dashboard import AgeAnalysisQuery  # noqa: E402
from app.services.dashboard_service import (  # noqa: E402
    _agency_lead_scope_predicate,
    _build_event_filters,
    _build_lead_filters,
    load_age_analysis_link_facts,
)


def _synthetic_user(tipo: str, agencia_id: int | None) -> Usuario:
    tipo_map = {
        "bb": UsuarioTipo.BB,
        "npbb": UsuarioTipo.NPBB,
        "agencia": UsuarioTipo.AGENCIA,
    }
    resolved = tipo_map.get(tipo.lower())
    if resolved is None:
        raise SystemExit(f"usuario-tipo invalido: {tipo} (use bb, npbb ou agencia)")
    return Usuario(
        email="orphan.cpf.report@npbb.local",
        password_hash="script-only",
        tipo_usuario=resolved,
        agencia_id=agencia_id,
        ativo=True,
    )


def _parse_date(value: str) -> date:
    y, m, d = value.strip().split("-", 2)
    return date(int(y), int(m), int(d))


def _nonempty_cpf(cpf: str | None) -> bool:
    if cpf is None:
        return False
    return str(cpf).strip() != ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Relatorio: orfaos do dashboard com CPF igual a lead ja vinculado a evento."
    )
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV)
    parser.add_argument("--usuario-tipo", default="npbb", help="bb | npbb | agencia")
    parser.add_argument("--agencia-id", type=int, default=None)
    parser.add_argument("--data-inicio", type=str, default=None, help="YYYY-MM-DD")
    parser.add_argument("--data-fim", type=str, default=None, help="YYYY-MM-DD")
    parser.add_argument("--evento-id", type=int, default=None)
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Grava uma linha por orfao com CPF e matches (lead/evento vinculados).",
    )
    args = parser.parse_args()
    load_dotenv(args.env_file)

    url = (
        os.getenv("DIRECT_URL")
        or os.getenv("WORKER_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or ""
    ).strip()
    if not url:
        raise SystemExit("Defina DIRECT_URL ou DATABASE_URL.")
    if args.usuario_tipo.lower() == "agencia" and args.agencia_id is None:
        raise SystemExit("Para usuario-tipo=agencia informe --agencia-id.")

    params = AgeAnalysisQuery(
        data_inicio=_parse_date(args.data_inicio) if args.data_inicio else None,
        data_fim=_parse_date(args.data_fim) if args.data_fim else None,
        evento_id=args.evento_id,
    )
    current_user = _synthetic_user(args.usuario_tipo, args.agencia_id)

    engine = create_engine(url, pool_pre_ping=True)
    with Session(engine) as session:
        link_facts = load_age_analysis_link_facts(session, params, current_user)
        connected_ids: set[int] = {f.lead_id for f in link_facts}
        events_by_lead: dict[int, list[tuple[int, str]]] = defaultdict(list)
        for f in link_facts:
            events_by_lead[f.lead_id].append((f.evento_id, f.evento_nome))

        lead_filters = _build_lead_filters(params)
        event_filters = _build_event_filters(params, current_user)
        conditions: list = [*lead_filters]
        if current_user.tipo_usuario == UsuarioTipo.AGENCIA:
            conditions.append(_agency_lead_scope_predicate(event_filters))
        if connected_ids:
            conditions.append(Lead.id.not_in(connected_ids))

        orphans = session.exec(select(Lead).where(*conditions)).all()

        orphans_total = len(orphans)
        orphans_with_cpf = [o for o in orphans if _nonempty_cpf(o.cpf)]
        owc_n = len(orphans_with_cpf)

        cpf_set = {str(o.cpf).strip() for o in orphans_with_cpf}
        connected_by_cpf: dict[str, list[int]] = defaultdict(list)
        if cpf_set and connected_ids:
            rows = session.exec(
                select(Lead.id, Lead.cpf).where(
                    Lead.id.in_(connected_ids),
                    Lead.cpf.is_not(None),
                )
            ).all()
            for lid, cpf in rows:
                if cpf is None or str(cpf).strip() == "":
                    continue
                key = str(cpf).strip()
                if key in cpf_set:
                    connected_by_cpf[key].append(int(lid))

        matches: list[dict[str, object]] = []
        for o in orphans_with_cpf:
            key = str(o.cpf).strip()
            matched_leads = connected_by_cpf.get(key, [])
            if not matched_leads:
                continue
            event_pairs: list[tuple[int, str]] = []
            for lid in matched_leads:
                event_pairs.extend(events_by_lead.get(lid, []))
            matches.append(
                {
                    "orphan_lead_id": o.id,
                    "cpf": key,
                    "orphan_nome": (o.nome or "").strip(),
                    "orphan_sobrenome": (o.sobrenome or "").strip(),
                    "orphan_evento_nome": (o.evento_nome or "").strip(),
                    "matched_connected_lead_ids": sorted(set(matched_leads)),
                    "matched_evento_ids": sorted({eid for eid, _ in event_pairs}),
                    "matched_evento_nomes": sorted({nome for _, nome in event_pairs}),
                }
            )

        match_n = len(matches)
        summary = {
            "filters": {
                "data_inicio": params.data_inicio.isoformat() if params.data_inicio else None,
                "data_fim": params.data_fim.isoformat() if params.data_fim else None,
                "evento_id": params.evento_id,
                "usuario_tipo": args.usuario_tipo,
            },
            "connected_distinct_leads": len(connected_ids),
            "orphans_sem_conexao_total": orphans_total,
            "orphans_com_cpf": owc_n,
            "orphans_com_cpf_com_match_em_lead_vinculado": match_n,
            "pct_dos_orfaos_com_cpf_com_match": round(
                (match_n / owc_n) * 100, 2
            )
            if owc_n
            else 0.0,
            "pct_dos_orfaos_totais_com_match": round(
                (match_n / orphans_total) * 100, 2
            )
            if orphans_total
            else 0.0,
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))

        if args.csv and matches:
            args.csv.parent.mkdir(parents=True, exist_ok=True)
            fieldnames = [
                "orphan_lead_id",
                "cpf",
                "orphan_nome",
                "orphan_sobrenome",
                "orphan_evento_nome",
                "matched_connected_lead_ids",
                "matched_evento_ids",
                "matched_evento_nomes",
            ]
            with args.csv.open("w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=fieldnames)
                w.writeheader()
                for row in matches:
                    out = dict(row)
                    mcl = row["matched_connected_lead_ids"]
                    mei = row["matched_evento_ids"]
                    men = row["matched_evento_nomes"]
                    assert isinstance(mcl, list)
                    assert isinstance(mei, list)
                    assert isinstance(men, list)
                    out["matched_connected_lead_ids"] = ";".join(str(x) for x in mcl)
                    out["matched_evento_ids"] = ";".join(str(x) for x in mei)
                    out["matched_evento_nomes"] = ";".join(str(x) for x in men)
                    w.writerow(out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
