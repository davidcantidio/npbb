import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Link,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import { ApiError, forgotPassword } from "../services/usuarios";

type Props = {
  open: boolean;
  initialEmail?: string;
  onClose: () => void;
};

const isValidEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

export function ForgotPasswordDialog({ open, initialEmail, onClose }: Props) {
  const [email, setEmail] = useState(initialEmail || "");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [debugResetUrl, setDebugResetUrl] = useState<string | null>(null);

  const normalizedInitialEmail = useMemo(() => (initialEmail || "").trim(), [initialEmail]);

  useEffect(() => {
    if (!open) return;
    setEmail(normalizedInitialEmail);
    setError(null);
    setSuccess(null);
    setDebugResetUrl(null);
  }, [open, normalizedInitialEmail]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setDebugResetUrl(null);

    const value = email.trim();
    if (!value) {
      setError("Informe seu email.");
      return;
    }
    if (!isValidEmail(value)) {
      setError("Email inválido.");
      return;
    }

    setSubmitting(true);
    try {
      const res = await forgotPassword(value);
      setSuccess(res.message || "Solicitação enviada.");
      setDebugResetUrl(res.reset_url || null);
    } catch (err: any) {
      if (err instanceof ApiError) {
        const code =
          typeof err.detail === "object" && err.detail && "code" in err.detail
            ? (err.detail as any).code
            : null;
        if (err.status === 404 && code === "USER_NOT_FOUND") {
          setError("Email não encontrado.");
        } else {
          setError(err.message || "Erro ao solicitar recuperação.");
        }
      } else {
        setError(err?.message || "Erro ao solicitar recuperação.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onClose={submitting ? undefined : onClose} maxWidth="xs" fullWidth>
      <DialogTitle>Recuperar senha</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Informe seu email para receber as instruções de recuperação.
          </Typography>

          <Box component="form" id="forgot-password-form" onSubmit={handleSubmit}>
            <Stack spacing={2}>
              <TextField
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                fullWidth
                required
                disabled={submitting}
              />

              {error && (
                <Alert severity="error" variant="filled">
                  {error}
                </Alert>
              )}

              {success && (
                <Alert severity="success" variant="filled">
                  {success}
                </Alert>
              )}

              {debugResetUrl && (
                <Alert severity="info">
                  <Typography variant="body2" sx={{ mb: 0.5 }}>
                    Modo debug: link de reset
                  </Typography>
                  <Link href={debugResetUrl} target="_blank" rel="noreferrer">
                    {debugResetUrl}
                  </Link>
                </Alert>
              )}
            </Stack>
          </Box>
        </Stack>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} disabled={submitting} sx={{ textTransform: "none" }}>
          Cancelar
        </Button>
        <Button
          variant="contained"
          type="submit"
          form="forgot-password-form"
          disabled={submitting}
          sx={{ textTransform: "none", fontWeight: 700 }}
        >
          {submitting ? <CircularProgress size={22} color="inherit" /> : "Enviar"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
