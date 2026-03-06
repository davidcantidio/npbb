"""Service for exporting Gold-stage leads to .xlsx or .csv files.

Design decisions:
- Returns bytes (or None when no data) so the HTTP layer stays thin.
- CSV uses UTF-8 BOM + semicolon separator for Excel compatibility in pt-BR.
- Column mapping is a module-level constant so callers can inspect it if needed.
"""

from __future__ import annotations

import csv
import io
import re
from datetime import date
from typing import Optional

import openpyxl
from sqlmodel import Session, select

from app.models.lead_batch import BatchStage, LeadBatch, PipelineStatus
from app.models.models import Evento, Lead

# Ordered list of (header_label, Lead attribute name) used in the exported file.
EXPORT_COLUMNS: list[tuple[str, str]] = [
    ("Nome completo", "nome"),
    ("Sobrenome", "sobrenome"),
    ("E-mail", "email"),
    ("CPF", "cpf"),
    ("RG", "rg"),
    ("Telefone", "telefone"),
    ("Gênero", "genero"),
    ("Evento de origem", "evento_nome"),
    ("Cidade", "cidade"),
    ("Estado", "estado"),
    ("Logradouro", "endereco_rua"),
    ("Número", "endereco_numero"),
    ("Complemento", "complemento"),
    ("Bairro", "bairro"),
    ("CEP", "cep"),
    ("Data de compra", "data_compra"),
    ("Data de criação", "data_criacao"),
    ("Estágio", "_estagio"),
]

_GOLD_PIPELINE_STATUSES = {PipelineStatus.PASS, PipelineStatus.PASS_WITH_WARNINGS}


def _build_query(session: Session, evento_id: Optional[int]):
    """Returns all Gold leads, optionally filtered by evento_id."""
    stmt = (
        select(Lead, Evento.nome.label("evento_ref_nome"))
        .join(LeadBatch, Lead.batch_id == LeadBatch.id)
        .outerjoin(Evento, Evento.id == LeadBatch.evento_id)
        .where(LeadBatch.stage == BatchStage.GOLD)
        .where(LeadBatch.pipeline_status.in_(_GOLD_PIPELINE_STATUSES))
    )
    if evento_id is not None:
        stmt = stmt.where(LeadBatch.evento_id == evento_id)
    return session.exec(stmt).all()


def _get_cell_value(lead: Lead, field: str) -> str:
    """Resolves a single cell value from a Lead row."""
    if field == "_estagio":
        return "Ouro"
    value = getattr(lead, field, None)
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _slug(text: str) -> str:
    """Converts an event name to a filesystem-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[àáâãäå]", "a", slug)
    slug = re.sub(r"[èéêë]", "e", slug)
    slug = re.sub(r"[ìíîï]", "i", slug)
    slug = re.sub(r"[òóôõö]", "o", slug)
    slug = re.sub(r"[ùúûü]", "u", slug)
    slug = re.sub(r"[ç]", "c", slug)
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")[:50]


def build_filename(evento_nome: Optional[str], formato: str) -> str:
    """Returns the download filename according to PRD 4.8."""
    today = date.today().isoformat()
    if evento_nome:
        return f"leads_ouro_{_slug(evento_nome)}_{today}.{formato}"
    return f"leads_ouro_todos_{today}.{formato}"


def _generate_xlsx(rows: list[tuple[Lead, str | None]]) -> bytes:
    """Generates an xlsx file from the lead rows."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Leads Ouro"

    headers = [col[0] for col in EXPORT_COLUMNS]
    ws.append(headers)

    for lead, _evento_ref in rows:
        row_data = [_get_cell_value(lead, field) for _, field in EXPORT_COLUMNS]
        ws.append(row_data)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _generate_csv(rows: list[tuple[Lead, str | None]]) -> bytes:
    """Generates a CSV file (semicolon separator, UTF-8 BOM) from the lead rows."""
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";", quoting=csv.QUOTE_MINIMAL)

    headers = [col[0] for col in EXPORT_COLUMNS]
    writer.writerow(headers)

    for lead, _evento_ref in rows:
        row_data = [_get_cell_value(lead, field) for _, field in EXPORT_COLUMNS]
        writer.writerow(row_data)

    # UTF-8 BOM + CSV content
    return b"\xef\xbb\xbf" + buf.getvalue().encode("utf-8")


def generate_gold_export(
    db: Session,
    evento_id: Optional[int],
    formato: str = "xlsx",
) -> tuple[bytes, str] | None:
    """Generates a Gold leads export file.

    Returns:
        (file_bytes, filename) tuple, or None if no matching leads exist.
    """
    rows = _build_query(db, evento_id)
    if not rows:
        return None

    # Resolve evento name for filename (first row has the evento ref if filtered)
    evento_nome: Optional[str] = None
    if evento_id is not None and rows:
        _lead, evento_ref = rows[0]
        evento_nome = evento_ref

    filename = build_filename(evento_nome, formato)

    if formato == "csv":
        file_bytes = _generate_csv(rows)
    else:
        file_bytes = _generate_xlsx(rows)

    return file_bytes, filename
