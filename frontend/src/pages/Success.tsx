import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Paper,
  Stack,
  Typography,
} from "@mui/material";

import { useAuth } from "../store/auth";

export default function Success() {
  const { user, loading, error, logout } = useAuth();

  return (
    <Container maxWidth="md" sx={{ minHeight: "100vh", display: "flex", alignItems: "center" }}>
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
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h5" fontWeight={700}>
            Login realizado
          </Typography>
          <Button onClick={logout} variant="outlined" color="primary">
            Sair
          </Button>
        </Box>

        {loading && (
          <Stack direction="row" spacing={1} alignItems="center">
            <CircularProgress size={22} />
            <Typography>Carregando dados do usuario...</Typography>
          </Stack>
        )}

        {error && (
          <Alert severity="error" variant="filled">
            {error}
          </Alert>
        )}

        {user && (
          <Box>
            <Typography variant="subtitle1" fontWeight={600} gutterBottom>
              Dados do usuario logado
            </Typography>
            <Paper
              variant="outlined"
              sx={{
                background: "#0f172a",
                color: "#e2e8f0",
                fontFamily: "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace",
                p: 2,
                borderRadius: 2,
                overflowX: "auto",
              }}
            >
              <pre style={{ margin: 0, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                {JSON.stringify(user, null, 2)}
              </pre>
            </Paper>
          </Box>
        )}
      </Paper>
    </Container>
  );
}
