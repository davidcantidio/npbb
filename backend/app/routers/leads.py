"""Rotas de conversoes de lead."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from pydantic import TypeAdapter, ValidationError
from openpyxl import load_workbook
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import Lead, LeadConversao, Usuario, now_utc
from app.schemas.lead_conversao import LeadConversaoCreate, LeadConversaoRead
from app.schemas.lead_import import LeadImportMapping
from app.utils.http_errors import raise_http_error
from app.utils.lead_import_normalize import coerce_field

router = APIRouter(prefix="/leads", tags=["leads"])

ALLOWED_IMPORT_EXTENSIONS = {".csv", ".xlsx"}
MAX_IMPORT_FILE_BYTES = 15 * 1024 * 1024


def _get_lead_or_404(*, session: Session, lead_id: int) -> Lead:
    lead = session.get(Lead, lead_id)
    if not lead:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="LEAD_NOT_FOUND",
            message="Lead nao encontrado",
        )
    return lead


@router.post("/{lead_id}/conversoes", response_model=LeadConversaoRead, status_code=status.HTTP_201_CREATED)
@router.post("/{lead_id}/conversoes/", response_model=LeadConversaoRead, status_code=status.HTTP_201_CREATED)
def criar_conversao(
    lead_id: int,
    payload: LeadConversaoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    lead = _get_lead_or_404(session=session, lead_id=lead_id)

    conversao = LeadConversao(
        lead_id=lead.id,
        tipo=payload.tipo,
        acao_nome=payload.acao_nome,
        fonte_origem=payload.fonte_origem,
        evento_id=payload.evento_id,
        created_at=now_utc(),
    )
    session.add(conversao)
    session.commit()
    session.refresh(conversao)
    return LeadConversaoRead.model_validate(conversao, from_attributes=True)


@router.get("/{lead_id}/conversoes", response_model=list[LeadConversaoRead])
@router.get("/{lead_id}/conversoes/", response_model=list[LeadConversaoRead])
def listar_conversoes(
    lead_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    _get_lead_or_404(session=session, lead_id=lead_id)
    conversoes = session.exec(
        select(LeadConversao).where(LeadConversao.lead_id == lead_id).order_by(LeadConversao.created_at.desc())
    ).all()
    return [LeadConversaoRead.model_validate(item, from_attributes=True) for item in conversoes]


@router.post("/import/upload")
@router.post("/import/upload/")
def validar_upload_import(
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_IMPORT_EXTENSIONS:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_FILE_TYPE",
            message="Formato de arquivo invalido (use .csv ou .xlsx)",
            field="file",
        )

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_IMPORT_FILE_BYTES:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="FILE_TOO_LARGE",
            message="Arquivo excede o tamanho maximo permitido",
            field="file",
            extra={"max_bytes": MAX_IMPORT_FILE_BYTES},
        )
    if size == 0:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="EMPTY_FILE",
            message="Arquivo vazio",
            field="file",
        )

    return {"filename": filename, "size_bytes": size}


def _detect_csv_delimiter(sample_text: str) -> str:
    first_line = sample_text.splitlines()[0] if sample_text else ""
    comma_count = first_line.count(",")
    semi_count = first_line.count(";")
    return ";" if semi_count > comma_count else ","


def _score_row_tabular(row: list[str]) -> int:
    non_empty = [cell for cell in row if cell.strip()]
    if not row:
        return 0
    fill_ratio = len(non_empty) / max(len(row), 1)
    if len(non_empty) >= 2 and fill_ratio >= 0.5:
        return int(fill_ratio * 100)
    return 0


def _detect_data_start_index(rows: list[list[str]]) -> int:
    best_idx = 0
    best_score = -1
    for idx, row in enumerate(rows[:50]):
        score = _score_row_tabular(row)
        if score > best_score:
            best_score = score
            best_idx = idx
    return best_idx


def _read_csv_sample(file: UploadFile, max_rows: int) -> dict:
    file.file.seek(0)
    sample_bytes = file.file.read(4096)
    try:
        sample_text = sample_bytes.decode("utf-8-sig", errors="ignore")
    except Exception:
        sample_text = ""
    delimiter = _detect_csv_delimiter(sample_text)

    file.file.seek(0)
    reader = csv.reader(file.file, delimiter=delimiter)
    rows: list[list[str]] = []
    for row in reader:
        if row is None:
            continue
        rows.append([cell.strip() for cell in row])
        if len(rows) >= max_rows + 1:
            break

    start_index = _detect_data_start_index(rows)
    headers = rows[start_index] if rows else []
    data_rows = rows[start_index + 1 :] if len(rows) > start_index + 1 else []
    return {
        "headers": headers,
        "rows": data_rows,
        "delimiter": delimiter,
        "start_index": start_index,
    }


def _read_xlsx_sample(file: UploadFile, max_rows: int) -> dict:
    file.file.seek(0)
    wb = load_workbook(file.file, read_only=True, data_only=True)
    ws = wb.worksheets[0]
    rows: list[list[str]] = []
    for row in ws.iter_rows(max_row=max_rows + 1, values_only=True):
        rows.append([("" if v is None else str(v)).strip() for v in row])
        if len(rows) >= max_rows + 1:
            break
    start_index = _detect_data_start_index(rows)
    headers = rows[start_index] if rows else []
    data_rows = rows[start_index + 1 :] if len(rows) > start_index + 1 else []
    return {
        "headers": headers,
        "rows": data_rows,
        "delimiter": None,
        "start_index": start_index,
    }


def _ensure_mapping_has_essential(mappings: list[LeadImportMapping]) -> None:
    essential = {"email", "cpf"}
    mapped_fields = {m.campo for m in mappings if m.campo}
    if not (mapped_fields & essential):
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="MAPPING_MISSING_ESSENTIAL",
            message="Mapeamento deve incluir email ou CPF",
        )


def _column_samples(rows: list[list[str]], col_index: int, max_samples: int = 5) -> list[str]:
    samples: list[str] = []
    for row in rows:
        if col_index >= len(row):
            continue
        value = row[col_index].strip()
        if not value:
            continue
        samples.append(value)
        if len(samples) >= max_samples:
            break
    return samples


def _score_email(values: list[str]) -> float:
    if not values:
        return 0.0
    pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    hits = sum(1 for v in values if pattern.match(v.lower()))
    return hits / len(values)


def _score_cpf(values: list[str]) -> float:
    if not values:
        return 0.0
    pattern = re.compile(r"^\d{11}$")
    hits = 0
    for v in values:
        digits = "".join(ch for ch in v if ch.isdigit())
        if pattern.match(digits):
            hits += 1
    return hits / len(values)


def _score_date(values: list[str]) -> float:
    if not values:
        return 0.0
    patterns = [
        re.compile(r"^\d{2}/\d{2}/\d{4}$"),
        re.compile(r"^\d{4}-\d{2}-\d{2}$"),
    ]
    hits = sum(1 for v in values if any(p.match(v.strip()) for p in patterns))
    return hits / len(values)


def _score_number(values: list[str]) -> float:
    if not values:
        return 0.0
    hits = 0
    for v in values:
        text = v.strip().replace(".", "").replace(",", ".")
        try:
            float(text)
            hits += 1
        except ValueError:
            continue
    return hits / len(values)


def _infer_column_mapping(header: str, samples: list[str]) -> LeadImportMapping:
    header_lc = header.lower().strip()
    scores = {
        "email": _score_email(samples),
        "cpf": _score_cpf(samples),
        "data": _score_date(samples),
        "numero": _score_number(samples),
    }

    campo = None
    confianca = None
    if scores["email"] >= 0.7:
        campo = "email"
        confianca = scores["email"]
    elif scores["cpf"] >= 0.7:
        campo = "cpf"
        confianca = scores["cpf"]
    elif "email" in header_lc:
        campo = "email"
        confianca = max(scores["email"], 0.6)
    elif "cpf" in header_lc:
        campo = "cpf"
        confianca = max(scores["cpf"], 0.6)
    elif "data" in header_lc or "nasc" in header_lc:
        campo = "data_nascimento"
        confianca = max(scores["data"], 0.5)
    elif scores["data"] >= 0.7:
        campo = "data_nascimento"
        confianca = scores["data"]
    elif scores["numero"] >= 0.7:
        campo = "ingresso_qtd"
        confianca = scores["numero"]

    return LeadImportMapping(coluna=header or "", campo=campo, confianca=confianca)


 


@router.post("/import/sample")
@router.post("/import/sample/")
def preview_import_sample(
    file: UploadFile = File(...),
    sample_rows: int = 10,
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_IMPORT_EXTENSIONS:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_FILE_TYPE",
            message="Formato de arquivo invalido (use .csv ou .xlsx)",
            field="file",
        )
    if sample_rows < 1 or sample_rows > 50:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_SAMPLE_SIZE",
            message="sample_rows deve ser entre 1 e 50",
            field="sample_rows",
        )

    if ext == ".xlsx":
        preview = _read_xlsx_sample(file, max_rows=sample_rows)
    else:
        preview = _read_csv_sample(file, max_rows=sample_rows)
    if not preview["rows"] and not preview["headers"]:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="EMPTY_FILE",
            message="Arquivo vazio",
            field="file",
        )
    headers = preview["headers"]
    rows = preview["rows"]
    suggestions: list[LeadImportMapping] = []
    samples_by_column: list[list[str]] = []
    for idx, header in enumerate(headers):
        samples = _column_samples(rows, idx)
        samples_by_column.append(samples)
        suggestions.append(_infer_column_mapping(header, samples))

    return {
        "filename": filename,
        **preview,
        "suggestions": [s.model_dump() for s in suggestions],
        "samples_by_column": samples_by_column,
    }


@router.post("/import/validate")
@router.post("/import/validate/")
def validar_mapeamento(
    mappings: list[LeadImportMapping],
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    _ensure_mapping_has_essential(mappings)
    return {"ok": True}


@router.post("/import")
@router.post("/import/")
def importar_leads(
    file: UploadFile = File(...),
    mappings_json: str = Form(...),
    fonte_origem: str | None = Form(None),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_IMPORT_EXTENSIONS:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_FILE_TYPE",
            message="Formato de arquivo invalido (use .csv ou .xlsx)",
            field="file",
        )
    if ext == ".xlsx":
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="XLSX_IMPORT_NOT_SUPPORTED",
            message="Importacao de .xlsx nao suportada no momento",
            field="file",
        )

    try:
        raw = json.loads(mappings_json)
        mappings = TypeAdapter(list[LeadImportMapping]).validate_python(raw)
    except (json.JSONDecodeError, ValidationError):
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_MAPPING",
            message="Mapeamento invalido",
            field="mappings",
        )

    _ensure_mapping_has_essential(mappings)

    preview = _read_csv_sample(file, max_rows=20)
    headers = preview["headers"]
    start_index = preview["start_index"]
    delimiter = preview["delimiter"]

    file.file.seek(0)
    reader = csv.reader(file.file, delimiter=delimiter)
    rows = list(reader)
    data_rows = rows[start_index + 1 :] if len(rows) > start_index + 1 else []

    mapping_by_index: dict[int, str] = {}
    for idx, m in enumerate(mappings):
        if m.campo:
            mapping_by_index[idx] = m.campo

    created = 0
    updated = 0
    skipped = 0

    with Session(get_session().__next__().bind) as session:
        for row in data_rows:
            if not row:
                continue
            payload: dict[str, object] = {}
            for idx, field in mapping_by_index.items():
                if idx >= len(row):
                    continue
                payload[field] = coerce_field(field, row[idx])

            if "fonte_origem" in Lead.model_fields and fonte_origem:
                payload["fonte_origem"] = fonte_origem

            lead = Lead(**payload)
            try:
                session.add(lead)
                session.commit()
                created += 1
            except IntegrityError:
                session.rollback()
                email = payload.get("email")
                cpf = payload.get("cpf")
                evento_nome = payload.get("evento_nome")
                sessao = payload.get("sessao")
                if not email and not cpf:
                    skipped += 1
                    continue
                email_clause = Lead.email.is_(None) if email is None else Lead.email == email
                cpf_clause = Lead.cpf.is_(None) if cpf is None else Lead.cpf == cpf
                evento_clause = Lead.evento_nome.is_(None) if evento_nome is None else Lead.evento_nome == evento_nome
                sessao_clause = Lead.sessao.is_(None) if sessao is None else Lead.sessao == sessao
                existing = session.exec(
                    select(Lead).where(email_clause, cpf_clause, evento_clause, sessao_clause)
                ).first()
                if not existing:
                    skipped += 1
                    continue
                for key, value in payload.items():
                    if value is not None:
                        setattr(existing, key, value)
                session.add(existing)
                session.commit()
                updated += 1

    return {"filename": filename, "created": created, "updated": updated, "skipped": skipped}


@router.post("/import/preview")
@router.post("/import/preview/")
def preview_import(
    file: UploadFile = File(...),
    sample_rows: int = 10,
    current_user: Usuario = Depends(get_current_user),
):
    return preview_import_sample(file=file, sample_rows=sample_rows, current_user=current_user)
