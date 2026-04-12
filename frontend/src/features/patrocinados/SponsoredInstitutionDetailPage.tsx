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
  Typography,
} from "@mui/material";
import ArrowBackRoundedIcon from "@mui/icons-material/ArrowBackRounded";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import OpenInNewRoundedIcon from "@mui/icons-material/OpenInNewRounded";
import SaveRoundedIcon from "@mui/icons-material/SaveRounded";
import { Link as RouterLink, useNavigate, useParams } from "react-router-dom";

import { useAuth } from "../../store/auth";
import {
  createInstitutionGroup,
  createSocialProfile,
  deleteSocialProfile,
  getSponsoredInstitution,
  listInstitutionGroups,
  listSocialProfiles,
  updateSponsoredInstitution,
} from "../../services/sponsorship";
import { toApiErrorMessage } from "../../services/http";
import type {
  SocialProfileRead,
  SponsoredInstitutionRead,
  SponsorshipGroupRead,
} from "../../types/sponsorship";
import ApiRequiredPanel from "./ApiRequiredPanel";
import { useSponsorshipApiMode } from "./sponsorshipMode";

type TabKey = "cadastro" | "perfis" | "grupos";

export default function SponsoredInstitutionDetailPage() {
  const apiMode = useSponsorshipApiMode();
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState<TabKey>("cadastro");
  const [institution, setInstitution] = useState<SponsoredInstitutionRead | null>(null);
  const [profiles, setProfiles] = useState<SocialProfileRead[]>([]);
  const [groups, setGroups] = useState<SponsorshipGroupRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [snack, setSnack] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [cnpj, setCnpj] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [notes, setNotes] = useState("");

  const [profilePlatform, setProfilePlatform] = useState("");
  const [profileHandle, setProfileHandle] = useState("");
  const [profileUrl, setProfileUrl] = useState("");

  const [groupName, setGroupName] = useState("");
  const [groupDescription, setGroupDescription] = useState("");
  const [groupRole, setGroupRole] = useState("");

  const institutionId = Number(id);

  const load = useCallback(async () => {
    if (!apiMode) {
      setLoading(false);
      return;
    }
    if (!token || !Number.isFinite(institutionId)) {
      setError("Instituicao invalida ou sessao indisponivel.");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [institutionData, profilesData, groupsData] = await Promise.all([
        getSponsoredInstitution(token, institutionId),
        listSocialProfiles(token, "institution", institutionId),
        listInstitutionGroups(token, institutionId),
      ]);
      setInstitution(institutionData);
      setProfiles(profilesData);
      setGroups(groupsData);
      setName(institutionData.name);
      setCnpj(institutionData.cnpj || "");
      setEmail(institutionData.email || "");
      setPhone(institutionData.phone || "");
      setNotes(institutionData.notes || "");
      if (!groupName) setGroupName(institutionData.name);
    } catch (err) {
      setError(toApiErrorMessage(err, "Nao foi possivel carregar a instituicao patrocinada."));
    } finally {
      setLoading(false);
    }
  }, [apiMode, token, institutionId, groupName]);

  useEffect(() => {
    void load();
  }, [load]);

  if (!apiMode) return <ApiRequiredPanel title="Instituicao patrocinada" />;

  const handleSave = async () => {
    if (!token || !institution) return;
    if (!name.trim()) {
      setSnack("Informe o nome da instituicao.");
      return;
    }
    try {
      const updated = await updateSponsoredInstitution(token, institution.id, {
        name: name.trim(),
        cnpj: cnpj.trim() || null,
        email: email.trim() || null,
        phone: phone.trim() || null,
        notes: notes.trim() || null,
      });
      setInstitution(updated);
      setSnack("Cadastro atualizado.");
    } catch (err) {
      setSnack(toApiErrorMessage(err, "Nao foi possivel atualizar a instituicao patrocinada."));
    }
  };

  const handleCreateProfile = async () => {
    if (!token || !institution) return;
    if (!profilePlatform.trim() || !profileHandle.trim()) {
      setSnack("Informe plataforma e handle do perfil.");
      return;
    }
    try {
      await createSocialProfile(token, {
        owner_type: "institution",
        owner_id: institution.id,
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
    if (!token || !institution) return;
    if (!groupName.trim()) {
      setSnack("Informe o nome do grupo.");
      return;
    }
    try {
      const group = await createInstitutionGroup(token, institution.id, {
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
          {institution?.name || "Instituicao patrocinada"}
        </Typography>
        <Button variant="contained" startIcon={<SaveRoundedIcon />} onClick={() => void handleSave()}>
          Salvar cadastro
        </Button>
      </Box>

      {loading ? <Alert severity="info">Carregando instituicao patrocinada...</Alert> : null}
      {error ? <Alert severity="error">{error}</Alert> : null}

      {!loading && !error && institution ? (
        <Paper variant="outlined">
          <Tabs value={tab} onChange={(_, next: TabKey) => setTab(next)} variant="scrollable">
            <Tab value="cadastro" label="Cadastro" />
            <Tab value="perfis" label={`Perfis sociais (${profiles.length})`} />
            <Tab value="grupos" label={`Grupos vinculados (${groups.length})`} />
          </Tabs>

          <Box hidden={tab !== "cadastro"} sx={{ p: { xs: 2, md: 3 } }}>
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
                Vincule a instituicao a um grupo para seguir com contratos e contrapartidas.
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
                label="Papel da instituicao no grupo"
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
