import CloudUploadRoundedIcon from "@mui/icons-material/CloudUploadRounded";
import ClearRoundedIcon from "@mui/icons-material/ClearRounded";
import DownloadRoundedIcon from "@mui/icons-material/DownloadRounded";
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { ALL_EVENTS_OPTION_ID } from "../../components/dashboard/AgeAnalysisFilters";
import { toApiErrorMessage } from "../../services/http";
import { listLeads, type LeadListItem, type ReferenciaEvento } from "../../services/leads_import";
import { triggerBlobDownload } from "../../services/leads_export";
import { exportLeadsListCsv } from "../../services/leads_list_export";
import { useAuth } from "../../store/auth";
import { useReferenciaEventos } from "../dashboard/useReferenciaEventos";
import { getLeadListDisplayCells } from "./leadsListExport";

const ALL_EVENTS_OPTION: ReferenciaEvento = {
  id: ALL_EVENTS_OPTION_ID,
  nome: "Todos os eventos",
  data_inicio_prevista: null,
};

const DEFAULT_PAGE_SIZE = 20;

type FilterForm = {
  data_inicio: string;
  data_fim: string;
  evento_id: number | null;
};

const EMPTY_FILTERS: FilterForm = {
  data_inicio: "",
  data_fim: "",
  evento_id: null,
};

function formatEventOptionLabel(option: ReferenciaEvento) {
  if (!option.data_inicio_prevista) return option.nome;
  return `${option.nome} • ${option.data_inicio_prevista}`;
}

function hasInvalidDateRange(filters: FilterForm) {
  if (!filters.data_inicio || !filters.data_fim) return false;
  return filters.data_fim < filters.data_inicio;
}

