import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  Grid,
  TextField,
  Typography,
} from "@mui/material";
import { useAuth } from "../store/auth";
import { listEventos, EventoListItem } from "../services/eventos";
import { getDashboardLeadsReport, DashboardLeadsReportResponse } from "../services/dashboard_leads";

type Filters = {
  eventoId: number | null;
  eventoNome: string;
  dataInicio: string;
  dataFim: string;
};

function MetricCard({ title, value, subtitle }: { title: string; value: string; subtitle?: string }) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="caption" color="text.secondary">
          {title}
        </Typography>
        <Typography variant="h5" fontWeight={800} sx={{ mt: 0.5 }}>
          {value}
        </Typography>
        {subtitle ? (
          <Typography variant="caption" color="text.secondary">
            {subtitle}
          </Typography>
        ) : null}
      </CardContent>
    </Card>
  );
}

function BarRow({ label, total, percent }: { label: string; total: number; percent: number }) {
  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
      <Box sx={{ minWidth: 90 }}>
        <Typography variant="caption" fontWeight={700}>
          {label}
        </Typography>
      </Box>
      <Box sx={{ flex: 1, height: 10, borderRadius: 999, bgcolor: "grey.200" }}>
        <Box
          sx={{
            height: "100%",
            borderRadius: 999,
            bgcolor: "primary.main",
            width: `${Math.min(Math.max(percent, 0), 100)}%`,
          }}
        />
      </Box>
      <Typography variant="caption" sx={{ minWidth: 80, textAlign: "right" }}>
        {total} ({percent.toFixed(1)}%)
      </Typography>
    </Box>
  );
}

