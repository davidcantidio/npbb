import {
  Alert,
  Box,
  Button,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import { useEffect, useMemo, useState } from "react";

import ImportMappingTable from "../features/import_wizard/ImportMappingTable";
import {
  listPublicidadeReferenciaEventos,
  previewPublicidadeImport,
  runPublicidadeImport,
  upsertPublicidadeAlias,
  type PublicidadeEventReference,
  type PublicidadeImportPreview,
  type PublicidadeImportReport,
  validatePublicidadeMapping,
} from "../services/publicidade_import";
import { useAuth } from "../store/auth";

export default function PublicidadeImport() {
  const { token } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<PublicidadeImportPreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mappingError, setMappingError] = useState<string | null>(null);
  const [importError, setImportError] = useState<string | null>(null);
  const [importResult, setImportResult] = useState<PublicidadeImportReport | null>(null);
  const [eventosRef, setEventosRef] = useState<PublicidadeEventReference[]>([]);
  const [referenceSelections, setReferenceSelections] = useState<Record<number, string>>({});
  const [dryRun, setDryRun] = useState(false);

  const availableFields = [
    { value: "", label: "Ignorar" },
    { value: "codigo_projeto", label: "Codigo do projeto (obrigatorio)" },
    { value: "projeto", label: "Projeto (obrigatorio)" },
    { value: "data_vinculacao", label: "Data de vinculacao (obrigatorio)" },
    { value: "meio", label: "Meio (obrigatorio)" },
    { value: "veiculo", label: "Veiculo (obrigatorio)" },
    { value: "uf", label: "UF (obrigatorio)" },
    { value: "uf_extenso", label: "UF por extenso" },
    { value: "municipio", label: "Municipio" },
    { value: "camada", label: "Camada (obrigatorio)" },
  ];

  const normalizeErrorMessage = (raw: string) => {
    if (raw.startsWith("{") && raw.endsWith("}")) {
      try {
        const parsed = JSON.parse(raw);
        const message =
          typeof parsed?.message === "string"
            ? parsed.message
            : typeof parsed?.detail?.message === "string"
              ? parsed.detail.message
              : typeof parsed?.detail === "string"
                ? parsed.detail
                : "";
        if (message) return message;
      } catch {
        return "Erro ao processar a importacao.";
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
    setImportError(null);
    setImportResult(null);
    try {
      const data = await previewPublicidadeImport(token, selected);
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
      await validatePublicidadeMapping(token, preview.suggestions);

      preview.headers.forEach((_, idx) => {
        const campo = preview.suggestions[idx]?.campo;
        if (campo !== "codigo_projeto") return;
        const sample = preview.samples_by_column[idx]?.[0];
        const selected = referenceSelections[idx];
        if (!sample || !selected) return;

        const ref = eventosRef.find((item) => String(item.id) === selected);
        if (!ref?.external_project_code) return;
        upsertPublicidadeAlias(token, {
          field_name: "codigo_projeto",
          valor_origem: sample,
          canonical_ref_id: ref.id,
          canonical_value: ref.external_project_code,
        }).catch(() => {
          // Alias funciona como cache, nao bloqueia fluxo.
        });
      });
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
      const result = await runPublicidadeImport(token, file, preview.suggestions, dryRun);
      setImportResult(result);
    } catch (err: any) {
      const message = err?.message ? normalizeErrorMessage(err.message) : "Erro ao executar importacao.";
      setImportError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!token || !preview) return;
    listPublicidadeReferenciaEventos(token)
      .then((items) => {
        setEventosRef(items);
      })
      .catch(() => {
        // silencioso: referencias sao auxiliares
      });
  }, [token, preview]);

  const referenceOptionsByField = useMemo(() => {
    return {
      codigo_projeto: eventosRef
        .filter((evento) => Boolean(evento.external_project_code))
        .map((evento) => ({
          value: String(evento.id),
          label: `${evento.nome} (${evento.external_project_code})`,
        })),
    };
  }, [eventosRef]);

  const eventByCode = useMemo(() => {
    const map: Record<string, string> = {};
    eventosRef.forEach((evento) => {
      if (!evento.external_project_code) return;
      map[evento.external_project_code] = String(evento.id);
    });
    return map;
  }, [eventosRef]);

  useEffect(() => {
    if (!preview) return;
    const initial: Record<number, string> = {};
    preview.headers.forEach((_, idx) => {
      const hit = preview.alias_hits?.[idx];
      if (!hit) return;
      if (hit.canonical_ref_id) {
        initial[idx] = String(hit.canonical_ref_id);
        return;
      }
      if (hit.canonical_value && eventByCode[hit.canonical_value]) {
        initial[idx] = eventByCode[hit.canonical_value];
      }
    });
    setReferenceSelections(initial);
  }, [preview, eventByCode]);

  return (
    <Box sx={{ width: "100%" }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Publicidade
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Importacao assistida de vinculacoes de publicidade
          </Typography>
        </Box>
        <Button variant="contained" sx={{ textTransform: "none", fontWeight: 700 }} component="label">
          Importar CSV/XLSX
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
            Selecione "Importar CSV/XLSX" para iniciar o fluxo de importacao assistida.
          </Typography>
        ) : null}

        {preview ? (
          <Box>
            <Typography variant="subtitle1" fontWeight={800} gutterBottom>
              Mapeamento de colunas
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ display: "block", mb: 2 }}>
              Obrigatorios: codigo_projeto, projeto, data_vinculacao, meio, veiculo, uf e camada.
            </Typography>

            <ImportMappingTable
              headers={preview.headers}
              samplesByColumn={preview.samples_by_column}
              suggestions={preview.suggestions}
              availableFields={availableFields}
              aliasHits={preview.alias_hits?.map((item) =>
                item
                  ? {
                      canonical_value: item.canonical_value,
                      canonical_ref_id: item.canonical_ref_id,
                    }
                  : null,
              )}
              referenceOptionsByField={referenceOptionsByField}
              referenceSelections={referenceSelections}
              onChangeField={(index, nextField) => {
                const nextPreview = { ...preview };
                nextPreview.suggestions = [...preview.suggestions];
                nextPreview.suggestions[index] = {
                  ...nextPreview.suggestions[index],
                  campo: nextField || null,
                };
                setPreview(nextPreview);
              }}
              onChangeReference={(index, nextValue) => {
                setReferenceSelections((prev) => ({
                  ...prev,
                  [index]: nextValue,
                }));
              }}
            />

            <FormControlLabel
              control={<Checkbox checked={dryRun} onChange={(event) => setDryRun(event.target.checked)} />}
              label="Somente validar (dry-run, sem persistir)"
            />

            {mappingError ? (
              <Alert severity="error" sx={{ mb: 2 }}>
                {mappingError}
              </Alert>
            ) : null}

            <Button
              variant="contained"
              sx={{ textTransform: "none", fontWeight: 700 }}
              onClick={handleRunImport}
              disabled={loading}
            >
              {dryRun ? "Validar arquivo" : "Importar"}
            </Button>

            {importError ? (
              <Alert severity="error" sx={{ mt: 2 }}>
                {importError}
              </Alert>
            ) : null}
          </Box>
        ) : null}
      </Paper>

      <Dialog open={Boolean(importResult)} onClose={() => setImportResult(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{dryRun ? "Validacao concluida" : "Importacao concluida"}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Arquivo: {importResult?.filename}
          </Typography>
          <Typography variant="body2">Linhas recebidas: {importResult?.received_rows ?? 0}</Typography>
          <Typography variant="body2">Linhas validas: {importResult?.valid_rows ?? 0}</Typography>
          <Typography variant="body2">Staging inseridas: {importResult?.staged_inserted ?? 0}</Typography>
          <Typography variant="body2">Staging ignoradas: {importResult?.staged_skipped ?? 0}</Typography>
          <Typography variant="body2">Final inseridas: {importResult?.upsert_inserted ?? 0}</Typography>
          <Typography variant="body2">Final atualizadas: {importResult?.upsert_updated ?? 0}</Typography>
          <Typography variant="body2">
            Sem correspondencia de evento: {importResult?.unresolved_event_id ?? 0}
          </Typography>
          {importResult?.errors?.length ? (
            <Alert severity="warning" sx={{ mt: 2 }}>
              {importResult.errors.length} linha(s) com erro. Primeiro erro:{" "}
              {`${importResult.errors[0].line} / ${importResult.errors[0].field} - ${importResult.errors[0].message}`}
            </Alert>
          ) : null}
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
