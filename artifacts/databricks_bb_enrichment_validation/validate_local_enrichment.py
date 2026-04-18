from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = Path(__file__).resolve().parent

LEADS_INPUT_PATH = ROOT / "aurea_tour_2025_hevert(in).csv"
EXPECTED_LAYOUT_PATH = ROOT / "data 2.csv"
SCHEMA_PATH = ROOT / "schema.txt"

SYNTHETIC_LEADS_PATH = ARTIFACT_DIR / "synthetic_leads.csv"
SYNTHETIC_BB_PATH = ARTIFACT_DIR / "synthetic_bb.csv"
SYNTHETIC_OUTPUT_PATH = ARTIFACT_DIR / "synthetic_output.csv"
REPORT_PATH = ARTIFACT_DIR / "validation_report.json"

MIN_VALID_DATE = date(1900, 1, 1)
SENTINEL_DATE = date(1, 1, 1)
CURRENT_DATE = date(2026, 4, 15)
KNOWN_INVALID_CPFS = {"12345678909"}

FINAL_OUTPUT_COLUMNS = [
    "evento",
    "data_evento",
    "Soma de ano_evento",
    "cliente",
    "cod_sexo",
    "cpf",
    "data_nascimento",
    "faixa_etaria",
    "Soma de idade",
    "local",
    "tipo_evento",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def only_digits(value: str | None) -> str:
    return re.sub(r"\D+", "", str(value or ""))


def calc_cpf_check_digit(numbers: list[int], start_weight: int) -> int:
    total = 0
    weight = start_weight
    for number in numbers:
        total += number * weight
        weight -= 1
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def make_valid_cpf(nine_digits: str) -> str:
    digits = [int(char) for char in nine_digits]
    first = calc_cpf_check_digit(digits, 10)
    second = calc_cpf_check_digit(digits + [first], 11)
    return nine_digits + str(first) + str(second)


def is_valid_cpf(value: str | None) -> bool:
    cpf = only_digits(value)
    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:
        return False
    if cpf in KNOWN_INVALID_CPFS:
        return False
    numbers = [int(character) for character in cpf]
    first = calc_cpf_check_digit(numbers[:9], 10)
    second = calc_cpf_check_digit(numbers[:10], 11)
    return first == numbers[9] and second == numbers[10]


def normalize_cpf(value: str | None) -> tuple[str | None, str | None, bool]:
    raw_digits = only_digits(value)
    normalized = raw_digits.zfill(11) if 1 <= len(raw_digits) <= 11 else None

    if len(raw_digits) == 0:
        issue = "CPF_EMPTY"
    elif len(raw_digits) > 11:
        issue = "CPF_GT_11"
    elif normalized == normalized[0] * 11:
        issue = "CPF_REPEATED_DIGITS"
    elif normalized in KNOWN_INVALID_CPFS:
        issue = "CPF_KNOWN_PLACEHOLDER"
    elif not is_valid_cpf(normalized):
        issue = "CPF_CHECK_DIGIT_INVALID"
    else:
        issue = None

    return normalized, issue, 1 <= len(raw_digits) <= 10


def parse_date_auto_safe(value: str | None, date_kind: str) -> tuple[date | None, str]:
    text = str(value or "").strip()
    if not text or text.lower() in {"nan", "nat", "none", "null"}:
        return None, "MISSING"

    slash_match = re.match(
        r"^(\d{1,2})/(\d{1,2})/(\d{4})(?: \d{1,2}:\d{1,2}(?::\d{1,2})?)?$",
        text,
    )
    formats = [
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    if slash_match:
        first = int(slash_match.group(1))
        second = int(slash_match.group(2))
        if first <= 12 and second <= 12:
            return None, "AMBIGUOUS"
        formats = ["%d/%m/%Y"] if first > 12 else ["%m/%d/%Y"]

    for pattern in formats:
        try:
            parsed = datetime.strptime(text, pattern).date()
            break
        except ValueError:
            parsed = None

    if parsed is None:
        return None, "UNPARSEABLE"
    if parsed < MIN_VALID_DATE:
        return parsed, "BEFORE_MIN"
    if date_kind == "birth" and parsed > CURRENT_DATE:
        return parsed, "FUTURE"
    return parsed, "VALID"


def parse_iso_date(value: str | None) -> date | None:
    text = str(value or "").strip()
    if not text or text.upper() == "NULL":
        return None
    return datetime.strptime(text, "%Y-%m-%d").date()


def valid_bb_birthdate(value: str | None) -> date | None:
    parsed = parse_iso_date(value)
    if parsed is None or parsed == SENTINEL_DATE or parsed < MIN_VALID_DATE or parsed > CURRENT_DATE:
        return None
    return parsed


def parse_bb_sample_from_schema() -> list[dict[str, str]]:
    text = SCHEMA_PATH.read_text(encoding="utf-8", errors="replace")
    start = text.find("|cod|")
    end = text.find("only showing", start)
    if start < 0 or end < 0:
        raise AssertionError("Could not find BB sample table in schema.txt")

    table_text = text[start:end]
    parts = re.split(r" \+[-+]+\+ ", table_text)
    headers = [column.strip() for column in parts[0].split("|") if column.strip()]
    marked_rows = re.sub(r"\|([NS]\s*)\|\s+\|(?=\d+\s*\|)", r"|\1|\n|", parts[1].strip())

    rows: list[dict[str, str]] = []
    for line in marked_rows.splitlines():
        cells = [cell.strip() for cell in line.strip("| ").split("|")]
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))
    return rows


