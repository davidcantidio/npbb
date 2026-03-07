import { memo, useCallback, useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  CircularProgress,
  Divider,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  LinearProgress,
  Paper,
  Skeleton,
  Snackbar,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import { useLocation, useNavigate } from "react-router-dom";
import {
  atribuirCota,
  deleteAtivo,
  exportAtivosCsv,
  listAtivos,
  type AtivoListItem,
} from "../services/ativos";
import { useAuth } from "../store/auth";
import { listDiretorias, listEventos, type Diretoria } from "../services/eventos";

type EventoOption = {
  id: number;
  nome: string;
};

type Filters = {
  evento_id: number | null;
  diretoria_id: number | null;
  data: string;
};

const EMPTY_FILTERS: Filters = {
  evento_id: null,
  diretoria_id: null,
  data: "",
};

function parseNumericParam(value: string | null) {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
}

function parseFiltersFromSearch(search: string): Filters {
  const params = new URLSearchParams(search);
  return {
    evento_id: parseNumericParam(params.get("evento_id")),
    diretoria_id: parseNumericParam(params.get("diretoria_id")),
    data: params.get("data") || "",
  };
}

function buildSearchFromFilters(filters: Filters): string {
  const params = new URLSearchParams();
  if (filters.evento_id) params.set("evento_id", String(filters.evento_id));
  if (filters.diretoria_id) params.set("diretoria_id", String(filters.diretoria_id));
  if (filters.data) params.set("data", filters.data);
  return params.toString();
}

function areFiltersEqual(a: Filters, b: Filters) {
  return a.evento_id === b.evento_id && a.diretoria_id === b.diretoria_id && a.data === b.data;
}

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
    const lower = trimmed.toLowerCase();
    if (lower.includes("usuario agencia sem agencia_id")) {
      return "Acesso nao permitido para este usuario.";
    }
    if (lower.includes("not authenticated") || lower.includes("unauthorized") || lower.includes("forbidden")) {
      return "Voce nao tem permissao para acessar estes dados.";
    }
    if (lower.includes("internal server error") || lower.includes("status code")) {
      return fallback;
    }
    return trimmed;
  }
  return fallback;
}

function formatDiretoriaNome(value: string) {
  return value
    .replace(/_/g, " ")
    .trim()
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

type AtivoCardProps = {
  grupo: {
    evento_id: number;
    evento_nome: string;
    diretorias: AtivoListItem[];
  };
  onAssign: (item: AtivoListItem) => void;
  onDelete: (item: AtivoListItem) => void;
  onOpenIngressos: (item: AtivoListItem) => void;
};

const AtivoCard = memo(function AtivoCard({ grupo, onAssign, onDelete, onOpenIngressos }: AtivoCardProps) {
  return (
    <Paper
      elevation={2}
      sx={{
        p: 2.5,
        borderRadius: 2,
        display: "flex",
        flexDirection: "column",
        gap: 2,
      }}
    >
      <Box>
        <Typography variant="subtitle1" fontWeight={800}>
          {grupo.evento_nome}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {grupo.diretorias.length} diretoria(s)
        </Typography>
      </Box>

      <Stack spacing={1}>
        {grupo.diretorias.map((item) => {
          const disponiveis =
            typeof item.disponiveis === "number" ? item.disponiveis : Math.max(item.total - item.usados, 0);
          const rawPercentual =
            typeof item.percentual_usado === "number"
              ? item.percentual_usado
              : item.total > 0
                ? item.usados / item.total
                : 0;
          const percentual = Math.max(0, Math.min(rawPercentual, 1));
          const percentualLabel = `${Math.round(percentual * 100)}%`;
          const usageColor = percentual >= 0.8 ? "error" : percentual >= 0.5 ? "warning" : "success";

          return (
            <Box
              key={item.id}
              sx={{
                p: 1.25,
                borderRadius: 1.5,
                backgroundColor: "action.hover",
                cursor: "pointer",
              }}
              onClick={() => onOpenIngressos(item)}
            >
              <Box display="flex" alignItems="flex-start" justifyContent="space-between" gap={1}>
                <Typography variant="caption">
                  <Box component="span" sx={{ fontWeight: 700 }}>
                    {formatDiretoriaNome(item.diretoria_nome)}
                  </Box>
                  {" • "}
                  {disponiveis} disponiveis de {item.total}
                </Typography>
                <Box display="flex" alignItems="center" gap={0.5}>
                  <IconButton
                    size="small"
                    aria-label="Editar cota"
                    onClick={(event) => {
                      event.stopPropagation();
                      onAssign(item);
                    }}
                    sx={{ color: "text.secondary" }}
                  >
                    <EditOutlinedIcon fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    aria-label="Excluir cota"
                    onClick={(event) => {
                      event.stopPropagation();
                      onDelete(item);
                    }}
                    disabled={item.usados > 0}
                    sx={{
                      color: item.usados > 0 ? "action.disabled" : "error.main",
                    }}
                  >
                    <DeleteOutlineIcon fontSize="small" />
                  </IconButton>
                </Box>
              </Box>

              <Box display="flex" alignItems="center" gap={1} mt={0.75}>
                <Box sx={{ flex: 1, position: "relative" }}>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min(percentual * 100, 100)}
                    color={usageColor}
                    sx={{
                      height: 16,
                      borderRadius: 999,
                      backgroundColor: "rgba(0,0,0,0.12)",
                    }}
                  />
                  <Typography
                    variant="caption"
                    sx={{
                      position: "absolute",
                      inset: 0,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontWeight: 800,
                      color: percentual >= 0.45 ? "#fff" : "text.primary",
                      pointerEvents: "none",
                    }}
                  >
                    {item.usados}
                  </Typography>
                </Box>
                <Typography variant="caption" color="text.secondary" sx={{ minWidth: 40, textAlign: "right" }}>
                  {percentualLabel}
                </Typography>
              </Box>
            </Box>
          );
        })}
      </Stack>
    </Paper>
  );
});

