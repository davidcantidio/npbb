"""Rotas de importacao assistida para o dominio de publicidade."""

from __future__ import annotations

import json
import os

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from pydantic import TypeAdapter, ValidationError
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import Evento, Usuario
from app.schemas.publicidade_import import (
    PublicidadeAliasHit,
    PublicidadeAliasRead,
    PublicidadeAliasUpsert,
    PublicidadeEventReference,
    PublicidadeImportMapping,
    PublicidadeImportPreview,
    PublicidadeImportReport,
    PublicidadeImportValidateResponse,
)
from app.services.imports.alias_service import find_alias, upsert_alias
from app.services.imports.domain_publicidade import (
    PUBLICIDADE_DOMAIN_SPEC,
    canonical_publicidade_field_name,
)
from app.observability.prometheus_leads_import import record_import_upload_rejection
from app.services.imports.file_reader import (
    DEFAULT_IMPORT_MAX_BYTES,
    ImportFileError,
    inspect_upload,
    read_file_sample,
)
from app.services.imports.mapping_validator import validate_mappings
from app.services.imports.suggestion_engine import suggest_columns
from app.services.publicidade_import import run_publicidade_import
from app.utils.http_errors import raise_http_error

router = APIRouter(prefix="/publicidade", tags=["publicidade"])


def _get_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


MAX_IMPORT_FILE_BYTES = _get_env_int("PUBLICIDADE_IMPORT_MAX_BYTES", DEFAULT_IMPORT_MAX_BYTES)


def _raise_import_file_error(err: ImportFileError) -> None:
    raise_http_error(
        status.HTTP_400_BAD_REQUEST,
        code=err.code,
        message=err.message,
        field=err.field,
        extra=err.extra,
    )


def _validate_domain_mapping_or_400(mappings: list[PublicidadeImportMapping]) -> None:
    validation = validate_mappings(PUBLICIDADE_DOMAIN_SPEC, mappings)
    if validation.ok:
        return
    if validation.unknown_fields:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="MAPPING_UNKNOWN_FIELDS",
            message="Mapeamento contem campos desconhecidos para publicidade",
            extra={"unknown_fields": list(validation.unknown_fields)},
        )
    if validation.duplicated_fields:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="MAPPING_DUPLICATED_FIELDS",
            message="Mapeamento contem campos duplicados",
            extra={"duplicated_fields": list(validation.duplicated_fields)},
        )
    if validation.missing_required_fields:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="MAPPING_MISSING_REQUIRED_FIELDS",
            message="Mapeamento incompleto: faltam campos obrigatorios do dominio",
            extra={"missing_required_fields": list(validation.missing_required_fields)},
        )
    if validation.missing_required_key_fields:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="MAPPING_MISSING_KEY_FIELDS",
            message="Mapeamento incompleto: faltam campos obrigatorios da chave natural",
            extra={"missing_required_key_fields": list(validation.missing_required_key_fields)},
        )
    raise_http_error(
        status.HTTP_400_BAD_REQUEST,
        code="INVALID_MAPPING",
        message="Mapeamento invalido",
    )


def _normalize_mapping_fields(mappings: list[PublicidadeImportMapping]) -> list[PublicidadeImportMapping]:
    normalized: list[PublicidadeImportMapping] = []
    for mapping in mappings:
        normalized.append(
            PublicidadeImportMapping(
                coluna=mapping.coluna,
                campo=canonical_publicidade_field_name(mapping.campo),
                confianca=mapping.confianca,
            )
        )
    return normalized


