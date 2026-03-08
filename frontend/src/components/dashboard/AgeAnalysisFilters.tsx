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
  onChange,
  onClear,
}: AgeAnalysisFiltersProps) {
  const selectedEvento =
    eventOptions.find((option) => option.id === value.evento_id) ?? eventOptions[0] ?? null;

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
                options={eventOptions}
                disableClearable
                value={selectedEvento}
                loading={isLoadingEvents}
                loadingText="Carregando eventos..."
                noOptionsText="Nenhum evento encontrado"
                getOptionLabel={formatEventOptionLabel}
                isOptionEqualToValue={(option, selectedValue) => option.id === selectedValue.id}
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
                    helperText={
                      isLoadingEvents
                        ? "Carregando eventos disponiveis."
                        : "Use a busca para localizar um evento especifico."
                    }
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
                helperText={hasInvalidRange ? "A data fim deve ser maior ou igual a data inicio." : " "}
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
