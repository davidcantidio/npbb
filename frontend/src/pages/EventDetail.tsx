import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Divider,
  IconButton,
  Link,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import { Link as RouterLink, useNavigate, useParams } from "react-router-dom";
import QrCode2Icon from "@mui/icons-material/QrCode2";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import DeleteOutlineOutlinedIcon from "@mui/icons-material/DeleteOutlineOutlined";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";

import { Agencia, listAgencias } from "../services/agencias";
import { useAuth } from "../store/auth";
import {
  DivisaoDemandante,
  Diretoria,
  EventoRead,
  StatusEvento,
  SubtipoEvento,
  Tag,
  Territorio,
  TipoEvento,
  deleteEvento,
  getEvento,
  listDivisoesDemandantes,
  listDiretorias,
  listStatusEvento,
  listSubtiposEvento,
  listTags,
  listTerritorios,
  listTiposEvento,
} from "../services/eventos";

function formatDate(value?: string | null) {
  if (!value) return "-";
  const [y, m, d] = value.split("-");
  if (!y || !m || !d) return value;
  return `${d}/${m}/${y}`;
}

function formatCurrency(value?: string | number | null) {
  if (value == null || value === "") return "-";
  const numeric = typeof value === "number" ? value : Number(String(value).replace(",", "."));
  if (!Number.isFinite(numeric)) return String(value);
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(numeric);
}

function statusChipColor(nome?: string) {
  switch (String(nome || "").toLowerCase()) {
    case "previsto":
      return "default" as const;
    case "a confirmar":
      return "warning" as const;
    case "confirmado":
      return "info" as const;
    case "realizado":
      return "success" as const;
    case "cancelado":
      return "error" as const;
    default:
      return "default" as const;
  }
}

