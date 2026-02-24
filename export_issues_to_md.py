#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def run_gh(args: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["gh"] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

def safe_filename(s: str, max_len: int = 80) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_-]+", "-", s, flags=re.UNICODE).strip("-")
    if not s:
        return "untitled"
    return s[:max_len]


def to_iso(dt: Optional[str]) -> Optional[str]:
    # gh usually returns ISO already; keep as-is if parse fails
    if not dt:
        return None
    try:
        # Accept "2026-02-17T11:47:00Z" etc.
        datetime.fromisoformat(dt.replace("Z", "+00:00"))
        return dt
    except Exception:
        return dt


def md_escape_yaml(s: str) -> str:
    # Minimal YAML-safe quoting
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def extract_names(items: Any, key: str = "login") -> List[str]:
    if not items:
        return []
    out = []
    for it in items:
        if isinstance(it, dict) and it.get(key):
            out.append(str(it[key]))
    return out


def format_comments(comments: Any, max_comments: int, max_chars: int) -> str:
    if not comments:
        return "_(sem comentários capturados)_\n"

    # comments can be either a list or {nodes:[...]}
    if isinstance(comments, dict) and "nodes" in comments:
        comments_list = comments.get("nodes") or []
    elif isinstance(comments, list):
        comments_list = comments
    else:
        comments_list = []

    if not comments_list:
        return "_(sem comentários capturados)_\n"

    # Keep last max_comments (most useful for “latest decisions”)
    comments_list = comments_list[-max_comments:]

    blocks = []
    for c in comments_list:
        author = (c.get("author") or {}).get("login") if isinstance(c, dict) else None
        created = to_iso(c.get("createdAt")) if isinstance(c, dict) else None
        body = (c.get("body") or "").strip() if isinstance(c, dict) else ""
        if max_chars and len(body) > max_chars:
            body = body[: max_chars - 3].rstrip() + "..."

        header = f"### Comentário — {author or 'desconhecido'} — {created or ''}".rstrip()
        blocks.append(f"{header}\n\n{body or '_[vazio]_'}\n")
    return "\n".join(blocks).strip() + "\n"


def build_markdown(issue: Dict[str, Any], repo: str, codex_instructions: str,
                   max_comments: int, max_comment_chars: int) -> str:
    number = issue.get("number")
    title = issue.get("title") or ""
    url = issue.get("url") or ""
    state = issue.get("state") or ""
    body = (issue.get("body") or "").strip()

    labels = extract_names(issue.get("labels") or [], key="name")
    assignees = extract_names(issue.get("assignees") or [], key="login")
    milestone = (issue.get("milestone") or {}).get("title") if isinstance(issue.get("milestone"), dict) else None

    created_at = to_iso(issue.get("createdAt"))
    updated_at = to_iso(issue.get("updatedAt"))

    comments_md = format_comments(issue.get("comments"), max_comments=max_comments, max_chars=max_comment_chars)

    fm_lines = [
        "---",
        "source: github_issue",
        f"repo: {md_escape_yaml(repo)}",
        f"issue_number: {number}",
        f"title: {md_escape_yaml(title)}",
        f"url: {md_escape_yaml(url)}",
        f"state: {md_escape_yaml(state)}",
        f"labels: [{', '.join(md_escape_yaml(x) for x in labels)}]",
        f"assignees: [{', '.join(md_escape_yaml(x) for x in assignees)}]",
        f"milestone: {md_escape_yaml(milestone) if milestone else 'null'}",
        f"created_at: {md_escape_yaml(created_at) if created_at else 'null'}",
        f"updated_at: {md_escape_yaml(updated_at) if updated_at else 'null'}",
        "---",
        "",
    ]

    md = []
    md.extend(fm_lines)
    md.append(f"# Issue #{number} — {title}\n")
    md.append("## Link\n")
    md.append(f"- {url}\n")
    md.append("## Prompt para Codex\n")
    md.append(codex_instructions.strip() + "\n")
    md.append("## Conteúdo da issue (body)\n")
    md.append(body if body else "_(sem body)_")
    md.append("\n\n## Comentários (últimos)\n")
    md.append(comments_md)
    md.append("\n## Checklist de entrega (preencher/validar)\n")
    md.append("- [ ] Implementação completa conforme descrito acima\n"
              "- [ ] Testes adicionados/atualizados (quando aplicável)\n"
              "- [ ] `lint/format` ok\n"
              "- [ ] Sem gambiarras silenciosas (se tiver workaround, documentar)\n")
    return "\n".join(md).rstrip() + "\n"


