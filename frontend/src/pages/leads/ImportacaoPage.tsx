import CloudUploadRoundedIcon from "@mui/icons-material/CloudUploadRounded";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  MenuItem,
  Paper,
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
import { ChangeEvent, FormEvent, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  createLeadBatch,
  getLeadBatchPreview,
  LeadBatch,
  LeadBatchPreview,
} from "../../services/leads_import";
import { toApiErrorMessage } from "../../services/http";
import { useAuth } from "../../store/auth";

const STEPS = ["Metadados e upload", "Preview de colunas"];
const PLATAFORMAS = ["email", "whatsapp", "drive", "manual", "outro"];
const ALLOWED_EXTENSIONS = [".csv", ".xlsx"];

function hasAllowedExtension(file: File) {
  const name = file.name.toLowerCase();
  return ALLOWED_EXTENSIONS.some((ext) => name.endsWith(ext));
}

export default function ImportacaoPage() {
  const { token, user } = useAuth();
  const navigate = useNavigate();

  const [activeStep, setActiveStep] = useState(0);
  const [quemEnviou, setQuemEnviou] = useState(user?.email ?? "");
  const [plataformaOrigem, setPlataformaOrigem] = useState("");
  const [dataEnvio, setDataEnvio] = useState(() => new Date().toISOString().slice(0, 10));
  const [file, setFile] = useState<File | null>(null);
  const [batch, setBatch] = useState<LeadBatch | null>(null);
  const [preview, setPreview] = useState<LeadBatchPreview | null>(null);
  const [loadingSubmit, setLoadingSubmit] = useState(false);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = useMemo(() => {
    return Boolean(quemEnviou.trim() && plataformaOrigem && dataEnvio && file && !loadingSubmit);
  }, [dataEnvio, file, loadingSubmit, plataformaOrigem, quemEnviou]);

  const handleSelectFile = (event: ChangeEvent<HTMLInputElement>) => {
    const nextFile = event.target.files?.[0] ?? null;
    setError(null);
    setFile(nextFile);
  };

  const handleSubmitStep1 = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token) {
      setError("Sessao expirada. Faca login novamente.");
      return;
    }
    if (!file) {
      setError("Selecione um arquivo CSV ou XLSX.");
      return;
    }
    if (!hasAllowedExtension(file)) {
      setError("Formato de arquivo invalido. Use CSV ou XLSX.");
      return;
    }
    if (!quemEnviou.trim() || !plataformaOrigem || !dataEnvio) {
      setError("Preencha todos os campos obrigatorios.");
      return;
    }

    setLoadingSubmit(true);
    setError(null);
    setPreview(null);
    try {
      const createdBatch = await createLeadBatch(token, {
        quem_enviou: quemEnviou.trim(),
        plataforma_origem: plataformaOrigem,
        data_envio: dataEnvio,
        file,
      });
      setBatch(createdBatch);

      setLoadingPreview(true);
      const batchPreview = await getLeadBatchPreview(token, createdBatch.id);
      setPreview(batchPreview);
      setActiveStep(1);
    } catch (err) {
      setError(toApiErrorMessage(err, "Falha ao enviar arquivo para camada Bronze."));
    } finally {
      setLoadingSubmit(false);
      setLoadingPreview(false);
    }
  };

  const handleBackToStep1 = () => {
    setActiveStep(0);
    setPreview(null);
    setError(null);
  };

  return (
    <Box sx={{ width: "100%" }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Importacao de Leads
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Fluxo unificado da camada Bronze: upload e preview inicial.
          </Typography>
        </Box>
      </Stack>

      <Paper elevation={1} sx={{ p: { xs: 2, md: 3 }, borderRadius: 3 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          {STEPS.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}

        {activeStep === 0 ? (
          <Box component="form" onSubmit={handleSubmitStep1}>
            <Stack spacing={2}>
              <TextField
                label="Quem enviou"
                value={quemEnviou}
                onChange={(event) => setQuemEnviou(event.target.value)}
                required
                fullWidth
              />

              <TextField
                select
                label="Plataforma de origem"
                value={plataformaOrigem}
                onChange={(event) => setPlataformaOrigem(event.target.value)}
                required
                fullWidth
              >
                {PLATAFORMAS.map((plataforma) => (
                  <MenuItem key={plataforma} value={plataforma}>
                    {plataforma}
                  </MenuItem>
                ))}
              </TextField>

              <TextField
                label="Data de envio"
                type="date"
                value={dataEnvio}
                onChange={(event) => setDataEnvio(event.target.value)}
                InputLabelProps={{ shrink: true }}
                required
                fullWidth
              />

              <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems={{ xs: "stretch", md: "center" }}>
                <Button variant="outlined" component="label" startIcon={<CloudUploadRoundedIcon />} sx={{ textTransform: "none" }}>
                  Selecionar CSV/XLSX
                  <input hidden type="file" accept=".csv,.xlsx" onChange={handleSelectFile} />
                </Button>
                <Typography variant="body2" color={file ? "text.primary" : "text.secondary"}>
                  {file ? file.name : "Nenhum arquivo selecionado"}
                </Typography>
              </Stack>

              <Box>
                <Button type="submit" variant="contained" disabled={!canSubmit}>
                  {loadingSubmit ? <CircularProgress size={18} color="inherit" /> : "Enviar para Bronze"}
                </Button>
              </Box>
            </Stack>
          </Box>
        ) : (
          <Stack spacing={2}>
            <Typography variant="subtitle1" fontWeight={700}>
              Preview do lote #{batch?.id}
            </Typography>
            {loadingPreview ? (
              <Box sx={{ py: 2, display: "flex", justifyContent: "center" }}>
                <CircularProgress size={24} />
              </Box>
            ) : null}
            {preview ? (
              <>
                <Typography variant="body2" color="text.secondary">
                  Colunas detectadas: {preview.headers.length} | Linhas de amostra: {preview.rows.length} de {preview.total_rows}
                </Typography>
                <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2 }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        {preview.headers.map((header) => (
                          <TableCell key={header}>{header || "-"}</TableCell>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {preview.rows.map((row, rowIndex) => (
                        <TableRow key={`row-${rowIndex}`}>
                          {preview.headers.map((_, columnIndex) => (
                            <TableCell key={`cell-${rowIndex}-${columnIndex}`}>
                              {row[columnIndex] ?? ""}
                            </TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </>
            ) : (
              <Alert severity="warning">Nao foi possivel carregar o preview.</Alert>
            )}

            <Stack direction={{ xs: "column", md: "row" }} spacing={1.5}>
              <Button variant="outlined" onClick={handleBackToStep1}>
                Cancelar
              </Button>
              <Button
                variant="contained"
                disabled={!batch}
                onClick={() => navigate(`/leads/mapeamento?batch_id=${batch?.id ?? ""}`)}
              >
                Avancar para Mapeamento
              </Button>
            </Stack>
          </Stack>
        )}
      </Paper>
    </Box>
  );
}
