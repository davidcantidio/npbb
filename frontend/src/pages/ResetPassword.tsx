import { useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useNavigate } from "react-router-dom";

import { ApiError, resetPassword } from "../services/usuarios";

type FormState = {
  password: string;
  confirmPassword: string;
};

const PASSWORD_RE = /^(?=.*[A-Za-z])(?=.*\d).{6,}$/;

export default function ResetPassword() {
  const navigate = useNavigate();
  const token = useMemo(() => new URLSearchParams(window.location.search).get("token") || "", []);
  const [form, setForm] = useState<FormState>({ password: "", confirmPassword: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleChange = (field: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!token) {
      setError("Token ausente. Verifique o link de recuperação.");
      return;
    }
    if (!PASSWORD_RE.test(form.password || "")) {
      setError("A senha deve ter no mínimo 6 caracteres, com pelo menos 1 letra e 1 número.");
      return;
    }
    if (form.password !== form.confirmPassword) {
      setError("As senhas não coincidem.");
      return;
    }

    setLoading(true);
    try {
      const res = await resetPassword(token, form.password);
      setSuccess(res.message || "Senha atualizada com sucesso.");
    } catch (err: any) {
      if (err instanceof ApiError) {
        const code =
          typeof err.detail === "object" && err.detail && "code" in err.detail
            ? (err.detail as any).code
            : null;
        if (code === "TOKEN_INVALID") setError("Token inválido.");
        else if (code === "TOKEN_EXPIRED") setError("Token expirado. Solicite novamente.");
        else if (code === "TOKEN_USED") setError("Token já utilizado. Solicite novamente.");
        else if (code === "PASSWORD_POLICY")
          setError("A senha deve ter no mínimo 6 caracteres, com pelo menos 1 letra e 1 número.");
        else setError(err.message || "Erro ao redefinir senha.");
      } else {
        setError(err?.message || "Erro ao redefinir senha.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ minHeight: "100vh", display: "flex", alignItems: "center" }}>
      <Paper
        elevation={3}
        sx={{
          width: "100%",
          p: 4,
          borderRadius: 3,
          display: "flex",
          flexDirection: "column",
          gap: 3,
        }}
      >
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Redefinir senha
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Escolha uma nova senha para sua conta.
          </Typography>
        </Box>

        <Box component="form" onSubmit={handleSubmit} noValidate>
          <Stack spacing={2.5}>
            <TextField
              label="Nova senha"
              type="password"
              value={form.password}
              onChange={handleChange("password")}
              required
              fullWidth
              autoComplete="new-password"
            />
            <TextField
              label="Confirmar nova senha"
              type="password"
              value={form.confirmPassword}
              onChange={handleChange("confirmPassword")}
              required
              fullWidth
              autoComplete="new-password"
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

            <Button
              variant="contained"
              size="large"
              type="submit"
              disabled={loading}
              sx={{ textTransform: "none", fontWeight: 700 }}
            >
              {loading ? <CircularProgress size={22} color="inherit" /> : "Atualizar senha"}
            </Button>

            <Button
              type="button"
              variant="text"
              onClick={() => {
                navigate("/login");
              }}
              sx={{ textTransform: "none", fontWeight: 700 }}
            >
              Voltar para login
            </Button>
          </Stack>
        </Box>
      </Paper>
    </Container>
  );
}
