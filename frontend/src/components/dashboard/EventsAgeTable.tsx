import type { ReactNode } from "react";
import { useMemo, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Typography,
} from "@mui/material";

import type { EventoAgeAnalysis } from "../../types/dashboard";
import {
  formatEventLocation,
  formatInteger,
  formatPercent,
  getDominantAgeRangeLabel,
  getNonBbMetrics,
} from "../../utils/ageAnalysis";
import { hasPartialBbData } from "../../utils/coverage";
import { CoverageBanner } from "./CoverageBanner";
import { InfoTooltip } from "./InfoTooltip";

type SortDirection = "asc" | "desc";

type SortKey =
  | "evento_nome"
  | "base_leads"
  | "clientes_bb_volume"
  | "clientes_bb_pct"
  | "nao_clientes_volume"
  | "nao_clientes_pct"
  | "cobertura_bb_pct"
  | "faixa_18_25_volume"
  | "faixa_18_25_pct"
  | "faixa_26_40_volume"
  | "faixa_26_40_pct"
  | "fora_18_40_volume"
  | "fora_18_40_pct"
  | "sem_info_volume"
  | "sem_info_pct"
  | "faixa_dominante";

type EventsAgeTableProps = {
  events: EventoAgeAnalysis[];
  onSelectEvento?: (eventoId: number) => void;
};

type ColumnDefinition = {
  key: SortKey;
  label: string;
  align?: "left" | "right";
  accessor: (event: EventoAgeAnalysis) => string | number | null;
  render: (event: EventoAgeAnalysis) => ReactNode;
};

const columns: ColumnDefinition[] = [
  {
    key: "evento_nome",
    label: "Evento",
    accessor: (event) => event.evento_nome,
    render: (event) => (
      <Box>
        <Typography variant="body2" fontWeight={700}>
          {event.evento_nome}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {formatEventLocation(event)}
        </Typography>
      </Box>
    ),
  },
  {
    key: "base_leads",
    label: "Base",
    align: "right",
    accessor: (event) => event.base_leads,
    render: (event) => formatInteger(event.base_leads),
  },
  {
    key: "clientes_bb_volume",
    label: "Clientes BB",
    align: "right",
    accessor: (event) => event.clientes_bb_volume,
    render: (event) => {
      const partialBbData = hasPartialBbData(
        event.clientes_bb_volume,
        event.clientes_bb_pct,
        event.cobertura_bb_pct,
      );

      return (
        <Stack spacing={0.35} alignItems="flex-end">
          <Typography variant="body2">
            {event.clientes_bb_volume === null ? "—" : formatInteger(event.clientes_bb_volume)} /{" "}
            {formatPercent(event.clientes_bb_pct)}
          </Typography>
          {partialBbData ? (
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.25 }}>
              <Typography variant="caption" color="text.secondary">
                (dados parciais)
              </Typography>
              <InfoTooltip
                label="Dados parciais"
                description="Dados parciais: a cobertura BB esta abaixo do limiar minimo para exibir a metrica com seguranca."
              />
            </Box>
          ) : null}
        </Stack>
      );
    },
  },
  {
    key: "nao_clientes_volume",
    label: "Nao clientes",
    align: "right",
    accessor: (event) => getNonBbMetrics(event).volume,
    render: (event) => {
      const nonBb = getNonBbMetrics(event);
      return `${nonBb.volume === null ? "—" : formatInteger(nonBb.volume)} / ${formatPercent(nonBb.pct)}`;
    },
  },
  {
    key: "cobertura_bb_pct",
    label: "Cobertura BB",
    align: "right",
    accessor: (event) => event.cobertura_bb_pct,
    render: (event) => (
      <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
        <CoverageBanner coverage={event.cobertura_bb_pct} variant="compact" scope="event" />
      </Box>
    ),
  },
  {
    key: "faixa_18_25_volume",
    label: "18-25",
    align: "right",
    accessor: (event) => event.faixas.faixa_18_25.volume,
    render: (event) =>
      `${formatInteger(event.faixas.faixa_18_25.volume)} / ${formatPercent(event.faixas.faixa_18_25.pct)}`,
  },
  {
    key: "faixa_26_40_volume",
    label: "26-40",
    align: "right",
    accessor: (event) => event.faixas.faixa_26_40.volume,
    render: (event) =>
      `${formatInteger(event.faixas.faixa_26_40.volume)} / ${formatPercent(event.faixas.faixa_26_40.pct)}`,
  },
  {
    key: "fora_18_40_volume",
    label: "Fora 18-40",
    align: "right",
    accessor: (event) => event.faixas.fora_18_40.volume,
    render: (event) =>
      `${formatInteger(event.faixas.fora_18_40.volume)} / ${formatPercent(event.faixas.fora_18_40.pct)}`,
  },
  {
    key: "sem_info_volume",
    label: "Sem info",
    align: "right",
    accessor: (event) => event.faixas.sem_info_volume,
    render: (event) =>
      `${formatInteger(event.faixas.sem_info_volume)} / ${formatPercent(event.faixas.sem_info_pct_da_base)}`,
  },
  {
    key: "faixa_dominante",
    label: "Faixa dominante",
    accessor: (event) => getDominantAgeRangeLabel(event.faixa_dominante),
    render: (event) => getDominantAgeRangeLabel(event.faixa_dominante),
  },
];

