"""File extraction helpers for backend ETL preview."""

from __future__ import annotations

import hashlib
import io
from typing import Any

from fastapi import UploadFile
from openpyxl import load_workbook

from app.services.imports.file_reader import inspect_upload
from etl.extract.xlsx_utils import build_columns_with_metadata, find_header_row


def read_upload_bytes(file: UploadFile, *, max_bytes: int) -> tuple[str, str, bytes]:
    filename, ext, _size = inspect_upload(file, max_bytes=max_bytes)
    file.file.seek(0)
    payload = file.file.read()
    file.file.seek(0)
    return filename, ext, payload


def compute_file_fingerprint(filename: str, payload: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(filename.encode("utf-8"))
    digest.update(b":")
    digest.update(payload)
    return digest.hexdigest()


def extract_xlsx_rows(payload: bytes) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    workbook = load_workbook(io.BytesIO(payload), read_only=False, data_only=True)
    ws = workbook.worksheets[0]
    header_row = find_header_row(ws, required_terms=["CPF", "Email"], max_scan_rows=40)
    columns_result = build_columns_with_metadata(ws, header_row=header_row, header_depth=1)
    data_start_row = header_row + columns_result.lineage.header_depth
    rows: list[dict[str, Any]] = []

    for row_idx in range(data_start_row, ws.max_row + 1):
        values = [ws.cell(row=row_idx, column=col_idx).value for col_idx in range(1, len(columns_result.columns) + 1)]
        if all(value is None or not str(value).strip() for value in values):
            continue
        rows.append(
            {
                "__row_number": row_idx,
                "__sheet_name": ws.title,
                **{
                    columns_result.columns[index]: values[index]
                    for index in range(len(columns_result.columns))
                },
            }
        )

    return rows, {
        "sheet_name": ws.title,
        "header_row": columns_result.lineage.header_row,
        "header_range": columns_result.lineage.header_range,
        "used_range": columns_result.lineage.used_range,
    }
