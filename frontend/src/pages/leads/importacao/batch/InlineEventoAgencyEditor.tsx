import { Button, CircularProgress, MenuItem, Stack, TextField, Typography } from "@mui/material";
import { useEffect, useState } from "react";

import { Agencia } from "../../../../services/agencias";
import { toApiErrorMessage } from "../../../../services/http";

type Props = {
  agencias: Agencia[];
  currentAgenciaId?: number | null;
  loading: boolean;
  loadError: string | null;
  onSave: (agenciaId: number) => Promise<void>;
};

export default function InlineEventoAgencyEditor({
  agencias,
  currentAgenciaId,
  loading,
  loadError,
  onSave,
}: Props) {
  const [selectedAgenciaId, setSelectedAgenciaId] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [hasExplicitSelection, setHasExplicitSelection] = useState(false);
  const hasAgencias = agencias.length > 0;

  useEffect(() => {
    if (typeof currentAgenciaId === "number" && Number.isFinite(currentAgenciaId)) {
      setSelectedAgenciaId(String(currentAgenciaId));
      setHasExplicitSelection(true);
      return;
    }
    setSelectedAgenciaId("");
    setHasExplicitSelection(false);
  }, [agencias, currentAgenciaId]);

  const helperText =
    saveError ??
    loadError ??
    (!hasAgencias && loading
      ? "Carregando agencias..."
      : !hasAgencias
        ? "Nenhuma agencia encontrada"
        : !hasExplicitSelection
          ? "Selecione a agencia para vincular o evento."
          : undefined);

  return (
    <Stack spacing={1}>
      <Typography variant="caption" color="text.secondary">
        Evento sem agencia. Vincule a agencia para liberar a importacao por ativacao.
      </Typography>
      <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
        <TextField
          select
          label="Agencia"
          size="small"
          value={selectedAgenciaId}
          onChange={(event) => {
            setSelectedAgenciaId(event.target.value);
            setHasExplicitSelection(Boolean(event.target.value));
            if (saveError) {
              setSaveError(null);
            }
          }}
          disabled={!hasAgencias || saving}
          error={Boolean(loadError || saveError)}
          helperText={helperText}
          sx={{ minWidth: 220 }}
        >
          <MenuItem value="">
            <em>Selecione a agencia</em>
          </MenuItem>
          {agencias.map((agencia) => (
            <MenuItem key={agencia.id} value={agencia.id}>
              {agencia.nome}
            </MenuItem>
          ))}
        </TextField>
        <Button
          variant="outlined"
          disabled={!selectedAgenciaId || !hasAgencias || saving || !hasExplicitSelection}
          onClick={async () => {
            setSaving(true);
            setSaveError(null);
            try {
              await onSave(Number(selectedAgenciaId));
            } catch (error) {
              setSaveError(toApiErrorMessage(error, "Falha ao salvar a agencia do evento."));
            } finally {
              setSaving(false);
            }
          }}
        >
          {saving ? <CircularProgress size={16} color="inherit" /> : "Salvar agencia"}
        </Button>
      </Stack>
    </Stack>
  );
}
