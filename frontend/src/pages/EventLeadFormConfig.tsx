import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Checkbox,
  CircularProgress,
  FormControlLabel,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { Link as RouterLink, useParams } from "react-router-dom";

import {
  getEventoFormConfig,
  getFormularioCamposPossiveis,
  listFormularioTemplates,
  type EventoFormConfig,
  type FormularioTemplate,
} from "../services/eventos";
import { useAuth } from "../store/auth";

export default function EventLeadFormConfig() {
  const { id } = useParams();
  const eventoId = Number(id);
  const { token } = useAuth();

  const [config, setConfig] = useState<EventoFormConfig | null>(null);
  const [camposPossiveis, setCamposPossiveis] = useState<string[]>([]);
  const [camposAtivos, setCamposAtivos] = useState<Set<string>>(() => new Set());
  const [templates, setTemplates] = useState<FormularioTemplate[]>([]);
  const [templateId, setTemplateId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedTemplate = useMemo(() => {
    if (templateId == null) return null;
    return templates.find((t) => t.id === templateId) ?? null;
  }, [templates, templateId]);

  const camposPossiveisUniq = useMemo(() => {
    const seen = new Set<string>();
    const items: string[] = [];
    for (const nome of camposPossiveis) {
      const normalized = String(nome || "").trim();
      if (!normalized) continue;
      if (seen.has(normalized.toLowerCase())) continue;
      seen.add(normalized.toLowerCase());
      items.push(normalized);
    }
    return items;
  }, [camposPossiveis]);

  const toggleCampo = useCallback((nome: string) => {
    setCamposAtivos((prev) => {
      const next = new Set(prev);
      if (next.has(nome)) next.delete(nome);
      else next.add(nome);
      return next;
    });
  }, []);

  const load = useCallback(async () => {
    if (!token || !Number.isFinite(eventoId)) return;
    setLoading(true);
    setError(null);
    try {
      const [configRes, templatesRes, camposRes] = await Promise.all([
        getEventoFormConfig(token, eventoId),
        listFormularioTemplates(token).catch(() => []),
        getFormularioCamposPossiveis(token),
      ]);
      setConfig(configRes);
      setTemplates(templatesRes);
      setCamposPossiveis(camposRes);
      setTemplateId(configRes.template_id ?? null);

      const catalogByLower = new Map(camposRes.map((nome) => [nome.trim().toLowerCase(), nome.trim()]));
      const initialAtivos = new Set<string>();
      for (const campo of configRes.campos || []) {
        const normalized = String(campo?.nome_campo || "").trim();
        if (!normalized) continue;
        initialAtivos.add(catalogByLower.get(normalized.toLowerCase()) ?? normalized);
      }
      setCamposAtivos(initialAtivos);
    } catch (err: any) {
      setError(err?.message || "Erro ao carregar configuração do formulário");
    } finally {
      setLoading(false);
    }
  }, [token, eventoId]);

  useEffect(() => {
    load();
  }, [load]);

  const subtitle = Number.isFinite(eventoId)
    ? `Configure o tema e os campos do formulário do evento #${eventoId}.`
    : "Configure o tema e os campos do formulário do evento.";

  return (
    <Box sx={{ width: "100%" }}>
      <Stack
        direction={{ xs: "column", md: "row" }}
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", md: "center" }}
        mb={2}
        gap={2}
      >
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Formulário de Lead
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        </Box>

        {Number.isFinite(eventoId) ? (
          <Button
            component={RouterLink}
            to={`/eventos/${eventoId}`}
            variant="outlined"
            startIcon={<ArrowBackIcon />}
            sx={{ textTransform: "none" }}
          >
            Voltar ao evento
          </Button>
        ) : null}
      </Stack>

      {error && (
        <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
        {loading ? (
          <Stack direction="row" spacing={1} alignItems="center">
            <CircularProgress size={22} />
            <Typography variant="body2" color="text.secondary">
              Carregando...
            </Typography>
          </Stack>
        ) : config ? (
          <Stack spacing={2}>
            <Box>
              <Typography variant="subtitle1" fontWeight={900} gutterBottom>
                Tema
              </Typography>
              <Autocomplete
                options={templates}
                value={selectedTemplate}
                onChange={(_, value) => setTemplateId(value ? value.id : null)}
                getOptionLabel={(option) => option.nome}
                isOptionEqualToValue={(option, value) => option.id === value.id}
                sx={{ width: "100%" }}
                renderInput={(params) => <TextField {...params} label="Tema" placeholder="Selecione..." />}
              />
              <Typography variant="caption" color="text.secondary" display="block" sx={{ pt: 0.5 }}>
                Trocar tema altera apenas o estado local (ainda não salva).
              </Typography>
            </Box>

            <Box>
              <Typography variant="subtitle1" fontWeight={900} gutterBottom>
                Campos possíveis
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Marque os campos que estarão ativos no formulário. (Placeholder: ainda não salva)
              </Typography>
            </Box>

            {camposPossiveisUniq.length ? (
              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
                  columnGap: 3,
                }}
              >
                {camposPossiveisUniq.map((nome) => (
                  <FormControlLabel
                    key={nome}
                    control={
                      <Checkbox
                        checked={camposAtivos.has(nome)}
                        onChange={() => toggleCampo(nome)}
                      />
                    }
                    label={nome}
                  />
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Nenhum campo disponível.
              </Typography>
            )}
          </Stack>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Nenhum dado para exibir.
          </Typography>
        )}
      </Paper>
    </Box>
  );
}
