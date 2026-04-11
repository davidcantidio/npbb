"""Transform and validate XLSX ETL rows for backend preview."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from core.leads_etl.models import etl_payload_to_lead_row
from core.leads_etl.models._errors import LeadRowAdapterError
from core.leads_etl.transform.column_normalize import normalize_column_name
from core.leads_etl.validate.framework import Check, CheckContext, CheckReport, CheckResult, CheckRunner, CheckStatus, Severity

from .contracts import EtlPreviewRow
from .validators import validate_normalized_lead_payload


@dataclass(frozen=True)
class _PreviewValidationState:
    approved_rows: tuple[EtlPreviewRow, ...]
    rejected_rows: tuple[EtlPreviewRow, ...]


class _RejectedRowsCheck(Check):
    check_id = "dq.preview.rejected_rows"
    description = "Rows rejected by canonical LeadRow validation."

    def run(self, context: CheckContext) -> CheckResult:
        state: _PreviewValidationState = context.require_resource("preview_state")
        sample = [
            {"row_number": row.row_number, "errors": row.errors}
            for row in state.rejected_rows[:5]
        ]
        status = CheckStatus.FAIL if state.rejected_rows else CheckStatus.PASS
        severity = Severity.ERROR if state.rejected_rows else Severity.INFO
        return CheckResult(
            check_id=self.check_id,
            status=status,
            severity=severity,
            message="Linhas invalidas encontradas no contrato canonico." if state.rejected_rows else "Nenhuma linha invalida no contrato canonico.",
            evidence={
                "finding_count": len(state.rejected_rows),
                "findings_sample": sample,
            },
        )


class _DuplicateRowsCheck(Check):
    check_id = "dq.preview.duplicates"
    description = "Duplicate rows inside preview batch."

    def run(self, context: CheckContext) -> CheckResult:
        state: _PreviewValidationState = context.require_resource("preview_state")
        seen: dict[str, list[int]] = {}
        duplicates: list[dict[str, Any]] = []
        for row in state.approved_rows:
            payload = row.payload
            email = str(payload.get("email") or "")
            cpf = str(payload.get("cpf") or "")
            evento_nome = str(payload.get("evento_nome") or "")
            sessao = str(payload.get("sessao") or "")
            if not email and not cpf:
                continue
            key = f"{email}|{cpf}|{evento_nome}|{sessao}"
            refs = seen.setdefault(key, [])
            refs.append(row.row_number)
        for key, row_numbers in seen.items():
            if len(row_numbers) > 1:
                duplicates.append({"dedupe_key": key, "row_numbers": row_numbers})
        status = CheckStatus.FAIL if duplicates else CheckStatus.PASS
        severity = Severity.WARNING if duplicates else Severity.INFO
        return CheckResult(
            check_id=self.check_id,
            status=status,
            severity=severity,
            message="Duplicidades encontradas no proprio lote." if duplicates else "Nenhuma duplicidade detectada no lote.",
            evidence={
                "duplicate_group_count": len(duplicates),
                "duplicate_total_rows": sum(len(item["row_numbers"]) for item in duplicates),
                "sample_duplicates": duplicates[:5],
            },
        )


def _normalize_payload(raw_row: dict[str, Any], *, evento_nome: str) -> dict[str, Any]:
    payload: dict[str, Any] = {"evento_nome": evento_nome}
    for key, value in raw_row.items():
        if key.startswith("__"):
            continue
        normalized_key = normalize_column_name(key)
        payload[normalized_key] = value
    if "evento" in payload and not payload.get("evento_nome"):
        payload["evento_nome"] = payload.get("evento")
    if "sexo" in payload and "genero" not in payload:
        payload["genero"] = payload.get("sexo")
    return payload


def build_preview_state(raw_rows: list[dict[str, Any]], *, evento_nome: str) -> _PreviewValidationState:
    approved_rows: list[EtlPreviewRow] = []
    rejected_rows: list[EtlPreviewRow] = []
    for row in raw_rows:
        row_number = int(row.get("__row_number") or 0)
        normalized = _normalize_payload(row, evento_nome=evento_nome)
        try:
            lead_row = etl_payload_to_lead_row(normalized)
        except (LeadRowAdapterError, ValidationError) as exc:
            rejected_rows.append(
                EtlPreviewRow(
                    row_number=row_number,
                    payload=normalized,
                    errors=[str(exc)] if isinstance(exc, LeadRowAdapterError) else [error["msg"] for error in exc.errors()],
                )
            )
            continue
        payload = lead_row.model_dump(mode="python")
        validation_errors = validate_normalized_lead_payload(payload)
        if validation_errors:
            rejected_rows.append(
                EtlPreviewRow(
                    row_number=row_number,
                    payload=payload,
                    errors=validation_errors,
                )
            )
            continue
        approved_rows.append(
            EtlPreviewRow(
                row_number=row_number,
                payload=payload,
                errors=[],
            )
        )
    return _PreviewValidationState(
        approved_rows=tuple(approved_rows),
        rejected_rows=tuple(rejected_rows),
    )


def run_preview_validation(raw_rows: list[dict[str, Any]], *, evento_nome: str) -> tuple[_PreviewValidationState, CheckReport]:
    state = build_preview_state(raw_rows, evento_nome=evento_nome)
    report = CheckRunner((_RejectedRowsCheck(), _DuplicateRowsCheck()), fail_on=Severity.ERROR).run(
        CheckContext(
            ingestion_id=None,
            resources={"preview_state": state},
        )
    )
    return state, report
