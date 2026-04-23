"""Compatibility helpers for the legacy leads_publicidade package."""

from __future__ import annotations

import importlib
import sys
from types import ModuleType
from typing import Any

LEGACY_PREFIX = "app.modules.leads_publicidade"
REAL_PREFIX = "app.modules.lead_imports"


def alias_module(legacy_name: str, target_globals: dict[str, Any]) -> ModuleType:
    """Expose a legacy module path as the real lead_imports module object."""

    real_name = legacy_name.replace(LEGACY_PREFIX, REAL_PREFIX, 1)
    module = importlib.import_module(real_name)
    target_globals.update(module.__dict__)
    sys.modules[legacy_name] = module
    return module
