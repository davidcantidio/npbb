from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import csv
import re
from typing import Sequence

from .normalization import strip_accents

MUNICIPIOS_DATA_PATH = Path(__file__).resolve().parent / "data" / "municipios.csv"

BRAZIL_STATES_BY_UF: dict[str, str] = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

INVALID_MARKERS = {
    "",
    "-",
    "-1",
    "unknown",
    "br-other",
    "br other",
    "na",
    "n/a",
    "nao informado",
    "não informado",
    "not informed",
    "sem informacao",
    "sem informação",
}

NON_BR_MARKERS = {
    "argentina",
    "bolivia",
    "canada",
    "chile",
    "colombia",
    "ecuador",
    "england",
    "france",
    "germany",
    "italy",
    "mexico",
    "paraguay",
    "peru",
    "portugal",
    "spain",
    "united kingdom",
    "united states",
    "uruguay",
    "usa",
    "venezuela",
}

SUSPICIOUS_DISPLAY_RE = re.compile(r"\B[A-Z]")

LOWERCASE_NAME_TOKENS = {"da", "das", "de", "do", "dos", "e"}

DISPLAY_TOKEN_OVERRIDES = {
    "belem": "Belém",
    "brasilia": "Brasília",
    "cuiaba": "Cuiabá",
    "florianopolis": "Florianópolis",
    "goiania": "Goiânia",
    "iguacu": "Iguaçu",
    "joao": "João",
    "luis": "Luís",
    "macapa": "Macapá",
    "maceio": "Maceió",
    "niteroi": "Niterói",
    "sao": "São",
    "vitoria": "Vitória",
}


def normalize_string(value: object) -> str:
    """Build a stable lookup key by stripping accents and normalizing whitespace."""

    text = strip_accents(str(value or "")).lower().strip()
    return re.sub(r"\s+", " ", text)


def limpeza_basica(raw_value: object) -> str:
    """Apply the shared cleanup rules before attempting municipality/state lookup."""

    if raw_value is None:
        return ""

    text = str(raw_value).strip()
    if not text:
        return ""

    if normalize_string(text) in INVALID_MARKERS:
        return ""

    text = text.replace("â€“", "-").replace("â€”", "-")
    text = re.sub(r"(?i)^brazil:\s*", "", text)
    text = re.sub(r"(?i)^state of\s+", "", text)
    text = re.sub(r"(?i)\(state\)", "", text)
    text = re.sub(r"(?i)^greater\s+", "", text)
    text = re.sub(r"(?i)\s+metropolitan area$", "", text)
    text = re.sub(r"(?i),\s*brazil metropolitan area$", "", text)
    text = re.sub(r"(?i),\s*brazil$", "", text)
    text = re.sub(r"(?i)\s+brazil$", "", text)
    text = re.sub(r"(?i)\s+area$", "", text)
    text = re.sub(r"(?i)\s+metro$", "", text)
    text = re.sub(r"(?i)federal district", "Distrito Federal", text)
    text = re.sub(r"\s+", " ", text).strip(" ,-/")
    return text


def compose_canonical_local(cidade: str, estado_uf: str) -> str:
    if not cidade or not estado_uf:
        return ""
    return f"{cidade}-{estado_uf}"


def _canonicalize_municipality_display_name(municipio: str) -> str:
    normalized_key = normalize_string(municipio)
    if not normalized_key:
        return ""
    if not SUSPICIOUS_DISPLAY_RE.search(municipio):
        return municipio

    title_tokens: list[str] = []
    for index, token in enumerate(normalized_key.split()):
        if token in LOWERCASE_NAME_TOKENS and index > 0:
            title_tokens.append(token)
            continue
        title_tokens.append(DISPLAY_TOKEN_OVERRIDES.get(token, token.capitalize()))
    return " ".join(title_tokens)


