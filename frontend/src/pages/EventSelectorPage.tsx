import { useCallback, useEffect, useState } from "react";
import {
  Alert,
  Autocomplete,
  Box,
  CircularProgress,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useNavigate } from "react-router-dom";

import EventWizardPageShell from "../components/eventos/EventWizardPageShell";
import { useAuth } from "../store/auth";
import { listEventos, type EventoListItem } from "../services/eventos";

const SECTION_LABELS: Record<string, string> = {
  editar: "Dados do evento",
  "formulario-lead": "Landing Page",
  gamificacao: "Gamificação",
  ativacoes: "Ativações",
  questionario: "Questionário",
};

type EventSelectorPageProps = {
  section: "editar" | "formulario-lead" | "gamificacao" | "ativacoes" | "questionario";
};

export default function EventSelectorPage({ section }: EventSelectorPageProps) {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [eventos, setEventos] = useState<EventoListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<EventoListItem | null>(null);

  const loadEventos = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const { items } = await listEventos(token, { limit: 200 });
      setEventos(items);
    } catch (err: unknown) {
      const msg =
        err && typeof err === "object" && "message" in err
          ? String((err as { message: unknown }).message)
          : "Erro ao carregar eventos.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadEventos();
  }, [loadEventos]);

  const handleSelect = (evento: EventoListItem | null) => {
    setSelected(evento);
    if (evento) {
      navigate(`/eventos/${evento.id}/${section}`, { replace: true });
    }
  };

  const sectionLabel = SECTION_LABELS[section] ?? section;

  return (
    <EventWizardPageShell width="regular" testId="event-selector-page">
      <Stack spacing={2}>
        <Box>
          <Typography variant="h4" fontWeight={800}>
            {sectionLabel}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Selecione um evento para configurar a seção {sectionLabel.toLowerCase()}.
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" variant="filled" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
          {loading ? (
            <Stack direction="row" spacing={1} alignItems="center">
              <CircularProgress size={22} />
              <Typography variant="body2" color="text.secondary">
                Carregando eventos...
              </Typography>
            </Stack>
          ) : eventos.length === 0 ? (
            <Alert severity="info">
              Nenhum evento encontrado. Crie um evento primeiro em Lista de eventos.
            </Alert>
          ) : (
            <Autocomplete
              options={eventos}
              getOptionLabel={(opt) => `${opt.nome} (#${opt.id})`}
              value={selected}
              onChange={(_, value) => handleSelect(value)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Selecionar evento"
                  placeholder="Digite ou selecione um evento"
                />
              )}
              isOptionEqualToValue={(opt, val) => opt.id === val.id}
            />
          )}
        </Paper>
      </Stack>
    </EventWizardPageShell>
  );
}
