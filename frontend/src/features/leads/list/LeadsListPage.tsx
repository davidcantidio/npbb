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
  MenuItem,
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
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { ALL_EVENTS_OPTION_ID } from "../../../components/dashboard/AgeAnalysisFilters";
import { toApiErrorMessage } from "../../../services/http";
import {
  listLeads,
  type LeadListItem,
  type LeadListOrigin,
  type LeadListSortBy,
  type LeadListSortDir,
  type ReferenciaEvento,
} from "../../../services/leads_import";
import { triggerBlobDownload } from "../../../services/leads_export";
import { exportLeadsListCsv } from "../../../services/leads_list_export";
import { useAuth } from "../../../store/auth";
import { useReferenciaEventos } from "../shared";
import { getLeadListDisplayCells } from "./leadsListExport";
import { inferActiveQuarter, quarterDateRangeISO } from "./leadsListQuarterPresets";

const ALL_EVENTS_OPTION: ReferenciaEvento = {
  id: ALL_EVENTS_OPTION_ID,
  nome: "Todos os eventos",
  data_inicio_prevista: null,
};

const DEFAULT_PAGE_SIZE = 20;
const DEFAULT_SORT_BY: LeadListSortBy = "data_criacao";
const DEFAULT_SORT_DIR: LeadListSortDir = "desc";

type FilterForm = {
  search: string;
  data_inicio: string;
  data_fim: string;
  evento_id: number | null;
  origem: LeadListOrigin | null;
};

function createEmptyFilters(): FilterForm {
  return { search: "", data_inicio: "", data_fim: "", evento_id: null, origem: null };
}

function formatEventOptionLabel(option: ReferenciaEvento) {
  if (!option.data_inicio_prevista) return option.nome;
  return `${option.nome} • ${option.data_inicio_prevista}`;
}

function hasInvalidDateRange(filters: FilterForm) {
  if (!filters.data_inicio || !filters.data_fim) return false;
  return filters.data_fim < filters.data_inicio;
}

function defaultSortDirFor(sortBy: LeadListSortBy): LeadListSortDir {
  return sortBy === "data_criacao" ? "desc" : "asc";
}

