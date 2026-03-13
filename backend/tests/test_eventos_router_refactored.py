"""TDD: testes que validam a estrutura refatorada do router de eventos.

Estes testes falham antes da refatoração e passam após a migração para o pacote
routers/eventos/ com subrouters por domínio.
"""

from __future__ import annotations

import pytest


def test_eventos_router_é_pacote_com_submodulos():
    """Após refatoração, app.routers.eventos deve ser um pacote (não um módulo .py)."""
    import app.routers.eventos as ev

    assert hasattr(ev, "__path__"), (
        "eventos deve ser um pacote (diretório com __init__.py), não um módulo .py"
    )


def test_eventos_router_importavel_e_tem_prefix():
    """Router principal deve ser importável e ter prefix /evento."""
    from app.routers.eventos import router

    assert router is not None
    assert router.prefix == "/evento"


def test_eventos_subrouters_existem():
    """Submódulos crud, csv, dicionarios, form_config etc devem existir."""
    import importlib

    submodulos_esperados = [
        "crud",
        "csv",
        "dicionarios",
        "form_config",
        "questionario",
        "gamificacoes",
        "ativacoes",
        "landing",
    ]
    for nome in submodulos_esperados:
        mod = importlib.import_module(f"app.routers.eventos.{nome}")
        assert mod is not None, f"Submódulo eventos.{nome} deve existir após refatoração"


def test_eventos_shared_contem_helpers():
    """Módulo _shared deve exportar helpers de visibilidade e erro."""
    from app.routers.eventos import _shared

    assert hasattr(_shared, "_apply_visibility")
    assert hasattr(_shared, "_raise_http")
    assert hasattr(_shared, "_check_evento_visible_or_404")