def build_synthetic_leads(real_leads: list[dict[str, str]]) -> list[dict[str, str]]:
    duplicate_match_cpf = make_valid_cpf("111444777")
    bb_precedence_cpf = make_valid_cpf("529982247")
    no_match_under18_cpf = make_valid_cpf("246813579")
    no_match_boundary_cpf = make_valid_cpf("987654321")

    fixture_specs = [
        ("match_real_bb_lpad", "1158635915", ""),
        ("match_synthetic_bb_duplicate", duplicate_match_cpf, ""),
        ("match_bb_precedence_over_lead", bb_precedence_cpf, "2000-01-01"),
        ("valid_no_match_fallback_under18", no_match_under18_cpf, "2008-01-15"),
        ("valid_no_match_fallback_age40", no_match_boundary_cpf, "1985-12-31"),
        ("invalid_cpf_no_match", "12345678909", ""),
        ("duplicate_lead_row_preserved", duplicate_match_cpf, ""),
    ]

    rows: list[dict[str, str]] = []
    for index, (case_name, cpf, birthdate) in enumerate(fixture_specs):
        source = dict(real_leads[index])
        source["nome"] = case_name
        source["cpf"] = cpf
        source["data_nascimento"] = birthdate
        source["data_evento"] = "6/28/2025"
        rows.append(source)
    return rows


def build_synthetic_bb_rows() -> list[dict[str, str]]:
    duplicate_match_cpf = make_valid_cpf("111444777")
    bb_precedence_cpf = make_valid_cpf("529982247")

    return [
        {
            "cod": "9001",
            "cod_tipo": "1",
            "cod_cpf_cgc": duplicate_match_cpf,
            "dta_nasc_csnt": "1980-01-01",
            "dta_ulta_atlz": "2024-01-01",
            "dta_revisao": "2024-01-02",
        },
        {
            "cod": "9002",
            "cod_tipo": "1",
            "cod_cpf_cgc": duplicate_match_cpf,
            "dta_nasc_csnt": "1985-06-28",
            "dta_ulta_atlz": "2025-01-01",
            "dta_revisao": "2024-12-31",
        },
        {
            "cod": "9003",
            "cod_tipo": "1",
            "cod_cpf_cgc": bb_precedence_cpf,
            "dta_nasc_csnt": "1970-03-15",
            "dta_ulta_atlz": "2024-08-01",
            "dta_revisao": "2024-08-01",
        },
    ]


def build_bb_index(bb_rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, Any]], int]:
    candidates: list[dict[str, Any]] = []
    for row in bb_rows:
        if str(row.get("cod_tipo", "")).strip() != "1":
            continue
        cpf, issue, _lpad = normalize_cpf(row.get("cod_cpf_cgc"))
        if cpf is None or issue is not None:
            continue
        candidates.append(
            {
                "cpf": cpf,
                "birthdate": valid_bb_birthdate(row.get("dta_nasc_csnt")),
                "dta_ulta_atlz": parse_iso_date(row.get("dta_ulta_atlz")),
                "dta_revisao": parse_iso_date(row.get("dta_revisao")),
                "cod": int(str(row.get("cod") or "0").strip()),
            }
        )

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        grouped[candidate["cpf"]].append(candidate)

    def order_date(value: date | None) -> date:
        return date.min if value is None or value == SENTINEL_DATE else value

    index: dict[str, dict[str, Any]] = {}
    for cpf, rows in grouped.items():
        index[cpf] = sorted(
            rows,
            key=lambda item: (
                order_date(item["dta_ulta_atlz"]),
                order_date(item["dta_revisao"]),
                item["cod"],
            ),
            reverse=True,
        )[0]

    return index, len(candidates)


