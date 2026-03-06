import {
  Alert,
  Autocomplete,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup,
  TextField,
} from "@mui/material";
import { useEffect, useState } from "react";
import { listReferenciaEventos, ReferenciaEvento } from "../services/leads_import";
import { exportLeadsGold, triggerBlobDownload } from "../services/leads_export";
import { formatEventoLabel } from "../utils/formatters";
import { useAuth } from "../store/auth";

type Props = {
  open: boolean;
  onClose: () => void;
  /** Called when export completes successfully (for showing a success toast). */
  onSuccess?: () => void;
  /** Called when HTTP 204 is returned (no leads found). */
  onEmpty?: () => void;
};

const TODOS_OPTION: ReferenciaEvento = {
  id: -1,
  nome: "Todos os eventos",
  data_inicio_prevista: null,
};

/**
 * Modal for exporting Gold-stage leads from the Dashboard.
 * Allows selecting a specific event (or all) and the file format.
 */
export default function ExportGoldModal({ open, onClose, onSuccess, onEmpty }: Props) {
  const { token } = useAuth();

  const [eventos, setEventos] = useState<ReferenciaEvento[]>([]);
  const [loadingEventos, setLoadingEventos] = useState(false);
  const [selectedEvento, setSelectedEvento] = useState<ReferenciaEvento>(TODOS_OPTION);
  const [formato, setFormato] = useState<"xlsx" | "csv">("xlsx");
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open || !token) return;
    setLoadingEventos(true);
    listReferenciaEventos(token)
      .then((items) => setEventos([TODOS_OPTION, ...items]))
      .catch(() => setEventos([TODOS_OPTION]))
      .finally(() => setLoadingEventos(false));
  }, [open, token]);

  const handleClose = () => {
    setError(null);
    onClose();
  };

  const handleExport = async () => {
    if (!token) return;
    setExporting(true);
    setError(null);
    try {
      const eventoId = selectedEvento.id === -1 ? null : selectedEvento.id;
      const result = await exportLeadsGold(token, { evento_id: eventoId, formato });

      if (result === null) {
        onEmpty?.();
        return;
      }

      triggerBlobDownload(result.blob, result.filename);
      onSuccess?.();
      handleClose();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Erro ao exportar leads.";
      setError(msg);
    } finally {
      setExporting(false);
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Exportar Leads Ouro</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 1 }}>
          {error ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          ) : null}
          <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
            <Autocomplete<ReferenciaEvento, false, true>
              options={eventos}
              loading={loadingEventos}
              disableClearable
              getOptionLabel={(ev) =>
                ev.id === -1 ? ev.nome : formatEventoLabel(ev.nome, ev.data_inicio_prevista)
              }
              isOptionEqualToValue={(opt, val) => opt.id === val.id}
              value={selectedEvento}
              onChange={(_, v) => setSelectedEvento(v)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Evento"
                  helperText={loadingEventos ? "Carregando eventos..." : undefined}
                />
              )}
            />

            <FormControl>
              <FormLabel>Formato</FormLabel>
              <RadioGroup
                row
                value={formato}
                onChange={(e) => setFormato(e.target.value as "xlsx" | "csv")}
              >
                <FormControlLabel value="xlsx" control={<Radio />} label=".xlsx (Excel)" />
                <FormControlLabel value="csv" control={<Radio />} label=".csv (separador ;)" />
              </RadioGroup>
            </FormControl>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={handleClose} disabled={exporting}>
          Cancelar
        </Button>
        <Button
          variant="contained"
          onClick={handleExport}
          disabled={exporting || loadingEventos}
          startIcon={exporting ? <CircularProgress size={16} color="inherit" /> : null}
        >
          Exportar
        </Button>
      </DialogActions>
    </Dialog>
  );
}
