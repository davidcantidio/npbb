from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable
import zipfile

import pandas as pd

from .constants import (
    ALL_COLUMNS,
    FINAL_FILENAME,
    OPTIONAL_COLUMNS,
    WARNING_ARQUIVO_ENCRIPTADO,
    WARNING_ARQUIVO_FONTE_AGREGADA,
    WARNING_ARQUIVO_ZIP_DUPLICADO,
    WARNING_CIDADE_FORA_MAPEAMENTO,
    WARNING_CPF_INVALIDO,
    WARNING_DATA_NASCIMENTO_AUSENTE,
    WARNING_DATA_NASCIMENTO_INVALIDA,
    WARNING_DUPLICIDADE_CPF_EVENTO,
    WARNING_LOCALIDADE_INVALIDA,
)
from .contracts import validate_databricks_contract
from .event_taxonomy import classify_event_type
from .geo_normalize import (
    LocalityNormalizationResult,
    normalize_brazilian_locality,
)
from .normalization import (
    BirthDateIssue,
    is_valid_cpf,
    normalize_cpf,
    normalize_data_nascimento,
    normalize_email,
    normalize_phone,
    parse_date,
)
from .source_adapter import (
    CITY_OUT_COL,
    REJECT_REASON_COL,
    ROW_COL_SOURCE,
    SHEET_COL_SOURCE,
    adapt_source_file,
    get_mapping_version,
)


@dataclass
class PipelineConfig:
    lote_id: str
    input_files: list[Path]
    scan_root: Path | None = None
    output_root: Path = Path("./eventos")
    anchored_on_evento_id: bool = False
    on_progress: Callable[["PipelineProgressEvent"], None] | None = None


@dataclass
class PipelineProgressEvent:
    step: str
    label: str
    pct: int | None = None
    meta: dict[str, Any] | None = None


@dataclass
class QualityMetrics:
    cpf_invalid_discarded: int = 0
    telefone_invalid: int = 0
    data_evento_invalid: int = 0
    data_nascimento_invalid: int = 0
    data_nascimento_missing: int = 0
    duplicidades_cpf_evento: int = 0
    cidade_fora_mapeamento: int = 0
    localidade_invalida: int = 0
    localidade_nao_resolvida: int = 0
    localidade_fora_brasil: int = 0
    localidade_cidade_uf_inconsistente: int = 0


@dataclass
class PipelineResult:
    lote_id: str
    status: str
    decision: str
    output_dir: Path
    report_path: Path
    summary_path: Path
    consolidated_path: Path
    exit_code: int


def _is_encrypted_ole_office(path: Path) -> bool:
    try:
        with path.open("rb") as file_handle:
            return file_handle.read(8) == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
    except OSError:
        return False


def _scan_root_inputs(scan_root: Path) -> tuple[list[Path], list[dict[str, str]], list[str]]:
    discovered: list[Path] = []
    skipped: list[dict[str, str]] = []
    scanned: list[str] = []

    for item in sorted(scan_root.iterdir(), key=lambda entry: entry.name.lower()):
        if not item.is_file():
            continue
        suffix = item.suffix.lower()
        if suffix not in {".csv", ".xlsx", ".zip"}:
            continue
        scanned.append(str(item))

        if suffix == ".zip":
            duplicate = False
            try:
                with zipfile.ZipFile(item) as zip_file:
                    zip_names = {
                        Path(member).name
                        for member in zip_file.namelist()
                        if member and not member.endswith("/")
                    }
                duplicate = any((scan_root / name).exists() for name in zip_names)
            except zipfile.BadZipFile:
                duplicate = False

            if duplicate:
                skipped.append({"file": str(item), "reason": WARNING_ARQUIVO_ZIP_DUPLICADO})
            else:
                skipped.append({"file": str(item), "reason": "ARQUIVO_ZIP_NAO_PROCESSADO"})
            continue

        if item.name == "fonte_de_dados.csv":
            skipped.append({"file": str(item), "reason": WARNING_ARQUIVO_FONTE_AGREGADA})
            continue

        if item.name == "modelo.csv":
            skipped.append({"file": str(item), "reason": "ARQUIVO_EXCLUIDO_PADRAO"})
            continue

        if item.name.endswith("_decrypted.xlsx"):
            skipped.append({"file": str(item), "reason": "ARQUIVO_TEMPORARIO_DECRYPTED_IGNORADO"})
            continue

        if suffix == ".xlsx" and _is_encrypted_ole_office(item):
            skipped.append({"file": str(item), "reason": WARNING_ARQUIVO_ENCRIPTADO})
            continue

        discovered.append(item)

    return discovered, skipped, scanned