export default function LeadsListPage() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const { eventOptions, isLoadingEvents, eventsError } = useReferenciaEventos(token);

  const eventOptionsWithAll = useMemo(
    () => [ALL_EVENTS_OPTION, ...eventOptions.filter((o) => o.id !== ALL_EVENTS_OPTION_ID)],
    [eventOptions],
  );

  const [draftFilters, setDraftFilters] = useState<FilterForm>(() => createEmptyFilters());
  const [appliedFilters, setAppliedFilters] = useState<FilterForm>(() => createEmptyFilters());
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);
  const [sortBy, setSortBy] = useState<LeadListSortBy>(DEFAULT_SORT_BY);
  const [sortDir, setSortDir] = useState<LeadListSortDir>(DEFAULT_SORT_DIR);
  const [rows, setRows] = useState<LeadListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const invalidRange = hasInvalidDateRange(draftFilters);
  const invalidSearch = draftFilters.search.trim().length === 1;

  const presetYear = new Date().getFullYear();
  const activeQuarterPreset = inferActiveQuarter(
    draftFilters.data_inicio,
    draftFilters.data_fim,
    presetYear,
  );

  const selectedEventDraft =
    eventOptionsWithAll.find((o) => o.id === (draftFilters.evento_id ?? ALL_EVENTS_OPTION_ID)) ??
    eventOptionsWithAll[0] ??
    null;

  useEffect(() => {
    if (!token) return;

    const controller = new AbortController();
    let isActive = true;

    setLoading(true);
    setError(null);

    void listLeads(token, {
      page,
      page_size: pageSize,
      sort_by: sortBy,
      sort_dir: sortDir,
      signal: controller.signal,
      ...(appliedFilters.search ? { search: appliedFilters.search } : {}),
      ...(appliedFilters.data_inicio ? { data_inicio: appliedFilters.data_inicio } : {}),
      ...(appliedFilters.data_fim ? { data_fim: appliedFilters.data_fim } : {}),
      ...(typeof appliedFilters.evento_id === "number" ? { evento_id: appliedFilters.evento_id } : {}),
      ...(appliedFilters.origem ? { origem: appliedFilters.origem } : {}),
    })
      .then((res) => {
        if (!isActive || controller.signal.aborted) return;
        setRows(res.items);
        setTotal(res.total);
      })
      .catch((err) => {
        if (!isActive || controller.signal.aborted) return;
        setError(toApiErrorMessage(err, "Nao foi possivel carregar os leads."));
        setRows([]);
        setTotal(0);
      })
      .finally(() => {
        if (!isActive || controller.signal.aborted) return;
        setLoading(false);
      });

    return () => {
      isActive = false;
      controller.abort();
    };
  }, [token, page, pageSize, appliedFilters, sortBy, sortDir]);

  const handleApply = () => {
    if (invalidRange || invalidSearch) return;
    setAppliedFilters({ ...draftFilters });
    setPage(1);
  };

  const handleClear = () => {
    const empty = createEmptyFilters();
    setDraftFilters(empty);
    setAppliedFilters({ ...empty });
    setPage(1);
  };

  const handleSortByChange = (nextSortBy: LeadListSortBy) => {
    setSortBy(nextSortBy);
    setSortDir((prev) => (sortBy === nextSortBy ? prev : defaultSortDirFor(nextSortBy)));
    setPage(1);
  };

  const handleSortDirChange = (nextSortDir: LeadListSortDir) => {
    setSortDir(nextSortDir);
    setPage(1);
  };

  const applyQuarterPreset = (quarter: 1 | 2 | 3 | 4) => {
    const { start, end } = quarterDateRangeISO(presetYear, quarter);
    setDraftFilters((prev) => ({ ...prev, data_inicio: start, data_fim: end }));
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
            Lista paginada de leads com busca, filtros e ordenacao executados no backend.
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
              <Grid item xs={12} md={5}>
                <TextField
                  label="Busca"
                  fullWidth
                  error={invalidSearch}
                  value={draftFilters.search}
                  placeholder="Nome, email, CPF, telefone ou evento"
                  helperText={
                    invalidSearch
                      ? "Digite ao menos 2 caracteres para buscar."
                      : "Busca prefixada no servidor."
                  }
                  onChange={(e) => setDraftFilters((prev) => ({ ...prev, search: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} md={4}>
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
              <Grid item xs={12} md={3}>
                <TextField
                  select
                  fullWidth
                  label="Origem"
                  value={draftFilters.origem ?? ""}
                  onChange={(e) =>
                    setDraftFilters((prev) => ({
                      ...prev,
                      origem: (e.target.value as LeadListOrigin | "") || null,
                    }))
                  }
                >
                  <MenuItem value="">Todas</MenuItem>
                  <MenuItem value="proponente">Proponente</MenuItem>
                  <MenuItem value="ativacao">Ativacao</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  label="Data início"
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
                    invalidRange ? "A data fim deve ser maior ou igual à data início." : " "
                  }
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  select
                  label="Ordenar por"
                  fullWidth
                  value={sortBy}
                  onChange={(e) => handleSortByChange(e.target.value as LeadListSortBy)}
                >
                  <MenuItem value="data_criacao">Criado em</MenuItem>
                  <MenuItem value="nome">Nome</MenuItem>
                  <MenuItem value="email">Email</MenuItem>
                  <MenuItem value="evento">Evento</MenuItem>
                  <MenuItem value="origem">Origem</MenuItem>
                  <MenuItem value="local">Local</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  select
                  label="Direcao"
                  fullWidth
                  value={sortDir}
                  onChange={(e) => handleSortDirChange(e.target.value as LeadListSortDir)}
                >
                  <MenuItem value="desc">Decrescente</MenuItem>
                  <MenuItem value="asc">Crescente</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <Stack spacing={1}>
                  <Typography variant="caption" color="text.secondary" component="p" sx={{ m: 0 }}>
                    Trimestres do ano {presetYear}
                  </Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    {([1, 2, 3, 4] as const).map((q) => (
                      <Button
                        key={q}
                        size="small"
                        variant={activeQuarterPreset === q ? "contained" : "outlined"}
                        onClick={() => applyQuarterPreset(q)}
                        aria-pressed={activeQuarterPreset === q}
                        aria-label={`${q}º trimestre de ${presetYear}`}
                      >
                        Q{q}
                      </Button>
                    ))}
                  </Stack>
                </Stack>
              </Grid>
            </Grid>
            <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
              <Button variant="contained" onClick={handleApply} disabled={invalidRange || invalidSearch}>
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
                <TableCell>Proponente / Ativação</TableCell>
                <TableCell>Início e fim do evento</TableCell>
                <TableCell>Evento (conversao)</TableCell>
                <TableCell>Evento (origem)</TableCell>
                <TableCell>Local</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.length === 0 && !loading ? (
                <TableRow>
                  <TableCell colSpan={8}>
                    <Typography color="text.secondary" sx={{ py: 3, textAlign: "center" }}>
                      Nenhum lead encontrado para os filtros atuais.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                rows.map((row) => {
                  const [nome, email, criadoEm, origem, periodoEvento, evConv, evOrig, local] =
                    getLeadListDisplayCells(row);
                  return (
                    <TableRow key={row.id} hover>
                      <TableCell>{nome}</TableCell>
                      <TableCell>{email}</TableCell>
                      <TableCell>{criadoEm}</TableCell>
                      <TableCell>{origem}</TableCell>
                      <TableCell>{periodoEvento}</TableCell>
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
