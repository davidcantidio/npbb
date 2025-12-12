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

import { useAuth } from "../store/auth";

type FormState = {
  email: string;
  password: string;
};

export default function Login() {
  const [form, setForm] = useState<FormState>({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { login, token, loading: authLoading } = useAuth();

  const handleChange = (field: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
  };

  useEffect(() => {
    if (!authLoading && token) {
      window.location.href = "/success";
    }
  }, [authLoading, token]);

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
      window.location.href = "/success";
    } catch (err: any) {
      setError(err?.message || "Erro ao autenticar");
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
              sx={{ textTransform: "none", fontWeight: 700 }}
            >
              {loading || authLoading ? <CircularProgress size={22} color="inherit" /> : "Entrar"}
            </Button>
            <Button
              type="button"
              variant="text"
              onClick={() => {
                window.location.href = "/register";
              }}
              sx={{ textTransform: "none", fontWeight: 700 }}
            >
              Criar Conta
            </Button>
          </Stack>
        </Box>
      </Paper>
    </Container>
  );
}
