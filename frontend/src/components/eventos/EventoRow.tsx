import { useEffect, useState } from "react";
import {
  Box,
  Button,
  Chip,
  FormControl,
  InputAdornment,
  MenuItem,
  Select,
  Stack,
  TableCell,
  TableRow,
  Skeleton,
  Typography,
  TextField,
} from "@mui/material";
import { Link as RouterLink, useNavigate } from "react-router-dom";

import { Agencia } from "../../services/agencias";
import { Diretoria, EventoListItem, EventoUpdate, StatusEvento } from "../../services/eventos";
import { DataHealthBar } from "./DataHealthBar";
import { EventDateTimeline } from "./EventDateTimeline";

function formatCurrency(value?: string | number | null) {
  if (value == null || value === "") return "-";
  const numeric = typeof value === "number" ? value : Number(String(value).replace(",", "."));
  if (!Number.isFinite(numeric)) return String(value);
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(numeric);
}

function parseCurrencyInput(raw: string) {
  const trimmed = raw.trim();
  if (!trimmed) return null;
  const normalized = trimmed.includes(",")
    ? trimmed.replace(/\./g, "").replace(",", ".")
    : trimmed.replace(/\s/g, "");
  const numeric = Number(normalized);
  return Number.isFinite(numeric) ? numeric : null;
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
  agenciaLabel?: string;
  agencias?: Agencia[];
  diretoriaLabel?: string;
  diretorias?: Diretoria[];
  statuses?: StatusEvento[];
  statusUpdating?: boolean;
  inlineUpdating?: boolean;
  onStatusChange?: (id: number, statusId: number) => void;
  onInlineUpdate?: (id: number, patch: EventoUpdate) => Promise<unknown>;
};

