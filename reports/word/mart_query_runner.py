"""Mart query runner and render payload adapters for Word report generation.

This module provides a single DB access layer to execute `mart_report_*` views
and convert row results into payloads for text/table/figure renderers.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .placeholders_mapping import ensure_mart_name
from .render_text import query_to_text_payload


@dataclass(frozen=True)
class MartQueryResult:
    """Result envelope for one mart query execution.

    Args:
        mart_name: Executed mart/view name.
        rows: Query rows converted to dictionaries.
        cached: Whether result came from in-memory cache.
    """

    mart_name: str
    rows: tuple[dict[str, Any], ...]
    cached: bool = False


class MartQueryRunnerError(ValueError):
    """Raised when mart query execution or adaptation fails."""


class MartQueryRunner:
    """Execute mart views and provide optional section-level caching.

    Args:
        session: SQLAlchemy-compatible session implementing `.execute(...)`.
        enable_cache: Enable in-memory cache by `(section, mart, params)` key.
    """

    def __init__(self, session: Any, *, enable_cache: bool = True) -> None:
        self.session = session
        self.enable_cache = bool(enable_cache)
        self._cache: dict[tuple[str, str, tuple[tuple[str, Any], ...]], tuple[dict[str, Any], ...]] = {}

    def _build_cache_key(
        self,
        *,
        section_cache_key: str | None,
        mart_name: str,
        params: Mapping[str, Any] | None,
    ) -> tuple[str, str, tuple[tuple[str, Any], ...]]:
        """Build deterministic cache key for one mart execution.

        Args:
            section_cache_key: Optional section/placeholder key.
            mart_name: Valid mart/view name.
            params: Query parameter mapping.

        Returns:
            Cache key tuple.
        """

        section = (section_cache_key or "__default__").strip() or "__default__"
        param_items = tuple(
            sorted((str(key), self._freeze_value(params[key])) for key in (params or {}))
        )
        return (section, mart_name, param_items)

    def _freeze_value(self, value: Any) -> Any:
        """Convert nested values to hashable cache-key-safe representation.

        Args:
            value: Raw parameter value.

        Returns:
            Hashable representation preserving logical content.
        """

        if isinstance(value, list):
            return tuple(self._freeze_value(item) for item in value)
        if isinstance(value, dict):
            return tuple(sorted((str(key), self._freeze_value(item)) for key, item in value.items()))
        return value

    def execute_view(
        self,
        mart_name: str,
        *,
        params: Mapping[str, Any] | None = None,
        section_cache_key: str | None = None,
    ) -> MartQueryResult:
        """Execute one `mart_report_*` view with optional equality filters.

        Args:
            mart_name: View name (`mart_report_*`).
            params: Optional equality filters (`column=value`).
            section_cache_key: Optional cache namespace (e.g. placeholder id).

        Returns:
            `MartQueryResult` with rows and cache metadata.

        Raises:
            MartQueryRunnerError: If view name/params are invalid or query fails.
        """

        safe_mart_name = ensure_mart_name(mart_name)
        safe_params: dict[str, Any] = {}
        for key, value in (params or {}).items():
            key_str = str(key).strip()
            if not key_str:
                raise MartQueryRunnerError(
                    f"Parametro invalido para mart {safe_mart_name}: chave vazia."
                )
            safe_params[key_str] = value

        cache_key = self._build_cache_key(
            section_cache_key=section_cache_key,
            mart_name=safe_mart_name,
            params=safe_params,
        )
        if self.enable_cache and cache_key in self._cache:
            return MartQueryResult(
                mart_name=safe_mart_name,
                rows=self._cache[cache_key],
                cached=True,
            )

        query = f'SELECT * FROM "{safe_mart_name}"'
        sql_params: dict[str, Any] = {}
        if safe_params:
            clauses: list[str] = []
            for index, (key, value) in enumerate(sorted(safe_params.items()), start=1):
                bind_name = f"p{index}"
                clauses.append(f'"{key}" = :{bind_name}')
                sql_params[bind_name] = value
            query = f"{query} WHERE {' AND '.join(clauses)}"

        try:
            result = self.session.execute(text(query), sql_params)
            rows = tuple(dict(row) for row in result.mappings().all())
        except SQLAlchemyError as exc:
            raise MartQueryRunnerError(
                f"Falha ao executar mart {safe_mart_name}. "
                "Como corrigir: validar se a view existe e se os parametros estao corretos."
            ) from exc

        if self.enable_cache:
            self._cache[cache_key] = rows

        return MartQueryResult(mart_name=safe_mart_name, rows=rows, cached=False)


def rows_to_text_payload(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    """Adapt query rows to text placeholder payload.

    Args:
        rows: Query rows from one mart/view.

    Returns:
        Text lines suitable for `render_text_placeholder`.

    Raises:
        MartQueryRunnerError: If adaptation fails.
    """

    try:
        return query_to_text_payload(rows)
    except ValueError as exc:
        raise MartQueryRunnerError(
            "Falha ao adaptar rows para payload de texto. "
            "Como corrigir: incluir colunas text/summary/value ou label+value."
        ) from exc


def rows_to_table_payload(
    rows: Sequence[Mapping[str, Any]],
    *,
    columns: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Adapt query rows to table placeholder payload.

    Args:
        rows: Query rows from one mart/view.
        columns: Optional explicit output columns order.

    Returns:
        Dictionary payload with `columns` and `rows`.

    Raises:
        MartQueryRunnerError: If contract columns are invalid.
    """

    if not isinstance(rows, Sequence):
        raise MartQueryRunnerError("rows_to_table_payload: rows deve ser sequencia de objetos.")
    row_dicts = [dict(row) for row in rows]

    if columns is None:
        if not row_dicts:
            raise MartQueryRunnerError(
                "rows_to_table_payload: rows vazio requer columns explicitas no mapping."
            )
        output_columns = list(row_dicts[0].keys())
    else:
        output_columns = [str(column).strip() for column in columns]
        if not output_columns or any(not column for column in output_columns):
            raise MartQueryRunnerError(
                "rows_to_table_payload: columns deve conter textos nao vazios."
            )

    for row_index, row in enumerate(row_dicts):
        missing = [column for column in output_columns if column not in row]
        if missing:
            missing_list = ", ".join(missing)
            raise MartQueryRunnerError(
                "rows_to_table_payload: contrato de colunas violado em "
                f"rows[{row_index}] (faltando: {missing_list})."
            )

    normalized_rows = [
        {column: row.get(column) for column in output_columns}
        for row in row_dicts
    ]
    return {"columns": output_columns, "rows": normalized_rows}


