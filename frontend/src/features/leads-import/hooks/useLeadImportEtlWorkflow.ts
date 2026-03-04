import { useCallback, useMemo, useState } from "react";
import { commitLeadImportEtl, previewLeadImportEtl, LeadImportEtlPreview, LeadImportEtlResult } from "../../../services/leads_import";
import { toApiErrorMessage } from "../../../services/http";

const MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024;
const ALLOWED_EXTENSIONS = [".xlsx"];
const ALLOWED_MIME_TYPES = [
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "application/vnd.ms-excel",
];

type EtlErrorState = {
  preview: string | null;
  commit: string | null;
};

type UseLeadImportEtlWorkflowResult = {
  file: File | null;
  preview: LeadImportEtlPreview | null;
  commitResult: LeadImportEtlResult | null;
  loading: boolean;
  errors: EtlErrorState;
  hasErrors: boolean;
  hasWarnings: boolean;
  canCommit: boolean;
  validateLeadFile: (selected: File) => string | null;
  handlePreview: (selected: File, eventoId: number, strict?: boolean) => Promise<void>;
  handleCommit: (eventoId: number, forceWarnings?: boolean) => Promise<void>;
  resetWorkflow: () => void;
  clearErrors: () => void;
};

export function useLeadImportEtlWorkflow(token: string | null): UseLeadImportEtlWorkflowResult {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<LeadImportEtlPreview | null>(null);
  const [commitResult, setCommitResult] = useState<LeadImportEtlResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<EtlErrorState>({ preview: null, commit: null });

  const validateLeadFile = useCallback((selected: File): string | null => {
    const lowerName = selected.name.toLowerCase();
    const hasAllowedExtension = ALLOWED_EXTENSIONS.some((ext) => lowerName.endsWith(ext));
    if (!hasAllowedExtension) return "Formato invalido. Use arquivo .xlsx.";
    if (selected.type && !ALLOWED_MIME_TYPES.includes(selected.type)) {
      return "Tipo MIME nao suportado para importacao ETL.";
    }
    if (selected.size <= 0) return "Arquivo vazio. Selecione um arquivo com conteudo.";
    if (selected.size > MAX_UPLOAD_SIZE_BYTES) return "Arquivo muito grande. Limite maximo: 50 MB.";
    return null;
  }, []);

  const clearErrors = useCallback(() => {
    setErrors({ preview: null, commit: null });
  }, []);

  const resetWorkflow = useCallback(() => {
    setFile(null);
    setPreview(null);
    setCommitResult(null);
    setLoading(false);
    setErrors({ preview: null, commit: null });
  }, []);

  const handlePreview = useCallback(async (selected: File, eventoId: number, strict = false) => {
    if (!token) return;

    const validationMessage = validateLeadFile(selected);
    if (validationMessage) {
      setFile(null);
      setPreview(null);
      setCommitResult(null);
      setErrors({ preview: validationMessage, commit: null });
      return;
    }

    setLoading(true);
    setErrors({ preview: null, commit: null });
    setPreview(null);
    setCommitResult(null);

    try {
      const data = await previewLeadImportEtl(token, selected, eventoId, strict);
      setFile(selected);
      setPreview(data);
    } catch (err) {
      const message = toApiErrorMessage(err, "Erro ao gerar preview ETL.");
      setErrors({ preview: message, commit: null });
    } finally {
      setLoading(false);
    }
  }, [token, validateLeadFile]);

  const handleCommit = useCallback(async (eventoId: number, forceWarnings = false) => {
    if (!token || !preview) return;

    setLoading(true);
    setErrors((prev) => ({ ...prev, commit: null }));

    try {
      const result = await commitLeadImportEtl(token, preview.session_token, eventoId, forceWarnings);
      setCommitResult(result);
    } catch (err) {
      const message = toApiErrorMessage(err, "Erro ao executar commit ETL.");
      setErrors((prev) => ({ ...prev, commit: message }));
    } finally {
      setLoading(false);
    }
  }, [preview, token]);

  const hasWarnings = useMemo(() => {
    if (!preview) return false;
    return preview.dq_report.some((item) => item.severity === "warning" && item.affected_rows > 0);
  }, [preview]);

  const hasErrors = useMemo(() => {
    if (!preview) return false;
    return preview.dq_report.some((item) => item.severity === "error" && item.affected_rows > 0);
  }, [preview]);

  const canCommit = Boolean(preview?.session_token) && !errors.preview && !hasErrors;

  return {
    file,
    preview,
    commitResult,
    loading,
    errors,
    hasErrors,
    hasWarnings,
    canCommit,
    validateLeadFile,
    handlePreview,
    handleCommit,
    resetWorkflow,
    clearErrors,
  };
}
