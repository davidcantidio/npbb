import json
import tempfile
from pathlib import Path

from report import interpret_indicators as ii


def test_detect_forbidden_terms_minimum_three() -> None:
    text = "Recomenda renovar. A empresa deve agir."
    found = ii.detect_forbidden_terms(text)
    assert len(found) >= 3


def test_rewrite_forbidden_terms() -> None:
    text = "Recomenda que o patrocinio deve continuar."
    rewritten, applied = ii.rewrite_forbidden_terms(text)
    assert "os dados sugerem" in rewritten.lower()
    assert "pode indicar" in rewritten.lower()
    assert len(applied) >= 2


def test_sanitize_text_removes_extra_lines() -> None:
    raw = "Linha 1\n\n\nLinha 2  \n\nLinha 3"
    cleaned = ii.sanitize_text(raw)
    assert "\n\n\n" not in cleaned
    assert "  " not in cleaned


def test_fallback_flag_for_mock_provider() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        indicators_path = tmp_path / "indicadores.json"
        prompt_path = tmp_path / "prompt.md"
        out_dir = tmp_path / "out"

        indicators_path.write_text(
            json.dumps(
                {
                    "base": {"posts_total": 1, "date_min": "2024-01-01", "date_max": "2024-01-02"},
                    "meta": {"principal_handle": "@teste", "since": "2024-01-01"},
                }
            ),
            encoding="utf-8",
        )
        prompt_path.write_text("Prompt base.", encoding="utf-8")

        exit_code = ii.main(
            [
                "--input",
                str(indicators_path),
                "--user",
                "@teste",
                "--provider",
                "mock",
                "--prompt",
                str(prompt_path),
                "--out",
                str(out_dir),
            ]
        )
        assert exit_code == 0

        meta = json.loads((out_dir / "interpretation.json").read_text(encoding="utf-8"))
        assert meta.get("fallback") is True
