import {
  Alert,
  Box,
  Button,
  CircularProgress,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Step,
  StepLabel,
  Stepper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import UploadFileRoundedIcon from "@mui/icons-material/UploadFileRounded";
import { useState } from "react";
import { createLeadBatch, getLeadBatchPreview, type LeadBatchPreviewResponse } from "../../../services/leads_import";
import { toApiErrorMessage } from "../../../services/http";

const STEPS = ["Metadados e Upload", "Preview de Colunas"];

const PLATAFORMAS = [
  { value: "email", label: "E-mail" },
  { value: "whatsapp", label: "WhatsApp" },
  { value: "drive", label: "Google Drive" },
  { value: "manual", label: "Manual" },
  { value: "outro", label: "Outro" },
];

type Props = {
  token: string | null;
  onBatchCreated?: (batchId: string) => void;
};

export function ImportacaoBronzeStepper({ token, onBatchCreated }: Props) {
  const [activeStep, setActiveStep] = useState(0);
  const [plataforma, setPlataforma] = useState("");
  const [dataEnvio, setDataEnvio] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [batchId, setBatchId] = useState<string | null>(null);
  const [preview, setPreview] = useState<LeadBatchPreviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files?.[0] ?? null;
    setFile(selected);
    e.currentTarget.value = "";
  }

  function validateStep1(): string | null {
    if (!plataforma) return "Selecione a plataforma de origem.";
    if (!dataEnvio) return "Informe a data de envio.";
    if (!file) return "Selecione um arquivo CSV ou XLSX.";
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (!["csv", "xlsx"].includes(ext ?? "")) return "Apenas arquivos .csv ou .xlsx são aceitos.";
    return null;
  }

  async function handleSubmitStep1() {
    const validationError = validateStep1();
    if (validationError) {
      setError(validationError);
      return;
    }
    if (!token || !file) return;

    setError(null);
    setLoading(true);
    try {
      const result = await createLeadBatch(token, {
        file,
        plataforma_origem: plataforma,
        data_envio: new Date(dataEnvio).toISOString(),
      });
      setBatchId(result.batch_id);
      const previewData = await getLeadBatchPreview(token, result.batch_id);
      setPreview(previewData);
      setActiveStep(1);
      onBatchCreated?.(result.batch_id);
    } catch (err) {
      setError(toApiErrorMessage(err, "Erro ao enviar o arquivo. Tente novamente."));
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setActiveStep(0);
    setPlataforma("");
    setDataEnvio("");
    setFile(null);
    setBatchId(null);
    setPreview(null);
    setError(null);
  }

  return (
    <Box>
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {STEPS.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {activeStep === 0 && (
        <Stack spacing={3} maxWidth={520}>
          <Typography variant="subtitle1" fontWeight={600}>
            Informações de envio
          </Typography>

          <FormControl fullWidth required>
            <InputLabel id="plataforma-label">Plataforma de origem</InputLabel>
            <Select
              labelId="plataforma-label"
              value={plataforma}
              label="Plataforma de origem"
              onChange={(e) => setPlataforma(e.target.value)}
              disabled={loading}
            >
              {PLATAFORMAS.map((p) => (
                <MenuItem key={p.value} value={p.value}>
                  {p.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            label="Data de envio"
            type="date"
            value={dataEnvio}
            onChange={(e) => setDataEnvio(e.target.value)}
            InputLabelProps={{ shrink: true }}
            required
            disabled={loading}
            fullWidth
          />

          <Box>
            <Typography variant="body2" color="text.secondary" mb={1}>
              Arquivo (CSV ou XLSX)
            </Typography>
            <Button
              variant="outlined"
              component="label"
              startIcon={<UploadFileRoundedIcon />}
              disabled={loading}
              sx={{ textTransform: "none" }}
            >
              {file ? file.name : "Selecionar arquivo"}
              <input type="file" hidden accept=".csv,.xlsx" onChange={handleFileChange} />
            </Button>
            {file && (
              <Typography variant="caption" color="text.secondary" display="block" mt={0.5}>
                {(file.size / 1024).toFixed(1)} KB
              </Typography>
            )}
          </Box>

          {error && <Alert severity="error">{error}</Alert>}

          <Box>
            <Button
              variant="contained"
              onClick={handleSubmitStep1}
              disabled={loading}
              sx={{ textTransform: "none", fontWeight: 700, minWidth: 160 }}
            >
              {loading ? <CircularProgress size={20} color="inherit" /> : "Enviar arquivo"}
            </Button>
          </Box>
        </Stack>
      )}

      {activeStep === 1 && preview && (
        <Stack spacing={3}>
          <Box>
            <Typography variant="subtitle1" fontWeight={600} gutterBottom>
              Preview — {preview.nome_arquivo}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Lote registrado:{" "}
              <strong>{batchId}</strong>
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {preview.colunas.length} coluna(s) detectada(s) · {preview.amostras.length} linha(s) de amostra
            </Typography>
          </Box>

          <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 320 }}>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow>
                  {preview.colunas.map((col) => (
                    <TableCell key={col} sx={{ fontWeight: 700, whiteSpace: "nowrap" }}>
                      {col}
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {preview.amostras.map((row, i) => (
                  <TableRow key={i}>
                    {row.map((cell, j) => (
                      <TableCell key={j} sx={{ whiteSpace: "nowrap" }}>
                        {cell}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <Alert severity="success">
            Arquivo salvo com sucesso na camada Bronze. O mapeamento de colunas estará disponível na fase Silver.
          </Alert>

          <Box>
            <Button variant="outlined" onClick={handleReset} sx={{ textTransform: "none" }}>
              Importar outro arquivo
            </Button>
          </Box>
        </Stack>
      )}
    </Box>
  );
}
