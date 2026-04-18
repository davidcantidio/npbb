import {
  Alert,
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
import { listAgencias } from "../services/agencias";
import { createEvento, EventoRead } from "../services/eventos/core";
import { useAuth } from "../store/auth";

const UF_LIST = [
  "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO",
  "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
  "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
];

type FormState = {
  nome: string;
  data_inicio_prevista: string;
  data_fim_prevista: string;
  cidade: string;
  estado: string;
  agencia_id: string;
};

function buildEmptyForm(defaultAgenciaId = ""): FormState {
  return {
    nome: "",
    data_inicio_prevista: "",
    data_fim_prevista: "",
    cidade: "",
    estado: "",
    agencia_id: defaultAgenciaId,
  };
}

const AGENCIA_REQUIRED_MESSAGE = "Agencia responsavel e obrigatoria";

const isEndDateBeforeStartDate = (startDate: string, endDate: string) =>
  Boolean(startDate && endDate && endDate < startDate);

const toErrorMessage = (error: unknown, fallback: string) =>
  error instanceof Error && error.message.trim() ? error.message : fallback;

function resolveAgenciaHelperText(params: {
  fieldError?: string;
  loadError?: string | null;
  loading: boolean;
  hasOptions: boolean;
}) {
  const { fieldError, loadError, loading, hasOptions } = params;
  if (fieldError) return fieldError;
  if (loadError) return loadError;
  if (loading) return "Carregando agencias...";
  if (!hasOptions) return "Nenhuma agencia encontrada";
  return undefined;
}

const AGENCY_FIELD_DISABLED_HELPER = "Agencia definida pelo seu usuario";

const EMPTY_FORM_ERRORS: Partial<Record<keyof FormState, string>> = {};

const DEFAULT_AGENCIAS_LOAD_ERROR = "Nao foi possivel carregar as agencias.";

const REQUIRED_END_DATE_MESSAGE = "Data de fim e obrigatoria";

const END_DATE_RANGE_MESSAGE = "Data de fim deve ser maior ou igual a data de inicio";

const REQUIRED_START_DATE_MESSAGE = "Data e obrigatoria";

const REQUIRED_CITY_MESSAGE = "Cidade e obrigatoria";

const REQUIRED_STATE_MESSAGE = "Estado e obrigatorio";

const REQUIRED_NAME_MESSAGE = "Nome e obrigatorio";

const CREATE_EVENT_ERROR_MESSAGE = "Erro ao criar evento.";

const AGENCIA_LIST_LIMIT = 200;

const QUICK_CREATE_FLAG_VALUE = true;

const toAgenciaDraft = (agenciaId?: number | null) =>
  typeof agenciaId === "number" && Number.isFinite(agenciaId) ? String(agenciaId) : "";

type Props = {
  open: boolean;
  onClose: () => void;
  onCreated: (evento: EventoRead) => void;
};

export default function QuickCreateEventoModal({ open, onClose, onCreated }: Props) {
  const { token, user } = useAuth();
  const userAgenciaId = typeof user?.agencia_id === "number" ? user.agencia_id : null;
  const isAgencyUser = String(user?.tipo_usuario || "").toLowerCase() === "agencia" && userAgenciaId !== null;

  const [form, setForm] = useState<FormState>(() => buildEmptyForm(toAgenciaDraft(userAgenciaId)));
  const [errors, setErrors] = useState<Partial<Record<keyof FormState, string>>>(EMPTY_FORM_ERRORS);
  const [agencias, setAgencias] = useState<Array<{ id: number; nome: string }>>([]);
  const [loadingAgencias, setLoadingAgencias] = useState(false);
  const [agenciasLoadError, setAgenciasLoadError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAgencyUser || userAgenciaId === null) return;
    setForm((prev) => (prev.agencia_id ? prev : { ...prev, agencia_id: String(userAgenciaId) }));
  }, [isAgencyUser, userAgenciaId]);

  useEffect(() => {
    let cancelled = false;
    if (!open || isAgencyUser) return undefined;

    setLoadingAgencias(true);
    setAgenciasLoadError(null);

    listAgencias({ limit: AGENCIA_LIST_LIMIT })
      .then((items) => {
        if (cancelled) return;
        setAgencias(items.map((item) => ({ id: item.id, nome: item.nome })));
      })
      .catch((error) => {
        if (cancelled) return;
        setAgencias([]);
        setAgenciasLoadError(toErrorMessage(error, DEFAULT_AGENCIAS_LOAD_ERROR));
      })
      .finally(() => {
        if (cancelled) return;
        setLoadingAgencias(false);
      });

    return () => {
      cancelled = true;
    };
  }, [isAgencyUser, open]);

  const handleClose = () => {
    setForm(buildEmptyForm(toAgenciaDraft(userAgenciaId)));
    setErrors(EMPTY_FORM_ERRORS);
    setServerError(null);
    onClose();
  };

  const validate = (): boolean => {
    const next: typeof errors = {};
    if (!form.nome.trim()) next.nome = REQUIRED_NAME_MESSAGE;
    if (!form.data_inicio_prevista) next.data_inicio_prevista = REQUIRED_START_DATE_MESSAGE;
    if (!form.data_fim_prevista) next.data_fim_prevista = REQUIRED_END_DATE_MESSAGE;
    if (isEndDateBeforeStartDate(form.data_inicio_prevista, form.data_fim_prevista)) {
      next.data_fim_prevista = END_DATE_RANGE_MESSAGE;
    }
    if (!form.cidade.trim()) next.cidade = REQUIRED_CITY_MESSAGE;
    if (!form.estado) next.estado = REQUIRED_STATE_MESSAGE;
    if (!form.agencia_id) next.agencia_id = AGENCIA_REQUIRED_MESSAGE;
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
        data_fim_prevista: form.data_fim_prevista,
        cidade: form.cidade.trim(),
        estado: form.estado,
        agencia_id: Number(form.agencia_id),
        concorrencia: false,
        criar_ativacao_padrao_bb: QUICK_CREATE_FLAG_VALUE,
      });
      setForm(buildEmptyForm(toAgenciaDraft(userAgenciaId)));
      setErrors(EMPTY_FORM_ERRORS);
      onCreated(created);
    } catch (err) {
      const msg = toErrorMessage(err, CREATE_EVENT_ERROR_MESSAGE);
      setServerError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const set = (field: keyof FormState) => (value: string) => {
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
              onChange={(event) => set("nome")(event.target.value)}
              error={Boolean(errors.nome)}
              helperText={errors.nome}
              required
              fullWidth
              autoFocus
            />
            <TextField
              label="Data de inicio"
              type="date"
              value={form.data_inicio_prevista}
              onChange={(event) => set("data_inicio_prevista")(event.target.value)}
              InputLabelProps={{ shrink: true }}
              error={Boolean(errors.data_inicio_prevista)}
              helperText={errors.data_inicio_prevista}
              required
              fullWidth
            />
            <TextField
              label="Data de fim"
              type="date"
              value={form.data_fim_prevista}
              onChange={(event) => set("data_fim_prevista")(event.target.value)}
              InputLabelProps={{ shrink: true }}
              error={Boolean(errors.data_fim_prevista)}
              helperText={errors.data_fim_prevista}
              required
              fullWidth
            />
            <TextField
              label="Cidade"
              value={form.cidade}
              onChange={(event) => set("cidade")(event.target.value)}
              error={Boolean(errors.cidade)}
              helperText={errors.cidade}
              required
              fullWidth
            />
            <TextField
              select
              label="Estado (UF)"
              value={form.estado}
              onChange={(event) => set("estado")(event.target.value)}
              error={Boolean(errors.estado)}
              helperText={errors.estado}
              required
              fullWidth
            >
              {UF_LIST.map((uf) => (
                <MenuItem key={uf} value={uf}>
                  {uf}
                </MenuItem>
              ))}
            </TextField>
            {isAgencyUser ? (
              <TextField
                label="Agencia responsavel"
                value={form.agencia_id ? `#${form.agencia_id}` : ""}
                disabled
                helperText={AGENCY_FIELD_DISABLED_HELPER}
                required
                fullWidth
              />
            ) : (
              <TextField
                select
                label="Agencia responsavel"
                value={form.agencia_id}
                onChange={(event) => set("agencia_id")(event.target.value)}
                error={Boolean(errors.agencia_id) || Boolean(agenciasLoadError)}
                helperText={resolveAgenciaHelperText({
                  fieldError: errors.agencia_id,
                  loadError: agenciasLoadError,
                  loading: loadingAgencias,
                  hasOptions: agencias.length > 0,
                })}
                required
                fullWidth
                disabled={loadingAgencias || agencias.length === 0}
              >
                <MenuItem value="">Selecione uma agencia</MenuItem>
                {agencias.map((agencia) => (
                  <MenuItem key={agencia.id} value={String(agencia.id)}>
                    {agencia.nome}
                  </MenuItem>
                ))}
              </TextField>
            )}
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
