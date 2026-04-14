from __future__ import annotations

from datetime import date, datetime, timezone

import pandas as pd

from .constants import ALL_COLUMNS
from .normalization import BIRTH_DATE_MIN


def _is_iso_date(value: str) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    try:
        date.fromisoformat(text)
    except ValueError:
        return False
    return True


def _is_birth_date_in_range(value: str, *, ref_date: date) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    try:
        birth_date = date.fromisoformat(text)
    except ValueError:
        return False
    return BIRTH_DATE_MIN <= birth_date <= ref_date


def validate_databricks_contract(df: pd.DataFrame, *, ref_date: date | None = None) -> list[str]:
    violations: list[str] = []
    if ref_date is None:
        # Fallback stays in UTC so ad-hoc validations match the pipeline cutoff policy.
        ref_date = datetime.now(timezone.utc).date()

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

    birth = df["data_nascimento"].astype(str).str.strip()
    birth_invalid = (birth != "") & (~birth.map(lambda value: _is_birth_date_in_range(value, ref_date=ref_date)))
    if birth_invalid.any():
        violations.append(
            "DATA_NASCIMENTO_INVALIDA_NO_PROCESSADO: "
            f"{int(birth_invalid.sum())} linha(s)"
        )

    estado = df["estado"].astype(str).str.strip()
    estado_invalid = (estado != "") & (~estado.str.fullmatch(r"[A-Z]{2}"))
    if estado_invalid.any():
        violations.append(
            f"ESTADO_INVALIDO_NO_PROCESSADO: {int(estado_invalid.sum())} linha(s)"
        )

    return violations