def render_date(value: date | None) -> str:
    return "" if value is None else value.isoformat()


def enrich_leads(
    leads: list[dict[str, str]],
    bb_index: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    final_rows: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    debug_rows: list[dict[str, Any]] = []

    for index, lead in enumerate(leads, start=1):
        cpf, cpf_issue, lpad_applied = normalize_cpf(lead.get("cpf"))
        event_date, event_status = parse_date_auto_safe(lead.get("data_evento"), "event")
        lead_birthdate, lead_birthdate_status = parse_date_auto_safe(
            lead.get("data_nascimento"),
            "birth",
        )
        lead_birthdate_valid = lead_birthdate if lead_birthdate_status == "VALID" else None
        match = bb_index.get(cpf) if cpf_issue is None else None
        final_birthdate = (match or {}).get("birthdate") or lead_birthdate_valid
        age = event_date.year - final_birthdate.year if event_date and final_birthdate else None
        faixa = "Desconhecido" if age is None else "<18" if age < 18 else "18-40" if age <= 40 else "40+"

        final_rows.append(
            {
                "evento": lead["evento"],
                "data_evento": render_date(event_date),
                "Soma de ano_evento": event_date.year if event_date else None,
                "cliente": bool(match),
                "cod_sexo": None,
                "cpf": cpf,
                "data_nascimento": render_date(final_birthdate),
                "faixa_etaria": faixa,
                "Soma de idade": age,
                "local": lead["local"],
                "tipo_evento": lead["tipo_evento"],
            }
        )
        debug_rows.append(
            {
                "row_num": index,
                "case": lead.get("nome"),
                "cpf_issue": cpf_issue,
                "lead_birthdate_status": lead_birthdate_status,
                "event_status": event_status,
                "birthdate_source": "bb" if (match or {}).get("birthdate") else "lead" if lead_birthdate_valid else "none",
                "cpf_lpad_applied": lpad_applied,
            }
        )
        if cpf_issue:
            issues.append({"row_num": index, "field": "cpf", "issue_code": cpf_issue})
        if lead_birthdate_status in {"AMBIGUOUS", "UNPARSEABLE", "BEFORE_MIN", "FUTURE"}:
            issues.append({"row_num": index, "field": "data_nascimento", "issue_code": lead_birthdate_status})
        if event_status != "VALID":
            issues.append({"row_num": index, "field": "data_evento", "issue_code": event_status})

    return final_rows, issues, debug_rows


def build_audit(final_rows: list[dict[str, Any]], issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    issue_counts = Counter(issue["issue_code"] for issue in issues)

    def metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "total_rows": len(rows),
            "cliente_true_rows": sum(1 for row in rows if row["cliente"] is True),
            "cliente_false_rows": sum(1 for row in rows if row["cliente"] is False),
            "final_birthdate_null_rows": sum(1 for row in rows if not row["data_nascimento"]),
        }

    audit: list[dict[str, Any]] = [{"escopo": "global", **metrics(final_rows), **issue_counts}]
    for column, scope in [("evento", "evento"), ("tipo_evento", "tipo_evento")]:
        for value in sorted({row[column] for row in final_rows}):
            rows = [row for row in final_rows if row[column] == value]
            audit.append({"escopo": scope, column: value, **metrics(rows)})
    for key in sorted({(row["evento"], row["tipo_evento"]) for row in final_rows}):
        rows = [row for row in final_rows if (row["evento"], row["tipo_evento"]) == key]
        audit.append({"escopo": "evento_tipo_evento", "evento": key[0], "tipo_evento": key[1], **metrics(rows)})
    return audit


def assert_validation(
    expected_columns: list[str],
    synthetic_leads: list[dict[str, str]],
    final_rows: list[dict[str, Any]],
    issues: list[dict[str, Any]],
    audit: list[dict[str, Any]],
) -> None:
    if expected_columns != FINAL_OUTPUT_COLUMNS:
        raise AssertionError(f"data 2.csv layout mismatch: {expected_columns}")
    if list(final_rows[0].keys()) != expected_columns:
        raise AssertionError(f"final layout mismatch: {list(final_rows[0].keys())}")
    if len(final_rows) != len(synthetic_leads):
        raise AssertionError("Cardinality was not preserved")

    by_case = {lead["nome"]: final_rows[index] for index, lead in enumerate(synthetic_leads)}
    debug_duplicate_cpf = make_valid_cpf("111444777")

    assert by_case["match_real_bb_lpad"]["cpf"] == "01158635915"
    assert by_case["match_real_bb_lpad"]["cliente"] is True
    assert by_case["match_real_bb_lpad"]["data_nascimento"] == "1938-06-24"
    assert by_case["match_real_bb_lpad"]["Soma de idade"] == 87
    assert by_case["match_real_bb_lpad"]["faixa_etaria"] == "40+"

    assert by_case["match_synthetic_bb_duplicate"]["cpf"] == debug_duplicate_cpf
    assert by_case["match_synthetic_bb_duplicate"]["cliente"] is True
    assert by_case["match_synthetic_bb_duplicate"]["data_nascimento"] == "1985-06-28"
    assert by_case["match_synthetic_bb_duplicate"]["Soma de idade"] == 40
    assert by_case["match_synthetic_bb_duplicate"]["faixa_etaria"] == "18-40"

    assert by_case["match_bb_precedence_over_lead"]["cliente"] is True
    assert by_case["match_bb_precedence_over_lead"]["data_nascimento"] == "1970-03-15"
    assert by_case["match_bb_precedence_over_lead"]["Soma de idade"] == 55
    assert by_case["match_bb_precedence_over_lead"]["faixa_etaria"] == "40+"

    assert by_case["valid_no_match_fallback_under18"]["cliente"] is False
    assert by_case["valid_no_match_fallback_under18"]["data_nascimento"] == "2008-01-15"
    assert by_case["valid_no_match_fallback_under18"]["Soma de idade"] == 17
    assert by_case["valid_no_match_fallback_under18"]["faixa_etaria"] == "<18"

    assert by_case["valid_no_match_fallback_age40"]["cliente"] is False
    assert by_case["valid_no_match_fallback_age40"]["data_nascimento"] == "1985-12-31"
    assert by_case["valid_no_match_fallback_age40"]["Soma de idade"] == 40
    assert by_case["valid_no_match_fallback_age40"]["faixa_etaria"] == "18-40"

    assert by_case["invalid_cpf_no_match"]["cliente"] is False
    assert by_case["invalid_cpf_no_match"]["cpf"] == "12345678909"
    assert by_case["invalid_cpf_no_match"]["data_nascimento"] == ""
    assert by_case["invalid_cpf_no_match"]["faixa_etaria"] == "Desconhecido"

    duplicate_rows = [row for row in final_rows if row["cpf"] == debug_duplicate_cpf]
    assert len(duplicate_rows) == 2
    assert all(row["cliente"] is True for row in duplicate_rows)

    issue_codes = Counter(issue["issue_code"] for issue in issues)
    assert issue_codes["CPF_KNOWN_PLACEHOLDER"] == 1

    audit_scopes = {row["escopo"] for row in audit}
    assert audit_scopes == {"global", "evento", "tipo_evento", "evento_tipo_evento"}


def main() -> None:
    real_leads = read_csv(LEADS_INPUT_PATH)
    expected_rows = read_csv(EXPECTED_LAYOUT_PATH)
    expected_columns = list(expected_rows[0].keys())
    real_bb_sample = parse_bb_sample_from_schema()

    synthetic_leads = build_synthetic_leads(real_leads)
    synthetic_bb_rows = build_synthetic_bb_rows()
    combined_bb_rows = real_bb_sample + synthetic_bb_rows

    write_csv(SYNTHETIC_LEADS_PATH, synthetic_leads, list(real_leads[0].keys()))
    write_csv(SYNTHETIC_BB_PATH, synthetic_bb_rows, list(synthetic_bb_rows[0].keys()))

    bb_index, bb_candidate_count = build_bb_index(combined_bb_rows)
    final_rows, issues, debug_rows = enrich_leads(synthetic_leads, bb_index)
    audit = build_audit(final_rows, issues)

    assert_validation(expected_columns, synthetic_leads, final_rows, issues, audit)

    write_csv(SYNTHETIC_OUTPUT_PATH, final_rows, FINAL_OUTPUT_COLUMNS)
    report = {
        "status": "passed",
        "real_reference": {
            "aurea_rows": len(real_leads),
            "data_2_rows": len(expected_rows),
            "schema_bb_sample_rows": len(real_bb_sample),
        },
        "synthetic_fixture": {
            "lead_rows": len(synthetic_leads),
            "synthetic_bb_rows": len(synthetic_bb_rows),
            "bb_candidates_after_validation": bb_candidate_count,
            "bb_dedup_index_size": len(bb_index),
        },
        "checks": {
            "layout_matches_data_2": expected_columns == FINAL_OUTPUT_COLUMNS,
            "cardinality_preserved": len(final_rows) == len(synthetic_leads),
            "audit_scopes": sorted({row["escopo"] for row in audit}),
        },
        "final_rows": final_rows,
        "debug_rows": debug_rows,
        "issues": issues,
        "audit": audit,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
