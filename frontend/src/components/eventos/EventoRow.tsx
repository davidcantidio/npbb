import {
  Box,
  Button,
  Chip,
  FormControl,
  IconButton,
  MenuItem,
  Select,
  Stack,
  TableCell,
  TableRow,
  Tooltip,
  Typography,
} from "@mui/material";
import QrCode2Icon from "@mui/icons-material/QrCode2";
import { Link as RouterLink } from "react-router-dom";

import { EventoListItem, StatusEvento } from "../../services/eventos";

const MS_PER_DAY = 1000 * 60 * 60 * 24;

function parseISODate(value?: string | null): Date | null {
  if (!value) return null;
  const [y, m, d] = value.split("-").map((part) => Number(part));
  if (!Number.isFinite(y) || !Number.isFinite(m) || !Number.isFinite(d)) return null;
  if (y < 1000 || m < 1 || m > 12 || d < 1 || d > 31) return null;
  const date = new Date(y, m - 1, d);
  if (Number.isNaN(date.getTime())) return null;
  if (date.getFullYear() !== y || date.getMonth() !== m - 1 || date.getDate() !== d) return null;
  return date;
}

function startOfToday(): Date {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), now.getDate());
}

function formatPtBrShort(date: Date): string {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  })
    .format(date)
    .replace(/\./g, "");
}

function pluralizeDay(n: number) {
  return n === 1 ? "dia" : "dias";
}

function formatCurrency(value?: string | number | null) {
  if (value == null || value === "") return "-";
  const numeric = typeof value === "number" ? value : Number(String(value).replace(",", "."));
  if (!Number.isFinite(numeric)) return String(value);
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(numeric);
}

function buildPeriodoInfo(start: Date, end: Date) {
  const today = startOfToday();
  const startTime = start.getTime();
  const endTime = end.getTime();
  const todayTime = today.getTime();

  const safeTotal = Math.max(1, endTime - startTime);

  if (todayTime < startTime) {
    const daysUntil = Math.max(0, Math.ceil((startTime - todayTime) / MS_PER_DAY));
    return {
      percentage: 0,
      statusText: `Início em ${daysUntil} ${pluralizeDay(daysUntil)}`,
      barColor: "grey.300",
      startLabel: formatPtBrShort(start),
      endLabel: formatPtBrShort(end),
    };
  }

  if (todayTime > endTime) {
    const daysSince = Math.max(0, Math.floor((todayTime - endTime) / MS_PER_DAY));
    return {
      percentage: 100,
      statusText: `Finalizado há ${daysSince} ${pluralizeDay(daysSince)}`,
      barColor: "grey.500",
      startLabel: formatPtBrShort(start),
      endLabel: formatPtBrShort(end),
    };
  }

  const elapsed = Math.max(0, todayTime - startTime);
  const percentage = Math.max(0, Math.min(100, (elapsed / safeTotal) * 100));
  const daysElapsed = Math.max(0, Math.floor(elapsed / MS_PER_DAY));
  const daysRemaining = Math.max(0, Math.ceil((endTime - todayTime) / MS_PER_DAY));

  return {
    percentage,
    statusText: `${daysElapsed} ${pluralizeDay(daysElapsed)} decorridos • ${daysRemaining} ${pluralizeDay(
      daysRemaining,
    )} restantes`,
    barColor: "success.main",
    startLabel: formatPtBrShort(start),
    endLabel: formatPtBrShort(end),
  };
}

function statusChipColor(nome?: string) {
  switch (String(nome || "").toLowerCase()) {
    case "previsto":
      return "default" as const;
    case "a confirmar":
      return "warning" as const;
    case "confirmado":
      return "info" as const;
    case "realizado":
      return "success" as const;
    case "cancelado":
      return "error" as const;
    default:
      return "default" as const;
  }
}

export type EventoRowProps = {
  item: EventoListItem;
  diretoriaLabel?: string;
  statuses?: StatusEvento[];
  statusUpdating?: boolean;
  onStatusChange?: (id: number, statusId: number) => void;
};

export function EventoRow({
  item,
  diretoriaLabel,
  statuses,
  statusUpdating,
  onStatusChange,
}: EventoRowProps) {
  const statusNome = statuses?.find((s) => s.id === item.status_id)?.nome;
  const statusLabel =
    statusNome || (typeof item.status_id === "number" ? `#${item.status_id}` : "-");
  const chipColor = statusChipColor(statusNome);

  const startIso = item.data_inicio_prevista || item.data_inicio_realizada || null;
  const endIso = item.data_fim_prevista || item.data_fim_realizada || startIso;
  const start = parseISODate(startIso);
  const end = parseISODate(endIso);
  const periodo = start && end ? buildPeriodoInfo(start, end) : null;

  return (
    <TableRow hover>
      <TableCell>
        {item.qr_code_url ? (
          <Tooltip title="Abrir QRCode">
            <IconButton
              component="a"
              href={item.qr_code_url}
              target="_blank"
              rel="noreferrer"
              size="small"
            >
              <QrCode2Icon fontSize="small" />
            </IconButton>
          </Tooltip>
        ) : (
          "-"
        )}
      </TableCell>
      <TableCell>
        <Button
          component={RouterLink}
          to={`/eventos/${item.id}`}
          variant="text"
          sx={{ textTransform: "none", fontWeight: 800, px: 0 }}
        >
          {item.nome}
        </Button>
      </TableCell>
      <TableCell>
        {periodo ? (
          <Stack spacing={0.5} sx={{ py: 0.5 }}>
            <Typography variant="body2" fontWeight={800}>
              {periodo.statusText}
            </Typography>
            <Box
              role="progressbar"
              aria-label={`Progresso do período do evento: ${periodo.statusText}. ${periodo.startLabel} → ${periodo.endLabel}`}
              aria-valuenow={Math.round(periodo.percentage)}
              aria-valuemin={0}
              aria-valuemax={100}
              sx={{
                height: 10,
                borderRadius: 1,
                overflow: "hidden",
                backgroundColor: "grey.200",
              }}
            >
              <Box
                sx={{
                  height: "100%",
                  width: `${periodo.percentage}%`,
                  backgroundColor: periodo.barColor,
                  transition: "width 180ms ease-out",
                }}
              />
            </Box>
            <Typography variant="caption" color="text.secondary">
              {periodo.startLabel} → {periodo.endLabel}
            </Typography>
          </Stack>
        ) : (
          <Typography variant="body2" color="text.secondary">
            -
          </Typography>
        )}
      </TableCell>
      <TableCell>
        {item.cidade} / {String(item.estado || "").toUpperCase()}
      </TableCell>
      <TableCell>{diretoriaLabel || "-"}</TableCell>
      <TableCell>{formatCurrency(item.investimento)}</TableCell>
      <TableCell>
        {statuses && statuses.length && onStatusChange ? (
          <FormControl size="small" fullWidth>
            <Select
              value={item.status_id}
              disabled={Boolean(statusUpdating)}
              onChange={(e) => onStatusChange(item.id, Number(e.target.value))}
              renderValue={() => <Chip label={statusLabel} color={chipColor} size="small" />}
              sx={{ "& .MuiSelect-select": { display: "flex", alignItems: "center" } }}
            >
              {statuses.map((s) => (
                <MenuItem key={s.id} value={s.id}>
                  <Chip label={s.nome} color={statusChipColor(s.nome)} size="small" />
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        ) : (
          <Chip label={statusLabel} color={chipColor} size="small" />
        )}
      </TableCell>
    </TableRow>
  );
}
