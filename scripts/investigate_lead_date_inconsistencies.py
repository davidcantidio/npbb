from __future__ import annotations

import csv
import importlib.util
import json
import re
import sys
import warnings
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lead_pipeline.contracts import validate_databricks_contract
from lead_pipeline.normalization import parse_date as gold_parse_date

OUTPUT_DIR = ROOT / "artifacts" / "lead_date_investigation"
SUMMARY_JSON_PATH = OUTPUT_DIR / "summary.json"
DECISION_MATRIX_CSV_PATH = OUTPUT_DIR / "date_parsing_decision_matrix.csv"
LINEAGE_CSV_PATH = OUTPUT_DIR / "lineage_samples.csv"

LEADS_V4_PATH = ROOT / "LEADS-v4.csv"
NOTEBOOK_IPYNB_PATH = ROOT / "notebook_origem1 1.ipynb"
NOTEBOOK_PY_PATH = ROOT / "scripts" / "databricks_bb_enrichment_notebook.py"
VALIDATE_LOCAL_PATH = (
    ROOT / "artifacts" / "databricks_bb_enrichment_validation" / "validate_local_enrichment.py"
)
MANUAL_IMPORT_DIR = (
    ROOT
    / "artifacts"
    / "manual_supabase_import_2026-04-20"
    / "_pipeline_output"
    / "manual_supabase_import_2026-04-20"
)
MANUAL_RAW_PATH = MANUAL_IMPORT_DIR / "raw.csv"
MANUAL_FINAL_PATH = MANUAL_IMPORT_DIR / "leads_multieventos_2025.csv"
MANUAL_REPORT_PATH = MANUAL_IMPORT_DIR / "report.json"

DATE_COLUMNS: tuple[tuple[str, str], ...] = (
    ("data_evento", "event"),
    ("data_nascimento", "birth"),
)
NULL_TOKENS = {"", "nan", "nat", "none", "null"}
SAMPLE_LIMIT = 5

TARGET_SAMPLES: tuple[dict[str, str], ...] = (
    {
        "sample_id": "amanda_cbvp",
        "cpf": "14439231764",
        "evento": "2ª Etapa Circuito Brasileiro de Vôlei de Praia",
    },
    {
        "sample_id": "amanda_beach_pro_tour",
        "cpf": "14439231764",
        "evento": "1ª Etapa Beach Pro Tour",
    },
    {
        "sample_id": "luis_gergen_expodireto",
        "cpf": "55644392015",
        "evento": "Expodireto Cotrijal",
    },
    {
        "sample_id": "hannah_gil_pa",
        "cpf": "00957793294",
        "evento": "Gilberto Gil - PA",
    },
    {
        "sample_id": "bruna_tomasi_birth_ambiguous",
        "cpf": "85363103087",
        "evento": "South Summit",
    },
)

AMBIGUOUS_EVENT_VALUES = (
    "2/4/2026",
    "2/9/2026",
    "3/4/2026",
    "3/9/2026",
    "3/11/2026",
)


@dataclass
class ValueAnalysis:
    raw: str
    iso_value: str | None
    mdy_value: str | None
    dmy_value: str | None
    auto_safe_value: str | None
    auto_safe_status: str
    format_class: str


@dataclass
class ExampleRecord:
    line_no: int
    raw: str
    iso_value: str | None
    mdy_value: str | None
    dmy_value: str | None
    auto_safe_status: str
    auto_safe_value: str | None


@dataclass
class ColumnProfile:
    column: str
    date_kind: str
    rows_seen: int = 0
    format_counts: Counter[str] = field(default_factory=Counter)
    auto_safe_counts: Counter[str] = field(default_factory=Counter)
    parse_success_counts: Counter[str] = field(default_factory=Counter)
    examples: dict[str, list[ExampleRecord]] = field(default_factory=dict)

    def maybe_add_example(self, category: str, example: ExampleRecord) -> None:
        bucket = self.examples.setdefault(category, [])
        if len(bucket) < SAMPLE_LIMIT:
            bucket.append(example)

    def to_summary(self) -> dict[str, Any]:
        return {
            "column": self.column,
            "date_kind": self.date_kind,
            "rows_seen": self.rows_seen,
            "format_counts": dict(self.format_counts),
            "auto_safe_counts": dict(self.auto_safe_counts),
            "parse_success_counts": dict(self.parse_success_counts),
            "examples": {
                key: [asdict(item) for item in value]
                for key, value in sorted(self.examples.items())
            },
        }


