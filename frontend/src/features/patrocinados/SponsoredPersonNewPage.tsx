import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  MenuItem,
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
import { createSponsoredPerson, listPersonRoles } from "../../services/sponsorship";
import { toApiErrorMessage } from "../../services/http";
import {
  compactInternationalPhone,
  formatInternationalPhoneInput,
  isValidEmail,
  isValidInternationalPhone,
} from "../../utils/contactValidation";
import { isValidCpf, normalizeCpf } from "../../utils/cpf";
import ApiRequiredPanel from "./ApiRequiredPanel";
import { useSponsorshipApiMode } from "./sponsorshipMode";
import type { SponsoredPersonRoleRead } from "../../types/sponsorship";

export default function SponsoredPersonNewPage() {
  const apiMode = useSponsorshipApiMode();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [personRoleOptions, setPersonRoleOptions] = useState<SponsoredPersonRoleRead[]>([]);
  const [roleId, setRoleId] = useState<number | "">("");
  const [cpf, setCpf] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [notes, setNotes] = useState("");
  const [snack, setSnack] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [phoneError, setPhoneError] = useState<string | null>(null);

  useEffect(() => {
    if (!apiMode || !token) return;
    void (async () => {
      try {
        const roles = await listPersonRoles(token);
        setPersonRoleOptions(roles);
      } catch {
        setSnack("Nao foi possivel carregar os papeis disponiveis.");
      }
    })();
  }, [apiMode, token]);

  if (!apiMode) return <ApiRequiredPanel title="Nova pessoa patrocinada" />;

  const cpfNorm = normalizeCpf(cpf);
  const cpfInvalid = cpfNorm.length > 0 && !isValidCpf(cpfNorm);

  const handleSave = async () => {
    if (!token) {
      setSnack("Sessao nao disponivel.");
      return;
    }
    if (!fullName.trim() || roleId === "") {
      setSnack("Informe nome e papel da pessoa patrocinada.");
      return;
    }
    const emailTrim = email.trim();
    const phoneCompact = compactInternationalPhone(phone);
    if (emailTrim && !isValidEmail(emailTrim)) {
      setEmailError("Email invalido.");
      setSnack("Corrija o email antes de salvar.");
      return;
    }
    if (phoneCompact && !isValidInternationalPhone(phone)) {
      setPhoneError("Telefone invalido. Use formato internacional E.164 (ex.: +5511987654321).");
      setSnack("Corrija o telefone antes de salvar.");
      return;
    }
    if (cpfNorm && !isValidCpf(cpfNorm)) {
      setSnack("Informe um CPF valido.");
      return;
    }
    try {
      const created = await createSponsoredPerson(token, {
        full_name: fullName.trim(),
        role_id: roleId,
        cpf: cpfNorm || null,
        email: emailTrim || null,
        phone: phoneCompact || null,
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
          <TextField
            select
            label="Papel"
            value={roleId === "" ? "" : String(roleId)}
            onChange={(e) => {
              const v = e.target.value;
              setRoleId(v === "" ? "" : Number(v));
            }}
            required
            fullWidth
            disabled={personRoleOptions.length === 0}
            helperText={personRoleOptions.length === 0 ? "Carregando opcoes de papel..." : undefined}
          >
            {personRoleOptions.map((opt) => (
              <MenuItem key={opt.id} value={String(opt.id)}>
                {opt.label}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            label="CPF"
            value={cpf}
            onChange={(e) => setCpf(e.target.value)}
            error={cpfInvalid}
            helperText={cpfInvalid ? "Informe um CPF valido." : "Opcional."}
            fullWidth
          />
          <TextField
            label="Email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              setEmailError(null);
            }}
            onBlur={() => {
              const t = email.trim();
              setEmailError(t && !isValidEmail(t) ? "Email invalido." : null);
            }}
            error={Boolean(emailError)}
            helperText={emailError || "Opcional. Ex.: nome@dominio.com"}
            type="email"
            fullWidth
          />
          <TextField
            label="Telefone"
            value={phone}
            onChange={(e) => {
              setPhone(formatInternationalPhoneInput(e.target.value));
              setPhoneError(null);
            }}
            onBlur={() => {
              const c = compactInternationalPhone(phone);
              setPhoneError(
                c && !isValidInternationalPhone(phone)
                  ? "Telefone invalido. Use formato internacional E.164 (ex.: +5511987654321)."
                  : null,
              );
            }}
            error={Boolean(phoneError)}
            helperText={
              phoneError ||
              "Opcional. Codigo do pais com + (E.164). Ex.: +5511987654321, +14155552671."
            }
            placeholder="+55 11 9999 9999"
            fullWidth
          />
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
