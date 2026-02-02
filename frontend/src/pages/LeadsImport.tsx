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
import { useState } from "react";
import {
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

  const availableFields = [
    { value: "", label: "Ignorar" },
    { value: "email", label: "Email" },
    { value: "cpf", label: "CPF" },
    { value: "nome", label: "Nome" },
    { value: "sobrenome", label: "Sobrenome" },
    { value: "telefone", label: "Telefone" },
    { value: "data_nascimento", label: "Data de nascimento" },
    { value: "evento_nome", label: "Evento" },
    { value: "sessao", label: "Sessao" },
    { value: "data_compra", label: "Data e hora da compra" },
    { value: "ingresso_qtd", label: "Quantidade de ingresso" },
    { value: "ingresso_tipo", label: "Ingresso" },
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
      setMappingError(null);
    } catch (err: any) {
      const message = err?.message ? normalizeErrorMessage(err.message) : "Erro ao validar mapeamento.";
      setMappingError(message);
    }
  };

  const handleRunImport = async () => {
    if (!token || !preview || !file) return;
    setImportError(null);
    setLoading(true);
    try {
      const result = await runLeadImport(token, file, preview.suggestions);
      setImportResult(result);
    } catch (err: any) {
      const message = err?.message ? normalizeErrorMessage(err.message) : "Erro ao importar arquivo.";
      setImportError(message);
    } finally {
      setLoading(false);
    }
  };

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
          Importar leads
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

      <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
        {error ? <Alert severity="error">{error}</Alert> : null}
        {!preview && !error ? (
          <Typography variant="body2" color="text.secondary">
            Selecione “Importar leads” para iniciar o fluxo de importacao.
          </Typography>
        ) : null}

        {preview ? (
          <Box>
            <Typography variant="subtitle1" fontWeight={700} gutterBottom>
              Mapeamento de colunas
            </Typography>
            {preview.headers.map((header, idx) => (
              <Stack key={`${header}-${idx}`} direction="row" spacing={2} alignItems="center" mb={2}>
                <Box sx={{ minWidth: 200 }}>
                  <Typography variant="body2" fontWeight={600}>
                    {header || `Coluna ${idx + 1}`}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Exemplo: {preview.samples_by_column[idx]?.[0] || "-"}
                  </Typography>
                </Box>
                <FormControl size="small" sx={{ minWidth: 220 }}>
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
                  >
                    {availableFields.map((field) => (
                      <MenuItem key={field.value} value={field.value}>
                        {field.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                {preview.suggestions[idx]?.confianca ? (
                  <Typography variant="caption" color="text.secondary">
                    Confiança: {Math.round((preview.suggestions[idx].confianca || 0) * 100)}%
                  </Typography>
                ) : null}
              </Stack>
            ))}

            {mappingError ? (
              <Alert severity="error" sx={{ mb: 2 }}>
                {mappingError}
              </Alert>
            ) : null}

            <Button
              variant="outlined"
              sx={{ textTransform: "none", fontWeight: 700 }}
              onClick={handleConfirmMapping}
              disabled={loading}
            >
              Confirmar mapeamento
            </Button>
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