@dataclass(frozen=True)
class ReferenceValidation:
    malformed_lines: tuple[int, ...] = ()
    duplicate_normalized_pairs: tuple[str, ...] = ()
    unknown_states: tuple[str, ...] = ()
    suspicious_display_names: tuple[str, ...] = ()

    @property
    def has_errors(self) -> bool:
        return bool(
            self.malformed_lines or self.duplicate_normalized_pairs or self.unknown_states
        )


@dataclass(frozen=True)
class MunicipalityEntry:
    municipio: str
    estado: str
    uf: str


@dataclass(frozen=True)
class MunicipalityReference:
    municipalities_by_name: dict[str, tuple[MunicipalityEntry, ...]]
    municipalities_by_name_uf: dict[tuple[str, str], MunicipalityEntry]
    states_by_key: dict[str, str]
    validation: ReferenceValidation


@dataclass(frozen=True)
class LocalityNormalizationResult:
    cidade: str = ""
    estado: str = ""
    local: str = ""
    issue_code: str | None = None
    matched_by: str | None = None

    @property
    def is_valid(self) -> bool:
        return self.issue_code is None


def _build_state_lookup() -> dict[str, str]:
    lookup: dict[str, str] = {}
    for uf, state_name in BRAZIL_STATES_BY_UF.items():
        for alias in (
            uf,
            state_name,
            strip_accents(state_name),
        ):
            lookup[normalize_string(alias)] = uf
    lookup[normalize_string("Federal District")] = "DF"
    return lookup


STATE_LOOKUP = _build_state_lookup()


def inspect_municipios_reference(
    path: Path | None = None,
) -> tuple[list[MunicipalityEntry], ReferenceValidation]:
    """Parse the CSV reference and return its entries plus structural validation results."""

    reference_path = path or MUNICIPIOS_DATA_PATH
    entries: list[MunicipalityEntry] = []
    malformed_lines: list[int] = []
    duplicate_normalized_pairs: list[str] = []
    unknown_states: list[str] = []
    suspicious_display_names: list[str] = []
    seen_pairs: dict[tuple[str, str], int] = {}
    header_checked = False

    with reference_path.open("r", encoding="utf-8-sig", newline="") as file_handle:
        reader = csv.reader(file_handle)
        for line_number, row in enumerate(reader, start=1):
            if not row or not any(str(column).strip() for column in row):
                continue

            if not header_checked:
                header_checked = True
                header_key = tuple(normalize_string(column) for column in row[:2])
                if header_key == ("municipio", "estado"):
                    continue

            if len(row) != 2:
                malformed_lines.append(line_number)
                continue

            municipio = str(row[0]).strip()
            estado = str(row[1]).strip()
            if not municipio or not estado:
                malformed_lines.append(line_number)
                continue

            estado_uf = STATE_LOOKUP.get(normalize_string(estado))
            if estado_uf is None:
                unknown_states.append(f"{line_number}:{estado}")
                continue

            normalized_pair = (normalize_string(municipio), estado_uf)
            if normalized_pair in seen_pairs:
                duplicate_normalized_pairs.append(f"{line_number}:{municipio}/{estado_uf}")
                continue
            seen_pairs[normalized_pair] = line_number

            if SUSPICIOUS_DISPLAY_RE.search(municipio):
                suspicious_display_names.append(f"{line_number}:{municipio}")

            entries.append(
                MunicipalityEntry(
                    municipio=_canonicalize_municipality_display_name(municipio),
                    estado=BRAZIL_STATES_BY_UF[estado_uf],
                    uf=estado_uf,
                )
            )

    validation = ReferenceValidation(
        malformed_lines=tuple(malformed_lines),
        duplicate_normalized_pairs=tuple(duplicate_normalized_pairs),
        unknown_states=tuple(unknown_states),
        suspicious_display_names=tuple(suspicious_display_names),
    )
    return entries, validation


def _format_reference_error(validation: ReferenceValidation) -> str:
    parts: list[str] = []
    if validation.malformed_lines:
        parts.append(f"malformed={list(validation.malformed_lines[:5])}")
    if validation.duplicate_normalized_pairs:
        parts.append(f"duplicates={list(validation.duplicate_normalized_pairs[:5])}")
    if validation.unknown_states:
        parts.append(f"unknown_states={list(validation.unknown_states[:5])}")
    return ", ".join(parts)


