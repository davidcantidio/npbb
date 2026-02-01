import {
  Alert,
  Autocomplete,
  Box,
  Button,
  CircularProgress,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useCallback, useEffect, useState } from "react";
import { listSolicitacoesIngressos, type SolicitacaoIngressoAdminListItem } from "../services/ingressos_admin";
import { useAuth } from "../store/auth";
import { listDiretorias, listEventos, type Diretoria, type EventoListItem } from "../services/eventos";

function getFriendlyErrorMessage(err: unknown, fallback: string) {
  const raw = typeof err === "object" && err ? (err as any).message : "";
  if (typeof raw === "string" && raw.trim()) {
    const trimmed = raw.trim();
    if (trimmed.startsWith("{") && trimmed.endsWith("}")) {
      try {
        const parsed = JSON.parse(trimmed);
        const parsedMessage =
          typeof parsed?.message === "string"
            ? parsed.message
            : typeof parsed?.detail === "string"
              ? parsed.detail
              : "";
        if (parsedMessage) return parsedMessage;
      } catch {
        return fallback;
      }
    }
    return trimmed;
  }
  return fallback;
}

export default function IngressosPortal() {
  const { token } = useAuth();
  const [items, setItems] = useState<SolicitacaoIngressoAdminListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [eventos, setEventos] = useState<EventoListItem[]>([]);
  const [eventosLoading, setEventosLoading] = useState(false);
  const [eventosError, setEventosError] = useState<string | null>(null);
  const [eventoId, setEventoId] = useState<string>("");
  const [diretorias, setDiretorias] = useState<Diretoria[]>([]);
  const [diretoriasLoading, setDiretoriasLoading] = useState(false);
  const [diretoriasError, setDiretoriasError] = useState<string | null>(null);
  const [diretoriaId, setDiretoriaId] = useState<string>("");

  const fetchSolicitacoes = useCallback(
    async (eventoIdValue: string, diretoriaIdValue: string) => {
      if (!token) return;
      setLoading(true);
      setError(null);
      try {
        const data = await listSolicitacoesIngressos(token, {
          evento_id: eventoIdValue ? Number(eventoIdValue) : undefined,
          diretoria_id: diretoriaIdValue ? Number(diretoriaIdValue) : undefined,
        });
        setItems(data);
      } catch (err: any) {
        setError(getFriendlyErrorMessage(err, "Nao foi possivel carregar os ingressos."));
      } finally {
        setLoading(false);
      }
    },
    [token],
  );

  useEffect(() => {
    if (!token) return;
    fetchSolicitacoes(eventoId, diretoriaId);
  }, [token, fetchSolicitacoes]);

  useEffect(() => {
    if (!token) return;
    setEventosLoading(true);
    setEventosError(null);
    listEventos(token, { skip: 0, limit: 200 })
      .then((res) => setEventos(res.items))
      .catch((err: any) =>
        setEventosError(getFriendlyErrorMessage(err, "Erro ao carregar eventos")),
      )
      .finally(() => setEventosLoading(false));
  }, [token]);

  useEffect(() => {
    if (!token) return;
    setDiretoriasLoading(true);
    setDiretoriasError(null);
    listDiretorias(token)
      .then((items) => setDiretorias(items))
      .catch((err: any) =>
        setDiretoriasError(getFriendlyErrorMessage(err, "Erro ao carregar diretorias")),
      )
      .finally(() => setDiretoriasLoading(false));
  }, [token]);


  return (
    <Box sx={{ width: "100%" }}>
      <Box mb={2}>
        <Typography variant="h4" fontWeight={800}>
          Ingressos
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Solicitacoes registradas em todos os eventos
        </Typography>
      </Box>

      <Stack direction={{ xs: "column", md: "row" }} spacing={1.5} mb={2}>
        <Autocomplete
          options={eventos}
          loading={eventosLoading}
          value={eventos.find((e) => e.id === (eventoId ? Number(eventoId) : -1)) ?? null}
          onChange={(_, value) => {
            setEventoId(value ? String(value.id) : "");
          }}
          getOptionLabel={(option) => option.nome}
          isOptionEqualToValue={(option, value) => option.id === value.id}
          sx={{ minWidth: 240 }}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Evento"
              placeholder="Selecione um evento"
              InputProps={{
                ...params.InputProps,
                endAdornment: (
                  <>
                    {eventosLoading ? <CircularProgress color="inherit" size={18} /> : null}
                    {params.InputProps.endAdornment}
                  </>
                ),
              }}
            />
          )}
        />
        <Autocomplete
          options={diretorias}
          loading={diretoriasLoading}
          value={
            diretorias.find((d) => d.id === (diretoriaId ? Number(diretoriaId) : -1)) ?? null
          }
          onChange={(_, value) => {
            setDiretoriaId(value ? String(value.id) : "");
          }}
          getOptionLabel={(option) => option.nome}
          isOptionEqualToValue={(option, value) => option.id === value.id}
          sx={{ minWidth: 220 }}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Diretoria"
              placeholder="Selecione uma diretoria"
              InputProps={{
                ...params.InputProps,
                endAdornment: (
                  <>
                    {diretoriasLoading ? <CircularProgress color="inherit" size={18} /> : null}
                    {params.InputProps.endAdornment}
                  </>
                ),
              }}
            />
          )}
        />
        <Button
          variant="contained"
          sx={{ textTransform: "none", fontWeight: 700 }}
          onClick={() => fetchSolicitacoes(eventoId, diretoriaId)}
          disabled={loading}
        >
          Aplicar filtro
        </Button>
        <Button
          variant="outlined"
          sx={{ textTransform: "none", fontWeight: 700 }}
          onClick={() => {
            setEventoId("");
            setDiretoriaId("");
            fetchSolicitacoes("", "");
          }}
          disabled={!eventoId && !diretoriaId}
        >
          Limpar
        </Button>
      </Stack>
      {eventosError ? (
        <Typography variant="caption" color="error" sx={{ mb: 1, display: "block" }}>
          {eventosError}
        </Typography>
      ) : null}
      {diretoriasError ? (
        <Typography variant="caption" color="error" sx={{ mb: 1, display: "block" }}>
          {diretoriasError}
        </Typography>
      ) : null}

      {error ? (
        <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="subtitle1" fontWeight={800} gutterBottom>
            Nao foi possivel carregar os ingressos
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {error}
          </Typography>
          <Button
            variant="contained"
            sx={{ textTransform: "none", fontWeight: 700 }}
            onClick={() => fetchSolicitacoes(eventoId, diretoriaId)}
          >
            Tentar novamente
          </Button>
        </Paper>
      ) : loading ? (
        <Stack direction="row" spacing={1} alignItems="center">
          <CircularProgress size={20} />
          <Typography variant="body2" color="text.secondary">
            Carregando solicitacoes...
          </Typography>
        </Stack>
      ) : items.length === 0 ? (
        <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="subtitle1" fontWeight={800} gutterBottom>
            Nenhuma solicitacao registrada
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Nenhum ingresso foi solicitado ate o momento.
          </Typography>
          <Button
            variant="outlined"
            sx={{ textTransform: "none", fontWeight: 700 }}
            onClick={() => fetchSolicitacoes(eventoId, diretoriaId)}
          >
            Atualizar
          </Button>
        </Paper>
      ) : (
        <Paper elevation={2} sx={{ borderRadius: 2, overflow: "hidden" }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Data</TableCell>
                <TableCell>Solicitante</TableCell>
                <TableCell>Indicado</TableCell>
                <TableCell>Diretoria</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{new Date(item.created_at).toLocaleString("pt-BR")}</TableCell>
                  <TableCell>{item.solicitante_email}</TableCell>
                  <TableCell>{item.indicado_email || "-"}</TableCell>
                  <TableCell>{item.diretoria_nome}</TableCell>
                  <TableCell>{item.status}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      )}
    </Box>
  );
}