export default function AtivosList() {
  const { token } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [items, setItems] = useState<AtivoListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState<number | null>(null);
  const [selected, setSelected] = useState<AtivoListItem | null>(null);
  const [quantidade, setQuantidade] = useState<string>("");
  const [saving, setSaving] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("Cota atualizada com sucesso.");
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [createEvento, setCreateEvento] = useState<EventoOption | null>(null);
  const [createDiretoria, setCreateDiretoria] = useState<Diretoria | null>(null);
  const [createQuantidade, setCreateQuantidade] = useState<string>("");
  const [createSaving, setCreateSaving] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<AtivoListItem | null>(null);
  const [deleteSaving, setDeleteSaving] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [filtersContainer, setFiltersContainer] = useState<HTMLElement | null>(null);
  const [filtersDraft, setFiltersDraft] = useState<Filters>(() => parseFiltersFromSearch(location.search));
  const [filtersApplied, setFiltersApplied] = useState<Filters>(() =>
    parseFiltersFromSearch(location.search),
  );
  const [eventoOptions, setEventoOptions] = useState<EventoOption[]>([]);
  const [diretorias, setDiretorias] = useState<Diretoria[]>([]);
  const [domainsLoading, setDomainsLoading] = useState(false);
  const hasActiveFilters =
    Boolean(filtersApplied.evento_id) ||
    Boolean(filtersApplied.diretoria_id) ||
    Boolean(filtersApplied.data);
  const hasDraftFilters =
    Boolean(filtersDraft.evento_id) ||
    Boolean(filtersDraft.diretoria_id) ||
    Boolean(filtersDraft.data);
  const selectedEvento = filtersDraft.evento_id
    ? eventoOptions.find((option) => option.id === filtersDraft.evento_id) || {
        id: filtersDraft.evento_id,
        nome: `#${filtersDraft.evento_id}`,
      }
    : null;
  const selectedDiretoria = filtersDraft.diretoria_id
    ? diretorias.find((option) => option.id === filtersDraft.diretoria_id) || {
        id: filtersDraft.diretoria_id,
        nome: `#${filtersDraft.diretoria_id}`,
      }
    : null;
  const showSkeletons = loading && items.length === 0;
  const showTopLoading = loading && items.length > 0;
  const quantidadeNumber = quantidade === "" ? null : Number(quantidade);
  const createQuantidadeNumber = createQuantidade === "" ? null : Number(createQuantidade);
  const usados = selected?.usados ?? 0;
  const isQuantidadeValid =
    quantidadeNumber !== null &&
    Number.isFinite(quantidadeNumber) &&
    quantidadeNumber >= 0 &&
    quantidadeNumber >= usados;
  const quantidadeError =
    quantidadeNumber === null
      ? "Informe a quantidade."
      : !Number.isFinite(quantidadeNumber) || quantidadeNumber < 0
        ? "Quantidade nao pode ser negativa."
        : quantidadeNumber < usados
          ? "Quantidade nao pode ser menor que os usados."
          : "";
  const isCreateValid =
    Boolean(createEvento) &&
    Boolean(createDiretoria) &&
    createQuantidadeNumber !== null &&
    Number.isFinite(createQuantidadeNumber) &&
    createQuantidadeNumber >= 0;
  const createQuantidadeError =
    createQuantidadeNumber === null
      ? "Informe a quantidade."
      : !Number.isFinite(createQuantidadeNumber) || createQuantidadeNumber < 0
        ? "Quantidade nao pode ser negativa."
        : "";

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const res = await listAtivos(token, {
        skip: 0,
        limit: 40,
        evento_id: filtersApplied.evento_id ?? undefined,
        diretoria_id: filtersApplied.diretoria_id ?? undefined,
        data: filtersApplied.data || undefined,
      });
      setItems(res.items);
      setTotal(res.total);
    } catch (err: any) {
      setError(getFriendlyErrorMessage(err, "Nao foi possivel carregar os ativos."));
    } finally {
      setLoading(false);
    }
  }, [token, filtersApplied]);

  const loadDomains = useCallback(async () => {
    if (!token) return;
    setDomainsLoading(true);
    try {
      const [eventosRes, diretoriasRes] = await Promise.all([
        listEventos(token, { skip: 0, limit: 200 }),
        listDiretorias(token),
      ]);
      const mappedEventos = eventosRes.items.map((evento) => ({
        id: evento.id,
        nome: evento.nome,
      }));
      setEventoOptions(mappedEventos);
      setDiretorias(diretoriasRes);
    } catch {
      setEventoOptions([]);
      setDiretorias([]);
    } finally {
      setDomainsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (!token) return;
    load();
  }, [token, load]);

  useEffect(() => {
    setFiltersContainer(document.getElementById("app-sidebar-slot"));
  }, []);

  useEffect(() => {
    const parsed = parseFiltersFromSearch(location.search);
    setFiltersApplied((prev) => (areFiltersEqual(prev, parsed) ? prev : parsed));
    setFiltersDraft((prev) => (areFiltersEqual(prev, parsed) ? prev : parsed));
  }, [location.search]);

  useEffect(() => {
    if (!token) return;
    loadDomains();
  }, [token, loadDomains]);

  const handleOpenModal = useCallback((item: AtivoListItem) => {
    setSelected(item);
    setQuantidade(String(item.total ?? 0));
    setModalError(null);
  }, []);

  const handleOpenDelete = useCallback((item: AtivoListItem) => {
    setDeleteTarget(item);
    setDeleteError(null);
  }, []);

  const handleOpenIngressos = useCallback(
    (item: AtivoListItem) => {
      navigate(`/ingressos?cota_id=${item.id}`);
    },
    [navigate],
  );

  const handleOpenCreate = () => {
    setCreateOpen(true);
    setCreateEvento(null);
    setCreateDiretoria(null);
    setCreateQuantidade("");
    setCreateError(null);
  };

  const handleCloseModal = () => {
    if (saving) return;
    setSelected(null);
    setQuantidade("");
    setModalError(null);
  };

  const handleCloseDelete = () => {
    if (deleteSaving) return;
    setDeleteTarget(null);
    setDeleteError(null);
  };

  const handleCloseCreate = () => {
    if (createSaving) return;
    setCreateOpen(false);
    setCreateError(null);
  };

  const handleQuantidadeChange = (value: string) => {
    if (value === "" || /^[0-9]+$/.test(value)) {
      setQuantidade(value);
    }
  };

  const handleCreateQuantidadeChange = (value: string) => {
    if (value === "" || /^[0-9]+$/.test(value)) {
      setCreateQuantidade(value);
    }
  };

  const handleSave = async () => {
    if (!token || !selected || !isQuantidadeValid || quantidadeNumber === null) return;
    setSaving(true);
    setModalError(null);
    const updatedTotal = quantidadeNumber;
    const rollbackItem = items.find((item) => item.id === selected.id) || null;
    if (rollbackItem) {
      const prevUsados = rollbackItem.usados;
      const nextDisponiveis = Math.max(updatedTotal - prevUsados, 0);
      const nextPercentual = updatedTotal > 0 ? prevUsados / updatedTotal : 0;
      const optimistic = {
        ...rollbackItem,
        total: updatedTotal,
        disponiveis: nextDisponiveis,
        percentual_usado: nextPercentual,
      };
      setItems((prev) => prev.map((item) => (item.id === optimistic.id ? optimistic : item)));
    }
    try {
      const updated = await atribuirCota(token, {
        evento_id: selected.evento_id,
        diretoria_id: selected.diretoria_id,
        quantidade: quantidadeNumber,
      });
      setItems((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
      setSelected(null);
      setQuantidade("");
      setSnackbarMessage("Cota atualizada com sucesso.");
      setSnackbarOpen(true);
    } catch (err: any) {
      if (rollbackItem) {
        setItems((prev) =>
          prev.map((item) => (item.id === rollbackItem.id ? rollbackItem : item)),
        );
      }
      setModalError(getFriendlyErrorMessage(err, "Nao foi possivel salvar a cota."));
    } finally {
      setSaving(false);
    }
  };

  const handleCreate = async () => {
    if (!token || !createEvento || !createDiretoria || !isCreateValid || createSaving) return;
    setCreateSaving(true);
    setCreateError(null);
    try {
      await atribuirCota(token, {
        evento_id: createEvento.id,
        diretoria_id: createDiretoria.id,
        quantidade: Number(createQuantidadeNumber),
      });
      setCreateOpen(false);
      setCreateEvento(null);
      setCreateDiretoria(null);
      setCreateQuantidade("");
      setSnackbarMessage("Ativo criado com sucesso.");
      setSnackbarOpen(true);
      await load();
    } catch (err: any) {
      setCreateError(getFriendlyErrorMessage(err, "Nao foi possivel criar o ativo."));
    } finally {
      setCreateSaving(false);
    }
  };

  const handleExport = async () => {
    if (!token || exporting) return;
    setExporting(true);
    setExportError(null);
    try {
      const { blob, filename } = await exportAtivosCsv(token, {
        evento_id: filtersApplied.evento_id ?? undefined,
        diretoria_id: filtersApplied.diretoria_id ?? undefined,
        data: filtersApplied.data || undefined,
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      const message = getFriendlyErrorMessage(
        err,
        "Nao foi possivel exportar o CSV. Ajuste os filtros e tente novamente.",
      );
      const lower = message.toLowerCase();
      if (lower.includes("limite de exportacao")) {
        setExportError("Limite de exportacao excedido. Ajuste os filtros e tente novamente.");
      } else {
        setExportError(message);
      }
    } finally {
      setExporting(false);
    }
  };

  const handleDelete = async () => {
    if (!token || !deleteTarget || deleteSaving) return;
    setDeleteSaving(true);
    setDeleteError(null);
    try {
      await deleteAtivo(token, deleteTarget.id);
      setItems((prev) => prev.filter((item) => item.id !== deleteTarget.id));
      setTotal((prev) =>
        typeof prev === "number" ? Math.max(prev - 1, 0) : prev,
      );
      setDeleteTarget(null);
      setSnackbarMessage("Ativo excluido com sucesso.");
      setSnackbarOpen(true);
    } catch (err: any) {
      setDeleteError(getFriendlyErrorMessage(err, "Nao foi possivel excluir o ativo."));
    } finally {
      setDeleteSaving(false);
    }
  };

  const updateSearch = useCallback(
    (filters: Filters) => {
      const qs = buildSearchFromFilters(filters);
      const nextSearch = qs ? `?${qs}` : "";
      if (nextSearch === location.search) return;
      navigate({ pathname: location.pathname, search: nextSearch }, { replace: true });
    },
    [location.pathname, location.search, navigate],
  );

  const handleApplyFilters = () => {
    setFiltersApplied(filtersDraft);
    updateSearch(filtersDraft);
  };

  const handleClearFilters = () => {
    setFiltersDraft(EMPTY_FILTERS);
    setFiltersApplied(EMPTY_FILTERS);
    updateSearch(EMPTY_FILTERS);
  };

  const filtersPanel = (
    <Stack spacing={2}>
      <Typography variant="subtitle2" fontWeight={800}>
        Filtros
      </Typography>
      <Autocomplete
        options={eventoOptions}
        value={selectedEvento}
        loading={domainsLoading}
        onChange={(_, value) =>
          setFiltersDraft((prev) => ({ ...prev, evento_id: value ? value.id : null }))
        }
        isOptionEqualToValue={(option, value) => option.id === value.id}
        getOptionLabel={(option) => option.nome}
        renderInput={(params) => (
          <TextField
            {...params}
            label="Evento"
            size="small"
            InputProps={{
              ...params.InputProps,
              endAdornment: (
                <>
                  {domainsLoading ? <CircularProgress size={16} /> : null}
                  {params.InputProps.endAdornment}
                </>
              ),
            }}
          />
        )}
        noOptionsText="Nenhum evento encontrado"
      />
      <Autocomplete
        options={diretorias}
        value={selectedDiretoria}
        loading={domainsLoading}
        onChange={(_, value) =>
          setFiltersDraft((prev) => ({ ...prev, diretoria_id: value ? value.id : null }))
        }
        isOptionEqualToValue={(option, value) => option.id === value.id}
        getOptionLabel={(option) => option.nome}
        renderInput={(params) => (
          <TextField
            {...params}
            label="Diretoria"
            size="small"
            InputProps={{
              ...params.InputProps,
              endAdornment: (
                <>
                  {domainsLoading ? <CircularProgress size={16} /> : null}
                  {params.InputProps.endAdornment}
                </>
              ),
            }}
          />
        )}
        noOptionsText="Nenhuma diretoria encontrada"
      />
      <TextField
        label="Data do evento"
        type="date"
        size="small"
        value={filtersDraft.data}
        onChange={(e) => setFiltersDraft((prev) => ({ ...prev, data: e.target.value }))}
        InputLabelProps={{ shrink: true }}
      />
      {!domainsLoading && eventoOptions.length === 0 && diretorias.length === 0 ? (
        <Typography variant="caption" color="text.secondary">
          Nenhuma opcao disponivel no momento.
        </Typography>
      ) : null}
      <Stack direction="row" spacing={1}>
        <Button
          variant="contained"
          sx={{ textTransform: "none", fontWeight: 700 }}
          onClick={handleApplyFilters}
          disabled={loading}
        >
          Aplicar
        </Button>
        <Button
          variant="outlined"
          sx={{ textTransform: "none", fontWeight: 700 }}
          onClick={handleClearFilters}
          disabled={!hasActiveFilters && !hasDraftFilters}
        >
          Limpar
        </Button>
      </Stack>
      <Divider />
      <Stack spacing={1}>
        <Typography variant="subtitle2" fontWeight={800}>
          Acoes
        </Typography>
        <Button
          variant="outlined"
          sx={{ textTransform: "none", fontWeight: 700 }}
          disabled={exporting}
          onClick={handleExport}
        >
          {exporting ? "Exportando..." : "Exportar CSV"}
        </Button>
        {exportError ? (
          <Alert
            severity="error"
            variant="outlined"
            action={
              <Button
                color="inherit"
                size="small"
                onClick={handleExport}
                disabled={exporting}
              >
                Tentar novamente
              </Button>
            }
          >
            {exportError}
          </Alert>
        ) : null}
      </Stack>
    </Stack>
  );

  const filtersPortal = filtersContainer ? createPortal(filtersPanel, filtersContainer) : null;
  const groupedItems = useMemo(() => {
    const grouped = new Map<number, { evento_id: number; evento_nome: string; diretorias: AtivoListItem[] }>();
    for (const item of items) {
      const current = grouped.get(item.evento_id);
      if (!current) {
        grouped.set(item.evento_id, {
          evento_id: item.evento_id,
          evento_nome: item.evento_nome,
          diretorias: [item],
        });
        continue;
      }
      current.diretorias.push(item);
    }

    return Array.from(grouped.values())
      .map((grupo) => ({
        ...grupo,
        diretorias: [...grupo.diretorias].sort((a, b) => {
          const nomeCompare = a.diretoria_nome.localeCompare(b.diretoria_nome);
          if (nomeCompare !== 0) return nomeCompare;
          return a.id - b.id;
        }),
      }))
      .sort((a, b) => {
        const nomeCompare = a.evento_nome.localeCompare(b.evento_nome);
        if (nomeCompare !== 0) return nomeCompare;
        return a.evento_id - b.evento_id;
      });
  }, [items]);

  const cardsGrid = useMemo(() => {
    if (showSkeletons) {
      return Array.from({ length: 4 }).map((_, index) => (
        <Paper
          key={`skeleton-${index}`}
          elevation={2}
          sx={{ p: 2.5, borderRadius: 2, display: "flex", flexDirection: "column", gap: 2 }}
        >
          <Box>
            <Skeleton variant="text" width="70%" height={24} />
            <Skeleton variant="text" width="50%" height={16} />
          </Box>
          <Box>
            <Skeleton variant="text" width="60%" height={18} />
            <Skeleton variant="text" width="40%" height={14} />
            <Skeleton variant="rectangular" height={8} sx={{ mt: 1, borderRadius: 999 }} />
          </Box>
          <Skeleton variant="rectangular" height={36} sx={{ borderRadius: 2 }} />
        </Paper>
      ));
    }

    return groupedItems.map((grupo) => (
      <AtivoCard
        key={grupo.evento_id}
        grupo={grupo}
        onAssign={handleOpenModal}
        onDelete={handleOpenDelete}
        onOpenIngressos={handleOpenIngressos}
      />
    ));
  }, [groupedItems, handleOpenDelete, handleOpenModal, handleOpenIngressos, showSkeletons]);

  return (
    <>
      {filtersPortal}
      <Box sx={{ width: "100%" }}>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", sm: "center" }}
        flexDirection={{ xs: "column", sm: "row" }}
        gap={1.5}
        mb={2}
      >
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Ativos
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {typeof total === "number" ? `${total} ativo(s)` : "Cotas por evento e diretoria"}
          </Typography>
        </Box>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={1} width={{ xs: "100%", sm: "auto" }}>
          <Button
            variant="outlined"
            sx={{ textTransform: "none", width: { xs: "100%", sm: "auto" } }}
            onClick={load}
            disabled={loading}
          >
            Atualizar
          </Button>
          <Button
            variant="contained"
            sx={{ textTransform: "none", fontWeight: 800, width: { xs: "100%", sm: "auto" } }}
            onClick={handleOpenCreate}
          >
            + Novo
          </Button>
        </Stack>
      </Box>
      {showTopLoading ? (
        <Box sx={{ mb: 2 }}>
          <LinearProgress />
        </Box>
      ) : null}

      {error ? (
        <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="subtitle1" fontWeight={800} gutterBottom>
            Nao foi possivel carregar os ativos
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {error}
          </Typography>
          <Button
            variant="contained"
            sx={{ textTransform: "none", fontWeight: 700 }}
            onClick={load}
            disabled={loading}
          >
            Tentar novamente
          </Button>
          <Button
            variant="text"
            sx={{ textTransform: "none", fontWeight: 700, ml: 1 }}
            onClick={handleClearFilters}
            disabled={loading}
          >
            Limpar filtros
          </Button>
        </Paper>
      ) : !loading && items.length === 0 ? (
        <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="subtitle1" fontWeight={800} gutterBottom>
            Nenhum ativo encontrado
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Ajuste os filtros ou limpe para ver todos os ativos.
          </Typography>
          <Button
            variant="outlined"
            sx={{ textTransform: "none", fontWeight: 700 }}
            onClick={handleClearFilters}
          >
            Limpar filtros
          </Button>
        </Paper>
      ) : (
        <Box
          sx={{
            display: "grid",
            gap: { xs: 1.5, sm: 2 },
            gridTemplateColumns: {
              xs: "1fr",
              sm: "repeat(2, minmax(0, 1fr))",
              lg: "repeat(3, minmax(0, 1fr))",
              xl: "repeat(4, minmax(0, 1fr))",
            },
          }}
        >
          {cardsGrid}
        </Box>
      )}

      <Dialog open={Boolean(selected)} onClose={handleCloseModal} fullWidth maxWidth="sm">
        <DialogTitle>Atribuir ingressos</DialogTitle>
        <DialogContent sx={{ pt: 1, display: "flex", flexDirection: "column", gap: 2 }}>
          <Box>
            <Typography variant="subtitle1" fontWeight={800}>
              {selected?.evento_nome || "-"}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Diretoria: {selected?.diretoria_nome || "-"}
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Total atual: {selected?.total ?? "-"} | Usados: {selected?.usados ?? "-"}
          </Typography>
          <TextField
            label="Nova quantidade total"
            type="number"
            value={quantidade}
            onChange={(e) => handleQuantidadeChange(e.target.value)}
            inputProps={{ min: 0, step: 1, inputMode: "numeric" }}
            error={Boolean(quantidadeError)}
            helperText={quantidadeError || "Nao pode ser menor que os usados."}
            fullWidth
          />
          {modalError ? (
            <Alert severity="error" variant="outlined">
              {modalError}
            </Alert>
          ) : null}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button
            variant="outlined"
            onClick={handleCloseModal}
            sx={{ textTransform: "none" }}
            disabled={saving}
          >
            Cancelar
          </Button>
          <Button
            variant="contained"
            sx={{ textTransform: "none", fontWeight: 700 }}
            disabled={!isQuantidadeValid}
            onClick={handleSave}
          >
            {saving ? "Salvando..." : "Salvar"}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={createOpen} onClose={handleCloseCreate} fullWidth maxWidth="sm">
        <DialogTitle>Novo ativo</DialogTitle>
        <DialogContent sx={{ pt: 1, display: "flex", flexDirection: "column", gap: 2 }}>
          <Autocomplete
            options={eventoOptions}
            value={createEvento}
            loading={domainsLoading}
            onChange={(_, value) => setCreateEvento(value)}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            getOptionLabel={(option) => option.nome}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Evento"
                size="small"
                InputProps={{
                  ...params.InputProps,
                  endAdornment: (
                    <>
                      {domainsLoading ? <CircularProgress size={16} /> : null}
                      {params.InputProps.endAdornment}
                    </>
                  ),
                }}
              />
            )}
            noOptionsText="Nenhum evento encontrado"
          />
          <Autocomplete
            options={diretorias}
            value={createDiretoria}
            loading={domainsLoading}
            onChange={(_, value) => setCreateDiretoria(value)}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            getOptionLabel={(option) => option.nome}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Diretoria"
                size="small"
                InputProps={{
                  ...params.InputProps,
                  endAdornment: (
                    <>
                      {domainsLoading ? <CircularProgress size={16} /> : null}
                      {params.InputProps.endAdornment}
                    </>
                  ),
                }}
              />
            )}
            noOptionsText="Nenhuma diretoria encontrada"
          />
          <TextField
            label="Quantidade total"
            type="number"
            value={createQuantidade}
            onChange={(e) => handleCreateQuantidadeChange(e.target.value)}
            inputProps={{ min: 0, step: 1, inputMode: "numeric" }}
            error={Boolean(createQuantidadeError)}
            helperText={createQuantidadeError || "Informe a quantidade total inicial."}
            fullWidth
          />
          {createError ? (
            <Alert severity="error" variant="outlined">
              {createError}
            </Alert>
          ) : null}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button
            variant="outlined"
            onClick={handleCloseCreate}
            sx={{ textTransform: "none" }}
            disabled={createSaving}
          >
            Cancelar
          </Button>
          <Button
            variant="contained"
            sx={{ textTransform: "none", fontWeight: 700 }}
            disabled={!isCreateValid || createSaving}
            onClick={handleCreate}
          >
            {createSaving ? "Criando..." : "Criar ativo"}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(deleteTarget)} onClose={handleCloseDelete} fullWidth maxWidth="sm">
        <DialogTitle>Excluir ativo</DialogTitle>
        <DialogContent sx={{ pt: 1, display: "flex", flexDirection: "column", gap: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Esta acao remove a cota selecionada. Essa operacao nao pode ser desfeita.
          </Typography>
          <Box>
            <Typography variant="subtitle2" fontWeight={800}>
              {deleteTarget?.evento_nome || "-"}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Diretoria: {deleteTarget?.diretoria_nome || "-"}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Usados: {deleteTarget?.usados ?? "-"}
            </Typography>
          </Box>
          {deleteTarget && deleteTarget.usados > 0 ? (
            <Alert severity="warning" variant="outlined">
              Nao e possivel excluir uma cota com solicitacoes emitidas.
            </Alert>
          ) : null}
          {deleteError ? (
            <Alert severity="error" variant="outlined">
              {deleteError}
            </Alert>
          ) : null}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button
            variant="outlined"
            onClick={handleCloseDelete}
            sx={{ textTransform: "none" }}
            disabled={deleteSaving}
          >
            Cancelar
          </Button>
          <Button
            variant="contained"
            color="error"
            sx={{ textTransform: "none", fontWeight: 700 }}
            disabled={deleteSaving || Boolean(deleteTarget && deleteTarget.usados > 0)}
            onClick={handleDelete}
          >
            {deleteSaving ? "Excluindo..." : "Excluir"}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert onClose={() => setSnackbarOpen(false)} severity="success" variant="filled">
          {snackbarMessage}
        </Alert>
      </Snackbar>
      </Box>
    </>
  );
}
