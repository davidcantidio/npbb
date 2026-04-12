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
import { createSponsoredPerson } from "../../services/sponsorship";
import { toApiErrorMessage } from "../../services/http";
import ApiRequiredPanel from "./ApiRequiredPanel";
import { useSponsorshipApiMode } from "./sponsorshipMode";

export default function SponsoredPersonNewPage() {
  const apiMode = useSponsorshipApiMode();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("");
  const [cpf, setCpf] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [notes, setNotes] = useState("");
  const [snack, setSnack] = useState<string | null>(null);

  if (!apiMode) return <ApiRequiredPanel title="Nova pessoa patrocinada" />;

  const handleSave = async () => {
    if (!token) {
      setSnack("Sessao nao disponivel.");
      return;
    }
    if (!fullName.trim() || !role.trim()) {
      setSnack("Informe nome e papel da pessoa patrocinada.");
      return;
    }
    try {
      const created = await createSponsoredPerson(token, {
        full_name: fullName.trim(),
        role: role.trim(),
        cpf: cpf.trim() || null,
        email: email.trim() || null,
        phone: phone.trim() || null,
        notes: notes.trim() || null,
      });
      navigate(`/patrocinados/pessoas/${created.id}`, { replace: true });
    } catch (err) {
      setSnack(toApiErrorMessage(err, "Nao foi possivel criar a pessoa patrocinada."));
    }
  };

  return (
    <Stack spacing={2}>
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "center" }}>
        <Button component={RouterLink} to="/patrocinados/novo" startIcon={<ArrowBackRoundedIcon />}>
          Voltar
        </Button>
        <Typography variant="h5" component="h1" fontWeight={800} sx={{ flex: "1 1 auto" }}>
          Nova pessoa patrocinada
        </Typography>
        <Button variant="contained" startIcon={<SaveRoundedIcon />} onClick={() => void handleSave()}>
          Salvar
        </Button>
      </Box>

      <Alert severity="info">
        Cadastre o patrocinado principal. Contratos e contrapartidas serao operados em grupos
        vinculados.
      </Alert>

      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
        <Stack spacing={2}>
          <TextField label="Nome completo" value={fullName} onChange={(e) => setFullName(e.target.value)} required fullWidth />
          <TextField label="Papel" value={role} onChange={(e) => setRole(e.target.value)} required fullWidth />
          <TextField label="CPF" value={cpf} onChange={(e) => setCpf(e.target.value)} fullWidth />
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
