from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from lead_pipeline.geo_normalize import (
    MUNICIPIOS_DATA_PATH,
    inspect_municipios_reference,
    normalize_brazilian_locality,
)


def test_reference_csv_is_versioned_and_structurally_valid() -> None:
    entries, validation = inspect_municipios_reference()

    assert MUNICIPIOS_DATA_PATH.exists()
    assert entries
    assert validation.malformed_lines == ()
    assert validation.duplicate_normalized_pairs == ()
    assert validation.unknown_states == ()


def test_reference_validation_detects_malformed_duplicate_and_suspicious_rows() -> None:
    temp_dir = Path("backend/tmp-pytest") / f"geo-normalize-{uuid4().hex}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    csv_path = temp_dir / "municipios.csv"
    csv_path.write_text(
        "\n".join(
            [
                "municipio,estado",
                "Sorocaba,São Paulo",
                "Sorocaba,SP",
                "Cidade Sem Estado",
                "SeverInia,São Paulo",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    _, validation = inspect_municipios_reference(csv_path)

    assert validation.malformed_lines == (4,)
    assert validation.duplicate_normalized_pairs == ("3:Sorocaba/SP",)
    assert validation.unknown_states == ()
    assert validation.suspicious_display_names == ("5:SeverInia",)


def test_normalize_brazilian_locality_resolves_city_and_uf_from_local() -> None:
    result = normalize_brazilian_locality(local="Sao Paulo-SP")

    assert result.issue_code is None
    assert result.cidade == "São Paulo"
    assert result.estado == "SP"
    assert result.local == "São Paulo-SP"


def test_normalize_brazilian_locality_resolves_explicit_city_and_state() -> None:
    result = normalize_brazilian_locality(cidade="Rio de Janeiro", estado="RJ")

    assert result.issue_code is None
    assert result.cidade == "Rio de Janeiro"
    assert result.estado == "RJ"
    assert result.local == "Rio de Janeiro-RJ"


def test_normalize_brazilian_locality_flags_non_brazil_input() -> None:
    result = normalize_brazilian_locality(local="London Area, United Kingdom")

    assert result.issue_code == "non_br"
    assert result.cidade == ""
    assert result.estado == ""
    assert result.local == ""


def test_normalize_brazilian_locality_flags_unresolved_input() -> None:
    result = normalize_brazilian_locality(local="Cidade Inventada 123")

    assert result.issue_code == "unresolved"
    assert result.cidade == ""
    assert result.estado == ""
    assert result.local == ""


def test_normalize_brazilian_locality_flags_city_state_mismatch() -> None:
    result = normalize_brazilian_locality(cidade="Sao Paulo", estado="RJ")

    assert result.issue_code == "cidade_uf_mismatch"
    assert result.cidade == ""
    assert result.estado == ""
    assert result.local == ""
