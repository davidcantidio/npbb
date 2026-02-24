import { Alert, Box, Paper, Stack, Typography } from "@mui/material";
import { useCallback, useMemo, useState } from "react";
import { runLeadImport } from "../../services/leads_import";
import { toApiErrorMessage } from "../../services/http";
import { useAuth } from "../../store/auth";
import { LeadImportSummaryDialog } from "./components/LeadImportSummaryDialog";
import { LeadImportUpload } from "./components/LeadImportUpload";
import { LeadListTable } from "./components/LeadListTable";
import { LeadMappingFieldOption, LeadMappingTable } from "./components/LeadMappingTable";
import { useLeadImportMapping } from "./hooks/useLeadImportMapping";
import { useLeadImportUpload } from "./hooks/useLeadImportUpload";
import { useLeadReferences } from "./hooks/useLeadReferences";
import { useLeadsTable } from "./hooks/useLeadsTable";

const AVAILABLE_FIELDS: LeadMappingFieldOption[] = [
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

/**
 * Page container for assisted lead import and lead listing.
 */
export default function LeadImportPage() {
  const { token } = useAuth();

  const {
    file,
    preview,
    setPreview,
    loading,
    setLoading,
    error,
    setError,
    handleUpload,
  } = useLeadImportUpload(token);

  const { referenceOptions } = useLeadReferences(token, preview);

  const {
    mappingError,
    setMappingError,
    aliasWarning,
    setAliasWarning,
    secondarySelections,
    setSecondarySelections,
    activeRowIndex,
    setActiveRowIndex,
    onSuggestionFieldChange,
    confirmMapping,
  } = useLeadImportMapping(token, preview, setPreview, referenceOptions);

  const {
    leads,
    leadsTotal,
    leadsPage,
    setLeadsPage,
    leadsPageSize,
    setLeadsPageSize,
    leadsLoading,
    leadsError,
    refresh,
  } = useLeadsTable(token);

  const [importResult, setImportResult] = useState<{
    filename: string;
    created: number;
    updated: number;
    skipped: number;
  } | null>(null);
  const [importError, setImportError] = useState<string | null>(null);

  const handleSelectFile = useCallback(
    async (selected: File) => {
      setError(null);
      setMappingError(null);
      setAliasWarning(null);
      setImportError(null);
      setImportResult(null);
      setSecondarySelections({});
      await handleUpload(selected);
    },
    [handleUpload, setAliasWarning, setError, setMappingError, setSecondarySelections],
  );

  const handleRunImport = useCallback(async () => {
    if (!token || !preview || !file) return;

    setImportError(null);
    setLoading(true);

    try {
      await confirmMapping(preview.suggestions, preview.headers, preview.samples_by_column);
      const result = await runLeadImport(token, file, preview.suggestions);
      setImportResult(result);
      setLeadsPage(1);
      refresh();
    } catch (err) {
      setImportError(toApiErrorMessage(err, "Erro ao importar arquivo."));
    } finally {
      setLoading(false);
    }
  }, [confirmMapping, file, preview, refresh, setLeadsPage, setLoading, token]);

  const hasPreview = useMemo(() => Boolean(preview), [preview]);

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
        <LeadImportUpload disabled={loading} onSelectFile={handleSelectFile} />
      </Stack>

      <Paper elevation={1} sx={{ p: { xs: 2, md: 3 }, borderRadius: 3 }}>
        {error ? <Alert severity="error">{error}</Alert> : null}

        {!hasPreview && !error ? (
          <Typography variant="body2" color="text.secondary">
            Selecione "Importar CSV/XLSX" para iniciar o fluxo de importacao.
          </Typography>
        ) : null}

        {preview ? (
          <LeadMappingTable
            preview={preview}
            availableFields={AVAILABLE_FIELDS}
            secondarySelections={secondarySelections}
            activeRowIndex={activeRowIndex}
            referenceOptions={referenceOptions}
            mappingError={mappingError}
            aliasWarning={aliasWarning}
            importError={importError}
            loading={loading}
            onFieldChange={onSuggestionFieldChange}
            onSecondaryChange={(index, value) => {
              setSecondarySelections((prev) => ({
                ...prev,
                [index]: value,
              }));
            }}
            onFocusRow={setActiveRowIndex}
            onImport={handleRunImport}
          />
        ) : null}
      </Paper>

      <Paper elevation={1} sx={{ mt: 3, borderRadius: 3, overflow: "hidden" }}>
        <LeadListTable
          leads={leads}
          leadsTotal={leadsTotal}
          leadsLoading={leadsLoading}
          leadsError={leadsError}
          leadsPage={leadsPage}
          leadsPageSize={leadsPageSize}
          onPageChange={setLeadsPage}
          onRowsPerPageChange={(pageSize) => {
            setLeadsPageSize(pageSize);
            setLeadsPage(1);
          }}
          onRefresh={refresh}
        />
      </Paper>

      <LeadImportSummaryDialog open={Boolean(importResult)} onClose={() => setImportResult(null)} result={importResult} />
    </Box>
  );
}