@router.post("/import/upload")
@router.post("/import/upload/")
def validar_upload_publicidade(
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    try:
        filename, _, size = inspect_upload(file, max_bytes=MAX_IMPORT_FILE_BYTES)
    except ImportFileError as err:
        record_import_upload_rejection(err, filename_hint=file.filename)
        _raise_import_file_error(err)
    return {"filename": filename, "size_bytes": size}


@router.post("/import/preview", response_model=PublicidadeImportPreview)
@router.post("/import/preview/", response_model=PublicidadeImportPreview)
def preview_import_publicidade(
    file: UploadFile = File(...),
    sample_rows: int = Form(10),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    try:
        preview, _ = read_file_sample(file, sample_rows=sample_rows, max_bytes=MAX_IMPORT_FILE_BYTES)
    except ImportFileError as err:
        record_import_upload_rejection(err, filename_hint=file.filename)
        _raise_import_file_error(err)

    suggestions, samples_by_column = suggest_columns(PUBLICIDADE_DOMAIN_SPEC, preview.headers, preview.rows)
    suggestion_models = [
        PublicidadeImportMapping(coluna=item.coluna, campo=item.campo, confianca=item.confianca)
        for item in suggestions
    ]

    alias_hits: list[PublicidadeAliasHit | None] = []
    for index, suggestion in enumerate(suggestion_models):
        hit: PublicidadeAliasHit | None = None
        if suggestion.campo in PUBLICIDADE_DOMAIN_SPEC.alias_fields and samples_by_column[index]:
            alias = find_alias(
                session,
                domain=PUBLICIDADE_DOMAIN_SPEC.domain,
                field_name=str(suggestion.campo),
                source_value=samples_by_column[index][0],
            )
            if alias:
                hit = PublicidadeAliasHit.model_validate(alias, from_attributes=True)
        alias_hits.append(hit)

    return PublicidadeImportPreview(
        filename=preview.filename,
        headers=preview.headers,
        rows=preview.rows,
        delimiter=preview.delimiter,
        start_index=preview.start_index,
        suggestions=suggestion_models,
        samples_by_column=samples_by_column,
        alias_hits=alias_hits,
    )


@router.post("/import/validate", response_model=PublicidadeImportValidateResponse)
@router.post("/import/validate/", response_model=PublicidadeImportValidateResponse)
def validar_mapeamento_publicidade(
    mappings: list[PublicidadeImportMapping],
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    mappings = _normalize_mapping_fields(mappings)
    _validate_domain_mapping_or_400(mappings)
    return PublicidadeImportValidateResponse(ok=True)


@router.post("/import", response_model=PublicidadeImportReport)
@router.post("/import/", response_model=PublicidadeImportReport)
def importar_publicidade(
    file: UploadFile = File(...),
    mappings_json: str = Form(...),
    dry_run: bool = Form(False),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    try:
        raw = json.loads(mappings_json)
        mappings = TypeAdapter(list[PublicidadeImportMapping]).validate_python(raw)
    except (json.JSONDecodeError, ValidationError):
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_MAPPING",
            message="Mapeamento invalido",
            field="mappings_json",
        )

    mappings = _normalize_mapping_fields(mappings)
    _validate_domain_mapping_or_400(mappings)
    try:
        return run_publicidade_import(
            session,
            file=file,
            mappings=mappings,
            dry_run=dry_run,
            max_bytes=MAX_IMPORT_FILE_BYTES,
        )
    except ImportFileError as err:
        record_import_upload_rejection(err, filename_hint=file.filename)
        _raise_import_file_error(err)
    except ValueError as err:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="IMPORT_VALIDATION_ERROR",
            message=str(err),
        )


@router.get("/referencias/eventos", response_model=list[PublicidadeEventReference])
@router.get("/referencias/eventos/", response_model=list[PublicidadeEventReference])
def listar_referencias_eventos(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    rows = session.exec(
        select(Evento.id, Evento.nome, Evento.external_project_code).order_by(Evento.nome)
    ).all()
    references: list[PublicidadeEventReference] = []
    for evento_id, nome, external_project_code in rows:
        if evento_id is None or not nome:
            continue
        references.append(
            PublicidadeEventReference(
                id=int(evento_id),
                nome=str(nome),
                external_project_code=(external_project_code or None),
            )
        )
    return references


@router.get("/aliases", response_model=PublicidadeAliasRead | None)
@router.get("/aliases/", response_model=PublicidadeAliasRead | None)
def buscar_alias_publicidade(
    field_name: str = Query(..., min_length=1, max_length=80),
    valor_origem: str = Query(..., min_length=1, max_length=255),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    field_name = canonical_publicidade_field_name(field_name) or field_name
    if field_name not in PUBLICIDADE_DOMAIN_SPEC.field_names():
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_ALIAS_FIELD",
            message="field_name invalido para o dominio publicidade",
            field="field_name",
        )

    alias = find_alias(
        session,
        domain=PUBLICIDADE_DOMAIN_SPEC.domain,
        field_name=field_name,
        source_value=valor_origem,
    )
    if not alias:
        return None
    return PublicidadeAliasRead.model_validate(alias, from_attributes=True)


@router.post("/aliases", response_model=PublicidadeAliasRead, status_code=status.HTTP_201_CREATED)
@router.post("/aliases/", response_model=PublicidadeAliasRead, status_code=status.HTTP_201_CREATED)
def criar_alias_publicidade(
    payload: PublicidadeAliasUpsert,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    field_name = canonical_publicidade_field_name(payload.field_name) or payload.field_name
    if field_name not in PUBLICIDADE_DOMAIN_SPEC.field_names():
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_ALIAS_FIELD",
            message="field_name invalido para o dominio publicidade",
            field="field_name",
        )

    canonical_value = payload.canonical_value
    if payload.canonical_ref_id:
        evento = session.get(Evento, int(payload.canonical_ref_id))
        if not evento:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="EVENTO_NOT_FOUND",
                message="Evento de referencia nao encontrado",
                field="canonical_ref_id",
            )
        if not canonical_value and evento.external_project_code:
            canonical_value = evento.external_project_code

    try:
        alias = upsert_alias(
            session,
            domain=PUBLICIDADE_DOMAIN_SPEC.domain,
            field_name=field_name,
            source_value=payload.valor_origem,
            canonical_value=canonical_value,
            canonical_ref_id=payload.canonical_ref_id,
        )
    except ValueError:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_ALIAS_VALUE",
            message="valor_origem obrigatorio",
            field="valor_origem",
        )
    return PublicidadeAliasRead.model_validate(alias, from_attributes=True)