@lru_cache(maxsize=1)
def load_municipality_reference() -> MunicipalityReference:
    """Load and cache the municipality/state reference used by the Gold pipeline."""

    entries, validation = inspect_municipios_reference()
    if validation.has_errors:
        raise RuntimeError(
            "municipios.csv invalido para lookup canônico: "
            + _format_reference_error(validation)
        )

    municipalities_by_name: dict[str, list[MunicipalityEntry]] = {}
    municipalities_by_name_uf: dict[tuple[str, str], MunicipalityEntry] = {}

    for entry in entries:
        municipality_key = normalize_string(entry.municipio)
        municipalities_by_name.setdefault(municipality_key, []).append(entry)
        municipalities_by_name_uf[(municipality_key, entry.uf)] = entry

    return MunicipalityReference(
        municipalities_by_name={
            key: tuple(values) for key, values in municipalities_by_name.items()
        },
        municipalities_by_name_uf=municipalities_by_name_uf,
        states_by_key=STATE_LOOKUP,
        validation=validation,
    )


def _contains_non_br_marker(*values: str) -> bool:
    normalized = f" {' '.join(normalize_string(value) for value in values if value)} "
    return any(f" {marker} " in normalized for marker in NON_BR_MARKERS)


def _resolve_state_to_uf(state_text: str, reference: MunicipalityReference) -> str | None:
    return reference.states_by_key.get(normalize_string(state_text))


def _resolved_result(entry: MunicipalityEntry, *, matched_by: str) -> LocalityNormalizationResult:
    return LocalityNormalizationResult(
        cidade=entry.municipio,
        estado=entry.uf,
        local=compose_canonical_local(entry.municipio, entry.uf),
        matched_by=matched_by,
    )


def _resolve_city_only(
    city_text: str,
    reference: MunicipalityReference,
    *,
    matched_by: str,
) -> LocalityNormalizationResult | None:
    municipality_key = normalize_string(city_text)
    matches = reference.municipalities_by_name.get(municipality_key, ())
    if not matches:
        return None
    if len(matches) > 1:
        return LocalityNormalizationResult(issue_code="unresolved", matched_by=matched_by)
    return _resolved_result(matches[0], matched_by=matched_by)


def _resolve_state_only(
    state_text: str,
    reference: MunicipalityReference,
    *,
    matched_by: str,
) -> LocalityNormalizationResult | None:
    estado_uf = _resolve_state_to_uf(state_text, reference)
    if estado_uf is None:
        return None
    return LocalityNormalizationResult(estado=estado_uf, matched_by=matched_by)


def _resolve_city_and_state(
    city_text: str,
    state_text: str,
    reference: MunicipalityReference,
    *,
    matched_by: str,
) -> LocalityNormalizationResult:
    estado_uf = _resolve_state_to_uf(state_text, reference)
    if estado_uf is None:
        issue_code = "non_br" if _contains_non_br_marker(city_text, state_text) else "unresolved"
        return LocalityNormalizationResult(issue_code=issue_code, matched_by=matched_by)

    municipality_key = normalize_string(city_text)
    if not municipality_key:
        return LocalityNormalizationResult(estado=estado_uf, matched_by=matched_by)

    exact_match = reference.municipalities_by_name_uf.get((municipality_key, estado_uf))
    if exact_match is not None:
        return _resolved_result(exact_match, matched_by=matched_by)

    if municipality_key in reference.municipalities_by_name:
        return LocalityNormalizationResult(
            issue_code="cidade_uf_mismatch",
            matched_by=matched_by,
        )

    return LocalityNormalizationResult(
        estado=estado_uf,
        issue_code="unresolved",
        matched_by=matched_by,
    )