export function EventoRow({
  item,
  agenciaLabel,
  agencias,
  diretoriaLabel,
  diretorias,
  statuses,
  statusUpdating,
  inlineUpdating,
  onStatusChange,
  onInlineUpdate,
}: EventoRowProps) {
  const navigate = useNavigate();
  const statusNome = statuses?.find((s) => s.id === item.status_id)?.nome;
  const statusLabel =
    statusNome || (typeof item.status_id === "number" ? `#${item.status_id}` : "-");
  const chipColor = statusChipColor(statusNome);

  const startIso = item.data_inicio_prevista || item.data_inicio_realizada || null;
  const endIso = item.data_fim_prevista || item.data_fim_realizada || null;
  const missingFields = item.data_health?.missing_fields ?? [];
  const focusField = missingFields[0];
  const editParams = new URLSearchParams();
  if (missingFields.length) editParams.set("missing", missingFields.join(","));
  if (focusField) editParams.set("focus", focusField);
  const editUrl = `/eventos/${item.id}/editar${editParams.toString() ? `?${editParams}` : ""}`;
  const hasAgencia = typeof item.agencia_id === "number" && Number.isFinite(item.agencia_id);
  const hasDiretoria = typeof item.diretoria_id === "number" && Number.isFinite(item.diretoria_id);
  const hasInvestimento =
    item.investimento !== null &&
    item.investimento !== undefined &&
    String(item.investimento).trim() !== "";
  const [agenciaDraft, setAgenciaDraft] = useState("");
  const [diretoriaDraft, setDiretoriaDraft] = useState("");
  const [investimentoDraft, setInvestimentoDraft] = useState("");
  const [investimentoEditing, setInvestimentoEditing] = useState(false);
  const [investimentoError, setInvestimentoError] = useState("");
  const fieldFontSize = "0.875rem";
  const controlHeight = 34;
  const controlRadius = 10;

  useEffect(() => {
    if (!hasAgencia) {
      setAgenciaDraft("");
    }
  }, [hasAgencia]);

  useEffect(() => {
    if (!hasDiretoria) {
      setDiretoriaDraft("");
    }
  }, [hasDiretoria]);

  useEffect(() => {
    if (!investimentoEditing) {
      setInvestimentoDraft(item.investimento != null ? String(item.investimento) : "");
      setInvestimentoError("");
    }
  }, [item.investimento, investimentoEditing]);

  const agenciaSelectDisabled = Boolean(inlineUpdating) || !agencias?.length || !onInlineUpdate;
  const diretoriaSelectDisabled = Boolean(inlineUpdating) || !diretorias?.length || !onInlineUpdate;

  const handleAgenciaChange = async (value: number) => {
    if (!onInlineUpdate || !Number.isFinite(value)) return;
    setAgenciaDraft(String(value));
    try {
      await onInlineUpdate(item.id, { agencia_id: value });
    } catch {
      setAgenciaDraft("");
    }
  };

  const handleDiretoriaChange = async (value: number) => {
    if (!onInlineUpdate || !Number.isFinite(value)) return;
    setDiretoriaDraft(String(value));
    try {
      await onInlineUpdate(item.id, { diretoria_id: value });
    } catch {
      setDiretoriaDraft("");
    }
  };

  const handleInvestimentoSave = async () => {
    if (!onInlineUpdate) return;
    const numeric = parseCurrencyInput(investimentoDraft);
    if (numeric == null || numeric < 0) {
      setInvestimentoError("Valor inválido");
      return;
    }
    try {
      setInvestimentoError("");
      await onInlineUpdate(item.id, { investimento: numeric });
      setInvestimentoEditing(false);
    } catch {
      setInvestimentoError("Erro ao salvar");
    }
  };

  return (
    <TableRow hover>
      <TableCell sx={{ width: 180, fontSize: fieldFontSize }}>
        {hasAgencia || !agencias?.length || !onInlineUpdate ? (
          <Typography variant="body2" sx={{ fontSize: "inherit" }}>
            {agenciaLabel || "-"}
          </Typography>
        ) : (
          <FormControl
            size="small"
            fullWidth
            sx={{ "& .MuiOutlinedInput-root": { height: controlHeight, borderRadius: controlRadius } }}
          >
            <Select
              value={agenciaDraft}
              displayEmpty
              disabled={agenciaSelectDisabled}
              onChange={(e) => handleAgenciaChange(Number(e.target.value))}
              renderValue={(value) => {
                if (!value) {
                  return (
                    <Typography color="text.secondary" sx={{ fontSize: "inherit" }}>
                      Selecionar
                    </Typography>
                  );
                }
                const selected = agencias.find((a) => String(a.id) === String(value));
                return selected?.nome ?? String(value);
              }}
              sx={{
                fontSize: "inherit",
                "& .MuiSelect-select": {
                  display: "flex",
                  alignItems: "center",
                  height: controlHeight,
                  paddingTop: 0,
                  paddingBottom: 0,
                  fontSize: "inherit",
                },
                "& .MuiOutlinedInput-notchedOutline": { borderRadius: controlRadius },
              }}
            >
              <MenuItem value="" disabled sx={{ fontSize: fieldFontSize }}>
                Selecionar
              </MenuItem>
              {agencias.map((ag) => (
                <MenuItem key={ag.id} value={ag.id} sx={{ fontSize: fieldFontSize }}>
                  {ag.nome}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}
      </TableCell>
      <TableCell sx={{ verticalAlign: "top", width: 260 }}>
        <Stack spacing={0.2}>
          <Button
            component={RouterLink}
            to={`/eventos/${item.id}`}
            variant="text"
            disableRipple
            sx={{
              textTransform: "none",
              fontWeight: 800,
              px: 0,
              py: 0,
              minHeight: "auto",
              justifyContent: "flex-start",
              fontSize: "1rem",
              lineHeight: 1.1,
            }}
          >
            {item.nome}
          </Button>
          {item.data_health ? (
            <DataHealthBar
              score={item.data_health.score}
              band={(item.data_health.band as any) || "na"}
              missing_preview={item.data_health.missing_fields}
              onClick={() => navigate(editUrl)}
              onViewAll={() => navigate(editUrl)}
            />
          ) : (
            <Box sx={{ maxWidth: 220 }}>
              <Skeleton variant="text" width={120} height={16} />
              <Skeleton variant="rounded" width="100%" height={8} />
            </Box>
          )}
        </Stack>
      </TableCell>
      <TableCell sx={{ width: 224, verticalAlign: "top" }}>
        <EventDateTimeline startDate={startIso} endDate={endIso} />
      </TableCell>
      <TableCell sx={{ fontSize: fieldFontSize, width: 175 }}>
        {item.cidade} / {String(item.estado || "").toUpperCase()}
      </TableCell>
      <TableCell sx={{ fontSize: fieldFontSize, width: 160 }}>
        {hasDiretoria || !diretorias?.length || !onInlineUpdate ? (
          <Typography variant="body2" sx={{ fontSize: "inherit" }}>
            {diretoriaLabel || "-"}
          </Typography>
        ) : (
          <FormControl
            size="small"
            fullWidth
            sx={{ "& .MuiOutlinedInput-root": { height: controlHeight, borderRadius: controlRadius } }}
          >
            <Select
              value={diretoriaDraft}
              displayEmpty
              disabled={diretoriaSelectDisabled}
              onChange={(e) => handleDiretoriaChange(Number(e.target.value))}
              renderValue={(value) => {
                if (!value) {
                  return (
                    <Typography color="text.secondary" sx={{ fontSize: "inherit" }}>
                      Selecionar
                    </Typography>
                  );
                }
                const selected = diretorias.find((d) => String(d.id) === String(value));
                return selected?.nome ?? String(value);
              }}
              sx={{
                fontSize: "inherit",
                "& .MuiSelect-select": {
                  display: "flex",
                  alignItems: "center",
                  height: controlHeight,
                  paddingTop: 0,
                  paddingBottom: 0,
                  fontSize: "inherit",
                },
                "& .MuiOutlinedInput-notchedOutline": { borderRadius: controlRadius },
              }}
            >
              <MenuItem value="" disabled sx={{ fontSize: fieldFontSize }}>
                Selecionar
              </MenuItem>
              {diretorias.map((dir) => (
                <MenuItem key={dir.id} value={dir.id} sx={{ fontSize: fieldFontSize }}>
                  {dir.nome}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}
      </TableCell>
      <TableCell sx={{ fontSize: fieldFontSize, width: 136 }}>
        {hasInvestimento ? (
          <Typography variant="body2" sx={{ fontSize: "inherit" }}>
            {formatCurrency(item.investimento)}
          </Typography>
        ) : !onInlineUpdate ? (
          <Typography variant="body2" sx={{ fontSize: "inherit" }}>
            -
          </Typography>
        ) : investimentoEditing ? (
          <Stack spacing={0.5}>
            <Stack direction="row" spacing={1} alignItems="center">
              <TextField
                size="small"
                value={investimentoDraft}
                onChange={(e) => setInvestimentoDraft(e.target.value)}
                placeholder="0,00"
                error={Boolean(investimentoError)}
                disabled={Boolean(inlineUpdating)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleInvestimentoSave();
                  }
                  if (e.key === "Escape") {
                    setInvestimentoEditing(false);
                  }
                }}
                InputProps={{
                  startAdornment: <InputAdornment position="start">R$</InputAdornment>,
                }}
                sx={{
                  minWidth: 120,
                  fontSize: "inherit",
                  "& .MuiOutlinedInput-root": { height: controlHeight, borderRadius: controlRadius },
                  "& .MuiOutlinedInput-input": { paddingTop: 0, paddingBottom: 0 },
                }}
              />
              <Button
                size="small"
                variant="contained"
                onClick={handleInvestimentoSave}
                disabled={Boolean(inlineUpdating)}
                sx={{
                  textTransform: "none",
                  fontSize: "inherit",
                  height: controlHeight,
                  minHeight: controlHeight,
                  borderRadius: controlRadius,
                }}
              >
                Salvar
              </Button>
              <Button
                size="small"
                variant="text"
                onClick={() => {
                  setInvestimentoEditing(false);
                  setInvestimentoError("");
                }}
                sx={{
                  textTransform: "none",
                  fontSize: "inherit",
                  height: controlHeight,
                  minHeight: controlHeight,
                  borderRadius: controlRadius,
                }}
              >
                Cancelar
              </Button>
            </Stack>
            {investimentoError ? (
              <Typography variant="caption" color="error">
                {investimentoError}
              </Typography>
            ) : null}
          </Stack>
        ) : (
          <Button
            size="small"
            variant="outlined"
            onClick={() => setInvestimentoEditing(true)}
            disabled={Boolean(inlineUpdating)}
            sx={{
              textTransform: "none",
              fontSize: "inherit",
              height: controlHeight,
              minHeight: controlHeight,
              borderRadius: controlRadius,
            }}
          >
            Adicionar
          </Button>
        )}
      </TableCell>
      <TableCell sx={{ fontSize: fieldFontSize, width: 140 }}>
        {statuses && statuses.length && onStatusChange ? (
          <FormControl
            size="small"
            fullWidth
            sx={{ "& .MuiOutlinedInput-root": { height: controlHeight, borderRadius: controlRadius } }}
          >
            <Select
              value={item.status_id}
              disabled={Boolean(statusUpdating)}
              onChange={(e) => onStatusChange(item.id, Number(e.target.value))}
              renderValue={() => (
                <Chip
                  label={statusLabel}
                  color={chipColor}
                  size="small"
                  sx={{ fontSize: "inherit", "& .MuiChip-label": { fontSize: "inherit" } }}
                />
              )}
              sx={{
                fontSize: "inherit",
                "& .MuiSelect-select": {
                  display: "flex",
                  alignItems: "center",
                  height: controlHeight,
                  paddingTop: 0,
                  paddingBottom: 0,
                  fontSize: "inherit",
                },
                "& .MuiOutlinedInput-notchedOutline": { borderRadius: controlRadius },
              }}
            >
              {statuses.map((s) => (
                <MenuItem key={s.id} value={s.id}>
                  <Chip
                    label={s.nome}
                    color={statusChipColor(s.nome)}
                    size="small"
                    sx={{ fontSize: "inherit", "& .MuiChip-label": { fontSize: "inherit" } }}
                  />
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        ) : (
          <Chip
            label={statusLabel}
            color={chipColor}
            size="small"
            sx={{ fontSize: "inherit", "& .MuiChip-label": { fontSize: "inherit" } }}
          />
        )}
      </TableCell>
    </TableRow>
  );
}
