from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .ppt_matching import FAMILY_NUMERIC_SCOPE, map_event_family


REQUIRED_TRUTH_COLUMNS = [
    "evento",
    "Contagem CPF",
    "Qtd Clientes BB",
    "Qtd Não Clientes",
    "Total Leads 18-25",
    "Total Leads 26-40",
]


@dataclass(frozen=True)
class TruthMetrics:
    total_leads: int
    clientes_bb: int
    nao_clientes: int
    faixa_18_25: int
    faixa_26_40: int
    fora_18_40: int


@dataclass(frozen=True)
class SourceEvent:
    name: str
    family: str
    metrics: TruthMetrics
    numeric_scope: str


@dataclass(frozen=True)
class TruthCatalog:
    source_events: list[SourceEvent]
    event_metrics: dict[str, TruthMetrics]
    family_metrics: dict[str, TruthMetrics]
    total_metrics: TruthMetrics


def load_truth_catalog(csv_path: Path) -> TruthCatalog:
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    missing = [column for column in REQUIRED_TRUTH_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"CSV sem colunas obrigatorias para auditoria: {missing}")

    numeric_df = df.copy()
    for column in REQUIRED_TRUTH_COLUMNS[1:]:
        numeric_df[column] = pd.to_numeric(numeric_df[column], errors="raise")

    source_events: list[SourceEvent] = []
    event_metrics: dict[str, TruthMetrics] = {}
    family_groups: dict[str, list[str]] = {}

    grouped_events = (
        numeric_df.groupby("evento", dropna=False)[REQUIRED_TRUTH_COLUMNS[1:]]
        .sum()
        .reset_index()
        .sort_values("evento")
    )
    for row in grouped_events.to_dict("records"):
        event_name = str(row["evento"])
        family = map_event_family(event_name)
        if family is None:
            raise ValueError(f"UNMAPPED_SOURCE_EVENT: {event_name}")

        metrics = TruthMetrics(
            total_leads=int(row["Contagem CPF"]),
            clientes_bb=int(row["Qtd Clientes BB"]),
            nao_clientes=int(row["Qtd Não Clientes"]),
            faixa_18_25=int(row["Total Leads 18-25"]),
            faixa_26_40=int(row["Total Leads 26-40"]),
            fora_18_40=int(row["Contagem CPF"] - row["Total Leads 18-25"] - row["Total Leads 26-40"]),
        )
        event_metrics[event_name] = metrics
        source_events.append(
            SourceEvent(
                name=event_name,
                family=family,
                metrics=metrics,
                numeric_scope=FAMILY_NUMERIC_SCOPE[family],
            )
        )
        family_groups.setdefault(family, []).append(event_name)

    family_metrics: dict[str, TruthMetrics] = {}
    for family, event_names in family_groups.items():
        family_df = numeric_df[numeric_df["evento"].isin(event_names)]
        total = int(family_df["Contagem CPF"].sum())
        faixa_18_25 = int(family_df["Total Leads 18-25"].sum())
        faixa_26_40 = int(family_df["Total Leads 26-40"].sum())
        family_metrics[family] = TruthMetrics(
            total_leads=total,
            clientes_bb=int(family_df["Qtd Clientes BB"].sum()),
            nao_clientes=int(family_df["Qtd Não Clientes"].sum()),
            faixa_18_25=faixa_18_25,
            faixa_26_40=faixa_26_40,
            fora_18_40=total - faixa_18_25 - faixa_26_40,
        )

    total = int(numeric_df["Contagem CPF"].sum())
    total_18_25 = int(numeric_df["Total Leads 18-25"].sum())
    total_26_40 = int(numeric_df["Total Leads 26-40"].sum())
    total_metrics = TruthMetrics(
        total_leads=total,
        clientes_bb=int(numeric_df["Qtd Clientes BB"].sum()),
        nao_clientes=int(numeric_df["Qtd Não Clientes"].sum()),
        faixa_18_25=total_18_25,
        faixa_26_40=total_26_40,
        fora_18_40=total - total_18_25 - total_26_40,
    )

    return TruthCatalog(
        source_events=source_events,
        event_metrics=event_metrics,
        family_metrics=family_metrics,
        total_metrics=total_metrics,
    )
