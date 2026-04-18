import { useEffect, useState } from "react";
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
import { useLocation, useNavigate } from "react-router-dom";

import { ForgotPasswordDialog } from "../components/ForgotPasswordDialog";
import { ApiError, toApiErrorCode, toApiErrorMessage } from "../services/http";
import { useAuth } from "../store/auth";

type FormState = {
  email: string;
  password: string;
};

function resolveLoginErrorMessage(err: unknown): string {
  const code = toApiErrorCode(err);
  if (code === "TIMEOUT") {
    return "O servidor demorou demais para responder. Confirme que o backend esta em execucao e tente novamente.";
  }
  if (code === "NETWORK_ERROR") {
    return "Nao foi possivel alcancar a API. Verifique se o backend, o proxy do Vite e o CORS estao configurados corretamente.";
  }
  if (err instanceof ApiError && err.status === 503) {
    if (code === "DB_TIMEOUT") {
      return "A autenticacao esta temporariamente indisponivel porque o banco de dados demorou demais para responder.";
    }
    if (code === "DB_UNAVAILABLE") {
      return "A autenticacao esta temporariamente indisponivel porque o backend nao conseguiu acessar o banco de dados.";
    }
  }
  return toApiErrorMessage(err, "Erro ao autenticar");
}

export default function Login() {
  const [form, setForm] = useState<FormState>({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [forgotOpen, setForgotOpen] = useState(false);
  const { login, token, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as any)?.from?.pathname || "/success";

  const handleChange = (field: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
  };

  useEffect(() => {
    if (!authLoading && token) {
      navigate(from, { replace: true });
    }
  }, [authLoading, token, navigate, from]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!form.email || !form.password) {
      setError("Preencha email e senha.");
      return;
    }
    setLoading(true);
    try {
      await login(form.email, form.password);
      navigate(from, { replace: true });
    } catch (err: unknown) {
      setError(resolveLoginErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ minHeight: "100vh", display: "flex", alignItems: "center" }}>
      <Paper
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
            Entrar
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Acesse o painel com suas credenciais corporativas.
          </Typography>
        </Box>

        <Box component="form" onSubmit={handleSubmit} noValidate>
          <Stack spacing={2.5}>
            <TextField
              label="Email"
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange("email")}
              required
              fullWidth
              autoComplete="email"
            />
            <TextField
              label="Senha"
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange("password")}
              required
              fullWidth
              autoComplete="current-password"
            />
            <Box display="flex" justifyContent="flex-end">
              <Button
                type="button"
                variant="text"
                size="small"
                onClick={() => setForgotOpen(true)}
              >
                Esqueceu a senha?
              </Button>
            </Box>
            {error && (
              <Alert severity="error" variant="filled">
                {error}
              </Alert>
            )}
            <Button
              variant="contained"
              size="large"
              type="submit"
              disabled={loading || authLoading}
            >
              {loading ? <CircularProgress size={22} color="inherit" /> : "Entrar"}
            </Button>
            <Button
              type="button"
              variant="text"
              onClick={() => {
                navigate("/novo-usuario");
              }}
            >
              Criar Conta
            </Button>
          </Stack>
        </Box>
      </Paper>
      <ForgotPasswordDialog
        open={forgotOpen}
        initialEmail={form.email}
        onClose={() => setForgotOpen(false)}
      />
    </Container>
  );
}
