import { useCallback, useEffect, useMemo, useRef, useState, type ChangeEvent } from "react";
import { createPortal } from "react-dom";
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  CircularProgress,
  FormControl,
  MenuItem,
  Pagination,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { Link as RouterLink } from "react-router-dom";

import { useAuth } from "../store/auth";
import {
  Diretoria,
  EventoListItem,
  StatusEvento,
  exportEventosCsv,
  importEventosCsv,
  listDiretorias,
  listEventos,
  listStatusEvento,
  updateEvento,
  type ImportEventosCsvError,
  type EventoUpdate,
} from "../services/eventos";
import { Agencia, listAgencias } from "../services/agencias";
import { EventoRow } from "../components/eventos/EventoRow";


type ImportSummary = {
  total: number;
  success: number;
  failed: number;
};

function formatImportError(error: ImportEventosCsvError): string {
  const line = Number.isFinite(error.line) ? error.line : "-";
  const field = error.field ? String(error.field) : "geral";
  const reason = error.message ? String(error.message) : "Erro ao importar linha";
  return `Linha ${line}: campo "${field}" - ${reason}.`;
}

type Filters = {
  search: string;
  estado: string;
  cidade: string;
  dataInicio: string;
  dataFim: string;
  diretoriaId: string;
};

const EMPTY_FILTERS: Filters = {
  search: "",
  estado: "",
  cidade: "",
  dataInicio: "",
  dataFim: "",
  diretoriaId: "",
};

function normalizeFilters(filters: Filters): Filters {
  const clean = (v: string) => v.trim();
  return {
    search: clean(filters.search),
    estado: clean(filters.estado).toUpperCase(),
    cidade: clean(filters.cidade),
    dataInicio: clean(filters.dataInicio),
    dataFim: clean(filters.dataFim),
    diretoriaId: clean(filters.diretoriaId),
  };
}

const UF_OPTIONS = [
  "AC",
  "AL",
  "AP",
  "AM",
  "BA",
  "CE",
  "DF",
  "ES",
  "GO",
  "MA",
  "MT",
  "MS",
  "MG",
  "PA",
  "PB",
  "PR",
  "PE",
  "PI",
  "RJ",
  "RN",
  "RS",
  "RO",
  "RR",
  "SC",
  "SP",
  "SE",
  "TO",
];

type EstadosCidadesData = {
  estados: Array<{
    sigla: string;
    nome: string;
    cidades: string[];
  }>;
};

let cachedCidadesPorUf: Record<string, string[]> | null = null;
let cachedAllCidades: string[] | null = null;

async function getCidadesData(): Promise<{ map: Record<string, string[]>; all: string[] }> {
  if (cachedCidadesPorUf && cachedAllCidades) {
    return { map: cachedCidadesPorUf, all: cachedAllCidades };
  }

  const mod = await import("../data/estados-cidades.json");
  const data = ((mod as any).default ?? mod) as EstadosCidadesData;

  const map: Record<string, string[]> = {};
  const allSet = new Set<string>();

  for (const estado of Array.isArray(data.estados) ? data.estados : []) {
    const uf = String(estado.sigla || "").toUpperCase();
    const cities = Array.isArray(estado.cidades) ? estado.cidades.filter(Boolean) : [];
    if (uf) map[uf] = cities;
    for (const c of cities) allSet.add(c);
  }

  cachedCidadesPorUf = map;
  cachedAllCidades = Array.from(allSet).sort((a, b) => a.localeCompare(b));
  return { map, all: cachedAllCidades };
}