def rows_to_chart_payload(
    rows: Sequence[Mapping[str, Any]],
    *,
    x_field: str | None = None,
    y_field: str | None = None,
    series_name: str | None = None,
) -> dict[str, Any]:
    """Adapt query rows to figure/chart payload contract.

    Args:
        rows: Query rows from one mart/view.
        x_field: Optional x-axis field. Inferred when omitted.
        y_field: Optional y-axis field. Inferred when omitted.
        series_name: Optional series label.

    Returns:
        Dictionary with chart payload (`data`, `x_field`, `y_field`, `series_name`).

    Raises:
        MartQueryRunnerError: If rows are empty or required fields cannot be inferred.
    """

    if not isinstance(rows, Sequence):
        raise MartQueryRunnerError("rows_to_chart_payload: rows deve ser sequencia de objetos.")
    row_dicts = [dict(row) for row in rows]
    if not row_dicts:
        raise MartQueryRunnerError("rows_to_chart_payload: rows vazio.")

    first_row = row_dicts[0]
    keys = list(first_row.keys())
    if x_field is None:
        if not keys:
            raise MartQueryRunnerError("rows_to_chart_payload: nao foi possivel inferir x_field.")
        x_field = keys[0]
    if y_field is None:
        if len(keys) < 2:
            raise MartQueryRunnerError("rows_to_chart_payload: nao foi possivel inferir y_field.")
        y_field = keys[1]

    if x_field not in first_row or y_field not in first_row:
        raise MartQueryRunnerError(
            f"rows_to_chart_payload: campos x/y ausentes ({x_field}, {y_field})."
        )

    return {
        "data": row_dicts,
        "x_field": x_field,
        "y_field": y_field,
        "series_name": series_name or y_field,
    }
