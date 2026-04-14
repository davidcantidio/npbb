from __future__ import annotations

from datetime import date

import pandas as pd

from .constants import ALL_COLUMNS


def _is_iso_date(value: str) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    try:
        date.fromisoformat(text)
    except ValueError:
        return False
    return True


def validate_databricks_contract(df: pd.DataFrame) -> list[str]:
    violations: list[str] = []

    actual_columns = list(df.columns)
    if actual_columns != ALL_COLUMNS:
        violations.append(
            "SCHEMA_INVALIDO: colunas esperadas "
            f"{ALL_COLUMNS}, obtidas {actual_columns}"
        )
        return violations

    cpf_invalid = ~df["cpf"].astype(str).str.fullmatch(r"\d{11}")
    if cpf_invalid.any():
        violations.append(f"CPF_INVALIDO_NO_PROCESSADO: {int(cpf_invalid.sum())} linha(s)")

    if df.duplicated(subset=["cpf", "evento"]).any():
        violations.append("CPF_EVENTO_DUPLICADO_NO_PROCESSADO")

    phone = df["telefone"].astype(str).str.strip()
    phone_invalid = (phone != "") & (~phone.str.fullmatch(r"\d{10,}"))
    if phone_invalid.any():
        violations.append(
            f"TELEFONE_INVALIDO_NO_PROCESSADO: {int(phone_invalid.sum())} linha(s)"
        )

    event_date = df["data_evento"].astype(str).str.strip()
    event_date_invalid = (event_date != "") & (~event_date.map(_is_iso_date))
    if event_date_invalid.any():
        violations.append(
            f"DATA_EVENTO_INVALIDA_NO_PROCESSADO: {int(event_date_invalid.sum())} linha(s)"
        )

    birth = df["data_nascimento"].astype(str)
    birth_invalid = (birth.str.strip() != "") & (~birth.map(_is_iso_date))
    if birth_invalid.any():
        violations.append(
            "DATA_NASCIMENTO_INVALIDA_NO_PROCESSADO: "
            f"{int(birth_invalid.sum())} linha(s)"
        )

    return violations
