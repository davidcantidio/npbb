"""Unit tests for file fingerprint hashing and metadata collection."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.registry import SourceFileNotFoundError, SourceFilePermissionError
from core.utils.file_fingerprint import collect_file_metadata, compute_file_sha256


def test_compute_file_sha256_is_stable_for_same_content(tmp_path: Path) -> None:
    """Hash is deterministic for the same file content and changes on content update."""
    target = tmp_path / "sample.txt"
    target.write_text("festival tmj 2025", encoding="utf-8")

    digest_first = compute_file_sha256(target)
    digest_second = compute_file_sha256(target)

    assert digest_first == digest_second
    assert len(digest_first) == 64

    target.write_text("festival tmj 2025 - updated", encoding="utf-8")
    assert compute_file_sha256(target) != digest_first


def test_collect_file_metadata_returns_minimum_audit_fields(tmp_path: Path) -> None:
    """Metadata returns absolute path, byte size and UTC mtime."""
    target = tmp_path / "metadata.bin"
    target.write_bytes(b"\x10\x20\x30")

    metadata = collect_file_metadata(target)

    assert Path(metadata.path) == target.resolve()
    assert metadata.file_size_bytes == 3
    assert metadata.file_mtime_utc.tzinfo is not None
    assert metadata.file_mtime_utc.utcoffset() is not None


def test_file_fingerprint_raises_not_found_for_missing_path(tmp_path: Path) -> None:
    """Hash and metadata helpers raise SourceFileNotFoundError on missing paths."""
    missing = tmp_path / "does_not_exist.pdf"

    with pytest.raises(SourceFileNotFoundError):
        compute_file_sha256(missing)

    with pytest.raises(SourceFileNotFoundError):
        collect_file_metadata(missing)


def test_file_fingerprint_raises_permission_error_when_read_or_stat_is_blocked(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Permission failures are converted to actionable registry exceptions."""
    target = tmp_path / "restricted.xlsx"
    target.write_text("secret", encoding="utf-8")

    def _deny_open(self: Path, mode: str = "r", buffering: int = -1, encoding=None, errors=None, newline=None):  # noqa: ANN001, ANN202
        raise PermissionError("denied")

    def _deny_stat(self: Path, *, follow_symlinks: bool = True):  # noqa: ANN202
        raise PermissionError("denied")

    monkeypatch.setattr(Path, "open", _deny_open)
    with pytest.raises(SourceFilePermissionError):
        compute_file_sha256(target)

    monkeypatch.setattr(Path, "stat", _deny_stat)
    with pytest.raises(SourceFilePermissionError):
        collect_file_metadata(target)

