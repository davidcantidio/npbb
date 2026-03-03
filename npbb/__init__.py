"""Compatibility package for absolute imports under `npbb.*`.

The repository still has modules importing `npbb.etl.*`/`npbb.core.*`.
This package provides a transitional alias layer while import paths are
incrementally normalized.
"""

from __future__ import annotations

import importlib
import sys
from types import ModuleType


def _alias_submodule(alias: str, target: str) -> None:
    try:
        module: ModuleType = importlib.import_module(target)
    except ModuleNotFoundError:
        return
    sys.modules[f"{__name__}.{alias}"] = module
    setattr(sys.modules[__name__], alias, module)


for _alias, _target in (
    ("core", "core"),
    ("etl", "etl"),
    ("backend", "backend"),
):
    _alias_submodule(_alias, _target)

