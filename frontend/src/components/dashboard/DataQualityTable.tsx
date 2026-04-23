import {
  Box,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";

import type { CompletenessMetrics, OrigemQualidadeRow } from "../../types/dashboard";
import { formatInteger, formatPercent } from "../../utils/ageAnalysis";

type DataQualityTableProps = {
  consolidated: CompletenessMetrics;
  rows: OrigemQualidadeRow[];
};

function SummaryItem({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <Box
      sx={{
        border: 1,
        borderColor: "divider",
        borderRadius: 2,
        px: 1.25,
        py: 1,
      }}
    >
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" fontWeight={700}>
        {value}
      </Typography>
    </Box>
  );
}

export function DataQualityTable({ consolidated, rows }: DataQualityTableProps) {
  return (
    <Card variant="outlined" component="section" aria-label="Qualidade dos dados por fonte do vinculo">
      <CardContent>
        <Typography variant="subtitle1" fontWeight={800} sx={{ mb: 1 }}>
          Qualidade dos dados por fonte do vinculo
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Consolidado primeiro, depois detalhamento por fonte. Percentuais sempre sobre o total de vinculos do recorte
          correspondente.
        </Typography>
        <Box
          sx={{
            display: "grid",
            gap: 1,
            mb: 2,
            gridTemplateColumns: {
              xs: "minmax(0, 1fr)",
              sm: "repeat(2, minmax(0, 1fr))",
              lg: "repeat(4, minmax(0, 1fr))",
            },
          }}
        >
          <SummaryItem label="Base consolidada" value={formatInteger(consolidated.base_vinculos)} />
          <SummaryItem
            label="Sem CPF"
            value={`${formatInteger(consolidated.sem_cpf_volume)} / ${formatPercent(consolidated.sem_cpf_pct)}`}
          />
          <SummaryItem
            label="Sem nascimento"
            value={`${formatInteger(consolidated.sem_data_nascimento_volume)} / ${formatPercent(
              consolidated.sem_data_nascimento_pct,
            )}`}
          />
          <SummaryItem
            label="Sem nome completo"
            value={`${formatInteger(consolidated.sem_nome_completo_volume)} / ${formatPercent(
              consolidated.sem_nome_completo_pct,
            )}`}
          />
        </Box>
        {rows.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            Nenhuma fonte com vinculos no filtro.
          </Typography>
        ) : (
          <TableContainer sx={{ overflowX: "auto" }}>
            <Table
              size="small"
              aria-label="Tabela de qualidade por fonte do vinculo"
              sx={{ minWidth: 720 }}
            >
              <TableHead>
                <TableRow>
                  <TableCell>Fonte do vinculo</TableCell>
                  <TableCell align="right">Vinculos</TableCell>
                  <TableCell align="right">Sem CPF</TableCell>
                  <TableCell align="right">Sem nascimento</TableCell>
                  <TableCell align="right">Sem nome completo</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.source_kind}>
                    <TableCell>
                      <Typography variant="body2" fontWeight={700}>
                        {row.label}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {row.source_kind}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">{formatInteger(row.base_vinculos)}</TableCell>
                    <TableCell align="right">
                      {formatInteger(row.sem_cpf_volume)} / {formatPercent(row.sem_cpf_pct)}
                    </TableCell>
                    <TableCell align="right">
                      {formatInteger(row.sem_data_nascimento_volume)} /{" "}
                      {formatPercent(row.sem_data_nascimento_pct)}
                    </TableCell>
                    <TableCell align="right">
                      {formatInteger(row.sem_nome_completo_volume)} /{" "}
                      {formatPercent(row.sem_nome_completo_pct)}
                    </TableCell>
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
