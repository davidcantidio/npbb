import { useState } from "react";
import {
  Alert,
  Box,
  Button,
  Paper,
  Snackbar,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import ArrowBackRoundedIcon from "@mui/icons-material/ArrowBackRounded";
import SaveRoundedIcon from "@mui/icons-material/SaveRounded";
import { Link as RouterLink, useNavigate } from "react-router-dom";

import { useAuth } from "../../store/auth";
import { createSponsorshipGroup } from "../../services/sponsorship";
import { toApiErrorMessage } from "../../services/http";
import ApiRequiredPanel from "./ApiRequiredPanel";
import { useSponsorshipApiMode } from "./sponsorshipMode";

export default function SponsorshipGroupNewPage() {
  const apiMode = useSponsorshipApiMode();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [snack, setSnack] = useState<string | null>(null);

  if (!apiMode) return <ApiRequiredPanel title="Novo grupo de patrocinio" />;

  const handleSave = async () => {
    if (!token) {
      setSnack("Sessao nao disponivel.");
      return;
    }
    if (!name.trim()) {
      setSnack("Informe o nome do grupo.");
      return;
    }
    try {
      const created = await createSponsorshipGroup(token, {
        name: name.trim(),
        description: description.trim() || null,
      });
      navigate(`/patrocinados/grupos/${created.id}`, { replace: true });
    } catch (err) {
      setSnack(toApiErrorMessage(err, "Nao foi possivel criar o grupo."));
    }
  };

  return (
    <Stack spacing={2}>
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "center" }}>
        <Button component={RouterLink} to="/patrocinados/novo" startIcon={<ArrowBackRoundedIcon />}>
          Voltar
        </Button>
        <Typography variant="h5" component="h1" fontWeight={800} sx={{ flex: "1 1 auto" }}>
          Novo grupo de patrocinio
        </Typography>
        <Button variant="contained" startIcon={<SaveRoundedIcon />} onClick={() => void handleSave()}>
          Salvar
        </Button>
      </Box>

      <Alert severity="info">
        Crie grupos quando quiser iniciar a operacao contratual sem passar primeiro por uma pessoa
        ou instituicao.
      </Alert>

      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
        <Stack spacing={2}>
          <TextField label="Nome do grupo" value={name} onChange={(e) => setName(e.target.value)} required fullWidth />
          <TextField
            label="Descricao"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            minRows={3}
            fullWidth
          />
        </Stack>
      </Paper>

      <Snackbar
        open={Boolean(snack)}
        autoHideDuration={4000}
        onClose={() => setSnack(null)}
        message={snack || undefined}
      />
    </Stack>
  );
}
