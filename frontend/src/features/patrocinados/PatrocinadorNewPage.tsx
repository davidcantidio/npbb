import { useState } from "react";
import {
  Alert,
  Box,
  Button,
  Paper,
  Snackbar,
  Stack,
  Typography,
} from "@mui/material";
import ArrowBackRoundedIcon from "@mui/icons-material/ArrowBackRounded";
import SaveRoundedIcon from "@mui/icons-material/SaveRounded";
import { Link as RouterLink, useNavigate } from "react-router-dom";

import { createPatrocinador } from "../../services/patrocinados_local";
import type { PatrocinadorInput } from "../../types/patrocinados";
import { PatrocinadorForm } from "./PatrocinadorForm";
import { emptyPatrocinadorInput } from "./defaults";

export default function PatrocinadorNewPage() {
  const navigate = useNavigate();
  const [value, setValue] = useState<PatrocinadorInput>(() => emptyPatrocinadorInput());
  const [snack, setSnack] = useState<{ message: string; severity: "success" | "error" } | null>(
    null,
  );

  const handleSave = () => {
    if (!value.nome_fantasia.trim()) {
      setSnack({ message: "Informe o nome fantasia.", severity: "error" });
      return;
    }
    const created = createPatrocinador(value);
    setSnack({ message: "Patrocinador criado.", severity: "success" });
    navigate(`/patrocinados/${created.id}`, { replace: true });
  };

  return (
    <Stack spacing={2}>
      <Alert severity="info">
        Os dados desta tela são armazenados apenas no seu navegador (localStorage) até a API de
        patrocinadores estar disponível.
      </Alert>

      <Box sx={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 2 }}>
        <Button
          component={RouterLink}
          to="/patrocinados"
          startIcon={<ArrowBackRoundedIcon />}
          color="inherit"
        >
          Voltar
        </Button>
        <Typography variant="h5" component="h1" fontWeight={800} sx={{ flex: "1 1 auto" }}>
          Novo patrocinador
        </Typography>
        <Button variant="contained" startIcon={<SaveRoundedIcon />} onClick={handleSave}>
          Salvar
        </Button>
      </Box>

      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
        <PatrocinadorForm value={value} onChange={setValue} />
      </Paper>

      <Snackbar
        open={Boolean(snack)}
        autoHideDuration={4000}
        onClose={() => setSnack(null)}
        message={snack?.message}
      />
    </Stack>
  );
}
