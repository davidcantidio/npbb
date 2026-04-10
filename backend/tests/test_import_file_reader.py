from __future__ import annotations

from io import BytesIO

import pytest
from fastapi import UploadFile

from app.services.imports.file_reader import (
    ALLOWED_IMPORT_EXTENSIONS,
    BYTES_PER_MEGABYTE,
    ImportFileError,
    inspect_upload,
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
    assert err.message == f"Arquivo '.txt' não é suportado. Extensões aceitas: {accepted_extensions}"
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
