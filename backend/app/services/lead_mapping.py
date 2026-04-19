"""Servico de mapeamento Silver: sugestao de colunas e persistencia em leads_silver.

Fluxo single:
  1. suggest_column_mapping(batch_id, db) -> list[ColumnSuggestion]
  2. mapear_batch(batch_id, evento_id, mapeamento, user_id, db) -> MapearResult

Fluxo batch:
  1. suggest_batch_column_mapping(batch_ids, db) -> BatchColumnPreview
  2. mapear_batches(batch_ids, mapeamento, user_id, db) -> BatchMapearResult

No modo batch, a agregacao e intencionalmente conservadora:
  - trim
  - lowercase
  - remocao de acentos
  - colapso de espacos internos
  - preservacao de pontuacao e separadores como "_" e "-"
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from sqlmodel import Session, select

from lead_pipeline.constants import ALL_COLUMNS, HEADER_SYNONYMS
from lead_pipeline.normalization import canonicalize_header, strip_accents

from app.models.lead_batch import BatchStage, LeadBatch, LeadColumnAlias, LeadSilver, PipelineStatus
from app.services.imports.file_reader import read_raw_file_headers, read_raw_file_rows
from app.services.imports.suggestion_engine import build_samples_by_column


CANONICAL_FIELDS = frozenset(ALL_COLUMNS)
SOURCE_FILE_FIELD = "source_file"
SOURCE_SHEET_FIELD = "source_sheet"
SOURCE_ROW_FIELD = "source_row"
SOURCE_ROW_ORIGINAL_FIELD = "source_row_original"
MAX_BATCH_COLUMN_SAMPLES = 5
BATCH_SOURCE_HEADER_AGGREGATION_RULE = (
    "trim + lowercase + remover acentos + colapsar espacos internos; preserva pontuacao e separadores como _ e -"
)

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


@dataclass
class BatchColumnOccurrence:
    batch_id: int
    file_name: str
    coluna_original: str
    amostras: list[str]
    campo_sugerido: str | None
    confianca: Confidence
    evento_id: int | None
    plataforma_origem: str


@dataclass
class BatchColumnGroup:
    chave_agregada: str
    nome_exibicao: str
    variantes: list[str]
    aparece_em_arquivos: int
    ocorrencias: list[BatchColumnOccurrence]
    campo_sugerido: str | None
    confianca: Confidence
    warnings: list[str] = field(default_factory=list)


@dataclass
class BatchColumnPreview:
    batch_ids: list[int]
    primary_batch_id: int | None
    aggregation_rule: str
    colunas: list[BatchColumnGroup]
    warnings: list[str]
    blockers: list[str]
    blocked_batch_ids: list[int]


@dataclass
class BatchMapearResult:
    primary_batch_id: int
    total_silver_count: int
    results: list[MapearResult]


@dataclass
class _LoadedBatchMappingContext:
    batch: LeadBatch
    headers: list[str]
    data_rows: list[list[str]]
    source_file: str
    source_sheet: str
    source_row_offset: int
    physical_lines: list[int]
    suggestions: list[ColumnSuggestion]
    samples_by_column: list[list[str]]
    blockers: list[str]


class BatchMappingBlockedError(ValueError):
    def __init__(self, blockers: list[str]):
        self.blockers = blockers
        super().__init__("; ".join(blockers))


def normalize_batch_source_header(header: str) -> str:
    """Normaliza o header do batch sem colapsar separadores como "_" e "-".

    A regra precisa ser mais conservadora do que `canonicalize_header` porque o
    mapeamento batch aplica a mesma decisao em varios arquivos. Preservar
    pontuacao e separadores evita over-grouping perigoso.
    """

    value = strip_accents(str(header or "").strip().lower())
    return " ".join(value.split())


def _load_aliases_by_platform(db: Session, plataforma_origem: str) -> dict[str, str]:
    aliases = db.exec(
        select(LeadColumnAlias).where(LeadColumnAlias.plataforma_origem == plataforma_origem)
    ).all()
    return {alias.nome_coluna_original: alias.campo_canonico for alias in aliases}


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


def _build_column_suggestions(headers: list[str], aliases_by_coluna: dict[str, str]) -> list[ColumnSuggestion]:
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


def _unique_positive_batch_ids(batch_ids: list[int]) -> list[int]:
    unique: list[int] = []
    seen: set[int] = set()
    for raw_batch_id in batch_ids:
        batch_id = int(raw_batch_id)
        if batch_id <= 0 or batch_id in seen:
            continue
        seen.add(batch_id)
        unique.append(batch_id)
    return unique


def _detect_batch_header_collisions(batch: LeadBatch, headers: list[str]) -> list[str]:
    collisions: list[str] = []
    headers_by_key: dict[str, list[str]] = defaultdict(list)

    for header in headers:
        if not header:
            continue
        key = normalize_batch_source_header(header)
        if not key:
            continue
        headers_by_key[key].append(header)

    for key, originals in headers_by_key.items():
        if len(originals) <= 1:
            continue
        originals_list = ", ".join(f'"{value}"' for value in originals)
        collisions.append(
            "Lote "
            f"#{batch.id} ({batch.nome_arquivo_original}) possui colunas que colidem na regra de agregacao batch "
            f'("{key}"): {originals_list}. Use o fluxo individual deste lote.'
        )
    return collisions


def _load_batch_mapping_context(batch_id: int, db: Session) -> _LoadedBatchMappingContext:
    batch = db.get(LeadBatch, batch_id)
    if not batch:
        raise ValueError(f"Lote {batch_id} nao encontrado")

    extracted = read_raw_file_rows(
        batch.arquivo_bronze,
        filename=batch.nome_arquivo_original,
    )
    headers = extracted.headers
    data_rows = extracted.rows
    aliases_by_coluna = _load_aliases_by_platform(db, batch.plataforma_origem)
    suggestions = _build_column_suggestions(headers, aliases_by_coluna)
    samples_by_column = build_samples_by_column(headers, data_rows, max_samples=MAX_BATCH_COLUMN_SAMPLES)

    blockers = _detect_batch_header_collisions(batch, headers)
    if batch.evento_id is None:
        blockers.append(
            f"Lote #{batch.id} ({batch.nome_arquivo_original}) nao possui evento de referencia salvo. "
            "Use o fluxo individual deste lote."
        )
    if batch.stage != BatchStage.BRONZE:
        blockers.append(
            f"Lote #{batch.id} ({batch.nome_arquivo_original}) esta em stage {batch.stage} e nao e elegivel "
            "para o mapeamento batch. Use apenas lotes em bronze."
        )

    return _LoadedBatchMappingContext(
        batch=batch,
        headers=headers,
        data_rows=data_rows,
        source_file=batch.nome_arquivo_original or "",
        source_sheet=extracted.sheet_name or "",
        source_row_offset=extracted.start_index + 2,
        physical_lines=extracted.physical_line_numbers,
        suggestions=suggestions,
        samples_by_column=samples_by_column,
        blockers=blockers,
    )


def _resolve_group_suggestion(occurrences: list[BatchColumnOccurrence]) -> tuple[str | None, Confidence, list[str]]:
    warnings: list[str] = []
    non_empty_suggestions = {occurrence.campo_sugerido for occurrence in occurrences if occurrence.campo_sugerido}

    if len(non_empty_suggestions) == 1 and len(non_empty_suggestions) == len(
        {occurrence.campo_sugerido or "" for occurrence in occurrences}
    ):
        campo = next(iter(non_empty_suggestions))
        confidence_order = {"exact_match": 3, "synonym_match": 2, "alias_match": 1, "none": 0}
        confianca = max(
            (occurrence.confianca for occurrence in occurrences),
            key=lambda value: confidence_order.get(value, -1),
        )
    else:
        campo = None
        confianca = "none"
        if len(non_empty_suggestions) > 1:
            warnings.append("Sugestoes automaticas divergentes entre os arquivos.")

    variantes = {occurrence.coluna_original for occurrence in occurrences}
    if len(variantes) > 1:
        warnings.append("Variacoes de cabecalho foram agrupadas pela regra normalizada do batch.")

    if len({occurrence.evento_id for occurrence in occurrences}) > 1:
        warnings.append("A coluna aparece em arquivos de eventos diferentes.")

    if len({occurrence.plataforma_origem for occurrence in occurrences}) > 1:
        warnings.append("A coluna aparece em arquivos de plataformas diferentes.")

    return campo, confianca, warnings


def _build_batch_column_preview(
    batch_ids: list[int],
    contexts: list[_LoadedBatchMappingContext],
) -> BatchColumnPreview:
    groups_by_key: dict[str, list[BatchColumnOccurrence]] = defaultdict(list)
    display_name_by_key: dict[str, str] = {}
    variants_by_key: dict[str, list[str]] = defaultdict(list)
    global_warnings: list[str] = []
    blockers: list[str] = []
    blocked_batch_ids: list[int] = []

    for context in contexts:
        if context.blockers and int(context.batch.id) not in blocked_batch_ids:
            blocked_batch_ids.append(int(context.batch.id))
        blockers.extend(context.blockers)
        suggestions_by_header = {
            suggestion.coluna_original: suggestion for suggestion in context.suggestions
        }

        for idx, header in enumerate(context.headers):
            if not header:
                continue
            key = normalize_batch_source_header(header)
            if not key:
                continue

            suggestion = suggestions_by_header.get(header)
            occurrence = BatchColumnOccurrence(
                batch_id=int(context.batch.id),
                file_name=context.batch.nome_arquivo_original,
                coluna_original=header,
                amostras=context.samples_by_column[idx] if idx < len(context.samples_by_column) else [],
                campo_sugerido=suggestion.campo_sugerido if suggestion else None,
                confianca=suggestion.confianca if suggestion else "none",
                evento_id=context.batch.evento_id,
                plataforma_origem=context.batch.plataforma_origem,
            )
            groups_by_key[key].append(occurrence)
            if key not in display_name_by_key:
                display_name_by_key[key] = header
            if header not in variants_by_key[key]:
                variants_by_key[key].append(header)

    platform_set = {context.batch.plataforma_origem for context in contexts}
    if len(platform_set) > 1:
        global_warnings.append(
            "O batch reune arquivos de plataformas diferentes. Alias salvos continuam sendo aplicados por lote."
        )

    event_set = {context.batch.evento_id for context in contexts if context.batch.evento_id is not None}
    if len(event_set) > 1:
        global_warnings.append(
            "O batch reune arquivos de eventos diferentes. Revise colunas ambiguas antes de aplicar o mesmo campo a todos."
        )

    groups: list[BatchColumnGroup] = []
    for key, occurrences in groups_by_key.items():
        campo_sugerido, confianca, warnings = _resolve_group_suggestion(occurrences)
        groups.append(
            BatchColumnGroup(
                chave_agregada=key,
                nome_exibicao=display_name_by_key[key],
                variantes=variants_by_key[key],
                aparece_em_arquivos=len({occurrence.batch_id for occurrence in occurrences}),
                ocorrencias=sorted(
                    occurrences,
                    key=lambda occurrence: (batch_ids.index(occurrence.batch_id), occurrence.coluna_original.lower()),
                ),
                campo_sugerido=campo_sugerido,
                confianca=confianca,
                warnings=warnings,
            )
        )

    groups.sort(key=lambda group: (-group.aparece_em_arquivos, group.nome_exibicao.lower()))

    return BatchColumnPreview(
        batch_ids=batch_ids,
        primary_batch_id=batch_ids[0] if batch_ids else None,
        aggregation_rule=BATCH_SOURCE_HEADER_AGGREGATION_RULE,
        colunas=groups,
        warnings=global_warnings,
        blockers=blockers,
        blocked_batch_ids=blocked_batch_ids,
    )


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
    aliases_by_coluna = _load_aliases_by_platform(db, batch.plataforma_origem)
    return _build_column_suggestions(extracted.headers, aliases_by_coluna)


def suggest_batch_column_mapping(
    batch_ids: list[int],
    db: Session,
) -> BatchColumnPreview:
    unique_batch_ids = _unique_positive_batch_ids(batch_ids)
    if not unique_batch_ids:
        raise ValueError("Informe ao menos um lote valido para o mapeamento batch.")

    contexts = [_load_batch_mapping_context(batch_id, db) for batch_id in unique_batch_ids]
    return _build_batch_column_preview(unique_batch_ids, contexts)


def _replace_existing_silver_rows(batch_id: int, db: Session) -> None:
    existing_silver = db.exec(select(LeadSilver).where(LeadSilver.batch_id == batch_id)).all()
    for row in existing_silver:
        db.delete(row)
    db.flush()


def _upsert_column_aliases(
    *,
    batch: LeadBatch,
    mapeamento: dict[str, str],
    user_id: int,
    db: Session,
) -> None:
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
            continue

        alias = LeadColumnAlias(
            nome_coluna_original=coluna_original,
            campo_canonico=campo_canonico,
            plataforma_origem=batch.plataforma_origem,
            criado_por=user_id,
        )
        db.add(alias)


def _apply_mapping_context(
    context: _LoadedBatchMappingContext,
    *,
    evento_id: int,
    mapeamento: dict[str, str],
    user_id: int,
    db: Session,
) -> MapearResult:
    _replace_existing_silver_rows(int(context.batch.id), db)

    silver_count = 0
    for row_index, row in enumerate(context.data_rows):
        dados_brutos: dict[str, Any] = {}
        for col_idx, header in enumerate(context.headers):
            campo_canonico = mapeamento.get(header)
            if not campo_canonico:
                continue
            value = row[col_idx] if col_idx < len(row) else ""
            dados_brutos[campo_canonico] = value

        if not dados_brutos:
            continue

        if len(context.physical_lines) == len(context.data_rows):
            physical_line = int(context.physical_lines[row_index])
        else:
            physical_line = context.source_row_offset + row_index

        dados_brutos[SOURCE_FILE_FIELD] = context.source_file
        dados_brutos[SOURCE_SHEET_FIELD] = context.source_sheet
        dados_brutos[SOURCE_ROW_ORIGINAL_FIELD] = physical_line
        dados_brutos[SOURCE_ROW_FIELD] = physical_line

        silver = LeadSilver(
            batch_id=int(context.batch.id),
            row_index=row_index,
            dados_brutos=dados_brutos,
            evento_id=evento_id,
        )
        db.add(silver)
        silver_count += 1

    _upsert_column_aliases(
        batch=context.batch,
        mapeamento=mapeamento,
        user_id=user_id,
        db=db,
    )

    context.batch.stage = BatchStage.SILVER
    context.batch.evento_id = evento_id
    context.batch.pipeline_status = PipelineStatus.PENDING
    context.batch.pipeline_report = None
    context.batch.pipeline_progress = None
    context.batch.gold_dq_discarded_rows = None
    context.batch.gold_dq_issue_counts = None
    context.batch.gold_dq_invalid_records_total = None
    db.add(context.batch)

    return MapearResult(
        batch_id=int(context.batch.id),
        silver_count=silver_count,
        stage="silver",
    )


def mapear_batch(
    batch_id: int,
    evento_id: int,
    mapeamento: dict[str, str],
    user_id: int,
    db: Session,
) -> MapearResult:
    """Aplica mapeamento confirmado em um lote e persiste a camada silver."""

    context = _load_batch_mapping_context(batch_id, db)
    try:
        result = _apply_mapping_context(
            context,
            evento_id=evento_id,
            mapeamento=mapeamento,
            user_id=user_id,
            db=db,
        )
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


def mapear_batches(
    batch_ids: list[int],
    mapeamento: dict[str, str],
    user_id: int,
    db: Session,
) -> BatchMapearResult:
    """Aplica um mapeamento agregado a varios lotes em uma unica transacao."""

    unique_batch_ids = _unique_positive_batch_ids(batch_ids)
    if not unique_batch_ids:
        raise ValueError("Informe ao menos um lote valido para o mapeamento batch.")

    normalized_mapping = {
        normalize_batch_source_header(chave): (campo or "").strip()
        for chave, campo in mapeamento.items()
        if normalize_batch_source_header(chave)
    }
    if not any(normalized_mapping.values()):
        raise ValueError("mapeamento nao pode ser vazio")

    contexts = [_load_batch_mapping_context(batch_id, db) for batch_id in unique_batch_ids]
    preview = _build_batch_column_preview(unique_batch_ids, contexts)
    if preview.blockers:
        raise BatchMappingBlockedError(preview.blockers)

    results: list[MapearResult] = []
    total_silver_count = 0
    try:
        for context in contexts:
            if context.batch.evento_id is None:
                raise BatchMappingBlockedError(
                    [f"Lote #{context.batch.id} nao possui evento de referencia salvo."]
                )

            batch_mapping: dict[str, str] = {}
            for header in context.headers:
                if not header:
                    continue
                selected_field = normalized_mapping.get(normalize_batch_source_header(header), "")
                if selected_field:
                    batch_mapping[header] = selected_field

            result = _apply_mapping_context(
                context,
                evento_id=int(context.batch.evento_id),
                mapeamento=batch_mapping,
                user_id=user_id,
                db=db,
            )
            results.append(result)
            total_silver_count += result.silver_count

        db.commit()
    except Exception:
        db.rollback()
        raise

    return BatchMapearResult(
        primary_batch_id=unique_batch_ids[0],
        total_silver_count=total_silver_count,
        results=results,
    )
