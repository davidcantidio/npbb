import { useCallback, useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Paper,
  Snackbar,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import ArrowBackRoundedIcon from "@mui/icons-material/ArrowBackRounded";
import SaveRoundedIcon from "@mui/icons-material/SaveRounded";
import { Link as RouterLink, useParams } from "react-router-dom";

import { useAuth } from "../../store/auth";
import {
  getSponsorshipGroup,
  listGroupContracts,
  listGroupMembers,
  listSponsoredInstitutions,
  listSponsoredPersons,
  updateSponsorshipGroup,
} from "../../services/sponsorship";
import { toApiErrorMessage } from "../../services/http";
import type {
  CounterpartRequirementRead,
  GroupMemberRead,
  RequirementOccurrenceRead,
  SponsoredInstitutionRead,
  SponsoredPersonRead,
  SponsorshipContractRead,
  SponsorshipGroupRead,
} from "../../types/sponsorship";
import ApiRequiredPanel from "./ApiRequiredPanel";
import GroupClausesPanel from "./SponsorshipGroupPanels/GroupClausesPanel";
import GroupContractsPanel from "./SponsorshipGroupPanels/GroupContractsPanel";
import GroupDeliveriesPanel from "./SponsorshipGroupPanels/GroupDeliveriesPanel";
import GroupMembersPanel from "./SponsorshipGroupPanels/GroupMembersPanel";
import GroupOccurrencesPanel from "./SponsorshipGroupPanels/GroupOccurrencesPanel";
import GroupRequirementsPanel from "./SponsorshipGroupPanels/GroupRequirementsPanel";
import { useSponsorshipApiMode } from "./sponsorshipMode";

type TabKey =
  | "members"
  | "contracts"
  | "clauses"
  | "requirements"
  | "occurrences"
  | "deliveries";

function normalizeSelectedId(current: number | null, nextIds: number[]) {
  if (nextIds.length === 0) return null;
  if (current != null && nextIds.includes(current)) return current;
  return nextIds[0];
}

export default function SponsorshipGroupPage() {
  const apiMode = useSponsorshipApiMode();
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const [tab, setTab] = useState<TabKey>("members");
  const [group, setGroup] = useState<SponsorshipGroupRead | null>(null);
  const [members, setMembers] = useState<GroupMemberRead[]>([]);
  const [contracts, setContracts] = useState<SponsorshipContractRead[]>([]);
  const [persons, setPersons] = useState<SponsoredPersonRead[]>([]);
  const [institutions, setInstitutions] = useState<SponsoredInstitutionRead[]>([]);
  const [requirements, setRequirements] = useState<CounterpartRequirementRead[]>([]);
  const [occurrences, setOccurrences] = useState<RequirementOccurrenceRead[]>([]);
  const [selectedContractId, setSelectedContractId] = useState<number | null>(null);
  const [selectedRequirementId, setSelectedRequirementId] = useState<number | null>(null);
  const [selectedOccurrenceId, setSelectedOccurrenceId] = useState<number | null>(null);
  const [groupName, setGroupName] = useState("");
  const [groupDescription, setGroupDescription] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [snack, setSnack] = useState<string | null>(null);

  const groupId = Number(id);

  const loadBase = useCallback(async () => {
    if (!apiMode) {
      setLoading(false);
      return;
    }
    if (!token || !Number.isFinite(groupId)) {
      setError("Grupo invalido ou sessao indisponivel.");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [groupData, membersData, contractsData, personsData, institutionsData] = await Promise.all([
        getSponsorshipGroup(token, groupId),
        listGroupMembers(token, groupId),
        listGroupContracts(token, groupId),
        listSponsoredPersons(token),
        listSponsoredInstitutions(token),
      ]);
      setGroup(groupData);
      setMembers(membersData);
      setContracts(contractsData);
      setPersons(personsData);
      setInstitutions(institutionsData);
      setGroupName(groupData.name);
      setGroupDescription(groupData.description || "");
    } catch (err) {
      setError(toApiErrorMessage(err, "Nao foi possivel carregar o grupo."));
    } finally {
      setLoading(false);
    }
  }, [apiMode, token, groupId]);

  useEffect(() => {
    void loadBase();
  }, [loadBase]);

  useEffect(() => {
    setSelectedContractId((current) =>
      normalizeSelectedId(current, contracts.map((contract) => contract.id)),
    );
  }, [contracts]);

  useEffect(() => {
    setSelectedRequirementId((current) =>
      normalizeSelectedId(current, requirements.map((requirement) => requirement.id)),
    );
  }, [requirements]);

  useEffect(() => {
    setSelectedOccurrenceId((current) =>
      normalizeSelectedId(current, occurrences.map((occurrence) => occurrence.id)),
    );
  }, [occurrences]);

  if (!apiMode) return <ApiRequiredPanel title="Grupo de patrocinio" />;

  const handleSaveGroup = async () => {
    if (!token || !group) return;
    if (!groupName.trim()) {
      setSnack("Informe o nome do grupo.");
      return;
    }
    try {
      await updateSponsorshipGroup(token, group.id, {
        name: groupName.trim(),
        description: groupDescription.trim() || null,
      });
      await loadBase();
      setSnack("Grupo atualizado.");
    } catch (err) {
      setSnack(toApiErrorMessage(err, "Nao foi possivel atualizar o grupo."));
    }
  };

  return (
    <Stack spacing={2}>
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "center" }}>
        <Button component={RouterLink} to="/patrocinados" startIcon={<ArrowBackRoundedIcon />}>
          Voltar
        </Button>
        <Typography variant="h5" component="h1" fontWeight={800} sx={{ flex: "1 1 auto" }}>
          {group?.name || "Grupo de patrocinio"}
        </Typography>
        <Button variant="contained" startIcon={<SaveRoundedIcon />} onClick={() => void handleSaveGroup()}>
          Salvar grupo
        </Button>
      </Box>

      {loading ? <Alert severity="info">Carregando grupo...</Alert> : null}
      {error ? <Alert severity="error">{error}</Alert> : null}

      {!loading && !error && group ? (
        <>
          <Alert severity="success">
            Fluxo operacional ativo: membros, contratos, clausulas, contrapartidas, ocorrencias,
            entregas e evidencias permanecem vinculados ao grupo.
          </Alert>

          <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
            <Stack spacing={2}>
              <TextField label="Nome do grupo" value={groupName} onChange={(e) => setGroupName(e.target.value)} required fullWidth />
              <TextField
                label="Descricao"
                value={groupDescription}
                onChange={(e) => setGroupDescription(e.target.value)}
                multiline
                minRows={2}
                fullWidth
              />
            </Stack>
          </Paper>

          <Paper variant="outlined">
            <Tabs value={tab} onChange={(_, next: TabKey) => setTab(next)} variant="scrollable" scrollButtons="auto">
              <Tab value="members" label={`Membros (${members.length})`} />
              <Tab value="contracts" label={`Contratos (${contracts.length})`} />
              <Tab value="clauses" label="Clausulas" />
              <Tab value="requirements" label="Contrapartidas" />
              <Tab value="occurrences" label="Ocorrencias" />
              <Tab value="deliveries" label="Entregas e evidencias" />
            </Tabs>

            <Box hidden={tab !== "members"} sx={{ p: { xs: 2, md: 3 } }}>
              <GroupMembersPanel
                token={token}
                groupId={group.id}
                members={members}
                persons={persons}
                institutions={institutions}
                onChanged={() => void loadBase()}
                onError={(message) => setSnack(message)}
              />
            </Box>

            <Box hidden={tab !== "contracts"} sx={{ p: { xs: 2, md: 3 } }}>
              <GroupContractsPanel
                token={token}
                groupId={group.id}
                contracts={contracts}
                selectedContractId={selectedContractId}
                onSelectContract={setSelectedContractId}
                onChanged={() => void loadBase()}
                onError={(message) => setSnack(message)}
              />
            </Box>

            <Box hidden={tab !== "clauses"} sx={{ p: { xs: 2, md: 3 } }}>
              <GroupClausesPanel
                token={token}
                contracts={contracts}
                selectedContractId={selectedContractId}
                onSelectContract={setSelectedContractId}
                onError={(message) => setSnack(message)}
              />
            </Box>

            <Box hidden={tab !== "requirements"} sx={{ p: { xs: 2, md: 3 } }}>
              <GroupRequirementsPanel
                token={token}
                contracts={contracts}
                selectedContractId={selectedContractId}
                onSelectContract={setSelectedContractId}
                onRequirementsChange={setRequirements}
                onError={(message) => setSnack(message)}
              />
            </Box>

            <Box hidden={tab !== "occurrences"} sx={{ p: { xs: 2, md: 3 } }}>
              <GroupOccurrencesPanel
                token={token}
                members={members}
                persons={persons}
                institutions={institutions}
                requirements={requirements}
                selectedRequirementId={selectedRequirementId}
                onSelectRequirement={setSelectedRequirementId}
                selectedOccurrenceId={selectedOccurrenceId}
                onSelectOccurrence={setSelectedOccurrenceId}
                onOccurrencesChange={setOccurrences}
                onError={(message) => setSnack(message)}
              />
            </Box>

            <Box hidden={tab !== "deliveries"} sx={{ p: { xs: 2, md: 3 } }}>
              <GroupDeliveriesPanel
                token={token}
                occurrences={occurrences}
                selectedOccurrenceId={selectedOccurrenceId}
                onSelectOccurrence={setSelectedOccurrenceId}
                onError={(message) => setSnack(message)}
              />
            </Box>
          </Paper>
        </>
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