def _ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _emit_progress(
    config: PipelineConfig,
    *,
    step: str,
    label: str,
    pct: int | None = None,
) -> None:
    if config.on_progress is None:
        return
    config.on_progress(PipelineProgressEvent(step=step, label=label, pct=pct))


def _truncate_for_report(value: str, *, limit: int = 120) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3].rstrip()}..."


def _stringify_row_for_report(row: dict[str, Any]) -> dict[str, str]:
    """Keep report payloads JSON-safe without mutating types used for normalization."""

    return {
        column: "" if row.get(column) is None else str(row.get(column, ""))
        for column in ALL_COLUMNS
    }


def _register_locality_issue(
    metrics: QualityMetrics,
    locality_result: LocalityNormalizationResult,
) -> None:
    if locality_result.issue_code is None:
        return

    metrics.localidade_invalida += 1
    if locality_result.issue_code == "non_br":
        metrics.localidade_fora_brasil += 1
    elif locality_result.issue_code == "cidade_uf_mismatch":
        metrics.localidade_cidade_uf_inconsistente += 1
    else:
        metrics.localidade_nao_resolvida += 1


def _normalize_row(
    row: dict[str, Any],
    *,
    city_out_of_mapping: bool,
    ref_date_utc: date,
    event_locality_owned: bool = False,
) -> tuple[
    dict[str, str],
    list[str],
    BirthDateIssue | None,
    LocalityNormalizationResult,
]:
    reasons: list[str] = []

    cpf = normalize_cpf(row.get("cpf", ""))
    phone = normalize_phone(row.get("telefone", ""))
    event_date = parse_date(row.get("data_evento", ""))
    birth_date, birth_date_issue = normalize_data_nascimento(
        row.get("data_nascimento", ""),
        ref_date=ref_date_utc,
    )
    event_locality_result: LocalityNormalizationResult | None = None
    if event_locality_owned:
        event_locality_result = normalize_brazilian_locality(local=row.get("local", ""))
        locality_result = normalize_brazilian_locality(
            cidade=row.get("cidade", ""),
            estado=row.get("estado", ""),
        )
    else:
        locality_result = normalize_brazilian_locality(
            cidade=row.get("cidade", ""),
            estado=row.get("estado", ""),
            local=row.get("local", ""),
        )

    if not is_valid_cpf(cpf):
        reasons.append("CPF_INVALIDO")
    if phone and len(phone) < 10:
        reasons.append("TELEFONE_INVALIDO")
    if event_date is None:
        reasons.append("DATA_EVENTO_INVALIDA")
    elif event_date == "" and not city_out_of_mapping:
        reasons.append("DATA_EVENTO_INVALIDA")

    normalized_row = {
        "nome": str(row.get("nome", "")).strip(),
        "cpf": cpf,
        "data_nascimento": birth_date,
        "email": normalize_email(row.get("email", "")),
        "telefone": phone,
        "evento": str(row.get("evento", "")).strip(),
        "tipo_evento": str(row.get("tipo_evento", "")).strip(),
        "local": (
            event_locality_result.local or str(row.get("local", "")).strip()
            if event_locality_owned and event_locality_result is not None
            else locality_result.local
        ),
        "data_evento": event_date if event_date is not None else "",
    }
    for column in OPTIONAL_COLUMNS:
        normalized_row[column] = str(row.get(column, "") or "").strip()
    normalized_row["cidade"] = locality_result.cidade
    normalized_row["estado"] = locality_result.estado
    return normalized_row, reasons, birth_date_issue, locality_result


