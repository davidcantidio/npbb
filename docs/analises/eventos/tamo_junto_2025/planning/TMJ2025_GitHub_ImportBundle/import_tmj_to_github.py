#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Importa épicos e issues do TMJ 2025 para um repositório GitHub e, opcionalmente,
adiciona tudo ao GitHub Project (ProjectV2) via GitHub CLI.

Pré-requisitos:
- GitHub CLI instalado: https://cli.github.com/
- Autenticado: gh auth login
- Se for adicionar ao Project: gh auth refresh -s project

Uso típico:
  python import_tmj_to_github.py --repo davidcantidio/npbb \
    --project "Fechamento de Eventos" \
    --csv TMJ2025_GitHub_Issues.csv

Modo dry-run:
  python import_tmj_to_github.py --repo ... --csv ... --dry-run

Observações:
- O script cria labels se não existirem (ou atualiza se existirem).
- Cria primeiro os épicos, depois as tasks, e coloca link do épico na descrição da task.
- Não cria "sprints" nativos; usa label sprint-1, sprint-2, etc.
'''
from __future__ import annotations

import argparse
import csv
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Iterable


URL_RE = re.compile(r"https?://github\.com/\S+")


@dataclass
class Row:
    work_item_id: int
    parent_work_item_id: Optional[int]
    kind: str  # epic | task
    title: str
    body: str
    labels: List[str]
    sprint: str


def run(cmd: List[str], *, stdin_text: Optional[str] = None, dry_run: bool = False) -> str:
    """Run a shell command and return stdout (raises on error)."""
    if dry_run:
        print("[dry-run]", " ".join(cmd))
        return ""

    p = subprocess.run(
        cmd,
        input=stdin_text,
        text=True,
        capture_output=True,
    )
    if p.returncode != 0:
        raise RuntimeError(
            f"Command failed ({p.returncode}): {' '.join(cmd)}\n"
            f"STDOUT:\n{p.stdout}\n\nSTDERR:\n{p.stderr}"
        )
    return p.stdout.strip()


def read_rows(csv_path: str) -> List[Row]:
    """Load rows from the prepared CSV export."""
    rows: List[Row] = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"work_item_id", "parent_work_item_id", "kind", "title", "body", "labels", "sprint"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV faltando colunas: {sorted(missing)}")

        for r in reader:
            wid = int(r["work_item_id"])
            parent_raw = (r.get("parent_work_item_id") or "").strip()
            parent = int(parent_raw) if parent_raw else None
            labels = [x.strip() for x in (r.get("labels") or "").split(",") if x.strip()]
            rows.append(
                Row(
                    work_item_id=wid,
                    parent_work_item_id=parent,
                    kind=(r.get("kind") or "").strip(),
                    title=(r.get("title") or "").strip(),
                    body=(r.get("body") or "").rstrip(),
                    labels=labels,
                    sprint=(r.get("sprint") or "").strip(),
                )
            )
    return rows


def ensure_labels(repo: str, labels: Iterable[str], *, dry_run: bool = False) -> None:
    """Create/update labels in the target repo so issue creation won't fail."""
    for lab in sorted(set(labels)):
        if not lab:
            continue
        # gh label create <name> -R <repo> -f
        run(["gh", "label", "create", lab, "-R", repo, "-f"], dry_run=dry_run)


def create_issue(
    repo: str,
    *,
    title: str,
    body: str,
    labels: List[str],
    project: Optional[str],
    dry_run: bool = False,
) -> str:
    """Create a GitHub issue and return its URL."""
    cmd = ["gh", "issue", "create", "-R", repo, "--title", title, "--body-file", "-"]
    for lab in labels:
        cmd.extend(["--label", lab])
    if project:
        cmd.extend(["--project", project])

    out = run(cmd, stdin_text=body, dry_run=dry_run)
    m = URL_RE.search(out)
    if not m:
        if dry_run:
            return ""
        raise RuntimeError(f"Não consegui extrair URL da issue criada. Saída:\n{out}")
    return m.group(0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="Repo destino, ex: davidcantidio/npbb")
    ap.add_argument("--project", default="", help='Título do GitHub Project para adicionar as issues (opcional).')
    ap.add_argument("--csv", required=True, help="CSV preparado (TMJ2025_GitHub_Issues.csv)")
    ap.add_argument("--dry-run", action="store_true", help="Não cria nada; só mostra comandos.")
    ap.add_argument("--only-epics", action="store_true", help="Cria apenas épicos (debug).")
    ap.add_argument("--limit", type=int, default=0, help="Limita a quantidade de issues criadas (debug).")
    args = ap.parse_args()

    project = args.project.strip() or None

    rows = read_rows(args.csv)
    epics = [r for r in rows if r.kind.lower() == "epic"]
    tasks = [r for r in rows if r.kind.lower() != "epic"]

    all_labels: List[str] = []
    for r in rows:
        all_labels.extend(r.labels)
    ensure_labels(args.repo, all_labels, dry_run=args.dry_run)

    created: Dict[int, str] = {}

    print(f"Criando {len(epics)} épicos...")
    for i, r in enumerate(epics, start=1):
        if args.limit and (len(created) >= args.limit):
            break
        url = create_issue(
            args.repo,
            title=r.title,
            body=r.body,
            labels=r.labels,
            project=project,
            dry_run=args.dry_run,
        )
        created[r.work_item_id] = url
        print(f"[epic {i}/{len(epics)}] {r.title} -> {url}")

    if args.only_epics:
        print("only-epics ativado; parando aqui.")
        return 0

    print(f"Criando {len(tasks)} tasks...")
    for i, r in enumerate(tasks, start=1):
        if args.limit and (len(created) >= args.limit):
            break

        body = r.body
        if r.parent_work_item_id and r.parent_work_item_id in created and created[r.parent_work_item_id]:
            body = body.rstrip() + f"\n**Link do épico (GitHub):** {created[r.parent_work_item_id]}\n"

        url = create_issue(
            args.repo,
            title=r.title,
            body=body,
            labels=r.labels,
            project=project,
            dry_run=args.dry_run,
        )
        created[r.work_item_id] = url
        print(f"[task {i}/{len(tasks)}] {r.title} -> {url}")

    out_map = os.path.join(os.path.dirname(args.csv), "TMJ2025_GitHub_created_map.csv")
    if not args.dry_run:
        with open(out_map, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["work_item_id", "github_url"])
            for wid, url in sorted(created.items(), key=lambda x: x[0]):
                w.writerow([wid, url])
        print(f"Mapa gerado: {out_map}")

    print("Fim.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Cancelado.")
        raise
    except Exception as e:
        print(str(e), file=sys.stderr)
        raise