def load_validate_local_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "validate_local_enrichment",
        VALIDATE_LOCAL_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {VALIDATE_LOCAL_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATE_LOCAL = load_validate_local_module()


def digits_only(value: str | None) -> str:
    return re.sub(r"\D+", "", str(value or ""))


def normalized_event(value: str | None) -> str:
    return str(value or "").strip().lower()


def safe_gold_parse(value: str) -> str | None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return gold_parse_date(value)


def try_parse_patterns(text: str, patterns: tuple[str, ...]) -> str | None:
    for pattern in patterns:
        try:
            return datetime.strptime(text, pattern).date().isoformat()
        except ValueError:
            continue
    return None


@lru_cache(maxsize=None)
def analyze_value(raw: str, date_kind: str) -> ValueAnalysis:
    text = str(raw or "").strip()
    lowered = text.lower()
    if lowered in NULL_TOKENS:
        return ValueAnalysis(
            raw=text,
            iso_value=None,
            mdy_value=None,
            dmy_value=None,
            auto_safe_value=None,
            auto_safe_status="MISSING",
            format_class="blank",
        )

    iso_value = try_parse_patterns(
        text,
        (
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
        ),
    )
    mdy_value = try_parse_patterns(
        text,
        (
            "%m/%d/%Y",
            "%m/%d/%Y %H:%M",
            "%m/%d/%Y %H:%M:%S",
        ),
    )
    dmy_value = try_parse_patterns(
        text,
        (
            "%d/%m/%Y",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y %H:%M:%S",
        ),
    )

    auto_safe_parsed, auto_safe_status = VALIDATE_LOCAL.parse_date_auto_safe(text, date_kind)
    auto_safe_value = auto_safe_parsed.isoformat() if auto_safe_parsed is not None else None

    if iso_value is not None:
        format_class = "iso_like"
    elif mdy_value is not None and dmy_value is not None and mdy_value == dmy_value:
        format_class = "both_valid_same"
    elif mdy_value is not None and dmy_value is not None and mdy_value != dmy_value:
        format_class = "both_valid_different"
    elif mdy_value is not None:
        format_class = "mdy_only"
    elif dmy_value is not None:
        format_class = "dmy_only"
    else:
        format_class = "unparseable"

    return ValueAnalysis(
        raw=text,
        iso_value=iso_value,
        mdy_value=mdy_value,
        dmy_value=dmy_value,
        auto_safe_value=auto_safe_value,
        auto_safe_status=auto_safe_status,
        format_class=format_class,
    )


def build_example(line_no: int, analysis: ValueAnalysis) -> ExampleRecord:
    return ExampleRecord(
        line_no=line_no,
        raw=analysis.raw,
        iso_value=analysis.iso_value,
        mdy_value=analysis.mdy_value,
        dmy_value=analysis.dmy_value,
        auto_safe_status=analysis.auto_safe_status,
        auto_safe_value=analysis.auto_safe_value,
    )


def profile_leads_csv() -> dict[str, Any]:
    profiles = {
        column: ColumnProfile(column=column, date_kind=date_kind)
        for column, date_kind in DATE_COLUMNS
    }
    sample_keys = {
        (sample["cpf"], sample["evento"]): sample["sample_id"]
        for sample in TARGET_SAMPLES
    }
    lead_samples: dict[str, dict[str, Any]] = {}
    event_value_counts: Counter[str] = Counter()

    with LEADS_V4_PATH.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for line_no, row in enumerate(reader, start=2):
            event_value = str(row.get("data_evento", "")).strip()
            event_value_counts[event_value] += 1

            sample_id = sample_keys.get((digits_only(row.get("cpf")), row.get("evento", "")))
            if sample_id and sample_id not in lead_samples:
                lead_samples[sample_id] = {
                    "line_no": line_no,
                    "nome": row.get("nome", ""),
                    "cpf": row.get("cpf", ""),
                    "evento": row.get("evento", ""),
                    "local": row.get("local", ""),
                    "data_evento": row.get("data_evento", ""),
                    "data_nascimento": row.get("data_nascimento", ""),
                }

            for column, date_kind in DATE_COLUMNS:
                profile = profiles[column]
                analysis = analyze_value(str(row.get(column, "")), date_kind)
                example = build_example(line_no, analysis)

                profile.rows_seen += 1
                profile.format_counts[analysis.format_class] += 1
                profile.auto_safe_counts[analysis.auto_safe_status] += 1
                profile.parse_success_counts["ISO_VALID" if analysis.iso_value else "ISO_NULL"] += 1
                profile.parse_success_counts["MDY_VALID" if analysis.mdy_value else "MDY_NULL"] += 1
                profile.parse_success_counts["DMY_VALID" if analysis.dmy_value else "DMY_NULL"] += 1

                profile.maybe_add_example(analysis.format_class, example)
                profile.maybe_add_example(f"AUTO_SAFE_{analysis.auto_safe_status}", example)

    event_gold_mismatch = []
    for raw_value in AMBIGUOUS_EVENT_VALUES:
        notebook_analysis = analyze_value(raw_value, "event")
        gold_value = safe_gold_parse(raw_value)
        event_gold_mismatch.append(
            {
                "raw": raw_value,
                "count": event_value_counts[raw_value],
                "notebook_auto_safe_status": notebook_analysis.auto_safe_status,
                "mdy_value": notebook_analysis.mdy_value,
                "gold_parse_value": gold_value,
                "gold_matches_mdy": gold_value == notebook_analysis.mdy_value,
            }
        )

    return {
        "row_count": profiles["data_evento"].rows_seen,
        "column_profiles": {
            name: profile.to_summary()
            for name, profile in profiles.items()
        },
        "event_value_counts": dict(event_value_counts),
        "lead_samples": lead_samples,
        "event_gold_mismatch": event_gold_mismatch,
    }


def lookup_csv_rows(
    path: Path,
    *,
    has_source_columns: bool,
) -> dict[tuple[str, str], dict[str, Any]]:
    results: dict[tuple[str, str], dict[str, Any]] = {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for line_no, row in enumerate(reader, start=2):
            key = (digits_only(row.get("cpf")), row.get("evento", ""))
            if key in results:
                continue
            payload: dict[str, Any] = {
                "line_no": line_no,
                "cpf": row.get("cpf", ""),
                "evento": row.get("evento", ""),
                "data_evento": row.get("data_evento", ""),
                "data_nascimento": row.get("data_nascimento", ""),
            }
            if has_source_columns:
                payload["source_file"] = row.get("source_file", "")
                payload["source_sheet"] = row.get("source_sheet", "")
                payload["source_row"] = row.get("source_row", "")
            results[key] = payload
    return results


def build_lineage_rows(profile_summary: dict[str, Any]) -> list[dict[str, Any]]:
    leads_lookup = profile_summary["lead_samples"]
    raw_lookup = lookup_csv_rows(MANUAL_RAW_PATH, has_source_columns=True)
    final_lookup = lookup_csv_rows(MANUAL_FINAL_PATH, has_source_columns=False)

    rows: list[dict[str, Any]] = []
    for sample in TARGET_SAMPLES:
        key = (sample["cpf"], sample["evento"])
        local_row = leads_lookup.get(sample["sample_id"], {})
        raw_row = raw_lookup.get(key, {})
        final_row = final_lookup.get(key, {})

        event_analysis = analyze_value(str(local_row.get("data_evento", "")), "event")
        birth_analysis = analyze_value(str(local_row.get("data_nascimento", "")), "birth")

        rows.append(
            {
                "sample_id": sample["sample_id"],
                "cpf": sample["cpf"],
                "evento": sample["evento"],
                "local_csv_line": local_row.get("line_no"),
                "local_data_evento": local_row.get("data_evento"),
                "local_data_nascimento": local_row.get("data_nascimento"),
                "notebook_event_status": event_analysis.auto_safe_status,
                "notebook_event_value": event_analysis.auto_safe_value,
                "notebook_birth_status": birth_analysis.auto_safe_status,
                "notebook_birth_value": birth_analysis.auto_safe_value,
                "gold_parse_event_from_local": safe_gold_parse(str(local_row.get("data_evento", ""))),
                "gold_parse_birth_from_local": safe_gold_parse(str(local_row.get("data_nascimento", ""))),
                "manual_raw_line": raw_row.get("line_no"),
                "manual_raw_data_evento": raw_row.get("data_evento"),
                "manual_raw_data_nascimento": raw_row.get("data_nascimento"),
                "manual_raw_source_file": raw_row.get("source_file"),
                "manual_raw_source_sheet": raw_row.get("source_sheet"),
                "manual_raw_source_row": raw_row.get("source_row"),
                "manual_final_line": final_row.get("line_no"),
                "manual_final_data_evento": final_row.get("data_evento"),
                "manual_final_data_nascimento": final_row.get("data_nascimento"),
            }
        )
    return rows


def compare_notebooks() -> dict[str, Any]:
    notebook = json.loads(NOTEBOOK_IPYNB_PATH.read_text(encoding="utf-8", errors="replace"))
    ipynb_cells = ["".join(cell.get("source", [])) for cell in notebook["cells"]]
    py_code = NOTEBOOK_PY_PATH.read_text(encoding="utf-8", errors="replace")

    def cell_index_containing(text: str) -> int | None:
        for idx, cell_source in enumerate(ipynb_cells):
            if text in cell_source:
                return idx
        return None

    def file_line_number(path: Path, needle: str) -> int | None:
        for idx, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            if needle in line:
                return idx
        return None

    start_marker = "def add_date_parse_columns(df, raw_column, prefix, date_kind):"

    findings = [
        {
            "id": "date_style_default",
            "classification": "drift_de_configuracao",
            "ipynb_evidence": {
                "cell": cell_index_containing('LEAD_DATE_STYLE = "AUTO_SAFE"'),
                "excerpt": 'LEAD_DATE_STYLE = "AUTO_SAFE"',
            },
            "py_evidence": {
                "line": file_line_number(NOTEBOOK_PY_PATH, 'dbutils.widgets.dropdown("lead_date_style", "MDY"'),
                "fallback_line": file_line_number(NOTEBOOK_PY_PATH, 'LEAD_DATE_STYLE = widget_text("lead_date_style", "MDY").upper()'),
                "excerpt": 'dbutils.widgets.dropdown("lead_date_style", "MDY", ["AUTO_SAFE", "DMY", "MDY"])',
            },
            "summary": "O `.ipynb` fixa `AUTO_SAFE`; o notebook exportado para script defaulta `MDY` via widget.",
        },
        {
            "id": "lead_source_contract",
            "classification": "drift_de_implementacao",
            "ipynb_evidence": {
                "cell": cell_index_containing('df_leads_raw = spark.read.table(LEADS_TABLE_NAME)'),
                "excerpt": 'df_leads_raw = spark.read.table(LEADS_TABLE_NAME)',
            },
            "py_evidence": {
                "line": file_line_number(NOTEBOOK_PY_PATH, "header_probe_df = spark.read.options(**csv_reader_options).csv(LEAD_CSV_PATH)"),
                "excerpt": "spark.read.options(**csv_reader_options).csv(LEAD_CSV_PATH)",
            },
            "summary": "O `.ipynb` consome uma tabela UC (`main.main.leads_coluna_origem`); o `.py` consome um CSV parametrizado.",
        },
        {
            "id": "staging_context_contract",
            "classification": "drift_de_implementacao",
            "ipynb_evidence": {
                "cell": cell_index_containing('CONTEXT_COLUMNS = ["tipo_evento", "origem"]'),
                "excerpt": 'CONTEXT_COLUMNS = ["tipo_evento", "origem"]',
            },
            "py_evidence": {
                "line": file_line_number(NOTEBOOK_PY_PATH, 'CONTEXT_COLUMNS = ["evento", "tipo_evento", "local", "data_evento"]'),
                "excerpt": 'CONTEXT_COLUMNS = ["evento", "tipo_evento", "local", "data_evento"]',
            },
            "summary": "Os dois artefatos exigem contextos e colunas de staging diferentes; o `.ipynb` injeta `origem`, o `.py` exige `evento/local/data_evento`.",
        },
        {
            "id": "date_parser_logic",
            "classification": "mesma_logica_parametrizada",
            "ipynb_evidence": {
                "cell": cell_index_containing(start_marker),
                "excerpt": start_marker,
            },
            "py_evidence": {
                "line": file_line_number(NOTEBOOK_PY_PATH, start_marker),
                "excerpt": start_marker,
            },
            "summary": "A função `add_date_parse_columns` é a mesma na lógica; as diferenças relevantes são docstring, comentários e formatação.",
        },
    ]

    return {"findings": findings}


def evaluate_gold_contract() -> dict[str, Any]:
    manual_report = json.loads(MANUAL_REPORT_PATH.read_text(encoding="utf-8", errors="replace"))
    final_df = pd.read_csv(MANUAL_FINAL_PATH, dtype=str, keep_default_na=False)
    raw_df = pd.read_csv(MANUAL_RAW_PATH, dtype=str, keep_default_na=False)
    raw_trimmed = raw_df.iloc[:, :34].copy()

    final_violations = validate_databricks_contract(final_df)
    raw_violations = validate_databricks_contract(raw_trimmed)

    return {
        "final_shape": {"rows": int(final_df.shape[0]), "columns": int(final_df.shape[1])},
        "raw_shape": {"rows": int(raw_df.shape[0]), "columns": int(raw_df.shape[1])},
        "final_contract_violations": final_violations,
        "raw_contract_violations": raw_violations,
        "manual_report_totals": manual_report.get("totals", {}),
        "manual_report_quality_metrics": manual_report.get("quality_metrics", {}),
        "manual_report_source_profiles": manual_report.get("source_profiles_detected", {}),
    }


def build_decision_matrix_rows(profile_summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for column_name, summary in profile_summary["column_profiles"].items():
        format_counts = Counter(summary["format_counts"])
        auto_counts = Counter(summary["auto_safe_counts"])
        parse_counts = Counter(summary["parse_success_counts"])
        rows.append(
            {
                "column": column_name,
                "rows_seen": summary["rows_seen"],
                "format_blank": format_counts["blank"],
                "format_iso_like": format_counts["iso_like"],
                "format_mdy_only": format_counts["mdy_only"],
                "format_dmy_only": format_counts["dmy_only"],
                "format_both_valid_same": format_counts["both_valid_same"],
                "format_both_valid_different": format_counts["both_valid_different"],
                "format_unparseable": format_counts["unparseable"],
                "iso_valid_rows": parse_counts["ISO_VALID"],
                "mdy_valid_rows": parse_counts["MDY_VALID"],
                "dmy_valid_rows": parse_counts["DMY_VALID"],
                "auto_safe_valid_rows": auto_counts["VALID"],
                "auto_safe_ambiguous_rows": auto_counts["AMBIGUOUS"],
                "auto_safe_missing_rows": auto_counts["MISSING"],
                "auto_safe_unparseable_rows": auto_counts["UNPARSEABLE"],
                "auto_safe_before_min_rows": auto_counts["BEFORE_MIN"],
                "auto_safe_future_rows": auto_counts["FUTURE"],
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows available to write {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    profile_summary = profile_leads_csv()
    decision_rows = build_decision_matrix_rows(profile_summary)
    lineage_rows = build_lineage_rows(profile_summary)
    notebook_diff = compare_notebooks()
    gold_contract = evaluate_gold_contract()

    summary = {
        "generated_at": datetime.now(UTC).isoformat(),
        "paths": {
            "leads_v4": str(LEADS_V4_PATH.relative_to(ROOT)),
            "notebook_ipynb": str(NOTEBOOK_IPYNB_PATH.relative_to(ROOT)),
            "notebook_py": str(NOTEBOOK_PY_PATH.relative_to(ROOT)),
            "manual_raw": str(MANUAL_RAW_PATH.relative_to(ROOT)),
            "manual_final": str(MANUAL_FINAL_PATH.relative_to(ROOT)),
            "manual_report": str(MANUAL_REPORT_PATH.relative_to(ROOT)),
        },
        "profile_summary": profile_summary,
        "decision_matrix": decision_rows,
        "lineage_rows": lineage_rows,
        "notebook_diff": notebook_diff,
        "gold_contract": gold_contract,
        "limitations": [
            "O artefato `notebook-run(1).docx` nao esta disponivel no workspace local.",
            "Nao houve acesso a Databricks nem ao banco BB; conclusoes sobre `main.main.leads_coluna_origem` e `corporativos_pd.db2mci.cliente` permanecem locais/inferenciais.",
        ],
    }

    SUMMARY_JSON_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_csv(DECISION_MATRIX_CSV_PATH, decision_rows)
    write_csv(LINEAGE_CSV_PATH, lineage_rows)

    print(f"summary_json={SUMMARY_JSON_PATH.relative_to(ROOT)}")
    print(f"decision_matrix_csv={DECISION_MATRIX_CSV_PATH.relative_to(ROOT)}")
    print(f"lineage_csv={LINEAGE_CSV_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
