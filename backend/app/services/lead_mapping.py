"""Servico de mapeamento Silver: sugestao de colunas e persistencia em leads_silver.

Fluxo:
  1. suggest_column_mapping(batch_id, db) -> list[ColumnSuggestion]
     Le arquivo_bronze do lote, extrai headers e retorna sugestao por coluna
     usando HEADER_SYNONYMS + LeadColumnAlias salvos.

  2. mapear_batch(batch_id, evento_id, mapeamento, user_id, db) -> MapearResult
     Le todas as linhas de arquivo_bronze, aplica mapeamento confirmado
     (coluna -> campo_canonico), persiste LeadSilver, salva aliases novos
     e atualiza stage do lote para silver.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlmodel import Session, select

from lead_pipeline.constants import ALL_COLUMNS, HEADER_SYNONYMS
from lead_pipeline.normalization import canonicalize_header

from app.models.lead_batch import BatchStage, LeadBatch, LeadColumnAlias, LeadSilver, PipelineStatus
from app.services.imports.file_reader import read_raw_file_headers, read_raw_file_rows


CANONICAL_FIELDS = frozenset(ALL_COLUMNS)
SOURCE_FILE_FIELD = "source_file"
SOURCE_SHEET_FIELD = "source_sheet"
SOURCE_ROW_FIELD = "source_row"
SOURCE_ROW_ORIGINAL_FIELD = "source_row_original"

Confidence = str  # "exact_match" | "synonym_match" | "alias_match" | "none"


@dataclass
class ColumnSuggestion:
    coluna_original: str
    campo_sugerido: str | None
    confianca: Confidence


@dataclass
class MapearResult:
    batch_id: int
    silver_count: int
    stage: str


def _suggest_for_header(
    header: str,
    aliases_by_coluna: dict[str, str],
) -> tuple[str | None, Confidence]:
    canonical = canonicalize_header(header)

    if canonical in CANONICAL_FIELDS:
        return canonical, "exact_match"

    synonym = HEADER_SYNONYMS.get(canonical)
    if synonym and synonym in CANONICAL_FIELDS:
        return synonym, "synonym_match"

    saved = aliases_by_coluna.get(header)
    if saved:
        return saved, "alias_match"

    saved_canonical = aliases_by_coluna.get(canonical)
    if saved_canonical:
        return saved_canonical, "alias_match"

    return None, "none"


def suggest_column_mapping(
    batch_id: int,
    db: Session,
) -> list[ColumnSuggestion]:
    """Retorna sugestoes automaticas de mapeamento para todas as colunas do lote."""
    batch = db.get(LeadBatch, batch_id)
    if not batch:
        raise ValueError(f"Lote {batch_id} nao encontrado")

    extracted = read_raw_file_headers(
        batch.arquivo_bronze,
        filename=batch.nome_arquivo_original,
    )
    headers = extracted.headers

    aliases = db.exec(
        select(LeadColumnAlias).where(LeadColumnAlias.plataforma_origem == batch.plataforma_origem)
    ).all()
    aliases_by_coluna: dict[str, str] = {a.nome_coluna_original: a.campo_canonico for a in aliases}

    suggestions: list[ColumnSuggestion] = []
    for header in headers:
        if not header:
            continue
        campo, confianca = _suggest_for_header(header, aliases_by_coluna)
        suggestions.append(
            ColumnSuggestion(
                coluna_original=header,
                campo_sugerido=campo,
                confianca=confianca,
            )
        )
    return suggestions


def mapear_batch(
    batch_id: int,
    evento_id: int,
    mapeamento: dict[str, str],
    user_id: int,
    db: Session,
) -> MapearResult:
    """Aplica mapeamento confirmado, persiste linhas silver, salva aliases, atualiza stage."""
    batch = db.get(LeadBatch, batch_id)
    if not batch:
        raise ValueError(f"Lote {batch_id} nao encontrado")

    extracted = read_raw_file_rows(
        batch.arquivo_bronze,
        filename=batch.nome_arquivo_original,
    )
    headers = extracted.headers
    data_rows = extracted.rows
    source_file = batch.nome_arquivo_original or ""
    source_sheet = extracted.sheet_name or ""
    source_row_offset = extracted.start_index + 2
    physical_lines = extracted.physical_line_numbers

    existing_silver = db.exec(select(LeadSilver).where(LeadSilver.batch_id == batch_id)).all()
    for row in existing_silver:
        db.delete(row)
    db.flush()

    silver_count = 0
    for row_index, row in enumerate(data_rows):
        dados_brutos: dict[str, Any] = {}
        for col_idx, header in enumerate(headers):
            campo_canonico = mapeamento.get(header)
            if not campo_canonico:
                continue
            value = row[col_idx] if col_idx < len(row) else ""
            dados_brutos[campo_canonico] = value

        if not dados_brutos:
            continue

        if len(physical_lines) == len(data_rows):
            physical_line = int(physical_lines[row_index])
        else:
            physical_line = source_row_offset + row_index

        dados_brutos[SOURCE_FILE_FIELD] = source_file
        dados_brutos[SOURCE_SHEET_FIELD] = source_sheet
        dados_brutos[SOURCE_ROW_ORIGINAL_FIELD] = physical_line
        dados_brutos[SOURCE_ROW_FIELD] = physical_line

        silver = LeadSilver(
            batch_id=batch_id,
            row_index=row_index,
            dados_brutos=dados_brutos,
            evento_id=evento_id,
        )
        db.add(silver)
        silver_count += 1

    for coluna_original, campo_canonico in mapeamento.items():
        if not campo_canonico:
            continue
        existing_alias = db.exec(
            select(LeadColumnAlias).where(
                LeadColumnAlias.nome_coluna_original == coluna_original,
                LeadColumnAlias.plataforma_origem == batch.plataforma_origem,
            )
        ).first()
        if existing_alias:
            if existing_alias.campo_canonico != campo_canonico:
                existing_alias.campo_canonico = campo_canonico
                db.add(existing_alias)
        else:
            alias = LeadColumnAlias(
                nome_coluna_original=coluna_original,
                campo_canonico=campo_canonico,
                plataforma_origem=batch.plataforma_origem,
                criado_por=user_id,
            )
            db.add(alias)

    batch.stage = BatchStage.SILVER
    batch.evento_id = evento_id
    batch.pipeline_status = PipelineStatus.PENDING
    batch.pipeline_report = None
    batch.pipeline_progress = None
    batch.gold_dq_discarded_rows = None
    batch.gold_dq_issue_counts = None
    batch.gold_dq_invalid_records_total = None
    db.add(batch)

    db.commit()

    return MapearResult(
        batch_id=batch_id,
        silver_count=silver_count,
        stage="silver",
    )