export default function EventDetail() {
  const navigate = useNavigate();
  const { id } = useParams();
  const eventoId = Number(id);
  const { token } = useAuth();

  const [evento, setEvento] = useState<EventoRead | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [domainsLoading, setDomainsLoading] = useState(false);
  const [domainsError, setDomainsError] = useState<string | null>(null);

  const [agencias, setAgencias] = useState<Agencia[]>([]);
  const [diretorias, setDiretorias] = useState<Diretoria[]>([]);
  const [divisoes, setDivisoes] = useState<DivisaoDemandante[]>([]);
  const [tipos, setTipos] = useState<TipoEvento[]>([]);
  const [subtipos, setSubtipos] = useState<SubtipoEvento[]>([]);
  const [territorios, setTerritorios] = useState<Territorio[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [statuses, setStatuses] = useState<StatusEvento[]>([]);

  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const load = useCallback(async () => {
    if (!token || !Number.isFinite(eventoId)) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getEvento(token, eventoId);
      setEvento(data);
    } catch (err: any) {
      setError(err?.message || "Erro ao carregar evento");
    } finally {
      setLoading(false);
    }
  }, [token, eventoId]);

  useEffect(() => {
    load();
  }, [load]);

  const loadDomains = useCallback(async () => {
    if (!token) return;
    setDomainsLoading(true);
    setDomainsError(null);

    try {
      const [agenciasRes, diretoriasRes, divisoesRes, tiposRes, territoriosRes, tagsRes, statusRes] =
        await Promise.allSettled([
          listAgencias({ limit: 200 }),
          listDiretorias(token),
          listDivisoesDemandantes(token),
          listTiposEvento(token),
          listTerritorios(token),
          listTags(token),
          listStatusEvento(token),
        ]);

      const failures: string[] = [];
      if (agenciasRes.status === "fulfilled") setAgencias(agenciasRes.value);
      else failures.push("agencias");

      if (diretoriasRes.status === "fulfilled") setDiretorias(diretoriasRes.value);
      else failures.push("diretorias");

      if (divisoesRes.status === "fulfilled") setDivisoes(divisoesRes.value);
      else failures.push("divisoes");

      if (tiposRes.status === "fulfilled") setTipos(tiposRes.value);
      else failures.push("tipos");

      if (territoriosRes.status === "fulfilled") setTerritorios(territoriosRes.value);
      else failures.push("territorios");

      if (tagsRes.status === "fulfilled") setTags(tagsRes.value);
      else failures.push("tags");

      if (statusRes.status === "fulfilled") setStatuses(statusRes.value);
      else failures.push("status");

      if (failures.length) setDomainsError(`Falha ao carregar domínios: ${failures.join(", ")}`);
    } finally {
      setDomainsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadDomains();
  }, [loadDomains]);

  useEffect(() => {
    if (!token || !evento?.tipo_id) return;
    let cancelled = false;
    listSubtiposEvento(token, { tipo_id: evento.tipo_id })
      .then((items) => {
        if (!cancelled) setSubtipos(items);
      })
      .catch(() => {
        if (!cancelled) setSubtipos([]);
      });
    return () => {
      cancelled = true;
    };
  }, [token, evento?.tipo_id]);

  const agenciaLabel = useMemo(() => {
    if (!evento) return "-";
    const a = agencias.find((ag) => ag.id === evento.agencia_id);
    return a ? `${a.nome}` : `#${evento.agencia_id}`;
  }, [agencias, evento]);

  const diretoriaLabel = useMemo(() => {
    if (!evento?.diretoria_id) return "-";
    const d = diretorias.find((dir) => dir.id === evento.diretoria_id);
    return d ? d.nome : `#${evento.diretoria_id}`;
  }, [diretorias, evento?.diretoria_id]);

  const divisaoLabel = useMemo(() => {
    if (!evento?.divisao_demandante_id) return "-";
    const d = divisoes.find((div) => div.id === evento.divisao_demandante_id);
    return d ? d.nome : `#${evento.divisao_demandante_id}`;
  }, [divisoes, evento?.divisao_demandante_id]);

  const tipoLabel = useMemo(() => {
    if (!evento) return "-";
    const t = tipos.find((tipo) => tipo.id === evento.tipo_id);
    return t ? t.nome : `#${evento.tipo_id}`;
  }, [tipos, evento]);

  const subtipoLabel = useMemo(() => {
    if (!evento?.subtipo_id) return "-";
    const s = subtipos.find((sub) => sub.id === evento.subtipo_id);
    return s ? s.nome : `#${evento.subtipo_id}`;
  }, [subtipos, evento?.subtipo_id]);

  const statusNome = useMemo(() => {
    if (!evento) return null;
    return statuses.find((s) => s.id === evento.status_id)?.nome ?? null;
  }, [statuses, evento]);

  const tagLabels = useMemo(() => {
    if (!evento) return [];
    const byId = new Map(tags.map((t) => [t.id, t.nome]));
    return (evento.tag_ids || []).map((idNum) => byId.get(idNum) || `#${idNum}`);
  }, [tags, evento]);

  const territorioLabels = useMemo(() => {
    if (!evento) return [];
    const byId = new Map(territorios.map((t) => [t.id, t.nome]));
    return (evento.territorio_ids || []).map((idNum) => byId.get(idNum) || `#${idNum}`);
  }, [territorios, evento]);

  if (!Number.isFinite(eventoId)) {
    return (
      <Box sx={{ width: "100%" }}>
        <Alert severity="error" variant="filled">
          ID de evento inválido.
        </Alert>
      </Box>
    );
  }

  const statusLabel = statusNome || (evento ? `#${evento.status_id}` : "-");
  const statusColor = statusChipColor(statusNome || undefined);

  return (
    <Box sx={{ width: "100%" }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2} gap={2}>
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Evento
          </Typography>
          <Stack direction="row" spacing={1} alignItems="center" sx={{ pt: 0.5 }}>
            <Typography variant="body2" color="text.secondary">
              #{eventoId}
            </Typography>
            {evento && <Chip label={statusLabel} color={statusColor} size="small" />}
          </Stack>
        </Box>

        <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" justifyContent="flex-end">
          <Button
            component={RouterLink}
            to="/eventos"
            variant="outlined"
            startIcon={<ArrowBackIcon />}
            sx={{ textTransform: "none" }}
          >
            Voltar
          </Button>
          <Button
            component={RouterLink}
            to={`/eventos/${eventoId}/editar`}
            variant="contained"
            startIcon={<EditOutlinedIcon />}
            disabled={!evento || loading}
            sx={{ textTransform: "none", fontWeight: 800 }}
          >
            Editar
          </Button>
          <Button
            component={RouterLink}
            to={`/eventos/${eventoId}/formulario-lead`}
            variant="outlined"
            disabled={!evento || loading}
            sx={{ textTransform: "none", fontWeight: 800 }}
          >
            Formulário de Lead
          </Button>
          <Button
            component={RouterLink}
            to={`/eventos/${eventoId}/gamificacao`}
            variant="outlined"
            disabled={!evento || loading}
            sx={{ textTransform: "none", fontWeight: 800 }}
          >
            Gamificação
          </Button>
          <Button
            color="error"
            variant="contained"
            startIcon={<DeleteOutlineOutlinedIcon />}
            disabled={!evento || deleting}
            onClick={() => setDeleteOpen(true)}
            sx={{ textTransform: "none", fontWeight: 800 }}
          >
            Excluir
          </Button>
        </Stack>
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

      <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
        {loading ? (
          <Stack direction="row" spacing={1} alignItems="center">
            <CircularProgress size={22} />
            <Typography variant="body2" color="text.secondary">
              Carregando...
            </Typography>
          </Stack>
        ) : evento ? (
          <Stack spacing={2.5}>
            <Box display="flex" justifyContent="space-between" alignItems="flex-start" gap={2}>
              <Box>
                <Typography variant="h5" fontWeight={900} gutterBottom>
                  {evento.nome}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Atualizado em {new Date(evento.updated_at).toLocaleString("pt-BR")}
                </Typography>
              </Box>

              {evento.qr_code_url ? (
                <TooltipQrLink url={evento.qr_code_url} />
              ) : (
                <Typography variant="body2" color="text.secondary">
                  QRCode: -
                </Typography>
              )}
            </Box>

            <Divider />

            <Stack direction={{ xs: "column", md: "row" }} spacing={3}>
              <Box flex={1}>
                <Info label="Agência" value={agenciaLabel} />
                <Info label="Diretoria" value={diretoriaLabel} />
                <Info label="Divisão demandante" value={divisaoLabel} />
                <Info label="Tipo de evento" value={tipoLabel} />
                <Info label="Subtipo" value={subtipoLabel} />
                <Info label="Investimento" value={formatCurrency(evento.investimento)} />
              </Box>
              <Box flex={1}>
                <Info label="UF" value={String(evento.estado || "-").toUpperCase()} />
                <Info label="Cidade" value={evento.cidade || "-"} />
                <Info
                  label="Início previsto"
                  value={formatDate(evento.data_inicio_prevista)}
                />
                <Info label="Fim previsto" value={formatDate(evento.data_fim_prevista)} />
                <Info
                  label="Início realizado"
                  value={formatDate(evento.data_inicio_realizada)}
                />
                <Info label="Fim realizado" value={formatDate(evento.data_fim_realizada)} />
              </Box>
            </Stack>

            <Divider />

            <Box>
              <Typography variant="subtitle2" fontWeight={800} gutterBottom>
                Descrição
              </Typography>
              <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
                {evento.descricao}
              </Typography>
            </Box>

            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <Box flex={1}>
                <Typography variant="subtitle2" fontWeight={800} gutterBottom>
                  Territórios
                </Typography>
                {territorioLabels.length ? (
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    {territorioLabels.map((label) => (
                      <Chip key={label} label={label} size="small" />
                    ))}
                  </Stack>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    -
                  </Typography>
                )}
              </Box>

              <Box flex={1}>
                <Typography variant="subtitle2" fontWeight={800} gutterBottom>
                  Tags
                </Typography>
                {tagLabels.length ? (
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    {tagLabels.map((label) => (
                      <Chip key={label} label={label} size="small" />
                    ))}
                  </Stack>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    -
                  </Typography>
                )}
              </Box>
            </Stack>

            {domainsLoading && (
              <Typography variant="body2" color="text.secondary">
                Carregando domínios...
              </Typography>
            )}
          </Stack>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Nenhum dado para exibir.
          </Typography>
        )}
      </Paper>

      <Dialog open={deleteOpen} onClose={() => (deleting ? null : setDeleteOpen(false))}>
        <DialogTitle>Excluir evento</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {evento ? `Tem certeza que deseja excluir o evento "${evento.nome}"?` : "Tem certeza?"}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteOpen(false)} disabled={deleting}>
            Cancelar
          </Button>
          <Button
            color="error"
            variant="contained"
            disabled={!token || deleting}
            onClick={async () => {
              if (!token) return;
              setDeleting(true);
              setError(null);
              try {
                await deleteEvento(token, eventoId);
                navigate("/eventos", { replace: true });
              } catch (err: any) {
                setError(err?.message || "Erro ao excluir evento");
              } finally {
                setDeleting(false);
                setDeleteOpen(false);
              }
            }}
          >
            {deleting ? "Excluindo..." : "Excluir"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <Box sx={{ mb: 1.5 }}>
      <Typography variant="caption" color="text.secondary" display="block">
        {label}
      </Typography>
      <Typography variant="body2" fontWeight={700}>
        {value}
      </Typography>
    </Box>
  );
}

function TooltipQrLink({ url }: { url: string }) {
  return (
    <Stack direction="row" spacing={0.5} alignItems="center">
      <IconButton component="a" href={url} target="_blank" rel="noreferrer" size="small">
        <QrCode2Icon fontSize="small" />
      </IconButton>
      <Link href={url} target="_blank" rel="noreferrer" underline="hover" fontSize={13}>
        Abrir QRCode
      </Link>
    </Stack>
  );
}
