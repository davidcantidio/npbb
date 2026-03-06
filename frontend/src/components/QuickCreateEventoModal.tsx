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
  MenuItem,
  Stack,
  TextField,
} from "@mui/material";
import { useEffect, useState } from "react";
import { createEvento, Diretoria, EventoRead, listDiretorias } from "../services/eventos/core";
import { useAuth } from "../store/auth";

const UF_LIST = [
  "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO",
  "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
  "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
];

type FormState = {
  nome: string;
  data_inicio_prevista: string;
  cidade: string;
  estado: string;
  diretoria_id: number | "";
};

const EMPTY_FORM: FormState = {
  nome: "",
  data_inicio_prevista: "",
  cidade: "",
  estado: "",
  diretoria_id: "",
};

type Props = {
  open: boolean;
  onClose: () => void;
  /** Called with the created evento on success so parent can auto-select it. */
  onCreated: (evento: EventoRead) => void;
};

/**
 * Minimal quick-create modal for an Evento.
 * Designed to be triggered from the mapping flow when no event is found.
 */
export default function QuickCreateEventoModal({ open, onClose, onCreated }: Props) {
  const { token } = useAuth();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [errors, setErrors] = useState<Partial<Record<keyof FormState, string>>>({});
  const [diretorias, setDiretorias] = useState<Diretoria[]>([]);
  const [loadingDiretorias, setLoadingDiretorias] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  useEffect(() => {
    if (!open || !token) return;
    setLoadingDiretorias(true);
    listDiretorias(token)
      .then(setDiretorias)
      .catch(() => setDiretorias([]))
      .finally(() => setLoadingDiretorias(false));
  }, [open, token]);

  const handleClose = () => {
    setForm(EMPTY_FORM);
    setErrors({});
    setServerError(null);
    onClose();
  };

  const validate = (): boolean => {
    const next: typeof errors = {};
    if (!form.nome.trim()) next.nome = "Nome é obrigatório";
    if (!form.data_inicio_prevista) next.data_inicio_prevista = "Data é obrigatória";
    if (!form.cidade.trim()) next.cidade = "Cidade é obrigatória";
    if (!form.estado) next.estado = "Estado é obrigatório";
    if (form.diretoria_id === "") next.diretoria_id = "Diretoria é obrigatória";
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSave = async () => {
    if (!validate() || !token) return;
    setSubmitting(true);
    setServerError(null);
    try {
      const created = await createEvento(token, {
        nome: form.nome.trim(),
        data_inicio_prevista: form.data_inicio_prevista,
        cidade: form.cidade.trim(),
        estado: form.estado,
        diretoria_id: Number(form.diretoria_id),
        concorrencia: false,
      });
      setForm(EMPTY_FORM);
      setErrors({});
      onCreated(created);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Erro ao criar evento.";
      setServerError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const set = (field: keyof FormState) => (value: string | number) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Criar evento rapidamente</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 1 }}>
          {serverError ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              {serverError}
            </Alert>
          ) : null}
          <Stack spacing={2}>
            <TextField
              label="Nome do evento"
              value={form.nome}
              onChange={(e) => set("nome")(e.target.value)}
              error={Boolean(errors.nome)}
              helperText={errors.nome}
              required
              fullWidth
              autoFocus
            />
            <TextField
              label="Data de início"
              type="date"
              value={form.data_inicio_prevista}
              onChange={(e) => set("data_inicio_prevista")(e.target.value)}
              InputLabelProps={{ shrink: true }}
              error={Boolean(errors.data_inicio_prevista)}
              helperText={errors.data_inicio_prevista}
              required
              fullWidth
            />
            <TextField
              label="Cidade"
              value={form.cidade}
              onChange={(e) => set("cidade")(e.target.value)}
              error={Boolean(errors.cidade)}
              helperText={errors.cidade}
              required
              fullWidth
            />
            <Autocomplete
              options={UF_LIST}
              value={form.estado || null}
              onChange={(_, v) => set("estado")(v ?? "")}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Estado (UF)"
                  required
                  error={Boolean(errors.estado)}
                  helperText={errors.estado}
                />
              )}
            />
            <TextField
              select
              label="Diretoria"
              value={form.diretoria_id}
              onChange={(e) => set("diretoria_id")(e.target.value)}
              error={Boolean(errors.diretoria_id)}
              helperText={errors.diretoria_id ?? (loadingDiretorias ? "Carregando..." : undefined)}
              required
              fullWidth
              disabled={loadingDiretorias}
            >
              {loadingDiretorias ? (
                <MenuItem disabled>
                  <CircularProgress size={14} sx={{ mr: 1 }} /> Carregando...
                </MenuItem>
              ) : null}
              {diretorias.map((d) => (
                <MenuItem key={d.id} value={d.id}>
                  {d.nome}
                </MenuItem>
              ))}
            </TextField>
          </Stack>
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={handleClose} disabled={submitting}>
          Cancelar
        </Button>
        <Button
          variant="contained"
          onClick={handleSave}
          disabled={submitting}
          startIcon={submitting ? <CircularProgress size={16} color="inherit" /> : null}
        >
          Salvar
        </Button>
      </DialogActions>
    </Dialog>
  );
}
