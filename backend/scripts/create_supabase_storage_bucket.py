"""Cria bucket no Supabase Storage se ainda nao existir (API de gestao).

Requer:
  SUPABASE_URL (ou SUPABASE_STORAGE_URL) — base https://<ref>.supabase.co
  SUPABASE_SERVICE_ROLE_KEY ou SUPABASE_STORAGE_SERVICE_ROLE_KEY

Uso:
  python scripts/create_supabase_storage_bucket.py
  python scripts/create_supabase_storage_bucket.py --bucket meu-bucket

Nao grava segredos; falha com instrucao clara se variaveis faltarem.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
for env_path in (BASE_DIR / ".env", BASE_DIR.parent / ".env"):
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    load_dotenv()


def _base_url() -> str:
    raw = (
        os.getenv("SUPABASE_STORAGE_URL")
        or os.getenv("SUPABASE_URL")
        or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        or ""
    ).strip().rstrip("/")
    if not raw:
        raise SystemExit(
            "Defina SUPABASE_URL ou SUPABASE_STORAGE_URL (ex.: https://xxxx.supabase.co)."
        )
    return raw


def _service_key() -> str:
    key = (
        os.getenv("SUPABASE_STORAGE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or ""
    ).strip()
    if not key:
        raise SystemExit("Defina SUPABASE_SERVICE_ROLE_KEY (service role) para criar bucket.")
    return key


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria bucket no Supabase Storage.")
    parser.add_argument(
        "--bucket",
        default=os.getenv("OBJECT_STORAGE_BUCKET", "lead-imports").strip() or "lead-imports",
        help="Id do bucket (default: OBJECT_STORAGE_BUCKET ou lead-imports)",
    )
    parser.add_argument(
        "--public",
        action="store_true",
        help="Cria bucket publico (default: privado)",
    )
    args = parser.parse_args()

    base = _base_url()
    key = _service_key()
    url = f"{base}/storage/v1/bucket"
    headers = {
        "Authorization": f"Bearer {key}",
        "apikey": key,
        "Content-Type": "application/json",
    }
    body = {"id": args.bucket, "name": args.bucket, "public": bool(args.public)}

    with httpx.Client(timeout=30.0) as client:
        r = client.post(url, headers=headers, json=body)
        if r.status_code in (200, 201):
            print(f"Bucket {args.bucket!r} criado ou atualizado com sucesso.")
            return
        if r.status_code == 409 or "already exists" in (r.text or "").lower():
            print(f"Bucket {args.bucket!r} ja existe — nada a fazer.")
            return
        print(f"Falha HTTP {r.status_code}: {r.text[:500]}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