export default function DashboardLeads() {
  const { token } = useAuth();
  const [eventos, setEventos] = useState<EventoListItem[]>([]);
  const [filters, setFilters] = useState<Filters>({
    eventoId: null,
    eventoNome: "",
    dataInicio: "",
    dataFim: "",
  });
  const [draft, setDraft] = useState(filters);
  const [loadingEventos, setLoadingEventos] = useState(false);
  const [loadingReport, setLoadingReport] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<DashboardLeadsReportResponse | null>(null);

  useEffect(() => {
    if (!token) return;
    setLoadingEventos(true);
    listEventos(token, { limit: 200 })
      .then((data) => setEventos(data.items))
      .catch((err: any) => setError(err?.message || "Falha ao carregar eventos"))
      .finally(() => setLoadingEventos(false));
  }, [token]);

  const selectedEvento = useMemo(
    () => eventos.find((item) => item.id === draft.eventoId) || null,
    [eventos, draft.eventoId],
  );

  const canApply = Boolean(draft.eventoId || draft.eventoNome.trim());

  const applyFilters = async () => {
    if (!token || !canApply) return;
    setLoadingReport(true);
    setError(null);
    try {
      const data = await getDashboardLeadsReport(token, {
        evento_id: draft.eventoId || undefined,
        evento_nome: draft.eventoId ? undefined : draft.eventoNome.trim(),
        data_inicio: draft.dataInicio || undefined,
        data_fim: draft.dataFim || undefined,
      });
      setReport(data);
      setFilters(draft);
    } catch (err: any) {
      setError(err?.message || "Nao foi possivel carregar o dashboard");
    } finally {
      setLoadingReport(false);
    }
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <Box>
        <Typography variant="h5" fontWeight={800}>
          Dashboard - Leads
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Analises agregadas do Festival TMJ 2025 (sem PII).
        </Typography>
      </Box>

      <Card variant="outlined">
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <Autocomplete
                options={eventos}
                value={selectedEvento}
                loading={loadingEventos}
                getOptionLabel={(option) => option.nome}
                isOptionEqualToValue={(option, value) => option.id === value.id}
                onChange={(_, value) =>
                  setDraft((prev) => ({
                    ...prev,
                    eventoId: value ? value.id : null,
                    eventoNome: value ? "" : prev.eventoNome,
                  }))
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Evento"
                    placeholder="Selecione um evento"
                    helperText="Prioriza evento_id quando selecionado"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                label="Evento (nome)"
                value={draft.eventoNome}
                placeholder="Festival TMJ 2025"
                onChange={(e) => setDraft((prev) => ({ ...prev, eventoNome: e.target.value }))}
                disabled={Boolean(draft.eventoId)}
                fullWidth
                helperText="Fallback quando evento_id nao estiver disponivel"
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                label="Data inicio"
                type="date"
                value={draft.dataInicio}
                onChange={(e) => setDraft((prev) => ({ ...prev, dataInicio: e.target.value }))}
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                label="Data fim"
                type="date"
                value={draft.dataFim}
                onChange={(e) => setDraft((prev) => ({ ...prev, dataFim: e.target.value }))}
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={12} sx={{ display: "flex", gap: 1 }}>
              <Button variant="contained" onClick={applyFilters} disabled={!canApply || loadingReport}>
                {loadingReport ? "Carregando..." : "Aplicar"}
              </Button>
              <Button
                variant="outlined"
                onClick={() =>
                  setDraft({ eventoId: null, eventoNome: "", dataInicio: "", dataFim: "" })
                }
              >
                Limpar
              </Button>
            </Grid>
            <Grid item xs={12}>
              {loadingEventos ? (
                <Typography variant="caption" color="text.secondary">
                  Carregando eventos...
                </Typography>
              ) : selectedEvento ? (
                <Typography variant="caption" color="text.secondary">
                  Evento selecionado: {selectedEvento.nome}
                </Typography>
              ) : null}
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {error ? <Alert severity="error">{error}</Alert> : null}

      {!report && !loadingReport ? (
        <Alert severity="info">Selecione um evento e aplique os filtros para ver o dashboard.</Alert>
      ) : null}

      {loadingReport ? (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      ) : null}

      {report ? (
        <>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <MetricCard title="Total de leads" value={String(report.big_numbers.total_leads)} />
            </Grid>
            <Grid item xs={12} md={3}>
              <MetricCard title="Total de compras" value={String(report.big_numbers.total_compras)} />
            </Grid>
            <Grid item xs={12} md={3}>
              <MetricCard title="Publico do evento" value={String(report.big_numbers.total_publico)} />
            </Grid>
            <Grid item xs={12} md={3}>
              <MetricCard
                title="Taxa de conversao"
                value={`${report.big_numbers.taxa_conversao.toFixed(2)}%`}
              />
            </Grid>
          </Grid>

          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" fontWeight={800}>
                    Perfil do publico - Idade
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    % sobre registros com idade
                  </Typography>
                  <Divider sx={{ my: 1 }} />
                  {report.perfil_publico.distribuicao_idade.length === 0 ? (
                    <Typography variant="body2" color="text.secondary">
                      Sem dados de idade.
                    </Typography>
                  ) : (
                    report.perfil_publico.distribuicao_idade.map((item) => (
                      <BarRow
                        key={item.faixa}
                        label={item.faixa}
                        total={item.total}
                        percent={item.percentual}
                      />
                    ))
                  )}
                  <Typography variant="caption" color="text.secondary">
                    Sem idade: {report.perfil_publico.percent_sem_idade.toFixed(1)}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" fontWeight={800}>
                    Perfil do publico - Genero
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    % sobre total de leads
                  </Typography>
                  <Divider sx={{ my: 1 }} />
                  {report.perfil_publico.distribuicao_genero.length === 0 ? (
                    <Typography variant="body2" color="text.secondary">
                      Sem dados de genero.
                    </Typography>
                  ) : (
                    report.perfil_publico.distribuicao_genero.map((item) => (
                      <BarRow
                        key={item.faixa}
                        label={item.faixa}
                        total={item.total}
                        percent={item.percentual}
                      />
                    ))
                  )}
                  <Typography variant="caption" color="text.secondary">
                    Sem genero: {report.perfil_publico.percent_sem_genero.toFixed(1)}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" fontWeight={800}>
                    Clientes BB
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Total: {report.clientes_bb.total_clientes_bb}
                  </Typography>
                  <Typography variant="body2">
                    Percentual: {report.clientes_bb.percentual_clientes_bb.toFixed(2)}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {report.clientes_bb.criterio_usado}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" fontWeight={800}>
                    Pre-venda
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Janela: {report.pre_venda.janela_pre_venda || "Nao definida"}
                  </Typography>
                  <Typography variant="body2">
                    Pre-venda: {report.pre_venda.volume_pre_venda}
                  </Typography>
                  <Typography variant="body2">
                    Total vendas: {report.pre_venda.volume_venda_geral}
                  </Typography>
                  {report.pre_venda.observacao ? (
                    <Typography variant="caption" color="text.secondary">
                      {report.pre_venda.observacao}
                    </Typography>
                  ) : null}
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" fontWeight={800}>
                    Performance nas redes
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Status: {report.redes.status}
                  </Typography>
                  {report.redes.observacao ? (
                    <Typography variant="caption" color="text.secondary">
                      {report.redes.observacao}
                    </Typography>
                  ) : null}
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" fontWeight={800}>
                Dados faltantes / Como coletar
              </Typography>
              <Divider sx={{ my: 1 }} />
              {report.dados_faltantes.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  Sem lacunas registradas.
                </Typography>
              ) : (
                report.dados_faltantes.map((item) => (
                  <Typography key={item} variant="body2">
                    - {item}
                  </Typography>
                ))
              )}
            </CardContent>
          </Card>
        </>
      ) : null}
    </Box>
  );
}

