import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Typography,
} from "@mui/material";
import { useEffect, useMemo, useState } from "react";
import {
  listReferenciaCidades,
  listReferenciaEstados,
  listReferenciaEventos,
  listReferenciaGeneros,
  createLeadAlias,
  previewLeadImport,
  runLeadImport,
  type LeadImportPreview,
  validateLeadMapping,
} from "../services/leads_import";
import { useAuth } from "../store/auth";

export default function LeadsImport() {
  const { token } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<LeadImportPreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mappingError, setMappingError] = useState<string | null>(null);
  const [importResult, setImportResult] = useState<{
    filename: string;
    created: number;
    updated: number;
    skipped: number;
  } | null>(null);
  const [importError, setImportError] = useState<string | null>(null);
  const [eventosRef, setEventosRef] = useState<Array<{ id: number; nome: string }>>([]);
  const [cidadesRef, setCidadesRef] = useState<string[]>([]);
  const [estadosRef, setEstadosRef] = useState<string[]>([]);
  const [generosRef, setGenerosRef] = useState<string[]>([]);
  const [secondarySelections, setSecondarySelections] = useState<Record<number, string>>({});
  const [activeRowIndex, setActiveRowIndex] = useState<number | null>(null);

  const availableFields = [
    { value: "", label: "Ignorar" },
    { value: "email", label: "Email (obrigatorio)" },
    { value: "cpf", label: "CPF (obrigatorio)" },
    { value: "nome", label: "Nome" },
    { value: "sobrenome", label: "Sobrenome" },
    { value: "telefone", label: "Telefone" },
    { value: "data_nascimento", label: "Data de nascimento" },
    { value: "evento_nome", label: "Evento" },
    { value: "sessao", label: "Sessao" },
    { value: "data_compra", label: "Data e hora da compra" },
    { value: "endereco_rua", label: "Rua (endereco)" },
    { value: "endereco_numero", label: "Numero (endereco)" },
    { value: "bairro", label: "Bairro" },
    { value: "cidade", label: "Cidade" },
    { value: "estado", label: "Estado" },
    { value: "cep", label: "CEP" },
    { value: "genero", label: "Genero" },
    { value: "codigo_promocional", label: "Codigo promocional" },
    { value: "ingresso_qtd", label: "Quantidade de ingresso" },
    { value: "ingresso_tipo", label: "Tipo de ingresso" },
  ];

  const normalizeErrorMessage = (raw: string) => {
    if (raw.startsWith("{") && raw.endsWith("}")) {
      try {
        const parsed = JSON.parse(raw);
        const msg =
          typeof parsed?.message === "string"
            ? parsed.message
            : typeof parsed?.detail === "string"
              ? parsed.detail
              : "";
        if (msg) return msg;
      } catch {
        return "Erro ao processar o arquivo.";
      }
    }
    return raw;
  };

  const handleUpload = async (selected: File) => {
    if (!token) return;
    setLoading(true);
    setError(null);
    setPreview(null);
    setMappingError(null);
    try {
      const data = await previewLeadImport(token, selected);
      setPreview(data);
    } catch (err: any) {
      const message = err?.message ? normalizeErrorMessage(err.message) : "Erro ao gerar preview do arquivo.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmMapping = async () => {
    if (!token || !preview) return;
    setMappingError(null);
    try {
      await validateLeadMapping(token, preview.suggestions);
      // persist aliases for reference fields
      preview.headers.forEach((_, idx) => {
        const campo = preview.suggestions[idx]?.campo;
        if (!campo || !["evento_nome", "cidade", "estado", "genero"].includes(campo)) return;
        const sample = preview.samples_by_column[idx]?.[0];
        const selected = secondarySelections[idx];
        if (!sample || !selected) return;

        const tipoMap: Record<string, string> = {
          evento_nome: "EVENTO",
          cidade: "CIDADE",
          estado: "ESTADO",
          genero: "GENERO",
        };
        const payload =
          campo === "evento_nome"
            ? { tipo: tipoMap[campo], valor_origem: sample, evento_id: Number(selected) }
            : { tipo: tipoMap[campo], valor_origem: sample, canonical_value: selected };
        createLeadAlias(token, payload).catch(() => {
          // silencioso: alias eh cache
        });
      });
      setMappingError(null);
    } catch (err: any) {
      const message = err?.message ? normalizeErrorMessage(err.message) : "Erro ao validar mapeamento.";
      setMappingError(message);
      throw err;
    }
  };

  const handleRunImport = async () => {
    if (!token || !preview || !file) return;
    setImportError(null);
    setLoading(true);
    try {
      await handleConfirmMapping();
      const result = await runLeadImport(token, file, preview.suggestions);
      setImportResult(result);
    } catch (err: any) {
      const message = err?.message ? normalizeErrorMessage(err.message) : "Erro ao importar arquivo.";
      setImportError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!token || !preview) return;
    Promise.all([
      listReferenciaEventos(token),
      listReferenciaCidades(token),
      listReferenciaEstados(token),
      listReferenciaGeneros(token),
    ])
      .then(([eventos, cidades, estados, generos]) => {
        setEventosRef(eventos);
        setCidadesRef(cidades);
        setEstadosRef(estados);
        setGenerosRef(generos);
      })
      .catch(() => {
        // silencioso: referencias sao auxiliares
      });
  }, [token, preview]);

  const referenceOptions = useMemo(() => {
    return {
      evento_nome: eventosRef.map((e) => ({ value: String(e.id), label: e.nome })),
      cidade: cidadesRef.map((c) => ({ value: c, label: c })),
      estado: estadosRef.map((c) => ({ value: c, label: c })),
      genero: generosRef.map((c) => ({ value: c, label: c })),
    };
  }, [eventosRef, cidadesRef, estadosRef, generosRef]);

  useEffect(() => {
    if (!preview) return;
    const initial: Record<number, string> = {};
    preview.headers.forEach((_, idx) => {
      const hit = preview.alias_hits?.[idx];
      if (hit?.evento_id) initial[idx] = String(hit.evento_id);
      if (hit?.canonical_value) initial[idx] = hit.canonical_value;
    });
    setSecondarySelections(initial);
  }, [preview]);

  useEffect(() => {
    if (!preview) return;
    const normalize = (value: string) =>
      value
        .normalize("NFKD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();
    setSecondarySelections((prev) => {
      const next = { ...prev };
      preview.headers.forEach((_, idx) => {
        const campo = preview.suggestions[idx]?.campo;
        if (!campo || !["evento_nome", "cidade", "estado", "genero"].includes(campo)) return;
        if (next[idx]) return;
        const sample = preview.samples_by_column[idx]?.[0];
        if (!sample) return;
        const options = referenceOptions[campo as keyof typeof referenceOptions] || [];
        const match = options.find((opt) => normalize(opt.label) === normalize(sample));
        if (match) next[idx] = match.value;
      });
      return next;
    });
  }, [preview, referenceOptions]);

  return (
    <Box sx={{ width: "100%" }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Leads
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Importacao e gestao de leads
          </Typography>
        </Box>
        <Button variant="contained" sx={{ textTransform: "none", fontWeight: 700 }} component="label">
          Importar XLSX
          <input
            type="file"
            hidden
            accept=".csv,.xlsx"
            onChange={(event) => {
              const selected = event.target.files?.[0];
              if (!selected) return;
              setFile(selected);
              handleUpload(selected);
            }}
          />
        </Button>
      </Stack>

      <Paper elevation={1} sx={{ p: { xs: 2, md: 3 }, borderRadius: 3 }}>
        {error ? <Alert severity="error">{error}</Alert> : null}
        {!preview && !error ? (
          <Typography variant="body2" color="text.secondary">
            Selecione "Importar XLSX" para iniciar o fluxo de importacao.
          </Typography>
        ) : null}

        {preview ? (
          <Box>
            <Typography variant="subtitle1" fontWeight={800} gutterBottom>
              Mapeamento de colunas
            </Typography>
            <Typography
              variant="caption"
              color="text.secondary"
              gutterBottom
              sx={{ display: "block", mb: 2 }}
            >
              Obrigatorio: Email ou CPF.
            </Typography>
            <Box
              sx={{
                display: { xs: "none", md: "grid" },
                gridTemplateColumns: "1.6fr 1fr 1fr 0.6fr",
                gap: 2,
                mb: 1,
              }}
            >
              <Typography variant="caption" color="text.secondary">
                Coluna / amostra
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Campo
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Referencia
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ textAlign: "right" }}>
                Confianca
              </Typography>
            </Box>
            {preview.headers.map((header, idx) => (
              <Box
                key={`${header}-${idx}`}
                sx={{
                  display: "grid",
                  gridTemplateColumns: { xs: "1fr", md: "1.6fr 1fr 1fr 0.6fr" },
                  gap: 2,
                  alignItems: "center",
                  mb: 1.5,
                  pb: 1.5,
                  borderBottom: "1px solid rgba(0,0,0,0.06)",
                  borderRadius: 2,
                  px: { xs: 0, md: 1 },
                  backgroundColor: activeRowIndex === idx ? "rgba(92, 71, 163, 0.08)" : "transparent",
                  transition: "background-color 150ms ease",
                }}
              >
                <Box>
                  <Typography variant="body2" fontWeight={700}>
                    {header || `Coluna ${idx + 1}`}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {preview.samples_by_column[idx]?.[0] || "-"}
                  </Typography>
                  {preview.alias_hits?.[idx] ? (
                    <Typography variant="caption" color="text.secondary">
                      Alias conhecido:{" "}
                      {preview.alias_hits[idx]?.canonical_value ||
                        preview.alias_hits[idx]?.evento_id ||
                        "-"}
                    </Typography>
                  ) : null}
                </Box>
                <FormControl
                  size="small"
                  fullWidth
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      borderRadius: 2,
                    },
                    "& .MuiOutlinedInput-root.Mui-focused .MuiOutlinedInput-notchedOutline": {
                      borderColor: "#5C47A3",
                      borderWidth: 2,
                      boxShadow: "0 0 0 2px rgba(92,71,163,0.15)",
                    },
                  }}
                >
                  <InputLabel>Campo</InputLabel>
                  <Select
                    label="Campo"
                    value={preview.suggestions[idx]?.campo || ""}
                    onChange={(event) => {
                      const next = { ...preview };
                      next.suggestions[idx] = {
                        ...next.suggestions[idx],
                        campo: event.target.value || null,
                      };
                      setPreview(next);
                    }}
                    onFocus={() => setActiveRowIndex(idx)}
                    onBlur={() => setActiveRowIndex(null)}
                  >
                    {availableFields.map((field) => (
                      <MenuItem key={field.value} value={field.value}>
                        {field.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <Box>
                  {["evento_nome", "cidade", "estado", "genero"].includes(
                    preview.suggestions[idx]?.campo || "",
                  ) ? (
                    <FormControl size="small" fullWidth>
                      <InputLabel>Referencia</InputLabel>
                      <Select
                        label="Referencia"
                        value={secondarySelections[idx] || ""}
                        onChange={(event) => {
                          setSecondarySelections((prev) => ({
                            ...prev,
                            [idx]: String(event.target.value || ""),
                          }));
                        }}
                        onFocus={() => setActiveRowIndex(idx)}
                        onBlur={() => setActiveRowIndex(null)}
                      >
                        <MenuItem value="">Selecionar</MenuItem>
                        {(referenceOptions[
                          preview.suggestions[idx]?.campo as keyof typeof referenceOptions
                        ] || []
                        ).map((opt) => (
                          <MenuItem key={opt.value} value={opt.value}>
                            {opt.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  ) : (
                    <Typography variant="caption" color="text.secondary">
                      -
                    </Typography>
                  )}
                </Box>
                <Box sx={{ textAlign: { xs: "left", md: "right" } }}>
                  {preview.suggestions[idx]?.confianca ? (
                    <Typography variant="caption" color="text.secondary">
                      {Math.round((preview.suggestions[idx].confianca || 0) * 100)}%
                    </Typography>
                  ) : (
                    <Typography variant="caption" color="text.secondary">
                      -
                    </Typography>
                  )}
                </Box>
              </Box>
            ))}

            {mappingError ? (
              <Alert severity="error" sx={{ mb: 2 }}>
                {mappingError}
              </Alert>
            ) : null}

            <Button
              variant="contained"
              sx={{ textTransform: "none", fontWeight: 700, ml: 1 }}
              onClick={handleRunImport}
              disabled={loading}
            >
              Importar
            </Button>
            {importError ? (
              <Alert severity="error" sx={{ mt: 2 }}>
                {importError}
              </Alert>
            ) : null}
          </Box>
        ) : null}
      </Paper>

      <Dialog open={Boolean(importResult)} onClose={() => setImportResult(null)} maxWidth="xs" fullWidth>
        <DialogTitle>Importacao concluida</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Arquivo: {importResult?.filename}
          </Typography>
          <Typography variant="body2">Criados: {importResult?.created ?? 0}</Typography>
          <Typography variant="body2">Atualizados: {importResult?.updated ?? 0}</Typography>
          <Typography variant="body2">Ignorados: {importResult?.skipped ?? 0}</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setImportResult(null)} sx={{ textTransform: "none", fontWeight: 700 }}>
            Fechar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
