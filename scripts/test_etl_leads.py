#!/usr/bin/env python3
"""
Script para testar o mecanismo ETL de leads na seção Leads.

Uso:
  PYTHONPATH=/workspace:/workspace/backend python scripts/test_etl_leads.py [caminho_arquivo.xlsx]

Se nenhum arquivo for passado, usa o fixture lead_import_sample.xlsx dos testes.
Exemplo com o arquivo Park Challenge:
  python scripts/test_etl_leads.py "25_Park Challenge_Base de Leads_Banco do Brasil_05_11.xlsx"
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date
from pathlib import Path

# Garante PYTHONPATH para imports (inclui PROJETOS para lead_pipeline)
WORKSPACE = Path(__file__).resolve().parent.parent
for p in [str(WORKSPACE), str(WORKSPACE / "backend"), str(WORKSPACE / "PROJETOS")]:
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault("SECRET_KEY", "test-etl-secret")
os.environ.setdefault("TESTING", "true")


def run_etl_test(file_path: Path) -> bool:
    from io import BytesIO

    from fastapi.testclient import TestClient
    from sqlalchemy.pool import StaticPool
    from sqlmodel import Session, SQLModel, create_engine, select

    from app.db.database import get_session
    from app.main import app
    from app.models.models import Evento, Lead, StatusEvento, Usuario
    from app.utils.security import hash_password

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with Session(engine) as s:
        for nome in ["Previsto", "A Confirmar", "Confirmado", "Realizado", "Cancelado"]:
            if not s.exec(select(StatusEvento).where(StatusEvento.nome == nome)).first():
                s.add(StatusEvento(nome=nome))
        s.commit()

        status = s.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
        evento = Evento(
            nome="Park Challenge - Teste ETL",
            cidade="Brasilia",
            estado="DF",
            concorrencia=False,
            data_inicio_prevista=date(2099, 1, 1),
            status_id=status.id,
        )
        s.add(evento)
        s.commit()
        s.refresh(evento)
        evento_id = evento.id

        test_password = os.environ.get("ETL_TEST_PASSWORD", "test-etl-pwd")
        user = Usuario(
            email="etl-test@npbb.com.br",
            password_hash=hash_password(test_password),
            tipo_usuario="npbb",
            ativo=True,
        )
        s.add(user)
        s.commit()
        s.refresh(user)

    with TestClient(app) as client:
        login = client.post("/auth/login", json={"email": user.email, "password": test_password})
        if login.status_code != 200:
            print(f"ERRO: Falha no login: {login.json()}")
            return False
        token = login.json()["access_token"]

        with file_path.open("rb") as fh:
            file_bytes = fh.read()
        filename = file_path.name

        print(f"\n=== ETL Preview: {filename} ===")
        preview = client.post(
            "/leads/import/etl/preview",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": (filename, BytesIO(file_bytes), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"evento_id": str(evento_id), "strict": "false"},
        )

        if preview.status_code != 200:
            print(f"ERRO Preview ({preview.status_code}): {preview.json()}")
            return False

        p = preview.json()
        session_token = p["session_token"]
        print(f"  session_token: {session_token[:20]}...")
        print(f"  total_rows: {p['total_rows']}")
        print(f"  valid_rows: {p['valid_rows']}")
        print(f"  invalid_rows: {p['invalid_rows']}")
        if p.get("dq_report"):
            for item in p["dq_report"][:5]:
                print(f"  DQ: [{item.get('severity', '?')}] {item.get('check_name', '?')} - {item.get('affected_rows', 0)} linhas")

        print(f"\n=== ETL Commit ===")
        commit = client.post(
            "/leads/import/etl/commit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "session_token": session_token,
                "evento_id": evento_id,
                "force_warnings": True,
            },
        )

        if commit.status_code != 200:
            print(f"ERRO Commit ({commit.status_code}): {commit.json()}")
            return False

        c = commit.json()
        print(f"  status: {c['status']}")
        print(f"  created: {c['created']}")
        print(f"  updated: {c['updated']}")
        print(f"  skipped: {c['skipped']}")
        print(f"  errors: {c['errors']}")

        with Session(engine) as s:
            leads = s.exec(select(Lead)).all()
            print(f"\n  Total de leads no banco: {len(leads)}")

    app.dependency_overrides.clear()
    print("\n=== ETL de leads: OK ===\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Testa o ETL de leads com um arquivo XLSX")
    parser.add_argument(
        "arquivo",
        nargs="?",
        default=None,
        help="Caminho do arquivo XLSX (ex: 25_Park Challenge_Base de Leads_Banco do Brasil_05_11.xlsx)",
    )
    args = parser.parse_args()

    if args.arquivo:
        file_path = Path(args.arquivo)
        if not file_path.is_absolute():
            file_path = (WORKSPACE / args.arquivo).resolve()
    else:
        file_path = WORKSPACE / "backend" / "tests" / "fixtures" / "lead_import_sample.xlsx"

    if not file_path.exists():
        print(f"Arquivo nao encontrado: {file_path}")
        print("\nColoque o arquivo no workspace e informe o caminho, por exemplo:")
        print('  python scripts/test_etl_leads.py "25_Park Challenge_Base de Leads_Banco do Brasil_05_11.xlsx"')
        sys.exit(1)

    if file_path.suffix.lower() != ".xlsx":
        print("O ETL de leads suporta apenas arquivos .xlsx")
        sys.exit(1)

    ok = run_etl_test(file_path)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
