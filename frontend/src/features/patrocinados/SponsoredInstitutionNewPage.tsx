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
import { createSponsoredInstitution } from "../../services/sponsorship";
import { toApiErrorMessage } from "../../services/http";
import ApiRequiredPanel from "./ApiRequiredPanel";
import { useSponsorshipApiMode } from "./sponsorshipMode";

export default function SponsoredInstitutionNewPage() {
  const apiMode = useSponsorshipApiMode();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [cnpj, setCnpj] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [notes, setNotes] = useState("");
  const [snack, setSnack] = useState<string | null>(null);

  if (!apiMode) return <ApiRequiredPanel title="Nova instituicao patrocinada" />;

  const handleSave = async () => {
    if (!token) {
      setSnack("Sessao nao disponivel.");
      return;
    }
    if (!name.trim()) {
      setSnack("Informe o nome da instituicao patrocinada.");
      return;
    }
    try {
      const created = await createSponsoredInstitution(token, {
        name: name.trim(),
        cnpj: cnpj.trim() || null,
        email: email.trim() || null,
        phone: phone.trim() || null,
        notes: notes.trim() || null,
      });
      navigate(`/patrocinados/instituicoes/${created.id}`, { replace: true });
    } catch (err) {
      setSnack(toApiErrorMessage(err, "Nao foi possivel criar a instituicao patrocinada."));
    }
  };

  return (
    <Stack spacing={2}>
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "center" }}>
        <Button component={RouterLink} to="/patrocinados/novo" startIcon={<ArrowBackRoundedIcon />}>
          Voltar
        </Button>
        <Typography variant="h5" component="h1" fontWeight={800} sx={{ flex: "1 1 auto" }}>
          Nova instituicao patrocinada
        </Typography>
        <Button variant="contained" startIcon={<SaveRoundedIcon />} onClick={() => void handleSave()}>
          Salvar
        </Button>
      </Box>

      <Alert severity="info">
        Use esta tela para parceiros e instituicoes vinculadas ao patrocinado.
      </Alert>

      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
        <Stack spacing={2}>
          <TextField label="Nome" value={name} onChange={(e) => setName(e.target.value)} required fullWidth />
          <TextField label="CNPJ" value={cnpj} onChange={(e) => setCnpj(e.target.value)} fullWidth />
          <TextField label="Email" value={email} onChange={(e) => setEmail(e.target.value)} type="email" fullWidth />
          <TextField label="Telefone" value={phone} onChange={(e) => setPhone(e.target.value)} fullWidth />
          <TextField
            label="Observacoes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
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