export default function LeadsListPage() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const { eventOptions, isLoadingEvents, eventsError } = useReferenciaEventos(token);

  const eventOptionsWithAll = useMemo(
    () => [ALL_EVENTS_OPTION, ...eventOptions.filter((o) => o.id !== ALL_EVENTS_OPTION_ID)],
    [eventOptions],
  );

  const [draftFilters, setDraftFilters] = useState<FilterForm>(EMPTY_FILTERS);
  const [appliedFilters, setAppliedFilters] = useState<FilterForm>(EMPTY_FILTERS);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);
  const [rows, setRows] = useState<LeadListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const invalidRange = hasInvalidDateRange(draftFilters);

  const selectedEventDraft =
    eventOptionsWithAll.find((o) => o.id === (draftFilters.evento_id ?? ALL_EVENTS_OPTION_ID)) ??
    eventOptionsWithAll[0] ??
    null;

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const res = await listLeads(token, {
        page,
        page_size: pageSize,
        ...(appliedFilters.data_inicio ? { data_inicio: appliedFilters.data_inicio } : {}),
        ...(appliedFilters.data_fim ? { data_fim: appliedFilters.data_fim } : {}),
        ...(typeof appliedFilters.evento_id === "number"
          ? { evento_id: appliedFilters.evento_id }
          : {}),
      });
      setRows(res.items);
      setTotal(res.total);
    } catch (err) {
      setError(toApiErrorMessage(err, "Nao foi possivel carregar os leads."));
      setRows([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [token, page, pageSize, appliedFilters]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleApply = () => {
    if (invalidRange) return;
    setAppliedFilters({ ...draftFilters });
    setPage(1);
  };

  const handleClear = () => {
    setDraftFilters(EMPTY_FILTERS);
    setAppliedFilters(EMPTY_FILTERS);
    setPage(1);
  };

  const handleExportCsv = async () => {
    if (!token || exporting) return;
    setExporting(true);
    setExportError(null);
    try {
      const result = await exportLeadsListCsv(token, appliedFilters);
      if (!result) return;
      triggerBlobDownload(result.blob, result.filename);
    } catch (err) {
      setExportError(toApiErrorMessage(err, "Nao foi possivel exportar os leads."));
    } finally {
      setExporting(false);
    }
  };

  return (
    <Stack spacing={3}>
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "flex-start", justifyContent: "space-between" }}>
        <Box>
          <Typography variant="h4" fontWeight={900}>
            Leads
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
            Lista de leads cadastrados. Filtre por periodo de criacao e pelo evento relacionado ao lead.
          </Typography>
        </Box>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          <Button
            variant="outlined"
            size="large"
            startIcon={
              exporting ? <CircularProgress color="inherit" size={20} /> : <DownloadRoundedIcon />
            }
            onClick={() => void handleExportCsv()}
            disabled={!token || exporting}
          >
            {exporting ? "Exportando…" : "Exportar CSV"}
          </Button>
          <Button
            variant="contained"
            size="large"
            startIcon={<CloudUploadRoundedIcon />}
            onClick={() => navigate("/leads/importar")}
          >
            Importar leads
          </Button>
        </Stack>
      </Box>

      <Card variant="outlined">
        <CardContent>
          <Stack spacing={2}>
            <Typography variant="subtitle1" fontWeight={800}>
              Filtros
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Autocomplete
                  options={eventOptionsWithAll}
                  disableClearable
                  value={selectedEventDraft}
                  loading={isLoadingEvents}
                  loadingText="Carregando eventos..."
                  noOptionsText="Nenhum evento encontrado"
                  getOptionLabel={formatEventOptionLabel}
                  isOptionEqualToValue={(option, value) => option.id === value.id}
                  onChange={(_, selected) =>
                    setDraftFilters((prev) => ({
                      ...prev,
                      evento_id:
                        selected?.id === ALL_EVENTS_OPTION_ID ? null : selected?.id ?? null,
                    }))
                  }
                  renderInput={(params) => (
                    <TextField {...params} label="Evento" placeholder="Todos" />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  label="Data inicio"
                  type="date"
                  fullWidth
                  value={draftFilters.data_inicio}
                  onChange={(e) => setDraftFilters((p) => ({ ...p, data_inicio: e.target.value }))}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  label="Data fim"
                  type="date"
                  fullWidth
                  value={draftFilters.data_fim}
                  onChange={(e) => setDraftFilters((p) => ({ ...p, data_fim: e.target.value }))}
                  error={invalidRange}
                  helperText={
                    invalidRange ? "A data fim deve ser maior ou igual a data inicio." : " "
                  }
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
            </Grid>
            <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
              <Button variant="contained" onClick={handleApply} disabled={invalidRange}>
                Aplicar filtros
              </Button>
              <Button variant="outlined" startIcon={<ClearRoundedIcon />} onClick={handleClear}>
                Limpar filtros
              </Button>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      {eventsError ? <Alert severity="warning">{eventsError}</Alert> : null}
      {error ? <Alert severity="error">{error}</Alert> : null}
      {exportError ? <Alert severity="error">{exportError}</Alert> : null}

      <Paper variant="outlined" sx={{ borderRadius: 2, overflow: "hidden" }}>
        <TableContainer sx={{ position: "relative", minHeight: 200 }}>
          {loading ? (
            <Box
              sx={{
                position: "absolute",
                inset: 0,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                bgcolor: "action.hover",
                zIndex: 1,
              }}
            >
              <CircularProgress size={32} />
            </Box>
          ) : null}
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Nome</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Criado em</TableCell>
                <TableCell>Evento (conversao)</TableCell>
                <TableCell>Evento (origem)</TableCell>
                <TableCell>Local</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.length === 0 && !loading ? (
                <TableRow>
                  <TableCell colSpan={6}>
                    <Typography color="text.secondary" sx={{ py: 3, textAlign: "center" }}>
                      Nenhum lead encontrado para os filtros atuais.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                rows.map((row) => {
                  const [nome, email, criadoEm, evConv, evOrig, local] = getLeadListDisplayCells(row);
                  return (
                    <TableRow key={row.id} hover>
                      <TableCell>{nome}</TableCell>
                      <TableCell>{email}</TableCell>
                      <TableCell>{criadoEm}</TableCell>
                      <TableCell>{evConv}</TableCell>
                      <TableCell>{evOrig}</TableCell>
                      <TableCell>{local}</TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
          <TablePagination
            component="div"
            count={total}
            page={page - 1}
            onPageChange={(_, next) => setPage(next + 1)}
            rowsPerPage={pageSize}
            onRowsPerPageChange={(e) => {
              setPageSize(Number.parseInt(e.target.value, 10));
              setPage(1);
            }}
            rowsPerPageOptions={[10, 20, 50, 100]}
            labelRowsPerPage="Por pagina"
            labelDisplayedRows={({ from, to, count }) =>
              `${from}-${to} de ${count !== -1 ? count : `mais de ${to}`}`
            }
          />
        </TableContainer>
      </Paper>
    </Stack>
  );
}
