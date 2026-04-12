import { useCallback, useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Paper,
  Stack,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Typography,
} from "@mui/material";
import AddRoundedIcon from "@mui/icons-material/AddRounded";
import OpenInNewRoundedIcon from "@mui/icons-material/OpenInNewRounded";
import { Link as RouterLink } from "react-router-dom";

import { useAuth } from "../../store/auth";
import {
  listSponsoredInstitutions,
  listSponsoredPersons,
  listSponsorshipGroups,
} from "../../services/sponsorship";
import { toApiErrorMessage } from "../../services/http";
import type {
  SponsoredInstitutionRead,
  SponsoredPersonRead,
  SponsorshipGroupRead,
} from "../../types/sponsorship";
import ApiRequiredPanel from "./ApiRequiredPanel";
import { useSponsorshipApiMode } from "./sponsorshipMode";

type TabKey = "persons" | "institutions" | "groups";

export default function PatrocinadosPage() {
  const apiMode = useSponsorshipApiMode();
  const { token } = useAuth();
  const [tab, setTab] = useState<TabKey>("persons");
  const [persons, setPersons] = useState<SponsoredPersonRead[]>([]);
  const [institutions, setInstitutions] = useState<SponsoredInstitutionRead[]>([]);
  const [groups, setGroups] = useState<SponsorshipGroupRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!apiMode) {
      setLoading(false);
      return;
    }
    if (!token) {
      setLoading(false);
      setError("Sessao nao disponivel.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [personsData, institutionsData, groupsData] = await Promise.all([
        listSponsoredPersons(token),
        listSponsoredInstitutions(token),
        listSponsorshipGroups(token),
      ]);
      setPersons(personsData);
      setInstitutions(institutionsData);
      setGroups(groupsData);
    } catch (err) {
      setError(toApiErrorMessage(err, "Nao foi possivel carregar patrocinados."));
    } finally {
      setLoading(false);
    }
  }, [apiMode, token]);

  useEffect(() => {
    void load();
  }, [load]);

  if (!apiMode) return <ApiRequiredPanel title="Patrocinados" />;

  return (
    <Stack spacing={2}>
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "center" }}>
        <Typography variant="h5" component="h1" fontWeight={800} sx={{ flex: "1 1 auto" }}>
          Patrocinados
        </Typography>
        <Button
          component={RouterLink}
          to="/patrocinados/novo"
          variant="contained"
          startIcon={<AddRoundedIcon />}
        >
          Novo cadastro
        </Button>
      </Box>

      <Alert severity="info">
        Fluxo owner-first ativo: pessoas, instituicoes e grupos sao entradas de primeiro nivel.
      </Alert>

      <Paper variant="outlined">
        <Tabs
          value={tab}
          onChange={(_, next: TabKey) => setTab(next)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label={`Pessoas (${persons.length})`} value="persons" />
          <Tab label={`Instituicoes (${institutions.length})`} value="institutions" />
          <Tab label={`Grupos (${groups.length})`} value="groups" />
        </Tabs>
      </Paper>

      {loading ? (
        <Stack alignItems="center" sx={{ py: 6 }}>
          <CircularProgress size={30} />
        </Stack>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : null}

      {!loading && !error && tab === "persons" ? (
        <TableContainer component={Paper} variant="outlined">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Pessoa</TableCell>
                <TableCell>Papel</TableCell>
                <TableCell align="center">Perfis</TableCell>
                <TableCell align="center">Grupos</TableCell>
                <TableCell align="center">Contratos</TableCell>
                <TableCell align="right">Abrir</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {persons.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6}>
                    <Typography color="text.secondary" sx={{ py: 2 }}>
                      Nenhuma pessoa patrocinada cadastrada.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                persons.map((person) => (
                  <TableRow key={person.id} hover>
                    <TableCell>
                      <Typography fontWeight={700}>{person.full_name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {person.email || "sem email"}
                      </Typography>
                    </TableCell>
                    <TableCell>{person.role}</TableCell>
                    <TableCell align="center">{person.social_profiles_count}</TableCell>
                    <TableCell align="center">{person.groups_count}</TableCell>
                    <TableCell align="center">{person.contracts_count}</TableCell>
                    <TableCell align="right">
                      <Button
                        component={RouterLink}
                        to={`/patrocinados/pessoas/${person.id}`}
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
      ) : null}

      {!loading && !error && tab === "institutions" ? (
        <TableContainer component={Paper} variant="outlined">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Instituicao</TableCell>
                <TableCell>CNPJ</TableCell>
                <TableCell align="center">Perfis</TableCell>
                <TableCell align="center">Grupos</TableCell>
                <TableCell align="center">Contratos</TableCell>
                <TableCell align="right">Abrir</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {institutions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6}>
                    <Typography color="text.secondary" sx={{ py: 2 }}>
                      Nenhuma instituicao patrocinada cadastrada.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                institutions.map((institution) => (
                  <TableRow key={institution.id} hover>
                    <TableCell>
                      <Typography fontWeight={700}>{institution.name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {institution.email || "sem email"}
                      </Typography>
                    </TableCell>
                    <TableCell>{institution.cnpj || "-"}</TableCell>
                    <TableCell align="center">{institution.social_profiles_count}</TableCell>
                    <TableCell align="center">{institution.groups_count}</TableCell>
                    <TableCell align="center">{institution.contracts_count}</TableCell>
                    <TableCell align="right">
                      <Button
                        component={RouterLink}
                        to={`/patrocinados/instituicoes/${institution.id}`}
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
      ) : null}

      {!loading && !error && tab === "groups" ? (
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
                    <Typography color="text.secondary" sx={{ py: 2 }}>
                      Nenhum grupo de patrocinio cadastrado.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                groups.map((group) => (
                  <TableRow key={group.id} hover>
                    <TableCell>
                      <Typography fontWeight={700}>{group.name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {group.description || "sem descricao"}
                      </Typography>
                    </TableCell>
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
      ) : null}
    </Stack>
  );
}
