import { Alert, Box, Button, Checkbox, Divider, FormControlLabel, Paper, Stack, TextField, Typography } from "@mui/material";
import { useCallback, useEffect, useMemo, useState } from "react";
import { LeadImportUpload } from "../components/LeadImportUpload";
import { LeadImportEtlSummaryDialog } from "../components/LeadImportEtlSummaryDialog";
import { useLeadImportEtlWorkflow } from "../hooks/useLeadImportEtlWorkflow";

type LeadImportEtlTabProps = {
  token: string | null;
};

export function LeadImportEtlTab({ token }: LeadImportEtlTabProps) {
  const [eventoId, setEventoId] = useState<string>("");
  const [strict, setStrict] = useState(false);
  const [selectionError, setSelectionError] = useState<string | null>(null);
  const [forceWarnings, setForceWarnings] = useState(false);

  const {
    preview,
    commitResult,
    loading,
    errors,
    hasErrors,
    hasWarnings,
    canCommit,
    handlePreview,
    handleCommit,
    resetWorkflow,
    clearErrors,
  } = useLeadImportEtlWorkflow(token);

  const canStartPreview = useMemo(() => Boolean(eventoId && !loading), [eventoId, loading]);

  useEffect(() => {
    if (!hasWarnings) {
      setForceWarnings(false);
    }
  }, [hasWarnings]);

  const handleSelectFile = useCallback(
    async (selected: File) => {
      clearErrors();
      resetWorkflow();
      setForceWarnings(false);
      if (!eventoId) {
        setSelectionError("Informe o Evento ID antes de enviar o arquivo.");
        return;
      }
      setSelectionError(null);
      await handlePreview(selected, Number(eventoId), strict);
    },
    [clearErrors, eventoId, handlePreview, resetWorkflow, strict],
  );

  const handleCommitClick = useCallback(async () => {
    if (!eventoId) return;
    await handleCommit(Number(eventoId), forceWarnings);
  }, [eventoId, forceWarnings, handleCommit]);

  return (
    <Box>
      <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems={{ xs: "stretch", md: "center" }} mb={2}>
        <Typography variant="h6" fontWeight={700}>
          Importacao avancada (ETL)
        </Typography>
        <Stack direction={{ xs: "column", md: "row" }} spacing={2} sx={{ flex: 1 }}>
          <TextField
            label="Evento ID"
            value={eventoId}
            onChange={(event) => {
              setEventoId(event.target.value);
              setSelectionError(null);
            }}
            type="number"
            size="small"
          />
          <Button
            variant={strict ? "contained" : "outlined"}
            onClick={() => setStrict((prev) => !prev)}
            sx={{ textTransform: "none", fontWeight: 700, whiteSpace: "nowrap" }}
          >
            Strict: {strict ? "ON" : "OFF"}
          </Button>
        </Stack>
        <LeadImportUpload
          label="Importar XLSX (ETL)"
          accept=".xlsx"
          disabled={!canStartPreview}
          onSelectFile={handleSelectFile}
        />
      </Stack>

      <Paper elevation={1} sx={{ p: { xs: 2, md: 3 }, borderRadius: 3 }}>
        {selectionError ? <Alert severity="warning">{selectionError}</Alert> : null}
        {errors.preview ? <Alert severity="error">{errors.preview}</Alert> : null}
        {errors.commit ? <Alert severity="error" sx={{ mt: 1 }}>{errors.commit}</Alert> : null}

        {!preview ? (
          <Typography variant="body2" color="text.secondary">
            Informe o Evento ID e envie um arquivo XLSX para gerar o preview ETL.
          </Typography>
        ) : (
          <Stack spacing={2}>
            <Stack spacing={0.5}>
              <Typography variant="subtitle1" fontWeight={700}>
                Preview ETL
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Sessao: {preview.session_token}
              </Typography>
            </Stack>
            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, flex: 1 }}>
                <Typography variant="body2">Total de linhas: {preview.total_rows}</Typography>
                <Typography variant="body2">Validas: {preview.valid_rows}</Typography>
                <Typography variant="body2">Invalidas: {preview.invalid_rows}</Typography>
              </Paper>
              <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, flex: 1 }}>
                <Typography variant="body2">Itens DQ: {preview.dq_report.length}</Typography>
                <Typography variant="body2">Warnings: {preview.dq_report.filter((item) => item.severity === "warning").length}</Typography>
                <Typography variant="body2">Errors: {preview.dq_report.filter((item) => item.severity === "error").length}</Typography>
              </Paper>
            </Stack>
            <Divider />
            <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems={{ xs: "stretch", md: "center" }}>
              <Button
                variant="contained"
                disabled={!canCommit || loading || (hasWarnings && !forceWarnings)}
                onClick={handleCommitClick}
                sx={{ textTransform: "none", fontWeight: 700 }}
              >
                Confirmar commit ETL
              </Button>
              {hasErrors ? (
                <Typography variant="body2" color="error.main">
                  Existem erros no DQ report. O commit so sera liberado quando nao houver erros.
                </Typography>
              ) : null}
              {hasWarnings ? (
                <Stack spacing={0.5}>
                  <Typography variant="body2" color="warning.main">
                    Aviso: o lote possui warnings. Confirme abaixo para liberar o commit.
                  </Typography>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={forceWarnings}
                        onChange={(event) => setForceWarnings(event.target.checked)}
                      />
                    }
                    label="Confirmar warnings e prosseguir com commit"
                  />
                </Stack>
              ) : null}
            </Stack>
          </Stack>
        )}
      </Paper>

      <LeadImportEtlSummaryDialog
        open={Boolean(commitResult)}
        onClose={() => {
          resetWorkflow();
          setForceWarnings(false);
        }}
        result={commitResult}
      />
    </Box>
  );
}
