"""Leitura padrao de arquivos de importacao (CSV/XLSX)."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from fastapi import UploadFile
from openpyxl import load_workbook

from app.services.imports.contracts import ImportPreviewResult

ALLOWED_IMPORT_EXTENSIONS = {".csv", ".xlsx"}
DEFAULT_IMPORT_MAX_BYTES = 50 * 1024 * 1024


@dataclass(frozen=True)
class ImportFileError(Exception):
    code: str
    message: str
    field: str = "file"
    extra: dict | None = None


def _detect_csv_delimiter(sample_text: str) -> str:
    first_line = sample_text.splitlines()[0] if sample_text else ""
    comma_count = first_line.count(",")
    semicolon_count = first_line.count(";")
    return ";" if semicolon_count > comma_count else ","


def _score_row_tabular(row: list[str]) -> int:
    if not row:
        return 0
    non_empty = [cell for cell in row if cell.strip()]
    fill_ratio = len(non_empty) / max(len(row), 1)
    if len(non_empty) >= 2 and fill_ratio >= 0.5:
        return int(fill_ratio * 100)
    return 0


def detect_data_start_index(rows: list[list[str]]) -> int:
    best_idx = 0
    best_score = -1
    for idx, row in enumerate(rows[:50]):
        score = _score_row_tabular(row)
        if score > best_score:
            best_idx = idx
            best_score = score
    return best_idx


def _decode_payload(raw: bytes) -> str:
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def inspect_upload(
    file: UploadFile,
    *,
    max_bytes: int = DEFAULT_IMPORT_MAX_BYTES,
) -> tuple[str, str, int]:
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_IMPORT_EXTENSIONS:
        raise ImportFileError(
            code="INVALID_FILE_TYPE",
            message="Formato de arquivo invalido (use .csv ou .xlsx)",
            field="file",
        )

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > max_bytes:
        raise ImportFileError(
            code="FILE_TOO_LARGE",
            message="Arquivo excede o tamanho maximo permitido",
            field="file",
            extra={"max_bytes": max_bytes},
        )
    if size == 0:
        raise ImportFileError(
            code="EMPTY_FILE",
            message="Arquivo vazio",
            field="file",
        )
    return filename, ext, size


def _read_csv_sample(file: UploadFile, *, max_rows: int) -> ImportPreviewResult:
    file.file.seek(0)
    raw = file.file.read()
    text = _decode_payload(raw)
    delimiter = _detect_csv_delimiter(text[:4096])
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows: list[list[str]] = []
    for row in reader:
        rows.append([str(cell).strip() for cell in row])
        if len(rows) >= max_rows + 1:
            break

    start_index = detect_data_start_index(rows)
    headers = rows[start_index] if rows else []
    data_rows = rows[start_index + 1 :] if len(rows) > start_index + 1 else []
    return ImportPreviewResult(
        filename=file.filename or "",
        headers=headers,
        rows=data_rows,
        delimiter=delimiter,
        start_index=start_index,
    )


def _read_xlsx_sample(file: UploadFile, *, max_rows: int) -> ImportPreviewResult:
    file.file.seek(0)
    wb = load_workbook(file.file, read_only=True, data_only=True)
    ws = wb.worksheets[0]

    rows: list[list[str]] = []
    for row in ws.iter_rows(max_row=max_rows + 1, values_only=True):
        rows.append([("" if v is None else str(v)).strip() for v in row])
        if len(rows) >= max_rows + 1:
            break

    start_index = detect_data_start_index(rows)
    headers = rows[start_index] if rows else []
    data_rows = rows[start_index + 1 :] if len(rows) > start_index + 1 else []
    return ImportPreviewResult(
        filename=file.filename or "",
        headers=headers,
        rows=data_rows,
        delimiter=None,
        start_index=start_index,
    )


def read_file_sample(
    file: UploadFile,
    *,
    sample_rows: int,
    max_bytes: int = DEFAULT_IMPORT_MAX_BYTES,
) -> tuple[ImportPreviewResult, str]:
    if sample_rows < 1 or sample_rows > 50:
        raise ImportFileError(
            code="INVALID_SAMPLE_SIZE",
            message="sample_rows deve ser entre 1 e 50",
            field="sample_rows",
        )

    _, ext, _ = inspect_upload(file, max_bytes=max_bytes)
    preview = _read_xlsx_sample(file, max_rows=sample_rows) if ext == ".xlsx" else _read_csv_sample(
        file, max_rows=sample_rows
    )
    if not preview.headers and not preview.rows:
        raise ImportFileError(code="EMPTY_FILE", message="Arquivo vazio", field="file")
    return preview, ext


def iter_data_rows(
    file: UploadFile,
    *,
    ext: str,
    start_index: int,
    delimiter: str | None = None,
) -> Iterator[list[str]]:
    if ext == ".xlsx":
        file.file.seek(0)
        wb = load_workbook(file.file, read_only=True, data_only=True)
        ws = wb.worksheets[0]
        for idx, row in enumerate(ws.iter_rows(values_only=True)):
            if idx <= start_index:
                continue
            yield [("" if v is None else str(v)).strip() for v in row]
        return

    file.file.seek(0)
    raw = file.file.read()
    text = _decode_payload(raw)
    active_delimiter = delimiter or _detect_csv_delimiter(text[:4096])
    reader = csv.reader(io.StringIO(text), delimiter=active_delimiter)
    for idx, row in enumerate(reader):
        if idx <= start_index:
            continue
        yield [str(cell).strip() for cell in row]
