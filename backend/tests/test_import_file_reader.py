from __future__ import annotations

from io import BytesIO

import pytest
from fastapi import UploadFile

from app.services.imports.file_reader import (
    ALLOWED_IMPORT_EXTENSIONS,
    BYTES_PER_MEGABYTE,
    ImportFileError,
    inspect_upload,
    read_raw_file_headers,
    read_raw_file_preview,
)


def _upload_file(filename: str, content: bytes) -> UploadFile:
    return UploadFile(filename=filename, file=BytesIO(content))


def test_inspect_upload_invalid_extension_message_includes_received_and_allowed_extensions() -> None:
    file = _upload_file("leads.txt", b"email\nfoo@example.com\n")

    with pytest.raises(ImportFileError) as exc_info:
        inspect_upload(file)

    err = exc_info.value
    accepted_extensions = ", ".join(sorted(ALLOWED_IMPORT_EXTENSIONS))
    assert err.code == "INVALID_FILE_TYPE"
    assert err.message == f"Arquivo '.txt' nao e suportado. Extensoes aceitas: {accepted_extensions}"
    for ext in ALLOWED_IMPORT_EXTENSIONS:
        assert ext in err.message


def test_inspect_upload_too_large_message_includes_received_size_and_limit_in_mb() -> None:
    max_bytes = 10 * BYTES_PER_MEGABYTE
    content = b"x" * int(24.3 * BYTES_PER_MEGABYTE)
    file = _upload_file("leads.csv", content)

    with pytest.raises(ImportFileError) as exc_info:
        inspect_upload(file, max_bytes=max_bytes)

    err = exc_info.value
    assert err.code == "FILE_TOO_LARGE"
    assert "24.3 MB" in err.message
    assert "10.0 MB" in err.message
    assert err.extra == {"max_bytes": max_bytes}


class _FakeWorksheet:
    def __init__(self, limit: int = 60) -> None:
        self.limit = limit

    def iter_rows(self, values_only: bool = True):
        assert values_only is True
        emitted = 0
        for idx in range(8):
            emitted += 1
            yield (f"linha solta {idx + 1}", "", "")
        emitted += 1
        yield ("nome", "email", "cpf")
        for idx in range(200):
            emitted += 1
            if emitted > self.limit:
                raise AssertionError("Reader exceeded preview/header scan window")
            yield (f"Lead {idx}", f"lead{idx}@example.com", f"{idx:011d}")


class _FakeWorkbook:
    def __init__(self, limit: int = 60) -> None:
        self.worksheets = [_FakeWorksheet(limit=limit)]
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_read_raw_file_preview_avoids_full_xlsx_scan(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.imports.file_reader.load_workbook",
        lambda *args, **kwargs: _FakeWorkbook(limit=60),
    )

    preview = read_raw_file_preview(b"fake-xlsx", filename="leads.xlsx", sample_rows=3)

    assert preview.start_index == 8
    assert preview.headers == ["nome", "email", "cpf"]
    assert preview.rows == [
        ["Lead 0", "lead0@example.com", "00000000000"],
        ["Lead 1", "lead1@example.com", "00000000001"],
        ["Lead 2", "lead2@example.com", "00000000002"],
    ]


def test_read_raw_file_headers_avoids_full_xlsx_scan(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.imports.file_reader.load_workbook",
        lambda *args, **kwargs: _FakeWorkbook(limit=60),
    )

    preview = read_raw_file_headers(b"fake-xlsx", filename="leads.xlsx")

    assert preview.start_index == 8
    assert preview.headers == ["nome", "email", "cpf"]
    assert preview.rows == []
