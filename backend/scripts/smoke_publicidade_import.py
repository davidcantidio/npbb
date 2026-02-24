"""Smoke test for publicidade import flow (API-level, MCP equivalent).

This script validates the assisted import pipeline end-to-end against a running
NPBB backend, using environment variables for credentials:

- NPBB_BASE_URL (default: http://localhost:8000)
- NPBB_TEST_EMAIL (required)
- NPBB_TEST_PASSWORD (required)
- NPBB_SMOKE_TIMEOUT_SEC (default: 20)

Flow:
1) POST /auth/login
2) GET /publicidade/referencias/eventos
3) POST /publicidade/import/preview
4) POST /publicidade/import/validate
5) POST /publicidade/import (dry_run=false)
6) Repeat import with same file name to validate idempotence

Outputs:
- concise stdout summary
- JSON report in reports/publicidade_smoke/<timestamp>.json
"""

from __future__ import annotations

import csv
import json
import os
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "reports" / "publicidade_smoke"


HEADERS = [
    "Codigo Projeto",
    "Projeto",
    "Data Vinculacao",
    "Meio",
    "Veiculo",
    "UF",
    "UF Extenso",
    "Municipio",
    "Camada",
]


MAPPINGS = [
    {"coluna": "Codigo Projeto", "campo": "codigo_projeto", "confianca": 0.99},
    {"coluna": "Projeto", "campo": "projeto", "confianca": 0.99},
    {"coluna": "Data Vinculacao", "campo": "data_veiculacao", "confianca": 0.99},
    {"coluna": "Meio", "campo": "meio", "confianca": 0.99},
    {"coluna": "Veiculo", "campo": "veiculo", "confianca": 0.99},
    {"coluna": "UF", "campo": "uf", "confianca": 0.99},
    {"coluna": "UF Extenso", "campo": "uf_extenso", "confianca": 0.95},
    {"coluna": "Municipio", "campo": "municipio", "confianca": 0.95},
    {"coluna": "Camada", "campo": "camada", "confianca": 0.99},
]


@dataclass
class RuntimeConfig:
    base_url: str
    email: str
    password: str
    timeout_sec: float


class SmokeError(RuntimeError):
    """Domain-specific error used to mark smoke execution failures."""


class ApiError(SmokeError):
    """HTTP call failed with a non-success status code."""

    def __init__(self, method: str, path: str, status: int, detail: str):
        super().__init__(f"{method} {path} -> {status}: {detail}")
        self.method = method
        self.path = path
        self.status = status
        self.detail = detail


def _read_config() -> RuntimeConfig:
    base_url = os.getenv("NPBB_BASE_URL", "http://localhost:8000").strip().rstrip("/")
    email = os.getenv("NPBB_TEST_EMAIL", "").strip()
    password = os.getenv("NPBB_TEST_PASSWORD", "")
    timeout_raw = os.getenv("NPBB_SMOKE_TIMEOUT_SEC", "20").strip()

    if not email:
        raise SmokeError("NPBB_TEST_EMAIL e obrigatorio.")
    if not password:
        raise SmokeError("NPBB_TEST_PASSWORD e obrigatorio.")
    try:
        timeout_sec = float(timeout_raw)
    except ValueError as exc:
        raise SmokeError("NPBB_SMOKE_TIMEOUT_SEC invalido.") from exc
    if timeout_sec <= 0:
        raise SmokeError("NPBB_SMOKE_TIMEOUT_SEC deve ser maior que zero.")

    return RuntimeConfig(
        base_url=base_url,
        email=email,
        password=password,
        timeout_sec=timeout_sec,
    )


def _parse_error_detail(body: bytes) -> str:
    text = body.decode("utf-8", errors="replace").strip()
    if not text:
        return "empty response body"
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text[:300]

    detail = payload.get("detail")
    if isinstance(detail, str):
        return detail
    if isinstance(detail, dict):
        message = detail.get("message")
        code = detail.get("code")
        if isinstance(message, str) and isinstance(code, str):
            return f"{code}: {message}"
        if isinstance(message, str):
            return message
    return text[:300]