def _extract_local_city_state(
    local_text: str,
    reference: MunicipalityReference,
) -> tuple[str, str] | None:
    for separator in ("/", "-", ","):
        if separator not in local_text:
            continue
        left, right = local_text.rsplit(separator, 1)
        city_text = left.strip()
        state_text = right.strip()
        if not city_text or not state_text:
            continue
        if _resolve_state_to_uf(state_text, reference) is not None:
            return city_text, state_text
    return None


def _resolve_freeform_local(
    local_text: str,
    reference: MunicipalityReference,
) -> LocalityNormalizationResult:
    city_state = _extract_local_city_state(local_text, reference)
    if city_state is not None:
        return _resolve_city_and_state(
            city_state[0],
            city_state[1],
            reference,
            matched_by="local_pair",
        )

    city_only = _resolve_city_only(local_text, reference, matched_by="local_city")
    if city_only is not None:
        return city_only

    state_only = _resolve_state_only(local_text, reference, matched_by="local_state")
    if state_only is not None:
        return state_only

    issue_code = "non_br" if _contains_non_br_marker(local_text) else "unresolved"
    return LocalityNormalizationResult(issue_code=issue_code, matched_by="local")


def normalize_brazilian_locality(
    *,
    cidade: object = "",
    estado: object = "",
    local: object = "",
) -> LocalityNormalizationResult:
    """Resolve city/state/local into the canonical municipality + UF representation."""

    reference = load_municipality_reference()
    raw_city = str(cidade or "").strip()
    raw_state = str(estado or "").strip()
    raw_local = str(local or "").strip()

    cleaned_city = limpeza_basica(raw_city)
    cleaned_state = limpeza_basica(raw_state)
    cleaned_local = limpeza_basica(raw_local)

    if not any((raw_city, raw_state, raw_local)):
        return LocalityNormalizationResult()

    if not any((cleaned_city, cleaned_state, cleaned_local)):
        issue_code = "non_br" if _contains_non_br_marker(raw_city, raw_state, raw_local) else "unresolved"
        return LocalityNormalizationResult(issue_code=issue_code, matched_by="input")

    if cleaned_city and cleaned_state:
        return _resolve_city_and_state(
            cleaned_city,
            cleaned_state,
            reference,
            matched_by="cidade_estado",
        )

    local_pair = (
        _extract_local_city_state(cleaned_local, reference) if cleaned_local else None
    )
    local_state = (
        _resolve_state_only(cleaned_local, reference, matched_by="local_state")
        if cleaned_local
        else None
    )

    if cleaned_city:
        if local_pair is not None and normalize_string(local_pair[0]) == normalize_string(cleaned_city):
            return _resolve_city_and_state(
                cleaned_city,
                local_pair[1],
                reference,
                matched_by="cidade_local",
            )
        if local_state is not None and local_state.estado:
            return _resolve_city_and_state(
                cleaned_city,
                local_state.estado,
                reference,
                matched_by="cidade_local",
            )
        city_only = _resolve_city_only(cleaned_city, reference, matched_by="cidade")
        if city_only is not None:
            return city_only
        issue_code = "non_br" if _contains_non_br_marker(cleaned_city, cleaned_local) else "unresolved"
        return LocalityNormalizationResult(issue_code=issue_code, matched_by="cidade")

    if cleaned_state:
        explicit_state = _resolve_state_only(cleaned_state, reference, matched_by="estado")
        if explicit_state is not None:
            if local_pair is not None:
                local_state_uf = _resolve_state_to_uf(local_pair[1], reference)
                if local_state_uf == explicit_state.estado:
                    return _resolve_city_and_state(
                        local_pair[0],
                        cleaned_state,
                        reference,
                        matched_by="estado_local",
                    )
            return explicit_state
        if _contains_non_br_marker(cleaned_state, cleaned_local):
            return LocalityNormalizationResult(issue_code="non_br", matched_by="estado")

    if cleaned_local:
        return _resolve_freeform_local(cleaned_local, reference)

    return LocalityNormalizationResult(issue_code="unresolved", matched_by="input")
