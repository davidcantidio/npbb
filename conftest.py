"""Pytest configuration shared across repository tests."""

from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register repository-level custom pytest options."""
    parser.addoption(
        "--update-snapshots",
        action="store_true",
        default=False,
        help="Update golden snapshot files instead of asserting current content.",
    )


@pytest.fixture
def update_snapshots(request: pytest.FixtureRequest) -> bool:
    """Return whether snapshot files should be updated during test run."""
    return bool(request.config.getoption("--update-snapshots"))