def _http_json(
    config: RuntimeConfig,
    *,
    method: str,
    path: str,
    token: str | None = None,
    payload: dict[str, Any] | list[Any] | None = None,
) -> Any:
    url = f"{config.base_url}{path}"
    headers = {"Accept": "application/json"}
    data: bytes | None = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=config.timeout_sec) as response:
            raw = response.read()
            if not raw:
                return None
            return json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = _parse_error_detail(err.read())
        raise ApiError(method, path, err.code, detail) from err
    except urllib.error.URLError as err:
        raise SmokeError(f"Falha de conexao em {method} {path}: {err}") from err


def _encode_multipart(
    fields: dict[str, str],
    files: dict[str, tuple[str, bytes, str]],
) -> tuple[bytes, str]:
    boundary = f"----npbb-smoke-{uuid4().hex}"
    chunks: list[bytes] = []
    boundary_line = f"--{boundary}\r\n".encode("utf-8")

    for name, value in fields.items():
        chunks.append(boundary_line)
        chunks.append(
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8")
        )
        chunks.append(str(value).encode("utf-8"))
        chunks.append(b"\r\n")

    for name, (filename, content, content_type) in files.items():
        chunks.append(boundary_line)
        chunks.append(
            (
                f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
                f"Content-Type: {content_type}\r\n\r\n"
            ).encode("utf-8")
        )
        chunks.append(content)
        chunks.append(b"\r\n")

    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(chunks)
    return body, f"multipart/form-data; boundary={boundary}"


def _http_multipart(
    config: RuntimeConfig,
    *,
    method: str,
    path: str,
    token: str,
    fields: dict[str, str],
    files: dict[str, tuple[str, bytes, str]],
) -> Any:
    url = f"{config.base_url}{path}"
    body, content_type = _encode_multipart(fields=fields, files=files)
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Content-Type": content_type,
    }
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=config.timeout_sec) as response:
            raw = response.read()
            if not raw:
                return None
            return json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = _parse_error_detail(err.read())
        raise ApiError(method, path, err.code, detail) from err
    except urllib.error.URLError as err:
        raise SmokeError(f"Falha de conexao em {method} {path}: {err}") from err


def _build_csv_bytes(codigo_projeto: str, stamp: str) -> bytes:
    output = tempfile.SpooledTemporaryFile(mode="w+", newline="", max_size=2048)
    writer = csv.writer(output, delimiter=";", lineterminator="\n")
    writer.writerow(HEADERS)
    writer.writerow(
        [
            codigo_projeto,
            f"Projeto Smoke {stamp}",
            datetime.now(timezone.utc).date().isoformat(),
            "DIGITAL",
            "PORTAL SMOKE",
            "SP",
            "Sao Paulo",
            "Sao Paulo",
            "NACIONAL",
        ]
    )
    output.seek(0)
    data = output.read().encode("utf-8")
    output.close()
    return data


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeError(message)