def _build_report(
    config: PipelineConfig,
    *,
    run_timestamp: datetime,
    raw_rows: int,
    valid_rows: int,
    metrics: QualityMetrics,
    fail_reasons: list[str],
    warnings: list[str],
    invalid_records: list[dict[str, Any]],
    data_nascimento_controle: list[dict[str, Any]],
    localidade_controle: list[dict[str, Any]],
    cidade_fora_mapeamento_controle: list[dict[str, Any]],
    source_profiles_detected: dict[str, list[str]],
    input_files_scanned: list[str],
    input_files_processed: list[str],
    input_files_skipped: list[dict[str, str]],
) -> dict[str, Any]:
    if fail_reasons:
        status = "FAIL"
        decision = "hold"
        exit_code = 2
    elif warnings:
        status = "PASS_WITH_WARNINGS"
        decision = "promote"
        exit_code = 0
    else:
        status = "PASS"
        decision = "promote"
        exit_code = 0

    report = {
        "lote_id": config.lote_id,
        "run_timestamp": run_timestamp.isoformat(),
        "input_files": [str(path) for path in config.input_files],
        "input_files_scanned": input_files_scanned,
        "input_files_processed": input_files_processed,
        "input_files_skipped": input_files_skipped,
        "source_profiles_detected": source_profiles_detected,
        "mapping_version": get_mapping_version(),
        "totals": {
            "raw_rows": raw_rows,
            "valid_rows": valid_rows,
            "discarded_rows": raw_rows - valid_rows,
        },
        "quality_metrics": asdict(metrics),
        "gate": {
            "status": status,
            "decision": decision,
            "fail_reasons": fail_reasons,
            "warnings": warnings,
        },
        "data_nascimento_controle": data_nascimento_controle,
        "localidade_controle": localidade_controle,
        "cidade_fora_mapeamento_controle": cidade_fora_mapeamento_controle,
        "invalid_records": invalid_records,
        "exit_code": exit_code,
    }
    return report


