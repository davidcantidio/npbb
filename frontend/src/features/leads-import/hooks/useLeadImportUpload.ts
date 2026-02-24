import { useCallback, useState } from "react";
import { LeadImportPreview, previewLeadImport } from "../../../services/leads_import";
import { toApiErrorMessage } from "../../../services/http";

const MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024;
const ALLOWED_EXTENSIONS = [".csv", ".xlsx"];
const ALLOWED_MIME_TYPES = [
  "text/csv",
  "application/csv",
  "application/vnd.ms-excel",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
];

/**
 * Handles file validation and preview generation for lead import.
 * @param token Auth token used by preview endpoint requests.
 * @returns Upload state plus handlers for validating and previewing lead files.
 */
export function useLeadImportUpload(token: string | null) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<LeadImportPreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateLeadFile = useCallback((selected: File): string | null => {
    const lowerName = selected.name.toLowerCase();
    const hasAllowedExtension = ALLOWED_EXTENSIONS.some((ext) => lowerName.endsWith(ext));
    if (!hasAllowedExtension) return "Formato invalido. Use arquivo .csv ou .xlsx.";
    if (selected.type && !ALLOWED_MIME_TYPES.includes(selected.type)) {
      return "Tipo MIME nao suportado para importacao.";
    }
    if (selected.size <= 0) return "Arquivo vazio. Selecione um arquivo com conteudo.";
    if (selected.size > MAX_UPLOAD_SIZE_BYTES) return "Arquivo muito grande. Limite maximo: 10 MB.";
    return null;
  }, []);

  const clearPreviewState = useCallback(() => {
    setPreview(null);
  }, []);

  const handleUpload = useCallback(async (selected: File) => {
    if (!token) return;

    const validationMessage = validateLeadFile(selected);
    if (validationMessage) {
      setFile(null);
      setError(validationMessage);
      setPreview(null);
      return;
    }

    setLoading(true);
    setError(null);
    setPreview(null);

    try {
      const data = await previewLeadImport(token, selected);
      setFile(selected);
      setPreview(data);
    } catch (err) {
      const message = toApiErrorMessage(err, "Erro ao gerar preview do arquivo.");
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [token, validateLeadFile]);

  return {
    file,
    setFile,
    preview,
    setPreview,
    loading,
    setLoading,
    error,
    setError,
    clearPreviewState,
    handleUpload,
  };
}
