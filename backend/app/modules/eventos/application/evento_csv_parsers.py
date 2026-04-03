"""Parsers e helpers para importação CSV de eventos."""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.models import Evento, Usuario


class CsvRowIssue(Exception):
    def __init__(self, field: str, message: str, value: str | None = None) -> None:
        super().__init__(message)
        self.field = field
        self.message = message
        self.value = value


def _normalize_str(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def normalize_csv_header(value: str) -> str:
    return value.replace("\ufeff", "").strip().lower().replace(" ", "_")


def detect_csv_delimiter(text: str) -> str:
    first_line = text.splitlines()[0] if text else ""
    comma_count = first_line.count(",")
    semi_count = first_line.count(";")
    return ";" if semi_count > comma_count else ","


def _parse_csv_bool(value: str, field: str) -> bool:
    text = value.strip().lower()
    if text in {"1", "true", "sim", "s", "yes", "y"}:
        return True
    if text in {"0", "false", "nao", "n", "no"}:
        return False
    raise CsvRowIssue(field, "valores aceitos: sim/nao, true/false, 1/0", value=value)


def _parse_csv_int(value: str, field: str) -> int:
    text = value.strip()
    if not text:
        raise CsvRowIssue(field, "obrigatorio", value=value)
    try:
        parsed = int(text)
    except ValueError:
        raise CsvRowIssue(field, "deve ser inteiro", value=value) from None
    if parsed < 1:
        raise CsvRowIssue(field, "deve ser inteiro >= 1", value=value)
    return parsed


def _parse_csv_int_optional(value: str, field: str) -> int | None:
    text = value.strip()
    if not text:
        return None
    try:
        parsed = int(text)
    except ValueError:
        raise CsvRowIssue(field, "deve ser inteiro", value=value) from None
    if parsed < 1:
        raise CsvRowIssue(field, "deve ser inteiro >= 1", value=value)
    return parsed


def _parse_csv_decimal(value: str, field: str) -> Decimal:
    text = value.strip()
    if not text:
        raise CsvRowIssue(field, "obrigatorio", value=value)
    normalized = text.replace("R$", "").replace(" ", "")
    if "," in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    try:
        return Decimal(normalized)
    except Exception:
        raise CsvRowIssue(field, "deve ser numero (ex: 1234,56 ou 1234.56)", value=value) from None


def _parse_csv_decimal_optional(value: str, field: str) -> Decimal | None:
    text = value.strip()
    if not text:
        return None
    return _parse_csv_decimal(text, field)


def _parse_csv_date(value: str, field: str) -> date:
    text = value.strip()
    if not text:
        raise CsvRowIssue(field, "obrigatorio", value=value)
    try:
        if "-" in text:
            return date.fromisoformat(text)
        return datetime.strptime(text, "%d/%m/%Y").date()
    except Exception:
        raise CsvRowIssue(
            field, "formato invalido (use AAAA-MM-DD ou DD/MM/AAAA)", value=value
        ) from None


def _parse_csv_date_optional(value: str, field: str) -> date | None:
    text = value.strip()
    if not text:
        return None
    return _parse_csv_date(text, field)


def _parse_csv_id_list(value: str, field: str) -> list[int] | None:
    text = value.strip()
    if not text:
        return None
    tokens = [t.strip() for t in re.split(r"[|;,]", text) if t.strip()]
    if not tokens:
        return None
    parsed: list[int] = []
    for token in tokens:
        try:
            num = int(token)
        except ValueError:
            raise CsvRowIssue(
                field, "lista deve conter somente inteiros >= 1", value=value
            ) from None
        if num < 1:
            raise CsvRowIssue(field, "lista deve conter somente inteiros >= 1", value=value)
        parsed.append(num)
    return parsed


def _get_csv_value(row: list[str], header_index: dict[str, int], key: str) -> str:
    idx = header_index.get(key)
    if idx is None:
        return ""
    if idx >= len(row):
        return ""
    return row[idx]


def build_evento_payload_from_row(row: list[str], header_index: dict[str, int]) -> dict[str, Any]:
    nome = _get_csv_value(row, header_index, "nome").strip()
    if not nome:
        raise CsvRowIssue("nome", "obrigatorio")
    cidade = _get_csv_value(row, header_index, "cidade").strip()
    if not cidade:
        raise CsvRowIssue("cidade", "obrigatorio")
    estado = _get_csv_value(row, header_index, "estado").strip()
    if not estado:
        raise CsvRowIssue("estado", "obrigatorio")

    data_inicio_prevista = _parse_csv_date(
        _get_csv_value(row, header_index, "data_inicio_prevista"), "data_inicio_prevista"
    )
    data_fim_prevista = _parse_csv_date_optional(
        _get_csv_value(row, header_index, "data_fim_prevista"), "data_fim_prevista"
    )

    data: dict[str, Any] = {
        "nome": nome,
        "cidade": cidade,
        "estado": estado.upper(),
        "data_inicio_prevista": data_inicio_prevista,
    }
    if data_fim_prevista:
        data["data_fim_prevista"] = data_fim_prevista

    descricao = _normalize_str(_get_csv_value(row, header_index, "descricao"))
    if descricao:
        data["descricao"] = descricao

    investimento_val = _parse_csv_decimal_optional(
        _get_csv_value(row, header_index, "investimento"), "investimento"
    )
    if investimento_val is not None:
        data["investimento"] = investimento_val

    concorrencia_raw = _get_csv_value(row, header_index, "concorrencia").strip()
    if concorrencia_raw:
        data["concorrencia"] = _parse_csv_bool(concorrencia_raw, "concorrencia")

    for key in (
        "agencia_id",
        "diretoria_id",
        "gestor_id",
        "tipo_id",
        "subtipo_id",
        "status_id",
        "divisao_demandante_id",
    ):
        raw = _get_csv_value(row, header_index, key)
        parsed = _parse_csv_int_optional(raw, key)
        if parsed is not None:
            data[key] = parsed

    tag_ids = _parse_csv_id_list(_get_csv_value(row, header_index, "tag_ids"), "tag_ids")
    if tag_ids is not None:
        data["tag_ids"] = tag_ids

    territorio_ids = _parse_csv_id_list(
        _get_csv_value(row, header_index, "territorio_ids"), "territorio_ids"
    )
    if territorio_ids is not None:
        data["territorio_ids"] = territorio_ids

    thumbnail = _normalize_str(_get_csv_value(row, header_index, "thumbnail"))
    if thumbnail:
        data["thumbnail"] = thumbnail

    qr_code_url = _normalize_str(_get_csv_value(row, header_index, "qr_code_url"))
    if qr_code_url:
        data["qr_code_url"] = qr_code_url

    external_project_code = _normalize_str(_get_csv_value(row, header_index, "external_project_code"))
    if external_project_code:
        data["external_project_code"] = external_project_code

    data_inicio_realizada = _parse_csv_date_optional(
        _get_csv_value(row, header_index, "data_inicio_realizada"), "data_inicio_realizada"
    )
    if data_inicio_realizada:
        data["data_inicio_realizada"] = data_inicio_realizada

    data_fim_realizada = _parse_csv_date_optional(
        _get_csv_value(row, header_index, "data_fim_realizada"), "data_fim_realizada"
    )
    if data_fim_realizada:
        data["data_fim_realizada"] = data_fim_realizada

    publico_projetado_raw = _get_csv_value(row, header_index, "publico_projetado").strip()
    if publico_projetado_raw:
        data["publico_projetado"] = _parse_csv_int(publico_projetado_raw, "publico_projetado")

    publico_realizado_raw = _get_csv_value(row, header_index, "publico_realizado").strip()
    if publico_realizado_raw:
        data["publico_realizado"] = _parse_csv_int(publico_realizado_raw, "publico_realizado")

    return data


def _evento_date_range(evento: Evento) -> tuple[date, date] | None:
    start = evento.data_inicio_prevista or evento.data_inicio_realizada
    if not start:
        return None
    end = evento.data_fim_prevista or evento.data_fim_realizada or start
    return (start, end)


def find_evento_match(
    session: Session,
    apply_visibility,
    nome: str,
    cidade: str,
    estado: str,
    start: date,
    end: date,
    current_user: Usuario,
) -> Evento | None:
    inicio = func.coalesce(Evento.data_inicio_prevista, Evento.data_inicio_realizada)
    fim = func.coalesce(Evento.data_fim_prevista, Evento.data_fim_realizada, inicio)

    query = select(Evento).where(
        func.lower(Evento.nome) == nome.lower(),
        func.lower(Evento.cidade) == cidade.lower(),
        func.lower(Evento.estado) == estado.lower(),
        inicio.is_not(None),
        inicio <= end,
        fim >= start,
    )
    query = apply_visibility(query, current_user)
    candidates = session.exec(query).all()
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    start_ord = start.toordinal()
    end_ord = end.toordinal()
    scored: list[tuple[int, Evento]] = []
    for item in candidates:
        rng = _evento_date_range(item)
        if not rng:
            scored.append((0, item))
            continue
        item_start, item_end = rng
        overlap_start = max(item_start.toordinal(), start_ord)
        overlap_end = min(item_end.toordinal(), end_ord)
        overlap = max(0, overlap_end - overlap_start)
        scored.append((overlap, item))
    scored.sort(key=lambda pair: (pair[0], pair[1].id or 0), reverse=True)
    return scored[0][1]