DEFAULT_CODEX_INSTRUCTIONS = """
Você é um agente de implementação (Codex).
Objetivo: implementar exatamente o que esta issue pede, com o menor trabalho manual possível.

Regras:
1) Se faltar contexto técnico (paths, nomes de módulos, convenções), faça a busca no repositório e assuma o padrão dominante.
2) Se a issue tiver critérios de aceitação implícitos, traduza em checklist e/ou testes.
3) Entregue mudanças pequenas e seguras (commits atômicos), sem “refatoração hobby”.
4) Se houver ambiguidade, tome a decisão mais conservadora e documente no PR/nota.

Saída esperada:
- Código implementado + testes (quando fizer sentido)
- Notas rápidas: o que mudou, como validar, riscos/limitações
""".strip()


def main():
    p = argparse.ArgumentParser(description="Exporta issues do GitHub (range numérico) para .md (prompts p/ Codex).")
    p.add_argument("--repo", required=True, help="owner/repo (ex: minhaorg/meurepo)")
    p.add_argument("--start", type=int, required=True, help="número inicial (inclusive)")
    p.add_argument("--end", type=int, required=True, help="número final (inclusive)")
    p.add_argument("--out", default="issues_md", help="pasta de saída")
    p.add_argument("--include-title-in-filename", action="store_true",
                   help="inclui slug do título no nome do arquivo (mais bonito, mais propenso a path longo)")
    p.add_argument("--max-comments", type=int, default=15, help="quantos comentários finais incluir")
    p.add_argument("--max-comment-chars", type=int, default=6000, help="limite de caracteres por comentário (0 = sem limite)")
    p.add_argument("--codex-instructions-file", default=None,
                   help="arquivo .txt/.md com instruções customizadas pro Codex (substitui o padrão)")
    args = p.parse_args()

    start, end = sorted([args.start, args.end])
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    codex_instructions = DEFAULT_CODEX_INSTRUCTIONS
    if args.codex_instructions_file:
        codex_instructions = Path(args.codex_instructions_file).read_text(encoding="utf-8")

    index_lines = [
        f"# Export de issues — {args.repo}",
        f"Range: #{start}–#{end}",
        "",
        "| Issue | State | Title | Arquivo |",
        "|---:|:---:|---|---|",
    ]

    fields = ",".join([
        "number", "title", "url", "state", "body",
        "labels", "assignees", "milestone", "createdAt", "updatedAt",
        "comments"
    ])

    missing = []
    exported = 0

    for n in range(start, end + 1):
        proc = run_gh(["issue", "view", str(n), "--repo", args.repo, "--json", fields])
        if proc.returncode != 0:
            missing.append(n)
            continue

        try:
            issue = json.loads(proc.stdout)
        except json.JSONDecodeError:
            missing.append(n)
            continue

        title = issue.get("title") or ""
        fname_base = f"{n:04d}"
        if args.include_title_in_filename:
            fname_base += f"-{safe_filename(title)}"

        md_path = out_dir / f"{fname_base}.md"
        md = build_markdown(
            issue=issue,
            repo=args.repo,
            codex_instructions=codex_instructions,
            max_comments=args.max_comments,
            max_comment_chars=args.max_comment_chars,
        )
        md_path.write_text(md, encoding="utf-8")

        exported += 1
        index_lines.append(
            f"| #{issue.get('number')} | {issue.get('state')} | {title.replace('|','\\|')} | `{md_path.name}` |"
        )

    index_path = out_dir / "index.md"
    index_path.write_text("\n".join(index_lines).rstrip() + "\n", encoding="utf-8")

    if missing:
        (out_dir / "missing.txt").write_text("\n".join(map(str, missing)) + "\n", encoding="utf-8")

    print(f"Exportadas: {exported} issues em: {out_dir.resolve()}")
    if missing:
        print(f"Faltando/indisponíveis: {len(missing)} (ver {out_dir / 'missing.txt'})")


if __name__ == "__main__":
    main()