export default function EventsList() {
  const { token } = useAuth();

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [filtersContainer, setFiltersContainer] = useState<HTMLElement | null>(null);

  const [items, setItems] = useState<EventoListItem[]>([]);
  const [total, setTotal] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);
  const [importSummary, setImportSummary] = useState<ImportSummary | null>(null);
  const [importErrors, setImportErrors] = useState<string[]>([]);

  const [filtersDraft, setFiltersDraft] = useState<Filters>(EMPTY_FILTERS);
  const [filtersApplied, setFiltersApplied] = useState<Filters>(EMPTY_FILTERS);

  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(25);

  const [cidades, setCidades] = useState<string[]>([]);
  const [cidadesLoading, setCidadesLoading] = useState(false);
  const [diretorias, setDiretorias] = useState<Diretoria[]>([]);
  const [agencias, setAgencias] = useState<Agencia[]>([]);
  const [statuses, setStatuses] = useState<StatusEvento[]>([]);
  const [domainsLoading, setDomainsLoading] = useState(false);
  const [domainsError, setDomainsError] = useState<string | null>(null);

  const [statusUpdatingId, setStatusUpdatingId] = useState<number | null>(null);
  const [exporting, setExporting] = useState(false);
  const [inlineUpdating, setInlineUpdating] = useState<Record<number, boolean>>({});

  const diretoriaById = useMemo(() => {
    const map = new Map<number, string>();
    for (const d of diretorias) map.set(d.id, d.nome);
    return map;
  }, [diretorias]);

  const agenciaById = useMemo(() => {
    const map = new Map<number, string>();
    for (const a of agencias) map.set(a.id, a.nome);
    return map;
  }, [agencias]);

  const eventoOptions = useMemo(() => {
    const names = new Set<string>();
    for (const item of items) {
      const name = String(item.nome || "").trim();
      if (name) names.add(name);
    }
    return Array.from(names).sort((a, b) => a.localeCompare(b));
  }, [items]);

  const pageCount = useMemo(() => {
    if (typeof total !== "number") return 0;
    return Math.max(1, Math.ceil(total / limit));
  }, [total, limit]);

  const loadDomains = useCallback(async () => {
    if (!token) return;
    setDomainsLoading(true);
    setDomainsError(null);
    try {
      const [agenciasRes, dirsRes, statusRes] = await Promise.allSettled([
        listAgencias({ limit: 200 }),
        listDiretorias(token),
        listStatusEvento(token),
      ]);

      const failures: string[] = [];
      if (agenciasRes.status === "fulfilled") setAgencias(agenciasRes.value);
      else failures.push("agencias");

      if (dirsRes.status === "fulfilled") setDiretorias(dirsRes.value);
      else failures.push("diretorias");

      if (statusRes.status === "fulfilled") setStatuses(statusRes.value);
      else failures.push("status");

      if (failures.length) {
        setDomainsError(`Falha ao carregar dom?nios: ${failures.join(", ")}`);
      }
    } finally {
      setDomainsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadDomains();
  }, [loadDomains]);

  useEffect(() => {
    setFiltersContainer(document.getElementById("app-sidebar-slot"));
  }, []);

  useEffect(() => {
    let cancelled = false;
    setCidadesLoading(true);
    getCidadesData()
      .then(({ map, all }) => {
        if (cancelled) return;
        const uf = String(filtersDraft.estado || "").trim().toUpperCase();
        setCidades(uf ? map[uf] ?? [] : all);
      })
      .catch(() => {
        if (!cancelled) setCidades([]);
      })
      .finally(() => {
        if (!cancelled) setCidadesLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [filtersDraft.estado]);

  const fetchItems = useCallback(
    async (options?: { silent?: boolean }) => {
      if (!token) return;
      const silent = Boolean(options?.silent);
      if (!silent) setLoading(true);
      setError(null);
      try {
        const applied = normalizeFilters(filtersApplied);
        const diretoriaIdNum = applied.diretoriaId ? Number(applied.diretoriaId) : null;
        const res = await listEventos(token, {
          skip: (page - 1) * limit,
          limit,
          search: applied.search || undefined,
          estado: applied.estado || undefined,
          cidade: applied.cidade || undefined,
          data_inicio: applied.dataInicio || undefined,
          data_fim: applied.dataFim || undefined,
          diretoria_id:
            typeof diretoriaIdNum === "number" && Number.isFinite(diretoriaIdNum)
              ? diretoriaIdNum
              : undefined,
        });
        setItems(res.items);
        setTotal(res.total);
      } catch (err: any) {
        if (!silent) setError(err?.message || "Erro ao carregar eventos");
      } finally {
        if (!silent) setLoading(false);
      }
    },
    [token, page, limit, filtersApplied],
  );

  const load = useCallback(async () => {
    await fetchItems();
  }, [fetchItems]);

  useEffect(() => {
    load();
  }, [load]);

  const handleStatusChange = useCallback(
    async (eventoId: number, nextStatusId: number) => {
      if (!token) return;
      const prevStatusId = items.find((i) => i.id === eventoId)?.status_id;
      if (!prevStatusId || prevStatusId === nextStatusId) return;

      setStatusUpdatingId(eventoId);
      setError(null);
      setItems((prev) =>
        prev.map((item) => (item.id === eventoId ? { ...item, status_id: nextStatusId } : item)),
      );

      try {
        const updated = await updateEvento(token, eventoId, { status_id: nextStatusId });
        setItems((prev) =>
          prev.map((item) => (item.id === eventoId ? { ...item, status_id: updated.status_id } : item)),
        );
      } catch (err: any) {
        setItems((prev) =>
          prev.map((item) =>
            item.id === eventoId ? { ...item, status_id: prevStatusId } : item,
          ),
        );
        setError(err?.message || "Erro ao atualizar status");
      } finally {
        setStatusUpdatingId(null);
      }
    },
    [items, token],
  );

  const handleInlineUpdate = useCallback(
    async (eventoId: number, patch: EventoUpdate) => {
      if (!token) throw new Error("Usuário não autenticado");
      setInlineUpdating((prev) => ({ ...prev, [eventoId]: true }));
      setError(null);
      try {
        const updated = await updateEvento(token, eventoId, patch);
        setItems((prev) =>
          prev.map((item) => (item.id === eventoId ? { ...item, ...updated } : item)),
        );
        fetchItems({ silent: true });
        return updated;
      } catch (err: any) {
        setError(err?.message || "Erro ao atualizar evento");
        throw err;
      } finally {
        setInlineUpdating((prev) => {
          const next = { ...prev };
          delete next[eventoId];
          return next;
        });
      }
    },
    [fetchItems, token],
  );

  const handleExportCsv = useCallback(async () => {
    if (!token) return;
    setExporting(true);
    setError(null);
    try {
      const applied = normalizeFilters(filtersApplied);
      const diretoriaIdNum = applied.diretoriaId ? Number(applied.diretoriaId) : null;

      const { blob, filename } = await exportEventosCsv(token, {
        skip: 0,
        limit: 10000,
        search: applied.search || undefined,
        estado: applied.estado || undefined,
        cidade: applied.cidade || undefined,
        data_inicio: applied.dataInicio || undefined,
        data_fim: applied.dataFim || undefined,
        diretoria_id:
          typeof diretoriaIdNum === "number" && Number.isFinite(diretoriaIdNum)
            ? diretoriaIdNum
            : undefined,
      });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename || "eventos.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.setTimeout(() => window.URL.revokeObjectURL(url), 1000);
    } catch (err: any) {
      setError(err?.message || "Erro ao exportar CSV");
    } finally {
      setExporting(false);
    }
  }, [filtersApplied, token]);

  const handleImportCsvClick = useCallback(() => {
    if (!token || importing) return;
    setImportSummary(null);
    setImportErrors([]);
    fileInputRef.current?.click();
  }, [token, importing]);

  const handleImportCsvChange = useCallback(
    async (event: ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      event.target.value = "";
      if (!file || !token) return;

      setImporting(true);
      setError(null);
      setImportSummary(null);
      setImportErrors([]);

      try {
        const result = await importEventosCsv(token, file);
        const errors = Array.isArray(result.errors) ? result.errors : [];
        setImportSummary({
          total: result.total ?? result.success + result.failed,
          success: result.success ?? 0,
          failed: result.failed ?? errors.length,
        });
        setImportErrors(errors.map(formatImportError));

        if (result.success > 0) {
          await load();
        }
      } catch (err: any) {
        setError(err?.message || "Erro ao importar CSV");
      } finally {
        setImporting(false);
      }
    },
    [load, token],
  );

  const filtersPanel = (
    <Box sx={{ pt: 1 }}>
      <Typography variant="caption" color="text.secondary" fontWeight={700} sx={{ mb: 1, display: "block" }}>
        Filtros
      </Typography>
      <Stack spacing={1.5}>
        <Autocomplete
          freeSolo
          options={eventoOptions}
          inputValue={filtersDraft.search}
          onInputChange={(_, value) =>
            setFiltersDraft((prev) => ({
              ...prev,
              search: String(value || ""),
            }))
          }
          onChange={(_, value) =>
            setFiltersDraft((prev) => ({
              ...prev,
              search: typeof value === "string" ? value : "",
            }))
          }
          fullWidth
          renderInput={(params) => (
            <TextField {...params} label="Evento" placeholder="Todos" fullWidth />
          )}
        />

        <Autocomplete
          options={UF_OPTIONS}
          value={filtersDraft.estado ? filtersDraft.estado.toUpperCase() : null}
          onChange={(_, value) =>
            setFiltersDraft((prev) => ({
              ...prev,
              estado: value ? String(value) : "",
              cidade: "",
            }))
          }
          fullWidth
          renderInput={(params) => (
            <TextField {...params} label="Estado" placeholder="Todos" fullWidth />
          )}
        />

        <Autocomplete
          freeSolo
          options={cidades}
          inputValue={filtersDraft.cidade}
          onInputChange={(_, value) =>
            setFiltersDraft((prev) => ({
              ...prev,
              cidade: String(value || ""),
            }))
          }
          onChange={(_, value) =>
            setFiltersDraft((prev) => ({
              ...prev,
              cidade: typeof value === "string" ? value : "",
            }))
          }
          loading={cidadesLoading}
          fullWidth
          renderInput={(params) => (
            <TextField
              {...params}
              label="Local"
              placeholder="Todos"
              fullWidth
              InputProps={{
                ...params.InputProps,
                endAdornment: (
                  <>
                    {cidadesLoading ? <CircularProgress color="inherit" size={18} /> : null}
                    {params.InputProps.endAdornment}
                  </>
                ),
              }}
            />
          )}
        />

        <Autocomplete
          options={diretorias}
          value={
            filtersDraft.diretoriaId
              ? diretorias.find((d) => String(d.id) === filtersDraft.diretoriaId) ?? null
              : null
          }
          onChange={(_, value) =>
            setFiltersDraft((prev) => ({
              ...prev,
              diretoriaId: value ? String(value.id) : "",
            }))
          }
          getOptionLabel={(option) => option.nome}
          isOptionEqualToValue={(option, value) => option.id === value.id}
          disabled={domainsLoading}
          fullWidth
          renderInput={(params) => (
            <TextField {...params} label="Diretoria" placeholder="Todas" fullWidth />
          )}
        />

        <Stack direction="row" spacing={1}>
          <TextField
            label="De"
            type="date"
            value={filtersDraft.dataInicio}
            onChange={(e) =>
              setFiltersDraft((prev) => ({ ...prev, dataInicio: e.target.value }))
            }
            fullWidth
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            label="Até"
            type="date"
            value={filtersDraft.dataFim}
            onChange={(e) => setFiltersDraft((prev) => ({ ...prev, dataFim: e.target.value }))}
            fullWidth
            InputLabelProps={{ shrink: true }}
          />
        </Stack>

        <Stack direction="row" spacing={1}>
          <Button
            type="button"
            variant="outlined"
            onClick={() => {
              setFiltersDraft(EMPTY_FILTERS);
              setFiltersApplied(EMPTY_FILTERS);
              setPage(1);
            }}
            sx={{ textTransform: "none" }}
            fullWidth
          >
            Limpar
          </Button>
          <Button
            type="button"
            variant="contained"
            onClick={() => {
              const normalized = normalizeFilters(filtersDraft);
              if (normalized.dataInicio && normalized.dataFim) {
                const start = new Date(normalized.dataInicio);
                const end = new Date(normalized.dataFim);
                if (Number.isFinite(start.getTime()) && Number.isFinite(end.getTime()) && end < start) {
                  setError("Intervalo de datas inválido: 'Até' deve ser maior/igual a 'De'.");
                  return;
                }
              }

              setFiltersApplied(normalized);
              setPage(1);
            }}
            sx={{ textTransform: "none", fontWeight: 800 }}
            fullWidth
          >
            Aplicar
          </Button>
        </Stack>
      </Stack>
    </Box>
  );

  const filtersPortal = filtersContainer ? createPortal(filtersPanel, filtersContainer) : null;

  return (
    <Box sx={{ width: "100%" }}>
      {filtersPortal}
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv,text/csv"
        onChange={handleImportCsvChange}
        style={{ display: "none" }}
      />
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Eventos
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {typeof total === "number" ? `${total} evento(s)` : "Listagem de eventos"}
          </Typography>
        </Box>
        <Box display="flex" gap={1}>
          <Button onClick={load} variant="outlined" disabled={loading} sx={{ textTransform: "none" }}>
            Atualizar
          </Button>
          <Button
            onClick={handleImportCsvClick}
            variant="outlined"
            disabled={loading || exporting || importing || !token}
            sx={{ textTransform: "none" }}
          >
            {importing ? "Importando..." : "Importar CSV"}
          </Button>
          <Button
            onClick={handleExportCsv}
            variant="outlined"
            disabled={loading || exporting || importing || !token}
            sx={{ textTransform: "none" }}
          >
            {exporting ? "Exportando..." : "Exportar CSV"}
          </Button>
          <Button
            component={RouterLink}
            to="/eventos/novo"
            variant="contained"
            sx={{ textTransform: "none", fontWeight: 800 }}
          >
            + Novo
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {domainsError && (
        <Alert severity="warning" variant="outlined" sx={{ mb: 2 }}>
          {domainsError}
        </Alert>
      )}

      {importSummary && (
        <Alert
          severity={importSummary.failed > 0 ? "warning" : "success"}
          variant="outlined"
          sx={{ mb: 2 }}
        >
          {`Importação concluída: ${importSummary.success} sucesso(s), ${importSummary.failed} erro(s).`}
          {importErrors.length > 0 && (
            <Box mt={1}>
              {importErrors.slice(0, 6).map((detail, index) => (
                <Typography key={`${detail}-${index}`} variant="body2" color="text.secondary">
                  {detail}
                </Typography>
              ))}
              {importErrors.length > 6 && (
                <Typography variant="body2" color="text.secondary">
                  {`...e mais ${importErrors.length - 6} erro(s).`}
                </Typography>
              )}
            </Box>
          )}
        </Alert>
      )}

      <Paper elevation={2} sx={{ borderRadius: 1, overflow: "hidden" }}>
        {loading ? (
          <Box
            sx={{
              p: 4,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 1,
            }}
          >
            <CircularProgress size={22} />
            <Typography variant="body2" color="text.secondary">
              Carregando...
            </Typography>
          </Box>
        ) : (
          <Table>
            <TableHead>
              <TableRow>
                <TableCell width={180}>Agência</TableCell>
                <TableCell width={260}>Nome</TableCell>
                <TableCell width={224}>Período</TableCell>
                <TableCell width={175}>Local</TableCell>
                <TableCell width={160}>Diretoria</TableCell>
                <TableCell width={136}>Investimento</TableCell>
                <TableCell width={140}>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((item) => {
                const agenciaLabel = item.agencia_id
                  ? agenciaById.get(item.agencia_id) || `#${item.agencia_id}`
                  : "-";
                const diretoriaLabel = item.diretoria_id
                  ? diretoriaById.get(item.diretoria_id) || `#${item.diretoria_id}`
                  : "-";
                return (
                  <EventoRow
                    key={item.id}
                    item={item}
                    agenciaLabel={agenciaLabel}
                    agencias={agencias}
                    diretoriaLabel={diretoriaLabel}
                    diretorias={diretorias}
                    statuses={statuses}
                    statusUpdating={statusUpdatingId === item.id}
                    onStatusChange={handleStatusChange}
                    inlineUpdating={Boolean(inlineUpdating[item.id])}
                    onInlineUpdate={handleInlineUpdate}
                  />
                );
              })}

              {!items.length && (
                <TableRow>
                  <TableCell colSpan={7}>
                    <Typography variant="body2" color="text.secondary">
                      Nenhum evento encontrado.
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        )}
      </Paper>

      <Box display="flex" justifyContent="space-between" alignItems="center" mt={2} gap={2}>
        <Stack direction="row" spacing={1} alignItems="center">
          <Typography variant="body2" color="text.secondary">
            Itens por página
          </Typography>
          <FormControl size="small">
            <Select
              value={String(limit)}
              onChange={(e) => {
                setLimit(Number(e.target.value));
                setPage(1);
              }}
            >
              {[10, 25, 50, 100].map((n) => (
                <MenuItem key={n} value={String(n)}>
                  {n}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Stack>

        {pageCount > 1 && (
          <Pagination
            count={pageCount}
            page={page}
            onChange={(_, next) => setPage(next)}
            color="primary"
            shape="rounded"
            showFirstButton
            showLastButton
            disabled={loading}
          />
        )}
      </Box>

    </Box>
  );
}
