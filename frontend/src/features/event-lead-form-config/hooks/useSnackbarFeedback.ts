import { useCallback, useState } from "react";

export type SnackbarState = {
  open: boolean;
  message: string;
  severity: "success" | "error" | "info";
};

export function useSnackbarFeedback() {
  const [snackbar, setSnackbar] = useState<SnackbarState>({
    open: false,
    message: "",
    severity: "success",
  });

  const copyToClipboard = useCallback(async (text: string, label: string) => {
    const value = (text || "").trim();
    if (!value) {
      setSnackbar({ open: true, message: `Sem URL para copiar (${label}).`, severity: "info" });
      return;
    }

    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(value);
        setSnackbar({ open: true, message: `Copiado: ${label}`, severity: "success" });
        return;
      }
    } catch {
      // fallback abaixo
    }

    try {
      const textarea = document.createElement("textarea");
      textarea.value = value;
      textarea.style.position = "fixed";
      textarea.style.top = "0";
      textarea.style.left = "0";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();
      const ok = document.execCommand("copy");
      document.body.removeChild(textarea);

      setSnackbar({
        open: true,
        message: ok ? `Copiado: ${label}` : `Não foi possível copiar (${label}).`,
        severity: ok ? "success" : "error",
      });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : `Não foi possível copiar (${label}).`;
      setSnackbar({ open: true, message, severity: "error" });
    }
  }, []);

  const closeSnackbar = useCallback(() => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  }, []);

  const handleSnackbarClose = useCallback((_event: unknown, reason?: string) => {
    if (reason === "clickaway") return;
    setSnackbar((prev) => ({ ...prev, open: false }));
  }, []);

  const showSuccess = useCallback((message: string) => {
    setSnackbar({ open: true, message, severity: "success" });
  }, []);

  const showError = useCallback((message: string) => {
    setSnackbar({ open: true, message, severity: "error" });
  }, []);

  return {
    snackbar,
    setSnackbar,
    copyToClipboard,
    closeSnackbar,
    handleSnackbarClose,
    showSuccess,
    showError,
  };
}
