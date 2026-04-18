import { useCallback, useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  IconButton,
  Paper,
  Snackbar,
  Stack,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  TextField,
  MenuItem,
  Typography,
} from "@mui/material";
import ArrowBackRoundedIcon from "@mui/icons-material/ArrowBackRounded";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import OpenInNewRoundedIcon from "@mui/icons-material/OpenInNewRounded";
import SaveRoundedIcon from "@mui/icons-material/SaveRounded";
import { Link as RouterLink, useNavigate, useParams } from "react-router-dom";

import { useAuth } from "../../store/auth";
import {
  createPersonGroup,
  createSocialProfile,
  deleteSocialProfile,
  getSponsoredPerson,
  listPersonGroups,
  listPersonRoles,
  listSocialProfiles,
  updateSponsoredPerson,
} from "../../services/sponsorship";
import { toApiErrorMessage } from "../../services/http";
import type {
  SocialProfileRead,
  SponsoredPersonRead,
  SponsoredPersonRoleRead,
  SponsorshipGroupRead,
} from "../../types/sponsorship";
import {
  compactInternationalPhone,
  displayInternationalPhoneFromApi,
  formatInternationalPhoneInput,
  isValidEmail,
  isValidInternationalPhone,
} from "../../utils/contactValidation";
import { isValidCpf, normalizeCpf } from "../../utils/cpf";
import ApiRequiredPanel from "./ApiRequiredPanel";
import { useSponsorshipApiMode } from "./sponsorshipMode";

type TabKey = "cadastro" | "perfis" | "grupos";