def _write_report(payload: dict[str, Any], stamp: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"{stamp}.json"
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
    return path


def main() -> int:
    config = _read_config()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"publicidade_smoke_{stamp}.csv"

    report: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": config.base_url,
        "status": "running",
        "steps": {},
    }

    try:
        login_payload = _http_json(
            config,
            method="POST",
            path="/auth/login",
            payload={"email": config.email, "password": config.password},
        )
        token = str(login_payload.get("access_token") or "")
        _assert(bool(token), "Login sem access_token.")
        report["steps"]["login"] = {
            "ok": True,
            "user_id": (login_payload.get("user") or {}).get("id"),
            "email": (login_payload.get("user") or {}).get("email"),
        }

        eventos = _http_json(
            config,
            method="GET",
            path="/publicidade/referencias/eventos",
            token=token,
        )
        _assert(isinstance(eventos, list), "Resposta de referencias/eventos nao e lista.")

        selected_event = next(
            (
                evento
                for evento in eventos
                if isinstance(evento, dict) and evento.get("external_project_code")
            ),
            None,
        )
        if selected_event:
            codigo_projeto = str(selected_event["external_project_code"])
            expected_unresolved = 0
        else:
            codigo_projeto = f"SMOKE-PUB-{stamp}"
            expected_unresolved = 1

        report["steps"]["event_reference"] = {
            "ok": True,
            "available_count": len(eventos),
            "selected_event_id": (selected_event or {}).get("id"),
            "selected_external_project_code": (selected_event or {}).get("external_project_code"),
            "expected_unresolved_event_id": expected_unresolved,
        }

        csv_bytes = _build_csv_bytes(codigo_projeto=codigo_projeto, stamp=stamp)
        file_arg = {"file": (filename, csv_bytes, "text/csv")}

        preview_payload = _http_multipart(
            config,
            method="POST",
            path="/publicidade/import/preview",
            token=token,
            fields={"sample_rows": "10"},
            files=file_arg,
        )
        _assert(
            isinstance(preview_payload, dict) and "headers" in preview_payload,
            "Preview sem payload esperado.",
        )
        report["steps"]["preview"] = {
            "ok": True,
            "headers_count": len(preview_payload.get("headers") or []),
            "start_index": preview_payload.get("start_index"),
        }

        validate_payload = _http_json(
            config,
            method="POST",
            path="/publicidade/import/validate",
            token=token,
            payload=MAPPINGS,
        )
        _assert(bool(validate_payload and validate_payload.get("ok")), "Validate nao retornou ok=true.")
        report["steps"]["validate"] = {"ok": True}

        import_first = _http_multipart(
            config,
            method="POST",
            path="/publicidade/import",
            token=token,
            fields={
                "mappings_json": json.dumps(MAPPINGS, ensure_ascii=True),
                "dry_run": "false",
            },
            files=file_arg,
        )
        _assert(import_first.get("received_rows") == 1, "Primeiro import: received_rows deve ser 1.")
        _assert(import_first.get("valid_rows") == 1, "Primeiro import: valid_rows deve ser 1.")
        _assert(
            import_first.get("unresolved_event_id") == expected_unresolved,
            "Primeiro import: unresolved_event_id inesperado.",
        )
        report["steps"]["import_first"] = {"ok": True, "payload": import_first}

        import_second = _http_multipart(
            config,
            method="POST",
            path="/publicidade/import",
            token=token,
            fields={
                "mappings_json": json.dumps(MAPPINGS, ensure_ascii=True),
                "dry_run": "false",
            },
            files=file_arg,
        )
        _assert(
            int(import_second.get("staged_skipped", 0)) >= 1,
            "Segundo import: staged_skipped deve ser >= 1.",
        )
        _assert(
            int(import_second.get("upsert_inserted", -1)) == 0,
            "Segundo import: upsert_inserted deve ser 0.",
        )
        report["steps"]["import_second"] = {"ok": True, "payload": import_second}

        report["status"] = "ok"
        report_path = _write_report(report, stamp)

        print("[SMOKE] publicidade import: OK")
        print(f"[SMOKE] base_url={config.base_url}")
        print(f"[SMOKE] selected_codigo_projeto={codigo_projeto}")
        print(
            "[SMOKE] first_import "
            f"received_rows={import_first.get('received_rows')} "
            f"valid_rows={import_first.get('valid_rows')} "
            f"unresolved_event_id={import_first.get('unresolved_event_id')}"
        )
        print(
            "[SMOKE] second_import "
            f"staged_skipped={import_second.get('staged_skipped')} "
            f"upsert_inserted={import_second.get('upsert_inserted')}"
        )
        print(f"[SMOKE] report={report_path}")
        return 0

    except Exception as err:
        report["status"] = "error"
        report["error"] = str(err)
        report_path = _write_report(report, stamp)
        print("[SMOKE] publicidade import: FAIL")
        print(f"[SMOKE] error={err}")
        print(f"[SMOKE] report={report_path}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
