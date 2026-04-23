import ClearRoundedIcon from "@mui/icons-material/ClearRounded";
import {
  Autocomplete,
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import type { ReferenciaEvento } from "../../services/leads_import";
import type { AgeAnalysisFilterFormValues } from "../../types/dashboard";

export const ALL_EVENTS_OPTION_ID = -1;

type AgeAnalysisFiltersProps = {
  value: AgeAnalysisFilterFormValues;
  eventOptions: ReferenciaEvento[];
  isLoadingEvents: boolean;
  hasInvalidRange: boolean;
  invalidEventoOption?: ReferenciaEvento | null;
  onChange: (nextValue: AgeAnalysisFilterFormValues) => void;
  onClear: () => void;
};

function formatEventOptionLabel(option: ReferenciaEvento) {
  if (!option.data_inicio_prevista) return option.nome;
  return `${option.nome} • ${option.data_inicio_prevista}`;
}

export function AgeAnalysisFilters({
  value,
  eventOptions,
  isLoadingEvents,
  hasInvalidRange,
  invalidEventoOption = null,
  onChange,
  onClear,
}: AgeAnalysisFiltersProps) {
  const fallbackEvento: ReferenciaEvento =
    eventOptions[0] ?? invalidEventoOption ?? { id: ALL_EVENTS_OPTION_ID, nome: "Todos os eventos", data_inicio_prevista: null };
  const hasExplicitEvento = typeof value.evento_id === "number";
  const selectedEvento = hasExplicitEvento
    ? eventOptions.find((option) => option.id === value.evento_id) ?? invalidEventoOption ?? fallbackEvento
    : fallbackEvento;
  const resolvedEventOptions =
    invalidEventoOption && !eventOptions.some((option) => option.id === invalidEventoOption.id)
      ? [invalidEventoOption, ...eventOptions]
      : eventOptions;
  const eventoHelperText = invalidEventoOption
    ? "O evento do filtro nao esta mais disponivel na referencia atual."
    : isLoadingEvents
      ? "Carregando eventos disponiveis."
      : "Use a busca para localizar um evento especifico.";

  return (
    <Card variant="outlined">
      <CardContent>
        <Stack spacing={2}>
          <Box>
            <Typography variant="subtitle1" fontWeight={800}>
              Filtros
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Refine o periodo e o evento para atualizar os indicadores da analise etaria.
            </Typography>
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Autocomplete
                options={resolvedEventOptions}
                disableClearable
                value={selectedEvento}
                loading={isLoadingEvents}
                loadingText="Carregando eventos..."
                noOptionsText="Nenhum evento encontrado"
                getOptionLabel={formatEventOptionLabel}
                isOptionEqualToValue={(option, selectedValue) => option.id === selectedValue?.id}
                onChange={(_, selectedValue) =>
                  onChange({
                    ...value,
                    evento_id:
                      selectedValue?.id === ALL_EVENTS_OPTION_ID ? null : selectedValue?.id ?? null,
                  })
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Evento"
                    placeholder="Todos os eventos"
                    error={Boolean(invalidEventoOption)}
                    helperText={eventoHelperText}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <TextField
                label="Data inicio"
                type="date"
                fullWidth
                value={value.data_inicio}
                onChange={(event) =>
                  onChange({
                    ...value,
                    data_inicio: event.target.value,
                  })
                }
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <TextField
                label="Data fim"
                type="date"
                fullWidth
                value={value.data_fim}
                onChange={(event) =>
                  onChange({
                    ...value,
                    data_fim: event.target.value,
                  })
                }
                error={hasInvalidRange}
                helperText={
                  hasInvalidRange
                    ? "A data fim deve ser maior ou igual a data inicio."
                    : " "
                }
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>

          <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
            <Button variant="outlined" startIcon={<ClearRoundedIcon />} onClick={onClear}>
              Limpar filtros
            </Button>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}