export default function SponsoredPersonDetailPage() {
  const apiMode = useSponsorshipApiMode();
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState<TabKey>("cadastro");
  const [person, setPerson] = useState<SponsoredPersonRead | null>(null);
  const [profiles, setProfiles] = useState<SocialProfileRead[]>([]);
  const [groups, setGroups] = useState<SponsorshipGroupRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [snack, setSnack] = useState<string | null>(null);

  const [fullName, setFullName] = useState("");
  const [personRoleOptions, setPersonRoleOptions] = useState<SponsoredPersonRoleRead[]>([]);
  const [roleId, setRoleId] = useState<number | "">("");
  const [cpf, setCpf] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [notes, setNotes] = useState("");
  const [emailError, setEmailError] = useState<string | null>(null);
  const [phoneError, setPhoneError] = useState<string | null>(null);

  const [profilePlatform, setProfilePlatform] = useState("");
  const [profileHandle, setProfileHandle] = useState("");
  const [profileUrl, setProfileUrl] = useState("");

  const [groupName, setGroupName] = useState("");
  const [groupDescription, setGroupDescription] = useState("");
  const [groupRole, setGroupRole] = useState("");

  const personId = Number(id);

  const load = useCallback(async () => {
    if (!apiMode) {
      setLoading(false);
      return;
    }
    if (!token || !Number.isFinite(personId)) {
      setError("Pessoa invalida ou sessao indisponivel.");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [personData, profilesData, groupsData, rolesData] = await Promise.all([
        getSponsoredPerson(token, personId),
        listSocialProfiles(token, "person", personId),
        listPersonGroups(token, personId),
        listPersonRoles(token),
      ]);
      setPerson(personData);
      setProfiles(profilesData);
      setGroups(groupsData);
      setPersonRoleOptions(rolesData);
      setFullName(personData.full_name);
      setRoleId(personData.role.id);
      setCpf(personData.cpf || "");
      setEmail(personData.email || "");
      setPhone(displayInternationalPhoneFromApi(personData.phone));
      setNotes(personData.notes || "");
      if (!groupName) setGroupName(personData.full_name);
    } catch (err) {
      setError(toApiErrorMessage(err, "Nao foi possivel carregar a pessoa patrocinada."));
    } finally {
      setLoading(false);
    }
  }, [apiMode, token, personId, groupName]);

  useEffect(() => {
    void load();
  }, [load]);

  if (!apiMode) return <ApiRequiredPanel title="Pessoa patrocinada" />;

  const cpfNorm = normalizeCpf(cpf);
  const cpfInvalid = cpfNorm.length > 0 && !isValidCpf(cpfNorm);

  const handleSave = async () => {
    if (!token || !person) return;
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
      const updated = await updateSponsoredPerson(token, person.id, {
        full_name: fullName.trim(),
        role_id: roleId,
        cpf: cpfNorm || null,
        email: emailTrim || null,
        phone: phoneCompact || null,
        notes: notes.trim() || null,
      });
      setPerson(updated);
      setRoleId(updated.role.id);
      setPhone(displayInternationalPhoneFromApi(updated.phone));
      setSnack("Cadastro atualizado.");
    } catch (err) {
      setSnack(toApiErrorMessage(err, "Nao foi possivel atualizar a pessoa patrocinada."));
    }
  };

  const handleCreateProfile = async () => {
    if (!token || !person) return;
    if (!profilePlatform.trim() || !profileHandle.trim()) {
      setSnack("Informe plataforma e handle do perfil.");
      return;
    }
    try {
      await createSocialProfile(token, {
        owner_type: "person",
        owner_id: person.id,
        platform: profilePlatform.trim(),
        handle: profileHandle.trim(),
        url: profileUrl.trim() || null,
        is_primary: profiles.length === 0,
      });
      setProfilePlatform("");
      setProfileHandle("");
      setProfileUrl("");
      await load();
      setSnack("Perfil social criado.");
    } catch (err) {
      setSnack(toApiErrorMessage(err, "Nao foi possivel criar o perfil social."));
    }
  };

  const handleDeleteProfile = async (profileId: number) => {
    if (!token) return;
    try {
      await deleteSocialProfile(token, profileId);
      await load();
      setSnack("Perfil social removido.");
    } catch (err) {
      setSnack(toApiErrorMessage(err, "Nao foi possivel remover o perfil social."));
    }
  };

  const handleCreateGroup = async () => {
    if (!token || !person) return;
    if (!groupName.trim()) {
      setSnack("Informe o nome do grupo.");
      return;
    }
    try {
      const group = await createPersonGroup(token, person.id, {
        name: groupName.trim(),
        description: groupDescription.trim() || null,
        role_in_group: groupRole.trim() || null,
      });
      navigate(`/patrocinados/grupos/${group.id}`);
    } catch (err) {
      setSnack(toApiErrorMessage(err, "Nao foi possivel criar o grupo vinculado."));
    }
  };

  return (
    <Stack spacing={2}>
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "center" }}>
        <Button component={RouterLink} to="/patrocinados" startIcon={<ArrowBackRoundedIcon />}>
          Voltar
        </Button>
        <Typography variant="h5" component="h1" fontWeight={800} sx={{ flex: "1 1 auto" }}>
          {person?.full_name || "Pessoa patrocinada"}
        </Typography>
        <Button variant="contained" startIcon={<SaveRoundedIcon />} onClick={() => void handleSave()}>
          Salvar cadastro
        </Button>
      </Box>

      {loading ? <Alert severity="info">Carregando pessoa patrocinada...</Alert> : null}
      {error ? <Alert severity="error">{error}</Alert> : null}

      {!loading && !error && person ? (
        <Paper variant="outlined">
          <Tabs value={tab} onChange={(_, next: TabKey) => setTab(next)} variant="scrollable">
            <Tab value="cadastro" label="Cadastro" />
            <Tab value="perfis" label={`Perfis sociais (${profiles.length})`} />
            <Tab value="grupos" label={`Grupos vinculados (${groups.length})`} />
          </Tabs>

          <Box hidden={tab !== "cadastro"} sx={{ p: { xs: 2, md: 3 } }}>
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
          </Box>

          <Box hidden={tab !== "perfis"} sx={{ p: { xs: 2, md: 3 } }}>
            <Stack spacing={2}>
              <Typography variant="subtitle1" fontWeight={800}>
                Novo perfil social
              </Typography>
              <TextField label="Plataforma" value={profilePlatform} onChange={(e) => setProfilePlatform(e.target.value)} fullWidth />
              <TextField label="Handle" value={profileHandle} onChange={(e) => setProfileHandle(e.target.value)} fullWidth />
              <TextField label="URL" value={profileUrl} onChange={(e) => setProfileUrl(e.target.value)} fullWidth />
              <Box>
                <Button variant="contained" onClick={() => void handleCreateProfile()}>
                  Adicionar perfil
                </Button>
              </Box>

              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Plataforma</TableCell>
                      <TableCell>Handle</TableCell>
                      <TableCell>URL</TableCell>
                      <TableCell align="right">Acoes</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {profiles.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={4}>
                          <Typography color="text.secondary">Nenhum perfil social cadastrado.</Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      profiles.map((profile) => (
                        <TableRow key={profile.id}>
                          <TableCell>{profile.platform}</TableCell>
                          <TableCell>{profile.handle}</TableCell>
                          <TableCell>{profile.url || "-"}</TableCell>
                          <TableCell align="right">
                            <IconButton
                              color="error"
                              size="small"
                              onClick={() => void handleDeleteProfile(profile.id)}
                            >
                              <DeleteOutlineIcon fontSize="small" />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Stack>
          </Box>

          <Box hidden={tab !== "grupos"} sx={{ p: { xs: 2, md: 3 } }}>
            <Stack spacing={2}>
              <Alert severity="info">
                Contratos e contrapartidas sao operados dentro de grupos. Crie um grupo vinculado
                para abrir o fluxo operacional.
              </Alert>

              <Typography variant="subtitle1" fontWeight={800}>
                Criar grupo vinculado
              </Typography>
              <TextField label="Nome do grupo" value={groupName} onChange={(e) => setGroupName(e.target.value)} fullWidth />
              <TextField
                label="Descricao"
                value={groupDescription}
                onChange={(e) => setGroupDescription(e.target.value)}
                multiline
                minRows={2}
                fullWidth
              />
              <TextField
                label="Papel da pessoa no grupo"
                value={groupRole}
                onChange={(e) => setGroupRole(e.target.value)}
                fullWidth
              />
              <Box>
                <Button variant="contained" onClick={() => void handleCreateGroup()}>
                  Criar grupo e abrir operacao
                </Button>
              </Box>

              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Grupo</TableCell>
                      <TableCell align="center">Membros</TableCell>
                      <TableCell align="center">Contratos</TableCell>
                      <TableCell align="right">Abrir</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {groups.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={4}>
                          <Typography color="text.secondary">Nenhum grupo vinculado.</Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      groups.map((group) => (
                        <TableRow key={group.id}>
                          <TableCell>{group.name}</TableCell>
                          <TableCell align="center">{group.members_count}</TableCell>
                          <TableCell align="center">{group.contracts_count}</TableCell>
                          <TableCell align="right">
                            <Button
                              component={RouterLink}
                              to={`/patrocinados/grupos/${group.id}`}
                              size="small"
                              startIcon={<OpenInNewRoundedIcon />}
                            >
                              Abrir
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Stack>
          </Box>
        </Paper>
      ) : null}

      <Snackbar
        open={Boolean(snack)}
        autoHideDuration={4000}
        onClose={() => setSnack(null)}
        message={snack || undefined}
      />
    </Stack>
  );
}
