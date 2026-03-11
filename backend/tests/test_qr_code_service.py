import base64

import pytest

from app.models.models import Ativacao
from app.services.landing_pages import hydrate_ativacao_public_urls
from app.services.qr_code import build_qr_code_data_url, build_qr_code_svg


def test_build_qr_code_svg_retorna_svg_para_conteudo_nao_vazio():
    svg = build_qr_code_svg("https://lp.example.com/landing/ativacoes/42")

    assert "<svg" in svg
    assert "</svg>" in svg


def test_build_qr_code_svg_rejeita_conteudo_vazio():
    with pytest.raises(ValueError, match="conteudo nao vazio"):
        build_qr_code_svg("   ")


def test_build_qr_code_data_url_retorna_svg_codificado():
    data_url = build_qr_code_data_url("https://lp.example.com/landing/ativacoes/42")

    assert data_url.startswith("data:image/svg+xml;base64,")
    encoded = data_url.split(",", 1)[1]
    decoded = base64.b64decode(encoded).decode("utf-8")
    assert "<svg" in decoded


def test_hydrate_ativacao_public_urls_preenche_campos_e_eh_idempotente(monkeypatch):
    monkeypatch.delenv("FRONTEND_ORIGIN", raising=False)
    monkeypatch.delenv("PUBLIC_LANDING_BASE_URL", raising=False)
    monkeypatch.setenv("PUBLIC_APP_BASE_URL", "https://lp.example.com")

    ativacao = Ativacao(id=42, evento_id=7, nome="Stand Principal")

    first_changed = hydrate_ativacao_public_urls(ativacao)

    assert first_changed is True
    assert ativacao.landing_url == "https://lp.example.com/landing/ativacoes/42"
    assert ativacao.url_promotor == "https://lp.example.com/landing/ativacoes/42"
    assert ativacao.qr_code_url.startswith("data:image/svg+xml;base64,")

    second_changed = hydrate_ativacao_public_urls(ativacao)

    assert second_changed is False
