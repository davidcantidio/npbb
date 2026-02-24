"""Coverage contract loader for session/day coverage governance.

This module loads a versioned YAML contract that defines:
- dataset expectations by canonical `session_type`;
- allowed status domain (`ok`, `gap`, `partial`);
- severity and missing-status semantics per dataset;
- gate-action hints consumed by report publication policies.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

import yaml

from .framework import Severity

try:  # pragma: no cover - import style depends on caller cwd
    from app.models.etl_registry import CoverageDataset
    from app.models.models import EventSessionType
except ModuleNotFoundError:  # pragma: no cover
    BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))
    from app.models.etl_registry import CoverageDataset
    from app.models.models import EventSessionType


DEFAULT_COVERAGE_CONTRACT_PATH = (
    Path(__file__).resolve().parent / "config" / "coverage_contract.yml"
)
_REQUIRED_STATUS_VALUES = ("ok", "gap", "partial")
_GATE_ACTION_VALUES = {"allow", "partial", "block"}


class CoverageContractError(ValueError):
    """Raised when coverage contract YAML is invalid."""


@dataclass(frozen=True)
class DatasetCoverageRule:
    """Coverage expectation rule for one dataset within one session type.

    Args:
        dataset: Canonical dataset identifier.
        required: Whether dataset is expected in session coverage matrix.
        severity: Severity used when this rule fails.
        status_on_missing: Status emitted when dataset is not observed.
        description: Optional human-readable rationale for operators.
    """

    dataset: CoverageDataset
    required: bool
    severity: Severity
    status_on_missing: str
    description: str | None = None


@dataclass(frozen=True)
class SessionCoverageContract:
    """Coverage rule set for one canonical session type."""

    session_type: EventSessionType
    datasets: tuple[DatasetCoverageRule, ...]


@dataclass(frozen=True)
class CoverageRequirementsContract:
    """Coverage-requirements view derived from full coverage contract."""

    default_required_datasets: tuple[CoverageDataset, ...]
    required_datasets_by_session_type: dict[EventSessionType, tuple[CoverageDataset, ...]]


@dataclass(frozen=True)
class CoverageContract:
    """Full parsed coverage contract.

    Args:
        version: Contract version.
        status_domain: Allowed status domain.
        default_required_datasets: Fallback required datasets.
        session_types: Per-session-type contract section.
        gate_actions: Gate decision hints by severity and status.
        source_path: Contract file path.
    """

    version: int
    status_domain: tuple[str, ...]
    default_required_datasets: tuple[CoverageDataset, ...]
    session_types: dict[EventSessionType, SessionCoverageContract]
    gate_actions: dict[Severity, dict[str, str]]
    source_path: Path


def _as_mapping(value: Any, *, field: str) -> Mapping[str, Any]:
    """Ensure one YAML node is a mapping."""

    if isinstance(value, Mapping):
        return value
    raise CoverageContractError(
        f"{field} invalido: esperado objeto YAML. Como corrigir: usar chave: valor."
    )


def _parse_version(value: Any) -> int:
    """Parse positive integer version field."""

    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise CoverageContractError(
            "version invalido: esperado inteiro positivo."
        ) from exc
    if parsed <= 0:
        raise CoverageContractError("version invalido: esperado inteiro positivo.")
    return parsed


def _normalize_dataset(value: Any, *, field: str) -> CoverageDataset:
    """Normalize raw dataset identifier into canonical enum."""

    text = str(value or "").strip().lower()
    aliases = {
        "access": "access_control",
        "sales": "ticket_sales",
    }
    normalized = aliases.get(text, text)
    if not normalized:
        raise CoverageContractError(
            f"{field} invalido: dataset vazio. "
            "Como corrigir: usar access_control|ticket_sales|optin|leads."
        )
    try:
        return CoverageDataset(normalized)
    except ValueError as exc:
        raise CoverageContractError(
            f"{field} invalido: dataset {normalized!r} nao suportado. "
            "Como corrigir: usar access_control|ticket_sales|optin|leads."
        ) from exc


def _normalize_session_type(value: Any, *, field: str) -> EventSessionType:
    """Normalize raw session type into canonical enum."""

    if isinstance(value, EventSessionType):
        return value

    text = str(value or "").strip().upper()
    if not text:
        raise CoverageContractError(
            f"{field} invalido: session_type vazio. "
            "Como corrigir: usar DIURNO_GRATUITO|NOTURNO_SHOW|OUTRO."
        )
    if text in EventSessionType.__members__:
        return EventSessionType[text]
    for session_type in EventSessionType:
        if session_type.value.upper() == text:
            return session_type
    raise CoverageContractError(
        f"{field} invalido: session_type {text!r} nao suportado. "
        "Como corrigir: usar DIURNO_GRATUITO|NOTURNO_SHOW|OUTRO."
    )


def _normalize_severity(value: Any, *, field: str) -> Severity:
    """Normalize severity field to framework domain."""

    text = str(value or "").strip().lower()
    if not text:
        raise CoverageContractError(
            f"{field} invalido: severidade vazia. Como corrigir: usar info|warning|error."
        )
    try:
        return Severity(text)
    except ValueError as exc:
        raise CoverageContractError(
            f"{field} invalido: severidade {text!r} nao suportada. "
            "Como corrigir: usar info|warning|error."
        ) from exc


def _parse_status_domain(raw: Any) -> tuple[str, ...]:
    """Parse and validate contract status domain."""

    if not isinstance(raw, list):
        raise CoverageContractError(
            "status_domain invalido: esperado lista. "
            "Como corrigir: usar [ok, gap, partial]."
        )
    values = tuple(str(item or "").strip().lower() for item in raw if str(item or "").strip())
    if len(values) != len(set(values)):
        raise CoverageContractError(
            "status_domain invalido: valores duplicados. "
            "Como corrigir: remover duplicidade."
        )
    required = set(_REQUIRED_STATUS_VALUES)
    if not required.issubset(set(values)):
        raise CoverageContractError(
            "status_domain invalido: obrigatorio conter ok, gap e partial."
        )
    return values


def _parse_required_dataset_list(raw: Any, *, field: str) -> tuple[CoverageDataset, ...]:
    """Parse list of datasets used for default/fallback requirements."""

    if not isinstance(raw, list):
        raise CoverageContractError(
            f"{field} invalido: esperado lista de datasets."
        )
    values: list[CoverageDataset] = []
    seen: set[CoverageDataset] = set()
    for index, item in enumerate(raw):
        dataset = _normalize_dataset(item, field=f"{field}[{index}]")
        if dataset in seen:
            continue
        seen.add(dataset)
        values.append(dataset)
    if not values:
        raise CoverageContractError(
            f"{field} invalido: lista vazia. Como corrigir: informar ao menos um dataset."
        )
    return tuple(values)


def _parse_gate_actions(raw: Any, *, status_domain: tuple[str, ...]) -> dict[Severity, dict[str, str]]:
    """Parse optional gate action hints by severity/status."""

    if raw in (None, ""):
        return {}
    root = _as_mapping(raw, field="gate_actions")
    output: dict[Severity, dict[str, str]] = {}
    for raw_severity, raw_rules in root.items():
        severity = _normalize_severity(raw_severity, field=f"gate_actions.{raw_severity}")
        rules_map = _as_mapping(raw_rules, field=f"gate_actions.{severity.value}")
        mapped: dict[str, str] = {}
        for raw_status, raw_action in rules_map.items():
            status = str(raw_status or "").strip().lower()
            if status not in status_domain:
                raise CoverageContractError(
                    f"gate_actions.{severity.value}.{raw_status} invalido: status fora do dominio."
                )
            action = str(raw_action or "").strip().lower()
            if action not in _GATE_ACTION_VALUES:
                raise CoverageContractError(
                    f"gate_actions.{severity.value}.{status} invalido: "
                    "acao deve ser allow|partial|block."
                )
            mapped[status] = action
        output[severity] = mapped
    return output


def _parse_session_rules(
    raw: Any,
    *,
    status_domain: tuple[str, ...],
) -> dict[EventSessionType, SessionCoverageContract]:
    """Parse per-session-type dataset rules."""

    section = _as_mapping(raw, field="session_types")
    output: dict[EventSessionType, SessionCoverageContract] = {}

    for raw_session_type, raw_payload in section.items():
        session_type = _normalize_session_type(
            raw_session_type,
            field=f"session_types.{raw_session_type}",
        )
        payload = _as_mapping(
            raw_payload,
            field=f"session_types.{session_type.value}",
        )
        datasets_raw = payload.get("datasets")
        if not isinstance(datasets_raw, list) or not datasets_raw:
            raise CoverageContractError(
                f"session_types.{session_type.value}.datasets invalido: "
                "esperado lista nao vazia."
            )

        rules: list[DatasetCoverageRule] = []
        seen_datasets: set[CoverageDataset] = set()
        for index, item in enumerate(datasets_raw):
            node = _as_mapping(
                item,
                field=f"session_types.{session_type.value}.datasets[{index}]",
            )
            dataset = _normalize_dataset(
                node.get("dataset"),
                field=f"session_types.{session_type.value}.datasets[{index}].dataset",
            )
            if dataset in seen_datasets:
                raise CoverageContractError(
                    f"session_types.{session_type.value} possui dataset duplicado ({dataset.value})."
                )
            seen_datasets.add(dataset)

            required = bool(node.get("required", True))
            severity = _normalize_severity(
                node.get("severity", "error"),
                field=f"session_types.{session_type.value}.datasets[{index}].severity",
            )
            status_on_missing = str(node.get("status_on_missing", "gap") or "").strip().lower()
            if status_on_missing not in status_domain:
                raise CoverageContractError(
                    f"session_types.{session_type.value}.datasets[{index}].status_on_missing "
                    f"invalido ({status_on_missing!r}). "
                    "Como corrigir: usar valor presente em status_domain."
                )
            description = node.get("description")
            if description is not None:
                description = str(description).strip() or None

            rules.append(
                DatasetCoverageRule(
                    dataset=dataset,
                    required=required,
                    severity=severity,
                    status_on_missing=status_on_missing,
                    description=description,
                )
            )

        output[session_type] = SessionCoverageContract(
            session_type=session_type,
            datasets=tuple(rules),
        )

    return output


def _validate_show_minimum(contract: CoverageContract) -> None:
    """Validate mandatory minimum for `NOTURNO_SHOW` session type."""

    show_policy = contract.session_types.get(EventSessionType.NOTURNO_SHOW)
    if show_policy is None:
        raise CoverageContractError(
            "Contrato invalido: session_types.NOTURNO_SHOW obrigatorio."
        )

    by_dataset = {rule.dataset: rule for rule in show_policy.datasets}
    access_rule = by_dataset.get(CoverageDataset.ACCESS_CONTROL)
    if access_rule is None:
        raise CoverageContractError(
            "Contrato invalido: NOTURNO_SHOW deve incluir dataset access_control."
        )
    if not access_rule.required or access_rule.severity != Severity.ERROR:
        raise CoverageContractError(
            "Contrato invalido: access_control em NOTURNO_SHOW deve ser required=true e severity=error."
        )


def load_coverage_contract(
    path: Path | str = DEFAULT_COVERAGE_CONTRACT_PATH,
) -> CoverageContract:
    """Load and validate coverage contract YAML.

    Args:
        path: Contract YAML path.

    Returns:
        Parsed and validated coverage contract.

    Raises:
        FileNotFoundError: If contract file does not exist.
        CoverageContractError: If YAML structure/domain is invalid.
    """

    contract_path = Path(path)
    if not contract_path.exists():
        raise FileNotFoundError(f"Coverage contract YAML not found: {contract_path}")

    payload = yaml.safe_load(contract_path.read_text(encoding="utf-8")) or {}
    root = _as_mapping(payload, field="$")
    version = _parse_version(root.get("version"))
    status_domain = _parse_status_domain(root.get("status_domain", list(_REQUIRED_STATUS_VALUES)))
    default_required = _parse_required_dataset_list(
        root.get("default_required_datasets", ["access_control"]),
        field="default_required_datasets",
    )
    session_types = _parse_session_rules(
        root.get("session_types"),
        status_domain=status_domain,
    )
    gate_actions = _parse_gate_actions(
        root.get("gate_actions"),
        status_domain=status_domain,
    )

    contract = CoverageContract(
        version=version,
        status_domain=status_domain,
        default_required_datasets=default_required,
        session_types=session_types,
        gate_actions=gate_actions,
        source_path=contract_path,
    )
    _validate_show_minimum(contract)
    return contract


def required_datasets_for_session_type(
    contract: CoverageContract,
    session_type: EventSessionType | str,
) -> tuple[CoverageDataset, ...]:
    """Resolve required datasets for one session type using contract rules.

    Args:
        contract: Parsed coverage contract.
        session_type: Canonical session type.

    Returns:
        Required dataset tuple for the given session type.
    """

    normalized = _normalize_session_type(session_type, field="session_type")
    session_policy = contract.session_types.get(normalized)
    if session_policy is None:
        return contract.default_required_datasets
    datasets = tuple(rule.dataset for rule in session_policy.datasets if rule.required)
    if datasets:
        return datasets
    return contract.default_required_datasets


def coverage_requirements_from_contract(
    contract: CoverageContract,
) -> CoverageRequirementsContract:
    """Build coverage-requirements view for evaluators from full contract.

    Args:
        contract: Parsed coverage contract.

    Returns:
        Requirements view with fallback + per-session required datasets.
    """

    mapping: dict[EventSessionType, tuple[CoverageDataset, ...]] = {}
    for session_type in contract.session_types:
        mapping[session_type] = required_datasets_for_session_type(contract, session_type)
    return CoverageRequirementsContract(
        default_required_datasets=contract.default_required_datasets,
        required_datasets_by_session_type=mapping,
    )