def _write_summary(report: dict[str, Any], summary_path: Path) -> None:
    gate = report["gate"]
    totals = report["totals"]
    metrics = report["quality_metrics"]

    lines = [
        "# Validation Summary",
        "",
        f"Lote: {report['lote_id']}",
        f"Status: {gate['status']}",
        f"Decision: {gate['decision']}",
        f"Source profiles: {report.get('source_profiles_detected', {})}",
        f"Mapping version: {report.get('mapping_version', '')}",
        "",
        "## Inputs",
        f"- input_files_scanned: {len(report.get('input_files_scanned', []))}",
        f"- input_files_processed: {len(report.get('input_files_processed', []))}",
        f"- input_files_skipped: {len(report.get('input_files_skipped', []))}",
        "",
        "## Totals",
        f"- raw_rows: {totals['raw_rows']}",
        f"- valid_rows: {totals['valid_rows']}",
        f"- discarded_rows: {totals['discarded_rows']}",
        "",
        "## Quality Metrics",
        f"- cpf_invalid_discarded: {metrics['cpf_invalid_discarded']}",
        f"- telefone_invalid: {metrics['telefone_invalid']}",
        f"- data_evento_invalid: {metrics['data_evento_invalid']}",
        f"- data_nascimento_invalid: {metrics['data_nascimento_invalid']}",
        f"- data_nascimento_missing: {metrics['data_nascimento_missing']}",
        f"- duplicidades_cpf_evento: {metrics['duplicidades_cpf_evento']}",
        f"- cidade_fora_mapeamento: {metrics['cidade_fora_mapeamento']}",
        f"- localidade_invalida: {metrics['localidade_invalida']}",
        f"- localidade_nao_resolvida: {metrics['localidade_nao_resolvida']}",
        f"- localidade_fora_brasil: {metrics['localidade_fora_brasil']}",
        (
            "- localidade_cidade_uf_inconsistente: "
            f"{metrics['localidade_cidade_uf_inconsistente']}"
        ),
        "",
        "## Skips",
        f"- {report.get('input_files_skipped', [])}",
        "",
        "## Gate",
        f"- fail_reasons: {gate['fail_reasons']}",
        f"- warnings: {gate['warnings']}",
        f"- localidade_controle: {len(report.get('localidade_controle', []))}",
    ]
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _collect_metric_warnings(metrics: QualityMetrics) -> list[str]:
    warnings: list[str] = []
    if metrics.cpf_invalid_discarded:
        warnings.append(WARNING_CPF_INVALIDO)
    if metrics.telefone_invalid:
        warnings.append("TELEFONE_INVALIDO")
    if metrics.data_evento_invalid:
        warnings.append("DATA_EVENTO_INVALIDA")
    if metrics.data_nascimento_invalid:
        warnings.append(WARNING_DATA_NASCIMENTO_INVALIDA)
    if metrics.data_nascimento_missing:
        warnings.append(WARNING_DATA_NASCIMENTO_AUSENTE)
    if metrics.duplicidades_cpf_evento:
        warnings.append(WARNING_DUPLICIDADE_CPF_EVENTO)
    if metrics.cidade_fora_mapeamento:
        warnings.append(WARNING_CIDADE_FORA_MAPEAMENTO)
    if metrics.localidade_invalida:
        warnings.append(WARNING_LOCALIDADE_INVALIDA)
    return warnings