function compareValues(a: string | number | null, b: string | number | null, direction: SortDirection) {
  const normalizedA = a ?? Number.NEGATIVE_INFINITY;
  const normalizedB = b ?? Number.NEGATIVE_INFINITY;

  if (typeof normalizedA === "string" && typeof normalizedB === "string") {
    return direction === "asc"
      ? normalizedA.localeCompare(normalizedB, "pt-BR")
      : normalizedB.localeCompare(normalizedA, "pt-BR");
  }

  const numericA = typeof normalizedA === "number" ? normalizedA : Number(normalizedA);
  const numericB = typeof normalizedB === "number" ? normalizedB : Number(normalizedB);
  return direction === "asc" ? numericA - numericB : numericB - numericA;
}

export function EventsAgeTable({ events, onSelectEvento }: EventsAgeTableProps) {
  const [sortBy, setSortBy] = useState<SortKey>("base_leads");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

  const sortedEvents = useMemo(() => {
    const activeColumn = columns.find((column) => column.key === sortBy) ?? columns[0];

    return [...events].sort((left, right) => {
      const comparison = compareValues(activeColumn.accessor(left), activeColumn.accessor(right), sortDirection);
      if (comparison !== 0) return comparison;
      return left.evento_nome.localeCompare(right.evento_nome, "pt-BR");
    });
  }, [events, sortBy, sortDirection]);

  const handleRequestSort = (key: SortKey) => {
    if (sortBy === key) {
      setSortDirection((current) => (current === "asc" ? "desc" : "asc"));
      return;
    }
    setSortBy(key);
    setSortDirection(key === "evento_nome" || key === "faixa_dominante" ? "asc" : "desc");
  };

  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="subtitle1" fontWeight={800} sx={{ mb: 2 }}>
          Eventos no filtro
        </Typography>

        {sortedEvents.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            Nenhum evento encontrado para a tabela.
          </Typography>
        ) : (
          <TableContainer data-testid="events-age-table-scroll" data-scroll-x="enabled" sx={{ overflowX: "auto" }}>
            <Table
              data-testid="events-age-table-grid"
              aria-label="Tabela de eventos da analise etaria"
              size="small"
              sx={{ minWidth: 1240 }}
            >
              <TableHead>
                <TableRow>
                  {columns.map((column) => (
                    <TableCell
                      key={column.key}
                      align={column.align ?? "left"}
                      sortDirection={sortBy === column.key ? sortDirection : false}
                    >
                      <TableSortLabel
                        active={sortBy === column.key}
                        direction={sortBy === column.key ? sortDirection : "asc"}
                        onClick={() => handleRequestSort(column.key)}
                      >
                        {column.label}
                      </TableSortLabel>
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {sortedEvents.map((event, index) => (
                  <TableRow
                    key={event.evento_id}
                    data-testid={`events-age-table-row-${event.evento_id}`}
                    hover
                    onClick={onSelectEvento ? () => onSelectEvento(event.evento_id) : undefined}
                    sx={{
                      cursor: onSelectEvento ? "pointer" : "default",
                      bgcolor: index % 2 === 0 ? "transparent" : "grey.50",
                    }}
                  >
                    {columns.map((column) => (
                      <TableCell key={column.key} align={column.align ?? "left"}>
                        {column.render(event)}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
    </Card>
  );
}