def _apply_event_taxonomy(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    if raw_df.empty:
        return raw_df, []

    typed_df = raw_df.copy()
    unknown_events: list[str] = []
    typed_values: list[str] = []

    for _, row in typed_df.iterrows():
        if str(row.get(REJECT_REASON_COL, "")).strip():
            typed_values.append(str(row.get("tipo_evento", "")).strip())
            continue
        event_name = str(row.get("evento", "")).strip()
        existing_type = str(row.get("tipo_evento", "")).strip()
        mapped_type = classify_event_type(event_name)
        if mapped_type is not None:
            typed_values.append(mapped_type)
            continue
        # Cadastro/export já pode trazer tipo (ex.: "Entretenimento") sem o nome constar na taxonomia fixa.
        if existing_type:
            typed_values.append(existing_type)
            continue
        unknown_events.append(event_name or "EVENTO_VAZIO")
        typed_values.append("")

    typed_df["tipo_evento"] = typed_values
    fail_reasons = [
        f"TIPO_EVENTO_NAO_MAPEADO [{event_name}]"
        for event_name in _ordered_unique(unknown_events)
    ]
    return typed_df, fail_reasons


def run_pipeline(config: PipelineConfig) -> PipelineResult:
    output_dir = config.output_root / config.lote_id
    output_dir.mkdir(parents=True, exist_ok=True)
    # Keep the DQ cutoff aligned with the UTC `run_timestamp` persisted in the report.
    run_timestamp = datetime.now(timezone.utc)
    ref_date_utc = run_timestamp.date()

    fail_reasons: list[str] = []
    accumulated_warnings: list[str] = []
    metrics = QualityMetrics()
    invalid_records: list[dict[str, Any]] = []
    data_nascimento_controle: list[dict[str, Any]] = []
    localidade_controle: list[dict[str, Any]] = []
    cidade_fora_mapeamento_controle: list[dict[str, Any]] = []
    raw_frames: list[pd.DataFrame] = []
    normalized_rows: list[dict[str, Any]] = []
    source_profiles_detected: dict[str, list[str]] = {}
    explicit_row_warnings: list[str] = []

    discovered_files: list[Path] = []
    input_files_skipped: list[dict[str, str]] = []
    input_files_scanned: list[str] = []

    if config.scan_root:
        discovered_files, scan_skipped, scanned = _scan_root_inputs(config.scan_root)
        input_files_skipped.extend(scan_skipped)
        input_files_scanned.extend(scanned)
        accumulated_warnings.extend(
            skipped["reason"]
            for skipped in scan_skipped
            if skipped["reason"] in {WARNING_ARQUIVO_ZIP_DUPLICADO, WARNING_ARQUIVO_ENCRIPTADO}
        )

    ordered_paths: list[Path] = []
    seen_paths: set[Path] = set()
    for item in [*config.input_files, *discovered_files]:
        resolved = item.resolve() if item.exists() else item
        if resolved in seen_paths:
            continue
        seen_paths.add(resolved)
        ordered_paths.append(item)

    if not input_files_scanned:
        input_files_scanned = [str(path) for path in ordered_paths]

    input_files_processed: list[str] = []
    _emit_progress(
        config,
        step="source_adapt",
        label="Lendo e adaptando arquivos de origem",
    )

    for input_file in ordered_paths:
        try:
            adapted = adapt_source_file(input_file)
        except Exception as exc:  # noqa: BLE001
            fail_reasons.append(f"ERRO_LEITURA_ARQUIVO [{input_file.name}]: {exc}")
            continue

        if adapted.skipped:
            reason = adapted.skip_reason or "ARQUIVO_IGNORADO"
            input_files_skipped.append({"file": str(input_file), "reason": reason})
            accumulated_warnings.extend(adapted.warnings)
            continue

        source_profiles_detected[input_file.name] = adapted.source_profiles
        if adapted.fail_reasons:
            fail_reasons.extend(adapted.fail_reasons)
            continue

        input_files_processed.append(str(input_file))
        accumulated_warnings.extend(adapted.warnings)

        adapted_df = adapted.dataframe.copy()
        if adapted_df.empty:
            continue
        if REJECT_REASON_COL not in adapted_df.columns:
            adapted_df[REJECT_REASON_COL] = ""
        if "source_file" not in adapted_df.columns:
            adapted_df["source_file"] = input_file.name
        else:
            source_file = adapted_df["source_file"].fillna("").astype(str).str.strip()
            adapted_df["source_file"] = source_file.mask(source_file == "", input_file.name)
        raw_frames.append(adapted_df)

    if raw_frames:
        raw_df = pd.concat(raw_frames, ignore_index=True)
    else:
        raw_df = pd.DataFrame(
            columns=[
                *ALL_COLUMNS,
                CITY_OUT_COL,
                SHEET_COL_SOURCE,
                ROW_COL_SOURCE,
                REJECT_REASON_COL,
                "source_file",
            ]
        )

    _emit_progress(
        config,
        step="event_taxonomy",
        label="Classificando tipo de evento",
    )
    raw_df, taxonomy_fail_reasons = _apply_event_taxonomy(raw_df)
    if taxonomy_fail_reasons:
        fail_reasons.extend(taxonomy_fail_reasons)

    raw_export = raw_df[[*ALL_COLUMNS, "source_file", SHEET_COL_SOURCE, ROW_COL_SOURCE]].copy()
    raw_export = raw_export.rename(
        columns={
            SHEET_COL_SOURCE: "source_sheet",
            ROW_COL_SOURCE: "source_row",
        }
    )
    raw_path = output_dir / "raw.csv"
    raw_export.to_csv(raw_path, index=False)

    total_raw_rows = len(raw_df.index)
    last_normalize_pct: int | None = None
    _emit_progress(
        config,
        step="normalize_rows",
        label="Normalizando campos (CPF, datas, telefone, local…)",
        pct=100 if total_raw_rows == 0 else 0,
    )
    if total_raw_rows == 0:
        last_normalize_pct = 100

    def _emit_normalize_progress(processed_rows: int) -> None:
        nonlocal last_normalize_pct
        if total_raw_rows <= 0:
            return
        pct = int((processed_rows * 100) / total_raw_rows)
        pct_bucket = 100 if processed_rows >= total_raw_rows else (pct // 5) * 5
        if last_normalize_pct is None or pct_bucket > last_normalize_pct:
            _emit_progress(
                config,
                step="normalize_rows",
                label="Normalizando campos (CPF, datas, telefone, local…)",
                pct=pct_bucket,
            )
            last_normalize_pct = pct_bucket

    for row_index, row in enumerate(raw_df.to_dict(orient="records"), start=1):
        raw_row_data = {column: row.get(column, "") for column in ALL_COLUMNS}
        row_data = _stringify_row_for_report(row)
        reject_reason = str(row.get(REJECT_REASON_COL, "")).strip()
        if reject_reason:
            explicit_row_warnings.append(reject_reason)
            invalid_records.append(
                {
                    "source_file": row["source_file"],
                    "source_sheet": str(row.get(SHEET_COL_SOURCE, "")),
                    "source_row": int(row.get(ROW_COL_SOURCE, 0)),
                    "motivo_rejeicao": reject_reason,
                    "row_data": row_data,
                }
            )
            _emit_normalize_progress(row_index)
            continue

        city_out_of_mapping = bool(row.get(CITY_OUT_COL, False))
        normalized_row, reasons, birth_date_issue, locality_result = _normalize_row(
            raw_row_data,
            city_out_of_mapping=city_out_of_mapping,
            ref_date_utc=ref_date_utc,
            event_locality_owned=config.anchored_on_evento_id,
        )

        if city_out_of_mapping and not config.anchored_on_evento_id:
            metrics.cidade_fora_mapeamento += 1
            cidade_fora_mapeamento_controle.append(
                {
                    "source_file": row["source_file"],
                    "source_sheet": str(row.get(SHEET_COL_SOURCE, "")),
                    "source_row": int(row.get(ROW_COL_SOURCE, 0)),
                }
            )
        if birth_date_issue is not None:
            data_nascimento_controle.append(
                {
                    "source_file": row["source_file"],
                    "source_sheet": str(row.get(SHEET_COL_SOURCE, "")),
                    "source_row": int(row.get(ROW_COL_SOURCE, 0)),
                    "issue": birth_date_issue.value,
                }
            )
            if birth_date_issue is BirthDateIssue.MISSING:
                metrics.data_nascimento_missing += 1
            else:
                metrics.data_nascimento_invalid += 1

        if locality_result.issue_code is not None:
            raw_cidade = row_data.get("cidade", "")
            raw_estado = row_data.get("estado", "")
            raw_local = "" if config.anchored_on_evento_id else row_data.get("local", "")
            _register_locality_issue(metrics, locality_result)
            localidade_controle.append(
                {
                    "source_file": row["source_file"],
                    "source_sheet": str(row.get(SHEET_COL_SOURCE, "")),
                    "source_row": int(row.get(ROW_COL_SOURCE, 0)),
                    "issue": locality_result.issue_code,
                    "matched_by": locality_result.matched_by,
                    "raw_value": _truncate_for_report(
                        " | ".join(
                            value
                            for value in (
                                raw_cidade,
                                raw_estado,
                                raw_local,
                            )
                            if value
                        )
                    ),
                    "raw_cidade": _truncate_for_report(raw_cidade),
                    "raw_estado": _truncate_for_report(raw_estado),
                    "raw_local": _truncate_for_report(raw_local),
                }
            )

        if reasons:
            if "CPF_INVALIDO" in reasons:
                metrics.cpf_invalid_discarded += 1
            if "TELEFONE_INVALIDO" in reasons:
                metrics.telefone_invalid += 1
            if "DATA_EVENTO_INVALIDA" in reasons:
                metrics.data_evento_invalid += 1

            invalid_records.append(
                {
                    "source_file": row["source_file"],
                    "source_sheet": str(row.get(SHEET_COL_SOURCE, "")),
                    "source_row": int(row.get(ROW_COL_SOURCE, 0)),
                    "motivo_rejeicao": ";".join(reasons),
                    "row_data": row_data,
                }
            )
            _emit_normalize_progress(row_index)
            continue

        normalized_rows.append(
            {
                **normalized_row,
                "__source_file": row["source_file"],
                "__source_sheet": str(row.get(SHEET_COL_SOURCE, "")),
                "__source_row": int(row.get(ROW_COL_SOURCE, 0)),
                "__row_data": row_data,
            }
        )
        _emit_normalize_progress(row_index)

    if normalized_rows:
        valid_df = pd.DataFrame(normalized_rows)
    else:
        valid_df = pd.DataFrame(
            columns=[*ALL_COLUMNS, "__source_file", "__source_sheet", "__source_row", "__row_data"]
        )

    _emit_progress(
        config,
        step="dedupe",
        label="Removendo duplicidades CPF + evento",
    )
    if not valid_df.empty:
        duplicated_mask = valid_df.duplicated(subset=["cpf", "evento"], keep="first")
        duplicated_rows = valid_df[duplicated_mask]
        metrics.duplicidades_cpf_evento = int(duplicated_mask.sum())
        for _, duplicate in duplicated_rows.iterrows():
            invalid_records.append(
                {
                    "source_file": duplicate["__source_file"],
                    "source_sheet": duplicate["__source_sheet"],
                    "source_row": int(duplicate["__source_row"]),
                    "motivo_rejeicao": WARNING_DUPLICIDADE_CPF_EVENTO,
                    "row_data": duplicate["__row_data"],
                }
            )
        valid_df = valid_df[~duplicated_mask]

    final_df = (
        valid_df[ALL_COLUMNS].copy()
        if not valid_df.empty
        else pd.DataFrame(columns=ALL_COLUMNS)
    )

    _emit_progress(
        config,
        step="contract_check",
        label="Validando contrato dos dados",
    )
    contract_violations = validate_databricks_contract(final_df, ref_date=ref_date_utc)
    if contract_violations:
        fail_reasons.extend(contract_violations)

    warnings = _ordered_unique(
        [
            *accumulated_warnings,
            *explicit_row_warnings,
            *_collect_metric_warnings(metrics),
        ]
    )
    report = _build_report(
        config=config,
        run_timestamp=run_timestamp,
        raw_rows=len(raw_df),
        valid_rows=len(final_df),
        metrics=metrics,
        fail_reasons=fail_reasons,
        warnings=warnings,
        invalid_records=invalid_records,
        data_nascimento_controle=data_nascimento_controle,
        localidade_controle=localidade_controle,
        cidade_fora_mapeamento_controle=cidade_fora_mapeamento_controle,
        source_profiles_detected=source_profiles_detected,
        input_files_scanned=input_files_scanned,
        input_files_processed=input_files_processed,
        input_files_skipped=input_files_skipped,
    )

    _emit_progress(
        config,
        step="write_outputs",
        label="Gravando relatório e CSV consolidado",
    )
    consolidated_path = output_dir / FINAL_FILENAME
    final_df.to_csv(consolidated_path, index=False)

    report_path = output_dir / "report.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    summary_path = output_dir / "validation-summary.md"
    _write_summary(report, summary_path)

    gate = report["gate"]
    return PipelineResult(
        lote_id=config.lote_id,
        status=gate["status"],
        decision=gate["decision"],
        output_dir=output_dir,
        report_path=report_path,
        summary_path=summary_path,
        consolidated_path=consolidated_path,
        exit_code=report["exit_code"],
    )
